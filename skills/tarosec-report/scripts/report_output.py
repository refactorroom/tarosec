"""Render and check structured report bundles."""
from __future__ import annotations

import json

from report_inputs import digest, load_schema, original_zone, safe_id, timestamp
from report_model import summarize_metrics
from validate_record import validate

GAP_READINGS = {
    "unresolved-reference": "Referenced record is missing or conflicting",
    "finding-evidence-unverified": "Finding lacks fully checked supporting evidence",
    "evidence-integrity-unresolved": "Artifact integrity needs review",
    "coverage-denominator-unavailable": "No steps qualify for the detection denominator",
    "scope-unsupplied": "No usable engagement scope was supplied",
    "no-usable-records": "No usable source records were supplied",
}
MODES_WITH_FINDINGS = {"technical", "remediation"}


def markdown(report):
    mode = report["type"]
    lines = [f"# Tarosec {mode} report", "", f"Report ID `{report['id']}`", "",
             "This report covers the supplied records. Digest matches establish byte consistency."]
    if report.get("generatedAt"):
        lines.append(f"Generated {report['generatedAt']}")
    for snapshot in report["snapshots"]:
        metrics = snapshot["metrics"]
        lines += ["", f"## {snapshot['label'].capitalize()} records", "",
                  f"- Findings reported: {metrics['findingCount']}",
                  f"- Findings counted in severity totals: {metrics['assessedFindingCount']}",
                  f"- False positives: {metrics['falsePositiveCount']}"]
        counts = [f"{key} {value}" for key, value in metrics["severityCounts"].items() if value]
        if counts:
            lines.append("- Severity totals: " + ", ".join(counts))
        for scope in snapshot["scope"]:
            lines.append(f"- Engagement `{scope['id']}` lists {scope['assetCount']} "
                         f"targets in {scope['environment']} ({scope['windowStart']} to {scope['windowEnd']}).")
        if mode in MODES_WITH_FINDINGS and snapshot["findings"]:
            lines += ["", "### Findings", ""]
            for row in snapshot["findings"]:
                refs = ", ".join(f"`{ref}`" for ref in row["evidenceRefs"]) or "none cited"
                lines += [f"- `{row['id']}` — {row['severity']}, {row['status']} ({row['producer']}).",
                          f"  Source confidence {row['confidence']}. Assessment confidence "
                          f"{row['assessmentConfidence']}. Claim strength {row['claimStrength']}.",
                          f"  Evidence {refs} ({row['evidenceState']})."]
                if "verificationStatus" in row:
                    lines.append(f"  Recorded verification {row['verificationStatus']}.")
        if mode == "executive":
            attention = [row for row in snapshot["findings"] if row["status"] != "False positive"]
            for row in attention[:5]:
                lines.append(f"- `{row['id']}` — {row['severity']}, {row['status']}. "
                             f"Assessment confidence {row['assessmentConfidence']}.")
        if mode == "incident" and any(row["activities"] for row in snapshot["cases"]):
            lines += ["", "### Recorded case activity", ""]
            for row in snapshot["cases"]:
                for item in row["activities"]:
                    refs = ", ".join(f"`{ref}`" for ref in item["evidenceRefs"]) or "none cited"
                    lines.append(f"- {item['at']} — `{row['id']}` activity {item['sequence']}, evidence {refs}.")
        if mode == "coverage":
            lines += ["", "### Detection coverage", "",
                      "Eligible steps have hash-matched evidence and a detection, partial detection, or "
                      "detection gap outcome. Full detections include late detections. "
                      "Simulation-linked steps are excluded."]
            denominator = metrics["eligibleStepCount"]
            if denominator:
                numerator = metrics["fullDetectionCount"]
                lines.append(f"Full detections among eligible steps: {numerator}/{denominator}.")
            else:
                lines.append("Detection rate unavailable.")
        if mode in {"technical", "coverage"}:
            if snapshot["exercises"] and mode == "technical":
                lines += ["", "### Recorded exercise steps", ""]
            for exercise in snapshot["exercises"]:
                for step in exercise["steps"]:
                    lines.append(f"- `{exercise['id']}/{step['id']}` — {step['outcome']} "
                                 f"({step['evidenceState']}).")
        if snapshot["simulations"]:
            lines += ["", "### Simulation results", ""]
        for simulation in snapshot["simulations"]:
            lines.append(f"- Simulation `{simulation['id']}` — {simulation['execution']}, "
                         f"{simulation['outcome'].replace('_', ' ')}.")
        if snapshot["gaps"]:
            lines += ["", "### Verification gaps and limits", "",
                      "The supplied records leave open verification questions."]
            for gap in snapshot["gaps"]:
                message = GAP_READINGS.get(gap["code"], gap["code"].replace("-", " ").capitalize())
                context = [f"`{gap[key]}`" for key in ("id", "reference") if key in gap]
                if "inputIndex" in gap:
                    context.append(f"input {gap['inputIndex']}")
                suffix = " (" + ", ".join(context) + ")" if context else ""
                lines.append(f"- {message}{suffix}.")
    if comparison := report.get("comparison"):
        lines += ["", "## Baseline and retest", "",
                  f"Baseline `{comparison['baselineId']}` and retest `{comparison['retestId']}`."]
        if "gap" in comparison:
            lines.append(comparison["gap"].replace("-", " ").capitalize() + ".")
        for row in comparison["rows"]:
            lines.append(f"- `{row['id']}` — {row['before']} → {row['after']} "
                         f"({row['assessment'].replace('-', ' ')}).")
    lines += ["", "See `evidence-manifest.json` for source record digests and evidence checks."]
    return "\n".join(lines) + "\n"


def json_text(record):
    return json.dumps(record, ensure_ascii=True, allow_nan=False, sort_keys=True, indent=2) + "\n"


def bundle(report):
    manifest = {
        "reportId": report["id"],
        "snapshots": [{key: snapshot[key] for key in ("label", "sources", "evidence", "simulations")}
                      for snapshot in report["snapshots"]],
    }
    return {"report.md": markdown(report), "evidence-manifest.json": json_text(manifest),
            "report.json": json_text(report)}


def identifiers_are_safe(value):
    identity_keys = {"id", "reference", "baselineId", "retestId", "technique"}
    if isinstance(value, list):
        return all(identifiers_are_safe(item) for item in value)
    if isinstance(value, dict):
        for key, item in value.items():
            if key in identity_keys and not safe_id(item):
                return False
            if key in {"evidenceRefs", "exerciseRefs"} and not all(map(safe_id, item)):
                return False
            if key == "originalTimezone" and original_zone(item) != item:
                return False
            if not identifiers_are_safe(item):
                return False
    return True


def validate_report(report):
    if validate(report, load_schema("report")):
        return ["report does not match tarosec.report/v1"]
    errors = []
    payload = {key: value for key, value in report.items() if key != "id"}
    if report["id"] != "REPORT-" + digest(payload):
        errors.append("report digest does not match")
    compare = report["type"] == "compare"
    expected_labels = ["baseline", "retest"] if compare else ["supplied"]
    if [row["label"] for row in report["snapshots"]] != expected_labels or compare != ("comparison" in report):
        errors.append("snapshot labels or comparison are inconsistent with the report mode")
    if "generatedAt" in report:
        instant = timestamp(report["generatedAt"])
        if instant is None or instant.tzinfo is None:
            errors.append("invalid generation timestamp")
    if not identifiers_are_safe(report):
        errors.append("unsafe report identifier or timezone")
    for snapshot in report["snapshots"]:
        if snapshot["metrics"] != summarize_metrics(snapshot["findings"], snapshot["exercises"]):
            errors.append("reported metrics are inconsistent with reported rows")
        source_ids = {(row["kind"], row["id"]) for row in snapshot["sources"]}
        for kind, key in (("finding", "findings"), ("case", "cases"), ("evidence", "evidence"),
                          ("exercise", "exercises"), ("engagement", "scope"), ("simulation-result", "simulations")):
            ids = [row["id"] for row in snapshot[key]]
            if len(set(ids)) != len(ids) or any((kind, ref) not in source_ids for ref in ids):
                errors.append(f"inconsistent {kind} provenance")
        evidence_ids = {row["id"] for row in snapshot["evidence"]}
        references = [*snapshot["findings"],
                      *(step for exercise in snapshot["exercises"] if not exercise["simulationLinked"]
                        for step in exercise["steps"]),
                      *(item for case in snapshot["cases"] for item in case["activities"])]
        if any(row["evidenceState"] != "unresolved" and
               (not row["evidenceRefs"] or set(row["evidenceRefs"]) - evidence_ids) for row in references):
            errors.append("resolved evidence reference is missing")
        for exercise in snapshot["exercises"]:
            related = [row for row in snapshot["simulations"] if exercise["id"] in row["exerciseRefs"]]
            if exercise["simulationLinked"] != bool(related):
                errors.append("simulation linkage is inconsistent")
            if related:
                allowed = {item["id"] for row in related for item in row["evidence"] if "match" in item["artifactChecks"]}
                if any(step["evidenceState"] != "unresolved" and
                       (not step["evidenceRefs"] or set(step["evidenceRefs"]) - allowed)
                       for step in exercise["steps"]):
                    errors.append("resolved simulation evidence reference is missing")
    return errors
