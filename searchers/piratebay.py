import requests
from urllib.parse import quote
from .base import TorrentResult
from config import TRACKERS, REQUEST_TIMEOUT, MAX_RESULTS_PER_SOURCE

API_URL = "https://apibay.org/q.php"

_NO_RESULT_SENTINEL = "No results returned"

_QUALITY_TAGS = ["2160p", "4K", "UHD", "1080p", "720p", "480p", "360p", "HDCAM", "CAM", "DVDSCR"]


def _detect_quality(name: str) -> str:
    upper = name.upper()
    for tag in _QUALITY_TAGS:
        if tag.upper() in upper:
            return tag
    return "?"


def _format_size(size_bytes: int) -> str:
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes //= 1024
    return f"{size_bytes:.1f} PB"


def search(query: str) -> list[TorrentResult]:
    results = []
    try:
        resp = requests.get(
            API_URL,
            params={"q": query, "cat": "200"},  # cat 200 = Video > Movies
            timeout=REQUEST_TIMEOUT,
        )
        resp.raise_for_status()
        data = resp.json()

        if not data or (len(data) == 1 and data[0].get("name") == _NO_RESULT_SENTINEL):
            return []

        for item in data[:MAX_RESULTS_PER_SOURCE]:
            info_hash = item.get("info_hash", "")
            name = item.get("name", "Unknown")
            encoded_name = quote(name)
            magnet = f"magnet:?xt=urn:btih:{info_hash}&dn={encoded_name}&tr={TRACKERS}"

            results.append(
                TorrentResult(
                    title=name,
                    quality=_detect_quality(name),
                    size=_format_size(int(item.get("size", 0))),
                    seeders=int(item.get("seeders", 0)),
                    leechers=int(item.get("leechers", 0)),
                    magnet=magnet,
                    source="TPB",
                )
            )
    except Exception:
        pass

    return results
