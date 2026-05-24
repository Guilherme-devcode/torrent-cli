import requests
from bs4 import BeautifulSoup
from urllib.parse import quote, urljoin
from .base import TorrentResult
from config import REQUEST_TIMEOUT, MAX_RESULTS_PER_SOURCE

BASE_URL = "https://kickasstorrents.to"

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
        url = f"{BASE_URL}/usearch/{quote(query)} category:movies/"
        resp = requests.get(url, headers=_HEADERS, timeout=REQUEST_TIMEOUT)
        if resp.status_code != 200:
            return []

        soup = BeautifulSoup(resp.text, "lxml")
        rows = soup.select("table.data tr:not(:first-child)")

        for row in rows[:MAX_RESULTS_PER_SOURCE]:
            try:
                title_el = row.select_one("a.cellMainLink")
                magnet_el = row.select_one("a[href^='magnet:']")
                if not title_el or not magnet_el:
                    continue

                name = title_el.get_text(strip=True)
                magnet = magnet_el["href"]
                tds = row.find_all("td")

                size = tds[1].get_text(strip=True) if len(tds) > 1 else "?"
                seeds = _safe_int(tds[4].get_text()) if len(tds) > 4 else 0
                leeches = _safe_int(tds[5].get_text()) if len(tds) > 5 else 0

                results.append(
                    TorrentResult(
                        title=name,
                        quality=_detect_quality(name),
                        size=size,
                        seeders=seeds,
                        leechers=leeches,
                        magnet=magnet,
                        source="KAT",
                    )
                )
            except Exception:
                continue

    except Exception:
        pass

    return results
