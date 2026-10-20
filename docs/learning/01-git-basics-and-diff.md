# Stage 1 — Git과 변경 내용

## 학습 목표

Git과 GitHub, 작업 트리와 스테이징, branch와 commit·push의 차이를 설명한다. 수집 코드가 어떤 변경을 읽는지 확인한다.

## 개념 설명

Git은 컴퓨터의 변경 이력을 관리하는 도구다. GitHub는 Git 저장소를 온라인에 보관하고 협업하는 서비스다. 작업 트리(working tree)는 편집 중인 파일, 스테이징(staging)은 다음 커밋에 넣기로 고른 변경이다. `git add`가 변경을 스테이징하고 `git commit`이 로컬 이력을 만든다. `git push`가 그 이력을 GitHub로 보낸다. 브랜치(branch)는 이력의 작업 줄기다. PR은 브랜치의 변경을 검토·병합해 달라는 GitHub 요청이며 커밋 자체가 아니다.

## 동작 원리

```text
저장소 폴더 → subprocess로 Git 실행 → branch/status/diff/diff --cached 수집 → GitChanges
```

## 실제 소스 해설

[`git_collector.py`](../../ai_gitgen/git_collector.py)의 `_git()`은 `subprocess.run(["git", ...])`으로 인수를 목록으로 전달한다. 셸 문자열을 실행하지 않아 파일명에 특수 문자가 있어도 명령으로 해석되지 않는다. `collect_changes()`는 저장소 여부를 확인하고 브랜치, status, 파일 목록, 두 diff를 `GitChanges`에 담는다. `has_changes`가 거짓이면 API를 호출하지 않는다. `--porcelain=v1 -z`는 기계가 읽기 쉬운 파일 목록을 만든다.

`git diff`는 스테이징 **전** 변경, `git diff --cached`는 스테이징 **후** 변경을 보여 준다. 새 미추적 파일은 두 diff 모두에 내용이 나타나지 않고 이름만 목록에 나온다. `git add 새파일` 후에는 staged diff에 내용이 나온다. 초기 커밋 전에도 이 규칙을 따른다.

## 실행 실습

Windows/macOS 공통: `git status --short`; `git diff`; `git diff --cached`. 테스트: Windows `python -m unittest tests.test_git_collector -v`, macOS `python3 -m unittest tests.test_git_collector -v`. 실습용 파일을 새로 만든 뒤 세 명령을 비교하고 `git add 파일명` 후 다시 비교한다. 실제 프로젝트 파일을 함부로 변경하지 않도록 연습용 저장소를 쓰는 것이 좋다.

## 실행 결과

실제 확인: 임시 Git 저장소에서 미추적 파일은 파일명만, `git add` 후 파일 내용은 staged diff에, 추가 편집은 unstaged diff에 나타났다. Git 외부 폴더 오류도 검증했다. 해당 테스트 2개 통과. 기능 커밋 `6504f63`.

## 오류 사례

Git 저장소가 아니면 `GitError`가 난다. 스테이징하지 않은 새 파일의 내용이 diff에 없는 것은 오류가 아니라 Git의 기본 동작이다. 커밋이 없는 빈 저장소에서 브랜치 이름은 환경에 따라 다를 수 있다.

## 확인 문제

1. Git과 GitHub의 차이는? **답:** Git은 로컬 이력 도구, GitHub는 온라인 협업 서비스다.
2. `git diff --cached`는 무엇을 보나? **답:** 다음 커밋을 위해 스테이징한 변경이다.
3. 미추적 파일 내용이 기본 diff에 없는 이유는? **답:** Git이 아직 추적하지 않아 diff 대상으로 삼지 않기 때문이다.
