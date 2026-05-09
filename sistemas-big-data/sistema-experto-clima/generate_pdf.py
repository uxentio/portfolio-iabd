"""
Script to convert documentacion_tecnica.md to a professional PDF using fpdf2.
"""
import re
import os
from fpdf import FPDF


class TechDocPDF(FPDF):
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=25)

    def header(self):
        if self.page_no() > 1:
            self.set_font("Helvetica", "I", 8)
            self.set_text_color(100, 100, 100)
            self.cell(0, 10, "Documentacion Tecnica - Sistema Experto de Control Climatico", 0, 0, "L")
            self.cell(0, 10, "UT3T1", 0, 1, "R")
            self.set_draw_color(0, 102, 153)
            self.set_line_width(0.5)
            self.line(10, 18, 200, 18)
            self.ln(5)

    def footer(self):
        if self.page_no() == 1:
            return
        self.set_y(-20)
        self.set_draw_color(0, 102, 153)
        self.set_line_width(0.3)
        self.line(10, self.get_y(), 200, self.get_y())
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(100, 100, 100)
        self.cell(0, 10, f"Pagina {self.page_no() - 1}", 0, 0, "C")


def render_rich_text(pdf, text, font_family="Helvetica", font_size=11, line_height=6):
    """Render text with inline bold and inline code support."""
    parts = re.split(r'(\*\*.*?\*\*|`[^`]+`)', text)
    for part in parts:
        if part.startswith("**") and part.endswith("**"):
            inner = part[2:-2]
            pdf.set_font(font_family, "B", font_size)
            pdf.write(line_height, inner)
            pdf.set_font(font_family, "", font_size)
        elif part.startswith("`") and part.endswith("`"):
            inner = part[1:-1]
            pdf.set_font("Courier", "", font_size - 1)
            w = pdf.get_string_width(inner) + 2
            pdf.set_fill_color(235, 235, 235)
            pdf.cell(w, line_height, inner, fill=True)
            pdf.set_font(font_family, "", font_size)
        else:
            pdf.set_font(font_family, "", font_size)
            pdf.write(line_height, part)


def render_code_block(pdf, code_lines):
    """Render a code block with light background."""
    pdf.ln(2)
    pdf.set_font("Courier", "", 8)

    x_start = 15
    block_width = 180
    line_h = 5

    total_h = len(code_lines) * line_h + 6

    if pdf.get_y() + total_h > 270:
        pdf.add_page()

    y_start = pdf.get_y()

    pdf.set_fill_color(242, 244, 248)
    pdf.set_draw_color(190, 200, 215)
    pdf.rect(x_start, y_start, block_width, total_h, style="DF")

    pdf.set_y(y_start + 3)
    pdf.set_text_color(40, 40, 55)

    for cl in code_lines:
        pdf.set_x(x_start + 4)
        if len(cl) > 105:
            cl = cl[:102] + "..."
        pdf.cell(block_width - 8, line_h, cl)
        pdf.ln(line_h)

    pdf.set_y(y_start + total_h + 2)
    pdf.set_text_color(40, 40, 40)


def render_table(pdf, table_lines):
    """Render a markdown table."""
    if len(table_lines) < 2:
        return

    headers = [c.strip() for c in table_lines[0].split("|") if c.strip()]
    rows = []
    for tl in table_lines[2:]:
        cols = [c.strip() for c in tl.split("|") if c.strip()]
        if cols:
            rows.append(cols)

    num_cols = len(headers)
    if num_cols == 0:
        return

    available_width = 180
    pdf.set_font("Helvetica", "B", 9)

    max_widths = []
    for j in range(num_cols):
        max_w = pdf.get_string_width(headers[j]) + 6
        for row in rows:
            if j < len(row):
                w = pdf.get_string_width(row[j]) + 6
                max_w = max(max_w, w)
        max_widths.append(max_w)

    total_measured = sum(max_widths)
    if total_measured > available_width:
        col_widths = [w * available_width / total_measured for w in max_widths]
    else:
        extra = (available_width - total_measured) / num_cols
        col_widths = [w + extra for w in max_widths]

    x_start = 15
    row_h = 8

    total_table_h = (len(rows) + 1) * row_h + 4
    if pdf.get_y() + total_table_h > 270:
        pdf.add_page()

    # Header row
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_fill_color(0, 102, 153)
    pdf.set_text_color(255, 255, 255)
    pdf.set_x(x_start)
    for j, h in enumerate(headers):
        pdf.cell(col_widths[j], row_h, h, border=1, fill=True, align="C")
    pdf.ln(row_h)

    # Data rows
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(40, 40, 40)
    for ri, row in enumerate(rows):
        if ri % 2 == 0:
            pdf.set_fill_color(240, 245, 252)
        else:
            pdf.set_fill_color(255, 255, 255)
        pdf.set_x(x_start)
        for j in range(num_cols):
            val = row[j] if j < len(row) else ""
            pdf.cell(col_widths[j], row_h, val, border=1, fill=True, align="C")
        pdf.ln(row_h)


def build_cover_page(pdf):
    """Create a professional cover page."""
    pdf.add_page()

    # Top decorative bar
    pdf.set_fill_color(0, 102, 153)
    pdf.rect(0, 0, 210, 8, "F")

    # Orange accent line
    pdf.set_fill_color(230, 126, 34)
    pdf.rect(0, 8, 210, 3, "F")

    # Title block
    pdf.ln(50)
    # Left accent bar
    pdf.set_fill_color(0, 102, 153)
    pdf.rect(15, 55, 4, 50, "F")

    pdf.set_x(25)
    pdf.set_font("Helvetica", "B", 26)
    pdf.set_text_color(0, 51, 102)
    pdf.multi_cell(165, 14, "Sistema Experto de\nControl Climatico\nde Edificios", 0, "L")

    pdf.ln(5)
    # Orange separator
    pdf.set_fill_color(230, 126, 34)
    pdf.rect(25, pdf.get_y(), 80, 2, "F")
    pdf.ln(10)

    # Subtitle
    pdf.set_x(25)
    pdf.set_font("Helvetica", "", 16)
    pdf.set_text_color(80, 80, 80)
    pdf.cell(165, 10, "Documentacion Tecnica - UT3T1", 0, 1, "L")

    pdf.ln(5)
    pdf.set_x(25)
    pdf.set_font("Helvetica", "I", 13)
    pdf.set_text_color(100, 100, 100)
    pdf.multi_cell(165, 8, "Diseno e implementacion de un sistema\nexperto con Experta", 0, "L")

    # Info box at bottom
    pdf.ln(40)
    y_box_start = pdf.get_y()
    pdf.set_fill_color(240, 245, 250)
    pdf.rect(25, y_box_start, 160, 30, "F")
    pdf.set_draw_color(0, 102, 153)
    pdf.rect(25, y_box_start, 160, 30, "D")

    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(60, 60, 60)
    pdf.set_xy(30, y_box_start + 5)
    pdf.cell(70, 8, "Asignatura: Sistemas Expertos", 0, 0)
    pdf.set_xy(110, y_box_start + 5)
    pdf.cell(70, 8, "Framework: Experta (Python)", 0, 1)
    pdf.set_xy(30, y_box_start + 15)
    pdf.cell(70, 8, "Unidad: UT3T1", 0, 0)
    pdf.set_xy(110, y_box_start + 15)
    pdf.cell(70, 8, "Modelo: Series Temporales", 0, 1)

    # Bottom decorative bar
    pdf.set_fill_color(0, 102, 153)
    pdf.rect(0, 289, 210, 8, "F")


def build_pdf(md_content, output_path):
    pdf = TechDocPDF()
    pdf.alias_nb_pages()

    # Cover page
    build_cover_page(pdf)

    # Content pages
    pdf.add_page()

    lines = md_content.split("\n")
    i = 0
    in_code_block = False
    code_lines = []

    while i < len(lines):
        line = lines[i]

        # --- Code blocks ---
        if line.strip().startswith("```"):
            if not in_code_block:
                in_code_block = True
                code_lines = []
                i += 1
                continue
            else:
                in_code_block = False
                render_code_block(pdf, code_lines)
                pdf.ln(4)
                i += 1
                continue

        if in_code_block:
            code_lines.append(line)
            i += 1
            continue

        # --- Horizontal rule ---
        if line.strip() == "---":
            pdf.ln(4)
            pdf.set_draw_color(200, 200, 200)
            pdf.set_line_width(0.3)
            pdf.line(10, pdf.get_y(), 200, pdf.get_y())
            pdf.ln(6)
            i += 1
            continue

        # --- Empty line ---
        if line.strip() == "":
            pdf.ln(3)
            i += 1
            continue

        # --- Headings ---
        if line.startswith("# ") and not line.startswith("## "):
            # Skip the main title (already on cover)
            i += 1
            continue

        if line.startswith("## "):
            heading = line[3:].strip()
            pdf.ln(6)
            # Section heading with background
            if pdf.get_y() > 250:
                pdf.add_page()
            pdf.set_font("Helvetica", "B", 16)
            pdf.set_text_color(0, 51, 102)
            pdf.set_fill_color(240, 245, 250)
            pdf.cell(0, 12, f"  {heading}", 0, 1, "L", fill=True)
            pdf.set_draw_color(0, 102, 153)
            pdf.set_line_width(0.8)
            pdf.line(10, pdf.get_y(), 200, pdf.get_y())
            pdf.ln(5)
            pdf.set_text_color(40, 40, 40)
            i += 1
            continue

        if line.startswith("### "):
            heading = line[4:].strip()
            pdf.ln(4)
            if pdf.get_y() > 260:
                pdf.add_page()
            pdf.set_font("Helvetica", "B", 13)
            pdf.set_text_color(0, 80, 130)
            pdf.cell(0, 10, f"  {heading}", 0, 1, "L")
            pdf.set_draw_color(180, 200, 220)
            pdf.set_line_width(0.3)
            pdf.line(10, pdf.get_y(), 120, pdf.get_y())
            pdf.ln(3)
            pdf.set_text_color(40, 40, 40)
            i += 1
            continue

        # --- Tables ---
        if "|" in line and i + 1 < len(lines) and "---" in lines[i + 1]:
            table_lines = []
            while i < len(lines) and "|" in lines[i]:
                table_lines.append(lines[i])
                i += 1
            render_table(pdf, table_lines)
            pdf.ln(4)
            continue

        # --- Bullet points ---
        bullet_match = re.match(r'^(\s*)- (.+)', line)
        if bullet_match:
            indent_level = len(bullet_match.group(1)) // 2
            text = bullet_match.group(2)
            x_offset = 15 + indent_level * 8
            pdf.set_x(x_offset)
            pdf.set_font("Helvetica", "", 11)
            pdf.set_text_color(40, 40, 40)
            pdf.set_font("Helvetica", "B", 11)
            pdf.write(6, "  -  ")
            render_rich_text(pdf, text)
            pdf.ln(7)
            i += 1
            continue

        # --- Numbered lists ---
        num_match = re.match(r'^(\s*)(\d+)\. (.+)', line)
        if num_match:
            indent_level = len(num_match.group(1)) // 3
            num = num_match.group(2)
            text = num_match.group(3)
            x_offset = 15 + indent_level * 8
            pdf.set_x(x_offset)
            pdf.set_font("Helvetica", "B", 11)
            pdf.set_text_color(0, 80, 130)
            pdf.write(6, f"  {num}. ")
            pdf.set_text_color(40, 40, 40)
            render_rich_text(pdf, text)
            pdf.ln(7)
            i += 1
            continue

        # --- Bold-only lines ---
        bold_line_match = re.match(r'^\*\*(.+)\*\*$', line.strip())
        if bold_line_match:
            pdf.ln(3)
            pdf.set_font("Helvetica", "B", 11)
            pdf.set_text_color(40, 40, 40)
            pdf.cell(0, 7, bold_line_match.group(1))
            pdf.ln(7)
            i += 1
            continue

        # --- Regular text ---
        pdf.set_font("Helvetica", "", 11)
        pdf.set_text_color(40, 40, 40)
        clean_line = line.replace("\\>", ">").replace("\\<", "<")
        render_rich_text(pdf, clean_line)
        pdf.ln(7)
        i += 1

    pdf.output(output_path)


if __name__ == "__main__":
    md_path = r"D:\UT3T1 - Diseño e impl\documentacion_tecnica.md"
    pdf_path = r"D:\UT3T1 - Diseño e impl\documentacion_tecnica.pdf"

    content = open(md_path, "r", encoding="utf-8").read()
    build_pdf(content, pdf_path)

    size = os.path.getsize(pdf_path)
    print(f"PDF generated successfully: {pdf_path}")
    print(f"File size: {size:,} bytes ({size/1024:.1f} KB)")
