import logging
import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/126.0 Safari/537.36"}
PATHS = ["", "about", "about-us", "team", "contact", "leadership"]

def crawl_website(base_url: str, timeout: int = 10) -> list:
    pages, base = [], base_url.rstrip("/")
    for path in PATHS:
        url = base if path == "" else f"{base}/{path}"
        try:
            r = requests.get(url, headers=HEADERS, timeout=timeout)
            if r.status_code == 200:
                soup = BeautifulSoup(r.text, "html.parser")
                for t in soup(["script", "style"]):
                    t.decompose()
                pages.append({"url": r.url, "text": soup.get_text(" ", strip=True), "html": r.text})
        except Exception as e:
            logger.debug(f"crawl fail {url}: {e}")
    return pages
