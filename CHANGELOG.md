# Changelog

Versionado semántico en fase de desarrollo (`0.x`): puede haber cambios grandes entre versiones menores.

## 0.3.0 — 2026-11-25
**Para actualizar:** `apa-init` con «actualiza apa-kit» (`iniciar.py --sincronizar`). Los documentos ya creados
se generan igual que antes: su `documento.toml` no se toca y su portada (`[portada].lineas`) sigue funcionando.
Los documentos **nuevos** traen la portada sin definir y no generan el Word hasta hacer la entrevista de portada.

### Nuevo
- **Portada por bloques (#13).** `[portada].bloques` es una lista ordenada de bloques `texto` (con `fuente`,
  `tamano` y `negrita` opcionales), `logo` y `espacio`; `{{TITULO}}` y `{{SUBTITULO}}` salen de `[documento]`.
  Permite, por ejemplo, la universidad y la facultad arriba del logo, o fuente y tamaños propios por línea.
- **Entrevista de portada en `apa-init`:** muestra la lista completa de elementos para que el autor marque los
  suyos y luego los ordene; si la institución dio una guía, se usa como fuente. Lista y ejemplos en
  `skills/apa-init/references/portadas.md` (incluido el ejemplo «Estándar universidades privadas de Bolivia»,
  `bolivia-privada`).
- **Forma de cita declarada (#8, #10):** `[citas]` en `documento.toml` (`conjuncion = "y"` o `"&"`,
  `sin_fecha = "s.f."` o `"s. f."`). `apa-escribir` escribe así y `revisar.py` suma el grupo «Formato de citas
  (sugerencias)», que no cuenta para `--estricto`. `apa7.md` trae una tabla de cómo se escribe cada cita.
- `revisar.py` lista en el grupo «Caracteres a evitar», con archivo y línea, las rayas (—), el guion medio (–) fuera
  de un rango numérico, las flechas (→) y los emojis o íconos de los capítulos y de `documento.toml` (#7, #14).
  `--estricto` también los cuenta.
- Regla de estilo en `apa-guia/references/reglas-ia.md` («Estilo») y en `apa-escribir`: puntuación normal, sin
  caracteres que delatan a la IA, también en el texto copiado de otro documento, con una guía para reemplazarlos
  sin romper la frase (#7, #14).
- Logo en el README y archivos para compartir en `docs/img/` (logo, imagen social de GitHub, historia vertical).

### Cambia
- **Los tipos traen `[portada].bloques = []`:** `generar_docx.py` no genera el Word hasta definir la portada (o
  si un bloque conserva texto de plantilla `[[…]]`). Definida, un dato de la portada sin valor en `.env` sale en
  blanco, no como `[[CLAVE]]`, y la salida lo avisa.
- La regla «sin rayas» de `reglas-ia.md` se aclara como decisión de estilo del kit, no como norma APA.
- El paquete único de Cowork incluye `references/portadas.md`.
- El sitio web pasa de la rama `gh-pages` a la carpeta `sitio/` de `main`, con validación en cada PR (`tests/probar_sitio.py`) y publicación automática (`.github/workflows/sitio.yml`).
- `herramientas/arte/preparar_arte.py` genera el logo y las imágenes para compartir a partir de las imágenes de la IA.

### Corrige
- `revisar.py` daba avisos falsos con citas correctas (#8, #10): leía solo la primera palabra del autor
  (`(React Team, 2024)` se buscaba como «Team»), no aceptaba `s. f.`, `s.f.-a` ni «en prensa», contaba como
  faltante al autor original de una cita secundaria y no reconocía varios años del mismo autor.
- En Linux sin `python3-venv`, `verificar_entorno.py` dejaba un `.apa/.venv/` roto que atrapaba a todos los
  scripts, y mostraba el error como una lista de Python (#9). Ahora lo borra, muestra la causa y el comando
  para instalarla; `_entorno.py` no relanza en un `.venv` sin `python-docx`.
- Atajos para actualizar índices (#11): en Word en español seleccionar todo es Ctrl+E (Ctrl+A abre un
  archivo) y en LibreOffice F9 no actualiza índices. Corregido en `apa-generar` y en el aviso del Word.
- Ya no se genera una página «Lista de tablas» o «Lista de figuras» vacía cuando el documento no tiene
  ninguna (#12).
- Las plantillas `tesis` y `tesis-software` ponían una raya en la portada (`{{FACULTAD}} — {{CARRERA}}`); ahora es
  una coma. Los documentos ya creados no cambian (#14).
- Sitio web (auditoría UX): enlaces de navegación, logo, resúmenes de preguntas y botones miden 44 px o más; la descarga del
  Cowork es el botón principal de «Instalar» y «Copiar texto» pasa a secundario; el aviso para móviles va antes de los botones;
  los botones heredan la fuente de la página; la tipografía se reduce a 4 tamaños (15, 17, 24 y 28/40 px); los dos botones
  «Copiar» tienen nombre accesible distinto; «Copiado» indica el siguiente paso; el iPad se reconoce como móvil (sin probar en
  un iPad real); logo de cabecera de 5 KB en lugar de 42 KB; se borra CSS sin uso. Medido con Edge a 320, 375 y 1280 px,
  en tema claro y oscuro, sin desborde horizontal. `tests/probar_sitio.py` fija estas correcciones.
- Tablas: una tabla que cabía en una página podía partirse, con el título y dos filas al pie de una hoja y el resto en la
  siguiente. Ahora ninguna fila se parte y cada tabla va atada a su título y a su nota: si cabe en una página, Word la mueve
  entera; si es más alta, la parte y repite el encabezado. En un barrido de 40 tablas en Word, pasó de 9 rotas a 0 con las
  mismas páginas. Se desactiva con `tablas_juntas = false` en `documento.toml`.

### Documenta
- Maquetación en `apa-guia/references/sintaxis.md`: por qué no usar saltos manuales, `<br>` dentro de una celda, tamaño
  de figuras y logo.

## 0.2.0 — apa-kit
**Cambio de diseño: el repositorio deja de ser una plantilla para clonar y pasa a ser un kit de skills.**
Quien necesite el diseño anterior puede descargar la etiqueta [`v0.1.0`](https://github.com/jhoel0521/apa-kit/releases/tag/v0.1.0).

### Rompe
- Ya no se clona dentro de `docs/`. Se instalan las skills (`npx skills add jhoel0521/apa-kit`, plugin o zip para Cowork)
  y `apa-init` crea `.apa/` y la carpeta del documento en el proyecto del usuario.
- `scripts/` ya no está en la raíz: el motor vive en `skills/apa-init/assets/scripts/` y se copia a `.apa/scripts/`.
- Se eliminan `PROMPT_INICIAL.md` y `GUIA_ESTUDIANTES.md` (la guía pasó a `docs/guia-estudiantes.md`).
- Valores por defecto ahora neutrales (APA 7 puro): `numerar_titulos = false`, `salto_nivel1 = false`, idioma `es`,
  `salida` = nombre de la carpeta del documento. Los tipos y `iniciar.py --migrar` escriben los valores explícitos.

### Nuevo
- Seis skills: `apa-guia`, `apa-init`, `apa-importar`, `apa-escribir`, `apa-generar`, `apa-revisar`.
- Seis tipos de documento: `tesis`, `tesis-software`, `trabajo-estudiante`, `articulo`, `informe`, `libre`.
- `iniciar.py`: crea, sincroniza (`--sincronizar`) y migra (`--migrar`) sin escribir nunca dentro de la skill.
- `revisar.py`: marcas pendientes, citas sin referencia y referencias sin cita (candidatos, no errores).
- Opciones de `documento.toml`: `salto_nivel1`, `etiqueta_seccion`, `encabezado`, `[portada].nota_autor` y la
  parte `titulo_cuerpo` de `[preliminares].orden`.
- Varios documentos por proyecto (`--doc <carpeta>` o `APA_DOC`).
- Paquetes: `apa-kit-cowork.zip` (una sola skill con todo), un zip por skill y el plugin (`herramientas/empaquetar.py`).
- Plugin y marketplace de Claude Code (`.claude-plugin/`).

### Cambia
- Los capítulos de ejemplo ya no suponen una tesis de software; eso quedó en el tipo `tesis-software`.
- La CI corre en cualquier repositorio (antes se saltaba fuera de `jhoel0521/plantilla-docs-apa`).

## 0.1.0 — plantilla
Plantilla de documentación académica en APA 7 para clonar en `docs/`, con generador `.docx`, importador de Word,
verificador de entorno y CI en Windows, macOS y Linux.
