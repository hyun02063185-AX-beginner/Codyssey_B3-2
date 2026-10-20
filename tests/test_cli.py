import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout, redirect_stderr
from unittest.mock import patch

import main


def git(cwd, *args):
    subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True)


class CLITests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        git(self.root, "init", "-q")
        git(self.root, "config", "user.name", "Test")
        git(self.root, "config", "user.email", "test@example.test")
        (self.root / "code.py").write_text("print('old')\n", encoding="utf-8")
        git(self.root, "add", ".")
        git(self.root, "commit", "-qm", "initial")

    def run_cli(self, *args, response=None, key="mock-key"):
        stdout, stderr = io.StringIO(), io.StringIO()
        mock_response = io.BytesIO(json.dumps({"choices": [{"message": {"content": response}}]}).encode())
        with patch.object(sys, "argv", ["main.py", *args]), patch.object(Path, "cwd", return_value=self.root), patch.dict(os.environ, {"CODYSSEY_API_KEY": key}), patch("ai_gitgen.ai_client.request.urlopen", return_value=mock_response) as urlopen, redirect_stdout(stdout), redirect_stderr(stderr):
            code = main.main()
        sent = json.loads(urlopen.call_args.args[0].data) if urlopen.called else None
        return code, stdout.getvalue(), stderr.getvalue(), urlopen.call_count, sent

    def test_no_changes_avoids_api(self):
        code, out, err, calls, _ = self.run_cli("commit")
        self.assertEqual(code, 0)
        self.assertIn("변경 사항이 없습니다", out)
        self.assertEqual(calls, 0)

    def test_commit_one_request_and_safe_context(self):
        (self.root / "code.py").write_text("print('user@example.com')\n", encoding="utf-8")
        code, out, err, calls, sent = self.run_cli("commit", "--api-url", "https://example.test/v1/chat/completions", "--model", "verified-model", response="Describe email masking in Git drafts")
        self.assertEqual(code, 0)
        self.assertEqual(calls, 1)
        self.assertIn("Describe email masking", out)
        self.assertIn("요청 횟수: 1", err)
        self.assertNotIn("user@example.com", sent["messages"][1]["content"])
        self.assertIn("[REDACTED EMAIL]", sent["messages"][1]["content"])

    def test_pr_structure_and_missing_key(self):
        (self.root / "code.py").write_text("print('new')\n", encoding="utf-8")
        args = ("pr", "--api-url", "https://example.test/v1/chat/completions", "--model", "verified-model")
        draft = "Title: Explain current code change\n## Why\n- Clarify behavior\n## What\n- Update print\n## How to Test\n- Tests passed"
        code, out, _, calls, _ = self.run_cli(*args, response=draft)
        self.assertEqual((code, calls), (0, 1))
        self.assertIn("## How to Test\n- 실행 권장", out)
        code, _, err, calls, _ = self.run_cli(*args, response=draft, key="")
        self.assertEqual((code, calls), (1, 0))
        self.assertIn("CODYSSEY_API_KEY", err)


if __name__ == "__main__":
    unittest.main()
