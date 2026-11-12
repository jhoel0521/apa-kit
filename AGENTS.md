# AGENTS.md — Reglas para agentes que desarrollan apa-kit

Este archivo es para quien **modifica el kit** (este repositorio). Si lo que quieres es **escribir un
documento** con apa-kit, no trabajes aquí: usa las skills (`apa-init`, `apa-escribir`…) en la carpeta del usuario;
sus reglas están en `skills/apa-guia/references/reglas-ia.md`.

Las decisiones de este archivo son humanas; la IA no las cambia por iniciativa propia.

## 1. Qué es
Un kit de skills (formato `SKILL.md`) para que cualquier agente cree y versione documentos académicos APA 7
(Markdown → Word) de cualquier carrera. Modelo de estructura: [ux-kit](https://github.com/jhoel0521/ux-kit).
Estructura y razones: `README.md` y `CONTRIBUTING.md`.

## 2. Antes de cambiar nada
1. `python3 -m pip install -r skills/apa-init/assets/scripts/requirements.txt` (Windows: `py -3 -m pip …`).
2. `python3 tests/prueba_humo.py` debe terminar en `todo bien`. Hazlo también al terminar.

## 3. Reglas
- **El núcleo no sabe de carreras.** Nada de ingeniería, derecho o filosofía en el motor ni en los tipos
  genéricos; lo específico es un tipo aparte.
- **Skills portables:** frontmatter solo con `name`, `description`, `license`, `compatibility`, `metadata`; sin
  dependencias de archivos entre skills (lo compartido está en `skills/apa-init/assets/`).
- **Las skills nunca escriben dentro de sí mismas:** `iniciar.py` solo usa la biblioteca estándar y escribe en el
  proyecto del usuario. La prueba de humo lo comprueba; no la debilites.
- **Multiplataforma:** igual en Windows, macOS y Linux. Python estándar, `pathlib`, UTF-8. **No agregues `.bat`,
  `.sh`, `.ps1` ni ejecutables.** Todo cambio en `scripts/` pasa la prueba de humo y la CI
  (`.github/workflows/probar.yml`: 3 sistemas × Python 3.9 y 3.13).
- **Compatibilidad hacia atrás del documento:** si cambias un valor por defecto de `documento.toml`, `iniciar.py
  --migrar` debe escribir el valor antiguo explícito y la prueba de humo debe comprobarlo.
- **Protección del Word editado a mano:** no la debilites (`generar_docx.py`, huellas en `dist/.huellas.json`).
- **Privacidad:** ningún dato personal en archivos versionados; los ejemplos usan `{{CLAVE}}`.
- **Referencias y datos:** no inventes referencias, DOI ni URL en ejemplos o documentación.
- **Python 3.9:** nada de `match`, ni `X | Y` en tipos, ni `tomllib` sin el respaldo `tomli`.
- **Git:** no hagas commit, push ni etiquetas sin pedido explícito. Mensajes: `feat:`, `fix:`, `docs:`, `test:`, `build:`.
- **Versiones:** `0.x`; al subir, actualiza `assets/VERSION`, `metadata.version` de cada skill, `plugin.json` y `CHANGELOG.md`.
