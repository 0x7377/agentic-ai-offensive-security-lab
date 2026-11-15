$ErrorActionPreference = "Stop"
Set-Location (Join-Path $PSScriptRoot "..")

function Write-Ok([string]$Message) { Write-Host "[OK] $Message" -ForegroundColor Green }
function Write-Warn([string]$Message) { Write-Warning $Message }
function Stop-Check([string]$Message) { throw "[ERROR] $Message" }

Write-Host "=== 시스템 ==="
foreach ($Command in @("git", "python", "docker", "opencode")) {
    $Found = Get-Command $Command -ErrorAction SilentlyContinue
    if (-not $Found) { Stop-Check "$Command 명령을 찾을 수 없습니다." }
    Write-Ok "$Command`: $($Found.Source)"
}
git --version
python --version
opencode --version

Write-Host "=== Docker ==="
docker info *> $null
if ($LASTEXITCODE -ne 0) { Stop-Check "Docker Desktop을 실행하세요." }
Write-Ok "Docker Client·Server 연결"

docker compose version *> $null
if ($LASTEXITCODE -ne 0) { Stop-Check "Docker Compose V2를 사용할 수 없습니다." }
Write-Ok "Docker Compose"

docker buildx version *> $null
if ($LASTEXITCODE -ne 0) { Stop-Check "Docker Buildx를 사용할 수 없습니다." }
Write-Ok "Docker Buildx"

$DockerCpus = [int](docker info --format '{{.NCPU}}')
$DockerMemory = [int64](docker info --format '{{.MemTotal}}')
Write-Host "Docker CPUs: $DockerCpus"
Write-Host "Docker memory bytes: $DockerMemory"
if ($DockerCpus -lt 4) { Write-Warn "Docker CPU가 4개 미만입니다." }
if ($DockerMemory -lt 8000000000) { Write-Warn "Docker 메모리가 약 8 GB 미만입니다." }

$Drive = Get-PSDrive -Name (Get-Location).Drive.Name -ErrorAction SilentlyContinue
if ($Drive) {
    Write-Host "Workspace free disk bytes: $($Drive.Free)"
    if ($Drive.Free -lt 15000000000) { Write-Warn "작업 디스크 여유 공간이 약 15 GB 미만입니다." }
}

Write-Host "=== 저장소 ==="
if (-not (Test-Path "docker-compose.yml")) { Stop-Check "저장소 루트에서 실행하지 않았습니다." }
if (-not (Test-Path ".env")) { Stop-Check ".env가 없습니다. Copy-Item .env.example .env 를 실행하세요." }
if (Select-String -Path ".env" -Pattern "replace-with-" -Quiet) {
    Stop-Check ".env의 예시 비밀번호를 실제 수업용 값으로 변경하세요."
}
Write-Ok ".env 예시 비밀번호 변경 확인"

git check-ignore -q .env
if ($LASTEXITCODE -ne 0) { Stop-Check ".env가 Git ignore 대상이 아닙니다." }
Write-Ok ".env Git 제외"

docker compose --profile "*" config --quiet
if ($LASTEXITCODE -ne 0) { Stop-Check "Compose 구성 검증 실패" }
$Services = docker compose --profile "*" config --services
foreach ($Service in @("3100", "3101", "3102", "3103", "3104", "3105", "postgres", "artex", "artex-classroom-init", "cve-mcp")) {
    if ($Services -notcontains $Service) { Stop-Check "Compose 서비스 누락: $Service" }
}
Write-Ok "Compose 구성과 필수 서비스"

Write-Host "=== 파일 ==="
foreach ($Path in @(
    "config/opencode.deepseek.jsonc.example",
    "config/opencode.vllm.jsonc.example",
    "skills/packages/adaptive-web-assessment.zip",
    "templates/common-task-template.md"
)) {
    if (-not (Test-Path $Path)) { Stop-Check "필수 파일 누락: $Path" }
}
Write-Ok "모델 설정·Skill·Task 템플릿"

$RuntimeFiles = Get-ChildItem runtime -Recurse -File | Where-Object { $_.Name -ne ".gitkeep" }
if ($RuntimeFiles) {
    Write-Warn "runtime에 기존 실행 데이터가 있습니다. 새 실습인지 재개 실습인지 확인하세요."
} else {
    Write-Ok "runtime 초기 상태"
}

Write-Host "=== 결과 ==="
Write-Ok "기본 사전 점검 완료"
Write-Host "다음 단계: docs/pre-class-checklist.md의 LLM·ARTEX·MCP 항목을 확인하세요."
