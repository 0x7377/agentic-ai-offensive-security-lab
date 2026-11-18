# ARTEX·MCP·Skill 준비

이 문서는 저장소 clone, Docker, OpenCode와 LLM 준비가 끝난 뒤 진행합니다. 모든 Docker 명령은 별도 표시가 없으면 저장소 루트에서 실행합니다.

## 준비 완료 기준

- 3100 실습 사이트 HTTP 200
- CVE MCP 컨테이너 healthy
- ARTEX와 PostgreSQL 정상 기동
- ARTEX 초기화 작업 종료 코드 0
- ARTEX 웹 로그인 성공
- ARTEX에서 3100 내부 주소 접근 가능
- 수업용 Skill ZIP 준비
- 실행 데이터와 API Key가 Git 대상에서 제외됨

## 1. 현재 경로와 환경 파일 확인

```bash
pwd
test -f docker-compose.yml && echo 'repository root OK'
test -f .env && echo '.env OK'
docker compose config --quiet
```

Windows PowerShell을 직접 쓰는 회차라면 다음을 사용합니다.

```powershell
Get-Location
Test-Path docker-compose.yml
Test-Path .env
docker compose config --quiet
```

`.env`가 없다면 `.env.example`을 복사하고 비밀번호를 바꿉니다. 기존 `.env`가 있다면 덮어쓰지 않습니다.

## 2. 3100 실습 사이트 시작

```bash
docker compose up -d --build 3100
docker compose ps 3100
```

`health: starting`은 초기 몇 초 동안 정상입니다. 10초 후 다시 확인합니다.

```bash
docker compose ps 3100
```

성공 기준:

- 상태가 `Up ... (healthy)`
- 브라우저에서 <http://127.0.0.1:3100> 첫 화면 표시

macOS·Ubuntu에서 HTTP 상태를 확인할 수 있습니다.

```bash
curl -sS -o /dev/null -w 'HTTP %{http_code}\n' http://127.0.0.1:3100/
```

Windows PowerShell에서는 다음을 사용합니다.

```powershell
(Invoke-WebRequest http://127.0.0.1:3100 -UseBasicParsing).StatusCode
```

## 3. CVE MCP 서버 시작

```bash
docker compose up -d --build cve-mcp
docker compose ps cve-mcp
```

성공 기준은 `cve-mcp`가 `healthy`인 것입니다. 최초 실행 때 CISA KEV 목록을 읽으므로 네트워크 상태에 따라 시간이 걸릴 수 있습니다.

```bash
docker compose logs --tail=80 cve-mcp
```

로그에서 다음을 확인합니다.

- Streamable HTTP 서버 시작
- `0.0.0.0:8000` 수신
- KEV catalog 로드 또는 외부 조회 상태

호스트에서 사용할 MCP URL은 다음과 같습니다.

```text
http://127.0.0.1:8800/mcp
```

ARTEX 컨테이너에서 사용할 URL은 다음과 같습니다.

```text
http://cve-mcp:8000/mcp
```

두 주소를 바꿔 입력하지 않습니다.

## 4. OpenCode에 MCP 등록

OpenCode 실습 폴더에서 등록합니다.

```bash
cd labs/3100
opencode mcp add cve-intel --url http://127.0.0.1:8800/mcp
opencode mcp list --standalone
```

성공 기준은 `cve-intel` 서버가 `connected`로 표시되는 것입니다. 일부 OpenCode 버전에서 목록 표시와 실제 연결 상태가 다를 수 있으므로 다음 설정 확인도 함께 사용합니다.

```bash
opencode debug config --standalone
```

최종 판정은 실제 MCP Tool이 호출되어 구조화된 CVE 결과를 반환하는지로 합니다. 모델이 기억으로 CVE를 답한 것은 MCP 연결 증거가 아닙니다.

## 5. OpenCode Skill 배치

첫 번째 Naive 실습 전에는 `.opencode/skills`가 비어 있어야 합니다. Skill 적용 단계가 되면 강사가 지정한 Skill 하나만 복사합니다.

저장소 루트에서 예시:

```bash
mkdir -p labs/3100/.opencode/skills
cp -R skills/source/adaptive-web-assessment \
  labs/3100/.opencode/skills/
find labs/3100/.opencode/skills -maxdepth 2 -name SKILL.md -print
```

Windows PowerShell:

```powershell
New-Item -ItemType Directory -Force labs\3100\.opencode\skills | Out-Null
Copy-Item -Recurse skills\source\adaptive-web-assessment labs\3100\.opencode\skills\
Get-ChildItem -Recurse labs\3100\.opencode\skills\SKILL.md
```

성공 기준:

```text
labs/3100/.opencode/skills/adaptive-web-assessment/SKILL.md
```

Skill의 디렉토리 이름, `SKILL.md` frontmatter의 이름과 프롬프트에서 부르는 ID를 일관되게 유지합니다. 모든 Skill을 한꺼번에 넣으면 선택 후보와 컨텍스트가 불필요하게 늘어날 수 있습니다.

수업 단계가 끝난 뒤 프로젝트 Skill을 비우려면 삭제 전에 목록을 확인합니다.

```bash
find labs/3100/.opencode/skills -mindepth 1 -maxdepth 1 -print
```

강사가 지정한 항목만 제거하며 전역 `~/.config/opencode/skills`는 수정하지 않습니다.

## 6. ARTEX 시작

저장소 루트로 돌아갑니다.

```bash
cd ../..
docker compose --profile artex up -d --wait --wait-timeout 180
docker compose --profile artex ps -a postgres artex artex-classroom-init
```

성공 기준:

| 서비스 | 정상 상태 |
|---|---|
| `postgres` | `healthy` |
| `artex` | `Up` |
| `artex-classroom-init` | `Exited (0)` |

`artex-classroom-init`는 한글 Agent 이름과 수업용 범위 안전장치를 적용하는 일회성 작업입니다. 종료 코드 0은 정상입니다.

문제가 있을 때만 제한된 로그를 확인합니다.

```bash
docker compose --profile artex logs --tail=80 postgres artex artex-classroom-init
```

## 7. ARTEX 첫 로그인

브라우저에서 <http://127.0.0.1:8787>을 엽니다.

1. 로그인 화면이 표시되는지 확인
2. `.env`에 설정한 관리자 비밀번호로 로그인
3. 상단 또는 좌측 메뉴가 한글로 표시되는지 확인
4. Agent 목록에서 수업용 Agent 이름 확인

비밀번호를 화면 공유, 채팅, 캡처에 노출하지 않습니다.

## 8. LLM 등록

ARTEX의 **시스템 설정 → LLM**으로 이동해 [LLM 연결 안내](setup-llm.md)의 회차별 값을 등록합니다.

등록 후 연결 시험을 실행하고 다음을 구분합니다.

- 모델 연결 성공: 짧은 LLM 응답 가능
- Tool 실행 성공: Agent가 HTTP·브라우저·MCP를 실제 호출

모델 연결 성공만으로 실습 준비가 모두 끝난 것은 아닙니다.

## 9. ARTEX에 MCP 등록

ARTEX의 **시스템 설정 → MCP**에서 새 MCP 서버를 추가합니다.

| 필드 | 입력값 |
|---|---|
| 이름 | `CVE MCP` |
| 전송 방식 | Streamable HTTP 또는 HTTP |
| URL | `http://cve-mcp:8000/mcp` |
| 활성화 | 켬 |

저장 후 Tool 목록 또는 연결 상태를 확인합니다. `127.0.0.1:8800`은 호스트용 주소이므로 ARTEX 화면에는 사용하지 않습니다.

## 10. ARTEX에 Skill 업로드

ARTEX의 **시스템 설정 → Skill**에서 강사가 지정한 ZIP만 업로드합니다.

배포 ZIP은 `skills/packages/`에 있습니다.

```bash
ls -1 skills/packages/*.zip
```

업로드 후 확인할 것:

- Skill 이름
- 설명
- 연결할 Agent
- 활성화 상태

Task에 Skill이 필요하다면 해당 Task를 수행할 Agent에 연결됐는지 확인합니다. 업로드됐다는 사실만으로 모든 Agent가 자동 사용하지는 않습니다.

## 11. ARTEX에서 실습 사이트 통신 확인

ARTEX와 실습 사이트는 같은 Docker 네트워크를 사용합니다. ARTEX 자산에는 호스트 주소가 아니라 내부 주소를 등록합니다.

```text
http://portal.digitaltrust.lab:8080
```

터미널에서 ARTEX 컨테이너 내부 통신을 확인합니다.

```bash
docker compose --profile artex exec -T artex \
  curl -I --max-time 15 http://portal.digitaltrust.lab:8080
```

HTTP 응답 헤더가 나오면 정상입니다. ARTEX 안에서 `127.0.0.1:3100`은 호스트 실습 사이트가 아니라 ARTEX 컨테이너 자신을 의미합니다.

## 12. 실행·중지·재개

일시 중지는 `stop`, 재개는 `start`를 우선합니다.

```bash
docker compose stop 3100 cve-mcp artex postgres
docker compose start postgres artex cve-mcp 3100
docker compose ps
```

일반 종료에 `down -v`를 사용하지 않습니다. `down -v`는 ARTEX 자산·Task·Finding이 들어 있는 DB 볼륨을 삭제합니다.

모든 프로필 컨테이너와 네트워크를 제거하되 DB 볼륨을 보존하려면 다음을 사용합니다.

```bash
docker compose --profile "*" down
```

## 13. Git과 비밀정보 확인

```bash
git status --short
git check-ignore .env labs/3100/opencode.jsonc
find runtime -type f ! -name .gitkeep -print
```

`.env`와 `opencode.jsonc`는 ignored로 표시돼야 합니다. `runtime`의 실행 데이터는 수업 결과를 내보낸 뒤 저장소에 커밋하지 않습니다.
