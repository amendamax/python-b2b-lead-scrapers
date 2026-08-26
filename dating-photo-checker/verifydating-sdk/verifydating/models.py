"""
verifydating.models
~~~~~~~~~~~~~~~~~~~
Data models representing VerifyDating API responses.
"""

from typing import Dict, Any, Optional

class ForensicDetails:
    def __init__(self, data: Dict[str, Any]):
        self.matches_count: int = data.get("matches_count", 0)
        self.deepfake_probability: float = data.get("deepfake_probability", 0.0)
        self.stolen_photo_detected: bool = data.get("stolen_photo_detected", False)
        self.scammer_info: str = data.get("scammer_info", "")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "matches_count": self.matches_count,
            "deepfake_probability": self.deepfake_probability,
            "stolen_photo_detected": self.stolen_photo_detected,
            "scammer_info": self.scammer_info
        }

class QuotaInfo:
    def __init__(self, data: Dict[str, Any]):
        self.tier: str = data.get("tier", "free")
        self.remaining: int = data.get("remaining", 0)
        self.limit: int = data.get("limit", 100)

class FaceCheckResult:
    def __init__(self, data: Dict[str, Any]):
        self.raw_data: Dict[str, Any] = data
        self.scan_id: str = data.get("scan_id", "")
        self.scam_probability: int = data.get("scam_probability", 0)
        self.risk_level: str = data.get("risk_level", "UNKNOWN")
        self.action_recommendation: str = data.get("action_recommendation", "APPROVE_PROFILE")
        self.verdict: str = data.get("verdict", "")
        
        forensic_raw = data.get("forensic_details", {})
        self.forensic_details: ForensicDetails = ForensicDetails(forensic_raw)
        
        quota_raw = data.get("quota", {})
        self.quota: QuotaInfo = QuotaInfo(quota_raw)

    @property
    def is_catfish(self) -> bool:
        return self.scam_probability >= 70

    @property
    def is_suspicious(self) -> bool:
        return 35 <= self.scam_probability < 70

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FaceCheckResult":
        return cls(data)

class DatingStats:
    def __init__(self, data: Dict[str, Any]):
        self.monitored_stolen_faces: int = data.get("monitored_stolen_faces", 0)
        self.deepfake_scam_signatures: int = data.get("deepfake_scam_signatures", 0)
        self.verified_safe_profiles: int = data.get("verified_safe_profiles", 0)
        self.average_response_ms: int = data.get("average_response_ms", 45)
        self.uptime: str = data.get("uptime", "99.99%")

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DatingStats":
        return cls(data)
