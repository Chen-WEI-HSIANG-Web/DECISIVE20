# Codex Task｜Initialize 決戰20 V1 CLI Project

You are working on a new project named:

- Chinese Name: 決戰20
- English Codename: Decisive 20
- Version: V1 CLI

The goal is to build a runnable Python CLI prototype for a text-based strategic decision pressure simulation game.

---

## 1. Objective

Create a runnable Python CLI game prototype with the following capabilities:

1. Load scenario initialization from JSON.
2. Run a turn-based event card gameplay loop.
3. Track resource state.
4. Track zone state.
5. Allow player option selection.
6. Resolve selected option effects.
7. Check victory and failure conditions.
8. Produce an end-game summary.
9. Include basic automated tests.

---

## 2. Technical Direction

Use Python standard library as much as possible.

Use:

- argparse for CLI entry.
- dataclasses for models.
- json for scenario loading.
- pytest for tests.

Do not introduce heavy dependencies unless necessary.

---

## 3. Required Project Structure

Create the following structure:

    decisive20/
    ├── README.md
    ├── DESIGN.md
    ├── pyproject.toml
    ├── .gitignore
    ├── decisive20/
    │   ├── __init__.py
    │   ├── __main__.py
    │   ├── cli.py
    │   ├── game.py
    │   ├── models.py
    │   ├── engine.py
    │   ├── renderer.py
    │   ├── scenario_loader.py
    │   └── validators.py
    ├── scenarios/
    │   └── taichung_defense_v1.json
    ├── tests/
    │   ├── test_loader.py
    │   ├── test_engine.py
    │   └── test_victory_conditions.py
    └── docs/
        ├── GAME_RULES_V1.md
        └── SCENARIO_SCHEMA.md

Important:

- __main__.py is required so the game can run with python -m decisive20.
- Keep game rules, rendering, loading, and validation separated.

---

## 4. CLI Commands

Implement the following commands:

    python -m decisive20 start --scenario scenarios/taichung_defense_v1.json
    python -m decisive20 validate --scenario scenarios/taichung_defense_v1.json
    python -m decisive20 demo

The CLI must support:

    python -m decisive20 --help
    python -m decisive20 start --help
    python -m decisive20 validate --help

---

## 5. V1 Gameplay Requirements

The game should follow this flow:

1. Load a scenario JSON file.
2. Validate the scenario.
3. Initialize game state.
4. Start at round 1.
5. Display scenario name, current round, total rounds, resources, and zones.
6. Draw one event card per round.
7. Display the event title, description, and options.
8. Ask the player to input an option code.
9. Apply the selected option effects.
10. Display the result.
11. Check victory and failure conditions.
12. Advance to the next round.
13. End with a battle summary.

---

## 6. Scenario Validation Rules

Validate the following rules:

1. rounds must be between 10 and 30.
2. morale must be between 0 and 100.
3. political_pressure must be between 0 and 100.
4. At least 1 event card must exist.
5. At least 3 zones must exist.
6. Each event card must have at least 2 options.
7. Each option must have an effects object.
8. Zone codes referenced in effects must exist.
9. Force names referenced in effects must exist.
10. Event option codes must be unique within each event card.

---

## 7. Supported Effects in V1

Support only the following effects:

    supply: int
    intel: int
    morale: int
    political_pressure: int
    enemy_pressure: int

    zone_defense:
      zone_code: delta

    zone_status:
      zone_code: new_status

    force_value:
      force_name: delta

Clamp values where appropriate:

| Field | Rule |
|---|---|
| morale | minimum 0, maximum 100 |
| political_pressure | minimum 0, maximum 100 |
| supply | minimum 0 |
| intel | minimum 0 |
| zone defense | minimum 0 |
| force value | minimum 0 |

---

## 8. Zone Status Values

Support the following zone status values in V1:

- friendly
- contested
- enemy_controlled
- cut_off
- destroyed

Display labels may be localized in the renderer.

| Internal Value | Display Label |
|---|---|
| friendly | 我方控制 |
| contested | 爭奪中 |
| enemy_controlled | 敵方控制 |
| cut_off | 被切斷 |
| destroyed | 已破壞 |

---

## 9. Victory Conditions V1

Support the following victory condition types:

- survive_rounds
- hold_min_core_zones
- enemy_pressure_zero

### survive_rounds

The player wins if they survive until the required round.

Example:

    {
      "type": "survive_rounds",
      "rounds": 20
    }

### hold_min_core_zones

The player wins if they hold at least the required number of core zones.

Example:

    {
      "type": "hold_min_core_zones",
      "min_zones": 3,
      "core_zones": ["A", "B", "C", "D"]
    }

### enemy_pressure_zero

The player wins if enemy pressure reaches 0.

Example:

    {
      "type": "enemy_pressure_zero"
    }

---

## 10. Failure Conditions V1

Support the following failure condition types:

- morale_zero
- political_pressure_max
- enemy_controls_zones
- supply_zero
- core_zones_lost

### morale_zero

The player loses if morale reaches 0.

Example:

    {
      "type": "morale_zero"
    }

### political_pressure_max

The player loses if political pressure reaches 100.

Example:

    {
      "type": "political_pressure_max"
    }

### enemy_controls_zones

The player loses if the enemy controls a specified number of zones.

Example:

    {
      "type": "enemy_controls_zones",
      "count": 5
    }

### supply_zero

The player loses if supply reaches 0.

Example:

    {
      "type": "supply_zero"
    }

### core_zones_lost

The player loses if all specified core zones are no longer friendly.

Example:

    {
      "type": "core_zones_lost",
      "core_zones": ["C", "D"]
    }

---

## 11. Required Data Models

Create data models in decisive20/models.py.

Use dataclasses.

Required models:

- Force
- ResourceState
- Zone
- EventOption
- EventCard
- Scenario
- GameState

GameState must include:

- scenario
- current_round
- resources
- zones
- forces
- event_deck
- event_discard
- ended
- ending_type
- log

---

## 12. Engine Requirements

Create decisive20/engine.py.

Required functions:

- apply_effects(game_state, effects)
- draw_event(game_state)
- check_victory(game_state)
- check_failure(game_state)
- advance_round(game_state)

Rules:

- apply_effects must mutate GameState safely.
- Unknown effect keys should raise a clear ValueError.
- Unknown zone codes should raise a clear ValueError.
- Unknown force names should raise a clear ValueError.
- Event deck should recycle discard pile if needed.

---

## 13. Renderer Requirements

Create decisive20/renderer.py.

Renderer responsibilities:

- Display game title.
- Display round status.
- Display resources.
- Display zones.
- Display event card.
- Display player options.
- Display effect results.
- Display end-game summary.

Do not mix renderer logic into engine.py.

---

## 14. Scenario Loader Requirements

Create decisive20/scenario_loader.py.

Responsibilities:

- Load scenario JSON.
- Convert JSON dictionaries into dataclass objects.
- Raise clear errors when required fields are missing.
- Call scenario validation before game start.

---

## 15. Initial Scenario

Create scenarios/taichung_defense_v1.json.

It should include:

- rounds: 20
- resources:
  - cp_per_turn: 3
  - supply: 10
  - intel: 5
  - morale: 70
  - political_pressure: 30
  - enemy_pressure: 10
- at least 4 zones:
  - A 台中港
  - B 清水 / 沙鹿防線
  - C 大肚山高地
  - D 台中市區
- at least 5 event cards.
- Each event card should have 2 to 4 options.

---

## 16. Documentation Requirements

Create README.md with:

- Project description.
- V1 scope.
- Install and run commands.
- CLI examples.
- Development commands.

Create DESIGN.md with:

- Product intent.
- V1 boundary.
- Game loop.
- Data model.
- Extensibility notes.

Create docs/GAME_RULES_V1.md with:

- Gameplay rules.
- Resource rules.
- Event card rules.
- Victory and failure rules.

Create docs/SCENARIO_SCHEMA.md with:

- JSON scenario structure.
- Required fields.
- Supported effect keys.
- Supported condition types.

---

## 17. Testing Requirements

Create tests for:

1. Scenario loading.
2. Scenario validation.
3. Effect application.
4. Victory condition.
5. Failure condition.

At minimum, this command should pass:

    python -m pytest

---

## 18. Scope Control

Do not build:

- GUI
- Web app
- Save/load
- Complex AI opponent
- Real military simulation
- Map rendering
- Multiplayer
- Database

---

## 19. Expected Codex Final Report Format

When finished, report using this format:

    Completed

    Changed Files

    How to Run

    Validation

    Known Limitations

    Recommended Next Step
