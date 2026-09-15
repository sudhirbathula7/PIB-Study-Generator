"""
PIB Study Generator
MCQ PDF Generator

This file is intentionally kept separate from the visual configuration.

To change:
    - fonts
    - font sizes
    - headings
    - colors
    - margins
    - spacing
    - logo
    - header/footer

edit:

    tools/style_config.py

The generator itself should mainly handle CONTENT and PDF generation.
"""

from __future__ import annotations

import base64
import os
import re
import webbrowser
from pathlib import Path
from typing import Optional

from markdown_pdf import MarkdownPdf, Section

try:
    from . import style_config as style
except ImportError:
    import style_config as style


# ============================================================
# BASIC HELPERS
# ============================================================

def get_logo_b64(logo_path=None) -> str:
    """
    Convert the configured logo into base64 so it can be embedded
    directly into the generated HTML/PDF.
    """

    if logo_path is None:
        logo_path = style.LOGO_PATH

    logo_path = Path(logo_path)

    if not logo_path.exists():
        return ""

    try:
        with open(logo_path, "rb") as file:
            return base64.b64encode(file.read()).decode("utf-8")
    except Exception:
        return ""


def format_date_str(yymmdd_str: str) -> str:
    """
    Convert YYMMDD into:

        DD-Month-YYYY

    Example:

        250915
        ->
        15-September-2025
    """

    if not yymmdd_str:
        return ""

    yymmdd_str = str(yymmdd_str).strip()

    if len(yymmdd_str) == 6 and yymmdd_str.isdigit():

        yy = "20" + yymmdd_str[0:2]
        mm = yymmdd_str[2:4]
        dd = yymmdd_str[4:6]

        months = {
            "01": "January",
            "02": "February",
            "03": "March",
            "04": "April",
            "05": "May",
            "06": "June",
            "07": "July",
            "08": "August",
            "09": "September",
            "10": "October",
            "11": "November",
            "12": "December",
        }

        month_name = months.get(mm)

        if month_name:
            return f"{dd}-{month_name}-{yy}"

    return yymmdd_str


def open_pdf(file_path) -> None:
    """
    Automatically open the generated PDF.

    Windows:
        os.startfile()

    Other systems:
        webbrowser.open()
    """

    absolute_path = os.path.abspath(file_path)

    if hasattr(os, "startfile"):
        try:
            os.startfile(absolute_path)
            return
        except Exception:
            pass

    try:
        webbrowser.open(f"file://{absolute_path}")
    except Exception:
        pass


def escape_html(text: str) -> str:
    """
    Escape basic HTML characters.

    We intentionally do not aggressively escape the entire input
    because the source material may already contain simple HTML.
    """

    if text is None:
        return ""

    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


# ============================================================
# MCQ PARSING
# ============================================================

def split_mcq_blocks(text: str) -> list[str]:
    """
    Split a raw MCQ document into individual questions.

    Recognises formats such as:

        1. Question...
        2. Question...

    and:

        Q1. Question...
        Q2. Question...
    """

    if not text:
        return []

    text = str(text).strip()

    pattern = r"(?=(?:^|\n)\s*(?:\d+\s*[.)]|Q\d+\s*[:.)]))"

    blocks = re.split(pattern, text, flags=re.IGNORECASE)

    cleaned = []

    for block in blocks:

        block = block.strip()

        if block:
            cleaned.append(block)

    return cleaned


def extract_answer(block: str) -> tuple[str, str]:
    """
    Extract:

        Answer: B

    from a question block.

    Returns:

        answer_text, remaining_question
    """

    match = re.search(
        r"\b(?:Answer|Ans)\s*:\s*(.*?)(?=\bExplanation\s*:|$)",
        block,
        flags=re.IGNORECASE | re.DOTALL,
    )

    if not match:
        return "", block

    answer = match.group(1).strip()

    remaining = (
        block[: match.start()] +
        block[match.end():]
    ).strip()

    return answer, remaining


def extract_explanation(block: str) -> tuple[str, str]:
    """
    Extract:

        Explanation: ...

    from a question block.
    """

    match = re.search(
        r"\bExplanation\s*:\s*(.*)$",
        block,
        flags=re.IGNORECASE | re.DOTALL,
    )

    if not match:
        return "", block

    explanation = match.group(1).strip()

    remaining = block[: match.start()].strip()

    return explanation, remaining


def extract_options(text: str) -> tuple[str, list[tuple[str, str]]]:
    """
    Extract options from formats such as:

        (a) Delhi
        (b) Mumbai
        (c) Chennai
        (d) Kolkata

    or:

        a) Delhi
        b) Mumbai
        c) Chennai
        d) Kolkata

    Returns:

        question_text,
        options
    """

    if not text:
        return "", []

    option_pattern = re.compile(
        r"(?:^|\s)"
        r"(\([a-dA-D]\)|[a-dA-D][.)])"
        r"\s+",
        flags=re.MULTILINE,
    )

    matches = list(option_pattern.finditer(text))

    if not matches:
        return text.strip(), []

    first_match = matches[0]

    question_text = text[: first_match.start()].strip()

    options = []

    for index, match in enumerate(matches):

        label = match.group(1).strip()

        content_start = match.end()

        if index + 1 < len(matches):
            content_end = matches[index + 1].start()
        else:
            content_end = len(text)

        content = text[content_start:content_end].strip()

        if content:
            options.append((label, content))

    return question_text, options


def parse_statements(question_text: str) -> Optional[dict]:
    """
    Detect questions containing:

        Statement 1:
        Statement 2:

    and optionally:

        Which of the statements given above is/are correct?

    """

    if not re.search(
        r"\bStatement\s*1\s*:",
        question_text,
        flags=re.IGNORECASE,
    ):
        return None

    first_statement = re.search(
        r"\bStatement\s*1\s*:",
        question_text,
        flags=re.IGNORECASE,
    )

    if not first_statement:
        return None

    lead = question_text[: first_statement.start()].strip()

    statement_area = question_text[first_statement.start():].strip()

    which_match = re.search(
        r"\bWhich of the\b.*$",
        statement_area,
        flags=re.IGNORECASE | re.DOTALL,
    )

    if which_match:

        statements_text = statement_area[: which_match.start()].strip()

        which_text = which_match.group(0).strip()

    else:

        statements_text = statement_area
        which_text = ""

    statement_matches = list(
        re.finditer(
            r"Statement\s*(\d+)\s*:\s*",
            statements_text,
            flags=re.IGNORECASE,
        )
    )

    statements = []

    for index, match in enumerate(statement_matches):

        number = match.group(1)

        content_start = match.end()

        if index + 1 < len(statement_matches):
            content_end = statement_matches[index + 1].start()
        else:
            content_end = len(statements_text)

        content = statements_text[
            content_start:content_end
        ].strip()

        if content:
            statements.append((number, content))

    if not statements:
        return None

    return {
        "lead": lead,
        "statements": statements,
        "which": which_text,
    }


# ============================================================
# HTML BUILDING
# ============================================================

def build_statement_html(parsed: dict) -> str:
    """
    Convert statement-based question data into HTML.
    """

    html_parts = []

    lead = parsed.get("lead", "").strip()

    if lead:
        html_parts.append(
            f'<div class="mcq-lead">{lead}</div>'
        )

    statements = parsed.get("statements", [])

    if statements:

        html_parts.append(
            '<div class="mcq-statements">'
        )

        for number, content in statements:

            html_parts.append(
                '<div class="mcq-statement">'
                f'<span class="statement-number">{number}.</span> '
                f'{content}'
                '</div>'
            )

        html_parts.append("</div>")

    which = parsed.get("which", "").strip()

    if which:
        html_parts.append(
            f'<div class="mcq-which">{which}</div>'
        )

    return "\n".join(html_parts)


def build_options_html(
    options: list[tuple[str, str]]
) -> str:
    """
    Build a two-column option layout.
    """

    if not options:
        return ""

    rows = []

    for index in range(0, len(options), 2):

        row = options[index:index + 2]

        cells = []

        for label, content in row:

            cells.append(
                '<div class="option-cell">'
                f'<span class="option-label">{label}</span> '
                f'{content}'
                '</div>'
            )

        while len(cells) < 2:
            cells.append(
                '<div class="option-cell"></div>'
            )

        rows.append(
            '<div class="option-row">'
            + "".join(cells)
            + "</div>"
        )

    return (
        '<div class="options-grid">'
        + "\n".join(rows)
        + "</div>"
    )


def build_question_html(
    question_number: int,
    block: str,
) -> str:
    """
    Convert one raw MCQ block into HTML.
    """

    answer, block = extract_answer(block)

    explanation, block = extract_explanation(block)

    question_text, options = extract_options(block)

    statement_data = parse_statements(question_text)

    if statement_data:

        question_html = build_statement_html(
            statement_data
        )

    else:

        question_html = (
            f'<div class="mcq-lead">'
            f'{question_text}'
            f'</div>'
        )

    options_html = build_options_html(options)

    answer_html = ""

    if answer:

        answer_html = (
            '<div class="mcq-answer">'
            f'<strong>{style.ANSWER_LABEL}:</strong> '
            f'{answer}'
            '</div>'
        )

    explanation_html = ""

    if explanation:

        explanation_html = (
            '<div class="mcq-explanation">'
            f'<strong>{style.EXPLANATION_LABEL}:</strong> '
            f'{explanation}'
            '</div>'
        )

    return f"""
<div class="mcq-card">

    <div class="question-number">
        {style.QUESTION_NUMBER_FORMAT.format(
            number=question_number
        )}
    </div>

    <div class="question-content">
        {question_html}
    </div>

    {options_html}

    {answer_html}

    {explanation_html}

</div>
"""


def format_mcq_content(text: str) -> str:
    """
    Convert raw MCQ text into the HTML used by the PDF.

    If the input already contains our MCQ HTML structure,
    it is returned unchanged.
    """

    if not text:
        return ""

    text = str(text).strip()

    if (
        '<div class="mcq-card"' in text
        or '<div class="mcq-item"' in text
    ):
        return text

    blocks = split_mcq_blocks(text)

    if not blocks:
        return text

    formatted = []

    for index, block in enumerate(blocks, start=1):

        formatted.append(
            build_question_html(index, block)
        )

    return "\n".join(formatted)


# ============================================================
# CSS GENERATION
# ============================================================

def build_css() -> str:
    """
    Generate all MCQ CSS from style_config.py.

    This is deliberately kept in one place so the PDF
    appearance can be controlled from style_config.py.
    """

    page_margin_top = style.PAGE_MARGIN_TOP
    page_margin_right = style.PAGE_MARGIN_RIGHT
    page_margin_bottom = style.PAGE_MARGIN_BOTTOM
    page_margin_left = style.PAGE_MARGIN_LEFT

    return f"""
@page {{
    size: {style.PAGE_SIZE};
    margin:
        {page_margin_top}pt
        {page_margin_right}pt
        {page_margin_bottom}pt
        {page_margin_left}pt;
}}

* {{
    box-sizing: border-box;
}}

body {{
    font-family: "{style.BODY_FONT}";
    font-size: {style.BODY_FONT_SIZE}pt;
    line-height: {style.BODY_LEADING}pt;
    color: {style.BODY_COLOR};
    margin: 0;
    padding: 0;
}}

.header {{
    width: 100%;
    border-bottom:
        1px solid {style.COLOR_BLUE};
    padding-bottom: 6px;
    margin-bottom: 10px;
}}

.header-table {{
    width: 100%;
    border-collapse: collapse;
}}

.header-table td {{
    border: none;
    padding: 0;
    vertical-align: middle;
}}

.logo-cell {{
    width: {style.LOGO_WIDTH}px;
}}

.logo {{
    width: {style.LOGO_WIDTH}px;
    height: auto;
}}

.title-cell {{
    text-align: left;
    padding-left: 8px !important;
}}

.document-title {{
    font-family: "{style.TITLE_FONT}";
    font-size: {style.TITLE_FONT_SIZE}pt;
    color: {style.TITLE_COLOR};
    line-height: 1.15;
    margin: 0;
}}

.date-cell {{
    text-align: right;
    white-space: nowrap;
}}

.document-date {{
    font-family: "{style.SMALL_FONT}";
    font-size: {style.SMALL_FONT_SIZE}pt;
    color: {style.SMALL_COLOR};
}}

.content-area {{
    width: 100%;
}}

.mcq-card {{
    width: 100%;
    margin-bottom: {style.QUESTION_SPACE_AFTER}pt;
    padding-bottom: 5px;
    page-break-inside: avoid;
}}

.mcq-card + .mcq-card {{
    border-top:
        {style.DIVIDER_WIDTH}px
        dashed
        {style.DIVIDER_COLOR};
    padding-top: 6px;
}}

.question-number {{
    display: inline;
    font-family: "{style.QUESTION_NUMBER_FONT}";
    font-size: {style.QUESTION_NUMBER_SIZE}pt;
    color: {style.QUESTION_NUMBER_COLOR};
    margin-right: 4px;
}}

.question-content {{
    display: inline;
}}

.mcq-lead {{
    display: inline;
    font-family: "{style.QUESTION_FONT}";
    font-size: {style.QUESTION_FONT_SIZE}pt;
    color: {style.QUESTION_COLOR};
    line-height: {style.QUESTION_LEADING}pt;
}}

.mcq-statements {{
    margin-top: 3px;
    margin-bottom: 4px;
}}

.mcq-statement {{
    font-family: "{style.BODY_FONT}";
    font-size: {style.BODY_FONT_SIZE}pt;
    color: {style.BODY_COLOR};
    line-height: {style.BODY_LEADING}pt;
    margin-bottom: 2px;
}}

.statement-number {{
    font-family: "{style.QUESTION_NUMBER_FONT}";
    color: {style.QUESTION_NUMBER_COLOR};
}}

.mcq-which {{
    font-family: "{style.QUESTION_FONT}";
    font-size: {style.QUESTION_FONT_SIZE}pt;
    color: {style.QUESTION_COLOR};
    line-height: {style.QUESTION_LEADING}pt;
    margin-top: 3px;
    margin-bottom: 4px;
}}

.options-grid {{
    display: table;
    width: 100%;
    margin-top: 4px;
    margin-bottom: 4px;
}}

.option-row {{
    display: table-row;
}}

.option-cell {{
    display: table-cell;
    width: 50%;
    vertical-align: top;
    padding:
        {style.OPTION_SPACE_BEFORE}pt
        6pt
        {style.OPTION_SPACE_AFTER}pt
        0;
    font-family: "{style.OPTION_FONT}";
    font-size: {style.OPTION_FONT_SIZE}pt;
    color: {style.OPTION_COLOR};
    line-height: {style.OPTION_LEADING}pt;
}}

.option-label {{
    font-family: "{style.QUESTION_NUMBER_FONT}";
    color: {style.QUESTION_NUMBER_COLOR};
}}

.mcq-answer {{
    border-left:
        2px solid
        {style.COLOR_GREEN};
    padding: 3px 6px;
    margin-top: 4px;
    margin-bottom: 3px;
    font-family: "{style.ANSWER_FONT}";
    font-size: {style.ANSWER_FONT_SIZE}pt;
    color: {style.ANSWER_COLOR};
    line-height: {style.ANSWER_LEADING}pt;
}}

.mcq-explanation {{
    border-left:
        2px solid
        {style.DIVIDER_COLOR};
    padding: 3px 6px;
    margin-top: 2px;
    margin-bottom: 4px;
    font-family: "{style.EXPLANATION_FONT}";
    font-size: {style.EXPLANATION_FONT_SIZE}pt;
    color: {style.EXPLANATION_COLOR};
    line-height: {style.EXPLANATION_LEADING}pt;
}}

.mcq-explanation strong {{
    font-family: "{style.ANSWER_FONT}";
}}

.footer {{
    width: 100%;
    text-align: {style.FOOTER_ALIGNMENT.lower()};
    font-family: "{style.FOOTER_FONT}";
    font-size: {style.FOOTER_FONT_SIZE}pt;
    color: {style.FOOTER_COLOR};
    margin-top: 8px;
}}

.notes-column {{
    display: none;
}}
"""


# ============================================================
# HEADER HTML
# ============================================================

def build_header(
    formatted_date: str,
) -> str:
    """
    Build the document header.
    """

    logo_b64 = ""

    if style.SHOW_LOGO:
        logo_b64 = get_logo_b64()

    logo_html = ""

    if logo_b64:

        logo_html = (
            '<td class="logo-cell">'
            f'<img '
            f'src="data:image/png;base64,{logo_b64}" '
            f'class="logo" '
            f'alt="Logo"/>'
            '</td>'
        )

    title = style.TITLE_TEXT

    date_html = ""

    if formatted_date:

        date_html = (
            f'<div class="document-date">'
            f'Date: {formatted_date}'
            f'</div>'
        )

    return f"""
<div class="header">

<table class="header-table">
<tr>

{logo_html}

<td class="title-cell">
    <div class="document-title">
        {title}
    </div>
</td>

<td class="date-cell">
    {date_html}
</td>

</tr>
</table>

</div>
"""


# ============================================================
# FOOTER HTML
# ============================================================

def build_footer() -> str:
    """
    Build the footer if enabled.
    """

    if not style.SHOW_FOOTER:
        return ""

    footer_text = style.FOOTER_TEXT

    return f"""
<div class="footer">
    {footer_text}
</div>
"""


# ============================================================
# OUTPUT PATH
# ============================================================

def default_output_path(
    yymmdd_str: str,
) -> Path:
    """
    Generate the default output path.

    Example:

        output/
            2025/
                September/
                    15/
                        250915_mcqs.pdf
    """

    date_text = format_date_str(yymmdd_str)

    if (
        len(yymmdd_str) == 6
        and yymmdd_str.isdigit()
    ):

        year = "20" + yymmdd_str[:2]

        parts = date_text.split("-")

        if len(parts) == 3:

            day = parts[0]
            month = parts[1]

        else:

            day = yymmdd_str[4:6]
            month = "Unknown"

    else:

        year = "Unknown"
        month = "Unknown"
        day = "Unknown"

    return (
        style.OUTPUT_DIR
        / year
        / month
        / day
        / f"{yymmdd_str}_mcqs.pdf"
    )


# ============================================================
# PDF GENERATOR
# ============================================================

def generate_mcq_pdf(
    mcq_data,
    output_path=None,
    yymmdd_str="",
):
    """
    Generate an MCQ PDF.

    Parameters
    ----------
    mcq_data:
        Raw MCQ text.

    output_path:
        Optional output PDF path.

    yymmdd_str:
        Optional date in YYMMDD format.

    Returns
    -------
    Path
        The generated PDF path.
    """

    if mcq_data is None:
        mcq_data = ""

    mcq_data = str(mcq_data)

    formatted_date = format_date_str(
        yymmdd_str
    )

    if output_path is None:

        output_path = default_output_path(
            yymmdd_str
        )

    output_path = Path(output_path)

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    structured_content = format_mcq_content(
        mcq_data
    )

    header_html = build_header(
        formatted_date
    )

    footer_html = build_footer()

    wrapped_content = f"""
{header_html}

<div class="content-area">

{structured_content}

</div>

{footer_html}
"""

    css = build_css()

    pdf = MarkdownPdf(
        toc_level=0
    )

    pdf.add_section(
        Section(
            wrapped_content,
            paper_size=style.PAGE_SIZE,
        ),
        user_css=css,
    )

    pdf.save(
        str(output_path)
    )

    print(
        f"Generated MCQ PDF: "
        f"{output_path.resolve()}"
    )

    open_pdf(output_path)

    return output_path


# ============================================================
# COMPATIBILITY ALIASES
# ============================================================

generate_mcqs = generate_mcq_pdf

generate_mcqs_pdf = generate_mcq_pdf


# ============================================================
# OPTIONAL COMMAND-LINE USAGE
# ============================================================

def main():
    """
    Simple command-line interface.

    Examples:

        python tools/generate_mcqs.py input.txt

        python tools/generate_mcqs.py input.txt 250915

        python tools/generate_mcqs.py input.txt 250915 output.pdf
    """

    import argparse

    parser = argparse.ArgumentParser(
        description="Generate a PDF from raw MCQs."
    )

    parser.add_argument(
        "input_file",
        help="Text file containing MCQs.",
    )

    parser.add_argument(
        "date",
        nargs="?",
        default="",
        help="Date in YYMMDD format.",
    )

    parser.add_argument(
        "output",
        nargs="?",
        default=None,
        help="Optional output PDF path.",
    )

    args = parser.parse_args()

    input_path = Path(args.input_file)

    if not input_path.exists():

        raise FileNotFoundError(
            f"Input file not found: {input_path}"
        )

    text = input_path.read_text(
        encoding="utf-8"
    )

    generate_mcq_pdf(
        text,
        output_path=args.output,
        yymmdd_str=args.date,
    )


if __name__ == "__main__":
    main()