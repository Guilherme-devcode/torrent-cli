from dataclasses import dataclass, field
from typing import Optional


@dataclass
class TorrentResult:
    title: str
    quality: str
    size: str
    seeders: int
    leechers: int
    magnet: str
    source: str
    year: Optional[int] = None
    imdb_rating: Optional[float] = None
    detail_url: Optional[str] = None  # used for lazy magnet fetch (1337x)
