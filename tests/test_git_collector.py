import subprocess
import tempfile
import unittest
from pathlib import Path

from ai_gitgen.git_collector import GitError, collect_changes


def git(cwd, *args):
    subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True)


class GitCollectorTests(unittest.TestCase):
    def test_non_repository(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(GitError):
                collect_changes(Path(directory))

    def test_untracked_staged_and_unstaged(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            git(root, "init", "-q")
            (root / "new.txt").write_text("first\n", encoding="utf-8")
            first = collect_changes(root)
            self.assertIn("new.txt", first.untracked_files)
            self.assertEqual(first.staged_diff, "")
            self.assertEqual(first.unstaged_diff, "")
            git(root, "add", "new.txt")
            staged = collect_changes(root)
            self.assertIn("+first", staged.staged_diff)
            self.assertEqual(staged.untracked_files, ())
            (root / "new.txt").write_text("first\nsecond\n", encoding="utf-8")
            mixed = collect_changes(root)
            self.assertIn("+second", mixed.unstaged_diff)
            self.assertIn("+first", mixed.staged_diff)


if __name__ == "__main__":
    unittest.main()
