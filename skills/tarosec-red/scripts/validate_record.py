#!/usr/bin/env python3
"""Validate a Tarosec JSON record against a Tarosec schema (stdlib only).

Supports the JSON Schema subset Tarosec schemas use. Any other keyword is an
error, so an unsupported constraint can never pass silently.

Usage: validate_record.py SCHEMA.json RECORD.json
Exit: 0 valid, 1 invalid, 2 usage/IO error.

Canonical copy: scripts/validate_record.py (synced into each skill by
scripts/sync_shared.py).
"""
from __future__ import annotations

import json
import re
import sys
from typing import Any

ANNOTATIONS = {"$schema", "$id", "title", "description"}
SUPPORTED = ANNOTATIONS | {
    "type", "const", "enum", "required", "properties", "additionalProperties",
    "items", "minItems", "minLength", "pattern", "uniqueItems",
}
TYPES = {
    "object": dict, "array": list, "string": str, "boolean": bool,
    "integer": int, "number": (int, float),
}


def _type_ok(value: Any, name: str) -> bool:
    if name in ("integer", "number") and isinstance(value, bool):
        return False
    return isinstance(value, TYPES[name])


def validate(value: Any, schema: dict, path: str = "$") -> list[str]:
    unknown = set(schema) - SUPPORTED
    if unknown:
        return [f"{path}: schema uses unsupported keyword(s) {sorted(unknown)}"]
    errors: list[str] = []
    if "type" in schema and not _type_ok(value, schema["type"]):
        return [f"{path}: expected {schema['type']}, got {type(value).__name__}"]
    if "const" in schema and value != schema["const"]:
        errors.append(f"{path}: must equal {schema['const']!r}")
    if "enum" in schema and value not in schema["enum"]:
        errors.append(f"{path}: {value!r} not in {schema['enum']}")
    if isinstance(value, str):
        if len(value) < schema.get("minLength", 0):
            errors.append(f"{path}: shorter than {schema['minLength']}")
        if "pattern" in schema and not re.search(schema["pattern"], value):
            errors.append(f"{path}: does not match {schema['pattern']}")
    if isinstance(value, list):
        if len(value) < schema.get("minItems", 0):
            errors.append(f"{path}: fewer than {schema['minItems']} items")
        if schema.get("uniqueItems") and len({json.dumps(v, sort_keys=True) for v in value}) != len(value):
            errors.append(f"{path}: items not unique")
        if "items" in schema:
            for i, item in enumerate(value):
                errors += validate(item, schema["items"], f"{path}[{i}]")
    if isinstance(value, dict):
        for key in schema.get("required", []):
            if key not in value:
                errors.append(f"{path}: missing required '{key}'")
        props = schema.get("properties", {})
        for key, sub in value.items():
            if key in props:
                errors += validate(sub, props[key], f"{path}.{key}")
            elif schema.get("additionalProperties") is False:
                errors.append(f"{path}: unexpected property '{key}'")
    return errors


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print(__doc__.strip().splitlines()[2], file=sys.stderr)
        return 2
    try:
        with open(argv[1], encoding="utf-8") as f:
            schema = json.load(f)
        with open(argv[2], encoding="utf-8") as f:
            record = json.load(f)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    errors = validate(record, schema)
    for e in errors:
        print(e)
    print("VALID" if not errors else f"INVALID ({len(errors)} error(s))")
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
