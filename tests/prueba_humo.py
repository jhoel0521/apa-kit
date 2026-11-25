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


PORTADA_MINIMA = """bloques = [
  { texto = "{{TITULO}}", negrita = true },
  { texto = "{{AUTOR}}" },
]"""


def definir_portada(carpeta, bloques=PORTADA_MINIMA):
    """Los tipos nuevos traen la portada sin definir (bloques = []): la prueba hace lo que haría la entrevista."""
    toml = carpeta / "documento.toml"
    texto = toml.read_text(encoding="utf-8")
    ok(f"{carpeta.name}: el tipo trae la portada sin definir (bloques = [])", "bloques = []" in texto)
    toml.write_text(texto.replace("bloques = []", bloques, 1), encoding="utf-8")


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


def comprobar_frontmatter(ruta, nombre_esperado):
    """YAML válido sin depender de PyYAML: sin «: » ni « #» dentro de valores sin comillas; name = carpeta."""
    import re
    texto = ruta.read_text(encoding="utf-8").replace("\r\n", "\n")
    m = re.match(r"---\n(.*?)\n---\n", texto, re.S)
    if not ok(f"{ruta.parent.name}: SKILL.md tiene frontmatter", m is not None):
        return
    campos = {}
    for ln in m.group(1).splitlines():
        sup = re.match(r"^([a-z][\w-]*):(?:\s+(.*))?$", ln)              # clave de primer nivel
        if sup:
            campos[sup.group(1)] = sup.group(2) or ""
            valor = sup.group(2) or ""
            if valor and valor[0] not in "\"'" and (": " in valor or " #" in valor):
                ok(f"{ruta.parent.name}: YAML válido en «{sup.group(1)}»", False, valor[:60])
        elif not re.match(r"^\s{2}[a-z][\w-]*:\s", ln):
            ok(f"{ruta.parent.name}: línea de frontmatter reconocible", False, ln[:60])
    ok(f"{ruta.parent.name}: name = «{nombre_esperado}»", campos.get("name") == nombre_esperado, str(campos.get("name")))
    ok(f"{ruta.parent.name}: tiene description y license", bool(campos.get("description")) and bool(campos.get("license")))
    try:
        import yaml  # solo si está instalado: parser real
        datos = yaml.safe_load(m.group(1))
        ok(f"{ruta.parent.name}: lo acepta un parser YAML real", isinstance(datos, dict))
    except ImportError:
        pass
    except Exception as e:
        ok(f"{ruta.parent.name}: lo acepta un parser YAML real", False, str(e)[:80])


def probar_skills():
    carpetas = sorted(p for p in (REPO / "skills").iterdir() if (p / "SKILL.md").exists())
    ok("existen las seis skills", [p.name for p in carpetas] ==
       ["apa-escribir", "apa-generar", "apa-guia", "apa-importar", "apa-init", "apa-revisar"], str([p.name for p in carpetas]))
    for p in carpetas:
        comprobar_frontmatter(p / "SKILL.md", p.name)
    # Lo que trae una plantilla sale tal cual en el Word del autor: sin rayas, flechas ni emojis.
    sucios = [f"{r.relative_to(REPO)}: {c}" for r in sorted((REPO / "skills" / "apa-init" / "assets" / "tipos").rglob("*"))
              if r.suffix in (".md", ".toml") for c in "—–→" if c in r.read_text(encoding="utf-8")]
    ok("las plantillas de los tipos no traen rayas ni flechas", not sucios, str(sucios))


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
        definir_portada(proyecto / tipo)
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
        from docx import Document
        texto = "\n".join(p.text for p in Document(docx).paragraphs)
        ok(f"'{tipo}': sin tablas ni figuras no hay listas vacías (#12)",
           "Lista de Tablas" not in texto and "Lista de Figuras" not in texto
           and "no se genera la lista de tablas" in sal and "no se genera la lista de figuras" in sal, sal[-300:])
        ok(f"'{tipo}': el aviso del índice da los atajos correctos (#11)",
           "Ctrl+E en Word en español" in texto and "Actualizar todo" in texto and "(Ctrl+A, F9)" not in texto)
    ok("iniciar.py no escribió nada dentro de la skill", listado(ASSETS.parent) == antes)
    ok("el motor quedó copiado en .apa/scripts/", (proyecto / ".apa" / "scripts" / "generar_docx.py").exists())
    ok("cada documento trae su .gitignore", (proyecto / "tesis" / ".gitignore").exists())

    code, sal = correr(proyecto, ".apa/scripts/generar_docx.py", "--estado")
    ok("con varios documentos pide elegir con --doc", code != 0 and "--doc" in sal, sal[-200:])
    code, sal = correr(proyecto, "-c", "import sys; sys.path.insert(0, '.apa/scripts'); sys.argv = ['x', '--doc', 'libre']; "
                                       "import os, _raiz; _raiz.carpeta_documento(); print(os.environ['APA_DOC'])")
    ok("--doc se exporta a APA_DOC (sobrevive al relanzar dentro de .venv)",
       code == 0 and sal.strip().endswith("libre"), sal[-200:])

    code, sal = correr(proyecto, ".apa/scripts/verificar_entorno.py", "--doc", "tesis")
    ok("verificar_entorno.py termina sin errores", code == 0, sal[-400:])
    return proyecto


def probar_demas_tipos(tmp):
    """Los tipos restantes se generan, y los trabajos profesionales traen encabezado, nota del autor y título repetido."""
    from docx import Document
    proyecto = tmp / "otros"
    proyecto.mkdir()
    esperado = {"trabajo-estudiante": "Trabajo", "informe": "Informe", "tesis-software": "Tesis", "articulo": "Articulo"}
    for tipo, salida in esperado.items():
        code, sal = correr(proyecto, INICIAR, "--tipo", tipo, "--destino", tipo)
        ok(f"iniciar.py crea el tipo '{tipo}'", code == 0, sal[-300:])
        definir_portada(proyecto / tipo)
        code, sal = correr(proyecto, ".apa/scripts/generar_docx.py", "--doc", tipo)
        docx = proyecto / tipo / "dist" / f"{salida}.docx"
        if not ok(f"genera el tipo '{tipo}'", code == 0 and docx.exists(), sal[-400:]):
            continue
        d = Document(docx)
        parrafos = [p.text for p in d.paragraphs]
        encabezado = d.sections[0].header.paragraphs[0].text
        titulos = titulos_nivel1(docx)
        if tipo == "articulo":
            ok("articulo: encabezado con título corto y número de página",
               "TÍTULO CORTO" in encabezado and "PAGE" in d.sections[0].header.paragraphs[0]._p.xml, encabezado)
            ok("articulo: nota del autor en la portada", "Nota del autor" in parrafos)
            ok("articulo: el título se repite al comenzar el texto", sum("Título del artículo" in t for t in parrafos) == 2)
            ok("articulo: sin números ni saltos en los títulos",
               all(not t[0][:1].isdigit() and not t[1] for t in titulos if not t[0].startswith("Referencias")), str(titulos))
        elif tipo == "trabajo-estudiante":
            ok("trabajo-estudiante: sin encabezado de título corto", "TÍTULO" not in encabezado.upper(), encabezado)
            ok("trabajo-estudiante: el título se repite al comenzar el texto",
               sum("Título del trabajo" in t for t in parrafos) == 2)
            ok("trabajo-estudiante: sin índice (no hay Heading de contenido)", not any(t == "Contenido" for t in parrafos))
        elif tipo == "informe":
            ok("informe: secciones numeradas «1. Introducción» sin salto de página",
               any(t[0].startswith("1. ") for t in titulos) and not any(t[1] for t in titulos if t[0][:1].isdigit()), str(titulos))
        elif tipo == "tesis-software":
            ok("tesis-software: usa la variable NOMBRE_SISTEMA", any("Nombre del sistema" in t for t in parrafos))
            ok("tesis-software: capítulos de análisis y pruebas", any("Desarrollo del Proyecto" in t[0] for t in titulos)
               and any("Pruebas y Resultados" in t[0] for t in titulos), str(titulos))
    code, sal = correr(proyecto, INICIAR, "--listar")
    ok("iniciar.py --listar muestra los seis tipos",
       all(t in sal for t in ("tesis", "tesis-software", "libre", "informe", "articulo", "trabajo-estudiante")), sal)


def probar_tablas_juntas(tmp):
    """Las tablas no parten filas y van atadas a su nota (se comprueba en el XML; la paginación real depende de Word)."""
    from docx import Document
    from docx.oxml.ns import qn
    proyecto = tmp / "tablas"
    proyecto.mkdir()
    correr(proyecto, INICIAR, "--tipo", "libre", "--destino", "doc")
    definir_portada(proyecto / "doc")
    (proyecto / "doc" / "capitulos" / "01-primera-seccion.md").write_text("\n".join([
        "# Tablas", "", "Tabla: Una tabla {#t1}", "", "| A | B |", "|---|---|", "| 1 | uno<br>dos |", "| 2 | tres |", "",
        "Nota: la nota.", ""]), encoding="utf-8")
    code, sal = correr(proyecto, ".apa/scripts/generar_docx.py", "--doc", "doc")
    docx = proyecto / "doc" / "dist" / "Documento.docx"
    if not ok("genera un documento con una tabla", code == 0 and docx.exists(), sal[-300:]):
        return
    parrafos = [p.text for p in Document(docx).paragraphs]
    ok("con una tabla y sin figuras solo se genera la lista de tablas (#12)",
       "Lista de Tablas" in parrafos and "Lista de Figuras" not in parrafos
       and "no se genera la lista de figuras" in sal, str([p for p in parrafos if p.startswith("Lista")]))
    t = Document(docx).tables[0]
    ok("tablas: ninguna fila se parte (cantSplit)",
       all(f._tr.trPr is not None and f._tr.trPr.find(qn("w:cantSplit")) is not None for f in t.rows))
    ok("tablas: todas las filas van con la siguiente, la última con la nota",
       all(p.paragraph_format.keep_with_next for f in t.rows for c in f.cells for p in c.paragraphs))
    ok("tablas: la celda admite salto de línea con <br>", len(t.rows[1].cells[1].paragraphs) == 2)
    # con tablas_juntas = false las filas fluyen libres
    toml = proyecto / "doc" / "documento.toml"
    toml.write_text(toml.read_text(encoding="utf-8").replace("[documento]", "[documento]\ntablas_juntas = false", 1), encoding="utf-8")
    code, sal = correr(proyecto, ".apa/scripts/generar_docx.py", "--doc", "doc", "--forzar")
    t = Document(docx).tables[0]
    ok("tablas_juntas = false deja las filas libres", code == 0 and not any(
        p.paragraph_format.keep_with_next for f in t.rows for c in f.cells for p in c.paragraphs), sal[-200:])


def probar_paquete(tmp):
    """El paquete único para Cowork funciona extraído en una carpeta cualquiera, sin el resto del repositorio."""
    import zipfile
    salida = tmp / "paquetes"
    code, sal = correr(REPO, REPO / "herramientas" / "empaquetar.py", "--salida", salida)
    ok("empaquetar.py crea los paquetes", code == 0 and (salida / "apa-kit-cowork.zip").exists(), sal[-300:])
    for nombre in ("apa-kit-plugin.zip", "apa-init.zip", "apa-guia.zip"):
        ok(f"existe {nombre}", (salida / nombre).exists())
    if not (salida / "apa-kit-cowork.zip").exists():
        return
    extraido = tmp / "cowork"
    zipfile.ZipFile(salida / "apa-kit-cowork.zip").extractall(extraido)
    skill = extraido / "apa-kit"
    comprobar_frontmatter(skill / "SKILL.md", "apa-kit")
    ok("el paquete único trae SKILL.md, flujos y referencias",
       all((skill / x).exists() for x in ("SKILL.md", "flujos/apa-init.md", "flujos/apa-revisar.md", "references/sintaxis.md")))
    antes = listado(skill)
    proyecto = tmp / "proyecto-cowork"
    proyecto.mkdir()
    code, sal = correr(proyecto, skill / "assets" / "scripts" / "iniciar.py", "--tipo", "articulo", "--destino", "mi-articulo")
    ok("el paquete único crea un documento", code == 0, sal[-300:])
    ok("el paquete único trae la guía de portadas", (skill / "references" / "portadas.md").exists())
    definir_portada(proyecto / "mi-articulo")
    code, sal = correr(proyecto, ".apa/scripts/generar_docx.py")
    ok("el paquete único genera el Word", code == 0 and (proyecto / "mi-articulo" / "dist" / "Articulo.docx").exists(), sal[-300:])
    ok("el paquete único no se modifica al usarlo", listado(skill) == antes)


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


def portada_ejemplo(nombre):
    """Bloque TOML de un ejemplo de skills/apa-init/references/portadas.md (lo que copia el agente)."""
    import re
    texto = (REPO / "skills" / "apa-init" / "references" / "portadas.md").read_text(encoding="utf-8")
    m = re.search(rf"### {re.escape(nombre)}.*?```toml\n(.*?)```", texto, re.S)
    return m.group(1).strip() if m else ""


def parrafos_portada(docx):
    """Párrafos de la portada: hasta el primero que empieza página nueva."""
    from docx import Document
    salida = []
    for p in Document(docx).paragraphs:
        if p.paragraph_format.page_break_before:
            break
        salida.append(p)
    return salida


def probar_portada(tmp):
    """Portada por bloques (#13): no se genera sin definirla; definida, los datos faltantes salen en blanco."""
    import re
    proyecto = tmp / "portada"
    proyecto.mkdir()
    correr(proyecto, INICIAR, "--tipo", "informe", "--destino", "inf")
    toml = proyecto / "inf" / "documento.toml"
    docx = proyecto / "inf" / "dist" / "Informe.docx"
    original = toml.read_text(encoding="utf-8")
    code, sal = correr(proyecto, ".apa/scripts/generar_docx.py", "--doc", "inf")
    ok("portada sin definir: no se genera el Word", code != 0 and "portada sin definir" in sal and not docx.exists(), sal[-300:])
    toml.write_text(original.replace("bloques = []", 'bloques = [{ texto = "[[Nombre de la carrera]]" }]'), encoding="utf-8")
    code, sal = correr(proyecto, ".apa/scripts/generar_docx.py", "--doc", "inf")
    ok("portada con texto de plantilla [[…]]: no se genera el Word", code != 0 and not docx.exists(), sal[-300:])
    toml.write_text(original.replace("bloques = []", 'bloques = [{ color = "rojo" }]'), encoding="utf-8")
    code, sal = correr(proyecto, ".apa/scripts/generar_docx.py", "--doc", "inf")
    ok("portada con un bloque desconocido: error claro", code != 0 and "no reconocido" in sal and not docx.exists(), sal[-300:])

    ejemplo = portada_ejemplo("Estándar universidades privadas de Bolivia")
    ok("portadas.md trae el ejemplo bolivia-privada", "Arial Black" in ejemplo, ejemplo[:200])
    toml.write_text(re.sub(r"\[portada\].*?(?=\n\[preliminares\])", lambda _: ejemplo, original, flags=re.S),
                    encoding="utf-8")
    code, sal = correr(proyecto, ".apa/scripts/generar_docx.py", "--doc", "inf")
    if not ok("el ejemplo bolivia-privada genera el Word", code == 0 and docx.exists(), sal[-400:]):
        return
    portada = parrafos_portada(docx)
    runs = [r for p in portada for r in p.runs if r.text.strip()]
    ok("bolivia-privada: la portada usa Arial Black", runs and all(r.font.name == "Arial Black" for r in runs),
       str([(r.text, r.font.name) for r in runs]))
    ok("bolivia-privada: el título sale de [documento].titulo", any("Título del informe" in p.text for p in portada))
    ok("portada definida sin .env: los datos faltantes salen en blanco, no como [[CLAVE]]",
       not any("ACTIVIDAD" in p.text or "DOCENTE" in p.text for p in portada) and "salen en blanco" in sal, sal[-400:])
    (proyecto / "inf" / ".env").write_text("AUTOR=Ana Pérez\nCARRERA=Carrera de ejemplo\n", encoding="utf-8")
    code, sal = correr(proyecto, ".apa/scripts/generar_docx.py", "--doc", "inf")
    portada = parrafos_portada(docx)
    ok("portada: usa los datos de .env", code == 0 and any(p.text == "Ana Pérez" for p in portada), sal[-300:])
    runs = [r for p in portada for r in p.runs if r.text.strip()]
    ok("bolivia-privada: tamaños 20, 14 y 12", {r.font.size.pt for r in runs if r.font.size} == {20.0, 14.0, 12.0},
       str({r.font.size.pt for r in runs if r.font.size}))


def probar_compatibilidad_02(tmp):
    """Un documento 0.2 (portada con lineas, sin bloques) se genera como antes y --sincronizar no lo toca."""
    proyecto = tmp / "v02"
    proyecto.mkdir()
    correr(proyecto, INICIAR, "--tipo", "libre", "--destino", "doc")
    toml = proyecto / "doc" / "documento.toml"
    texto = toml.read_text(encoding="utf-8").replace('subtitulo = ""', 'subtitulo = "Subtítulo antiguo"')
    texto = texto.replace("bloques = []", 'lineas = [\n  "{{AUTOR}}",\n  "Línea antigua",\n]')
    toml.write_text(texto, encoding="utf-8")
    antes = toml.read_bytes()
    code, sal = correr(proyecto, ".apa/scripts/generar_docx.py", "--doc", "doc")
    docx = proyecto / "doc" / "dist" / "Documento.docx"
    if not ok("documento 0.2 (lineas, sin bloques): se genera", code == 0 and docx.exists(), sal[-300:]):
        return
    textos = [p.text for p in parrafos_portada(docx) if p.text.strip()]
    ok("documento 0.2: la portada sale como antes (título, subtítulo, líneas)",
       textos == ["Título del documento", "Subtítulo antiguo", "AUTOR", "Línea antigua"], str(textos))
    code, sal = correr(proyecto, INICIAR, "--sincronizar")
    ok("documento 0.2: --sincronizar no modifica documento.toml", code == 0 and toml.read_bytes() == antes, sal[-200:])


def probar_entorno(proyecto):
    """Un .apa/.venv/ a medio crear (sin python-docx) no atrapa a los scripts (#9)."""
    venv = proyecto / ".apa" / ".venv"
    for py in ("Scripts/python.exe", "bin/python3"):
        (venv / py).parent.mkdir(parents=True, exist_ok=True)
        (venv / py).write_text("", encoding="utf-8")
    consulta = "import sys; sys.path.insert(0, '.apa/scripts'); import _entorno; print(_entorno.venv_listo())"
    code, sal = correr(proyecto, "-c", consulta)
    ok("_entorno: un .venv sin python-docx no se usa", code == 0 and sal.strip().endswith("False"), sal[-200:])
    (venv / "lib" / "python3.12" / "site-packages" / "docx").mkdir(parents=True)
    code, sal = correr(proyecto, "-c", consulta)
    ok("_entorno: un .venv con python-docx sí se usa", code == 0 and sal.strip().endswith("True"), sal[-200:])
    shutil.rmtree(venv)


def probar_revisar(proyecto):
    """revisar.py lista candidatos: una cita sin referencia, una referencia sin cita y las marcas."""
    caps = proyecto / "libre" / "capitulos"
    capitulo = "\n".join([
        "# Introducción",
        "",
        "Según Kelsen (1960) la norma es el origen. Lo discuten (Pérez & Díaz, 2020; García et al., 2018a).",
        "El marco es amplio (American Psychological Association [APA], 2020, p. 12). [[pendiente: agregar cifra]]",
        "El ciclo —reportar y moderar— sigue → luego ✅. Rango correcto: pp. 10–15.",
        "",
        "```",
        "(Ejemplo, 1999) código ignorado — tampoco cuenta",
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
    ok("revisar.py lista rayas, flechas y emojis con archivo:línea",
       "Caracteres a evitar (rayas, flechas, emojis): 4" in sal and "01-primera-seccion.md:5  raya:" in sal
       and "flecha:" in sal and "emoji o ícono:" in sal, sal)
    ok("revisar.py acepta el guion medio en un rango numérico (pp. 10–15)", "guion medio" not in sal, sal)
    code, _ = correr(proyecto, ".apa/scripts/revisar.py", "--doc", "libre", "--estricto")
    ok("revisar.py --estricto termina con código 1 si queda algo", code == 1)


def probar_revisar_citas(proyecto):
    """Citas APA 7 bien escritas no dan avisos falsos (#8, #10). Autores y obras inventados."""
    caps = proyecto / "libre" / "capitulos"
    capitulo = "\n".join([
        "# Citas",
        "",
        "Así lo plantea Alvarado (2021).",
        "Uno (Benítez y Cuéllar, 2019). Otro (Dorado & Esquivel, 2018, p. 14).",
        "Fajardo et al. (2017) señalan algo (Ibarra et ál., 2016) y lo repiten (Ibarra et al, 2016).",
        "Un grupo (Equipo Alfa Beta, 2024). Equipo Alfa Beta (2024) añade algo.",
        "Según el Consejo Nacional Ficticio (2020) hay datos.",
        "Primero (Organización Ficticia de Salud [OFS], 2020). Luego (OFS, 2020, p. 3).",
        "La Agencia Ejemplo de Datos (AED, 2019) informa. Después AED (2019) agrega.",
        "Aduanas (Dirección Ficticia de Aduanas, 2021) y su sigla (DFA, 2021).",
        "Sin fecha (Marín, s. f.), con letra (Navas, s.f.-a) y (Navas, s. f.-b).",
        "Ortiz (s. f.) sostiene algo. En prensa (Paredes, en prensa).",
        "Varios años (Quiroga, 2020, 2022) y letras (Rivas, 2015a, 2015b). Mal (Salinas, 2014c).",
        "Secundaria (Tapia, 2018, como se citó en Urquiza, 2019). Valdez (como se citó en Wilde, 2021) plantea.",
        "Peal (2018, como se citó en Tsai, 2017) lo dijo.",
        "Varias (Yáñez, 2012; véase también Zárate, 2013; cf. Arce, 2011).",
        "Iniciales (B. Cortez, 2010) y (L. Cortez, 2011). Compuesto (Lerma Duarte, 2011, pp. 25-64).",
        "Sin autor (*Economía regional*, 2008) y (Economía regional…, 2008).",
        "Personal (E. Mamani, comunicación personal, 8 de febrero de 2021). Herramienta (versión 2020).",
        "Sin referencia (Nieto, 2009). Mal escrita (Zuleta,2011,pg. 13).",
        ""])
    referencias = "\n".join([
        "# Referencias {.sin-numero}",
        "",
        "Alvarado, R. (2021). *Título uno*. Editorial Ejemplo.",
        "Benítez, A., y Cuéllar, M. (2019). *Título*. Editorial Ejemplo.",
        "Dorado, L., & Esquivel, T. (2018). *Título*. Editorial Ejemplo.",
        "Fajardo, P., Gil, R., y Hurtado, S. (2017). *Título*. Editorial Ejemplo.",
        "Ibarra, C., Jara, D., y Luna, E. (2016). *Título*. Editorial Ejemplo.",
        "Equipo Alfa Beta. (2024, 23 de octubre). *Título*. Sitio Ejemplo.",
        "Consejo Nacional Ficticio. (2020). *Título*. Editorial Ejemplo.",
        "Organización Ficticia de Salud. (2020). *Título*. OFS.",
        "Agencia Ejemplo de Datos. (2019). *Título*. Editorial Ejemplo.",
        "Dirección Ficticia de Aduanas (DFA). (2021, 13 de abril). *Título*. Sitio Ejemplo.",
        "Marín, J. (s.f.). *Título*. Editorial Ejemplo.",
        "Navas, O. (s. f.-a). *Título uno*. Editorial Ejemplo.",
        "Navas, O. (s. f.-b). *Título dos*. Editorial Ejemplo.",
        "Ortiz, Q. (s. f.). *Título*. Editorial Ejemplo.",
        "Paredes, V. (en prensa). *Título*. Revista Ejemplo.",
        "Quiroga, W. (2020). *Título uno*. Editorial Ejemplo.",
        "Quiroga, W. (2022). *Título dos*. Editorial Ejemplo.",
        "Rivas, X. (2015a). *Título uno*. Editorial Ejemplo.",
        "Rivas, X. (2015b). *Título dos*. Editorial Ejemplo.",
        "Salinas, Y. (2014a). *Título uno*. Editorial Ejemplo.",
        "Salinas, Y. (2014b). *Título dos*. Editorial Ejemplo.",
        "Urquiza, Z. (2019). *Título*. Editorial Ejemplo.",
        "Wilde, A. (2021). *Título*. Editorial Ejemplo.",
        "Tsai, K. (2017). *Título*. Editorial Ejemplo.",
        "Yáñez, B. (2012). *Título*. Editorial Ejemplo.",
        "Zárate, C. (2013). *Título*. Editorial Ejemplo.",
        "Arce, D. (2011). *Título*. Editorial Ejemplo.",
        "Cortez, B. (2010). *Título uno*. Editorial Ejemplo.",
        "Cortez, L. (2011). *Título dos*. Editorial Ejemplo.",
        "Lerma Duarte, H. D. (2011). *Título*. Editorial Ejemplo.",
        "*Economía regional del altiplano*. (2008). Editorial Ejemplo.",
        "Zuleta, E. (2011). *Título*. Editorial Ejemplo.",
        "Olmos, F. (2005). *Título*. Editorial Ejemplo.",
        ""])
    (caps / "01-primera-seccion.md").write_text(capitulo, encoding="utf-8")
    (caps / "90-referencias.md").write_text(referencias, encoding="utf-8")
    code, sal = correr(proyecto, ".apa/scripts/revisar.py", "--doc", "libre")
    sin_ref = sal.split("== Citas sin referencia")[1].split("== Referencias que no se citan")[0]
    sin_cita = sal.split("== Referencias que no se citan")[1].split("== Caracteres")[0]
    sugerencias = sal.split("== Formato de citas")[1].split("Resumen:")[0]
    ok("citas: solo 2 citas sin referencia (Nieto 2009, Salinas 2014c)",
       sin_ref.startswith(": 2") and "Nieto (2009)" in sin_ref and "Salinas (2014c)" in sin_ref, sin_ref)
    ok("citas: solo 3 referencias sin cita (Olmos, Salinas 2014a y 2014b)",
       sin_cita.startswith(": 3") and "Olmos (2005)" in sin_cita and "Salinas (2014a)" in sin_cita
       and "Salinas (2014b)" in sin_cita, sin_cita)
    for falso in ("Team", "Beta (", "Según", "Tapia", "Valdez", "Peal", "Mamani", "OFS (", "AED (", "Square"):
        ok(f"citas: no aparece el falso aviso «{falso}»", falso not in sin_ref + sin_cita, sin_ref + sin_cita)
    ok("citas: sugiere «y» en lugar de «&» (la forma declarada)", "Dorado & Esquivel" in sugerencias, sugerencias)
    ok("citas: sugiere «et al.» con punto y sin tilde", "Ibarra et ál." in sugerencias and "Ibarra et al," in sugerencias,
       sugerencias)
    ok("citas: sugiere «s.f.» (la forma declarada)", "Marín, s. f." in sugerencias, sugerencias)
    ok("citas: sugiere «p.» y el espacio tras la coma", "pg." in sugerencias and "espacio" in sugerencias, sugerencias)
    toml = proyecto / "libre" / "documento.toml"
    texto = toml.read_text(encoding="utf-8")
    toml.write_text(texto.replace('conjuncion = "y"', 'conjuncion = "&"').replace('sin_fecha = "s.f."', 'sin_fecha = "s. f."'),
                    encoding="utf-8")
    code, sal = correr(proyecto, ".apa/scripts/revisar.py", "--doc", "libre")
    sugerencias = sal.split("== Formato de citas")[1].split("Resumen:")[0]
    ok("citas: con [citas] «&» y «s. f.», cambian las sugerencias",
       "Benítez y Cuéllar" in sugerencias and "Dorado & Esquivel" not in sugerencias and "Navas, s.f.-a" in sugerencias,
       sugerencias)
    toml.write_text(texto, encoding="utf-8")
    (caps / "01-primera-seccion.md").write_text("# Uno\n\nTexto (Alvarado & Benítez, 2021).\n", encoding="utf-8")
    (caps / "90-referencias.md").write_text("# Referencias {.sin-numero}\n\nAlvarado, R., & Benítez, A. (2021). *T*.\n",
                                            encoding="utf-8")
    code, sal = correr(proyecto, ".apa/scripts/revisar.py", "--doc", "libre", "--estricto")
    ok("citas: las sugerencias de formato no cuentan para --estricto", code == 0 and "Dorado" not in sal, sal[-300:])


def probar_migrar(tmp):
    """Un documento del diseño antiguo se genera igual que antes y sigue protegido contra regeneración."""
    proyecto = tmp / "antiguo"
    shutil.copytree(FIXTURES / "diseno-antiguo", proyecto)
    huellas = proyecto / "docs" / "dist" / ".huellas.json"
    huellas.parent.mkdir(exist_ok=True)
    huellas.write_text(json.dumps({"Documento.docx": "abc"}), encoding="utf-8")
    code, sal = correr(proyecto, INICIAR, "--migrar", "docs")
    ok("--migrar convierte el diseño antiguo", code == 0, sal[-300:])
    ok("--migrar avisa de lo obsoleto de la plantilla antigua", "AVISO de la plantilla antigua" in sal and "scripts" in sal, sal)
    ok("--migrar no borra nada solo", (proyecto / "docs" / "scripts" / "generar_docx.py").exists())
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
        probar_skills()
        proyecto = probar_tipos(tmp)
        probar_demas_tipos(tmp)
        probar_tablas_juntas(tmp)
        probar_portada(tmp)
        probar_compatibilidad_02(tmp)
        probar_paquete(tmp)
        probar_importar(tmp, proyecto)
        probar_sincronizar(proyecto)
        probar_entorno(proyecto)
        probar_revisar(proyecto)
        probar_revisar_citas(proyecto)
        probar_migrar(tmp)
    print("\nRESULTADO:", "todo bien" if not fallos else f"{len(fallos)} fallo(s): " + "; ".join(fallos))
    sys.exit(1 if fallos else 0)


if __name__ == "__main__":
    main()
