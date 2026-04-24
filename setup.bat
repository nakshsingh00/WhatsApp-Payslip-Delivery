@echo off
REM ============================================
REM PaySlip Generator — Windows Setup Script
REM Holistic Allied Services
REM ============================================
REM Run this once on a new machine: setup.bat

echo ============================================
echo   PaySlip Generator — Setup
echo   Holistic Allied Services
echo ============================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed.
    echo Install it from: https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation.
    pause
    exit /b 1
)
echo ✓ Python found

REM Install Python packages
echo.
echo Installing Python packages...
pip install pandas openpyxl jinja2 weasyprint twilio python-dotenv

REM Create .env from template if it doesn't exist
if not exist .env (
    echo.
    echo Creating .env file...
    (
        echo # Twilio WhatsApp Configuration
        echo TWILIO_ACCOUNT_SID=your_account_sid_here
        echo TWILIO_AUTH_TOKEN=your_auth_token_here
        echo WHATSAPP_BUSINESS_NUMBER=+14155238886
        echo.
        echo # Company Information
        echo COMPANY_NAME=Holistic Allied Services
        echo COMPANY_ADDRESS=Facility Management ^& Security
        echo.
        echo # Processing Settings
        echo LOG_LEVEL=INFO
        echo MESSAGE_DELAY_SECONDS=2
        echo PAYSLIP_RETENTION_DAYS=90
    ) > .env
    echo ✓ .env created — edit it with your Twilio credentials
) else (
    echo ✓ .env already exists
)

REM Create data directories
if not exist data\logs mkdir data\logs
if not exist data\sample mkdir data\sample
if not exist data\generated_payslips mkdir data\generated_payslips
if not exist data\archived_payslips mkdir data\archived_payslips
if not exist data\reports mkdir data\reports

echo.
echo ============================================
echo   Setup complete!
echo.
echo   To run the app:  python run.py
echo ============================================
pause
