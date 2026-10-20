# Stage 0 — 프로젝트 준비와 CLI

## 학습 목표

Python 파일 실행, 모듈과 함수, `argparse`의 역할을 설명하고 `--help`를 실행할 수 있다.

## 개념 설명

CLI(Command Line Interface)는 터미널에 명령을 입력해 쓰는 프로그램이다. `python main.py commit`에서 Python은 실행기, `main.py`는 진입 파일, `commit`은 위치 인수다. `import`는 다른 파일의 기능을 가져온다. 함수는 `def`로 이름 붙인 작업 단위다. `main.py` 맨 아래의 `if __name__ == "__main__":`는 파일을 직접 실행했을 때만 `main()`을 호출한다. Python 3.10 이상과 Git이 필요하다. `.gitignore`는 Git이 `.env`나 임시 Python 파일을 추적하지 않게 한다.

## 동작 원리

```text
python main.py --help → main.py 실행 → build_parser()가 인수 정의 → argparse가 도움말 출력
```

## 실제 소스 해설

[`main.py`](../../main.py)의 `build_parser()`는 `commit`/`pr`과 API 옵션을 정의한다. `main()`은 인수를 읽고 `collect_changes()`로 넘어간다. [`ai_gitgen/__init__.py`](../../ai_gitgen/__init__.py)가 `ai_gitgen`을 Python 패키지로 만든다. 패키지는 관련 모듈을 담은 폴더다. `argparse`는 잘못된 명령을 자동으로 거절하고 사용법을 보여 준다.

## 실행 실습

Windows: `python --version`; `git --version`; `python main.py --help`.

macOS: `python3 --version`; `git --version`; `python3 main.py --help`.

## 실행 결과

실제 확인: Windows에서 Python 3.14.6, Git 2.54.0, `--help` 출력 성공. 버전 번호는 사용자 환경에서 다를 수 있다. 이 단계의 기준 커밋은 `b68dbc5`다.

## 오류 사례

`python` 명령을 찾지 못하면 Python 설치 또는 PATH를 확인한다. `invalid choice`는 `commit`/`pr` 이외의 명령을 넣었을 때 `argparse`가 알리는 오류다. `--help`는 API 키 없이도 작동한다.

## 확인 문제

1. `main.py`를 직접 실행할 때만 `main()`이 호출되는 이유는? **답:** `__name__ == "__main__"` 조건 때문이다.
2. `argparse`가 하는 일은? **답:** 명령 인수를 읽고 검사하며 도움말을 만든다.
3. `.env`를 `.gitignore`에 넣은 이유는? **답:** 비밀 설정 파일이 Git 커밋에 들어갈 가능성을 낮추기 위해서다.
