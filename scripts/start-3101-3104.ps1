$ErrorActionPreference = "Stop"
Set-Location (Join-Path $PSScriptRoot "..")
docker compose up -d --build 3101 3102 3103 3104
docker compose ps 3101 3102 3103 3104
