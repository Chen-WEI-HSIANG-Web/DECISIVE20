from pathlib import Path

from decisive20.cli import main
from decisive20.game import run_game


def test_cli_start_routes_to_run_game(monkeypatch):
    called = {}

    def fake_run_game(scenario_path):
        called["scenario_path"] = scenario_path
        return 0

    monkeypatch.setattr("decisive20.cli.run_game", fake_run_game)

    exit_code = main(["start", "--scenario", "scenarios/taichung_defense_v1.json"])

    assert exit_code == 0
    assert called["scenario_path"] == "scenarios/taichung_defense_v1.json"


def test_cli_demo_routes_to_default_scenario(monkeypatch):
    called = {}

    def fake_run_game(scenario_path):
        called["scenario_path"] = scenario_path
        return 0

    monkeypatch.setattr("decisive20.cli.run_game", fake_run_game)

    exit_code = main(["demo"])

    assert exit_code == 0
    assert Path(called["scenario_path"]).name == "taichung_defense_v1.json"


def test_run_game_completes_non_interactively():
    answers = iter(["A", "A", "A", "A", "A"])
    output_lines = []

    exit_code = run_game(
        "scenarios/taichung_defense_v1.json",
        input_func=lambda _prompt: next(answers),
        output_func=output_lines.append,
    )

    full_output = "\n".join(output_lines)

    assert exit_code == 0
    assert "=== Decisive 20: Taichung Defense V1 ===" in full_output
    assert "=== End Game Summary ===" in full_output
    assert "Result: victory" in full_output
