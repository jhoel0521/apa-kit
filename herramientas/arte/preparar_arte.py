"""Prepara el arte de apa-kit (logo, imagen para compartir e historia) a partir de tres imágenes generadas con IA.

Uso:
    python3 herramientas/arte/preparar_arte.py --logo logo.jpg --banner banner.jpg --historia historia.jpg

Entradas (las que entrega el generador de imágenes, sin texto):
    --logo       cuadrado, p. ej. 2048x2048 (fondo azul redondeado con la hoja y el sello «7»)
    --banner     horizontal, con el icono a la izquierda y espacio libre a la derecha
    --historia   vertical 9:16, con el icono en el centro
Salidas:
    sitio/img/   og.jpg (1200x630), story.jpg (1080x1920), logo-256.png, favicon-192.png, apple-touch-icon.png
    docs/img/    logo.png, logo-cuadrado-1024.png, social-preview.jpg (1280x640), story.jpg
Necesita Pillow (pip install Pillow). Los originales NO se guardan en el repositorio (pesan 1-2 MB cada uno).
Si cambias og.jpg, sube el «?v=» de la URL de og:image en sitio/index.html: WhatsApp y Facebook guardan la vista previa.
"""
import argparse
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

RAIZ = Path(__file__).resolve().parents[2]
AMBAR, TEXTO = "#f2b134", "#e8eef5"
LEMA = ("Tu tesis en formato APA 7,", "con tu asistente de IA")
ETIQUETA = "Markdown → Word · cualquier carrera"
ENLACE = "jhoel0521.github.io/apa-kit"


def fuente(negrita, tam):
    # Pillow busca estos nombres en las carpetas de fuentes de Windows, macOS y Linux.
    nombres = (["segoeuib.ttf", "arialbd.ttf", "Arial Bold.ttf", "DejaVuSans-Bold.ttf", "LiberationSans-Bold.ttf"] if negrita
               else ["segoeui.ttf", "arial.ttf", "Arial.ttf", "DejaVuSans.ttf", "LiberationSans-Regular.ttf"])
    for n in nombres:
        try:
            return ImageFont.truetype(n, tam)
        except OSError:
            continue
    return ImageFont.load_default(tam)


def es_azul(p):
    return p[2] > p[0] + 35 and p[2] > 70


def logo_cuadrado(ruta):
    """El JPG del generador trae las esquinas blancas: se rellenan para obtener un cuadrado a sangre."""
    img = Image.open(ruta).convert("RGB")
    L = img.size[0]
    azul = img.getpixel((int(L * 0.06), int(L * 0.5)))
    caja, px = int(L * 0.24), img.load()
    for ox, oy in ((0, 0), (L - caja, 0), (0, L - caja), (L - caja, L - caja)):
        for x in range(ox, ox + caja):
            for y in range(oy, oy + caja):
                if not es_azul(px[x, y]):
                    px[x, y] = azul
    return img.resize((1024, 1024), Image.LANCZOS)


def redondeado(img):
    mask = Image.new("L", (4096, 4096), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, 4095, 4095], radius=int(4096 * 0.22), fill=255)
    out = img.convert("RGBA")
    out.putalpha(mask.resize(img.size, Image.LANCZOS))
    return out


def paleta(img):
    """Pocos colores: el logo es plano y así pesa una fracción (el ruido del JPG lo infla)."""
    if img.mode == "RGBA":
        alfa = img.getchannel("A")
        q = img.convert("RGB").quantize(colors=48, dither=Image.Dither.NONE).convert("RGBA")
        q.putalpha(alfa)
        return q
    return img.convert("RGB").quantize(colors=48, dither=Image.Dither.NONE)


def banner(ruta, w, h):
    img = Image.open(ruta).convert("RGB")
    W, H = img.size
    alto = int(W * h / w)
    # el icono queda en el 49 % de la altura de la imagen original: se recorta alrededor de él
    top = max(0, min(H - alto, int(H * 0.49) - alto // 2))
    img = img.crop((0, top, W, top + alto)).resize((w, h), Image.LANCZOS)
    d, k, x = ImageDraw.Draw(img), h / 630, int(w * 0.43)
    d.text((x, int(h * 0.33)), "apa-kit", font=fuente(True, int(118 * k)), fill="white", anchor="lm")
    d.text((x, int(h * 0.55)), LEMA[0], font=fuente(False, int(42 * k)), fill=TEXTO, anchor="lm")
    d.text((x, int(h * 0.65)), LEMA[1], font=fuente(False, int(42 * k)), fill=TEXTO, anchor="lm")
    d.text((x, int(h * 0.82)), ETIQUETA, font=fuente(False, int(29 * k)), fill=AMBAR, anchor="lm")
    return img


def historia(ruta):
    """9:16; el texto queda por encima de los últimos 340 px, que las apps de historias tapan con sus botones."""
    img = Image.open(ruta).convert("RGB")
    W, H = img.size
    alto = int(W * 16 / 9)
    img = img.crop((0, (H - alto) // 2, W, (H - alto) // 2 + alto)).resize((1080, 1920), Image.LANCZOS)
    d = ImageDraw.Draw(img)
    d.text((540, 1305), "apa-kit", font=fuente(True, 122), fill="white", anchor="mm")
    d.text((540, 1430), LEMA[0], font=fuente(False, 54), fill=TEXTO, anchor="mm")
    d.text((540, 1495), LEMA[1], font=fuente(False, 54), fill=TEXTO, anchor="mm")
    d.text((540, 1558), ENLACE, font=fuente(True, 36), fill=AMBAR, anchor="mm")
    return img


def jpeg(img, ruta):
    img.convert("RGB").save(ruta, quality=84, optimize=True, progressive=True, subsampling=0)


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    for k in ("logo", "banner", "historia"):
        ap.add_argument(f"--{k}", required=True, type=Path)
    ap.add_argument("--sitio", type=Path, default=RAIZ / "sitio" / "img")
    ap.add_argument("--docs", type=Path, default=RAIZ / "docs" / "img")
    a = ap.parse_args()
    a.sitio.mkdir(parents=True, exist_ok=True)
    a.docs.mkdir(parents=True, exist_ok=True)

    cuadrado = logo_cuadrado(a.logo)
    redondo = redondeado(cuadrado)
    paleta(redondo.resize((256, 256), Image.LANCZOS)).save(a.sitio / "logo-256.png", optimize=True)
    paleta(redondo.resize((192, 192), Image.LANCZOS)).save(a.sitio / "favicon-192.png", optimize=True)
    paleta(cuadrado.resize((180, 180), Image.LANCZOS)).save(a.sitio / "apple-touch-icon.png", optimize=True)
    paleta(redondo.resize((256, 256), Image.LANCZOS)).save(a.docs / "logo.png", optimize=True)
    paleta(cuadrado).save(a.docs / "logo-cuadrado-1024.png", optimize=True)
    jpeg(banner(a.banner, 1200, 630), a.sitio / "og.jpg")
    jpeg(banner(a.banner, 1280, 640), a.docs / "social-preview.jpg")
    hist = historia(a.historia)
    jpeg(hist, a.sitio / "story.jpg")
    jpeg(hist, a.docs / "story.jpg")
    for carpeta in (a.sitio, a.docs):
        for f in sorted(carpeta.glob("*")):
            print(f"{f.relative_to(RAIZ) if RAIZ in f.parents else f}  {Image.open(f).size}  {f.stat().st_size // 1024} KB")


if __name__ == "__main__":
    main()
