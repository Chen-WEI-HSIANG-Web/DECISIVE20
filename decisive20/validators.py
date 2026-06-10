from __future__ import annotations

from decisive20.constants import (
    SUPPORTED_EFFECT_KEYS,
    VALID_FAILURE_TYPES,
    VALID_VICTORY_TYPES,
    ZoneStatus,
)
from decisive20.models import Scenario


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

    zone_codes = [zone.code for zone in scenario.zones]
    if len(zone_codes) != len(set(zone_codes)):
        raise ValueError("zone codes must be unique")
    zone_code_set = set(zone_codes)

    force_names = [force.name for force in scenario.forces]
    if len(force_names) != len(set(force_names)):
        raise ValueError("force names must be unique")
    force_name_set = set(force_names)

    for zone in scenario.zones:
        if zone.status not in ZoneStatus.ALL:
            raise ValueError(f"unsupported zone status: {zone.status}")

    _validate_events(scenario, zone_code_set, force_name_set)
    _validate_conditions(scenario, zone_code_set)


def _validate_events(scenario: Scenario, zone_codes: set[str], force_names: set[str]) -> None:
    for event in scenario.events:
        if len(event.options) < 2:
            raise ValueError(f"event '{event.code}' must have at least 2 options")

        option_codes = [option.code for option in event.options]
        if len(option_codes) != len(set(option_codes)):
            raise ValueError(f"event '{event.code}' has duplicate option codes")

        for option in event.options:
            if not isinstance(option.effects, dict):
                raise ValueError(f"option '{option.code}' must have an effects object")
            if not isinstance(option.cost, int) or option.cost < 0:
                raise ValueError(f"option '{option.code}' cost must be a non-negative integer")

            for key, value in option.effects.items():
                if key not in SUPPORTED_EFFECT_KEYS:
                    raise ValueError(f"unsupported effect key: {key}")

                if key == "zone_defense":
                    _require_dict(value, "zone_defense")
                    for zone_code in value:
                        if zone_code not in zone_codes:
                            raise ValueError(f"unknown zone code in effects: {zone_code}")

                elif key == "zone_status":
                    _require_dict(value, "zone_status")
                    for zone_code, status in value.items():
                        if zone_code not in zone_codes:
                            raise ValueError(f"unknown zone code in effects: {zone_code}")
                        if status not in ZoneStatus.ALL:
                            raise ValueError(f"unsupported zone status: {status}")

                elif key == "force_value":
                    _require_dict(value, "force_value")
                    for force_name in value:
                        if force_name not in force_names:
                            raise ValueError(f"unknown force name in effects: {force_name}")


def _validate_conditions(scenario: Scenario, zone_codes: set[str]) -> None:
    if not scenario.victory_conditions:
        raise ValueError("at least 1 victory condition must exist")
    if not scenario.failure_conditions:
        raise ValueError("at least 1 failure condition must exist")

    for condition in scenario.victory_conditions:
        ctype = _condition_type(condition, VALID_VICTORY_TYPES, "victory")
        if ctype == "survive_rounds":
            _require_key(condition, "rounds", "survive_rounds")
        elif ctype == "hold_min_core_zones":
            _require_key(condition, "min_zones", "hold_min_core_zones")
            _require_zone_list(condition, "core_zones", zone_codes, "hold_min_core_zones")

    for condition in scenario.failure_conditions:
        ctype = _condition_type(condition, VALID_FAILURE_TYPES, "failure")
        if ctype == "enemy_controls_zones":
            _require_key(condition, "count", "enemy_controls_zones")
        elif ctype == "core_zones_lost":
            _require_zone_list(condition, "core_zones", zone_codes, "core_zones_lost")


def _condition_type(condition: dict, valid: set[str], kind: str) -> str:
    if "type" not in condition:
        raise ValueError(f"{kind} condition missing 'type'")
    ctype = condition["type"]
    if ctype not in valid:
        raise ValueError(f"unsupported {kind} condition: {ctype}")
    return ctype


def _require_key(condition: dict, key: str, ctype: str) -> None:
    if key not in condition:
        raise ValueError(f"{ctype} condition requires '{key}'")


def _require_zone_list(condition: dict, key: str, zone_codes: set[str], ctype: str) -> None:
    _require_key(condition, key, ctype)
    value = condition[key]
    if not isinstance(value, list) or not value:
        raise ValueError(f"{ctype} '{key}' must be a non-empty list")
    for zone_code in value:
        if zone_code not in zone_codes:
            raise ValueError(f"{ctype} references unknown zone code: {zone_code}")


def _require_dict(value, name: str) -> None:
    if not isinstance(value, dict):
        raise ValueError(f"{name} must be an object")
