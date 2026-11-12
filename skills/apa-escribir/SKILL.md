---
name: apa-escribir
description: Ayuda a redactar o mejorar un capítulo de un documento académico en formato APA 7, un capítulo por vez, sin inventar datos, citas ni referencias. Úsala cuando el usuario diga "ayúdame con mi introducción", "escribe el marco teórico", "mejora la redacción de este capítulo", "agrega una sección sobre…", "pon esta tabla o figura" o "cita a este autor". Requiere que apa-init ya haya creado el documento.
license: MIT
compatibility: Cualquier agente que admita SKILL.md. No ejecuta código para redactar; usa los scripts solo para comprobar.
metadata:
  version: "0.2.0"
  kit: apa-kit
  profile: core
---

# apa-escribir

Trabaja **un capítulo por vez**, en `<documento>/capitulos/NN-nombre.md`. Antes de empezar lee
`skills/apa-guia/SKILL.md` y sus `references/reglas-ia.md` y `references/sintaxis.md`. Si no existe
`<documento>/documento.toml`, usa **apa-init**; si el usuario ya tiene su trabajo en Word, **apa-importar**.

## Reglas que no se negocian
1. **El contenido lo decide el autor.** No inventes datos, resultados, entrevistas, cifras ni citas. Si
   falta información, pregunta o deja `[[pendiente: qué falta]]`.
2. **Referencias:** nunca agregues una referencia, DOI o URL sin comprobar que existe. Las que propongas
   van con `[[verificar]]` hasta que el autor las confirme. Una cita en el texto necesita su referencia.
3. **Solo editas** los `.md` de `capitulos/`, `recursos/` y `documento.toml`. Nunca un `.docx`.
4. **Datos personales** solo en `.env`; en los `.md`, `{{CLAVE}}`.
5. No hagas commit ni push sin que lo pidan.

## Flujo para cada capítulo
1. **Lee solo ese archivo** (y `documento.toml` si hace falta). No cargues todo el documento: ahí está la
   ventaja de un archivo por capítulo.
2. **Pregunta lo que falta** (objetivo del capítulo, fuentes, datos). Reconoce las marcas `[[…]]` como
   huecos que el autor debe llenar con su información.
3. **Propón el texto** en el estilo del autor, en párrafos continuos, con las citas que él te dé en
   formato `(Autor, año)`. Mejora la redacción sin cambiar su sentido ni sus datos.
4. **Tablas y figuras:** cada tabla con `Tabla: Título {#clave}` y cada figura con título; se citan con
   `@tabla:clave` / `@figura:clave`, nunca con el número escrito. Las imágenes van en `recursos/figuras/`.
5. **Comprueba:** `python .apa/scripts/generar_docx.py --estado` (ver el avance) y, si cambiaste
   referencias cruzadas o imágenes, `python .apa/scripts/generar_docx.py` para ver si hay errores. Con
   `py -3` en Windows o `python3` en macOS/Linux; con varios documentos, `--doc <carpeta>`.
6. **Cierra el capítulo** resumiendo qué cambió y qué quedó pendiente. Si el autor usa git, sugiere un
   mensaje de commit (`docs(cap2): …`) y espera su orden.

## Capítulos nuevos
Un archivo por capítulo, con prefijo numérico para el orden (`03-metodologia.md`). `00-*` son preliminares
(resumen, dedicatoria; sin número ni índice salvo `{.en-indice}`), `90-referencias.md` y `95-anexos.md`
llevan `{.sin-numero}`. No supongas el índice: si la institución dio uno, síguelo.

## Registro de uso de IA
Si la institución exige declarar el uso de IA, anota la sesión (solicitud, resultado, decisión del autor,
verificación) en el capítulo o anexo que el autor indique.
