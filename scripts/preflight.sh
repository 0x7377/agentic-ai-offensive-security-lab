#!/usr/bin/env sh
set -eu

cd "$(dirname "$0")/.."

ok() { printf '[OK] %s\n' "$1"; }
warn() { printf '[WARN] %s\n' "$1"; }
fail() { printf '[ERROR] %s\n' "$1" >&2; exit 1; }

check_command() {
  command -v "$1" >/dev/null 2>&1 || fail "$1 명령을 찾을 수 없습니다."
  ok "$1: $(command -v "$1")"
}

printf '%s\n' '=== 시스템 ==='
printf 'OS: '; uname -srm
check_command git
check_command python3
check_command docker
check_command opencode
printf 'Git: '; git --version
printf 'Python: '; python3 --version
printf 'OpenCode: '; opencode --version

printf '%s\n' '=== Docker ==='
docker info >/dev/null 2>&1 || fail 'Docker 엔진에 연결할 수 없습니다. Docker Desktop을 실행하세요.'
ok 'Docker Client·Server 연결'
docker compose version >/dev/null || fail 'Docker Compose V2를 사용할 수 없습니다.'
ok "$(docker compose version)"
docker buildx version >/dev/null || fail 'Docker Buildx를 사용할 수 없습니다.'
ok 'Docker Buildx'

docker_cpus=$(docker info --format '{{.NCPU}}')
docker_memory=$(docker info --format '{{.MemTotal}}')
printf 'Docker CPUs: %s\n' "$docker_cpus"
printf 'Docker memory bytes: %s\n' "$docker_memory"
[ "$docker_cpus" -ge 4 ] || warn 'Docker CPU가 4개 미만입니다.'
[ "$docker_memory" -ge 8000000000 ] || warn 'Docker 메모리가 약 8 GB 미만입니다.'

disk_kb=$(df -Pk . | awk 'NR==2 {print $4}')
printf 'Workspace free disk KB: %s\n' "$disk_kb"
[ "$disk_kb" -ge 15000000 ] || warn '작업 디스크 여유 공간이 약 15 GB 미만입니다.'

printf '%s\n' '=== 저장소 ==='
test -f docker-compose.yml || fail '저장소 루트에서 실행하지 않았습니다.'
test -f .env || fail '.env가 없습니다. cp .env.example .env 를 실행하세요.'
if grep -q 'replace-with-' .env; then
  fail '.env의 예시 비밀번호를 실제 수업용 값으로 변경하세요.'
fi
ok '.env 예시 비밀번호 변경 확인'

git check-ignore -q .env || fail '.env가 Git ignore 대상이 아닙니다.'
ok '.env Git 제외'
git check-ignore -q labs/3100/opencode.jsonc || fail '개인 OpenCode 설정이 Git ignore 대상이 아닙니다.'
ok 'OpenCode 개인 설정 Git 제외'

docker compose --profile '*' config --quiet || fail 'Compose 구성 검증에 실패했습니다.'
services=$(docker compose --profile '*' config --services)
for service in 3100 3101 3102 3103 3104 3105 postgres artex artex-classroom-init cve-mcp; do
  printf '%s\n' "$services" | grep -qx "$service" || fail "Compose 서비스 누락: $service"
done
ok 'Compose 구성과 필수 서비스'

printf '%s\n' '=== 파일 ==='
test -f config/opencode.deepseek.jsonc.example || fail 'DeepSeek OpenCode 예제 누락'
test -f config/opencode.vllm.jsonc.example || fail 'vLLM OpenCode 예제 누락'
test -f skills/packages/adaptive-web-assessment.zip || fail '수업용 Skill 패키지 누락'
test -f templates/common-task-template.md || fail '공통 Task 템플릿 누락'
ok '모델 설정·Skill·Task 템플릿'

if find runtime -type f ! -name .gitkeep | grep -q .; then
  warn 'runtime에 기존 실행 데이터가 있습니다. 새 실습인지 재개 실습인지 확인하세요.'
else
  ok 'runtime 초기 상태'
fi

printf '%s\n' '=== 결과 ==='
ok '기본 사전 점검 완료'
printf '%s\n' '다음 단계: docs/pre-class-checklist.md의 LLM·ARTEX·MCP 항목을 확인하세요.'
