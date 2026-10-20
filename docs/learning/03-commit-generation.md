# Stage 3 — 커밋 메시지 만들기

## 학습 목표

Git 변경이 프롬프트로 바뀌는 과정과 제목 검증 이유를 이해한다.

## 개념 설명

커밋은 Git의 한 시점 기록이며 메시지는 그 변경을 설명한다. 좋은 제목은 `update` 같은 모호한 말보다 구체적인 동작을 말한다. 이 프로그램은 제목 50자 이내를 권장하고 72자를 넘으면 거절한다. 본문은 선택 사항이다. 생성된 글을 자동으로 커밋하지 않으므로 사용자가 실제 diff와 비교한 뒤 사용할 수 있다.

## 동작 원리

```text
python main.py commit → collect_changes() → prepare_context() → AIClient.generate() → validate_commit() → 검토용 출력
```

## 실제 소스 해설

[`main.py`](../../main.py)의 `main()`은 `commit`일 때 [`prompts.py`](../../ai_gitgen/prompts.py)의 `COMMIT_SYSTEM`을 고른다. 이 프롬프트는 변경 사항만 설명하고 테스트 성공을 주장하지 말라고 지시한다. [`validators.py`](../../ai_gitgen/validators.py)의 `validate_commit()`은 첫 줄을 제목으로 보고 길이·빈 내용·의미 없는 제목·코드 블록을 검사한다. `AIClient.generate()`는 한 번만 호출된다. 오류는 사용자에게 메시지로 표시되고 초안을 출력하지 않는다.

## 실행 실습

Windows: `git diff`; `python -m unittest tests.test_cli -v`; 설정 완료 후 `python main.py commit`.

macOS: `git diff`; `python3 -m unittest tests.test_cli -v`; 설정 완료 후 `python3 main.py commit`.

## 실행 결과

실제 확인: 모의 API 통합 테스트에서 변경이 있는 저장소의 `commit` 요청이 1회였고 `Describe email masking in Git drafts`가 검토 구획 안에 출력됐다. 이는 **모의 응답**이며 실제 AI의 품질 증거가 아니다. 실제 코디세이 출력 평가는 키·접속 규격 부족으로 미완료다. 기능 커밋 `17d27bf`.

## 오류 사례

변경이 없으면 `변경 사항이 없습니다`를 출력하고 요청은 0회다. 제목이 73자 이상이거나 `fix`뿐이면 `DraftError`가 난다. API가 형식 밖 텍스트를 주면 사용자가 명령을 다시 실행할 수 있지만 새 요청이므로 비용을 확인해야 한다.

## 확인 문제

1. 프롬프트에 Git diff가 필요한 이유는? **답:** AI가 실제 변경을 설명할 근거가 되기 때문이다.
2. 왜 제목 길이를 검사하나? **답:** 읽기 쉬운 Git 이력을 유지하고 형식 오류를 막기 위해서다.
3. 출력이 곧 커밋인가? **답:** 아니다. 메시지 초안만 출력한다.
