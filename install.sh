#!/usr/bin/env bash
# install.sh — instala torrent-cli no sistema do usuário
# Uso: bash install.sh [--uninstall]
set -euo pipefail

INSTALL_DIR="$HOME/.local/share/torrent-cli"
BIN_DIR="$HOME/.local/bin"
LAUNCHER="$BIN_DIR/torrent-cli"
SOURCE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

RED='\033[0;31m'; GREEN='\033[0;32m'; CYAN='\033[0;36m'
YELLOW='\033[1;33m'; BOLD='\033[1m'; NC='\033[0m'

step() { echo -e "${CYAN}[${1}/${TOTAL}]${NC} ${2}"; }
ok()   { echo -e "      ${GREEN}✓${NC} ${1}"; }
warn() { echo -e "      ${YELLOW}!${NC} ${1}"; }
fail() { echo -e "      ${RED}✗${NC} ${1}"; exit 1; }

banner() {
    echo -e "\n${BOLD}┌─────────────────────────────────┐${NC}"
    echo -e "${BOLD}│        torrent-cli installer    │${NC}"
    echo -e "${BOLD}└─────────────────────────────────┘${NC}\n"
}

# ── Desinstalação ─────────────────────────────────────────────────────────────
uninstall() {
    banner
    echo -e "${YELLOW}Desinstalando torrent-cli...${NC}\n"

    if [ -f "$LAUNCHER" ]; then
        rm -f "$LAUNCHER"
        ok "Launcher removido: $LAUNCHER"
    else
        warn "Launcher não encontrado: $LAUNCHER"
    fi

    if [ -d "$INSTALL_DIR" ]; then
        rm -rf "$INSTALL_DIR"
        ok "Arquivos removidos: $INSTALL_DIR"
    else
        warn "Diretório não encontrado: $INSTALL_DIR"
    fi

    echo -e "\n${GREEN}${BOLD}✓ torrent-cli desinstalado.${NC}\n"
    exit 0
}

[ "${1:-}" = "--uninstall" ] && uninstall

# ── Instalação ────────────────────────────────────────────────────────────────
TOTAL=5
banner

# 1. Python
step 1 "Verificando Python 3.10+..."
PYTHON=""
for cmd in python3.13 python3.12 python3.11 python3.10 python3; do
    if command -v "$cmd" &>/dev/null; then
        VER=$("$cmd" -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>/dev/null || true)
        MAJOR=$(echo "$VER" | cut -d. -f1)
        MINOR=$(echo "$VER" | cut -d. -f2)
        if [ "${MAJOR:-0}" -ge 3 ] && [ "${MINOR:-0}" -ge 10 ]; then
            PYTHON="$cmd"
            ok "Python $VER → $(command -v "$cmd")"
            break
        fi
    fi
done
[ -z "$PYTHON" ] && fail "Python 3.10+ não encontrado. Instale com: sudo apt install python3"

# 2. Copiar arquivos
step 2 "Copiando arquivos para $INSTALL_DIR..."
mkdir -p "$INSTALL_DIR/searchers"
cp "$SOURCE_DIR"/*.py      "$INSTALL_DIR/"
cp "$SOURCE_DIR/requirements.txt" "$INSTALL_DIR/"
cp "$SOURCE_DIR/searchers/"*.py   "$INSTALL_DIR/searchers/"
ok "Arquivos copiados"

# 3. Ambiente virtual
step 3 "Criando ambiente virtual..."
if [ -d "$INSTALL_DIR/.venv" ]; then
    warn "Ambiente virtual existente removido e recriado"
    rm -rf "$INSTALL_DIR/.venv"
fi
"$PYTHON" -m venv "$INSTALL_DIR/.venv"
ok "Ambiente virtual criado"

# 4. Dependências
step 4 "Instalando dependências Python..."
"$INSTALL_DIR/.venv/bin/pip" install --quiet --upgrade pip
"$INSTALL_DIR/.venv/bin/pip" install --quiet -r "$INSTALL_DIR/requirements.txt"
ok "requests · rich · beautifulsoup4 · lxml instalados"

# 5. Launcher
step 5 "Criando launcher em $LAUNCHER..."
mkdir -p "$BIN_DIR"
cat > "$LAUNCHER" <<LAUNCHER
#!/usr/bin/env bash
exec "$INSTALL_DIR/.venv/bin/python" "$INSTALL_DIR/torrent_cli.py" "\$@"
LAUNCHER
chmod +x "$LAUNCHER"
ok "torrent-cli pronto em $LAUNCHER"

# ── Cliente torrent ────────────────────────────────────────────────────────────
echo ""
echo -e "${CYAN}[+]${NC} Verificando cliente torrent..."
if command -v aria2c &>/dev/null; then
    ok "aria2c: $(aria2c --version | head -1)"
elif command -v transmission-cli &>/dev/null; then
    ok "transmission-cli encontrado"
elif command -v qbittorrent-nox &>/dev/null; then
    ok "qbittorrent-nox encontrado"
else
    warn "Nenhum cliente torrent instalado. Instale um dos seguintes:"
    echo "        sudo apt install aria2            ← recomendado"
    echo "        sudo apt install transmission-cli"
    echo "        sudo apt install qbittorrent-nox"
fi

# ── PATH ──────────────────────────────────────────────────────────────────────
echo ""
if [[ ":$PATH:" == *":$BIN_DIR:"* ]]; then
    ok "~/.local/bin já está no PATH"
else
    warn "~/.local/bin não está no PATH. Execute os comandos abaixo:"
    echo ""
    RC="$HOME/.bashrc"
    [ -f "$HOME/.zshrc" ] && RC="$HOME/.zshrc"
    echo -e "    ${YELLOW}echo 'export PATH=\"\$HOME/.local/bin:\$PATH\"' >> $RC${NC}"
    echo -e "    ${YELLOW}source $RC${NC}"
fi

# ── Fim ───────────────────────────────────────────────────────────────────────
echo ""
echo -e "${BOLD}${GREEN}✓ Instalação concluída!${NC}"
echo ""
echo -e "  Execute:       ${BOLD}torrent-cli${NC}"
echo -e "  Desinstalar:   ${BOLD}bash install.sh --uninstall${NC}"
echo ""
