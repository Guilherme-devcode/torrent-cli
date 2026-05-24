import requests
from bs4 import BeautifulSoup
from urllib.parse import quote
from .base import TorrentResult
from config import REQUEST_TIMEOUT, MAX_RESULTS_PER_SOURCE

BASE_URL = "https://torrentgalaxy.to"

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
        resp = requests.get(
            f"{BASE_URL}/torrents.php",
            params={"search": query, "cat": "3", "sort": "seeders", "order": "desc"},
            headers=_HEADERS,
            timeout=REQUEST_TIMEOUT,
        )
        if resp.status_code != 200:
            return []

        soup = BeautifulSoup(resp.text, "lxml")
        rows = soup.select("div.tgxtablerow")

        for row in rows[:MAX_RESULTS_PER_SOURCE]:
            try:
                title_el = row.select_one("a.txlight")
                magnet_el = row.select_one("a[href^='magnet:']")
                if not title_el or not magnet_el:
                    continue

                name = title_el.get_text(strip=True)
                magnet = magnet_el["href"]

                seeds_el = row.select_one("font.tgxtableseeds")
                leeches_el = row.select_one("font.tgxtableleeches")
                size_el = row.select_one("span.badge-secondary")

                results.append(
                    TorrentResult(
                        title=name,
                        quality=_detect_quality(name),
                        size=size_el.get_text(strip=True) if size_el else "?",
                        seeders=_safe_int(seeds_el.get_text()) if seeds_el else 0,
                        leechers=_safe_int(leeches_el.get_text()) if leeches_el else 0,
                        magnet=magnet,
                        source="TGx",
                    )
                )
            except Exception:
                continue

    except Exception:
        pass

    return results
