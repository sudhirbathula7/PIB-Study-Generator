"""
PIB Study Generator
Compact Summary / Quick Revision PDF renderer.

The renderer intentionally follows the original reference layout:
- A4
- 8mm top/bottom margins
- 14mm left/right margins
- compact logo + title header
- blue divider
- 79% main content
- 21% Notes column
- dashed Notes separator
- tight paragraph/bullet spacing
"""

from pathlib import Path
import html
import re
import sys
import webbrowser

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.lib.units import mm

from . import style_config as style


# ============================================================
# BASIC HELPERS
# ============================================================

def format_date_str(value):
    if not value:
        return ""

    value = str(value).strip()

    # DDMMYYYY
    if len(value) == 8 and value.isdigit():
        return f"{value[:2]}-{value[2:4]}-{value[4:]}"

    return value


def open_pdf(path):
    """
    Open the generated PDF using the default system viewer.
    """
    try:
        webbrowser.open(Path(path).resolve().as_uri())
    except Exception:
        pass


def normalize_lines(data):
    if data is None:
        return []

    if isinstance(data, (list, tuple)):
        return [str(item).rstrip() for item in data]

    text = str(data)
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    return [line.rstrip() for line in text.split("\n")]


# ============================================================
# TEXT CLEANING
# ============================================================

def strip_html(text):
    """
    Remove HTML from incoming AI-generated text.

    This is important because the previous renderer allowed
    generated HTML such as <div>, <span>, etc. to leak into
    the final PDF.
    """

    text = str(text)

    text = re.sub(
        r"<br\s*/?>",
        "\n",
        text,
        flags=re.IGNORECASE,
    )

    text = re.sub(
        r"</p\s*>",
        "\n",
        text,
        flags=re.IGNORECASE,
    )

    text = re.sub(
        r"<[^>]+>",
        "",
        text,
    )

    return html.unescape(text)


def safe_inline(text):
    """
    Convert limited Markdown to safe ReportLab markup.

    Raw HTML is removed first.
    """

    text = strip_html(text)

    # Escape XML/HTML characters before inserting our own tags.
    text = html.escape(
        text,
        quote=False,
    )

    # Inline code.
    text = re.sub(
        r"`([^`]+)`",
        r'<font name="Courier">\1</font>',
        text,
    )

    # Bold.
    text = re.sub(
        r"\*\*([^*]+)\*\*",
        r"<b>\1</b>",
        text,
    )

    text = re.sub(
        r"__([^_]+)__",
        r"<b>\1</b>",
        text,
    )

    # Italic.
    text = re.sub(
        r"(?<!\*)\*([^*]+)\*(?!\*)",
        r"<i>\1</i>",
        text,
    )

    text = re.sub(
        r"(?<!_)_([^_]+)_(?!_)",
        r"<i>\1</i>",
        text,
    )

    return text.replace(
        "\n",
        "<br/>",
    )


# ============================================================
# TABLE PARSING
# ============================================================

def is_table_separator(line):
    cells = [
        cell.strip()
        for cell in line.strip().strip("|").split("|")
    ]

    if not cells:
        return False

    return all(
        re.fullmatch(r":?-{3,}:?", cell)
        for cell in cells
    )


def build_table(rows):
    """
    Convert a Markdown-style table into a compact ReportLab table.
    """

    if not rows:
        return None

    normalized = []

    for row in rows:
        normalized.append(
            [
                safe_inline(cell.strip())
                for cell in row
            ]
        )

    column_count = max(
        len(row)
        for row in normalized
    )

    for row in normalized:
        while len(row) < column_count:
            row.append("")

    table_data = []

    for row_index, row in enumerate(normalized):

        cells = []

        for cell in row:

            if row_index == 0:
                paragraph = Paragraph(
                    cell,
                    style.TABLE_HEADER_STYLE,
                )
            else:
                paragraph = Paragraph(
                    cell,
                    style.TABLE_STYLE,
                )

            cells.append(paragraph)

        table_data.append(cells)

    table = Table(
        table_data,
        repeatRows=1,
        hAlign="LEFT",
    )

    table.setStyle(
        TableStyle(
            [
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    style.TABLE_BORDER_COLOR,
                ),
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    style.TABLE_HEADER_BACKGROUND,
                ),
                (
                    "TEXTCOLOR",
                    (0, 0),
                    (-1, 0),
                    style.TABLE_HEADER_COLOR,
                ),
                (
                    "FONTNAME",
                    (0, 0),
                    (-1, 0),
                    style.BODY_BOLD_FONT,
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "TOP",
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    style.TABLE_CELL_PADDING_LEFT,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    style.TABLE_CELL_PADDING_RIGHT,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    style.TABLE_CELL_PADDING_TOP,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    style.TABLE_CELL_PADDING_BOTTOM,
                ),
            ]
        )
    )

    return table


# ============================================================
# MARKDOWN → REPORTLAB
# ============================================================

def parse_markdown(data):
    """
    Convert the limited Markdown structure produced by the
    study generator into ReportLab flowables.

    Supported:
    - # headings
    - ## headings
    - ### headings
    - numbered topic headings
    - • bullets
    - ○ sub-bullets
    - - / * bullets
    - Markdown tables
    - normal paragraphs
    """

    lines = normalize_lines(data)

    story = []

    index = 0

    while index < len(lines):

        raw_line = lines[index]
        stripped = raw_line.strip()

        # ----------------------------------------------------
        # Empty line
        # ----------------------------------------------------

        if not stripped:
            index += 1
            continue

        # ----------------------------------------------------
        # Markdown table
        # ----------------------------------------------------

        if (
            "|" in stripped
            and index + 1 < len(lines)
            and is_table_separator(lines[index + 1])
        ):

            rows = []

            while (
                index < len(lines)
                and "|" in lines[index].strip()
            ):

                row = [
                    cell.strip()
                    for cell in
                    lines[index]
                    .strip()
                    .strip("|")
                    .split("|")
                ]

                rows.append(row)

                index += 1

            if len(rows) >= 2:

                table = build_table(rows)

                if table:
                    story.append(table)
                    story.append(
                        Spacer(1, 3)
                    )

            continue

        # ----------------------------------------------------
        # Markdown headings
        # ----------------------------------------------------

        heading_match = re.match(
            r"^(#{1,6})\s+(.+)$",
            stripped,
        )

        if heading_match:

            level = len(
                heading_match.group(1)
            )

            heading_text = (
                heading_match.group(2).strip()
            )

            if level == 1:
                paragraph_style = style.H1_STYLE

            elif level == 2:
                paragraph_style = style.H2_STYLE

            elif level == 3:
                paragraph_style = style.H3_STYLE

            else:
                paragraph_style = style.H4_STYLE

            story.append(
                Paragraph(
                    safe_inline(heading_text),
                    paragraph_style,
                )
            )

            index += 1
            continue

        # ----------------------------------------------------
        # Numbered topic heading
        #
        # Example:
        # 1. Data Centre Infrastructure in India
        # ----------------------------------------------------

        numbered_heading = re.match(
            r"^(\d+)\.\s+(.+)$",
            stripped,
        )

        if numbered_heading:

            text = stripped

            story.append(
                Paragraph(
                    safe_inline(text),
                    style.H3_STYLE,
                )
            )

            index += 1
            continue

        # ----------------------------------------------------
        # Bullet / sub-bullet
        # ----------------------------------------------------

        bullet_match = re.match(
            r"^(\s*)([-*•○◦])\s+(.*)$",
            raw_line,
        )

        if bullet_match:

            indentation = bullet_match.group(1)
            marker = bullet_match.group(2)
            text = bullet_match.group(3)

            indentation_spaces = len(
                indentation.expandtabs(4)
            )

            is_subbullet = (
                indentation_spaces >= 2
                or marker in ("○", "◦")
            )

            if is_subbullet:

                bullet_style = style.SUB_BULLET_STYLE

                if marker in ("○", "◦"):
                    bullet_character = marker
                else:
                    bullet_character = (
                        style.SUB_BULLET
                    )

            else:

                bullet_style = style.BULLET_STYLE

                if marker in ("•",):
                    bullet_character = marker
                else:
                    bullet_character = (
                        style.MAIN_BULLET
                    )

            paragraph_text = (
                f"{bullet_character} "
                f"{safe_inline(text)}"
            )

            story.append(
                Paragraph(
                    paragraph_text,
                    bullet_style,
                )
            )

            index += 1
            continue

        # ----------------------------------------------------
        # Horizontal rule
        # ----------------------------------------------------

        if re.fullmatch(
            r"[-*_]{3,}",
            stripped,
        ):

            index += 1
            continue

        # ----------------------------------------------------
        # Ordinary paragraph
        # ----------------------------------------------------

        story.append(
            Paragraph(
                safe_inline(stripped),
                style.BODY_STYLE,
            )
        )

        index += 1

    return story


# ============================================================
# TITLE
# ============================================================

def infer_title(output_path):
    """
    Determine whether the output is Summary or Quick Revision.
    """

    name = str(output_path).lower()

    if (
        "quick_revision" in name
        or "quick-revision" in name
        or "revision" in name
    ):
        return "Quick Revision"

    return "Summary"


# ============================================================
# LOGO
# ============================================================

def get_logo_path():
    """
    Find the project logo.

    Several common filenames are supported so the renderer
    remains compatible with the existing project.
    """

    project_root = (
        Path(__file__).resolve().parent.parent
    )

    candidates = [
        project_root / "assets" / "brand_logo.png",
        project_root / "assets" / "logo.png",
        project_root / "assets" / "logo.jpg",
        project_root / "assets" / "logo.jpeg",
    ]

    for candidate in candidates:

        if candidate.exists():
            return candidate

    return None


# Compatibility alias used by the MCQ renderer.
_logo_path = get_logo_path


# ============================================================
# SHARED HEADER / FOOTER
# ============================================================

def draw_header(canvas, doc):

    page_width, page_height = A4

    left = style.MARGIN_LEFT
    right = (
        page_width
        - style.MARGIN_RIGHT
    )

    top = (
        page_height
        - style.MARGIN_TOP
    )

    # --------------------------------------------------------
    # Logo
    # --------------------------------------------------------

    logo_path = get_logo_path()

    if logo_path:

        try:

            from reportlab.lib.utils import ImageReader

            image = ImageReader(
                str(logo_path)
            )

            image_width, image_height = (
                image.getSize()
            )

            target_width = (
                style.HEADER_LOGO_WIDTH
            )

            target_height = (
                target_width
                * image_height
                / image_width
            )

            canvas.drawImage(
                image,
                left,
                top - target_height,
                width=target_width,
                height=target_height,
                preserveAspectRatio=True,
                mask="auto",
            )

        except Exception:
            pass

    # --------------------------------------------------------
    # Header title
    # --------------------------------------------------------

    title_x = (
        left
        + style.HEADER_LOGO_CELL_WIDTH
        + 0
    )

    title = getattr(
        doc,
        "_pib_header_title",
        style.BRAND_NAME,
    )

    canvas.setFont(
        style.BODY_BOLD_FONT,
        style.HEADER_TITLE_SIZE,
    )

    canvas.setFillColor(
        style.HEADER_TITLE_COLOR
    )

    max_title_width = (
        right
        - title_x
    )

    words = title.split()

    lines = []
    current_line = ""

    for word in words:

        candidate = (
            word
            if not current_line
            else f"{current_line} {word}"
        )

        candidate_width = canvas.stringWidth(
            candidate,
            style.BODY_BOLD_FONT,
            style.HEADER_TITLE_SIZE,
        )

        if candidate_width <= max_title_width:

            current_line = candidate

        else:

            if current_line:
                lines.append(
                    current_line
                )

            current_line = word

    if current_line:
        lines.append(current_line)

    title_y = top - 12

    for line in lines[:2]:

        canvas.drawString(
            title_x,
            title_y,
            line,
        )

        title_y -= (
            style.HEADER_TITLE_LEADING
        )

    # --------------------------------------------------------
    # Blue divider
    # --------------------------------------------------------

    divider_y = (
        top
        - max(
            30,
            len(lines[:2])
            * style.HEADER_TITLE_LEADING
            + 8,
        )
    )

    canvas.setStrokeColor(
        style.HEADER_DIVIDER_COLOR
    )

    canvas.setLineWidth(
        style.HEADER_DIVIDER_WIDTH
    )

    canvas.line(
        left,
        divider_y,
        right,
        divider_y,
    )

    # --------------------------------------------------------
    # Date
    # --------------------------------------------------------

    date_text = getattr(
        doc,
        "_pib_date_text",
        "",
    )

    if date_text:

        canvas.setFont(
            style.BODY_FONT,
            7.5,
        )

        canvas.setFillColor(
            style.NOTES_TEXT_COLOR
        )

        canvas.drawRightString(
            right,
            divider_y - 10,
            date_text,
        )

    # --------------------------------------------------------
    # Notes separator
    # --------------------------------------------------------

    usable_width = (
        page_width
        - style.MARGIN_LEFT
        - style.MARGIN_RIGHT
    )

    content_width = (
        usable_width
        * style.CONTENT_COLUMN_RATIO
    )

    separator_x = (
        style.MARGIN_LEFT
        + content_width
    )

    canvas.setStrokeColor(
        style.NOTES_SEPARATOR_COLOR
    )

    canvas.setLineWidth(
        style.NOTES_SEPARATOR_WIDTH
    )

    canvas.setDash(
        2,
        2,
    )

    canvas.line(
        separator_x,
        divider_y - 3,
        separator_x,
        style.MARGIN_BOTTOM + 3,
    )

    canvas.setDash()

    # --------------------------------------------------------
    # Notes label
    # --------------------------------------------------------

    notes_center = (
        separator_x
        + (
            usable_width
            * style.NOTES_COLUMN_RATIO
            / 2
        )
    )

    canvas.setFont(
        style.BODY_FONT,
        style.NOTES_TEXT_SIZE,
    )

    canvas.setFillColor(
        style.NOTES_TEXT_COLOR
    )

    canvas.drawCentredString(
        notes_center,
        divider_y - 16,
        "NOTES",
    )


def draw_footer(canvas, doc):

    page_width, _ = A4

    left = style.MARGIN_LEFT

    right = (
        page_width
        - style.MARGIN_RIGHT
    )

    footer_y = 4.5 * mm

    canvas.setFont(
        style.BODY_FONT,
        style.FOOTER_FONT_SIZE,
    )

    canvas.setFillColor(
        style.FOOTER_COLOR
    )

    canvas.drawString(
        left,
        footer_y,
        style.BRAND_NAME,
    )

    canvas.drawRightString(
        right,
        footer_y,
        f"Page {doc.page}",
    )


def draw_page(canvas, doc):

    canvas.saveState()

    draw_header(
        canvas,
        doc,
    )

    draw_footer(
        canvas,
        doc,
    )

    canvas.restoreState()


# ============================================================
# DOCUMENT TEMPLATE
# ============================================================

class PIBSummaryDocTemplate(
    BaseDocTemplate
):

    def __init__(
        self,
        filename,
        header_title,
        date_text="",
    ):

        super().__init__(
            filename,
            pagesize=A4,
            leftMargin=style.MARGIN_LEFT,
            rightMargin=style.MARGIN_RIGHT,

            # Header occupies only a small compact area.
            topMargin=(
                style.MARGIN_TOP
                + 34
            ),

            bottomMargin=(
                style.MARGIN_BOTTOM
                + 4
            ),

            title=header_title,
            author=style.BRAND_NAME,
        )

        usable_width = (
            A4[0]
            - style.MARGIN_LEFT
            - style.MARGIN_RIGHT
        )

        main_width = (
            usable_width
            * style.CONTENT_COLUMN_RATIO
            - style.CONTENT_RIGHT_PADDING
        )

        frame_height = (
            A4[1]
            - self.topMargin
            - self.bottomMargin
        )

        main_frame = Frame(
            style.MARGIN_LEFT,
            self.bottomMargin,
            main_width,
            frame_height,
            leftPadding=0,
            rightPadding=0,
            topPadding=0,
            bottomPadding=0,
            id="PIBMainContent",
        )

        template = PageTemplate(
            id="PIBSummary",
            frames=[main_frame],
            onPage=draw_page,
        )

        self.addPageTemplates(
            [template]
        )

        self._pib_header_title = (
            header_title
        )

        self._pib_date_text = (
            date_text
        )


# ============================================================
# PUBLIC GENERATOR
# ============================================================

def generate_summary_pdf(
    summary_data,
    output_path=None,
    yymmdd_str="",
):
    """
    Generate either Summary or Quick Revision PDF.

    The actual visual layout is identical for both.
    """

    if output_path is None:
        output_path = Path(
            "summary.pdf"
        )

    output_path = Path(
        output_path
    )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    document_title = infer_title(
        output_path
    )

    date_text = format_date_str(
        yymmdd_str
    )

    document = PIBSummaryDocTemplate(
        str(output_path),
        header_title=style.BRAND_NAME,
        date_text=date_text,
    )

    story = []

    raw_text = str(
        summary_data or ""
    ).strip()

    # --------------------------------------------------------
    # Parse content
    # --------------------------------------------------------

    story.extend(
        parse_markdown(
            raw_text
        )
    )

    # --------------------------------------------------------
    # If content is empty
    # --------------------------------------------------------

    if not story:

        story.append(
            Paragraph(
                "No content available.",
                style.BODY_STYLE,
            )
        )

    # --------------------------------------------------------
    # Build
    # --------------------------------------------------------

    document.build(
        story
    )

    return str(
        output_path
    )


# ============================================================
# COMPATIBILITY ALIASES
# ============================================================

generate_summary = (
    generate_summary_pdf
)

generate_summary_pdf_file = (
    generate_summary_pdf
)


# ============================================================
# COMMAND LINE
# ============================================================

if __name__ == "__main__":

    if len(sys.argv) < 3:

        print(
            "Usage:"
        )

        print(
            "python tools/generate_summary.py "
            "INPUT.txt OUTPUT.pdf [DDMMYYYY]"
        )

        raise SystemExit(1)

    input_path = Path(
        sys.argv[1]
    )

    output_path = Path(
        sys.argv[2]
    )

    date_value = (
        sys.argv[3]
        if len(sys.argv) > 3
        else ""
    )

    input_text = (
        input_path
        .read_text(
            encoding="utf-8"
        )
    )

    generated = generate_summary_pdf(
        input_text,
        output_path=output_path,
        yymmdd_str=date_value,
    )

    print(
        f"Generated: {generated}"
    )