import os
from pathlib import Path

DOWNLOAD_DIR = os.environ.get(
    "TORRENT_DOWNLOAD_DIR",
    str(Path.home() / "Downloads" / "Movies")
)

GAMES_DOWNLOAD_DIR = os.environ.get(
    "TORRENT_GAMES_DIR",
    str(Path.home() / "Downloads" / "Games")
)

TRACKERS = "&tr=".join([
    "udp://tracker.opentrackr.org:1337/announce",
    "udp://open.tracker.cl:1337/announce",
    "udp://tracker.openbittorrent.com:6969/announce",
    "http://tracker.openbittorrent.com:80/announce",
    "udp://opentracker.i2p.rocks:6969/announce",
    "udp://exodus.desync.com:6969/announce",
    "udp://tracker.torrent.eu.org:451/announce",
    "udp://tracker.tiny-vps.com:6969/announce",
    "udp://tracker.moeking.me:6969/announce",
    "udp://tracker.internetwarriors.net:1337/announce",
    "udp://9.rarbg.to:2920/announce",
    "udp://tracker.cyberia.is:6969/announce",
])

REQUEST_TIMEOUT = 12
MAX_RESULTS_PER_SOURCE = 20
