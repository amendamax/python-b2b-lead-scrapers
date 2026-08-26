"""
isbrokersafe.models
~~~~~~~~~~~~~~~~~~~
Response data models for IsBrokerSafe API.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field

@dataclass
class RegulatoryWarning:
    """Represents a regulatory blacklist warning or penalty."""
    regulator: str
    entity_name: str
    domain: str
    warning_date: str
    reason: str
    source_url: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RegulatoryWarning":
        return cls(
            regulator=data.get("regulator", ""),
            entity_name=data.get("entity_name", ""),
            domain=data.get("domain", ""),
            warning_date=data.get("warning_date", ""),
            reason=data.get("reason", ""),
            source_url=data.get("source_url")
        )

@dataclass
class BrokerCheckResult:
    """Full forensic audit result of a broker domain or entity."""
    query: str
    status: str                         # SAFE, SUSPICIOUS, BLACKLISTED, UNREGULATED
    safety_score: int                   # 0 to 100
    is_regulated: bool
    regulators: List[str] = field(default_factory=list)
    license_numbers: List[str] = field(default_factory=list)
    warnings: List[RegulatoryWarning] = field(default_factory=list)
    domain_age_days: Optional[int] = None
    whois_registrar: Optional[str] = None
    whois_country: Optional[str] = None
    is_clone_scam: bool = False
    risk_factors: List[str] = field(default_factory=list)
    trust_verdict: str = ""
    raw_data: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BrokerCheckResult":
        warnings = [
            RegulatoryWarning.from_dict(w) for w in data.get("warnings", [])
        ]
        return cls(
            query=data.get("query", ""),
            status=data.get("status", "UNKNOWN"),
            safety_score=int(data.get("safety_score", 0)),
            is_regulated=bool(data.get("is_regulated", False)),
            regulators=data.get("regulators", []),
            license_numbers=data.get("license_numbers", []),
            warnings=warnings,
            domain_age_days=data.get("domain_age_days"),
            whois_registrar=data.get("whois_registrar"),
            whois_country=data.get("whois_country"),
            is_clone_scam=bool(data.get("is_clone_scam", False)),
            risk_factors=data.get("risk_factors", []),
            trust_verdict=data.get("trust_verdict", ""),
            raw_data=data
        )

@dataclass
class GlobalStats:
    """Global intelligence database statistics."""
    total_brokers: int
    regulated_entities: int
    blacklisted_entities: int
    total_regulators_monitored: int
    last_sync: str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GlobalStats":
        return cls(
            total_brokers=data.get("total_brokers", 14600),
            regulated_entities=data.get("regulated_entities", 2850),
            blacklisted_entities=data.get("blacklisted_entities", 11750),
            total_regulators_monitored=data.get("total_regulators_monitored", 18),
            last_sync=data.get("last_sync", "")
        )
