# CLAUDE.md

Lee y cumple primero **@AGENTS.md** (reglas comunes) y **@README.md** (manual y sintaxis).

## Reglas para Claude
- Responde en español.
- Antes de generar el documento, ejecuta `python docs/scripts/verificar_entorno.py`.
- Para revisar el avance usa `python docs/scripts/generar_docx.py --estado`, no abras el `.docx`.
- Si el autor comparte el documento editado, pídele una conversión a `.md` para leerlo; no edites
  el `.docx`.
- No agregues `Co-Authored-By` en los commits salvo que el autor lo pida.
- Para integrar este template en otro proyecto sigue `PROMPT_INICIAL.md` paso a paso.
