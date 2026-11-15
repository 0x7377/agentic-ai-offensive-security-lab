# 3101 실습 대상

- Host PC: `http://127.0.0.1:3101`
- ARTEX 내부 주소: `http://rail.korail.lab:8080`
- 목적: 철도 승무운영 통합지원 형태의 로컬 교육용 웹 자산을 수동 및 ARTEX로 점검한다.

화면, 계정, 인물, 일정 정보는 모두 합성 데이터다. 취약점 유형, 성공 조건, 페이로드는 이 문서에서 제공하지 않는다.

## 안전 경계

- 로컬 Docker 네트워크 안에서만 실습한다.
- 호스트 볼륨과 Docker socket을 마운트하지 않는다.
- 컨테이너는 non-root, read-only root filesystem, capability drop 상태로 실행한다.
