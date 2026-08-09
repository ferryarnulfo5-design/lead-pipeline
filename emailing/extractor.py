import re

EMAIL_RE = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
JUNK = {"example.com", "sentry.io", "wixpress.com", "squarespace.com", "schema.org", "wordpress.org",
        "woocommerce.com", "godaddy.com", "cloudflare.com", "google.com", "gmail.com", "yahoo.com",
        "hotmail.com", "outlook.com", "aol.com"}

def extract_emails(pages: list) -> list:
    found = set()
    for p in pages:
        blob = (p.get("html") or "") + " " + (p.get("text") or "")
        for m in EMAIL_RE.findall(blob):
            m = m.rstrip(".,;:)").lower()
            dom = m.split("@")[-1]
            if dom in JUNK or m.endswith((".png", ".jpg", ".jpeg", ".gif", ".svg", ".css", ".js")):
                continue
            found.add(m)
    return sorted(found)
