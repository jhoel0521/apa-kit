# Portadas: entrevista y ejemplos

La portada de un documento se define en `[portada].bloques` de `documento.toml`: una lista ordenada de bloques.
Los tipos nuevos la traen vacía (`bloques = []`) y **el Word no se genera hasta definirla**. Este archivo es la
guía de la entrevista de portada de `apa-init`.

## 1. Entrevista (no asumas nada)

1. Pregunta si la institución dio una guía o un ejemplo de portada (PDF, imagen, Word). Si la tiene y puedes leer
   ese formato, léela y saca de ella los elementos, su orden, la fuente y los tamaños. Si no puedes leerla, dilo.
2. Muestra al autor **la lista completa** de elementos (sección 2) para que marque los que lleva su portada. Si
   hay guía o el autor eligió un ejemplo (sección 4), muestra ya marcados los que vienen de ahí, pero que el autor
   confirme o cambie cada uno. Puede agregar un elemento que no esté en la lista.
3. Pide el **orden** de los elementos marcados, de arriba abajo.
4. Pregunta si la institución pide fuente o tamaño distintos en la portada (si no, se usa la del documento).
5. Escribe los bloques en `[portada].bloques`. Por cada `{{CLAVE}}` nueva, agrégala a `.env.example` (vacía) y
   pide su valor al autor para `.env`. **Nunca** escribas un dato personal en `documento.toml`: solo `{{CLAVE}}`.
6. Genera el Word y pide al autor que mire la portada. Si ocupa más de una página, quita bloques `espacio`,
   reduce `espacios_arriba` o el tamaño de letra.

Si el autor no sabe todavía cómo es su portada, déjala vacía y explícale que el Word no se generará hasta
definirla. Si la portada está definida pero falta un dato en `.env`, el Word sale con ese lugar en blanco y un
aviso: lo mejor es completarlo en `.env` (si lo llena a mano en el Word, la protección del Word editado impedirá
regenerarlo encima).

## 2. Elementos posibles

| Elemento | Clave sugerida | Notas |
|---|---|---|
| Logo de la institución | (bloque `logo`) | Archivo en `recursos/logos/` |
| Universidad o institución | `{{UNIVERSIDAD}}` | |
| Facultad | `{{FACULTAD}}` | |
| Carrera | `{{CARRERA}}` | |
| Departamento o área | `{{DEPARTAMENTO}}` | |
| Actividad académica | `{{ACTIVIDAD}}` | Proyecto, práctico, informe, monografía… |
| Título | `{{TITULO}}` | Automática: sale de `[documento].titulo` |
| Subtítulo | `{{SUBTITULO}}` | Automática: sale de `[documento].subtitulo` |
| Autor o integrantes | `{{AUTOR}}` | Varios integrantes: un bloque por persona (`{{AUTOR2}}`…) |
| Código o registro del estudiante | `{{REGISTRO}}` | |
| Materia y sigla | `{{MATERIA}}`, `{{SIGLA}}` | |
| Docente o tutor | `{{DOCENTE}}` o `{{TUTOR}}` | |
| Grupo o paralelo | `{{GRUPO}}` | |
| Gestión o semestre | `{{GESTION}}` | |
| Ciudad y país | `{{CIUDAD}}`, `{{PAIS}}` | |
| Fecha de entrega | `{{FECHA}}` | |
| Nota del autor (artículos) | (clave `nota_autor`) | Va al pie, fuera de `bloques` |

## 3. Cómo se escribe cada bloque

```toml
[portada]
espacios_arriba = 1                      # líneas en blanco antes del primer bloque
bloques = [
  { logo = "recursos/logos/logo.png", ancho_cm = 5 },
  { espacio = 1 },                       # una línea en blanco
  { texto = "{{TITULO}}", negrita = true },
  { texto = "Tutor: {{TUTOR}}", fuente = "Arial", tamano = 12 },
]
```

- `texto`: una línea centrada. Admite `**negrita**`, `*cursiva*` y varias `{{CLAVE}}`. `fuente`, `tamano` (en
  puntos) y `negrita` son opcionales; si faltan, se usa la fuente y el tamaño de `[documento]`.
- `logo`: imagen centrada; `ancho_cm` opcional (4 cm si falta). Si el archivo no existe, sale sin logo y avisa.
- `espacio`: cantidad de líneas en blanco.

La portada por bloques usa interlineado sencillo. El texto de plantilla `[[…]]` dentro de un bloque cuenta como
portada sin definir.

## 4. Ejemplos

Cópialos como punto de partida y ajústalos con el autor. Ninguno es obligatorio.

### Estándar universidades privadas de Bolivia (`bolivia-privada`)

Logo; actividad académica; título; autor, carrera y docente; ciudad y país, y fecha. Todo centrado en Arial
Black: 14 pt, el título en 20 pt y el pie en 12 pt. Arial Black viene con Windows y Mac; en Linux o LibreOffice
puede no estar instalada y Word o LibreOffice la reemplazan por otra.

```toml
[portada]
espacios_arriba = 1
bloques = [
  { logo = "recursos/logos/logo.png", ancho_cm = 6 },
  { espacio = 1 },
  { texto = "{{ACTIVIDAD}}", fuente = "Arial Black", tamano = 14 },
  { espacio = 1 },
  { texto = "{{TITULO}}", fuente = "Arial Black", tamano = 20 },
  { espacio = 1 },
  { texto = "{{AUTOR}}", fuente = "Arial Black", tamano = 14 },
  { texto = "{{CARRERA}}", fuente = "Arial Black", tamano = 14 },
  { texto = "{{DOCENTE}}", fuente = "Arial Black", tamano = 14 },
  { espacio = 3 },
  { texto = "{{CIUDAD}}, {{PAIS}}", fuente = "Arial Black", tamano = 12 },
  { texto = "{{FECHA}}", fuente = "Arial Black", tamano = 12 },
]
```

### Portada de estudiante APA 7

Título en negrita; autor; facultad y universidad; curso; docente; fecha.

```toml
[portada]
espacios_arriba = 3
bloques = [
  { texto = "{{TITULO}}", negrita = true },
  { espacio = 1 },
  { texto = "{{AUTOR}}" },
  { texto = "{{FACULTAD}}, {{UNIVERSIDAD}}" },
  { texto = "{{CURSO}}" },
  { texto = "{{DOCENTE}}" },
  { texto = "{{FECHA}}" },
]
```

### Universidad y facultad arriba del logo

```toml
[portada]
espacios_arriba = 0
bloques = [
  { texto = "{{UNIVERSIDAD}}", negrita = true, tamano = 14 },
  { texto = "{{FACULTAD}}", negrita = true },
  { espacio = 1 },
  { logo = "recursos/logos/logo.png", ancho_cm = 6 },
  { espacio = 1 },
  { texto = "{{TITULO}}", negrita = true, tamano = 14 },
  { espacio = 2 },
  { texto = "{{MATERIA}}" },
  { texto = "Docente: {{DOCENTE}}" },
  { texto = "Estudiante: {{AUTOR}}" },
  { espacio = 2 },
  { texto = "{{CIUDAD}}, {{FECHA}}" },
]
```

## 5. Documentos de la versión 0.2

Si `[portada]` no tiene la clave `bloques` (documentos creados antes de la 0.3.0), el generador sigue usando
`logo`, `titulo`, `subtitulo` y `[portada].lineas` como antes. Para pasar a bloques, haz la entrevista y
reemplaza `lineas` por `bloques`; el título y el subtítulo entran como `{{TITULO}}` y `{{SUBTITULO}}`.
