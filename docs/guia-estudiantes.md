# Guía para estudiantes (sin programar)

Para escribir tu tesis, trabajo o informe en **formato APA 7** con ayuda de un asistente de IA. No necesitas
saber programar ni usar git. Tú decides el contenido; apa-kit se encarga del formato (márgenes, títulos,
tablas, figuras, índice, referencias).

## Lo que necesitas
- Una computadora con **Windows, macOS o Linux** (un celular o tablet no sirve).
- **Claude** con la función de *skills* (Claude Code, Cowork o claude.ai) u otro asistente que admita skills.
- **Python 3.9 o superior**. Si no lo tienes, el asistente te pedirá permiso y te dirá cómo instalarlo.
- Microsoft Word o LibreOffice (gratis) para abrir el resultado y actualizar el índice.

## Paso 1 — Instalar apa-kit
- **En Cowork o claude.ai:** descarga `apa-kit-cowork.zip` de la página de
  [Releases](https://github.com/jhoel0521/apa-kit/releases) y súbelo en *Configuración → Skills*.
- **En Claude Code:** escribe `/plugin install apa-kit --marketplace jhoel0521/apa-kit`.

## Paso 2 — Elegir una carpeta de trabajo
Crea una carpeta para tu trabajo (por ejemplo `Documentos/MiTesis`) y ábrela con tu asistente. Todo se guardará ahí.

## Paso 3 — Pedir lo que quieres
Escríbele al asistente con tus palabras. Algunos ejemplos:

- «Quiero escribir mi tesis en formato APA.»
- «Ya tengo mi tesis en Word, pásala a APA.» *(te pedirá el archivo; el original no se modifica)*
- «Ayúdame con mi marco teórico.»
- «¿Qué me falta antes de entregar?»
- «Genera mi Word.»

El asistente te irá preguntando: qué tipo de documento es, cómo se llama tu universidad, qué índice te pide tu
facultad. **Tus datos personales** (nombre, carnet, tutor…) se guardan solo en un archivo llamado `.env` que
nunca se comparte.

## Paso 4 — Abrir el Word
El Word queda en la carpeta `dist/` de tu documento. Al abrirlo, responde **Sí** a «¿actualizar campos?» para que
se llenen el índice y las listas de tablas y figuras. En LibreOffice: *Herramientas → Actualizar → Todos los índices y tablas*.

## Cómo seguir escribiendo (elige UNA forma)
1. **Con tu asistente:** le pides cambios y los hace en los capítulos. Es la más cómoda.
2. **Tú mismo en los archivos de texto:** cada capítulo es un archivo en `capitulos/`. Se editan con *Obsidian*
   (gratis) o *Visual Studio Code*.
3. **En Word y volver a importar:** sigues en Word y cuando quieras pasas al asistente, que reimporta. Los
   capítulos anteriores se guardan en una carpeta aparte para que no se pierda nada.

No mezcles las formas: si editas en Word y a la vez en los capítulos, una pisará a la otra.

## Guardar versiones
- **Sin git:** antes de cada revisión con tu tutor, copia la carpeta y ponle la fecha (`MiTesis_2026-11-20`).
  OneDrive, iCloud o Google Drive también guardan versiones.
- **Con git (opcional):** guarda cada versión y permite volver atrás. Pídele al asistente «activa las versiones»;
  te explicará cada paso. Si lo subes a internet, que sea un repositorio **privado**.

## Reglas de oro
- El asistente **no debe inventar** datos, citas ni referencias. Lo que no sepa lo deja como `[[pendiente]]`;
  verifica tú que cada referencia exista antes de entregar.
- **Si editas el Word a mano**, apa-kit no lo sobrescribirá al generar de nuevo (te avisará). Renómbralo para conservarlo.
- Si tu institución exige declarar el uso de IA, pídele al asistente que registre cada sesión.

## Problemas frecuentes
| Me aparece… | Qué hacer |
|---|---|
| «No encontré capítulos» al importar | En tu Word aplica el estilo **Título 1** a los nombres de capítulo y **Título 2** a los subtítulos, y vuelve a importar |
| «externally-managed-environment» | Es normal en Linux y Mac con Homebrew; apa-kit crea un entorno propio solo |
| «ALTO: … cambió después de generarse» | Editaste el Word a mano. Renómbralo, o cambia `salida` en `documento.toml` |
| El índice sale vacío | Falta actualizar los campos (Paso 4) |
| Marcas amarillas `[[…]]` en el Word | Son datos que faltan; pídele al asistente «qué me falta» |
