from __future__ import annotations

import argparse
from pathlib import Path

from decisive20.game import run_game
from decisive20.scenario_loader import load_scenario


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="decisive20")
    subparsers = parser.add_subparsers(dest="command", required=True)

    start_parser = subparsers.add_parser("start", help="Start a scenario.")
    start_parser.add_argument("--scenario", required=True, help="Path to scenario JSON.")
    start_parser.set_defaults(handler=_handle_start)

    validate_parser = subparsers.add_parser("validate", help="Validate a scenario file.")
    validate_parser.add_argument("--scenario", required=True, help="Path to scenario JSON.")
    validate_parser.set_defaults(handler=_handle_validate)

    demo_parser = subparsers.add_parser("demo", help="Run the default demo scenario.")
    demo_parser.set_defaults(handler=_handle_demo)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.handler(args)


def _handle_start(args: argparse.Namespace) -> int:
    return run_game(args.scenario)


def _handle_validate(args: argparse.Namespace) -> int:
    scenario = load_scenario(args.scenario)
    print(f"Scenario '{scenario.name}' is valid.")
    return 0


def _handle_demo(args: argparse.Namespace) -> int:
    scenario_path = Path(__file__).resolve().parent.parent / "scenarios" / "taichung_defense_v1.json"
    return run_game(scenario_path)
