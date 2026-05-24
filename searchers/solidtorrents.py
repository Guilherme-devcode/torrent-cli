import requests
from urllib.parse import quote
from .base import TorrentResult
from config import TRACKERS, REQUEST_TIMEOUT, MAX_RESULTS_PER_SOURCE

API_URL = "https://solidtorrents.net/api/v1/search"

_HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:120.0) Gecko/20100101 Firefox/120.0",
}

_QUALITY_TAGS = ["2160p", "4K", "UHD", "1080p", "720p", "480p", "360p", "HDCAM", "CAM"]


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
            params={"q": query, "category": "VIDEO", "sort": "seedCount"},
            headers=_HEADERS,
            timeout=REQUEST_TIMEOUT,
        )
        resp.raise_for_status()
        data = resp.json()

        for item in data.get("results", [])[:MAX_RESULTS_PER_SOURCE]:
            info_hash = item.get("infohash", "")
            if not info_hash:
                continue

            name = item.get("title", "Unknown")
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
                    source="Solid",
                )
            )
    except Exception:
        pass

    return results
