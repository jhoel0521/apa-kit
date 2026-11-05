"""Importa un documento Word (.docx) ya avanzado a capitulos/*.md.

Pensado para quien ya escribió buena parte de su tesis en Word o Google Docs
(Archivo → Descargar → Microsoft Word) y quiere seguir con esta plantilla.

Uso (desde la carpeta de la plantilla):
    python3 scripts/importar_docx.py "/ruta/Mi tesis.docx"      # en Windows: py -3 scripts/importar_docx.py "C:/ruta/Mi tesis.docx"
    python3 scripts/importar_docx.py "Mi tesis.docx" --oracion    # TÍTULOS EN MAYÚSCULAS → Títulos en oración

Qué hace:
- NO modifica tu documento: guarda una copia en original/ (carpeta ignorada por git).
- Los capítulos que había en capitulos/ se mueven a capitulos/_antes-de-importar-<fecha>/ (no se borra nada).
- Divide el documento por títulos de nivel 1 en un archivo .md por capítulo.
- Quita la numeración escrita a mano ("CAPÍTULO I", "1.2.") porque el generador numera solo.
- Convierte negritas, cursivas, listas, tablas e imágenes (a recursos/figuras/), con sus títulos
  "Tabla N"/"Figura N"/"Cuadro N"/"Gráfico N" y sus notas o fuentes.
- Lo que no puede convertir (ecuaciones, cuadros de texto, gráficos de Excel, notas al pie) queda
  marcado como [[revisar: ...]] para completarlo a mano.
- El texto de la portada se guarda en original/portada.txt para pasar los datos a .env.
"""
import _entorno  # noqa: F401  (usa .venv/ si existe)

import argparse
import re
import shutil
import sys
import unicodedata
from datetime import datetime
from pathlib import Path

from docx import Document
from docx.oxml.ns import qn
from docx.table import Table
from docx.text.paragraph import Paragraph
from docx.text.run import Run

DOCS = Path(__file__).resolve().parents[1]
CAPITULOS = DOCS / "capitulos"
FIGURAS = DOCS / "recursos" / "figuras"
ORIGINAL = DOCS / "original"

RE_CAPITULO = re.compile(r"^cap[ií]tulo\s+([ivxlc]+|\d+|[a-záéíóúñ]+)\b[\s.:\-–—]*", re.I)
RE_NUMERO = re.compile(r"^(\d+(\.\d+)*\.?|[IVXLC]+\.|[A-Z]\.)\s+")
RE_LEYENDA = re.compile(r"^(tabla|cuadro|figura|gr[aá]fico|ilustraci[oó]n|imagen|diagrama)\s+(\d+(\.\d+)*)\s*[.:\-–—]?\s*(.*)$", re.I)
RE_NOTA = re.compile(r"^(nota|fuente)\s*[.:]\s*(.*)$", re.I)
TIPO = {"tabla": "tabla", "cuadro": "tabla"}  # el resto son figuras

PRELIMINARES = {"resumen": "00-resumen", "abstract": "00-resumen", "dedicatoria": "00-dedicatoria",
                "agradecimiento": "00-agradecimientos", "agradecimientos": "00-agradecimientos",
                "epigrafe": "00-epigrafe", "prologo": "00-prologo", "presentacion": "00-presentacion"}
INDICES = ("indice", "contenido", "tabla de contenido", "lista de tablas", "lista de figuras",
           "indice de tablas", "indice de figuras", "indice de cuadros", "indice de graficos",
           "lista de cuadros", "lista de graficos", "indice general")
FINALES = {"referencias": "90-referencias", "bibliografia": "90-referencias",
           "referencias bibliograficas": "90-referencias", "anexos": "95-anexos", "anexo": "95-anexos",
           "apendices": "95-anexos", "apendice": "95-anexos", "glosario": "92-glosario"}

avisos = []


def plano(txt):
    return "".join(c for c in unicodedata.normalize("NFD", txt.casefold())
                   if unicodedata.category(c) != "Mn").strip(" .:")


def slug(txt):
    s = re.sub(r"[^a-z0-9]+", "-", plano(txt)).strip("-")
    return s[:40] or "capitulo"


# ================================================================ lectura de Word
def nivel_titulo(p):
    """Nivel 1..4 si el párrafo es un título (por estilo o nivel de esquema), si no 0."""
    nombre = (p.style.name if p.style is not None else "").lower()
    if nombre.startswith(("toc", "table of figures", "tabla de ilustraciones")):
        return -1  # entrada de un índice automático
    if nombre in ("title", "título", "titulo", "subtitle", "subtítulo"):
        return 0
    m = re.match(r"(heading|t[ií]tulo)\s*(\d)", nombre)
    if m:
        return min(int(m.group(2)), 4)
    estilo = p.style
    while estilo is not None:
        lvl = estilo.element.find(f"{qn('w:pPr')}/{qn('w:outlineLvl')}")
        if lvl is not None and int(lvl.get(qn("w:val"))) < 9:
            return min(int(lvl.get(qn("w:val"))) + 1, 4)
        estilo = estilo.base_style
    lvl = p._p.find(f"{qn('w:pPr')}/{qn('w:outlineLvl')}")
    if lvl is not None and int(lvl.get(qn("w:val"))) < 9:
        return min(int(lvl.get(qn("w:val"))) + 1, 4)
    return 0


def es_negrita(p):
    runs = [Run(r, p) for r in p._p.xpath(".//w:r") if (Run(r, p).text or "").strip()]
    if not runs:
        return False
    estilo_b = bool(p.style is not None and p.style.font.bold)
    return all(r.bold or (r.bold is None and estilo_b) for r in runs)


class Lector:
    def __init__(self, doc):
        self.doc = doc
        self.n_img = 0
        self.notas_pie = self._notas_pie()
        self.formato_listas = self._formatos_lista()

    def _notas_pie(self):
        notas = {}
        for rel in self.doc.part.rels.values():
            if rel.reltype.endswith("/footnotes"):
                from lxml import etree
                raiz = etree.fromstring(rel.target_part.blob)
                for fn in raiz.findall(qn("w:footnote")):
                    txt = "".join(t.text or "" for t in fn.iter(qn("w:t"))).strip()
                    if txt:
                        notas[fn.get(qn("w:id"))] = txt
        return notas

    def _formatos_lista(self):
        """numId -> {ilvl: numFmt} para saber si una lista es numerada o de viñetas."""
        try:
            num = self.doc.part.numbering_part.element
        except Exception:
            return {}
        abstractos = {}
        for a in num.findall(qn("w:abstractNum")):
            abstractos[a.get(qn("w:abstractNumId"))] = {
                lv.get(qn("w:ilvl")): (lv.find(qn("w:numFmt")).get(qn("w:val"))
                                       if lv.find(qn("w:numFmt")) is not None else "bullet")
                for lv in a.findall(qn("w:lvl"))}
        res = {}
        for n in num.findall(qn("w:num")):
            ref = n.find(qn("w:abstractNumId"))
            if ref is not None:
                res[n.get(qn("w:numId"))] = abstractos.get(ref.get(qn("w:val")), {})
        return res

    def lista(self, p):
        """(nivel, ordenada) si el párrafo es parte de una lista de Word, si no None."""
        numpr = p._p.find(f"{qn('w:pPr')}/{qn('w:numPr')}")
        nombre = (p.style.name if p.style is not None else "").lower()
        if numpr is None:
            if "list bullet" in nombre or "viñeta" in nombre:
                return 0, False
            if "list number" in nombre:
                return 0, True
            return None
        ilvl = numpr.find(qn("w:ilvl"))
        numid = numpr.find(qn("w:numId"))
        nivel = int(ilvl.get(qn("w:val"))) if ilvl is not None else 0
        clave = numid.get(qn("w:val")) if numid is not None else None
        if clave == "0":
            return None
        fmt = self.formato_listas.get(clave, {}).get(str(nivel), "bullet")
        return nivel, fmt not in ("bullet", "none")

    def texto(self, p, con_formato=True):
        """Texto en Markdown del párrafo. Devuelve (texto, imágenes guardadas)."""
        partes, imagenes = [], []
        for r_el in p._p.xpath(".//w:r"):
            if r_el.xpath("ancestor::w:del"):
                continue
            for blip in r_el.xpath(".//a:blip/@r:embed"):
                ruta = self._guardar_imagen(blip)
                if ruta:
                    imagenes.append(ruta)
            if r_el.xpath(".//c:chart"):
                partes.append(("[[revisar: gráfico de Excel no importado; pégalo como imagen]]", False, False))
            for fn in r_el.xpath("./w:footnoteReference/@w:id"):
                partes.append((f" [[nota al pie: {self.notas_pie.get(fn, '?')}]]", False, False))
            r = Run(r_el, p)
            t = r.text
            if t:
                partes.append((t, bool(r.bold), bool(r.italic)))
        if p._p.xpath(".//m:oMath"):
            partes.append((" [[revisar: ecuación no importada]]", False, False))
        if p._p.xpath(".//w:txbxContent"):
            partes.append((" [[revisar: cuadro de texto no importado]]", False, False))
        return self._unir(partes, con_formato), imagenes

    @staticmethod
    def _unir(partes, con_formato):
        # junta runs seguidos con el mismo formato y aplica ** y * fuera de los espacios
        grupos = []
        for t, b, i in partes:
            if grupos and grupos[-1][1:] == (b, i):
                grupos[-1][0] += t
            else:
                grupos.append([t, b, i])
        salida = []
        for t, b, i in grupos:
            if not con_formato or not t.strip() or not (b or i):
                salida.append(t)
                continue
            marca = "**" if b and not i else "*" if i and not b else "***"
            ini = len(t) - len(t.lstrip())
            fin = len(t.rstrip())
            salida.append(t[:ini] + marca + t[ini:fin] + marca + t[fin:])
        txt = "".join(salida).replace("\t", " ").replace("\n", " ")
        # une negritas partidas por Word: "**Decisión del** **Product**" -> "**Decisión del Product**"
        txt = re.sub(r"(?<!\*)\*\*(\s*)\*\*(?!\*)", r"\1", txt)
        return re.sub(r" {2,}", " ", txt).strip()

    def _guardar_imagen(self, rid):
        parte = self.doc.part.related_parts.get(rid)
        if parte is None:
            return None
        ext = Path(parte.partname).suffix.lower() or ".png"
        if ext in (".emf", ".wmf"):
            avisos.append(f"imagen {Path(parte.partname).name} en formato {ext}: Word la muestra pero no se "
                          "puede insertar; expórtala como PNG")
        self.n_img += 1
        FIGURAS.mkdir(parents=True, exist_ok=True)
        ruta = FIGURAS / f"importada-{self.n_img:03d}{ext}"
        ruta.write_bytes(parte.blob)
        return ruta

    def tabla(self, t):
        filas = []
        for fila in t.rows:
            celdas, vistos = [], set()
            for c in fila.cells:
                if id(c._tc) in vistos:  # celdas combinadas se repiten en python-docx
                    continue
                vistos.add(id(c._tc))
                txt = "<br>".join(x for x in (self.texto(p)[0] for p in c.paragraphs) if x)
                celdas.append(txt.replace("|", "\\|"))
            filas.append(celdas)
        if filas:  # el generador ya pone en negrita el encabezado
            filas[0] = [c.replace("**", "") for c in filas[0]]
        n = max(len(f) for f in filas) if filas else 0
        return [f + [""] * (n - len(f)) for f in filas]

    def bloques(self):
        """Recorre el cuerpo en orden (incluye controles de contenido, salta índices automáticos)."""
        def recorrer(padre):
            for hijo in padre.iterchildren():
                if hijo.tag == qn("w:p"):
                    yield Paragraph(hijo, self.doc._body)
                elif hijo.tag == qn("w:tbl"):
                    yield Table(hijo, self.doc._body)
                elif hijo.tag == qn("w:sdt"):
                    galeria = hijo.xpath(".//w:docPartGallery/@w:val")
                    if galeria and "Table of Contents" in galeria[0]:
                        continue
                    contenido = hijo.find(qn("w:sdtContent"))
                    if contenido is not None:
                        yield from recorrer(contenido)
        yield from recorrer(self.doc.element.body)


# ================================================================ conversión
class Capitulo:
    def __init__(self, archivo, titulo, attrs=""):
        self.archivo, self.lineas = archivo, []
        if titulo:
            self.lineas.append(f"# {titulo}{attrs}")


def limpiar_titulo(txt, oracion):
    txt = re.sub(r"[*]", "", txt).strip()
    txt = RE_CAPITULO.sub("", txt)
    txt = RE_NUMERO.sub("", txt).strip(" .:-–—")
    if oracion and txt.isupper() and len(txt) > 3:
        txt = txt[0] + txt[1:].lower()
    return txt


def convertir(origen, oracion):
    doc = Document(origen)
    lector = Lector(doc)
    hay_estilos = any(nivel_titulo(p) > 0 for p in doc.paragraphs)
    if not hay_estilos:
        avisos.append("el documento no usa estilos de título (Título 1, Título 2…); detecto los títulos "
                      "por negrita y numeración: revisa que los capítulos hayan quedado bien")

    portada, capitulos = [], []
    actual = None
    pendiente_cap = False      # "CAPÍTULO I" en una línea y el nombre en la siguiente
    leyenda = None             # "Tabla 3" vista antes de la tabla
    ultimo = None              # último bloque tabla/figura emitido (para leyendas debajo)
    en_indice = False
    usados = set()
    vistas = {}                # palabras usadas en leyendas: tabla, cuadro, figura, gráfico…
    cuenta = {"titulos": 0, "parrafos": 0, "tablas": 0, "figuras": 0, "revisar": 0}

    def nuevo_capitulo(titulo):
        nonlocal actual, en_indice
        clave = plano(titulo)
        en_indice = clave in INDICES
        if en_indice:
            actual = None
            return
        if clave in PRELIMINARES:
            base, attrs = PRELIMINARES[clave], ""
        elif clave in FINALES:
            base, attrs = FINALES[clave], " {.sin-numero}"
        else:
            base = f"{sum(1 for c in capitulos if c.archivo[:2].isdigit() and 0 < int(c.archivo[:2]) < 90) + 1:02d}-{slug(titulo)}"
            attrs = ""
        existente = next((c for c in capitulos if c.archivo == base), None)
        if existente:  # p. ej. Resumen y Abstract en el mismo archivo
            existente.lineas += ["", f"# {titulo}{attrs}"]
            actual = existente
        else:
            actual = Capitulo(base, titulo, attrs)
            capitulos.append(actual)

    def emitir(*lineas):
        if actual is None:
            return
        if actual.lineas and actual.lineas[-1] != "":
            actual.lineas.append("")
        actual.lineas.extend(lineas)

    def clave_unica(tipo, n):
        k = f"{tipo}{n}".replace(".", "-")
        while k in usados:
            k += "b"
        usados.add(k)
        return k

    for bloque in lector.bloques():
        if isinstance(bloque, Table):
            if actual is None or en_indice:
                continue
            filas = lector.tabla(bloque)
            if not filas:
                continue
            if len(filas) == 1 or not any(any(c for c in f) for f in filas[1:]):
                avisos.append(f"tabla de una sola fila en «{actual.archivo}»: ¿era un recuadro? revísala")
            titulo = leyenda["titulo"] if leyenda and leyenda["tipo"] == "tabla" else ""
            k = clave_unica("tabla", leyenda["n"] if leyenda else cuenta["tablas"] + 1)
            leyenda = None
            ley = f"Tabla: {titulo or '[[título de la tabla]]'} {{#{k}}}"
            emitir(ley, "", "| " + " | ".join(filas[0]) + " |", "|" + "---|" * len(filas[0]),
                   *["| " + " | ".join(f) + " |" for f in filas[1:]])
            ultimo = {"tipo": "tabla", "cap": actual, "idx": actual.lineas.index(ley), "titulado": bool(titulo)}
            cuenta["tablas"] += 1
            continue

        p = bloque
        nivel = nivel_titulo(p)
        if nivel == -1:
            continue
        txt, imagenes = lector.texto(p)
        crudo = re.sub(r"\*", "", txt).strip()

        if not hay_estilos and crudo and es_negrita(p) and len(crudo.split()) <= 14 and not crudo.endswith("."):
            if RE_CAPITULO.match(crudo) or plano(crudo) in PRELIMINARES or plano(crudo) in FINALES \
                    or plano(crudo) in INDICES:
                nivel = 1
            elif actual is None and not pendiente_cap:
                nivel = 0  # antes del primer capítulo, las MAYÚSCULAS en negrita son la portada
            elif re.match(r"^\d+\.\d+\.\d+", crudo):
                nivel = 3
            elif re.match(r"^\d+\.\d+", crudo):
                nivel = 2
            elif re.match(r"^\d+\.?\s", crudo) or crudo.isupper():
                nivel = 1 if actual is None or crudo.isupper() else 2

        # ---- leyendas y notas de tablas/figuras
        m = RE_LEYENDA.match(crudo) if crudo and len(crudo) < 250 else None
        if m and nivel == 0:
            tipo = TIPO.get(plano(m.group(1)), "figura")
            vistas[plano(m.group(1))] = vistas.get(plano(m.group(1)), 0) + 1
            titulo = m.group(4).strip()
            if ultimo and not ultimo["titulado"] and ultimo["tipo"] == tipo and titulo:
                # leyenda debajo (estilo Word por defecto): se aplica al bloque anterior
                cap, i = ultimo["cap"], ultimo["idx"]
                cap.lineas[i] = re.sub(r"\[\[título de la (tabla|figura)\]\]", titulo, cap.lineas[i])
                ultimo["titulado"] = True
            else:
                leyenda = {"tipo": tipo, "n": m.group(2), "titulo": titulo, "pide_titulo": not titulo}
            continue
        if leyenda and leyenda.get("pide_titulo") and crudo and nivel == 0 and not imagenes:
            leyenda["titulo"], leyenda["pide_titulo"] = crudo, False  # APA: el título va en la línea siguiente
            continue
        mn = RE_NOTA.match(crudo) if crudo else None
        if mn and ultimo and ultimo["cap"] is actual and actual.lineas and \
                actual.lineas[-1].startswith(("|", "![")):
            cuerpo = re.sub(r"^[*\s]*(nota|fuente)[*\s]*[.:][*\s]*", "", txt, flags=re.I).strip()
            if plano(mn.group(1)) == "fuente":
                cuerpo = "Fuente: " + cuerpo
            emitir(f"Nota: {cuerpo}")
            continue

        # ---- títulos
        if nivel > 0 and crudo:
            if nivel == 1 or pendiente_cap:
                limpio = limpiar_titulo(crudo, oracion)
                if not limpio:  # "CAPÍTULO I" sin nombre: el nombre viene después
                    pendiente_cap = True
                    continue
                pendiente_cap = False
                nuevo_capitulo(limpio)
            elif actual is not None and not en_indice:
                emitir(f"{'#' * nivel} {limpiar_titulo(crudo, oracion)}")
            cuenta["titulos"] += 1
            continue
        if pendiente_cap and crudo:
            pendiente_cap = False
            nuevo_capitulo(limpiar_titulo(crudo, oracion))
            continue

        # ---- portada y contenido
        if actual is None:
            if not en_indice and crudo:
                portada.append(crudo)
            continue
        if en_indice:
            continue
        for img in imagenes:
            titulo = leyenda["titulo"] if leyenda and leyenda["tipo"] == "figura" else ""
            k = clave_unica("figura", leyenda["n"] if leyenda else cuenta["figuras"] + 1)
            leyenda = None
            rel = Path("..") / img.relative_to(DOCS)
            linea = f"![{titulo or '[[título de la figura]]'}]({rel.as_posix()}){{#{k}}}"
            emitir(linea)
            ultimo = {"tipo": "figura", "cap": actual, "idx": len(actual.lineas) - 1, "titulado": bool(titulo)}
            cuenta["figuras"] += 1
        if not crudo:
            continue
        lst = lector.lista(p)
        if lst:
            nivel_l, ordenada = lst
            item = f"{'  ' * nivel_l}{'1.' if ordenada else '-'} {txt}"
            if actual.lineas and re.match(r"^\s*(-|\d+\.)\s", actual.lineas[-1]):
                actual.lineas.append(item)
            else:
                emitir(item)
        else:
            if re.match(r"^([#>|]|\d+[.)]\s|[-*+]\s|Tabla:|Nota:|!\[)", txt):
                txt = "\u200b" + txt  # evita que una frase se lea como sintaxis especial
            if plano(actual.archivo) == "90-referencias":
                actual.lineas.append(txt)  # una referencia por línea, sin línea vacía
            else:
                emitir(txt)
                cuenta["parrafos"] += 1
    for palabra, clave in (("cuadro", "etiqueta_tabla"), ("grafico", "etiqueta_figura")):
        rival = "tabla" if palabra == "cuadro" else "figura"
        if vistas.get(palabra, 0) > vistas.get(rival, 0):
            avisos.append(f'tu documento usa «{palabra.title()}»: en documento.toml pon {clave} = '
                          f'"{"Cuadro" if palabra == "cuadro" else "Gráfico"}" (APA 7 usa «{rival.title()}»)')
    if leyenda:
        avisos.append(f"leyenda «{leyenda['tipo'].title()} {leyenda['n']}» sin tabla o figura asociada")
    # "como muestra la Tabla 3" -> "como muestra la @tabla:tabla3" (numeración automática)
    def a_ref(m):
        tipo = TIPO.get(plano(m.group(1)), "figura")
        k = f"{tipo}{m.group(2)}".replace(".", "-")
        return f"@{tipo}:{k}" if k in usados else m.group(0)

    for c in capitulos:
        c.lineas = [ln if ln.startswith(("Tabla:", "![", "#")) else
                    re.sub(r"\b(Tabla|Cuadro|Figura|Gr[aá]fico|Ilustraci[oó]n)\s+(\d+(?:\.\d+)*)\b", a_ref, ln)
                    for ln in c.lineas]
        cuenta["revisar"] += sum(ln.count("[[") for ln in c.lineas)
    return portada, capitulos, cuenta


def palabras(txt):
    return len(re.findall(r"\w+", re.sub(r"\[\[.*?\]\]|[*#|>`-]", " ", txt)))


def main():
    ap = argparse.ArgumentParser(description="Importa un .docx a capitulos/*.md")
    ap.add_argument("docx", help="ruta del documento Word (.docx)")
    ap.add_argument("--oracion", action="store_true", help="pasar TÍTULOS EN MAYÚSCULAS a tipo oración")
    args = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")

    origen = Path(args.docx).expanduser().resolve()
    if not origen.exists():
        sys.exit(f"No encuentro {origen}")
    if origen.suffix.lower() != ".docx":
        sys.exit("Solo se admite .docx. Si es .doc u .odt, ábrelo en Word y usa Guardar como → .docx. "
                 "Si está en Google Docs: Archivo → Descargar → Microsoft Word (.docx).")

    sello = datetime.now().strftime("%Y%m%d-%H%M")
    ORIGINAL.mkdir(exist_ok=True)
    copia = ORIGINAL / f"{sello}-{origen.name}"
    shutil.copy2(origen, copia)

    portada, capitulos, cuenta = convertir(copia, args.oracion)
    if not capitulos:
        sys.exit("No encontré capítulos. ¿El documento tiene títulos? Usa los estilos Título 1 / Título 2 "
                 "de Word en los nombres de capítulo y vuelve a importar.")

    previos = sorted(CAPITULOS.glob("*.md"))
    if previos:
        resguardo = CAPITULOS / f"_antes-de-importar-{sello}"
        resguardo.mkdir(parents=True)
        for f in previos:
            shutil.move(str(f), resguardo / f.name)
    for c in capitulos:
        (CAPITULOS / f"{c.archivo}.md").write_text("\n".join(c.lineas).rstrip() + "\n", encoding="utf-8")
    (ORIGINAL / "portada.txt").write_text(
        "# Texto que estaba antes del primer capítulo (portada). Pasa estos datos a .env.\n"
        + "\n".join(portada) + "\n", encoding="utf-8")

    doc = Document(copia)
    total_orig = palabras(" ".join(p.text for p in doc.paragraphs) + " " +
                          " ".join(c.text for t in doc.tables for f in t.rows for c in f.cells))
    total_md = sum(palabras("\n".join(c.lineas)) for c in capitulos)

    print(f"Copia del original: {copia.relative_to(DOCS)}  (tu archivo no se modificó)")
    if previos:
        print(f"Capítulos anteriores movidos a: capitulos/_antes-de-importar-{sello}/")
    print(f"\nArchivos creados en capitulos/:")
    for c in capitulos:
        print(f"  {c.archivo}.md")
    print(f"\nTítulos {cuenta['titulos']} · párrafos {cuenta['parrafos']} · tablas {cuenta['tablas']} · "
          f"figuras {cuenta['figuras']} · marcas [[ ]] para revisar {cuenta['revisar']}")
    print(f"Palabras: original ≈ {total_orig} · importadas ≈ {total_md} "
          f"({100 * total_md // max(total_orig, 1)} %; la diferencia normal es portada e índices)")
    print("Portada guardada en original/portada.txt → copia esos datos a .env")
    for a in avisos:
        print("AVISO ", a)
    print("\nSiguiente paso: python3 scripts/generar_docx.py   (en Windows: py -3 scripts/generar_docx.py)")


if __name__ == "__main__":
    main()
