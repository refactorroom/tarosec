#!/usr/bin/env python3
"""Validate a Tarosec report and optionally check its bundle and source records."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from report_inputs import MAX_REPORT_BYTES, bounded_read, json_bytes
from report_model import build_report
from report_output import bundle, validate_report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("report", type=Path)
    parser.add_argument("--bundle", action="store_true", help="also check Markdown and manifest")
    parser.add_argument("--input", type=Path, help="recompute the report from these source records")
    parser.add_argument("--retest", type=Path, help="second source snapshot if originally used")
    args = parser.parse_args()
    if args.retest and not args.input:
        parser.error("--retest requires --input")
    try:
        report = json_bytes(bounded_read(args.report, MAX_REPORT_BYTES))
        errors = validate_report(report)
        if not errors and args.retest and report["type"] != "compare":
            parser.error("--retest requires a comparison report")
        if not errors and args.bundle:
            for name, expected in bundle(report).items():
                if name != "report.json" and bounded_read(args.report.parent / name, MAX_REPORT_BYTES) != expected.encode("utf-8"):
                    errors.append(f"{name} differs from the report")
        if not errors and args.input:
            comparison = report.get("comparison", {})
            actual = build_report(args.input, report["type"], args.retest, comparison.get("baselineId"),
                                  comparison.get("retestId"), report.get("generatedAt"))
            if actual != report:
                errors.append("report differs from the supplied source records or evidence bytes")
    except (OSError, ValueError, RecursionError):
        print("error: unable to read report, bundle or source records", file=sys.stderr)
        return 2
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    check = "source and structure" if args.input else "structure and internal consistency"
    print(f"VALID ({check})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
