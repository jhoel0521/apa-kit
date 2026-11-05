# AGENTS.md — Reglas para agentes de IA en este repositorio

Lo lee cualquier asistente de IA (Claude Code, Codex, Gemini, Copilot…) antes de trabajar aquí.
Las decisiones de este archivo son humanas; la IA no las cambia por iniciativa propia.

## 1. Qué es
Repositorio de un documento académico (tesis) escrito en Markdown y generado en Word con formato
APA 7. Este repositorio es un **template** que se clona dentro de la carpeta `docs/` de otros
proyectos. Manual completo: `README.md`. En los comandos, `docs/` es la carpeta donde quedó el template.

## 2. Antes de hacer cualquier cosa
1. Ejecuta `python docs/scripts/verificar_entorno.py`. Si termina con errores, corrígelos o
   informa al autor; no generes el documento con errores.
2. Ejecuta `python docs/scripts/generar_docx.py --estado` para conocer el avance.

## 3. Reglas
- **El contenido lo decide el autor.** La IA no inventa datos, resultados, entrevistas, cifras ni
  requisitos. Si falta información, pregunta o deja `[[pendiente: qué falta]]`.
- **Referencias:** nunca agregues una referencia, DOI o URL sin verificar que existe. Las que
  propongas van con `[[verificar]]` hasta que el autor las confirme.
- **Edita solo `capitulos/*.md`, `recursos/`, `documento.toml` y `scripts/`.** Nunca edites un `.docx`
  ni un `.pdf`. Si el autor ya editó el documento en Word, no lo regeneres encima (el script lo
  impide; no uses `--forzar` sin permiso explícito).
- **Privacidad:** datos personales solo en `.env` (ignorado). No los copies a `.md`, `.toml`,
  README, commits ni mensajes. Usa `{{CLAVE}}`.
- **Formato:** respeta la sintaxis de `README.md` §4. Cada tabla lleva `Tabla:` con título y
  cada figura su título; cita tablas y figuras con `@tabla:` / `@figura:`, nunca con el número a mano.
- **Git:** no hagas commit ni push sin pedido explícito. Mensajes: `docs(cap2): …`, `build: …`.
- **Uso de IA:** si la institución exige declararlo, registra cada sesión (solicitud, resultado de
  la IA, decisión del autor, verificación) en el capítulo o anexo que el autor indique.

## 4. Integrar el template en otro proyecto

Sigue [`PROMPT_INICIAL.md`](PROMPT_INICIAL.md): clonar en `docs/` (u otra carpeta si ya existe),
revisar si el proyecto tiene git, borrar el `.git` del template y hacer commit, o preguntar al
autor si lo mantiene como fork o independiente y qué hace con la licencia.
