#!/usr/bin/env sh
set -eu
cd "$(dirname "$0")/.."
docker compose up -d --build 3100
docker compose ps 3100
