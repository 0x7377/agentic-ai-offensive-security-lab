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
현재 작업 폴더의 최상위 파일과 디렉토리 이름만 읽어서 알려줘. 파일은 수정하지 마.
```

성공 기준:

- 응답이 반환됨
- 현재 폴더의 `README.md`, `tasks`, `static` 등을 인식함
- 파일을 수정하지 않음

종료는 `Ctrl+C`를 사용합니다.

## 8. 권한 승인 원칙

OpenCode가 명령 실행을 요청하면 다음을 확인합니다.

1. 현재 작업 폴더가 `labs/3100`인지
2. 대상 주소가 `127.0.0.1:3100` 또는 강사가 지정한 실습 주소인지
3. 파일 삭제, Docker 전체 정리, 시스템 설정 변경이 포함되지 않았는지
4. 명령의 기대 결과를 이해했는지

`sudo`, `docker system prune`, `docker compose down -v`, 홈 디렉토리 전체 수정은 수업 중 강사의 명시적 안내 없이 승인하지 않습니다.

## 9. Skill 실습 전 상태

첫 번째 Naive 실습 전에는 프로젝트 Skill 폴더가 비어 있어야 합니다.

```bash
find .opencode/skills -mindepth 1 -maxdepth 1 -print
```

출력이 없어야 합니다. Skill은 강의 단계에서 `skills/source`의 지정 항목만 복사합니다. 자세한 절차는 [ARTEX·MCP·Skill 준비](setup-artex.md)를 참고합니다.
