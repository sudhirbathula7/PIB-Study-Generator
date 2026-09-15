"""
PIB Study Generator
Main Pipeline

Workflow:

    input_today.txt
            |
            +---- RAW DATA ---------> raw_data archive
            |
            +---- SUMMARY ----------> Summary PDF
            |
            +---- QUICK REVISION ---> Quick Revision PDF
            |
            +---- MCQS -------------> MCQ PDF
            |
            +---- SUMMARY +
            |     QUICK REVISION +
            |     MCQS -------------> Complete PDF

Final PDFs are stored in:

    output/
        YEAR/
            MONTH/

The visual formatting of the PDFs is controlled by:

    tools/style_config.py
"""

from __future__ import annotations

import datetime
from pathlib import Path
import sys


# ============================================================
# PROJECT PATH
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent

INPUT_FILE = PROJECT_ROOT / "input_today.txt"


# ============================================================
# IMPORT GENERATORS
# ============================================================

try:
    from tools.generate_summary import generate_summary_pdf
    from tools.generate_mcqs import generate_mcq_pdf
    from tools.generate_combined import generate_combined_pdf

except ImportError as error:

    print()
    print("=" * 70)
    print("ERROR: Could not import the PDF generators.")
    print("=" * 70)
    print()
    print(f"Details: {error}")
    print()
    print("Make sure these files exist:")
    print()
    print("    tools/generate_summary.py")
    print("    tools/generate_mcqs.py")
    print("    tools/generate_combined.py")
    print()
    sys.exit(1)


# ============================================================
# DATE
# ============================================================

def get_today_info():
    """
    Return today's date information.
    """

    now = datetime.datetime.now()

    year = now.strftime("%Y")
    month = now.strftime("%B")
    yymmdd = now.strftime("%y%m%d")

    return (
        now,
        year,
        month,
        yymmdd,
    )


# ============================================================
# DIRECTORIES
# ============================================================

def create_directories(
    year: str,
    month: str,
):
    """
    Create the required project directories.

    RAW DATA archive:

        raw_data/
            YEAR/
                MONTH/

    Final PDFs:

        output/
            YEAR/
                MONTH/
    """

    raw_dir = (
        PROJECT_ROOT
        / "raw_data"
        / year
        / month
    )

    output_dir = (
        PROJECT_ROOT
        / "output"
        / year
        / month
    )

    raw_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    return (
        raw_dir,
        output_dir,
    )


# ============================================================
# INPUT PARSER
# ============================================================

def parse_input_file(
    content: str,
):
    """
    Parse input_today.txt.

    Expected structure:

        === RAW DATA ===

        ...

        === SUMMARY ===

        ...

        === QUICK REVISION ===

        ...

        === MCQS ===

        ...

    Returns:

        raw_data,
        summary,
        quick_revision,
        mcqs
    """

    raw_marker = "=== RAW DATA ==="
    summary_marker = "=== SUMMARY ==="
    quick_revision_marker = "=== QUICK REVISION ==="
    mcq_marker = "=== MCQS ==="

    # --------------------------------------------------------
    # Check all required markers
    # --------------------------------------------------------

    required_markers = [
        raw_marker,
        summary_marker,
        quick_revision_marker,
        mcq_marker,
    ]

    for marker in required_markers:

        if marker not in content:

            raise ValueError(
                f"Missing marker: {marker}"
            )

    # --------------------------------------------------------
    # RAW DATA
    # --------------------------------------------------------

    raw_data = (
        content
        .split(raw_marker, 1)[1]
        .split(summary_marker, 1)[0]
        .strip()
    )

    # --------------------------------------------------------
    # SUMMARY
    # --------------------------------------------------------

    summary = (
        content
        .split(summary_marker, 1)[1]
        .split(quick_revision_marker, 1)[0]
        .strip()
    )

    # --------------------------------------------------------
    # QUICK REVISION
    # --------------------------------------------------------

    quick_revision = (
        content
        .split(quick_revision_marker, 1)[1]
        .split(mcq_marker, 1)[0]
        .strip()
    )

    # --------------------------------------------------------
    # MCQS
    # --------------------------------------------------------

    mcqs = (
        content
        .split(mcq_marker, 1)[1]
        .strip()
    )

    return (
        raw_data,
        summary,
        quick_revision,
        mcqs,
    )


# ============================================================
# SAVE RAW DATA
# ============================================================

def save_raw_data(
    raw_data: str,
    raw_dir: Path,
    yymmdd: str,
):
    """
    Save RAW DATA to the archive.
    """

    output_file = (
        raw_dir
        / f"{yymmdd}.txt"
    )

    output_file.write_text(
        raw_data,
        encoding="utf-8",
    )

    print(
        "Raw data archived to:"
    )

    print(
        f"  {output_file}"
    )

    return output_file


# ============================================================
# GENERATE SUMMARY PDF
# ============================================================

def generate_summary(
    summary_text: str,
    output_dir: Path,
    yymmdd: str,
):
    """
    Generate the Summary PDF.
    """

    if not summary_text:

        print(
            "Summary section is empty."
        )

        print(
            "Skipping Summary PDF."
        )

        return None

    output_file = (
        output_dir
        / f"{yymmdd}_summary.pdf"
    )

    print()
    print(
        "Generating Summary PDF..."
    )

    try:

        result = generate_summary_pdf(
            summary_text,
            output_path=output_file,
            yymmdd_str=yymmdd,
        )

        return result

    except Exception as error:

        print()
        print(
            "ERROR while generating Summary PDF:"
        )

        print(error)

        return None


# ============================================================
# GENERATE QUICK REVISION PDF
# ============================================================

def generate_quick_revision(
    quick_revision_text: str,
    output_dir: Path,
    yymmdd: str,
):
    """
    Generate the Quick Revision PDF.

    The Quick Revision uses the same PDF engine as the Summary
    generator but is saved as a separate PDF.
    """

    if not quick_revision_text:

        print(
            "Quick Revision section is empty."
        )

        print(
            "Skipping Quick Revision PDF."
        )

        return None

    output_file = (
        output_dir
        / f"{yymmdd}_quick_revision.pdf"
    )

    print()
    print(
        "Generating Quick Revision PDF..."
    )

    try:

        result = generate_summary_pdf(
            quick_revision_text,
            output_path=output_file,
            yymmdd_str=yymmdd,
        )

        return result

    except Exception as error:

        print()
        print(
            "ERROR while generating Quick Revision PDF:"
        )

        print(error)

        return None


# ============================================================
# GENERATE MCQ PDF
# ============================================================

def generate_mcqs(
    mcq_text: str,
    output_dir: Path,
    yymmdd: str,
):
    """
    Generate the MCQ PDF.
    """

    if not mcq_text:

        print(
            "MCQ section is empty."
        )

        print(
            "Skipping MCQ PDF."
        )

        return None

    output_file = (
        output_dir
        / f"{yymmdd}_mcqs.pdf"
    )

    print()
    print(
        "Generating MCQ PDF..."
    )

    try:

        result = generate_mcq_pdf(
            mcq_text,
            output_path=output_file,
            yymmdd_str=yymmdd,
        )

        return result

    except Exception as error:

        print()
        print(
            "ERROR while generating MCQ PDF:"
        )

        print(error)

        return None


# ============================================================
# GENERATE COMPLETE PDF
# ============================================================

def generate_complete(
    summary_pdf,
    quick_revision_pdf,
    mcq_pdf,
    output_dir: Path,
    yymmdd: str,
):
    """
    Generate the Complete PDF.

    Exact order:

        1. Summary
        2. Quick Revision
        3. MCQs

    The Complete PDF is only created when all three
    individual PDFs were generated successfully.
    """

    if summary_pdf is None:

        print()
        print(
            "Summary PDF is unavailable."
        )

        print(
            "Skipping Complete PDF."
        )

        return None

    if quick_revision_pdf is None:

        print()
        print(
            "Quick Revision PDF is unavailable."
        )

        print(
            "Skipping Complete PDF."
        )

        return None

    if mcq_pdf is None:

        print()
        print(
            "MCQ PDF is unavailable."
        )

        print(
            "Skipping Complete PDF."
        )

        return None

    # --------------------------------------------------------
    # Verify files exist
    # --------------------------------------------------------

    summary_pdf = Path(summary_pdf)
    quick_revision_pdf = Path(quick_revision_pdf)
    mcq_pdf = Path(mcq_pdf)

    if not summary_pdf.exists():

        print(
            "Summary PDF file does not exist."
        )

        return None

    if not quick_revision_pdf.exists():

        print(
            "Quick Revision PDF file does not exist."
        )

        return None

    if not mcq_pdf.exists():

        print(
            "MCQ PDF file does not exist."
        )

        return None

    # --------------------------------------------------------
    # Complete PDF path
    # --------------------------------------------------------

    output_file = (
        output_dir
        / f"{yymmdd}_complete.pdf"
    )

    print()
    print(
        "Generating Complete PDF..."
    )

    try:

        result = generate_combined_pdf(
            summary_pdf=summary_pdf,
            quick_revision_pdf=quick_revision_pdf,
            mcq_pdf=mcq_pdf,
            output_path=output_file,
            open_after=True,
        )

        return result

    except Exception as error:

        print()
        print(
            "ERROR while generating Complete PDF:"
        )

        print(error)

        return None


# ============================================================
# MAIN PIPELINE
# ============================================================

def main():

    print()
    print("=" * 70)
    print("PIB STUDY GENERATOR")
    print("=" * 70)
    print()

    # --------------------------------------------------------
    # Date
    # --------------------------------------------------------

    (
        now,
        year,
        month,
        yymmdd,
    ) = get_today_info()

    print(
        f"Date: {now.strftime('%d-%B-%Y')}"
    )

    print(
        f"Project: {PROJECT_ROOT}"
    )

    print()

    # --------------------------------------------------------
    # Input file
    # --------------------------------------------------------

    if not INPUT_FILE.exists():

        print(
            "ERROR:"
        )

        print()

        print(
            f"Input file not found:\n"
            f"  {INPUT_FILE}"
        )

        print()

        print(
            "Create input_today.txt in the "
            "project root with:"
        )

        print()

        print(
            "=== RAW DATA ==="
        )

        print()

        print(
            "=== SUMMARY ==="
        )

        print()

        print(
            "=== QUICK REVISION ==="
        )

        print()

        print(
            "=== MCQS ==="
        )

        return

    # --------------------------------------------------------
    # Read input
    # --------------------------------------------------------

    try:

        content = INPUT_FILE.read_text(
            encoding="utf-8"
        )

    except Exception as error:

        print(
            "ERROR reading input_today.txt:"
        )

        print(error)

        return

    if not content.strip():

        print(
            "ERROR: input_today.txt is empty."
        )

        return

    # --------------------------------------------------------
    # Parse sections
    # --------------------------------------------------------

    try:

        (
            raw_data,
            summary_text,
            quick_revision_text,
            mcq_text,
        ) = parse_input_file(
            content
        )

    except ValueError as error:

        print()
        print(
            "ERROR in input_today.txt:"
        )

        print(error)

        print()

        print(
            "Expected markers:"
        )

        print()

        print(
            "=== RAW DATA ==="
        )

        print(
            "=== SUMMARY ==="
        )

        print(
            "=== QUICK REVISION ==="
        )

        print(
            "=== MCQS ==="
        )

        return

    # --------------------------------------------------------
    # Create directories
    # --------------------------------------------------------

    (
        raw_dir,
        output_dir,
    ) = create_directories(
        year,
        month,
    )

    print(
        "Final output directory:"
    )

    print(
        f"  {output_dir}"
    )

    print()

    # --------------------------------------------------------
    # Save RAW DATA
    # --------------------------------------------------------

    save_raw_data(
        raw_data,
        raw_dir,
        yymmdd,
    )

    # --------------------------------------------------------
    # Generate Summary
    # --------------------------------------------------------

    summary_pdf = generate_summary(
        summary_text,
        output_dir,
        yymmdd,
    )

    # --------------------------------------------------------
    # Generate Quick Revision
    # --------------------------------------------------------

    quick_revision_pdf = generate_quick_revision(
        quick_revision_text,
        output_dir,
        yymmdd,
    )

    # --------------------------------------------------------
    # Generate MCQs
    # --------------------------------------------------------

    mcq_pdf = generate_mcqs(
        mcq_text,
        output_dir,
        yymmdd,
    )

    # --------------------------------------------------------
    # Generate Complete PDF
    # --------------------------------------------------------

    complete_pdf = generate_complete(
        summary_pdf,
        quick_revision_pdf,
        mcq_pdf,
        output_dir,
        yymmdd,
    )

    # --------------------------------------------------------
    # Final report
    # --------------------------------------------------------

    print()
    print("=" * 70)
    print("PIPELINE COMPLETE")
    print("=" * 70)
    print()

    print(
        "Final output directory:"
    )

    print(
        f"  {output_dir}"
    )

    print()

    if summary_pdf:

        print(
            "✓ Summary PDF:"
        )

        print(
            f"  {summary_pdf}"
        )

        print()

    else:

        print(
            "✗ Summary PDF: NOT CREATED"
        )

        print()

    if quick_revision_pdf:

        print(
            "✓ Quick Revision PDF:"
        )

        print(
            f"  {quick_revision_pdf}"
        )

        print()

    else:

        print(
            "✗ Quick Revision PDF: NOT CREATED"
        )

        print()

    if mcq_pdf:

        print(
            "✓ MCQ PDF:"
        )

        print(
            f"  {mcq_pdf}"
        )

        print()

    else:

        print(
            "✗ MCQ PDF: NOT CREATED"
        )

        print()

    if complete_pdf:

        print(
            "✓ Complete PDF:"
        )

        print(
            f"  {complete_pdf}"
        )

        print()

    else:

        print(
            "✗ Complete PDF: NOT CREATED"
        )

        print()

    print("=" * 70)


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()
