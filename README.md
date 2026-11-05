# Template de documentación académica en APA 7

Escribes los capítulos en Markdown, un script los convierte en un `.docx` con formato APA 7 y Git
guarda el historial de cada cambio. Los datos personales y los documentos finales **no** se
versionan.

Es un **template**: se clona dentro de la carpeta `docs/` de cualquier proyecto (una app, un
sistema, una tesis) y deja de depender de este repositorio.

- Sitio: https://jhoel0521.github.io/plantilla-docs-apa/
- Repositorio: https://github.com/jhoel0521/plantilla-docs-apa
- Funciona en **Windows, macOS y Linux** (probado en CI con Python 3.9 y 3.13). No hay ejecutables
  propios: todo es Python legible. iPhone y iPad no pueden usarla (no instalan Python).

## Inicio rápido

| Quiero… | Hago… |
|---|---|
| Integrarlo en un proyecto con un agente de IA | Copio el **Prompt A** de [`PROMPT_INICIAL.md`](PROMPT_INICIAL.md) en el agente, abierto en la raíz del proyecto |
| Usarlo con mi tesis en Word, sin programar | Sigo [`GUIA_ESTUDIANTES.md`](GUIA_ESTUDIANTES.md) o pego el **Prompt B** en mi asistente |
| Integrarlo a mano | `cd mi-proyecto` → `git clone https://github.com/jhoel0521/plantilla-docs-apa.git docs` → si el proyecto tiene git: `rm -rf docs/.git`, `git add docs`, commit. Detalle en `PROMPT_INICIAL.md` |
| Importar un Word existente | `python3 docs/scripts/importar_docx.py "Mi tesis.docx"` |
| Generar el documento | `python3 docs/scripts/generar_docx.py` |
| Ver el avance | `python3 docs/scripts/generar_docx.py --estado` |

Los comandos suponen que el template quedó en `docs/` y se ejecutan desde la raíz del proyecto.
Si lo clonaste con otro nombre, cambia `docs/` por ese nombre. Dentro de este mismo repositorio
usa `python3 scripts/...`. **En Windows escribe `py -3` donde diga `python3`.**

## 1. Requisitos del sistema

| Requisito | Versión mínima | Para qué | Cómo comprobarlo |
|---|---|---|---|
| Python | 3.9 | ejecutar `scripts/` | `python3 --version` (Windows: `py -3 --version`) |
| python-docx | 1.1.0 | escribir el `.docx` APA | lo instala el verificador |
| Pillow | 10.1 | insertar imágenes y generar diagramas | lo instala el verificador |
| tomli | 2.0 | solo en Python 3.9 y 3.10 | lo instala el verificador |
| Git | 2.x | historial y control de qué se versiona | `git --version` |
| Microsoft Word o LibreOffice | cualquiera | actualizar índices (F9) y exportar a PDF | opcional |
| Fuente Times New Roman | — | fuente APA configurada por defecto | opcional (`fuente` en `documento.toml`) |

Todo se comprueba con un solo comando, que además instala las librerías que falten:

```
python3 docs/scripts/verificar_entorno.py --instalar      # Windows: py -3 ...
```

El script revisa Python, las librerías de `requirements.txt`, Git, que `.env`, `dist/`, `*.docx` y
`*.pdf` estén ignorados y no versionados, la estructura de carpetas, si `.env` está completo y las
herramientas opcionales. También detecta si quedó un `.git` del template dentro de otro
repositorio. Termina con código 1 si hay errores.

Si el sistema no deja instalar librerías globalmente (Debian, Ubuntu y Homebrew lo bloquean con el
error `externally-managed-environment`), el verificador crea un entorno aislado en `.venv/` y los
demás scripts lo usan automáticamente.

## 2. Estructura

```
docs/                        (la raíz de este template, clonada en tu proyecto)
├─ README.md                 este manual
├─ PROMPT_INICIAL.md         prompts A (proyecto de software) y B (estudiante que no programa)
├─ GUIA_ESTUDIANTES.md       paso a paso sin programar, para Windows, macOS y Linux
├─ AGENTS.md  CLAUDE.md      reglas para agentes de IA al escribir el documento
├─ LICENSE                   MIT: conserva el aviso de copyright
├─ scripts/
│  ├─ verificar_entorno.py   requisitos del sistema y privacidad del repo
│  ├─ generar_docx.py        capitulos/*.md → dist/<salida>.docx  (--estado, --forzar)
│  ├─ importar_docx.py       tu Word existente → capitulos/*.md (no modifica el original)
│  ├─ prueba_humo.py         comprueba que todo funciona en tu equipo (importa y genera un ejemplo)
│  ├─ _entorno.py            usa .venv/ si existe
│  ├─ apa.py                 estilos APA 7 (solo formato, sin contenido)
│  └─ diagramas.py           diagramas como código → recursos/diagramas/*.png
├─ recursos/
│  ├─ logos/                 logo de la universidad (logo.png)
│  ├─ figuras/               capturas, fotos, imágenes externas
│  └─ diagramas/             PNG generados por scripts/diagramas.py
├─ capitulos/                el contenido, en orden alfabético de archivo
│  ├─ 00-*.md                preliminares (dedicatoria, resumen…): sin número, fuera del índice
│  ├─ 01-…md a 89-…md        capítulos numerados automáticamente
│  └─ 90-referencias.md, 95-anexos.md
├─ original/                 copia de tu Word importado y su portada (IGNORADO por git)
├─ dist/                     documentos de salida (IGNORADO por git)
├─ .venv/                    entorno aislado de Python, si hizo falta (IGNORADO)
├─ __pycache__/              caché de Python (IGNORADO)
├─ documento.toml            título, papel, fuente, portada, orden de preliminares
├─ .env.example              plantilla de datos personales (versionada, vacía)
├─ .env                      tus datos reales (IGNORADO)
├─ requirements.txt
└─ .gitignore                funciona aunque el proyecto tenga su propio .gitignore
```

## 3. Uso

```
python3 docs/scripts/verificar_entorno.py     # antes de trabajar; crea docs/.env: complétalo
python3 docs/scripts/importar_docx.py "Mi tesis.docx"   # solo si ya tienes tu documento en Word
python3 docs/scripts/diagramas.py             # si cambiaste diagramas
python3 docs/scripts/generar_docx.py          # genera docs/dist/Tesis.docx
python3 docs/scripts/generar_docx.py --estado   # palabras, tablas, figuras y pendientes por capítulo
python3 docs/scripts/prueba_humo.py           # comprobación completa de tu instalación
```

Al abrir el `.docx` hay que actualizar los campos para llenar el índice y las listas de tablas y
figuras: en **Word** (Windows o Mac) responde **Sí** a la pregunta (o Ctrl/⌘ + A y F9); en
**LibreOffice**, *Herramientas → Actualizar → Todos los índices y tablas*.

**Protección del documento editado a mano.** El generador guarda una huella de cada `.docx` que
crea. Si después lo editas en Word, se niega a sobrescribirlo. En ese caso renómbralo (por ejemplo,
`Tesis_entregado_2026-11.docx`), cambia `salida` en `documento.toml` o usa `--forzar` si quieres
perder esas ediciones.

El generador falla y **no** escribe el documento si una imagen no existe, una referencia
`@tabla:`, `@figura:` o `@sec:` no tiene destino o hay claves repetidas. Las variables sin valor y
las tablas sin título solo dan aviso.

## 4. Sintaxis de los capítulos

| Escribes | Resultado |
|---|---|
| `# Título` … `#### Título` | Niveles APA 1 a 4. Cada `#` empieza página. Numeración automática: `Capítulo 2.`, `2.1.`, `2.1.1.` |
| `# Título {#clave}` | El título se puede citar con `@sec:clave` → «Capítulo 2» o «sección 2.3» |
| `{.sin-numero}` / `{.sin-indice}` / `{.en-indice}` | No numerar · no mostrar en el índice · mostrar en el índice un preliminar |
| Líneas seguidas | Un párrafo con sangría de 1,27 cm. Una línea vacía separa párrafos |
| `**negrita**` `*cursiva*` `` `código` `` | Formato en línea |
| `[[pendiente]]` | Texto resaltado en amarillo; `--estado` los cuenta |
| `{{AUTOR}}` | Valor de `.env` o de `[variables]` en `documento.toml` |
| `- ítem` / `1. ítem` | Viñetas / lista numerada (sangría de 2 espacios = subnivel) |
| `> texto` | Cita en bloque (40 palabras o más) |
| `Tabla: Título {#clave anchos=4,3,9.5 tam=10}` + tabla `\|…\|` | Tabla APA numerada; `anchos` en cm, opcional |
| `![Título](../recursos/figuras/x.png){#clave ancho=14}` | Figura APA numerada; `ancho` en cm, opcional |
| `Nota: texto` justo después de una tabla o figura | *Nota.* APA bajo la tabla o figura |
| `@tabla:clave` `@figura:clave` `@sec:clave` | «Tabla 3», «Figura 2», «sección 2.1» |
| ```` ``` ```` | Bloque de código |
| `\newpage` | Salto de página |
| `<!-- comentario -->` | No aparece en el documento |
| Bajo `# Referencias` | Una referencia por línea, con sangría francesa y orden alfabético (`{.sin-orden}` lo desactiva) |

`capitulos/02-marco-teorico.md` trae un ejemplo de cada elemento.

## 5. Privacidad

- Nombre, carnet, tutor, universidad, etc. solo en `.env`. En los `.md` y en
  `documento.toml` se usa `{{CLAVE}}`.
- `original/`, `dist/`, `.venv/`, `*.docx` y `*.pdf` nunca se suben. Para entregar, copia el archivo de `dist/` a otro lado.
- Si algo se versionó por error: `git rm --cached <archivo>`, y si ya hay commits con datos
  personales, limpia el historial **antes** de subir a un remoto.

## 6. Licencia y uso de IA

MIT (ver `LICENSE`). Al integrar el template en otro proyecto conserva el archivo `LICENSE` o su
aviso de copyright. La estructura y los scripts se crearon con asistencia de Claude Code
(Anthropic) a partir del generador del proyecto StudyPlan y fueron revisados por el autor.
