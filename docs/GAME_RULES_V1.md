# Game Rules V1

## Overview

決戰20 is a turn-based decision-pressure wargame. You command the defense of a
contested city across a fixed number of rounds. Each round you respond to a crisis
event, spend Command Points (CP) on strategic actions, and then weather an enemy
assault. Standing still loses — you must actively manage morale, supply, politics,
and your defensive line.

## Round Structure

Each round runs five phases in order:

1. **Upkeep** — gain `cp_per_turn` CP (carried over, capped at `2 × cp_per_turn`),
   pay supply upkeep, and the enemy escalates (`enemy_pressure` rises).
2. **Status** — the current resources and zone map are displayed.
3. **Event** — one event card is drawn; you choose one option. Options may cost CP.
4. **Command phase** — spend remaining CP on standing actions until you enter `done`.
5. **Enemy phase** — the enemy assaults your softest zones (see below).

After each phase, failure conditions are checked first, then victory conditions.

## Command Points (CP) and Standing Actions

- `reinforce <zone>` — cost 1 CP — that zone's defense +2.
- `recon` — cost 1 CP — intel +2.
- `rally` — cost 2 CP — morale +6.
- `counter` — cost 2 CP — spend 2 intel, enemy_pressure −3.
- `done` — end the command phase.

An action only appears when you can afford it (and `counter` needs ≥2 intel).

## Enemy Phase

- Number of assaults = `attacks_base + enemy_pressure // 8` (capped at zone count).
- The enemy targets the **lowest-defense** zones first, breaking ties toward core
  zones. Each zone is assaulted **at most once per round**.
- Assault power = `enemy_pressure // 3 + random(0..4) + attack_power_bonus`.
  - If power > defense: the zone degrades one step
    (friendly → contested → enemy_controlled), defense −1, morale −3, politics +2.
  - Otherwise: the zone holds, defense −1, morale −1.
- A friendly zone therefore takes at least two rounds to fall — enough time to
  reinforce or counterattack.

The run is **seeded** (`--seed`): the same seed and inputs always produce the same
game, but without a seed each playthrough differs.

## Resource Rules

- `morale` and `political_pressure` are clamped to 0..100.
- `supply`, `intel`, `cp`, zone defense, and force value never drop below 0.
- `enemy_pressure` is clamped to a minimum of 0.

## Victory Rules

- `survive_rounds` — reach the required round.
- `hold_min_core_zones` — hold at least N listed core zones (friendly).
- `enemy_pressure_zero` — grind enemy pressure down to 0.

## Failure Rules

- `morale_zero` — morale reaches 0.
- `political_pressure_max` — political pressure reaches 100.
- `enemy_controls_zones` — enemy controls N zones.
- `supply_zero` — supply reaches 0.
- `core_zones_lost` — all listed core zones are no longer friendly.

## Scoring

At the end a score and rank (S/A/B/C/D) are awarded based on rounds survived, zones
held (core zones weighted higher), remaining morale/supply/intel, low political
pressure, enemy pressure reduced, and a win/loss bonus.
