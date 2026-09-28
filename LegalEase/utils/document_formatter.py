from __future__ import annotations

import io
import re
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.shared import Inches, Pt
from fpdf import FPDF

from utils.text_utils import sanitize_text, terms_from_string

ROOT = Path(__file__).resolve().parents[1]
LOGO_PATH = ROOT / "assets" / "logo.png"


def _safe_pdf_text(text: str) -> str:
    text = sanitize_text(text)
    return text.encode("latin-1", errors="replace").decode("latin-1")


def _add_docx_footer(document: Document) -> None:
    section = document.sections[-1]
    footer = section.footer
    paragraph = footer.paragraphs[0]
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = paragraph.add_run(
        "LegalEase - AI-assisted draft. Review by a qualified legal professional before execution."
    )
    run.font.name = "Times New Roman"
    run.font.size = Pt(8)


def format_docx(
    text: str,
    doc_type: str,
    terms: str = "",
) -> bytes:
    document = Document()
    section = document.sections[0]
    section.top_margin = Inches(0.7)
    section.bottom_margin = Inches(0.7)
    section.left_margin = Inches(0.8)
    section.right_margin = Inches(0.8)

    if LOGO_PATH.exists():
        paragraph = document.add_paragraph()
        paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = paragraph.add_run()
        run.add_picture(str(LOGO_PATH), width=Inches(1.0))

    title = document.add_paragraph()
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = title.add_run(sanitize_text(doc_type).upper())
    run.bold = True
    run.font.name = "Times New Roman"
    run.font.size = Pt(16)

    for raw_block in re.split(r"\n\s*\n", sanitize_text(text)):
        block = raw_block.strip()
        if not block:
            continue

        lines = block.splitlines()
        first = lines[0].strip()

        if (
            first.isupper()
            and len(first) <= 80
            and not first.endswith((".", ":", ";"))
        ):
            p = document.add_paragraph()
            r = p.add_run(first)
            r.bold = True
            r.font.name = "Times New Roman"
            r.font.size = Pt(12)
            for line in lines[1:]:
                p = document.add_paragraph(line.strip())
                p.paragraph_format.space_after = Pt(6)
                for r in p.runs:
                    r.font.name = "Times New Roman"
                    r.font.size = Pt(11)
        else:
            p = document.add_paragraph()
            p.paragraph_format.space_after = Pt(8)
            for idx, line in enumerate(lines):
                if idx:
                    p.add_run("\n")
                r = p.add_run(line.strip())
                r.font.name = "Times New Roman"
                r.font.size = Pt(11)

    term_items = terms_from_string(terms)
    if term_items:
        heading = document.add_paragraph()
        r = heading.add_run("SUPPLIED TERMS")
        r.bold = True
        r.font.name = "Times New Roman"
        r.font.size = Pt(12)

        table = document.add_table(rows=1, cols=2)
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        table.style = "Table Grid"
        hdr = table.rows[0].cells
        hdr[0].text = "No."
        hdr[1].text = "Term"
        for i, item in enumerate(term_items, start=1):
            cells = table.add_row().cells
            cells[0].text = str(i)
            cells[1].text = item
            for cell in cells:
                cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER

    _add_docx_footer(document)

    buffer = io.BytesIO()
    document.save(buffer)
    return buffer.getvalue()


def _pdf_multiline(pdf: FPDF, text: str, height: float = 6) -> None:
    """Write a multi-line block from the left margin with fpdf2-safe cursor handling."""
    pdf.set_x(pdf.l_margin)
    pdf.multi_cell(pdf.epw, height, _safe_pdf_text(text))
    pdf.set_x(pdf.l_margin)


class LegalPDF(FPDF):
    def __init__(self, doc_type: str):
        super().__init__()
        self.doc_type = sanitize_text(doc_type)

    def header(self):
        if LOGO_PATH.exists():
            try:
                self.image(str(LOGO_PATH), x=95, y=8, w=20)
            except Exception:
                pass
        self.set_y(30)
        self.set_font("Helvetica", "B", 13)
        self.cell(0, 8, _safe_pdf_text(self.doc_type.upper()), align="C")
        self.set_x(self.l_margin)
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_x(self.l_margin)
        self.set_font("Helvetica", "", 8)
        self.cell(
            0,
            8,
            "LegalEase - AI-assisted draft | Review before execution",
            align="C",
        )


def format_pdf(text: str, doc_type: str, terms: str = "") -> bytes:
    pdf = LegalPDF(doc_type)
    pdf.set_auto_page_break(auto=True, margin=18)
    pdf.add_page()
    pdf.set_font("Helvetica", "", 11)

    for raw_block in re.split(r"\n\s*\n", sanitize_text(text)):
        block = raw_block.strip()
        if not block:
            continue

        lines = block.splitlines()
        first = lines[0].strip()
        is_heading = (
            first.isupper()
            and len(first) <= 80
            and not first.endswith((".", ":", ";"))
        )

        if is_heading:
            pdf.set_font("Helvetica", "B", 11)
            _pdf_multiline(pdf, first, 7)
            pdf.set_font("Helvetica", "", 10.5)
            for line in lines[1:]:
                if line.strip():
                    _pdf_multiline(pdf, line.strip(), 6)
            pdf.ln(2)
        else:
            pdf.set_font("Helvetica", "", 10.5)
            for line in lines:
                if line.strip():
                    _pdf_multiline(pdf, line.strip(), 6)
            pdf.ln(2)

    term_items = terms_from_string(terms)
    if term_items:
        pdf.set_font("Helvetica", "B", 11)
        _pdf_multiline(pdf, "SUPPLIED TERMS", 7)
        pdf.set_font("Helvetica", "", 10)
        for i, item in enumerate(term_items, start=1):
            _pdf_multiline(pdf, f"{i}. {item}", 6)

    return bytes(pdf.output(dest="S"))


def format_txt(text: str) -> bytes:
    return sanitize_text(text).encode("utf-8")
