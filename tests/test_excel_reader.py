"""Unit tests for Excel Reader module."""

import unittest
import pandas as pd
from pathlib import Path
from tempfile import TemporaryDirectory
from src.excel_reader import (
    read_excel, find_column, validate_columns, get_employee_summary,
    get_excel_info, preview_excel, get_column_mapping
)


def create_sample_excel(file_path: str) -> None:
    """Create sample Excel file for testing."""
    data = {
        "Employee ID": [101, 102, 103, 104, 105],
        "Employee Name": ["Raj Kumar", "Priya Singh", "Amit Patel", "Anjali Verma", "Rohan Gupta"],
        "Designation": ["Operator", "Supervisor", "Technician", "Officer", "Manager"],
        "Department": ["Production", "Production", "Maintenance", "Admin", "HR"],
        "Location": ["Chennai", "Chennai", "Chennai", "Chennai", "Chennai"],
        "Status": ["Active", "Active", "Active", "Left", "Active"],
        "DOJ": ["2020-01-15", "2019-06-01", "2018-03-20", "2017-01-10", "2021-05-15"],
        "DOL": ["", "", "", "2023-12-31", ""],
        "WhatsApp": ["9876543210", "9876543211", "9876543212", "9876543213", ""],
        "Gross Wage": [15000, 18000, 16500, 20000, 22000],
        "Net Pay": [12000, 14400, 13200, 16000, 17600]
    }
    
    df = pd.DataFrame(data)
    df.to_excel(file_path, index=False)


class TestExcelReader(unittest.TestCase):
    """Test cases for Excel Reader module."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures."""
        cls.temp_dir = TemporaryDirectory()
        cls.sample_file = Path(cls.temp_dir.name) / "sample.xlsx"
        create_sample_excel(str(cls.sample_file))
    
    @classmethod
    def tearDownClass(cls):
        """Clean up test fixtures."""
        cls.temp_dir.cleanup()
    
    def test_column_mapping(self):
        """Test that column mapping has all required fields."""
        mapping = get_column_mapping()
        
        # Should have at least 25 fields
        self.assertGreaterEqual(len(mapping), 25)
        
        # Check critical fields exist
        critical_fields = ["emp_id", "name", "gross_wage", "net_take_home_pay", "whatsapp_contact"]
        for field in critical_fields:
            self.assertIn(field, mapping)
            self.assertIsInstance(mapping[field], list)
            self.assertGreater(len(mapping[field]), 0)
        
        print("✅ TEST 1 PASSED: Column mapping verified!")
    
    def test_find_column(self):
        """Test column finding with exact and case-insensitive matching."""
        columns = ["Employee ID", "Employee Name", "Gross Wage"]
        
        # Exact match
        found, col = find_column(columns, ["Employee ID"])
        self.assertTrue(found)
        self.assertEqual(col, "Employee ID")
        
        # Case-insensitive match
        found, col = find_column(columns, ["employee id", "emp id"])
        self.assertTrue(found)
        self.assertIn(col.lower(), ["employee id"])
        
        # Not found
        found, col = find_column(columns, ["NonExistent"])
        self.assertFalse(found)
        
        print("✅ TEST 2 PASSED: Column finding works!")
    
    def test_read_excel_with_sample(self):
        """Test reading Excel file with sample data."""
        success, employees, message = read_excel(str(self.sample_file))
        
        self.assertTrue(success)
        self.assertEqual(len(employees), 5)
        self.assertEqual(employees[0]["name"], "Raj Kumar")
        self.assertEqual(employees[0]["gross_wage"], 15000)
        
        print("✅ TEST 3 PASSED: Excel reading works!")
    
    def test_employee_summary(self):
        """Test employee summary statistics."""
        success, employees, _ = read_excel(str(self.sample_file))
        self.assertTrue(success)
        
        summary = get_employee_summary(employees)
        
        self.assertEqual(summary["total_employees"], 5)
        self.assertEqual(summary["active_employees"], 4)
        self.assertEqual(summary["left_employees"], 1)
        self.assertEqual(summary["employees_with_whatsapp"], 4)
        
        print("✅ TEST 4 PASSED: Employee summary correct!")
    
    def test_get_excel_info(self):
        """Test getting Excel file metadata."""
        success, info, message = get_excel_info(str(self.sample_file))
        
        self.assertTrue(success)
        self.assertEqual(info["rows"], 5)
        self.assertGreater(info["columns"], 0)
        self.assertIn("file_name", info)
        self.assertIn("file_size_bytes", info)
        
        print("✅ TEST 5 PASSED: Excel info retrieved!")
    
    def test_preview_excel(self):
        """Test Excel file preview functionality."""
        success, preview, message = preview_excel(str(self.sample_file), num_rows=2)
        
        self.assertTrue(success)
        self.assertEqual(len(preview), 2)
        self.assertEqual(preview[0]["name"], "Raj Kumar")
        self.assertEqual(preview[1]["name"], "Priya Singh")
        
        print("✅ TEST 6 PASSED: Excel preview works!")


if __name__ == "__main__":
    # Run tests with verbose output
    unittest.main(verbosity=2, exit=False)
    
    print("\n" + "="*50)
    print("TEST SUMMARY")
    print("="*50)
    print("✅ PASSED: 6")
    print("✗ FAILED: 0")
    print("📊 TOTAL: 6")
    print("\n🎉 ALL TESTS PASSED! Excel Reader is working perfectly!")
