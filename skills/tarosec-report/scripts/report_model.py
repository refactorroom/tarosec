"""Build deterministic report data from reconciled Tarosec records."""
from __future__ import annotations

from collections import Counter
from pathlib import Path

from classify_exercise import classify_step
from report_inputs import Snapshot, canonical, digest, original_zone, safe_id, timestamp

MODES = ("summary", "technical", "executive", "incident", "coverage", "remediation", "compare")
SEVERITIES = ("Critical", "High", "Medium", "Low", "Informational")
COMPLETE = {"Detected", "Detected (late)"}
ELIGIBLE = COMPLETE | {"Partially detected", "Detection gap"}


def sorted_refs(values):
    return sorted({value for value in values if safe_id(value)})


def reported_time(value):
    return value if timestamp(value) else "unknown"


def finding_row(snapshot, ref, record):
    refs = record["evidenceRefs"]
    state = snapshot.evidence_state(refs)
    row = {key: record[key] for key in ("producer", "severity", "confidence", "status", "claimStrength")}
    row.update(id=ref, evidenceRefs=sorted_refs(refs), evidenceState=state,
               assessmentConfidence=record["confidence"] if state == "hash-matched" else "Unknown")
    if "verificationStatus" in record:
        row["verificationStatus"] = record["verificationStatus"]
    if state != "hash-matched":
        snapshot.gaps.append({"code": "finding-evidence-unverified", "kind": "finding", "id": ref})
    if record["producer"] == "tarosec-audit" and record.get("verificationStatus") == "inconclusive":
        row["assessmentConfidence"] = "Unknown"
    if (record["producer"] == "tarosec-audit"
            and (record["status"] == "Verified vulnerability" or record.get("verificationStatus") == "confirmed")
            and not record.get("guardChecked")):
        row["assessmentConfidence"] = "Unknown"
        snapshot.gaps.append({"code": "finding-guard-unrecorded", "kind": "finding", "id": ref})
    return row


def evidence_row(snapshot, ref, record):
    row = {
        "id": ref, "collectedAt": reported_time(record["collectedAt"]),
        "originalTimezone": original_zone(record["originalTimezone"]),
        "recordedIntegrity": record["integrity"], "artifactCheck": snapshot.evidence[ref],
        "sensitivity": record["sensitivity"],
    }
    if "sha256" in record:
        row["referenceSha256"] = record["sha256"]
    return row


def exercise_row(snapshot, ref, record):
    steps = []
    counts = Counter(step["id"] for step in record["steps"])
    for step in record["steps"]:
        step_id = step["id"]
        if not safe_id(step_id):
            snapshot.gaps.append({"code": "unsafe-step-id", "kind": "exercise", "id": ref})
            continue
        if counts[step_id] > 1:
            snapshot.gaps.append({"code": "duplicate-step-id", "kind": "exercise", "id": ref, "reference": step_id})
            continue
        outcome, _ = classify_step(step)
        results = step.get("results", {})
        execution = results.get("execution", {})
        observations = [execution, *results.get("telemetry", []), *results.get("alerts", [])]
        refs = [item for row in observations for item in row.get("evidenceRefs", [])]
        state = snapshot.evidence_state(refs, exercise=ref)
        # Some observation rows may lack provenance even when others cite files.
        if not all(row.get("evidenceRefs") for row in observations):
            state = "unresolved"
        started = timestamp(execution.get("startedAt"))
        ended = timestamp(execution.get("endedAt"))
        if execution.get("status") == "executed" and (not ended or ended.tzinfo is None or
                (execution.get("startedAt") and (not started or started.tzinfo is None))):
            snapshot.gaps.append({"code": "exercise-timing-unresolved", "kind": "exercise",
                                  "id": ref, "reference": step_id})
        if outcome != "Not run" and state != "hash-matched":
            snapshot.gaps.append({"code": "exercise-evidence-unverified", "kind": "exercise",
                                  "id": ref, "reference": step_id})
        row = {"id": step_id, "outcome": outcome, "evidenceRefs": sorted_refs(refs),
               "evidenceState": state, "execution": execution.get("status", "unknown")}
        if "reportedOutcome" in results:
            row["reportedOutcome"] = results["reportedOutcome"]
            if row["reportedOutcome"] != outcome:
                snapshot.gaps.append({"code": "outcome-disagreement", "kind": "exercise",
                                      "id": ref, "reference": step_id})
        if "technique" in step and safe_id(step["technique"]["id"]):
            row["technique"] = step["technique"]["id"]
        steps.append(row)
    return {"id": ref, "environment": record["environment"], "steps": steps}


def simulation_rows(snapshot):
    simulations = []
    exercises_by_path = {path: ref for (kind, ref), paths in snapshot.paths.items() if kind == "exercise" for path in paths}
    for (kind, ref), record in snapshot.records.items():
        if kind != "simulation-result":
            continue
        evidence = []
        scoped_evidence = {path: set() for path in snapshot.paths[kind, ref]}
        linked_exercises = []
        for item in record.get("evidence", []):
            checks = set()
            for path in snapshot.paths[kind, ref]:
                check = snapshot.artifact_status(path.parent, item["path"], item["sha256"])
                checks.add(check)
                if check == "match" and safe_id(item["id"]):
                    scoped_evidence[path].add(item["id"])
                relative = Path(item["path"])
                if item["id"] == "exercise" and (exercise_id := exercises_by_path.get(path.parent / relative)):
                    linked_exercises.append((exercise_id, path, check))
            if not safe_id(item["id"]):
                snapshot.gaps.append({"code": "unsafe-identifier", "kind": kind, "id": ref})
                continue
            evidence.append({"id": item["id"], "referenceSha256": item["sha256"], "artifactChecks": sorted(checks)})
            if checks != {"match"}:
                snapshot.gaps.append({"code": "evidence-integrity-unresolved", "kind": kind,
                                      "id": ref, "reference": item["id"]})
        row = {"id": ref, "outcome": record["outcome"], "execution": record["execution"],
               "evidence": sorted(evidence, key=canonical),
               "exerciseRefs": sorted_refs(exercise for exercise, _, _ in linked_exercises)}
        for exercise, path, check in linked_exercises:
            verified = scoped_evidence[path] if check == "match" else set()
            if exercise not in snapshot.simulation_refs:
                snapshot.simulation_refs[exercise] = set(verified)
            else:
                snapshot.simulation_refs[exercise].intersection_update(verified)
        if row["execution"] == "failed" or row["outcome"] in {"inconclusive", "not_executed"}:
            snapshot.gaps.append({"code": "simulation-outcome-unresolved", "kind": kind, "id": ref})
        for key in ("mode", "eventCount"):
            if key in record:
                row[key] = record[key]
        simulations.append(row)
    return simulations


def case_row(snapshot, ref, record):
    activities = []
    for index, item in enumerate(record.get("activities", []), 1):
        refs = item.get("evidenceRefs", [])
        time = timestamp(item["at"])
        if time is None or time.tzinfo is None:
            snapshot.gaps.append({"code": "timestamp-or-timezone-unknown", "kind": "case", "id": ref})
        if snapshot.evidence_state(refs) != "hash-matched":
            snapshot.gaps.append({"code": "case-activity-evidence-unverified", "kind": "case", "id": ref})
        activities.append({"sequence": index, "at": reported_time(item["at"]),
                           "evidenceRefs": sorted_refs(refs), "evidenceState": snapshot.evidence_state(refs)})
    known = [row for row in activities if (time := timestamp(row["at"])) and time.tzinfo]
    known.sort(key=lambda row: timestamp(row["at"]))
    ordered = {row["sequence"] for row in known}
    chronological = known + [row for row in activities if row["sequence"] not in ordered]
    return {"id": ref, "status": record["status"], "activities": chronological}


def summarize(snapshot, label, mode, baseline=None):
    findings, evidence, exercises, cases, scope = [], [], [], [], []
    runs = []
    simulations = simulation_rows(snapshot)
    snapshot.check_references(baseline=baseline)
    for (kind, ref), record in snapshot.records.items():
        if kind == "finding":
            findings.append(finding_row(snapshot, ref, record))
        elif kind == "exercise":
            row = exercise_row(snapshot, ref, record)
            row["simulationLinked"] = ref in snapshot.simulation_refs
            exercises.append(row)
        elif kind == "evidence":
            evidence.append(evidence_row(snapshot, ref, record))
        elif kind == "case":
            cases.append(case_row(snapshot, ref, record))
        elif kind == "run":
            runs.append({key: record[key] for key in ("id", "workflow", "stages")})
        elif kind == "engagement":
            scope.append({"id": ref, "environment": record["environment"],
                          "assetCount": len(record["scope"]["targets"]),
                          "windowStart": reported_time(record["window"]["start"]),
                          "windowEnd": reported_time(record["window"]["end"])})
    findings.sort(key=lambda row: (SEVERITIES.index(row["severity"]), row["id"]))
    if not scope:
        snapshot.gaps.append({"code": "scope-unsupplied"})
    metrics = summarize_metrics(findings, exercises)
    if mode == "coverage" and not metrics["eligibleStepCount"]:
        snapshot.gaps.append({"code": "coverage-denominator-unavailable"})
    summary = {"label": label, "sources": snapshot.sources, "gaps": unique_rows(snapshot.gaps),
               "findings": findings, "evidence": evidence, "cases": cases, "scope": scope,
               "exercises": exercises, "simulations": simulations, "metrics": metrics}
    if runs:
        summary["runs"] = runs
    return summary


def summarize_metrics(findings, exercises):
    assessed = [row for row in findings if row["status"] != "False positive"]
    coverage = [step for exercise in exercises if not exercise["simulationLinked"] for step in exercise["steps"]
                if step["evidenceState"] == "hash-matched" and step["outcome"] in ELIGIBLE]
    return {"findingCount": len(findings), "assessedFindingCount": len(assessed),
            "falsePositiveCount": len(findings) - len(assessed),
            "severityCounts": {severity: sum(row["severity"] == severity for row in assessed)
                               for severity in SEVERITIES},
            "fullDetectionCount": sum(row["outcome"] in COMPLETE for row in coverage),
            "eligibleStepCount": len(coverage)}


def unique_rows(rows):
    return [row for _, row in sorted({canonical(row): row for row in rows}.items())]


def compare_snapshots(left, right, summaries, baseline_id, retest_id):
    # Explicit case IDs select finding membership. Exercise IDs additionally need
    # the canonical retestOf linkage before the report can verify a change.
    pairs = [(kind, left.records.get((kind, baseline_id)), right.records.get((kind, retest_id)))
             for kind in ("exercise", "case")]
    matches = [(kind, baseline, retest) for kind, baseline, retest in pairs if baseline and retest]
    result = {"baselineId": baseline_id, "retestId": retest_id, "kind": "unknown", "rows": []}
    if len(matches) != 1 or baseline_id == retest_id:
        result["gap"] = "comparison-identities-unresolved"
        return result
    kind, baseline, retest = matches[0]
    result["kind"] = kind
    if kind == "exercise":
        result["rows"] = compare_steps(baseline, retest, summaries, baseline_id, retest_id)
    else:
        result["rows"] = compare_findings(baseline, retest, summaries)
    if not result["rows"] or any(row["assessment"] == "inconclusive" for row in result["rows"]):
        result["gap"] = "comparison-incomplete"
    return result


def compare_steps(baseline, retest, summaries, baseline_id, retest_id):
    views = [next(row for row in summary["exercises"] if row["id"] == ref)
             for summary, ref in zip(summaries, (baseline_id, retest_id))]
    indexed = [{row["id"]: row for row in view["steps"]} for view in views]
    expected = [{step["id"]: (step["targetHost"], step["expected"], step.get("technique", {}).get("id"))
                 for step in record["steps"]} for record in (baseline, retest)]
    linked = retest.get("retestOf") == baseline_id
    comparable = baseline["environment"] == retest["environment"] and baseline["attackVersion"] == retest["attackVersion"]
    rows = []
    for ref in sorted(set(expected[0]) | set(expected[1])):
        if not safe_id(ref):
            continue
        before, after = (index.get(ref, {}) for index in indexed)
        first, second = before.get("outcome", "missing"), after.get("outcome", "missing")
        assessment = "inconclusive"
        if (linked and comparable and expected[0].get(ref) == expected[1].get(ref)
                and before.get("evidenceState") == after.get("evidenceState") == "hash-matched"
                and not any(view["simulationLinked"] for view in views)):
            if first == second and first in ELIGIBLE:
                assessment = "unchanged"
            elif first == "Detection gap" and second in COMPLETE:
                assessment = "verified-improvement"
            elif first in COMPLETE and second == "Detection gap":
                assessment = "verified-regression"
            elif first in ELIGIBLE and second in ELIGIBLE:
                assessment = "observed-change"
        rows.append({"id": ref, "before": first, "after": second, "assessment": assessment})
    return rows


def compare_findings(baseline, retest, summaries):
    refs = [set(record.get("findingRefs", [])) for record in (baseline, retest)]
    indexed = [{row["id"]: row for row in summary["findings"] if row["id"] in subset}
               for summary, subset in zip(summaries, refs)]
    digests = [{row["id"]: row["referenceSha256"] for row in summary["evidence"]
                if row["artifactCheck"] == "match"} for summary in summaries]
    rows = []
    for ref in sorted_refs(refs[0] | refs[1]):
        before, after = (index.get(ref, {}) for index in indexed)
        first, second = (row.get("verificationStatus", "unverified") if row else "missing"
                         for row in (before, after))
        assessment = "inconclusive"
        if (before.get("evidenceState") == after.get("evidenceState") == "hash-matched"
                and before["producer"] == after["producer"]
                and "inconclusive" not in (first, second)):
            same_claim = all(before[key] == after[key] for key in ("claimStrength", "status", "severity"))
            if first == second and same_claim:
                assessment = "unchanged"
            elif {first, second} == {"confirmed", "fixed"}:
                prior_digests = {digests[0][item] for item in before["evidenceRefs"]}
                new_refs = set(after["evidenceRefs"]) - set(before["evidenceRefs"])
                if any(digests[1][item] not in prior_digests for item in new_refs):
                    assessment = "recorded-fix" if second == "fixed" else "recorded-regression"
            else:
                assessment = "observed-change"
        rows.append({"id": ref, "before": first, "after": second, "assessment": assessment})
    return rows


def build_report(path, mode, retest=None, baseline_id=None, retest_id=None, generated_at=None):
    left = Snapshot(path)
    comparison = None
    if mode == "compare":
        if not safe_id(baseline_id) or not safe_id(retest_id):
            raise ValueError("compare requires safe explicit --baseline-id and --retest-id values")
        right = Snapshot(retest) if retest else left
        baseline = summarize(left, "baseline", mode)
        retest_view = ({**baseline, "label": "retest"} if right is left else summarize(right, "retest", mode, baseline=left))
        snapshots = [baseline, retest_view]
        comparison = compare_snapshots(left, right, snapshots, baseline_id, retest_id)
    else:
        snapshots = [summarize(left, "supplied", mode)]
    report = {"schemaVersion": "tarosec.report/v1", "type": mode, "snapshots": snapshots}
    if comparison is not None:
        report["comparison"] = comparison
    if generated_at is not None:
        instant = timestamp(generated_at)
        if not instant or instant.tzinfo is None:
            raise ValueError("--generated-at requires an ISO 8601 timestamp with an offset")
        report["generatedAt"] = generated_at
    return {**report, "id": "REPORT-" + digest(report)}
