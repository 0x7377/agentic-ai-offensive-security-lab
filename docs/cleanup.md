# 수업 환경 정리

## 잠시 중단

다음 수업에서 이어서 사용할 때는 컨테이너만 중지합니다. 데이터, 컨테이너와 이미지는 보존됩니다.

```bash
docker compose stop 3100 3101 3102 3103 3104 3105 cve-mcp artex postgres
```

재개할 때는 필요한 서비스만 시작합니다.

```bash
docker compose start postgres artex cve-mcp 3100
```

## 컨테이너와 네트워크 정리

데이터 볼륨과 이미지는 보존합니다.

```bash
docker compose --profile "*" down
```

## ARTEX 데이터까지 초기화

등록한 자산, 작업, Finding이 삭제됩니다. 결과를 먼저 내보내고 강사의 안내가 있을 때만 실행합니다.

```bash
docker compose --profile "*" down -v
```

## 수업용 이미지 삭제

macOS / Linux:

```bash
docker images --format '{{.Repository}}:{{.Tag}}' | grep '^ai-security-classroom/'
```

Windows PowerShell:

```powershell
docker images --format '{{.Repository}}:{{.Tag}}' | Select-String '^ai-security-classroom/'
```

목록을 확인한 뒤 Docker Desktop의 **Images** 화면에서 `ai-security-classroom/*` 이미지만 선택해 삭제합니다.
