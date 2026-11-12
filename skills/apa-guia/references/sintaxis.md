# Sintaxis de los capítulos (Markdown de apa-kit)

Cada capítulo es un archivo `.md` en `<documento>/capitulos/`. Se unen en orden alfabético de archivo
(por eso el prefijo numérico: `01-`, `02-`…). `00-*` son preliminares y `90-`/`95-` van al final.
Ejemplo completo de todos los elementos: `ejemplo-sintaxis.md` (en esta misma carpeta).

| Escribes | Resultado |
|---|---|
| `# Título` … `#### Título` | Niveles APA 1 a 4. Con `numerar_titulos = true` se numeran solos: `Capítulo 2.`, `2.1.`, `2.1.1.` |
| `# Título {#clave}` | El título se puede citar con `@sec:clave` → «Capítulo 2» o «sección 2.3» |
| `{.sin-numero}` / `{.sin-indice}` / `{.en-indice}` | No numerar · no mostrar en el índice · mostrar en el índice un preliminar |
| Líneas seguidas | Un párrafo con sangría de 1,27 cm. Una línea vacía separa párrafos |
| `**negrita**` `*cursiva*` `` `código` `` | Formato en línea |
| `[[pendiente: qué falta]]` | Texto resaltado en amarillo; `--estado` y `revisar.py` los cuentan |
| `{{AUTOR}}` | Valor de `.env` o de `[variables]` en `documento.toml` |
| `- ítem` / `1. ítem` | Viñetas / lista numerada (sangría de 2 espacios = subnivel) |
| `> texto` | Cita en bloque (40 palabras o más) |
| `Tabla: Título {#clave anchos=4,3,9.5 tam=10}` + tabla `\|…\|` | Tabla APA numerada; `anchos` en cm, opcional |
| `![Título](../recursos/figuras/x.png){#clave ancho=14}` | Figura APA numerada; `ancho` en cm, opcional |
| `Nota: texto` justo después de una tabla o figura | *Nota.* APA bajo la tabla o figura |
| `@tabla:clave` `@figura:clave` `@sec:clave` | «Tabla 3», «Figura 2», «sección 2.1» |
| ```` ``` ```` | Bloque de código |
| `\newpage` | Salto de página |
| `<!-- comentario -->` | No aparece en el documento |
| Bajo `# Referencias` | Una referencia por línea, con sangría francesa y orden alfabético (`{.sin-orden}` lo desactiva) |

## Reglas que el generador hace cumplir
- Cada tabla lleva `Tabla:` con título, y cada figura su título. Cítalas con `@tabla:` / `@figura:`,
  **nunca con el número escrito a mano** (se renumeran solas al mover una tabla).
- Falla y **no escribe** el documento si: una imagen no existe, una referencia `@tabla:`, `@figura:` o
  `@sec:` no tiene destino, o hay claves repetidas.
- Solo avisa si: una variable `{{CLAVE}}` no tiene valor, o una tabla no tiene título.
- Las imágenes van en `<documento>/recursos/figuras/` y se citan con ruta relativa al capítulo
  (`../recursos/figuras/x.png`).

## Opciones de `documento.toml` que cambian el formato
| Clave | Efecto |
|---|---|
| `numerar_titulos` | `true`: Capítulo N. / N.M. automáticos. APA 7 no los exige; muchas facultades sí |
| `salto_nivel1` | `true`: cada título de nivel 1 empieza página. Preliminares, Referencias y Anexos siempre empiezan página |
| `etiqueta_seccion` | Palabra de las referencias `@sec:` («Capítulo», «Sección») |
| `etiqueta_tabla` / `etiqueta_figura` | «Tabla»/«Figura», o «Cuadro»/«Gráfico» si la facultad lo pide |
| `fuente`, `tamano`, `papel`, `justificar` | Tipografía y página (APA 7 admite Times New Roman 12, Calibri 11, Arial 11…) |
| `[preliminares].orden` | Orden de portada, previos, índice y listas |
