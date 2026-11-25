"""Usa el entorno aislado `.apa/.venv/` si existe.

Cada script de apa-kit hace `import _entorno` en su primera línea. Si hay un `.venv/` y el
script no corre ya dentro de él, se relanza con ese Python. Así funciona igual en Windows, macOS y
Linux, incluso cuando el sistema no deja instalar librerías globalmente (PEP 668: Debian, Ubuntu,
Homebrew). Solo usa la biblioteca estándar.

Para saltarlo: variable de entorno APA_SIN_VENV=1.
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


def venv_listo():
    """True si el .venv tiene su Python y python-docx instalado. Un .venv a medio crear (por ejemplo, si
    faltaba python3-venv en Debian/Ubuntu) no cuenta: relanzar ahí dejaría al usuario atrapado sin librerías."""
    if python_del_venv() is None:
        return False
    paquetes = [VENV / "Lib" / "site-packages"] + sorted(VENV.glob("lib/python*/site-packages"))
    return any((p / "docx").is_dir() for p in paquetes)


def dentro_del_venv():
    return Path(sys.prefix).resolve() == VENV.resolve()


def relanzar():
    if dentro_del_venv() or os.environ.get("APA_SIN_VENV") or not venv_listo():
        return
    py = python_del_venv()
    sys.exit(subprocess.run([str(py), *sys.argv]).returncode)


relanzar()
