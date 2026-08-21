import os
import re
import json
import logging
from typing import Dict, List, Any, Optional, Set
from datetime import datetime, timezone

logger = logging.getLogger("AutomationEngine.FileParser")

class ConfigParser:
    """
    Robust parser for key=value formatted configuration files.
    Supports comments (# and ;), inline comments, whitespace stripping,
    and automatic type casting (bool, int, float, str).
    """
    @staticmethod
    def parse(file_path: str) -> Dict[str, Any]:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Configuration file not found: {file_path}")
        
        config = {}
        with open(file_path, "r", encoding="utf-8") as f:
            for line_no, raw_line in enumerate(f, 1):
                line = raw_line.strip()
                if not line or line.startswith("#") or line.startswith(";"):
                    continue
                
                if "=" not in line:
                    logger.warning(f"Skipping malformed line {line_no} in {file_path}: {line}")
                    continue
                
                key, val = line.split("=", 1)
                key = key.strip()
                if "#" in val:
                    val = val.split("#", 1)[0]
                if ";" in val:
                    val = val.split(";", 1)[0]
                val = val.strip()

                if val.lower() in ("true", "yes", "1", "on"):
                    typed_val: Any = True
                elif val.lower() in ("false", "no", "0", "off"):
                    typed_val = False
                elif re.match(r"^-?\d+$", val):
                    typed_val = int(val)
                elif re.match(r"^-?\d+\.\d+$", val):
                    typed_val = float(val)
                else:
                    if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
                        val = val[1:-1]
                    typed_val = val
                
                config[key] = typed_val
        
        return config


class AppPasswordsParser:
    """
    Parser and validator for app_passwords.json (the only allowed JSON data file).
    Maps Gmail account email to 16-character app password / credentials.
    """
    @staticmethod
    def parse(file_path: str) -> Dict[str, str]:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"App passwords file not found: {file_path}")
        
        with open(file_path, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON format in {file_path}: {e}")
        
        cleaned = {}
        for email, password in data.items():
            if email.startswith("_"):
                continue  # Skip comments/metadata keys
            email_clean = email.strip().lower()
            pass_clean = str(password).strip()
            cleaned[email_clean] = pass_clean
        
        return cleaned


class AccountsParser:
    """
    Parser for accounts.txt.
    Returns ordered, verified list of active Gmail addresses.
    """
    EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")

    @staticmethod
    def parse(file_path: str, app_passwords: Optional[Dict[str, str]] = None) -> List[str]:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Accounts file not found: {file_path}")
        
        accounts: List[str] = []
        seen: Set[str] = set()
        
        with open(file_path, "r", encoding="utf-8") as f:
            for raw_line in f:
                line = raw_line.strip()
                if not line or line.startswith("#") or line.startswith(";"):
                    continue
                parts = re.split(r"[:|,\t\s]+", line)
                email = parts[0].strip().lower()
                if not AccountsParser.EMAIL_REGEX.match(email):
                    logger.warning(f"Skipping invalid email syntax in {file_path}: {email}")
                    continue
                if email in seen:
                    continue
                
                # If password was provided on the line, auto-register it
                if len(parts) > 1 and app_passwords is not None:
                    if email not in app_passwords or not app_passwords[email]:
                        app_passwords[email] = parts[1].strip()

                if app_passwords is not None and email not in app_passwords:
                    logger.warning(f"Account {email} listed in {file_path} but missing from app_passwords.json!")
                
                seen.add(email)
                accounts.append(email)
        
        return accounts


class LeadsParser:
    """
    Parser for leads.txt.
    Deduplicates and cleans recipient email queue.
    """
    @staticmethod
    def parse(file_path: str) -> List[str]:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Leads file not found: {file_path}")
        
        leads: List[str] = []
        seen: Set[str] = set()
        
        with open(file_path, "r", encoding="utf-8") as f:
            for raw_line in f:
                line = raw_line.strip()
                if not line or line.startswith("#") or line.startswith(";"):
                    continue
                email = line.split()[0].strip().lower()
                if AccountsParser.EMAIL_REGEX.match(email):
                    if email not in seen:
                        seen.add(email)
                        leads.append(email)
                else:
                    logger.warning(f"Skipping invalid lead email: {line}")
        
        return leads


class TemplateParser:
    """
    Parser and renderer for letter.html.
    """
    @staticmethod
    def parse(file_path: str) -> str:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Letter template not found: {file_path}")
        
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        if not content.strip():
            raise ValueError(f"Letter template file is empty: {file_path}")
        
        return content

    @staticmethod
    def render(template_str: str, placeholders: Dict[str, str]) -> str:
        rendered = template_str
        for key, value in placeholders.items():
            pattern = re.compile(rf"\{{\{{\s*{re.escape(key)}\s*\}}\}}", re.IGNORECASE)
            rendered = pattern.sub(str(value), rendered)
        return rendered


class LinksParser:
    """
    Parser for links.txt.
    Loads list of rotation destination links.
    """
    @staticmethod
    def parse(file_path: str) -> List[str]:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Links file not found: {file_path}")
        
        links: List[str] = []
        with open(file_path, "r", encoding="utf-8") as f:
            for raw_line in f:
                line = raw_line.strip()
                if not line or line.startswith("#") or line.startswith(";"):
                    continue
                links.append(line)
        return links


class LimitReachedLogger:
    """
    Thread-safe append logger for 24-reached.txt.
    Logs when an account hits its 24-hour dispatch limit.
    """
    @staticmethod
    def record(account_email: str, daily_limit: int, cooldown_until: datetime, file_path: str = "24-reached.txt") -> None:
        timestamp_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        cooldown_str = cooldown_until.strftime("%Y-%m-%d %H:%M:%S UTC")
        log_line = f"[{timestamp_str}] | ACCOUNT: {account_email} | LIMIT_REACHED: {daily_limit} | COOLDOWN_UNTIL: {cooldown_str}\n"
        
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(log_line)
        logger.info(f"Recorded 24h limit exhaustion for {account_email} in {file_path}")
