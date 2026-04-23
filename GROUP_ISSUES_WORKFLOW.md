# Group Issues Workflow

## Project: PaySlip Generation & WhatsApp Delivery Utility
**Company**: Holistic Allied Services  
**Last Updated**: April 22, 2026

This document shows all issues organized into logical groups, in the order they should be completed. Each group builds on the previous — do not start a group until all issues in the prior group are done.

---

## Group 1: Foundation Setup
**Status**: ✅ Complete | **Issues**: #1–4 | **Total Time**: 5h

These four issues establish the entire foundation before any real code is written. They must be done first.

| # | Issue | Status | Time |
|---|-------|--------|------|
| 1 | Project Structure & Environment Setup | ✅ Done | 2h |
| 2 | Logging System | ✅ Done | 1.5h |
| 3 | Configuration Management | ✅ Done | 1h |
| 4 | Git Workflow & Documentation | ✅ Done | 0.5h |

**Group Output**: Working project skeleton, logging, config system, Git connected to GitHub.

---

## Group 2: Excel Data Processing
**Status**: ✅ Complete | **Issues**: #5–6 | **Total Time**: 7h

Reads and validates the raw payroll Excel data. These two issues together form the data intake layer.

| # | Issue | Status | Time |
|---|-------|--------|------|
| 5 | Excel Reader Module | ✅ Done | 4h |
| 6 | Data Validation Module | ✅ Done | 3h |

**Group Output**: `excel_reader.py` (7 functions), `validators.py` (7 functions), 32 tests all passing.

---

## Group 3: Data Pipeline
**Status**: 🔄 In Progress | **Issues**: #7–8 | **Total Time**: 6h

Cleans and prepares the validated data, then builds the payslip template that will be filled with employee data.

| # | Issue | Status | Time |
|---|-------|--------|------|
| 7 | Data Cleaning Module | 🔄 Next | 2h |
| 8 | HTML PaySlip Template | ⏳ Planned | 4h |

**Group Output**: `cleaners.py`, Jinja2 HTML template with Holistic Allied Services branding.

---

## Group 4: PDF Generation
**Status**: ⏳ Planned | **Issues**: #9–12 | **Total Time**: 6h

Converts the rendered HTML template to PDF files — one per employee — and manages storage and archival.

| # | Issue | Status | Time |
|---|-------|--------|------|
| 9 | PDF Generator — Single Payslip | ⏳ Planned | 2h |
| 10 | PDF Generator — Batch Processing | ⏳ Planned | 2h |
| 11 | PDF Quality Verification | ⏳ Planned | 1h |
| 12 | PDF Auto-Archival | ⏳ Planned | 1h |

**Group Output**: `pdf_generator.py`, batch PDF generation for 100–500 employees, auto-archival.

---

## Group 5: WhatsApp Delivery
**Status**: ⏳ Planned | **Issues**: #13–18 | **Total Time**: 8h

Delivers generated payslip PDFs to employees via WhatsApp using the Twilio API. Includes full reliability features.

| # | Issue | Status | Time |
|---|-------|--------|------|
| 13 | Twilio API Setup & Configuration | ⏳ Planned | 1h |
| 14 | Send Single WhatsApp Message | ⏳ Planned | 2h |
| 15 | Batch WhatsApp Delivery | ⏳ Planned | 2h |
| 16 | Delivery Status Tracking | ⏳ Planned | 1h |
| 17 | Retry Logic for Failed Deliveries | ⏳ Planned | 1h |
| 18 | Rate Limiting & Message Queue | ⏳ Planned | 1h |

**Group Output**: `whatsapp_sender.py`, full delivery pipeline with retry, tracking, and rate limiting.

---

## Group 6: Testing & Quality Assurance
**Status**: ⏳ Planned | **Issues**: #19–24 | **Total Time**: 6h

Validates the entire system works correctly under all conditions before deployment.

| # | Issue | Status | Time |
|---|-------|--------|------|
| 19 | Unit Tests — All Modules | ⏳ Planned | 1h |
| 20 | Integration Tests | ⏳ Planned | 1h |
| 21 | End-to-End Workflow Tests | ⏳ Planned | 1h |
| 22 | Load Testing (100+ Employees) | ⏳ Planned | 1h |
| 23 | Error Scenario Testing | ⏳ Planned | 1h |
| 24 | User Acceptance Testing | ⏳ Planned | 1h |

**Group Output**: Full test suite, load test results, UAT sign-off from Holistic Allied Services.

---

## Group 7: GUI & Deployment
**Status**: ⏳ Planned | **Issues**: #25–30 | **Total Time**: 9h

Wraps everything in a desktop GUI so non-technical staff can operate the tool, then packages it for handoff.

| # | Issue | Status | Time |
|---|-------|--------|------|
| 25 | User Acceptance Testing | ⏳ Planned | 1h |
| 26 | GUI Main Window (Tkinter) | ⏳ Planned | 2h |
| 27 | GUI File Selection & Data Preview | ⏳ Planned | 2h |
| 28 | GUI Progress Tracking & Status | ⏳ Planned | 1h |
| 29 | GUI Execution Log & Reports | ⏳ Planned | 1h |
| 30 | Deployment Preparation & Packaging | ⏳ Planned | 2h |

**Group Output**: `gui.py`, `run.py` launcher, setup scripts, deployable application package.

---

## Group 8: Advanced Features
**Status**: ⏳ Planned | **Issues**: #31–35 | **Total Time**: 9h

Adds reporting, history tracking, and optional API capabilities on top of the core tool. These are lower priority — the core tool is fully functional without them.

| # | Issue | Status | Time |
|---|-------|--------|------|
| 31 | Execution Report Generator | ⏳ Planned | 2h |
| 32 | Batch History & Run Log | ⏳ Planned | 1h |
| 33 | Employee Delivery Log | ⏳ Planned | 1h |
| 34 | Analytics Dashboard | ⏳ Planned | 2h |
| 35 | REST API Endpoints | ⏳ Planned | 3h |

**Group Output**: CSV/PDF delivery reports, batch run history, employee delivery log, analytics screen, optional API layer.

---

## Group 9: Maintenance & Support
**Status**: ⏳ Planned | **Issues**: #36–46 | **Total Time**: 8.5h

Covers all documentation, security review, and formal handover. The last group — completes when the tool is signed off by Holistic Allied Services.

| # | Issue | Status | Time |
|---|-------|--------|------|
| 36 | User Guide (Non-Technical) | ⏳ Planned | 2h |
| 37 | Technical Architecture Documentation | ⏳ Planned | 1h |
| 38 | Troubleshooting Guide & FAQ | ⏳ Planned | 1h |
| 39 | Configuration Reference Guide | ⏳ Planned | 1h |
| 40 | Performance Optimization | ⏳ Planned | 1h |
| 41 | Security Audit & Code Review | ⏳ Planned | 1h |
| 42 | Backup & Recovery Procedures | ⏳ Planned | 0.5h |
| 43 | Monthly Operation Checklist | ⏳ Planned | 0.5h |
| 44 | HR System Integration Notes | ⏳ Planned | 0.5h |
| 45 | Future Enhancement Roadmap | ⏳ Planned | 0.5h |
| 46 | Final Project Handover & Sign-off | ⏳ Planned | 1h |

**Group Output**: Complete documentation suite, security sign-off, accepted and delivered tool.

---

## Overall Progress

```
Group 1: Foundation         [██████████] ✅ 100% (5/5h)
Group 2: Excel Data         [██████████] ✅ 100% (7/7h)
Group 3: Data Pipeline      [░░░░░░░░░░] 🔄   0% (0/6h)  ← CURRENT
Group 4: PDF Generation     [░░░░░░░░░░] ⏳   0% (0/6h)
Group 5: WhatsApp Delivery  [░░░░░░░░░░] ⏳   0% (0/8h)
Group 6: Testing & QA       [░░░░░░░░░░] ⏳   0% (0/6h)
Group 7: GUI & Deployment   [░░░░░░░░░░] ⏳   0% (0/9h)
Group 8: Advanced Features  [░░░░░░░░░░] ⏳   0% (0/9h)
Group 9: Maintenance        [░░░░░░░░░░] ⏳   0% (0/8.5h)

TOTAL: 12/65 hours (18%) complete  |  46 issues total  |  6 done, 40 remaining
```

---

## Completion Order Rules

1. **Never start a group before the prior group is fully done.** Each group's code depends on the previous group's output.
2. **Within a group, issues should be done in number order.** They are sequenced deliberately.
3. **Exception**: Group 8 (Advanced Features) and Group 9 (Maintenance) can be worked on in parallel once Group 7 is complete.
4. **Group 8 is optional for initial delivery** — the tool is fully functional after Group 7. Group 8 adds reporting and analytics on top.
5. **WhatsApp numbers**: The user will add WhatsApp contact numbers to the Excel file before Group 5 begins. No action required before then.
6. **Twilio credentials**: Will be needed before Group 5 begins. Instructions are in `.env.example`.
