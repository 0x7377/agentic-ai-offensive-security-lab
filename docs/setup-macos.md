# macOS 실습 환경 준비

이 문서는 Apple Silicon과 Intel Mac을 모두 대상으로 합니다. 이미 설치된 도구는 다시 설치하지 말고 버전과 동작만 확인합니다.

## 준비 완료 기준

- macOS 버전과 CPU 아키텍처 확인
- Docker Client·Server·Compose·Buildx 정상
- `hello-world` 컨테이너 실행 성공
- Git과 Python 3 사용 가능
- 저장소가 사용자 홈 아래에 위치
- Docker에 CPU 4개, 메모리 8 GB 이상 할당

## 1. Mac 사양 확인

Apple 메뉴의 **이 Mac에 관하여**에서 칩과 메모리를 확인합니다. 터미널은 **응용 프로그램 → 유틸리티 → 터미널**에서 엽니다.

```bash
uname -m
sw_vers
sysctl -n hw.memsize
df -h ~
```

아키텍처는 일반적으로 다음처럼 표시됩니다.

| 출력 | 의미 |
|---|---|
| `arm64` | Apple Silicon |
| `x86_64` | Intel 또는 Rosetta 터미널 |

호스트 메모리는 16 GB 이상, 여유 디스크는 15 GB 이상을 권장합니다. 부족하면 수업 전에 강사와 실습 장비를 조율합니다.

## 2. Command Line Tools와 Git

먼저 설치 여부를 확인합니다.

```bash
git --version
python3 --version
xcode-select -p
```

`xcode-select`가 개발자 도구를 찾지 못하면 다음 명령을 실행하고 설치 창을 완료합니다.

```bash
xcode-select --install
```

설치 후 새 터미널에서 다시 확인합니다.

```bash
git --version
python3 --version
```

Git과 Python의 정확한 마이너 버전보다 명령이 정상 실행되는지가 중요합니다.

## 3. Docker Desktop 설치

공식 설치 페이지에서 칩에 맞는 Docker Desktop을 받습니다.

- <https://docs.docker.com/desktop/setup/install/mac-install/>

DMG를 열고 Docker를 **Applications**로 옮긴 뒤 실행합니다. 최초 실행 시 이용 조건과 필요한 권한 요청을 확인합니다.

```bash
open -a Docker
```

메뉴 막대의 Docker 아이콘이 정상 상태가 될 때까지 기다립니다. 이후 다음 명령을 하나씩 실행합니다.

```bash
docker version
docker compose version
docker buildx version
docker run --rm hello-world
```

성공 기준:

- `docker version`에 Client와 Server가 모두 표시됨
- Compose와 Buildx 버전이 출력됨
- 마지막 명령에 `Hello from Docker!`가 출력됨

Server 항목이 없으면 Docker Desktop이 아직 준비되지 않았거나 실행되지 않은 상태입니다.

## 4. Docker 자원 설정

Docker Desktop에서 **Settings → Resources**를 엽니다.

| 항목 | 권장값 |
|---|---:|
| CPU | 4개 이상 |
| Memory | 8 GB 이상 |
| Disk image limit | 여유 공간 15 GB 이상 |

호스트 메모리가 16 GB라면 Docker에 8 GB 정도를 할당하고 다른 대형 프로그램을 종료합니다. 설정을 바꿨다면 **Apply & Restart** 후 다시 확인합니다.

```bash
docker info --format 'CPU={{.NCPU}} MemoryBytes={{.MemTotal}}'
docker system df
```

Apple Silicon에서 이미지 실행 중 `exec format error`가 발생할 때만 Docker Desktop의 가상화·Rosetta 설정을 확인합니다. Rosetta가 필요하다는 명확한 오류가 있을 때 다음 명령을 사용합니다.

```bash
softwareupdate --install-rosetta
```

## 5. 저장소 받기

저장소는 사용자 홈 아래에 둡니다. iCloud Drive, 외장 네트워크 드라이브처럼 동기화·권한 개입이 있는 경로는 피합니다.

```bash
mkdir -p ~/ai-security-lab
cd ~/ai-security-lab
git clone <강사가 안내한 저장소 URL>
cd agentic-ai-offensive-security-lab
pwd
git status --short
```

`pwd`의 마지막 경로가 `agentic-ai-offensive-security-lab`이고, `git status`에 임의 변경이 없어야 합니다.

같은 디렉토리가 이미 있다면 덮어쓰거나 다시 clone하지 않습니다. 다음 명령으로 현재 저장소인지 확인한 뒤 강사에게 기존 설치 여부를 알립니다.

```bash
git remote -v
git status --short
```

## 6. 환경 파일 준비

저장소 루트에서 실행합니다.

```bash
cp .env.example .env
chmod 600 .env
```

텍스트 편집기로 `.env`를 열고 다음 두 값을 예시 문자열이 아닌 수업용 비밀번호로 바꿉니다.

- `POSTGRES_PASSWORD`
- `ARTEX_ADMIN_PASSWORD`

API Key는 `.env`에 미리 넣지 않습니다. DeepSeek 키는 [LLM 연결 안내](setup-llm.md)에 따라 환경 변수 또는 ARTEX 화면에 직접 입력합니다.

## 7. OS 단계 사전 점검

OpenCode 설치 전에도 Docker와 저장소 상태는 점검할 수 있습니다.

```bash
docker info >/dev/null && echo 'Docker OK'
docker compose config --quiet
git --version
python3 --version
```

이후 [OpenCode 설치와 첫 실행](setup-opencode.md)로 이동합니다. 모든 설치를 마친 뒤에는 저장소 루트에서 다음 종합 점검을 실행합니다.

```bash
./scripts/preflight.sh
```

실행 권한 오류가 있을 때만 다음 명령을 한 번 실행합니다.

```bash
chmod +x scripts/*.sh
```
