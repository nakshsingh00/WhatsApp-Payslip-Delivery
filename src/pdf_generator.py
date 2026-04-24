"""PDF generation module for PaySlip WhatsApp Tool.

Converts rendered HTML payslips into PDF files using WeasyPrint.
Handles single payslip generation, batch processing with progress tracking,
PDF quality verification, and auto-archival of old files.

Pipeline position: Excel → Validate → Clean → Template → **PDF** → WhatsApp

Note: WeasyPrint requires system libraries (Pango, GLib).
On macOS: brew install pango
The DYLD_LIBRARY_PATH may need to include /opt/homebrew/lib
"""

import os
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple
from src.template_generator import render_payslip
from src.logger import setup_logger

logger = setup_logger(__name__)

# Default output directories
OUTPUT_DIR = Path("data/generated_payslips")
ARCHIVE_DIR = Path("data/archived_payslips")

# Template directory (for WeasyPrint base_url so CSS loads correctly)
TEMPLATE_DIR = Path(__file__).parent.parent / "templates"


def generate_pdf(
    employee: Dict,
    output_dir: Optional[str] = None,
    pay_period: str = "",
    pay_month: str = "",
    filename: Optional[str] = None
) -> Tuple[bool, str]:
    """
    Generate a single payslip PDF for one employee.

    Takes a cleaned employee dictionary, renders it into HTML using the
    Jinja2 template, then converts that HTML to a PDF using WeasyPrint.

    How it works (simplified):
        1. render_payslip() fills the HTML template with employee data
        2. WeasyPrint reads that HTML like a browser would
        3. WeasyPrint "prints" it to a PDF file instead of a screen

    Args:
        employee: Cleaned employee dictionary (from cleaners.py)
        output_dir: Folder to save PDFs (default: data/generated_payslips/)
        pay_period: Display text like "MARCH, 2026"
        pay_month: Short month like "Mar-26"
        filename: Custom filename (default: auto-generated from employee data)

    Returns:
        Tuple of (success: bool, file_path_or_error: str)

    Example:
        >>> success, path = generate_pdf(employee, pay_period="MARCH, 2026")
        >>> if success:
        ...     print(f"PDF saved to: {path}")
    """
    # Import WeasyPrint here (not at top) so the rest of the module
    # still works even if WeasyPrint isn't installed yet
    try:
        import weasyprint
    except ImportError:
        return False, "WeasyPrint not installed. Run: pip3 install weasyprint"
    except OSError as e:
        return False, f"WeasyPrint system libraries missing: {e}"

    try:
        # Step 1: Set up output directory, sorted by location
        out_dir = Path(output_dir) if output_dir else OUTPUT_DIR
        location = str(employee.get("location", "")).strip()
        if location:
            out_dir = out_dir / location
        out_dir.mkdir(parents=True, exist_ok=True)

        # Step 2: Generate filename if not provided
        if not filename:
            emp_id = str(employee.get("emp_id", "UNKNOWN")).replace("/", "_")
            emp_name = str(employee.get("name", "Unknown")).replace(" ", "_")
            month_tag = pay_month.replace("-", "_") if pay_month else "payslip"
            filename = f"{emp_id}_{emp_name}_{month_tag}.pdf"

        output_path = out_dir / filename

        # Step 3: Render HTML from template
        html = render_payslip(
            employee=employee,
            pay_period=pay_period,
            pay_month=pay_month
        )

        # Step 4: Convert HTML to PDF
        # base_url tells WeasyPrint where to find the CSS file
        pdf_doc = weasyprint.HTML(
            string=html,
            base_url=str(TEMPLATE_DIR)
        )
        pdf_doc.write_pdf(str(output_path))

        file_size = output_path.stat().st_size
        emp_name = employee.get("name", "Unknown")
        logger.info(f"PDF generated: {emp_name} → {output_path} ({file_size} bytes)")

        return True, str(output_path)

    except Exception as e:
        emp_name = employee.get("name", "Unknown")
        logger.error(f"PDF generation failed for {emp_name}: {e}")
        return False, f"Error generating PDF for {emp_name}: {str(e)}"


def batch_generate_pdfs(
    employees: List[Dict],
    output_dir: Optional[str] = None,
    pay_period: str = "",
    pay_month: str = "",
    on_progress: Optional[Callable[[int, int, str], None]] = None
) -> Dict:
    """
    Generate PDFs for a list of employees with progress tracking.

    Processes employees one by one. If one fails, it logs the error
    and continues with the next — it does NOT stop the entire batch.

    The on_progress callback is called after each employee, which is
    how the GUI progress bar will know how far along we are.

    Args:
        employees: List of cleaned employee dictionaries
        output_dir: Folder to save PDFs
        pay_period: Display text like "MARCH, 2026"
        pay_month: Short month like "Mar-26"
        on_progress: Optional callback(current, total, employee_name)
                     Called after each employee is processed

    Returns:
        Dictionary with batch results:
        {
            "total": 125,
            "success": 120,
            "failed": 5,
            "generated_files": ["path1.pdf", "path2.pdf", ...],
            "errors": [{"name": "Raj Kumar", "error": "..."}]
        }

    Example:
        >>> def show_progress(current, total, name):
        ...     print(f"Processing {current}/{total}: {name}")
        >>> results = batch_generate_pdfs(employees, on_progress=show_progress)
    """
    total = len(employees)
    logger.info(f"Starting batch PDF generation: {total} employees")

    results = {
        "total": total,
        "success": 0,
        "failed": 0,
        "generated_files": [],
        "errors": []
    }

    for idx, emp in enumerate(employees, 1):
        emp_name = emp.get("name", f"Employee {idx}")

        success, result = generate_pdf(
            employee=emp,
            output_dir=output_dir,
            pay_period=pay_period,
            pay_month=pay_month
        )

        if success:
            results["success"] += 1
            results["generated_files"].append(result)
        else:
            results["failed"] += 1
            results["errors"].append({"name": emp_name, "error": result})
            logger.warning(f"Skipping {emp_name}: {result}")

        # Notify progress callback (for GUI progress bar)
        if on_progress:
            on_progress(idx, total, emp_name)

        # Log progress every 25 employees
        if idx % 25 == 0:
            logger.info(f"Batch progress: {idx}/{total} processed")

    logger.info(
        f"Batch complete: {results['success']}/{total} succeeded, "
        f"{results['failed']} failed"
    )

    return results


def verify_pdf(file_path: str) -> Tuple[bool, str]:
    """
    Verify that a generated PDF file is valid and not corrupted.

    Checks three things:
        1. The file exists on disk
        2. The file is not empty (size > 0)
        3. The file starts with '%PDF' (the PDF magic bytes)

    This catches common issues like:
        - Disk was full during generation (empty file)
        - WeasyPrint crashed mid-write (truncated file)
        - Wrong file path (file doesn't exist)

    Args:
        file_path: Path to the PDF file to verify

    Returns:
        Tuple of (valid: bool, message: str)
    """
    path = Path(file_path)

    # Check 1: File exists
    if not path.exists():
        return False, f"File not found: {file_path}"

    # Check 2: File is not empty
    file_size = path.stat().st_size
    if file_size == 0:
        return False, f"File is empty (0 bytes): {file_path}"

    # Check 3: Starts with PDF magic bytes (%PDF)
    try:
        with open(path, 'rb') as f:
            header = f.read(5)
        if not header.startswith(b'%PDF'):
            return False, f"Not a valid PDF (bad header): {file_path}"
    except Exception as e:
        return False, f"Could not read file: {e}"

    logger.debug(f"PDF verified: {file_path} ({file_size} bytes)")
    return True, f"Valid PDF: {file_path} ({file_size} bytes)"


def verify_batch(file_paths: List[str]) -> Dict:
    """
    Verify a batch of PDF files.

    Args:
        file_paths: List of PDF file paths to verify

    Returns:
        Dictionary with verification results:
        {
            "total": 125,
            "valid": 123,
            "invalid": 2,
            "issues": [{"file": "path.pdf", "error": "..."}]
        }
    """
    total = len(file_paths)
    results = {
        "total": total,
        "valid": 0,
        "invalid": 0,
        "issues": []
    }

    for path in file_paths:
        valid, msg = verify_pdf(path)
        if valid:
            results["valid"] += 1
        else:
            results["invalid"] += 1
            results["issues"].append({"file": path, "error": msg})

    logger.info(f"Batch verification: {results['valid']}/{total} valid")
    return results


def archive_old_pdfs(
    source_dir: Optional[str] = None,
    archive_dir: Optional[str] = None,
    retention_days: int = 90
) -> Dict:
    """
    Move PDF files older than retention_days to the archive folder.

    This prevents the generated_payslips folder from growing forever.
    Old files aren't deleted — they're moved to archived_payslips/
    where they stay safe but out of the way.

    How file age is determined:
        Uses the file's last modified time. If a file was last modified
        more than retention_days ago, it gets archived.

    Args:
        source_dir: Folder to scan (default: data/generated_payslips/)
        archive_dir: Folder to move old files to (default: data/archived_payslips/)
        retention_days: How many days to keep files before archiving (default: 90)

    Returns:
        Dictionary with archival results:
        {
            "scanned": 150,
            "archived": 45,
            "kept": 105,
            "errors": []
        }
    """
    src = Path(source_dir) if source_dir else OUTPUT_DIR
    dst = Path(archive_dir) if archive_dir else ARCHIVE_DIR

    results = {
        "scanned": 0,
        "archived": 0,
        "kept": 0,
        "errors": []
    }

    # Make sure both directories exist
    if not src.exists():
        logger.info(f"Source directory does not exist: {src}")
        return results

    dst.mkdir(parents=True, exist_ok=True)

    cutoff_date = datetime.now() - timedelta(days=retention_days)

    for pdf_file in src.glob("*.pdf"):
        results["scanned"] += 1

        # Get file modification time
        mod_time = datetime.fromtimestamp(pdf_file.stat().st_mtime)

        if mod_time < cutoff_date:
            # File is older than retention period — archive it
            try:
                dest_path = dst / pdf_file.name
                shutil.move(str(pdf_file), str(dest_path))
                results["archived"] += 1
                logger.debug(f"Archived: {pdf_file.name}")
            except Exception as e:
                results["errors"].append({"file": pdf_file.name, "error": str(e)})
                logger.error(f"Failed to archive {pdf_file.name}: {e}")
        else:
            results["kept"] += 1

    logger.info(
        f"Archival complete: {results['archived']} archived, "
        f"{results['kept']} kept (retention: {retention_days} days)"
    )

    return results
