# Decisive 20 V1 Design

## Product Intent

V1 is a text-only prototype focused on scenario loading, event resolution, and end-condition evaluation. It is not a full simulation and intentionally avoids GUI, persistence, networking, and advanced AI behavior.

## V1 Boundary

- Python CLI only
- Standard-library-first implementation
- JSON-driven scenario setup
- Deterministic event deck recycling
- Local automated tests with pytest

## Game Loop

1. Load scenario JSON.
2. Validate scenario data.
3. Build initial `GameState`.
4. Render current round status.
5. Draw one event card.
6. Collect player option input.
7. Apply effects and record the result.
8. Check failure, then victory.
9. Advance round when the game continues.
10. Render an end-game summary.

## Data Model

- `Force`: named combat value holder
- `ResourceState`: stores resource values including `cp_per_turn`
- `Zone`: map zone state, defense, and core flag
- `EventOption`: selectable player response plus effects
- `EventCard`: titled event and options
- `Scenario`: loaded scenario definition
- `GameState`: mutable runtime state

## Extensibility Notes

- Effect handling is centralized in `engine.py`.
- Scenario parsing and validation stay in `scenario_loader.py` and `validators.py`.
- Rendering is isolated in `renderer.py` so output can change without altering rules.
