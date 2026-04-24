"""Excel reader module for PaySlip WhatsApp Tool."""

import pandas as pd
from pathlib import Path
from typing import Tuple, List, Dict, Optional
from src.logger import setup_logger

logger = setup_logger(__name__)


def get_column_mapping() -> Dict[str, List[str]]:
    """
    Get mapping of field names to possible Excel column names.
    
    Returns:
        Dictionary mapping field names to list of possible column names
    """
    return {
        "emp_id": ["Emp ID", "Employee ID", "EMP_ID", "Employee Code"],
        "name": ["Name", "Employee Name", "Emp Name"],
        "designation": ["Designation", "Designation/Grade", "Job Title"],
        "department": ["Department", "Dept", "Deptt", "Deparment"],
        "location": ["Location", "City", "Office Location"],
        "gender": ["Gender", "Sex"],
        "status": ["Status", "Employee Status", "Emp Status"],
        "date_of_joining": ["Date of Joining", "DOJ", "Joining Date"],
        "date_of_leaving": ["Date of Leaving", "DOL", "Left Date"],
        "whatsapp_contact": ["Whatsapp Nmbr", "WhatsApp", "WhatsApp Contact",
                             "Mobile", "Phone", "Whatsapp Number", "WhatsApp No"],
        "minimum_wages": ["Minimum Wages", "Min Wages", "MW"],
        "house_rent": ["House Rent Allowance", "House Rent", "HRA"],
        "special_allowance": ["Special Allowance", "SA", "Spec Allowance"],
        "extra_duty_allowance": ["Extra Duty Allowance", "EDA", "Extra Duty"],
        "travelling_allowance": ["Travelling Allowance", "Travelling Allownace",
                                 "TA", "Travel Allowance"],
        "bonus": ["Bonus @ 8.33% on Min. Wage", "Bonus", "Performance Bonus"],
        "leave_with_wages": ["Leave (with Wages) - 18 Days / Year",
                             "Leave with Wages", "LWW", "Leave Wages"],
        "labour_welfare_fund": ["Labour Welfare Fund", "LWF", "Welfare Fund"],
        "cost_of_uniform": ["Cost of uniform", "Cost of Uniform", "Uniform",
                            "Uniform Cost"],
        "gross_wage": ["Gross Wage", "Gross", "Gross Amount"],
        "ctc": ["CTC", "Cost to Company"],
        "epf_13": ["E.P.F @ 13% on Minimum Wages", "EPF 13%", "EPF_13",
                   "EPF Employee", "PF Employee"],
        "esi_3_25": ["E.S.I @ 3.25% on Gross Wage", "ESI 3.25%", "ESI_3.25",
                     "ESI Employee"],
        "epf_12": ["E.P.F @ 12% on Minimum Wages", "EPF 12%", "EPF_12",
                   "EPF Employer"],
        "esi_0_75": ["E.S.I @ 0.75% on Gross Wage", "ESI 0.75%", "ESI_0.75",
                     "ESI Employer"],
        "professional_tax": ["Professional Tax", "PT", "Prof Tax"],
        "total_deductions": ["Total Deductions", "Total Ded", "Deductions"],
        "net_take_home_pay": ["Net Take Home Pay", "Net Pay", "Net Amount",
                              "Net Take Home Pay "],
        "remarks": ["Remarks", "Notes", "Comments"]
    }


def find_column(df_columns: List[str], possible_names: List[str]) -> Tuple[bool, str]:
    """
    Find column name in DataFrame by matching against possible names.
    
    Args:
        df_columns: List of column names in DataFrame
        possible_names: List of possible column names to match
        
    Returns:
        Tuple of (found: bool, column_name: str)
    """
    import re as _re

    # First try exact match (case-sensitive)
    for col in df_columns:
        if col in possible_names:
            return True, col

    # Then try case-insensitive match
    df_cols_lower = {col.lower(): col for col in df_columns}
    for name in possible_names:
        if name.lower() in df_cols_lower:
            return True, df_cols_lower[name.lower()]

    # Then try normalized whitespace match (handles Excel wrapped headers)
    # "E.P.F @ 13%\non Minimum\nWages" matches "E.P.F @ 13% on Minimum Wages"
    def normalize(s):
        return _re.sub(r'\s+', ' ', str(s).strip().lower())

    df_cols_norm = {normalize(col): col for col in df_columns}
    for name in possible_names:
        if normalize(name) in df_cols_norm:
            return True, df_cols_norm[normalize(name)]

    # Finally try substring/contains match for long column names
    for name in possible_names:
        name_norm = normalize(name)
        if len(name_norm) >= 8:  # Only for reasonably long names
            for col_norm, col_orig in df_cols_norm.items():
                if name_norm in col_norm or col_norm in name_norm:
                    return True, col_orig

    return False, ""


def validate_columns(df: pd.DataFrame, required_fields: List[str] = None) -> Tuple[bool, str]:
    """
    Validate that required columns exist in DataFrame.
    
    Args:
        df: Pandas DataFrame
        required_fields: List of field names to validate (if None, validates critical fields)
        
    Returns:
        Tuple of (valid: bool, message: str)
    """
    if required_fields is None:
        required_fields = ["emp_id", "name", "gross_wage", "net_take_home_pay"]
    
    column_mapping = get_column_mapping()
    missing_fields = []
    
    for field in required_fields:
        if field not in column_mapping:
            missing_fields.append(f"Unknown field: {field}")
            continue
        
        found, _ = find_column(df.columns.tolist(), column_mapping[field])
        if not found:
            missing_fields.append(f"Column for '{field}' not found")
    
    if missing_fields:
        message = "Validation failed: " + "; ".join(missing_fields)
        return False, message
    
    return True, "All required columns found"


def read_excel(file_path: str) -> Tuple[bool, List[Dict], str]:
    """
    Read Excel file and return employee data as list of dictionaries.
    
    Args:
        file_path: Path to Excel file
        
    Returns:
        Tuple of (success: bool, employees: List[Dict], message: str)
    """
    try:
        file = Path(file_path)
        if not file.exists():
            return False, [], f"File not found: {file_path}"

        # Try reading with default header (row 0)
        df = pd.read_excel(file_path)

        # Auto-detect header row: if columns are mostly "Unnamed", the real
        # headers are on a later row. Scan the first 10 rows for known names.
        unnamed_count = sum(1 for c in df.columns if str(c).startswith("Unnamed"))
        if unnamed_count > len(df.columns) / 2:
            logger.info("Detected non-standard header row, scanning for real headers...")
            known_names = {"name", "emp id", "designation", "status", "gross wage",
                           "minimum wages", "net take home pay", "location"}
            raw = pd.read_excel(file_path, header=None, nrows=10)
            for row_idx in range(10):
                row_vals = [str(v).strip().lower() for v in raw.iloc[row_idx] if str(v) != "nan"]
                matches = sum(1 for v in row_vals if v in known_names)
                if matches >= 3:
                    logger.info(f"Found header row at index {row_idx}")
                    df = pd.read_excel(file_path, header=row_idx)
                    break

        # Strip whitespace from column names (handles "Net Take Home Pay " etc.)
        df.columns = [str(c).strip() for c in df.columns]

        logger.info(f"Excel file read successfully: {len(df)} rows, {len(df.columns)} columns")
        
        # Validate columns
        valid, message = validate_columns(df)
        if not valid:
            logger.warning(f"Column validation warning: {message}")
        
        # Map columns
        column_mapping = get_column_mapping()
        employees = []
        
        for idx, row in df.iterrows():
            employee = {}
            for field, possible_names in column_mapping.items():
                found, col_name = find_column(df.columns.tolist(), possible_names)
                if found:
                    value = row[col_name]
                    # Handle NaN values
                    if pd.isna(value):
                        employee[field] = None
                    else:
                        employee[field] = value
                else:
                    employee[field] = None
            
            employees.append(employee)
        
        logger.info(f"Successfully processed {len(employees)} employees")
        return True, employees, f"Successfully read {len(employees)} employees"
    
    except Exception as e:
        logger.error(f"Error reading Excel file: {str(e)}")
        return False, [], f"Error reading Excel file: {str(e)}"


def get_employee_summary(employees: List[Dict]) -> Dict:
    """
    Get summary statistics about employees.
    
    Args:
        employees: List of employee dictionaries
        
    Returns:
        Dictionary with summary statistics
    """
    total = len(employees)
    active = 0
    left = 0
    with_whatsapp = 0
    
    for emp in employees:
        status = emp.get("status", "").lower() if emp.get("status") else ""
        if status == "active":
            active += 1
        elif status == "left":
            left += 1
        
        whatsapp = emp.get("whatsapp_contact")
        if whatsapp and str(whatsapp).strip():
            with_whatsapp += 1
    
    return {
        "total_employees": total,
        "active_employees": active,
        "left_employees": left,
        "employees_with_whatsapp": with_whatsapp
    }


def get_excel_info(file_path: str) -> Tuple[bool, Dict, str]:
    """
    Get metadata about Excel file.
    
    Args:
        file_path: Path to Excel file
        
    Returns:
        Tuple of (success: bool, info: Dict, message: str)
    """
    try:
        file = Path(file_path)
        if not file.exists():
            return False, {}, f"File not found: {file_path}"
        
        df = pd.read_excel(file_path)
        
        info = {
            "file_name": file.name,
            "file_size_bytes": file.stat().st_size,
            "rows": len(df),
            "columns": len(df.columns),
            "column_names": df.columns.tolist()
        }
        
        return True, info, "File info retrieved successfully"
    
    except Exception as e:
        logger.error(f"Error getting Excel info: {str(e)}")
        return False, {}, f"Error getting Excel info: {str(e)}"


def preview_excel(file_path: str, num_rows: int = 5) -> Tuple[bool, List[Dict], str]:
    """
    Get preview of first N rows from Excel file.
    
    Args:
        file_path: Path to Excel file
        num_rows: Number of rows to preview (default: 5)
        
    Returns:
        Tuple of (success: bool, preview_data: List[Dict], message: str)
    """
    try:
        success, employees, message = read_excel(file_path)
        if not success:
            return False, [], message
        
        preview = employees[:num_rows]
        return True, preview, f"Preview of first {min(num_rows, len(employees))} rows"
    
    except Exception as e:
        logger.error(f"Error previewing Excel file: {str(e)}")
        return False, [], f"Error previewing Excel file: {str(e)}"
