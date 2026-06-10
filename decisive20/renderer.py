from __future__ import annotations

from decisive20.models import EventCard, GameState, Zone

STATUS_LABELS = {
    "friendly": "Friendly",
    "contested": "Contested",
    "enemy_controlled": "Enemy Controlled",
    "cut_off": "Cut Off",
    "destroyed": "Destroyed",
}


def render_title(scenario_name: str) -> str:
    return f"=== Decisive 20: {scenario_name} ==="


def render_round_status(game_state: GameState) -> str:
    return (
        f"Round {game_state.current_round}/{game_state.scenario.rounds}\n"
        f"Supply={game_state.resources.supply} "
        f"Intel={game_state.resources.intel} "
        f"Morale={game_state.resources.morale} "
        f"PoliticalPressure={game_state.resources.political_pressure} "
        f"EnemyPressure={game_state.resources.enemy_pressure}"
    )


def render_zones(game_state: GameState) -> str:
    lines = ["Zones:"]
    for zone in game_state.zones.values():
        lines.append(_format_zone(zone))
    return "\n".join(lines)


def render_event_card(event: EventCard) -> str:
    lines = [f"Event {event.code}: {event.title}", event.description, "Options:"]
    for option in event.options:
        lines.append(f"  {option.code} - {option.text}")
    return "\n".join(lines)


def render_effect_results(messages: list[str]) -> str:
    if not messages:
        return "No changes applied."
    return "\n".join(f"- {message}" for message in messages)


def render_endgame_summary(game_state: GameState) -> str:
    result = game_state.ending_type or "unknown"
    lines = [
        "=== End Game Summary ===",
        f"Result: {result}",
        f"Final round: {game_state.current_round}",
        render_round_status(game_state),
        render_zones(game_state),
        "Log:",
    ]
    lines.extend(f"- {entry}" for entry in game_state.log)
    return "\n".join(lines)


def _format_zone(zone: Zone) -> str:
    label = STATUS_LABELS.get(zone.status, zone.status)
    core_flag = " core" if zone.core else ""
    return f"- {zone.code} {zone.name}: defense={zone.defense}, status={label}{core_flag}"
