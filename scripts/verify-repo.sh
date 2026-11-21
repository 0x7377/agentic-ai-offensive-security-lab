#!/usr/bin/env sh
set -eu
cd "$(dirname "$0")/.."

test -f README.md
test -f docker-compose.yml
test -f runtime/artex-data/.gitkeep
test -f runtime/artex-skills/.gitkeep

if find runtime -type f ! -name .gitkeep | grep -q .; then
  printf '[ERROR] runtime 아래 실행 데이터가 있습니다.\n' >&2
  exit 1
fi

if find . -type d \( -name __pycache__ -o -name node_modules \) -print | grep -q .; then
  printf '[ERROR] 캐시 또는 의존성 디렉토리가 포함되어 있습니다.\n' >&2
  exit 1
fi

for service in 3100 3101 3102 3103 3104 3105; do
  test -f "labs/$service/Dockerfile"
done

test -f labs/3100/AGENTS.md

test -f skills/packages/SHA256SUMS.txt
(
  cd skills/packages
  if command -v shasum >/dev/null 2>&1; then
    shasum -a 256 -c SHA256SUMS.txt >/dev/null
  else
    sha256sum -c SHA256SUMS.txt >/dev/null
  fi
)

POSTGRES_PASSWORD=verify-only ARTEX_ADMIN_PASSWORD=verify-only docker compose config --quiet
printf '[OK] 저장소 구조와 Compose 구성을 검증했습니다.\n'
