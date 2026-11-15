# 문제 해결과 중단·재개

오류가 발생하면 기존 데이터나 이미지를 먼저 지우지 않습니다. 실패한 단계, 현재 상태와 제한된 로그를 확인하고 해당 단계만 재시도합니다.

## 먼저 기록할 정보

```bash
uname -a
docker version
docker compose version
docker buildx version
opencode --version
docker compose --profile "*" ps -a
```

지원 요청에는 다음만 전달합니다.

- OS와 아키텍처
- Docker와 OpenCode 버전
- 실패한 문서 단계
- 실행한 명령
- 마지막 오류 20~80줄

API Key, `.env`, 쿠키, 인증 헤더, 전체 runtime 폴더를 공유하지 않습니다.

## Docker Server가 표시되지 않음

증상:

- `Cannot connect to the Docker daemon`
- `docker version`에 Client만 표시

확인:

- Docker Desktop 실행 상태
- Windows: Settings → Resources → WSL Integration에서 Ubuntu 활성화
- Windows: Ubuntu 탭을 닫았다가 다시 열기
- macOS: 메뉴 막대 Docker 아이콘 상태

Docker Desktop이 완전히 시작된 뒤 다시 실행합니다.

## `opencode: command not found`

```bash
command -v opencode
echo "$PATH" | tr ':' '\n'
```

설치 스크립트가 안내한 bin 경로가 PATH에 있는지 확인하고 새 터미널을 엽니다. V1과 V2를 반복 설치하지 않습니다. 기존 경로가 여러 개면 다음 결과를 강사에게 전달합니다.

```bash
which -a opencode
```

## OpenCode 모델이 표시되지 않음

`labs/3100`에서 확인합니다.

```bash
pwd
ls -l opencode.jsonc
opencode debug config --standalone
opencode models --standalone
```

확인 항목:

- 설정 파일명이 `opencode.jsonc`인지
- Base URL 끝의 `/v1` 포함 여부가 강사 안내와 같은지
- provider ID와 최상위 model prefix가 같은지
- DeepSeek 환경 변수가 같은 터미널에 설정됐는지
- 모델 ID의 대소문자와 철자

## LLM 오류

| 상태 | 먼저 확인할 것 |
|---|---|
| 401 | API Key 누락·오타·만료 |
| 402 | DeepSeek 잔액 또는 결제 상태 |
| 404 | Base URL·모델 ID·API 경로 |
| 429 | 호출 빈도·동시 작업 수·공유 서버 부하 |
| timeout | 강의장 네트워크·VPN·서버 상태 |
| 빈 모델 목록 | vLLM 서버 기동 및 `/v1/models` |

같은 오류가 반복되면 Task를 새로 만들지 말고 호출을 중지합니다.

## 포트가 이미 사용 중임

```bash
docker ps --format 'table {{.Names}}\t{{.Ports}}'
```

macOS:

```bash
lsof -nP -iTCP:3100 -sTCP:LISTEN
lsof -nP -iTCP:8787 -sTCP:LISTEN
```

Windows PowerShell:

```powershell
Get-NetTCPConnection -LocalPort 3100,8787,8800 -ErrorAction SilentlyContinue
```

다른 프로젝트를 임의로 종료하지 않습니다. 포트 소유자를 확인한 뒤 강사와 종료 또는 포트 변경을 결정합니다.

## 컨테이너가 `unhealthy` 또는 종료됨

```bash
docker compose --profile "*" ps -a
docker compose logs --tail=80 <서비스명>
```

서비스명은 `3100`, `3101`, `artex`, `cve-mcp`처럼 한 개만 넣습니다. 전체 로그를 한꺼번에 출력하지 않습니다.

종료 코드 137은 메모리 부족 가능성이 큽니다. Docker 할당 메모리와 호스트 여유 메모리를 확인합니다.

## 웹 페이지가 열리지 않음

```bash
docker compose ps 3100
curl -sS -o /dev/null -w 'HTTP %{http_code}\n' http://127.0.0.1:3100/
```

Windows PowerShell:

```powershell
(Invoke-WebRequest http://127.0.0.1:3100 -UseBasicParsing).StatusCode
```

컨테이너가 healthy인데 브라우저만 실패하면 프록시, VPN, 기관 보안 프로그램과 주소 오타를 확인합니다.

## ARTEX가 바로 열리지 않음

```bash
docker compose --profile artex ps -a postgres artex artex-classroom-init
docker compose --profile artex logs --tail=80 artex artex-classroom-init
```

`artex-classroom-init`의 `Exited (0)`은 정상입니다. `postgres`가 healthy가 되기 전에는 ARTEX 초기화가 지연될 수 있습니다.

## ARTEX에서 실습 자산에 접근하지 못함

ARTEX 자산에는 `127.0.0.1:310x`가 아니라 내부 주소를 입력합니다.

```bash
docker compose --profile artex exec -T artex \
  curl -I --max-time 15 http://portal.digitaltrust.lab:8080
```

내부 주소 표는 루트 README를 확인합니다. ARTEX 안의 `127.0.0.1`은 ARTEX 자신입니다.

## MCP가 연결되지 않음

```bash
docker compose ps cve-mcp
docker compose logs --tail=80 cve-mcp
```

주소를 구분합니다.

- OpenCode: `http://127.0.0.1:8800/mcp`
- ARTEX: `http://cve-mcp:8000/mcp`

OpenCode에서는 다음을 함께 확인합니다.

```bash
opencode mcp list
opencode debug config --standalone
```

목록 표시만으로 판단하지 말고 실제 CVE Tool Call 결과를 확인합니다.

## 중단 후 재개

컨테이너와 데이터를 보존한 채 멈춥니다.

```bash
docker compose stop
```

프로필 서비스는 명시적으로 멈출 수 있습니다.

```bash
docker compose stop 3100 3101 3102 3103 3104 3105 cve-mcp artex postgres
```

재개:

```bash
docker compose start postgres artex cve-mcp 3100
docker compose ps
```

재개 후 LLM, MCP와 실습 자산 통신을 다시 확인합니다. 이전에 실행하지 않은 명령을 자동으로 이어서 실행하지 않습니다.

## 사용하지 말아야 할 초기화

문제 해결 목적으로 다음을 사용하지 않습니다.

```text
docker compose down -v
docker system prune -a
WSL 배포판 삭제
runtime 디렉토리 전체 삭제
```

이 작업은 복구가 어렵거나 다른 프로젝트까지 영향을 줄 수 있습니다. 데이터 초기화가 필요하면 결과를 내보낸 뒤 강사의 안내에 따라 명시된 프로젝트만 처리합니다.
