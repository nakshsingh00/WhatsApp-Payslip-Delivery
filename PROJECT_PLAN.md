# PaySlip Generation & WhatsApp Delivery Utility
## Complete Project Plan

**Client**: Holistic Allied Services  
**Version**: 3.0  
**Last Updated**: April 22, 2026  

---

## Project Overview

Build a standalone desktop utility that automates payslip generation and WhatsApp delivery for Holistic Allied Services. The tool reads employee payroll data from an Excel file, validates and cleans the data, generates professional PDF payslips, and sends them to employees via WhatsApp — all triggered manually by the payroll administrator through a simple desktop GUI.

**Technology**: Python 3.8+  
**Deployment**: Local-only, no cloud infrastructure  
**Platform**: Windows / Mac / Linux  
**Scale**: 100–500 employees per batch  
**Currency**: Indian Rupees (₹)  
**Timezone**: IST (Indian Standard Time)  

---

## Phase 1: Project Setup & Infrastructure

**Goal**: Establish the development foundation — environment, dependencies, configuration, and version control.  
**Status**: ✅ Complete

### 1.1 Project Structure & Environment
Create the project directory layout (`src/`, `tests/`, `data/`, `templates/`), initialize a Python virtual environment, and install all required packages via `requirements.txt`.

**Deliverables**: Directory structure, virtual environment, `.gitignore`, `requirements.txt`  
**Status**: ✅ Done

### 1.2 Logging System
Build a centralized logging module with IST timezone support, automatic daily log files (`payslip_YYYYMMDD.log`), and both file and console output at configurable log levels.

**Deliverables**: `src/logger.py`, `data/logs/` directory  
**Status**: ✅ Done

### 1.3 Configuration Management
Implement secure configuration management using `python-dotenv` so that Twilio credentials, company details, and processing settings are loaded from a `.env` file — never hardcoded in source code.

**Deliverables**: `src/config.py`, `.env.example` template  
**Status**: ✅ Done

### 1.4 Git Workflow & Version Control
Set up the Git branching strategy (`main` → `development` → `feature/task-name`), create base documentation, and push the project to GitHub.

**Deliverables**: `README.md`, `SETUP.md`, GitHub repository linked and active  
**Status**: ✅ Done

---

## Phase 2: Excel Data Processing

**Goal**: Read and extract payroll data from the Excel file reliably, regardless of minor column name variations.  
**Status**: ✅ Complete

### 2.1 Excel File Reading
Build the core Excel reading module using `pandas` and `openpyxl`. Implement a flexible 29-field column mapping system that finds columns by matching multiple possible name variations (case-insensitive), so the tool works even if the payroll file uses slightly different headers.

**Deliverables**: `src/excel_reader.py` (7 functions, 290 lines)  
**Status**: ✅ Done

### 2.2 Employee Data Extraction
Extract each employee's row into a structured dictionary containing all 29 payroll fields: employee info, earnings components, deduction components, net pay, WhatsApp contact, and remarks.

**Deliverables**: Structured employee dictionaries, `get_employee_summary()` function  
**Status**: ✅ Done

### 2.3 File Metadata & Preview
Provide utility functions to inspect an Excel file before processing — file name, size, row count, column list — and preview the first N rows to help the user confirm they've loaded the correct file.

**Deliverables**: `get_excel_info()`, `preview_excel()` functions  
**Status**: ✅ Done

---

## Phase 3: Data Validation

**Goal**: Detect data quality issues in the payroll file before any payslips are generated, so errors are caught early.  
**Status**: ✅ Complete

### 3.1 Phone Number Validation
Validate WhatsApp contact numbers against Indian mobile format: 10 digits, first digit must be 6–9. Handle common variations (spaces, dashes, country code prefix) and normalize to the standard format.

**Deliverables**: `validate_phone_number()` function  
**Status**: ✅ Done

### 3.2 Salary Calculation Verification
Verify that each employee's numbers are internally consistent: Net Take Home = Gross Wage − Total Deductions, within a configurable rounding tolerance. Flag any records where the math does not add up.

**Deliverables**: `validate_salary_calculation()` function  
**Status**: ✅ Done

### 3.3 Deduction Compliance Checks
Validate that EPF and ESI deductions fall within the expected legal percentages (EPF ≈ 13% of minimum wages, ESI ≈ 3.25% of gross). Flag records where deductions are outside the acceptable tolerance.

**Deliverables**: `validate_deductions()` function  
**Status**: ✅ Done

### 3.4 Complete Record & Batch Reporting
Validate every field in an employee record in one call, combining all individual validators. Process an entire batch and return a summary report with total valid/invalid counts and per-employee error details.

**Deliverables**: `validate_employee_data()`, `generate_validation_report()`, `check_for_salary_holds()` functions  
**Status**: ✅ Done

---

## Phase 4: Data Cleaning & Normalization

**Goal**: Standardize all data into consistent formats so the payslip template receives clean, uniform inputs.  
**Status**: 🔄 In Progress (Next)

### 4.1 Phone Number Normalization
Convert phone numbers to a consistent 10-digit format, stripping country codes, spaces, dashes, and parentheses. Output is always a plain 10-digit string ready for Twilio.

**Deliverables**: `normalize_phone()` function in `src/cleaners.py`

### 4.2 Currency Value Conversion
Convert salary and deduction values from raw Excel types (strings with commas, floats with extra precision, None) to clean Python floats. Handle Indian number formatting (e.g., "1,50,000" → 150000.0).

**Deliverables**: `convert_currency()` function

### 4.3 Date Standardization
Ensure all date fields (Date of Joining, Date of Leaving) are in DD/MM/YYYY string format for consistent display on payslips. Handle Excel date objects, string dates, and blank cells.

**Deliverables**: `standardize_dates()` function

### 4.4 Missing Value Handling
Replace `None` and blank values with appropriate defaults per field type — empty string for text fields, 0.0 for numeric fields, "Active" for missing status. Preserve the remarks field exactly as written.

**Deliverables**: `handle_missing_values()` function, `preserve_remarks()` function

---

## Phase 5: HTML PaySlip Template

**Goal**: Design a professional, print-ready payslip layout matching Holistic Allied Services' branding.  
**Status**: ⏳ Planned

### 5.1 Template Design & Structure
Build the HTML payslip layout with clearly separated sections: company header (logo, name, address), employee information block, pay period, earnings table, deductions table, and net pay summary.

**Deliverables**: `templates/payslip_template.html` (Jinja2 template)

### 5.2 Stylesheet & Branding
Write CSS to match Holistic Allied Services' visual identity — correct fonts, colors, table styling, and borders. Include print-specific styles so the payslip fits cleanly on A4 paper with proper margins.

**Deliverables**: `templates/styles.css`

### 5.3 Data Binding & Test Render
Wire all template variables to the cleaned employee data dictionary using Jinja2. Render a test payslip with real employee data and verify all values display correctly, including Indian Rupee (₹) formatting.

**Deliverables**: `src/template_generator.py`, verified sample render

---

## Phase 6: PDF Generation

**Goal**: Convert rendered HTML payslips to professional PDF files, one per employee, with batch support.  
**Status**: ⏳ Planned

### 6.1 Single Payslip PDF
Implement the core PDF generator using WeasyPrint to convert Jinja2-rendered HTML to a PDF file. Handle font embedding, page size (A4), and output file naming (`EMP_ID_Name_Month.pdf`).

**Deliverables**: `generate_pdf()` function in `src/pdf_generator.py`

### 6.2 Batch PDF Generation
Extend the generator to process all employees in a list, generating one PDF per employee with progress tracking. Handle individual employee failures gracefully — log the error and continue the batch.

**Deliverables**: `batch_generate_pdfs()` function with progress callback

### 6.3 PDF Verification
After generation, verify each PDF is valid: non-empty file, readable, correct page count. Log any corrupt or missing outputs so they can be regenerated before sending.

**Deliverables**: `verify_pdfs()` function

### 6.4 PDF Auto-Archival
Move generated PDFs older than 90 days (configurable via `.env`) from the active output folder to the archive folder. Prevents indefinite disk usage growth.

**Deliverables**: `archive_pdfs()` function, configurable `PAYSLIP_RETENTION_DAYS` setting

---

## Phase 7: WhatsApp Integration

**Goal**: Deliver payslip PDFs to employees via WhatsApp using the Twilio API reliably and at scale.  
**Status**: ⏳ Planned

### 7.1 Twilio API Setup
Configure the Twilio client with credentials from `.env`, verify the WhatsApp Business number is active, and test the API connection before any batch delivery begins.

**Deliverables**: Twilio client initialization in `src/whatsapp_sender.py`, connection health check

### 7.2 Single Message Delivery
Implement `send_message()` to send one payslip PDF to one employee's WhatsApp number. Validates the phone number, attaches the PDF, sends via Twilio, and logs the result.

**Deliverables**: `send_message()` function

### 7.3 Batch Delivery with Rate Limiting
Process the full employee list sequentially with a configurable delay between messages (default: 2 seconds) to stay within Twilio's rate limits. Track sent/failed counts in real time.

**Deliverables**: `send_batch()` function, `rate_limit()` queue wrapper

### 7.4 Delivery Tracking & Retry
Capture delivery status per employee (sent, delivered, failed) from Twilio's API response. Automatically retry failed messages up to 3 times with exponential backoff. Write unresolved failures to a retry queue file.

**Deliverables**: `track_delivery()`, `retry_failed()` functions, `data/reports/retry_queue.json`

---

## Phase 8: Desktop GUI

**Goal**: Wrap all functionality in a simple Tkinter GUI so payroll staff can operate the tool without any technical knowledge.  
**Status**: ⏳ Planned

### 8.1 Main Application Window
Build the primary Tkinter window with a logical step-by-step layout: (1) Load Excel File, (2) Validate & Preview, (3) Generate Payslips, (4) Send via WhatsApp, (5) View Report. Include confirmation dialogs before any bulk action.

**Deliverables**: `src/gui.py` (main window and navigation flow)

### 8.2 File Selection & Data Preview
Add a file browser dialog for Excel selection followed by a scrollable table showing the first 10 rows. Display validation results inline — green checkmarks for valid rows, red warnings for issues.

**Deliverables**: File browser widget, data preview table

### 8.3 Progress & Execution Log
Show a progress bar and live status during PDF generation and WhatsApp sending ("Sending 45 of 125..."). Display a scrolling timestamped execution log so the user can see exactly what is happening.

**Deliverables**: Progress bar widget, scrolling log panel

### 8.4 Post-Run Report Viewer
After a batch completes, show a summary dialog (total sent, failed, cost estimate in ₹) and provide a button to open the saved CSV delivery report from `data/reports/`.

**Deliverables**: Summary dialog, report file link

---

## Phase 9: Testing & Quality Assurance

**Goal**: Verify the complete system is reliable, handles errors gracefully, and meets performance targets.  
**Status**: ⏳ Planned

### 9.1 Unit Test Coverage
Ensure every public function across all modules has unit tests covering the happy path and at least one error/edge case. Target: 100% function coverage.

**Deliverables**: Complete unit test suite across all `src/` modules

### 9.2 Integration Testing
Test the pipeline as an end-to-end chain: Excel read → validate → clean → render → generate PDF. Use a real test Excel file and verify the output PDF is correct.

**Deliverables**: `tests/test_integration.py`

### 9.3 End-to-End & Load Testing
Run the full workflow including Twilio sandbox delivery with a test batch of 5–10 employees. Separately, run a load test with 100–500 employees and verify performance — PDF generation speed, memory usage, send throughput.

**Deliverables**: E2E test script, load test results and performance report

### 9.4 Error Scenario Testing
Test all known failure modes: missing Excel file, corrupt data, invalid phone numbers, Twilio API unavailable, disk full. Confirm the tool exits cleanly and logs the failure in every case.

**Deliverables**: Error scenario test cases, confirmed graceful failure in all scenarios

---

## Phase 10: Deployment & Packaging

**Goal**: Package the tool so it can be handed to Holistic Allied Services and run on any Windows/Mac machine in minutes.  
**Status**: ⏳ Planned

### 10.1 Launcher & Setup Scripts
Create a one-click `run.py` launcher and platform-specific setup scripts (`setup.bat` for Windows, `setup.sh` for Mac/Linux) that install dependencies and create the `.env` from the template automatically.

**Deliverables**: `run.py`, `setup.bat`, `setup.sh`

### 10.2 User Acceptance Testing
Run the complete tool with real payroll data from Holistic Allied Services (or a realistic anonymized copy). Get sign-off from the payroll administrator that outputs are correct and the GUI is usable.

**Deliverables**: UAT session, final adjustments, sign-off

### 10.3 Deployment Checklist
Verify all pre-launch items: no credentials in code, `.env` template complete, logs working, tests passing, documentation done. Final checklist review before handover.

**Deliverables**: Completed deployment checklist, handover package

---

## Phase 11: Documentation

**Goal**: Produce complete documentation so the tool can be used, maintained, and supported without the original developer.  
**Status**: ⏳ Planned

### 11.1 User Guide
Step-by-step instructions for the payroll administrator: how to set up the tool, prepare the Excel file, run the tool, interpret results, and troubleshoot common issues. Written for non-technical users with screenshots.

**Deliverables**: `docs/USAGE.md`, annotated screenshots

### 11.2 Technical Documentation
Developer-facing documentation: architecture overview, module descriptions, API reference for all public functions, environment variable reference, and contribution guidelines.

**Deliverables**: `docs/ARCHITECTURE.md`, updated `README.md`

### 11.3 Troubleshooting Guide & FAQ
Covers the 15 most common errors users are likely to encounter, with exact error messages and step-by-step resolution for each. Includes FAQ section for recurring questions.

**Deliverables**: `docs/TROUBLESHOOTING.md`, `docs/FAQ.md`

---

## Phase 12: Maintenance & Future Roadmap

**Goal**: Define how the tool will be maintained and identify enhancement opportunities after initial delivery.  
**Status**: ⏳ Planned

### 12.1 Performance Optimization
Profile and optimize any bottlenecks identified during load testing — PDF generation parallelization, Excel parsing speed, WhatsApp send throughput.

**Deliverables**: Optimization report, any code improvements

### 12.2 Future Enhancement Roadmap
Document potential future enhancements for consideration: payslip email delivery option, analytics dashboard, HR system integration, automated scheduling, multi-company support.

**Deliverables**: `docs/ROADMAP.md` with prioritized enhancement list

### 12.3 Support & Handover
Final handover session with Holistic Allied Services: walkthrough of the tool, handover of credentials setup guide, explanation of how to update the tool for future months.

**Deliverables**: Handover session, credentials guide, monthly operation checklist

---

## Implementation Timeline

| Phase | Description | Hours | Priority | Status |
|-------|-------------|-------|----------|--------|
| 1 | Project Setup & Infrastructure | 5h | P0 | ✅ Done |
| 2 | Excel Data Processing | 4h | P0 | ✅ Done |
| 3 | Data Validation | 3h | P0 | ✅ Done |
| 4 | Data Cleaning & Normalization | 2h | P0 | 🔄 Next |
| 5 | HTML PaySlip Template | 4h | P0 | ⏳ Planned |
| 6 | PDF Generation | 6h | P0 | ⏳ Planned |
| 7 | WhatsApp Integration | 8h | P0 | ⏳ Planned |
| 8 | Desktop GUI | 6h | P0 | ⏳ Planned |
| 9 | Testing & Quality Assurance | 6h | P0 | ⏳ Planned |
| 10 | Deployment & Packaging | 4h | P0 | ⏳ Planned |
| 11 | Documentation | 3h | P1 | ⏳ Planned |
| 12 | Maintenance & Roadmap | 2h | P2 | ⏳ Planned |
| **Total** | | **53h** | | **23% Complete** |

**Hours Complete**: 12/53 (23%)  
**Hours Remaining**: 41/53 (77%)

---

## Technology Stack

| Category | Library | Version | Purpose |
|----------|---------|---------|---------|
| Data Processing | pandas | 1.3.0+ | Excel reading, data manipulation |
| Excel I/O | openpyxl | 3.0.0+ | Excel file handling |
| Templating | Jinja2 | 3.0.0+ | HTML template rendering |
| PDF | WeasyPrint | 54.0+ | HTML to PDF conversion |
| WhatsApp | twilio | 7.0.0+ | WhatsApp Business API |
| Config | python-dotenv | 0.19.0+ | Environment variable management |
| Timezone | pytz | latest | IST timezone support |
| Testing | pytest | 6.0.0+ | Test framework |
| GUI | tkinter | built-in | Desktop user interface |

---

## Project Structure

```
payslip-whatsapp-tool/
├── src/
│   ├── logger.py              ✅ Complete
│   ├── config.py              ✅ Complete
│   ├── excel_reader.py        ✅ Complete
│   ├── validators.py          ✅ Complete
│   ├── cleaners.py            🔄 Next
│   ├── template_generator.py  ⏳ Phase 5
│   ├── pdf_generator.py       ⏳ Phase 6
│   ├── whatsapp_sender.py     ⏳ Phase 7
│   ├── gui.py                 ⏳ Phase 8
│   └── main.py                ⏳ Phase 8
├── tests/
│   ├── test_excel_reader.py   ✅ 6 tests passing
│   ├── test_validators.py     ✅ 26 tests passing
│   ├── test_cleaners.py       🔄 Next
│   ├── test_integration.py    ⏳ Phase 9
│   └── test_pdf_generator.py  ⏳ Phase 6
├── templates/
│   ├── payslip_template.html  ⏳ Phase 5
│   └── styles.css             ⏳ Phase 5
├── data/
│   ├── logs/                  ✅ Active
│   ├── sample/
│   ├── generated_payslips/
│   ├── reports/
│   └── archived_payslips/
├── docs/
│   ├── USAGE.md               ⏳ Phase 11
│   ├── TROUBLESHOOTING.md     ⏳ Phase 11
│   └── ARCHITECTURE.md        ⏳ Phase 11
├── .env.example               ✅ Complete
├── .gitignore                 ✅ Complete
├── requirements.txt           ✅ Complete
├── run.py                     ⏳ Phase 10
└── README.md                  ✅ Complete
```

---

## Excel Payroll Data Structure

The tool reads Excel files with the following column structure (Holistic Allied Services format):

**Employee Information**: Sr No., Emp ID, Name, Designation, Department, Location, Gender, Date of Joining, Date of Leaving, Status, WhatsApp Contact

**Earnings (₹)**: Minimum Wages, House Rent Allowance, Special Allowance, Extra Duty Allowance, Travelling Allowance, Bonus @ 8.33%, Leave with Wages, Labour Welfare Fund, Cost of Uniform, Gross Wage, CTC

**Deductions (₹)**: EPF @ 13%, ESI @ 3.25%, EPF @ 12%, ESI @ 0.75%, Professional Tax, Total Deductions

**Net Pay**: Net Take Home Pay

**Notes**: Remarks

The column finder uses flexible matching so minor variations in column names (e.g., "House Rent" vs "HRA" vs "House Rent Allowance") are handled automatically.

---

## Success Criteria

- [ ] All 100–500 payslips generated correctly from a real Excel file
- [ ] All generated PDFs match the approved payslip design
- [ ] All WhatsApp messages delivered successfully (or logged for retry)
- [ ] Tool runs without errors on Windows and Mac
- [ ] Processing completes in under 10 minutes for 500 employees
- [ ] No employee salary data leaves the local machine (except via Twilio WhatsApp)
- [ ] No credentials hardcoded in source code
- [ ] All tests passing (target: 100%)
- [ ] Non-technical staff can operate the tool with the user guide only
- [ ] Payroll administrator has signed off on output accuracy

---

## Key Design Decisions

**Local-only deployment**: All data stays on the user's machine. No cloud storage, no remote servers beyond the Twilio API call. This protects employee salary data and eliminates ongoing infrastructure costs.

**Manual trigger model**: The payroll administrator explicitly clicks to start each step. No automated scheduling or background processes. This gives full control and prevents accidental sends.

**Flexible column mapping**: Excel column names in real payroll files are inconsistent. The tool matches columns by trying multiple possible names, so it works without modifying the Excel file each month.

**Twilio for WhatsApp**: Uses the official Twilio WhatsApp Business API rather than unofficial methods. This ensures reliability, compliance, and no account suspension risk.

**Indian localization**: All phone validation, currency formatting, date handling, and timezone displays are built for the Indian context — 10-digit mobile numbers starting 6–9, ₹ symbol, DD/MM/YYYY dates, IST timestamps.
