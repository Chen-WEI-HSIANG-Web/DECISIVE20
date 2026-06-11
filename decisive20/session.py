from __future__ import annotations

"""Headless, step-driven game session.

`GameSession` wraps the pure rule functions in :mod:`decisive20.engine` into an
explicit state machine that can be paused between player decisions. The CLI
drives it turn by turn, and a future web backend can drive the same primitives
over HTTP — no rule logic lives here, only sequencing.

Round flow (each method advances the machine and returns the messages it
produced, for the caller to render):

    open_round()           upkeep + draw event   → phase EVENT  (or ENDED)
    choose_event_option()  resolve the event     → phase COMMAND (or ENDED)
    command() * N          spend Command Points   (stays in COMMAND)
    end_command()          enemy phase + advance → phase SETUP  (or ENDED)
"""

from enum import Enum
from pathlib import Path
from typing import Union

from decisive20.constants import INTEL_TELEGRAPH_THRESHOLD, Ending
from decisive20.engine import (
    COMMAND_ACTIONS,
    advance_round,
    apply_effects,
    available_commands,
    build_initial_game_state,
    check_failure,
    check_victory,
    compute_score,
    draw_event,
    enemy_phase,
    perform_command,
    predict_enemy_targets,
    start_turn,
)
from decisive20.models import EventCard, GameState, Scenario
from decisive20.scenario_loader import load_scenario


class Phase(str, Enum):
    SETUP = "setup"      # constructed, or between rounds — ready for open_round()
    EVENT = "event"      # an event is presented — awaiting choose_event_option()
    COMMAND = "command"  # command phase — awaiting command() / end_command()
    ENDED = "ended"      # game over — read score/rank/log


class GameSession:
    def __init__(self, scenario: Scenario, seed: int | None = None) -> None:
        self.game_state: GameState = build_initial_game_state(scenario, seed=seed)
        self.phase: Phase = Phase.SETUP
        self.current_event: EventCard | None = None
        self.upkeep_messages: list[str] = []

    @classmethod
    def from_path(cls, scenario_path: Union[str, Path], seed: int | None = None) -> "GameSession":
        return cls(load_scenario(scenario_path), seed=seed)

    @property
    def scenario(self) -> Scenario:
        return self.game_state.scenario

    @property
    def ended(self) -> bool:
        return self.phase == Phase.ENDED

    # ------------------------------------------------------------------ #
    # State machine transitions
    # ------------------------------------------------------------------ #
    def open_round(self) -> list[str]:
        """Run upkeep and draw the round's event. → EVENT (or ENDED)."""
        if self.phase != Phase.SETUP:
            raise ValueError("目前無法開始新回合")
        gs = self.game_state
        self.upkeep_messages = start_turn(gs)
        if self._resolve():
            self.current_event = None
            return self.upkeep_messages
        self.current_event = draw_event(gs)
        self.phase = Phase.EVENT
        return self.upkeep_messages

    def choose_event_option(self, option_code: str) -> list[str]:
        """Apply the chosen event option's effects. → COMMAND (or ENDED)."""
        if self.phase != Phase.EVENT or self.current_event is None:
            raise ValueError("目前並非事件選擇階段")

        options = {option.code.lower(): option for option in self.current_event.options}
        option = options.get(option_code.strip().lower())
        if option is None:
            raise ValueError("無效的選項代碼")

        gs = self.game_state
        if gs.cp < option.cost:
            raise ValueError(f"指令點不足（需 {option.cost}，現有 {gs.cp}）")

        messages = apply_effects(gs, option.effects)
        gs.cp -= option.cost
        gs.event_discard.append(self.current_event)
        self.current_event = None
        if self._resolve():
            return messages
        self.phase = Phase.COMMAND
        return messages

    def command(
        self, action_key: str, target: str | None = None, force: str | None = None
    ) -> str:
        """Perform one command action. Stays in COMMAND (or ENDED)."""
        if self.phase != Phase.COMMAND:
            raise ValueError("目前並非指揮階段")
        message = perform_command(self.game_state, action_key, target, force)
        self._resolve()
        return message

    def end_command(self) -> list[str]:
        """Run the enemy phase and advance the round. → SETUP (or ENDED)."""
        if self.phase != Phase.COMMAND:
            raise ValueError("目前並非指揮階段")
        gs = self.game_state
        messages = enemy_phase(gs)
        if self._resolve():
            return messages
        if gs.current_round >= self.scenario.rounds:
            # Final round played out — settle victory / incomplete and stop.
            self._finalize()
            return messages
        advance_round(gs)
        self.phase = Phase.SETUP
        return messages

    # ------------------------------------------------------------------ #
    # Web-facing snapshot — the serialization bridge for a future backend.
    # ------------------------------------------------------------------ #
    def snapshot(self) -> dict:
        gs = self.game_state
        res = gs.resources
        event = None
        if self.current_event is not None:
            event = {
                "code": self.current_event.code,
                "title": self.current_event.title,
                "description": self.current_event.description,
                "options": [
                    {
                        "code": option.code,
                        "text": option.text,
                        "cost": option.cost,
                        "affordable": gs.cp >= option.cost,
                        "effects": option.effects,
                    }
                    for option in self.current_event.options
                ],
            }

        # Intel telegraph: once intel clears the threshold the player can see
        # which zones the enemy is lined up to hit this round.
        telegraph_visible = gs.resources.intel >= INTEL_TELEGRAPH_THRESHOLD
        predicted_attacks = predict_enemy_targets(gs) if telegraph_visible else []

        deploy_action = COMMAND_ACTIONS["deploy"]
        can_deploy = self.phase == Phase.COMMAND and deploy_action.is_available(gs)
        return {
            "scenario_name": self.scenario.name,
            "round": gs.current_round,
            "total_rounds": self.scenario.rounds,
            "phase": self.phase.value,
            "cp": gs.cp,
            "resources": {
                "supply": res.supply,
                "intel": res.intel,
                "morale": res.morale,
                "political_pressure": res.political_pressure,
                "enemy_pressure": res.enemy_pressure,
            },
            "zones": [
                {
                    "code": zone.code,
                    "name": zone.name,
                    "defense": zone.defense,
                    "status": zone.status,
                    "core": zone.core,
                }
                for zone in gs.zones.values()
            ],
            "forces": [
                {
                    "name": force.name,
                    "value": force.value,
                    "assigned_zone": force.assigned_zone,
                }
                for force in gs.forces.values()
            ],
            "telegraph_visible": telegraph_visible,
            "telegraph_threshold": INTEL_TELEGRAPH_THRESHOLD,
            "predicted_attacks": predicted_attacks,
            "deploy_cost": deploy_action.cost,
            "can_deploy": can_deploy,
            "event": event,
            "available_commands": [
                {
                    "key": action.key,
                    "label": action.label,
                    "cost": action.cost,
                    "needs_target": action.needs_target,
                }
                for action in available_commands(gs)
            ],
            "ended": gs.ended,
            "ending_type": gs.ending_type,
            "score": gs.score,
            "rank": gs.rank,
            "log": list(gs.log),
        }

    # ------------------------------------------------------------------ #
    # Internal helpers
    # ------------------------------------------------------------------ #
    def _resolve(self) -> bool:
        """Check failure then victory; finalize and stop if the game ended."""
        if check_failure(self.game_state) or check_victory(self.game_state):
            self._finalize()
            return True
        return False

    def _finalize(self) -> None:
        gs = self.game_state
        if not gs.ended:
            gs.ended = True
            gs.ending_type = Ending.INCOMPLETE
            gs.log.append("遊戲結束，未觸發任何勝負條件。")
        compute_score(gs)
        self.phase = Phase.ENDED
