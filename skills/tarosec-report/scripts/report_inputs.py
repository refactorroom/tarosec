"""Read bounded Tarosec snapshots and reconcile their evidence."""
from __future__ import annotations

import hashlib
import json
import os
import re
import stat
from collections import defaultdict
from datetime import datetime
from io import StringIO
from pathlib import Path
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from validate_record import load_json, validate

SCHEMAS = Path(__file__).resolve().parent.parent / "assets" / "schemas"
KINDS = ("case", "engagement", "evidence", "exercise", "finding", "simulation-result")
MAX_ENTRIES = 2000
MAX_RECORD_BYTES = 1024 * 1024
MAX_ARTIFACT_BYTES = 32 * 1024 * 1024
MAX_READ_BYTES = 128 * 1024 * 1024
MAX_REPORT_BYTES = 64 * 1024 * 1024
IDENTIFIER = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}")
TOKEN = re.compile(r"(?i)(?:gh[pousr]_|github_pat_|xox[baprs]-|sk[-_]|AKIA|ASIA|AIza|eyJ[A-Za-z0-9_-]+\.)[A-Za-z0-9_-]{12,}")
REFERENCE_FIELDS = {
    "engagementRef": "engagement", "evidenceRefs": "evidence", "findingRefs": "finding",
    "exerciseRefs": "exercise", "relatedFindings": "finding", "relatedExercises": "exercise",
    "retestOf": "exercise",
}


def safe_id(value):
    return isinstance(value, str) and IDENTIFIER.fullmatch(value) is not None and TOKEN.search(value) is None


def canonical(value):
    return json.dumps(value, ensure_ascii=True, allow_nan=False, separators=(",", ":"), sort_keys=True)


def digest(value):
    return hashlib.sha256(canonical(value).encode("ascii")).hexdigest()


def load_schema(kind):
    with (SCHEMAS / f"{kind}.schema.json").open(encoding="utf-8") as file:
        return load_json(file)


def timestamp(value):
    if not value or len(value) > 40 or not re.fullmatch(r"[0-9TtZz:+.,-]+", value):
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def original_zone(value):
    if value in ("UTC", "GMT", "Z", "unknown") or re.fullmatch(r"[+-](?:0[0-9]|1[0-9]|2[0-3]):[0-5][0-9]", value):
        return value
    if len(value) <= 64 and re.fullmatch(r"[A-Za-z_+-]+(?:/[A-Za-z0-9_+-]+){1,3}", value):
        try:
            ZoneInfo(value)
            return value
        except ZoneInfoNotFoundError:
            pass
    return "unknown"


def bounded_read(path, limit):
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0)
    if path.is_symlink():
        raise ValueError("symbolic link")
    with os.fdopen(os.open(path, flags), "rb") as file:
        info = os.fstat(file.fileno())
        if not stat.S_ISREG(info.st_mode) or info.st_size > limit:
            raise ValueError("not a regular file within the read limit")
        value = file.read(limit + 1)
        if len(value) > limit:
            raise ValueError("read limit exceeded")
        return value


def json_bytes(raw):
    return load_json(StringIO(raw.decode("utf-8")))


def references(value):
    if isinstance(value, list):
        for row in value:
            yield from references(row)
    elif isinstance(value, dict):
        for key, sub in value.items():
            if key in REFERENCE_FIELDS:
                for item in sub if isinstance(sub, list) else [sub]:
                    yield REFERENCE_FIELDS[key], item
            elif isinstance(sub, (dict, list)):
                yield from references(sub)


def candidates(path):
    if not path.is_dir():
        return [path], []
    remaining = [path]
    files = []
    visited = 0
    skipped = False
    while remaining:
        directory = remaining.pop()
        with os.scandir(directory) as entries:
            for entry in entries:
                visited += 1
                if visited > MAX_ENTRIES:
                    # Reject the whole traversal to avoid a filesystem-dependent subset.
                    return [], [{"code": "input-entry-limit"}]
                if entry.name.startswith("."):
                    continue
                if entry.is_symlink():
                    skipped = True
                elif entry.is_dir(follow_symlinks=False):
                    remaining.append(Path(entry.path))
                elif entry.name.endswith(".json"):
                    files.append(Path(entry.path))
    return sorted(files), [{"code": "symbolic-link-skipped"}] if skipped else []


class Snapshot:
    def __init__(self, path):
        if path.is_symlink() or not (path.is_dir() or path.is_file()):
            raise ValueError("input must be an existing regular JSON file or directory")
        path = path.resolve()
        self.root = path if path.is_dir() else path.parent
        self.records = {}
        self.paths = {}
        self.sources = []
        self.evidence = {}
        self.simulation_refs = {}
        self.artifact_bytes = 0
        self.artifact_cache = {}
        files, self.gaps = candidates(path)
        self.load_records(files, directory=path.is_dir())

    def load_records(self, files, directory):
        schemas = {kind: load_schema(kind) for kind in KINDS}
        matches = defaultdict(dict)
        total = 0
        ignored = {"report", "scenario", "simulation-events", "simulation-alerts"}
        for index, file in enumerate(files, 1):
            try:
                raw = bounded_read(file, min(MAX_RECORD_BYTES, MAX_READ_BYTES - total))
                total += len(raw)
                record = json_bytes(raw)
            except (OSError, ValueError, RecursionError):
                self.gaps.append({"code": "unreadable-or-malformed-json", "inputIndex": index})
                continue
            version = record.get("schemaVersion", "") if isinstance(record, dict) else ""
            if not isinstance(version, str) or not version.startswith("tarosec."):
                if not directory:
                    self.gaps.append({"code": "unsupported-record", "inputIndex": index})
                continue
            kind = version[8:].split("/", 1)[0]
            if kind in ignored and directory:
                continue
            if kind not in schemas:
                self.gaps.append({"code": "unsupported-record", "inputIndex": index})
                continue
            errors = validate(record, schemas[kind])
            if errors:
                self.gaps.append({"code": "invalid-record", "kind": kind, "inputIndex": index})
                continue
            identity = digest(record)
            ref = record.get("runId", identity) if kind == "simulation-result" else record["id"]
            if not safe_id(ref):
                self.gaps.append({"code": "unsafe-identifier", "kind": kind, "inputIndex": index})
                continue
            self.sources.append({"kind": kind, "id": ref, "contentSha256": identity, "inputIndex": index})
            paths = matches[(kind, ref)].setdefault(identity, (record, []))[1]
            paths.append(file)
        for key, variants in sorted(matches.items()):
            kind, ref = key
            if len(variants) > 1:
                self.gaps.append({"code": "conflicting-id", "kind": kind, "id": ref})
                continue
            record, paths = next(iter(variants.values()))
            self.records[key] = record
            self.paths[key] = paths
            if len(paths) > 1:
                self.gaps.append({"code": "duplicate-id", "kind": kind, "id": ref})
        if not self.records:
            self.gaps.append({"code": "no-usable-records"})

    def check_references(self, baseline=None):
        for (kind, ref), record in self.records.items():
            for target_kind, target_id in set(references(record)):
                target = target_kind, target_id
                external_retest = (baseline is not None and kind == "exercise"
                                   and target_kind == "exercise" and target_id == record.get("retestOf")
                                   and target in baseline.records)
                resolved = target in self.records or external_retest
                if kind == "exercise" and target_kind == "evidence" and ref in self.simulation_refs:
                    resolved = target_id in self.simulation_refs[ref]
                if not resolved:
                    gap = {"code": "unresolved-reference", "kind": kind, "id": ref, "targetKind": target_kind}
                    if safe_id(target_id):
                        gap["reference"] = target_id
                    self.gaps.append(gap)
            if kind == "evidence":
                self.add_evidence(ref, record)

    def artifact_status(self, root, name, expected):
        if not name or not expected:
            return "no-reference" if not name else "hash-unavailable"
        rel = Path(name)
        if rel.is_absolute() or ".." in rel.parts:
            return "outside-input"
        key = root, rel
        if key not in self.artifact_cache:
            current = root
            for part in rel.parts:
                current /= part
                if current.is_symlink():
                    return "outside-input"
            self.artifact_cache[key] = None
            try:
                raw = bounded_read(current, min(MAX_ARTIFACT_BYTES, MAX_READ_BYTES - self.artifact_bytes))
                self.artifact_bytes += len(raw)
                self.artifact_cache[key] = hashlib.sha256(raw).hexdigest()
            except (OSError, ValueError):
                pass
        actual = self.artifact_cache[key]
        if actual is None:
            return "artifact-unavailable"
        return "match" if actual == expected else "mismatch"

    def add_evidence(self, ref, record):
        check = self.artifact_status(self.root, record.get("artifactPath"), record.get("sha256"))
        self.evidence[ref] = check
        if check != "match" or record["integrity"] == "mismatch":
            self.gaps.append({"code": "evidence-integrity-unresolved", "kind": "evidence", "id": ref})
        if not timestamp(record["collectedAt"]) or original_zone(record["originalTimezone"]) == "unknown":
            self.gaps.append({"code": "timestamp-or-timezone-unknown", "kind": "evidence", "id": ref})

    def evidence_state(self, refs, exercise=None):
        if exercise in self.simulation_refs:
            return "hash-matched" if refs and set(refs) <= self.simulation_refs[exercise] else "unresolved"
        if not refs or any(("evidence", ref) not in self.records for ref in refs):
            return "unresolved"
        if any(self.evidence[ref] in {"outside-input", "mismatch", "artifact-unavailable"}
               or self.records["evidence", ref]["integrity"] == "mismatch" for ref in refs):
            return "unresolved"
        if all(self.evidence[ref] == "match" for ref in refs):
            return "hash-matched"
        return "records-only"
