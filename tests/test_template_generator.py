"""Unit tests for Template Generator module."""

import os
import unittest
import tempfile
from src.template_generator import (
    EmployeeData, get_template_env, render_payslip, render_payslip_to_file
)


# --- Sample cleaned employee data (as it would come from cleaners.py) ---
SAMPLE_EMPLOYEE = {
    "emp_id": "HAS/BLR/0046",
    "name": "SYED ANSAR BASHA",
    "designation": "DRIVER",
    "department": "Admin",
    "location": "Bangalore",
    "gender": "M",
    "status": "Active",
    "date_of_joining": "01/11/2025",
    "date_of_leaving": "",
    "whatsapp_contact": "9876543210",
    "minimum_wages": 16253.0,
    "house_rent": 4063.0,
    "special_allowance": 500.0,
    "extra_duty_allowance": 2500.0,
    "travelling_allowance": 6500.0,
    "bonus": 1354.0,
    "leave_with_wages": 0.0,
    "labour_welfare_fund": 5.0,
    "cost_of_uniform": 0.0,
    "gross_wage": 30970.0,
    "ctc": 35000.0,
    "epf_13": 1800.0,
    "esi_3_25": 157.0,
    "epf_12": 1800.0,
    "esi_0_75": 0.0,
    "professional_tax": 0.0,
    "total_deductions": 1962.0,
    "net_take_home_pay": 29008.0,
    "remarks": ""
}


class TestEmployeeData(unittest.TestCase):
    """Test the EmployeeData dot-notation wrapper."""

    def test_access_existing_field(self):
        """Existing fields should return their values."""
        emp = EmployeeData({"name": "Raj Kumar", "emp_id": "EMP001"})
        self.assertEqual(emp.name, "Raj Kumar")
        self.assertEqual(emp.emp_id, "EMP001")
        print("✅ TEST 1 PASSED: Dot notation access works!")

    def test_access_missing_field(self):
        """Missing fields should return empty string (not crash)."""
        emp = EmployeeData({"name": "Raj Kumar"})
        self.assertEqual(emp.department, "")
        self.assertEqual(emp.whatsapp_contact, "")
        print("✅ TEST 2 PASSED: Missing fields return '' safely!")

    def test_numeric_fields(self):
        """Numeric fields should return their values as-is."""
        emp = EmployeeData({"gross_wage": 30970.0, "epf_13": 1800.0})
        self.assertEqual(emp.gross_wage, 30970.0)
        self.assertEqual(emp.epf_13, 1800.0)
        print("✅ TEST 3 PASSED: Numeric fields accessible!")


class TestGetTemplateEnv(unittest.TestCase):
    """Test Jinja2 environment setup."""

    def test_default_env(self):
        """Default environment should find the templates directory."""
        env = get_template_env()
        self.assertIsNotNone(env)
        # Should be able to load our template without error
        template = env.get_template("payslip_template.html")
        self.assertIsNotNone(template)
        print("✅ TEST 4 PASSED: Jinja2 environment loads templates!")


class TestRenderPayslip(unittest.TestCase):
    """Test payslip HTML rendering."""

    def test_render_contains_employee_name(self):
        """Rendered HTML should contain the employee's name."""
        html = render_payslip(
            SAMPLE_EMPLOYEE,
            pay_period="MARCH, 2026",
            pay_month="Mar-26"
        )
        self.assertIn("SYED ANSAR BASHA", html)
        print("✅ TEST 5 PASSED: Employee name appears in rendered HTML!")

    def test_render_contains_employee_id(self):
        """Rendered HTML should contain the employee ID."""
        html = render_payslip(SAMPLE_EMPLOYEE, pay_period="MARCH, 2026")
        self.assertIn("HAS/BLR/0046", html)
        print("✅ TEST 6 PASSED: Employee ID appears in rendered HTML!")

    def test_render_contains_salary_amounts(self):
        """Rendered HTML should contain the salary amounts."""
        html = render_payslip(SAMPLE_EMPLOYEE, pay_period="MARCH, 2026")
        self.assertIn("16,253", html)   # minimum_wages
        self.assertIn("30,970", html)   # gross_wage
        self.assertIn("1,962", html)    # total_deductions
        self.assertIn("29,008", html)   # net_take_home_pay
        print("✅ TEST 7 PASSED: Salary amounts appear correctly!")

    def test_render_contains_pay_period(self):
        """Rendered HTML should contain the pay period."""
        html = render_payslip(SAMPLE_EMPLOYEE, pay_period="MARCH, 2026")
        self.assertIn("MARCH, 2026", html)
        print("✅ TEST 8 PASSED: Pay period appears in rendered HTML!")

    def test_render_contains_company_logo(self):
        """Rendered HTML should contain the company logo image."""
        html = render_payslip(SAMPLE_EMPLOYEE, pay_period="MARCH, 2026")
        self.assertIn("logo.jpg", html)
        self.assertIn("Holistic Allied Services", html)  # alt text
        print("✅ TEST 9 PASSED: Company logo appears in rendered HTML!")

    def test_render_contains_deduction_items(self):
        """Rendered HTML should contain deduction line items."""
        html = render_payslip(SAMPLE_EMPLOYEE, pay_period="MARCH, 2026")
        self.assertIn("PF Employee", html)
        self.assertIn("ESI Employee", html)
        self.assertIn("1,800", html)  # epf_13
        print("✅ TEST 10 PASSED: Deduction items appear correctly!")

    def test_render_contains_earnings_items(self):
        """Rendered HTML should contain earning line items."""
        html = render_payslip(SAMPLE_EMPLOYEE, pay_period="MARCH, 2026")
        self.assertIn("Basic Salary", html)
        self.assertIn("HRA", html)
        self.assertIn("Special Allowance", html)
        self.assertIn("Travelling Allowance", html)
        print("✅ TEST 11 PASSED: Earning items appear correctly!")

    def test_render_with_remarks(self):
        """Remarks should appear when present."""
        emp_with_remarks = dict(SAMPLE_EMPLOYEE)
        emp_with_remarks["remarks"] = "Salary on hold"
        html = render_payslip(emp_with_remarks, pay_period="MARCH, 2026")
        self.assertIn("Salary on hold", html)
        print("✅ TEST 12 PASSED: Remarks appear when present!")

    def test_render_without_remarks(self):
        """Remarks section should not appear when empty."""
        html = render_payslip(SAMPLE_EMPLOYEE, pay_period="MARCH, 2026")
        self.assertNotIn("Remarks:", html)
        print("✅ TEST 13 PASSED: Remarks hidden when empty!")

    def test_render_is_valid_html(self):
        """Rendered output should be valid HTML with proper structure."""
        html = render_payslip(SAMPLE_EMPLOYEE, pay_period="MARCH, 2026")
        self.assertIn("<!DOCTYPE html>", html)
        self.assertIn("<html", html)
        self.assertIn("</html>", html)
        self.assertIn("<body>", html)
        print("✅ TEST 14 PASSED: Output is valid HTML!")

    def test_render_with_zero_values(self):
        """Zero salary values should render as 0, not crash."""
        empty_emp = {
            "emp_id": "TEST001",
            "name": "Test Employee",
            "designation": "",
            "department": "",
            "location": "",
            "gender": "",
            "status": "Active",
            "date_of_joining": "",
            "date_of_leaving": "",
            "whatsapp_contact": "",
            "minimum_wages": 0.0,
            "house_rent": 0.0,
            "special_allowance": 0.0,
            "extra_duty_allowance": 0.0,
            "travelling_allowance": 0.0,
            "bonus": 0.0,
            "leave_with_wages": 0.0,
            "labour_welfare_fund": 0.0,
            "cost_of_uniform": 0.0,
            "gross_wage": 0.0,
            "ctc": 0.0,
            "epf_13": 0.0,
            "esi_3_25": 0.0,
            "epf_12": 0.0,
            "esi_0_75": 0.0,
            "professional_tax": 0.0,
            "total_deductions": 0.0,
            "net_take_home_pay": 0.0,
            "remarks": ""
        }
        html = render_payslip(empty_emp, pay_period="MARCH, 2026")
        self.assertIn("Test Employee", html)
        print("✅ TEST 15 PASSED: Zero-value employee renders without crash!")


class TestRenderPayslipToFile(unittest.TestCase):
    """Test saving rendered HTML to a file."""

    def test_save_html_file(self):
        """Rendered HTML should save to a file that exists and has content."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "test_payslip.html")
            result = render_payslip_to_file(
                SAMPLE_EMPLOYEE,
                output_path,
                pay_period="MARCH, 2026",
                pay_month="Mar-26"
            )

            self.assertEqual(result, output_path)
            self.assertTrue(os.path.exists(output_path))

            with open(output_path, 'r', encoding='utf-8') as f:
                content = f.read()
            self.assertIn("SYED ANSAR BASHA", content)
            self.assertIn("29,008", content)

        print("✅ TEST 16 PASSED: HTML file saved and contains correct data!")

    def test_creates_parent_dirs(self):
        """Should create parent directories if they don't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "subdir", "deep", "payslip.html")
            result = render_payslip_to_file(
                SAMPLE_EMPLOYEE,
                output_path,
                pay_period="MARCH, 2026"
            )

            self.assertTrue(os.path.exists(output_path))

        print("✅ TEST 17 PASSED: Parent directories created automatically!")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("  TEMPLATE GENERATOR - TEST SUITE")
    print("=" * 60 + "\n")
    unittest.main(verbosity=2)
