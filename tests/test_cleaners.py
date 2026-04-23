"""Unit tests for Data Cleaning module."""

import unittest
from datetime import datetime
from src.cleaners import (
    normalize_phone, convert_currency, standardize_date,
    handle_missing_values, clean_employee_data, clean_all_employees
)


class TestNormalizePhone(unittest.TestCase):
    """Test cases for phone number normalization."""

    def test_clean_10_digit_number(self):
        """Already clean numbers should pass through unchanged."""
        self.assertEqual(normalize_phone("9876543210"), "9876543210")
        self.assertEqual(normalize_phone("6000000000"), "6000000000")
        print("✅ TEST 1 PASSED: Clean 10-digit numbers pass through!")

    def test_strip_country_code(self):
        """Numbers with +91 or 91 prefix should have it removed."""
        self.assertEqual(normalize_phone("+919876543210"), "9876543210")
        self.assertEqual(normalize_phone("919876543210"), "9876543210")
        self.assertEqual(normalize_phone("+91-9876543210"), "9876543210")
        print("✅ TEST 2 PASSED: Country code stripped correctly!")

    def test_strip_spaces_and_dashes(self):
        """Spaces, dashes, and other separators should be removed."""
        self.assertEqual(normalize_phone("987 654 3210"), "9876543210")
        self.assertEqual(normalize_phone("987-654-3210"), "9876543210")
        self.assertEqual(normalize_phone("  9876543210  "), "9876543210")
        self.assertEqual(normalize_phone("(987) 654-3210"), "9876543210")
        print("✅ TEST 3 PASSED: Spaces and dashes stripped!")

    def test_float_from_excel(self):
        """Excel sometimes stores phone numbers as floats like 9876543210.0."""
        self.assertEqual(normalize_phone(9876543210.0), "9876543210")
        self.assertEqual(normalize_phone(9876543210), "9876543210")
        print("✅ TEST 4 PASSED: Float/int phone numbers handled!")

    def test_empty_and_none(self):
        """None and empty strings should return empty string."""
        self.assertEqual(normalize_phone(None), "")
        self.assertEqual(normalize_phone(""), "")
        self.assertEqual(normalize_phone("   "), "")
        print("✅ TEST 5 PASSED: Empty/None returns blank!")

    def test_leading_zero(self):
        """Numbers with leading 0 (like 09876543210) should strip it."""
        self.assertEqual(normalize_phone("09876543210"), "9876543210")
        print("✅ TEST 6 PASSED: Leading zero stripped!")


class TestConvertCurrency(unittest.TestCase):
    """Test cases for currency value conversion."""

    def test_already_numeric(self):
        """Numbers should pass through as floats."""
        self.assertEqual(convert_currency(15000), 15000.0)
        self.assertEqual(convert_currency(15000.50), 15000.50)
        self.assertEqual(convert_currency(0), 0.0)
        print("✅ TEST 7 PASSED: Numeric values convert to float!")

    def test_string_with_commas(self):
        """String numbers with commas should have commas removed."""
        self.assertEqual(convert_currency("15,000"), 15000.0)
        self.assertEqual(convert_currency("1,50,000"), 150000.0)
        self.assertEqual(convert_currency("1,500,000"), 1500000.0)
        print("✅ TEST 8 PASSED: Comma-separated strings converted!")

    def test_rupee_symbol(self):
        """₹ symbol and Rs prefix should be stripped."""
        self.assertEqual(convert_currency("₹15,000"), 15000.0)
        self.assertEqual(convert_currency("Rs 15000"), 15000.0)
        self.assertEqual(convert_currency("Rs. 15000"), 15000.0)
        self.assertEqual(convert_currency("INR 15000"), 15000.0)
        print("✅ TEST 9 PASSED: Currency symbols stripped!")

    def test_none_and_empty(self):
        """None and empty string should return 0.0."""
        self.assertEqual(convert_currency(None), 0.0)
        self.assertEqual(convert_currency(""), 0.0)
        self.assertEqual(convert_currency("   "), 0.0)
        print("✅ TEST 10 PASSED: None/empty returns 0.0!")

    def test_invalid_string(self):
        """Non-parseable strings should return 0.0 without crashing."""
        self.assertEqual(convert_currency("N/A"), 0.0)
        self.assertEqual(convert_currency("not a number"), 0.0)
        print("✅ TEST 11 PASSED: Invalid strings return 0.0 safely!")


class TestStandardizeDate(unittest.TestCase):
    """Test cases for date standardization."""

    def test_datetime_object(self):
        """Python datetime objects should convert to DD/MM/YYYY."""
        dt = datetime(2026, 4, 22)
        self.assertEqual(standardize_date(dt), "22/04/2026")
        print("✅ TEST 12 PASSED: datetime objects converted!")

    def test_already_correct_format(self):
        """DD/MM/YYYY strings should pass through unchanged."""
        self.assertEqual(standardize_date("22/04/2026"), "22/04/2026")
        self.assertEqual(standardize_date("01/01/2025"), "01/01/2025")
        print("✅ TEST 13 PASSED: Correct format passes through!")

    def test_iso_format(self):
        """ISO format YYYY-MM-DD should convert to DD/MM/YYYY."""
        self.assertEqual(standardize_date("2026-04-22"), "22/04/2026")
        self.assertEqual(standardize_date("2025-01-01"), "01/01/2025")
        print("✅ TEST 14 PASSED: ISO dates converted!")

    def test_dash_separated(self):
        """DD-MM-YYYY should convert to DD/MM/YYYY."""
        self.assertEqual(standardize_date("22-04-2026"), "22/04/2026")
        print("✅ TEST 15 PASSED: Dash-separated dates converted!")

    def test_none_and_empty(self):
        """None and empty should return empty string."""
        self.assertEqual(standardize_date(None), "")
        self.assertEqual(standardize_date(""), "")
        self.assertEqual(standardize_date("   "), "")
        print("✅ TEST 16 PASSED: Empty/None returns blank!")

    def test_unparseable_date(self):
        """Unparseable strings should be returned as-is (not crash)."""
        result = standardize_date("sometime in April")
        self.assertEqual(result, "sometime in April")
        print("✅ TEST 17 PASSED: Unparseable dates returned as-is!")


class TestHandleMissingValues(unittest.TestCase):
    """Test cases for missing value handling."""

    def test_fills_missing_text_fields(self):
        """None text fields should become empty strings."""
        emp = {"name": None, "designation": None, "emp_id": None}
        result = handle_missing_values(emp)
        self.assertEqual(result["name"], "")
        self.assertEqual(result["designation"], "")
        self.assertEqual(result["emp_id"], "")
        print("✅ TEST 18 PASSED: Missing text fields filled with ''!")

    def test_fills_missing_currency_fields(self):
        """None currency fields should become 0.0."""
        emp = {"minimum_wages": None, "gross_wage": None, "net_take_home_pay": None}
        result = handle_missing_values(emp)
        self.assertEqual(result["minimum_wages"], 0.0)
        self.assertEqual(result["gross_wage"], 0.0)
        self.assertEqual(result["net_take_home_pay"], 0.0)
        print("✅ TEST 19 PASSED: Missing currency fields filled with 0.0!")

    def test_default_status_is_active(self):
        """Missing status should default to 'Active'."""
        emp = {"status": None}
        result = handle_missing_values(emp)
        self.assertEqual(result["status"], "Active")

        emp2 = {"status": ""}
        result2 = handle_missing_values(emp2)
        self.assertEqual(result2["status"], "Active")
        print("✅ TEST 20 PASSED: Missing status defaults to Active!")

    def test_preserves_existing_values(self):
        """Existing non-None values should NOT be overwritten."""
        emp = {"name": "Raj Kumar", "status": "Left", "gross_wage": 25000}
        result = handle_missing_values(emp)
        self.assertEqual(result["name"], "Raj Kumar")
        self.assertEqual(result["status"], "Left")
        self.assertEqual(result["gross_wage"], 25000)
        print("✅ TEST 21 PASSED: Existing values preserved!")

    def test_does_not_modify_original(self):
        """The original dictionary should not be changed."""
        emp = {"name": None, "status": None}
        result = handle_missing_values(emp)
        self.assertIsNone(emp["name"])  # Original still None
        self.assertEqual(result["name"], "")  # New one is ""
        print("✅ TEST 22 PASSED: Original dict not modified!")


class TestCleanEmployeeData(unittest.TestCase):
    """Test cases for the master clean_employee_data function."""

    def test_full_clean(self):
        """A realistic messy employee record should come out clean."""
        messy_employee = {
            "emp_id": "EMP001",
            "name": "Raj Kumar",
            "designation": "Operator",
            "department": "Production",
            "location": "Chennai",
            "gender": "M",
            "status": "Active",
            "date_of_joining": "2020-01-15",
            "date_of_leaving": None,
            "whatsapp_contact": "+91 9876543210",
            "minimum_wages": "₹15,000",
            "house_rent": "3,000",
            "special_allowance": 1000,
            "extra_duty_allowance": None,
            "travelling_allowance": "1000.00",
            "bonus": 1250,
            "leave_with_wages": None,
            "labour_welfare_fund": 100,
            "cost_of_uniform": 100,
            "gross_wage": "24,450",
            "ctc": "32,450",
            "epf_13": "1,950",
            "esi_3_25": 794,
            "epf_12": 1800,
            "esi_0_75": 184,
            "professional_tax": 200,
            "total_deductions": "4,928",
            "net_take_home_pay": "19,522",
            "remarks": "Salary on hold"
        }

        cleaned = clean_employee_data(messy_employee)

        # Phone should be normalized
        self.assertEqual(cleaned["whatsapp_contact"], "9876543210")

        # Currency fields should be floats
        self.assertEqual(cleaned["minimum_wages"], 15000.0)
        self.assertEqual(cleaned["house_rent"], 3000.0)
        self.assertEqual(cleaned["gross_wage"], 24450.0)
        self.assertEqual(cleaned["net_take_home_pay"], 19522.0)
        self.assertEqual(cleaned["special_allowance"], 1000.0)

        # Missing currency fields should be 0.0
        self.assertEqual(cleaned["extra_duty_allowance"], 0.0)
        self.assertEqual(cleaned["leave_with_wages"], 0.0)

        # Date should be DD/MM/YYYY
        self.assertEqual(cleaned["date_of_joining"], "15/01/2020")
        self.assertEqual(cleaned["date_of_leaving"], "")

        # Remarks should be preserved exactly
        self.assertEqual(cleaned["remarks"], "Salary on hold")

        # Text fields should be unchanged
        self.assertEqual(cleaned["name"], "Raj Kumar")
        self.assertEqual(cleaned["status"], "Active")

        print("✅ TEST 23 PASSED: Full employee record cleaned correctly!")

    def test_completely_empty_record(self):
        """A record with all None values should get defaults without crashing."""
        empty_employee = {
            "emp_id": None,
            "name": None,
            "whatsapp_contact": None,
            "status": None,
            "gross_wage": None,
            "date_of_joining": None,
        }

        cleaned = clean_employee_data(empty_employee)

        self.assertEqual(cleaned["emp_id"], "")
        self.assertEqual(cleaned["name"], "")
        self.assertEqual(cleaned["whatsapp_contact"], "")
        self.assertEqual(cleaned["status"], "Active")
        self.assertEqual(cleaned["gross_wage"], 0.0)
        self.assertEqual(cleaned["date_of_joining"], "")

        print("✅ TEST 24 PASSED: Empty record gets safe defaults!")


class TestCleanAllEmployees(unittest.TestCase):
    """Test cases for batch cleaning."""

    def test_batch_clean(self):
        """Batch cleaning should process all employees."""
        employees = [
            {"name": "Raj Kumar", "whatsapp_contact": "+919876543210", "gross_wage": "15,000"},
            {"name": "Priya Singh", "whatsapp_contact": "8765432109", "gross_wage": 20000},
            {"name": None, "whatsapp_contact": None, "gross_wage": None},
        ]

        cleaned = clean_all_employees(employees)

        self.assertEqual(len(cleaned), 3)
        self.assertEqual(cleaned[0]["whatsapp_contact"], "9876543210")
        self.assertEqual(cleaned[0]["gross_wage"], 15000.0)
        self.assertEqual(cleaned[1]["gross_wage"], 20000.0)
        self.assertEqual(cleaned[2]["name"], "")
        self.assertEqual(cleaned[2]["gross_wage"], 0.0)

        print("✅ TEST 25 PASSED: Batch cleaning works!")

    def test_empty_batch(self):
        """Empty list should return empty list."""
        cleaned = clean_all_employees([])
        self.assertEqual(cleaned, [])
        print("✅ TEST 26 PASSED: Empty batch returns empty list!")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("  DATA CLEANERS - TEST SUITE")
    print("=" * 60 + "\n")
    unittest.main(verbosity=2)
