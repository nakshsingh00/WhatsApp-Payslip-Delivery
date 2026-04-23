"""Unit tests for PDF Generator module."""

import os
import time
import unittest
import tempfile
from pathlib import Path
from src.pdf_generator import (
    generate_pdf, batch_generate_pdfs, verify_pdf, verify_batch,
    archive_old_pdfs
)


# --- Sample cleaned employee (same data as the test payslip that looked correct) ---
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

SAMPLE_EMPLOYEE_2 = {
    "emp_id": "HAS/BLR/0099",
    "name": "PRIYA SHARMA",
    "designation": "SUPERVISOR",
    "department": "Operations",
    "location": "Bangalore",
    "gender": "F",
    "status": "Active",
    "date_of_joining": "15/03/2023",
    "date_of_leaving": "",
    "whatsapp_contact": "8765432109",
    "minimum_wages": 20000.0,
    "house_rent": 5000.0,
    "special_allowance": 2000.0,
    "extra_duty_allowance": 0.0,
    "travelling_allowance": 3000.0,
    "bonus": 1666.0,
    "leave_with_wages": 0.0,
    "labour_welfare_fund": 10.0,
    "cost_of_uniform": 0.0,
    "gross_wage": 31676.0,
    "ctc": 38000.0,
    "epf_13": 2600.0,
    "esi_3_25": 200.0,
    "epf_12": 2400.0,
    "esi_0_75": 0.0,
    "professional_tax": 200.0,
    "total_deductions": 3000.0,
    "net_take_home_pay": 28676.0,
    "remarks": ""
}


class TestGeneratePdf(unittest.TestCase):
    """Test single PDF generation."""

    def test_generate_single_pdf(self):
        """Should generate a valid PDF file for one employee."""
        with tempfile.TemporaryDirectory() as tmpdir:
            success, path = generate_pdf(
                SAMPLE_EMPLOYEE,
                output_dir=tmpdir,
                pay_period="MARCH, 2026",
                pay_month="Mar-26"
            )

            self.assertTrue(success, f"PDF generation failed: {path}")
            self.assertTrue(os.path.exists(path))
            self.assertGreater(os.path.getsize(path), 0)
            self.assertTrue(path.endswith(".pdf"))

        print("✅ TEST 1 PASSED: Single PDF generated successfully!")

    def test_auto_filename(self):
        """Auto-generated filename should contain emp_id and name."""
        with tempfile.TemporaryDirectory() as tmpdir:
            success, path = generate_pdf(
                SAMPLE_EMPLOYEE,
                output_dir=tmpdir,
                pay_period="MARCH, 2026",
                pay_month="Mar-26"
            )

            filename = os.path.basename(path)
            self.assertIn("HAS_BLR_0046", filename)
            self.assertIn("SYED_ANSAR_BASHA", filename)

        print("✅ TEST 2 PASSED: Auto filename contains employee info!")

    def test_custom_filename(self):
        """Custom filename should be used when provided."""
        with tempfile.TemporaryDirectory() as tmpdir:
            success, path = generate_pdf(
                SAMPLE_EMPLOYEE,
                output_dir=tmpdir,
                pay_period="MARCH, 2026",
                filename="custom_payslip.pdf"
            )

            self.assertTrue(path.endswith("custom_payslip.pdf"))

        print("✅ TEST 3 PASSED: Custom filename used!")

    def test_creates_output_directory(self):
        """Should create the output directory if it doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            deep_dir = os.path.join(tmpdir, "sub", "deep", "payslips")
            success, path = generate_pdf(
                SAMPLE_EMPLOYEE,
                output_dir=deep_dir,
                pay_period="MARCH, 2026"
            )

            self.assertTrue(success)
            self.assertTrue(os.path.exists(deep_dir))

        print("✅ TEST 4 PASSED: Output directory created automatically!")

    def test_pdf_starts_with_magic_bytes(self):
        """Generated file should be a real PDF (starts with %PDF)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            success, path = generate_pdf(
                SAMPLE_EMPLOYEE,
                output_dir=tmpdir,
                pay_period="MARCH, 2026"
            )

            with open(path, 'rb') as f:
                header = f.read(5)
            self.assertTrue(header.startswith(b'%PDF'))

        print("✅ TEST 5 PASSED: Generated file is a real PDF!")


class TestBatchGeneratePdfs(unittest.TestCase):
    """Test batch PDF generation."""

    def test_batch_two_employees(self):
        """Batch should generate PDFs for all employees."""
        with tempfile.TemporaryDirectory() as tmpdir:
            results = batch_generate_pdfs(
                [SAMPLE_EMPLOYEE, SAMPLE_EMPLOYEE_2],
                output_dir=tmpdir,
                pay_period="MARCH, 2026",
                pay_month="Mar-26"
            )

            self.assertEqual(results["total"], 2)
            self.assertEqual(results["success"], 2)
            self.assertEqual(results["failed"], 0)
            self.assertEqual(len(results["generated_files"]), 2)

        print("✅ TEST 6 PASSED: Batch generated 2 PDFs!")

    def test_batch_progress_callback(self):
        """Progress callback should be called for each employee."""
        progress_log = []

        def on_progress(current, total, name):
            progress_log.append((current, total, name))

        with tempfile.TemporaryDirectory() as tmpdir:
            batch_generate_pdfs(
                [SAMPLE_EMPLOYEE, SAMPLE_EMPLOYEE_2],
                output_dir=tmpdir,
                pay_period="MARCH, 2026",
                on_progress=on_progress
            )

        self.assertEqual(len(progress_log), 2)
        self.assertEqual(progress_log[0], (1, 2, "SYED ANSAR BASHA"))
        self.assertEqual(progress_log[1], (2, 2, "PRIYA SHARMA"))

        print("✅ TEST 7 PASSED: Progress callback called correctly!")

    def test_empty_batch(self):
        """Empty employee list should return zero results."""
        with tempfile.TemporaryDirectory() as tmpdir:
            results = batch_generate_pdfs([], output_dir=tmpdir)

        self.assertEqual(results["total"], 0)
        self.assertEqual(results["success"], 0)

        print("✅ TEST 8 PASSED: Empty batch returns zero results!")


class TestVerifyPdf(unittest.TestCase):
    """Test PDF verification."""

    def test_verify_valid_pdf(self):
        """A real generated PDF should pass verification."""
        with tempfile.TemporaryDirectory() as tmpdir:
            success, path = generate_pdf(
                SAMPLE_EMPLOYEE,
                output_dir=tmpdir,
                pay_period="MARCH, 2026"
            )

            valid, msg = verify_pdf(path)
            self.assertTrue(valid, msg)

        print("✅ TEST 9 PASSED: Valid PDF passes verification!")

    def test_verify_missing_file(self):
        """Non-existent file should fail verification."""
        valid, msg = verify_pdf("/tmp/does_not_exist_12345.pdf")
        self.assertFalse(valid)
        self.assertIn("not found", msg.lower())

        print("✅ TEST 10 PASSED: Missing file fails verification!")

    def test_verify_empty_file(self):
        """Empty file should fail verification."""
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            empty_path = f.name
            # File is created but has 0 bytes

        try:
            valid, msg = verify_pdf(empty_path)
            self.assertFalse(valid)
            self.assertIn("empty", msg.lower())
        finally:
            os.unlink(empty_path)

        print("✅ TEST 11 PASSED: Empty file fails verification!")

    def test_verify_not_a_pdf(self):
        """A text file renamed to .pdf should fail verification."""
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False, mode='w') as f:
            f.write("This is not a PDF file")
            fake_path = f.name

        try:
            valid, msg = verify_pdf(fake_path)
            self.assertFalse(valid)
            self.assertIn("not a valid pdf", msg.lower())
        finally:
            os.unlink(fake_path)

        print("✅ TEST 12 PASSED: Fake PDF fails verification!")

    def test_verify_batch(self):
        """Batch verification should check all files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            _, path1 = generate_pdf(SAMPLE_EMPLOYEE, output_dir=tmpdir, pay_period="MARCH, 2026")
            _, path2 = generate_pdf(SAMPLE_EMPLOYEE_2, output_dir=tmpdir, pay_period="MARCH, 2026")

            results = verify_batch([path1, path2])
            self.assertEqual(results["valid"], 2)
            self.assertEqual(results["invalid"], 0)

        print("✅ TEST 13 PASSED: Batch verification works!")


class TestArchiveOldPdfs(unittest.TestCase):
    """Test PDF auto-archival."""

    def test_archive_old_files(self):
        """Files older than retention period should be moved to archive."""
        with tempfile.TemporaryDirectory() as tmpdir:
            source = os.path.join(tmpdir, "generated")
            archive = os.path.join(tmpdir, "archived")
            os.makedirs(source)

            # Create a "old" PDF file and backdate its modification time
            old_file = os.path.join(source, "old_payslip.pdf")
            with open(old_file, 'wb') as f:
                f.write(b'%PDF-fake-old-file')

            # Set modification time to 100 days ago
            old_time = time.time() - (100 * 86400)
            os.utime(old_file, (old_time, old_time))

            # Create a "new" PDF file (today)
            new_file = os.path.join(source, "new_payslip.pdf")
            with open(new_file, 'wb') as f:
                f.write(b'%PDF-fake-new-file')

            results = archive_old_pdfs(
                source_dir=source,
                archive_dir=archive,
                retention_days=90
            )

            self.assertEqual(results["scanned"], 2)
            self.assertEqual(results["archived"], 1)
            self.assertEqual(results["kept"], 1)

            # Old file should be in archive, not in source
            self.assertFalse(os.path.exists(old_file))
            self.assertTrue(os.path.exists(os.path.join(archive, "old_payslip.pdf")))

            # New file should still be in source
            self.assertTrue(os.path.exists(new_file))

        print("✅ TEST 14 PASSED: Old files archived, new files kept!")

    def test_archive_empty_directory(self):
        """Empty source directory should return zero results."""
        with tempfile.TemporaryDirectory() as tmpdir:
            source = os.path.join(tmpdir, "empty_source")
            os.makedirs(source)

            results = archive_old_pdfs(source_dir=source)
            self.assertEqual(results["scanned"], 0)
            self.assertEqual(results["archived"], 0)

        print("✅ TEST 15 PASSED: Empty directory returns zero!")

    def test_archive_nonexistent_directory(self):
        """Non-existent source should return zero results (not crash)."""
        results = archive_old_pdfs(source_dir="/tmp/does_not_exist_xyz")
        self.assertEqual(results["scanned"], 0)

        print("✅ TEST 16 PASSED: Non-existent dir handled gracefully!")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("  PDF GENERATOR - TEST SUITE")
    print("=" * 60 + "\n")
    unittest.main(verbosity=2)
