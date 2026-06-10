from __future__ import annotations

from decisive20.models import Scenario

VALID_ZONE_STATUSES = {
    "friendly",
    "contested",
    "enemy_controlled",
    "cut_off",
    "destroyed",
}

SUPPORTED_EFFECT_KEYS = {
    "supply",
    "intel",
    "morale",
    "political_pressure",
    "enemy_pressure",
    "zone_defense",
    "zone_status",
    "force_value",
}


def validate_scenario(scenario: Scenario) -> None:
    if not 10 <= scenario.rounds <= 30:
        raise ValueError("rounds must be between 10 and 30")

    if not 0 <= scenario.resources.morale <= 100:
        raise ValueError("morale must be between 0 and 100")

    if not 0 <= scenario.resources.political_pressure <= 100:
        raise ValueError("political_pressure must be between 0 and 100")

    if len(scenario.events) < 1:
        raise ValueError("at least 1 event card must exist")

    if len(scenario.zones) < 3:
        raise ValueError("at least 3 zones must exist")

    zone_codes = {zone.code for zone in scenario.zones}
    force_names = {force.name for force in scenario.forces}

    for zone in scenario.zones:
        if zone.status not in VALID_ZONE_STATUSES:
            raise ValueError(f"unsupported zone status: {zone.status}")

    for event in scenario.events:
        if len(event.options) < 2:
            raise ValueError(f"event '{event.code}' must have at least 2 options")

        option_codes = [option.code for option in event.options]
        if len(option_codes) != len(set(option_codes)):
            raise ValueError(f"event '{event.code}' has duplicate option codes")

        for option in event.options:
            if not isinstance(option.effects, dict):
                raise ValueError(f"option '{option.code}' must have an effects object")

            for key, value in option.effects.items():
                if key not in SUPPORTED_EFFECT_KEYS:
                    raise ValueError(f"unsupported effect key: {key}")

                if key == "zone_defense":
                    if not isinstance(value, dict):
                        raise ValueError("zone_defense must be an object")
                    for zone_code in value:
                        if zone_code not in zone_codes:
                            raise ValueError(f"unknown zone code in effects: {zone_code}")

                if key == "zone_status":
                    if not isinstance(value, dict):
                        raise ValueError("zone_status must be an object")
                    for zone_code, status in value.items():
                        if zone_code not in zone_codes:
                            raise ValueError(f"unknown zone code in effects: {zone_code}")
                        if status not in VALID_ZONE_STATUSES:
                            raise ValueError(f"unsupported zone status: {status}")

                if key == "force_value":
                    if not isinstance(value, dict):
                        raise ValueError("force_value must be an object")
                    for force_name in value:
                        if force_name not in force_names:
                            raise ValueError(f"unknown force name in effects: {force_name}")
