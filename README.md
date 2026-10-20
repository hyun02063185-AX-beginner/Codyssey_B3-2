# Codyssey B3-2 — AI Git 초안 생성기

현재 Git 저장소의 변경 내용을 읽어 커밋 메시지 또는 Pull Request(PR) 제목·본문의 **검토용 초안**을 만듭니다. Python 3.10 이상과 Git이 필요합니다. 프로그램은 커밋, push, PR 등록을 자동 실행하지 않습니다.

## 시작하기

별도 Python 패키지 설치가 필요하지 않습니다. 아래 예시는 저장소의 부모 폴더에서 시작합니다.

Windows PowerShell:

```powershell
cd Codyssey_B3-2
python main.py --help
$env:CODYSSEY_API_KEY = "발급받은 키" # 현재 터미널에만 설정; 기록하거나 커밋하지 않기
$env:CODYSSEY_API_URL = "https://copa.codyssey.kr/v1/chat/completions"
$env:CODYSSEY_MODEL = "gpt-5-mini"
python main.py commit
python main.py pr
```

macOS 터미널:

```sh
cd Codyssey_B3-2
python3 main.py --help
export CODYSSEY_API_KEY='발급받은 키'
export CODYSSEY_API_URL='https://copa.codyssey.kr/v1/chat/completions'
export CODYSSEY_MODEL='gpt-5-mini'
python3 main.py commit
python3 main.py pr
```

키가 없다면 `python main.py --help`와 `python -m unittest discover -s tests`는 실행할 수 있습니다. 키가 없는 생성 명령은 이유를 알리고 종료합니다. 키 자체를 명령 인수에 넣지 마세요. 터미널 기록에 남을 수 있습니다.

**API 규격:** 이 클라이언트는 [Chat Completions 요청·응답 형식](https://platform.openai.com/docs/api-reference/chat/create)을 사용합니다: HTTPS POST, Bearer 인증, JSON `model`/`messages`, 응답 `choices[0].message.content`. 위 코디세이 URL과 모델은 사용자가 2026-10-20 Windows PowerShell에서 `commit`과 `pr`을 각각 1회 성공 실행한 설정입니다. 코드는 URL·모델을 고정하지 않으며 `--api-url`과 `--model`로 환경변수를 대신할 수 있습니다. 서버와 모델이 지원할 때만 `--temperature 0.2` 또는 `--max-tokens 500`을 지정하세요. 두 선택 파라미터의 코디세이 지원 여부는 검증되지 않았습니다. 매번 `commit` 또는 `pr` 호출은 최대 1회의 API 요청을 수행하며, 재시도하지 않습니다.

## 무엇을 읽고 보내는가

프로그램은 `git status --short`, `git diff`, `git diff --cached`로 현재 브랜치의 변경 사항을 수집합니다. 미추적 파일은 **이름만** 보냅니다. `git diff`는 기본적으로 미추적 파일 내용을 포함하지 않습니다. `git add` 후의 변경은 `git diff --cached`에서 확인할 수 있습니다. 아직 커밋이 없는 저장소에서도 이 규칙이 적용됩니다. 변경 사항이 없으면 API를 호출하지 않습니다.

기본 안전 모드는 `.env`, 개인키 파일과 비슷한 경로를 발견하면 전송을 막고, diff에서 이메일·Bearer 토큰·일부 자격증명 할당값·알려진 토큰 패턴을 가립니다. 16,000자 초과 문맥은 전송하지 않습니다. 자동 필터가 모든 비밀을 알아낼 수는 없으므로 외부 API에 코드를 보내기 전 `git diff`와 `git diff --cached`를 직접 확인하세요. `--unsafe`는 필터를 끕니다. 민감정보가 전혀 없음을 확인한 경우에만 사용하세요. API 키는 환경변수에서만 읽으며 출력하지 않습니다. `.env` 파일은 Git에서 제외됩니다.

## 결과 예시

아래는 **모의 응답 통합 테스트**로 검증한 구조를 읽기 쉽게 나타낸 예시입니다. [QA 보고서](reports/QA.md)에 사용자가 제공한 실제 코디세이 API 성공 결과를 별도로 기록했습니다.

```text
=== 검토용 초안: COMMIT ===
Describe email masking in Git drafts
=== 끝: 내용을 확인한 뒤 사용하세요 ===
AI API 요청 횟수: 1
```

```text
=== 검토용 초안: PR ===
Title: Explain current code change

## Why
- Clarify behavior

## What
- Update print

## How to Test
- 실행 권장: python -m unittest discover -s tests
=== 끝: 내용을 확인한 뒤 사용하세요 ===
AI API 요청 횟수: 1
```

API 요청 횟수는 표준 오류 스트림에 표시됩니다. PR의 How to Test는 모델이 테스트 성공을 지어내지 못하도록 실행 **권장 명령**으로 교체합니다. 실제로 수행한 검증은 사용자가 PR에 직접 기입해야 합니다. 초안은 복사하여 검토한 후 사용하세요.

## 개발·학습·검증

```text
python -m unittest discover -s tests -v
```

macOS에서는 `python3`를 사용하세요. [학습 목차](docs/learning/INDEX.md)는 Stage 0부터 순서대로 읽을 수 있습니다. [최종 QA 보고서](reports/QA.md)는 모의 API와 실제 API 검증을 구분합니다. API 요청은 공급자 요금 정책에 따라 비용이 발생할 수 있습니다. 이 프로그램은 가격을 추정하지 않으며 자동 재시도도 하지 않습니다.
