# Decisive 20 V1 Design

## Product Intent

V1 delivers a playable decision-pressure wargame loop across both terminal and
browser surfaces. The player responds to crisis events, spends Command Points,
deploys limited forces, manages morale/supply/intel/political pressure, and
survives a seeded rule-based enemy that acts back each round.

The design goal is still prototype clarity: deterministic rules, JSON scenarios,
small local persistence, and a shared engine that can be tested without UI
automation.

## Shipped V1 Boundary

- Python CLI play loop
- Headless `GameSession` state machine used by CLI and web API
- JSON-driven scenario setup and validation
- Seeded, reproducible event deck and enemy behavior
- CP economy with event choices and command-phase actions
- Force deployment and garrison-based effective defense
- Intel telegraph for projected enemy targets
- FastAPI backend for game creation, scenario catalogue, state transitions, and
  health checks
- React/Vite browser UI served as committed FastAPI static assets
- SQLite-backed session persistence, including seeded RNG state
- Local automated Python tests with pytest
- Frontend production build with Vite

## Round Loop

1. **Upkeep** - gain CP, pay supply upkeep, escalate enemy pressure.
2. **Status** - render resources, forces, and zone map.
3. **Event** - draw one card; player picks a costed option; effects apply.
4. **Command phase** - spend remaining CP on actions until `done`.
5. **Enemy phase** - seeded assaults on the softest zones.

Failure is checked before victory after state-changing phases. A final score and
rank are computed when the game ends.

## Core Rules

- CP gained each round is capped at twice `cp_per_turn`.
- Event options can modify resources, zone defense/status, force value, and CP.
- Standing command actions:
  - `reinforce <zone>`: spend CP to increase zone defense.
  - `recon`: spend CP to gain intel.
  - `rally`: spend CP to recover morale.
  - `counter`: spend CP and intel to reduce enemy pressure.
- Deployment command:
  - `deploy <force> <zone>` assigns or reassigns a force to a zone.
  - Deployed forces add to effective defense.
  - A garrison can absorb a breach before territory degrades.
- Intel telegraph:
  - Once intel reaches `INTEL_TELEGRAPH_THRESHOLD`, the next enemy targets are
    exposed in the CLI and web snapshot.

## Data Model

- `Force`: named combat value holder and optional assigned zone.
- `ResourceState`: resource values including `cp_per_turn`.
- `Zone`: map zone state, defense, and core flag.
- `EventOption`: selectable response, effects, and CP cost.
- `EventCard`: titled event and options.
- `EnemyConfig` / `UpkeepConfig`: per-round tuning knobs.
- `Scenario`: loaded scenario definition, including win/loss conditions.
- `GameState`: mutable runtime state, including CP, score/rank, event deck,
  discard pile, log, and seeded RNG.
- `GameSession`: explicit phase machine that wraps the engine for CLI and HTTP.

## Architecture

- `constants.py` - status vocabulary, labels, effect/condition whitelists, and
  balance constants.
- `models.py` - dataclasses only.
- `scenario_loader.py` + `validators.py` - parsing and load-time validation;
  invalid effects, zones, costs, and conditions are rejected before play.
- `engine.py` - deterministic rule functions: upkeep, effects, command actions,
  enemy phase, victory/failure, scoring, and target prediction.
- `renderer.py` - CLI presentation only; no rule ownership.
- `game.py` - CLI orchestration using injected `input_func` / `output_func`.
- `session.py` - headless step-driven state machine and JSON snapshot contract.
- `web/app.py` - FastAPI routes, scenario catalogue, validation of web overrides,
  and static frontend serving.
- `web/store.py` - interchangeable in-memory and SQLite game stores.
- `frontend/` - React/Vite UI that consumes only the HTTP API.
- `decisive20/web/static/` - committed production frontend bundle.

## Persistence Design

The default web store is SQLite. It stores pickled `GameSession` blobs keyed by
game id, which preserves the current event, phase, scenario state, and seeded RNG
stream across process restarts.

This is intentionally local-prototype persistence. It is not intended as a stable
cross-version save format, external API contract, or untrusted-data format.

## Web Contract

The web API exposes a server-side game id and returns full state snapshots after
each action. The frontend does not implement game rules; it sends event choices,
commands, and end-command actions, then renders the returned snapshot.

Supported web setup options include scenario file selection and overrides for
validated victory/failure condition lists.

## Validation Strategy

- Python behavior is covered by pytest across CLI, loader, validators, engine,
  session, persistence, victory conditions, and web API.
- Scenario validation is available through `python -m decisive20 validate`.
- Frontend delivery is checked with `npm run build`.
- CI runs the basic regression path: install Python dev dependencies, run
  `pytest`, install frontend dependencies with `npm ci`, and run the Vite build.

## Extensibility Notes

- New effects: add to `SUPPORTED_EFFECT_KEYS`, validator rules, and
  `apply_effects`.
- New command actions: add a `CommandAction`; decide whether it is a standing
  menu action or a dedicated UI action like `deploy`.
- New win/loss types: extend the whitelists in `constants.py`, validator logic,
  engine checks, scenario docs, and frontend setup controls if needed.
- Difficulty is tuned per scenario through `enemy`, `upkeep`, event option
  costs/effects, initial resources, and win/loss conditions.

## Deferred

- Multiplayer and networking beyond the local FastAPI app
- Account/auth support
- Portable save format or migration-aware persistence
- Scenario authoring tools
- Frontend unit/component tests
- Richer AI beyond seeded deterministic target selection
