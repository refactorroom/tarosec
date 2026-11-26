"""Regression checks for one-command scan evidence storage and failure status."""

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch


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
            for initial, suffix in [(None, b""), (b"node_modules/", b"node_modules/\n")]:
                with self.subTest(initial=initial):
                    if initial is not None:
                        ignore.write_bytes(initial)
                    runs = []
                    for _ in range(2):
                        result = self.scan_without_semgrep(project, "--bughunter-report", incoming,
                                                           "--update-gitignore")
                        self.assertEqual(result.returncode, 1, result.stderr)
                        run = Path(result.stdout.strip())
                        runs.append(run)
                        self.assertEqual(run.parent, project.resolve() / ".tarosec" / "reports")
                        self.assertEqual((run / "bughunter-report.md").read_bytes(), incoming.read_bytes())
                        self.assertIn("rules-unavailable", (run / "scan-summary.md").read_text())
                        self.assertEqual(ignore.read_bytes(), suffix + b"# Tarosec run output\n/.tarosec/\n")
                    self.assertNotEqual(*runs)

    def test_project_settings_survive_runs_and_cli_override_is_recorded(self):
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory).resolve()
            first = self.scan_without_semgrep(project)
            self.assertEqual(first.returncode, 1, first.stderr)
            settings_path = project / ".tarosec" / "tarosec.json"
            settings = json.loads(settings_path.read_text())
            self.assertEqual(settings["semgrep"]["rulesets"], [".tarosec/rules/semgrep.yml"])
            self.assertFalse((project / ".gitignore").exists())
            rule_file = project / "local.yml"
            rule_file.touch()
            settings["semgrep"] = {"rulesets": ["p/typescript", "local.yml"], "exclude": ["vendor/"],
                                   "jobs": 3, "timeoutSeconds": 60}
            custom = json.dumps(settings)
            settings_path.write_text(custom)

            runs = [
                ((), [], "registry-disabled"),
                (("--config", rule_file), [str(rule_file)], "scanner-unavailable"),
            ]
            for args, expected_rules, reason in runs:
                with self.subTest(args=args):
                    result = self.scan_without_semgrep(project, *args)
                    self.assertEqual(result.returncode, 1, result.stderr)
                    run = Path(result.stdout.strip())
                    snapshot = json.loads((run / "scan-settings.json").read_text())
                    self.assertEqual(snapshot["resolvedRulesets"], expected_rules)
                    self.assertEqual(snapshot["exclude"], [".tarosec", "vendor/"])
                    self.assertEqual((snapshot["jobs"], snapshot["timeoutSeconds"]), (3, 60))
                    stages = json.loads((run / "run.json").read_text())["stages"]
                    self.assertEqual(stages["scan"], {"status": "not_run", "reason": reason})
                    self.assertEqual(stages["report"], {"status": "not_run"})
                    self.assertEqual(settings_path.read_text(), custom)

    def test_registry_fetch_flag_is_unavailable(self):
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)
            result = self.scan_without_semgrep(project, "--allow-registry")
            self.assertEqual(result.returncode, 2)
            self.assertIn("unrecognized arguments: --allow-registry", result.stderr)
            self.assertFalse((project / ".tarosec").exists())

    def test_default_audit_routing_does_not_write_to_project(self):
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)
            source = project / "app.py"
            source.write_text("VALUE = 1\n")
            output = subprocess.run([sys.executable, "-B", str(SCRIPTS / "route.py"),
                                     "--evidence", "project", "--available", "tarosec-audit"],
                                    cwd=project, check=True, capture_output=True, text=True)
            self.assertEqual(json.loads(output.stdout)["skill"], "tarosec-audit")
            self.assertEqual(list(project.iterdir()), [source])
            self.assertEqual(source.read_text(), "VALUE = 1\n")

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

    @unittest.skipUnless(os.name == "posix", "fake Semgrep uses a POSIX executable")
    def test_semgrep_state_is_written_inside_the_run_directory(self):
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory).resolve()
            rules = project / "rules.yml"
            rules.touch()
            scanner = project / "semgrep"
            scanner.write_text(f"#!{sys.executable}\n"
                               "import json, os, sys\n"
                               "from pathlib import Path\n"
                               "paths = {name: os.environ[name] for name in "
                               "('SEMGREP_LOG_FILE', 'SEMGREP_SETTINGS_FILE')}\n"
                               "assert 'SEMGREP_RULES' not in os.environ\n"
                               "assert 'SEMGREP_APP_TOKEN' not in os.environ\n"
                               "json_out = Path(sys.argv[sys.argv.index('--json-output') + 1])\n"
                               "json_out.with_name('child-paths.json').write_text(json.dumps(paths))\n"
                               "json_out.write_text(json.dumps({'results': [], 'errors': [], "
                               "'paths': {'scanned': ['app.py']}}))\n"
                               "Path(sys.argv[sys.argv.index('--sarif-output') + 1]).write_text('{}')\n")
            scanner.chmod(0o700)
            with patch.dict(os.environ, {"SEMGREP_RULES": "p/typescript", "SEMGREP_APP_TOKEN": "synthetic"}):
                result = self.scan_without_semgrep(project, "--config", rules)
            self.assertEqual(result.returncode, 0, result.stderr)
            run = Path(result.stdout.strip())
            paths = json.loads((run / "child-paths.json").read_text())
            self.assertEqual(paths, {"SEMGREP_LOG_FILE": str(run / "semgrep-internal.log"),
                                     "SEMGREP_SETTINGS_FILE": str(run / "semgrep-user-settings.yml")})
