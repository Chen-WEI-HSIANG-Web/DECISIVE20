from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Force:
    name: str
    value: int


@dataclass
class ResourceState:
    cp_per_turn: int
    supply: int
    intel: int
    morale: int
    political_pressure: int
    enemy_pressure: int


@dataclass
class Zone:
    code: str
    name: str
    defense: int
    status: str
    core: bool = False


@dataclass
class EventOption:
    code: str
    text: str
    effects: dict[str, Any]
    cost: int = 0  # Command Points required to choose this option.


@dataclass
class EventCard:
    code: str
    title: str
    description: str
    options: list[EventOption]


@dataclass
class EnemyConfig:
    """Drives the seeded enemy phase."""

    escalation_per_round: int = 1   # enemy_pressure gained each round after the first.
    attacks_base: int = 1           # baseline number of assaults per round.
    attack_power_bonus: int = 0     # flat modifier added to every assault roll.


@dataclass
class UpkeepConfig:
    """Per-round bookkeeping applied during the upkeep phase."""

    supply_per_round: int = 1       # supply consumed each round.
    cp_per_round: int | None = None  # CP gained each round; falls back to cp_per_turn.


@dataclass
class Scenario:
    name: str
    rounds: int
    resources: ResourceState
    forces: list[Force]
    zones: list[Zone]
    events: list[EventCard]
    victory_conditions: list[dict[str, Any]]
    failure_conditions: list[dict[str, Any]]
    enemy: EnemyConfig = field(default_factory=EnemyConfig)
    upkeep: UpkeepConfig = field(default_factory=UpkeepConfig)


@dataclass
class GameState:
    scenario: Scenario
    current_round: int
    resources: ResourceState
    zones: dict[str, Zone]
    forces: dict[str, Force]
    event_deck: list[EventCard]
    event_discard: list[EventCard] = field(default_factory=list)
    cp: int = 0
    ended: bool = False
    ending_type: str | None = None
    score: int = 0
    rank: str = "-"
    log: list[str] = field(default_factory=list)
    rng: random.Random = field(default_factory=random.Random)
