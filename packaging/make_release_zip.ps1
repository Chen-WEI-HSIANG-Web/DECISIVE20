param(
    [string]$Version = "0.1.0"
)

$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot

$DistDir = Join-Path $ProjectRoot "dist\Decisive20"
$ExePath = Join-Path $DistDir "Decisive20.exe"
$ReleaseDir = Join-Path $ProjectRoot "release"
$ZipPath = Join-Path $ReleaseDir "Decisive20-Windows-v$Version.zip"

if (-not (Test-Path $ExePath)) {
    throw "Missing $ExePath. Run packaging\build_exe.bat first."
}

if (-not (Test-Path $ReleaseDir)) {
    New-Item -ItemType Directory -Path $ReleaseDir | Out-Null
}

if (Test-Path $ZipPath) {
    Remove-Item $ZipPath
}

Compress-Archive `
    -Path (Join-Path $DistDir "*") `
    -DestinationPath $ZipPath `
    -CompressionLevel Optimal `
    -ErrorAction Stop

Write-Host ""
Write-Host "Release zip created: $ZipPath"
Write-Host "Upload this file to GitHub Releases."
