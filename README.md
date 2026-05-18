# PaySlip Generator & WhatsApp Delivery System

A standalone desktop application that automates payslip generation and WhatsApp delivery for **Holistic Allied Services** — an Indian facility management and security company with 500+ employees across 18+ locations.

Reads payroll data from Excel, validates and cleans it, generates professional branded PDF payslips, sorts them by office location, and delivers them to employees via WhatsApp.

---

## Features

- **Excel Payroll Processing** — Reads Excel files with 29+ salary fields, auto-detects header rows, handles inconsistent column names and messy formatting
- **Data Validation** — Indian phone number format (10-digit, 6-9 first digit), salary calculation verification (Net = Gross - Deductions), EPF/ESI compliance checks
- **Data Cleaning** — Normalizes phone numbers, converts currency strings to numbers, standardizes dates to DD/MM/YYYY, fills missing values with smart defaults
- **PDF Payslip Generation** — Professional branded payslips with company logo, earnings/deductions breakdown, net salary — matching the client's existing template format
- **Location-Based Sorting** — Generated PDFs are automatically organized into folders by office location (Bangalore, Lucknow, Amritsar, etc.)
- **WhatsApp Delivery** — Sends payslip notifications via Twilio WhatsApp API with rate limiting, retry logic with exponential backoff, and delivery tracking
- **Desktop GUI** — Simple Tkinter interface with file browser, data preview table, progress bar, and execution log — designed for non-technical payroll staff
- **IST Timezone Logging** — All timestamps in Indian Standard Time with daily rotating log files

## Performance

| Metric | Value |
|--------|-------|
| Employees processed | 502 |
| PDF generation time | ~45 seconds |
| Speed | ~12 PDFs/second |
| Test suite | 124 tests, 100% passing |

---

## Quick Start

### Prerequisites

- Python 3.8+
- macOS, Windows, or Linux
- [Homebrew](https://brew.sh) (macOS only — for system dependencies)

### Installation

**1. Clone the repository**

```bash
git clone https://github.com/nakshsingh00/WhatsApp-Payslip-Delivery.git
cd WhatsApp-Payslip-Delivery
git checkout development
```

**2. Run the setup script**

macOS / Linux:
```bash
bash setup.sh
```

Windows:
```
setup.bat
```

This installs all dependencies (Pango, pandas, WeasyPrint, Twilio, etc.) and creates the `.env` configuration file.

**3. Launch the application**

```bash
python3 run.py
```

> **Note (macOS):** If WeasyPrint gives a library error, run:
> ```bash
> export DYLD_LIBRARY_PATH="/opt/homebrew/lib"
> python3 run.py
> ```

---

## Usage

### Step 1: Load Excel File

Click **Browse** in Tab 1 and select your payroll Excel file. The tool auto-detects the header row and maps columns to the 29 standard payroll fields.

Supported column names include variations like:
- `"Emp ID"`, `"Employee ID"`, `"Employee Code"`
- `"Minimum Wages"`, `"Min Wages"`, `"MW"`
- `"E.P.F @ 13% on Minimum Wages"`, `"EPF 13%"`, `"EPF Employee"`
- `"Whatsapp Nmbr"`, `"WhatsApp Contact"`, `"Mobile"`

### Step 2: Select Pay Period

Pick the **Month** and **Year** from the dropdown menus. Both the payslip title ("MARCH, 2026") and employee info ("Mar-26") are generated automatically.

### Step 3: Validate & Generate

- Click **Validate Data** — runs all validators and cleans the data
- Switch to **Tab 2** → Click **Generate All Payslips**
- PDFs are saved to `data/generated_payslips/`, sorted into location folders:

```
data/generated_payslips/
├── Amritsar/          (38 payslips)
├── Bangalore/         (48 payslips)
├── Lucknow/           (76 payslips)
├── GBKM/              (55 payslips)
├── Noida/             (46 payslips)
├── Coimbatore/        (37 payslips)
├── ...
└── (18 location folders total)
```

### Step 4: Send via WhatsApp (Optional)

Requires a Twilio account. Edit `.env` with your credentials:

```
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token_here
WHATSAPP_BUSINESS_NUMBER=+14155238886
```

Then use **Tab 3** → **Test Connection** → **Send All via WhatsApp**.

---

## Project Structure

```
WhatsApp-Payslip-Delivery/
│
├── src/                              # Source modules
│   ├── excel_reader.py               # Excel processing with flexible column mapping
│   ├── validators.py                 # Phone, salary, deduction validation
│   ├── cleaners.py                   # Data normalization and cleaning
│   ├── template_generator.py         # Jinja2 HTML payslip rendering
│   ├── pdf_generator.py              # WeasyPrint PDF conversion + batch processing
│   ├── whatsapp_sender.py            # Twilio WhatsApp API integration
│   ├── gui.py                        # Tkinter desktop application
│   └── logger.py                     # IST timezone logging
│
├── tests/                            # Test suite (124 tests)
│   ├── test_excel_reader.py          # 6 tests
│   ├── test_validators.py            # 26 tests
│   ├── test_cleaners.py              # 26 tests
│   ├── test_template_generator.py    # 17 tests
│   ├── test_pdf_generator.py         # 16 tests
│   ├── test_gui.py                   # 10 tests
│   ├── test_whatsapp_sender.py       # 10 tests
│   └── test_integration.py           # 13 integration + error tests
│
├── templates/                        # Payslip template files
│   ├── payslip_template.html         # Jinja2 HTML template
│   ├── styles.css                    # Print-ready A4 stylesheet
│   └── logo.jpg                      # Company logo
│
├── data/                             # Data directories
│   ├── sample/                       # Test Excel files
│   ├── generated_payslips/           # Output PDFs (sorted by location)
│   ├── archived_payslips/            # Auto-archived old PDFs
│   ├── reports/                      # WhatsApp delivery reports (JSON)
│   └── logs/                         # Application logs
│
├── run.py                            # Application launcher
├── setup.sh                          # Mac/Linux setup script
├── setup.bat                         # Windows setup script
├── requirements.txt                  # Python dependencies
├── .env                              # Twilio credentials (not committed)
└── .gitignore                        # Git ignore rules
```

---

## Tech Stack

| Category | Technology | Purpose |
|----------|-----------|---------|
| Language | Python 3.8+ | Core application |
| GUI | Tkinter | Desktop user interface |
| Data Processing | pandas, openpyxl | Excel reading and data manipulation |
| Templating | Jinja2 | HTML payslip template rendering |
| PDF Generation | WeasyPrint | HTML/CSS to PDF conversion |
| WhatsApp | Twilio API | WhatsApp Business message delivery |
| Configuration | python-dotenv | Environment variable management |
| Version Control | Git + GitHub | Feature branch workflow |

---

## Architecture

```
┌─────────────┐    ┌──────────────┐    ┌───────────┐    ┌───────────────────┐    ┌───────────────┐    ┌──────────────────┐
│ Excel File  │───>│ Excel Reader │───>│ Validators │───>│ Cleaners          │───>│ Template      │───>│ PDF Generator    │
│ (.xlsx)     │    │ (29 fields)  │    │ (phone,    │    │ (normalize,       │    │ Generator     │    │ (WeasyPrint)     │
│             │    │              │    │  salary,   │    │  convert,         │    │ (Jinja2 HTML) │    │                  │
│             │    │              │    │  deductions)│   │  standardize)     │    │               │    │                  │
└─────────────┘    └──────────────┘    └──────────────┘  └───────────────────┘    └───────────────┘    └────────┬─────────┘
                                                                                                               │
                                                                                                               ▼
                   ┌──────────────────────────────────────────────────────────────────────────────┐    ┌──────────────────┐
                   │                         Desktop GUI (Tkinter)                                │    │ WhatsApp Sender  │
                   │  Tab 1: Load & Preview  │  Tab 2: Generate  │  Tab 3: WhatsApp  │  Tab 4: Log│<──│ (Twilio API)     │
                   └──────────────────────────────────────────────────────────────────────────────┘    └──────────────────┘
```

---

## Module Details

### Excel Reader (`excel_reader.py`)
- **Flexible column mapping**: 29 payroll fields, each with multiple possible column name variations
- **Auto header detection**: Scans first 10 rows for known column names when the default header row contains "Unnamed" columns
- **Whitespace normalization**: Handles wrapped Excel headers with newlines
- **Substring matching**: Falls back to partial name matching for long column headers like `"E.P.F @ 13% on Minimum Wages"`

### Validators (`validators.py`)
- Indian phone number validation (10-digit, first digit 6-9)
- Salary calculation verification (Net = Gross - Deductions with configurable tolerance)
- EPF deduction compliance (~13% of minimum wages)
- ESI deduction compliance (~3.25% of gross wage)
- Employee status validation (Active, Left, Suspended, etc.)
- Batch validation with summary report generation

### Cleaners (`cleaners.py`)
- Phone normalization: strips country codes (+91), spaces, dashes, handles Excel float format
- Currency conversion: `"₹15,000"` / `"1,50,000"` / `None` → clean Python float
- Date standardization: handles 12+ date formats including `1-Sep-25`, `2026-04-22`, `22/04/2026`, `10/13/77`
- Missing value handling: smart defaults per field type (text→"", currency→0.0, status→"Active")

### PDF Generator (`pdf_generator.py`)
- Single and batch PDF generation via WeasyPrint
- Location-based folder sorting (output organized by office location)
- Progress callbacks for GUI progress bar integration
- PDF quality verification (file exists, non-empty, valid PDF header)
- Auto-archival of old PDFs (configurable retention period)

### WhatsApp Sender (`whatsapp_sender.py`)
- Twilio API integration with credential management via `.env`
- Single message and batch delivery with configurable rate limiting (default: 2s between messages)
- Delivery status tracking (queued, sent, delivered, failed)
- Retry logic with exponential backoff (3 attempts)
- JSON delivery reports saved to `data/reports/`

### GUI (`gui.py`)
- 4-tab interface: Load & Preview, Generate PDFs, Send WhatsApp, Execution Log
- File browser with data preview table (first 10 rows)
- Month/Year dropdown pickers with live preview
- Background threading for batch operations (GUI stays responsive)
- Scrolling timestamped execution log
- Auto-generated delivery reports

---

## Excel File Format

The tool expects an Excel file with the following columns (column name variations are handled automatically):

### Employee Information
| Field | Example Column Names |
|-------|---------------------|
| Employee ID | `Emp ID`, `Employee ID`, `Employee Code` |
| Name | `Name`, `Employee Name` |
| Designation | `Designation`, `Job Title` |
| Department | `Department`, `Deparment` |
| Location | `Location`, `City` |
| Status | `Status`, `Employee Status` |
| Date of Joining | `Date of Joining`, `DOJ` |
| WhatsApp Number | `Whatsapp Nmbr`, `Mobile`, `WhatsApp Contact` |

### Earnings (INR)
| Field | Example Column Names |
|-------|---------------------|
| Minimum Wages | `Minimum Wages`, `Min Wages` |
| House Rent Allowance | `House Rent Allowance`, `HRA` |
| Special Allowance | `Special Allowance` |
| Extra Duty Allowance | `Extra Duty Allowance` |
| Travelling Allowance | `Travelling Allowance`, `Travelling Allownace` |
| Bonus | `Bonus @ 8.33% on Min. Wage`, `Bonus` |
| Leave with Wages | `Leave (with Wages) - 18 Days / Year` |
| Labour Welfare Fund | `Labour Welfare Fund` |
| Cost of Uniform | `Cost of uniform` |
| Gross Wage | `Gross Wage`, `Gross` |

### Deductions (INR)
| Field | Example Column Names |
|-------|---------------------|
| EPF 13% (Employee) | `E.P.F @ 13% on Minimum Wages`, `EPF 13%` |
| ESI 3.25% (Employee) | `E.S.I @ 3.25% on Gross Wage`, `ESI 3.25%` |
| Professional Tax | `Professional Tax`, `PT` |
| Total Deductions | `Total Deductions` |
| Net Take Home Pay | `Net Take Home Pay`, `Net Pay` |

---

## Payslip Output

Each generated payslip includes:
- Company logo and branding (Holistic Allied Services)
- Employee information (name, designation, department, date of joining)
- Earnings breakdown (Basic Salary, HRA, Special Allowance, Extra Duty, Travelling, Bonus)
- Deductions breakdown (PF Employee, ESI Employee, Labour Welfare Fund, Professional Tax)
- Total Earnings, Total Deductions, and Net Salary
- Pay period and generation timestamp

---

## Testing

Run the full test suite:

```bash
python3 -m unittest discover tests/ -v
```

| Test File | Tests | Coverage |
|-----------|-------|----------|
| `test_excel_reader.py` | 6 | Column mapping, file reading, previews |
| `test_validators.py` | 26 | Phone, salary, deductions, status, batch reports |
| `test_cleaners.py` | 26 | Phone normalization, currency, dates, missing values |
| `test_template_generator.py` | 17 | HTML rendering, dot notation, file output |
| `test_pdf_generator.py` | 16 | PDF generation, batch, verification, archival |
| `test_gui.py` | 10 | Window init, state management, UI components |
| `test_whatsapp_sender.py` | 10 | Connection, send, batch, reports |
| `test_integration.py` | 13 | Full pipeline, error scenarios, edge cases |
| **Total** | **124** | **All passing** |

---

## Configuration

### Environment Variables (`.env`)

```bash
# Twilio WhatsApp (optional — only needed for WhatsApp delivery)
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token_here
WHATSAPP_BUSINESS_NUMBER=+14155238886

# Company Information
COMPANY_NAME=Holistic Allied Services
COMPANY_ADDRESS=Facility Management & Security

# Processing Settings
LOG_LEVEL=INFO
MESSAGE_DELAY_SECONDS=2
PAYSLIP_RETENTION_DAYS=90
```

> The `.env` file is in `.gitignore` and is never committed to the repository.

---

## Indian Localization

This tool is built specifically for Indian payroll:
- **Phone numbers**: 10-digit Indian mobile format (first digit 6-9)
- **Currency**: Indian Rupees (INR) with comma formatting
- **Dates**: DD/MM/YYYY format
- **Timezone**: IST (Indian Standard Time) for all logs and timestamps
- **Deductions**: EPF @ 13%, ESI @ 3.25%, Professional Tax — standard Indian compliance rates
- **Scale**: Tested with 500+ employees across 18 Indian cities

---

## License

This project was built for Holistic Allied Services. All rights reserved.

---

## Author

Built by [Naksh Singh](https://github.com/nakshsingh00)
