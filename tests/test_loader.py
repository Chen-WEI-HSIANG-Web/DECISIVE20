from pathlib import Path

import pytest

from decisive20.scenario_loader import load_scenario, scenario_from_dict


def test_load_scenario_success():
    scenario = load_scenario(Path("scenarios/taichung_defense_v1.json"))
    assert scenario.name == "台中防衛戰 V1"
    assert len(scenario.events) >= 5
    # Enemy / upkeep config parsed.
    assert scenario.enemy.escalation_per_round == 1
    assert scenario.upkeep.supply_per_round == 1
    # Option costs parsed.
    assert scenario.events[0].options[0].cost >= 0


def test_scenario_from_dict_requires_fields():
    with pytest.raises(ValueError, match="missing required scenario fields"):
        scenario_from_dict({"name": "broken"})


def test_scenario_from_dict_reports_missing_nested_field():
    raw = {
        "name": "x",
        "rounds": 20,
        "resources": {"cp_per_turn": 3, "supply": 10, "intel": 5, "morale": 70},
        "forces": [],
        "zones": [],
        "events": [],
        "victory_conditions": [],
        "failure_conditions": [],
    }
    with pytest.raises(ValueError, match="missing required field"):
        scenario_from_dict(raw)
