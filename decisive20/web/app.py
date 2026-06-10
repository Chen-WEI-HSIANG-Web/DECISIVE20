from __future__ import annotations

"""FastAPI backend exposing :class:`GameSession` over HTTP.

Each game lives server-side in an in-memory store keyed by a generated id, so
the non-serializable parts of ``GameState`` (the seeded RNG, the event deck)
never have to leave the process. The client only ever sees ``snapshot()`` JSON.

Endpoints (all under ``/api``):

    POST /api/games                      create a game, returns game_id + state
    GET  /api/games/{gid}                current state
    POST /api/games/{gid}/event          {"option": "A"}  resolve the event
    POST /api/games/{gid}/command        {"action": "...", "target": "A"?}
    POST /api/games/{gid}/end-command    enemy phase + open next round

Out-of-order or invalid actions raise ``ValueError`` in the session layer and
surface here as HTTP 400 with the (Traditional Chinese) message.
"""

import os
import uuid
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from decisive20.session import GameSession, Phase
from decisive20.web.store import GameStore, SqliteGameStore

DEFAULT_SCENARIO = "taichung_defense_v1.json"
_SCENARIO_DIR = Path(__file__).resolve().parents[2] / "scenarios"
_STATIC_DIR = Path(__file__).resolve().parent / "static"
DEFAULT_DB_PATH = os.environ.get("DECISIVE20_DB", "decisive20_games.db")


class NewGameRequest(BaseModel):
    seed: int | None = None
    scenario: str | None = None  # filename within the scenarios directory


class EventChoiceRequest(BaseModel):
    option: str


class CommandRequest(BaseModel):
    action: str
    target: str | None = None


def _resolve_scenario_path(name: str | None) -> Path:
    """Resolve a scenario filename safely inside the scenarios directory."""
    filename = name or DEFAULT_SCENARIO
    candidate = (_SCENARIO_DIR / filename).resolve()
    if candidate.parent != _SCENARIO_DIR or not candidate.is_file():
        raise HTTPException(status_code=404, detail=f"找不到劇本：{filename}")
    return candidate


def create_app(store: GameStore | None = None) -> FastAPI:
    app = FastAPI(title="決戰20 Decisive 20", version="0.1.0")
    store = store if store is not None else SqliteGameStore(DEFAULT_DB_PATH)

    @app.exception_handler(ValueError)
    async def _value_error_handler(_request: Request, exc: ValueError) -> JSONResponse:
        return JSONResponse(status_code=400, content={"detail": str(exc)})

    def _get_session(game_id: str) -> GameSession:
        session = store.load(game_id)
        if session is None:
            raise HTTPException(status_code=404, detail="找不到對局，請重新開始。")
        return session

    def _state(session: GameSession, messages: list[str] | None = None) -> dict:
        payload = session.snapshot()
        payload["messages"] = messages or []
        return payload

    @app.get("/api/healthz")
    def healthz() -> dict:
        return {"status": "ok", "games": store.count()}

    @app.post("/api/games")
    def new_game(body: NewGameRequest | None = None) -> dict:
        body = body or NewGameRequest()
        scenario_path = _resolve_scenario_path(body.scenario)
        session = GameSession.from_path(scenario_path, seed=body.seed)
        upkeep = session.open_round()
        game_id = uuid.uuid4().hex
        store.save(game_id, session)
        payload = _state(session, upkeep)
        payload["game_id"] = game_id
        return payload

    @app.get("/api/games/{game_id}")
    def get_game(game_id: str) -> dict:
        return _state(_get_session(game_id))

    @app.post("/api/games/{game_id}/event")
    def choose_event(game_id: str, body: EventChoiceRequest) -> dict:
        session = _get_session(game_id)
        messages = session.choose_event_option(body.option)
        store.save(game_id, session)
        return _state(session, messages)

    @app.post("/api/games/{game_id}/command")
    def run_command(game_id: str, body: CommandRequest) -> dict:
        session = _get_session(game_id)
        message = session.command(body.action, body.target)
        store.save(game_id, session)
        return _state(session, [message])

    @app.post("/api/games/{game_id}/end-command")
    def end_command(game_id: str) -> dict:
        session = _get_session(game_id)
        messages = list(session.end_command())
        # Roll straight into the next round so the client gets the next event.
        if session.phase == Phase.SETUP:
            messages.extend(session.open_round())
        store.save(game_id, session)
        return _state(session, messages)

    @app.delete("/api/games/{game_id}")
    def delete_game(game_id: str) -> dict:
        store.delete(game_id)
        return {"deleted": game_id}

    # Serve the built React app (index.html + hashed assets). Mounted last so
    # the explicit /api routes always take precedence over the SPA catch-all.
    if (_STATIC_DIR / "index.html").is_file():
        app.mount("/", StaticFiles(directory=_STATIC_DIR, html=True), name="static")

    return app


app = create_app()
