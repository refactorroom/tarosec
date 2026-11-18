import subprocess
import sys
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts/init_workspace.py"


def run(project, skill="tarosec-audit"):
    return subprocess.run([sys.executable, "-B", str(SCRIPT), str(project), "--skill", skill],
                          capture_output=True, text=True, timeout=10)


class WorkspaceTests(unittest.TestCase):
    def test_preserves_ignore_and_creates_distinct_ignored_runs(self):
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)
            subprocess.run(["git", "init", "-q", str(project)], check=True)
            (project / ".gitignore").write_text("*.log\n!/.tarosec/\n!important.log")
            first = run(project)
            second = run(project, "tarosec-blue")
            self.assertEqual(first.returncode, 0, first.stderr)
            self.assertEqual(second.returncode, 0, second.stderr)
            self.assertNotEqual(first.stdout, second.stdout)
            self.assertTrue(Path(first.stdout.strip()).is_dir())
            self.assertEqual((project / ".gitignore").read_text(),
                             "*.log\n!/.tarosec/\n!important.log\n/.tarosec/\n")
            ignored = subprocess.run(["git", "check-ignore", "-q", ".tarosec/runs/example"], cwd=project)
            self.assertEqual(ignored.returncode, 0)

    def test_parallel_invocations_have_distinct_runs(self):
        with tempfile.TemporaryDirectory() as directory:
            with ThreadPoolExecutor(max_workers=4) as pool:
                results = list(pool.map(lambda _: run(directory), range(4)))
            self.assertTrue(all(result.returncode == 0 for result in results))
            self.assertEqual(len({result.stdout for result in results}), 4)
            self.assertEqual((Path(directory) / ".gitignore").read_text(), "/.tarosec/\n")

    def test_symlink_workspace_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory, tempfile.TemporaryDirectory() as other:
            project = Path(directory)
            (project / ".tarosec").symlink_to(other, target_is_directory=True)
            self.assertNotEqual(run(project).returncode, 0)
            self.assertFalse((Path(other) / "runs").exists())
