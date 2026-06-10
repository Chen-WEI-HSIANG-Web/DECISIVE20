from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from decisive20.game import run_game
from decisive20.scenario_loader import load_scenario

DEFAULT_SCENARIO = "taichung_defense_v1.json"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="decisive20",
        description="決戰20 — 回合制策略決策壓力兵棋遊戲（命令列介面）。",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    start_parser = subparsers.add_parser("start", help="開始一個劇本。")
    start_parser.add_argument("--scenario", required=True, help="劇本 JSON 檔案路徑。")
    _add_play_args(start_parser)
    start_parser.set_defaults(handler=_handle_start)

    validate_parser = subparsers.add_parser("validate", help="驗證劇本檔案。")
    validate_parser.add_argument("--scenario", required=True, help="劇本 JSON 檔案路徑。")
    validate_parser.set_defaults(handler=_handle_validate)

    demo_parser = subparsers.add_parser("demo", help="執行預設示範劇本。")
    _add_play_args(demo_parser)
    demo_parser.set_defaults(handler=_handle_demo)

    return parser


def _add_play_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--seed", type=int, default=None, help="亂數種子，用於可重現的對局。")
    parser.add_argument("--no-color", action="store_true", help="關閉 ANSI 彩色輸出。")


def _force_utf8_stdout() -> None:
    # Windows consoles often default to a legacy codepage (e.g. cp950) that
    # cannot encode the game's box-drawing and CJK glyphs.
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            try:
                reconfigure(encoding="utf-8")
            except (ValueError, OSError):
                pass


def main(argv: list[str] | None = None) -> int:
    _force_utf8_stdout()
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.handler(args)


def _use_color(args: argparse.Namespace) -> bool:
    if getattr(args, "no_color", False):
        return False
    if os.environ.get("NO_COLOR"):
        return False
    return sys.stdout.isatty()


def _handle_start(args: argparse.Namespace) -> int:
    return run_game(args.scenario, seed=args.seed, color=_use_color(args))


def _handle_validate(args: argparse.Namespace) -> int:
    scenario = load_scenario(args.scenario)
    print(f"劇本「{scenario.name}」驗證通過。")
    return 0


def _handle_demo(args: argparse.Namespace) -> int:
    scenario_path = Path(__file__).resolve().parent.parent / "scenarios" / DEFAULT_SCENARIO
    return run_game(scenario_path, seed=args.seed, color=_use_color(args))
