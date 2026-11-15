# Windows 실습 환경 준비

이 과정은 Windows 11 x64, WSL2, Ubuntu 24.04와 Docker Desktop의 Linux 컨테이너 모드를 기준으로 합니다. 수업 명령은 PowerShell과 Ubuntu 명령을 구분해서 실행해야 합니다.

## 준비 완료 기준

- Windows의 가상화 기능 활성화
- WSL2와 Ubuntu 24.04 정상 실행
- Docker Desktop의 WSL2 엔진과 Ubuntu 통합 활성화
- Ubuntu에서 Docker Client·Server·Compose·Buildx 정상
- Git, curl, Python 3, unzip 사용 가능
- 저장소가 WSL의 사용자 홈 아래에 위치

## 1. Windows와 가상화 확인

작업 관리자의 **성능 → CPU**에서 **가상화: 사용**인지 확인합니다. 꺼져 있다면 PC 제조사 안내에 따라 UEFI/BIOS에서 Intel VT-x 또는 AMD-V를 활성화합니다.

PowerShell에서 Windows 버전과 WSL 상태를 확인합니다.

```powershell
Get-ComputerInfo | Select-Object WindowsProductName, WindowsVersion, OsBuildNumber
wsl --status
wsl --version
```

Windows on ARM이나 기관 VDI처럼 중첩 가상화가 제한된 환경은 수업 전에 강사에게 알립니다.

## 2. Windows Terminal과 WSL2 설치

Windows Terminal이 없다면 일반 PowerShell에서 설치합니다.

```powershell
winget install --id Microsoft.WindowsTerminal -e
```

`winget`을 찾지 못하면 Microsoft Store에서 **App Installer**를 설치하거나 업데이트합니다.

Ubuntu가 없다면 관리자 PowerShell에서 실행합니다.

```powershell
wsl --install -d Ubuntu-24.04
```

안내가 나오면 작업을 저장하고 재부팅합니다. Ubuntu 최초 실행에서 Linux 사용자명과 비밀번호를 만듭니다. 비밀번호 입력 중 문자가 표시되지 않는 것은 정상입니다.

재부팅 후 일반 PowerShell에서 확인합니다.

```powershell
wsl --update
wsl --set-default-version 2
wsl --list --verbose
```

`Ubuntu-24.04`의 VERSION이 `2`여야 합니다. VERSION이 1일 때만 변환합니다.

```powershell
wsl --set-version Ubuntu-24.04 2
```

이후 Windows Terminal의 탭 메뉴에서 **Ubuntu-24.04**를 엽니다.

## 3. Ubuntu 기본 도구 설치

아래 명령은 PowerShell이 아니라 Ubuntu 탭에서 실행합니다.

```bash
sudo apt update
sudo apt install -y git curl ca-certificates python3 unzip zip
git --version
curl --version
python3 --version
```

성공 기준은 각 도구의 버전이 출력되는 것입니다.

## 4. Docker Desktop 설치와 WSL 연동

Docker Desktop을 공식 페이지에서 설치합니다.

- <https://docs.docker.com/desktop/setup/install/windows-install/>

설치 후 Docker Desktop을 실행하고 다음 설정을 확인합니다.

| 설정 위치 | 확인할 값 |
|---|---|
| Settings → General | Use WSL 2 based engine 활성화 |
| Settings → Resources → WSL Integration | Ubuntu-24.04 활성화 |

설정을 바꿨다면 **Apply & Restart**를 선택합니다. WSL Integration이 보이지 않으면 Docker Desktop이 Windows 컨테이너 모드인지 확인하고 Linux 컨테이너 모드로 전환합니다.

Ubuntu 탭을 새로 열어 다음을 확인합니다.

```bash
docker version
docker compose version
docker buildx version
docker run --rm hello-world
```

성공 기준:

- Client와 Server가 모두 표시됨
- Compose와 Buildx 버전이 출력됨
- `Hello from Docker!`가 출력됨

이 구성에서는 Ubuntu 안에 `docker-ce`나 별도 Docker 엔진을 설치하지 않습니다. Docker Desktop이 제공하는 엔진을 사용합니다.

## 5. WSL 자원과 디스크 확인

PowerShell에서 다음 파일을 열 수 있습니다.

```powershell
notepad "$env:USERPROFILE\.wslconfig"
```

호스트 RAM이 16 GB 이상인 PC의 예시는 다음과 같습니다. 기존 `.wslconfig`가 있다면 덮어쓰지 말고 항목을 병합합니다.

```ini
[wsl2]
memory=8GB
processors=4
swap=4GB
```

실제 PC보다 큰 값을 지정하지 않습니다. 변경 후 실행 중인 WSL 작업을 저장하고 Docker Desktop을 종료한 다음 PowerShell에서 실행합니다.

```powershell
wsl --shutdown
```

Docker Desktop과 Ubuntu를 다시 열어 확인합니다.

```bash
free -h
df -h ~
docker info --format 'CPU={{.NCPU}} MemoryBytes={{.MemTotal}}'
docker system df
```

## 6. 저장소 받기

저장소는 WSL의 Linux 홈 아래에 둡니다. `/mnt/c`, 바탕 화면, OneDrive에서 직접 실행하면 파일 권한과 I/O 성능 문제가 생길 수 있습니다.

Ubuntu 탭에서 실행합니다.

```bash
mkdir -p ~/ai-security-lab
cd ~/ai-security-lab
git clone <강사가 안내한 저장소 URL>
cd agentic-ai-offensive-security-lab
pwd
git status --short
```

`pwd`가 `/home/<사용자>/ai-security-lab/agentic-ai-offensive-security-lab` 형태여야 합니다.

Windows 탐색기로 현재 WSL 폴더를 보고 싶을 때만 다음 명령을 사용합니다.

```bash
explorer.exe .
```

같은 디렉토리가 이미 있다면 삭제하거나 다시 clone하지 말고 현재 상태를 확인합니다.

```bash
git remote -v
git status --short
```

## 7. 환경 파일 준비

Ubuntu 탭의 저장소 루트에서 실행합니다.

```bash
cp .env.example .env
chmod 600 .env
nano .env
```

`nano`에서는 저장할 때 `Ctrl+O`, Enter, 종료할 때 `Ctrl+X`를 누릅니다. 다음 두 값을 예시 문자열이 아닌 수업용 비밀번호로 바꿉니다.

- `POSTGRES_PASSWORD`
- `ARTEX_ADMIN_PASSWORD`

API Key는 이 파일에 미리 넣지 않습니다.

## 8. OS 단계 사전 점검

```bash
docker info >/dev/null && echo 'Docker OK'
docker compose config --quiet
git --version
python3 --version
```

이후 [OpenCode 설치와 첫 실행](setup-opencode.md)로 이동합니다. 모든 설치를 완료한 다음 Ubuntu 탭에서 실행합니다.

```bash
./scripts/preflight.sh
```

PowerShell에서 저장소를 운용하기로 강사가 별도로 지정한 경우에만 다음 스크립트를 사용합니다.

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\preflight.ps1
```

기본 Windows 교육 흐름은 Ubuntu 탭에서 Linux 명령을 사용하는 방식입니다.
