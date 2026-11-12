---
name: apa-init
description: Prepara un proyecto para escribir un documento con formato APA 7 (tesis, trabajo, informe, monografía o cualquier texto académico, de cualquier carrera) y lo versiona con git si el usuario quiere. Crea la carpeta .apa/ con los scripts y la carpeta del documento con sus capítulos en Markdown. Úsala cuando el usuario diga "quiero escribir mi tesis", "empezar un documento en formato APA", "armar mi trabajo en APA 7", "configurar apa-kit" o "actualizar apa-kit". No requiere descargar ninguna plantilla.
license: MIT
compatibility: Cualquier agente que admita SKILL.md (Claude Code, Cowork, Codex…). Scripts en Python 3.9 o superior; el verificador instala python-docx y Pillow.
metadata:
  version: "0.2.0"
  kit: apa-kit
  profile: core
---

# apa-init

Crea o sincroniza `.apa/` en la carpeta de trabajo del usuario y le crea su documento. Todo lo que apa-kit
necesita queda en el proyecto, así cualquier agente puede continuar el trabajo después.

`ASSETS` = la carpeta `assets/` junto a este SKILL.md. **No escribas nunca dentro de la skill**: todo lo que
se crea va en la carpeta de trabajo del usuario (`--proyecto`, por defecto la carpeta actual).

**Comando de Python:** usa el que funcione en el equipo: `py -3` (Windows), `python3` (macOS y Linux) o
`python`. Donde abajo diga `python`, es ese. Si no sabes el sistema, pregúntalo. Con quien no programa:
habla en lenguaje simple y explica en una frase qué hace cada comando antes de ejecutarlo.

Antes de empezar, lee `skills/apa-guia/SKILL.md` (reglas y lenguaje); si no la tienes cargada, pídela.

## 1. Detectar
Mira la carpeta de trabajo y decide el modo:
- **No hay `.apa/`** → *crear* (paso 2).
- **Hay `.apa/`** y el usuario quiere actualizar → *sincronizar* (paso 5).
- **Hay un `docs/` con `scripts/generar_docx.py` y `documento.toml`** (la plantilla antigua `v0.1.0`) →
  *migrar* (paso 6).
- Si ya hay un `.docx` del usuario con su trabajo avanzado → después de crear, ofrece **apa-importar**.
- ¿Hay `.git` en la carpeta o en un padre? Anótalo para el paso 4.

## 2. Preguntar (una cosa por vez, sin inventar)
1. **Qué documento es** y su tipo: ejecuta `python ASSETS/scripts/iniciar.py --listar` y propón el más cercano
   (`tesis`, `libre`…). Si la institución dio un índice, usa `libre` y arma los capítulos con ese índice.
2. **Nombre de la carpeta** del documento (p. ej. `tesis`). Puede haber varios en el mismo proyecto.
3. Carrera o área (solo para el tono; no cambia el formato), título provisional, papel (carta/A4/oficio),
   si usa «Tabla/Figura» o «Cuadro/Gráfico», y si tiene logo (`recursos/logos/logo.png`).
No pidas datos personales en el chat para escribirlos en archivos versionados: van solo en `.env` (paso 3).

## 3. Crear
```bash
python -B ASSETS/scripts/iniciar.py --tipo <tipo> --destino <carpeta>
python .apa/scripts/verificar_entorno.py --instalar --doc <carpeta>
```
Muestra la salida de cada comando. `verificar_entorno.py` instala `python-docx` y `Pillow` y crea
`<carpeta>/.env` desde `.env.example`. Si el sistema impide instalar librerías
(`externally-managed-environment`), el propio verificador crea `.apa/.venv/` y los demás scripts lo usan
solos. Repite hasta 0 `[ERROR]`; explica los `[AVISO]` en una frase. No instales software del sistema sin permiso.

Luego completa `<carpeta>/.env` **con el usuario**, valor por valor, y ajusta `<carpeta>/documento.toml`
(título, `salida`, papel, etiquetas). Datos personales solo en `.env`.

## 3.1 Reglas para los agentes del proyecto (pregunta antes)
Pregunta al usuario si quiere dejar escrito, en el `AGENTS.md` o `CLAUDE.md` de su carpeta de trabajo, cómo debe
comportarse cualquier agente futuro con su documento. Si acepta y el archivo **no contiene ya** la marca
`apa-kit`, **añade al final** (sin tocar el resto; si el archivo no existe, créalo):
```markdown
## Documento APA 7 (apa-kit)
- Los documentos viven en <carpeta del documento>/capitulos/*.md; el motor está en .apa/scripts/ (no se edita).
- Edita solo los .md, recursos/ y documento.toml. Nunca un .docx. No inventes datos, citas ni referencias.
- Datos personales solo en <carpeta del documento>/.env; en los .md usa {{CLAVE}}.
- Para trabajar usa las skills apa-escribir, apa-revisar y apa-generar (o lee skills/apa-guia).
- Sin commit ni push sin que el usuario lo pida.
```

## 4. Versiones con git (recomendado, opcional)
Explica en una frase: «git guarda cada versión de tu documento, así puedes volver atrás». Si el usuario
quiere y git no está instalado, pide permiso antes de instalarlo. Si no hay repositorio: `git init` en la
carpeta de trabajo. Comprueba que `.env`, `original/` y `dist/` quedan ignorados (el verificador lo hace).
No hagas commit ni push sin que lo pida. Si lo sube a internet, que sea un repositorio **privado**.
Sin git: sugiere copiar la carpeta con la fecha antes de cada revisión con el tutor.

## 5. Sincronizar
```bash
python -B ASSETS/scripts/iniciar.py --sincronizar
```
Reemplaza `.apa/scripts/` por la versión de la skill. **No toca** capítulos, `.env` ni `documento.toml`.
Si hay cambios en `git status` bajo `.apa/`, muéstralos antes de que el usuario haga commit.

## 6. Migrar la plantilla antigua
```bash
python -B ASSETS/scripts/iniciar.py --migrar docs
```
Copia el motor a `.apa/scripts/` y escribe en `docs/documento.toml` las opciones que antes eran
implícitas (`numerar_titulos`, `salto_nivel1`, `idioma`, `salida`), para que el documento salga **igual que
antes**. No toca `dist/`, así que la protección del Word editado a mano sigue vigente. Después, genera con
**apa-generar** y compara. El script lista lo obsoleto de la plantilla antigua (`docs/scripts/`,
`requirements.txt`, y sobre todo el `AGENTS.md` y `CLAUDE.md` viejos, que mandan a los agentes al motor
anterior). Pregunta al usuario y bórralos con su permiso, conservando `LICENSE`; no los borres solos.

## 7. Cierre
Resume: tipo y carpeta creados, si hay git, qué falta en `.env`, y el siguiente paso:
- ¿Ya tiene su trabajo en Word? → **apa-importar**.
- ¿Empieza de cero? → **apa-escribir**, un capítulo por vez.
- Para ver el avance o generar el Word → **apa-generar**.
