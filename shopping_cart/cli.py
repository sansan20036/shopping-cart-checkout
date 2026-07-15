"""Command-line interface."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Sequence, TextIO

from .domain import CheckoutService
from .exceptions import ShoppingCartError
from .parser import CheckoutInputParser


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="計算購物車結算金額")
    parser.add_argument(
        "input_file",
        nargs="?",
        type=Path,
        help="輸入檔案；省略時從標準輸入讀取",
    )
    return parser


def main(
    argv: Sequence[str] | None = None,
    *,
    stdin: TextIO = sys.stdin,
    stdout: TextIO = sys.stdout,
    stderr: TextIO = sys.stderr,
) -> int:
    args = build_argument_parser().parse_args(argv)

    try:
        text = (
            args.input_file.read_text(encoding="utf-8")
            if args.input_file
            else stdin.read()
        )
        request = CheckoutInputParser().parse(text)
        total = CheckoutService().calculate(request)
    except (ShoppingCartError, OSError) as exc:
        print(f"錯誤：{exc}", file=stderr)
        return 2

    print(f"{total:.2f}", file=stdout)
    return 0
