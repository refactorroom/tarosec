#!/usr/bin/env python3
"""Create a unique Tarosec run directory and print its path.

By default runs are created under PROJECT/.tarosec/workspace/. The helper also
writes PROJECT/.tarosec/README.md when it is missing and makes sure the
project's .gitignore ignores .tarosec/workspace/.
"""
import argparse
import os
import sys
import tempfile
from pathlib import Path

SKILLS = (
    "tarosec", "tarosec-audit", "tarosec-red", "tarosec-blue",
    "tarosec-purple", "tarosec-simulate", "tarosec-report", "tarosec-git-issues",
)
IGNORE_ENTRY = "/.tarosec/workspace/"
IGNORE_MATCHES = {".tarosec/workspace", ".tarosec/workspace/", "/.tarosec/workspace",
                  "/.tarosec/workspace/", ".tarosec/", "/.tarosec/", ".tarosec", "/.tarosec"}
README = """# .tarosec

Tarosec stores security work for this project here.

- `workspace/` holds one directory per run, such as `tarosec-audit-XXXX/`.
  Every Tarosec skill saves scan results, findings, evidence and reports there.
  It is listed in `.gitignore` because runs can contain sensitive data.
  Review a run before you copy anything out of it or share it.

Delete old runs when you no longer need them. Tarosec recreates `workspace/`
on the next run.
"""


def safe_directory(path):
    """Create path (one level) privately, refusing symbolic links."""
    if path.is_symlink():
        raise ValueError(f"{path.name} must not be a symbolic link")
    if path.exists():
        if not path.is_dir():
            raise ValueError(f"{path.name} exists and is not a directory")
    else:
        path.mkdir(mode=0o700)
    return path


def ensure_readme(base):
    readme = base / "README.md"
    if readme.is_symlink():
        raise ValueError(".tarosec/README.md must not be a symbolic link")
    if not readme.exists():
        readme.write_text(README, encoding="utf-8", newline="\n")


def ensure_ignored(project):
    ignore = project / ".gitignore"
    if ignore.is_symlink():
        raise ValueError(".gitignore must not be a symbolic link")
    data = ignore.read_bytes() if ignore.exists() else b""
    lines = data.decode("utf-8", errors="replace").splitlines()
    if any(line.strip() in IGNORE_MATCHES for line in lines):
        return
    newline = b"\r\n" if b"\r\n" in data else b"\n"
    prefix = b"" if not data or data.endswith((b"\n", b"\r")) else newline
    with ignore.open("ab") as file:
        file.write(prefix + b"# Tarosec run output" + newline + IGNORE_ENTRY.encode() + newline)


def initialize(project, skill, output_dir=None):
    project = Path(project).resolve(strict=True)
    if not project.is_dir():
        raise ValueError("project must be an existing directory")
    if skill not in SKILLS:
        raise ValueError("unknown Tarosec skill")
    if output_dir is None:
        base = safe_directory(project / ".tarosec")
        ensure_readme(base)
        parent = safe_directory(base / "workspace")
        ensure_ignored(project)
    else:
        parent = Path(output_dir).resolve(strict=True)
        if not parent.is_dir():
            raise ValueError("output must be an existing directory")
    return Path(tempfile.mkdtemp(prefix=f"{skill}-", dir=parent))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project", help="existing project directory")
    parser.add_argument("--skill", required=True, choices=SKILLS)
    parser.add_argument("--output-dir", type=Path,
                        help="existing parent directory (default: PROJECT/.tarosec/workspace)")
    args = parser.parse_args()
    try:
        print(initialize(args.project, args.skill, args.output_dir))
    except (OSError, RuntimeError, ValueError) as error:
        print(f"Initialization failed: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
