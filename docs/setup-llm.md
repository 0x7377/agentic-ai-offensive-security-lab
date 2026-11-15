# DeepSeek 또는 vLLM 연결

두 교육 회차는 실습 표적과 프롬프트는 같고 LLM 연결만 다릅니다. 강사가 지정한 회차 하나만 준비합니다.

| 구분 | DeepSeek API 회차 | 강의장 vLLM 회차 |
|---|---|---|
| Base URL | `https://api.deepseek.com` | 강사가 안내한 URL |
| 기본 모델 | `deepseek-flash` | 강사가 안내한 Qwen 모델 |
| 인증 | 개인 API Key | 강의 환경에 따라 없음 또는 안내값 |
| 비용 | 개인 잔액 사용 | 강의장 공유 자원 사용 |
| 운영 특성 | 비교적 빠른 응답 | 동시 사용 시 지연 가능 |

## 준비 완료 기준

- Base URL에 네트워크 연결 가능
- 모델 목록에서 지정 모델 확인
- 짧은 1회 응답 성공
- OpenCode 모델 목록에 수업 모델 표시
- ARTEX에 같은 Base URL·모델 등록
- API Key가 파일이나 명령 기록에 남지 않음

## A. DeepSeek API 회차

### 1. 계정과 API Key

DeepSeek 개발자 플랫폼에 본인 계정으로 로그인합니다.

- 플랫폼: <https://platform.deepseek.com/>
- API Key: <https://platform.deepseek.com/api_keys>
- 공식 모델·요금: <https://api-docs.deepseek.com/quick_start/pricing/>

가입, 결제, API Key 발급과 입력은 수강생이 직접 수행합니다. 키를 채팅, 화면 캡처, 보고서, `.env`, `opencode.jsonc`에 넣지 않습니다.

요금과 최소 충전 단위는 바뀔 수 있으므로 강사가 안내한 예상 사용량과 공식 페이지의 현재 가격을 확인합니다. 모델 호출과 ARTEX 연결 테스트도 과금될 수 있습니다.

### 2. 잔액과 모델 확인

저장소의 점검 스크립트는 키를 숨김 입력받으며 저장하지 않습니다.

```bash
python3 scripts/llm-check.py deepseek balance
python3 scripts/llm-check.py deepseek models
```

성공 기준:

- 잔액 API가 사용 가능 상태를 반환
- 모델 목록에 `deepseek-flash` 표시

401은 키, 402는 잔액, 429는 호출 빈도 제한을 먼저 확인합니다. 같은 오류가 반복되면 추가 호출을 멈춥니다.

### 3. 유료 1회 호출

다음 명령은 짧은 응답을 한 번 요청하므로 소액 요금이 발생합니다.

```bash
python3 scripts/llm-check.py deepseek chat --model deepseek-flash
```

`API_OK`에 해당하는 짧은 응답과 사용량이 표시되면 정상입니다. 응답 텍스트만 확인하지 말고 HTTP 성공과 모델명도 함께 확인합니다.

### 4. OpenCode 연결

```bash
cp config/opencode.deepseek.jsonc.example labs/3100/opencode.jsonc
read -s -p 'DeepSeek API Key: ' DEEPSEEK_API_KEY
export DEEPSEEK_API_KEY
echo
cd labs/3100
opencode models --standalone
```

macOS zsh에서는 `read -s "DEEPSEEK_API_KEY?DeepSeek API Key: "` 형식도 사용할 수 있습니다.

## B. 강의장 vLLM 회차

### 1. 강사 안내값 확인

다음 두 값은 강의장 네트워크와 서버 구성에 따라 달라질 수 있습니다.

- Base URL
- 모델 ID

예시 강의 환경:

```text
Base URL: http://192.168.123.112:8081/v1
Model: qwen3.8-flash-next
```

예시값을 고정된 운영 주소로 간주하지 말고 수업 당일 안내를 우선합니다.

### 2. 네트워크와 모델 목록 확인

```bash
python3 scripts/llm-check.py vllm models \
  --base-url http://192.168.123.112:8081/v1
```

Windows PowerShell에서 직접 실행한다면 줄바꿈 없이 한 줄로 입력합니다.

성공 기준:

- HTTP 200
- 모델 목록에 강사가 지정한 모델 ID 표시

연결 실패 시 순서대로 확인합니다.

1. 강의장 유선·무선 네트워크에 연결됐는지
2. Base URL과 포트가 정확한지
3. VPN 또는 기관 보안 프로그램이 사설망 통신을 막는지
4. 강사 PC에서 서버가 기동 중인지

### 3. 짧은 1회 호출

공유 서버 부하를 피하기 위해 강사가 호출을 안내한 뒤 실행합니다.

```bash
python3 scripts/llm-check.py vllm chat \
  --base-url http://192.168.123.112:8081/v1 \
  --model qwen3.8-flash-next
```

### 4. OpenCode 연결

```bash
cp config/opencode.vllm.jsonc.example labs/3100/opencode.jsonc
```

강사 안내값이 예제와 다르면 `baseURL`, provider 아래 모델 ID, 최상위 `model`을 함께 맞춥니다.

```bash
cd labs/3100
opencode models --standalone
```

## ARTEX 입력값

ARTEX의 **시스템 설정 → LLM**에서 새 연결을 만들 때 다음 원칙을 적용합니다.

### DeepSeek

| 필드 | 입력 |
|---|---|
| 이름 | `DeepSeek Flash` |
| 형식 | OpenAI / Chat Completions |
| Base URL | `https://api.deepseek.com` |
| 모델 | `deepseek-flash` |
| API Key | 본인이 직접 입력 |
| Thinking | 수업 안내값, 기본은 비활성 |
| Max tokens | 4096 또는 강사 안내값 |

### vLLM

| 필드 | 입력 |
|---|---|
| 이름 | `Classroom vLLM` |
| 형식 | OpenAI / Chat Completions |
| Base URL | 강사가 안내한 Base URL |
| 모델 | 강사가 안내한 모델 ID |
| API Key | 강의 환경 안내값 |
| Max tokens | 4096 또는 강사 안내값 |

연결 테스트 성공은 모델 응답 가능 여부만 뜻합니다. 브라우저와 HTTP Tool이 실제 실습 자산에 접근하는지는 별도로 확인해야 합니다.

## 비용과 공유 서버 운영

- DeepSeek: Task 시작 전 범위와 중단 조건을 확인하고 불필요한 재시작을 피합니다.
- vLLM: 조별 시작 시각을 분산하고 느리다고 같은 Task를 중복 생성하지 않습니다.
- `max_tokens`는 한 응답의 출력 상한이며 누적 비용·누적 시간을 제한하지 않습니다.
- 브라우저 탭을 닫는 것만으로 ARTEX Task가 중지되지 않을 수 있습니다. Task 화면에서 상태를 확인합니다.
