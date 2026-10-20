import io
import json
import unittest
from unittest.mock import patch
from urllib.error import HTTPError, URLError

from ai_gitgen.ai_client import AIClient, APIError


class AIClientTests(unittest.TestCase):
    def setUp(self):
        self.client = AIClient("https://example.test/v1/chat/completions", "verified-model", "test-key", temperature=0.2, max_tokens=250)

    def test_request_shape_and_response(self):
        response = io.BytesIO(json.dumps({"choices": [{"message": {"content": "Useful title"}}]}).encode())
        with patch("ai_gitgen.ai_client.request.urlopen", return_value=response) as urlopen:
            self.assertEqual(self.client.generate("system", "user"), "Useful title")
        sent = urlopen.call_args.args[0]
        body = json.loads(sent.data)
        self.assertEqual(body["model"], "verified-model")
        self.assertEqual(body["temperature"], 0.2)
        self.assertEqual(body["max_tokens"], 250)
        self.assertEqual(body["messages"][1]["content"], "user")
        self.assertEqual(self.client.request_count, 1)

    def test_bad_key_and_network(self):
        for failure, expected in [(HTTPError("url", 401, "secret", {}, None), "인증"), (URLError("offline"), "네트워크")]:
            with self.subTest(failure=failure), patch("ai_gitgen.ai_client.request.urlopen", side_effect=failure):
                with self.assertRaisesRegex(APIError, expected):
                    self.client.generate("s", "u")
        self.assertEqual(self.client.request_count, 2)

    def test_missing_content(self):
        with patch("ai_gitgen.ai_client.request.urlopen", return_value=io.BytesIO(b'{"choices": []}')):
            with self.assertRaisesRegex(APIError, "텍스트"):
                self.client.generate("s", "u")

    def test_no_optional_parameters_by_default(self):
        client = AIClient("https://example.test/v1/chat/completions", "model", "key")
        with patch("ai_gitgen.ai_client.request.urlopen", return_value=io.BytesIO(b'{"choices":[{"message":{"content":"ok"}}]}')) as urlopen:
            client.generate("s", "u")
        body = json.loads(urlopen.call_args.args[0].data)
        self.assertNotIn("temperature", body)
        self.assertNotIn("max_tokens", body)


if __name__ == "__main__":
    unittest.main()
