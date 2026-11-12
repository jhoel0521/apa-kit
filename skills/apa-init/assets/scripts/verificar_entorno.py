"""Verifica que la máquina y el documento cumplen los requisitos para generar el .docx.

Uso (desde la carpeta del proyecto; en Windows `py -3`, en macOS/Linux `python3`):
    python .apa/scripts/verificar_entorno.py              # solo revisa
    python .apa/scripts/verificar_entorno.py --instalar   # además instala las librerías que falten
    python .apa/scripts/verificar_entorno.py --doc tesis  # si hay varios documentos

Funciona en Windows, macOS y Linux, con o sin git. Si el sistema no deja instalar librerías
globalmente (PEP 668), crea un entorno aislado en `.apa/.venv/` que los demás scripts usan solos.
Ejecútalo desde `.apa/scripts/`, nunca desde la carpeta de la skill (no debe escribir ahí).

Código de salida 0 si no hay errores (los avisos no bloquean). Un agente de IA debe ejecutarlo
antes de generar o modificar el documento.
"""
import _entorno  # noqa: F401  (usa .venv/ si existe)

import argparse
import importlib.metadata as md
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _raiz import SCRIPTS, carpeta_apa, carpeta_documento  # noqa: E402

DOCS = carpeta_documento()
PY_MIN = (3, 9)  # Python de fábrica de macOS; tomli reemplaza a tomllib por debajo de 3.11
CARPETAS = ["capitulos", "recursos/logos", "recursos/figuras", "recursos/diagramas"]
ARCHIVOS = ["documento.toml", ".env.example", ".gitignore"]
# git es opcional: quien no programa puede trabajar sin historial.

resultado = {"OK": 0, "AVISO": 0, "ERROR": 0}


def informe(nivel, msg):
    resultado[nivel] += 1
    print(f"[{nivel:5}] {msg}")


def git(*args):
    r = subprocess.run(["git", *args], cwd=DOCS, capture_output=True, text=True, encoding="utf-8")
    return r.returncode, r.stdout.strip()


def version(v):
    return tuple(int(x) for x in re.findall(r"\d+", v)[:3])


def como_instalar_python():
    if sys.platform == "win32":
        return "winget install Python.Python.3.13  (o https://www.python.org/downloads/ marcando «Add python.exe to PATH»)"
    if sys.platform == "darwin":
        return "brew install python  (o https://www.python.org/downloads/macos/)"
    return "sudo apt install python3 python3-venv python3-pip  (Debian/Ubuntu) · sudo dnf install python3  (Fedora)"


# ================================================================ Python y librerías
def requisitos():
    """[(linea, nombre, mínimo)] de requirements.txt aplicables a este Python (soporta ; python_version)."""
    res = []
    for ln in (SCRIPTS / "requirements.txt").read_text(encoding="utf-8").splitlines():
        ln = ln.split("#")[0].strip()
        if not ln:
            continue
        ln, _, marca = ln.partition(";")
        m = re.search(r'python_version\s*(<|>=)\s*"([\d.]+)"', marca)
        if m:
            actual, umbral = sys.version_info[:2], version(m.group(2))[:2]
            if (actual < umbral) != (m.group(1) == "<"):
                continue  # el requisito no aplica a esta versión de Python
        m = re.match(r"\s*([A-Za-z0-9_.-]+)\s*(>=)?\s*([\d.]+)?", ln)
        res.append((ln.strip(), m.group(1), m.group(3)))
    return res


def faltantes():
    """Requisitos sin instalar o demasiado viejos: [(linea, nombre, mensaje, version_o_None)]."""
    malos = []
    for linea, nombre, minimo in requisitos():
        try:
            v = md.version(nombre)
        except md.PackageNotFoundError:
            malos.append((linea, nombre, f"falta la librería {nombre}", None))
            continue
        if minimo and version(v) < version(minimo):
            malos.append((linea, nombre, f"{nombre} {v} instalada; se necesita >= {minimo}", v))
    return malos


def instalar_librerias():
    """Instala con pip; si el sistema lo rechaza (PEP 668), usa un entorno aislado .venv/.
    Devuelve 'pip', 'venv' o None."""
    req = str(SCRIPTS / "requirements.txt")
    if not os.environ.get("APA_FORZAR_VENV"):  # variable solo para probar el camino .venv
        r = subprocess.run([sys.executable, "-m", "pip", "install", "-r", req], capture_output=True,
                           text=True, encoding="utf-8", errors="replace")
        if r.returncode == 0:
            return "pip"
    print("    pip no pudo instalar en el sistema (normal en Debian/Ubuntu/Homebrew); "
          "creo un entorno aislado en .apa/.venv/ ...")
    v = subprocess.run([sys.executable, "-m", "venv", str(_entorno.VENV)], capture_output=True,
                       text=True, encoding="utf-8", errors="replace")
    py = _entorno.python_del_venv()
    if v.returncode != 0 or py is None:
        print("    no pude crear .venv/:", (v.stderr or v.stdout).strip().splitlines()[-1:] or "")
        print("    instala el soporte de entornos virtuales:", como_instalar_python())
        return None
    r = subprocess.run([str(py), "-m", "pip", "install", "-r", req], capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    if r.returncode != 0:
        print("    falló pip en .venv/:", "\n".join(r.stderr.strip().splitlines()[-3:]))
        return None
    return "venv"


def revisar_python():
    v = sys.version_info
    if v[:2] >= PY_MIN:
        informe("OK", f"Python {v.major}.{v.minor}.{v.micro} ({sys.executable})")
    else:
        informe("ERROR", f"Python {v.major}.{v.minor}: se necesita {PY_MIN[0]}.{PY_MIN[1]} o superior. "
                         f"Instálalo con: {como_instalar_python()}")
    for _, nombre, minimo in requisitos():
        try:
            informe("OK", f"{nombre} {md.version(nombre)}")
        except md.PackageNotFoundError:
            informe("ERROR", f"falta la librería {nombre} (ejecuta con --instalar)")


# ================================================================ Git y privacidad
def revisar_git():
    if not shutil.which("git"):
        informe("AVISO", "git no está instalado: es opcional, sirve para guardar versiones "
                         "(https://git-scm.com · Windows: winget install Git.Git · Mac: brew install git)")
        return
    _, v = git("--version")
    informe("OK", v)
    code, _ = git("rev-parse", "--is-inside-work-tree")
    if code != 0:
        informe("AVISO", "sin historial de versiones (git). Es opcional; para activarlo: git init "
                         "(apa-init puede activarlo)")
        return
    _, raiz = git("rev-parse", "--show-toplevel")
    _, prefijo = git("rev-parse", "--show-prefix")
    informe("OK", f"repositorio {raiz}")
    _, nombre = git("config", "user.name")
    if not nombre:
        informe("AVISO", "git sin user.name configurado (git config --global user.name ...)")
    # Lo que nunca debe versionarse: datos personales, copias del Word original y documentos de salida.
    for ruta in [".env", "original/x.docx", "dist/Documento.docx", "dist/Documento.pdf", "x.docx"]:
        code, _ = git("check-ignore", "-q", ruta)
        if code == 0:
            informe("OK", f"ignorado por git: {ruta}")
        else:
            informe("ERROR", f"git NO ignora {DOCS.name}/{ruta}: revisa {DOCS.name}/.gitignore")
    apa = carpeta_apa()
    if apa and subprocess.run(["git", "check-ignore", "-q", ".venv/pyvenv.cfg"], cwd=apa).returncode != 0:
        informe("ERROR", ".apa/.gitignore no ignora .venv/: revisa .apa/.gitignore")
    _, versionados = git("ls-files", "--full-name", ".")
    prohibidos = [f for f in versionados.splitlines()
                  if re.search(r"(^|/)\.env$|\.docx$|\.pdf$|(^|/)(dist|original|\.venv)/(?!\.gitkeep)", f)]
    for f in prohibidos:
        informe("ERROR", f"versionado por error: {f} (git rm --cached {f})")
    if not prohibidos:
        informe("OK", "ningún .env, .docx, .pdf ni salida de dist/ está versionado")


# ================================================================ estructura, datos, opcionales
def revisar_estructura():
    for c in CARPETAS:
        (informe("OK", f"carpeta {DOCS.name}/{c}") if (DOCS / c).is_dir()
         else informe("ERROR", f"falta la carpeta {DOCS.name}/{c}"))
    for a in ARCHIVOS:
        (informe("OK", f"archivo {DOCS.name}/{a}") if (DOCS / a).is_file()
         else informe("ERROR", f"falta {DOCS.name}/{a}"))
    caps = sorted((DOCS / "capitulos").glob("*.md"))
    (informe("OK", f"{len(caps)} archivo(s) .md en capitulos/") if caps
     else informe("ERROR", f"no hay capítulos en {DOCS.name}/capitulos/"))


def revisar_env():
    ejemplo, env = DOCS / ".env.example", DOCS / ".env"
    if not env.exists():
        env.write_text(ejemplo.read_text(encoding="utf-8"), encoding="utf-8")
        informe("AVISO", f"creé {env}: ábrelo con un editor de texto (Bloc de notas, TextEdit en modo "
                         "texto, gedit…) y completa tus datos de portada. Este archivo nunca se comparte")
        return
    claves = lambda p: {ln.split("=", 1)[0].strip(): ln.split("=", 1)[1].strip()  # noqa: E731
                        for ln in p.read_text(encoding="utf-8").splitlines()
                        if "=" in ln and not ln.lstrip().startswith("#")}
    valores = claves(env)
    vacias = [k for k in claves(ejemplo) if not valores.get(k)]
    if vacias:
        informe("AVISO", f".env sin valor en: {', '.join(vacias)}")
    else:
        informe("OK", ".env completo")


def editor_de_oficina():
    """('Microsoft Word' | 'LibreOffice' | None)."""
    if sys.platform == "win32":
        bases = [os.environ.get("ProgramFiles", r"C:\Program Files"),
                 os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)")]
        if any((Path(b) / "Microsoft Office" / "root" / "Office16" / "WINWORD.EXE").exists() for b in bases):
            return "Microsoft Word"
    elif sys.platform == "darwin":
        if Path("/Applications/Microsoft Word.app").exists():
            return "Microsoft Word"
        if Path("/Applications/LibreOffice.app").exists():
            return "LibreOffice"
    if shutil.which("soffice") or shutil.which("libreoffice"):
        return "LibreOffice"
    return None


def revisar_opcionales():
    if sys.platform == "win32":
        ok = (Path(os.environ.get("WINDIR", "C:/Windows")) / "Fonts" / "times.ttf").exists()
    elif sys.platform == "darwin":
        ok = any(Path(p).exists() for p in ("/System/Library/Fonts/Supplemental/Times New Roman.ttf",
                                             "/Library/Fonts/Times New Roman.ttf"))
    else:
        ok = None  # en Linux, LibreOffice sustituye la fuente (Liberation Serif); no es un problema
    if ok is True:
        informe("OK", "fuente Times New Roman instalada")
    elif ok is False:
        informe("AVISO", "no se encontró Times New Roman: el documento la pedirá igual, pero se verá con "
                         "otra fuente hasta instalarla (o cambia `fuente` en documento.toml)")
    editor = editor_de_oficina()
    if editor:
        informe("OK", f"editor para actualizar índices: {editor}")
    else:
        informe("AVISO", "sin Word ni LibreOffice: no podrás actualizar el índice ni exportar a PDF "
                         "(LibreOffice es gratis: https://www.libreoffice.org)")


def main():
    ap = argparse.ArgumentParser(description="Verifica requisitos del entorno")
    ap.add_argument("--instalar", action="store_true", help="instalar las librerías que falten")
    args = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")

    if args.instalar and sys.version_info[:2] >= PY_MIN and faltantes():
        print("Instalando librerías:", ", ".join(m[1] for m in faltantes()))
        modo = instalar_librerias()
        if modo == "venv":
            print("    listo: los scripts usarán .venv/ automáticamente\n")
            _entorno.relanzar()  # vuelve a ejecutar esta verificación dentro de .venv/
        elif modo == "pip":
            # pip puede instalar en una carpeta de usuario que este Python aún no conoce: vuelve a
            # ejecutar la verificación en un proceso nuevo (una sola vez).
            if not os.environ.get("APA_REINTENTO"):
                print("    listo; vuelvo a verificar\n")
                sys.exit(subprocess.run([sys.executable, *sys.argv],
                                        env={**os.environ, "APA_REINTENTO": "1"}).returncode)
        else:
            print()

    if carpeta_apa() is None and SCRIPTS.parent != DOCS:
        informe("AVISO", "estos scripts no están en .apa/scripts/: ejecútalos desde allí (apa-init los copia) "
                         "para no escribir dentro de la skill")
    print(f"Verificando {DOCS}\n")
    print("== Python y librerías")
    revisar_python()
    print("\n== Git y privacidad")
    revisar_git()
    print("\n== Estructura")
    revisar_estructura()
    print("\n== Datos personales")
    revisar_env()
    print("\n== Herramientas opcionales")
    revisar_opcionales()
    print(f"\nResumen: {resultado['OK']} OK · {resultado['AVISO']} avisos · {resultado['ERROR']} errores")
    sys.exit(1 if resultado["ERROR"] else 0)


if __name__ == "__main__":
    main()
