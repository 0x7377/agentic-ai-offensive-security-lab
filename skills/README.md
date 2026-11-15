# 수업용 Skill

- `source/`: 사람이 읽고 수정하는 Skill 원본
- `packages/`: ARTEX에 업로드할 ZIP 파일
- `templates/`: Skill 제작 실습의 시작 템플릿

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
