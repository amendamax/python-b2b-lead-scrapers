"""
Configuration loader for Salesforce MCP Server and Data Aggregator.
Loads environment variables and sets sensible defaults.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
ENV_PATH = BASE_DIR / '.env'

if ENV_PATH.exists():
    load_dotenv(dotenv_path=ENV_PATH)
else:
    load_dotenv()

# Salesforce Configuration
SF_USERNAME = os.getenv("SALESFORCE_USERNAME", "amendamax@gmail.com")
SF_PASSWORD = os.getenv("SALESFORCE_PASSWORD", "")
SF_SECURITY_TOKEN = os.getenv("SALESFORCE_SECURITY_TOKEN", "")
SF_DOMAIN = os.getenv("SALESFORCE_DOMAIN", "centineltrust.my.salesforce.com")
SF_INSTANCE_TYPE = os.getenv("SALESFORCE_INSTANCE_TYPE", "login")

# Local Aggregation Table Configuration
DB_PATH = os.getenv("AGGREGATION_DB_PATH", str(BASE_DIR / "data_aggregation.db"))
CACHE_TTL = int(os.getenv("CACHE_TTL_SECONDS", "300"))

# Server Metadata
SERVER_NAME = "salesforce-docupletion-mcp"
SERVER_VERSION = "1.0.0"
