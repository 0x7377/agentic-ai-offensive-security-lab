#!/usr/bin/env sh
set -eu
cd "$(dirname "$0")/.."
docker compose up -d --build cve-mcp
docker compose ps cve-mcp
