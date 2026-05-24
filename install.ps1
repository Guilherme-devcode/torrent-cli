# install.ps1 — instala torrent-cli no Windows
# Uso: powershell -ExecutionPolicy Bypass -File install.ps1 [-Uninstall]
#Requires -Version 5.1
param([switch]$Uninstall)
$ErrorActionPreference = "Stop"

$AppDir  = Join-Path $env:APPDATA "torrent-cli"
$BinDir  = Join-Path $AppDir "bin"
$BatPath = Join-Path $BinDir "torrent-cli.bat"
$Source  = Split-Path -Parent $MyInvocation.MyCommand.Path

function Step($n, $total, $msg) { Write-Host "[$n/$total] $msg" -ForegroundColor Cyan }
function Ok($msg)   { Write-Host "      [OK] $msg" -ForegroundColor Green }
function Warn($msg) { Write-Host "      [!]  $msg" -ForegroundColor Yellow }
function Fail($msg) { Write-Host "      [X]  $msg" -ForegroundColor Red; exit 1 }

function Banner {
    Write-Host ""
    Write-Host "+-----------------------------------+" -ForegroundColor White
    Write-Host "|      torrent-cli installer        |" -ForegroundColor White
    Write-Host "+-----------------------------------+" -ForegroundColor White
    Write-Host ""
}

# ── Desinstalação ─────────────────────────────────────────────────────────────
function Uninstall-App {
    Banner
    Write-Host "Desinstalando torrent-cli..." -ForegroundColor Yellow
    Write-Host ""

    if (Test-Path $AppDir) {
        Remove-Item $AppDir -Recurse -Force
        Ok "Arquivos removidos: $AppDir"
    } else {
        Warn "Diretório nao encontrado: $AppDir"
    }

    # Remove do PATH do usuario
    $UserPath = [Environment]::GetEnvironmentVariable("PATH", "User")
    if ($UserPath -like "*$BinDir*") {
        $NewPath = ($UserPath -split ";" | Where-Object { $_ -ne $BinDir }) -join ";"
        [Environment]::SetEnvironmentVariable("PATH", $NewPath, "User")
        Ok "$BinDir removido do PATH"
    }

    Write-Host ""
    Write-Host "[OK] torrent-cli desinstalado." -ForegroundColor Green
    Write-Host ""
    exit 0
}

if ($Uninstall) { Uninstall-App }

# ── Instalação ────────────────────────────────────────────────────────────────
$Total = 5
Banner

# 1. Python
Step 1 $Total "Verificando Python 3.10+..."
$Python = $null
foreach ($cmd in @("python", "python3", "py")) {
    try {
        $ver = & $cmd -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}')" 2>$null
        if ($ver -match "^(\d+)\.(\d+)") {
            $major = [int]$Matches[1]; $minor = [int]$Matches[2]
            if ($major -ge 3 -and $minor -ge 10) {
                $Python = $cmd
                Ok "Python $ver encontrado (comando: $cmd)"
                break
            }
        }
    } catch {}
}
if (-not $Python) {
    Fail "Python 3.10+ nao encontrado."
    Write-Host "      Baixe em: https://www.python.org/downloads/" -ForegroundColor Yellow
    Write-Host "      Marque 'Add Python to PATH' durante a instalacao." -ForegroundColor Yellow
    exit 1
}

# 2. Copiar arquivos
Step 2 $Total "Copiando arquivos para $AppDir..."
New-Item -ItemType Directory -Force -Path "$AppDir\searchers" | Out-Null
Get-ChildItem "$Source\*.py"           | Copy-Item -Destination $AppDir -Force
Copy-Item "$Source\requirements.txt"    -Destination $AppDir -Force
Get-ChildItem "$Source\searchers\*.py" | Copy-Item -Destination "$AppDir\searchers" -Force
Ok "Arquivos copiados"

# 3. Ambiente virtual
Step 3 $Total "Criando ambiente virtual..."
if (Test-Path "$AppDir\.venv") {
    Warn "Ambiente virtual existente removido e recriado"
    Remove-Item "$AppDir\.venv" -Recurse -Force
}
& $Python -m venv "$AppDir\.venv"
Ok "Ambiente virtual criado"

# 4. Dependencias
Step 4 $Total "Instalando dependencias Python..."
$Pip = "$AppDir\.venv\Scripts\pip.exe"
& $Pip install --quiet --upgrade pip 2>$null
& $Pip install --quiet -r "$AppDir\requirements.txt"
Ok "requests . rich . beautifulsoup4 . lxml instalados"

# 5. Launcher
Step 5 $Total "Criando launcher..."
New-Item -ItemType Directory -Force -Path $BinDir | Out-Null
$PythonExe = "$AppDir\.venv\Scripts\python.exe"
$Script    = "$AppDir\torrent_cli.py"
$BatContent = "@echo off`r`n`"$PythonExe`" `"$Script`" %*"
Set-Content -Path $BatPath -Value $BatContent -Encoding ASCII
Ok "Launcher criado: $BatPath"

# PATH
$UserPath = [Environment]::GetEnvironmentVariable("PATH", "User")
if ($UserPath -like "*$BinDir*") {
    Ok "$BinDir ja esta no PATH"
} else {
    [Environment]::SetEnvironmentVariable("PATH", "$UserPath;$BinDir", "User")
    Ok "$BinDir adicionado ao PATH do usuario"
    Warn "Abra um NOVO terminal para o PATH entrar em vigor"
}

# ── Cliente torrent ────────────────────────────────────────────────────────────
Write-Host ""
Write-Host "[+] Verificando cliente torrent..." -ForegroundColor Cyan
$aria   = Get-Command aria2c       -ErrorAction SilentlyContinue
$qbit   = Get-Command qbittorrent  -ErrorAction SilentlyContinue
$qbitnox = Get-Command qbittorrent-nox -ErrorAction SilentlyContinue
if ($aria) {
    Ok "aria2c encontrado"
} elseif ($qbit -or $qbitnox) {
    Ok "qBittorrent encontrado"
} else {
    Warn "Nenhum cliente torrent encontrado. Instale um:"
    Write-Host "        aria2 (recomendado) : https://github.com/aria2/aria2/releases" -ForegroundColor Yellow
    Write-Host "          Extraia aria2c.exe e adicione ao PATH" -ForegroundColor Yellow
    Write-Host "        qBittorrent         : https://www.qbittorrent.org/download" -ForegroundColor Yellow
}

# ── Fim ───────────────────────────────────────────────────────────────────────
Write-Host ""
Write-Host "[OK] Instalacao concluida!" -ForegroundColor Green
Write-Host ""
Write-Host "  Execute (novo terminal): " -NoNewline
Write-Host "torrent-cli" -ForegroundColor Cyan
Write-Host "  Desinstalar:            " -NoNewline
Write-Host "powershell -ExecutionPolicy Bypass -File install.ps1 -Uninstall" -ForegroundColor Yellow
Write-Host ""
