#!/usr/bin/env python3
"""
torrent-cli — busca e baixa filmes e jogos via torrent direto no terminal.
Filmes: YTS · The Pirate Bay · 1337x · SolidTorrents · LimeTorrents
Jogos:  FitGirl Repacks
"""

import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

from rich import box
from rich.columns import Columns
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt
from rich.table import Table
from rich.text import Text

import config
from downloader import download
from searchers.base import TorrentResult
from searchers import yts, piratebay, l337x, solidtorrents, limetorrents
from searchers import fitgirl

console = Console()

_MOVIE_SOURCES = [
    ("YTS", yts.search),
    ("The Pirate Bay", piratebay.search),
    ("1337x", l337x.search),
    ("SolidTorrents", solidtorrents.search),
    ("LimeTorrents", limetorrents.search),
]

_GAME_SOURCES = [
    ("FitGirl", fitgirl.search),
]

_SEEDS_THRESHOLD_HIGH = 100
_SEEDS_THRESHOLD_MED = 10


def _banner() -> None:
    title = Text("TORRENT-CLI", style="bold cyan", justify="center")
    subtitle = Text(
        "Filmes · YTS · TPB · 1337x · Solid · Lime   |   Jogos · FitGirl Repacks",
        style="dim",
        justify="center",
    )
    console.print()
    console.print(Panel.fit(title, border_style="cyan"))
    console.print(subtitle)
    console.print()


def _pick_mode() -> str:
    """Show mode selection menu and return 'filme' or 'jogo'."""
    console.print(
        Panel(
            "[bold cyan][F][/bold cyan] Filme / Série\n"
            "[bold magenta][J][/bold magenta] Jogo [dim](FitGirl Repacks)[/dim]",
            title="[bold]O que deseja buscar?[/bold]",
            border_style="dim",
            expand=False,
        )
    )
    while True:
        raw = Prompt.ask(
            "[bold]Modo[/bold] [dim]· 'q' para sair[/dim]",
            default="f",
        ).strip().lower()

        if raw in ("q", "sair", "exit", "quit"):
            raise SystemExit(0)
        if raw in ("f", "filme", "filmes", "movie", "movies"):
            return "filme"
        if raw in ("j", "jogo", "jogos", "game", "games"):
            return "jogo"

        console.print("[red]Digite 'f' para filme ou 'j' para jogo[/red]")


def _search_all(query: str, sources: list) -> list[TorrentResult]:
    results: list[TorrentResult] = []

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
        console=console,
    ) as prog:
        prog.add_task(f"[cyan]Buscando: [bold]{query}[/bold]", total=None)

        with ThreadPoolExecutor(max_workers=len(sources)) as ex:
            futures = {ex.submit(fn, query): name for name, fn in sources}
            for future in as_completed(futures):
                name = futures[future]
                try:
                    found = future.result()
                    results.extend(found)
                    status = f"[green]✓[/green] {len(found)} resultado(s)"
                except Exception:
                    status = "[red]✗ erro[/red]"
                prog.console.print(f"  {name}: {status}")

    return results


def _seeds_color(n: int) -> str:
    if n >= _SEEDS_THRESHOLD_HIGH:
        return "bright_green"
    if n >= _SEEDS_THRESHOLD_MED:
        return "green"
    if n > 0:
        return "yellow"
    return "red"


def _display_movie_results(results: list[TorrentResult], query: str) -> None:
    if not results:
        console.print(f"\n[red]Nenhum resultado para:[/red] [bold]{query}[/bold]")
        return

    table = Table(
        title=f"Filmes: [bold cyan]{query}[/bold cyan]",
        box=box.ROUNDED,
        border_style="blue",
        header_style="bold magenta",
        show_lines=False,
        expand=False,
    )
    table.add_column("#", style="dim", width=4, justify="right")
    table.add_column("Título", min_width=28, max_width=52, no_wrap=True)
    table.add_column("Qualidade", style="cyan", width=11)
    table.add_column("Tamanho", style="yellow", width=10)
    table.add_column("Seeds", width=7, justify="right")
    table.add_column("Peers", style="red", width=7, justify="right")
    table.add_column("IMDB", style="yellow", width=5)
    table.add_column("Fonte", style="blue", width=7)

    for i, r in enumerate(results, 1):
        color = _seeds_color(r.seeders)
        seeds_cell = f"[{color}]{r.seeders}[/{color}]"
        rating = f"{r.imdb_rating:.1f}" if r.imdb_rating else "-"
        year = f" ({r.year})" if r.year else ""
        title = (r.title[:50] + year)[:52]

        table.add_row(
            str(i),
            title,
            r.quality,
            r.size,
            seeds_cell,
            str(r.leechers),
            rating,
            r.source,
        )

    console.print()
    console.print(table)
    console.print(f"[dim]  {len(results)} resultado(s) encontrado(s)[/dim]\n")


def _display_game_results(results: list[TorrentResult], query: str) -> None:
    if not results:
        console.print(f"\n[red]Nenhum jogo encontrado para:[/red] [bold]{query}[/bold]")
        return

    table = Table(
        title=f"Jogos (FitGirl): [bold magenta]{query}[/bold magenta]",
        box=box.ROUNDED,
        border_style="magenta",
        header_style="bold cyan",
        show_lines=False,
        expand=False,
    )
    table.add_column("#", style="dim", width=4, justify="right")
    table.add_column("Título", min_width=36, max_width=64, no_wrap=True)
    table.add_column("Tamanho Repack", style="yellow", width=16)
    table.add_column("Fonte", style="magenta", width=9)

    for i, r in enumerate(results, 1):
        table.add_row(str(i), r.title[:64], r.size, r.source)

    console.print()
    console.print(table)
    console.print(f"[dim]  {len(results)} jogo(s) encontrado(s)[/dim]\n")


def _resolve_magnet(result: TorrentResult) -> str:
    if result.magnet:
        return result.magnet

    if result.source == "1337x" and result.detail_url:
        console.print("[dim]Buscando magnet link na página do torrent...[/dim]")
        magnet = l337x.get_magnet(result.detail_url)
        if magnet:
            result.magnet = magnet
            return magnet

    if result.source == "FitGirl" and result.detail_url:
        console.print("[dim]Buscando magnet links na página do FitGirl...[/dim]")
        magnets = fitgirl.get_all_magnets(result.detail_url)
        if not magnets:
            return ""
        if len(magnets) == 1:
            result.magnet = magnets[0][1]
            return result.magnet
        return _pick_fitgirl_magnet(magnets)

    return ""


def _pick_fitgirl_magnet(magnets: list[tuple[str, str]]) -> str:
    """Let the user choose among multiple FitGirl magnet links."""
    console.print("\n[bold]Links de download disponíveis:[/bold]")
    for i, (label, _) in enumerate(magnets, 1):
        console.print(f"  [cyan]{i}[/cyan]. {label or 'Download'}")

    while True:
        raw = Prompt.ask(
            f"[bold]Escolha[/bold] [dim](1-{len(magnets)})[/dim]",
            default="1",
        ).strip()
        try:
            idx = int(raw) - 1
            if 0 <= idx < len(magnets):
                return magnets[idx][1]
            console.print(f"[red]Número fora do intervalo (1-{len(magnets)})[/red]")
        except ValueError:
            console.print("[red]Digite um número válido[/red]")


def _pick_result(results: list[TorrentResult]) -> TorrentResult | None:
    while True:
        raw = Prompt.ask(
            f"[bold]Escolha[/bold] [dim]número (1-{len(results)})[/dim]"
            " [dim]· 'n' nova busca · 'm' mudar modo · 'q' sair[/dim]",
            default="n",
        ).strip().lower()

        if raw in ("n", "nova", ""):
            return None
        if raw in ("m", "modo"):
            raise _ChangeModeSignal()
        if raw in ("q", "sair", "exit"):
            raise SystemExit(0)

        try:
            idx = int(raw) - 1
            if 0 <= idx < len(results):
                return results[idx]
            console.print(f"[red]Número fora do intervalo (1-{len(results)})[/red]")
        except ValueError:
            console.print("[red]Digite um número válido[/red]")


class _ChangeModeSignal(Exception):
    pass


def _run_movie_loop() -> None:
    console.print(f"[dim]Pasta de download:[/dim] [cyan]{config.DOWNLOAD_DIR}[/cyan]")
    console.print("[dim]Altere com TORRENT_DOWNLOAD_DIR[/dim]\n")

    while True:
        query = Prompt.ask(
            "[bold blue]Filme[/bold blue] [dim](nome · 'n' nova busca · 'm' mudar modo · 'q' sair)[/dim]"
        ).strip()

        if not query:
            continue
        if query.lower() in ("q", "sair", "exit", "quit"):
            console.print("\n[bold]Até logo![/bold]")
            raise SystemExit(0)
        if query.lower() in ("m", "modo"):
            raise _ChangeModeSignal()

        results = _search_all(query, _MOVIE_SOURCES)
        results.sort(key=lambda r: r.seeders, reverse=True)
        _display_movie_results(results, query)

        if not results:
            continue

        selected = _pick_result(results)
        if selected is None:
            continue

        magnet = _resolve_magnet(selected)
        if not magnet:
            console.print("[red]Não foi possível obter o magnet link.[/red]")
            continue

        console.print(
            f"\n[bold green]Selecionado:[/bold green] {selected.title}"
            f" | {selected.quality} | {selected.size}"
            f" | [green]{selected.seeders}[/green] seeds"
        )
        confirm = Prompt.ask("[bold]Iniciar download?[/bold]", choices=["s", "n"], default="s")
        if confirm == "s":
            download(magnet, config.DOWNLOAD_DIR)


def _run_game_loop() -> None:
    console.print(f"[dim]Pasta de download:[/dim] [magenta]{config.GAMES_DOWNLOAD_DIR}[/magenta]")
    console.print("[dim]Altere com TORRENT_GAMES_DIR[/dim]\n")

    while True:
        query = Prompt.ask(
            "[bold magenta]Jogo[/bold magenta] [dim](nome · 'n' nova busca · 'm' mudar modo · 'q' sair)[/dim]"
        ).strip()

        if not query:
            continue
        if query.lower() in ("q", "sair", "exit", "quit"):
            console.print("\n[bold]Até logo![/bold]")
            raise SystemExit(0)
        if query.lower() in ("m", "modo"):
            raise _ChangeModeSignal()

        results = _search_all(query, _GAME_SOURCES)
        _display_game_results(results, query)

        if not results:
            continue

        selected = _pick_result(results)
        if selected is None:
            continue

        magnet = _resolve_magnet(selected)
        if not magnet:
            console.print("[red]Não foi possível obter o magnet link.[/red]")
            continue

        console.print(
            f"\n[bold green]Selecionado:[/bold green] {selected.title}"
            f" | Repack {selected.size}"
        )
        confirm = Prompt.ask("[bold]Iniciar download?[/bold]", choices=["s", "n"], default="s")
        if confirm == "s":
            download(magnet, config.GAMES_DOWNLOAD_DIR)


def main() -> None:
    _banner()

    mode = _pick_mode()

    while True:
        try:
            if mode == "filme":
                _run_movie_loop()
            else:
                _run_game_loop()
        except _ChangeModeSignal:
            console.print()
            mode = _pick_mode()
        except KeyboardInterrupt:
            console.print("\n\n[bold]Até logo![/bold]")
            break


if __name__ == "__main__":
    main()
