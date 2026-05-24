import shutil
import subprocess
from pathlib import Path

from rich.console import Console

import config

console = Console()


def _has(cmd: str) -> bool:
    return shutil.which(cmd) is not None


def _ensure_dir(path: str) -> None:
    Path(path).mkdir(parents=True, exist_ok=True)


def _with_trackers(magnet: str) -> str:
    if not config.TRACKERS:
        return magnet
    sep = "&" if "?" in magnet else "?"
    return f"{magnet}{sep}tr={config.TRACKERS}"


def download(magnet: str, download_dir: str) -> None:
    _ensure_dir(download_dir)
    magnet = _with_trackers(magnet)

    if _has("aria2c"):
        _aria2c(magnet, download_dir)
    elif _has("transmission-cli"):
        _transmission(magnet, download_dir)
    elif _has("qbittorrent-nox"):
        _qbittorrent(magnet, download_dir)
    else:
        _no_client(magnet)


def _aria2c(magnet: str, download_dir: str) -> None:
    console.print(f"\n[bold green]Iniciando download com aria2c[/bold green]")
    console.print(f"[dim]Pasta: {download_dir}[/dim]\n")
    subprocess.run(
        [
            "aria2c",
            "--seed-time=0",
            "--max-connection-per-server=16",
            "--split=16",
            "--min-split-size=1M",
            f"--dir={download_dir}",
            "--console-log-level=notice",
            "--bt-enable-lpd=true",
            "--enable-dht=true",
            "--enable-peer-exchange=true",
            "--bt-save-metadata=true",
            magnet,
        ]
    )


def _transmission(magnet: str, download_dir: str) -> None:
    console.print(f"\n[bold green]Iniciando download com transmission-cli[/bold green]")
    console.print(f"[dim]Pasta: {download_dir}[/dim]\n")
    subprocess.run([
        "transmission-cli",
        f"--download-dir={download_dir}",
        "--dht",
        "--lpd",
        "--utp",
        magnet,
    ])


def _qbittorrent(magnet: str, download_dir: str) -> None:
    console.print(f"\n[bold green]Iniciando download com qbittorrent-nox[/bold green]")
    console.print(f"[dim]Pasta: {download_dir}[/dim]\n")
    subprocess.run(["qbittorrent-nox", "--save-path", download_dir, magnet])


def _no_client(magnet: str) -> None:
    console.print("\n[bold red]Nenhum cliente torrent encontrado![/bold red]")
    console.print("\nInstale um dos seguintes e rode o setup novamente:")
    console.print("  [yellow]sudo apt install aria2[/yellow]         ← recomendado")
    console.print("  [yellow]sudo apt install transmission-cli[/yellow]")
    console.print("  [yellow]sudo apt install qbittorrent-nox[/yellow]")
    console.print(f"\n[bold]Magnet link para download manual:[/bold]")
    console.print(f"[dim]{magnet}[/dim]")
