"""Genera los paquetes de apa-kit en build/. Solo biblioteca estándar.

Uso:  python3 herramientas/empaquetar.py        (en Windows: py -3 herramientas/empaquetar.py)

Crea:
  build/apa-kit-cowork.zip   UNA sola skill «apa-kit» con todo adentro (motor, tipos, referencias y los
                             cinco flujos). Es la que se sube a Cowork o a claude.ai: no depende de que las
                             skills se vean entre sí ni de que .apa/ sobreviva entre sesiones.
  build/<skill>.zip          una skill suelta (apa-init, apa-guia…), para agentes que las instalan por separado.
  build/apa-kit-plugin.zip   el plugin completo (.claude-plugin/ + skills/), para /plugin.
"""
import re
import shutil
import sys
import zipfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SKILLS = REPO / "skills"
BUILD = REPO / "build"
VERSION = (SKILLS / "apa-init" / "assets" / "VERSION").read_text(encoding="utf-8").strip()
FLUJOS = ["apa-init", "apa-importar", "apa-escribir", "apa-revisar", "apa-generar", "apa-guia"]
EXCLUIR = ("__pycache__", ".venv", ".pyc", ".DS_Store")

SKILL_UNICA = """---
name: apa-kit
description: Crea, importa, escribe, revisa y genera documentos académicos en formato APA 7 (tesis, trabajo de curso, ensayo, monografía, artículo, informe) de cualquier carrera, con los capítulos en Markdown y la salida en Word. Úsala cuando el usuario diga "quiero escribir mi tesis", "formato APA", "pasa mi Word a APA", "ayúdame con mi introducción", "revisa mis citas y referencias", "genera mi Word", "cuánto llevo" o "actualiza apa-kit". No requiere descargar ninguna plantilla ni saber programar.
license: MIT
compatibility: Cualquier agente que admita SKILL.md (Claude Code, Cowork, claude.ai, Codex…). Scripts en Python 3.9 o superior; el verificador instala python-docx y Pillow.
metadata:
  version: "{version}"
  kit: apa-kit
  profile: bundle
---

# apa-kit (paquete único)

Todo apa-kit en una sola skill. `ASSETS` = la carpeta `assets/` que está junto a este SKILL.md (contiene
`scripts/` con el motor y `tipos/` con los tipos de documento). **Nunca escribas dentro de esta skill**: todo se
crea en la carpeta de trabajo del usuario.

Elige el flujo según lo que pida el usuario y **lee solo ese archivo** (cargar poco contexto es la idea):

| El usuario quiere… | Lee |
|---|---|
| Empezar un documento, elegir tipo, activar versiones con git, actualizar o migrar apa-kit | `flujos/apa-init.md` |
| Pasar su trabajo de Word o Google Docs a capítulos Markdown | `flujos/apa-importar.md` |
| Redactar o mejorar un capítulo, poner tablas, figuras o citas | `flujos/apa-escribir.md` (+ `references/sintaxis.md`) |
| Saber qué le falta: pendientes, citas sin referencia, antes de entregar | `flujos/apa-revisar.md` |
| Generar el Word, ver el avance, actualizar el índice | `flujos/apa-generar.md` |
| Reglas APA 7, sintaxis, conducta del agente, tipos de documento | `flujos/apa-guia.md` y `references/` |

Dentro de los flujos, las referencias a `skills/apa-guia/SKILL.md` significan `flujos/apa-guia.md`, y las de
`skills/apa-guia/references/…` significan `references/…`. Las reglas mínimas son siempre las mismas:
no inventar datos ni referencias, editar solo los `.md`, `recursos/` y `documento.toml`, datos personales solo
en `.env`, y no hacer commit ni push sin que el usuario lo pida.
"""


def incluir(ruta):
    return not any(parte in ruta.parts or ruta.name.endswith(parte) for parte in EXCLUIR)


def comprimir(carpeta, destino, prefijo=""):
    destino.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(destino, "w", zipfile.ZIP_DEFLATED) as z:
        for f in sorted(carpeta.rglob("*")):
            if f.is_file() and incluir(f.relative_to(carpeta)):
                z.write(f, (Path(prefijo) / f.relative_to(carpeta)).as_posix())
    return destino


def sin_frontmatter(texto):
    return re.sub(r"\A---\n.*?\n---\n", "", texto.replace("\r\n", "\n"), count=1, flags=re.S).lstrip("\n")


def armar_paquete_unico(tmp):
    raiz = tmp / "apa-kit"
    shutil.copytree(SKILLS / "apa-init" / "assets", raiz / "assets", ignore=shutil.ignore_patterns(*EXCLUIR))
    shutil.copytree(SKILLS / "apa-guia" / "references", raiz / "references")
    (raiz / "flujos").mkdir()
    for nombre in FLUJOS:
        cuerpo = sin_frontmatter((SKILLS / nombre / "SKILL.md").read_text(encoding="utf-8"))
        nota = ("> En el paquete único: `ASSETS` es `../assets/` desde este archivo; `skills/apa-guia/SKILL.md` es "
                "`flujos/apa-guia.md` y `skills/apa-guia/references/` es `references/`.\n\n")
        (raiz / "flujos" / f"{nombre}.md").write_text(nota + cuerpo, encoding="utf-8")
    (raiz / "SKILL.md").write_text(SKILL_UNICA.format(version=VERSION), encoding="utf-8")
    return raiz


def main():
    global BUILD
    sys.stdout.reconfigure(encoding="utf-8")
    if len(sys.argv) == 3 and sys.argv[1] == "--salida":
        BUILD = Path(sys.argv[2]).resolve()
    elif len(sys.argv) > 1:
        sys.exit("Uso: empaquetar.py [--salida CARPETA]")
    if BUILD.exists():
        shutil.rmtree(BUILD)
    BUILD.mkdir()
    tmp = BUILD / "_armado"
    tmp.mkdir()
    creados = [comprimir(armar_paquete_unico(tmp), BUILD / "apa-kit-cowork.zip", "apa-kit")]
    for carpeta in sorted(p for p in SKILLS.iterdir() if (p / "SKILL.md").exists()):
        creados.append(comprimir(carpeta, BUILD / f"{carpeta.name}.zip", carpeta.name))
    plugin = tmp / "plugin"
    plugin.mkdir()
    shutil.copytree(REPO / ".claude-plugin", plugin / ".claude-plugin")
    shutil.copytree(SKILLS, plugin / "skills", ignore=shutil.ignore_patterns(*EXCLUIR))
    for extra in ("LICENSE", "README.md", "CHANGELOG.md"):
        if (REPO / extra).exists():
            shutil.copy2(REPO / extra, plugin / extra)
    creados.append(comprimir(plugin, BUILD / "apa-kit-plugin.zip", "apa-kit"))
    shutil.rmtree(tmp)
    print(f"apa-kit {VERSION}: paquetes en {BUILD}")
    for z in creados:
        print(f"  {z.name:24} {z.stat().st_size // 1024:>5} KB")


if __name__ == "__main__":
    main()
