"""
PIB Study Generator
Combined PDF Generator

Combines:

    1. Summary PDF
    2. Quick Revision PDF
    3. MCQ PDF

into one Complete PDF.

The visual appearance of the individual documents is controlled
by:

    tools/style_config.py
"""

from __future__ import annotations

import os
import shutil
import subprocess
import webbrowser
from pathlib import Path


try:
    from . import style_config as style
except ImportError:
    import style_config as style


# ============================================================
# PDF HELPERS
# ============================================================

def open_pdf(file_path) -> None:
    """
    Open a PDF using the operating system's default PDF viewer.
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


def check_pdf(path) -> bool:
    """
    Check whether a PDF exists and is not empty.
    """

    path = Path(path)

    return (
        path.exists()
        and path.is_file()
        and path.stat().st_size > 0
    )


# ============================================================
# MERGE USING PYPDF
# ============================================================

def merge_with_pypdf(
    pdf_files: list[Path],
    output_path: Path,
) -> bool:
    """
    Merge PDFs using pypdf.

    The PDFs are merged in exactly the order supplied
    in pdf_files.
    """

    try:
        from pypdf import PdfReader, PdfWriter
    except ImportError:
        return False

    try:

        writer = PdfWriter()

        for pdf_file in pdf_files:

            reader = PdfReader(
                str(pdf_file)
            )

            for page in reader.pages:
                writer.add_page(page)

        with open(
            output_path,
            "wb",
        ) as output_file:

            writer.write(
                output_file
            )

        return check_pdf(output_path)

    except Exception as error:

        print()
        print(
            "pypdf merge failed:"
        )

        print(error)

        return False


# ============================================================
# MERGE USING GHOSTSCRIPT
# ============================================================

def find_ghostscript() -> str | None:
    """
    Find Ghostscript if it is installed.

    This is only a fallback.
    """

    possible_commands = [
        "gswin64c",
        "gswin32c",
        "gs",
    ]

    for command in possible_commands:

        executable = shutil.which(
            command
        )

        if executable:
            return executable

    return None


def merge_with_ghostscript(
    pdf_files: list[Path],
    output_path: Path,
) -> bool:
    """
    Merge PDFs using Ghostscript.
    """

    ghostscript = find_ghostscript()

    if not ghostscript:
        return False

    command = [
        ghostscript,
        "-dBATCH",
        "-dNOPAUSE",
        "-sDEVICE=pdfwrite",
        f"-sOutputFile={output_path}",
    ]

    command.extend(
        str(pdf)
        for pdf in pdf_files
    )

    try:

        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:

            print()
            print(
                "Ghostscript merge failed:"
            )

            print(result.stderr)

            return False

        return check_pdf(output_path)

    except Exception as error:

        print()
        print(
            "Could not execute Ghostscript:"
        )

        print(error)

        return False


# ============================================================
# MAIN MERGE FUNCTION
# ============================================================

def generate_combined_pdf(
    summary_pdf,
    quick_revision_pdf,
    mcq_pdf,
    output_path=None,
    open_after=True,
):
    """
    Combine Summary + Quick Revision + MCQs.

    Order:

        1. Summary
        2. Quick Revision
        3. MCQs

    Parameters
    ----------
    summary_pdf:
        Path to Summary PDF.

    quick_revision_pdf:
        Path to Quick Revision PDF.

    mcq_pdf:
        Path to MCQ PDF.

    output_path:
        Optional output PDF path.

    open_after:
        Automatically open the finished PDF.

    Returns
    -------
    Path
        Complete PDF path.
    """

    summary_pdf = Path(summary_pdf)
    quick_revision_pdf = Path(quick_revision_pdf)
    mcq_pdf = Path(mcq_pdf)

    # --------------------------------------------------------
    # Validate all three PDFs
    # --------------------------------------------------------

    if not check_pdf(summary_pdf):

        raise FileNotFoundError(
            "Summary PDF not found or empty:\n"
            f"{summary_pdf}"
        )

    if not check_pdf(quick_revision_pdf):

        raise FileNotFoundError(
            "Quick Revision PDF not found or empty:\n"
            f"{quick_revision_pdf}"
        )

    if not check_pdf(mcq_pdf):

        raise FileNotFoundError(
            "MCQ PDF not found or empty:\n"
            f"{mcq_pdf}"
        )

    # --------------------------------------------------------
    # Default output
    # --------------------------------------------------------

    if output_path is None:

        output_path = (
            summary_pdf.parent
            / f"{summary_pdf.stem}_complete.pdf"
        )

    output_path = Path(output_path)

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    # --------------------------------------------------------
    # Exact document order
    # --------------------------------------------------------

    pdf_files = [
        summary_pdf,
        quick_revision_pdf,
        mcq_pdf,
    ]

    print()
    print(
        "Combining PDFs..."
    )

    print(
        f"1. Summary:        {summary_pdf}"
    )

    print(
        f"2. Quick Revision: {quick_revision_pdf}"
    )

    print(
        f"3. MCQs:           {mcq_pdf}"
    )

    print(
        f"Output:            {output_path}"
    )

    # --------------------------------------------------------
    # Method 1: pypdf
    # --------------------------------------------------------

    if merge_with_pypdf(
        pdf_files,
        output_path,
    ):

        print()
        print(
            "Complete PDF created successfully."
        )

        print(
            output_path.resolve()
        )

        if open_after:
            open_pdf(output_path)

        return output_path

    # --------------------------------------------------------
    # Method 2: Ghostscript
    # --------------------------------------------------------

    if merge_with_ghostscript(
        pdf_files,
        output_path,
    ):

        print()
        print(
            "Complete PDF created successfully "
            "using Ghostscript."
        )

        print(
            output_path.resolve()
        )

        if open_after:
            open_pdf(output_path)

        return output_path

    # --------------------------------------------------------
    # No merge engine available
    # --------------------------------------------------------

    raise RuntimeError(
        "\n"
        "Unable to combine the PDFs.\n\n"
        "Install pypdf with:\n"
        "    python -m pip install pypdf\n\n"
        "Then run the generator again.\n"
    )


# ============================================================
# COMPATIBILITY ALIASES
# ============================================================

generate_combined = generate_combined_pdf
combine_pdfs = generate_combined_pdf


# ============================================================
# COMMAND-LINE INTERFACE
# ============================================================

def main():
    """
    Command-line usage:

        python tools/generate_combined.py \
            summary.pdf \
            quick_revision.pdf \
            mcqs.pdf

    Or:

        python tools/generate_combined.py \
            summary.pdf \
            quick_revision.pdf \
            mcqs.pdf \
            complete.pdf
    """

    import argparse

    parser = argparse.ArgumentParser(
        description=(
            "Combine Summary, Quick Revision and MCQ PDFs "
            "into one Complete PDF."
        )
    )

    parser.add_argument(
        "summary_pdf",
        help="Path to the Summary PDF.",
    )

    parser.add_argument(
        "quick_revision_pdf",
        help="Path to the Quick Revision PDF.",
    )

    parser.add_argument(
        "mcq_pdf",
        help="Path to the MCQ PDF.",
    )

    parser.add_argument(
        "output",
        nargs="?",
        default=None,
        help="Optional Complete PDF output path.",
    )

    parser.add_argument(
        "--no-open",
        action="store_true",
        help="Do not automatically open the PDF.",
    )

    args = parser.parse_args()

    generate_combined_pdf(
        summary_pdf=args.summary_pdf,
        quick_revision_pdf=args.quick_revision_pdf,
        mcq_pdf=args.mcq_pdf,
        output_path=args.output,
        open_after=not args.no_open,
    )


if __name__ == "__main__":
    main()
