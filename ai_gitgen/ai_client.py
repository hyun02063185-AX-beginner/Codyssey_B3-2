"""Configurable Chat Completions REST client (one request per draft)."""

import json
from urllib import error, parse, request


class APIError(Exception):
    """The configured AI service could not produce a valid response."""


class AIClient:
    def __init__(self, url: str, model: str, api_key: str, *, temperature=None, max_tokens=None):
        parsed = parse.urlsplit(url)
        if parsed.scheme != "https" or not parsed.netloc or parsed.username or parsed.password or parsed.query or parsed.fragment:
            raise APIError("API URL은 사용자 정보와 쿼리가 없는 HTTPS 주소여야 합니다.")
        if not model.strip() or not api_key:
            raise APIError("모델과 CODYSSEY_API_KEY가 필요합니다.")
        if temperature is not None and not 0 <= temperature <= 2:
            raise APIError("temperature는 0~2 범위여야 합니다.")
        if max_tokens is not None and not 1 <= max_tokens <= 8192:
            raise APIError("max_tokens는 1~8192 범위여야 합니다.")
        self.url, self.model, self.api_key = url, model, api_key
        self.temperature, self.max_tokens = temperature, max_tokens
        self.request_count = 0

    def generate(self, system: str, user: str) -> str:
        payload = {"model": self.model, "messages": [
            {"role": "system", "content": system}, {"role": "user", "content": user}
        ]}
        if self.temperature is not None:
            payload["temperature"] = self.temperature
        if self.max_tokens is not None:
            payload["max_tokens"] = self.max_tokens
        outgoing = request.Request(
            self.url,
            data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
            method="POST",
        )
        self.request_count += 1
        try:
            with request.urlopen(outgoing, timeout=30) as response:
                data = json.load(response)
        except error.HTTPError as exc:
            if exc.code in (401, 403):
                raise APIError(f"인증 또는 권한 오류 (HTTP {exc.code}).") from None
            raise APIError(f"AI API 응답 오류 (HTTP {exc.code}).") from None
        except (error.URLError, TimeoutError, OSError):
            raise APIError("AI API 네트워크 연결에 실패했습니다.") from None
        except (ValueError, UnicodeError):
            raise APIError("AI API 응답이 올바른 JSON이 아닙니다.") from None
        try:
            content = data["choices"][0]["message"]["content"]
            if not isinstance(content, str) or not content.strip():
                raise ValueError()
            return content.strip()
        except (KeyError, IndexError, TypeError, ValueError):
            raise APIError("AI API 응답에 텍스트가 없습니다.") from None
