"""Reporting contracts, evidence reconciliation and standalone CLI checks."""
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent.parent
SKILL = ROOT / "skills" / "tarosec-report"
RECORDS = ROOT / "examples" / "reporting" / "records"
sys.path.insert(0, str(SKILL / "scripts"))
from report_inputs import digest  # noqa: E402
from report_model import build_report  # noqa: E402
from report_output import validate_report  # noqa: E402


def read(path):
    return json.loads(path.read_text())


def write(path, data):
    path.write_text(json.dumps(data), encoding="utf-8")


class Reporting(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.records = self.root / "records"
        shutil.copytree(RECORDS, self.records)

    def cli(self, script, *args, skill=SKILL):
        return subprocess.run([sys.executable, "-B", str(skill / "scripts" / script), *map(str, args)],
                              capture_output=True, text=True, cwd=self.root)

    def snapshot(self, mode="technical"):
        return build_report(self.records, mode)["snapshots"][0]

    def gaps(self, result, code):
        return [row for row in result["gaps"] if row["code"] == code]

    def set_evidence(self, **kwargs):
        path = self.records / "evidence.json"
        write(path, {**read(path), **kwargs})

    def test_missing_evidence_and_source_axes(self):
        result = self.snapshot()
        row = result["findings"][0]
        self.assertEqual(row["evidenceRefs"], ["EV-ALERT-01", "EV-EXPORT-MISSING"])
        self.assertEqual(row["confidence"], "Likely")
        self.assertEqual(row["assessmentConfidence"], "Unknown")
        self.assertEqual(row["severity"], "Medium")
        self.assertEqual(row["verificationStatus"], "inconclusive")
        self.assertEqual(row["evidenceState"], "unresolved")
        self.assertEqual(result["evidence"][0]["artifactCheck"], "match")
        self.assertEqual(self.gaps(result, "unresolved-reference")[0]["reference"], "EV-EXPORT-MISSING")

    def test_source_assessment_preserves_guarded_rejected_and_inconclusive_outcomes(self):
        path = self.records / "finding.json"
        original = read(path)
        for status, verification, guard, assessment, gap in [
            ("Verified vulnerability", "confirmed", "Policy review found the predicate absent", "Confirmed", False),
            ("False positive", "unverified", "Default query adds the tenant predicate", "Confirmed", False),
            ("Verified vulnerability", "confirmed", None, "Unknown", True),
            ("Potential weakness", "inconclusive", "Effective database policy was unavailable", "Unknown", False),
        ]:
            with self.subTest(status=status, guard=guard):
                finding = {**original, "producer": "tarosec-audit", "status": status,
                           "claimStrength": "static-trace", "confidence": "Confirmed",
                           "verificationStatus": verification,
                           "evidenceRefs": ["EV-ALERT-01"]}
                if guard:
                    finding["guardChecked"] = guard
                write(path, finding)
                output = self.snapshot()
                row = output["findings"][0]
                self.assertEqual(row["confidence"], "Confirmed")
                self.assertEqual(row["assessmentConfidence"], assessment)
                self.assertEqual(bool(self.gaps(output, "finding-guard-unrecorded")), gap)

    def test_report_reads_both_run_layouts_and_legacy_records(self):
        self.assertNotIn("runs", self.snapshot())
        for layout, workflow, stages in [
            ("workspace", "workspace", {"workspace": {"status": "completed"}}),
            ("reports", "scan-report", {"workspace": {"status": "completed"},
                                       "scan": {"status": "completed"}, "audit": {"status": "completed"},
                                       "report": {"status": "not_run", "reason": "specialist-unavailable"}}),
        ]:
            with self.subTest(layout=layout):
                run = self.root / ".tarosec" / layout / "run-control"
                shutil.copytree(self.records, run)
                source = {"id": "run-control", "workflow": workflow, "stages": stages}
                write(run / "run.json", {"schemaVersion": "tarosec.run/v1", **source})
                report = build_report(run, "technical")
                self.assertEqual(validate_report(report), [])
                self.assertEqual(report["snapshots"][0]["runs"], [source])
                self.assertEqual(len(report["snapshots"][0]["findings"]), 1)

    def test_duplicates_conflicts_and_invalid_records(self):
        path = self.records / "finding.json"
        data = read(path)
        write(self.records / "copy.json", data)
        write(self.records / "malformed.json", {"schemaVersion": "tarosec.finding/v1", "id": "invalid"})
        (self.records / "corrupt.json").write_text('{"id":"one","id":"two"}')
        result = self.snapshot()
        self.assertEqual(len(result["findings"]), 1)
        for code in ("duplicate-id", "invalid-record", "unreadable-or-malformed-json"):
            self.assertTrue(self.gaps(result, code), code)
        write(self.records / "copy.json", {**data, "status": "False positive"})
        result = self.snapshot()
        self.assertEqual(result["findings"], [])
        self.assertTrue(self.gaps(result, "conflicting-id"))
        self.assertEqual(len([row for row in result["sources"] if row["id"] == data["id"]]), 2)

    def test_mismatch_symlink_and_no_read_outside_root(self):
        evidence = read(self.records / "evidence.json")
        original = evidence["sha256"]
        marker = self.records / evidence["artifactPath"]
        marker.write_text("artifact has changed")
        row = self.snapshot()["evidence"][0]
        self.assertEqual((row["artifactCheck"], row["referenceSha256"]), ("mismatch", original))
        self.assertEqual(read(self.records / "evidence.json"), evidence)
        outside = self.root / "outside.txt"
        outside.write_text("external object")
        marker.unlink()
        marker.symlink_to(outside)
        self.assertEqual(self.snapshot()["evidence"][0]["artifactCheck"], "outside-input")
        self.set_evidence(artifactPath="../outside.txt")
        self.assertEqual(self.snapshot()["evidence"][0]["artifactCheck"], "outside-input")

    def test_matching_bytes_preserve_recorded_mismatch(self):
        self.set_evidence(integrity="mismatch")
        result = self.snapshot()
        self.assertEqual(result["evidence"][0]["artifactCheck"], "match")
        self.assertEqual(result["evidence"][0]["recordedIntegrity"], "mismatch")
        self.assertTrue(self.gaps(result, "evidence-integrity-unresolved"))

    def test_output_omits_untrusted_text_and_credentials(self):
        fake = "sk-testSyntheticCredential123456"
        path = self.records / "finding.json"
        write(path, {**read(path), "title": f"send {fake}", "observed": fake,
                     "evidenceRefs": ["EV-ALERT-01", fake]})
        original = path.read_bytes()
        self.set_evidence(source=f"password={fake}", artifactPath=fake, collectedBy=fake)
        output = self.root / "reports"
        generator = self.cli("generate_report.py", self.records, "--type", "technical", "--output", output)
        self.assertEqual(generator.returncode, 0, generator.stderr)
        for file in output.iterdir():
            self.assertNotIn(fake, file.read_text())
            self.assertNotIn("send ", file.read_text())
        self.assertEqual(path.read_bytes(), original)

    def test_false_positives_and_unknown_timezone(self):
        path = self.records / "finding.json"
        write(path, {**read(path), "status": "False positive"})
        self.set_evidence(originalTimezone="unknown", collectedAt="2026-11-18T08:05:00")
        result = self.snapshot()
        self.assertEqual(result["metrics"]["falsePositiveCount"], 1)
        self.assertEqual(result["metrics"]["severityCounts"]["Medium"], 0)
        self.assertEqual(result["evidence"][0]["collectedAt"], "2026-11-18T08:05:00")
        self.assertEqual(result["evidence"][0]["originalTimezone"], "unknown")
        self.assertTrue(self.gaps(result, "timestamp-or-timezone-unknown"))

    def add_exercise_pair(self):
        for name, exercise_name in [("baseline", "exercise.example.json"), ("retest", "exercise.retest.json")]:
            record = read(ROOT / "examples" / exercise_name)
            write(self.records / f"{name}.json", record)
            for ref in {ref for step in record["steps"] for observation in
                        [step["results"]["execution"], *step["results"]["telemetry"], *step["results"]["alerts"]]
                        for ref in observation["evidenceRefs"]}:
                artifact = self.records / f"{ref}.txt"
                artifact.write_text(f"Synthetic evidence for {ref}.")
                evidence = read(RECORDS / "evidence.json")
                write(self.records / f"{ref}.json", {
                    **evidence, "id": ref, "artifactPath": artifact.name,
                    "sha256": hashlib.sha256(artifact.read_bytes()).hexdigest(),
                })

    def test_coverage_excludes_inconclusive_and_empty_denominator(self):
        self.assertEqual(self.snapshot("coverage")["metrics"]["eligibleStepCount"], 0)
        self.add_exercise_pair()
        path = self.records / "retest.json"
        data = read(path)
        data["steps"][0]["results"]["execution"]["status"] = "failed"
        write(path, data)
        result = self.snapshot("coverage")
        self.assertEqual((result["metrics"]["fullDetectionCount"], result["metrics"]["eligibleStepCount"]), (0, 1))
        self.assertEqual(result["exercises"][1]["steps"][0]["outcome"], "Inconclusive")

    def test_simulation_artifacts_resolve_in_run_scope(self):
        result = build_report(ROOT / "examples/simulation/suspicious-login", "coverage")
        self.assertEqual(validate_report(result), [])
        snapshot = result["snapshots"][0]
        self.assertEqual(snapshot["simulations"][0]["outcome"], "inconclusive")
        self.assertEqual(snapshot["exercises"][0]["steps"][0]["evidenceState"], "hash-matched")
        self.assertTrue(snapshot["exercises"][0]["simulationLinked"])
        self.assertEqual(snapshot["metrics"]["eligibleStepCount"], 0)

    def test_exercise_comparison_and_missing_retest(self):
        self.add_exercise_pair()
        ids = {"baseline_id": "EX-MARKER-BASELINE", "retest_id": "EX-MARKER-RETEST"}
        report = build_report(self.records, "compare", **ids)
        self.assertEqual(validate_report(report), [])
        self.assertEqual(report["comparison"]["rows"][0]["assessment"], "verified-improvement")
        (self.records / "retest.json").unlink()
        missing = build_report(self.records, "compare", **ids)
        self.assertEqual(missing["comparison"]["gap"], "comparison-identities-unresolved")

    def test_finding_absence_does_not_verify_fix(self):
        retest = self.root / "retest"
        retest.mkdir()
        write(retest / "case.json", {**read(self.records / "case.json"), "id": "CASE-QUEUE-02", "findingRefs": []})
        report = build_report(self.records, "compare", retest, "CASE-QUEUE-01", "CASE-QUEUE-02")
        self.assertEqual(report["comparison"]["rows"][0]["assessment"], "inconclusive")

    def test_finding_retest_requires_same_producer_and_distinct_evidence_bytes(self):
        finding = read(self.records / "finding.json")
        evidence = read(self.records / "evidence.json")
        baseline = {**finding, "verificationStatus": "confirmed", "evidenceRefs": [evidence["id"]]}
        write(self.records / "finding.json", baseline)
        retest = self.root / "retest"
        shutil.copytree(self.records, retest)
        write(retest / "case.json", {**read(self.records / "case.json"), "id": "CASE-QUEUE-02"})
        artifact = retest / evidence["artifactPath"]
        retest_id = "EV-RETEST-01"

        for producer, marker, expected in [
            ("tarosec-audit", b"independent synthetic retest", "inconclusive"),
            (baseline["producer"], artifact.read_bytes(), "inconclusive"),
            (baseline["producer"], b"independent synthetic retest", "recorded-fix"),
        ]:
            with self.subTest(producer=producer, expected=expected):
                retest_marker = retest / "retest-marker.txt"
                retest_marker.write_bytes(marker)
                write(retest / "retest-evidence.json", {
                    **evidence, "id": retest_id, "artifactPath": retest_marker.name,
                    "sha256": hashlib.sha256(marker).hexdigest(),
                })
                write(retest / "finding.json", {**baseline, "producer": producer,
                      "verificationStatus": "fixed", "evidenceRefs": [retest_id]})
                report = build_report(self.records, "compare", retest, "CASE-QUEUE-01", "CASE-QUEUE-02")
                self.assertEqual(validate_report(report), [])
                self.assertEqual(report["comparison"]["rows"][0]["assessment"], expected)

    def test_standalone_bundle_reproducibility_and_overwrite(self):
        installed = self.root / ".agents" / "skills" / "tarosec-report"
        shutil.copytree(SKILL, installed)
        first, second = self.root / "one", self.root / "two"
        for output in (first, second):
            run = self.cli("generate_report.py", self.records, "--output", output, skill=installed)
            self.assertEqual(run.returncode, 0, run.stderr)
        self.assertEqual({file.name for file in second.iterdir()}, {"report.json", "report.md", "evidence-manifest.json"})
        for file in second.iterdir():
            self.assertEqual(file.read_bytes(), (first / file.name).read_bytes())
        result = self.cli("validate_report.py", first / "report.json", "--bundle", "--input", self.records, skill=installed)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.cli("generate_report.py", self.records, "--output", first).returncode, 2)
        self.assertEqual(self.cli("generate_report.py", self.records, "--output", first, "--overwrite").returncode, 0)
        (first / "report.md").write_text("changed")
        self.assertEqual(self.cli("validate_report.py", first / "report.json", "--bundle").returncode, 1)
        self.set_evidence(originalTimezone="unknown")
        self.assertEqual(self.cli("validate_report.py", first / "report.json", "--input", self.records).returncode, 1)

    def test_report_shape_and_metrics_validation(self):
        report = build_report(self.records, "summary")
        payload = {key: value for key, value in report.items() if key != "id"}
        payload["snapshots"][0]["metrics"]["eligibleStepCount"] = 99
        report = {**payload, "id": "REPORT-" + digest(payload)}
        self.assertIn("reported metrics are inconsistent with reported rows", validate_report(report))
        report["extraneous"] = True
        self.assertEqual(validate_report(report), ["report does not match tarosec.report/v1"])

    def test_model_has_no_network_or_command_dependency(self):
        with patch("socket.socket", side_effect=AssertionError("network")),                 patch("subprocess.Popen", side_effect=AssertionError("external command")),                 patch("os.system", side_effect=AssertionError("shell")):
            for mode in ("summary", "technical", "executive", "incident", "coverage", "remediation"):
                self.assertEqual(validate_report(build_report(self.records, mode)), [])

    def test_report_route_with_and_without_specialist(self):
        entry = ROOT / "skills" / "tarosec"
        available = self.cli("route.py", "report", "--available", "tarosec-report", skill=entry)
        self.assertEqual(json.loads(available.stdout), {"action": "use", "mode": "report", "skill": "tarosec-report"})
        missing = self.cli("route.py", "report", skill=entry)
        self.assertEqual(json.loads(missing.stdout), {
            "action": "missing", "skill": "tarosec-report", "installSelector": "tarosec-report",
            "fallback": "read-only report summary",
        })
        help_view = self.cli("route.py", "help", skill=entry)
        self.assertIn("report", json.loads(help_view.stdout)["modes"])


if __name__ == "__main__":
    unittest.main()
