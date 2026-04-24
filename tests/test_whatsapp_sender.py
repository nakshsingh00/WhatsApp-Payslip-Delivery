"""Unit tests for WhatsApp Sender module.

Note: Tests that actually send messages are marked with 'live' in the name
and only run when TWILIO_LIVE_TEST=1 is set. All other tests use mocking
or test helper functions without hitting the Twilio API.
"""

import os
import json
import unittest
import tempfile
from unittest.mock import patch, MagicMock
from src.whatsapp_sender import (
    verify_connection, send_message, send_batch,
    save_delivery_report, get_delivery_status
)


class TestVerifyConnection(unittest.TestCase):
    """Test Twilio connection verification."""

    def test_verify_connection_works(self):
        """Should connect successfully with valid .env credentials."""
        connected, msg = verify_connection()
        self.assertTrue(connected, f"Connection failed: {msg}")
        self.assertIn("Connected", msg)
        print("✅ TEST 1 PASSED: Twilio connection verified!")


class TestSendMessage(unittest.TestCase):
    """Test single message sending."""

    def test_invalid_phone_returns_failure(self):
        """Invalid phone number should fail without calling Twilio."""
        success, result = send_message("123", "/tmp/fake.pdf", "Test")
        self.assertFalse(success)
        self.assertEqual(result["status"], "failed")
        self.assertIn("Invalid phone", result["error"])
        print("✅ TEST 2 PASSED: Invalid phone rejected!")

    def test_missing_pdf_returns_failure(self):
        """Missing PDF file should fail without calling Twilio."""
        success, result = send_message(
            "9876543210", "/tmp/nonexistent_payslip.pdf", "Test"
        )
        self.assertFalse(success)
        self.assertEqual(result["status"], "failed")
        self.assertIn("PDF not found", result["error"])
        print("✅ TEST 3 PASSED: Missing PDF rejected!")

    def test_empty_phone_returns_failure(self):
        """Empty phone should fail."""
        success, result = send_message("", "/tmp/fake.pdf", "Test")
        self.assertFalse(success)
        self.assertIn("Invalid", result["error"])
        print("✅ TEST 4 PASSED: Empty phone rejected!")

    def test_result_has_required_fields(self):
        """Result dict should always contain the expected keys."""
        success, result = send_message("bad", "/tmp/fake.pdf", "Test")
        self.assertIn("phone", result)
        self.assertIn("name", result)
        self.assertIn("message_sid", result)
        self.assertIn("status", result)
        self.assertIn("error", result)
        self.assertIn("timestamp", result)
        print("✅ TEST 5 PASSED: Result has all required fields!")


class TestSendBatch(unittest.TestCase):
    """Test batch sending."""

    @patch("src.whatsapp_sender.send_message")
    def test_batch_skips_no_phone(self, mock_send):
        """Employees without phone numbers should be skipped."""
        employees = [
            {"name": "No Phone", "emp_id": "E001", "whatsapp_contact": ""},
            {"name": "Has NaN", "emp_id": "E002", "whatsapp_contact": "nan"},
            {"name": "Has NA", "emp_id": "E003", "whatsapp_contact": "#N/A"},
        ]

        results = send_batch(employees, "/tmp", delay_seconds=0)

        self.assertEqual(results["total"], 3)
        self.assertEqual(results["skipped"], 3)
        self.assertEqual(results["sent"], 0)
        mock_send.assert_not_called()
        print("✅ TEST 6 PASSED: Employees without phone numbers skipped!")

    @patch("src.whatsapp_sender.send_message")
    def test_batch_progress_callback(self, mock_send):
        """Progress callback should be called for each employee."""
        mock_send.return_value = (True, {"status": "queued", "message_sid": "SM123"})

        progress_log = []
        def on_progress(current, total, name, status):
            progress_log.append((current, total, name))

        employees = [
            {"name": "Emp A", "emp_id": "E001", "whatsapp_contact": "9876543210"},
            {"name": "Emp B", "emp_id": "E002", "whatsapp_contact": "8765432109"},
        ]

        results = send_batch(
            employees, "/tmp",
            delay_seconds=0, on_progress=on_progress
        )

        self.assertEqual(len(progress_log), 2)
        self.assertEqual(progress_log[0][2], "Emp A")
        self.assertEqual(progress_log[1][2], "Emp B")
        print("✅ TEST 7 PASSED: Progress callback called!")

    @patch("src.whatsapp_sender.send_message")
    def test_batch_counts_sent_and_failed(self, mock_send):
        """Batch should correctly count sent and failed."""
        mock_send.side_effect = [
            (True, {"status": "queued", "message_sid": "SM1"}),
            (False, {"status": "failed", "error": "API error"}),
        ]

        employees = [
            {"name": "Success", "emp_id": "E001", "whatsapp_contact": "9876543210"},
            {"name": "Failure", "emp_id": "E002", "whatsapp_contact": "8765432109"},
        ]

        results = send_batch(employees, "/tmp", delay_seconds=0)

        self.assertEqual(results["sent"], 1)
        self.assertEqual(results["failed"], 1)
        print("✅ TEST 8 PASSED: Batch counts sent/failed correctly!")


class TestSaveDeliveryReport(unittest.TestCase):
    """Test delivery report saving."""

    def test_save_report_creates_file(self):
        """Report should be saved as a JSON file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            results = {
                "total": 2, "sent": 1, "failed": 1,
                "deliveries": [], "errors": []
            }

            path = save_delivery_report(results, output_dir=tmpdir)

            self.assertTrue(os.path.exists(path))
            self.assertTrue(path.endswith(".json"))

            with open(path, 'r') as f:
                saved = json.load(f)
            self.assertEqual(saved["total"], 2)

        print("✅ TEST 9 PASSED: Report saved as JSON!")


class TestLiveDelivery(unittest.TestCase):
    """Live tests that actually send WhatsApp messages.

    Only run when TWILIO_LIVE_TEST=1 environment variable is set.
    """

    @unittest.skipUnless(
        os.getenv("TWILIO_LIVE_TEST") == "1",
        "Set TWILIO_LIVE_TEST=1 to run live WhatsApp tests"
    )
    def test_live_send_message(self):
        """Actually send a test message via WhatsApp."""
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            f.write(b"%PDF-test")
            pdf_path = f.name

        try:
            success, result = send_message(
                phone_number="9217464908",
                pdf_path=pdf_path,
                employee_name="Test Employee",
                pay_period="MARCH, 2026"
            )
            self.assertTrue(success, f"Live send failed: {result}")
            self.assertIsNotNone(result["message_sid"])
            print("✅ LIVE TEST PASSED: Message sent via WhatsApp!")
        finally:
            os.unlink(pdf_path)


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("  WHATSAPP SENDER - TEST SUITE")
    print("=" * 60 + "\n")
    unittest.main(verbosity=2)
