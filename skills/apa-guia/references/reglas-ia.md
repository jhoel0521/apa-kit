# Reglas para el agente al escribir un documento académico

Las decisiones de este archivo son humanas: no las cambies por iniciativa propia.

## Contenido
- **El contenido lo decide el autor.** No inventes datos, resultados, entrevistas, cifras, citas ni
  requisitos. Si falta información, pregunta o deja `[[pendiente: qué falta]]`.
- **Referencias:** nunca agregues una referencia, DOI o URL sin comprobar que existe. Las que propongas
  van con `[[verificar]]` hasta que el autor las confirme.
- Una cita en el texto `(Autor, año)` debe tener su referencia en `Referencias`, y al revés.

## Archivos
- Edita solo los `.md` de `<documento>/capitulos/`, `<documento>/recursos/` y `<documento>/documento.toml`.
- **Nunca edites un `.docx` ni un `.pdf`**, ni el Word original del usuario ni su copia en `original/`.
- Si el autor ya editó el Word generado, no lo regeneres encima (el generador lo impide). No uses
  `--forzar` sin permiso explícito del autor.
- **No toques `.apa/scripts/`**: es del kit y se sobrescribe al sincronizar.

## Privacidad
- Datos personales (nombre, carnet, tutor, universidad…) solo en `<documento>/.env`, que git ignora.
  En los `.md` y el `.toml` usa `{{CLAVE}}`. No los copies a commits, README ni mensajes.

## Trabajo con capítulos (por qué esta herramienta existe)
- Un capítulo por archivo: lee y edita **solo el capítulo que toca**, no todo el documento. Así no
  pierdes contexto y cada cambio queda como una versión pequeña en git.
- Antes de generar el documento, ejecuta `verificar_entorno.py`; si termina con errores, corrígelos o
  avisa al autor.
- Para ver el avance usa `generar_docx.py --estado`; no abras el `.docx`.

## Git (si el autor lo usa)
- No hagas commit ni push sin pedido explícito. Mensajes sugeridos: `docs(cap2): …`, `build: …`.
- Si sube el repositorio a internet, que sea privado: contiene su trabajo.

## Uso de IA
Si la institución exige declararlo, registra cada sesión (solicitud, resultado de la IA, decisión del
autor, verificación) en el capítulo o anexo que el autor indique.

## Cómo hablar con quien no programa
- Lenguaje simple. Explica en una frase qué hace cada comando antes de ejecutarlo.
- Git es opcional: no lo exijas ni lo instales sin permiso. Ofrécelo como «guardar versiones».
- Dale el comando de Python que funcione en su equipo: `py -3` (Windows), `python3` (macOS y Linux).
- iPhone y iPad no pueden ejecutar los scripts (no instalan Python): que use una computadora.
