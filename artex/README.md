# 수업용 ARTEX 구성

`source/`는 `jiwoochris/artex-global`의 `v0.3.15-global.1` 태그를 깨끗하게 가져온 소스다.
현재 기본 Compose는 같은 태그의 GHCR 이미지를 사용한다. `classroom/agents-ko.sql`은 수업에
필요한 한글 Agent 이름, 최소 권한 Tool 설정 및 선택 기업 URL의 Task 자산 연결 안전장치를
적용한다.

현재 작업 디렉터리에 있던 광범위한 미커밋 번역 변경은 포함하지 않았다. 향후 코드 수준의
수정은 이 기준 소스에 작은 단위로 적용하고 테스트한 뒤 수업용 이미지로 릴리스한다.

- Upstream: `https://github.com/jiwoochris/artex-global.git`
- 기준 태그: `v0.3.15-global.1`
- 라이선스: `source/LICENSE`의 AGPL-3.0

