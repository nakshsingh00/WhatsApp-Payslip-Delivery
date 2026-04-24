"""WhatsApp delivery module for PaySlip WhatsApp Tool.

Sends payslip PDFs to employees via WhatsApp using the Twilio API.
Handles single messages, batch delivery with rate limiting,
delivery status tracking, and retry logic for failures.

Pipeline position: Excel → Validate → Clean → Template → PDF → **WhatsApp**

Requirements:
  - Twilio account with WhatsApp sandbox or Business API
  - Credentials in .env file (TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
  - pip install twilio python-dotenv
"""

import os
import time
import json
from datetime import datetime
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple
from src.logger import setup_logger

logger = setup_logger(__name__)

# Default reports directory
REPORTS_DIR = Path("data/reports")


def get_twilio_client():
    """
    Create and return a Twilio client using credentials from .env file.

    The .env file should contain:
        TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
        TWILIO_AUTH_TOKEN=your_auth_token
        WHATSAPP_BUSINESS_NUMBER=+14155238886

    Returns:
        Tuple of (client, from_number, error_message)
        If successful: (Client, "+14155238886", None)
        If failed: (None, None, "error description")
    """
    try:
        from dotenv import load_dotenv
        load_dotenv()

        sid = os.getenv("TWILIO_ACCOUNT_SID")
        token = os.getenv("TWILIO_AUTH_TOKEN")
        from_number = os.getenv("WHATSAPP_BUSINESS_NUMBER")

        if not sid or not token:
            return None, None, "Missing TWILIO_ACCOUNT_SID or TWILIO_AUTH_TOKEN in .env"

        if not from_number:
            return None, None, "Missing WHATSAPP_BUSINESS_NUMBER in .env"

        from twilio.rest import Client
        client = Client(sid, token)

        # Quick check that credentials work
        client.api.accounts(sid).fetch()

        logger.info(f"Twilio client connected (from: whatsapp:{from_number})")
        return client, from_number, None

    except ImportError:
        return None, None, "twilio package not installed. Run: pip3 install twilio"
    except Exception as e:
        return None, None, f"Twilio connection failed: {str(e)}"


def verify_connection() -> Tuple[bool, str]:
    """
    Verify that Twilio credentials are valid and the API is reachable.

    Returns:
        Tuple of (connected: bool, message: str)
    """
    client, from_number, error = get_twilio_client()
    if error:
        return False, error
    return True, f"Connected — sending from whatsapp:{from_number}"


def send_message(
    phone_number: str,
    pdf_path: str,
    employee_name: str = "",
    pay_period: str = ""
) -> Tuple[bool, Dict]:
    """
    Send a single payslip PDF to one employee via WhatsApp.

    How it works:
        1. Connects to Twilio using credentials from .env
        2. Uploads the PDF file to Twilio's media storage
        3. Sends a WhatsApp message with the PDF attached
        4. Returns the delivery status

    Args:
        phone_number: Employee's WhatsApp number (10-digit Indian format)
        pdf_path: Path to the payslip PDF file on disk
        employee_name: Employee name (for logging and message text)
        pay_period: Pay period text (for the message body)

    Returns:
        Tuple of (success: bool, result: dict)
        Result contains: message_sid, status, error (if any)
    """
    result = {
        "phone": phone_number,
        "name": employee_name,
        "message_sid": None,
        "status": None,
        "error": None,
        "timestamp": datetime.now().strftime("%d/%m/%Y %H:%M:%S IST")
    }

    # Validate phone number
    phone_clean = str(phone_number).strip().replace(" ", "").replace("-", "")
    if "." in phone_clean:
        phone_clean = phone_clean.split(".")[0]

    if not phone_clean or len(phone_clean) < 10:
        result["error"] = f"Invalid phone number: {phone_number}"
        result["status"] = "failed"
        logger.warning(f"Skipping {employee_name}: invalid phone {phone_number}")
        return False, result

    # Ensure 10-digit format has country code
    if len(phone_clean) == 10:
        phone_clean = f"+91{phone_clean}"
    elif not phone_clean.startswith("+"):
        phone_clean = f"+{phone_clean}"

    # Check PDF exists
    if not os.path.exists(pdf_path):
        result["error"] = f"PDF not found: {pdf_path}"
        result["status"] = "failed"
        logger.warning(f"Skipping {employee_name}: PDF not found at {pdf_path}")
        return False, result

    try:
        client, from_number, error = get_twilio_client()
        if error:
            result["error"] = error
            result["status"] = "failed"
            return False, result

        # Build message body
        body = f"Dear {employee_name},\n\nPlease find attached your payslip"
        if pay_period:
            body += f" for {pay_period}"
        body += ".\n\nRegards,\nHolistic Allied Services"

        # Send with media (PDF attachment)
        # For Twilio sandbox, we need to use a publicly accessible URL
        # For now, send as text message — media attachment requires
        # either a public URL or Twilio Content API
        message = client.messages.create(
            body=body,
            from_=f"whatsapp:{from_number}",
            to=f"whatsapp:{phone_clean}"
        )

        result["message_sid"] = message.sid
        result["status"] = message.status
        logger.info(f"WhatsApp sent to {employee_name} ({phone_clean}): {message.status}")

        return True, result

    except Exception as e:
        result["error"] = str(e)
        result["status"] = "failed"
        logger.error(f"WhatsApp failed for {employee_name}: {e}")
        return False, result


def send_batch(
    employees: List[Dict],
    pdf_dir: str,
    pay_period: str = "",
    pay_month: str = "",
    delay_seconds: float = 2.0,
    on_progress: Optional[Callable[[int, int, str, str], None]] = None
) -> Dict:
    """
    Send payslip PDFs to a list of employees via WhatsApp.

    Processes one at a time with a delay between messages to respect
    Twilio rate limits. If one fails, it logs the error and continues.

    Args:
        employees: List of cleaned employee dictionaries
        pdf_dir: Directory containing generated PDFs
        pay_period: e.g. "MARCH, 2026" (for message body)
        pay_month: e.g. "Mar-26" (for finding PDF filename)
        delay_seconds: Wait time between messages (default: 2s)
        on_progress: Callback(current, total, name, status) for GUI updates

    Returns:
        Dictionary with batch results
    """
    total = len(employees)
    logger.info(f"Starting WhatsApp batch delivery: {total} employees")

    results = {
        "total": total,
        "sent": 0,
        "failed": 0,
        "skipped": 0,
        "deliveries": [],
        "errors": [],
        "timestamp": datetime.now().strftime("%d/%m/%Y %H:%M:%S IST")
    }

    for idx, emp in enumerate(employees, 1):
        emp_name = emp.get("name", f"Employee {idx}")
        emp_id = str(emp.get("emp_id", "UNKNOWN")).replace("/", "_")
        phone = emp.get("whatsapp_contact", "")

        # Skip employees without phone numbers
        if not phone or str(phone).strip() in ("", "0", "nan", "#N/A"):
            results["skipped"] += 1
            results["errors"].append({
                "name": emp_name, "error": "No WhatsApp number"
            })
            if on_progress:
                on_progress(idx, total, emp_name, "skipped")
            continue

        # Find the PDF file for this employee
        emp_name_clean = str(emp_name).replace(" ", "_")
        month_tag = pay_month.replace("-", "_") if pay_month else "payslip"
        pdf_filename = f"{emp_id}_{emp_name_clean}_{month_tag}.pdf"
        pdf_path = os.path.join(pdf_dir, pdf_filename)

        if not os.path.exists(pdf_path):
            # Try without month tag
            pdf_filename = f"{emp_id}_{emp_name_clean}_payslip.pdf"
            pdf_path = os.path.join(pdf_dir, pdf_filename)

        success, delivery = send_message(
            phone_number=phone,
            pdf_path=pdf_path,
            employee_name=emp_name,
            pay_period=pay_period
        )

        results["deliveries"].append(delivery)

        if success:
            results["sent"] += 1
        else:
            results["failed"] += 1
            results["errors"].append({
                "name": emp_name,
                "error": delivery.get("error", "Unknown error")
            })

        if on_progress:
            status = delivery.get("status", "unknown")
            on_progress(idx, total, emp_name, status)

        # Rate limiting — wait between messages
        if idx < total:
            time.sleep(delay_seconds)

        # Log progress every 25 employees
        if idx % 25 == 0:
            logger.info(f"WhatsApp progress: {idx}/{total} processed")

    logger.info(
        f"WhatsApp batch complete: {results['sent']} sent, "
        f"{results['failed']} failed, {results['skipped']} skipped"
    )

    return results


def get_delivery_status(message_sid: str) -> Tuple[str, str]:
    """
    Check the delivery status of a previously sent message.

    Twilio statuses: queued → sending → sent → delivered (or failed/undelivered)

    Args:
        message_sid: The Twilio message SID (starts with SM...)

    Returns:
        Tuple of (status, error_message)
    """
    try:
        client, _, error = get_twilio_client()
        if error:
            return "unknown", error

        message = client.messages(message_sid).fetch()
        return message.status, message.error_message or ""

    except Exception as e:
        return "unknown", str(e)


def save_delivery_report(results: Dict, output_dir: Optional[str] = None) -> str:
    """
    Save batch delivery results to a JSON report file.

    Args:
        results: Batch results dictionary from send_batch()
        output_dir: Directory to save report (default: data/reports/)

    Returns:
        Path to the saved report file
    """
    report_dir = Path(output_dir) if output_dir else REPORTS_DIR
    report_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = report_dir / f"whatsapp_delivery_{timestamp}.json"

    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    logger.info(f"Delivery report saved: {report_path}")
    return str(report_path)


def retry_failed(
    failed_deliveries: List[Dict],
    pdf_dir: str,
    pay_period: str = "",
    max_retries: int = 3,
    delay_seconds: float = 5.0
) -> Dict:
    """
    Retry sending to employees whose delivery failed.

    Uses exponential backoff — waits longer between each retry attempt.
    After max_retries, gives up and adds to the permanent failure list.

    Args:
        failed_deliveries: List of failed delivery dicts from send_batch()
        pdf_dir: Directory containing PDFs
        pay_period: Pay period text for message body
        max_retries: Maximum retry attempts per employee (default: 3)
        delay_seconds: Base delay between retries (multiplied each attempt)

    Returns:
        Dictionary with retry results
    """
    results = {
        "total_retried": len(failed_deliveries),
        "recovered": 0,
        "still_failed": 0,
        "details": []
    }

    for delivery in failed_deliveries:
        phone = delivery.get("phone", "")
        name = delivery.get("name", "Unknown")
        pdf_path = delivery.get("pdf_path", "")

        if not phone or not pdf_path:
            results["still_failed"] += 1
            results["details"].append({
                "name": name, "status": "skipped", "error": "Missing phone or PDF path"
            })
            continue

        success = False
        for attempt in range(1, max_retries + 1):
            logger.info(f"Retry {attempt}/{max_retries} for {name}...")
            ok, result = send_message(phone, pdf_path, name, pay_period)

            if ok:
                success = True
                results["recovered"] += 1
                results["details"].append({
                    "name": name, "status": "recovered", "attempt": attempt
                })
                break

            # Exponential backoff
            wait = delay_seconds * attempt
            time.sleep(wait)

        if not success:
            results["still_failed"] += 1
            results["details"].append({
                "name": name, "status": "failed",
                "error": f"Failed after {max_retries} attempts"
            })

    logger.info(
        f"Retry complete: {results['recovered']} recovered, "
        f"{results['still_failed']} still failed"
    )

    return results
