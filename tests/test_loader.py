from pathlib import Path

import pytest

from decisive20.scenario_loader import load_scenario, scenario_from_dict


def test_load_scenario_success():
    scenario = load_scenario(Path("scenarios/taichung_defense_v1.json"))
    assert scenario.name == "Taichung Defense V1"
    assert len(scenario.events) >= 5


def test_scenario_from_dict_requires_fields():
    with pytest.raises(ValueError, match="missing required scenario fields"):
        scenario_from_dict({"name": "broken"})
