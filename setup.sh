#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/.venv"

echo "=== torrent-cli setup ==="
echo ""

# Virtual environment
if [ ! -d "$VENV_DIR" ]; then
    echo "[1/3] Criando ambiente virtual Python..."
    python3 -m venv "$VENV_DIR"
    echo "      OK"
else
    echo "[1/3] Ambiente virtual já existe, OK"
fi

# Python deps
echo "[2/3] Instalando dependências Python..."
"$VENV_DIR/bin/pip" install -r "$SCRIPT_DIR/requirements.txt" --quiet
echo "      OK"

# Torrent client check
echo "[3/3] Verificando clientes torrent..."
if command -v aria2c &>/dev/null; then
    echo "      ✓ aria2c: $(aria2c --version | head -1)"
else
    echo "      ✗ aria2c não encontrado (recomendado)"
    echo "        Ubuntu/Debian : sudo apt install aria2"
    echo "        Fedora/RHEL   : sudo dnf install aria2"
    echo "        Arch          : sudo pacman -S aria2"
fi
if command -v transmission-cli &>/dev/null; then
    echo "      ✓ transmission-cli encontrado"
fi

# Wrapper script
cat > "$SCRIPT_DIR/run.sh" <<'EOF'
#!/usr/bin/env bash
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec "$DIR/.venv/bin/python" "$DIR/torrent_cli.py" "$@"
EOF
chmod +x "$SCRIPT_DIR/run.sh"

echo ""
echo "=== Pronto! ==="
echo ""
echo "Execute:"
echo "  ./run.sh"
echo "  ou: bash run.sh"
echo ""
echo "Pasta padrão de download: ~/Downloads/Movies"
echo "Para alterar: export TORRENT_DOWNLOAD_DIR=/outro/caminho && ./run.sh"
