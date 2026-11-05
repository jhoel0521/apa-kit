# Prompt inicial: integrar el template en un proyecto

Copia el bloque siguiente en tu agente de IA (Claude Code, Codex, Gemini…) **abierto en la raíz del
proyecto real**.

- Repositorio: https://github.com/jhoel0521/plantilla-docs-apa
- URL para clonar: `https://github.com/jhoel0521/plantilla-docs-apa.git`

---

```text
Integra el template de documentación APA 7 en este proyecto. Sigue los pasos EN ORDEN, muéstrame
la salida de cada comando y detente a preguntarme donde se indica. No inventes datos personales.

URL del template: https://github.com/jhoel0521/plantilla-docs-apa.git
Carpeta destino: docs   (si te doy otra, usa esa)

PASO 1 — Ubicación
- Confirma que estás en la raíz del proyecto real (muestra `pwd` y lista los archivos).

PASO 2 — Carpeta destino
- Si `docs/` no existe o está vacía: `git clone https://github.com/jhoel0521/plantilla-docs-apa.git docs`.
- Si `docs/` ya existe con contenido: NO la sobrescribas. Pregúntame qué nombre usar
  (por ejemplo `docs/tesis`, `docs/informe` o `documento`) y clona ahí.
  En adelante, DESTINO es esa carpeta.

PASO 3 — ¿El proyecto ya usa git?
- Ejecuta en la raíz: `git rev-parse --is-inside-work-tree`.

PASO 3.1 — SÍ tiene git (caso normal: el template pasa a ser parte del proyecto)
  a. Borra el historial del template: elimina `DESTINO/.git` (en PowerShell:
     `Remove-Item -Recurse -Force DESTINO/.git`; en bash: `rm -rf DESTINO/.git`).
  b. Conserva `DESTINO/LICENSE` (la licencia MIT exige mantener el aviso de copyright).
  c. Comprueba que lo privado queda fuera: `git status --ignored DESTINO` debe mostrar
     `DESTINO/.env` y `DESTINO/dist/` como ignorados, y
     `git ls-files DESTINO | grep -E "\.env$|\.docx$|\.pdf$"` no debe devolver nada.
  d. `git add DESTINO` y `git commit -m "docs: integrar template de documentación APA 7"`.
     Sin Co-Authored-By de la IA salvo que yo lo pida.

PASO 3.2 — NO tiene git
  Pregúntame cuál de estas opciones prefiero y espera mi respuesta:
  a. Fork / vinculado al template: conservar `DESTINO/.git`, renombrar el remoto con
     `git -C DESTINO remote rename origin template` para poder traer mejoras con
     `git -C DESTINO pull template main`, y agregar mi propio remoto si lo tengo.
  b. Independiente: borrar `DESTINO/.git`, hacer `git init` en la raíz del proyecto y el commit
     del paso 3.1.d.
  c. Sin git: borrar `DESTINO/.git` y no versionar (desaconsejado: se pierde el historial).
  En todas las opciones pregúntame si mantengo la licencia MIT del template tal cual o si la
  cambio para mi proyecto (el aviso de copyright del template debe conservarse igual).

PASO 4 — Requisitos del sistema
- `python DESTINO/scripts/verificar_entorno.py --instalar`
- Si falta Python ≥ 3.11 o Git, detente y dime qué instalar. No instales software del sistema
  sin mi permiso. Repite la verificación hasta que dé 0 errores.

PASO 5 — Datos personales
- Copia `DESTINO/.env.example` a `DESTINO/.env` y pídeme los valores (autor, universidad,
  tutor…). Escríbelos SOLO en `.env`; nunca en .md, .toml, README ni commits.

PASO 6 — Configuración del documento
- Pregúntame: título, tipo de documento (tesis, informe, entrega…), nombre del archivo de
  salida, papel y si hay logo. Ajusta `DESTINO/documento.toml`.
- Pregúntame el índice que exige mi institución y adapta `DESTINO/capitulos/` (un archivo por
  capítulo, prefijo numérico para el orden). No supongas el índice.

PASO 7 — Prueba final
- `python DESTINO/scripts/generar_docx.py` debe terminar en `OK .../dist/<salida>.docx`.
- `python DESTINO/scripts/generar_docx.py --estado` para mostrar el avance.
- Resúmeme: carpeta usada, opción de git elegida, commit creado (hash) y pendientes.

Reglas permanentes: lee `DESTINO/AGENTS.md` antes de editar capítulos. Nunca edites un .docx;
nunca uses --forzar sin mi permiso; no hagas push sin pedírtelo yo.
```

---

## Lo mismo, a mano

```bash
cd ~/mi-proyecto                                  # 1. proyecto real
git clone https://github.com/jhoel0521/plantilla-docs-apa.git docs                 # 2. (otro nombre si docs/ ya existe)
git rev-parse --is-inside-work-tree               # 3. ¿tiene git?
# 3.1 sí tiene git
rm -rf docs/.git
git add docs && git commit -m "docs: integrar template de documentación APA 7"
# 3.2 no tiene git → decidir: fork (git -C docs remote rename origin template),
#     independiente (rm -rf docs/.git && git init) — conservar LICENSE en ambos casos
python docs/scripts/verificar_entorno.py --instalar   # 4.
cp docs/.env.example docs/.env                        # 5. y completarlo
python docs/scripts/generar_docx.py                   # 7.
```

## Traer mejoras del template a un proyecto que borró `.git`

Los scripts son independientes del contenido, así que basta con reemplazar `scripts/`:

```bash
git clone --depth 1 https://github.com/jhoel0521/plantilla-docs-apa.git /tmp/template
cp /tmp/template/scripts/*.py docs/scripts/
python docs/scripts/verificar_entorno.py && python docs/scripts/generar_docx.py
git diff docs/scripts      # revisar antes del commit
```

No copies `capitulos/`, `documento.toml` ni `.env`: son de tu proyecto.
