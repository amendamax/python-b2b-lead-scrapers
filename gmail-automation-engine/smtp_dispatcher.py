import smtplib
import ssl
import random
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate
from typing import Dict, Any, Optional

logger = logging.getLogger("AutomationEngine.SMTPDispatcher")

class SMTPDispatcher:
    """
    High-reliability Gmail SMTP sender supporting STARTTLS, App Passwords,
    MIME multipart construction, link rotation, and deterministic headers.
    """
    def __init__(self, host: str = "smtp.gmail.com", port: int = 587, use_tls: bool = True, timeout: int = 30):
        self.host = host
        self.port = port
        self.use_tls = use_tls
        self.timeout = timeout

    def send_email(
        self,
        account_email: str,
        app_password: str,
        recipient_email: str,
        subject: str,
        html_body: str,
        message_id: str,
        proxy: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Constructs and delivers a single MIME email via Gmail SMTP.
        Returns result dictionary: {'success': bool, 'message_id': str, 'error': Optional[str]}
        """
        # 1. Build MIME message
        msg = MIMEMultipart("alternative")
        msg["From"] = account_email
        msg["To"] = recipient_email
        msg["Subject"] = subject
        msg["Date"] = formatdate(localtime=True)
        msg["Message-ID"] = message_id
        
        # Attach HTML body
        msg.attach(MIMEText(html_body, "html", "utf-8"))

        # Clean app password
        clean_password = app_password.replace(" ", "")

        # 2. Transmit via SMTP
        try:
            if self.use_tls:
                server = smtplib.SMTP(self.host, self.port, timeout=self.timeout)
                server.ehlo()
                context = ssl.create_default_context()
                server.starttls(context=context)
                server.ehlo()
            else:
                context = ssl.create_default_context()
                server = smtplib.SMTP_SSL(self.host, self.port, timeout=self.timeout, context=context)
                server.ehlo()

            # Authenticate
            server.login(account_email, clean_password)
            
            # Send
            server.sendmail(account_email, [recipient_email], msg.as_string())
            server.quit()

            logger.info(f"Successfully sent message {message_id} to {recipient_email} via {account_email}")
            return {"success": True, "message_id": message_id, "error": None}

        except smtplib.SMTPAuthenticationError as e:
            err = f"Auth failed for {account_email}: {e}"
            logger.error(err)
            return {"success": False, "message_id": message_id, "error": err}
        except smtplib.SMTPException as e:
            err = f"SMTP error for {recipient_email}: {e}"
            logger.error(err)
            return {"success": False, "message_id": message_id, "error": err}
        except Exception as e:
            err = f"Unexpected transmission error: {e}"
            logger.error(err)
            return {"success": False, "message_id": message_id, "error": err}
