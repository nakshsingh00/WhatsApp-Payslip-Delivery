"""Data cleaning module for PaySlip WhatsApp Tool.

This module sits between the Excel reader and the template/PDF generator.
It takes raw employee data from Excel and normalizes everything into
consistent formats so the rest of the pipeline gets clean inputs.

Pipeline position: Excel Reader → Validators → **Cleaners** → Template → PDF
"""

import re
from datetime import datetime
from typing import Dict, List, Optional, Union
from src.logger import setup_logger

logger = setup_logger(__name__)


# --- Currency fields that need numeric conversion ---
CURRENCY_FIELDS = [
    "minimum_wages", "house_rent", "special_allowance",
    "extra_duty_allowance", "travelling_allowance", "bonus",
    "leave_with_wages", "labour_welfare_fund", "cost_of_uniform",
    "gross_wage", "ctc", "epf_13", "esi_3_25", "epf_12", "esi_0_75",
    "professional_tax", "total_deductions", "net_take_home_pay"
]

# --- Date fields that need DD/MM/YYYY standardization ---
DATE_FIELDS = ["date_of_joining", "date_of_leaving"]

# --- Text fields where missing = empty string ---
TEXT_FIELDS = [
    "emp_id", "name", "designation", "department",
    "location", "gender", "remarks"
]


def normalize_phone(phone: Optional[Union[str, int, float]]) -> str:
    """
    Normalize a phone number to clean 10-digit Indian format.

    Handles common messy formats from Excel:
      - "91 9876543210" → "9876543210"
      - "+91-987-654-3210" → "9876543210"
      - 9876543210.0 (float from Excel) → "9876543210"
      - "  987 654 3210  " → "9876543210"

    Args:
        phone: Raw phone value from Excel (could be str, int, float, or None)

    Returns:
        Clean 10-digit string, or empty string if input is unusable
    """
    if phone is None or str(phone).strip() == "":
        logger.debug("Phone is empty, returning blank")
        return ""

    # Step 1: Convert to string (handles floats like 9876543210.0)
    phone_str = str(phone).strip()

    # Step 2: Remove the decimal part if it's a float (e.g., "9876543210.0")
    if "." in phone_str:
        phone_str = phone_str.split(".")[0]

    # Step 3: Remove all non-digit characters (spaces, dashes, plus, parens)
    digits_only = re.sub(r'\D', '', phone_str)

    # Step 4: If it starts with "91" and has 12 digits, strip the country code
    if len(digits_only) == 12 and digits_only.startswith("91"):
        digits_only = digits_only[2:]

    # Step 5: If it starts with "0" and has 11 digits, strip the leading zero
    if len(digits_only) == 11 and digits_only.startswith("0"):
        digits_only = digits_only[1:]

    # Step 6: Validate we have exactly 10 digits
    if len(digits_only) == 10:
        logger.debug(f"Phone normalized: {phone} → {digits_only}")
        return digits_only
    else:
        logger.warning(f"Could not normalize phone: {phone} → got {digits_only} ({len(digits_only)} digits)")
        return digits_only  # Return what we have — validator will catch it


def convert_currency(value: Optional[Union[str, int, float]]) -> float:
    """
    Convert a raw Excel salary/deduction value to a clean Python float.

    Handles common formats:
      - "₹15,000" → 15000.0
      - "1,50,000" (Indian format) → 150000.0
      - "15000.50" (string) → 15000.5
      - 15000 (int) → 15000.0
      - None → 0.0

    The Indian number system uses commas differently:
      - International: 1,500,000
      - Indian: 15,00,000
    Both should become 1500000.0

    Args:
        value: Raw currency value from Excel

    Returns:
        Clean float value, or 0.0 if input is unusable
    """
    if value is None:
        return 0.0

    # If it's already a number, just convert and return
    if isinstance(value, (int, float)):
        return float(value)

    # It's a string — clean it up
    text = str(value).strip()

    if text == "":
        return 0.0

    # Remove currency symbols, spaces, and commas
    # This handles: ₹, Rs, Rs., INR, and commas in any position
    text = re.sub(r'[₹,\s]', '', text)
    text = re.sub(r'^(Rs\.?|INR)\s*', '', text, flags=re.IGNORECASE)

    try:
        result = float(text)
        return result
    except ValueError:
        logger.warning(f"Could not convert currency value: {value}")
        return 0.0


def standardize_date(date_value: Optional[Union[str, datetime]]) -> str:
    """
    Standardize a date to DD/MM/YYYY string format.

    Handles:
      - datetime objects (from Excel) → "22/04/2026"
      - "2026-04-22" (ISO format) → "22/04/2026"
      - "22/04/2026" (already correct) → "22/04/2026"
      - "22-04-2026" → "22/04/2026"
      - None or blank → ""

    Args:
        date_value: Raw date from Excel (could be datetime, string, or None)

    Returns:
        Date string in DD/MM/YYYY format, or empty string if unusable
    """
    if date_value is None or str(date_value).strip() == "":
        return ""

    # If it's already a datetime object (pandas/Excel often gives us these)
    if isinstance(date_value, datetime):
        return date_value.strftime("%d/%m/%Y")

    text = str(date_value).strip()

    # Try common date formats, one by one
    formats_to_try = [
        "%d/%m/%Y",   # 22/04/2026 (already correct)
        "%d-%m-%Y",   # 22-04-2026
        "%Y-%m-%d",   # 2026-04-22 (ISO format)
        "%d/%m/%y",   # 22/04/26 (2-digit year)
        "%d-%m-%y",   # 22-04-26
        "%Y/%m/%d",   # 2026/04/22
        "%d-%b-%y",   # 1-Sep-25 (Excel short month name, 2-digit year)
        "%d-%b-%Y",   # 1-Sep-2025 (Excel short month name, 4-digit year)
        "%d %b %Y",   # 1 Sep 2025
        "%d %b %y",   # 1 Sep 25
        "%m/%d/%Y",   # 10/13/77 (US format seen in BLR data)
        "%m/%d/%y",   # 10/13/77
    ]

    for fmt in formats_to_try:
        try:
            parsed = datetime.strptime(text, fmt)
            return parsed.strftime("%d/%m/%Y")
        except ValueError:
            continue

    # None of the formats matched — return as-is and log a warning
    logger.warning(f"Could not parse date: {date_value}")
    return text


def handle_missing_values(employee: Dict) -> Dict:
    """
    Fill in missing/None values with appropriate defaults.

    Rules:
      - Text fields (name, designation, etc.) → empty string ""
      - Currency fields (salary, deductions, etc.) → 0.0
      - Status → "Active" (most employees are active)
      - Remarks → preserved exactly as-is (never auto-filled)

    This does NOT modify the original dictionary — it returns a new one.

    Args:
        employee: Raw employee dictionary from Excel reader

    Returns:
        New dictionary with missing values filled in
    """
    # Start with a copy so we don't modify the original
    cleaned = dict(employee)

    # Text fields: None → ""
    for field in TEXT_FIELDS:
        if cleaned.get(field) is None:
            cleaned[field] = ""

    # Currency fields: None → 0.0
    for field in CURRENCY_FIELDS:
        if cleaned.get(field) is None:
            cleaned[field] = 0.0

    # Status: None → "Active"
    if cleaned.get("status") is None or str(cleaned.get("status", "")).strip() == "":
        cleaned["status"] = "Active"

    # Phone: None → ""
    if cleaned.get("whatsapp_contact") is None:
        cleaned["whatsapp_contact"] = ""

    # Date fields: None → ""
    for field in DATE_FIELDS:
        if cleaned.get(field) is None:
            cleaned[field] = ""

    return cleaned


def clean_employee_data(employee: Dict) -> Dict:
    """
    Master cleaning function — runs all cleaners on one employee record.

    This is the function you'll call from the main pipeline. It:
      1. Fills in missing values with defaults
      2. Normalizes the phone number
      3. Converts all currency fields to floats
      4. Standardizes all date fields to DD/MM/YYYY

    Args:
        employee: Raw employee dictionary from Excel reader

    Returns:
        Fully cleaned employee dictionary ready for template rendering
    """
    # Step 1: Handle missing values first (so we have defaults to work with)
    cleaned = handle_missing_values(employee)

    # Step 2: Normalize phone number
    cleaned["whatsapp_contact"] = normalize_phone(cleaned.get("whatsapp_contact"))

    # Step 3: Convert all currency fields to clean floats
    for field in CURRENCY_FIELDS:
        cleaned[field] = convert_currency(cleaned.get(field))

    # Step 4: Standardize date fields
    for field in DATE_FIELDS:
        cleaned[field] = standardize_date(cleaned.get(field))

    emp_name = cleaned.get("name", "Unknown")
    emp_id = cleaned.get("emp_id", "N/A")
    logger.info(f"Cleaned employee data: {emp_name} ({emp_id})")

    return cleaned


def clean_all_employees(employees: List[Dict]) -> List[Dict]:
    """
    Clean an entire batch of employee records.

    Runs clean_employee_data() on each employee and returns the
    full cleaned list. Logs progress for large batches.

    Args:
        employees: List of raw employee dictionaries

    Returns:
        List of cleaned employee dictionaries
    """
    total = len(employees)
    logger.info(f"Starting batch cleaning: {total} employees")

    cleaned_list = []
    for idx, emp in enumerate(employees, 1):
        cleaned = clean_employee_data(emp)
        cleaned_list.append(cleaned)

        # Log progress every 50 employees (useful for large batches)
        if idx % 50 == 0:
            logger.info(f"Cleaned {idx}/{total} employees...")

    logger.info(f"Batch cleaning complete: {total} employees cleaned")
    return cleaned_list
