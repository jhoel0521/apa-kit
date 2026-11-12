"""Prueba de humo de apa-kit: prepara proyectos temporales con iniciar.py y genera documentos reales.

Uso:  python3 tests/prueba_humo.py        (en Windows: py -3 tests/prueba_humo.py)
Termina con código 0 si todo funciona. No toca nada fuera de una carpeta temporal.
Sirve para comprobar una instalación nueva (Windows, macOS, Linux) y como prueba automática en CI.
Requiere python-docx y Pillow (python3 skills/apa-init/assets/scripts/verificar_entorno.py --instalar
instala lo que falte, pero lo hace dentro de .apa/, así que en el repo usa: pip install -r
skills/apa-init/assets/scripts/requirements.txt).
"""
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
ASSETS = REPO / "skills" / "apa-init" / "assets"
INICIAR = ASSETS / "scripts" / "iniciar.py"
FIXTURES = REPO / "tests" / "fixtures"

fallos = []


def ok(nombre, condicion, detalle=""):
    print(("OK    " if condicion else "FALLO ") + nombre + (f"  [{detalle}]" if detalle and not condicion else ""))
    if not condicion:
        fallos.append(nombre)
    return condicion


def correr(cwd, *args):
    env = {**os.environ, "PYTHONIOENCODING": "utf-8", "APA_SIN_VENV": "1", "PYTHONDONTWRITEBYTECODE": "1"}
    env.pop("APA_DOC", None)
    r = subprocess.run([sys.executable, "-B", *map(str, args)], cwd=cwd, capture_output=True, text=True,
                       encoding="utf-8", errors="replace", env=env)
    return r.returncode, (r.stdout + r.stderr).strip()


def listado(base):
    return sorted(str(p.relative_to(base)) for p in base.rglob("*") if "__pycache__" not in p.parts)


def huella_carpeta(base):
    h = hashlib.sha256()
    for p in sorted(base.rglob("*")):
        if p.is_file():
            h.update(str(p.relative_to(base)).encode() + p.read_bytes())
    return h.hexdigest()


def crear_word(ruta, imagen):
    from docx import Document
    d = Document()
    d.add_heading("Capítulo I. Introducción", 1)
    p = d.add_paragraph("El presente trabajo analiza la norma según el Cuadro 1 y la ")
    p.add_run("Figura 1").bold = True
    p.add_run(". Incluye ")
    p.add_run("cursiva").italic = True
    p.add_run(" y acentos: ñ, á, é, í, ó, ú, ü.")
    d.add_heading("1.1. Planteamiento del problema", 2)
    d.add_paragraph("Primer elemento", style="List Bullet")
    d.add_paragraph("Segundo elemento", style="List Bullet")
    cap = d.add_paragraph()
    cap.add_run("Cuadro 1").bold = True
    d.add_paragraph("Comparación de normas")
    t = d.add_table(rows=3, cols=2)
    for i, fila in enumerate([("Norma", "Artículo"), ("Código Civil", "984"), ("Ley 1178", "31")]):
        for j, v in enumerate(fila):
            t.cell(i, j).text = v
    d.add_paragraph("Fuente: Elaboración propia.")
    d.add_picture(str(imagen))
    d.add_paragraph("Figura 1. Imagen de prueba")
    d.add_heading("Capítulo II. Marco teórico", 1)
    d.add_paragraph("Según Kelsen (1960), la norma fundamental es el punto de partida.")
    d.add_heading("Referencias", 1)
    d.add_paragraph("Kelsen, H. (1960). Teoría pura del derecho. Eudeba.")
    d.save(ruta)


def titulos_nivel1(docx):
    from docx import Document
    return [(p.text, bool(p.paragraph_format.page_break_before))
            for p in Document(docx).paragraphs if p.style.name == "Heading 1"]


def probar_tipos(tmp):
    """Cada tipo: iniciar.py -> generar_docx.py -> el .docx respeta numeración y saltos del tipo."""
    antes = listado(ASSETS.parent)
    proyecto = tmp / "proyecto"
    proyecto.mkdir()
    for tipo, numerado, salta in (("tesis", True, True), ("libre", False, False)):
        code, sal = correr(proyecto, INICIAR, "--tipo", tipo, "--destino", tipo)
        ok(f"iniciar.py crea el tipo '{tipo}'", code == 0, sal[-300:])
        if code != 0:
            continue
        code, sal = correr(proyecto, ".apa/scripts/generar_docx.py", "--doc", tipo)
        ok(f"genera el tipo '{tipo}'", code == 0, sal[-300:])
        docx = proyecto / tipo / "dist" / f"{ {'tesis': 'Tesis', 'libre': 'Documento'}[tipo] }.docx"
        if not ok(f"existe dist/{docx.name}", docx.exists()):
            continue
        t1 = titulos_nivel1(docx)
        cuerpo = [t for t in t1 if t[0] and not t[0].startswith(("Referencias", "Anexos"))]  # {.sin-numero}
        ok(f"'{tipo}': títulos {'con' if numerado else 'sin'} «Capítulo N.»",
           bool(cuerpo) and all(t[0].startswith("Capítulo") == numerado for t in cuerpo), str(t1))
        ok(f"'{tipo}': nivel 1 {'empieza' if salta else 'NO empieza'} página nueva",
           bool(cuerpo) and all(t[1] == salta for t in cuerpo), str(t1))
        ref = [t for t in t1 if t[0].startswith("Referencias")]
        ok(f"'{tipo}': Referencias siempre en página nueva", bool(ref) and ref[0][1] is True, str(t1))
    ok("iniciar.py no escribió nada dentro de la skill", listado(ASSETS.parent) == antes)
    ok("el motor quedó copiado en .apa/scripts/", (proyecto / ".apa" / "scripts" / "generar_docx.py").exists())
    ok("cada documento trae su .gitignore", (proyecto / "tesis" / ".gitignore").exists())

    code, sal = correr(proyecto, ".apa/scripts/generar_docx.py", "--estado")
    ok("con varios documentos pide elegir con --doc", code != 0 and "--doc" in sal, sal[-200:])

    code, sal = correr(proyecto, ".apa/scripts/verificar_entorno.py", "--doc", "tesis")
    ok("verificar_entorno.py termina sin errores", code == 0, sal[-400:])
    return proyecto


def probar_importar(tmp, proyecto):
    from PIL import Image
    Image.new("RGB", (200, 100), "#4477aa").save(tmp / "figura.png")
    crear_word(tmp / "ejemplo.docx", tmp / "figura.png")
    code, sal = correr(proyecto, ".apa/scripts/importar_docx.py", tmp / "ejemplo.docx", "--doc", "tesis")
    ok("importa un Word", code == 0, sal[-300:])
    code, sal = correr(proyecto, ".apa/scripts/generar_docx.py", "--doc", "tesis", "--forzar")
    ok("genera el documento importado", code == 0, sal[-300:])
    docx = proyecto / "tesis" / "dist" / "Tesis.docx"
    if docx.exists():
        from docx import Document
        d = Document(docx)
        textos = "\n".join(p.text for p in d.paragraphs)
        ok("importado: tiene el capítulo Introducción", any("Introducción" in t for t, _ in titulos_nivel1(docx)))
        ok("importado: conserva la tabla", len(d.tables) == 1)
        ok("importado: conserva la figura", len(d.inline_shapes) == 1)
        ok("importado: resuelve las referencias cruzadas", "@" not in textos)
        ok("importado: conserva acentos y ñ", "ñ" in textos and "ü" in textos)


def probar_sincronizar(proyecto):
    caps = huella_carpeta(proyecto / "libre" / "capitulos")
    motor = proyecto / ".apa" / "scripts" / "generar_docx.py"
    motor.write_text("# estropeado\n", encoding="utf-8")
    code, sal = correr(proyecto, INICIAR, "--sincronizar")
    ok("--sincronizar restaura el motor", code == 0 and "estropeado" not in motor.read_text(encoding="utf-8"), sal[-200:])
    ok("--sincronizar no toca los capítulos", huella_carpeta(proyecto / "libre" / "capitulos") == caps)


def probar_revisar(proyecto):
    """revisar.py lista candidatos: una cita sin referencia, una referencia sin cita y las marcas."""
    caps = proyecto / "libre" / "capitulos"
    capitulo = "\n".join([
        "# Introducción",
        "",
        "Según Kelsen (1960) la norma es el origen. Lo discuten (Pérez & Díaz, 2020; García et al., 2018a).",
        "El marco es amplio (American Psychological Association [APA], 2020, p. 12). [[pendiente: agregar cifra]]",
        "",
        "```",
        "(Ejemplo, 1999) código ignorado",
        "```",
        "<!-- (Oculto, 2001) comentario ignorado -->",
        ""])
    referencias = "\n".join([
        "# Referencias {.sin-numero}",
        "",
        "American Psychological Association. (2020). *Manual*. APA.",
        "Kelsen, H. (1960). Teoría pura del derecho. Eudeba.",
        "García, M., & Ruiz, P. (2018). Sobre normas. X. [[verificar]]",
        "Rawls, J. (1971). *A theory of justice*. Harvard University Press.",
        ""])
    (caps / "01-primera-seccion.md").write_text(capitulo, encoding="utf-8")
    (caps / "90-referencias.md").write_text(referencias, encoding="utf-8")
    code, sal = correr(proyecto, ".apa/scripts/revisar.py", "--doc", "libre")
    ok("revisar.py termina con código 0", code == 0, sal[-200:])
    ok("revisar.py detecta la cita sin referencia (Pérez)", "Pérez (2020)" in sal, sal)
    ok("revisar.py detecta la referencia sin cita (Rawls)", "Rawls (1971)" in sal, sal)
    ok("revisar.py no marca lo bien citado (Kelsen, García 2018a, APA)",
       not any(f"{a} (" in sal.split("Referencias que no se citan")[0].split("Citas sin referencia")[1]
               for a in ("Kelsen", "García", "American")), sal)
    ok("revisar.py ignora código y comentarios", "Ejemplo" not in sal and "Oculto" not in sal, sal)
    ok("revisar.py cuenta pendiente y verificar", "Pendientes: 1" in sal and "Por verificar" in sal and ": 1" in sal)
    code, _ = correr(proyecto, ".apa/scripts/revisar.py", "--doc", "libre", "--estricto")
    ok("revisar.py --estricto termina con código 1 si queda algo", code == 1)


def probar_migrar(tmp):
    """Un documento del diseño antiguo se genera igual que antes y sigue protegido contra regeneración."""
    proyecto = tmp / "antiguo"
    shutil.copytree(FIXTURES / "diseno-antiguo", proyecto)
    huellas = proyecto / "docs" / "dist" / ".huellas.json"
    huellas.parent.mkdir(exist_ok=True)
    huellas.write_text(json.dumps({"Documento.docx": "abc"}), encoding="utf-8")
    code, sal = correr(proyecto, INICIAR, "--migrar", "docs")
    ok("--migrar convierte el diseño antiguo", code == 0, sal[-300:])
    ok("--migrar conserva dist/.huellas.json", huellas.exists() and json.loads(huellas.read_text())["Documento.docx"] == "abc")
    texto = (proyecto / "docs" / "documento.toml").read_text(encoding="utf-8")
    for clave in ("numerar_titulos = true", "salto_nivel1 = true", 'idioma = "es-BO"', 'salida = "Documento"'):
        ok(f"--migrar escribe explícito: {clave}", clave in texto)
    (proyecto / "docs" / "dist" / ".huellas.json").unlink()
    code, sal = correr(proyecto, ".apa/scripts/generar_docx.py")
    docx = proyecto / "docs" / "dist" / "Documento.docx"
    ok("migrado: genera sin indicar --doc", code == 0 and docx.exists(), sal[-300:])
    if docx.exists():
        t1 = titulos_nivel1(docx)
        ok("migrado: conserva «Capítulo N.» y salto de página", t1 and t1[0][0].startswith("Capítulo 1.") and t1[0][1], str(t1))
        from docx import Document
        ok("migrado: conserva el idioma es-BO", Document(docx).core_properties.language == "es-BO")
        d = Document(docx)
        d.add_paragraph("editado a mano en Word")
        d.save(docx)
        code, sal = correr(proyecto, ".apa/scripts/generar_docx.py")
        ok("migrado: un .docx editado a mano sigue protegido", code != 0 and "ALTO" in sal, sal[-200:])


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    with tempfile.TemporaryDirectory(prefix="apa-kit-humo-") as tmp:
        tmp = Path(tmp)
        proyecto = probar_tipos(tmp)
        probar_importar(tmp, proyecto)
        probar_sincronizar(proyecto)
        probar_revisar(proyecto)
        probar_migrar(tmp)
    print("\nRESULTADO:", "todo bien" if not fallos else f"{len(fallos)} fallo(s): " + "; ".join(fallos))
    sys.exit(1 if fallos else 0)


if __name__ == "__main__":
    main()
