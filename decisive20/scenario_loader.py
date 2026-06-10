from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from decisive20.models import EventCard, EventOption, Force, ResourceState, Scenario, Zone
from decisive20.validators import validate_scenario


def load_scenario(path: str | Path) -> Scenario:
    scenario_path = Path(path)
    with scenario_path.open("r", encoding="utf-8") as handle:
        raw_data = json.load(handle)

    scenario = scenario_from_dict(raw_data)
    validate_scenario(scenario)
    return scenario


def scenario_from_dict(raw_data: dict[str, Any]) -> Scenario:
    required_fields = {
        "name",
        "rounds",
        "resources",
        "forces",
        "zones",
        "events",
        "victory_conditions",
        "failure_conditions",
    }
    missing = sorted(required_fields - raw_data.keys())
    if missing:
        raise ValueError(f"missing required scenario fields: {', '.join(missing)}")

    resource_data = raw_data["resources"]
    resources = ResourceState(
        cp_per_turn=resource_data["cp_per_turn"],
        supply=resource_data["supply"],
        intel=resource_data["intel"],
        morale=resource_data["morale"],
        political_pressure=resource_data["political_pressure"],
        enemy_pressure=resource_data["enemy_pressure"],
    )

    forces = [
        Force(name=force["name"], value=force["value"])
        for force in raw_data["forces"]
    ]
    zones = [
        Zone(
            code=zone["code"],
            name=zone["name"],
            defense=zone["defense"],
            status=zone["status"],
            core=zone.get("core", False),
        )
        for zone in raw_data["zones"]
    ]
    events = [
        EventCard(
            code=event["code"],
            title=event["title"],
            description=event["description"],
            options=[
                EventOption(
                    code=option["code"],
                    text=option["text"],
                    effects=option["effects"],
                )
                for option in event["options"]
            ],
        )
        for event in raw_data["events"]
    ]

    try:
        return Scenario(
            name=raw_data["name"],
            rounds=raw_data["rounds"],
            resources=resources,
            forces=forces,
            zones=zones,
            events=events,
            victory_conditions=raw_data["victory_conditions"],
            failure_conditions=raw_data["failure_conditions"],
        )
    except KeyError as exc:
        raise ValueError(f"missing required field: {exc.args[0]}") from exc
