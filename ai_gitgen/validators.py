"""Reject malformed drafts and normalize test instructions."""

import re


class DraftError(Exception):
    """The model returned an unusable draft."""


TEST_CLAIM = re.compile(r"(?i)(?:tests?\s+(?:passed|succeeded|were run)|테스트(?:가|는|를)?\s*(?:통과|완료|실행했|실행됨))")


def validate_commit(raw: str) -> str:
    value = raw.strip()
    if value.startswith("```") or not value:
        raise DraftError("커밋 메시지가 비어 있거나 코드 블록입니다.")
    title = value.splitlines()[0].strip()
    if len(title) > 72 or len(title) < 8 or title.lower() in {"update", "changes", "fix", "수정", "변경"}:
        raise DraftError("커밋 제목이 너무 길거나 의미가 부족합니다.")
    if title.startswith(("#", "-", "Title:")):
        raise DraftError("커밋 제목 형식이 잘못되었습니다.")
    return value


def validate_pr(raw: str) -> str:
    value = raw.strip()
    match = re.fullmatch(
        r"Title: ([^\n]+)\n+## Why\n(.+?)\n+## What\n(.+?)\n+## How to Test\n(.+)",
        value, re.S,
    )
    if not match:
        raise DraftError("PR 제목 또는 필수 섹션(Why, What, How to Test)이 없습니다.")
    title, why, what, how = (part.strip() for part in match.groups())
    if len(title) > 80 or len(title) < 8:
        raise DraftError("PR 제목 길이가 잘못되었습니다.")
    if TEST_CLAIM.search("\n".join((title, why, what))):
        raise DraftError("PR 본문에 확인되지 않은 테스트 수행 주장이 있습니다.")
    for section in (why, what, how):
        if not any(re.match(r"^-\s+\S", line) for line in section.splitlines()):
            raise DraftError("각 PR 섹션에는 불릿이 필요합니다.")
    # Testing claims are not verifiable from a diff. Replace all generated
    # testing prose with a reproducible action, without claiming it passed.
    return f"Title: {title}\n\n## Why\n{why}\n\n## What\n{what}\n\n## How to Test\n- 실행 권장: python -m unittest discover -s tests"
