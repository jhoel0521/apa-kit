---
name: apa-revisar
description: Revisa un documento académico en APA 7 antes de entregarlo - lista las marcas pendientes, las citas que no tienen su referencia, las referencias que nadie cita y el texto de plantilla sin reemplazar. Úsala cuando el usuario diga "revisa mi tesis", "qué me falta", "están bien mis citas y referencias", "antes de entregar" o "qué tengo pendiente". Requiere que apa-init ya haya creado .apa/ y el documento.
license: MIT
compatibility: Cualquier agente que admita SKILL.md. Requiere Python 3.9+ y la carpeta .apa/ creada por apa-init.
metadata:
  version: "0.2.0"
  kit: apa-kit
  profile: core
---

# apa-revisar

Si no existe `.apa/scripts/` o `<documento>/documento.toml`, no sigas: usa **apa-init**. Lee las reglas de
`skills/apa-guia/SKILL.md`. Esta skill **informa y pregunta; no corrige por su cuenta**: todo lo que
encuentra es un *candidato* que se confirma con el autor.

**Comando de Python:** `py -3` (Windows), `python3` (macOS y Linux) o `python`, el que funcione. Con varios
documentos añade `--doc <carpeta>`.

## 1. Avance
```bash
python .apa/scripts/generar_docx.py --estado
```
Palabras, tablas, figuras y marcas por capítulo, contra la meta de `documento.toml`.

## 2. Candidatos
```bash
python .apa/scripts/revisar.py
```
Termina siempre con código 0 (con `--estricto`, 1 si queda algo). Explica al usuario cada grupo:

| Grupo | Qué significa | Qué hacer |
|---|---|---|
| Pendientes `[[pendiente: …]]` | Falta contenido que solo el autor puede dar | Pregunta el dato; **no lo inventes** |
| Por verificar `[[verificar]]` | Referencia o dato propuesto sin comprobar | Pide al autor que confirme que existe; solo entonces quita la marca |
| Por revisar `[[revisar: …]]` | El importador no pudo convertir ecuaciones, cuadros de texto, notas al pie, imágenes EMF… | Resuélvelo con el autor mirando su Word original |
| Texto de plantilla `[[…]]` | Párrafo guía que no se reemplazó | Escribirlo con el autor o borrar el apartado si su institución no lo pide |
| Citas sin referencia | `(Autor, año)` sin entrada bajo `# Referencias` | Pregunta de dónde sale; agrega la referencia con `[[verificar]]` |
| Referencias que no se citan | Entrada de la lista que ningún capítulo cita | Pregunta si se cita o se quita |

Falsos positivos frecuentes: autores corporativos (`Organización Mundial de la Salud [OMS], 2020`), citas
secundarias («citado en…»), años con letra (`2020a`) y textos como «Ley 1178 (1990)». Revisa antes de
afirmar que hay un error.

## 3. Lista antes de entregar
1. `revisar.py` sin pendientes ni citas huérfanas (salvo falsos positivos confirmados).
2. Todas las referencias comprobadas por el autor (ninguna `[[verificar]]` viva).
3. `generar_docx.py` termina en `OK` y se abre en Word aceptando «actualizar campos».
4. Datos personales completos en `.env` (el generador avisa de las variables vacías).
5. Si la institución exige declarar el uso de IA: sesión registrada donde indique el autor.
