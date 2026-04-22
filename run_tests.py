#!/usr/bin/env python3
"""Test runner for validators."""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import unittest
from tests.test_validators import TestValidators

if __name__ == "__main__":
    # Create a test suite
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestValidators)
    
    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "="*60)
    print("TEST SUMMARY - DATA VALIDATORS")
    print("="*60)
    print(f"✅ PASSED: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"✗ FAILED: {len(result.failures) + len(result.errors)}")
    print(f"📊 TOTAL: {result.testsRun}")
    
    if result.wasSuccessful():
        print("\n🎉 ALL TESTS PASSED! Data Validators are working perfectly!")
    else:
        print(f"\n❌ Some tests failed!")
        sys.exit(1)
