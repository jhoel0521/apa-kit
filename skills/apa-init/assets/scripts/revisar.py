"""Revisa un documento apa-kit y lista CANDIDATOS a confirmar (no errores).

Uso (desde la carpeta del proyecto; en Windows `py -3`, en macOS/Linux `python3`):
    python .apa/scripts/revisar.py                  # informe en pantalla
    python .apa/scripts/revisar.py --doc tesis      # si hay varios documentos
    python .apa/scripts/revisar.py --estricto       # termina con código 1 si queda algo por resolver

Qué busca en <documento>/capitulos/*.md:
  1. Marcas sin resolver: [[pendiente…]], [[verificar…]], [[revisar…]] y textos de plantilla [[…]].
  2. Citas (Autor, año) / Autor (año) que no tienen su referencia bajo «# Referencias». Reconoce autores de
     grupo y siglas, s.f. y s. f. (con letra), en prensa, varios años, años con letra, citas secundarias
     («como se citó en»), comunicaciones personales y remisiones (véase, cf.).
  3. Referencias que no se citan en ningún capítulo.
  4. Caracteres que delatan texto generado o pegado sin revisar: rayas (—), guion medio (–) fuera de un
     rango numérico como «pp. 10–15», flechas (→) y emojis o íconos. También en documento.toml.
  5. Sugerencias de formato según [citas] de documento.toml, y bloques de la portada sin {{CLAVE}}
     (informativos: no cuentan para --estricto).

Es una ayuda: puede equivocarse (por ejemplo, «Ley 1178 (1990)»). El agente debe
confirmar cada candidato con el autor. Por defecto siempre termina con código 0.
"""
import _entorno  # noqa: F401  (usa .venv/ si existe)

import argparse
import re
import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _raiz import carpeta_documento  # noqa: E402

DOCS = carpeta_documento()

MAYUS = "A-ZÁÉÍÓÚÑÜ"
# Fecha de una cita o referencia: año (con letra: 2020a), sin fecha (s.f. o s. f., con letra: s.f.-a) o en prensa.
ANIO = (r"(?:(?<!\d)(?:1[5-9]\d\d|20\d\d)[a-z]?(?![\w])"
        r"|s\.\s?f\.(?:-[a-z])?|en\s+prensa(?:-[a-z])?)")
RE_MARCA = re.compile(r"\[\[\s*([^\]]*?)\s*\]\]")
RE_COMENTARIO = re.compile(r"<!--.*?-->", re.S)
RE_GRUPO = re.compile(r"\(([^()]*)\)")                     # cualquier paréntesis (sin anidar)
RE_TIENE_ANIO = re.compile(ANIO, re.I)
RE_PARTE = re.compile(rf"^(?P<autor>.+?),\s*(?P<anios>{ANIO}(?:\s*,\s*{ANIO})*)(?=\s*(?:,|$))", re.I)
RE_NARRATIVA = re.compile(rf"\((?P<anios>{ANIO}(?:\s*,\s*{ANIO})*)\s*[,)]", re.I)
RE_REF_FECHA = re.compile(rf"\((?P<anio>{ANIO})(?:,[^)]*)?\)", re.I)
RE_SECUNDARIA = re.compile(r",?\s*(?:como\s+se\s+cit[oó]\s+en|citad[oa]\s+(?:en|por)|as\s+cited\s+in)\s+", re.I)
RE_PREFIJO = re.compile(r"^(?:(?:v[eé]ase|ver|see)(?:\s+(?:tambi[eé]n|also))?|cf\.|p\.\s?ej\.,?|e\.\s?g\.,?"
                        r"|por\s+ejemplo,?)\s+", re.I)
RE_INICIALES = re.compile(rf"^(?:[{MAYUS}]\.\s?(?:-[{MAYUS}]\.\s?)?)+")
RE_SIGLA = re.compile(rf"\s*[\[(]([{MAYUS}][A-Za-z{MAYUS}&]{{1,14}})[\])]\s*$")
RE_ES_SIGLA = re.compile(rf"^[{MAYUS}][{MAYUS}&]{{1,14}}$")
RE_ET_AL = re.compile(r"\s+et\s+[aá]l\b\.?.*$", re.I)
RE_CONJ = re.compile(r"\s+(?:y|e|&)\s+.*$")
RE_PERSONA = re.compile(rf"^([^,]+?),\s*[{MAYUS}]\.")
CONECTORES = {"de", "del", "la", "las", "los", "el", "y", "e", "&", "van", "von", "da", "di", "der", "den"}
# Palabras con mayúscula que suelen ir antes de un autor y no son parte de su nombre.
VACIAS = {"segun", "para", "en", "como", "desde", "con", "por", "tras", "asi", "ademas", "el", "la", "los", "las",
          "un", "una", "de", "del", "este", "esta", "estos", "estas", "lo", "al", "a", "y", "e", "pero", "sin",
          "embargo", "luego", "despues", "tambien", "ya", "aunque", "si", "cuando", "donde", "mientras"}

# Caracteres a evitar en el texto del documento (ver apa-guia/references/reglas-ia.md, «Estilo»).
# El guion medio solo se acepta entre dos números: APA 7 lo usa en rangos («pp. 10–15», «2019–2021»).
CARACTERES = [
    ("raya", re.compile("[—―]")),
    ("guion medio", re.compile(r"(?<!\d)–|–(?!\d)")),
    ("flecha", re.compile("[←-⇿⟰-⟿⤀-⥿⬀-⯿]")),
    ("emoji o ícono", re.compile("[\U0001f000-\U0001faff☀-➿️]")),
]


def plano(txt):
    return "".join(c for c in unicodedata.normalize("NFD", txt.casefold()) if unicodedata.category(c) != "Mn")


def norm_anio(t):
    """'2020a' -> ('2020', 'a') · 's. f.-b' -> ('sf', 'b') · 'en prensa' -> ('en prensa', '')."""
    t = re.sub(r"\s+", "", plano(t))
    m = re.match(r"(\d{4}|s\.f\.|enprensa)-?([a-z]?)$", t)
    if not m:
        return t, ""
    return {"s.f.": "s.f.", "enprensa": "en prensa"}.get(m.group(1), m.group(1)), m.group(2)


def mostrar_anio(base, letra):
    return base + ("-" + letra if letra and not base[0].isdigit() else letra)


def limpiar_autor(texto):
    """Quita formato Markdown, comillas, puntos suspensivos e iniciales; devuelve (autor, sigla o None)."""
    s = re.sub(r"[*_“”\"«»]", "", texto).replace("…", " ").replace("...", " ").strip(" ,.")
    sigla = None
    m = RE_SIGLA.search(s)
    if m:
        sigla, s = m.group(1), s[:m.start()].strip(" ,.")
    s = RE_INICIALES.sub("", s).strip()
    return re.sub(r"\s+", " ", s), sigla


def config():
    """documento.toml leído con tomllib/tomli; {} si no se puede (revisar.py sigue con los valores por defecto)."""
    try:
        try:
            import tomllib
        except ModuleNotFoundError:  # Python 3.9 y 3.10
            import tomli as tomllib
        with (DOCS / "documento.toml").open("rb") as f:
            return tomllib.load(f)
    except Exception:  # sin tomli, sin archivo o TOML inválido: no impide revisar
        return {}


def leer(ruta):
    """Líneas del capítulo con su número, sin comentarios HTML ni bloques de código."""
    texto = ruta.read_text(encoding="utf-8")
    texto = RE_COMENTARIO.sub(lambda m: "\n" * m.group(0).count("\n"), texto)
    salida, en_codigo = [], False
    for n, ln in enumerate(texto.splitlines(), 1):
        if ln.strip().startswith("```"):
            en_codigo = not en_codigo
            continue
        if not en_codigo:
            salida.append((n, ln))
    return salida


def buscar_caracteres(lineas, nombre):
    """[(dónde, qué, fragmento)] de cada carácter a evitar en las líneas dadas."""
    hallados = []
    for n, ln in lineas:
        for que, patron in CARACTERES:
            for m in patron.finditer(ln):
                ini, fin = max(0, m.start() - 30), m.end() + 30
                fragmento = ("…" if ini else "") + ln[ini:fin].strip() + ("…" if fin < len(ln) else "")
                hallados.append((f"{nombre}:{n}", que, fragmento))
    return hallados


def caracteres_toml():
    """Líneas de documento.toml sin comentarios: la portada y los títulos también salen en el Word."""
    ruta = DOCS / "documento.toml"
    if not ruta.exists():
        return []
    lineas = [(n, ln) for n, ln in enumerate(ruta.read_text(encoding="utf-8").splitlines(), 1)
              if not ln.lstrip().startswith("#")]
    return buscar_caracteres(lineas, ruta.name)


def analizar(capitulos):
    """Primera pasada: marcas, caracteres, referencias (bajo «# Referencias») y líneas de texto con su lugar."""
    marcas, caracteres, refs, textos = [], [], [], []
    for ruta in capitulos:
        en_refs = False
        lineas = leer(ruta)
        caracteres += buscar_caracteres(lineas, ruta.name)
        for n, ln in lineas:
            titulo = re.match(r"^(#{1,4})\s+(.+?)\s*(\{[^}]*\})?\s*$", ln)
            if titulo and len(titulo.group(1)) == 1:
                en_refs = plano(titulo.group(2)).startswith(("referencias", "bibliografia"))
                continue
            for m in RE_MARCA.finditer(ln):
                texto = m.group(1)
                tipo = next((t for t in ("pendiente", "verificar", "revisar") if plano(texto).startswith(t)), "plantilla")
                marcas.append((tipo, f"{ruta.name}:{n}", texto))
            limpio = RE_MARCA.sub("", ln)
            if en_refs:
                ref = leer_referencia(limpio)
                if ref:
                    ref["donde"] = f"{ruta.name}:{n}"
                    refs.append(ref)
            elif limpio.strip():
                textos.append((f"{ruta.name}:{n}", limpio))
    return marcas, caracteres, refs, textos


def leer_referencia(linea):
    """Una entrada de Referencias: autor (apellido de persona o nombre completo de grupo), fecha y sigla."""
    s = re.sub(r"^\s*(?:[-*+]|\d+\.)\s+", "", linea).strip()
    m = RE_REF_FECHA.search(s)
    if not s or s.startswith("#") or not m:
        return None
    autores = re.sub(r"[*_]", "", s[:m.start()]).strip()     # sin quitar el punto final: «Kelsen, H.»
    base, letra = norm_anio(m.group("anio"))
    persona = RE_PERSONA.match(autores)
    if persona:
        visible, sigla = persona.group(1).strip(), None
    else:
        visible, sigla = limpiar_autor(autores)
    return {"clave": plano(visible), "visible": visible, "persona": bool(persona), "sigla": sigla,
            "base": base, "letra": letra}


def variantes(nombre):
    """Nombre completo, antes de «et al.» y antes de «y»/«&»: el completo va primero para no partir
    «Dirección de Impuestos y Aduanas»."""
    n = re.sub(r"\s+", " ", nombre).strip()
    salida = []
    for v in (n, RE_ET_AL.sub("", n), RE_CONJ.sub("", RE_ET_AL.sub("", n))):
        if v and v not in salida:
            salida.append(v)
    return salida


class Resolutor:
    """Busca a qué referencia corresponde el autor de una cita (sin acentos, por nombre completo, sigla,
    primer apellido o comienzo del título de una obra sin autor)."""

    def __init__(self, refs):
        self.claves = {r["clave"] for r in refs}
        self.alias = {plano(r["sigla"]): r["clave"] for r in refs if r["sigla"]}
        self.primeras = {}
        for r in refs:
            if r["persona"] and r["clave"]:
                self.primeras.setdefault(r["clave"].split()[0], r["clave"])
        self.grupos = [r["clave"] for r in refs if not r["persona"]]

    def __call__(self, nombre):
        vs = [plano(v) for v in variantes(nombre)]
        for k in vs:
            if k in self.claves:
                return k
            if k in self.alias:
                return self.alias[k]
        for k in vs:
            if k in self.primeras:
                return self.primeras[k]
            if len(k.split()) >= 2:
                for g in self.grupos:
                    if g.startswith(k):
                        return g
        return None


def corrida(antes):
    """Palabras del nombre justo antes del paréntesis de una cita narrativa (hasta 8), en orden."""
    tokens = antes.split()
    run, i = [], len(tokens) - 1
    while i >= 0 and len(run) < 8:
        tok = re.sub(r"[*_“”\"«»]", "", tokens[i])
        if plano(tok) in ("al.", "al") and i > 0 and plano(tokens[i - 1]) == "et":
            run[:0] = [tokens[i - 1], tok]
            i -= 2
            continue
        if re.match(rf"^[{MAYUS}]\.(?:-[{MAYUS}]\.)?$", tok):       # inicial: P. Smith
            run.insert(0, tok)
        elif not tok or tok[-1] in ".,;:!?)":                     # fin de la frase anterior
            break
        elif re.match(rf"^[{MAYUS}]", tok) or plano(tok) in CONECTORES:
            run.insert(0, tok)
        else:
            break
        i -= 1
    return run


def nombre_narrativo(run, resolver):
    """El sufijo más largo de la corrida que coincide con una referencia; si ninguno, el nombre sin palabras
    vacías delante («Según el Banco Regional» -> «Banco Regional»)."""
    for j in range(len(run)):
        if plano(run[j]) in CONECTORES:
            continue
        candidato = " ".join(run[j:])
        if resolver(candidato):
            return candidato
    while run and (plano(run[0]) in VACIAS or plano(run[0]) in CONECTORES):
        run = run[1:]
    return " ".join(run)


def citas_del_texto(textos, refs, forma):
    """Segunda pasada: cada cita (parentética o narrativa) con la clave de su referencia, y las sugerencias
    de formato según [citas] de documento.toml."""
    resolver = Resolutor(refs)
    conj, sf = forma.get("conjuncion", "y"), forma.get("sin_fecha", "s.f.")

    # Siglas presentadas en el texto: «(Nombre Completo [SIGLA], 2020)» o «Nombre Completo (SIGLA, 2020)».
    for _, ln in textos:
        for g in RE_GRUPO.finditer(ln):
            if not RE_TIENE_ANIO.search(g.group(1)):
                continue
            for parte in g.group(1).split(";"):
                m = RE_PARTE.match(RE_PREFIJO.sub("", parte.strip()))
                if not m:
                    continue
                autor, sigla = limpiar_autor(m.group("autor"))
                if sigla and resolver(autor):
                    resolver.alias.setdefault(plano(sigla), resolver(autor))
                elif RE_ES_SIGLA.match(autor) and plano(autor) not in resolver.alias:
                    largo = nombre_narrativo(corrida(ln[:g.start()]), resolver)
                    if largo and resolver(largo):
                        resolver.alias[plano(autor)] = resolver(largo)

    citas, sugerencias = [], []

    def anotar(nombre, anios, donde):
        for a in re.split(r"\s*,\s*", anios.strip()):
            base, letra = norm_anio(a)
            citas.append({"nombre": variantes(nombre)[-1], "clave": resolver(nombre), "base": base,
                          "letra": letra, "donde": donde})

    def sugerir(texto, donde, consejo):
        sugerencias.append((donde, texto.strip()[:70], consejo))

    for donde, ln in textos:
        for g in RE_GRUPO.finditer(ln):
            contenido = g.group(1)
            if not RE_TIENE_ANIO.search(contenido):
                continue
            if re.search(r"\bet\s+ál\b|\bet\s+al\b(?!\.)", contenido, re.I):
                sugerir(contenido, donde, "escribe «et al.» (sin tilde y con punto)")
            if re.search(r"(?<![\w.])(?:pg|p[aá]gs?)\.", contenido, re.I):
                sugerir(contenido, donde, "APA usa «p.» para una página y «pp.» para varias")
            if re.search(r",(?=[^\s\d])|(?<=[^\d\s]),(?=\d)", contenido):
                sugerir(contenido, donde, "falta un espacio después de la coma")
            if sf == "s.f." and re.search(r"\bs\.\s+f\.", contenido):
                sugerir(contenido, donde, "el documento declara «s.f.» sin espacio ([citas] de documento.toml)")
            elif sf == "s. f." and re.search(r"\bs\.f\.", contenido):
                sugerir(contenido, donde, "el documento declara «s. f.» con espacio ([citas] de documento.toml)")
            for parte in contenido.split(";"):
                parte = parte.strip()
                if re.search(r"comunicaci[oó]n\s+personal", parte, re.I):
                    continue                                   # APA: no va en Referencias
                parte = RE_SECUNDARIA.split(parte)[-1]            # cita secundaria: solo la fuente consultada
                parte = RE_PREFIJO.sub("", parte)
                m = RE_PARTE.match(parte)
                if not m:
                    continue
                autor, _ = limpiar_autor(m.group("autor"))
                if not re.match(rf"^[{MAYUS}]", autor):
                    continue
                if conj == "y" and re.search(r"\s&\s", autor):
                    sugerir(parte, donde, "el documento declara «y» entre dos autores ([citas] de documento.toml)")
                elif conj == "&" and re.search(r"\sy\s", autor) and plano(autor) not in resolver.claves:
                    sugerir(parte, donde, "el documento declara «&» entre dos autores ([citas] de documento.toml)")
                anotar(autor, m.group("anios"), donde)
        for m in RE_NARRATIVA.finditer(ln):
            cierre = ln.find(")", m.start())
            if RE_SECUNDARIA.search(ln[m.start():cierre if cierre > 0 else None]):
                continue                                       # Peal (2018, como se citó en Tsai, 2018)
            run = corrida(ln[:m.start()])
            nombre = nombre_narrativo(run, resolver)
            if not nombre:
                continue
            if "&" in nombre.split():
                sugerir(nombre, donde, "en la cita narrativa se escribe «y», no «&»")
            anotar(limpiar_autor(nombre)[0], m.group("anios"), donde)
    return citas, sugerencias


def emparejar(citas, refs):
    """Citas sin referencia y referencias sin cita. Una cita con letra (2020a) va con la referencia de la
    misma letra; si ninguna referencia de ese autor y año tiene letra, se acepta cualquier letra."""
    con_letra = {(r["clave"], r["base"]) for r in refs if r["letra"]}

    def casa(c, r):
        return (c["clave"] == r["clave"] and c["base"] == r["base"]
                and (c["letra"] == r["letra"] or (c["clave"], c["base"]) not in con_letra))
    sin_ref, vistas = [], set()
    for c in citas:
        llave = (c["clave"] or plano(c["nombre"]), c["base"], c["letra"])
        if llave not in vistas and not any(casa(c, r) for r in refs):
            vistas.add(llave)
            sin_ref.append((c["donde"], c["nombre"], mostrar_anio(c["base"], c["letra"])))
    sin_cita = [(r["donde"], r["visible"], mostrar_anio(r["base"], r["letra"])) for r in refs
                if not any(casa(c, r) for c in citas)]
    return sin_ref, sin_cita


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--estricto", action="store_true", help="código 1 si queda algo por resolver")
    args = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")

    capitulos = sorted((DOCS / "capitulos").glob("*.md"))
    if not capitulos:
        sys.exit(f"No hay capítulos en {DOCS / 'capitulos'}")
    cfg = config()
    marcas, caracteres, refs, textos = analizar(capitulos)
    caracteres = caracteres_toml() + caracteres
    citas, sugerencias = citas_del_texto(textos, refs, cfg.get("citas", {}))
    sin_ref, sin_cita = emparejar(citas, refs)
    bloques = cfg.get("portada", {}).get("bloques", [])
    sin_clave = [str(b["texto"]) for b in bloques if isinstance(b, dict) and "texto" in b and "{{" not in str(b["texto"])]

    print(f"Revisión de {DOCS.name}/  ({len(capitulos)} archivos) · son CANDIDATOS: confírmalos con el autor\n")
    etiquetas = {"pendiente": "Pendientes", "verificar": "Por verificar (referencias o datos sin comprobar)",
                 "revisar": "Por revisar (el importador no pudo convertirlo)",
                 "plantilla": "Texto de plantilla sin reemplazar"}
    for tipo, titulo in etiquetas.items():
        lista = [m for m in marcas if m[0] == tipo]
        print(f"== {titulo}: {len(lista)}")
        for _, donde, texto in lista[:15]:
            print(f"   {donde}  [[{texto[:70]}]]")
        if len(lista) > 15:
            print(f"   … y {len(lista) - 15} más")
    print(f"\n== Citas sin referencia: {len(sin_ref)}")
    for donde, autor, anio in sin_ref:
        print(f"   {donde}  {autor} ({anio})  -> no está bajo «# Referencias»")
    print(f"\n== Referencias que no se citan: {len(sin_cita)}")
    for donde, autor, anio in sin_cita:
        print(f"   {donde}  {autor} ({anio})  -> ningún capítulo la cita")
    print(f"\n== Caracteres a evitar (rayas, flechas, emojis): {len(caracteres)}")
    for donde, que, fragmento in caracteres[:30]:
        print(f"   {donde}  {que}: {fragmento}")
    if len(caracteres) > 30:
        print(f"   … y {len(caracteres) - 30} más")
    if caracteres:
        print("   -> Cámbialos por puntuación normal (reglas-ia.md, «Estilo»). Si el texto es del autor, pregúntale antes.")
    forma = cfg.get("citas", {})
    print(f"\n== Formato de citas (sugerencias; [citas] declara «{forma.get('conjuncion', 'y')}» y "
          f"«{forma.get('sin_fecha', 's.f.')}»): {len(sugerencias)}")
    for donde, texto, consejo in sugerencias[:20]:
        print(f"   {donde}  ({texto})  -> {consejo}")
    if len(sugerencias) > 20:
        print(f"   … y {len(sugerencias) - 20} más")
    if sin_clave:
        print(f"\n== Portada: bloques de texto sin {{{{CLAVE}}}}: {len(sin_clave)}")
        for texto in sin_clave:
            print(f"   «{texto[:70]}»  -> confirma con el autor que no es un dato personal (esos van en .env)")
    print(f"\nResumen: {len(marcas)} marcas · {len(sin_ref)} citas sin referencia · {len(sin_cita)} referencias sin cita"
          f" · {len(caracteres)} caracteres a evitar · {len(sugerencias)} sugerencias de formato")
    # Las sugerencias de formato y la portada son informativas: no cuentan para --estricto.
    pendientes = [m for m in marcas if m[0] != "plantilla"]
    sys.exit(1 if args.estricto and (pendientes or sin_ref or sin_cita or caracteres) else 0)


if __name__ == "__main__":
    main()
