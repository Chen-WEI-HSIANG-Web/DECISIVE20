import pytest

from decisive20.engine import (
    apply_effects,
    available_commands,
    build_initial_game_state,
    compute_score,
    draw_event,
    effective_defense,
    enemy_phase,
    perform_command,
    predict_enemy_targets,
    start_turn,
)
from decisive20.scenario_loader import load_scenario


@pytest.fixture()
def game_state():
    scenario = load_scenario("scenarios/taichung_defense_v1.json")
    return build_initial_game_state(scenario, seed=7)


def test_apply_effects_updates_resources_and_zone(game_state):
    messages = apply_effects(
        game_state,
        {"supply": -3, "zone_defense": {"A": 2}, "force_value": {"預備旅": -2}},
    )
    assert game_state.resources.supply == 13
    assert game_state.zones["A"].defense == 7
    assert game_state.forces["預備旅"].value == 4
    assert messages


def test_apply_effects_rejects_unknown_zone(game_state):
    with pytest.raises(ValueError, match="未知的防區代碼"):
        apply_effects(game_state, {"zone_defense": {"Z": 1}})


def test_apply_effects_clamps_morale(game_state):
    apply_effects(game_state, {"morale": 999})
    assert game_state.resources.morale == 100
    apply_effects(game_state, {"morale": -999})
    assert game_state.resources.morale == 0


def test_start_turn_grants_cp_and_drains_supply(game_state):
    supply_before = game_state.resources.supply
    start_turn(game_state)
    assert game_state.cp == game_state.resources.cp_per_turn
    assert game_state.resources.supply == supply_before - 1


def test_start_turn_escalates_enemy_after_first_round(game_state):
    game_state.current_round = 2
    pressure_before = game_state.resources.enemy_pressure
    start_turn(game_state)
    assert game_state.resources.enemy_pressure == pressure_before + 1


def test_command_reinforce_spends_cp_and_raises_defense(game_state):
    game_state.cp = 3
    perform_command(game_state, "reinforce", "A")
    assert game_state.cp == 2
    assert game_state.zones["A"].defense == 7  # 5 + 2


def test_counter_requires_intel(game_state):
    game_state.cp = 3
    game_state.resources.intel = 0
    assert all(action.key != "counter" for action in available_commands(game_state))
    with pytest.raises(ValueError):
        perform_command(game_state, "counter")


def test_enemy_phase_is_deterministic_under_seed():
    scenario = load_scenario("scenarios/taichung_defense_v1.json")
    a = build_initial_game_state(scenario, seed=42)
    b = build_initial_game_state(scenario, seed=42)
    a.resources.enemy_pressure = 20
    b.resources.enemy_pressure = 20
    msgs_a = enemy_phase(a)
    msgs_b = enemy_phase(b)
    assert msgs_a == msgs_b
    assert {c: z.status for c, z in a.zones.items()} == {c: z.status for c, z in b.zones.items()}


def test_enemy_phase_skips_when_no_pressure(game_state):
    game_state.resources.enemy_pressure = 0
    messages = enemy_phase(game_state)
    assert any("無攻勢" in message for message in messages)


def test_draw_event_recycles_and_reshuffles(game_state):
    drawn = []
    for _ in range(len(game_state.event_deck)):
        drawn.append(draw_event(game_state).code)
        game_state.event_discard.append(game_state.scenario.events[0])
    # Deck empty -> recycle from discard without error.
    recycled = draw_event(game_state)
    assert recycled is not None


def test_compute_score_sets_rank(game_state):
    game_state.ending_type = "victory"
    score, rank = compute_score(game_state)
    assert score > 0
    assert rank in {"S", "A", "B", "C", "D"}


# --------------------------------------------------------------------------- #
# Force deployment
# --------------------------------------------------------------------------- #
def test_deploy_assigns_force_and_spends_cp(game_state):
    game_state.cp = 3
    perform_command(game_state, "deploy", "A", force="預備旅")
    assert game_state.forces["預備旅"].assigned_zone == "A"
    assert game_state.cp == 2


def test_deploy_rejects_depleted_force(game_state):
    game_state.cp = 3
    game_state.forces["預備旅"].value = 0
    with pytest.raises(ValueError, match="戰力"):
        perform_command(game_state, "deploy", "A", force="預備旅")


def test_deploy_excluded_from_standing_menu(game_state):
    game_state.cp = 3
    assert all(action.key != "deploy" for action in available_commands(game_state))


def test_effective_defense_counts_garrison(game_state):
    zone = game_state.zones["A"]
    base = zone.defense
    game_state.forces["預備旅"].assigned_zone = "A"  # value 6
    assert effective_defense(game_state, zone) == base + 6


def test_garrison_absorbs_breach_instead_of_territory(game_state):
    # Make C the lone soft target and garrison it.
    for code, zone in game_state.zones.items():
        zone.defense = 0 if code == "C" else 20
    game_state.forces["預備旅"].value = 5
    game_state.forces["預備旅"].assigned_zone = "C"
    game_state.resources.enemy_pressure = 20  # power (6..10) > eff (5) → breach
    status_before = game_state.zones["C"].status

    enemy_phase(game_state)

    # The garrison soaked the breach: force weakened, zone NOT degraded.
    assert game_state.forces["預備旅"].value < 5
    assert game_state.zones["C"].status == status_before


# --------------------------------------------------------------------------- #
# Intel telegraph
# --------------------------------------------------------------------------- #
def test_predict_enemy_targets_is_stable_and_nonempty(game_state):
    game_state.resources.enemy_pressure = 8
    predicted = predict_enemy_targets(game_state)
    assert predicted == predict_enemy_targets(game_state)
    assert predicted


def test_deploying_off_a_soft_zone_removes_it_from_prediction(game_state):
    game_state.resources.enemy_pressure = 8
    soft = predict_enemy_targets(game_state)[0]
    force = next(iter(game_state.forces.values()))
    force.value = 50
    force.assigned_zone = soft  # now the hardest zone, not a target
    assert soft not in predict_enemy_targets(game_state)
