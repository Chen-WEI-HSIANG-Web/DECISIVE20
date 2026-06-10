# Decisive 20 V1 Design

## Product Intent

V1 is a text-only prototype that delivers a real, playable decision-pressure loop:
scenario loading, a CP-driven command economy, a seeded enemy opponent, and
end-condition + score evaluation. It intentionally avoids GUI, persistence,
networking, and complex AI, but it is a *game* — choices have costs, the world acts
back, and outcomes are scored.

## V1 Boundary

- Python CLI only
- Standard-library-first implementation (`argparse`, `dataclasses`, `json`, `random`)
- JSON-driven scenario setup
- Seeded, reproducible event deck and enemy behavior
- Local automated tests with pytest

## Round Loop (five phases)

1. **Upkeep** — gain CP, pay supply upkeep, escalate enemy pressure.
2. **Status** — render resources and the zone map.
3. **Event** — draw one card; player picks a (possibly costed) option; apply effects.
4. **Command phase** — spend remaining CP on standing actions until `done`.
5. **Enemy phase** — seeded assaults on the softest zones.

Failure is checked before victory after each phase. A final score and rank are
computed at the end.

## Data Model

- `Force`: named combat value holder
- `ResourceState`: resource values including `cp_per_turn`
- `Zone`: map zone state, defense, and core flag
- `EventOption`: selectable response, its `effects`, and its CP `cost`
- `EventCard`: titled event and options
- `EnemyConfig` / `UpkeepConfig`: per-round tuning knobs
- `Scenario`: loaded scenario definition
- `GameState`: mutable runtime state (incl. `cp`, `score`, `rank`, seeded `rng`)

## Architecture

- `constants.py` — status vocabulary, labels, effect/condition whitelists.
- `models.py` — dataclasses only.
- `scenario_loader.py` + `validators.py` — parsing and load-time validation;
  invalid conditions/zones/costs are rejected before play, not at runtime.
- `engine.py` — all rules: upkeep, effects, command actions, enemy phase, win/loss,
  scoring. Pure and deterministic given a seed.
- `renderer.py` — all presentation (bars, panels, banners, color). No rules.
- `game.py` — orchestrates the phases and player I/O via injected
  `input_func` / `output_func` (which makes the whole loop unit-testable).

## Extensibility Notes

- New effects: add to `SUPPORTED_EFFECT_KEYS` and handle in `apply_effects`.
- New standing actions: add a `CommandAction` to `COMMAND_ACTIONS`.
- New win/loss types: extend the whitelists in `constants.py`, the validator, and
  the corresponding check in `engine.py`.
- Difficulty is tuned per scenario via `enemy` / `upkeep` / option `cost`.

## Deferred (post-V1)

GUI, save/load, networking/multiplayer, smarter AI, map rendering, content tooling.
