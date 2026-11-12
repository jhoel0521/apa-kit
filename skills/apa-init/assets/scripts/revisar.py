"""Revisa un documento apa-kit y lista CANDIDATOS a confirmar (no errores).

Uso (desde la carpeta del proyecto; en Windows `py -3`, en macOS/Linux `python3`):
    python .apa/scripts/revisar.py                  # informe en pantalla
    python .apa/scripts/revisar.py --doc tesis      # si hay varios documentos
    python .apa/scripts/revisar.py --estricto       # termina con código 1 si queda algo por resolver

Qué busca en <documento>/capitulos/*.md:
  1. Marcas sin resolver: [[pendiente…]], [[verificar…]], [[revisar…]] y textos de plantilla [[…]].
  2. Citas (Autor, año) / Autor (año) que no tienen su referencia bajo «# Referencias».
  3. Referencias que no se citan en ningún capítulo.

Es una ayuda: puede equivocarse (autores corporativos, citas secundarias, años con letra). El agente debe
confirmar cada candidato con el autor. Por defecto siempre termina con código 0.
"""
import _entorno  # noqa: F401  (usa .venv/ si existe)

import argparse
import re
import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _raiz import carpeta_documento  # noqa: E402

DOCS = carpeta_documento()

NOMBRE = r"[A-ZÁÉÍÓÚÑÜ][\wÁÉÍÓÚÑÜáéíóúñü'’-]+"
RE_MARCA = re.compile(r"\[\[\s*([^\]]*?)\s*\]\]")
RE_PARENTESIS = re.compile(r"\(([^()]*?\b(?:1[5-9]\d\d|20\d\d)[a-z]?\b[^()]*?)\)")
RE_AUTOR_ANIO = re.compile(rf"^(?:cf\.|v[eé]ase|ver|e\.g\.,|p\. ej\.,)?\s*({NOMBRE}[^,;()]*?),\s*((?:1[5-9]\d\d|20\d\d)[a-z]?)\b")
RE_NARRATIVA = re.compile(rf"\b({NOMBRE})(?:\s+(?:y|e|&)\s+{NOMBRE}|\s+et al\.)?\s+\(((?:1[5-9]\d\d|20\d\d)[a-z]?)[,)]")
RE_REFERENCIA = re.compile(r"\(((?:1[5-9]\d\d|20\d\d)[a-z]?|s\. ?f\.|en prensa)[^)]*\)")
RE_COMENTARIO = re.compile(r"<!--.*?-->", re.S)


def plano(txt):
    return "".join(c for c in unicodedata.normalize("NFD", txt.casefold()) if unicodedata.category(c) != "Mn")


VISIBLE = {}  # clave sin acentos -> cómo lo escribió el autor (para mostrarlo bien)


def clave(autor, anio):
    """(primer apellido o palabra del autor sin acentos, año)."""
    primera = re.match(rf"\s*({NOMBRE})", autor)
    texto = primera.group(1) if primera else autor.strip()
    VISIBLE.setdefault(plano(texto), texto)
    return (plano(texto), anio)


def leer(ruta):
    """Líneas del capítulo con su número, sin comentarios HTML ni bloques de código."""
    texto = ruta.read_text(encoding="utf-8")
    texto = RE_COMENTARIO.sub(lambda m: "\n" * m.group(0).count("\n"), texto)
    salida, en_codigo = [], False
    for n, ln in enumerate(texto.splitlines(), 1):
        if ln.strip().startswith("```"):
            en_codigo = not en_codigo
            continue
        if not en_codigo:
            salida.append((n, ln))
    return salida


def analizar(capitulos):
    marcas, citas, referencias = [], {}, {}
    for ruta in capitulos:
        en_refs = False
        for n, ln in leer(ruta):
            titulo = re.match(r"^(#{1,4})\s+(.+?)\s*(\{[^}]*\})?\s*$", ln)
            if titulo and len(titulo.group(1)) == 1:
                en_refs = plano(titulo.group(2)).startswith(("referencias", "bibliografia"))
                continue
            for m in RE_MARCA.finditer(ln):
                texto = m.group(1)
                tipo = next((t for t in ("pendiente", "verificar", "revisar") if plano(texto).startswith(t)), "plantilla")
                marcas.append((tipo, f"{ruta.name}:{n}", texto))
            limpio = RE_MARCA.sub("", ln)
            if en_refs:
                s = limpio.strip()
                if s and not s.startswith("#") and RE_REFERENCIA.search(s):
                    m = RE_REFERENCIA.search(s)
                    referencias[clave(s, m.group(1))] = f"{ruta.name}:{n}"
                continue
            for grupo in RE_PARENTESIS.finditer(limpio):
                for parte in grupo.group(1).split(";"):
                    m = RE_AUTOR_ANIO.match(parte.strip())
                    if m:
                        citas.setdefault(clave(m.group(1), m.group(2)), f"{ruta.name}:{n}")
            for m in RE_NARRATIVA.finditer(limpio):
                citas.setdefault(clave(m.group(1), m.group(2)), f"{ruta.name}:{n}")
    return marcas, citas, referencias


def coincide(k, otros):
    """Año con letra (2020a) coincide con el año simple; el autor se compara sin acentos."""
    autor, anio = k
    base = re.sub(r"[a-z]$", "", anio)
    return any(a == autor and re.sub(r"[a-z]$", "", y) == base for a, y in otros)


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--estricto", action="store_true", help="código 1 si queda algo por resolver")
    args = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")

    capitulos = sorted((DOCS / "capitulos").glob("*.md"))
    if not capitulos:
        sys.exit(f"No hay capítulos en {DOCS / 'capitulos'}")
    marcas, citas, referencias = analizar(capitulos)
    sin_ref = sorted((k, d) for k, d in citas.items() if not coincide(k, referencias))
    sin_cita = sorted((k, d) for k, d in referencias.items() if not coincide(k, citas))

    print(f"Revisión de {DOCS.name}/  ({len(capitulos)} archivos)  —  son CANDIDATOS: confírmalos con el autor\n")
    etiquetas = {"pendiente": "Pendientes", "verificar": "Por verificar (referencias o datos sin comprobar)",
                 "revisar": "Por revisar (el importador no pudo convertirlo)",
                 "plantilla": "Texto de plantilla sin reemplazar"}
    for tipo, titulo in etiquetas.items():
        lista = [m for m in marcas if m[0] == tipo]
        print(f"== {titulo}: {len(lista)}")
        for _, donde, texto in lista[:15]:
            print(f"   {donde}  [[{texto[:70]}]]")
        if len(lista) > 15:
            print(f"   … y {len(lista) - 15} más")
    print(f"\n== Citas sin referencia: {len(sin_ref)}")
    for (autor, anio), donde in sin_ref:
        print(f"   {donde}  {VISIBLE.get(autor, autor)} ({anio})  -> no está bajo «# Referencias»")
    print(f"\n== Referencias que no se citan: {len(sin_cita)}")
    for (autor, anio), donde in sin_cita:
        print(f"   {donde}  {VISIBLE.get(autor, autor)} ({anio})  -> ningún capítulo la cita")
    print(f"\nResumen: {len(marcas)} marcas · {len(sin_ref)} citas sin referencia · {len(sin_cita)} referencias sin cita")
    pendientes = [m for m in marcas if m[0] != "plantilla"]
    sys.exit(1 if args.estricto and (pendientes or sin_ref or sin_cita) else 0)


if __name__ == "__main__":
    main()
