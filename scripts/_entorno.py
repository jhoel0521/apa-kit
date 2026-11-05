"""Usa el entorno aislado `.venv/` de la plantilla si existe.

Cada script de la plantilla hace `import _entorno` en su primera línea. Si hay un `.venv/` y el
script no corre ya dentro de él, se relanza con ese Python. Así funciona igual en Windows, macOS y
Linux, incluso cuando el sistema no deja instalar librerías globalmente (PEP 668: Debian, Ubuntu,
Homebrew). Solo usa la biblioteca estándar.

Para saltarlo: variable de entorno PLANTILLA_SIN_VENV=1.
"""
import os
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
VENV = RAIZ / ".venv"


def python_del_venv():
    """Ruta del Python del .venv (Windows: Scripts/python.exe; Mac/Linux: bin/python3), o None."""
    for rel in ("Scripts/python.exe", "bin/python3", "bin/python"):
        ruta = VENV / rel
        if ruta.exists():
            return ruta
    return None


def dentro_del_venv():
    return Path(sys.prefix).resolve() == VENV.resolve()


def relanzar():
    py = python_del_venv()
    if py is None or dentro_del_venv() or os.environ.get("PLANTILLA_SIN_VENV"):
        return
    sys.exit(subprocess.run([str(py), *sys.argv]).returncode)


relanzar()
