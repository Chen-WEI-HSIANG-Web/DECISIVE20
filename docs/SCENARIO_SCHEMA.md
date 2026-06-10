# Scenario Schema

## Top-Level Structure

```json
{
  "name": "Scenario Name",
  "rounds": 20,
  "resources": {},
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
