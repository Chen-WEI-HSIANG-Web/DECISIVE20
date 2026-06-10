from __future__ import annotations

from copy import deepcopy

from decisive20.models import EventCard, Force, GameState, Scenario, Zone


def build_initial_game_state(scenario: Scenario) -> GameState:
    return GameState(
        scenario=scenario,
        current_round=1,
        resources=deepcopy(scenario.resources),
        zones={zone.code: deepcopy(zone) for zone in scenario.zones},
        forces={force.name: deepcopy(force) for force in scenario.forces},
        event_deck=[deepcopy(event) for event in scenario.events],
        event_discard=[],
        log=[],
    )


def apply_effects(game_state: GameState, effects: dict) -> list[str]:
    messages: list[str] = []

    for key, value in effects.items():
        if key == "supply":
            game_state.resources.supply = max(0, game_state.resources.supply + int(value))
            messages.append(f"Supply changed by {int(value)}.")
        elif key == "intel":
            game_state.resources.intel = max(0, game_state.resources.intel + int(value))
            messages.append(f"Intel changed by {int(value)}.")
        elif key == "morale":
            next_value = game_state.resources.morale + int(value)
            game_state.resources.morale = min(100, max(0, next_value))
            messages.append(f"Morale changed by {int(value)}.")
        elif key == "political_pressure":
            next_value = game_state.resources.political_pressure + int(value)
            game_state.resources.political_pressure = min(100, max(0, next_value))
            messages.append(f"Political pressure changed by {int(value)}.")
        elif key == "enemy_pressure":
            next_value = game_state.resources.enemy_pressure + int(value)
            game_state.resources.enemy_pressure = max(0, next_value)
            messages.append(f"Enemy pressure changed by {int(value)}.")
        elif key == "zone_defense":
            _apply_zone_defense(game_state, value, messages)
        elif key == "zone_status":
            _apply_zone_status(game_state, value, messages)
        elif key == "force_value":
            _apply_force_value(game_state, value, messages)
        else:
            raise ValueError(f"Unknown effect key: {key}")

    game_state.log.extend(messages)
    return messages


def draw_event(game_state: GameState) -> EventCard:
    if not game_state.event_deck:
        if not game_state.event_discard:
            raise ValueError("No events available to draw")
        game_state.event_deck = game_state.event_discard
        game_state.event_discard = []

    event = game_state.event_deck.pop(0)
    return event


def check_victory(game_state: GameState) -> bool:
    for condition in game_state.scenario.victory_conditions:
        condition_type = condition["type"]
        if condition_type == "survive_rounds":
            if game_state.current_round >= condition["rounds"]:
                game_state.ended = True
                game_state.ending_type = "victory"
                game_state.log.append("Victory: survive_rounds achieved.")
                return True
        elif condition_type == "hold_min_core_zones":
            held = sum(
                1
                for zone_code in condition["core_zones"]
                if game_state.zones[zone_code].status == "friendly"
            )
            if held >= condition["min_zones"]:
                game_state.ended = True
                game_state.ending_type = "victory"
                game_state.log.append("Victory: hold_min_core_zones achieved.")
                return True
        elif condition_type == "enemy_pressure_zero":
            if game_state.resources.enemy_pressure == 0:
                game_state.ended = True
                game_state.ending_type = "victory"
                game_state.log.append("Victory: enemy pressure reduced to zero.")
                return True
        else:
            raise ValueError(f"Unsupported victory condition: {condition_type}")
    return False


def check_failure(game_state: GameState) -> bool:
    for condition in game_state.scenario.failure_conditions:
        condition_type = condition["type"]
        if condition_type == "morale_zero" and game_state.resources.morale == 0:
            return _mark_failure(game_state, "Failure: morale reached zero.")
        if (
            condition_type == "political_pressure_max"
            and game_state.resources.political_pressure >= 100
        ):
            return _mark_failure(game_state, "Failure: political pressure reached maximum.")
        if condition_type == "enemy_controls_zones":
            enemy_zones = sum(
                1 for zone in game_state.zones.values() if zone.status == "enemy_controlled"
            )
            if enemy_zones >= condition["count"]:
                return _mark_failure(game_state, "Failure: enemy controls too many zones.")
        if condition_type == "supply_zero" and game_state.resources.supply == 0:
            return _mark_failure(game_state, "Failure: supply reached zero.")
        if condition_type == "core_zones_lost":
            statuses = [game_state.zones[zone_code].status for zone_code in condition["core_zones"]]
            if all(status != "friendly" for status in statuses):
                return _mark_failure(game_state, "Failure: all listed core zones were lost.")
        if condition_type not in {
            "morale_zero",
            "political_pressure_max",
            "enemy_controls_zones",
            "supply_zero",
            "core_zones_lost",
        }:
            raise ValueError(f"Unsupported failure condition: {condition_type}")
    return False


def advance_round(game_state: GameState) -> None:
    if not game_state.ended:
        game_state.current_round += 1


def _apply_zone_defense(game_state: GameState, changes: dict, messages: list[str]) -> None:
    for zone_code, delta in changes.items():
        zone = _get_zone(game_state, zone_code)
        zone.defense = max(0, zone.defense + int(delta))
        messages.append(f"Zone {zone.code} defense changed by {int(delta)}.")


def _apply_zone_status(game_state: GameState, changes: dict, messages: list[str]) -> None:
    for zone_code, status in changes.items():
        zone = _get_zone(game_state, zone_code)
        zone.status = status
        messages.append(f"Zone {zone.code} status changed to {status}.")


def _apply_force_value(game_state: GameState, changes: dict, messages: list[str]) -> None:
    for force_name, delta in changes.items():
        force = _get_force(game_state, force_name)
        force.value = max(0, force.value + int(delta))
        messages.append(f"Force {force.name} value changed by {int(delta)}.")


def _get_zone(game_state: GameState, zone_code: str) -> Zone:
    try:
        return game_state.zones[zone_code]
    except KeyError as exc:
        raise ValueError(f"Unknown zone code: {zone_code}") from exc


def _get_force(game_state: GameState, force_name: str) -> Force:
    try:
        return game_state.forces[force_name]
    except KeyError as exc:
        raise ValueError(f"Unknown force name: {force_name}") from exc


def _mark_failure(game_state: GameState, message: str) -> bool:
    game_state.ended = True
    game_state.ending_type = "failure"
    game_state.log.append(message)
    return True
