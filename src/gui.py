"""Desktop GUI for PaySlip WhatsApp Tool.

Provides a simple step-by-step interface for payroll staff:
  1. Load Excel File
  2. Preview & Validate
  3. Generate Payslips (PDF)
  4. Send via WhatsApp (coming soon)
  5. View Report

Built with Tkinter (Python's built-in GUI library — no install needed).

Key concept for beginners:
  The GUI runs an "event loop" — it sits and waits for you to click a button.
  When you click, it runs the associated function, then goes back to waiting.
  Heavy work (like generating 500 PDFs) runs in a background thread so the
  window doesn't freeze while it's working.
"""

import os
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
from src.logger import setup_logger

logger = setup_logger(__name__)


class PaySlipApp:
    """
    Main application window.

    This class creates the entire GUI and wires up all the buttons
    to the underlying functions (excel_reader, cleaners, pdf_generator, etc.)
    """

    def __init__(self, root: tk.Tk):
        """
        Initialize the application.

        Args:
            root: The main Tkinter window (created by tk.Tk())
        """
        self.root = root
        self.root.title("PaySlip Generator — Holistic Allied Services")
        self.root.geometry("900x700")
        self.root.minsize(800, 600)

        # --- Application state ---
        self.file_path: Optional[str] = None       # Path to loaded Excel file
        self.raw_employees: List[Dict] = []         # Raw data from Excel
        self.cleaned_employees: List[Dict] = []     # Cleaned data
        self.generated_files: List[str] = []        # Generated PDF paths
        self.pay_period: str = ""                    # e.g. "MARCH, 2026"
        self.pay_month: str = ""                     # e.g. "Mar-26"

        # --- Build the GUI ---
        self._create_menu()
        self._create_header()
        self._create_notebook()
        self._create_status_bar()

        logger.info("GUI initialized")

    # ================================================================
    # GUI CONSTRUCTION
    # ================================================================

    def _create_menu(self):
        """Create the top menu bar (File, Help)."""
        menubar = tk.Menu(self.root)

        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Load Excel File", command=self._load_file)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)

        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="About", command=self._show_about)
        menubar.add_cascade(label="Help", menu=help_menu)

        self.root.config(menu=menubar)

    def _create_header(self):
        """Create the app title header."""
        header = ttk.Frame(self.root, padding=10)
        header.pack(fill=tk.X)

        title = ttk.Label(
            header,
            text="PaySlip Generator & WhatsApp Sender",
            font=("Helvetica", 16, "bold")
        )
        title.pack(side=tk.LEFT)

        subtitle = ttk.Label(
            header,
            text="Holistic Allied Services",
            font=("Helvetica", 10),
            foreground="gray"
        )
        subtitle.pack(side=tk.RIGHT)

    def _create_notebook(self):
        """
        Create the tabbed interface (notebook).

        Each tab is one step in the workflow:
          Tab 1: Load & Preview
          Tab 2: Generate PDFs
          Tab 3: Send WhatsApp (placeholder)
          Tab 4: Execution Log
        """
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Tab 1: Load & Preview
        self.tab_load = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.tab_load, text="  1. Load & Preview  ")
        self._build_load_tab()

        # Tab 2: Generate PDFs
        self.tab_generate = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.tab_generate, text="  2. Generate PDFs  ")
        self._build_generate_tab()

        # Tab 3: Send WhatsApp
        self.tab_whatsapp = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.tab_whatsapp, text="  3. Send WhatsApp  ")
        self._build_whatsapp_tab()

        # Tab 4: Execution Log
        self.tab_log = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.tab_log, text="  4. Log  ")
        self._build_log_tab()

    def _create_status_bar(self):
        """Create the bottom status bar."""
        self.status_var = tk.StringVar(value="Ready — Load an Excel file to begin")
        status_bar = ttk.Label(
            self.root,
            textvariable=self.status_var,
            relief=tk.SUNKEN,
            anchor=tk.W,
            padding=5
        )
        status_bar.pack(fill=tk.X, side=tk.BOTTOM)

    # ================================================================
    # TAB 1: LOAD & PREVIEW
    # ================================================================

    def _build_load_tab(self):
        """Build the file loading and data preview tab."""

        # --- File selection row ---
        file_frame = ttk.LabelFrame(self.tab_load, text="Excel File", padding=10)
        file_frame.pack(fill=tk.X, pady=(0, 10))

        self.file_label = ttk.Label(file_frame, text="No file loaded")
        self.file_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

        ttk.Button(
            file_frame, text="Browse...", command=self._load_file
        ).pack(side=tk.RIGHT, padx=(10, 0))

        # --- Pay period row ---
        period_frame = ttk.LabelFrame(self.tab_load, text="Pay Period", padding=10)
        period_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(period_frame, text="Period (e.g. MARCH, 2026):").pack(side=tk.LEFT)
        self.period_entry = ttk.Entry(period_frame, width=25)
        self.period_entry.pack(side=tk.LEFT, padx=10)
        self.period_entry.insert(0, self._default_pay_period())

        ttk.Label(period_frame, text="Month (e.g. Mar-26):").pack(side=tk.LEFT, padx=(20, 0))
        self.month_entry = ttk.Entry(period_frame, width=15)
        self.month_entry.pack(side=tk.LEFT, padx=10)
        self.month_entry.insert(0, self._default_pay_month())

        # --- Info & validation summary ---
        info_frame = ttk.LabelFrame(self.tab_load, text="File Summary", padding=10)
        info_frame.pack(fill=tk.X, pady=(0, 10))

        self.info_text = tk.StringVar(value="Load a file to see summary")
        ttk.Label(info_frame, textvariable=self.info_text, wraplength=800).pack(anchor=tk.W)

        # --- Data preview table ---
        preview_frame = ttk.LabelFrame(self.tab_load, text="Data Preview (first 10 rows)", padding=5)
        preview_frame.pack(fill=tk.BOTH, expand=True)

        # Treeview = Tkinter's table widget
        columns = ("Emp ID", "Name", "Designation", "Gross", "Deductions", "Net Pay", "Phone", "Status")
        self.preview_tree = ttk.Treeview(
            preview_frame, columns=columns, show="headings", height=8
        )

        for col in columns:
            self.preview_tree.heading(col, text=col)
            width = 120 if col == "Name" else 90
            self.preview_tree.column(col, width=width, anchor=tk.W if col == "Name" else tk.E)

        # Scrollbar for the table
        scrollbar = ttk.Scrollbar(preview_frame, orient=tk.VERTICAL, command=self.preview_tree.yview)
        self.preview_tree.configure(yscrollcommand=scrollbar.set)

        self.preview_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # --- Validate button ---
        btn_frame = ttk.Frame(self.tab_load)
        btn_frame.pack(fill=tk.X, pady=5)

        ttk.Button(
            btn_frame, text="Validate Data", command=self._validate_data
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            btn_frame, text="Clear", command=self._clear_data
        ).pack(side=tk.RIGHT, padx=5)

    # ================================================================
    # TAB 2: GENERATE PDFs
    # ================================================================

    def _build_generate_tab(self):
        """Build the PDF generation tab."""

        # --- Output directory ---
        dir_frame = ttk.LabelFrame(self.tab_generate, text="Output Directory", padding=10)
        dir_frame.pack(fill=tk.X, pady=(0, 10))

        self.output_dir_var = tk.StringVar(value=str(Path("data/generated_payslips").absolute()))
        ttk.Label(dir_frame, textvariable=self.output_dir_var, wraplength=700).pack(side=tk.LEFT, fill=tk.X, expand=True)

        ttk.Button(
            dir_frame, text="Change...", command=self._choose_output_dir
        ).pack(side=tk.RIGHT, padx=(10, 0))

        # --- Generate controls ---
        gen_frame = ttk.LabelFrame(self.tab_generate, text="Generate", padding=10)
        gen_frame.pack(fill=tk.X, pady=(0, 10))

        self.gen_status = tk.StringVar(value="Load and validate data first")
        ttk.Label(gen_frame, textvariable=self.gen_status, font=("Helvetica", 11)).pack(anchor=tk.W, pady=(0, 10))

        # Progress bar
        self.progress_var = tk.DoubleVar(value=0)
        self.progress_bar = ttk.Progressbar(
            gen_frame, variable=self.progress_var, maximum=100, length=500
        )
        self.progress_bar.pack(fill=tk.X, pady=(0, 5))

        self.progress_label = tk.StringVar(value="")
        ttk.Label(gen_frame, textvariable=self.progress_label).pack(anchor=tk.W)

        # Buttons
        btn_frame = ttk.Frame(gen_frame)
        btn_frame.pack(fill=tk.X, pady=(10, 0))

        self.gen_button = ttk.Button(
            btn_frame, text="Generate All Payslips", command=self._generate_pdfs
        )
        self.gen_button.pack(side=tk.LEFT, padx=5)

        ttk.Button(
            btn_frame, text="Open Output Folder",
            command=lambda: self._open_folder(self.output_dir_var.get())
        ).pack(side=tk.LEFT, padx=5)

        # --- Results ---
        results_frame = ttk.LabelFrame(self.tab_generate, text="Results", padding=10)
        results_frame.pack(fill=tk.BOTH, expand=True)

        self.results_text = scrolledtext.ScrolledText(
            results_frame, height=10, font=("Courier", 10), state=tk.DISABLED
        )
        self.results_text.pack(fill=tk.BOTH, expand=True)

    # ================================================================
    # TAB 3: SEND WHATSAPP (placeholder)
    # ================================================================

    def _build_whatsapp_tab(self):
        """Build the WhatsApp delivery tab."""

        # --- Connection status ---
        conn_frame = ttk.LabelFrame(self.tab_whatsapp, text="Twilio Connection", padding=10)
        conn_frame.pack(fill=tk.X, pady=(0, 10))

        self.wa_conn_var = tk.StringVar(value="Not checked")
        ttk.Label(conn_frame, textvariable=self.wa_conn_var).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(conn_frame, text="Test Connection", command=self._test_whatsapp_connection).pack(side=tk.RIGHT)

        # --- Send controls ---
        send_frame = ttk.LabelFrame(self.tab_whatsapp, text="Send Payslips", padding=10)
        send_frame.pack(fill=tk.X, pady=(0, 10))

        self.wa_status = tk.StringVar(value="Generate PDFs first, then send via WhatsApp")
        ttk.Label(send_frame, textvariable=self.wa_status, font=("Helvetica", 11)).pack(anchor=tk.W, pady=(0, 10))

        # Progress bar
        self.wa_progress_var = tk.DoubleVar(value=0)
        self.wa_progress_bar = ttk.Progressbar(send_frame, variable=self.wa_progress_var, maximum=100)
        self.wa_progress_bar.pack(fill=tk.X, pady=(0, 5))

        self.wa_progress_label = tk.StringVar(value="")
        ttk.Label(send_frame, textvariable=self.wa_progress_label).pack(anchor=tk.W)

        btn_frame = ttk.Frame(send_frame)
        btn_frame.pack(fill=tk.X, pady=(10, 0))

        self.wa_send_button = ttk.Button(btn_frame, text="Send All via WhatsApp", command=self._send_whatsapp)
        self.wa_send_button.pack(side=tk.LEFT, padx=5)

        # --- Delivery results ---
        wa_results_frame = ttk.LabelFrame(self.tab_whatsapp, text="Delivery Results", padding=10)
        wa_results_frame.pack(fill=tk.BOTH, expand=True)

        self.wa_results_text = scrolledtext.ScrolledText(wa_results_frame, height=10, font=("Courier", 10), state=tk.DISABLED)
        self.wa_results_text.pack(fill=tk.BOTH, expand=True)

    # ================================================================
    # TAB 4: EXECUTION LOG
    # ================================================================

    def _build_log_tab(self):
        """Build the scrolling execution log tab."""
        self.log_text = scrolledtext.ScrolledText(
            self.tab_log, font=("Courier", 10), state=tk.DISABLED
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)

        btn_frame = ttk.Frame(self.tab_log)
        btn_frame.pack(fill=tk.X, pady=5)

        ttk.Button(
            btn_frame, text="Clear Log", command=self._clear_log
        ).pack(side=tk.RIGHT, padx=5)

    # ================================================================
    # ACTIONS
    # ================================================================

    def _load_file(self):
        """Open file dialog and load an Excel file."""
        path = filedialog.askopenfilename(
            title="Select Payroll Excel File",
            filetypes=[
                ("Excel files", "*.xlsx *.xls"),
                ("All files", "*.*")
            ]
        )

        if not path:
            return  # User cancelled

        self.file_path = path
        self.file_label.config(text=path)
        self._set_status(f"Loading: {os.path.basename(path)}...")
        self._log(f"Loading file: {path}")

        try:
            from src.excel_reader import read_excel, get_employee_summary

            success, employees, message = read_excel(path)

            if not success:
                messagebox.showerror("Error", f"Failed to load file:\n{message}")
                self._log(f"ERROR: {message}")
                self._set_status("File load failed")
                return

            self.raw_employees = employees

            # Show summary
            summary = get_employee_summary(employees)
            total = summary.get("total_employees", 0)
            active = summary.get("active_employees", 0)
            whatsapp = summary.get("with_whatsapp", 0)

            self.info_text.set(
                f"Total employees: {total}  |  Active: {active}  |  "
                f"With WhatsApp: {whatsapp}  |  File: {os.path.basename(path)}"
            )

            # Populate preview table
            self._populate_preview(employees[:10])

            self._log(f"Loaded {total} employees from {os.path.basename(path)}")
            self._set_status(f"Loaded {total} employees — validate data next")
            self.gen_status.set(f"{total} employees loaded — validate before generating")

            # Switch to load tab
            self.notebook.select(self.tab_load)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load file:\n{str(e)}")
            self._log(f"ERROR loading file: {e}")
            self._set_status("File load failed")

    def _populate_preview(self, employees: List[Dict]):
        """Fill the preview table with employee data."""
        # Clear existing rows
        for row in self.preview_tree.get_children():
            self.preview_tree.delete(row)

        for emp in employees:
            self.preview_tree.insert("", tk.END, values=(
                emp.get("emp_id", ""),
                emp.get("name", ""),
                emp.get("designation", ""),
                f"{emp.get('gross_wage', 0) or 0:,.0f}",
                f"{emp.get('total_deductions', 0) or 0:,.0f}",
                f"{emp.get('net_take_home_pay', 0) or 0:,.0f}",
                emp.get("whatsapp_contact", ""),
                emp.get("status", "")
            ))

    def _validate_data(self):
        """Run validation on loaded employee data."""
        if not self.raw_employees:
            messagebox.showwarning("No Data", "Load an Excel file first.")
            return

        self._log("Running data validation...")
        self._set_status("Validating data...")

        try:
            from src.validators import generate_validation_report
            from src.cleaners import clean_all_employees

            # Step 1: Validate raw data
            report = generate_validation_report(self.raw_employees)
            total = report["total_employees"]
            valid = report["valid_employees"]
            invalid = report["invalid_employees"]

            self._log(f"Validation: {valid}/{total} valid, {invalid} with issues")

            if report["issues"]:
                for issue in report["issues"][:5]:  # Show first 5 issues
                    name = issue.get("name", "Unknown")
                    errors = ", ".join(issue.get("errors", []))
                    self._log(f"  Warning: {name} — {errors}")
                if len(report["issues"]) > 5:
                    self._log(f"  ... and {len(report['issues']) - 5} more issues")

            # Step 2: Clean data
            self.cleaned_employees = clean_all_employees(self.raw_employees)
            self._log(f"Data cleaned: {len(self.cleaned_employees)} employees ready")

            self.gen_status.set(
                f"{len(self.cleaned_employees)} employees validated and cleaned — ready to generate"
            )
            self._set_status(
                f"Validation complete: {valid}/{total} valid — "
                f"ready to generate PDFs"
            )

            messagebox.showinfo(
                "Validation Complete",
                f"Results:\n\n"
                f"Total employees: {total}\n"
                f"Valid: {valid}\n"
                f"Issues found: {invalid}\n\n"
                f"Data has been cleaned and is ready for PDF generation."
            )

        except Exception as e:
            messagebox.showerror("Error", f"Validation failed:\n{str(e)}")
            self._log(f"ERROR during validation: {e}")

    def _generate_pdfs(self):
        """Generate payslip PDFs in a background thread."""
        if not self.cleaned_employees:
            messagebox.showwarning(
                "Not Ready",
                "Please load and validate data first (Tab 1)."
            )
            return

        # Get pay period from entries
        self.pay_period = self.period_entry.get().strip()
        self.pay_month = self.month_entry.get().strip()

        if not self.pay_period:
            messagebox.showwarning("Missing", "Please enter the Pay Period (e.g. MARCH, 2026)")
            return

        total = len(self.cleaned_employees)
        confirm = messagebox.askyesno(
            "Confirm",
            f"Generate payslips for {total} employees?\n\n"
            f"Pay period: {self.pay_period}\n"
            f"Output: {self.output_dir_var.get()}"
        )

        if not confirm:
            return

        # Disable button during generation
        self.gen_button.config(state=tk.DISABLED)
        self.progress_var.set(0)
        self._log(f"Starting PDF generation: {total} employees, period: {self.pay_period}")
        self._set_status("Generating PDFs...")

        # Run in background thread so GUI doesn't freeze
        thread = threading.Thread(target=self._generate_worker, daemon=True)
        thread.start()

    def _generate_worker(self):
        """
        Background worker for PDF generation.

        This runs in a separate thread. It uses root.after() to safely
        update the GUI from the background thread (Tkinter rule: only
        the main thread can touch GUI widgets directly).
        """
        try:
            # Set the library path for WeasyPrint on macOS
            os.environ.setdefault("DYLD_LIBRARY_PATH", "/opt/homebrew/lib")

            from src.pdf_generator import batch_generate_pdfs, verify_batch

            output_dir = self.output_dir_var.get()
            total = len(self.cleaned_employees)

            def on_progress(current, count, name):
                """Called after each employee — updates the progress bar."""
                pct = (current / count) * 100
                self.root.after(0, lambda: self.progress_var.set(pct))
                self.root.after(0, lambda: self.progress_label.set(
                    f"Processing {current}/{count}: {name}"
                ))
                self.root.after(0, lambda: self._set_status(
                    f"Generating PDF {current}/{count}: {name}"
                ))

            results = batch_generate_pdfs(
                employees=self.cleaned_employees,
                output_dir=output_dir,
                pay_period=self.pay_period,
                pay_month=self.pay_month,
                on_progress=on_progress
            )

            # Verify generated PDFs
            self.generated_files = results["generated_files"]
            if self.generated_files:
                verify_results = verify_batch(self.generated_files)
            else:
                verify_results = {"valid": 0, "invalid": 0, "issues": []}

            # Update GUI from main thread
            def finish():
                self.gen_button.config(state=tk.NORMAL)
                self.progress_var.set(100)
                self.progress_label.set(
                    f"Done: {results['success']} generated, {results['failed']} failed"
                )

                # Write results to results text box
                self._write_results(results, verify_results)

                self._log(
                    f"PDF generation complete: {results['success']}/{total} succeeded, "
                    f"{results['failed']} failed"
                )
                self._set_status(
                    f"Generation complete: {results['success']} PDFs created"
                )

                if results["failed"] == 0:
                    messagebox.showinfo(
                        "Success",
                        f"All {results['success']} payslips generated successfully!\n\n"
                        f"Files saved to:\n{output_dir}"
                    )
                else:
                    messagebox.showwarning(
                        "Partial Success",
                        f"Generated: {results['success']}\n"
                        f"Failed: {results['failed']}\n\n"
                        f"Check the Log tab for error details."
                    )

            self.root.after(0, finish)

        except Exception as e:
            def show_error():
                self.gen_button.config(state=tk.NORMAL)
                self.progress_label.set(f"Error: {e}")
                messagebox.showerror("Error", f"PDF generation failed:\n{str(e)}")
                self._log(f"ERROR during PDF generation: {e}")
                self._set_status("Generation failed")

            self.root.after(0, show_error)

    def _write_results(self, gen_results: Dict, verify_results: Dict):
        """Write generation results to the results text box."""
        self.results_text.config(state=tk.NORMAL)
        self.results_text.delete("1.0", tk.END)

        lines = [
            f"{'=' * 50}",
            f"  PDF GENERATION REPORT",
            f"  {datetime.now().strftime('%d/%m/%Y %H:%M IST')}",
            f"{'=' * 50}",
            f"",
            f"  Pay Period:    {self.pay_period}",
            f"  Output Dir:    {self.output_dir_var.get()}",
            f"",
            f"  Total:         {gen_results['total']}",
            f"  Successful:    {gen_results['success']}",
            f"  Failed:        {gen_results['failed']}",
            f"",
            f"  PDF Verified:  {verify_results['valid']} valid",
            f"                 {verify_results['invalid']} invalid",
            f"{'=' * 50}",
        ]

        if gen_results["errors"]:
            lines.append("")
            lines.append("  ERRORS:")
            for err in gen_results["errors"]:
                lines.append(f"    - {err['name']}: {err['error']}")

        if verify_results.get("issues"):
            lines.append("")
            lines.append("  VERIFICATION ISSUES:")
            for issue in verify_results["issues"]:
                lines.append(f"    - {issue['file']}: {issue['error']}")

        lines.append("")
        lines.append("  Generated files:")
        for f in gen_results.get("generated_files", [])[:10]:
            lines.append(f"    {os.path.basename(f)}")
        if len(gen_results.get("generated_files", [])) > 10:
            lines.append(f"    ... and {len(gen_results['generated_files']) - 10} more")

        self.results_text.insert("1.0", "\n".join(lines))
        self.results_text.config(state=tk.DISABLED)

    # ================================================================
    # HELPER METHODS
    # ================================================================

    def _set_status(self, text: str):
        """Update the bottom status bar."""
        self.status_var.set(text)

    def _log(self, message: str):
        """Add a timestamped entry to the execution log."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        entry = f"[{timestamp}] {message}\n"

        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, entry)
        self.log_text.see(tk.END)  # Auto-scroll to bottom
        self.log_text.config(state=tk.DISABLED)

        logger.info(message)

    def _clear_log(self):
        """Clear the execution log."""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete("1.0", tk.END)
        self.log_text.config(state=tk.DISABLED)

    def _clear_data(self):
        """Clear all loaded data and reset."""
        self.file_path = None
        self.raw_employees = []
        self.cleaned_employees = []
        self.generated_files = []
        self.file_label.config(text="No file loaded")
        self.info_text.set("Load a file to see summary")
        self.gen_status.set("Load and validate data first")
        self.progress_var.set(0)
        self.progress_label.set("")

        for row in self.preview_tree.get_children():
            self.preview_tree.delete(row)

        self._set_status("Ready — Load an Excel file to begin")
        self._log("Data cleared")

    def _choose_output_dir(self):
        """Open folder dialog to choose PDF output directory."""
        path = filedialog.askdirectory(title="Choose Output Folder")
        if path:
            self.output_dir_var.set(path)

    def _open_folder(self, path: str):
        """Open a folder in the system file manager."""
        import subprocess
        import sys

        if not os.path.exists(path):
            os.makedirs(path, exist_ok=True)

        if sys.platform == "darwin":
            subprocess.run(["open", path])
        elif sys.platform == "win32":
            os.startfile(path)
        else:
            subprocess.run(["xdg-open", path])

    def _test_whatsapp_connection(self):
        """Test the Twilio WhatsApp connection."""
        self._log("Testing Twilio connection...")
        try:
            from src.whatsapp_sender import verify_connection
            connected, msg = verify_connection()
            self.wa_conn_var.set(msg)
            if connected:
                self._log(f"Twilio: {msg}")
            else:
                self._log(f"Twilio ERROR: {msg}")
                messagebox.showerror("Connection Failed", msg)
        except Exception as e:
            self.wa_conn_var.set(f"Error: {e}")
            self._log(f"Twilio ERROR: {e}")

    def _send_whatsapp(self):
        """Send payslip notifications via WhatsApp in a background thread."""
        if not self.generated_files:
            messagebox.showwarning(
                "Not Ready",
                "Please generate PDFs first (Tab 2) before sending via WhatsApp."
            )
            return

        if not self.cleaned_employees:
            messagebox.showwarning("Not Ready", "No employee data loaded.")
            return

        # Count employees with phone numbers
        with_phone = sum(1 for e in self.cleaned_employees
                         if e.get("whatsapp_contact") and
                         str(e.get("whatsapp_contact")).strip() not in ("", "0", "nan"))

        confirm = messagebox.askyesno(
            "Confirm WhatsApp Send",
            f"Send WhatsApp messages to {with_phone} employees?\n\n"
            f"Total employees: {len(self.cleaned_employees)}\n"
            f"With WhatsApp number: {with_phone}\n"
            f"Without number (will be skipped): {len(self.cleaned_employees) - with_phone}\n\n"
            f"This will use your Twilio account credits."
        )

        if not confirm:
            return

        self.wa_send_button.config(state=tk.DISABLED)
        self.wa_progress_var.set(0)
        self._log("Starting WhatsApp delivery...")

        thread = threading.Thread(target=self._whatsapp_worker, daemon=True)
        thread.start()

    def _whatsapp_worker(self):
        """Background worker for WhatsApp delivery."""
        try:
            from src.whatsapp_sender import send_batch, save_delivery_report

            output_dir = self.output_dir_var.get()

            def on_progress(current, total, name, status):
                pct = (current / total) * 100
                self.root.after(0, lambda: self.wa_progress_var.set(pct))
                self.root.after(0, lambda: self.wa_progress_label.set(
                    f"Sending {current}/{total}: {name} — {status}"
                ))
                self.root.after(0, lambda: self._set_status(
                    f"WhatsApp {current}/{total}: {name}"
                ))

            results = send_batch(
                employees=self.cleaned_employees,
                pdf_dir=output_dir,
                pay_period=self.pay_period,
                pay_month=self.pay_month,
                delay_seconds=2.0,
                on_progress=on_progress
            )

            # Save report
            report_path = save_delivery_report(results)

            def finish():
                self.wa_send_button.config(state=tk.NORMAL)
                self.wa_progress_var.set(100)
                self.wa_progress_label.set(
                    f"Done: {results['sent']} sent, {results['failed']} failed, "
                    f"{results['skipped']} skipped"
                )

                # Write results
                self.wa_results_text.config(state=tk.NORMAL)
                self.wa_results_text.delete("1.0", tk.END)
                lines = [
                    f"{'=' * 50}",
                    f"  WHATSAPP DELIVERY REPORT",
                    f"  {results.get('timestamp', '')}",
                    f"{'=' * 50}",
                    f"",
                    f"  Total:    {results['total']}",
                    f"  Sent:     {results['sent']}",
                    f"  Failed:   {results['failed']}",
                    f"  Skipped:  {results['skipped']}",
                    f"",
                    f"  Report saved: {report_path}",
                    f"{'=' * 50}",
                ]
                if results["errors"]:
                    lines.append("")
                    lines.append("  ERRORS:")
                    for err in results["errors"][:20]:
                        lines.append(f"    - {err['name']}: {err['error']}")
                    if len(results["errors"]) > 20:
                        lines.append(f"    ... and {len(results['errors']) - 20} more")

                self.wa_results_text.insert("1.0", "\n".join(lines))
                self.wa_results_text.config(state=tk.DISABLED)

                self._log(
                    f"WhatsApp delivery complete: {results['sent']} sent, "
                    f"{results['failed']} failed, {results['skipped']} skipped"
                )
                self._set_status(f"WhatsApp: {results['sent']} sent")

                messagebox.showinfo(
                    "WhatsApp Delivery Complete",
                    f"Sent: {results['sent']}\n"
                    f"Failed: {results['failed']}\n"
                    f"Skipped: {results['skipped']}\n\n"
                    f"Report saved to:\n{report_path}"
                )

            self.root.after(0, finish)

        except Exception as e:
            def show_error():
                self.wa_send_button.config(state=tk.NORMAL)
                messagebox.showerror("Error", f"WhatsApp delivery failed:\n{str(e)}")
                self._log(f"WhatsApp ERROR: {e}")
            self.root.after(0, show_error)

    def _show_about(self):
        """Show the About dialog."""
        messagebox.showinfo(
            "About",
            "PaySlip Generator & WhatsApp Sender\n"
            "Version 1.0\n\n"
            "For: Holistic Allied Services\n"
            "Facility Management & Security\n\n"
            "Generates payslip PDFs from Excel data\n"
            "and delivers them via WhatsApp."
        )

    def _default_pay_period(self) -> str:
        """Generate default pay period from current date."""
        now = datetime.now()
        return f"{now.strftime('%B').upper()}, {now.year}"

    def _default_pay_month(self) -> str:
        """Generate default short month from current date."""
        now = datetime.now()
        return f"{now.strftime('%b')}-{now.strftime('%y')}"


def run_app():
    """Launch the application."""
    root = tk.Tk()
    app = PaySlipApp(root)
    root.mainloop()


if __name__ == "__main__":
    run_app()
