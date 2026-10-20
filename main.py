"""B3-2 command line entry point."""

import argparse


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Git 변경을 읽어 AI 커밋 메시지와 PR 초안을 생성합니다.")
    parser.add_argument("command", choices=("commit", "pr"), help="생성할 초안 종류")
    return parser


def main() -> int:
    build_parser().parse_args()
    raise SystemExit("아직 구현 중입니다.")


if __name__ == "__main__":
    raise SystemExit(main())
