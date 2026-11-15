#!/usr/bin/env python3
"""skills/source 하위 Skill을 재현 가능한 ZIP으로 패키징한다."""

import hashlib
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "skills" / "source"
OUTPUT = ROOT / "skills" / "packages"


def package(skill_dir: Path) -> None:
    output = OUTPUT / f"{skill_dir.name}.zip"
    with ZipFile(output, "w", ZIP_DEFLATED) as archive:
        for path in sorted(p for p in skill_dir.rglob("*") if p.is_file()):
            relative = Path(skill_dir.name) / path.relative_to(skill_dir)
            info = ZipInfo(relative.as_posix(), (2026, 1, 1, 0, 0, 0))
            info.compress_type = ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, path.read_bytes())
    print(f"created: {output.relative_to(ROOT)}")


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    skills = [p for p in sorted(SOURCE.iterdir()) if p.is_dir() and (p / "SKILL.md").is_file()]
    if not skills:
        raise SystemExit("skills/source에서 SKILL.md를 찾지 못했습니다.")
    for skill in skills:
        package(skill)
    lines = []
    for archive in sorted(OUTPUT.glob("*.zip")):
        digest = hashlib.sha256(archive.read_bytes()).hexdigest()
        lines.append(f"{digest}  {archive.name}")
    (OUTPUT / "SHA256SUMS.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"created: {(OUTPUT / 'SHA256SUMS.txt').relative_to(ROOT)}")


if __name__ == "__main__":
    main()
