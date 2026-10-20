"""Minimize and screen Git context before sending it to an external API."""

import re

from .git_collector import GitChanges


class SecurityError(Exception):
    """Potentially sensitive change content cannot be sent safely."""


RISKY_PATH = re.compile(r"(^|/)(\.env(?:\.|$)|id_(?:rsa|ed25519)|[^/]+\.(?:pem|key|p12|pfx)$)", re.I)
PRIVATE_KEY = re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----.*?-----END [A-Z ]*PRIVATE KEY-----", re.S)
PRIVATE_KEY_MARKER = re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----", re.I)
EMAIL = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I)
BEARER = re.compile(r"\bBearer\s+[^\s\"']+", re.I)
ASSIGNMENT = re.compile(r"(?i)\b(api[_-]?key|access[_-]?token|secret|password)\b(\s*[:=]\s*)([\"']?)[^\s\"']{8,}\3")
KNOWN_TOKEN = re.compile(r"\b(?:sk-[A-Za-z0-9_-]{16,}|ghp_[A-Za-z0-9]{16,}|github_pat_[A-Za-z0-9_]{16,}|AKIA[A-Z0-9]{16})\b")


def prepare_context(changes: GitChanges, *, safe: bool = True, limit: int = 16000) -> str:
    if safe and any(RISKY_PATH.search(name.replace("\\", "/")) for name in changes.files):
        raise SecurityError("비밀 파일로 보이는 경로가 변경 목록에 있어 전송을 중단했습니다.")
    sections = [
        f"Branch: {changes.branch}",
        "Status:\n" + changes.status,
        "Changed files:\n" + "\n".join(changes.files),
        "Untracked files (names only):\n" + "\n".join(changes.untracked_files),
        "Staged diff:\n" + changes.staged_diff,
        "Unstaged diff:\n" + changes.unstaged_diff,
    ]
    context = "\n\n".join(sections)
    if safe:
        if PRIVATE_KEY_MARKER.search(context) and not PRIVATE_KEY.search(context):
            raise SecurityError("완전하지 않은 개인키 블록이 있어 전송을 중단했습니다.")
        context = PRIVATE_KEY.sub("[REDACTED PRIVATE KEY]", context)
        context = EMAIL.sub("[REDACTED EMAIL]", context)
        context = BEARER.sub("Bearer [REDACTED]", context)
        context = ASSIGNMENT.sub(lambda m: m.group(1) + m.group(2) + "[REDACTED]", context)
        context = KNOWN_TOKEN.sub("[REDACTED TOKEN]", context)
    if len(context) > limit:
        raise SecurityError("Git 변경 내용이 전송 한도를 초과합니다. 변경을 나눠 실행하세요.")
    return context
