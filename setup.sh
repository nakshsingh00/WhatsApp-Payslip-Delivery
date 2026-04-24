#!/bin/bash
# ============================================
# PaySlip Generator — Mac/Linux Setup Script
# Holistic Allied Services
# ============================================
# Run this once on a new machine:  bash setup.sh

set -e

echo "============================================"
echo "  PaySlip Generator — Setup"
echo "  Holistic Allied Services"
echo "============================================"
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed."
    echo "Install it from: https://www.python.org/downloads/"
    exit 1
fi
echo "✓ Python 3 found: $(python3 --version)"

# Install Homebrew dependencies (macOS only)
if [[ "$OSTYPE" == "darwin"* ]]; then
    if command -v brew &> /dev/null; then
        echo ""
        echo "Installing system dependencies (Pango for PDF generation)..."
        brew install pango 2>/dev/null || echo "✓ Pango already installed"
    else
        echo ""
        echo "WARNING: Homebrew not found. Install it from https://brew.sh"
        echo "Then run: brew install pango"
    fi
fi

# Install Python packages
echo ""
echo "Installing Python packages..."
pip3 install pandas openpyxl jinja2 weasyprint twilio python-dotenv

# Create .env from template if it doesn't exist
if [ ! -f .env ]; then
    echo ""
    echo "Creating .env file from template..."
    cat > .env << 'ENVEOF'
# Twilio WhatsApp Configuration
TWILIO_ACCOUNT_SID=your_account_sid_here
TWILIO_AUTH_TOKEN=your_auth_token_here
WHATSAPP_BUSINESS_NUMBER=+14155238886

# Company Information
COMPANY_NAME=Holistic Allied Services
COMPANY_ADDRESS=Facility Management & Security

# Processing Settings
LOG_LEVEL=INFO
MESSAGE_DELAY_SECONDS=2
PAYSLIP_RETENTION_DAYS=90
ENVEOF
    echo "✓ .env created — edit it with your Twilio credentials"
else
    echo "✓ .env already exists"
fi

# Create data directories
mkdir -p data/logs data/sample data/generated_payslips data/archived_payslips data/reports

echo ""
echo "============================================"
echo "  Setup complete!"
echo ""
echo "  To run the app:  python3 run.py"
echo "============================================"
