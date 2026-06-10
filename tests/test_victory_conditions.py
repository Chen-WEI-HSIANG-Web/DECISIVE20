from decisive20.engine import build_initial_game_state, check_failure, check_victory
from decisive20.scenario_loader import load_scenario


def test_enemy_pressure_zero_triggers_victory():
    scenario = load_scenario("scenarios/taichung_defense_v1.json")
    game_state = build_initial_game_state(scenario)
    game_state.resources.enemy_pressure = 0
    assert check_victory(game_state) is True
    assert game_state.ending_type == "victory"


def test_supply_zero_triggers_failure():
    scenario = load_scenario("scenarios/taichung_defense_v1.json")
    game_state = build_initial_game_state(scenario)
    game_state.resources.supply = 0
    assert check_failure(game_state) is True
    assert game_state.ending_type == "failure"
