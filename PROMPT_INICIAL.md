# Prompts iniciales

Copia el prompt que te corresponda en tu asistente de IA (Claude, Codex, Gemini, ChatGPT con acceso
a archivos…) y él hará la instalación contigo, paso a paso.

- Repositorio: https://github.com/jhoel0521/plantilla-docs-apa
- URL para clonar: `https://github.com/jhoel0521/plantilla-docs-apa.git`
- ZIP (sin git): https://github.com/jhoel0521/plantilla-docs-apa/archive/refs/heads/main.zip

| Tu caso | Prompt |
|---|---|
| Tienes un proyecto de software (con o sin git) y quieres su documentación en `docs/` | **A** |
| No programas (derecho, contabilidad…), no usas git y ya tienes tu documento avanzado en Word o Google Docs | **B** (ver también [`GUIA_ESTUDIANTES.md`](GUIA_ESTUDIANTES.md)) |
| Empiezas un documento desde cero, sin proyecto de software | **B**, respondiendo «no tengo documento» en el paso 4 |

## Prompt A — integrar en un proyecto de software

Ábrelo **en la raíz del proyecto real**.

```text
Integra el template de documentación APA 7 en este proyecto. Sigue los pasos EN ORDEN, muéstrame
la salida de cada comando y detente a preguntarme donde se indica. No inventes datos personales.

Comando de Python: usa el que funcione en mi sistema (`py -3` en Windows; `python3` en macOS y
Linux). Donde abajo diga `python`, significa ese comando. Pregúntame mi sistema si no lo sabes.

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
- Si falta Python ≥ 3.9 o Git, detente y dime qué instalar. No instales software del sistema
  sin mi permiso. Repite la verificación hasta que dé 0 errores.

PASO 5 — Datos personales
- El verificador ya creó `DESTINO/.env` desde `.env.example`. Pídeme los valores (autor, universidad,
  tutor…). Escríbelos SOLO en `.env`; nunca en .md, .toml, README ni commits.

PASO 6 — Configuración del documento
- Pregúntame: título, tipo de documento (tesis, informe, entrega…), nombre del archivo de
  salida, papel y si hay logo. Ajusta `DESTINO/documento.toml`.
- Si ya tengo el documento avanzado en Word, pídeme la ruta del .docx e impórtalo con
  `python DESTINO/scripts/importar_docx.py "<ruta>"` (no modifica el original).
- Si no, pregúntame el índice que exige mi institución y adapta `DESTINO/capitulos/` (un archivo
  por capítulo, prefijo numérico para el orden). No supongas el índice.

PASO 7 — Prueba final
- `python DESTINO/scripts/generar_docx.py` debe terminar en `OK .../dist/<salida>.docx`.
- `python DESTINO/scripts/generar_docx.py --estado` para mostrar el avance.
- Resúmeme: carpeta usada, opción de git elegida, commit creado (hash) y pendientes.

Reglas permanentes: lee `DESTINO/AGENTS.md` antes de editar capítulos. Nunca edites un .docx;
nunca uses --forzar sin mi permiso; no hagas push sin pedírtelo yo.
```

---

## Prompt B — estudiante que no programa, con su documento avanzado

Ábrelo en cualquier carpeta (por ejemplo, *Documentos*). No necesitas git.

```text
Quiero usar la plantilla de documentos APA 7 de https://github.com/jhoel0521/plantilla-docs-apa
con mi tesis, que ya tengo avanzada en Word (o Google Docs). NO soy programador: explícame cada
paso con palabras simples, sin términos técnicos, y pregúntame antes de instalar algo o de tomar
una decisión por mí. No inventes contenido de mi tesis ni datos personales.

Comando de Python: usa el que funcione en mi sistema (`py -3` en Windows; `python3` en macOS y
Linux). Donde abajo diga `python`, significa ese comando. Pregúntame mi sistema si no lo sabes.

PASO 1 — Mi computadora
- Pregúntame si uso Windows, macOS o Linux (iPhone/iPad no sirven: no pueden instalar Python).
- Revisa si tengo Python 3.9 o superior (`py -3 --version` o `python3 --version`).
- Si no está, explícame que es un programa gratuito necesario y PÍDEME PERMISO para instalarlo:
  Windows: `winget install Python.Python.3.13` (o python.org marcando «Add python.exe to PATH»);
  macOS: `brew install python` (o python.org/downloads/macos); Linux: `sudo apt install python3
  python3-venv python3-pip`.
- Git NO es obligatorio. No lo instales ahora.

PASO 2 — Carpeta de trabajo
- Pregúntame dónde crearla. Propón `Documentos/MiTesis`.
- Descarga la plantilla SIN git:
  Windows PowerShell:
    Invoke-WebRequest https://github.com/jhoel0521/plantilla-docs-apa/archive/refs/heads/main.zip -OutFile plantilla.zip
    Expand-Archive plantilla.zip . ; Rename-Item plantilla-docs-apa-main MiTesis ; Remove-Item plantilla.zip
  macOS/Linux:
    curl -L -o plantilla.zip https://github.com/jhoel0521/plantilla-docs-apa/archive/refs/heads/main.zip
    unzip plantilla.zip && mv plantilla-docs-apa-main MiTesis && rm plantilla.zip
- Si ya tengo git instalado, puedes clonar en su lugar y luego borrar la carpeta `.git` de MiTesis.
- Conserva el archivo LICENSE (es la licencia de la plantilla; no afecta a mi tesis).

PASO 3 — Preparar
- Dentro de MiTesis: `python scripts/verificar_entorno.py --instalar`. Repite hasta que no haya
  [ERROR]. Si el sistema impide instalar librerías (error «externally-managed-environment»), el
  propio verificador crea una carpeta `.venv/` y los demás scripts la usan solos. Explícame los
  [AVISO] en una frase.

PASO 4 — Mi documento
- Pregúntame dónde está mi .docx. Si está en Google Docs, dime cómo descargarlo
  (Archivo → Descargar → Microsoft Word). Si es .doc u .odt, que lo guarde como .docx.
- Importa: `python scripts/importar_docx.py "<ruta>"` (mi archivo original NO se modifica).
- Muéstrame el resumen: capítulos creados, tablas, figuras, porcentaje de palabras y avisos.
  Si el porcentaje es bajo o los capítulos no coinciden con mi índice, revisa conmigo antes de
  seguir (puede que mi Word no use los estilos Título 1/2/3; explícame cómo aplicarlos y
  reimporta).
- Si NO tengo documento: pregúntame el índice que pide mi universidad y crea un archivo por
  capítulo en `capitulos/`.

PASO 5 — Portada y formato
- Lee `original/portada.txt` y propónme los valores de `.env` (AUTOR, UNIVERSIDAD, FACULTAD,
  CARRERA, GRADO, TUTOR, CIUDAD, FECHA). CONFÍRMALOS conmigo uno por uno y escríbelos SOLO en `.env`.
- Pregúntame: título exacto, si mi facultad usa «Tabla» o «Cuadro», «Figura» o «Gráfico»,
  tamaño de papel y si tengo el logo de la universidad (va en recursos/logos/logo.png).
  Ajusta `documento.toml`.

PASO 6 — Generar y comparar
- `python scripts/generar_docx.py`. Dime dónde quedó el documento (`dist/`) y cómo actualizar el
  índice: en Word (Windows o Mac) responder «Sí» a «¿actualizar campos?»; en LibreOffice,
  Herramientas → Actualizar → Todos los índices y tablas.
- Lista las marcas [[revisar: …]] que quedaron (ecuaciones, notas al pie, cuadros de texto,
  imágenes EMF) y ayúdame a resolverlas una por una.
- Pídeme que compare con mi original y corrige juntos lo que no coincida.

PASO 7 — Versiones (opcional)
- Explícame en una frase qué es guardar versiones y pregúntame si lo quiero.
  - Si NO: recomiéndame copiar la carpeta con la fecha antes de cada revisión con mi tutor.
  - Si SÍ: pide permiso para instalar git (`winget install Git.Git`), luego `git init`,
    comprueba que `.env`, `original/` y `dist/` están ignorados y guarda la primera versión
    (`git add -A && git commit -m "Primera versión importada"`). No lo subas a internet salvo que
    yo lo pida, y si lo pido, en un repositorio PRIVADO.

PASO 8 — Cómo sigo
- Explícame las tres formas de seguir (GUIA_ESTUDIANTES.md, paso 6): pedirte cambios a ti,
  editar los capítulos con Obsidian o VS Code, o seguir en Word y reimportar. Recomiéndame
  una sola y adviérteme que no las mezcle.

Reglas permanentes: lee AGENTS.md. Nunca modifiques mi Word original ni un .docx generado;
nunca uses --forzar sin mi permiso; nunca copies mis datos personales fuera de .env.
```

---

## Prompt A, a mano

```bash
cd ~/mi-proyecto                                  # 1. proyecto real
git clone https://github.com/jhoel0521/plantilla-docs-apa.git docs                 # 2. (otro nombre si docs/ ya existe)
git rev-parse --is-inside-work-tree               # 3. ¿tiene git?
# 3.1 sí tiene git
rm -rf docs/.git
git add docs && git commit -m "docs: integrar template de documentación APA 7"
# 3.2 no tiene git → decidir: fork (git -C docs remote rename origin template),
#     independiente (rm -rf docs/.git && git init) — conservar LICENSE en ambos casos
python3 docs/scripts/verificar_entorno.py --instalar  # 4. (Windows: py -3). Crea docs/.env: complétalo
python3 docs/scripts/generar_docx.py                  # 7.
```

## Traer mejoras del template a un proyecto que borró `.git`

Los scripts son independientes del contenido, así que basta con reemplazar `scripts/`:

```bash
git clone --depth 1 https://github.com/jhoel0521/plantilla-docs-apa.git /tmp/template
cp /tmp/template/scripts/*.py docs/scripts/
python3 docs/scripts/verificar_entorno.py && python3 docs/scripts/generar_docx.py
git diff docs/scripts      # revisar antes del commit
```

No copies `capitulos/`, `documento.toml` ni `.env`: son de tu proyecto.
