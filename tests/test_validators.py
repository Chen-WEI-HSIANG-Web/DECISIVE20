import copy

import pytest

from decisive20.scenario_loader import scenario_from_dict
from decisive20.validators import validate_scenario


def _raw():
    return {
        "name": "Test",
        "rounds": 20,
        "resources": {
            "cp_per_turn": 3,
            "supply": 10,
            "intel": 5,
            "morale": 70,
            "political_pressure": 30,
            "enemy_pressure": 10,
        },
        "forces": [{"name": "f1", "value": 5}],
        "zones": [
            {"code": "A", "name": "A", "defense": 4, "status": "friendly", "core": True},
            {"code": "B", "name": "B", "defense": 4, "status": "friendly", "core": True},
            {"code": "C", "name": "C", "defense": 4, "status": "contested", "core": True},
        ],
        "events": [
            {
                "code": "E1",
                "title": "t",
                "description": "d",
                "options": [
                    {"code": "A", "text": "a", "effects": {"morale": 1}},
                    {"code": "B", "text": "b", "effects": {"supply": -1}},
                ],
            }
        ],
        "victory_conditions": [{"type": "survive_rounds", "rounds": 20}],
        "failure_conditions": [{"type": "morale_zero"}],
    }


def test_valid_scenario_passes():
    validate_scenario(scenario_from_dict(_raw()))


def test_unknown_victory_type_rejected():
    raw = _raw()
    raw["victory_conditions"] = [{"type": "win_somehow"}]
    with pytest.raises(ValueError, match="unsupported victory condition"):
        validate_scenario(scenario_from_dict(raw))


def test_condition_references_unknown_zone_rejected():
    raw = _raw()
    raw["failure_conditions"] = [{"type": "core_zones_lost", "core_zones": ["Z"]}]
    with pytest.raises(ValueError, match="unknown zone code"):
        validate_scenario(scenario_from_dict(raw))


def test_duplicate_zone_codes_rejected():
    raw = _raw()
    raw["zones"].append(copy.deepcopy(raw["zones"][0]))
    with pytest.raises(ValueError, match="zone codes must be unique"):
        validate_scenario(scenario_from_dict(raw))


def test_negative_option_cost_rejected():
    raw = _raw()
    raw["events"][0]["options"][0]["cost"] = -1
    with pytest.raises(ValueError, match="cost must be a non-negative integer"):
        validate_scenario(scenario_from_dict(raw))


def test_missing_condition_key_rejected():
    raw = _raw()
    raw["victory_conditions"] = [{"type": "survive_rounds"}]
    with pytest.raises(ValueError, match="requires 'rounds'"):
        validate_scenario(scenario_from_dict(raw))
