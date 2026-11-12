---
name: apa-guia
description: Reglas y sintaxis para escribir cualquier documento académico en formato APA 7 con apa-kit (tesis, trabajo, informe, monografía; de cualquier carrera: derecho, lengua, filosofía, ingeniería…). Explica cómo se escribe cada capítulo en Markdown, cómo citar tablas y figuras, qué decide el autor y qué hace el generador, y las reglas para que un agente no invente datos ni referencias. Úsala cuando el usuario pregunte "cómo escribo en APA", "cómo pongo una tabla o figura", "cómo cito", "qué sintaxis uso" o cuando vayas a editar capítulos de un documento apa-kit.
license: MIT
compatibility: Cualquier agente que admita SKILL.md. Es solo documentación: no ejecuta nada.
metadata:
  version: "0.2.0"
  kit: apa-kit
  profile: core
---

# apa-guia

Base común de apa-kit. Las demás skills (`apa-init`, `apa-importar`, `apa-escribir`, `apa-generar`,
`apa-revisar`) la citan. Carga solo la parte que necesites:

| Necesito… | Lee |
|---|---|
| Escribir o editar un capítulo (títulos, tablas, figuras, citas cruzadas, variables) | `references/sintaxis.md` (+ `references/ejemplo-sintaxis.md`, un capítulo con todos los elementos) |
| Saber qué resuelve el generador y qué decide el autor (citas, referencias, estructura) | `references/apa7.md` |
| Reglas de conducta del agente (no inventar, referencias, privacidad, git, archivos que no se tocan) | `references/reglas-ia.md` |
| Elegir el tipo de documento (`tesis`, `libre`…) | `references/tipos.md` |

## Cómo está organizado un proyecto
```
<carpeta del usuario>/
├─ .apa/scripts/        motor del kit (lo copia apa-init; no se edita)
└─ <documento>/         una carpeta por documento (p. ej. tesis/)
   ├─ documento.toml    título, formato, portada
   ├─ capitulos/*.md    un archivo por capítulo → lee y edita solo el que toca
   ├─ recursos/         figuras, diagramas, logos
   ├─ .env              datos personales (ignorado por git)
   └─ dist/             el .docx generado (ignorado por git)
```
Un `.md` por capítulo más git significa que cada cambio es una versión pequeña, y que no hace falta
cargar todo el documento en el contexto.

## Reglas mínimas (el detalle está en `references/reglas-ia.md`)
1. El contenido lo decide el autor. No inventes datos, citas ni referencias; deja `[[pendiente: …]]` o
   `[[verificar]]`.
2. Edita solo `.md`, `recursos/` y `documento.toml`. Nunca un `.docx`.
3. Datos personales solo en `.env`; en los `.md`, `{{CLAVE}}`.
4. Cita tablas y figuras con `@tabla:`/`@figura:`, nunca con el número a mano.
5. Antes de generar, `verificar_entorno.py`; para ver el avance, `generar_docx.py --estado`.
6. Sin commit ni push sin pedido explícito.

## Flujo completo
`apa-init` (crear) → `apa-importar` (si hay un Word) → `apa-escribir` (capítulo por capítulo) →
`apa-revisar` (citas y pendientes) → `apa-generar` (el Word).
