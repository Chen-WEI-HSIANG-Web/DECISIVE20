from __future__ import annotations

from pathlib import Path
from typing import Callable

from decisive20.engine import (
    advance_round,
    apply_effects,
    build_initial_game_state,
    check_failure,
    check_victory,
    draw_event,
)
from decisive20.renderer import (
    render_effect_results,
    render_endgame_summary,
    render_event_card,
    render_round_status,
    render_title,
    render_zones,
)
from decisive20.scenario_loader import load_scenario


def run_game(
    scenario_path: str | Path,
    input_func: Callable[[str], str] = input,
    output_func: Callable[[str], None] = print,
) -> int:
    scenario = load_scenario(scenario_path)
    game_state = build_initial_game_state(scenario)

    output_func(render_title(scenario.name))

    while not game_state.ended and game_state.current_round <= scenario.rounds:
        output_func(render_round_status(game_state))
        output_func(render_zones(game_state))

        event = draw_event(game_state)
        output_func(render_event_card(event))
        chosen_option = _prompt_for_option(event, input_func, output_func)

        messages = apply_effects(game_state, chosen_option.effects)
        game_state.event_discard.append(event)
        output_func(render_effect_results(messages))

        if check_failure(game_state):
            break

        if check_victory(game_state):
            break

        if game_state.current_round >= scenario.rounds:
            break

        advance_round(game_state)

    if not game_state.ended:
        check_failure(game_state)
    if not game_state.ended:
        check_victory(game_state)
    if not game_state.ended:
        game_state.ended = True
        game_state.ending_type = "incomplete"
        game_state.log.append("Game ended without a configured victory or failure trigger.")

    output_func(render_endgame_summary(game_state))
    return 0 if game_state.ending_type == "victory" else 1


def _prompt_for_option(event, input_func, output_func):
    options = {option.code.lower(): option for option in event.options}
    while True:
        answer = input_func("Choose option: ").strip().lower()
        selected = options.get(answer)
        if selected is not None:
            return selected
        output_func("Invalid option code. Try again.")
