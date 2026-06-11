$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot

python -m pip install -e ".[web,exe]"
python -m PyInstaller --clean --noconfirm packaging\Decisive20.spec

Write-Host ""
Write-Host "Build complete: $ProjectRoot\dist\Decisive20\Decisive20.exe"
