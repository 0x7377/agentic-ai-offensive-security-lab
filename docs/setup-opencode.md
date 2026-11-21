# OpenCode 설치와 첫 실행

OpenCode는 현재 폴더를 작업 공간으로 삼아 LLM, 파일, 명령, Skill, MCP Tool을 연결하는 터미널 기반 Agent Harness입니다. 웹 채팅과 달리 허용된 범위에서 실제 도구를 호출하므로 반드시 실습 폴더와 명령 대상을 확인해야 합니다.

이 과정은 OpenCode V2 구성 형식을 사용합니다. OpenCode V1과 V2는 기본 명령명이 같으므로 기존 설치가 있다면 먼저 버전을 확인합니다.

- 공식 설치 안내: <https://opencode.ai/docs>
- CLI 안내: <https://opencode.ai/docs/cli>

## 준비 완료 기준

- `opencode --version` 정상 출력
- `opencode` 명령의 실제 경로 확인
- `labs/3100`에서 OpenCode 실행
- 수업 모델이 모델 목록에 표시
- 간단한 질문에 응답
- Skill과 MCP를 추가하기 전 기본 상태 확인

## 1. 기존 설치 확인

macOS 터미널 또는 Windows의 Ubuntu 탭에서 실행합니다.

```bash
command -v opencode || true
opencode --version || true
```

정상 버전이 출력되면 다시 설치하지 않습니다. V1을 사용 중이거나 설치 경로가 여러 개라면 임의로 덮어쓰지 말고 다음 결과를 강사에게 보여 줍니다.

```bash
which -a opencode
opencode --version
```

## 2. macOS 설치

Homebrew가 있다면 다음 방법을 권장합니다.

```bash
brew install anomalyco/tap/opencode-v2
opencode --version
```

Homebrew가 없거나 강사가 설치 스크립트 방식을 지정했다면 공식 V2 설치 스크립트를 사용합니다.

```bash
curl -fsSL https://opencode.ai/v2/install | bash
```

설치 종료 메시지에 PATH 안내가 나오면 그대로 적용하고 새 터미널을 엽니다.

```bash
command -v opencode
opencode --version
```

`command not found`이면 설치를 반복하지 말고 설치 마지막에 안내된 경로가 `PATH`에 포함됐는지 확인합니다.

```bash
echo "$PATH" | tr ':' '\n'
```

## 3. Windows 설치

OpenCode V2 공식 문서상 Windows 패키지 관리자를 통한 CLI 설치는 지원되지 않습니다. 이 수업에서는 WSL2의 Ubuntu 탭에 Linux CLI를 설치합니다.

Ubuntu 탭에서 실행합니다.

```bash
curl -fsSL https://opencode.ai/v2/install | bash
```

설치 메시지의 PATH 안내를 적용하거나 Ubuntu 탭을 닫았다가 다시 엽니다.

```bash
command -v opencode
opencode --version
```

PowerShell에 설치된 별도 `opencode.exe`와 Ubuntu의 `opencode`를 섞지 않습니다. 저장소와 OpenCode를 모두 Ubuntu 환경에서 실행합니다.

## 4. 모델 설정 파일 배치

저장소 루트에서 교육 회차에 맞는 설정 하나만 복사합니다.

### DeepSeek 회차

```bash
cp config/opencode.deepseek.jsonc.example labs/3100/opencode.jsonc
```

### Experiential Labs 회차

```bash
cp config/opencode.experiential.jsonc.example labs/3100/opencode.jsonc
```

### vLLM 회차

```bash
cp config/opencode.vllm.jsonc.example labs/3100/opencode.jsonc
```

`labs/3100/opencode.jsonc`는 개인 실행 설정이므로 Git에 포함되지 않습니다. 예제 파일은
하나만 선택하며 서로 합치지 않습니다.

vLLM의 Base URL과 모델명은 강의 환경에 따라 달라질 수 있습니다. 다음 두 값을 강사가 안내한 정보와 대조합니다.

```jsonc
"baseURL": "http://192.168.123.112:8081/v1"
"model": "class-vllm/qwen3.8-flash-next"
```

직접 수정했다면 JSON의 따옴표와 쉼표를 지웁니다. API Key를 설정 파일에 직접 작성하지 않습니다.

## 5. API Key 입력

DeepSeek 회차에서만 OpenCode를 실행할 동일한 터미널에 환경 변수를 설정합니다.

```bash
read -s "DEEPSEEK_API_KEY?DeepSeek API Key: "
export DEEPSEEK_API_KEY
echo
```

Windows Ubuntu의 기본 Bash에서 위 `read` 문법이 동작하지 않으면 다음을 사용합니다.

```bash
read -s -p 'DeepSeek API Key: ' DEEPSEEK_API_KEY
export DEEPSEEK_API_KEY
echo
```

키 값 자체를 출력하지 않고 설정 여부만 확인합니다.

```bash
test -n "$DEEPSEEK_API_KEY" && echo 'DeepSeek key is set'
```

새 터미널을 열면 환경 변수는 사라집니다. `.zshrc`, `.bashrc`, 명령 기록, Git 파일에 API Key를 저장하지 않습니다.

### Experiential Labs

Experiential Labs 회차에서는 `xpl_`로 시작하는 Gateway Key를 사용합니다.

macOS zsh:

```bash
read -s "EXPLABS_API_KEY?Experiential Labs API Key: "
export EXPLABS_API_KEY
echo
```

Windows WSL2 Ubuntu Bash:

```bash
read -s -p 'Experiential Labs API Key: ' EXPLABS_API_KEY
export EXPLABS_API_KEY
echo
```

설정 여부만 확인합니다.

```bash
test -n "$EXPLABS_API_KEY" && echo 'Experiential Labs key is set'
```

## 6. 모델 목록 확인

실습 폴더로 이동합니다.

```bash
cd labs/3100
pwd
opencode models --standalone
```

성공 기준:

- DeepSeek 회차: `class-deepseek/deepseek-flash` 표시
- Experiential Labs 회차: `experiential/deepseek-v4.1-flash` 표시
- vLLM 회차: `class-vllm/qwen3.8-flash-next` 또는 강사가 지정한 모델 표시

모델이 없다면 다음을 확인합니다.

```bash
ls -l opencode.jsonc
opencode debug config --standalone
```

설정 전체를 공유할 때는 API Key가 포함되지 않았는지 먼저 확인합니다.

## 7. 첫 실행

현재 경로가 `labs/3100`인지 확인한 다음 실행합니다.

```bash
opencode --standalone
```

이 수업에서는 모든 회차를 `--standalone`으로 실행합니다. 현재 터미널의 Provider 설정과
API Key를 새 OpenCode 프로세스에 직접 전달하며, 이전 실습에서 남은 백그라운드 서비스의
설정과 섞이는 문제를 막습니다. 이미 서비스가 실행 중이라면 다음처럼 중지한 뒤 같은
터미널에서 실행합니다.

```bash
opencode service stop
opencode --standalone
```

첫 화면에서 모델명을 확인하고 다음처럼 짧게 요청합니다.

```text
현재 프로젝트 지침에 따라 웹 점검 중 읽으면 안 되는 로컬 파일과, 대신 사용해야 할 점검 근거를 두 문장으로 알려줘. 파일은 열지 마.
```

성공 기준:

- 응답이 반환됨
- `server.py`, `static/**`, `Dockerfile` 등 표적 구현 파일을 읽지 않는다고 설명함
- 브라우저와 HTTP 응답에서 관찰한 정보를 점검 근거로 사용한다고 설명함
- 파일을 수정하지 않음

이 동작은 `labs/3100/AGENTS.md`에서 정의합니다. OpenCode는 현재 작업 폴더의
`AGENTS.md`를 세션 시작 시 프로젝트 지침으로 자동 로드합니다. 지침을 추가하거나 수정한
뒤에는 기존 대화를 이어 쓰지 말고 새 `--standalone` 세션을 시작합니다.

종료는 `Ctrl+C`를 사용합니다.

## 8. 권한 승인 원칙

OpenCode가 명령 실행을 요청하면 다음을 확인합니다.

1. 현재 작업 폴더가 `labs/3100`인지
2. 대상 주소가 `127.0.0.1:3100` 또는 강사가 지정한 실습 주소인지
3. 파일 삭제, Docker 전체 정리, 시스템 설정 변경이 포함되지 않았는지
4. 명령의 기대 결과를 이해했는지

`sudo`, `docker system prune`, `docker compose down -v`, 홈 디렉토리 전체 수정은 수업 중 강사의 명시적 안내 없이 승인하지 않습니다.
`cat`, `grep`, `rg`, `find` 등으로 `labs/3100`의 표적 구현 소스를 읽으려는 명령도
승인하지 않습니다. 표적 조사는 실행 중인 `http://127.0.0.1:3100`에 대한 브라우저 또는
HTTP 요청으로 수행합니다.

## 9. 준비된 Skill 적용

첫 번째 Naive 실습 전에는 프로젝트 Skill 폴더가 비어 있어야 합니다.

```bash
find .opencode/skills -mindepth 1 -maxdepth 1 -print
```

출력이 없어야 합니다. Skill은 강의 단계에서 `skills/source`의 지정 항목만 복사합니다.

기본 실행을 마친 뒤 OpenCode를 종료하고 저장소 루트에서 3100 전용 Skill을 설치합니다.

macOS Terminal과 Windows WSL2의 Ubuntu에서 같은 Bash 명령을 사용합니다. Windows에서는
PowerShell의 `Copy-Item`이나 별도로 설치한 `opencode.exe`와 혼용하지 않습니다.

```bash
mkdir -p labs/3100/.opencode/skills
cp -R skills/source/public-web-inventory labs/3100/.opencode/skills/
cp -R skills/source/known-vulnerability-triage labs/3100/.opencode/skills/
```

다음 파일이 보이면 설치가 끝난 것입니다.

```text
labs/3100/.opencode/skills/public-web-inventory/SKILL.md
labs/3100/.opencode/skills/public-web-inventory/references/report-schema.md
labs/3100/.opencode/skills/known-vulnerability-triage/SKILL.md
```

저장소 루트에서 CVE MCP를 기동합니다.

```bash
docker compose up -d --build cve-mcp
docker compose ps cve-mcp
```

프로젝트 폴더로 이동해 MCP를 등록하고 저장된 설정을 확인합니다.

```bash
cd labs/3100
opencode mcp add cve-intel --url http://127.0.0.1:8800/mcp
opencode debug config --standalone
opencode --standalone
```

새 세션의 OpenCode 입력창에서 다음 Slash Command를 차례로 실행합니다.

```text
/skills
/mcps
```

`/skills`에서 `public-web-inventory`와 `known-vulnerability-triage`, `/mcps`에서
`cve-intel connected`를 확인합니다. 각 목록은 `Esc`로 닫습니다. 두 명령은 상태 확인용이며
Skill이나 MCP를 직접 실행하지 않습니다. `/public-web-inventory` 또는 `/cve-intel` 같은 실행
명령은 사용하지 않습니다.

이어서 두 실습 요청을 일반 프롬프트로 실행합니다. 공개 경로·API 조사에는
`public-web-inventory`, 제품·버전 기반 CVE 조사에는 `known-vulnerability-triage`가 선택되는지
확인합니다. CVE 조사에서는 `cve-intel` Tool Call과 Tool Result가 실제 실행 기록에 남아야 합니다.
Skill을 직접 작성하거나 수정하는 과정은 수강생 실습에 포함하지 않습니다.
