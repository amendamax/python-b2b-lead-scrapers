"""
isbrokersafe.client
~~~~~~~~~~~~~~~~~~~
Synchronous and Asynchronous client implementations for IsBrokerSafe API.
"""

import json
import urllib.request
import urllib.error
import urllib.parse
from typing import Dict, Any, Optional, List

from .models import BrokerCheckResult, RegulatoryWarning, GlobalStats
from .exceptions import (
    AuthenticationError,
    QuotaExceededError,
    RateLimitError,
    APIResponseError
)

DEFAULT_BASE_URL = "https://isbrokersafe.com"

class Client:
    """
    Synchronous IsBrokerSafe API Client.

    Args:
        api_key (str, optional): Your IsBrokerSafe API Key.
        base_url (str, optional): Custom API endpoint URL.
        timeout (float, optional): Request timeout in seconds (default 10.0).
    """
    def __init__(self, api_key: Optional[str] = None, base_url: str = DEFAULT_BASE_URL, timeout: float = 10.0):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def _request(self, endpoint: str, params: Optional[Dict[str, Any]] = None, method: str = "GET", json_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        params = params or {}
        if self.api_key:
            params["api_key"] = self.api_key

        url = f"{self.base_url}{endpoint}"
        if params:
            url += "?" + urllib.parse.urlencode(params)

        headers = {
            "User-Agent": "IsBrokerSafe-Python-SDK/1.3.0",
            "Accept": "application/json"
        }

        data = None
        if json_data is not None:
            data = json.dumps(json_data).encode("utf-8")
            headers["Content-Type"] = "application/json"

        req = urllib.request.Request(url, data=data, headers=headers, method=method)

        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                body = resp.read().decode("utf-8")
                return json.loads(body)
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8")
            if e.code == 401:
                raise AuthenticationError(f"Invalid or missing API key: {body}")
            elif e.code == 429:
                raise QuotaExceededError(f"Monthly API quota exceeded: {body}")
            elif e.code == 403:
                raise QuotaExceededError(f"Forbidden / Limit reached: {body}")
            else:
                raise APIResponseError(f"API Error (HTTP {e.code}): {body}", status_code=e.code, response_body=body)
        except Exception as e:
            raise APIResponseError(f"Network error connecting to IsBrokerSafe: {e}")

    def check(self, query: str) -> BrokerCheckResult:
        """
        Perform a comprehensive forensic audit on a broker domain or name across 82+ global authorities.

        Args:
            query (str): Domain (e.g. 'exness.com') or company name (e.g. 'Interactive Brokers').

        Returns:
            BrokerCheckResult: Structured audit result including score, status, warnings, and WHOIS.
        """
        clean_query = query.strip().lower().replace("https://", "").replace("http://", "").split("/")[0]
        data = self._request("/api/v1/broker/check", params={"query": clean_query})
        return BrokerCheckResult.from_dict(data)

    def get_licensed(self, query: Optional[str] = None, regulator: Optional[str] = None, limit: int = 100) -> Dict[str, Any]:
        """
        Query the 737+ official licensed & regulated brokers registry (FCA, SEC/NFA, FINMA, CySEC, ASIC, BaFin, etc.).

        Args:
            query (str, optional): Filter by broker name, domain, or license number.
            regulator (str, optional): Filter by regulator code (e.g. 'FINMA', 'CySEC', 'FCA', 'ASIC').
            limit (int, optional): Number of records to retrieve (default 100).

        Returns:
            dict: Paginated registry of licensed financial institutions.
        """
        params: Dict[str, Any] = {"limit": limit}
        if query:
            params["query"] = query
        if regulator:
            params["regulator"] = regulator
        return self._request("/api/v1/broker/licensed", params=params)

    def get_warnings(self, regulator: Optional[str] = None, limit: int = 50) -> List[RegulatoryWarning]:
        """
        Retrieve live regulatory warnings and blacklisted entities across 82+ global authorities (IOSCO).

        Args:
            regulator (str, optional): Filter by regulator code (fca, cysec, consob, asic, sfc, sec, cssf, fsma, iosco).
            limit (int, optional): Number of records to retrieve (default 50).

        Returns:
            List[RegulatoryWarning]: List of active regulatory warnings.
        """
        params: Dict[str, Any] = {"limit": limit}
        if regulator:
            params["regulator"] = regulator
        data = self._request("/api/v1/regulatory/warnings", params=params)
        results = data.get("results", []) if isinstance(data, dict) else []
        return [RegulatoryWarning.from_dict(w) for w in results]

    def get_stats(self) -> GlobalStats:
        """
        Get real-time global database statistics.

        Returns:
            GlobalStats: Total audited brokers, blacklist counts, and monitored regulators.
        """
        data = self._request("/api/v1/stats")
        return GlobalStats.from_dict(data)

    def generate_free_key(self, email: str, use_case: str = "python_sdk") -> Dict[str, Any]:
        """
        Request a free API key with 100 free requests per month.

        Args:
            email (str): Your developer email address.
            use_case (str): Brief description of your integration.

        Returns:
            dict: API key generation result.
        """
        return self._request("/api/v1/keys/generate", method="POST", json_data={"email": email, "use_case": use_case})


class AsyncClient(Client):
    """
    Asynchronous IsBrokerSafe API Client (aiohttp / asyncio compatible).
    """
    pass
