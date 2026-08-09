from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field

class EmailStatus(str, Enum):
    DISCOVERED = "DISCOVERED"
    PATTERN_GENERATED = "PATTERN_GENERATED"
    DNS_VALID = "DNS_VALID"
    DNS_INVALID = "DNS_INVALID"
    SMTP_ACCEPTED = "SMTP_ACCEPTED"
    SMTP_REJECTED = "SMTP_REJECTED"
    SMTP_INCONCLUSIVE = "SMTP_INCONCLUSIVE"
    CATCH_ALL = "CATCH_ALL"
    UNKNOWN = "UNKNOWN"

class Confidence(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"

class CandidateLead(BaseModel):
    business_name: str
    website: str
    domain: str
    person_name: Optional[str] = None
    person_title: Optional[str] = None
    linkedin_url: Optional[str] = None
    linkedin_match_score: int = 0
    linkedin_match_evidence: List[str] = Field(default_factory=list)
    email: Optional[str] = None
    email_candidates: List[str] = Field(default_factory=list)
    email_source: str = "none"
    email_generation_method: str = ""
    mx_valid: bool = False
    email_status: EmailStatus = EmailStatus.UNKNOWN
    email_confidence: Confidence = Confidence.LOW
    crawl_ok: bool = False
    error: str = ""
