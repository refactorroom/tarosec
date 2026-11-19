import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SIM = ROOT / "skills/tarosec-simulate"
ROUTER = ROOT / "skills/tarosec/scripts/route.py"
RUNNER = SIM / "scripts/simulate.py"
PURPLE = ROOT / "skills/tarosec-purple/scripts/classify_exercise.py"


def call(script, *args):
    return subprocess.run([sys.executable, "-B", str(script), *map(str, args)],
                          capture_output=True, text=True, timeout=10)


class RouterTests(unittest.TestCase):
    def test_explicit_modes_and_safe_defaults(self):
        cases = [
            (["--evidence", "project"], "audit"), ([], "audit"), (["scan"], "audit"),
            (["red"], "red"), (["--evidence", "logs"], "blue"), (["incident"], "blue"),
            (["purple"], "purple"), (["simulate"], "simulate"), (["intel"], "audit"),
            (["verify", "--evidence", "exercise"], "purple"),
        ]
        for args, name in cases:
            with self.subTest(args=args):
                skill = f"tarosec-{name}"
                completed = call(ROUTER, *args, "--available", skill, "--available", "tarosec")
                self.assertEqual(completed.returncode, 0, completed.stderr)
                self.assertEqual(json.loads(completed.stdout)["skill"], skill)

    def test_missing_unknown_and_help(self):
        self.assertEqual(json.loads(call(ROUTER, "simulate").stdout)["action"], "missing")
        self.assertEqual(json.loads(call(ROUTER, "help").stdout)["action"], "help")
        result = call(ROUTER, "tarosec", "--available", "tarosec")
        self.assertEqual(result.returncode, 1)
        self.assertEqual(json.loads(result.stdout)["action"], "unsupported")


class SimulationTests(unittest.TestCase):
    def setUp(self):
        work = tempfile.TemporaryDirectory()
        self.addCleanup(work.cleanup)
        self.root = Path(work.name)
        self.source = self.root / "source"
        self.output = self.root / "result"
        shutil.copytree(SIM / "assets/scenarios/auth.suspicious-login", self.source)

    def success(self, *args, output=None):
        output = output or self.output
        completed = call(RUNNER, *args, "--output", output)
        self.assertEqual(completed.returncode, 0, completed.stderr)
        return json.loads((output / "result.json").read_text())

    def failure(self, *args, output=None):
        output = output or self.output
        run = call(RUNNER, *args, "--output", output)
        self.assertEqual(run.returncode, 1, run.stderr)
        self.assertEqual(json.loads(run.stderr)["outcome"], "not_executed")
        return run.stderr

    def test_catalog_runs_are_deterministic_and_inconclusive(self):
        catalog = call(RUNNER, "list").stdout.splitlines()
        self.assertEqual(set(catalog), {
            "auth.benign-login-retry", "auth.suspicious-login",
            "endpoint.ransomware-behavior", "web.attack-patterns",
        })
        for scenario in catalog:
            with self.subTest(scenario=scenario):
                first, second = self.root / f"{scenario}-first", self.root / f"{scenario}-second"
                result = self.success("synthetic", scenario, output=first)
                self.success("synthetic", scenario, output=second)
                self.assertEqual(result["outcome"], "inconclusive")
                for item in result["evidence"]:
                    artifact = first / item["path"]
                    self.assertEqual(hashlib.sha256(artifact.read_bytes()).hexdigest(), item["sha256"])
                    self.assertEqual(artifact.read_bytes(), (second / item["path"]).read_bytes())
                self.assertEqual((first / "result.json").read_bytes(), (second / "result.json").read_bytes())
                self.assertTrue(all(event["synthetic"] for event in json.loads((first / "events.json").read_text())))
                self.assertIn("2026-01-01T00:00:00+00:00", result["startedAt"])

    def test_benign_login_control_preserves_retry_without_suspicious_markers(self):
        result = self.success("synthetic", "benign-login-retry")
        events = json.loads((self.output / "events.json").read_text())
        self.assertEqual([event["type"] for event in events],
                         ["auth.failure", "auth.failure", "auth.success"])
        self.assertEqual(result["outcome"], "inconclusive")

    def test_replay_normalizes_json_and_ndjson(self):
        first = self.success("replay", self.source)
        events = json.loads((self.source / "events.json").read_text())
        (self.source / "events.ndjson").write_text("\n".join(map(json.dumps, reversed(events))))
        second = self.success("replay", self.source, "--ndjson", output=self.root / "second")
        self.assertEqual(first, second)
        self.failure("replay", self.source)
        self.assertEqual(first, json.loads((self.output / "result.json").read_text()))

    def test_every_catalog_fixture_rejects_malformed_event_types(self):
        for fixture in sorted((SIM / "assets/scenarios").iterdir()):
            with self.subTest(scenario=fixture.name):
                source = self.root / fixture.name
                shutil.copytree(fixture, source)
                path = source / "events.json"
                events = json.loads(path.read_text())
                events[-1]["type"] = "unsupported-event"
                path.write_text(json.dumps(events))
                self.assertIn("outside allowed choices", self.failure("replay", source))
                self.assertFalse(self.output.exists())

    def test_rule_assessment_agrees_with_purple(self):
        for fired, complete, missing, expected, purple in (
            (True, True, False, "detected", "Detected"),
            (True, True, True, "partially_detected", "Partially detected"),
            (False, True, False, "not_detected", "Detection gap"),
            (False, False, False, "inconclusive", "Inconclusive"),
            (False, True, True, "inconclusive", "Inconclusive"),
        ):
            with self.subTest(outcome=expected, missing=missing):
                scratch = Path(tempfile.mkdtemp(dir=self.root))
                source = scratch / "source"
                shutil.copytree(self.source, source)
                path = source / "events.json"
                events = json.loads(path.read_text())
                path.write_text(json.dumps(events[:-1] if missing else events))
                prepared = self.success("replay", source, output=scratch / "prepared")
                digest = next(record["sha256"] for record in prepared["evidence"] if record["id"] == "events")
                alert = {"rule": "login-sequence", "status": "fired" if fired else "not_fired"}
                if fired:
                    alert["offsetSeconds"] = 25
                (source / "alerts.json").write_text(json.dumps({
                    "schemaVersion": "tarosec.simulation-alerts/v1", "eventsSha256": digest,
                    "windowComplete": complete, "alerts": [alert],
                }))
                output = scratch / "reported"
                result = self.success("replay", source, "--alerts", output=output)
                self.assertEqual(result["outcome"], expected)
                classified = call(PURPLE, output / "exercise.json", "--json")
                self.assertEqual(classified.returncode, 0, classified.stderr)
                self.assertEqual(json.loads(classified.stdout)["steps"][0]["outcome"], purple)

    def test_malformed_input_is_rejected_without_echoing_content(self):
        path = self.source / "events.json"
        path.write_text(json.dumps([{"type": "auth.failure", "offsetSeconds": 0,
                                     "command": "DONT_PRINT_THIS_SECRET"}]))
        error = self.failure("replay", self.source)
        self.assertIn("unexpected property", error)
        self.assertNotIn("DONT_PRINT_THIS_SECRET", error)
        self.assertFalse(self.output.exists())
        path.write_bytes(b" " * (256 * 1024 + 1))
        self.assertIn("byte limit", self.failure("replay", self.source))

    def test_unsafe_paths_and_actions_are_rejected(self):
        self.failure("synthetic", "../source")
        self.failure("replay", "https://example.test/scenario")
        self.failure("replay", self.source, output=self.source / "child")
        self.assertEqual(call(RUNNER, "lab", self.source).returncode, 2)
        events = self.source / "events.json"
        events.unlink()
        events.symlink_to(SIM / "assets/scenarios/auth.suspicious-login/events.json")
        self.failure("replay", self.source)
        self.assertFalse(self.output.exists())

    def test_missing_and_unbound_observations_do_not_produce_a_result(self):
        self.failure("replay", self.source, "--alerts")
        (self.source / "alerts.json").write_text(json.dumps({
            "schemaVersion": "tarosec.simulation-alerts/v1", "eventsSha256": "0" * 64,
            "windowComplete": True, "alerts": [],
        }))
        self.assertIn("digest mismatch", self.failure("replay", self.source, "--alerts"))
        self.assertFalse(self.output.exists())


if __name__ == "__main__":
    unittest.main()
