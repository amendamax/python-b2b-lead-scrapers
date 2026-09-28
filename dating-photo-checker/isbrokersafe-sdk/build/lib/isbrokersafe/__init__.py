"""
IsBrokerSafe Official Python SDK
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Enterprise Real-Time Financial Broker and Crypto Fraud Intelligence API Client.

Basic usage:

    import isbrokersafe

    client = isbrokersafe.Client(api_key="YOUR_API_KEY")
    result = client.check("exness.com")
    print(result.status, result.safety_score, result.is_regulated)

:copyright: (c) 2026 by VasileDev Group.
:license: MIT, see LICENSE for more details.
"""

__title__ = "isbrokersafe"
__version__ = "1.0.0"
__author__ = "VasileDev Group"
__license__ = "MIT"
__copyright__ = "Copyright 2026 VasileDev Group"

from .client import Client, AsyncClient
from .models import BrokerCheckResult, RegulatoryWarning, GlobalStats
from .exceptions import (
    IsBrokerSafeError,
    AuthenticationError,
    QuotaExceededError,
    RateLimitError,
    APIResponseError
)

__all__ = [
    "Client",
    "AsyncClient",
    "BrokerCheckResult",
    "RegulatoryWarning",
    "GlobalStats",
    "IsBrokerSafeError",
    "AuthenticationError",
    "QuotaExceededError",
    "RateLimitError",
    "APIResponseError"
]
