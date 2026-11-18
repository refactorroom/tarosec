#!/usr/bin/env python3
"""Classify each step of a Tarosec purple exercise into a detection outcome.

Offline and deterministic: reads a tarosec.exercise/v1 JSON file with recorded
results and prints per-step outcomes. It never executes emulation, contacts a
SIEM/EDR, or decides authorization.

Usage: classify_exercise.py EXERCISE.json [--json]
Exit: 0 classified, 1 invalid exercise, 2 usage/IO error.

Outcomes (most specific first):
  Not run          execution status not_run/blocked, or no results recorded
  Inconclusive     execution failed/unknown, alert export unknown, or a missing
                   expected source whose health is false/unknown
  Prevented        executed and a control blocked it (alert state reported alongside)
  Detected         an expected rule fired on the target host within latency budget
  Detected (late)  expected rule fired on the target host after the latency budget
  Telemetry gap    executed, a healthy source recorded nothing it was expected to
  Detection gap    executed, expected telemetry observed, expected rule did not fire
"""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from validate_record import validate  # noqa: E402  (synced sibling)

SCHEMA = os.path.join(HERE, "..", "assets", "schemas", "exercise.schema.json")


def _ts(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    return dt if dt.tzinfo else None  # naive timestamps cannot be ordered safely


def classify_step(step: dict) -> tuple[str, list[str]]:
    reasons: list[str] = []
    res = step.get("results")
    if not res:
        return "Not run", ["no results recorded"]
    status = res["execution"]["status"]
    if status in ("not_run", "blocked"):
        return "Not run", [f"execution status {status}"]
    if status in ("failed", "unknown"):
        return "Inconclusive", [f"execution {status}: no evidence the behavior occurred"]

    expected = step["expected"]
    host = step["targetHost"]
    alerts = [a for a in res.get("alerts", []) if a["ruleId"] in expected["detections"]]
    for a in res.get("alerts", []):
        if a["ruleId"] not in expected["detections"] and a["status"] == "fired":
            reasons.append(f"unexpected rule {a['ruleId']} fired (not counted)")
    on_host = [a for a in alerts if a["status"] == "fired" and a.get("host", host) == host]
    off_host = [a for a in alerts if a["status"] == "fired" and a.get("host", host) != host]
    for a in off_host:
        reasons.append(f"{a['ruleId']} fired on {a['host']}, not target {host} (not counted)")

    if res["execution"].get("prevented"):
        state = "with alert" if on_host else "without matching alert"
        return "Prevented", reasons + [f"control blocked execution ({state})"]

    if on_host:
        ended = _ts(res["execution"].get("endedAt"))
        budget = expected["maxLatencySeconds"]
        late = []
        for a in on_host:
            fired = _ts(a.get("firedAt"))
            if ended is None or fired is None:
                reasons.append(f"{a['ruleId']} latency unmeasurable (missing or naive timestamp)")
                return "Detected", reasons
            delay = (fired - ended).total_seconds()
            if delay <= budget:
                return "Detected", reasons + [f"{a['ruleId']} fired {delay:.0f}s after execution"]
            late.append(f"{a['ruleId']} fired {delay:.0f}s after execution (budget {budget}s)")
        return "Detected (late)", reasons + late

    if any(a["status"] == "unknown" for a in alerts) or not alerts:
        return "Inconclusive", reasons + ["alert state for expected rule(s) unknown or not exported"]

    telemetry = {t["source"]: t for t in res.get("telemetry", [])}
    missing_healthy, missing_unknown = [], []
    for src in expected["telemetrySources"]:
        t = telemetry.get(src)
        if t is None or t["status"] == "unknown":
            missing_unknown.append(src)
        elif t["status"] == "absent":
            (missing_healthy if t.get("sourceHealthy") is True else missing_unknown).append(src)
    if missing_unknown:
        return "Inconclusive", reasons + [
            f"no confirmed collection from {', '.join(missing_unknown)} (source health false/unknown)"]
    if missing_healthy:
        return "Telemetry gap", reasons + [f"healthy source(s) recorded nothing: {', '.join(missing_healthy)}"]
    return "Detection gap", reasons + ["expected telemetry observed; expected rule(s) did not fire"]


def main(argv: list[str]) -> int:
    args = [a for a in argv[1:] if a != "--json"]
    if len(args) != 1:
        print("usage: classify_exercise.py EXERCISE.json [--json]", file=sys.stderr)
        return 2
    try:
        with open(args[0], encoding="utf-8") as f:
            exercise = json.load(f)
        with open(SCHEMA, encoding="utf-8") as f:
            schema = json.load(f)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    errors = validate(exercise, schema)
    if errors:
        print("INVALID exercise:\n" + "\n".join(errors))
        return 1
    rows = []
    for step in exercise["steps"]:
        outcome, reasons = classify_step(step)
        rows.append({"step": step["id"], "technique": step["technique"]["id"],
                     "outcome": outcome, "reasons": reasons})
    if "--json" in argv:
        print(json.dumps({"exercise": exercise["id"], "steps": rows}, indent=2))
    else:
        for r in rows:
            print(f"{r['step']}\t{r['technique']}\t{r['outcome']}\t{'; '.join(r['reasons'])}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
