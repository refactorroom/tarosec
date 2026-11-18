#!/usr/bin/env python3
"""Create a project workspace and a unique run directory."""
import argparse
import os
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path


def initialize(project, skill):
    project = Path(project).resolve(strict=True)
    if not project.is_dir():
        raise ValueError("project must be an existing directory")
    workspace = project / ".tarosec"
    ignore = project / ".gitignore"
    if workspace.is_symlink() or (workspace.exists() and not workspace.is_dir()):
        raise ValueError(".tarosec must be a directory, not a symlink or file")
    if ignore.is_symlink() or (ignore.exists() and not ignore.is_file()):
        raise ValueError(".gitignore must be a regular file, not a symlink")
    flags = os.O_RDWR | os.O_CREAT | getattr(os, "O_NOFOLLOW", 0)
    fd = os.open(ignore, flags, 0o644)
    with os.fdopen(fd, "r+", encoding="utf-8", newline="") as stream:
        try:
            import fcntl
            fcntl.flock(stream.fileno(), fcntl.LOCK_EX)
        except ImportError:
            pass
        contents = stream.read()
        lines = contents.splitlines()
        if not lines or lines[-1] != "/.tarosec/":
            stream.seek(0, os.SEEK_END)
            if contents and not contents.endswith(("\n", "\r")):
                stream.write("\n")
            stream.write("/.tarosec/\n")
            stream.flush()
    workspace.mkdir(mode=0o700, exist_ok=True)
    runs = workspace / "runs"
    if runs.is_symlink() or (runs.exists() and not runs.is_dir()):
        raise ValueError(".tarosec/runs must be a directory, not a symlink")
    runs.mkdir(mode=0o700, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run = runs / f"{stamp}-{skill}-{uuid.uuid4().hex[:12]}"
    run.mkdir(mode=0o700)
    return run


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project", help="existing project directory")
    parser.add_argument("--skill", required=True, choices=[
        "tarosec", "tarosec-audit", "tarosec-red", "tarosec-blue",
        "tarosec-purple", "tarosec-simulate",
    ])
    args = parser.parse_args()
    try:
        print(initialize(args.project, args.skill))
    except (OSError, UnicodeError, ValueError) as error:
        print(f"Initialization failed: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
