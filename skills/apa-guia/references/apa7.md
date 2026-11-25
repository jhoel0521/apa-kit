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
- **Citas en el texto:** ver «Cómo se escribe una cita» abajo. Cita textual de menos de 40 palabras entre
  comillas con página `(p. 12)`; de 40 o más, en bloque (`> texto`), sin comillas.
- **Forma de la cita:** `[citas]` de `documento.toml` declara la conjunción entre dos autores dentro del
  paréntesis (`conjuncion = "y"` o `"&"`) y cómo se escribe «sin fecha» (`sin_fecha = "s.f."` o `"s. f."`).
  Las guías en español no coinciden; por defecto el kit usa «y» y «s.f.». Escribe siempre en la forma
  declarada: `revisar.py` sugiere corregir lo distinto.
- **Lista de referencias:** una por línea bajo `# Referencias`; DOI como URL (`https://doi.org/…`).
  El generador no valida que existan: verifícalas una por una.
- **Estructura del documento:** qué capítulos lleva depende de la institución y del tipo de trabajo
  (ver `tipos.md`).
- **Lenguaje:** sin sesgo, claro y conciso.

## Cómo se escribe una cita
Ejemplos inventados, con la forma por defecto (`y`, `s.f.`):

| Caso | Narrativa | Parentética | En Referencias |
|---|---|---|---|
| Un autor | Pérez (2023) | (Pérez, 2023) · (Pérez, 2023, p. 14) | Pérez, J. (2023). … |
| Dos autores | Pérez y Gómez (2023) | (Pérez y Gómez, 2023) | Pérez, J., y Gómez, L. (2023). … |
| Tres o más | Pérez et al. (2023), desde la primera cita | (Pérez et al., 2023) | Todos los autores (hasta 20) |
| Grupo con sigla, primera vez | Organización Ejemplo de Salud (OES, 2020) | (Organización Ejemplo de Salud [OES], 2020) | Organización Ejemplo de Salud. (2020). … |
| Grupo con sigla, después | OES (2020) | (OES, 2020) | (la misma) |
| Sin fecha | Pérez (s.f.) | (Pérez, s.f.) | Pérez, J. (s.f.). … |
| Varias sin fecha del mismo autor | Pérez (s.f.-a) | (Pérez, s.f.-a, s.f.-b) | Pérez, J. (s.f.-a). … |
| En prensa | Pérez (en prensa) | (Pérez, en prensa) | Pérez, J. (en prensa). … |
| Mismo autor, varios años | Pérez (2020, 2021) | (Pérez, 2020, 2021) | Una entrada por año |
| Mismo autor y año | Pérez (2020a) | (Pérez, 2020a, 2020b) | Pérez, J. (2020a). … |
| Varias obras | | (Arce, 2019; Pérez, 2020) | En orden alfabético, separadas por «;» |
| Cita secundaria | Peal (2018, como se citó en Tsai, 2019) | (Peal, 2018, como se citó en Tsai, 2019) | **Solo Tsai** |
| Comunicación personal | J. Zapata (comunicación personal, 8 de febrero de 2021) | (J. Zapata, comunicación personal, 8 de febrero de 2021) | **No va** |
| Obra sin autor | *Título breve* (2008) | (*Título breve*, 2008) | El título en lugar del autor |
| Remisión | | (véase Pérez, 2020) · (cf. Pérez, 2020) | Normal |

Localizadores: `p. 13`, `pp. 13-14`, `párr. 3`, `cap. 2`. «et al.» va sin tilde y con punto.

## Portada y encabezado
- La portada se define en `[portada].bloques`, en la entrevista de portada de apa-init (lista de elementos y
  ejemplos en `references/portadas.md` de apa-init). Los tipos la traen vacía y el Word no se genera hasta
  definirla.
- `encabezado = "TÍTULO CORTO"` en `[documento]` pone el título corto a la izquierda y el número a la
  derecha en todas las páginas (trabajos profesionales). Sin él, solo el número.
- La parte `titulo_cuerpo` de `[preliminares].orden` repite el título, en negrita y centrado, al comenzar
  el texto, como pide APA 7.

## Qué no cubre aún el kit
- Niveles de título 5, notas al pie y ecuaciones (el importador las marca `[[revisar: …]]`).
- Validar que una referencia exista o esté bien formada: eso lo confirma el autor.
