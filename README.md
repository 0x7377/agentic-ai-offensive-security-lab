# Agentic AI for Offensive Security — 실습 키트

OpenCode와 ARTEX를 이용한 취약점 진단 수업용 저장소입니다. 이 저장소 하나에 실습 표적, ARTEX 수업 환경, MCP 서버, 수업용 Skill과 작업 템플릿을 모았습니다.

> 이 환경은 교육용으로 제공된 로컬 표적에만 사용합니다. 강의 슬라이드와 정답·강사용 실행 데이터는 포함하지 않습니다.

## 준비물

- Docker Desktop 4.x 이상
- Git
- OpenCode 실습에 사용할 LLM 접속 정보
  - 강사가 안내한 vLLM Base URL과 모델명, 또는
  - 개인 DeepSeek API Key
- Chrome 또는 Edge 최신 버전
- 권장 메모리: 16 GB 이상
- 권장 Docker 할당: CPU 4개 이상, 메모리 8 GB 이상
- 여유 디스크: 15 GB 이상

## 강의 전 준비 순서

처음 참여한다면 아래 순서대로 진행합니다. 각 문서에는 실행 위치, 명령, 성공 기준과 오류 확인 방법이 포함돼 있습니다.

1. [macOS 준비](docs/setup-macos.md) 또는 [Windows 준비](docs/setup-windows.md)
2. [OpenCode 설치와 첫 실행](docs/setup-opencode.md)
3. [DeepSeek 또는 vLLM 연결](docs/setup-llm.md)
4. [ARTEX·MCP·Skill 준비](docs/setup-artex.md)
5. [수업 전 최종 점검표](docs/pre-class-checklist.md)

## 1. 저장소 받기

```bash
git clone <강사가 안내한 저장소 URL>
cd agentic-ai-offensive-security-lab
```

환경 파일을 만들고 예시 비밀번호를 반드시 바꿉니다. 이 단계는 OS와 OpenCode 설치를 완료한 뒤 저장소 루트에서 진행합니다.

### macOS / Linux

```bash
cp .env.example .env
./scripts/preflight.sh
```

### Windows PowerShell

```powershell
Copy-Item .env.example .env
powershell -ExecutionPolicy Bypass -File .\scripts\preflight.ps1
```

## 2. 실습 흐름

| 단계 | 실행 대상 | 호스트 PC 접속 주소 | ARTEX 내부 주소 |
|---|---|---|---|
| OpenCode 기초 | `3100` | <http://127.0.0.1:3100> | `http://portal.digitaltrust.lab:8080` |
| 개별 진단 | `3101` | <http://127.0.0.1:3101> | `http://rail.korail.lab:8080` |
| 개별 진단 | `3102` | <http://127.0.0.1:3102> | `http://research.nrf.lab:8080` |
| 개별 진단 | `3103` | <http://127.0.0.1:3103> | `http://workorder.kogas-tech.lab:8080` |
| 개별 진단 | `3104` | <http://127.0.0.1:3104> | `http://customs.kcs.lab:8080` |
| 종합 실습 | `3105` | <http://127.0.0.1:3105> | `http://nris.research.lab:8080` |
| ARTEX | `artex` | <http://127.0.0.1:8787> | — |
| CVE MCP | `cve-mcp` | <http://127.0.0.1:8800/mcp> | `http://cve-mcp:8000/mcp` |

숫자는 포트이자 Compose 서비스명입니다. 표적의 취약점 종류는 서비스명에 노출하지 않습니다.

## 3. 단계별 실행

### OpenCode 기초 실습만 시작

```bash
docker compose up -d --build 3100
```

### CVE MCP 서버 시작

```bash
docker compose up -d --build cve-mcp
```

### ARTEX 시작

```bash
docker compose --profile artex up -d
```

첫 실행은 이미지 다운로드와 DB 초기화로 몇 분 걸릴 수 있습니다. 상태는 `docker compose ps`로 확인합니다.

### 개별 실습 표적 시작

```bash
docker compose up -d --build 3101 3102 3103 3104
```

### 개별 실습 표적 종료

```bash
docker compose stop 3101 3102 3103 3104
```

### 종합 실습만 시작

```bash
docker compose up -d --build 3105
```

### 전체 종료

```bash
docker compose --profile "*" down
```

DB 볼륨까지 초기화하려면 `docker compose --profile "*" down -v`를 사용합니다. 이 명령은 ARTEX에 등록한 자산·작업·Finding을 삭제하므로 강사의 안내가 있을 때만 실행하세요.

## 저장소 구성

```text
.
├── artex/              # 고정 버전 ARTEX 소스와 수업용 초기화 SQL
├── config/             # OpenCode의 vLLM / DeepSeek / Experiential 설정 예시
├── docs/               # OS별 준비, 문제 해결, 정리 안내
├── labs/3100~3105/     # Docker Compose로 실행하는 실습 표적
├── mcp/                # CVE MCP 서버
├── runtime/            # 실행 중 생성되는 ARTEX 데이터(커밋 제외)
├── scripts/            # 준비 점검과 단계별 실행 도우미
├── skills/             # Skill 원본, 배포 ZIP, 제작 템플릿
└── templates/          # ARTEX 작업 템플릿과 실습 기록 양식
```

## 문제 해결

포트 충돌, Docker 미실행, ARTEX 초기화 지연은 [문제 해결 안내](docs/troubleshooting.md)를 확인하세요. 수업 종료 후 정리 방법은 [환경 정리 안내](docs/cleanup.md)에 있습니다.

## 출처와 라이선스

이 저장소가 직접 작성한 Lab, Compose, 스크립트, 템플릿과 문서는 Apache License 2.0으로 배포합니다.

제3자 구성요소는 각자의 기존 라이선스를 유지합니다.

- `artex/source/`: AGPL-3.0
- `mcp/cve-mcp-server/`: Apache-2.0
- Claude-BugHunter에서 변형한 일부 Skill 콘텐츠: CC BY 4.0

정확한 범위와 저작자 표시는 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)와 [LICENSES/README.md](LICENSES/README.md)를 확인하세요.
