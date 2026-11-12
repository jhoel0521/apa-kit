---
name: apa-generar
description: Genera el documento Word (.docx) con formato APA 7 a partir de los capítulos en Markdown, y muestra el avance del trabajo (palabras, tablas, figuras y pendientes por capítulo). Úsala cuando el usuario diga "genera mi Word", "sácame el documento", "ver cuánto llevo", "cómo voy con mi tesis", "actualiza el índice" o "pásalo a PDF". Requiere que apa-init ya haya creado .apa/ y el documento.
license: MIT
compatibility: Cualquier agente que admita SKILL.md. Requiere Python 3.9+ y la carpeta .apa/ creada por apa-init.
metadata:
  version: "0.2.0"
  kit: apa-kit
  profile: core
---

# apa-generar

Convierte `<documento>/capitulos/*.md` en `<documento>/dist/<salida>.docx` con formato APA 7.
Si no existe `.apa/scripts/` o `<documento>/documento.toml`, no sigas: usa **apa-init**. Lee las reglas de
`skills/apa-guia/SKILL.md` (nunca edites el `.docx`; no uses `--forzar` sin permiso).

**Comando de Python:** `py -3` (Windows), `python3` (macOS y Linux) o `python`, el que funcione. Si hay
varios documentos en el proyecto, añade `--doc <carpeta>` a cada comando.

## 1. Verificar (siempre antes de generar)
```bash
python .apa/scripts/verificar_entorno.py
```
Si termina con `[ERROR]`, corrígelos o avisa al autor. No generes con errores. Los `[AVISO]` no bloquean.

## 2. Ver el avance (sin abrir el .docx)
```bash
python .apa/scripts/generar_docx.py --estado
```
Muestra palabras, tablas, figuras y marcas `[[pendiente]]` por capítulo. Resume al usuario cuánto falta.

## 3. Generar
```bash
python .apa/scripts/generar_docx.py
```
Termina en `OK …/dist/<salida>.docx`. El generador **falla y no escribe nada** si una imagen no existe,
una referencia `@tabla:`/`@figura:`/`@sec:` no tiene destino o hay claves repetidas: muestra el error
tal cual y corrige el `.md` indicado (archivo:línea). Los avisos (variables sin valor, tabla sin título)
no bloquean, pero cuéntaselos al usuario.

Si responde `ALTO: … cambió después de generarse`, el usuario editó el Word a mano. **No uses `--forzar`.**
Explícale: renombrar su Word (p. ej. `Tesis_entregado_2026-11.docx`) o cambiar `salida` en `documento.toml`.

## 4. Entregar
Dile dónde quedó el archivo (`<documento>/dist/`) y cómo actualizar índices al abrirlo:
- **Word** (Windows o Mac): responder **Sí** a «¿actualizar campos?» (o Ctrl/⌘ + A y F9).
- **LibreOffice:** *Herramientas → Actualizar → Todos los índices y tablas*.
Para entregar, que copie el archivo de `dist/` a otro lado: `dist/` no se versiona.
