from decisive20.constants import ZoneStatus
from decisive20.engine import build_initial_game_state, check_failure, check_victory
from decisive20.scenario_loader import load_scenario


def _state():
    scenario = load_scenario("scenarios/taichung_defense_v1.json")
    return build_initial_game_state(scenario, seed=1)


def test_enemy_pressure_zero_triggers_victory():
    game_state = _state()
    game_state.resources.enemy_pressure = 0
    assert check_victory(game_state) is True
    assert game_state.ending_type == "victory"


def test_survive_rounds_triggers_victory():
    game_state = _state()
    game_state.current_round = game_state.scenario.rounds
    assert check_victory(game_state) is True
    assert game_state.ending_type == "victory"


def test_supply_zero_triggers_failure():
    game_state = _state()
    game_state.resources.supply = 0
    assert check_failure(game_state) is True
    assert game_state.ending_type == "failure"


def test_core_zones_lost_triggers_failure():
    game_state = _state()
    for code in ("A", "B", "C"):
        game_state.zones[code].status = ZoneStatus.ENEMY_CONTROLLED
    assert check_failure(game_state) is True
    assert game_state.ending_type == "failure"


def test_enemy_controls_zones_triggers_failure():
    game_state = _state()
    for code in ("A", "B", "C"):
        game_state.zones[code].status = ZoneStatus.ENEMY_CONTROLLED
    assert check_failure(game_state) is True
