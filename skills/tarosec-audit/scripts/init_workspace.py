#!/usr/bin/env python3
"""Create a unique run directory outside a project and print its path."""
import argparse
import os
import sys
import tempfile
from pathlib import Path

SKILLS = (
    "tarosec", "tarosec-audit", "tarosec-red", "tarosec-blue",
    "tarosec-purple", "tarosec-simulate", "tarosec-report",
)


def initialize(project, skill, output_dir=None):
    project = Path(project).resolve(strict=True)
    if not project.is_dir():
        raise ValueError("project must be an existing directory")
    if skill not in SKILLS:
        raise ValueError("unknown Tarosec skill")
    if output_dir is None:
        # tempfile.gettempdir() probes candidates by writing a file. Select a
        # candidate without probing so containment is checked before any write.
        output_dir = os.getenv("TMPDIR") or os.getenv("TEMP") or os.getenv("TMP")
        if not output_dir and os.name != "nt":
            output_dir = "/tmp"
        if not output_dir:
            raise ValueError("choose an existing directory with --output-dir")

    parent = Path(output_dir).resolve(strict=True)
    if not parent.is_dir() or parent.is_relative_to(project):
        raise ValueError("output must be an existing directory outside the project")
    return Path(tempfile.mkdtemp(prefix=f"{skill}-", dir=parent))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project", help="existing project directory")
    parser.add_argument("--skill", required=True, choices=SKILLS)
    parser.add_argument("--output-dir", type=Path,
                        help="existing parent directory outside the project (default: system temporary directory)")
    args = parser.parse_args()
    try:
        print(initialize(args.project, args.skill, args.output_dir))
    except (OSError, RuntimeError, ValueError) as error:
        print(f"Initialization failed: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
