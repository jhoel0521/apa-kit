"""Genera el documento APA 7 (.docx) a partir de docs/capitulos/*.md.

Uso (desde la raíz del repositorio):
    python docs/scripts/generar_docx.py            # genera docs/dist/<salida>.docx
    python docs/scripts/generar_docx.py --estado   # avance por capítulo, sin generar
    python docs/scripts/generar_docx.py --forzar   # sobrescribe aunque el .docx se haya editado a mano

Fuentes:
    docs/documento.toml   configuración del documento (título, papel, fuente, preliminares…)
    docs/.env             datos personales para {{VARIABLES}} (NO se versiona; ver .env.example)
    docs/capitulos/*.md   contenido, en orden alfabético de archivo
    docs/recursos/        logos, figuras y diagramas

La sintaxis Markdown admitida está en docs/README.md.
"""
import argparse
import hashlib
import json
import re
import sys
import tomllib
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from apa import DocumentoAPA  # noqa: E402

DOCS = Path(__file__).resolve().parents[1]
CAPITULOS = DOCS / "capitulos"
RECURSOS = DOCS / "recursos"
DIST = DOCS / "dist"
HUELLAS = DIST / ".huellas.json"

RE_TITULO = re.compile(r"^(#{1,4})\s+(.+?)\s*$")
RE_ATRIB = re.compile(r"\s*\{([^{}]*)\}\s*$")
RE_FIGURA = re.compile(r"^!\[(.*?)\]\((.+?)\)\s*$")
RE_LEYENDA = re.compile(r"^Tabla:\s*(.+)$")
RE_NOTA = re.compile(r"^Nota:\s*(.+)$")
RE_LISTA = re.compile(r"^(\s*)([-*+]|\d+[.)])\s+(.*)$")
RE_REF = re.compile(r"@(tabla|figura|sec):([A-Za-z0-9_-]+)")
RE_VAR = re.compile(r"\{\{\s*([A-Z0-9_]+)\s*\}\}")
RE_PENDIENTE = re.compile(r"\[\[[^\]]+\]\]")
SALTOS = {r"\newpage", "<!-- salto -->", "\\pagebreak"}

errores, avisos = [], []


# ================================================================ configuración
def cargar_env(ruta):
    datos = {}
    if ruta.exists():
        for ln in ruta.read_text(encoding="utf-8").splitlines():
            ln = ln.strip()
            if ln and not ln.startswith("#") and "=" in ln:
                k, v = ln.split("=", 1)
                datos[k.strip()] = v.strip().strip('"').strip("'")
    return datos


def cargar_config():
    ruta = DOCS / "documento.toml"
    if not ruta.exists():
        sys.exit(f"Falta {ruta}")
    with ruta.open("rb") as f:
        return tomllib.load(f)


def atributos(txt):
    """'Texto {#clave .clase k=v}' -> ('Texto', {'id':..., 'clases': set, k: v})."""
    attrs = {"id": None, "clases": set()}
    m = RE_ATRIB.search(txt)
    if not m:
        return txt, attrs
    for tok in re.findall(r'[^\s"]+="[^"]*"|\S+', m.group(1)):
        if tok.startswith("#"):
            attrs["id"] = tok[1:]
        elif tok.startswith("."):
            attrs["clases"].add(tok[1:])
        elif "=" in tok:
            k, v = tok.split("=", 1)
            attrs[k] = v.strip('"')
    return txt[:m.start()].rstrip(), attrs


# ================================================================ lectura del Markdown
def parsear(ruta):
    """Convierte un .md en una lista de bloques. Cada bloque guarda archivo:línea para los errores."""
    texto = re.sub(r"<!--(?! salto).*?-->", "", ruta.read_text(encoding="utf-8"), flags=re.S)
    lineas = texto.splitlines()
    bloques, i, leyenda, en_refs = [], 0, None, None
    origen = lambda n: f"{ruta.relative_to(DOCS)}:{n + 1}"  # noqa: E731

    while i < len(lineas):
        ln = lineas[i]
        s = ln.strip()
        if not s:
            i += 1
            continue
        if s in SALTOS:
            bloques.append({"tipo": "salto"})
            i += 1
            continue

        m = RE_TITULO.match(s)
        if m:
            txt, at = atributos(m.group(2))
            nivel = len(m.group(1))
            bloques.append({"tipo": "titulo", "nivel": nivel, "texto": txt, "at": at, "origen": origen(i)})
            es_refs = "referencias" in at["clases"] or _plano(txt) in ("referencias", "bibliografia")
            if es_refs:
                en_refs = nivel
                bloques.append({"tipo": "referencias", "items": [], "orden": "sin-orden" not in at["clases"]})
            elif en_refs and nivel <= en_refs:
                en_refs = None
            i += 1
            continue

        if en_refs:  # cada línea no vacía es una referencia
            bloques[-1]["items"].append(re.sub(r"^[-*]\s+", "", s))
            i += 1
            continue

        if s.startswith("```"):
            j = i + 1
            while j < len(lineas) and not lineas[j].strip().startswith("```"):
                j += 1
            bloques.append({"tipo": "codigo", "lineas": lineas[i + 1:j]})
            i = j + 1
            continue

        m = RE_LEYENDA.match(s)
        if m:
            txt, at = atributos(m.group(1))
            leyenda = {"titulo": txt, "at": at, "origen": origen(i)}
            i += 1
            continue

        if s.startswith("|"):
            filas = []
            while i < len(lineas) and lineas[i].strip().startswith("|"):
                celdas = [c.strip().replace("\\|", "|")
                          for c in re.split(r"(?<!\\)\|", lineas[i].strip().strip("|"))]
                if not all(re.fullmatch(r":?-{2,}:?", c) for c in celdas if c):
                    filas.append(celdas)
                i += 1
            if not leyenda:
                avisos.append(f"{origen(i - 1)}: tabla sin línea 'Tabla: título' antes; queda sin número")
            bloques.append({"tipo": "tabla", "filas": filas, "leyenda": leyenda, "nota": None,
                            "origen": origen(i - 1)})
            leyenda = None
            continue

        resto, at = atributos(s) if s.startswith("![") else (s, None)
        m = RE_FIGURA.match(resto)
        if m:
            img = (ruta.parent / m.group(2)).resolve()
            if not img.exists():
                img = (RECURSOS / m.group(2)).resolve()
            bloques.append({"tipo": "figura", "titulo": m.group(1), "ruta": img, "at": at, "nota": None,
                            "origen": origen(i)})
            if not img.exists():
                errores.append(f"{origen(i)}: no existe la imagen {m.group(2)}")
            i += 1
            continue

        m = RE_NOTA.match(s)
        if m and bloques and bloques[-1]["tipo"] in ("tabla", "figura") and not bloques[-1]["nota"]:
            bloques[-1]["nota"] = m.group(1)
            i += 1
            continue

        if RE_LISTA.match(ln):
            items = []
            while i < len(lineas) and lineas[i].strip():
                ml = RE_LISTA.match(lineas[i])
                if ml:
                    items.append([len(ml.group(1).expandtabs(4)) // 2, ml.group(2)[0].isdigit(), ml.group(3)])
                elif items:  # línea de continuación del ítem anterior
                    items[-1][2] += " " + lineas[i].strip()
                i += 1
            bloques.append({"tipo": "lista", "items": [tuple(x) for x in items]})
            continue

        if s.startswith(">"):
            partes = []
            while i < len(lineas) and lineas[i].strip().startswith(">"):
                partes.append(lineas[i].strip()[1:].strip())
                i += 1
            bloques.append({"tipo": "cita", "texto": " ".join(partes)})
            continue

        partes = [s]  # párrafo: líneas seguidas hasta una línea vacía o un bloque especial
        i += 1
        while i < len(lineas):
            t = lineas[i].strip()
            if (not t or RE_TITULO.match(t) or t.startswith(("|", ">", "```", "![")) or RE_LISTA.match(lineas[i])
                    or RE_LEYENDA.match(t) or t in SALTOS):
                break
            partes.append(t)
            i += 1
        bloques.append({"tipo": "parrafo", "texto": " ".join(partes)})

    if leyenda:
        errores.append(f"{leyenda['origen']}: 'Tabla:' sin tabla debajo")
    return bloques


def _plano(txt):
    return "".join(c for c in unicodedata.normalize("NFD", txt.casefold()) if unicodedata.category(c) != "Mn")


# ================================================================ numeración y referencias
def numerar(secciones, cfg):
    """Asigna números a títulos, tablas y figuras en el orden de aparición y registra las claves."""
    claves, cap, sub = {}, 0, [0, 0, 0]
    tablas = figuras = 0
    numerar_titulos = cfg.get("numerar_titulos", True)
    formato = cfg.get("formato_capitulo", "Capítulo {n}. {titulo}")
    padre_numerado = False

    def registrar(tipo, clave, valor, origen):
        if not clave:
            return
        if (tipo, clave) in claves:
            errores.append(f"{origen}: clave repetida #{clave}")
        claves[(tipo, clave)] = valor

    for previo, bloques in secciones:
        for b in bloques:
            if b["tipo"] == "titulo":
                at, n = b["at"], b["nivel"]
                b["en_indice"] = ("en-indice" in at["clases"]) if previo else ("sin-indice" not in at["clases"])
                numerado = numerar_titulos and not previo and "sin-numero" not in at["clases"]
                if n == 1:
                    padre_numerado = numerado
                    if numerado:
                        cap += 1
                        sub = [0, 0, 0]
                        b["mostrar"] = formato.format(n=cap, titulo=b["texto"])
                        registrar("sec", at["id"], f"Capítulo {cap}", b["origen"])
                    else:
                        b["mostrar"] = b["texto"]
                        registrar("sec", at["id"], f"«{b['texto']}»", b["origen"])
                elif numerado and padre_numerado and n <= 3:
                    sub[n - 2] += 1
                    for k in range(n - 1, 3):
                        sub[k] = 0
                    num = ".".join(str(x) for x in [cap] + sub[:n - 1])
                    b["mostrar"] = f"{num}. {b['texto']}"
                    registrar("sec", at["id"], f"sección {num}", b["origen"])
                else:
                    b["mostrar"] = b["texto"]
                    registrar("sec", at["id"], f"«{b['texto']}»", b["origen"])
            elif b["tipo"] == "tabla" and b["leyenda"]:
                tablas += 1
                registrar("tabla", b["leyenda"]["at"]["id"], f"Tabla {tablas}", b["origen"])
            elif b["tipo"] == "figura":
                figuras += 1
                registrar("figura", b["at"]["id"], f"Figura {figuras}", b["origen"])
    return claves


class Sustituto:
    """Reemplaza {{VARIABLES}} del .env y @tabla:/@figura:/@sec: por su número."""

    def __init__(self, variables, claves):
        self.variables, self.claves = variables, claves
        self.faltan, self.sin_resolver = set(), set()

    def __call__(self, txt):
        def var(m):
            v = self.variables.get(m.group(1))
            if v:
                return v
            self.faltan.add(m.group(1))
            return f"[[{m.group(1)}]]"

        def ref(m):
            v = self.claves.get((m.group(1), m.group(2)))
            if v is None:
                self.sin_resolver.add(m.group(0))
                return f"[[{m.group(0)}]]"
            return v
        return RE_REF.sub(ref, RE_VAR.sub(var, txt))


# ================================================================ escritura
def renderizar(doc, bloques, sub, cfg):
    tam_tabla = cfg.get("tamano_tabla")
    for b in bloques:
        t = b["tipo"]
        if t == "titulo":
            doc.titulo(min(b["nivel"], 4), sub(b["mostrar"]), en_indice=b["en_indice"])
        elif t == "parrafo":
            doc.parrafo(sub(b["texto"]))
        elif t == "lista":
            doc.lista([(n, o, sub(x)) for n, o, x in b["items"]])
        elif t == "cita":
            doc.cita(sub(b["texto"]))
        elif t == "codigo":
            doc.codigo(b["lineas"])
        elif t == "salto":
            doc.salto()
        elif t == "referencias":
            items = [sub(x) for x in b["items"]]
            for x in sorted(items, key=lambda r: _plano(re.sub(r"[\[\]*_`]", "", r))) if b["orden"] else items:
                doc.referencia(x)
        elif t == "tabla":
            ley = b["leyenda"]
            if ley:
                doc.leyenda("Tabla", sub(ley["titulo"]))
            filas = [[sub(c) for c in f] for f in b["filas"]]
            anchos = None
            if ley and "anchos" in ley["at"]:
                anchos = [float(x) for x in ley["at"]["anchos"].split(",")]
                if len(anchos) != len(filas[0]):
                    errores.append(f"{b['origen']}: 'anchos' tiene {len(anchos)} valores y la tabla "
                                   f"{len(filas[0])} columnas")
                    anchos = None
            size = float(ley["at"]["tam"]) if ley and "tam" in ley["at"] else tam_tabla
            doc.tabla(filas[0], filas[1:], anchos, size)
            if b["nota"]:
                doc.nota(sub(b["nota"]))
        elif t == "figura" and b["ruta"].exists():
            ancho = float(b["at"]["ancho"]) if "ancho" in b["at"] else None
            doc.figura(b["ruta"], sub(b["titulo"]), ancho, sub(b["nota"]) if b["nota"] else None)


def portada(doc, cfg, sub):
    p = cfg.get("portada", {})
    for _ in range(int(p.get("espacios_arriba", 2))):
        doc.vacio()
    logo = cfg.get("logo")
    if logo:
        ruta = DOCS / logo
        if ruta.exists():
            doc.imagen(ruta, float(cfg.get("logo_ancho_cm", 4)))
        else:
            avisos.append(f"documento.toml: no existe el logo {logo}; la portada sale sin logo")
    titulo = doc.parrafo(sub(cfg.get("titulo", "[[Título del documento]]")), "Normal", "centro")
    for r in titulo.runs:
        r.bold = True
    if cfg.get("subtitulo"):
        doc.parrafo(sub(cfg["subtitulo"]), "Normal", "centro")
    doc.vacio()
    for ln in p.get("lineas", []):
        doc.parrafo(sub(ln), "Normal", "centro")
    doc.salto()


# ================================================================ protección del .docx editado a mano
def _sha(ruta):
    return hashlib.sha256(ruta.read_bytes()).hexdigest()


def puede_escribir(salida, forzar):
    if not salida.exists() or forzar:
        return True
    huellas = json.loads(HUELLAS.read_text(encoding="utf-8")) if HUELLAS.exists() else {}
    if huellas.get(salida.name) == _sha(salida):
        return True
    sys.exit(f"ALTO: {salida.relative_to(DOCS)} cambió después de generarse (¿lo editaste en Word?).\n"
             "  No lo sobrescribo. Renómbralo, cambia 'salida' en documento.toml o usa --forzar.")


def guardar_huella(salida):
    huellas = json.loads(HUELLAS.read_text(encoding="utf-8")) if HUELLAS.exists() else {}
    huellas[salida.name] = _sha(salida)
    HUELLAS.write_text(json.dumps(huellas, indent=2), encoding="utf-8")


# ================================================================ main
def archivos_md():
    todos = sorted(CAPITULOS.glob("*.md"))
    previos = [f for f in todos if f.name.startswith("00")]
    return previos, [f for f in todos if f not in previos]


def estado(cfg):
    """Resumen de avance: palabras, tablas, figuras y pendientes [[...]] por archivo."""
    previos, caps = archivos_md()
    print(f"{'Archivo':38} {'Palabras':>8} {'Tablas':>6} {'Figuras':>7} {'Pend.':>5}")
    total = 0
    for f in previos + caps:
        txt = re.sub(r"<!--.*?-->", "", f.read_text(encoding="utf-8"), flags=re.S)
        palabras = len(re.findall(r"\b\w+\b", re.sub(r"^\s*\|.*$", "", txt, flags=re.M)))
        total += palabras
        tablas = len(re.findall(r"^Tabla:", txt, re.M))
        figuras = len(re.findall(r"^!\[", txt, re.M))
        pend = len(RE_PENDIENTE.findall(txt))
        print(f"{f.name:38} {palabras:>8} {tablas:>6} {figuras:>7} {pend:>5}")
    meta = cfg.get("meta_palabras")
    print(f"{'TOTAL':38} {total:>8}" + (f"   meta {meta} ({100 * total // meta} %)" if meta else ""))


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--estado", action="store_true", help="mostrar el avance sin generar")
    ap.add_argument("--forzar", action="store_true", help="sobrescribir aunque el .docx se haya editado")
    args = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")

    cfg = cargar_config()
    dcfg = cfg.get("documento", {})
    if args.estado:
        estado(dcfg)
        return

    env = cargar_env(DOCS / ".env")
    if not env:
        avisos.append("no hay .env: la portada sale con [[marcadores]] (copia .env.example)")
    previos, caps = archivos_md()
    if not caps:
        sys.exit(f"No hay capítulos en {CAPITULOS}")
    secciones = [(True, parsear(f)) for f in previos] + [(False, parsear(f)) for f in caps]
    claves = numerar(secciones, dcfg)
    sub = Sustituto({**cfg.get("variables", {}), **env}, claves)

    doc = DocumentoAPA(dcfg.get("fuente", "Times New Roman"), int(dcfg.get("tamano", 12)),
                       dcfg.get("idioma", "es-BO"), dcfg.get("papel", "carta"), dcfg.get("justificar", False))
    portada_cfg = {**dcfg, "portada": cfg.get("portada", {})}
    for parte in cfg.get("preliminares", {}).get("orden", ["portada", "previos", "indice",
                                                            "lista_tablas", "lista_figuras"]):
        if parte == "portada":
            portada(doc, portada_cfg, sub)
        elif parte == "previos":
            for _, bloques in secciones[:len(previos)]:
                renderizar(doc, bloques, sub, dcfg)
        elif parte == "indice":
            doc.indice(int(dcfg.get("niveles_indice", 3)))
        elif parte == "lista_tablas":
            doc.lista_tablas()
        elif parte == "lista_figuras":
            doc.lista_figuras()
        else:
            errores.append(f"documento.toml: parte de preliminares desconocida '{parte}'")
    for _, bloques in secciones[len(previos):]:
        renderizar(doc, bloques, sub, dcfg)

    if sub.faltan:
        avisos.append("variables sin valor en .env: " + ", ".join(sorted(sub.faltan)))
    for r in sorted(sub.sin_resolver):
        errores.append(f"referencia sin destino: {r} (¿falta {{#clave}} en el título, 'Tabla:' o figura?)")
    for a in avisos:
        print("AVISO ", a)
    if errores:
        for e in errores:
            print("ERROR ", e)
        sys.exit(f"{len(errores)} error(es): no se generó el documento.")

    salida = DIST / f"{dcfg.get('salida', 'Documento')}.docx"
    puede_escribir(salida, args.forzar)
    DIST.mkdir(exist_ok=True)
    doc.doc.core_properties.title = sub(dcfg.get("titulo", ""))
    doc.doc.core_properties.language = dcfg.get("idioma", "es-BO")
    try:
        doc.doc.save(salida)
    except PermissionError:
        sys.exit(f"No se pudo escribir {salida.name}: ciérralo en Word y vuelve a intentar.")
    guardar_huella(salida)
    pend = sum(len(RE_PENDIENTE.findall(f.read_text(encoding="utf-8"))) for f in previos + caps)
    print(f"OK {DOCS.name}/{salida.relative_to(DOCS).as_posix()}  capítulos={len(caps)} tablas={doc.contadores['Tabla']} "
          f"figuras={doc.contadores['Figura']} pendientes={pend}")
    print("Al abrir en Word acepta 'actualizar campos' para llenar el índice y las listas.")


if __name__ == "__main__":
    main()
