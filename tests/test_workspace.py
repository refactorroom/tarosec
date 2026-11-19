import os
import subprocess
import sys
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts/init_workspace.py"


def run(project, *options, skill="tarosec-audit", script=SCRIPT, env=None):
    return subprocess.run([sys.executable, "-B", str(script), str(project), "--skill", skill,
                           *map(str, options)], capture_output=True, text=True, timeout=10, env=env)


class WorkspaceTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name).resolve()
        self.project = self.root / "project"
        self.project.mkdir()
        self.output = self.root / "output"
        self.output.mkdir()

    def test_default_does_not_write_to_project(self):
        ignore = self.project / ".gitignore"
        ignore.write_bytes(b"*.log\r\n!important.log")
        result = run(self.project)
        self.assertEqual(result.returncode, 0, result.stderr)
        directory = Path(result.stdout.strip())
        if directory.is_dir() and not directory.is_relative_to(self.project):
            self.addCleanup(directory.rmdir)
        self.assertTrue(directory.is_dir())
        self.assertFalse(directory.resolve().is_relative_to(self.project))
        self.assertEqual(ignore.read_bytes(), b"*.log\r\n!important.log")
        self.assertEqual(set(self.project.iterdir()), {ignore})

    def test_standalone_report_accepts_explicit_output(self):
        script = ROOT / "skills/tarosec-report/scripts/init_workspace.py"
        result = run(self.project, "--output-dir", self.output, skill="tarosec-report", script=script)
        self.assertEqual(result.returncode, 0, result.stderr)
        directory = Path(result.stdout.strip())
        self.assertTrue(directory.is_dir())
        self.assertEqual(directory.parent, self.output)
        self.assertEqual(list(self.project.iterdir()), [])

    def test_parallel_invocations_have_distinct_runs(self):
        with ThreadPoolExecutor(max_workers=4) as pool:
            results = list(pool.map(lambda _: run(self.project, "--output-dir", self.output), range(4)))
        for result in results:
            self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(len(set(self.output.iterdir())), 4)
        self.assertEqual(list(self.project.iterdir()), [])

    def test_rejects_output_inside_project_including_aliases(self):
        internal = self.project / "internal"
        internal.mkdir()
        alias = self.root / "alias"
        alias.symlink_to(internal, target_is_directory=True)
        for output in (self.project, internal, alias):
            with self.subTest(output=output):
                self.assertNotEqual(run(self.project, "--output-dir", output).returncode, 0)
        self.assertEqual(set(self.project.iterdir()), {internal})
        self.assertEqual(list(internal.iterdir()), [])

    def test_rejects_default_temp_directory_inside_project(self):
        env = {key: value for key, value in os.environ.items() if key not in {"TMPDIR", "TEMP", "TMP"}}
        env["TMPDIR"] = str(self.project)
        result = run(self.project, env=env)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(list(self.project.iterdir()), [])
