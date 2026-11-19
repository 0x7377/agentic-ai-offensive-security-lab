# 수업 전 최종 점검표

강의 전날 또는 수업 시작 전에 한 번 확인합니다. 직접 확인하지 못한 항목은 완료로 표시하지 않습니다.

## PC와 도구

- [ ] 호스트 메모리 16 GB 이상 또는 강사와 대체 장비 협의
- [ ] 여유 디스크 15 GB 이상
- [ ] Docker Desktop 실행
- [ ] `docker version`에 Client·Server 표시
- [ ] `docker compose version` 정상
- [ ] `docker buildx version` 정상
- [ ] `docker run --rm hello-world` 성공
- [ ] Git과 Python 3 정상
- [ ] OpenCode V2 명령 정상

## 저장소

- [ ] 저장소가 사용자 홈 아래에 있음
- [ ] Windows는 WSL Ubuntu 홈에 있음
- [ ] `.env` 생성 및 예시 비밀번호 변경
- [ ] `.env`가 Git ignored 상태
- [ ] `docker compose config --quiet` 성공
- [ ] `./scripts/preflight.sh` 성공

## LLM

### DeepSeek 회차

- [ ] 개인 API Key 발급
- [ ] Key를 파일·채팅·캡처에 저장하지 않음
- [ ] 잔액 또는 사용 가능 상태 확인
- [ ] 모델 목록에 `deepseek-flash` 표시
- [ ] 짧은 1회 호출 성공
- [ ] OpenCode 모델 목록 표시
- [ ] ARTEX LLM 연결 시험 성공

### vLLM 회차

- [ ] 강사 안내 Base URL 확인
- [ ] 강사 안내 모델 ID 확인
- [ ] `/models` 요청 성공
- [ ] 지정 모델 표시
- [ ] OpenCode 모델 목록 표시
- [ ] ARTEX LLM 연결 시험 성공

## OpenCode·Skill·MCP

- [ ] `labs/3100`에서 OpenCode 실행
- [ ] Naive 실습 전 `.opencode/skills`가 비어 있음
- [ ] 3100 컨테이너 healthy
- [ ] 호스트 브라우저에서 3100 접속
- [ ] CVE MCP 컨테이너 healthy
- [ ] OpenCode MCP 등록 또는 설정 확인
- [ ] `skills/source/public-web-inventory/SKILL.md` 존재
- [ ] `skills/packages/public-web-inventory.zip` 존재
- [ ] `skills/source/known-vulnerability-triage/SKILL.md` 존재
- [ ] `skills/packages/known-vulnerability-triage.zip` 존재
- [ ] Skill 배포 ZIP 무결성 확인

macOS에서는 다음 명령의 모든 항목이 `OK`인지 확인합니다.

```bash
cd skills/packages
shasum -a 256 -c SHA256SUMS.txt
cd ../..
```

Ubuntu에서는 `shasum -a 256` 대신 `sha256sum -c SHA256SUMS.txt`를 사용합니다.

## ARTEX

- [ ] PostgreSQL healthy
- [ ] ARTEX 접속 가능
- [ ] `artex-classroom-init` 종료 코드 0
- [ ] 관리자 로그인 성공
- [ ] 메뉴와 Agent 이름 한글 표시
- [ ] CVE MCP 연결 상태 확인
- [ ] 지정 Skill 업로드 및 Agent 연결
- [ ] ARTEX에서 `portal.digitaltrust.lab:8080` 통신 성공

## 실습 표적

개별 실습을 시작할 때만 기동합니다.

```bash
docker compose up -d --build 3101 3102 3103 3104
docker compose ps 3101 3102 3103 3104
```

- [ ] 3101 healthy, 호스트 HTTP 200
- [ ] 3102 healthy, 호스트 HTTP 200
- [ ] 3103 healthy, 호스트 HTTP 200
- [ ] 3104 healthy, 호스트 HTTP 200

종합 실습은 개별 실습을 중지한 뒤 별도로 확인합니다.

```bash
docker compose stop 3101 3102 3103 3104
docker compose up -d --build 3105
docker compose ps 3105
```

- [ ] 3105 healthy, 호스트 HTTP 200

## 완료 기록

- 점검 일시:
- OS·아키텍처:
- Docker 버전:
- OpenCode 버전:
- 교육 회차: DeepSeek / vLLM
- 사용 모델:
- 미완료 항목과 사유:
