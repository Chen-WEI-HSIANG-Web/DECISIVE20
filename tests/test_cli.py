from pathlib import Path

from decisive20.cli import main
from decisive20.game import run_game


def test_cli_start_routes_to_run_game(monkeypatch):
    called = {}

    def fake_run_game(scenario_path, seed=None, color=False):
        called["scenario_path"] = scenario_path
        called["seed"] = seed
        return 0

    monkeypatch.setattr("decisive20.cli.run_game", fake_run_game)

    exit_code = main(
        ["start", "--scenario", "scenarios/taichung_defense_v1.json", "--seed", "5", "--no-color"]
    )

    assert exit_code == 0
    assert called["scenario_path"] == "scenarios/taichung_defense_v1.json"
    assert called["seed"] == 5


def test_cli_demo_routes_to_default_scenario(monkeypatch):
    called = {}

    def fake_run_game(scenario_path, seed=None, color=False):
        called["scenario_path"] = scenario_path
        return 0

    monkeypatch.setattr("decisive20.cli.run_game", fake_run_game)

    exit_code = main(["demo", "--no-color"])

    assert exit_code == 0
    assert Path(called["scenario_path"]).name == "taichung_defense_v1.json"


def _auto_input(prompt: str) -> str:
    # Always pick option A for events; end the command phase immediately.
    if "選項" in prompt:
        return "A"
    return "done"


def test_run_game_completes_and_scores():
    output_lines = []
    exit_code = run_game(
        "scenarios/taichung_defense_v1.json",
        seed=123,
        input_func=_auto_input,
        output_func=output_lines.append,
        color=False,
    )
    full_output = "\n".join(output_lines)

    assert exit_code in {0, 1}
    assert "決戰20" in full_output
    assert "戰役結算" in full_output
    assert "評級" in full_output


def test_run_game_is_reproducible_under_seed():
    def play():
        lines = []
        code = run_game(
            "scenarios/taichung_defense_v1.json",
            seed=999,
            input_func=_auto_input,
            output_func=lines.append,
            color=False,
        )
        return code, "\n".join(lines)

    assert play() == play()
