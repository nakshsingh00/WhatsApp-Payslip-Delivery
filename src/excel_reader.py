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
        "emp_id": ["Employee ID", "Emp ID", "EMP_ID", "Employee Code"],
        "name": ["Employee Name", "Name", "Emp Name"],
        "designation": ["Designation", "Designation/Grade", "Job Title"],
        "department": ["Department", "Dept", "Deptt"],
        "location": ["Location", "City", "Office Location"],
        "gender": ["Gender", "Sex"],
        "status": ["Status", "Employee Status", "Emp Status"],
        "date_of_joining": ["DOJ", "Date of Joining", "Joining Date"],
        "date_of_leaving": ["DOL", "Date of Leaving", "Left Date"],
        "whatsapp_contact": ["WhatsApp", "WhatsApp Contact", "Mobile", "Phone"],
        "minimum_wages": ["Minimum Wages", "Min Wages", "MW"],
        "house_rent": ["House Rent", "HRA", "House Rent Allowance"],
        "special_allowance": ["Special Allowance", "SA", "Spec Allowance"],
        "extra_duty_allowance": ["Extra Duty Allowance", "EDA", "Extra Duty"],
        "travelling_allowance": ["Travelling Allowance", "TA", "Travel Allowance"],
        "bonus": ["Bonus", "Performance Bonus"],
        "leave_with_wages": ["Leave with Wages", "LWW", "Leave Wages"],
        "labour_welfare_fund": ["Labour Welfare Fund", "LWF", "Welfare Fund"],
        "cost_of_uniform": ["Cost of Uniform", "Uniform", "Uniform Cost"],
        "gross_wage": ["Gross Wage", "Gross", "Gross Amount"],
        "ctc": ["CTC", "Cost to Company"],
        "epf_13": ["EPF 13%", "EPF_13", "EPF Employee"],
        "esi_3_25": ["ESI 3.25%", "ESI_3.25", "ESI Employee"],
        "epf_12": ["EPF 12%", "EPF_12", "EPF Employer"],
        "esi_0_75": ["ESI 0.75%", "ESI_0.75", "ESI Employer"],
        "professional_tax": ["Professional Tax", "PT", "Prof Tax"],
        "total_deductions": ["Total Deductions", "Total Ded", "Deductions"],
        "net_take_home_pay": ["Net Take Home Pay", "Net Pay", "Net Amount"],
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
    # First try exact match (case-sensitive)
    for col in df_columns:
        if col in possible_names:
            return True, col
    
    # Then try case-insensitive match
    df_cols_lower = {col.lower(): col for col in df_columns}
    for name in possible_names:
        if name.lower() in df_cols_lower:
            return True, df_cols_lower[name.lower()]
    
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
        
        # Read Excel file
        df = pd.read_excel(file_path)
        logger.info(f"Excel file read successfully: {len(df)} rows")
        
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
