import logging
import time

logger = logging.getLogger(__name__)
try:
    from ddgs import DDGS
except ImportError:
    from duckduckgo_search import DDGS

def find_linkedin_candidates(company_name, domain, max_results=3, sleep_sec=2.0):
    queries = [
        f'site:linkedin.com/in ("CEO" OR "Owner" OR "Founder") "{company_name}"',
        f'site:linkedin.com/in ("President" OR "Managing Director") "{company_name}"',
        f'site:linkedin.com/in "{company_name}"',
    ]
    out, seen = [], set()
    for q in queries:
        try:
            with DDGS() as ddgs:
                for r in ddgs.text(q, max_results=max_results):
                    href = r.get("href", "")
                    if "linkedin.com/in/" in href and href not in seen:
                        seen.add(href)
                        out.append({"url": href, "snippet": f"{r.get('title', '')} {r.get('body', '')}"})
        except Exception as e:
            logger.warning(f"dork failed: {e}")
        time.sleep(sleep_sec)
    return out
