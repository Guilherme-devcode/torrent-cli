import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote
from .base import TorrentResult
from config import TRACKERS, REQUEST_TIMEOUT, MAX_RESULTS_PER_SOURCE

BASE_URL = "https://www.limetorrents.lol"

_HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:120.0) Gecko/20100101 Firefox/120.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "DNT": "1",
}

_HASH_RE = re.compile(r"/torrent/([A-Fa-f0-9]{40})\.torrent", re.IGNORECASE)

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
        slug = query.replace(" ", "-")
        resp = requests.get(
            f"{BASE_URL}/search/movies/{quote(slug)}/",
            headers=_HEADERS,
            timeout=REQUEST_TIMEOUT,
        )
        if resp.status_code != 200:
            return []

        soup = BeautifulSoup(resp.text, "lxml")
        table = soup.find("table", class_="table2")
        if not table:
            return []

        for row in table.find_all("tr")[1:MAX_RESULTS_PER_SOURCE + 1]:
            try:
                tds = row.find_all("td")
                if len(tds) < 4:
                    continue

                torrent_link = tds[0].find("a", class_="csprite_dl14")
                title_link = tds[0].select_one("div.tt-name a:not(.csprite_dl14)")
                if not title_link or not torrent_link:
                    continue

                name = title_link.get_text(strip=True)
                torrent_href = torrent_link.get("href", "")
                match = _HASH_RE.search(torrent_href)
                if not match:
                    continue

                info_hash = match.group(1).upper()
                encoded_name = quote(name)
                magnet = f"magnet:?xt=urn:btih:{info_hash}&dn={encoded_name}&tr={TRACKERS}"

                size = tds[2].get_text(strip=True) if len(tds) > 2 else "?"
                seeds = _safe_int(tds[3].get_text()) if len(tds) > 3 else 0
                leeches = _safe_int(tds[4].get_text()) if len(tds) > 4 else 0

                results.append(
                    TorrentResult(
                        title=name,
                        quality=_detect_quality(name),
                        size=size,
                        seeders=seeds,
                        leechers=leeches,
                        magnet=magnet,
                        source="Lime",
                    )
                )
            except Exception:
                continue

    except Exception:
        pass

    return results
