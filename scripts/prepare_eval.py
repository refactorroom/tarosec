#!/usr/bin/env python3
"""Prepare a blind evaluation workspace for one case and arm.

Copies only the case fixture (never evaluations/reviewer/) into a NEW directory
and writes PROMPT.md. The baseline arm gets no skill instructions; the skill arm
is told to use the Tarosec plugin through the host (no fake programmatic call).

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
    task = (dest / "TASK.md").read_text()
    prefix = "" if a.arm == "baseline" else (
        "The Tarosec plugin is installed for this session. Use its skills if they apply.\n\n")
    (dest / "PROMPT.md").write_text(prefix + task)
    print(dest)
    return 0


if __name__ == "__main__":
    sys.exit(main())
