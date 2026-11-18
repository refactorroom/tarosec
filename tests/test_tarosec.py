"""Structural, helper and fixture checks. These validate artifacts, not model behavior."""
import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "skills" / "tarosec-purple" / "scripts"))
from validate_record import validate  # noqa: E402
import classify_exercise as ce  # noqa: E402

SKILLS = sorted(p for p in (ROOT / "skills").iterdir() if (p / "SKILL.md").is_file())
FIX = ROOT / "evaluations" / "fixtures"


def load(p):
    return json.loads(Path(p).read_text())


def frontmatter(text):
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    assert m, "missing frontmatter"
    fm = {}
    for line in m.group(1).splitlines():
        if re.match(r"^[a-z-]+:", line):
            k, _, v = line.partition(":")
            fm[k] = v.strip()
    return fm


class SkillFormat(unittest.TestCase):
    def test_four_p0_skills(self):
        self.assertEqual([p.name for p in SKILLS],
                         ["tarosec-audit", "tarosec-blue", "tarosec-purple", "tarosec-red"])

    def test_frontmatter_matches_spec(self):
        for skill in SKILLS:
            fm = frontmatter((skill / "SKILL.md").read_text())
            self.assertEqual(fm["name"], skill.name)
            self.assertRegex(fm["name"], r"^[a-z0-9]+(-[a-z0-9]+)*$")
            self.assertLessEqual(len(fm["name"]), 64)
            self.assertTrue(0 < len(fm["description"]) <= 1024, skill.name)
            self.assertIn("Not for", fm["description"], f"{skill.name}: needs non-trigger")

    def test_body_size(self):
        for skill in SKILLS:
            self.assertLess(len((skill / "SKILL.md").read_text().splitlines()), 500)

    def test_links_resolve_inside_skill(self):
        for skill in SKILLS:
            for md in skill.rglob("*.md"):
                for target in re.findall(r"\]\(([^)#]+)\)", md.read_text()):
                    if target.startswith("http"):
                        continue
                    resolved = (md.parent / target).resolve()
                    self.assertTrue(resolved.exists(), f"{md}: {target}")
                    self.assertIn(skill.resolve(), resolved.parents, f"{md}: {target} escapes skill")

    def test_backticked_skill_paths_exist(self):
        for skill in SKILLS:
            for p in re.findall(r"`((?:assets|scripts|references)/[^`\s]+)`", (skill / "SKILL.md").read_text()):
                self.assertTrue((skill / p).exists(), f"{skill.name}: {p}")

    def test_shared_files_in_sync(self):
        r = subprocess.run([sys.executable, "-B", str(ROOT / "scripts" / "sync_shared.py"), "--check"],
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stdout)


class Schemas(unittest.TestCase):
    def test_examples_valid(self):
        for kind in ("engagement", "exercise", "finding"):
            errs = validate(load(ROOT / f"examples/{kind}.example.json"), load(ROOT / f"schemas/{kind}.schema.json"))
            self.assertEqual(errs, [], kind)

    def test_validator_rejects(self):
        schema = load(ROOT / "schemas/finding.schema.json")
        bad = load(ROOT / "examples/finding.example.json")
        bad["confidence"] = "Very high"
        bad["extra"] = 1
        del bad["remediation"]
        self.assertEqual(len(validate(bad, schema)), 3)

    def test_validator_refuses_unsupported_keyword(self):
        self.assertTrue(validate(1, {"maximum": 0}))

    def test_fixtures_schema_valid(self):
        schema = load(ROOT / "schemas/exercise.schema.json")
        for f in ("P1-purple-mixed", "P2-purple-authorization", "P3-purple-attack-mismatch"):
            self.assertEqual(validate(load(FIX / f / "exercise.json"), schema), [], f)
        self.assertEqual(validate(load(FIX / "R1-red-scope/engagement.json"),
                                  load(ROOT / "schemas/engagement.schema.json")), [])


def step(**res):
    base = {"id": "X", "technique": {"id": "T1059.001", "name": "PowerShell"}, "description": "d",
            "targetHost": "h1", "expected": {"telemetrySources": ["s"], "detections": ["R"], "maxLatencySeconds": 60}}
    if res:
        base["results"] = res
    return base


EXEC = {"status": "executed", "endedAt": "2026-01-01T00:00:00Z"}
TEL_OK = [{"source": "s", "status": "observed", "sourceHealthy": True}]


class Classifier(unittest.TestCase):
    def outcome(self, s):
        return ce.classify_step(s)[0]

    def test_p1_answer_key(self):
        ex = load(FIX / "P1-purple-mixed/exercise.json")
        self.assertEqual([self.outcome(s) for s in ex["steps"]],
                         ["Detected", "Detection gap", "Inconclusive", "Inconclusive", "Detected (late)"])

    def test_not_run(self):
        self.assertEqual(self.outcome(step()), "Not run")
        self.assertEqual(self.outcome(step(execution={"status": "blocked"})), "Not run")

    def test_prevented(self):
        s = step(execution={**EXEC, "prevented": True}, alerts=[{"ruleId": "R", "status": "not_fired"}])
        self.assertEqual(self.outcome(s), "Prevented")

    def test_telemetry_gap_needs_healthy_source(self):
        absent = [{"source": "s", "status": "absent", "sourceHealthy": True}]
        s = step(execution=EXEC, telemetry=absent, alerts=[{"ruleId": "R", "status": "not_fired"}])
        self.assertEqual(self.outcome(s), "Telemetry gap")
        absent[0].pop("sourceHealthy")
        self.assertEqual(self.outcome(s), "Inconclusive")

    def test_missing_alert_export_is_inconclusive(self):
        self.assertEqual(self.outcome(step(execution=EXEC, telemetry=TEL_OK)), "Inconclusive")
        s = step(execution=EXEC, telemetry=TEL_OK, alerts=[{"ruleId": "R", "status": "unknown"}])
        self.assertEqual(self.outcome(s), "Inconclusive")

    def test_naive_timestamp_not_used_for_latency(self):
        s = step(execution={"status": "executed", "endedAt": "2026-01-01T00:00:00"}, telemetry=TEL_OK,
                 alerts=[{"ruleId": "R", "status": "fired", "firedAt": "2026-01-01T05:00:00", "host": "h1"}])
        outcome, reasons = ce.classify_step(s)
        self.assertEqual(outcome, "Detected")
        self.assertIn("unmeasurable", reasons[-1])

    def test_unexpected_rule_not_counted(self):
        s = step(execution=EXEC, telemetry=TEL_OK, alerts=[
            {"ruleId": "R", "status": "not_fired"},
            {"ruleId": "OTHER", "status": "fired", "firedAt": "2026-01-01T00:00:10Z", "host": "h1"}])
        self.assertEqual(self.outcome(s), "Detection gap")

    def test_cli_rejects_invalid(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "x.json"
            p.write_text(json.dumps({"schemaVersion": "nope"}))
            r = subprocess.run([sys.executable, "-B", str(ROOT / "skills/tarosec-purple/scripts/classify_exercise.py"), str(p)],
                               capture_output=True, text=True)
            self.assertEqual(r.returncode, 1)


class AuditFixtureDistinguishes(unittest.TestCase):
    """Both suites are green; only the vulnerable variant lets user 101 read invoice 1."""

    def run_variant(self, name):
        code = ("import sys; sys.path.insert(0,'app'); import invoices as i\n"
                "try:\n print('LEAK', i.get_invoice(i.User(id=101, tenant_id=10), 1).id)\n"
                "except (i.NotFound, i.Forbidden):\n print('DENIED')\n"
                "try:\n print('LEAK', i.get_invoice(i.User(id=100, tenant_id=10), 3).id)\n"
                "except (i.NotFound, i.Forbidden):\n print('DENIED')")
        cwd = FIX / name
        tests = subprocess.run([sys.executable, "-B", "-m", "unittest", "discover", "-s", "tests"],
                               cwd=cwd, capture_output=True, text=True)
        probe = subprocess.run([sys.executable, "-B", "-c", code], cwd=cwd, capture_output=True, text=True)
        return tests.returncode, probe.stdout.split()

    def test_vulnerable_green_but_leaks(self):
        rc, out = self.run_variant("A1-audit-green-idor")
        self.assertEqual(rc, 0)
        self.assertEqual(out, ["LEAK", "1", "LEAK", "3"])

    def test_control_green_and_denies(self):
        rc, out = self.run_variant("A1-audit-green-idor-control")
        self.assertEqual(rc, 0)
        self.assertEqual(out, ["DENIED", "DENIED"])


class PrepareEval(unittest.TestCase):
    def test_blind_copy(self):
        with tempfile.TemporaryDirectory() as d:
            dest = Path(d) / "ws"
            r = subprocess.run([sys.executable, "-B", str(ROOT / "scripts/prepare_eval.py"),
                                "--case", "P1", "--arm", "skill", "--dest", str(dest)], capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stderr)
            names = {p.name for p in dest.rglob("*")}
            self.assertNotIn("cases.json", names)
            self.assertIn("PROMPT.md", names)
            self.assertNotIn("Inconclusive", "".join(p.read_text() for p in dest.rglob("*.md")))
            r2 = subprocess.run([sys.executable, "-B", str(ROOT / "scripts/prepare_eval.py"),
                                 "--case", "P1", "--arm", "skill", "--dest", str(dest)], capture_output=True, text=True)
            self.assertEqual(r2.returncode, 2)


if __name__ == "__main__":
    unittest.main()
