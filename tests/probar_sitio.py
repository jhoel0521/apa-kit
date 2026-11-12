"""Revisa el sitio (sitio/): SEO, vista previa al compartir, imágenes y sitemap. Solo biblioteca estándar.

Uso:  python3 tests/probar_sitio.py        (en Windows: py -3 tests/probar_sitio.py)
Termina con código 1 si algo falla. Lo ejecuta la CI en cada PR que toca sitio/.
"""
import json
import re
import sys
from pathlib import Path

SITIO = Path(__file__).resolve().parents[1] / "sitio"
URL = "https://jhoel0521.github.io/apa-kit/"
fallos = []


def ok(nombre, condicion, detalle=""):
    print(("OK    " if condicion else "FALLO ") + nombre + (f"  [{detalle}]" if detalle and not condicion else ""))
    if not condicion:
        fallos.append(nombre)


def meta(html, clave, valor):
    m = re.search(rf'<meta\s+{clave}="{re.escape(valor)}"\s+content="([^"]*)"', html)
    return m.group(1) if m else None


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    html = (SITIO / "index.html").read_text(encoding="utf-8")
    titulo = re.search(r"<title>([^<]*)</title>", html)
    desc = meta(html, "name", "description")
    ok("tiene <title> de 60 caracteres o menos", bool(titulo) and len(titulo.group(1)) <= 60, titulo.group(1) if titulo else "")
    ok("tiene descripción de 160 caracteres o menos", bool(desc) and len(desc) <= 160, str(len(desc or "")))
    ok("tiene enlace canónico", f'<link rel="canonical" href="{URL}">' in html)
    for p in ("og:title", "og:description", "og:url", "og:image", "og:image:width", "og:image:height", "og:type"):
        ok(f"tiene {p}", meta(html, "property", p) is not None)
    ok("tiene twitter:card grande", meta(html, "name", "twitter:card") == "summary_large_image")
    ok("tiene twitter:image", meta(html, "name", "twitter:image") is not None)
    ok("tiene theme-color", meta(html, "name", "theme-color") is not None)
    ok("<html> declara el idioma", '<html lang="es">' in html)

    # Correcciones de la auditoría UX
    botones = re.findall(r"<button[^>]*data-copy[^>]*>[^<]*</button>", html)
    nombres = [(re.search(r'aria-label="([^"]*)"', b) or re.search(r">([^<]*)<", b)).group(1) for b in botones]
    ok("los botones de copiar tienen nombre accesible distinto", len(botones) >= 3 and len(set(nombres)) == len(nombres), str(nombres))
    ok("el aviso del móvil va antes de los botones principales", 0 <= html.find('id="movil"') < html.find('class="btns"'))
    ok("la descarga principal es un botón (.btn)", bool(re.search(r'<a class="btn" href="[^"]*apa-kit-cowork\.zip"', html)))
    ok("los controles tienen altura mínima de 44 px (nav, logo, resúmenes)",
       "min-height: 44px" in html and re.search(r"nav a \{[^}]*min-height: 44px", html) and re.search(r"summary \{[^}]*padding: 12px 0", html))
    ok("los botones heredan la fuente de la página", "button { font: inherit; }" in html)
    tamanos = set(re.findall(r"font-size: (var\(--fs-[a-z]+\)|\d+px|[\d.]+em|clamp\([^)]*\))", html))
    ok("la tipografía usa la escala de 4 tamaños (sin px sueltos)", all(t.startswith("var(--fs-") or t.startswith("clamp") for t in tamanos), str(sorted(tamanos)))
    ok("detecta el iPad (iPadOS se presenta como Mac)", "maxTouchPoints" in html)

    ld = re.search(r'ld\+json">\s*(\{.*?\})\s*</script>', html, re.S)
    try:
        datos = json.loads(ld.group(1)) if ld else {}
    except ValueError:
        datos = {}
    ok("datos estructurados (JSON-LD) válidos", datos.get("@type") == "SoftwareApplication" and datos.get("name") == "apa-kit")

    og = meta(html, "property", "og:image") or ""
    archivo = SITIO / re.sub(r"^" + re.escape(URL), "", og.split("?")[0])
    ok("la imagen de og:image existe", archivo.is_file(), str(archivo))
    ok("la imagen de compartir pesa menos de 300 KB (límite práctico de WhatsApp)",
       archivo.is_file() and archivo.stat().st_size < 300 * 1024, f"{archivo.stat().st_size // 1024 if archivo.is_file() else '?'} KB")
    locales = re.findall(r'(?:src|href)="(img/[^"?]+)', html)
    ok("todas las imágenes referenciadas existen", all((SITIO / r).is_file() for r in locales),
       str([r for r in locales if not (SITIO / r).is_file()]))

    mapa = (SITIO / "sitemap.xml").read_text(encoding="utf-8")
    ok("el sitemap incluye la URL canónica", f"<loc>{URL}</loc>" in mapa)
    viejos = [x for x in ("plantilla-docs-apa", "main.zip", "PROMPT_INICIAL", "GUIA_ESTUDIANTES", "Tesis.docx") if x in html]
    ok("no quedan referencias a la plantilla anterior", not viejos, str(viejos))
    enlaces = re.findall(r'github\.com/jhoel0521/apa-kit/blob/main/([^"#]+)', html)
    raiz = SITIO.parent
    ok("los archivos de GitHub que enlaza el sitio existen en el repositorio",
       all((raiz / e).is_file() for e in enlaces), str([e for e in enlaces if not (raiz / e).is_file()]))

    print("\nRESULTADO:", "todo bien" if not fallos else f"{len(fallos)} fallo(s): " + "; ".join(fallos))
    sys.exit(1 if fallos else 0)


if __name__ == "__main__":
    main()
