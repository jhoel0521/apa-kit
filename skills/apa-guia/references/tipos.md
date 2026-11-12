# Tipos de documento

`iniciar.py --listar` muestra los tipos instalados. Cada tipo trae su `documento.toml`, su `.env.example`
y sus capítulos; ninguno incluye texto de una carrera concreta, solo marcas `[[…]]` neutras (salvo
`tesis-software`, que existe justamente para eso).

| Tipo | Para quién | Formato por defecto |
|---|---|---|
| `tesis` | Tesis de grado o posgrado de cualquier carrera (Filosofía, Derecho, Lengua, Ingeniería…) | Capítulos numerados, cada uno en página nueva, con índice y listas |
| `tesis-software` | Tesis de sistemas o software: análisis, diseño, implementación y pruebas | Como `tesis`, más la variable `NOMBRE_SISTEMA` |
| `trabajo-estudiante` | Ensayo, monografía o trabajo de curso | Portada de estudiante APA 7 (curso, docente, fecha), título repetido al comenzar el texto, sin índice ni numeración |
| `articulo` | Artículo académico o trabajo profesional | Encabezado con título corto y número, nota del autor, resumen, Método/Resultados/Discusión, sin índice ni numeración |
| `informe` | Informe técnico, de práctica, de pasantía o de proyecto | Secciones numeradas `1.`, `1.1.`, texto seguido, con índice |
| `libre` | Cualquier documento APA 7 cuyo índice dicta la institución: el agente lo arma preguntando | Sin numerar, sin saltos de página |

## Cómo elegir
1. Pregunta qué documento es y si la institución entregó un índice o una guía.
2. Si hay índice oficial, usa `libre` (o el tipo que coincida en lo esencial) y crea un archivo `.md`
   por sección con el orden del índice. **No supongas el índice.**
3. Si el documento ya existe en Word, empieza por `apa-importar` en lugar de escribir de cero.
4. Cualquier tipo se ajusta en `documento.toml`: `numerar_titulos`, `salto_nivel1`, `encabezado`,
   etiquetas, fuente… (ver `sintaxis.md`). Elegir un tipo no encierra al usuario.

Para agregar un tipo nuevo, ver `CONTRIBUTING.md` del repositorio.
