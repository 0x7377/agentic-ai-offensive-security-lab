# OpenCode · Skill · MCP 실습 작업 폴더

OpenCode는 터미널에서 LLM과 대화하면서 파일 읽기, 명령 실행, Skill 절차 로드, MCP 도구
호출을 한 작업 흐름으로 묶는 에이전트 실행 환경이다. 웹 채팅처럼 답변만 받는 것이 아니라,
현재 폴더를 작업 공간으로 삼아 허용된 도구를 실제로 사용한다. 따라서 OpenCode를 실행하기
전에 터미널의 현재 경로가 `labs/3100`인지 반드시 확인한다.

OpenCode에서 보이는 과정은 다음과 같다.

1. 사용자의 요청을 해석하고 작업 순서를 세운다.
2. 현재 폴더의 파일과 등록된 Skill을 읽는다.
3. 필요한 명령이나 MCP Tool을 호출한다.
4. Tool Result를 확인하고 다음 행동 또는 최종 답변을 결정한다.

명령 실행 승인은 단순한 다음 버튼이 아니다. 명령, 대상 주소, 파일 경로가 수업 Scope와
일치하는지 확인하는 사용자 통제 단계다.

따라서 첫 번째 실행 전에는 `.opencode/skills/`가 비어 있어야 한다. 기본 실행을 마친 뒤
저장소에 포함된 `public-web-inventory`와 `known-vulnerability-triage` Skill을 이 폴더로
한 번에 복사해 활성화한다. 수강생이 Skill을 새로 작성하는 실습은 진행하지 않는다.

## 모델 설정

저장소 루트에서 모델에 맞는 예시를 이 작업 폴더로 복사한다.

macOS Terminal과 Windows WSL2의 Ubuntu에서 같은 Bash 명령을 사용한다. Windows에서는
PowerShell의 `Copy-Item`이나 별도로 설치한 `opencode.exe`와 혼용하지 않는다.

```bash
cp config/opencode.deepseek.jsonc.example labs/3100/opencode.jsonc
# 또는
cp config/opencode.experiential.jsonc.example labs/3100/opencode.jsonc
# 또는
cp config/opencode.vllm.jsonc.example labs/3100/opencode.jsonc
```

DeepSeek 사용자는 `DEEPSEEK_API_KEY`, Experiential Labs 사용자는 `EXPLABS_API_KEY`를
OpenCode를 실행할 동일한 터미널에 설정한다. vLLM의 Base URL과 모델명은 강사가 안내한
값을 입력한다.

설정을 마친 뒤 작업 경로로 이동한다.

```bash
cd labs/3100
```

모델 목록은 `opencode models --standalone`로 확인한다. 이 수업의 모든 회차는 기존
백그라운드 서비스를 사용하지 않고 `opencode --standalone`으로 실행한다.

## 권한 주의

OpenCode가 명령 실행 승인을 물으면 명령과 대상 주소를 읽은 뒤 승인한다. 이 수업의 허용
대상은 `127.0.0.1:3100`과 강의자료에 명시한 로컬 실습 주소뿐이다. 승인 화면을 무조건
통과시키지 않는다.

## 준비된 Skill 설치

기본 실행을 끝낸 뒤 OpenCode를 종료하고, 저장소 루트에서 다음 명령을 실행한다.

macOS Terminal과 Windows WSL2의 Ubuntu에서 실행한다.

```bash
mkdir -p labs/3100/.opencode/skills
cp -R skills/source/public-web-inventory labs/3100/.opencode/skills/
cp -R skills/source/known-vulnerability-triage labs/3100/.opencode/skills/
```

설치 결과는 다음 두 파일로 확인한다.

```text
labs/3100/.opencode/skills/public-web-inventory/
├── SKILL.md
└── references/report-schema.md
labs/3100/.opencode/skills/known-vulnerability-triage/
└── SKILL.md
```

## CVE MCP 기동과 등록

두 Skill을 복사한 뒤 저장소 루트에서 CVE MCP를 기동한다.

```bash
docker compose up -d --build cve-mcp
docker compose ps cve-mcp
```

OpenCode 프로젝트 폴더로 이동해 프로젝트 범위 MCP를 등록하고 설정을 확인한다.

```bash
cd labs/3100
opencode mcp add cve-intel --url http://127.0.0.1:8800/mcp
opencode debug config --standalone
```

출력에서 `cve-intel` 서버와 URL이 확인되어야 한다. 그다음 같은 폴더에서 새 세션을 시작한다.

```bash
opencode --standalone
```

## 설치한 Skill과 MCP 사용

OpenCode 입력창에서 다음 Slash Command를 차례로 입력한다.

```text
/skills
```

목록에 `public-web-inventory`와 `known-vulnerability-triage`가 모두 표시되는지 확인하고
`Esc`로 닫는다. 이어서 다음 명령을 입력한다.

```text
/mcps
```

`cve-intel`이 `connected`로 표시되는지 확인하고 `Esc`로 닫는다.

`/skills`와 `/mcps`는 로드·연결 상태를 확인하는 메뉴이며 Skill이나 MCP를 실행하지 않는다.
`/public-web-inventory`, `/known-vulnerability-triage`, `/cve-intel` 같은 실행 명령은 없다.
실제 사용은 다음의 일반 프롬프트를 입력하면 Harness가 적절한 Skill을 선택하고 필요한 MCP
Tool을 호출하는 방식이다.

공개 경로·API 조사에는 `tasks/02-skilled.md`, 제품·버전 기반 CVE 조사에는
`tasks/04-mcp-enabled.md`의 요청을 사용한다.

공개 경로·API 조사 요청에는 `public-web-inventory`, 제품·버전 기반 CVE 조사 요청에는
`known-vulnerability-triage`가 선택되는지 확인한다. 후자의 실행 기록에는 `cve-intel` MCP
Tool Call과 Tool Result가 남아야 한다. 최종 답변에 이름이 적힌 것만으로 사용을 판단하지 않는다.
