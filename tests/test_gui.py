"""Unit tests for GUI module.

Note: These tests verify the GUI initializes correctly and that
the helper methods work. They don't test interactive clicks
(that would require a GUI testing framework like pytest-qt).
"""

import unittest
import tkinter as tk
from src.gui import PaySlipApp


class TestGuiInit(unittest.TestCase):
    """Test GUI initialization."""

    def setUp(self):
        """Create a Tk root and app for each test."""
        self.root = tk.Tk()
        self.root.withdraw()  # Hide window during tests
        self.app = PaySlipApp(self.root)

    def tearDown(self):
        """Destroy the window after each test."""
        self.root.destroy()

    def test_window_title(self):
        """Window should have the correct title."""
        self.assertIn("PaySlip Generator", self.root.title())
        self.assertIn("Holistic Allied Services", self.root.title())
        print("✅ TEST 1 PASSED: Window title correct!")

    def test_initial_state(self):
        """App should start with empty state."""
        self.assertIsNone(self.app.file_path)
        self.assertEqual(self.app.raw_employees, [])
        self.assertEqual(self.app.cleaned_employees, [])
        self.assertEqual(self.app.generated_files, [])
        print("✅ TEST 2 PASSED: Initial state is empty!")

    def test_notebook_has_four_tabs(self):
        """Notebook should have 4 tabs."""
        tab_count = self.app.notebook.index("end")
        self.assertEqual(tab_count, 4)
        print("✅ TEST 3 PASSED: 4 tabs created!")

    def test_status_bar_exists(self):
        """Status bar should show ready message."""
        status = self.app.status_var.get()
        self.assertIn("Ready", status)
        print("✅ TEST 4 PASSED: Status bar shows ready!")

    def test_get_pay_period(self):
        """Pay period should generate both formats from dropdowns."""
        period, month = self.app._get_pay_period()
        self.assertIn("2026", period)
        self.assertTrue(period.isupper())
        self.assertIn("-", month)
        self.assertIn("26", month)
        print("✅ TEST 5 PASSED: Pay period generates both formats!")

    def test_period_preview_updates(self):
        """Preview text should show both formats."""
        self.app._update_period_preview()
        preview = self.app.period_preview_var.get()
        self.assertIn("Title:", preview)
        self.assertIn("Info:", preview)
        print("✅ TEST 6 PASSED: Period preview updates!")

    def test_clear_data(self):
        """Clear should reset all state."""
        # Simulate having data
        self.app.raw_employees = [{"name": "Test"}]
        self.app.cleaned_employees = [{"name": "Test"}]
        self.app.file_path = "/tmp/test.xlsx"

        self.app._clear_data()

        self.assertIsNone(self.app.file_path)
        self.assertEqual(self.app.raw_employees, [])
        self.assertEqual(self.app.cleaned_employees, [])
        self.assertIn("Ready", self.app.status_var.get())
        print("✅ TEST 7 PASSED: Clear resets all state!")

    def test_log_adds_entry(self):
        """Log should add timestamped entries."""
        self.app._log("Test message")
        self.app.log_text.config(state=tk.NORMAL)
        content = self.app.log_text.get("1.0", tk.END)
        self.app.log_text.config(state=tk.DISABLED)
        self.assertIn("Test message", content)
        print("✅ TEST 8 PASSED: Log entry added!")

    def test_populate_preview(self):
        """Preview table should populate with employee data."""
        employees = [
            {
                "emp_id": "EMP001", "name": "Raj Kumar",
                "designation": "Operator", "gross_wage": 25000,
                "total_deductions": 3000, "net_take_home_pay": 22000,
                "whatsapp_contact": "9876543210", "status": "Active"
            }
        ]
        self.app._populate_preview(employees)
        items = self.app.preview_tree.get_children()
        self.assertEqual(len(items), 1)
        print("✅ TEST 9 PASSED: Preview table populated!")

    def test_set_status(self):
        """Status bar should update."""
        self.app._set_status("Testing 123")
        self.assertEqual(self.app.status_var.get(), "Testing 123")
        print("✅ TEST 10 PASSED: Status bar updates!")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("  GUI - TEST SUITE")
    print("=" * 60 + "\n")
    unittest.main(verbosity=2)
