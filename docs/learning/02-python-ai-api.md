# Stage 2 — Python에서 AI API 호출

## 학습 목표

API, HTTP, JSON, 인증, 환경변수를 설명하고 요청과 응답 코드를 따라간다.

## 개념 설명

API는 프로그램끼리 기능을 요청하는 약속이다. REST API는 보통 URL에 HTTP 요청을 보내고 JSON으로 데이터를 주고받는다. URL은 서버 주소, POST는 자료를 보내는 HTTP 방식, JSON은 키와 값으로 표현한 텍스트 형식이다. API 키는 사용 권한을 증명하는 비밀값이며 `CODYSSEY_API_KEY` 환경변수에서 읽는다. 프롬프트(prompt)는 AI에 주는 지시다. 컨텍스트(context)는 이번 Git 변경 내용이다. 응답은 서버가 돌려준 JSON이다.

`temperature`는 생성의 무작위성, `max_tokens`는 출력 토큰 수 상한 요청이다. 토큰은 모델이 처리하는 텍스트 단위다. 공급자·모델마다 지원이 달라 이 프로그램은 두 옵션을 지정했을 때만 보낸다. 토큰 사용량과 가격도 공급자 정책에 달려 있으며 이 프로그램은 비용을 계산하지 않는다.

## 동작 원리

```text
환경변수/옵션 + Git 컨텍스트 → JSON 인코딩 → HTTPS POST + Bearer 키 → JSON 응답 → 텍스트
```

## 실제 소스 해설

[`ai_client.py`](../../ai_gitgen/ai_client.py)의 `AIClient.__init__()`은 HTTPS URL, 모델, 키, 파라미터 범위를 검사한다. `generate()`는 `urllib.request.Request`에 `model`과 `messages`를 JSON으로 넣는다. `request.urlopen()`이 실제 네트워크 요청을 보낸다. `request_count`는 요청 시도마다 1 증가한다. `choices[0].message.content`를 읽고 비어 있으면 오류로 처리한다. 인증 오류·네트워크 오류·잘못된 JSON을 `APIError`로 바꾼다. 자동 재시도는 없다. [`main.py`](../../main.py)는 설정을 환경변수와 CLI 옵션에서 읽는다.

코디세이 Public API의 URL·모델·호환성은 확인되지 않았다. 따라서 이 코드는 [문서화된 Chat Completions 형식](https://platform.openai.com/docs/api-reference/chat/create)만 구현하고 기본 URL이나 모델을 추측하지 않는다.

## 실행 실습

키 없이 Windows: `python -m unittest tests.test_ai_client -v`; macOS: `python3 -m unittest tests.test_ai_client -v`. 확인된 공급자 설정을 받은 뒤에만 README의 환경변수를 설정하고 `python main.py commit`(macOS `python3`)을 실행한다.

## 실행 결과

실제 확인: 모의 HTTP 응답으로 요청 JSON, 선택 파라미터, 인증 실패, 네트워크 실패, 응답 누락을 검사했다. 실제 API 요청 0회. API 코드 커밋 `3a0fcc6`. 공급자 실제 연결은 아직 미검증이다.

## 오류 사례

키가 없으면 `CODYSSEY_API_KEY` 오류로 종료한다. HTTP 401/403은 키 또는 권한을 확인한다. 네트워크 오류는 연결을 확인한 뒤 사용자가 다시 실행한다. 무작정 자동 재시도하면 비용이 늘 수 있다. 지원하지 않는 파라미터 오류가 나오면 해당 옵션을 빼고 공급자 문서를 확인한다.

## 확인 문제

1. JSON은 무엇인가? **답:** 요청·응답을 키와 값으로 표현하는 텍스트 형식이다.
2. 키를 소스에 넣지 않는 이유는? **답:** Git 이력이나 공유 파일로 비밀값이 퍼질 수 있기 때문이다.
3. 요청 횟수가 비용과 관계있는 이유는? **답:** 공급자가 요청 또는 토큰 사용량에 따라 과금할 수 있기 때문이다.
