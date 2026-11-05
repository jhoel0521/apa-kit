# AGENTS.md — Reglas para agentes de IA en este repositorio

Lo lee cualquier asistente de IA (Claude Code, Codex, Gemini, Copilot…) antes de trabajar aquí.
Las decisiones de este archivo son humanas; la IA no las cambia por iniciativa propia.

## 1. Qué es
Repositorio de un documento académico (tesis) escrito en Markdown y generado en Word con formato
APA 7. Este repositorio es un **template** que se clona dentro de la carpeta `docs/` de otros
proyectos. Manual completo: `README.md`. En los comandos, `docs/` es la carpeta donde quedó el template.

## 1.1 Quién es el usuario (léelo aunque hayas llegado aquí por tu cuenta)
Esta plantilla la usan **dos perfiles**. Averigua cuál es antes de proponer pasos:

| Señal | Perfil | Cómo atenderlo |
|---|---|---|
| La carpeta está dentro de un proyecto de software (hay `app/`, `src/`, `package.json`, `.git` en el padre…) | Programador | Prompt A de `PROMPT_INICIAL.md`; comandos con rutas `docs/…` |
| La carpeta está sola (p. ej. `Documentos/MiTesis`), sin `.git`, o el usuario habla de su carrera, su tutor o «mi Word» | Estudiante que no programa | Prompt B y `GUIA_ESTUDIANTES.md`; comandos con rutas relativas a la carpeta |

Con un estudiante que no programa:
- Habla en lenguaje simple; explica en una frase qué hace cada comando antes de ejecutarlo.
- **Git es opcional.** No lo exijas ni lo instales sin permiso; ofrece el historial como algo
  opcional (Prompt B, paso 7). Si lo sube a internet, que sea un repositorio privado.
- Si tiene un documento avanzado, **impórtalo** (`scripts/importar_docx.py`) en vez de pedirle que
  copie el texto a mano. Si `capitulos/` todavía tiene los capítulos de ejemplo de la plantilla
  (`02-marco-teorico.md` habla de «la sintaxis admitida»), ofrécele importar su Word.
- Dale los comandos con el Python de su sistema (`py -3` en Windows, `python3` en macOS y Linux) y
  explícale cómo abrir una terminal en su carpeta (GUIA_ESTUDIANTES.md, paso 2).
- iPhone y iPad no pueden ejecutar los scripts (no instalan Python): dile que use una computadora.
- Él decide cómo seguir escribiendo (contigo, editando los `.md` o en Word y reimportando). No
  mezcles: si reimporta, los `.md` anteriores pasan a `capitulos/_antes-de-importar-<fecha>/`.

## 2. Antes de hacer cualquier cosa
1. Ejecuta `python docs/scripts/verificar_entorno.py` (usa `py -3` en Windows o `python3` en macOS/Linux
   si `python` no existe). Si termina con errores, corrígelos o
   informa al autor; no generes el documento con errores.
2. Ejecuta `python docs/scripts/generar_docx.py --estado` para conocer el avance.

## 3. Reglas
- **El contenido lo decide el autor.** La IA no inventa datos, resultados, entrevistas, cifras ni
  requisitos. Si falta información, pregunta o deja `[[pendiente: qué falta]]`.
- **Referencias:** nunca agregues una referencia, DOI o URL sin verificar que existe. Las que
  propongas van con `[[verificar]]` hasta que el autor las confirme.
- **Edita solo `capitulos/*.md`, `recursos/`, `documento.toml` y `scripts/`.** Nunca edites un `.docx`
  ni un `.pdf`, ni el Word original del usuario ni su copia en `original/` (solo lectura). Si el autor ya editó el documento en Word, no lo regeneres encima (el script lo
  impide; no uses `--forzar` sin permiso explícito).
- **Multiplataforma:** debe funcionar igual en Windows, macOS y Linux. No agregues `.bat`, `.sh`,
  `.ps1` ni ejecutables (los antivirus los marcan); todo es Python estándar, rutas con `pathlib` y
  textos en UTF-8. Todo cambio en `scripts/` debe pasar `python scripts/prueba_humo.py` y la CI
  (`.github/workflows/probar.yml`: 3 sistemas × Python 3.9 y 3.13).
- **Importación:** después de `importar_docx.py`, revisa con el usuario el resumen (porcentaje de
  palabras, capítulos, avisos) y resuelve las marcas `[[revisar: …]]` con él; no las borres sin
  resolverlas. Los datos de `original/portada.txt` se confirman con el usuario antes de ir a `.env`.
- **Privacidad:** datos personales solo en `.env` (ignorado). `original/` también está ignorado. No los copies a `.md`, `.toml`,
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
