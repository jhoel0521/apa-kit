"""Encuentra la carpeta del documento (la que tiene documento.toml).

Los scripts viven en `.apa/scripts/` y el documento en otra carpeta (p. ej. `tesis/`). Orden de búsqueda:
  1. `--doc <carpeta>` en la línea de comandos (se quita de sys.argv para no estorbar a argparse)
  2. variable de entorno APA_DOC
  3. la carpeta actual, si tiene documento.toml
  4. un único `*/documento.toml` dentro de la carpeta actual (o de su padre, si estás en .apa/)
  5. diseño antiguo: los scripts dentro de `<documento>/scripts/`
Si hay varios documentos y no se indica cuál, termina con un mensaje que los lista. Solo biblioteca estándar.
"""
import os
import sys
from pathlib import Path

NOMBRE = "documento.toml"
SCRIPTS = Path(__file__).resolve().parent


def _quitar_opcion_doc():
    """Lee y quita `--doc X` / `--doc=X` de sys.argv. Devuelve X o None."""
    args, valor, i = sys.argv, None, 1
    while i < len(args):
        if args[i] == "--doc" and i + 1 < len(args):
            valor = args[i + 1]
            del args[i:i + 2]
            continue
        if args[i].startswith("--doc="):
            valor = args[i].split("=", 1)[1]
            del args[i]
            continue
        i += 1
    return valor


def _hijos(base):
    try:
        return sorted(p.parent for p in base.glob(f"*/{NOMBRE}") if not p.parent.name.startswith("."))
    except OSError:
        return []


def buscar_documentos():
    """Todas las carpetas candidatas cerca del directorio actual (para los mensajes de error)."""
    cwd = Path.cwd()
    vistos = []
    for base in (cwd, cwd.parent):
        for c in ([base] if (base / NOMBRE).exists() else []) + _hijos(base):
            if c not in vistos:
                vistos.append(c)
    return vistos


def carpeta_documento():
    explicito = _quitar_opcion_doc() or os.environ.get("APA_DOC")
    if explicito:
        ruta = Path(explicito).expanduser().resolve()
        if not (ruta / NOMBRE).exists():
            sys.exit(f"No hay {NOMBRE} en {ruta}. Indica la carpeta del documento con --doc.")
        return ruta
    cwd = Path.cwd().resolve()
    if (cwd / NOMBRE).exists():
        return cwd
    for base in (cwd, cwd.parent):
        hijos = _hijos(base)
        if len(hijos) == 1:
            return hijos[0]
        if len(hijos) > 1:
            lista = "\n  ".join(str(h) for h in hijos)
            sys.exit(f"Hay varios documentos; elige uno con --doc <carpeta>:\n  {lista}")
    antiguo = SCRIPTS.parent
    if (antiguo / NOMBRE).exists():          # diseño antiguo: <documento>/scripts/
        return antiguo
    sys.exit(f"No encuentro {NOMBRE}. Ejecuta apa-init, o indica la carpeta con --doc <carpeta>.")


def carpeta_apa():
    """La carpeta `.apa/` que contiene estos scripts, o None si se ejecutan desde otro sitio."""
    return SCRIPTS.parent if SCRIPTS.parent.name == ".apa" else None
