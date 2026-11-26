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

    def test_default_creates_tarosec_workspace(self):
        ignore = self.project / ".gitignore"
        ignore.write_bytes(b"*.log\r\n!important.log")
        result = run(self.project)
        self.assertEqual(result.returncode, 0, result.stderr)
        directory = Path(result.stdout.strip())
        self.assertTrue(directory.is_dir())
        self.assertEqual(directory.parent, (self.project / ".tarosec/workspace").resolve())
        self.assertTrue((self.project / ".tarosec/README.md").is_file())
        self.assertEqual(ignore.read_bytes(), b"*.log\r\n!important.log")
        self.assertTrue((directory / "run.json").is_file())

    def test_default_is_idempotent(self):
        readme = self.project / ".tarosec"
        for _ in range(2):
            self.assertEqual(run(self.project, "--update-gitignore").returncode, 0)
        (readme / "README.md").write_text("custom")
        self.assertEqual(run(self.project, "--update-gitignore").returncode, 0)
        self.assertEqual((readme / "README.md").read_text(), "custom")
        ignore = (self.project / ".gitignore").read_text()
        self.assertEqual(ignore.count("/.tarosec/workspace/"), 1)
        self.assertEqual(len(list((readme / "workspace").iterdir())), 3)

    def test_respects_existing_tarosec_ignore(self):
        (self.project / ".gitignore").write_text(".tarosec/\n")
        self.assertEqual(run(self.project).returncode, 0)
        self.assertEqual((self.project / ".gitignore").read_text(), ".tarosec/\n")

    def test_rejects_symlinked_workspace(self):
        (self.project / ".tarosec").mkdir()
        (self.project / ".tarosec/workspace").symlink_to(self.output, target_is_directory=True)
        self.assertNotEqual(run(self.project).returncode, 0)
        self.assertEqual(list(self.output.iterdir()), [])

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
