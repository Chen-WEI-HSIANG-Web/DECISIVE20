# 決戰20 Decisive 20

決戰20 is a Python CLI prototype for a turn-based **strategic decision-pressure**
wargame. You command a city's defense over a fixed number of rounds, spending
Command Points on strategic actions and weathering a seeded, rule-based enemy that
escalates over time. Passive play loses; active management wins.

## V1 Scope

- Load and validate a scenario from JSON
- Five-phase round loop: upkeep → status → event → command → enemy
- Command Point economy with costed event options and standing actions
  (reinforce / recon / rally / counter)
- A seeded enemy that assaults your weakest zones each round
- Resource, zone, and force tracking with victory/failure evaluation
- End-game score and rank (S/A/B/C/D)
- Reproducible runs via `--seed`

## Install and Run

```bash
python -m venv .venv
.venv\Scripts\activate
python -m pip install -e .[dev]
```

## CLI Examples

```bash
python -m decisive20 --help
python -m decisive20 demo
python -m decisive20 demo --seed 7
python -m decisive20 start --scenario scenarios/taichung_defense_v1.json --seed 42
python -m decisive20 validate --scenario scenarios/taichung_defense_v1.json
```

Use `--no-color` to disable ANSI colors (also auto-disabled when output is piped or
`NO_COLOR` is set). On legacy Windows consoles the CLI forces UTF-8 output so the
box-drawing and Chinese characters render correctly.

## How to Play

Each round you:

1. Read the crisis **event** and pick an option (some cost Command Points).
2. In the **command phase**, type actions to spend remaining CP:
   `reinforce A`, `recon`, `rally`, `counter`, then `done`.
3. Survive the **enemy phase**, which attacks your softest zones.

See [docs/GAME_RULES_V1.md](docs/GAME_RULES_V1.md) for full rules and
[docs/SCENARIO_SCHEMA.md](docs/SCENARIO_SCHEMA.md) for authoring scenarios.

## Web Backend (FastAPI)

A headless `GameSession` state machine (`decisive20/session.py`) drives both the
CLI and an HTTP API, so the rule engine is shared and never duplicated.

```bash
python -m pip install -e .[web]
python -m uvicorn decisive20.web:app --reload --port 8000
```

API (all under `/api`):

| Method & path | Purpose |
| --- | --- |
| `POST /api/games` | Create a game (`{"seed": 7}` optional), returns `game_id` + state |
| `GET /api/games/{id}` | Current state snapshot |
| `POST /api/games/{id}/event` | Resolve the event (`{"option": "A"}`) |
| `POST /api/games/{id}/command` | Run a command (`{"action": "reinforce", "target": "A"}`) |
| `POST /api/games/{id}/end-command` | Enemy phase, then open the next round |

Each response is the session `snapshot()` (round, phase, resources, zones,
forces, current event, available commands, score/rank/log) plus a `messages`
list for the step. Out-of-order or invalid actions return HTTP 400 with a
Traditional Chinese `detail`. Interactive docs are served at `/docs`, and the
single-page UI at `/`.

### Frontend (React + Vite)

The browser UI is a React app (`frontend/`) animated with Framer Motion. The
production build is committed under `decisive20/web/static/`, so `uvicorn` serves
it directly with no Node step required.

To work on the UI:

```bash
cd frontend
npm install
npm run dev      # Vite dev server on :5173, proxies /api to :8000
# (run `uvicorn decisive20.web:app --port 8000` alongside it)
npm run build    # rebuild the committed bundle into ../decisive20/web/static
```

### Persistence

Games are stored in SQLite so they survive a server restart — each session
(including the seeded RNG, which keeps a reloaded game deterministic) is
persisted on every action. The database path defaults to `decisive20_games.db`
in the working directory; override it with the `DECISIVE20_DB` environment
variable. Tests use an in-memory store (`MemoryGameStore`) for isolation.

## Development Commands

```bash
python -m pytest
python -m decisive20 validate --scenario scenarios/taichung_defense_v1.json
```
