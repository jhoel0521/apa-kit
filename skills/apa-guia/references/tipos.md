# Tipos de documento

`iniciar.py --listar` muestra los tipos instalados. Cada tipo trae su `documento.toml`, su `.env.example`
y sus capítulos; ninguno incluye texto de una carrera concreta, solo marcas `[[…]]` neutras.

| Tipo | Para quién | Formato por defecto |
|---|---|---|
| `tesis` | Tesis de grado o posgrado de cualquier carrera (Filosofía, Derecho, Lengua, Ingeniería…) | Capítulos numerados, cada uno en página nueva |
| `libre` | Cualquier documento APA 7 cuyo índice dicta la institución: el agente lo arma preguntando | Sin numerar, sin saltos de página |

## Cómo elegir
1. Pregunta qué documento es y si la institución entregó un índice o una guía.
2. Si hay índice oficial, usa `libre` (o `tesis` si coincide en lo esencial) y crea un archivo `.md`
   por sección con el orden del índice. **No supongas el índice.**
3. Si el documento ya existe en Word, empieza por `apa-importar` en lugar de escribir de cero.

Para agregar un tipo nuevo, ver `CONTRIBUTING.md` del repositorio.
