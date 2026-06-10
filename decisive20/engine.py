from __future__ import annotations

import random
from copy import deepcopy
from dataclasses import dataclass
from typing import Callable

from decisive20.constants import (
    BOUNDED_RESOURCES,
    DEGRADE_STATUS,
    Ending,
    ZoneStatus,
)
from decisive20.models import EventCard, Force, GameState, Scenario, Zone


def build_initial_game_state(scenario: Scenario, seed: int | None = None) -> GameState:
    rng = random.Random(seed)
    deck = [deepcopy(event) for event in scenario.events]
    rng.shuffle(deck)
    return GameState(
        scenario=scenario,
        current_round=1,
        resources=deepcopy(scenario.resources),
        zones={zone.code: deepcopy(zone) for zone in scenario.zones},
        forces={force.name: deepcopy(force) for force in scenario.forces},
        event_deck=deck,
        event_discard=[],
        cp=0,
        log=[],
        rng=rng,
    )


# --------------------------------------------------------------------------- #
# Upkeep phase
# --------------------------------------------------------------------------- #
def start_turn(game_state: GameState) -> list[str]:
    """Apply per-round upkeep: gain CP, drain supply, escalate the enemy."""
    messages: list[str] = []
    upkeep = game_state.scenario.upkeep
    enemy = game_state.scenario.enemy

    cp_gain = upkeep.cp_per_round
    if cp_gain is None:
        cp_gain = game_state.resources.cp_per_turn
    cp_cap = game_state.resources.cp_per_turn * 2
    game_state.cp = min(cp_cap, game_state.cp + cp_gain)
    messages.append(f"獲得指令點 +{cp_gain}（目前 {game_state.cp}）。")

    if upkeep.supply_per_round:
        before = game_state.resources.supply
        game_state.resources.supply = max(0, before - upkeep.supply_per_round)
        spent = before - game_state.resources.supply
        if spent:
            messages.append(f"後勤消耗：補給 -{spent}（目前 {game_state.resources.supply}）。")

    if game_state.current_round > 1 and enemy.escalation_per_round:
        game_state.resources.enemy_pressure += enemy.escalation_per_round
        messages.append(
            f"戰事升溫：敵軍壓力 +{enemy.escalation_per_round}"
            f"（目前 {game_state.resources.enemy_pressure}）。"
        )

    game_state.log.extend(messages)
    return messages


# --------------------------------------------------------------------------- #
# Effect application
# --------------------------------------------------------------------------- #
def apply_effects(game_state: GameState, effects: dict) -> list[str]:
    messages: list[str] = []

    for key, value in effects.items():
        if key in {"supply", "intel", "cp"}:
            _apply_floor_resource(game_state, key, int(value), messages)
        elif key in {"morale", "political_pressure"}:
            _apply_bounded_resource(game_state, key, int(value), messages)
        elif key == "enemy_pressure":
            next_value = game_state.resources.enemy_pressure + int(value)
            game_state.resources.enemy_pressure = max(0, next_value)
            messages.append(f"敵軍壓力 {_signed(int(value))}（目前 {game_state.resources.enemy_pressure}）。")
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


def _apply_floor_resource(game_state: GameState, key: str, delta: int, messages: list[str]) -> None:
    if key == "cp":
        game_state.cp = max(0, game_state.cp + delta)
        messages.append(f"指令點 {_signed(delta)}（目前 {game_state.cp}）。")
        return
    current = getattr(game_state.resources, key)
    setattr(game_state.resources, key, max(0, current + delta))
    messages.append(f"{_RES_LABELS[key]} {_signed(delta)}（目前 {getattr(game_state.resources, key)}）。")


def _apply_bounded_resource(game_state: GameState, key: str, delta: int, messages: list[str]) -> None:
    current = getattr(game_state.resources, key)
    setattr(game_state.resources, key, min(100, max(0, current + delta)))
    messages.append(f"{_RES_LABELS[key]} {_signed(delta)}（目前 {getattr(game_state.resources, key)}）。")


# --------------------------------------------------------------------------- #
# Event deck
# --------------------------------------------------------------------------- #
def draw_event(game_state: GameState) -> EventCard:
    if not game_state.event_deck:
        if not game_state.event_discard:
            raise ValueError("No events available to draw")
        game_state.event_deck = game_state.event_discard
        game_state.event_discard = []
        game_state.rng.shuffle(game_state.event_deck)

    return game_state.event_deck.pop(0)


# --------------------------------------------------------------------------- #
# Command phase — standing strategic actions
# --------------------------------------------------------------------------- #
@dataclass
class CommandAction:
    key: str
    label: str
    cost: int
    needs_target: bool
    apply: Callable[[GameState, Zone | None], str]
    is_available: Callable[[GameState], bool]


def _cmd_reinforce(game_state: GameState, zone: Zone | None) -> str:
    assert zone is not None
    zone.defense += 2
    return f"增援 {zone.code} {zone.name}：防禦 +2（{zone.defense}）。"


def _cmd_recon(game_state: GameState, _zone: Zone | None) -> str:
    game_state.resources.intel += 2
    return f"偵察行動：情報 +2（{game_state.resources.intel}）。"


def _cmd_rally(game_state: GameState, _zone: Zone | None) -> str:
    game_state.resources.morale = min(100, game_state.resources.morale + 6)
    return f"動員民心：士氣 +6（{game_state.resources.morale}）。"


def _cmd_counter(game_state: GameState, _zone: Zone | None) -> str:
    game_state.resources.intel = max(0, game_state.resources.intel - 2)
    game_state.resources.enemy_pressure = max(0, game_state.resources.enemy_pressure - 3)
    return (
        f"反制作戰：消耗情報 2，敵軍壓力 -3"
        f"（壓力 {game_state.resources.enemy_pressure} / 情報 {game_state.resources.intel}）。"
    )


COMMAND_ACTIONS: dict[str, CommandAction] = {
    "reinforce": CommandAction(
        key="reinforce",
        label="增援防區（指定區域，防禦 +2）",
        cost=1,
        needs_target=True,
        apply=_cmd_reinforce,
        is_available=lambda gs: gs.cp >= 1,
    ),
    "recon": CommandAction(
        key="recon",
        label="偵察（情報 +2）",
        cost=1,
        needs_target=False,
        apply=_cmd_recon,
        is_available=lambda gs: gs.cp >= 1,
    ),
    "rally": CommandAction(
        key="rally",
        label="動員（士氣 +6）",
        cost=2,
        needs_target=False,
        apply=_cmd_rally,
        is_available=lambda gs: gs.cp >= 2,
    ),
    "counter": CommandAction(
        key="counter",
        label="反制（消耗情報 2，敵軍壓力 -3）",
        cost=2,
        needs_target=False,
        apply=_cmd_counter,
        is_available=lambda gs: gs.cp >= 2 and gs.resources.intel >= 2,
    ),
}


def available_commands(game_state: GameState) -> list[CommandAction]:
    return [action for action in COMMAND_ACTIONS.values() if action.is_available(game_state)]


def perform_command(game_state: GameState, action_key: str, target: str | None = None) -> str:
    action = COMMAND_ACTIONS.get(action_key)
    if action is None:
        raise ValueError(f"未知的指令：{action_key}")
    if not action.is_available(game_state):
        raise ValueError(f"指令目前不可用：{action_key}")

    zone: Zone | None = None
    if action.needs_target:
        if target is None:
            raise ValueError(f"指令「{action_key}」需要指定目標防區")
        zone = _get_zone(game_state, target)

    game_state.cp -= action.cost
    message = action.apply(game_state, zone)
    game_state.log.append(message)
    return message


# --------------------------------------------------------------------------- #
# Enemy phase — seeded, rule-based opponent
# --------------------------------------------------------------------------- #
def enemy_phase(game_state: GameState) -> list[str]:
    messages: list[str] = []
    enemy = game_state.scenario.enemy
    pressure = game_state.resources.enemy_pressure

    if pressure <= 0:
        messages.append("敵軍壓力歸零，本回合無攻勢。")
        game_state.log.extend(messages)
        return messages

    candidates = [
        zone for zone in game_state.zones.values() if zone.status in ZoneStatus.ATTACKABLE
    ]
    if not candidates:
        messages.append("敵軍找不到可攻擊的我方防區。")
        game_state.log.extend(messages)
        return messages

    # The enemy presses the softest targets first (core zones break ties), and
    # each zone is assaulted at most once per round so a position takes time to fall.
    attacks = min(enemy.attacks_base + pressure // 8, len(candidates))
    candidates.sort(key=lambda z: (z.defense, 0 if z.core else 1))
    targets = candidates[:attacks]

    messages.append(f"敵軍發動 {attacks} 波攻勢（壓力 {pressure}）：")
    for target in targets:
        power = pressure // 3 + game_state.rng.randint(0, 4) + enemy.attack_power_bonus

        if power > target.defense:
            target.status = DEGRADE_STATUS[target.status]
            target.defense = max(0, target.defense - 1)
            game_state.resources.morale = max(0, game_state.resources.morale - 3)
            game_state.resources.political_pressure = min(
                100, game_state.resources.political_pressure + 2
            )
            messages.append(
                f"  ▼ {target.code} {target.name} 失守（攻擊 {power} > 防禦 {target.defense + 1}），"
                f"轉為「{_status_label(target.status)}」；士氣 -3，政治壓力 +2。"
            )
        else:
            target.defense = max(0, target.defense - 1)
            game_state.resources.morale = max(0, game_state.resources.morale - 1)
            messages.append(
                f"  ✓ {target.code} {target.name} 守住（攻擊 {power} ≤ 防禦 {target.defense + 1}），"
                f"防禦 -1（{target.defense}）；士氣 -1。"
            )

    game_state.log.extend(messages)
    return messages


# --------------------------------------------------------------------------- #
# Win / loss evaluation
# --------------------------------------------------------------------------- #
def check_victory(game_state: GameState) -> bool:
    for condition in game_state.scenario.victory_conditions:
        condition_type = condition["type"]
        if condition_type == "survive_rounds":
            if game_state.current_round >= condition["rounds"]:
                return _mark(game_state, Ending.VICTORY, "勝利：成功堅守至指定回合。")
        elif condition_type == "hold_min_core_zones":
            held = sum(
                1
                for zone_code in condition["core_zones"]
                if game_state.zones[zone_code].status == ZoneStatus.FRIENDLY
            )
            if held >= condition["min_zones"]:
                return _mark(game_state, Ending.VICTORY, "勝利：守住足夠的核心防區。")
        elif condition_type == "enemy_pressure_zero":
            if game_state.resources.enemy_pressure == 0:
                return _mark(game_state, Ending.VICTORY, "勝利：敵軍壓力被壓制歸零。")
        else:
            raise ValueError(f"Unsupported victory condition: {condition_type}")
    return False


def check_failure(game_state: GameState) -> bool:
    for condition in game_state.scenario.failure_conditions:
        condition_type = condition["type"]
        if condition_type == "morale_zero" and game_state.resources.morale == 0:
            return _mark(game_state, Ending.FAILURE, "失敗：士氣崩潰歸零。")
        if (
            condition_type == "political_pressure_max"
            and game_state.resources.political_pressure >= 100
        ):
            return _mark(game_state, Ending.FAILURE, "失敗：政治壓力達到上限。")
        if condition_type == "enemy_controls_zones":
            enemy_zones = sum(
                1
                for zone in game_state.zones.values()
                if zone.status == ZoneStatus.ENEMY_CONTROLLED
            )
            if enemy_zones >= condition["count"]:
                return _mark(game_state, Ending.FAILURE, "失敗：敵軍控制過多防區。")
        if condition_type == "supply_zero" and game_state.resources.supply == 0:
            return _mark(game_state, Ending.FAILURE, "失敗：補給耗盡。")
        if condition_type == "core_zones_lost":
            statuses = [
                game_state.zones[zone_code].status for zone_code in condition["core_zones"]
            ]
            if all(status != ZoneStatus.FRIENDLY for status in statuses):
                return _mark(game_state, Ending.FAILURE, "失敗：所有核心防區皆已失守。")
    return False


def advance_round(game_state: GameState) -> None:
    if not game_state.ended:
        game_state.current_round += 1


# --------------------------------------------------------------------------- #
# Scoring
# --------------------------------------------------------------------------- #
def compute_score(game_state: GameState) -> tuple[int, str]:
    res = game_state.resources
    score = game_state.current_round * 10

    for zone in game_state.zones.values():
        if zone.status == ZoneStatus.FRIENDLY:
            score += 25 if zone.core else 15
        elif zone.status == ZoneStatus.CONTESTED:
            score += 5
        elif zone.status == ZoneStatus.ENEMY_CONTROLLED:
            score -= 15 if zone.core else 8
        elif zone.status == ZoneStatus.DESTROYED:
            score -= 12

    score += res.morale
    score += res.supply * 3
    score += res.intel * 2
    score += (100 - res.political_pressure)
    score += max(0, game_state.scenario.resources.enemy_pressure - res.enemy_pressure) * 4

    if game_state.ending_type == Ending.VICTORY:
        score += 250
    elif game_state.ending_type == Ending.FAILURE:
        score -= 100

    score = max(0, score)
    game_state.score = score
    game_state.rank = _rank_for(score)
    return score, game_state.rank


def _rank_for(score: int) -> str:
    if score >= 650:
        return "S"
    if score >= 500:
        return "A"
    if score >= 350:
        return "B"
    if score >= 200:
        return "C"
    return "D"


# --------------------------------------------------------------------------- #
# Internal helpers
# --------------------------------------------------------------------------- #
_RES_LABELS = {
    "supply": "補給",
    "intel": "情報",
    "morale": "士氣",
    "political_pressure": "政治壓力",
    "enemy_pressure": "敵軍壓力",
    "cp": "指令點",
}


def _signed(value: int) -> str:
    return f"+{value}" if value >= 0 else str(value)


def _status_label(status: str) -> str:
    from decisive20.constants import STATUS_LABELS

    return STATUS_LABELS.get(status, status)


def _apply_zone_defense(game_state: GameState, changes: dict, messages: list[str]) -> None:
    for zone_code, delta in changes.items():
        zone = _get_zone(game_state, zone_code)
        zone.defense = max(0, zone.defense + int(delta))
        messages.append(f"防區 {zone.code} 防禦 {_signed(int(delta))}（{zone.defense}）。")


def _apply_zone_status(game_state: GameState, changes: dict, messages: list[str]) -> None:
    for zone_code, status in changes.items():
        zone = _get_zone(game_state, zone_code)
        zone.status = status
        messages.append(f"防區 {zone.code} 狀態變更為「{_status_label(status)}」。")


def _apply_force_value(game_state: GameState, changes: dict, messages: list[str]) -> None:
    for force_name, delta in changes.items():
        force = _get_force(game_state, force_name)
        force.value = max(0, force.value + int(delta))
        messages.append(f"部隊 {force.name} 戰力 {_signed(int(delta))}（{force.value}）。")


def _get_zone(game_state: GameState, zone_code: str) -> Zone:
    try:
        return game_state.zones[zone_code]
    except KeyError as exc:
        raise ValueError(f"未知的防區代碼：{zone_code}") from exc


def _get_force(game_state: GameState, force_name: str) -> Force:
    try:
        return game_state.forces[force_name]
    except KeyError as exc:
        raise ValueError(f"未知的部隊名稱：{force_name}") from exc


def _mark(game_state: GameState, ending: str, message: str) -> bool:
    game_state.ended = True
    game_state.ending_type = ending
    game_state.log.append(message)
    return True
