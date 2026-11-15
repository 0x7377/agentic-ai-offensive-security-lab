#!/usr/bin/env sh
set -eu
cd "$(dirname "$0")/.."
docker compose up -d --build 3101 3102 3103 3104
docker compose ps 3101 3102 3103 3104
