# Stage 4 — PR 설명 만들기

## 학습 목표

PR과 커밋의 역할을 구분하고 Why·What·How to Test 구조를 검사한다.

## 개념 설명

커밋은 변경 이력 한 건이고 PR(Pull Request)은 GitHub에서 브랜치의 변경을 검토·병합해 달라는 요청이다. PR 제목은 최대 80자다. `Why`는 변경 이유, `What`은 바뀐 내용, `How to Test`는 검증 방법을 설명한다. 세 부분에는 각각 하나 이상의 `-` 불릿이 필요하다. 이 도구는 PR **글 초안**만 만들고 GitHub에 PR을 생성하지 않는다.

## 동작 원리

```text
python main.py pr → Git 변경 수집·보호 → PR_SYSTEM으로 API 1회 → validate_pr() → 검토용 제목·본문
```

## 실제 소스 해설

[`prompts.py`](../../ai_gitgen/prompts.py)의 `PR_SYSTEM`이 `Title:`과 세 섹션을 요청한다. [`validators.py`](../../ai_gitgen/validators.py)의 `validate_pr()`은 제목 길이, 섹션 순서, 불릿 존재를 검사한다. AI가 테스트 완료를 지어낼 수 있으므로 `How to Test`의 AI 문장은 버리고 `python -m unittest discover -s tests`라는 **실행 권장 명령**으로 바꾼다. 실제 수행 결과는 사용자가 확인해서 추가해야 한다. [`main.py`](../../main.py)가 결과를 출력한다.

## 실행 실습

Windows: `python -m unittest tests.test_drafts -v`; 설정 완료 후 `python main.py pr`.

macOS: `python3 -m unittest tests.test_drafts -v`; 설정 완료 후 `python3 main.py pr`.

## 실행 결과

Codex 직접 검증: 모의 API가 `All tests passed`라고 답한 통합 테스트에서 출력은 `- 실행 권장: python -m unittest discover -s tests`로 바뀌었다. 제목·섹션·불릿 검증 테스트 통과. 기능 커밋 `17d27bf`.

사용자 제공 실제 API 사례(2026-10-20): `python main.py pr` 성공, 요청 1회. 제목은 `docs(learning): AI 생성 커밋 메시지 검토 안내 추가`였다. 사용자는 Why가 목적을 설명하고, What이 실제 수정 파일·문구와 맞으며, How to Test에 실행 권장 명령이 포함됐다고 확인했다. PR 본문 전문은 제공되지 않아 불릿을 새로 만들지 않는다.

## 오류 사례

`## Why`가 빠지거나 불릿 대신 일반 문장만 있으면 `DraftError`가 난다. 80자를 넘는 제목도 거절한다. 출력이 아무리 자연스러워도 실제 변경에 맞는지 사람이 검토해야 한다.

## 확인 문제

1. PR과 커밋의 차이는? **답:** 커밋은 Git 이력, PR은 GitHub의 검토·병합 요청이다.
2. `How to Test`에서 성공 주장 문장을 교체하는 이유는? **답:** diff만으로 테스트 실행 여부를 알 수 없기 때문이다.
3. 이 명령이 PR을 등록하나? **답:** 아니다. 제목·본문 초안만 출력한다.
