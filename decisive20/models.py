from __future__ import annotations

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


@dataclass
class EventCard:
    code: str
    title: str
    description: str
    options: list[EventOption]


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


@dataclass
class GameState:
    scenario: Scenario
    current_round: int
    resources: ResourceState
    zones: dict[str, Zone]
    forces: dict[str, Force]
    event_deck: list[EventCard]
    event_discard: list[EventCard] = field(default_factory=list)
    ended: bool = False
    ending_type: str | None = None
    log: list[str] = field(default_factory=list)
