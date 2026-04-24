#!/usr/bin/env python3
"""
PaySlip Generator & WhatsApp Sender
Holistic Allied Services

Double-click this file or run: python3 run.py
"""

import os
import sys

# Set library path for WeasyPrint on macOS
if sys.platform == "darwin":
    os.environ.setdefault("DYLD_LIBRARY_PATH", "/opt/homebrew/lib")

# Make sure we can import from src/
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Change to project directory so relative paths work
os.chdir(os.path.dirname(os.path.abspath(__file__)))

from src.gui import run_app

if __name__ == "__main__":
    run_app()
