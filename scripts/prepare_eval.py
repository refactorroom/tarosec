#!/usr/bin/env python3
"""Prepare a blind evaluation workspace for one case and arm.

Copies the case fixture into a new directory and writes the same PROMPT.md for
both arms. The skill arm also installs Tarosec in Codex's project skill directory.
The runner must separately restrict access to the source repo and external tools.

Usage: prepare_eval.py --case P1 --arm baseline|skill --dest /tmp/tarosec-P1-baseline
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CASES = ROOT / "evaluations" / "reviewer" / "cases.json"
FIXTURES = ROOT / "evaluations" / "fixtures"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--case", required=True)
    ap.add_argument("--arm", required=True, choices=["baseline", "skill"])
    ap.add_argument("--dest", required=True)
    a = ap.parse_args()
    cases = {c["id"]: c for c in json.loads(CASES.read_text())["cases"]}
    if a.case not in cases:
        print(f"unknown case {a.case}; known: {', '.join(cases)}", file=sys.stderr)
        return 2
    dest = Path(a.dest).resolve()
    if dest.exists():
        print(f"refusing to overwrite existing {dest}", file=sys.stderr)
        return 2
    if ROOT in dest.parents or dest == ROOT:
        print("destination must be outside the tarosec repository", file=sys.stderr)
        return 2
    shutil.copytree(FIXTURES / cases[a.case]["fixture"], dest)
    if cases[a.case].get("reportExample"):
        shutil.copytree(ROOT / "examples" / "reporting" / "records", dest / "records")
    shutil.copyfile(dest / "TASK.md", dest / "PROMPT.md")
    arm = cases[a.case]
    if a.arm == "skill" or "baselineSkills" in arm:
        installed = arm.get("installedSkills" if a.arm == "skill" else "baselineSkills")
        skill_root = dest / ".agents" / "skills"
        ignore = shutil.ignore_patterns("__pycache__", "*.pyc")
        if installed is None:
            shutil.copytree(ROOT / "skills", skill_root, ignore=ignore)
        else:
            for name in installed:
                shutil.copytree(ROOT / "skills" / name, skill_root / name, ignore=ignore)
    print(dest)
    return 0


if __name__ == "__main__":
    sys.exit(main())
