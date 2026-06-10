import pytest

from decisive20.engine import apply_effects, build_initial_game_state, draw_event
from decisive20.scenario_loader import load_scenario


@pytest.fixture()
def game_state():
    scenario = load_scenario("scenarios/taichung_defense_v1.json")
    return build_initial_game_state(scenario)


def test_apply_effects_updates_resources_and_zone(game_state):
    messages = apply_effects(
        game_state,
        {"supply": -3, "zone_defense": {"A": 2}, "force_value": {"reserve_brigade": -2}},
    )
    assert game_state.resources.supply == 7
    assert game_state.zones["A"].defense == 7
    assert game_state.forces["reserve_brigade"].value == 4
    assert messages


def test_apply_effects_rejects_unknown_zone(game_state):
    with pytest.raises(ValueError, match="Unknown zone code"):
        apply_effects(game_state, {"zone_defense": {"Z": 1}})


def test_draw_event_recycles_discard(game_state):
    first_event = draw_event(game_state)
    game_state.event_discard.append(first_event)
    game_state.event_deck.clear()
    recycled = draw_event(game_state)
    assert recycled.code == first_event.code
