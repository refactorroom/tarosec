#!/usr/bin/env python3
"""Generate an offline Tarosec Markdown, JSON and evidence manifest bundle."""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from tempfile import NamedTemporaryFile

from report_inputs import MAX_REPORT_BYTES, bounded_read, json_bytes
from report_model import MODES, build_report
from report_output import bundle, validate_report


def write_bundle(output, contents, overwrite):
    # The parent must already exist. Refuse a symlink or a populated directory
    # without an explicit overwrite of an existing Tarosec bundle.
    if output.is_symlink():
        raise ValueError("output directory must not be a symbolic link")
    try:
        output.mkdir(mode=0o700)
    except FileExistsError:
        if not overwrite or not output.is_dir():
            raise ValueError("output already exists")
        try:
            previous = json_bytes(bounded_read(output / "report.json", MAX_REPORT_BYTES))
            if validate_report(previous):
                raise ValueError
            for name in contents:
                if not (output / name).is_file() or (output / name).is_symlink():
                    raise ValueError
        except (OSError, ValueError, RecursionError):
            raise ValueError("--overwrite requires an existing Tarosec report bundle") from None
    lock = output / ".tarosec-report.lock"
    staged = {}
    with lock.open("x", encoding="utf-8"):
        try:
            for name, text in contents.items():
                with NamedTemporaryFile(mode="w", encoding="utf-8", newline="\n", delete=False, dir=output) as file:
                    staged[name] = file.name
                    file.write(text)
            # Publish report.json last so bundle validation can detect an
            # interruption that left a companion from another generation.
            for name, temporary in staged.items():
                os.replace(temporary, output / name)
        finally:
            for temporary in staged.values():
                Path(temporary).unlink(missing_ok=True)
            lock.unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="JSON record or evidence directory")
    parser.add_argument("--type", choices=MODES, default="summary")
    parser.add_argument("--output", required=True, type=Path, help="new report directory")
    parser.add_argument("--overwrite", action="store_true", help="replace an existing report bundle")
    parser.add_argument("--retest", type=Path, help="second snapshot directory or file")
    parser.add_argument("--baseline-id")
    parser.add_argument("--retest-id")
    parser.add_argument("--generated-at", help="optional explicit ISO 8601 timestamp with offset")
    args = parser.parse_args()
    if args.type != "compare" and any((args.retest, args.baseline_id, args.retest_id)):
        parser.error("comparison options require --type compare")
    if args.type == "compare" and not all((args.baseline_id, args.retest_id)):
        parser.error("compare requires --baseline-id and --retest-id")
    try:
        output = args.output.absolute()
        for source in (args.input, args.retest):
            if source is None:
                continue
            input_path, output_path = source.resolve(), output.resolve()
            if (input_path == output_path or output_path in input_path.parents
                    or (source.is_dir() and input_path in output_path.parents)):
                raise ValueError("use a separate output directory outside the supplied inputs")
        report = build_report(args.input, args.type, args.retest, args.baseline_id, args.retest_id, args.generated_at)
        errors = validate_report(report)
        if errors:
            raise ValueError("generated report failed its contract")
        contents = bundle(report)
        if any(len(value.encode("utf-8")) > MAX_REPORT_BYTES for value in contents.values()):
            raise ValueError("generated bundle exceeds the output size limit")
        write_bundle(output, contents, args.overwrite)
    except (OSError, RecursionError):
        print("error: unable to read inputs or write report bundle within the requested paths", file=sys.stderr)
        return 2
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    gap_count = sum(len(snapshot["gaps"]) for snapshot in report["snapshots"])
    gap_count += int(bool(report.get("comparison", {}).get("gap")))
    print(f"{report['id']} saved with {gap_count} gap(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
