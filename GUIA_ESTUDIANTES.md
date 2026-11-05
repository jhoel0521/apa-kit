# Guía para estudiantes que no programan

Para ti si estudias derecho, contabilidad, administración, educación u otra carrera y ya tienes tu
tesis o trabajo **avanzado en Word o Google Docs**. No necesitas saber programar ni usar git.
Funciona en **Windows, macOS y Linux**.

> **iPhone y iPad no pueden usarla**: no permiten instalar Python. Usa una computadora.

## Qué ganas

- Tu documento queda en **formato APA 7** sin pelear con márgenes, sangrías, títulos ni índices.
- Los números de capítulos, tablas y figuras se ponen **solos**; si mueves una tabla, se renumera.
- El índice y las listas de tablas y figuras se generan automáticamente.
- Tu Word original **nunca se modifica**.

## Qué necesitas

| Necesitas | Windows | macOS | Linux (Ubuntu/Debian) |
|---|---|---|---|
| **Python** 3.9 o superior (gratis) | `winget install Python.Python.3.13` o <https://www.python.org/downloads/> marcando «Add python.exe to PATH» | `brew install python` o <https://www.python.org/downloads/macos/> | `sudo apt install python3 python3-venv python3-pip` |
| Tu documento en **.docx** | Word: *Guardar como → .docx*. Google Docs: *Archivo → Descargar → Microsoft Word (.docx)* | igual | igual |
| Un programa para abrir el resultado | Word o LibreOffice | Word o LibreOffice | LibreOffice |

Git **no es necesario**.

## Dos formas de usarla

**A. Con un asistente de IA (la más fácil).** Abre tu asistente (Claude, Codex, Gemini…) con acceso a
tus archivos y pega el **Prompt B** de [`PROMPT_INICIAL.md`](PROMPT_INICIAL.md). Él descarga la
plantilla, instala lo que falte, importa tu Word y te va preguntando. Tú decides; él ejecuta.

**B. Tú mismo, con 3 comandos.** Sigue los pasos de abajo.

## Paso a paso (forma B)

### 1. Descargar la plantilla
Descarga el ZIP <https://github.com/jhoel0521/plantilla-docs-apa/archive/refs/heads/main.zip>,
descomprímelo en *Documentos* y renombra la carpeta a **`MiTesis`**.

### 2. Abrir una terminal en esa carpeta
- **Windows:** abre la carpeta, clic derecho en un espacio vacío → *Abrir en Terminal*.
- **macOS:** abre *Terminal*, escribe `cd ` (con un espacio) y **arrastra la carpeta `MiTesis`** a la
  ventana; pulsa Enter. La primera vez, macOS puede ofrecer instalar «herramientas de línea de
  comandos»: acepta.
- **Linux:** clic derecho en la carpeta → *Abrir en terminal*.

En los comandos siguientes, usa **`py -3`** en Windows y **`python3`** en macOS y Linux.

### 3. Revisar la computadora
```
py -3 scripts/verificar_entorno.py --instalar        # Windows
python3 scripts/verificar_entorno.py --instalar      # macOS y Linux
```
Instala lo que falta y crea el archivo `.env` para tus datos. Los `[AVISO]` no impiden seguir; los
`[ERROR]` sí, y dicen qué hacer.

### 4. Importar tu Word
```
py -3 scripts/importar_docx.py "C:/Users/yo/Documents/Mi tesis.docx"        # Windows
python3 scripts/importar_docx.py "/Users/yo/Documents/Mi tesis.docx"        # macOS y Linux
```
Truco: escribe el comando hasta `importar_docx.py ` y **arrastra tu archivo .docx a la terminal**:
pega la ruta completa.

El programa guarda una copia de tu Word en `original/` (el tuyo no se toca), crea un archivo por
capítulo en `capitulos/`, copia tus imágenes a `recursos/figuras/` y deja `[[revisar: …]]` en lo que
no pudo traer (ecuaciones, cuadros de texto, gráficos de Excel, notas al pie). Termina con un
resumen: revisa que el **porcentaje de palabras** sea alto (cerca de 90–100 %).

> Funciona mejor si en Word los capítulos usan el estilo **Título 1** y los subtítulos **Título 2**,
> **Título 3** (pestaña *Inicio → Estilos*). Si no, intenta reconocerlos por la negrita y la
> numeración y te avisa.

### 5. Tus datos de portada
Abre el archivo **`.env`** con un editor de texto (Bloc de notas; en Mac, TextEdit en *Formato →
Convertir a texto plano*; en Linux, gedit) y completa lo que está después de cada `=`. Si no lo ves:
en Mac pulsa ⌘ + Mayús + `.`; en Linux, Ctrl + H. Tu portada anterior quedó en `original/portada.txt`.

```
AUTOR=María Pérez Rojas
UNIVERSIDAD=Universidad ...
CARRERA=Derecho
TUTOR=Dr. ...
```
El título y otras opciones están en **`documento.toml`**. Si tu facultad pide «Cuadro» en vez de
«Tabla», cambia `etiqueta_tabla = "Cuadro"`. Tu logo va en `recursos/logos/logo.png`.

### 6. Generar el documento
```
py -3 scripts/generar_docx.py        # Windows
python3 scripts/generar_docx.py      # macOS y Linux
```
Queda en `dist/Tesis.docx`. **Actualiza el índice y las listas al abrirlo:**
- **Word (Windows o Mac):** responde **Sí** a «¿Desea actualizar los campos?». Si no pregunta:
  Ctrl + A (⌘ + A en Mac) y luego F9.
- **LibreOffice:** *Herramientas → Actualizar → Todos los índices y tablas*.

Compáralo con tu original y corrige lo marcado en amarillo.

### 7. Seguir escribiendo
Elige **una** forma y no las mezcles:
- **Con tu asistente de IA:** *«en el capítulo 2 agrega un subtítulo sobre la Ley 1178…»*,
  *«ordena mis referencias»*, *«¿qué me falta?»*. Las reglas están en `AGENTS.md`.
- **Editando los capítulos tú mismo:** son archivos de texto en `capitulos/`. Se editan cómodo con
  **Obsidian** (gratis) o **Visual Studio Code**. Solo necesitas: `# Capítulo` y `## Subtítulo`,
  `**negrita**`, `*cursiva*`, `- viñeta` y `[[falta completar]]` (sale resaltado en amarillo). El
  resto está en el [`README.md`](README.md), sección 4.
- **Siguiendo en Word:** escribe en tu Word y, cuando quieras el formato APA, **vuelve a importarlo**
  (paso 4). Los capítulos anteriores se guardan en `capitulos/_antes-de-importar-<fecha>/`.

Para ver tu avance: `python3 scripts/generar_docx.py --estado` (Windows: `py -3 …`).

### 8. Guardar versiones (opcional)
- **Sin git:** antes de cada revisión con tu tutor, copia la carpeta `MiTesis` y ponle la fecha
  (`MiTesis_2026-11-20`). OneDrive, iCloud o Google Drive también guardan versiones.
- **Con git:** instálalo (<https://git-scm.com>) y pide a tu asistente «activa el historial de
  versiones y guarda una versión». Tus datos, tu Word original y los documentos generados **nunca**
  se guardan en el historial. Si lo subes a internet, que sea un repositorio **privado**.

### Entregar
Copia el `.docx` de `dist/` donde quieras. Para PDF: *Archivo → Guardar como → PDF* en Word, o
*Archivo → Exportar como PDF* en LibreOffice. Si editas a mano ese `.docx`, el programa **no lo
sobrescribe** al regenerar: te pedirá que le cambies el nombre.

## Problemas frecuentes

| Mensaje o problema | Solución |
|---|---|
| `py` o `python3` «no se reconoce» / «command not found» | Instala Python (tabla de arriba); en Windows marca «Add to PATH» y abre una terminal nueva |
| `externally-managed-environment` | El verificador lo resuelve solo: crea una carpeta `.venv/` con lo necesario. Si falla, instala `python3-venv` (Linux) |
| «No encontré capítulos» | Aplica **Título 1** a los nombres de capítulo en Word e importa de nuevo |
| «No se pudo escribir … ciérralo en Word» | Cierra el documento de `dist/` y genera otra vez |
| «ALTO: … cambió después de generarse» | Editaste el documento generado: cámbiale el nombre para conservarlo y vuelve a generar |
| Imagen en formato EMF/WMF | En Word: clic derecho sobre la imagen → *Guardar como imagen* → PNG; reemplázala en `recursos/figuras/` |
| Ecuaciones, notas al pie, cuadros de texto | Quedan como `[[revisar: …]]`. APA 7 desaconseja las notas al pie: pasa su contenido al texto |
| Tu universidad no usa APA | Papel, fuente, «Cuadro» y portada se cambian en `documento.toml`; lo demás, pídeselo a tu asistente |
