# Decisive 20

Decisive 20 is a Python CLI prototype for a turn-based strategic decision pressure simulation game.

## V1 Scope

- Load a scenario from JSON
- Validate the scenario before play
- Run a round-based event loop
- Track resources, zones, and forces
- Resolve event option effects
- Check victory and failure conditions
- Print an end-game summary

## Install and Run

```bash
python -m venv .venv
.venv\Scripts\activate
python -m pip install -e .[dev]
```

## CLI Examples

```bash
python -m decisive20 --help
python -m decisive20 start --scenario scenarios/taichung_defense_v1.json
python -m decisive20 validate --scenario scenarios/taichung_defense_v1.json
python -m decisive20 demo
```

## Development Commands

```bash
python -m pytest
python -m decisive20 validate --scenario scenarios/taichung_defense_v1.json
```
