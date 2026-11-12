# APA 7 en lo que el generador resuelve (y en lo que no)

El generador aplica el **formato**; el **contenido** y su corrección (citas, referencias, redacción)
son del autor. Cuando la institución pida algo distinto de APA 7, manda la institución: ajústalo en
`documento.toml`.

## Lo que `generar_docx.py` hace solo
- Página (carta, A4 u oficio) con márgenes de 2,54 cm, interlineado doble, sangría de 1,27 cm en el
  primer renglón, alineado a la izquierda, número de página arriba a la derecha.
- Fuente configurable (por defecto Times New Roman 12; APA 7 admite también Calibri 11, Arial 11…).
- Títulos de nivel 1 a 4 con el estilo APA de cada nivel; numeración opcional.
- Tablas y figuras numeradas, con título y *Nota.*; índice y listas de tablas y figuras (se llenan al
  abrir en Word: aceptar «actualizar campos»).
- Referencias con sangría francesa y orden alfabético.

## Lo que decide el autor
- **Citas en el texto:** `(Autor, año)` o `Autor (año)`; dos autores con «y»; tres o más con «et al.».
  Cita textual de menos de 40 palabras entre comillas con página `(p. 12)`; de 40 o más, en bloque
  (`> texto`), sin comillas.
- **Lista de referencias:** una por línea bajo `# Referencias`; DOI como URL (`https://doi.org/…`).
  El generador no valida que existan: verifícalas una por una.
- **Estructura del documento:** qué capítulos lleva depende de la institución y del tipo de trabajo
  (ver `tipos.md`).
- **Lenguaje:** sin sesgo, claro y conciso.

## Qué no cubre aún el kit
- Portada APA 7 «de estudiante» y «profesional» como tipos propios, encabezado con título corto y nota
  de autor: llegan en tipos de documento posteriores. Hoy la portada es un bloque de líneas
  configurable en `[portada]`.
- Niveles de título 5, notas al pie y ecuaciones (el importador las marca `[[revisar: …]]`).
