from __future__ import annotations

from decisive20.constants import STATUS_COLORS, STATUS_LABELS, Ending, ZoneStatus
from decisive20.engine import CommandAction
from decisive20.models import EventCard, GameState, Zone

_WIDTH = 60


def _color(text: str, code: str, enabled: bool) -> str:
    if not enabled:
        return text
    return f"\033[{code}m{text}\033[0m"


def _bar(value: int, maximum: int, width: int = 12) -> str:
    maximum = max(1, maximum)
    filled = max(0, min(width, round(value / maximum * width)))
    return "[" + "#" * filled + "-" * (width - filled) + "]"


def _banner(text: str) -> str:
    pad = max(0, _WIDTH - len(text) - 4)
    left = pad // 2
    right = pad - left
    return "─" * left + f"  {text}  " + "─" * right


def render_title(scenario_name: str) -> str:
    line = "═" * _WIDTH
    return f"{line}\n  決戰20  DECISIVE 20 — {scenario_name}\n{line}"


def render_round_status(game_state: GameState, color: bool = False) -> str:
    res = game_state.resources
    lines = [
        _banner(f"第 {game_state.current_round} / {game_state.scenario.rounds} 回合"),
        f"  指令點 CP : {game_state.cp}",
        f"  補給 Supply  {_bar(res.supply, 20)} {res.supply}",
        f"  情報 Intel   {_bar(res.intel, 20)} {res.intel}",
        f"  士氣 Morale  {_bar(res.morale, 100)} {res.morale}/100",
        f"  政治壓力     {_bar(res.political_pressure, 100)} {res.political_pressure}/100",
        f"  敵軍壓力     {_bar(res.enemy_pressure, 40)} {res.enemy_pressure}",
    ]
    return "\n".join(lines)


def render_zones(game_state: GameState, color: bool = False) -> str:
    lines = ["  防區地圖："]
    for zone in game_state.zones.values():
        lines.append("  " + _format_zone(zone, color))
    return "\n".join(lines)


def render_upkeep(messages: list[str]) -> str:
    return "\n".join(f"  · {message}" for message in messages)


def render_event_card(event: EventCard, game_state: GameState, color: bool = False) -> str:
    lines = [
        _banner("事件"),
        _color(f"  〔{event.code}〕{event.title}", "96", color),
        f"  {event.description}",
        "  選項：",
    ]
    for option in event.options:
        cost_tag = f"（CP {option.cost}）" if option.cost else "（免費）"
        affordable = game_state.cp >= option.cost
        marker = "  " if affordable else "✗ "
        text = f"  {marker}{option.code}. {option.text} {cost_tag}"
        lines.append(text if affordable else _color(text, "90", color))
    return "\n".join(lines)


def render_command_menu(actions: list[CommandAction], game_state: GameState) -> str:
    lines = [_banner("指揮階段"), f"  可用指令點 CP：{game_state.cp}"]
    if not actions:
        lines.append("  （無可執行指令）")
    for action in actions:
        lines.append(f"  · {action.key} — {action.label}（CP {action.cost}）")
    lines.append("  · done — 結束指揮階段")
    lines.append("  指令格式：reinforce A ｜ recon ｜ rally ｜ counter ｜ done")
    return "\n".join(lines)


def render_message(message: str) -> str:
    return f"  → {message}"


def render_effect_results(messages: list[str]) -> str:
    if not messages:
        return "  （無變化）"
    return "\n".join(f"  → {message}" for message in messages)


def render_enemy_phase(messages: list[str], color: bool = False) -> str:
    header = _color(_banner("敵軍行動"), "91", color)
    body = "\n".join(f"  {message}" for message in messages)
    return f"{header}\n{body}"


def render_endgame_summary(game_state: GameState, color: bool = False) -> str:
    result_map = {
        Ending.VICTORY: ("勝利 VICTORY", "92"),
        Ending.FAILURE: ("失敗 DEFEAT", "91"),
        Ending.INCOMPLETE: ("未分勝負 INCOMPLETE", "93"),
    }
    label, code = result_map.get(game_state.ending_type, ("未知", "0"))
    lines = [
        "═" * _WIDTH,
        _banner("戰役結算"),
        f"  結果：{_color(label, code, color)}",
        f"  存活回合：{game_state.current_round} / {game_state.scenario.rounds}",
        f"  最終評分：{game_state.score}  評級：{_color(game_state.rank, '96', color)}",
        "",
        render_round_status(game_state, color),
        render_zones(game_state, color),
        "",
        "  戰況紀錄：",
    ]
    lines.extend(f"    - {entry}" for entry in game_state.log)
    lines.append("═" * _WIDTH)
    return "\n".join(lines)


def _format_zone(zone: Zone, color: bool = False) -> str:
    label = STATUS_LABELS.get(zone.status, zone.status)
    label = _color(label, STATUS_COLORS.get(zone.status, "0"), color)
    core_flag = " ★核心" if zone.core else ""
    defense_bar = _bar(zone.defense, 10, width=8)
    return f"{zone.code} {zone.name:<10} 防禦 {defense_bar} {zone.defense:<2} 狀態 {label}{core_flag}"
