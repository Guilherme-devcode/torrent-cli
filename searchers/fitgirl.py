import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote
from .base import TorrentResult
from config import REQUEST_TIMEOUT, MAX_RESULTS_PER_SOURCE

BASE_URL = "https://fitgirl-repacks.site"

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64; rv:120.0) Gecko/20100101 Firefox/120.0"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Referer": BASE_URL,
}


def _extract_size(text: str) -> str:
    m = re.search(r'[Rr]epack\s+[Ss]ize\s*:?\s*([0-9.,]+\s*(?:GB|MB|TB))', text)
    if m:
        return m.group(1).strip()
    m = re.search(r'([0-9.,]+\s*(?:GB|MB))', text)
    if m:
        return m.group(1).strip()
    return "?"


def search(query: str) -> list[TorrentResult]:
    results = []
    try:
        url = f"{BASE_URL}/?s={quote(query)}"
        resp = requests.get(url, headers=_HEADERS, timeout=REQUEST_TIMEOUT)
        if resp.status_code != 200:
            return []

        soup = BeautifulSoup(resp.text, "lxml")
        articles = soup.select("article.post, article.type-post")[:MAX_RESULTS_PER_SOURCE]

        for article in articles:
            try:
                title_el = article.select_one(".entry-title a, h1.entry-title a, h2.entry-title a")
                if not title_el:
                    continue

                title = title_el.get_text(strip=True)
                detail_url = title_el["href"]

                excerpt_el = article.select_one(".entry-content, .entry-summary, .post-content")
                size = "?"
                if excerpt_el:
                    size = _extract_size(excerpt_el.get_text())

                results.append(TorrentResult(
                    title=title,
                    quality="Repack",
                    size=size,
                    seeders=0,
                    leechers=0,
                    magnet="",
                    source="FitGirl",
                    detail_url=detail_url,
                ))
            except Exception:
                continue

    except Exception:
        pass

    return results


def get_magnet(detail_url: str) -> str:
    magnets = get_all_magnets(detail_url)
    return magnets[0][1] if magnets else ""


def get_all_magnets(detail_url: str) -> list[tuple[str, str]]:
    """Return list of (label, magnet_url) from a FitGirl repack detail page."""
    results = []
    try:
        resp = requests.get(detail_url, headers=_HEADERS, timeout=REQUEST_TIMEOUT)
        soup = BeautifulSoup(resp.text, "lxml")

        for a in soup.find_all("a", href=lambda h: h and h.startswith("magnet:")):
            label = a.get_text(strip=True) or "Download"
            results.append((label, a["href"]))

    except Exception:
        pass

    return results
