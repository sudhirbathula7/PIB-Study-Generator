"""
PIB Study Generator
Summary PDF Generator

This generator uses tools/style_config.py for visual formatting.

To change fonts, sizes, colours, margins, headings, logo,
header/footer, spacing, etc., edit style_config.py.
"""

from __future__ import annotations

import os
import re
import webbrowser
from pathlib import Path

from markdown_pdf import MarkdownPdf, Section

try:
    from . import style_config as style
except ImportError:
    import style_config as style


# ============================================================
# BASIC HELPERS
# ============================================================

def open_pdf(file_path) -> None:
    """
    Open the generated PDF automatically.
    """

    absolute_path = os.path.abspath(file_path)

    if hasattr(os, "startfile"):
        try:
            os.startfile(absolute_path)
            return
        except Exception:
            pass

    try:
        webbrowser.open(
            f"file://{absolute_path}"
        )
    except Exception:
        pass


def format_date_str(yymmdd_str: str) -> str:
    """
    Convert YYMMDD to DD-Month-YYYY.

    Example:

        250915

    becomes:

        15-September-2025
    """

    if not yymmdd_str:
        return ""

    value = str(yymmdd_str).strip()

    if len(value) == 6 and value.isdigit():

        year = "20" + value[:2]
        month = value[2:4]
        day = value[4:6]

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

        month_name = months.get(month)

        if month_name:
            return (
                f"{day}-{month_name}-{year}"
            )

    return value


# ============================================================
# TEXT CLEANING
# ============================================================

def clean_text(text: str) -> str:
    """
    Basic cleanup for source text.
    """

    if text is None:
        return ""

    text = str(text)

    text = text.replace(
        "\r\n",
        "\n",
    )

    text = text.replace(
        "\r",
        "\n",
    )

    # Remove excessive blank lines.
    text = re.sub(
        r"\n{3,}",
        "\n\n",
        text,
    )

    # Remove excessive spaces.
    text = re.sub(
        r"[ \t]+",
        " ",
        text,
    )

    return text.strip()


def escape_html(text: str) -> str:
    """
    Escape text for safe HTML insertion.
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
# MARKDOWN / SOURCE PARSING
# ============================================================

def normalize_markdown(text: str) -> str:
    """
    Normalise common Markdown heading formats.

    This lets the summary generator accept material such as:

        # Main Heading

        ## Section

        ### Subsection

    while keeping the styling controlled by CSS.
    """

    text = clean_text(text)

    lines = text.splitlines()

    output = []

    for line in lines:

        stripped = line.strip()

        if not stripped:
            output.append("")
            continue

        # Preserve Markdown headings.
        if re.match(
            r"^#{1,6}\s+",
            stripped,
        ):
            output.append(stripped)
            continue

        # Convert common all-caps section headings.
        if (
            len(stripped) < 100
            and stripped.isupper()
            and not stripped.endswith(".")
        ):
            output.append(
                "## " + stripped.title()
            )
            continue

        output.append(stripped)

    return "\n".join(output)


# ============================================================
# SUMMARY SECTIONS
# ============================================================

def detect_heading_level(line: str) -> int:
    """
    Detect a Markdown heading level.

    Returns 0 when the line is not a heading.
    """

    match = re.match(
        r"^\s*(#{1,6})\s+(.+)$",
        line,
    )

    if not match:
        return 0

    return len(match.group(1))


def heading_text(line: str) -> str:
    """
    Return the actual text of a Markdown heading.
    """

    return re.sub(
        r"^\s*#{1,6}\s+",
        "",
        line,
    ).strip()


def convert_summary_to_markdown(
    text: str,
) -> str:
    """
    Prepare summary content for MarkdownPdf.

    The content remains mostly Markdown so that users can
    freely edit the source material.

    The styling is handled separately by build_css().
    """

    text = normalize_markdown(text)

    if not text:
        return ""

    lines = text.splitlines()

    result = []

    for line in lines:

        stripped = line.strip()

        if not stripped:
            result.append("")
            continue

        # Keep headings.
        if stripped.startswith("#"):
            result.append(stripped)
            continue

        # Preserve Markdown bullets.
        if re.match(
            r"^[-*+]\s+",
            stripped,
        ):
            result.append(stripped)
            continue

        # Preserve numbered lists.
        if re.match(
            r"^\d+[.)]\s+",
            stripped,
        ):
            result.append(stripped)
            continue

        # Preserve blockquotes.
        if stripped.startswith(">"):
            result.append(stripped)
            continue

        result.append(stripped)

    return "\n".join(result)


# ============================================================
# CSS
# ============================================================

def build_css() -> str:
    """
    Generate the complete summary stylesheet from
    style_config.py.

    Edit style_config.py instead of changing this CSS
    unless you specifically need a new layout feature.
    """

    return f"""
@page {{
    size: {style.PAGE_SIZE};
    margin:
        {style.PAGE_MARGIN_TOP}pt
        {style.PAGE_MARGIN_RIGHT}pt
        {style.PAGE_MARGIN_BOTTOM}pt
        {style.PAGE_MARGIN_LEFT}pt;
}}

* {{
    box-sizing: border-box;
}}

body {{
    font-family: "{style.SUMMARY_BODY_FONT}";
    font-size: {style.SUMMARY_BODY_SIZE}pt;
    line-height: {style.SUMMARY_BODY_LEADING}pt;
    color: {style.SUMMARY_BODY_COLOR};
    margin: 0;
    padding: 0;
}}

.summary-header {{
    width: 100%;
    margin-bottom: 16px;
}}

.summary-logo {{
    display: block;
    margin-left: auto;
    margin-right: auto;
    width: {style.LOGO_WIDTH}px;
    height: auto;
    margin-bottom: {style.LOGO_SPACE_AFTER}pt;
}}

.summary-title {{
    font-family: "{style.SUMMARY_TITLE_FONT}";
    font-size: {style.SUMMARY_TITLE_SIZE}pt;
    color: {style.SUMMARY_TITLE_COLOR};
    text-align: {style.TITLE_ALIGNMENT.lower()};
    line-height: 1.2;
    margin-top: {style.TITLE_SPACE_BEFORE}pt;
    margin-bottom: {style.TITLE_SPACE_AFTER}pt;
}}

.summary-date {{
    font-family: "{style.SMALL_FONT}";
    font-size: {style.SMALL_FONT_SIZE}pt;
    color: {style.SMALL_COLOR};
    text-align: center;
    margin-bottom: 12px;
}}

h1 {{
    font-family: "{style.SUMMARY_TITLE_FONT}";
    font-size: {style.SUMMARY_TITLE_SIZE}pt;
    color: {style.SUMMARY_TITLE_COLOR};
    line-height: 1.2;
    margin-top: {style.TITLE_SPACE_BEFORE}pt;
    margin-bottom: {style.TITLE_SPACE_AFTER}pt;
    page-break-after: avoid;
}}

h2 {{
    font-family: "{style.SUMMARY_SECTION_FONT}";
    font-size: {style.SUMMARY_SECTION_SIZE}pt;
    color: {style.SUMMARY_SECTION_COLOR};
    line-height: 1.25;
    margin-top: {style.SECTION_HEADING_SPACE_BEFORE}pt;
    margin-bottom: {style.SECTION_HEADING_SPACE_AFTER}pt;
    page-break-after: avoid;
}}

h3 {{
    font-family: "{style.SUBHEADING_FONT}";
    font-size: {style.SUBHEADING_SIZE}pt;
    color: {style.SUBHEADING_COLOR};
    line-height: 1.25;
    margin-top: {style.SUBHEADING_SPACE_BEFORE}pt;
    margin-bottom: {style.SUBHEADING_SPACE_AFTER}pt;
    page-break-after: avoid;
}}

h4 {{
    font-family: "{style.SUBHEADING_FONT}";
    font-size: {style.SUBHEADING_SIZE}pt;
    color: {style.SUBHEADING_COLOR};
    line-height: 1.25;
    margin-top: {style.SUBHEADING_SPACE_BEFORE}pt;
    margin-bottom: {style.SUBHEADING_SPACE_AFTER}pt;
    page-break-after: avoid;
}}

p {{
    font-family: "{style.SUMMARY_BODY_FONT}";
    font-size: {style.SUMMARY_BODY_SIZE}pt;
    color: {style.SUMMARY_BODY_COLOR};
    line-height: {style.SUMMARY_BODY_LEADING}pt;
    margin-top: {style.BODY_SPACE_BEFORE}pt;
    margin-bottom: {style.BODY_SPACE_AFTER}pt;
    text-align: {style.BODY_ALIGNMENT.lower()};
}}

strong {{
    font-family: "{style.FONT_NAME_BOLD}";
}}

em {{
    font-family: "{style.FONT_NAME_ITALIC}";
}}

ul,
ol {{
    margin-top: 4px;
    margin-bottom: 8px;
    padding-left: {style.LIST_LEFT_INDENT}pt;
}}

li {{
    font-family: "{style.SUMMARY_BODY_FONT}";
    font-size: {style.SUMMARY_BODY_SIZE}pt;
    color: {style.SUMMARY_BODY_COLOR};
    line-height: {style.SUMMARY_BODY_LEADING}pt;
    margin-bottom: 3px;
}}

blockquote {{
    border-left:
        3px solid
        {style.DIVIDER_COLOR};
    margin-left: 8px;
    margin-right: 0;
    padding-left: 10px;
    color: {style.EXPLANATION_COLOR};
}}

table {{
    width: 100%;
    border-collapse: collapse;
    margin-top: 8px;
    margin-bottom: 10px;
}}

th {{
    font-family: "{style.TABLE_HEADER_FONT}";
    font-size: {style.TABLE_HEADER_SIZE}pt;
    color: {style.TABLE_HEADER_TEXT_COLOR};
    background-color: {style.TABLE_HEADER_BACKGROUND};
    border:
        {style.TABLE_BORDER_WIDTH}px solid
        {style.TABLE_BORDER_COLOR};
    padding: {style.TABLE_CELL_PADDING}pt;
    text-align: left;
}}

td {{
    font-family: "{style.TABLE_FONT}";
    font-size: {style.TABLE_FONT_SIZE}pt;
    color: {style.TABLE_TEXT_COLOR};
    border:
        {style.TABLE_BORDER_WIDTH}px solid
        {style.TABLE_BORDER_COLOR};
    padding: {style.TABLE_CELL_PADDING}pt;
    vertical-align: top;
}}

hr {{
    border: none;
    border-top:
        {style.DIVIDER_WIDTH}px solid
        {style.DIVIDER_COLOR};
    margin-top: {style.DIVIDER_SPACE_BEFORE}pt;
    margin-bottom: {style.DIVIDER_SPACE_AFTER}pt;
}}

.summary-footer {{
    width: 100%;
    text-align: {style.FOOTER_ALIGNMENT.lower()};
    font-family: "{style.FOOTER_FONT}";
    font-size: {style.FOOTER_FONT_SIZE}pt;
    color: {style.FOOTER_COLOR};
    margin-top: 15px;
}}

.page-break {{
    page-break-before: always;
}}

.no-break {{
    page-break-inside: avoid;
}}
"""


# ============================================================
# LOGO
# ============================================================

def build_logo_html() -> str:
    """
    Add the configured logo when enabled.

    Uses a normal file URL because MarkdownPdf/Chromium can
    load local images.
    """

    if not style.SHOW_LOGO:
        return ""

    logo_path = Path(style.LOGO_PATH)

    if not logo_path.exists():
        return ""

    logo_uri = logo_path.resolve().as_uri()

    return (
        '<img '
        f'src="{logo_uri}" '
        f'class="summary-logo" '
        'alt="Logo"/>'
    )


# ============================================================
# HEADER / FOOTER
# ============================================================

def build_header(
    formatted_date: str,
) -> str:
    """
    Build the summary title block.
    """

    logo_html = build_logo_html()

    date_html = ""

    if formatted_date:

        date_html = (
            '<div class="summary-date">'
            f'Date: {formatted_date}'
            '</div>'
        )

    return f"""
<div class="summary-header">

    {logo_html}

    <div class="summary-title">
        {style.SUMMARY_TITLE}
    </div>

    {date_html}

</div>
"""


def build_footer() -> str:
    """
    Build the footer.
    """

    if not style.SHOW_FOOTER:
        return ""

    return f"""
<div class="summary-footer">
    {style.FOOTER_TEXT}
</div>
"""


# ============================================================
# OUTPUT PATH
# ============================================================

def default_output_path(
    yymmdd_str: str,
) -> Path:
    """
    Generate a standard summary output path.
    """

    date_text = format_date_str(
        yymmdd_str
    )

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
        / f"{yymmdd_str}_summary.pdf"
    )


# ============================================================
# MAIN GENERATOR
# ============================================================

def generate_summary_pdf(
    summary_data,
    output_path=None,
    yymmdd_str="",
):
    """
    Generate a summary PDF.

    Parameters
    ----------
    summary_data:
        Summary text in Markdown/plain text.

    output_path:
        Optional output PDF path.

    yymmdd_str:
        Optional date in YYMMDD format.

    Returns
    -------
    Path
        Generated PDF path.
    """

    if summary_data is None:
        summary_data = ""

    summary_data = str(summary_data)

    if output_path is None:

        output_path = default_output_path(
            yymmdd_str
        )

    output_path = Path(output_path)

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    formatted_date = format_date_str(
        yymmdd_str
    )

    markdown_content = (
        convert_summary_to_markdown(
            summary_data
        )
    )

    header_html = build_header(
        formatted_date
    )

    footer_html = build_footer()

    document = f"""
{header_html}

<div class="summary-content">

{markdown_content}

</div>

{footer_html}
"""

    css = build_css()

    pdf = MarkdownPdf(
        toc_level=0
    )

    pdf.add_section(
        Section(
            document,
            paper_size=style.PAGE_SIZE,
        ),
        user_css=css,
    )

    pdf.save(
        str(output_path)
    )

    print(
        f"Generated summary PDF: "
        f"{output_path.resolve()}"
    )

    open_pdf(output_path)

    return output_path


# ============================================================
# COMPATIBILITY ALIASES
# ============================================================

generate_summary = generate_summary_pdf

generate_summary_pdf_file = generate_summary_pdf


# ============================================================
# COMMAND-LINE INTERFACE
# ============================================================

def main():
    """
    Command-line usage:

        python tools/generate_summary.py input.txt

        python tools/generate_summary.py input.txt 250915

        python tools/generate_summary.py input.txt 250915 output.pdf
    """

    import argparse

    parser = argparse.ArgumentParser(
        description="Generate a summary PDF."
    )

    parser.add_argument(
        "input_file",
        help="Text/Markdown file containing the summary.",
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

    input_path = Path(
        args.input_file
    )

    if not input_path.exists():

        raise FileNotFoundError(
            f"Input file not found: {input_path}"
        )

    summary_text = input_path.read_text(
        encoding="utf-8"
    )

    generate_summary_pdf(
        summary_text,
        output_path=args.output,
        yymmdd_str=args.date,
    )


if __name__ == "__main__":
    main()
