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

따라서 이 폴더에는 수강생이 현재 단계에서 볼 자료만 둔다. 첫 번째 Skill 실습 전에는
`.opencode/skills/`가 비어 있어야 한다. 강사가 Skill을 배포한 뒤에만 해당 폴더로 복사한다.

## 모델 설정

저장소 루트에서 모델에 맞는 예시를 이 작업 폴더로 복사한다.

### macOS / Linux

```bash
cp config/opencode.deepseek.jsonc.example labs/3100/opencode.jsonc
# 또는
cp config/opencode.experiential.jsonc.example labs/3100/opencode.jsonc
# 또는
cp config/opencode.vllm.jsonc.example labs/3100/opencode.jsonc
```

### Windows PowerShell

```powershell
Copy-Item config\opencode.deepseek.jsonc.example labs\3100\opencode.jsonc
# 또는
Copy-Item config\opencode.experiential.jsonc.example labs\3100\opencode.jsonc
# 또는
Copy-Item config\opencode.vllm.jsonc.example labs\3100\opencode.jsonc
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
