"""
PIB Study Generator
PDF merger.

Combines:
    1. Summary PDF
    2. Quick Revision PDF
    3. MCQ PDF

The individual PDFs are responsible for their own layout.
This file ONLY merges them in the required order.
"""

from pathlib import Path
import sys
import webbrowser

from pypdf import PdfReader, PdfWriter


# ============================================================
# OPEN PDF
# ============================================================

def open_pdf(path):
    """
    Open the generated PDF using the default application.
    """

    try:
        webbrowser.open(
            Path(path).resolve().as_uri()
        )
    except Exception:
        pass


# ============================================================
# VALIDATE PDF
# ============================================================

def validate_pdf(path):
    """
    Validate that a PDF exists and can be read.
    """

    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(
            f"PDF not found: {path}"
        )

    if path.stat().st_size == 0:
        raise ValueError(
            f"PDF is empty: {path}"
        )

    try:
        reader = PdfReader(
            str(path)
        )

        if len(reader.pages) == 0:
            raise ValueError(
                f"PDF contains no pages: {path}"
            )

    except Exception as exc:
        raise ValueError(
            f"Unable to read PDF: {path}\n{exc}"
        ) from exc

    return path


# ============================================================
# MERGE
# ============================================================

def generate_combined_pdf(
    summary_pdf,
    quick_revision_pdf,
    mcq_pdf,
    output_path,
    open_after=False,
):
    """
    Merge the three generated PDFs in this exact order:

        Summary
        Quick Revision
        MCQs
    """

    summary_pdf = validate_pdf(
        summary_pdf
    )

    quick_revision_pdf = validate_pdf(
        quick_revision_pdf
    )

    mcq_pdf = validate_pdf(
        mcq_pdf
    )

    output_path = Path(
        output_path
    )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    writer = PdfWriter()

    input_files = [
        summary_pdf,
        quick_revision_pdf,
        mcq_pdf,
    ]

    for pdf_path in input_files:

        reader = PdfReader(
            str(pdf_path)
        )

        for page in reader.pages:
            writer.add_page(
                page
            )

    # Metadata
    writer.add_metadata(
        {
            "/Title": "PIB Study Material",
            "/Author": "PIB Study Generator",
            "/Creator": "PIB Study Generator",
            "/Producer": "PIB Study Generator",
        }
    )

    with output_path.open(
        "wb"
    ) as output_file:

        writer.write(
            output_file
        )

    if open_after:
        open_pdf(
            output_path
        )

    return str(
        output_path
    )


# ============================================================
# COMPATIBILITY ALIASES
# ============================================================

generate_combined = (
    generate_combined_pdf
)

merge_pdfs = (
    generate_combined_pdf
)


# ============================================================
# COMMAND LINE
# ============================================================

if __name__ == "__main__":

    if len(sys.argv) < 5:

        print(
            "Usage:"
        )

        print(
            "python tools/generate_combined.py "
            "SUMMARY.pdf QUICK_REVISION.pdf "
            "MCQS.pdf OUTPUT.pdf"
        )

        raise SystemExit(1)

    summary_path = Path(
        sys.argv[1]
    )

    quick_revision_path = Path(
        sys.argv[2]
    )

    mcq_path = Path(
        sys.argv[3]
    )

    output_path = Path(
        sys.argv[4]
    )

    result = generate_combined_pdf(
        summary_pdf=summary_path,
        quick_revision_pdf=quick_revision_path,
        mcq_pdf=mcq_path,
        output_path=output_path,
        open_after=False,
    )

    print(
        f"Generated: {result}"
    )