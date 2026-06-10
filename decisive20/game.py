from __future__ import annotations

from pathlib import Path
from typing import Callable

from decisive20.constants import Ending
from decisive20.engine import available_commands
from decisive20.renderer import (
    render_command_menu,
    render_effect_results,
    render_endgame_summary,
    render_enemy_phase,
    render_event_card,
    render_message,
    render_round_status,
    render_title,
    render_upkeep,
    render_zones,
)
from decisive20.session import GameSession, Phase


def run_game(
    scenario_path: str | Path,
    seed: int | None = None,
    input_func: Callable[[str], str] = input,
    output_func: Callable[[str], None] = print,
    color: bool = False,
) -> int:
    """Drive a :class:`GameSession` through a terminal play session."""
    session = GameSession.from_path(scenario_path, seed=seed)
    game_state = session.game_state

    output_func(render_title(session.scenario.name))

    upkeep_messages = session.open_round()
    while True:
        output_func(render_upkeep(upkeep_messages))
        if session.phase == Phase.ENDED:
            break

        # Status
        output_func(render_round_status(game_state, color))
        output_func(render_zones(game_state, color))

        # Event
        event = session.current_event
        output_func(render_event_card(event, game_state, color))
        option_code = _prompt_for_option(event, game_state, input_func, output_func)
        messages = session.choose_event_option(option_code)
        output_func(render_effect_results(messages))
        if session.phase == Phase.ENDED:
            break

        # Command phase
        _command_phase(session, input_func, output_func)
        if session.phase == Phase.ENDED:
            break

        # Enemy phase (advances the round, or ends the game)
        output_func(render_enemy_phase(session.end_command(), color))
        if session.phase == Phase.ENDED:
            break

        upkeep_messages = session.open_round()

    output_func(render_endgame_summary(game_state, color))
    return 0 if game_state.ending_type == Ending.VICTORY else 1


def _prompt_for_option(event, game_state, input_func, output_func) -> str:
    options = {option.code.lower(): option for option in event.options}
    while True:
        answer = input_func("選擇選項代碼： ").strip().lower()
        selected = options.get(answer)
        if selected is None:
            output_func(render_message("無效的選項代碼，請重試。"))
            continue
        if game_state.cp < selected.cost:
            output_func(render_message(f"指令點不足（需 {selected.cost}，現有 {game_state.cp}）。"))
            continue
        return selected.code


def _command_phase(session: GameSession, input_func, output_func) -> None:
    game_state = session.game_state
    while session.phase == Phase.COMMAND:
        actions = available_commands(game_state)
        if not actions:
            break
        output_func(render_command_menu(actions, game_state))
        raw = input_func("指令> ").strip()
        if not raw:
            continue
        parts = raw.split()
        verb = parts[0].lower()
        if verb in {"done", "pass", "skip", "end"}:
            break

        action = next((a for a in actions if a.key == verb), None)
        if action is None:
            output_func(render_message("無效或不可用的指令。"))
            continue

        target = parts[1].upper() if len(parts) > 1 else None
        if action.needs_target and target is None:
            output_func(render_message(f"指令 '{verb}' 需要指定區域，例如：{verb} A"))
            continue
        try:
            message = session.command(verb, target)
        except ValueError as exc:
            output_func(render_message(str(exc)))
            continue
        output_func(render_message(message))
