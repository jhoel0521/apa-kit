"""Prepara un proyecto para escribir documentos APA 7 con apa-kit. Solo biblioteca estándar.

Se ejecuta desde la carpeta de la skill (`ASSETS/scripts/iniciar.py`) y escribe SIEMPRE en el proyecto del
usuario, nunca dentro de la skill. Con `python -B` no deja ni caché.

    python -B iniciar.py --listar                              # tipos de documento disponibles
    python -B iniciar.py --tipo tesis --destino tesis          # crea .apa/ y la carpeta tesis/
    python -B iniciar.py --sincronizar                         # actualiza .apa/scripts/ sin tocar el contenido
    python -B iniciar.py --migrar docs                         # convierte el diseño antiguo (docs/scripts/…)

Opciones comunes: `--proyecto <carpeta>` (por defecto, la carpeta actual).
En Windows usa `py -3`; en macOS y Linux, `python3`.
"""
import argparse
import re
import shutil
import sys
from pathlib import Path

ASSETS = Path(__file__).resolve().parent.parent          # …/skills/apa-init/assets
MOTOR = ASSETS / "scripts"
TIPOS = ASSETS / "tipos"
VERSION = (ASSETS / "VERSION").read_text(encoding="utf-8").strip() if (ASSETS / "VERSION").exists() else "0"

GITIGNORE_DOC = """# Datos personales: solo en tu disco (copia .env.example como .env)
.env

# Copia del Word original importado (tiene datos personales)
original/

# Documentos de salida: se regeneran con generar_docx.py
dist/*
!dist/.gitkeep
*.docx
*.pdf

# Archivos temporales de Word
~$*
"""
GITIGNORE_APA = """# Entorno aislado de Python y caché
.venv/
__pycache__/
*.pyc
"""
CARPETAS_DOC = ["capitulos", "recursos/logos", "recursos/figuras", "recursos/diagramas", "dist"]
IGNORAR = shutil.ignore_patterns("__pycache__", "*.pyc", ".venv")


def fallar(msg):
    sys.exit(f"ERROR: {msg}")


def salida_utf8():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError:
        pass


def descripcion(tipo):
    toml = TIPOS / tipo / "documento.toml"
    m = re.search(r'^descripcion\s*=\s*"(.*)"', toml.read_text(encoding="utf-8"), re.M) if toml.exists() else None
    return m.group(1) if m else ""


def listar_tipos():
    return sorted(p.name for p in TIPOS.iterdir() if (p / "documento.toml").exists()) if TIPOS.exists() else []


def comprobar_destino_fuera_de_skill(ruta):
    ruta = ruta.resolve()
    if ASSETS in ruta.parents or ruta == ASSETS:
        fallar(f"{ruta} está dentro de la skill. Usa --proyecto con la carpeta de trabajo del usuario.")


def copiar_motor(proyecto):
    """Reemplaza .apa/scripts/ por el motor del kit (esa carpeta es del kit, el usuario no la edita)."""
    apa = proyecto / ".apa"
    destino = apa / "scripts"
    if destino.resolve() == MOTOR.resolve():
        fallar("estás ejecutando iniciar.py desde .apa/scripts/. Ejecútalo desde la carpeta de la skill "
               "(skills/apa-init/assets/scripts/iniciar.py).")
    if destino.exists():
        shutil.rmtree(destino)
    apa.mkdir(exist_ok=True)
    shutil.copytree(MOTOR, destino, ignore=IGNORAR)
    (apa / ".gitignore").write_text(GITIGNORE_APA, encoding="utf-8")
    anterior = (apa / "VERSION").read_text(encoding="utf-8").strip() if (apa / "VERSION").exists() else None
    (apa / "VERSION").write_text(VERSION + "\n", encoding="utf-8")
    return anterior


def crear(proyecto, tipo, destino):
    if tipo not in listar_tipos():
        fallar(f"tipo desconocido '{tipo}'. Disponibles: {', '.join(listar_tipos())}")
    carpeta = (proyecto / destino).resolve()
    comprobar_destino_fuera_de_skill(carpeta)
    if (carpeta / "documento.toml").exists():
        fallar(f"{carpeta} ya tiene un documento. Elige otra carpeta o usa --sincronizar.")
    if carpeta.exists() and any(carpeta.iterdir()):
        fallar(f"{carpeta} no está vacía. Elige una carpeta nueva.")
    copiar_motor(proyecto)
    shutil.copytree(TIPOS / tipo, carpeta, dirs_exist_ok=True, ignore=IGNORAR)
    for c in CARPETAS_DOC:
        (carpeta / c).mkdir(parents=True, exist_ok=True)
    (carpeta / "dist" / ".gitkeep").touch()
    (carpeta / ".gitignore").write_text(GITIGNORE_DOC, encoding="utf-8")
    toml = carpeta / "documento.toml"
    toml.write_text(re.sub(r'^version_kit\s*=.*$', f'version_kit = "{VERSION}"',
                           toml.read_text(encoding="utf-8"), flags=re.M), encoding="utf-8")
    print(f"OK motor copiado a {proyecto / '.apa' / 'scripts'}")
    print(f"OK documento '{tipo}' creado en {carpeta}")
    print(f"   siguiente paso: python .apa/scripts/verificar_entorno.py --instalar --doc {destino}")


def sincronizar(proyecto):
    if not (proyecto / ".apa").exists():
        fallar("no hay .apa/ en este proyecto: ejecuta primero apa-init (sin --sincronizar).")
    anterior = copiar_motor(proyecto)
    print(f"OK .apa/scripts/ actualizado ({anterior or '?'} -> {VERSION}). Tus documentos no se tocaron.")


# Valores que el diseño antiguo aplicaba por defecto y que ahora cambian: se escriben explícitos para
# que un documento migrado se genere EXACTAMENTE igual que antes.
EXPLICITOS_ANTIGUOS = [("numerar_titulos", "true"), ("salto_nivel1", "true"), ('etiqueta_seccion', '"Capítulo"'),
                       ("idioma", '"es-BO"'), ("salida", '"Documento"')]


def migrar(proyecto, carpeta):
    doc = (proyecto / carpeta).resolve()
    toml = doc / "documento.toml"
    if not toml.exists():
        fallar(f"{doc} no tiene documento.toml: no parece un documento del diseño antiguo.")
    if not (doc / "scripts" / "generar_docx.py").exists():
        fallar(f"{doc} no tiene scripts/generar_docx.py: ya está migrado o no es el diseño antiguo.")
    texto = toml.read_text(encoding="utf-8")
    if not re.search(r"^\[documento\]\s*$", texto, re.M):
        fallar("documento.toml no tiene la sección [documento]; revísalo a mano.")
    nuevos = [f"{k} = {v}" for k, v in EXPLICITOS_ANTIGUOS if not re.search(rf"^{k}\s*=", texto, re.M)]
    if nuevos:
        bloque = "# Escrito por la migración: valores del diseño antiguo, para que el documento salga igual.\n" \
                 + "\n".join(nuevos) + "\n"
        texto = re.sub(r"^(\[documento\][^\n]*\n)", lambda m: m.group(1) + bloque, texto, count=1, flags=re.M)
    if not re.search(r"^\[kit\]", texto, re.M):
        texto = texto.rstrip() + f'\n\n[kit]\ntipo = "tesis"\nversion_kit = "{VERSION}"\n'
    toml.write_text(texto, encoding="utf-8")
    copiar_motor(proyecto)
    print(f"OK {carpeta}/documento.toml: escritas {len(nuevos)} clave(s) del diseño antiguo "
          f"({', '.join(k for k, _ in EXPLICITOS_ANTIGUOS if any(n.startswith(k + ' ') for n in nuevos)) or 'ninguna'})")
    print(f"OK motor nuevo en .apa/scripts/. {carpeta}/dist/ y su protección del .docx editado siguen intactos.")
    obsoletos = [n for n in ("scripts", "requirements.txt", "AGENTS.md", "CLAUDE.md", "PROMPT_INICIAL.md",
                             "GUIA_ESTUDIANTES.md", "README.md") if (doc / n).exists()]
    if obsoletos:
        print(f"AVISO de la plantilla antigua que ya no se usa en {carpeta}/: {', '.join(obsoletos)}")
        print("   Su AGENTS.md y CLAUDE.md mandan a los agentes a scripts/ (el motor viejo). Bórralos con el usuario,")
        print("   conservando LICENSE. No se borran solos.")


def main():
    salida_utf8()
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--proyecto", default=".", help="carpeta de trabajo del usuario (por defecto, la actual)")
    ap.add_argument("--tipo", help="tipo de documento (ver --listar)")
    ap.add_argument("--destino", help="carpeta del documento dentro del proyecto (p. ej. tesis)")
    ap.add_argument("--listar", action="store_true", help="mostrar los tipos de documento")
    ap.add_argument("--sincronizar", action="store_true", help="actualizar .apa/scripts/ sin tocar el contenido")
    ap.add_argument("--migrar", metavar="CARPETA", help="convertir un documento del diseño antiguo (docs/scripts/…)")
    args = ap.parse_args()

    if args.listar:
        for t in listar_tipos():
            print(f"{t:20} {descripcion(t)}")
        return
    proyecto = Path(args.proyecto).resolve()
    comprobar_destino_fuera_de_skill(proyecto)
    if args.sincronizar:
        sincronizar(proyecto)
    elif args.migrar:
        migrar(proyecto, args.migrar)
    elif args.tipo and args.destino:
        crear(proyecto, args.tipo, args.destino)
    else:
        ap.error("indica --tipo y --destino, o --sincronizar, o --migrar CARPETA, o --listar")


if __name__ == "__main__":
    main()
