import dns.resolver
from models.lead import EmailStatus, Confidence

def check_mx(domain: str) -> bool:
    try:
        return len(dns.resolver.resolve(domain, "MX", lifetime=10)) > 0
    except Exception:
        try:
            return len(dns.resolver.resolve(domain, "A", lifetime=10)) > 0
        except Exception:
            return False

def classify_email(email, source, mx_valid):
    if not email:
        return EmailStatus.UNKNOWN
    if not mx_valid:
        return EmailStatus.DNS_INVALID
    return EmailStatus.DNS_VALID if source == "website_scrape" else EmailStatus.PATTERN_GENERATED

def final_confidence(linkedin_score, email_status, email_source="none"):
    strong, moderate = linkedin_score >= 75, linkedin_score >= 55
    if email_status == EmailStatus.SMTP_ACCEPTED:
        return Confidence.HIGH if strong else Confidence.MEDIUM
    if email_status == EmailStatus.DNS_VALID and email_source == "website_scrape":
        return Confidence.HIGH if strong else (Confidence.MEDIUM if moderate else Confidence.LOW)
    if email_status in (EmailStatus.DNS_VALID, EmailStatus.PATTERN_GENERATED):
        return Confidence.MEDIUM if moderate else Confidence.LOW
    return Confidence.LOW
