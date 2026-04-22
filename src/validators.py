"""Data validation module for PaySlip WhatsApp Tool."""

import re
from typing import Tuple, List, Dict, Optional
from src.logger import setup_logger

logger = setup_logger(__name__)


def validate_phone_number(phone: Optional[str]) -> Tuple[bool, str]:
    """
    Validate Indian phone number (10 digits).
    
    Args:
        phone: Phone number to validate
        
    Returns:
        Tuple of (valid: bool, message: str)
    """
    try:
        if not phone or phone is None:
            return False, "Phone number is empty"
        
        # Convert to string and remove spaces/dashes
        phone_str = str(phone).strip().replace(" ", "").replace("-", "")
        
        # Check if exactly 10 digits
        if not re.match(r'^\d{10}$', phone_str):
            return False, f"Invalid format: {phone_str} (expected 10 digits)"
        
        # Check if starts with valid digit (6-9 for Indian mobile numbers)
        first_digit = int(phone_str[0])
        if first_digit < 6:
            return False, f"Invalid first digit: {first_digit} (should be 6-9 for mobile)"
        
        return True, f"Valid phone number: {phone_str}"
    
    except Exception as e:
        return False, f"Error validating phone: {str(e)}"


def validate_salary_calculation(gross: float, deductions: float, net: float, tolerance: float = 0.01) -> Tuple[bool, str]:
    """
    Validate salary calculation: Net = Gross - Deductions.
    
    Args:
        gross: Gross wage amount
        deductions: Total deductions
        net: Net take-home pay
        tolerance: Acceptable difference (default: 0.01)
        
    Returns:
        Tuple of (valid: bool, message: str)
    """
    try:
        gross = float(gross) if gross else 0
        deductions = float(deductions) if deductions else 0
        net = float(net) if net else 0
        
        calculated_net = gross - deductions
        difference = abs(calculated_net - net)
        
        if difference > tolerance:
            return False, f"Salary mismatch: Calculated={calculated_net}, Actual={net}, Difference={difference}"
        
        return True, f"Salary calculation valid: {gross} - {deductions} = {net}"
    
    except Exception as e:
        return False, f"Error validating salary: {str(e)}"


def validate_deductions(epf_employee: float, esi_employee: float, gross: float) -> Tuple[bool, str]:
    """
    Validate deduction percentages (EPF 13%, ESI 3.25%).
    
    Args:
        epf_employee: EPF employee contribution
        esi_employee: ESI employee contribution
        gross: Gross wage
        
    Returns:
        Tuple of (valid: bool, message: str)
    """
    try:
        epf_employee = float(epf_employee) if epf_employee else 0
        esi_employee = float(esi_employee) if esi_employee else 0
        gross = float(gross) if gross else 0
        
        errors = []
        
        # Check EPF (should be approximately 13% of gross)
        if gross > 0 and epf_employee > 0:
            epf_percent = (epf_employee / gross) * 100
            if not (12 <= epf_percent <= 14):  # Allow 1% tolerance
                errors.append(f"EPF {epf_percent:.2f}% (expected ~13%)")
        
        # Check ESI (should be approximately 3.25% of gross)
        if gross > 0 and esi_employee > 0:
            esi_percent = (esi_employee / gross) * 100
            if not (2.5 <= esi_percent <= 4):  # Allow 0.75% tolerance
                errors.append(f"ESI {esi_percent:.2f}% (expected ~3.25%)")
        
        if errors:
            return False, f"Deduction percentage error: {', '.join(errors)}"
        
        return True, f"Deductions valid: EPF={epf_employee}, ESI={esi_employee}"
    
    except Exception as e:
        return False, f"Error validating deductions: {str(e)}"


def validate_employee_status(status: Optional[str]) -> Tuple[bool, str]:
    """
    Validate employee status (Active, Left, etc.).
    
    Args:
        status: Employee status string
        
    Returns:
        Tuple of (valid: bool, message: str)
    """
    try:
        if not status:
            return False, "Status is empty"
        
        status_str = str(status).strip().lower()
        
        valid_statuses = ["active", "left", "suspended", "resigned", "retired", "terminated"]
        
        if status_str not in valid_statuses:
            return False, f"Invalid status: {status} (valid: {', '.join(valid_statuses)})"
        
        return True, f"Valid status: {status}"
    
    except Exception as e:
        return False, f"Error validating status: {str(e)}"


def validate_employee_data(employee: Dict) -> Tuple[bool, List[str]]:
    """
    Validate complete employee record.
    
    Args:
        employee: Employee dictionary with all fields
        
    Returns:
        Tuple of (valid: bool, errors: List[str])
    """
    errors = []
    
    # Validate required fields
    if not employee.get("emp_id"):
        errors.append("Employee ID is missing")
    
    if not employee.get("name"):
        errors.append("Employee name is missing")
    
    # Validate phone number if provided
    if employee.get("whatsapp_contact"):
        valid, msg = validate_phone_number(employee["whatsapp_contact"])
        if not valid:
            errors.append(f"WhatsApp: {msg}")
    
    # Validate status if provided
    if employee.get("status"):
        valid, msg = validate_employee_status(employee["status"])
        if not valid:
            errors.append(f"Status: {msg}")
    
    # Validate salary calculation if all components provided
    if (employee.get("gross_wage") and employee.get("total_deductions") and 
        employee.get("net_take_home_pay")):
        valid, msg = validate_salary_calculation(
            employee["gross_wage"],
            employee["total_deductions"],
            employee["net_take_home_pay"]
        )
        if not valid:
            errors.append(f"Salary: {msg}")
    
    # Validate deductions if provided
    if (employee.get("epf_13") and employee.get("esi_3_25") and 
        employee.get("gross_wage")):
        valid, msg = validate_deductions(
            employee["epf_13"],
            employee["esi_3_25"],
            employee["gross_wage"]
        )
        if not valid:
            errors.append(f"Deductions: {msg}")
    
    return len(errors) == 0, errors


def generate_validation_report(employees: List[Dict]) -> Dict:
    """
    Generate validation report for batch of employees.
    
    Args:
        employees: List of employee dictionaries
        
    Returns:
        Dictionary with validation report
    """
    total = len(employees)
    valid_count = 0
    invalid_count = 0
    validation_issues = []
    
    for idx, emp in enumerate(employees, 1):
        valid, errors = validate_employee_data(emp)
        
        if valid:
            valid_count += 1
        else:
            invalid_count += 1
            emp_id = emp.get("emp_id", f"Row {idx}")
            emp_name = emp.get("name", "Unknown")
            
            validation_issues.append({
                "emp_id": emp_id,
                "name": emp_name,
                "errors": errors,
                "row": idx
            })
    
    report = {
        "total_employees": total,
        "valid_employees": valid_count,
        "invalid_employees": invalid_count,
        "validation_rate": f"{(valid_count/total*100):.1f}%" if total > 0 else "0%",
        "issues": validation_issues
    }
    
    logger.info(f"Validation report: {valid_count}/{total} employees valid")
    
    return report


def check_for_salary_holds(remarks: Optional[str]) -> Tuple[bool, str]:
    """
    Check if employee has salary hold indicated in remarks.
    
    Args:
        remarks: Remarks/Notes field
        
    Returns:
        Tuple of (has_hold: bool, message: str)
    """
    try:
        if not remarks:
            return False, "No remarks"
        
        remarks_str = str(remarks).lower()
        
        hold_keywords = ["hold", "suspend", "deduction", "advance", "loan", "penalty", "dues"]
        
        for keyword in hold_keywords:
            if keyword in remarks_str:
                return True, f"Possible hold detected: '{remarks}'"
        
        return False, "No hold detected"
    
    except Exception as e:
        return False, f"Error checking holds: {str(e)}"
