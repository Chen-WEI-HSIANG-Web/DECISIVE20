# Game Rules V1

## Overview

決戰20 is a turn-based decision-pressure wargame. You command the defense of a
contested city across a fixed number of rounds. Each round you respond to a
crisis event, spend Command Points (CP), deploy forces, and then weather an enemy
assault. Standing still loses: you must actively manage morale, supply, politics,
intel, and the defensive line.

The same rules drive the CLI and web UI through the shared `GameSession` state
machine.

## Round Structure

Each round runs five phases in order:

1. **Upkeep** - gain CP, pay supply upkeep, and escalate enemy pressure after the
   first round.
2. **Status** - display resources, forces, and zone map.
3. **Event** - draw one event card; choose one option. Options may cost CP.
4. **Command phase** - spend remaining CP on actions until `done`.
5. **Enemy phase** - the enemy assaults projected soft targets.

After state-changing phases, failure conditions are checked first, then victory
conditions.

## Command Points (CP)

- CP gain defaults to `cp_per_turn`, unless `upkeep.cp_per_round` overrides it.
- Carried CP is capped at `2 * cp_per_turn`.
- Event options can cost CP and can also add or remove CP through effects.
- Commands only appear or succeed when the player can afford them.

## Command Actions

- `reinforce <zone>` - cost 1 CP; target zone defense +2.
- `recon` - cost 1 CP; intel +2.
- `rally` - cost 2 CP; morale +6.
- `counter` - cost 2 CP and requires at least 2 intel; intel -2 and
  enemy_pressure -3.
- `deploy <force> <zone>` - cost 1 CP; assign or reassign a force to a zone.
- `done` - end the command phase.

In the web UI, deployment is exposed through force/zone selection rather than the
standing command menu, but it uses the same rule engine action.

## Forces and Effective Defense

Forces have a combat value and may be assigned to one zone.

- A deployed force adds its value to that zone's effective defense.
- Enemy targeting uses effective defense, not only printed zone defense.
- If an assault beats effective defense and a garrison is present, the strongest
  garrison absorbs the breach before the zone degrades.
- A force that absorbs a breach loses value. If its value reaches 0, it is
  removed from its zone.

## Intel Telegraph

If intel reaches `INTEL_TELEGRAPH_THRESHOLD` (currently 4), the player can see
which zones the enemy is projected to strike next.

- `recon` raises intel and can reveal the telegraph.
- `counter` spends intel and can hide the telegraph again.
- Prediction is deterministic from the current board: it does not consume random
  rolls and does not change the game state.

## Enemy Phase

- Number of assaults = `attacks_base + enemy_pressure // 8`, capped at the count
  of attackable zones.
- Attackable zones are friendly, contested, or cut off.
- The enemy targets the lowest effective-defense zones first, with core zones
  used as an earlier tie-breaker.
- Each zone is assaulted at most once per round.
- Assault power = `enemy_pressure // 3 + random(0..4) + attack_power_bonus`.
- If power is greater than effective defense:
  - A garrison absorbs the breach if present.
  - Otherwise, the zone degrades one step:
    `friendly -> contested -> enemy_controlled`.
  - Morale falls and political pressure rises.
- If power does not beat effective defense, the zone holds but defense and morale
  still take light damage.

The run is seeded with `--seed` or API `seed`: the same seed and same choices
produce the same game. Without a seed, each run differs.

## Resource Rules

- `morale` and `political_pressure` are clamped to 0..100.
- `supply`, `intel`, `cp`, zone defense, and force value never drop below 0.
- `enemy_pressure` is clamped to a minimum of 0.

## Victory Rules

Supported victory condition types:

- `survive_rounds` - reach the required round.
- `hold_min_core_zones` - hold at least N listed core zones as friendly.
- `enemy_pressure_zero` - reduce enemy pressure to 0.

## Failure Rules

Supported failure condition types:

- `morale_zero` - morale reaches 0.
- `political_pressure_max` - political pressure reaches 100.
- `enemy_controls_zones` - enemy controls at least N zones.
- `supply_zero` - supply reaches 0.
- `core_zones_lost` - all listed core zones are no longer friendly.

## Scenario Selection and Condition Overrides

The CLI starts from a scenario JSON file. The web API and UI can list available
scenario files and create a game from a selected scenario.

When creating a web game, supported victory and failure condition lists may be
overridden. Overrides are validated through the same scenario validator before
the game starts.

## Scoring

At the end, the game computes score and rank (S/A/B/C/D) from:

- rounds survived
- friendly and contested zones, with core zones weighted higher
- morale, supply, and intel remaining
- lower political pressure
- enemy pressure reduced from the scenario start
- victory bonus or failure penalty
