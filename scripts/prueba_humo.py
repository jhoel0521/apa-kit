"""Prueba de humo: crea un Word de ejemplo, lo importa y genera el documento en una copia temporal.

Uso:  python3 scripts/prueba_humo.py     (en Windows: py -3 scripts/prueba_humo.py)
Termina con código 0 si todo funciona. No toca tus capítulos, tu .env ni tu carpeta dist/.
Sirve para comprobar una instalación nueva (Windows, macOS, Linux) y como prueba automática en CI.
"""
import _entorno  # noqa: F401  (usa .venv/ si existe)

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

DOCS = Path(__file__).resolve().parents[1]


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


def ejecutar(copia, *args):
    env = {**os.environ, "PYTHONIOENCODING": "utf-8", "PLANTILLA_SIN_VENV": "1"}
    r = subprocess.run([sys.executable, *args], cwd=copia, capture_output=True, text=True,
                       encoding="utf-8", errors="replace", env=env)
    return r.returncode, (r.stdout + r.stderr).strip()


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    from PIL import Image
    fallos = []
    with tempfile.TemporaryDirectory(prefix="plantilla-humo-") as tmp:
        tmp = Path(tmp)
        copia = tmp / "plantilla"
        shutil.copytree(DOCS, copia, ignore=shutil.ignore_patterns(
            ".git", ".venv", "dist", "original", "__pycache__", ".env", "_antes-de-importar-*"))
        (copia / "dist").mkdir()
        Image.new("RGB", (200, 100), "#4477aa").save(tmp / "figura.png")
        crear_word(tmp / "ejemplo.docx", tmp / "figura.png")

        pasos = [
            ("generar la plantilla tal cual", ["scripts/generar_docx.py"], None),
            ("importar un Word", ["scripts/importar_docx.py", str(tmp / "ejemplo.docx")], None),
            ("generar el documento importado", ["scripts/generar_docx.py", "--forzar"], None),
            ("mostrar el avance", ["scripts/generar_docx.py", "--estado"], None),
        ]
        for nombre, args, _ in pasos:
            code, salida = ejecutar(copia, *args)
            print(("OK    " if code == 0 else "FALLO ") + nombre)
            if code != 0:
                fallos.append(nombre)
                print("      " + "\n      ".join(salida.splitlines()[-8:]))

        docx = copia / "dist" / "Tesis.docx"
        if docx.exists():
            from docx import Document
            d = Document(docx)
            titulos = [p.text for p in d.paragraphs if p.style.name.startswith("Heading")]
            textos = "\n".join(p.text for p in d.paragraphs)
            controles = [("tiene capítulos importados", any("Introducción" in t for t in titulos)),
                         ("conserva la tabla", len(d.tables) == 1),
                         ("conserva la figura", len(d.inline_shapes) == 1),
                         ("resuelve las referencias cruzadas (Cuadro/Figura)", "@" not in textos),
                         ("conserva acentos y ñ", "ñ" in textos and "ü" in textos)]
            for nombre, ok in controles:
                print(("OK    " if ok else "FALLO ") + nombre)
                if not ok:
                    fallos.append(nombre)
        else:
            fallos.append("no se creó dist/Tesis.docx")
            print("FALLO no se creó dist/Tesis.docx")

    print("\nRESULTADO:", "todo bien" if not fallos else f"{len(fallos)} fallo(s): " + "; ".join(fallos))
    sys.exit(1 if fallos else 0)


if __name__ == "__main__":
    main()
