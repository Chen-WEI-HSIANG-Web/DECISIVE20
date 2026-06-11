# 決戰20 Decisive 20

決戰20 is a playable strategic decision-pressure wargame prototype. It includes
a Python CLI, a shared headless game session, a FastAPI web backend, a React/Vite
browser UI, and local SQLite persistence for active games.

You command a city's defense over a fixed number of rounds, spending Command
Points on strategic actions, deploying forces, reading enemy intent when intel is
high enough, and weathering a seeded rule-based opponent that escalates over
time. Passive play loses; active management wins.

## Shipped V1 Scope

- Load and validate JSON scenarios
- Two bundled scenarios:
  - `taichung_defense_v1.json`
  - `kaohsiung_landing_v1.json`
- Five-phase round loop: upkeep -> status -> event -> command -> enemy
- Command Point economy with costed event options and standing actions
  (`reinforce`, `recon`, `rally`, `counter`)
- Force deployment with `deploy`, including garrison defense and force attrition
- Intel telegraph that reveals projected enemy targets once intel reaches the
  configured threshold
- Seeded enemy assaults against the softest zones, using effective defense
  including garrisoned forces
- Configurable victory and failure conditions from scenario JSON, with web UI
  overrides for supported condition types
- Shared `GameSession` state machine used by both CLI and web API
- FastAPI backend with scenario catalogue, game state endpoints, and health check
- React + Vite browser UI served as committed static assets by FastAPI
- SQLite persistence for server-side game sessions, including seeded RNG state
- End-game score and rank (S/A/B/C/D)
- Reproducible runs via `--seed`
- Automated Python test suite and a basic CI path for `pytest` + frontend build

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
python -m decisive20 validate --scenario scenarios/kaohsiung_landing_v1.json
```

Use `--no-color` to disable ANSI colors. Color also auto-disables when output is
piped or `NO_COLOR` is set. On legacy Windows consoles the CLI forces UTF-8
output so box-drawing and Chinese characters render correctly.

## How to Play

Each round you:

1. Read the crisis event and pick an option. Some options cost Command Points.
2. Spend remaining CP in the command phase:
   `reinforce A`, `deploy 預備旅 A`, `recon`, `rally`, `counter`, then `done`.
3. Survive the enemy phase. The enemy attacks the softest zones after counting
   zone defense and deployed forces.

See [docs/GAME_RULES_V1.md](docs/GAME_RULES_V1.md) for full rules and
[docs/SCENARIO_SCHEMA.md](docs/SCENARIO_SCHEMA.md) for authoring scenarios.

## Web Backend (FastAPI)

A headless `GameSession` state machine (`decisive20/session.py`) drives both the
CLI and the HTTP API, so rule logic is shared instead of duplicated.

```bash
python -m pip install -e .[web]
python -m uvicorn decisive20.web:app --reload --port 8000
```

API routes:

| Method & path | Purpose |
| --- | --- |
| `GET /api/healthz` | Health check and current stored game count |
| `GET /api/scenarios` | Scenario catalogue with default win/loss setup |
| `POST /api/games` | Create a game; accepts optional `seed`, `scenario`, `victory_conditions`, and `failure_conditions` |
| `GET /api/games/{id}` | Current state snapshot |
| `POST /api/games/{id}/event` | Resolve the current event with `{"option": "A"}` |
| `POST /api/games/{id}/command` | Run a command such as `{"action": "deploy", "target": "A", "force": "預備旅"}` |
| `POST /api/games/{id}/end-command` | Resolve enemy phase, then open the next round when applicable |
| `DELETE /api/games/{id}` | Delete a stored game |

Each response returns the session `snapshot()` plus a `messages` list for that
step. The snapshot includes round, phase, CP, resources, zones, forces, current
event, available commands, intel telegraph fields, score/rank/log, and ending
state. Out-of-order or invalid actions return HTTP 400 with a Traditional
Chinese `detail`. Interactive docs are served at `/docs`, and the single-page UI
at `/`.

## Frontend (React + Vite)

The browser UI lives in `frontend/` and uses React, Vite, and Framer Motion. The
production build is committed under `decisive20/web/static/`, so `uvicorn` serves
the UI directly without a Node step at runtime.

```bash
cd frontend
npm install
npm run dev      # Vite dev server on :5173, proxies /api to :8000
# run `python -m uvicorn decisive20.web:app --port 8000` alongside it
npm run build    # rebuilds ../decisive20/web/static
```

On Windows PowerShell, local execution policy may block `npm.ps1`. Use
`cmd /c npm run build` if that happens.

## Windows EXE Launcher

The project can be packaged as an onedir Windows launcher. The executable starts
the local FastAPI server, opens the browser to the Web UI, and stores game data
under `%LOCALAPPDATA%\Decisive20\decisive20_games.db`.

```bash
packaging\build_exe.bat
dist\Decisive20\Decisive20.exe
```

PowerShell users can also run:

```powershell
.\packaging\build_exe.ps1
```

The launcher accepts optional runtime arguments:

```bash
dist\Decisive20\Decisive20.exe --port 8765
dist\Decisive20\Decisive20.exe --no-browser
```

## Persistence

Games are stored in SQLite so they survive a server restart. Each persisted
session includes the seeded RNG state, keeping a reloaded game deterministic.
The database path defaults to `decisive20_games.db` in the working directory;
override it with the `DECISIVE20_DB` environment variable. Tests use
`MemoryGameStore` for isolation.

The SQLite store pickles local `GameSession` objects. This is acceptable for the
current single-application local prototype, but it is not a portable save format
or an untrusted-data interchange format.

## Development Commands

```bash
python -m pytest
python -m compileall decisive20
python -m decisive20 validate --scenario scenarios/taichung_defense_v1.json
python -m decisive20 validate --scenario scenarios/kaohsiung_landing_v1.json
cd frontend
cmd /c npm run build
```
