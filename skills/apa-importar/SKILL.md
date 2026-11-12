---
name: apa-importar
description: Convierte un documento de Word (.docx) o Google Docs ya avanzado en capítulos Markdown para seguir con apa-kit, sin modificar el original. Úsala cuando el usuario diga "ya tengo mi tesis en Word", "pasa mi Word a APA", "importa mi documento", "tengo mi trabajo en Google Docs" o "quiero reimportar mi Word". Requiere que apa-init ya haya creado .apa/ y el documento.
license: MIT
compatibility: Cualquier agente que admita SKILL.md. Requiere Python 3.9+ y la carpeta .apa/ creada por apa-init. Solo lee archivos .docx.
metadata:
  version: "0.2.0"
  kit: apa-kit
  profile: core
---

# apa-importar

Convierte un `.docx` en `<documento>/capitulos/*.md`. Si no existe `.apa/scripts/`, usa **apa-init** primero.
Lee `skills/apa-guia/SKILL.md`. **Nunca modifiques el Word original** ni su copia en `original/` (solo lectura).
Con quien no programa: lenguaje simple y una frase de explicación antes de cada comando.

**Comando de Python:** `py -3` (Windows), `python3` (macOS y Linux) o `python`, el que funcione. Con varios
documentos añade `--doc <carpeta>`.

## 1. El archivo
Pregunta dónde está el `.docx`. Si está en Google Docs: *Archivo → Descargar → Microsoft Word (.docx)*. Si es
`.doc` u `.odt`, que lo guarde como `.docx` desde Word o LibreOffice.
Funciona mejor si en Word los capítulos usan el estilo **Título 1** y los subtítulos **Título 2** y **3**. Si
no, el importador dice «No encontré capítulos»: pide al usuario aplicar esos estilos y reimporta.

## 2. Aviso antes de importar
Si `capitulos/` aún tiene los capítulos de ejemplo del tipo elegido, se moverán a
`capitulos/_antes-de-importar-<fecha>/` (no se borra nada). Si ya escribió ahí, dile que **no mezcle**: o sigue
escribiendo en los `.md`, o sigue en Word y reimporta. Que elija una.

## 3. Importar
```bash
python .apa/scripts/importar_docx.py "<ruta del .docx>"
```
Opción `--oracion` convierte TÍTULOS EN MAYÚSCULAS a «Títulos en oración» (úsala si el Word los tiene así).
El script:
- guarda una copia en `<documento>/original/` (ignorada por git) y deja el texto de la portada en
  `original/portada.txt`;
- divide por títulos de nivel 1 en un archivo `.md` por capítulo y quita la numeración escrita a mano;
- convierte negritas, cursivas, listas, tablas e imágenes (a `recursos/figuras/`) con sus títulos y notas;
- marca con `[[revisar: …]]` lo que no puede convertir (ecuaciones, cuadros de texto, gráficos de Excel,
  notas al pie, imágenes EMF).

## 4. Revisar el resultado **con el usuario**
Muestra el resumen del script: capítulos creados, tablas, figuras, **porcentaje de palabras recuperadas** y
avisos. Si el porcentaje es bajo o los capítulos no coinciden con el índice de su Word, revisa con él antes de
seguir. Resuelve las `[[revisar: …]]` una por una, mirando el Word original; **no las borres sin resolverlas**.
Luego usa **apa-revisar** para listar lo que queda.

## 5. Datos de portada
Lee `original/portada.txt` y propón los valores del `.env` (autor, universidad, carrera, tutor, fecha…).
**Confírmalos con el usuario uno por uno** y escríbelos solo en `.env`. Ajusta el título en `documento.toml`.

## 6. Comparar
Genera con **apa-generar** y pide al usuario que compare con su Word original; corrijan juntos lo que no
coincida. Si cambia de idea y reimporta después, los `.md` anteriores pasan a
`capitulos/_antes-de-importar-<fecha>/`.
