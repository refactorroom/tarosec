"""Regression checks for one-command scan evidence storage and failure status."""

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPTS = Path(__file__).resolve().parents[1] / "skills" / "tarosec" / "scripts"


class ScanReport(unittest.TestCase):
    def scan_without_semgrep(self, project, *args):
        return subprocess.run([sys.executable, "-B", str(SCRIPTS / "scan.py"), str(project), *map(str, args)],
                              capture_output=True, text=True, env={**os.environ, "PATH": str(project)})

    def test_routes_to_dispatcher_workflow(self):
        result = subprocess.run([sys.executable, "-B", str(SCRIPTS / "route.py"), "scan-report"],
                                capture_output=True, text=True, check=True)
        self.assertEqual(json.loads(result.stdout), {"action": "workflow", "mode": "scan-report"})

    def test_first_scan_persists_inputs_and_retries_do_not_duplicate_ignore_entry(self):
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)
            incoming = project / "assessment.md"
            incoming.write_text("Existing assessment evidence\n", encoding="utf-8")
            ignore = project / ".gitignore"
            for initial, expected in [(None, b"/.tarosec/\n"),
                                      (b"node_modules/", b"node_modules/\n/.tarosec/\n")]:
                with self.subTest(initial=initial):
                    if initial is not None:
                        ignore.write_bytes(initial)
                    runs = []
                    for _ in range(2):
                        result = self.scan_without_semgrep(project, "--bughunter-report", incoming)
                        self.assertEqual(result.returncode, 1, result.stderr)
                        run = Path(result.stdout.strip())
                        runs.append(run)
                        self.assertEqual(run.parent, project.resolve() / ".tarosec" / "reports")
                        self.assertEqual((run / "bughunter-report.md").read_bytes(), incoming.read_bytes())
                        self.assertIn("Failed or incomplete", (run / "scan-summary.md").read_text())
                        self.assertEqual(ignore.read_bytes(), expected)
                    self.assertNotEqual(*runs)

    def test_project_settings_survive_runs_and_cli_override_is_recorded(self):
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory).resolve()
            first = self.scan_without_semgrep(project)
            self.assertEqual(first.returncode, 1, first.stderr)
            settings_path = project / ".tarosec" / "tarosec.json"
            settings = json.loads(settings_path.read_text())
            self.assertEqual(settings["semgrep"]["rulesets"], ["p/security-audit"])
            rule_file = project / "local.yml"
            rule_file.touch()
            settings["semgrep"] = {"rulesets": ["p/typescript", "local.yml"], "exclude": ["vendor/"],
                                   "jobs": 3, "timeoutSeconds": 60}
            custom = json.dumps(settings)
            settings_path.write_text(custom)

            runs = [((), ["p/typescript", str(rule_file)]), (("--config", rule_file), [str(rule_file)])]
            for args, expected_rules in runs:
                with self.subTest(args=args):
                    result = self.scan_without_semgrep(project, *args)
                    self.assertEqual(result.returncode, 1, result.stderr)
                    run = Path(result.stdout.strip())
                    self.assertEqual(json.loads((run / "scan-settings.json").read_text()), {
                        "rulesets": expected_rules, "exclude": [".tarosec", "vendor/"],
                        "jobs": 3, "timeoutSeconds": 60,
                    })
                    self.assertEqual(settings_path.read_text(), custom)

    def test_invalid_settings_do_not_start_a_run_or_replace_file(self):
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)
            workspace = project / ".tarosec"
            workspace.mkdir()
            settings = workspace / "tarosec.json"
            invalid = '{"version": 1, "semgrep": {"jobs": true}}'
            settings.write_text(invalid)
            result = self.scan_without_semgrep(project)
            self.assertEqual(result.returncode, 2)
            self.assertIn("semgrep.jobs must be a positive integer", result.stderr)
            self.assertFalse((workspace / "reports").exists())
            self.assertEqual(settings.read_text(), invalid)
