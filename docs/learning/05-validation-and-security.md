# Stage 5 — 형식 검증과 민감정보 보호

## 학습 목표

입력·출력 검증과 기본 안전 모드가 무엇을 막는지 설명한다.

## 개념 설명

AI API로 diff를 보내면 코드가 외부 서비스에 전달된다. API 키, 이메일, 인증 토큰, 개인키 같은 정보가 섞일 수 있으므로 전송 전에 검사한다. 검증(validation)은 형식과 범위를 확인하는 일이다. 마스킹(redaction)은 민감한 텍스트를 `[REDACTED]`로 바꾸는 일이다. 자동 검사는 완전하지 않으므로 보내기 전 사람이 `git diff`를 읽어야 한다.

## 동작 원리

```text
GitChanges → prepare_context(safe=True) → 위험 경로 차단·패턴 마스킹·길이 제한 → API
API 응답 → validate_commit()/validate_pr() → 형식이 맞을 때만 출력
```

## 실제 소스 해설

[`security.py`](../../ai_gitgen/security.py)의 `prepare_context()`는 `.env`·개인키 경로를 차단하고 이메일, Bearer 문자열, 자격증명 할당값, 알려진 토큰 패턴을 가린다. 불완전한 개인키 블록은 전송을 막는다. 16,000자 초과 문맥도 거절한다. [`main.py`](../../main.py)는 `--unsafe`가 없으면 안전 모드를 켠다. `--unsafe`는 필터를 비활성화하므로 diff에 비밀이 없음을 직접 확인해야 한다. [`ai_client.py`](../../ai_gitgen/ai_client.py)는 HTTPS URL, 모델, 키, 파라미터 범위를 확인하고 키를 로그에 출력하지 않는다. [`validators.py`](../../ai_gitgen/validators.py)는 생성된 문구의 형식을 검증한다.

## 실행 실습

Windows: `python -m unittest tests.test_drafts -v`; `python main.py commit --help`.

macOS: `python3 -m unittest tests.test_drafts -v`; `python3 main.py commit --help`.

`git diff`와 `git diff --cached`를 읽고 민감정보가 있으면 파일에서 제거한 뒤 실행한다. 테스트용으로 실제 비밀값을 만들거나 입력하지 않는다.

## 실행 결과

실제 확인: 모의 데이터에서 이메일·토큰 마스킹, `.env` 경로 차단, 안전 모드 해제 시 원문 유지가 테스트됐다. 실제 비밀값은 사용하지 않았다. 보안 로직은 기능 커밋 `17d27bf`에 포함된다.

## 오류 사례

`.env` 변경이 목록에 있으면 `SecurityError`가 난다. diff가 너무 크면 분할해야 한다. 자동 필터가 알아보지 못하는 새로운 비밀 형식은 남을 수 있다. `--unsafe`는 이 위험을 높인다. HTTP 오류 본문은 그대로 출력하지 않아 서버가 보낸 민감 문구가 노출되지 않게 한다.

## 확인 문제

1. 기본 안전 모드를 켠 이유는? **답:** 평소 실행에서 민감정보 전송 가능성을 줄이기 위해서다.
2. 마스킹만 믿으면 안 되는 이유는? **답:** 모든 비밀 형식을 패턴으로 식별할 수 없기 때문이다.
3. `--unsafe`는 무엇을 바꾸나? **답:** 민감정보 필터를 끈다.
