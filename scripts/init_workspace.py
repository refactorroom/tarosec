#!/usr/bin/env python3
"""Create a unique Tarosec run directory and print its path.

By default runs are created under PROJECT/.tarosec/workspace/. Updating
the project's .gitignore requires --update-gitignore.
"""
import argparse
import json
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
  Use `--update-gitignore` to ignore the run directory in Git. Review a run
  before copying or sharing it because it may contain sensitive data.

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


def ensure_ignored(project, entry=IGNORE_ENTRY):
    ignore = project / ".gitignore"
    if ignore.is_symlink() or (ignore.exists() and not ignore.is_file()):
        raise ValueError(".gitignore must be a regular file")
    data = ignore.read_bytes() if ignore.exists() else b""
    lines = data.decode("utf-8", errors="replace").splitlines()
    matches = IGNORE_MATCHES if entry == IGNORE_ENTRY else {entry, entry.lstrip("/")}
    if any(line.strip() in matches for line in lines):
        return
    newline = b"\r\n" if b"\r\n" in data else b"\n"
    prefix = b"" if not data or data.endswith((b"\n", b"\r")) else newline
    with ignore.open("ab") as file:
        file.write(prefix + b"# Tarosec run output" + newline + entry.encode() + newline)


def write_manifest(run, workflow, stages):
    manifest = {"schemaVersion": "tarosec.run/v1", "id": run.name,
                "workflow": workflow, "stages": stages}
    with tempfile.TemporaryDirectory(dir=run) as staging:
        temporary = Path(staging) / "run.json"
        temporary.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        os.replace(temporary, run / "run.json")


def initialize(project, skill, output_dir=None, update_gitignore=False):
    project = Path(project).resolve(strict=True)
    if not project.is_dir():
        raise ValueError("project must be an existing directory")
    if skill not in SKILLS:
        raise ValueError("unknown Tarosec skill")
    if output_dir is None:
        base = safe_directory(project / ".tarosec")
        ensure_readme(base)
        parent = safe_directory(base / "workspace")
    else:
        parent = Path(output_dir).resolve(strict=True)
        if not parent.is_dir():
            raise ValueError("output must be an existing directory")
    if update_gitignore:
        if output_dir is not None:
            raise ValueError("--update-gitignore applies only to the default workspace")
        ensure_ignored(project)
    run = Path(tempfile.mkdtemp(prefix=f"{skill}-", dir=parent))
    write_manifest(run, "workspace", {"workspace": {"status": "completed"}})
    return run


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project", help="existing project directory")
    parser.add_argument("--skill", required=True, choices=SKILLS)
    parser.add_argument("--output-dir", type=Path,
                        help="existing parent directory (default: PROJECT/.tarosec/workspace)")
    parser.add_argument("--update-gitignore", action="store_true", help="ignore the default workspace in Git")
    args = parser.parse_args()
    try:
        print(initialize(args.project, args.skill, args.output_dir, args.update_gitignore))
    except (OSError, RuntimeError, ValueError) as error:
        print(f"Initialization failed: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
