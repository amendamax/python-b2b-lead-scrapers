"""
VerifyDating Python SDK
~~~~~~~~~~~~~~~~~~~~~~~
Official Python client library for VerifyDating B2B Anti-Catfish & Facial Scam Intelligence API.

:copyright: (c) 2026 VasileDev Group / VerifyDating.net
:license: MIT, see LICENSE for more details.
"""

__version__ = "1.0.0"
__author__ = "VasileDev Group"

from .client import Client, AsyncClient
from .models import FaceCheckResult, ForensicDetails, QuotaInfo, DatingStats
from .exceptions import (
    VerifyDatingError,
    AuthenticationError,
    QuotaExceededError,
    RateLimitError,
    APIResponseError
)

__all__ = [
    "Client",
    "AsyncClient",
    "FaceCheckResult",
    "ForensicDetails",
    "QuotaInfo",
    "DatingStats",
    "VerifyDatingError",
    "AuthenticationError",
    "QuotaExceededError",
    "RateLimitError",
    "APIResponseError"
]
