# Contribuir a apa-kit

Gracias por ayudar. apa-kit quiere servir a cualquier agente, carrera y tipo de documento.

## Reglas de base
1. **Las skills son portables.** En el `SKILL.md` solo los campos estándar: `name`, `description`, `license`,
   `compatibility`, `metadata`. Sin sintaxis propia de un agente en el cuerpo. Prueba los cambios en al menos dos agentes.
2. **Sin dependencias entre skills.** El material compartido vive en `skills/apa-init/assets/` y se copia a `.apa/`
   del proyecto; las demás skills leen `.apa/`. El paquete para Cowork (`herramientas/empaquetar.py`) junta todo en una.
3. **El núcleo no sabe de carreras.** Ningún texto de ingeniería, derecho o filosofía en el motor ni en los tipos
   genéricos. Lo específico va en un tipo propio (como `tesis-software`).
4. **El motor no inventa contenido.** Las reglas para agentes están en `skills/apa-guia/references/reglas-ia.md`.
5. **Multiplataforma.** Debe funcionar igual en Windows, macOS y Linux: Python estándar, rutas con `pathlib`,
   textos en UTF-8. No agregues `.bat`, `.sh`, `.ps1` ni ejecutables (los antivirus los marcan).
6. **Datos personales:** nunca en archivos versionados. Los ejemplos usan `{{CLAVE}}`.

## Contribuciones frecuentes
| Quiero… | Dónde |
|---|---|
| Agregar un **tipo de documento** | `skills/apa-init/assets/tipos/<tipo>/` (ver abajo) |
| Mejorar el formato APA | `skills/apa-init/assets/scripts/formato_apa.py` (solo formato, sin contenido) |
| Cambiar cómo se lee el Markdown | `skills/apa-init/assets/scripts/generar_docx.py` |
| Mejorar la importación de Word | `skills/apa-init/assets/scripts/importar_docx.py` |
| Ajustar el flujo de una skill | `skills/<skill>/SKILL.md` |
| Reglas y sintaxis | `skills/apa-guia/references/` |

## Agregar un tipo de documento
1. Crea `skills/apa-init/assets/tipos/<tipo>/` con:
   - `documento.toml` con una sección `[kit]` (`tipo`, `descripcion` en **una línea sin comillas internas**,
     `version_kit = "0"`), `[documento]`, `[portada]` y `[preliminares]`. Copia el de `tesis` o `libre` y ajusta
     `numerar_titulos`, `salto_nivel1`, `encabezado`, etc.
   - `.env.example` con **solo** las claves que usa su portada.
   - `capitulos/*.md`: un archivo por capítulo, con prefijo numérico. Solo marcas `[[…]]` neutras, sin datos inventados.
2. Agrégalo a la tabla de `skills/apa-guia/references/tipos.md` y del `README.md`.
3. Añádelo a `probar_demas_tipos` en `tests/prueba_humo.py` con sus comprobaciones propias.
4. `python3 tests/prueba_humo.py` debe terminar en `todo bien`.

## Probar
```bash
python3 -m pip install -r skills/apa-init/assets/scripts/requirements.txt   # Windows: py -3 -m pip …
python3 tests/prueba_humo.py          # crea cada tipo, importa un Word, genera, sincroniza, migra y empaqueta
python3 herramientas/empaquetar.py    # paquetes en build/ (ignorada por git)
claude plugin validate .              # el manifiesto del plugin
```
La CI repite la prueba en Windows, macOS y Linux con Python 3.9 y 3.13 (`.github/workflows/probar.yml`).
Todo cambio en `scripts/` debe pasarla.

## Commits y versiones
- Mensajes: `feat: …`, `fix: …`, `docs: …`, `test: …`, `build: …`.
- Versionado semántico mientras sea `0.x`: `0.2.1` arreglos, `0.3.0` funciones nuevas o cambios que rompen.
  `1.0.0` queda para cuando el autor declare el kit estable.
- Al subir de versión actualiza `skills/apa-init/assets/VERSION`, `metadata.version` de cada `SKILL.md`,
  `.claude-plugin/plugin.json` y `CHANGELOG.md`.
