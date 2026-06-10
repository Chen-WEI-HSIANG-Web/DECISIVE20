# Game Rules V1

## Gameplay Rules

- The game starts from a scenario JSON file.
- Each round draws one event card.
- The player chooses one option code from the displayed event.
- The selected option mutates resources, zones, and forces.
- The game ends immediately when any failure condition triggers.
- If no failure condition triggers, victory conditions are checked.

## Resource Rules

- `morale` is clamped between 0 and 100.
- `political_pressure` is clamped between 0 and 100.
- `supply`, `intel`, zone defense, and force value never drop below 0.
- `enemy_pressure` is clamped to a minimum of 0.

## Event Card Rules

- Each event card must have at least two options.
- Option codes must be unique within a card.
- Unsupported effect keys are rejected.
- When the event deck empties, the discard pile is recycled.

## Victory Rules

- `survive_rounds`
- `hold_min_core_zones`
- `enemy_pressure_zero`

## Failure Rules

- `morale_zero`
- `political_pressure_max`
- `enemy_controls_zones`
- `supply_zero`
- `core_zones_lost`
