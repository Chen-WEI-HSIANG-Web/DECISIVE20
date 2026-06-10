# Scenario Schema

## Top-Level Structure

```json
{
  "name": "Scenario Name",
  "rounds": 20,
  "resources": {},
  "enemy": {},
  "upkeep": {},
  "forces": [],
  "zones": [],
  "events": [],
  "victory_conditions": [],
  "failure_conditions": []
}
```

## Required Fields

- `name`
- `rounds`
- `resources`
- `forces`
- `zones`
- `events`
- `victory_conditions`
- `failure_conditions`

## Optional Fields

- `enemy` — enemy phase tuning:
  - `escalation_per_round` (default 1) — enemy_pressure gained each round after the first.
  - `attacks_base` (default 1) — baseline assaults per round.
  - `attack_power_bonus` (default 0) — flat modifier on every assault.
- `upkeep` — per-round bookkeeping:
  - `supply_per_round` (default 1) — supply consumed each round.
  - `cp_per_round` (default `null` → uses `cp_per_turn`) — CP gained each round.

## Event Option Fields

- `code`, `text`, `effects` (required)
- `cost` (default 0) — Command Points required to choose the option.

## Resource Fields

- `cp_per_turn`
- `supply`
- `intel`
- `morale`
- `political_pressure`
- `enemy_pressure`

## Supported Effect Keys

- `supply`
- `intel`
- `morale`
- `political_pressure`
- `enemy_pressure`
- `cp`
- `zone_defense`
- `zone_status`
- `force_value`

## Zone Effect Format

```json
{
  "zone_defense": {
    "A": 1,
    "B": -2
  },
  "zone_status": {
    "C": "contested"
  }
}
```

## Force Effect Format

```json
{
  "force_value": {
    "reserve_brigade": 2
  }
}
```

## Supported Condition Types

- Victory: `survive_rounds`, `hold_min_core_zones`, `enemy_pressure_zero`
- Failure: `morale_zero`, `political_pressure_max`, `enemy_controls_zones`, `supply_zero`, `core_zones_lost`
