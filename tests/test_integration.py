"""Integration tests — test the full pipeline end-to-end.

These tests verify that all modules work together correctly:
  Excel Reader → Validators → Cleaners → Template → PDF

Each test runs the real pipeline with test data, not mocks.
"""

import os
import unittest
import tempfile
from src.excel_reader import read_excel
from src.validators import generate_validation_report
from src.cleaners import clean_all_employees
from src.template_generator import render_payslip
from src.pdf_generator import generate_pdf, batch_generate_pdfs, verify_batch


# Path to test Excel file
TEST_EXCEL = os.path.join("data", "sample", "test_payroll_march2026.xlsx")


class TestFullPipeline(unittest.TestCase):
    """Test the complete pipeline from Excel to PDF."""

    def test_read_clean_render(self):
        """Excel → Clean → Render HTML should produce valid HTML."""
        success, employees, msg = read_excel(TEST_EXCEL)
        self.assertTrue(success, msg)
        self.assertGreater(len(employees), 0)

        cleaned = clean_all_employees(employees)
        self.assertEqual(len(cleaned), len(employees))

        html = render_payslip(cleaned[0], pay_period="MARCH, 2026")
        self.assertIn("<!DOCTYPE html>", html)
        self.assertIn(cleaned[0]["name"], html)

        print("✅ INTEGRATION 1 PASSED: Excel → Clean → HTML works!")

    def test_read_clean_generate_pdf(self):
        """Excel → Clean → PDF should produce a valid PDF file."""
        success, employees, msg = read_excel(TEST_EXCEL)
        cleaned = clean_all_employees(employees)

        with tempfile.TemporaryDirectory() as tmpdir:
            ok, path = generate_pdf(
                cleaned[0], output_dir=tmpdir,
                pay_period="MARCH, 2026", pay_month="Mar-26"
            )

            self.assertTrue(ok, path)
            self.assertTrue(os.path.exists(path))

            # Verify it's a real PDF
            with open(path, 'rb') as f:
                self.assertTrue(f.read(5).startswith(b'%PDF'))

        print("✅ INTEGRATION 2 PASSED: Excel → Clean → PDF works!")

    def test_full_batch_pipeline(self):
        """Excel → Clean → Batch PDF → Verify should all succeed."""
        success, employees, msg = read_excel(TEST_EXCEL)
        cleaned = clean_all_employees(employees)

        with tempfile.TemporaryDirectory() as tmpdir:
            results = batch_generate_pdfs(
                cleaned, output_dir=tmpdir,
                pay_period="MARCH, 2026", pay_month="Mar-26"
            )

            self.assertEqual(results["success"], len(cleaned))
            self.assertEqual(results["failed"], 0)

            # Verify all generated PDFs
            verify = verify_batch(results["generated_files"])
            self.assertEqual(verify["valid"], len(cleaned))
            self.assertEqual(verify["invalid"], 0)

        print("✅ INTEGRATION 3 PASSED: Full batch pipeline works!")

    def test_validation_before_cleaning(self):
        """Validation report should work on raw data before cleaning."""
        success, employees, msg = read_excel(TEST_EXCEL)
        report = generate_validation_report(employees)

        self.assertIn("total_employees", report)
        self.assertIn("valid_employees", report)
        self.assertGreater(report["total_employees"], 0)

        print("✅ INTEGRATION 4 PASSED: Validation on raw data works!")

    def test_location_folder_sorting(self):
        """PDFs should be sorted into location subfolders."""
        success, employees, msg = read_excel(TEST_EXCEL)
        cleaned = clean_all_employees(employees)

        with tempfile.TemporaryDirectory() as tmpdir:
            results = batch_generate_pdfs(
                cleaned, output_dir=tmpdir,
                pay_period="MARCH, 2026", pay_month="Mar-26"
            )

            # Check that location subfolders were created
            for pdf_path in results["generated_files"]:
                self.assertTrue(os.path.exists(pdf_path))

            # At least one location folder should exist
            subdirs = [d for d in os.listdir(tmpdir)
                       if os.path.isdir(os.path.join(tmpdir, d))]
            self.assertGreater(len(subdirs), 0,
                               "Expected location subfolders in output")

        print("✅ INTEGRATION 5 PASSED: Location folder sorting works!")

    def test_cleaned_data_has_correct_types(self):
        """After cleaning, currency fields should be floats and phones strings."""
        success, employees, msg = read_excel(TEST_EXCEL)
        cleaned = clean_all_employees(employees)

        for emp in cleaned:
            # Currency fields should be floats
            self.assertIsInstance(emp.get("gross_wage", 0), float)
            self.assertIsInstance(emp.get("net_take_home_pay", 0), float)
            self.assertIsInstance(emp.get("minimum_wages", 0), float)

            # Phone should be a string
            self.assertIsInstance(emp.get("whatsapp_contact", ""), str)

            # Status should not be None
            self.assertIsNotNone(emp.get("status"))

        print("✅ INTEGRATION 6 PASSED: Cleaned data has correct types!")


class TestErrorScenarios(unittest.TestCase):
    """Test that the pipeline handles errors gracefully."""

    def test_missing_excel_file(self):
        """Missing Excel file should return failure, not crash."""
        success, employees, msg = read_excel("/tmp/does_not_exist_xyz.xlsx")
        self.assertFalse(success)
        self.assertEqual(employees, [])
        print("✅ ERROR 1 PASSED: Missing Excel file handled!")

    def test_empty_employee_list(self):
        """Empty list should produce empty results, not crash."""
        cleaned = clean_all_employees([])
        self.assertEqual(cleaned, [])

        with tempfile.TemporaryDirectory() as tmpdir:
            results = batch_generate_pdfs([], output_dir=tmpdir)
            self.assertEqual(results["total"], 0)
            self.assertEqual(results["success"], 0)

        print("✅ ERROR 2 PASSED: Empty employee list handled!")

    def test_employee_with_all_none_values(self):
        """Employee with all None fields should clean without crashing."""
        from src.cleaners import clean_employee_data

        empty_emp = {k: None for k in [
            "emp_id", "name", "designation", "department", "location",
            "gender", "status", "whatsapp_contact", "minimum_wages",
            "gross_wage", "net_take_home_pay", "total_deductions"
        ]}

        cleaned = clean_employee_data(empty_emp)
        self.assertEqual(cleaned["name"], "")
        self.assertEqual(cleaned["status"], "Active")
        self.assertEqual(cleaned["gross_wage"], 0.0)

        print("✅ ERROR 3 PASSED: All-None employee handled!")

    def test_pdf_generation_with_zero_salary(self):
        """Employee with zero salary should still generate a valid PDF."""
        from src.cleaners import clean_employee_data

        zero_emp = clean_employee_data({
            "emp_id": "TEST/ZERO", "name": "Zero Salary Employee",
            "designation": "Test", "department": "Test",
            "location": "Test", "status": "Active",
            "minimum_wages": 0, "house_rent": 0,
            "special_allowance": 0, "extra_duty_allowance": 0,
            "travelling_allowance": 0, "bonus": 0,
            "leave_with_wages": 0, "labour_welfare_fund": 0,
            "cost_of_uniform": 0, "gross_wage": 0, "ctc": 0,
            "epf_13": 0, "esi_3_25": 0, "epf_12": 0, "esi_0_75": 0,
            "professional_tax": 0, "total_deductions": 0,
            "net_take_home_pay": 0, "remarks": ""
        })

        with tempfile.TemporaryDirectory() as tmpdir:
            ok, path = generate_pdf(
                zero_emp, output_dir=tmpdir, pay_period="TEST"
            )
            self.assertTrue(ok, path)

        print("✅ ERROR 4 PASSED: Zero salary PDF generated!")

    def test_special_characters_in_name(self):
        """Employee names with special characters should not crash PDF gen."""
        from src.cleaners import clean_employee_data

        emp = clean_employee_data({
            "emp_id": "TEST/SPECIAL", "name": "Raj's \"Test\" Employee (Jr.)",
            "designation": "Test & Dev", "department": "R&D",
            "location": "Test City", "status": "Active",
            "minimum_wages": 10000, "gross_wage": 10000,
            "net_take_home_pay": 9000, "total_deductions": 1000,
            "house_rent": 0, "special_allowance": 0,
            "extra_duty_allowance": 0, "travelling_allowance": 0,
            "bonus": 0, "leave_with_wages": 0, "labour_welfare_fund": 0,
            "cost_of_uniform": 0, "ctc": 12000,
            "epf_13": 500, "esi_3_25": 200, "epf_12": 500,
            "esi_0_75": 50, "professional_tax": 200, "remarks": ""
        })

        with tempfile.TemporaryDirectory() as tmpdir:
            ok, path = generate_pdf(emp, output_dir=tmpdir, pay_period="TEST")
            self.assertTrue(ok, path)

        print("✅ ERROR 5 PASSED: Special characters in name handled!")

    def test_very_large_salary_values(self):
        """Very large salary numbers should render correctly."""
        from src.cleaners import clean_employee_data

        emp = clean_employee_data({
            "emp_id": "TEST/BIG", "name": "High Earner",
            "designation": "CEO", "department": "Management",
            "location": "Mumbai", "status": "Active",
            "minimum_wages": 9999999, "gross_wage": 15000000,
            "net_take_home_pay": 12000000, "total_deductions": 3000000,
            "house_rent": 2000000, "special_allowance": 1000000,
            "extra_duty_allowance": 500000, "travelling_allowance": 500000,
            "bonus": 1000000, "leave_with_wages": 0, "labour_welfare_fund": 0,
            "cost_of_uniform": 0, "ctc": 20000000,
            "epf_13": 1000000, "esi_3_25": 500000, "epf_12": 1000000,
            "esi_0_75": 200000, "professional_tax": 300000, "remarks": ""
        })

        html = render_payslip(emp, pay_period="TEST")
        self.assertIn("15,000,000", html)  # Gross wage formatted
        self.assertIn("12,000,000", html)  # Net pay formatted

        print("✅ ERROR 6 PASSED: Large salary values rendered correctly!")

    def test_whatsapp_batch_with_mixed_phones(self):
        """Batch with valid, invalid, and missing phones should handle all."""
        from unittest.mock import patch

        employees = [
            {"name": "Valid", "emp_id": "E1", "whatsapp_contact": "9876543210", "location": ""},
            {"name": "Empty", "emp_id": "E2", "whatsapp_contact": "", "location": ""},
            {"name": "NaN", "emp_id": "E3", "whatsapp_contact": "nan", "location": ""},
            {"name": "Hash", "emp_id": "E4", "whatsapp_contact": "#N/A", "location": ""},
        ]

        from src.whatsapp_sender import send_batch

        with patch("src.whatsapp_sender.send_message") as mock_send:
            mock_send.return_value = (True, {"status": "queued", "message_sid": "SM1"})
            results = send_batch(employees, "/tmp", delay_seconds=0)

        self.assertEqual(results["skipped"], 3)  # Empty, NaN, #N/A
        self.assertEqual(results["sent"], 1)      # Valid

        print("✅ ERROR 7 PASSED: Mixed phone numbers handled correctly!")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("  INTEGRATION & ERROR TESTS")
    print("=" * 60 + "\n")
    unittest.main(verbosity=2)
