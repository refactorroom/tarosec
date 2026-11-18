#!/usr/bin/env python3
"""Copy the shared foundation into every skill so each installs independently.

Agent Skills hosts load a skill directory on its own, so a skill cannot rely on
repo-root files. Canonical sources live at the repo root; each skill gets copies:

  references/*.md          -> skills/<skill>/references/shared/
  schemas/*.schema.json    -> skills/<skill>/assets/schemas/
  scripts/validate_record.py -> skills/<skill>/scripts/
  LICENSE, SOURCE_NOTICES.md  -> skills/<skill>/

Usage: sync_shared.py [--check]   (--check: exit 1 on drift, write nothing)
"""
from __future__ import annotations

import filecmp
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def plan() -> list[tuple[Path, Path]]:
    pairs = []
    for skill in sorted(p for p in (ROOT / "skills").iterdir() if (p / "SKILL.md").is_file()):
        for src in sorted((ROOT / "references").glob("*.md")):
            pairs.append((src, skill / "references" / "shared" / src.name))
        for src in sorted((ROOT / "schemas").glob("*.schema.json")):
            if src.name.startswith(("simulation-", "scenario.")) and skill.name != "tarosec-simulate":
                continue
            pairs.append((src, skill / "assets" / "schemas" / src.name))
        src = ROOT / "scripts" / "validate_record.py"
        pairs.append((src, skill / "scripts" / src.name))
        for name in ("LICENSE", "SOURCE_NOTICES.md"):
            pairs.append((ROOT / name, skill / name))
    if (ROOT / "skills/tarosec-simulate/SKILL.md").is_file():
        classifier = "scripts/classify_exercise.py"
        pairs.append((ROOT / "skills/tarosec-purple" / classifier,
                      ROOT / "skills/tarosec-simulate" / classifier))
    return pairs


def main(argv: list[str]) -> int:
    check = "--check" in argv
    drift = [(s, d) for s, d in plan() if not d.is_file() or not filecmp.cmp(s, d, shallow=False)]
    for src, dst in drift:
        rel = dst.relative_to(ROOT)
        if check:
            print(f"DRIFT {rel}")
        else:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(src, dst)
            print(f"synced {rel}")
    if check:
        print("in sync" if not drift else f"{len(drift)} file(s) out of sync; run scripts/sync_shared.py")
        return 1 if drift else 0
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
