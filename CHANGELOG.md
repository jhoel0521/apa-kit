# Changelog

Versionado semántico en fase de desarrollo (`0.x`): puede haber cambios grandes entre versiones menores.

## Sin publicar
### Corrige
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
