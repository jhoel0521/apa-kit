"""Genera diagramas simples (PNG) en <documento>/recursos/diagramas/ con Pillow.

Uso: python .apa/scripts/diagramas.py [--doc carpeta]

Es un ejemplo del patrón "diagrama como código": el PNG se regenera desde aquí y se cita en
los capítulos con ![Título](../recursos/diagramas/archivo.png){#clave}. Agrega tus funciones.
"""
import _entorno  # noqa: F401  (usa .venv/ si existe)

import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).parent))
from _raiz import carpeta_documento  # noqa: E402

DOC = carpeta_documento()
SALIDA = DOC / "recursos" / "diagramas"
ESCALA = 2  # resolución x2 para que se vea nítido al imprimir


def fuente(tam):
    # Pillow busca estos nombres en las carpetas de fuentes de Windows, macOS y Linux.
    for nombre in ("segoeui.ttf", "arial.ttf", "Arial.ttf", "Helvetica.ttc", "LiberationSans-Regular.ttf",
                   "DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(nombre, tam * ESCALA)
        except OSError:
            continue
    return ImageFont.load_default(tam * ESCALA)  # Pillow >= 10.1: fuente escalable incluida


def flujo(nombre, pasos, ancho_caja=220, alto_caja=70, sep=60):
    """Diagrama de flujo horizontal: una caja por paso y flechas entre ellas."""
    s = ESCALA
    w = (len(pasos) * ancho_caja + (len(pasos) - 1) * sep + 40) * s
    h = (alto_caja + 40) * s
    img = Image.new("RGB", (w, h), "white")
    d = ImageDraw.Draw(img)
    f = fuente(14)
    for i, (titulo, detalle) in enumerate(pasos):
        x0 = (20 + i * (ancho_caja + sep)) * s
        y0 = 20 * s
        x1, y1 = x0 + ancho_caja * s, y0 + alto_caja * s
        d.rounded_rectangle([x0, y0, x1, y1], radius=8 * s, outline="black", width=2 * s, fill="#F2F2F2")
        cx = (x0 + x1) // 2
        d.text((cx, y0 + 22 * s), titulo, fill="black", font=f, anchor="mm")
        d.text((cx, y0 + 48 * s), detalle, fill="#404040", font=fuente(11), anchor="mm")
        if i < len(pasos) - 1:
            ay = (y0 + y1) // 2
            d.line([x1 + 6 * s, ay, x1 + (sep - 8) * s, ay], fill="black", width=2 * s)
            tip = x1 + (sep - 6) * s
            d.polygon([(tip, ay), (tip - 10 * s, ay - 6 * s), (tip - 10 * s, ay + 6 * s)], fill="black")
    SALIDA.mkdir(parents=True, exist_ok=True)
    ruta = SALIDA / f"{nombre}.png"
    img.save(ruta)
    print("OK", ruta.relative_to(DOC))


if __name__ == "__main__":
    flujo("flujo-documento", [
        ("capitulos/*.md", "contenido"),
        ("generar_docx.py", "formato APA 7"),
        ("dist/<salida>.docx", "Word: actualizar campos"),
    ])
