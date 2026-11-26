#!/usr/bin/env python3
"""Resolve one normalized Tarosec mode against the host's available skills."""
import argparse
import json

ROUTES = {
    "audit": "tarosec-audit", "scan": "tarosec-audit", "red": "tarosec-red",
    "blue": "tarosec-blue", "logs": "tarosec-blue", "incident": "tarosec-blue",
    "purple": "tarosec-purple", "simulate": "tarosec-simulate",
    "intel": "tarosec-audit", "verify": "tarosec-audit", "report": "tarosec-report",
}


def route(mode, evidence, available):
    if mode == "help":
        return {"action": "help", "modes": sorted([*ROUTES, "help", "scan-report"])}
    if mode == "scan-report":
        return {"action": "workflow", "mode": mode}
    mode = mode or {"logs": "blue", "exercise": "purple"}.get(evidence, "audit")
    skill = "tarosec-purple" if mode == "verify" and evidence == "exercise" else ROUTES.get(mode)
    if skill is None:
        return {"action": "unsupported", "message": "Unknown mode. Use help for supported modes."}
    if skill in available:
        return {"action": "use", "skill": skill, "mode": mode}
    fallback = "read-only report summary" if mode == "report" else "read-only inventory"
    return {"action": "missing", "skill": skill, "installSelector": skill, "fallback": fallback}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", nargs="?")
    parser.add_argument("--evidence", choices=("project", "logs", "exercise", "unknown"), default="unknown")
    parser.add_argument("--available", action="append", default=[])
    args = parser.parse_args()
    result = route(args.mode, args.evidence, args.available)
    print(json.dumps(result, sort_keys=True))
    return int(result["action"] == "unsupported")


if __name__ == "__main__":
    raise SystemExit(main())
