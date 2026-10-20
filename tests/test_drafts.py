import unittest

from ai_gitgen.git_collector import GitChanges
from ai_gitgen.security import SecurityError, prepare_context
from ai_gitgen.validators import DraftError, validate_commit, validate_pr


class DraftTests(unittest.TestCase):
    def test_commit_validation(self):
        self.assertEqual(validate_commit("Add Git change collection"), "Add Git change collection")
        for value in ("fix", "x" * 73, "```\nmessage\n```"):
            with self.subTest(value=value), self.assertRaises(DraftError):
                validate_commit(value)

    def test_pr_validation_and_testing_claim_replacement(self):
        draft = "Title: Add secure Git draft generation\n## Why\n- Review changes faster\n## What\n- Add CLI\n## How to Test\n- All tests passed"
        result = validate_pr(draft)
        self.assertIn("## How to Test\n- 실행 권장:", result)
        self.assertNotIn("All tests passed", result)
        for value in (draft.replace("## Why", "## Reason"), draft.replace("- Add CLI", "Add CLI"), draft.replace("secure Git draft generation", "x" * 81)):
            with self.subTest(value=value), self.assertRaises(DraftError):
                validate_pr(value)

    def test_safe_context(self):
        changes = GitChanges("main", " M app.py", ("app.py",), "+email: test@example.com\n+api_key=123456789abcdef\n+Authorization: Bearer abcdef123", "", ())
        safe = prepare_context(changes)
        self.assertNotIn("test@example.com", safe)
        self.assertNotIn("123456789abcdef", safe)
        self.assertNotIn("abcdef123", safe)
        self.assertIn("test@example.com", prepare_context(changes, safe=False))

    def test_sensitive_file_block(self):
        changes = GitChanges("main", "?? .env", (".env",), "", "", (".env",))
        with self.assertRaises(SecurityError):
            prepare_context(changes)


if __name__ == "__main__":
    unittest.main()
