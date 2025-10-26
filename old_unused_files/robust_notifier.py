#!/usr/bin/env python3
"""
Enhanced notification system with SMTP timeouts and fallback mechanisms
"""

import os
import ssl
import smtplib
import time
import logging
from pathlib import Path
from typing import Optional, Dict, Any
from email.message import EmailMessage
import requests

logger = logging.getLogger(__name__)

class RobustNotifier:
    """Enhanced notification system with reliability and fallback options"""

    def __init__(self):
        self.email_config = self._load_email_config()
        self.telegram_config = self._load_telegram_config()
        self.max_retries = 3
        self.retry_delay = 5

    def _load_email_config(self) -> Dict[str, Optional[str]]:
        """Load email configuration from environment"""
        return {
            "smtp_server": os.getenv("SMTP_SERVER", "smtp.gmail.com"),
            "smtp_port": int(os.getenv("SMTP_PORT", "465")),
            "email_from": os.getenv("EMAIL_FROM"),
            "email_to": os.getenv("EMAIL_TO"),
            "email_password": os.getenv("EMAIL_PASSWORD")
        }

    def _load_telegram_config(self) -> Dict[str, Optional[str]]:
        """Load Telegram configuration from environment"""
        return {
            "bot_token": os.getenv("TELEGRAM_BOT_TOKEN"),
            "chat_id": os.getenv("TELEGRAM_CHAT_ID")
        }

    def send_notification(self, subject: str, message: str,
                         attachment_path: Optional[str] = None,
                         priority: str = "normal") -> bool:
        """
        Send notification with fallback options

        Args:
            subject: Message subject/title
            message: Message body
            attachment_path: Optional file to attach (email only)
            priority: "high", "normal", or "low"

        Returns:
            True if any notification method succeeded
        """
        success = False

        # Try email first for all priorities
        if self._email_configured():
            try:
                email_success = self.send_email(subject, message, attachment_path)
                if email_success:
                    success = True
                    logger.info(f"Email notification sent: {subject}")
            except Exception as e:
                logger.error(f"Email notification failed: {e}")

        # Try Telegram as backup/secondary notification
        if self._telegram_configured():
            try:
                telegram_message = f"*{subject}*\n\n{message}"
                telegram_success = self.send_telegram(telegram_message)
                if telegram_success:
                    success = True
                    logger.info(f"Telegram notification sent: {subject}")
            except Exception as e:
                logger.error(f"Telegram notification failed: {e}")

        if not success:
            logger.error(f"All notification methods failed for: {subject}")

        return success

    def send_email(self, subject: str, body: str,
                   attachment_path: Optional[str] = None) -> bool:
        """Send email with robust error handling and timeouts"""

        if not self._email_configured():
            logger.warning("Email not configured, skipping email notification")
            return False

        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = self.email_config["email_from"]
        msg["To"] = self.email_config["email_to"]
        msg.set_content(body)

        # Add attachment if provided
        if attachment_path and Path(attachment_path).is_file():
            try:
                with open(attachment_path, "rb") as f:
                    file_data = f.read()

                file_name = Path(attachment_path).name

                # Determine content type based on file extension
                if file_name.lower().endswith(('.png', '.jpg', '.jpeg')):
                    maintype, subtype = "image", "png" if file_name.lower().endswith('.png') else "jpeg"
                else:
                    maintype, subtype = "application", "octet-stream"

                msg.add_attachment(
                    file_data,
                    maintype=maintype,
                    subtype=subtype,
                    filename=file_name
                )
                logger.debug(f"Added attachment: {file_name}")

            except Exception as e:
                logger.warning(f"Failed to attach file {attachment_path}: {e}")

        # Send email with retries and timeout
        for attempt in range(self.max_retries):
            try:
                context = ssl.create_default_context()

                # Use SMTP_SSL with explicit timeout
                with smtplib.SMTP_SSL(
                    self.email_config["smtp_server"],
                    self.email_config["smtp_port"],
                    context=context,
                    timeout=30  # 30 second timeout
                ) as server:

                    server.login(
                        self.email_config["email_from"],
                        self.email_config["email_password"]
                    )
                    server.send_message(msg)

                logger.info(f"Email sent successfully on attempt {attempt + 1}")
                return True

            except smtplib.SMTPAuthenticationError:
                logger.error("SMTP authentication failed - check credentials")
                break  # Don't retry auth failures

            except smtplib.SMTPRecipientsRefused:
                logger.error("SMTP recipients refused - check email addresses")
                break  # Don't retry recipient failures

            except (smtplib.SMTPException, OSError, TimeoutError) as e:
                logger.warning(f"Email attempt {attempt + 1} failed: {e}")

                if attempt < self.max_retries - 1:
                    logger.info(f"Retrying email in {self.retry_delay} seconds...")
                    time.sleep(self.retry_delay)
                else:
                    logger.error("All email attempts failed")

            except Exception as e:
                logger.error(f"Unexpected email error: {e}")
                break

        return False

    def send_telegram(self, message: str, parse_mode: str = "Markdown") -> bool:
        """Send Telegram message with error handling"""

        if not self._telegram_configured():
            logger.warning("Telegram not configured, skipping Telegram notification")
            return False

        url = f"https://api.telegram.org/bot{self.telegram_config['bot_token']}/sendMessage"

        payload = {
            "chat_id": self.telegram_config["chat_id"],
            "text": message,
            "parse_mode": parse_mode
        }

        for attempt in range(self.max_retries):
            try:
                response = requests.post(
                    url,
                    json=payload,
                    timeout=10
                )
                response.raise_for_status()

                result = response.json()
                if result.get("ok"):
                    logger.info(f"Telegram message sent successfully on attempt {attempt + 1}")
                    return True
                else:
                    logger.error(f"Telegram API error: {result}")

            except requests.exceptions.RequestException as e:
                logger.warning(f"Telegram attempt {attempt + 1} failed: {e}")

                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)

            except Exception as e:
                logger.error(f"Unexpected Telegram error: {e}")
                break

        return False

    def send_alert(self, alert_type: str, symbol: str, message: str,
                   chart_path: Optional[str] = None) -> bool:
        """Send trading alert with appropriate formatting"""

        subject = f"ZoneSync Alert - {alert_type} - {symbol}"

        formatted_message = (
            f"Alert Type: {alert_type}\n"
            f"Symbol: {symbol}\n"
            f"Time: {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())}\n"
            f"\n{message}"
        )

        # Determine priority based on alert type
        priority = "high" if alert_type.lower() in ["entry", "exit", "stop"] else "normal"

        return self.send_notification(
            subject=subject,
            message=formatted_message,
            attachment_path=chart_path,
            priority=priority
        )

    def send_system_alert(self, alert_level: str, component: str, message: str) -> bool:
        """Send system/bot health alerts"""

        subject = f"ZoneSync System - {alert_level.upper()} - {component}"

        formatted_message = (
            f"Component: {component}\n"
            f"Level: {alert_level.upper()}\n"
            f"Time: {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())}\n"
            f"\n{message}"
        )

        priority = "high" if alert_level.lower() in ["error", "critical"] else "normal"

        return self.send_notification(
            subject=subject,
            message=formatted_message,
            priority=priority
        )

    def _email_configured(self) -> bool:
        """Check if email is properly configured"""
        required_fields = ["email_from", "email_to", "email_password"]
        return all(self.email_config.get(field) for field in required_fields)

    def _telegram_configured(self) -> bool:
        """Check if Telegram is properly configured"""
        required_fields = ["bot_token", "chat_id"]
        return all(self.telegram_config.get(field) for field in required_fields)

    def test_notifications(self) -> Dict[str, bool]:
        """Test all notification methods"""
        results = {}

        test_subject = "ZoneSync Test Notification"
        test_message = "This is a test message to verify notification systems are working."

        if self._email_configured():
            logger.info("Testing email notifications...")
            results["email"] = self.send_email(test_subject, test_message)
        else:
            logger.warning("Email not configured, skipping test")
            results["email"] = False

        if self._telegram_configured():
            logger.info("Testing Telegram notifications...")
            results["telegram"] = self.send_telegram(f"*{test_subject}*\n\n{test_message}")
        else:
            logger.warning("Telegram not configured, skipping test")
            results["telegram"] = False

        return results


# Global notifier instance
notifier = RobustNotifier()

# Convenience functions for backward compatibility
def send_email(subject: str, body: str, attachment_path: Optional[str] = None) -> bool:
    """Send email notification"""
    return notifier.send_email(subject, body, attachment_path)

def send_alert(alert_type: str, symbol: str, message: str,
               chart_path: Optional[str] = None) -> bool:
    """Send trading alert"""
    return notifier.send_alert(alert_type, symbol, message, chart_path)

def send_system_alert(level: str, component: str, message: str) -> bool:
    """Send system alert"""
    return notifier.send_system_alert(level, component, message)


if __name__ == "__main__":
    # Test notifications when run directly
    logging.basicConfig(level=logging.INFO)

    print("Testing notification systems...")
    results = notifier.test_notifications()

    for method, success in results.items():
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"{method.capitalize()}: {status}")