"""Verifica que la máquina y el repositorio cumplen los requisitos para generar el documento.

Uso (desde la raíz del proyecto; la carpeta del template suele llamarse docs/):
    python docs/scripts/verificar_entorno.py              # solo revisa
    python docs/scripts/verificar_entorno.py --instalar   # además instala las librerías que falten

Funciona igual si el template es una carpeta de otro repositorio o un repositorio propio.

Código de salida 0 si no hay errores (los avisos no bloquean). Un agente de IA debe ejecutarlo
antes de generar o modificar el documento.
"""
import argparse
import importlib.metadata as md
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

DOCS = Path(__file__).resolve().parents[1]
PY_MIN = (3, 11)  # tomllib
CARPETAS = ["scripts", "capitulos", "recursos/logos", "recursos/figuras", "recursos/diagramas"]
ARCHIVOS = ["documento.toml", ".env.example", ".gitignore", "requirements.txt", "README.md", "LICENSE"]

resultado = {"OK": 0, "AVISO": 0, "ERROR": 0}


def informe(nivel, msg):
    resultado[nivel] += 1
    print(f"[{nivel:5}] {msg}")


def git(*args):
    r = subprocess.run(["git", *args], cwd=DOCS, capture_output=True, text=True, encoding="utf-8")
    return r.returncode, r.stdout.strip()


def version(v):
    return tuple(int(x) for x in re.findall(r"\d+", v)[:3])


def revisar_python():
    v = sys.version_info
    if v[:2] >= PY_MIN:
        informe("OK", f"Python {v.major}.{v.minor}.{v.micro} ({sys.executable})")
    else:
        informe("ERROR", f"Python {v.major}.{v.minor}: se necesita {PY_MIN[0]}.{PY_MIN[1]} o superior")


def revisar_librerias(instalar):
    req = DOCS / "requirements.txt"
    faltan = []
    for ln in req.read_text(encoding="utf-8").splitlines():
        ln = ln.split("#")[0].strip()
        if not ln:
            continue
        m = re.match(r"([A-Za-z0-9_.-]+)\s*(>=)?\s*([\d.]+)?", ln)
        nombre, minimo = m.group(1), m.group(3)
        try:
            v = md.version(nombre)
        except md.PackageNotFoundError:
            faltan.append(ln)
            informe("ERROR", f"falta la librería {nombre}")
            continue
        if minimo and version(v) < version(minimo):
            faltan.append(ln)
            informe("ERROR", f"{nombre} {v} instalada; se necesita >= {minimo}")
        else:
            informe("OK", f"{nombre} {v}")
    if faltan and instalar:
        print("    instalando:", ", ".join(faltan))
        r = subprocess.run([sys.executable, "-m", "pip", "install", "-r", str(req)])
        if r.returncode == 0:
            informe("OK", "librerías instaladas; vuelve a ejecutar la verificación")
    elif faltan:
        print(f"    instálalas con: {Path(sys.executable).name} -m pip install -r {DOCS.name}/requirements.txt")


def revisar_git():
    if not shutil.which("git"):
        informe("ERROR", "git no está instalado (https://git-scm.com)")
        return
    _, v = git("--version")
    informe("OK", v)
    code, _ = git("rev-parse", "--is-inside-work-tree")
    if code != 0:
        informe("AVISO", "la carpeta no está dentro de un repositorio git (ver PROMPT_INICIAL.md)")
        return
    _, raiz = git("rev-parse", "--show-toplevel")
    _, prefijo = git("rev-parse", "--show-prefix")
    informe("OK", f"repositorio {raiz}" + (f" (template en {prefijo.rstrip('/')}/)" if prefijo else " (template como repo propio)"))
    padre = subprocess.run(["git", "-C", str(DOCS.parent), "rev-parse", "--show-toplevel"],
                           capture_output=True, text=True)
    if not prefijo and padre.returncode == 0:
        informe("AVISO", f"{DOCS.name}/ conserva el .git del template dentro del repositorio "
                         f"{padre.stdout.strip()}: bórralo para integrarlo (PROMPT_INICIAL.md, paso 3.1)")
    if prefijo and (DOCS / ".git").exists():
        informe("ERROR", f"{DOCS.name}/.git existe dentro de otro repositorio: bórralo (ver PROMPT_INICIAL.md)")
    _, nombre = git("config", "user.name")
    if not nombre:
        informe("AVISO", "git sin user.name configurado (git config --global user.name ...)")
    # Lo que nunca debe versionarse: datos personales y documentos de salida.
    for ruta in [".env", "dist/Documento.docx", "dist/Documento.pdf", "scripts/__pycache__/x.pyc", "x.docx"]:
        code, _ = git("check-ignore", "-q", ruta)
        if code == 0:
            informe("OK", f"ignorado por git: {ruta}")
        else:
            informe("ERROR", f"git NO ignora {DOCS.name}/{ruta}: revisa {DOCS.name}/.gitignore")
    _, versionados = git("ls-files", "--full-name", ".")
    prohibidos = [f for f in versionados.splitlines()
                  if re.search(r"(^|/)\.env$|\.docx$|\.pdf$|(^|/)dist/(?!\.gitkeep)", f)]
    for f in prohibidos:
        informe("ERROR", f"versionado por error: {f} (git rm --cached {f})")
    if not prohibidos:
        informe("OK", "ningún .env, .docx, .pdf ni salida de dist/ está versionado")


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
        informe("AVISO", "no existe .env: copia .env.example y complétalo (la portada saldrá con marcadores)")
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


def revisar_opcionales():
    fuentes = Path(os.environ.get("WINDIR", "C:/Windows")) / "Fonts"
    if sys.platform == "win32":
        (informe("OK", "fuente Times New Roman instalada") if (fuentes / "times.ttf").exists()
         else informe("AVISO", "no se encontró Times New Roman"))
    word = any(Path(p).exists() for p in [
        r"C:\Program Files\Microsoft Office\root\Office16\WINWORD.EXE",
        r"C:\Program Files (x86)\Microsoft Office\root\Office16\WINWORD.EXE"])
    soffice = shutil.which("soffice") or shutil.which("libreoffice")
    if word or soffice:
        informe("OK", "editor para actualizar índices: " + ("Microsoft Word" if word else "LibreOffice"))
    else:
        informe("AVISO", "sin Word ni LibreOffice: no podrás actualizar el índice (F9) ni exportar a PDF")


def main():
    ap = argparse.ArgumentParser(description="Verifica requisitos del entorno")
    ap.add_argument("--instalar", action="store_true", help="instalar las librerías que falten")
    args = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    print(f"Verificando {DOCS}\n")
    print("== Python y librerías");     revisar_python(); revisar_librerias(args.instalar)  # noqa: E702
    print("\n== Git y privacidad");     revisar_git()  # noqa: E702
    print("\n== Estructura");           revisar_estructura()  # noqa: E702
    print("\n== Datos personales");     revisar_env()  # noqa: E702
    print("\n== Herramientas opcionales"); revisar_opcionales()  # noqa: E702
    print(f"\nResumen: {resultado['OK']} OK · {resultado['AVISO']} avisos · {resultado['ERROR']} errores")
    sys.exit(1 if resultado["ERROR"] else 0)


if __name__ == "__main__":
    main()
