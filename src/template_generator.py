"""Template generator module for PaySlip WhatsApp Tool.

Uses Jinja2 to combine cleaned employee data with the HTML payslip template.
This produces a rendered HTML string for each employee, which is then
converted to PDF in the next step (Issue #9).

Pipeline position: Excel → Validate → Clean → **Template** → PDF → WhatsApp
"""

from datetime import datetime
from pathlib import Path
from typing import Dict, Optional
from jinja2 import Environment, FileSystemLoader
from src.logger import setup_logger

logger = setup_logger(__name__)

# Default template directory (relative to project root)
TEMPLATE_DIR = Path(__file__).parent.parent / "templates"


class EmployeeData:
    """
    Wrapper that lets us use dot notation in Jinja2 templates.

    Instead of {{ employee['name'] }} we can write {{ employee.name }}.
    This makes the HTML template much cleaner and easier to read.

    Jinja2 templates access variables using dots (like employee.name),
    but Python dictionaries use brackets (like employee['name']).
    This class bridges that gap.
    """

    def __init__(self, data: Dict):
        """
        Create an EmployeeData wrapper from a dictionary.

        Args:
            data: Cleaned employee dictionary from cleaners.py
        """
        self._data = data

    def __getattr__(self, name: str):
        """
        Called when someone accesses employee.something in the template.

        If the key exists in the dictionary, return its value.
        If not, return an empty string (so the template doesn't crash).
        """
        if name.startswith('_'):
            raise AttributeError(name)
        return self._data.get(name, "")


def get_template_env(template_dir: Optional[Path] = None) -> Environment:
    """
    Create a Jinja2 Environment that knows where to find our templates.

    Think of this as telling Jinja2: "the HTML files are in this folder."

    Args:
        template_dir: Path to templates folder (defaults to project's templates/)

    Returns:
        Configured Jinja2 Environment
    """
    if template_dir is None:
        template_dir = TEMPLATE_DIR

    env = Environment(
        loader=FileSystemLoader(str(template_dir)),
        autoescape=True  # Prevents HTML injection (security best practice)
    )

    logger.debug(f"Jinja2 environment created, templates dir: {template_dir}")
    return env


def render_payslip(
    employee: Dict,
    pay_period: str = "",
    pay_month: str = "",
    company_name: str = "HOLISTIC ALLIED SERVICES",
    company_address: str = "Facility Management & Security",
    template_dir: Optional[Path] = None
) -> str:
    """
    Render a single payslip HTML from employee data.

    This is the main function you'll use. It takes one cleaned employee
    dictionary, plugs the values into the HTML template, and returns
    a complete HTML string ready for PDF conversion.

    Args:
        employee: Cleaned employee dictionary (output of clean_employee_data)
        pay_period: Display text like "MARCH, 2026" (shown in title bar)
        pay_month: Short month like "Mar-26" (shown in employee info)
        company_name: Company name for header
        company_address: Company address/tagline for header
        template_dir: Optional custom template directory

    Returns:
        Rendered HTML string

    Example:
        >>> html = render_payslip(cleaned_employee, pay_period="MARCH, 2026", pay_month="Mar-26")
        >>> # html is now a complete HTML document ready for WeasyPrint
    """
    env = get_template_env(template_dir)
    template = env.get_template("payslip_template.html")

    # Wrap the dict so Jinja2 can use dot notation (employee.name)
    emp_obj = EmployeeData(employee)

    # Company info as a simple object too
    company = EmployeeData({
        "name": company_name,
        "address": company_address
    })

    # Render the template with all our variables
    html = template.render(
        employee=emp_obj,
        company=company,
        pay_period=pay_period,
        pay_month=pay_month,
        generated_date=datetime.now().strftime("%d/%m/%Y %H:%M IST")
    )

    emp_name = employee.get("name", "Unknown")
    emp_id = employee.get("emp_id", "N/A")
    logger.info(f"Rendered payslip HTML for: {emp_name} ({emp_id})")

    return html


def render_payslip_to_file(
    employee: Dict,
    output_path: str,
    pay_period: str = "",
    pay_month: str = "",
    company_name: str = "HOLISTIC ALLIED SERVICES",
    company_address: str = "Facility Management & Security",
    template_dir: Optional[Path] = None
) -> str:
    """
    Render a payslip and save it as an HTML file.

    Useful for previewing the payslip in a browser before generating PDFs.
    Also useful for debugging template issues.

    Args:
        employee: Cleaned employee dictionary
        output_path: Where to save the HTML file
        pay_period: Display text like "MARCH, 2026"
        pay_month: Short month like "Mar-26"
        company_name: Company name for header
        company_address: Company address/tagline
        template_dir: Optional custom template directory

    Returns:
        The output file path (same as input, for convenience)
    """
    html = render_payslip(
        employee=employee,
        pay_period=pay_period,
        pay_month=pay_month,
        company_name=company_name,
        company_address=company_address,
        template_dir=template_dir
    )

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(html, encoding="utf-8")

    logger.info(f"Payslip HTML saved to: {output_path}")
    return str(output)
