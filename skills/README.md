# 수업용 Skill

- `source/`: 사람이 읽고 수정하는 Skill 원본
- `packages/`: ARTEX에 업로드할 ZIP 파일
- `templates/`: 강사용 Skill 확장 템플릿

3100 OpenCode 실습에서는 `source/public-web-inventory/`와
`source/known-vulnerability-triage/`를 직접 작성하지 않고 프로젝트 Skill 경로로 함께 복사해
사용합니다. 전자는 공개 경로·API·폼·입력 지점의 읽기 전용 인벤토리를, 후자는 관찰된
제품·버전의 CVE Intelligence MCP 조회 절차와 적용 가능성 분류를 제공합니다.

Skill은 디렉토리 루트의 `SKILL.md`를 중심으로 필요에 따라 `references/`, `scripts/`, `assets/`를 함께 둡니다.

원본을 수정한 뒤 패키지를 다시 만들려면 저장소 루트에서 실행합니다.

```bash
python3 scripts/package-skills.py
```

Windows에서는 `python` 명령을 사용할 수도 있습니다.

```powershell
python scripts\package-skills.py
```

배포 전에 패키지 무결성을 확인합니다.

macOS:

```bash
cd skills/packages
shasum -a 256 -c SHA256SUMS.txt
```

Ubuntu:

```bash
cd skills/packages
sha256sum -c SHA256SUMS.txt
```

Windows PowerShell:

```powershell
Get-FileHash skills\packages\*.zip -Algorithm SHA256
```

PowerShell 출력은 `SHA256SUMS.txt`의 각 파일 값과 대조합니다.
