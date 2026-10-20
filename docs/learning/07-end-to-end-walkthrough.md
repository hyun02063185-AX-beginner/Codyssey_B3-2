# Stage 7 — 전체 실행 실습

## 학습 목표

변경 확인부터 AI 초안 검토, 수동 커밋과 push까지의 순서를 재현한다.

## 개념 설명

초안은 AI가 작성한 제안이며 최종 책임은 변경 내용을 아는 개발자에게 있다. 커밋은 로컬 Git 기록, push는 원격 GitHub 전송이다. PR은 GitHub에서 별도로 열어 검토를 받는다. 이 도구는 메시지와 PR 설명만 출력하므로 우발적인 커밋·push·PR 생성을 막는다.

## 동작 원리

```text
파일 편집 → git status/diff 확인 → commit/pr 초안 생성 → 실제 변경과 비교 → 수동 git add/commit/push → 필요하면 수동 PR
```

## 실제 소스 해설

[`main.py`](../../main.py)가 명령을 읽고 [`git_collector.py`](../../ai_gitgen/git_collector.py), [`security.py`](../../ai_gitgen/security.py), [`ai_client.py`](../../ai_gitgen/ai_client.py), [`validators.py`](../../ai_gitgen/validators.py)를 순서대로 호출한다. 예외 처리 블록은 오류를 표준 오류로 알리고 종료 코드 1을 반환한다. 성공하면 구획 표시 안에 검토용 글을 출력한다. `finally`는 시도한 API 요청 횟수를 알린다.

## 실행 실습

공통: `git status --short`; `git diff`; `git diff --cached`; `git add 파일명`. 확인된 공급자 설정 뒤 Windows는 `python main.py commit`과 `python main.py pr`, macOS는 `python3 main.py commit`과 `python3 main.py pr`을 실행한다. 초안을 확인한 다음에만 `git commit -m "검토한 제목"`과 `git push origin main`을 수동 실행한다. PR은 GitHub에서 별도로 작성한다. 다른 사람의 변경이 있는 공동 저장소에서는 push 전 동기화와 충돌 확인이 필요하다.

## 실행 결과

Codex 직접 확인: 이 프로젝트의 기능 커밋은 `b68dbc5`(기준점), `6504f63`(Git 수집), `3a0fcc6`(API 클라이언트), `17d27bf`(초안·보안) 순서로 작성됐다. 사용자 제공 실제 API 실행에서는 실습 메모 변경을 설명하는 커밋 초안과 PR 초안이 생성됐다. 이 실제 AI 제목을 Git 커밋에 적용했다는 증거는 아직 없다. 테스트 결과는 [QA 보고서](../../reports/QA.md)에 기록했다. 위 `git commit`·`git push` 명령은 **학습 실습 예시**다.

## 오류 사례

변경이 없으면 초안 대신 `변경 사항이 없습니다`가 나온다. 키가 없거나 설정이 맞지 않으면 API 전에 오류가 난다. push에서 충돌이나 보호 규칙 오류가 나면 강제 push를 하지 말고 원인을 확인한다.

## 확인 문제

1. 초안을 바로 커밋하지 않는 이유는? **답:** AI가 실제 변경을 잘못 설명할 수 있어 검토가 필요하기 때문이다.
2. commit과 push의 차이는? **답:** commit은 로컬 기록, push는 원격 전송이다.
3. 이 도구가 PR을 생성하나? **답:** 아니다. PR 설명 초안만 만든다.
