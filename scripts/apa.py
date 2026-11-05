"""Formato APA 7 sobre python-docx. Solo formato: el contenido viene de capitulos/*.md.

Lo usa generar_docx.py. No tiene datos personales ni texto del documento.
"""
import re

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK, WD_COLOR_INDEX, WD_LINE_SPACING
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

PAPELES = {"carta": (21.59, 27.94), "a4": (21.0, 29.7), "oficio": (21.59, 35.56)}
MARGEN = 2.54  # cm (1 pulgada, APA 7)
SANGRIA = 1.27  # cm (0,5 pulgadas, APA 7)

# **negrita** · [texto](url) · [[pendiente]] · `código` · *cursiva*
TOKEN = re.compile(r"(\*\*[^*]+\*\*|\[[^\[\]]+\]\([^)]+\)|\[\[[^\]]+\]\]|`[^`]+`|\*[^*\s][^*]*\*)")


class DocumentoAPA:
    def __init__(self, fuente="Times New Roman", tamano=12, idioma="es-BO", papel="carta",
                 justificar=False, etiquetas=None):
        self.doc = Document()
        self.fuente, self.tamano, self.idioma = fuente, tamano, idioma
        self.justificar = justificar
        ancho, alto = PAPELES[papel]
        self.ancho_texto = ancho - 2 * MARGEN
        self.contadores = {"Tabla": 0, "Figura": 0}
        # Nombre visible: APA usa Tabla/Figura; algunas facultades piden Cuadro/Gráfico.
        self.etiquetas = {"Tabla": "Tabla", "Figura": "Figura", **(etiquetas or {})}
        self._salto_pendiente = False
        self._estilos()
        self._pagina(ancho, alto)

    # ------------------------------------------------------------ estilos
    def _lang(self, rpr):
        lang = rpr.find(qn("w:lang"))
        if lang is None:
            lang = OxmlElement("w:lang")
            rpr.append(lang)
        lang.set(qn("w:val"), self.idioma)
        lang.set(qn("w:eastAsia"), self.idioma)

    def _fuente(self, st, size=None, bold=None, italic=None, nombre=None):
        nombre = nombre or self.fuente
        st.font.name = nombre
        st.font.size = Pt(size or self.tamano)
        st.font.color.rgb = RGBColor(0, 0, 0)
        if bold is not None:
            st.font.bold = bold
        if italic is not None:
            st.font.italic = italic
        rpr = st.element.get_or_add_rPr()
        rf = rpr.find(qn("w:rFonts"))
        if rf is None:
            rf = OxmlElement("w:rFonts")
            rpr.append(rf)
        for k in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"):
            rf.set(qn(k), nombre)
        for k in ("w:asciiTheme", "w:hAnsiTheme", "w:cstheme", "w:eastAsiaTheme"):
            if rf.get(qn(k)) is not None:
                del rf.attrib[qn(k)]
        self._lang(rpr)

    def _estilo(self, nombre, base="Normal"):
        st = self.doc.styles
        if nombre in [s.name for s in st]:
            return st[nombre]
        nuevo = st.add_style(nombre, 1)
        nuevo.base_style = st[base]
        return nuevo

    def _estilos(self):
        st = self.doc.styles
        normal = st["Normal"]
        self._fuente(normal)
        pf = normal.paragraph_format
        pf.line_spacing_rule = WD_LINE_SPACING.DOUBLE
        pf.space_before = pf.space_after = Pt(0)
        pf.widow_control = True

        cuerpo = self._estilo("Cuerpo APA")
        cuerpo.paragraph_format.first_line_indent = Cm(SANGRIA)
        if self.justificar:
            cuerpo.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

        niveles = {1: (WD_ALIGN_PARAGRAPH.CENTER, True, False), 2: (WD_ALIGN_PARAGRAPH.LEFT, True, False),
                   3: (WD_ALIGN_PARAGRAPH.LEFT, True, True), 4: (WD_ALIGN_PARAGRAPH.LEFT, True, False)}
        for n, (al, b, i) in niveles.items():
            h = st[f"Heading {n}"]
            self._fuente(h, bold=b, italic=i)
            f = h.paragraph_format
            f.alignment = al
            f.line_spacing_rule = WD_LINE_SPACING.DOUBLE
            f.space_before = Pt(12 if n == 1 else 6)
            f.space_after = Pt(0)
            f.keep_with_next = True
            f.first_line_indent = Cm(SANGRIA if n == 4 else 0)
            f.page_break_before = n == 1  # cada capítulo empieza en página nueva

        sin = self._estilo("Titulo sin indice")
        self._fuente(sin, bold=True)
        sin.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
        sin.paragraph_format.keep_with_next = True

        cap = st["Caption"]
        self._fuente(cap, bold=False, italic=False)
        cap.paragraph_format.line_spacing_rule = WD_LINE_SPACING.DOUBLE
        cap.paragraph_format.space_before = Pt(12)
        cap.paragraph_format.space_after = Pt(0)
        cap.paragraph_format.keep_with_next = True

        tt = self._estilo("Texto tabla")
        self._fuente(tt, size=self.tamano - 2)
        tt.paragraph_format.line_spacing_rule = WD_LINE_SPACING.SINGLE
        tt.paragraph_format.space_after = Pt(2)

        cita = self._estilo("Cita en bloque")
        cita.paragraph_format.left_indent = Cm(SANGRIA)

        cod = self._estilo("Codigo")
        self._fuente(cod, size=self.tamano - 2, nombre="Consolas")
        cod.paragraph_format.line_spacing_rule = WD_LINE_SPACING.SINGLE
        cod.paragraph_format.left_indent = Cm(0.63)

        ref = self._estilo("Referencia APA")
        ref.paragraph_format.left_indent = Cm(SANGRIA)
        ref.paragraph_format.first_line_indent = Cm(-SANGRIA)

        for nivel in range(1, 4):
            nombre = "List Bullet" if nivel == 1 else f"List Bullet {nivel}"
            self._fuente(st[nombre])
            st[nombre].paragraph_format.line_spacing_rule = WD_LINE_SPACING.DOUBLE
            num = self._estilo(f"Lista numerada APA {nivel}")
            num.paragraph_format.left_indent = Cm(0.63 * (nivel + 1))
            num.paragraph_format.first_line_indent = Cm(-0.63)

        for i in range(1, 5):
            toc = self._estilo(f"TOC {i}")
            self._fuente(toc)
            toc.paragraph_format.left_indent = Cm(0.6 * (i - 1))
            toc.paragraph_format.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE

    def _pagina(self, ancho, alto):
        sec = self.doc.sections[0]
        sec.page_width, sec.page_height = Cm(ancho), Cm(alto)
        for lado in ("left_margin", "right_margin", "top_margin", "bottom_margin"):
            setattr(sec, lado, Cm(MARGEN))
        hdr = sec.header.paragraphs[0]
        hdr.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        self.campo(hdr, "PAGE", "1")
        # Word pregunta al abrir si actualiza índices y numeración (equivale a Ctrl+A, F9).
        upd = OxmlElement("w:updateFields")
        upd.set(qn("w:val"), "true")
        self.doc.settings.element.append(upd)

    # ------------------------------------------------------------ primitivas
    def campo(self, par, instr, marcador=""):
        def fld(tipo):
            r = par.add_run()
            e = OxmlElement("w:fldChar")
            e.set(qn("w:fldCharType"), tipo)
            r._r.append(e)
        fld("begin")
        r = par.add_run()
        t = OxmlElement("w:instrText")
        t.set(qn("xml:space"), "preserve")
        t.text = f" {instr} "
        r._r.append(t)
        fld("separate")
        visible = par.add_run(marcador)
        fld("end")
        return visible

    def _par(self, estilo=None):
        p = self.doc.add_paragraph(style=estilo)
        if self._salto_pendiente:
            p.paragraph_format.page_break_before = True
            self._salto_pendiente = False
        return p

    def salto(self):
        """El siguiente párrafo empieza en página nueva (sin dejar páginas en blanco)."""
        self._salto_pendiente = True

    def texto(self, par, txt, size=None):
        for parte in TOKEN.split(txt):
            if not parte:
                continue
            if parte.startswith("**"):
                r = par.add_run(parte[2:-2])
                r.bold = True
            elif parte.startswith("[["):
                r = par.add_run(parte[2:-2])
                r.font.highlight_color = WD_COLOR_INDEX.YELLOW
            elif parte.startswith("["):
                m = re.match(r"\[([^\]]+)\]\(([^)]+)\)", parte)
                r = par.add_run(m.group(1) if m.group(1) == m.group(2) else f"{m.group(1)} ({m.group(2)})")
            elif parte.startswith("`"):
                r = par.add_run(parte[1:-1])
                r.font.name = "Consolas"
            elif parte.startswith("*"):
                r = par.add_run(parte[1:-1])
                r.italic = True
            else:
                r = par.add_run(parte)
            if size:
                r.font.size = Pt(size)
        return par

    # ------------------------------------------------------------ bloques
    def parrafo(self, txt, estilo="Cuerpo APA", alinear=None):
        p = self.texto(self._par(estilo), txt)
        if alinear == "centro":
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        return p

    def vacio(self):
        return self._par()

    def titulo(self, nivel, txt, en_indice=True):
        if not en_indice:
            p = self._par("Titulo sin indice")
            if nivel == 1:
                p.paragraph_format.page_break_before = True
            return self.texto(p, txt)
        p = self.doc.add_heading(level=nivel)
        self._salto_pendiente = False  # Heading 1 ya trae salto de página
        return self.texto(p, txt)

    def lista(self, items):
        """items: [(nivel 0..2, ordenada, texto)]. Las numeradas se reinician en cada lista."""
        cuenta = {}
        for nivel, ordenada, txt in items:
            nivel = min(nivel, 2)
            for k in [k for k in cuenta if k > nivel]:
                del cuenta[k]
            if ordenada:
                cuenta[nivel] = cuenta.get(nivel, 0) + 1
                p = self._par(f"Lista numerada APA {nivel + 1}")
                p.add_run(f"{cuenta[nivel]}.\t")
            else:
                p = self._par("List Bullet" if nivel == 0 else f"List Bullet {nivel + 1}")
            self.texto(p, txt)

    def cita(self, txt):
        return self.texto(self._par("Cita en bloque"), txt)

    def codigo(self, lineas):
        for ln in lineas or [""]:
            self._par("Codigo").add_run(ln)

    def referencia(self, txt):
        return self.texto(self._par("Referencia APA"), txt)

    def leyenda(self, tipo, titulo):
        """Tabla N / Figura N en negrita y el título en cursiva en la línea siguiente (APA 7)."""
        self.contadores[tipo] += 1
        nombre = self.etiquetas[tipo]
        p = self._par("Caption")
        p.add_run(f"{nombre} ").bold = True
        self.campo(p, f"SEQ {nombre} \\* ARABIC", str(self.contadores[tipo])).bold = True
        p.add_run().add_break(WD_BREAK.LINE)
        desde = len(p.runs)
        self.texto(p, titulo)
        for r in p.runs[desde:]:
            r.italic = True
        return self.contadores[tipo]

    def nota(self, txt):
        p = self.texto(self._par("Texto tabla"), "*Nota.* " + txt)
        p.paragraph_format.space_before = Pt(4)
        p.paragraph_format.space_after = Pt(12)
        return p

    def _borde(self, celda, **lados):
        tcPr = celda._tc.get_or_add_tcPr()
        b = tcPr.find(qn("w:tcBorders"))
        if b is None:
            b = OxmlElement("w:tcBorders")
            tcPr.append(b)
        for lado, val in lados.items():
            e = OxmlElement(f"w:{lado}")
            e.set(qn("w:val"), val)
            e.set(qn("w:sz"), "8")
            e.set(qn("w:space"), "0")
            e.set(qn("w:color"), "000000")
            b.append(e)

    def _celda(self, celda, txt, negrita=False, size=None):
        celda.paragraphs[0].style = self.doc.styles["Texto tabla"]
        for i, ln in enumerate(re.split(r"<br\s*/?>", txt)):
            p = celda.paragraphs[0] if i == 0 else celda.add_paragraph(style="Texto tabla")
            self.texto(p, f"**{ln}**" if negrita and ln.strip() else ln, size)

    def tabla(self, encabezados, filas, anchos=None, size=None):
        """Tabla APA: solo bordes horizontales; encabezado repetido en cada página."""
        n = len(encabezados)
        if not anchos:
            pesos = [min(max(len(str(f[i])) if i < len(f) else 0 for f in [encabezados] + filas), 45) + 6
                     for i in range(n)]
            anchos = [self.ancho_texto * w / sum(pesos) for w in pesos]
        t = self.doc.add_table(rows=1 + len(filas), cols=n)
        t.alignment = WD_TABLE_ALIGNMENT.CENTER
        t.autofit = False
        for c, h in zip(t.rows[0].cells, encabezados):
            self._celda(c, h, negrita=True, size=size)
            self._borde(c, top="single", bottom="single")
        trPr = t.rows[0]._tr.get_or_add_trPr()
        rep = OxmlElement("w:tblHeader")
        rep.set(qn("w:val"), "true")
        trPr.append(rep)
        for fila, datos in zip(t.rows[1:], filas):
            for i, c in enumerate(fila.cells):
                self._celda(c, datos[i] if i < len(datos) else "", size=size)
        for c in t.rows[-1].cells:
            self._borde(c, bottom="single")
        for fila in t.rows:
            for c, w in zip(fila.cells, anchos):
                c.width = Cm(w)
        return t

    def imagen(self, ruta, ancho_cm):
        p = self._par()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.keep_with_next = True
        p.add_run().add_picture(str(ruta), width=Cm(min(ancho_cm, self.ancho_texto)))
        return p

    def figura(self, ruta, titulo, ancho_cm=None, nota=None):
        self.leyenda("Figura", titulo)
        p = self.imagen(ruta, ancho_cm or self.ancho_texto)
        p.paragraph_format.keep_with_next = bool(nota)
        if nota:
            self.nota(nota)

    # ------------------------------------------------------------ índices
    def _lista_campo(self, titulo, instr, aviso):
        self.titulo(1, titulo, en_indice=False)
        self.campo(self._par(), instr, aviso)

    def indice(self, niveles=3):
        self._lista_campo("Índice de Contenidos", f'TOC \\o "1-{niveles}" \\h \\z \\u',
                          "Actualice los campos (Ctrl+A, F9) para generar el índice.")

    def _lista_de(self, tipo):
        n = self.etiquetas[tipo]
        self._lista_campo(f"Lista de {n}s", f'TOC \\h \\z \\c "{n}"',
                          f"Actualice los campos (Ctrl+A, F9) para generar la lista de {n.lower()}s.")

    def lista_tablas(self):
        self._lista_de("Tabla")

    def lista_figuras(self):
        self._lista_de("Figura")
