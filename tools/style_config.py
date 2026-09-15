"""
PIB Study Generator
Shared PDF styling configuration.

EDIT THIS FILE when you want to change:
- Fonts
- Font sizes
- Colors
- Headings
- Margins
- Spacing
- Logo
- Header / footer
- Question and answer formatting

The generators should NOT contain most visual formatting.
Instead, they import the settings from this file.
"""

from pathlib import Path


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

ASSETS_DIR = PROJECT_ROOT / "assets"
FONTS_DIR = PROJECT_ROOT / "fonts"
OUTPUT_DIR = PROJECT_ROOT / "output"

LOGO_PATH = ASSETS_DIR / "brand_logo.png"


# ============================================================
# FONT CONFIGURATION
# ============================================================
#
# OPTION 1:
# Use standard ReportLab fonts:
#
#     "Helvetica"
#     "Helvetica-Bold"
#     "Times-Roman"
#     "Times-Bold"
#     "Courier"
#
# OPTION 2:
# Put your .ttf fonts inside:
#
#     fonts/
#
# and specify their paths below.
#
# Example:
#
# REGULAR_FONT_FILE = FONTS_DIR / "NotoSans-Regular.ttf"
# BOLD_FONT_FILE = FONTS_DIR / "NotoSans-Bold.ttf"
#
# For now we use standard fonts so the program works
# immediately without requiring additional font files.
# ============================================================

FONT_NAME = "Helvetica"
FONT_NAME_BOLD = "Helvetica-Bold"
FONT_NAME_ITALIC = "Helvetica-Oblique"
FONT_NAME_BOLD_ITALIC = "Helvetica-BoldOblique"

# If you later want custom fonts, set these to actual .ttf files.
REGULAR_FONT_FILE = None
BOLD_FONT_FILE = None
ITALIC_FONT_FILE = None
BOLD_ITALIC_FONT_FILE = None


# ============================================================
# DOCUMENT TITLE
# ============================================================

TITLE_TEXT = "PIB Study Material"

TITLE_FONT = FONT_NAME_BOLD
TITLE_FONT_SIZE = 20

TITLE_COLOR = "#1F2937"

TITLE_ALIGNMENT = "CENTER"

TITLE_SPACE_BEFORE = 0
TITLE_SPACE_AFTER = 12


# ============================================================
# SUBTITLE
# ============================================================

SUBTITLE_FONT = FONT_NAME
SUBTITLE_FONT_SIZE = 11

SUBTITLE_COLOR = "#4B5563"

SUBTITLE_ALIGNMENT = "CENTER"

SUBTITLE_SPACE_BEFORE = 0
SUBTITLE_SPACE_AFTER = 16


# ============================================================
# MAIN SECTION HEADINGS
# ============================================================

SECTION_HEADING_FONT = FONT_NAME_BOLD
SECTION_HEADING_SIZE = 15

SECTION_HEADING_COLOR = "#111827"

SECTION_HEADING_ALIGNMENT = "LEFT"

SECTION_HEADING_SPACE_BEFORE = 14
SECTION_HEADING_SPACE_AFTER = 8

SECTION_HEADING_BORDER = False

SECTION_HEADING_BORDER_COLOR = "#D1D5DB"


# ============================================================
# SUBSECTION HEADINGS
# ============================================================

SUBHEADING_FONT = FONT_NAME_BOLD
SUBHEADING_SIZE = 12

SUBHEADING_COLOR = "#1F2937"

SUBHEADING_ALIGNMENT = "LEFT"

SUBHEADING_SPACE_BEFORE = 10
SUBHEADING_SPACE_AFTER = 5


# ============================================================
# BODY TEXT
# ============================================================

BODY_FONT = FONT_NAME
BODY_FONT_SIZE = 10

BODY_COLOR = "#111827"

BODY_ALIGNMENT = "JUSTIFY"

BODY_LEADING = 14

BODY_SPACE_BEFORE = 0
BODY_SPACE_AFTER = 6


# ============================================================
# SMALL / SECONDARY TEXT
# ============================================================

SMALL_FONT = FONT_NAME
SMALL_FONT_SIZE = 8.5

SMALL_COLOR = "#4B5563"

SMALL_LEADING = 11


# ============================================================
# QUESTION CONFIGURATION
# ============================================================

QUESTION_FONT = FONT_NAME_BOLD
QUESTION_FONT_SIZE = 11

QUESTION_COLOR = "#111827"

QUESTION_LEADING = 15

QUESTION_SPACE_BEFORE = 10
QUESTION_SPACE_AFTER = 5


# ============================================================
# QUESTION NUMBER
# ============================================================

QUESTION_NUMBER_FONT = FONT_NAME_BOLD
QUESTION_NUMBER_SIZE = 11

QUESTION_NUMBER_COLOR = "#111827"

QUESTION_NUMBER_FORMAT = "{number}."


# ============================================================
# OPTION CONFIGURATION
# ============================================================

OPTION_FONT = FONT_NAME
OPTION_FONT_SIZE = 10

OPTION_COLOR = "#111827"

OPTION_LEADING = 14

OPTION_INDENT = 18

OPTION_SPACE_BEFORE = 1
OPTION_SPACE_AFTER = 2

# Example:
#
# A. Option one
# B. Option two
# C. Option three
# D. Option four

OPTION_LABELS = [
    "A",
    "B",
    "C",
    "D",
]


# ============================================================
# ANSWER CONFIGURATION
# ============================================================

ANSWER_LABEL = "Answer"

ANSWER_FONT = FONT_NAME_BOLD
ANSWER_FONT_SIZE = 10

ANSWER_COLOR = "#111827"

ANSWER_LEADING = 14

ANSWER_SPACE_BEFORE = 5
ANSWER_SPACE_AFTER = 3


# ============================================================
# EXPLANATION CONFIGURATION
# ============================================================

EXPLANATION_LABEL = "Explanation"

EXPLANATION_FONT = FONT_NAME
EXPLANATION_FONT_SIZE = 9.5

EXPLANATION_COLOR = "#374151"

EXPLANATION_LEADING = 13

EXPLANATION_SPACE_BEFORE = 2
EXPLANATION_SPACE_AFTER = 8


# ============================================================
# SUMMARY CONFIGURATION
# ============================================================

SUMMARY_TITLE = "Summary"

SUMMARY_TITLE_FONT = FONT_NAME_BOLD
SUMMARY_TITLE_SIZE = 18

SUMMARY_TITLE_COLOR = "#111827"

SUMMARY_SECTION_FONT = FONT_NAME_BOLD
SUMMARY_SECTION_SIZE = 13

SUMMARY_SECTION_COLOR = "#1F2937"

SUMMARY_BODY_FONT = FONT_NAME
SUMMARY_BODY_SIZE = 10

SUMMARY_BODY_COLOR = "#111827"

SUMMARY_BODY_LEADING = 14


# ============================================================
# TABLE CONFIGURATION
# ============================================================

TABLE_FONT = FONT_NAME
TABLE_FONT_SIZE = 9

TABLE_HEADER_FONT = FONT_NAME_BOLD
TABLE_HEADER_SIZE = 9

TABLE_TEXT_COLOR = "#111827"
TABLE_HEADER_TEXT_COLOR = "#111827"

TABLE_HEADER_BACKGROUND = "#E5E7EB"
TABLE_BORDER_COLOR = "#9CA3AF"

TABLE_BORDER_WIDTH = 0.5

TABLE_CELL_PADDING = 5


# ============================================================
# PAGE CONFIGURATION
# ============================================================

PAGE_SIZE = "A4"

PAGE_MARGIN_LEFT = 42
PAGE_MARGIN_RIGHT = 42
PAGE_MARGIN_TOP = 45
PAGE_MARGIN_BOTTOM = 45


# ============================================================
# HEADER
# ============================================================

SHOW_HEADER = False

HEADER_TEXT = "PIB Study Generator"

HEADER_FONT = FONT_NAME
HEADER_FONT_SIZE = 8

HEADER_COLOR = "#6B7280"

HEADER_ALIGNMENT = "RIGHT"


# ============================================================
# FOOTER
# ============================================================

SHOW_FOOTER = True

FOOTER_TEXT = "PIB Study Generator"

FOOTER_FONT = FONT_NAME
FOOTER_FONT_SIZE = 8

FOOTER_COLOR = "#6B7280"

FOOTER_ALIGNMENT = "CENTER"

SHOW_PAGE_NUMBER = True

PAGE_NUMBER_FORMAT = "Page {page}"


# ============================================================
# LOGO
# ============================================================

SHOW_LOGO = True

LOGO_WIDTH = 90
LOGO_HEIGHT = 90

LOGO_ALIGNMENT = "CENTER"

LOGO_SPACE_BEFORE = 0
LOGO_SPACE_AFTER = 10


# ============================================================
# DIVIDERS
# ============================================================

SHOW_SECTION_DIVIDERS = False

DIVIDER_COLOR = "#D1D5DB"

DIVIDER_WIDTH = 0.5

DIVIDER_SPACE_BEFORE = 5
DIVIDER_SPACE_AFTER = 8


# ============================================================
# GENERAL SPACING
# ============================================================

PARAGRAPH_SPACE = 6

LINE_SPACING = 14

LIST_INDENT = 18

LIST_LEFT_INDENT = 18

LIST_RIGHT_INDENT = 0


# ============================================================
# COLORS
# ============================================================

COLOR_BLACK = "#000000"
COLOR_WHITE = "#FFFFFF"

COLOR_DARK = "#111827"
COLOR_GRAY = "#6B7280"
COLOR_LIGHT_GRAY = "#E5E7EB"

COLOR_BLUE = "#2563EB"
COLOR_GREEN = "#15803D"
COLOR_RED = "#DC2626"
COLOR_ORANGE = "#EA580C"


# ============================================================
# PDF METADATA
# ============================================================

PDF_AUTHOR = "PIB Study Generator"

PDF_TITLE_MCQ = "PIB Study Generator - MCQs"

PDF_TITLE_SUMMARY = "PIB Study Generator - Summary"

PDF_SUBJECT = "UPSC PIB Study Material"


# ============================================================
# EASY CUSTOMIZATION PRESETS
# ============================================================
#
# You normally do NOT need to change these.
#
# If you want a different visual theme later, we can modify
# this section and the rest of the generators will automatically
# use the new settings.
# ============================================================

THEME_NAME = "Clean Academic"

USE_ROUNDED_BOXES = False

USE_SHADOWS = False

USE_BACKGROUND_COLOR = False

PAGE_BACKGROUND_COLOR = "#FFFFFF"


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def hex_to_rgb(hex_color):
    """
    Convert a hex color such as '#1F2937' into RGB values
    between 0 and 1.

    Example:

        hex_to_rgb("#FF0000")

    returns:

        (1.0, 0.0, 0.0)
    """

    hex_color = hex_color.strip().lstrip("#")

    if len(hex_color) != 6:
        raise ValueError(
            f"Invalid hex color: {hex_color}. "
            "Use format '#RRGGBB'."
        )

    red = int(hex_color[0:2], 16) / 255
    green = int(hex_color[2:4], 16) / 255
    blue = int(hex_color[4:6], 16) / 255

    return red, green, blue


def get_font_file(font_file):
    """
    Return the font path if configured and available.
    Otherwise return None.
    """

    if font_file is None:
        return None

    path = Path(font_file)

    if path.exists():
        return path

    return None
