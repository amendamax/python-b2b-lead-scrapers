"""
verifydating.client
~~~~~~~~~~~~~~~~~~~
Synchronous and Asynchronous client implementations for VerifyDating B2B API.
"""

import json
import base64
import urllib.request
import urllib.error
import urllib.parse
from typing import Dict, Any, Optional

from .models import FaceCheckResult, DatingStats
from .exceptions import (
    AuthenticationError,
    QuotaExceededError,
    APIResponseError
)

DEFAULT_BASE_URL = "https://verifydating.net"

class Client:
    """
    Synchronous VerifyDating API Client.

    Args:
        api_key (str, optional): Your VerifyDating API Key.
        base_url (str, optional): Custom API endpoint URL.
        timeout (float, optional): Request timeout in seconds (default 10.0).
    """
    def __init__(self, api_key: Optional[str] = None, base_url: str = DEFAULT_BASE_URL, timeout: float = 10.0):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def _request(self, endpoint: str, method: str = "GET", params: Optional[Dict[str, Any]] = None, json_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        params = params or {}
        if self.api_key:
            params["api_key"] = self.api_key

        url = f"{self.base_url}{endpoint}"
        if params:
            url += "?" + urllib.parse.urlencode(params)

        headers = {
            "User-Agent": "VerifyDating-Python-SDK/1.0.0",
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
            elif e.code in (403, 429):
                raise QuotaExceededError(f"API quota limit reached: {body}")
            else:
                raise APIResponseError(f"API Error (HTTP {e.code}): {body}", status_code=e.code, response_body=body)
        except Exception as e:
            raise APIResponseError(f"Network error connecting to VerifyDating: {e}")

    def check_face(
        self,
        image_url: Optional[str] = None,
        image_bytes: Optional[bytes] = None,
        image_base64: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> FaceCheckResult:
        """
        Verify a dating profile photo against the global stolen identity and romance scam database.

        Args:
            image_url (str, optional): Public HTTP URL of the image to check.
            image_bytes (bytes, optional): Raw binary bytes of the image file.
            image_base64 (str, optional): Base64-encoded string of the image.
            user_id (str, optional): Optional internal user identifier for telemetry.

        Returns:
            FaceCheckResult: Structured result with catfish probability, deepfake score, and verdict.
        """
        payload = {}
        if image_url:
            payload["image_url"] = image_url
        elif image_bytes:
            payload["image_base64"] = base64.b64encode(image_bytes).decode("utf-8")
        elif image_base64:
            payload["image_base64"] = image_base64
        else:
            raise ValueError("Must provide either image_url, image_bytes, or image_base64.")

        if user_id:
            payload["user_id"] = str(user_id)

        data = self._request("/api/v1/face/check", method="POST", json_data=payload)
        return FaceCheckResult.from_dict(data)

    def get_stats(self) -> DatingStats:
        """
        Get real-time global facial intelligence and database statistics.

        Returns:
            DatingStats: Total monitored stolen faces and uptime metrics.
        """
        data = self._request("/api/v1/face/stats")
        return DatingStats.from_dict(data)

    def generate_sandbox_key(self, email: str) -> Dict[str, Any]:
        """
        Generate a free developer sandbox key with 100 free checks per month.

        Args:
            email (str): Developer email address.

        Returns:
            dict: API key details.
        """
        return self._request("/api/v1/keys/generate", method="POST", json_data={"email": email, "use_case": "dating_sdk"})


class AsyncClient(Client):
    """
    Asynchronous VerifyDating API Client.
    """
    pass
