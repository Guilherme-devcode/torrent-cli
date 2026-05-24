# torrent-cli

CLI para buscar e baixar **filmes** e **jogos** via torrent direto no terminal.

| Categoria | Fontes |
|-----------|--------|
| Filmes    | YTS · The Pirate Bay · 1337x · SolidTorrents · LimeTorrents |
| Jogos     | FitGirl Repacks |

---

## Instalação

### Linux

```bash
git clone https://github.com/Guilherme-devcode/torrent-cli.git
cd torrent-cli
bash install.sh
```

Abre um novo terminal e execute:

```bash
torrent-cli
```

> **Requisito:** Python 3.10 ou superior.
> Instale um cliente torrent caso ainda não tenha: `sudo apt install aria2`

---

### Windows

1. Instale o [Python 3.10+](https://www.python.org/downloads/) — marque **"Add Python to PATH"** durante a instalação.
2. Clone ou baixe o repositório.
3. Abra o PowerShell na pasta do projeto e execute:

```powershell
powershell -ExecutionPolicy Bypass -File install.ps1
```

4. Abra um **novo** terminal e execute:

```cmd
torrent-cli
```

> Instale o [aria2](https://github.com/aria2/aria2/releases) (extraia `aria2c.exe` e coloque no PATH) ou o [qBittorrent](https://www.qbittorrent.org/download) para realizar os downloads.

---

## Desinstalação

**Linux**
```bash
bash install.sh --uninstall
```

**Windows**
```powershell
powershell -ExecutionPolicy Bypass -File install.ps1 -Uninstall
```

---

## Configuração

As pastas de download podem ser alteradas via variáveis de ambiente:

| Variável | Padrão | Descrição |
|----------|--------|-----------|
| `TORRENT_DOWNLOAD_DIR` | `~/Downloads/Movies` | Pasta para filmes |
| `TORRENT_GAMES_DIR` | `~/Downloads/Games` | Pasta para jogos |

**Linux / macOS**
```bash
export TORRENT_GAMES_DIR="/mnt/jogos"
torrent-cli
```

**Windows**
```cmd
set TORRENT_GAMES_DIR=D:\Jogos
torrent-cli
```

---

## Uso

Ao iniciar, escolha o modo de busca:

```
┌─────────────────────────────────┐
│    O que deseja buscar?         │
│  [F] Filme / Série              │
│  [J] Jogo (FitGirl Repacks)     │
└─────────────────────────────────┘
```

Durante qualquer busca, os seguintes comandos estão disponíveis:

| Comando | Ação |
|---------|------|
| número  | Seleciona o resultado |
| `n`     | Nova busca |
| `m`     | Muda o modo (filme ↔ jogo) |
| `q`     | Sai do programa |
