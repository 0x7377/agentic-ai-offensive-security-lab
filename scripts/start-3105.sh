#!/usr/bin/env sh
set -eu
cd "$(dirname "$0")/.."
docker compose up -d --build 3105
docker compose ps 3105
