import smtplib
import ssl
import random
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate
from typing import Dict, Any, Optional

try:
    import socks
except ImportError:
    socks = None

logger = logging.getLogger("AutomationEngine.SMTPDispatcher")

class SMTPDispatcher:
    """
    High-reliability Gmail SMTP sender supporting STARTTLS, App Passwords,
    MIME multipart construction, link rotation, and SOCKS5/HTTP Proxy routing.
    """
    def __init__(self, host: str = "smtp.gmail.com", port: int = 587, use_tls: bool = True, timeout: int = 30):
        self.host = host
        self.port = port
        self.use_tls = use_tls
        self.timeout = timeout

    def _create_smtp_connection(self, proxy: Optional[str] = None) -> smtplib.SMTP:
        if proxy and socks is not None:
            proxy_type = socks.HTTP
            p = proxy.strip()
            if p.startswith("socks5://"):
                proxy_type = socks.SOCKS5
                p = p[9:]
            elif p.startswith("socks4://"):
                proxy_type = socks.SOCKS4
                p = p[9:]
            elif p.startswith("http://"):
                proxy_type = socks.HTTP
                p = p[7:]
            elif p.startswith("https://"):
                proxy_type = socks.HTTP
                p = p[8:]

            p_user, p_pass = None, None
            if "@" in p:
                auth, host_port = p.split("@", 1)
                if ":" in auth:
                    p_user, p_pass = auth.split(":", 1)
                else:
                    p_user = auth
                p_host, p_port = host_port.split(":", 1)
            elif p.count(":") == 3:
                p_host, p_port, p_user, p_pass = p.split(":")
            else:
                p_host, p_port = p.split(":", 1)

            logger.info(f"Connecting to SMTP via Proxy ({p_host}:{p_port})...")
            sock = socks.socksocket()
            sock.set_proxy(proxy_type, p_host, int(p_port), username=p_user, password=p_pass)
            sock.settimeout(self.timeout)
            sock.connect((self.host, self.port))

            server = smtplib.SMTP(timeout=self.timeout)
            server.sock = sock
            server.file = None
            return server
        else:
            return smtplib.SMTP(self.host, self.port, timeout=self.timeout)

    def send_email(
        self,
        account_email: str,
        app_password: str,
        recipient_email: str,
        subject: str,
        html_body: str,
        message_id: str,
        sender_name: Optional[str] = None,
        proxy: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Constructs and delivers a single MIME email via Gmail SMTP with proxy support.
        """
        # 1. Build MIME message
        msg = MIMEMultipart("alternative")
        if sender_name:
            msg["From"] = f'"{sender_name}" <{account_email}>'
        else:
            msg["From"] = account_email
        msg["To"] = recipient_email
        msg["Subject"] = subject
        msg["Date"] = formatdate(localtime=True)
        msg["Message-ID"] = message_id
        
        # Attach HTML body
        msg.attach(MIMEText(html_body, "html", "utf-8"))

        clean_password = app_password.replace(" ", "")

        # 2. Transmit via SMTP
        try:
            server = self._create_smtp_connection(proxy)
            server.ehlo()
            if self.use_tls:
                context = ssl.create_default_context()
                server.starttls(context=context)
                server.ehlo()

            # Authenticate
            server.login(account_email, clean_password)
            
            # Send
            server.sendmail(account_email, [recipient_email], msg.as_string())
            try:
                server.quit()
            except Exception:
                pass

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
