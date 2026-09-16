"""
PIB Study Generator
Shared visual configuration for Summary and MCQ PDF renderers.

Design target:
- A4
- Compact 8mm top/bottom margins
- 14mm left/right margins
- Compact header
- 79% study-content column
- 21% Notes column
- Thin blue divider
- Dashed Notes separator
- Dense, readable study layout
"""

from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm


# ============================================================
# PAGE
# ============================================================

PAGE_SIZE = A4

MARGIN_TOP = 8 * mm
MARGIN_BOTTOM = 8 * mm
MARGIN_LEFT = 14 * mm
MARGIN_RIGHT = 14 * mm


# ============================================================
# HEADER
# ============================================================

HEADER_LOGO_WIDTH = 44
HEADER_LOGO_HEIGHT = 44

HEADER_LOGO_CELL_WIDTH = 52

HEADER_TITLE_SIZE = 14.5
HEADER_TITLE_LEADING = 17

HEADER_TITLE_COLOR = colors.HexColor("#1A365D")

HEADER_DIVIDER_COLOR = colors.HexColor("#2B6CB0")
HEADER_DIVIDER_WIDTH = 2


# ============================================================
# CONTENT / NOTES COLUMNS
# ============================================================

CONTENT_COLUMN_RATIO = 0.79
NOTES_COLUMN_RATIO = 0.21

CONTENT_RIGHT_PADDING = 10
NOTES_LEFT_PADDING = 8

NOTES_SEPARATOR_COLOR = colors.HexColor("#CBD5E0")
NOTES_SEPARATOR_WIDTH = 0.8

NOTES_TEXT_COLOR = colors.HexColor("#A0AEC0")
NOTES_TEXT_SIZE = 7.5


# ============================================================
# BODY
# ============================================================

BODY_FONT = "Helvetica"
BODY_BOLD_FONT = "Helvetica-Bold"

BODY_SIZE = 10
BODY_LEADING = 13.5

BODY_COLOR = colors.HexColor("#1A202C")


# ============================================================
# HEADINGS
# ============================================================

H1_SIZE = 11
H1_LEADING = 13

H2_SIZE = 11
H2_LEADING = 13

H3_SIZE = 10
H3_LEADING = 12

H4_SIZE = 9.5
H4_LEADING = 11


H1_COLOR = colors.HexColor("#1A365D")
H2_COLOR = colors.HexColor("#2B6CB0")
H3_COLOR = colors.HexColor("#2C5282")
H4_COLOR = colors.HexColor("#9C4221")


# ============================================================
# SPACING
# ============================================================

PARAGRAPH_SPACE_BEFORE = 2
PARAGRAPH_SPACE_AFTER = 3

BULLET_SPACE_AFTER = 2
SUB_BULLET_SPACE_AFTER = 2

H1_SPACE_BEFORE = 5
H1_SPACE_AFTER = 2

H2_SPACE_BEFORE = 5
H2_SPACE_AFTER = 2

H3_SPACE_BEFORE = 4
H3_SPACE_AFTER = 2

H4_SPACE_BEFORE = 3
H4_SPACE_AFTER = 1


# ============================================================
# BULLETS
# ============================================================

MAIN_BULLET = "•"
SUB_BULLET = "○"

MAIN_BULLET_LEFT = 14
MAIN_BULLET_FIRST = 0

SUB_BULLET_LEFT = 25
SUB_BULLET_FIRST = 0


# ============================================================
# TABLES
# ============================================================

TABLE_FONT_SIZE = 8.5
TABLE_LEADING = 10.4

TABLE_BORDER_COLOR = colors.HexColor("#CBD5E0")
TABLE_HEADER_BACKGROUND = colors.HexColor("#EBF8FF")
TABLE_HEADER_COLOR = colors.HexColor("#2C5282")

TABLE_CELL_PADDING_TOP = 3
TABLE_CELL_PADDING_BOTTOM = 3
TABLE_CELL_PADDING_LEFT = 5
TABLE_CELL_PADDING_RIGHT = 5


# ============================================================
# BLOCKQUOTES / CALLOUTS
# ============================================================

BLOCKQUOTE_BACKGROUND = colors.HexColor("#F7FAFC")
BLOCKQUOTE_BORDER = colors.HexColor("#3182CE")

BLOCKQUOTE_FONT_SIZE = 9
BLOCKQUOTE_LEADING = 11.5


# ============================================================
# MCQ
# ============================================================

MCQ_QUESTION_SIZE = 10
MCQ_QUESTION_LEADING = 13.2

MCQ_OPTION_SIZE = 9.5
MCQ_OPTION_LEADING = 12.2

MCQ_STATEMENT_SIZE = 9.5
MCQ_STATEMENT_LEADING = 12.2

MCQ_ANSWER_SIZE = 9
MCQ_ANSWER_LEADING = 11.5

MCQ_EXPLANATION_SIZE = 9
MCQ_EXPLANATION_LEADING = 11.5

MCQ_OPTION_GAP = 4

MCQ_BLOCK_SPACE_BEFORE = 4
MCQ_BLOCK_SPACE_AFTER = 5

MCQ_ANSWER_BACKGROUND = colors.HexColor("#F0FFF4")
MCQ_ANSWER_BORDER = colors.HexColor("#9AE6B4")

MCQ_EXPLANATION_BACKGROUND = colors.HexColor("#F7FAFC")
MCQ_EXPLANATION_BORDER = colors.HexColor("#CBD5E0")


# ============================================================
# FOOTER
# ============================================================

FOOTER_FONT_SIZE = 7
FOOTER_COLOR = colors.HexColor("#A0AEC0")


# ============================================================
# BRAND
# ============================================================

BRAND_NAME = "PIB Study Material"


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

ASSETS_DIR = PROJECT_ROOT / "assets"

LOGO_PATH = ASSETS_DIR / "brand_logo.png"


# ============================================================
# HELPERS
# ============================================================

def hex_to_rgb(hex_color: str):
    """
    Convert #RRGGBB to an RGB tuple in the 0-1 range.
    """
    value = hex_color.lstrip("#")

    if len(value) != 6:
        raise ValueError(f"Invalid hex colour: {hex_color}")

    return (
        int(value[0:2], 16) / 255.0,
        int(value[2:4], 16) / 255.0,
        int(value[4:6], 16) / 255.0,
    )


def mm_to_pt(value):
    """
    Millimetres to ReportLab points.
    """
    return value * mm


def get_logo_path():
    """
    Return the configured logo path if available.
    """
    if LOGO_PATH.exists():
        return LOGO_PATH

    return None


def get_font_file(font_name):
    """
    Kept for compatibility with older generator code.
    Helvetica is built into ReportLab, so no external font file
    is required.
    """
    return None


# ============================================================
# SHARED PARAGRAPH STYLES
# ============================================================

BODY_STYLE = ParagraphStyle(
    "PIBBody",
    fontName=BODY_FONT,
    fontSize=BODY_SIZE,
    leading=BODY_LEADING,
    textColor=BODY_COLOR,
    alignment=TA_LEFT,
    spaceBefore=PARAGRAPH_SPACE_BEFORE,
    spaceAfter=PARAGRAPH_SPACE_AFTER,
    allowWidows=0,
    allowOrphans=0,
)


H1_STYLE = ParagraphStyle(
    "PIBH1",
    parent=BODY_STYLE,
    fontName=BODY_BOLD_FONT,
    fontSize=H1_SIZE,
    leading=H1_LEADING,
    textColor=H1_COLOR,
    spaceBefore=H1_SPACE_BEFORE,
    spaceAfter=H1_SPACE_AFTER,
    borderColor=colors.HexColor("#E2E8F0"),
    borderWidth=0,
    borderPadding=0,
)


H2_STYLE = ParagraphStyle(
    "PIBH2",
    parent=BODY_STYLE,
    fontName=BODY_BOLD_FONT,
    fontSize=H2_SIZE,
    leading=H2_LEADING,
    textColor=H2_COLOR,
    spaceBefore=H2_SPACE_BEFORE,
    spaceAfter=H2_SPACE_AFTER,
)


H3_STYLE = ParagraphStyle(
    "PIBH3",
    parent=BODY_STYLE,
    fontName=BODY_BOLD_FONT,
    fontSize=H3_SIZE,
    leading=H3_LEADING,
    textColor=H3_COLOR,
    spaceBefore=H3_SPACE_BEFORE,
    spaceAfter=H3_SPACE_AFTER,
)


H4_STYLE = ParagraphStyle(
    "PIBH4",
    parent=BODY_STYLE,
    fontName=BODY_BOLD_FONT,
    fontSize=H4_SIZE,
    leading=H4_LEADING,
    textColor=H4_COLOR,
    spaceBefore=H4_SPACE_BEFORE,
    spaceAfter=H4_SPACE_AFTER,
)


BULLET_STYLE = ParagraphStyle(
    "PIBBullet",
    parent=BODY_STYLE,
    fontName=BODY_FONT,
    fontSize=BODY_SIZE,
    leading=BODY_LEADING,
    leftIndent=MAIN_BULLET_LEFT,
    firstLineIndent=-MAIN_BULLET_LEFT,
    spaceBefore=0,
    spaceAfter=BULLET_SPACE_AFTER,
)


SUB_BULLET_STYLE = ParagraphStyle(
    "PISubBullet",
    parent=BODY_STYLE,
    fontName=BODY_FONT,
    fontSize=BODY_SIZE,
    leading=BODY_LEADING,
    leftIndent=SUB_BULLET_LEFT,
    firstLineIndent=-SUB_BULLET_LEFT,
    spaceBefore=0,
    spaceAfter=SUB_BULLET_SPACE_AFTER,
)


TABLE_STYLE = ParagraphStyle(
    "PIBTable",
    parent=BODY_STYLE,
    fontName=BODY_FONT,
    fontSize=TABLE_FONT_SIZE,
    leading=TABLE_LEADING,
    spaceBefore=0,
    spaceAfter=0,
)


TABLE_HEADER_STYLE = ParagraphStyle(
    "PIBTableHeader",
    parent=TABLE_STYLE,
    fontName=BODY_BOLD_FONT,
    textColor=TABLE_HEADER_COLOR,
)


MCQ_QUESTION_STYLE = ParagraphStyle(
    "PIBMCQQuestion",
    parent=BODY_STYLE,
    fontName=BODY_FONT,
    fontSize=MCQ_QUESTION_SIZE,
    leading=MCQ_QUESTION_LEADING,
    spaceBefore=0,
    spaceAfter=3,
)


MCQ_OPTION_STYLE = ParagraphStyle(
    "PIBMCQOption",
    parent=BODY_STYLE,
    fontName=BODY_FONT,
    fontSize=MCQ_OPTION_SIZE,
    leading=MCQ_OPTION_LEADING,
    spaceBefore=0,
    spaceAfter=1,
)


MCQ_STATEMENT_STYLE = ParagraphStyle(
    "PIBMCQStatement",
    parent=BODY_STYLE,
    fontName=BODY_FONT,
    fontSize=MCQ_STATEMENT_SIZE,
    leading=MCQ_STATEMENT_LEADING,
    leftIndent=12,
    firstLineIndent=-12,
    spaceBefore=0,
    spaceAfter=1,
)


MCQ_ANSWER_STYLE = ParagraphStyle(
    "PIBMCQAnswer",
    parent=BODY_STYLE,
    fontName=BODY_BOLD_FONT,
    fontSize=MCQ_ANSWER_SIZE,
    leading=MCQ_ANSWER_LEADING,
    textColor=colors.HexColor("#22543D"),
    spaceBefore=0,
    spaceAfter=0,
)


MCQ_EXPLANATION_STYLE = ParagraphStyle(
    "PIBMCQExplanation",
    parent=BODY_STYLE,
    fontName=BODY_FONT,
    fontSize=MCQ_EXPLANATION_SIZE,
    leading=MCQ_EXPLANATION_LEADING,
    spaceBefore=0,
    spaceAfter=0,
)


# ============================================================
# BACKWARD-COMPATIBILITY ALIASES
# ============================================================

PAGE_MARGINS = {
    "top": MARGIN_TOP,
    "bottom": MARGIN_BOTTOM,
    "left": MARGIN_LEFT,
    "right": MARGIN_RIGHT,
}

CONTENT_RATIO = CONTENT_COLUMN_RATIO
NOTES_RATIO = NOTES_COLUMN_RATIO