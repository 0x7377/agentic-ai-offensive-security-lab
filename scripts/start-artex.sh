#!/usr/bin/env sh
set -eu
cd "$(dirname "$0")/.."
docker compose --profile artex up -d
docker compose ps
