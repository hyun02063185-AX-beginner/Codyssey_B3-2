"""B3-2 command line entry point."""

import argparse
import os
from pathlib import Path
import sys

from ai_gitgen.ai_client import AIClient, APIError
from ai_gitgen.git_collector import GitError, collect_changes
from ai_gitgen.prompts import COMMIT_SYSTEM, PR_SYSTEM
from ai_gitgen.security import SecurityError, prepare_context
from ai_gitgen.validators import DraftError, validate_commit, validate_pr


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Git 변경을 읽어 AI 커밋 메시지와 PR 초안을 생성합니다.")
    parser.add_argument("command", choices=("commit", "pr"), help="생성할 초안 종류")
    parser.add_argument("--api-url", default=os.getenv("CODYSSEY_API_URL"), help="확인된 Chat Completions HTTPS URL")
    parser.add_argument("--model", default=os.getenv("CODYSSEY_MODEL"), help="공급자가 지원하는 모델 ID")
    parser.add_argument("--temperature", type=float, help="공급자와 모델이 지원할 때만 사용 (0~2)")
    parser.add_argument("--max-tokens", type=int, help="공급자와 모델이 지원할 때만 사용 (1~8192)")
    parser.add_argument("--unsafe", action="store_true", help="민감정보 필터를 끕니다. 전송 내용을 직접 확인한 경우에만 사용")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    client = None
    try:
        changes = collect_changes(Path.cwd())
        if not changes.has_changes:
            print("변경 사항이 없습니다.")
            return 0
        context = prepare_context(changes, safe=not args.unsafe)
        if not args.api_url or not args.model:
            raise APIError("확인된 API 주소와 모델이 필요합니다. --api-url, --model 또는 환경변수를 설정하세요.")
        client = AIClient(
            args.api_url, args.model, os.getenv("CODYSSEY_API_KEY", ""),
            temperature=args.temperature, max_tokens=args.max_tokens,
        )
        system = COMMIT_SYSTEM if args.command == "commit" else PR_SYSTEM
        raw = client.generate(system, context)
        draft = validate_commit(raw) if args.command == "commit" else validate_pr(raw)
        print("=== 검토용 초안: " + args.command.upper() + " ===")
        print(draft)
        print("=== 끝: 내용을 확인한 뒤 사용하세요 ===")
        return 0
    except (GitError, SecurityError, APIError, DraftError) as exc:
        print(f"오류: {exc}", file=sys.stderr)
        return 1
    finally:
        print(f"AI API 요청 횟수: {client.request_count if client else 0}", file=sys.stderr)


if __name__ == "__main__":
    raise SystemExit(main())
