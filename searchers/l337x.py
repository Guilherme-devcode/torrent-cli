import requests
from bs4 import BeautifulSoup
from urllib.parse import quote, urljoin
from .base import TorrentResult
from config import REQUEST_TIMEOUT, MAX_RESULTS_PER_SOURCE

BASE_URL = "https://1337x.to"

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64; rv:120.0) Gecko/20100101 Firefox/120.0"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "DNT": "1",
}

_QUALITY_TAGS = ["2160p", "4K", "UHD", "1080p", "720p", "480p", "360p", "HDCAM", "CAM"]


def _detect_quality(name: str) -> str:
    upper = name.upper()
    for tag in _QUALITY_TAGS:
        if tag.upper() in upper:
            return tag
    return "?"


def _safe_int(text: str) -> int:
    try:
        return int(text.replace(",", "").strip())
    except (ValueError, AttributeError):
        return 0


def search(query: str) -> list[TorrentResult]:
    results = []
    try:
        url = f"{BASE_URL}/search/{quote(query)}/1/"
        resp = requests.get(url, headers=_HEADERS, timeout=REQUEST_TIMEOUT)

        if resp.status_code != 200:
            return []

        soup = BeautifulSoup(resp.text, "lxml")
        rows = soup.select("table.table-list tbody tr")

        for row in rows[:MAX_RESULTS_PER_SOURCE]:
            try:
                name_el = row.select_one(".name a:last-child")
                if not name_el:
                    continue

                name = name_el.get_text(strip=True)
                detail_url = urljoin(BASE_URL, name_el["href"])
                tds = row.find_all("td")

                seeds = _safe_int(tds[1].get_text()) if len(tds) > 1 else 0
                leeches = _safe_int(tds[2].get_text()) if len(tds) > 2 else 0

                # Size cell has a hidden <span> with extra text — grab only first text node
                size = "?"
                if len(tds) > 4:
                    size_td = tds[4]
                    for span in size_td.find_all("span"):
                        span.decompose()
                    size = size_td.get_text(strip=True) or "?"

                results.append(
                    TorrentResult(
                        title=name,
                        quality=_detect_quality(name),
                        size=size,
                        seeders=seeds,
                        leechers=leeches,
                        magnet="",  # fetched lazily
                        source="1337x",
                        detail_url=detail_url,
                    )
                )
            except Exception:
                continue

    except Exception:
        pass

    return results


def get_magnet(detail_url: str) -> str:
    """Fetch the magnet link from a 1337x torrent detail page."""
    try:
        resp = requests.get(detail_url, headers=_HEADERS, timeout=REQUEST_TIMEOUT)
        soup = BeautifulSoup(resp.text, "lxml")
        magnet_el = soup.find("a", href=lambda h: h and h.startswith("magnet:"))
        if magnet_el:
            return magnet_el["href"]
    except Exception:
        pass
    return ""
