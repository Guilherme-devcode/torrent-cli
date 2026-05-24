import requests
from urllib.parse import quote
from .base import TorrentResult
from config import TRACKERS, REQUEST_TIMEOUT, MAX_RESULTS_PER_SOURCE

API_URL = "https://yts.mx/api/v2/list_movies.json"


def search(query: str) -> list[TorrentResult]:
    results = []
    try:
        resp = requests.get(
            API_URL,
            params={"query_term": query, "limit": MAX_RESULTS_PER_SOURCE, "sort_by": "seeds"},
            timeout=REQUEST_TIMEOUT,
        )
        resp.raise_for_status()
        data = resp.json()

        if data.get("status") != "ok":
            return []

        movies = data.get("data", {}).get("movies") or []

        for movie in movies:
            for torrent in movie.get("torrents", []):
                info_hash = torrent.get("hash", "")
                encoded_name = quote(movie["title_english"])
                magnet = f"magnet:?xt=urn:btih:{info_hash}&dn={encoded_name}&tr={TRACKERS}"
                quality = torrent.get("quality", "?")
                codec = torrent.get("video_codec", "")
                label = f"{quality} {codec}".strip()

                results.append(
                    TorrentResult(
                        title=movie["title_english"],
                        quality=label,
                        size=torrent.get("size", "?"),
                        seeders=torrent.get("seeds", 0),
                        leechers=torrent.get("peers", 0),
                        magnet=magnet,
                        source="YTS",
                        year=movie.get("year"),
                        imdb_rating=float(movie.get("rating", 0)) or None,
                    )
                )
    except Exception:
        pass

    return results
