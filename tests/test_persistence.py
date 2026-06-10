from fastapi.testclient import TestClient

from decisive20.session import GameSession, Phase
from decisive20.web import create_app
from decisive20.web.store import SqliteGameStore

SCENARIO = "scenarios/taichung_defense_v1.json"


def test_sqlite_store_roundtrips_a_session(tmp_path):
    store = SqliteGameStore(tmp_path / "games.db")
    session = GameSession.from_path(SCENARIO, seed=42)
    session.open_round()
    store.save("g1", session)

    loaded = store.load("g1")
    assert loaded is not None
    assert loaded.phase == Phase.EVENT
    assert loaded.snapshot() == session.snapshot()


def test_sqlite_store_survives_new_store_instance(tmp_path):
    """A brand-new store object on the same file == a process restart."""
    db = tmp_path / "games.db"
    SqliteGameStore(db).save("g1", _played_session(seed=7))

    reopened = SqliteGameStore(db)  # simulates restart
    loaded = reopened.load("g1")
    assert loaded is not None
    assert loaded.game_state.current_round >= 1
    assert reopened.count() == 1


def test_game_survives_app_restart(tmp_path):
    """Play a turn, throw away the app, rebuild it on the same DB, keep playing."""
    db = tmp_path / "games.db"

    app1 = create_app(store=SqliteGameStore(db))
    c1 = TestClient(app1)
    game = c1.post("/api/games", json={"seed": 7}).json()
    gid = game["game_id"]
    c1.post(f"/api/games/{gid}/event", json={"option": "A"})
    state_before = c1.get(f"/api/games/{gid}").json()

    # Rebuild the app (new in-memory FastAPI, same SQLite file) — the restart.
    app2 = create_app(store=SqliteGameStore(db))
    c2 = TestClient(app2)
    state_after = c2.get(f"/api/games/{gid}").json()

    assert state_after["round"] == state_before["round"]
    assert state_after["phase"] == state_before["phase"]
    assert state_after["zones"] == state_before["zones"]
    assert state_after["cp"] == state_before["cp"]

    # And the reloaded game is still playable + deterministic.
    if state_after["phase"] == "command":
        resp = c2.post(f"/api/games/{gid}/end-command")
        assert resp.status_code == 200


def test_reloaded_game_is_deterministic(tmp_path):
    """Saving/reloading mid-game must not perturb the seeded RNG stream."""
    db = tmp_path / "games.db"

    # Reference run: never touches the store.
    ref = GameSession.from_path(SCENARIO, seed=2024)
    ref.open_round()
    ref.choose_event_option("A")
    ref.end_command()
    reference = ref.snapshot()

    # Persisted run: save + reload between every step.
    store = SqliteGameStore(db)
    s = GameSession.from_path(SCENARIO, seed=2024)
    s.open_round()
    store.save("g", s)
    s = store.load("g")
    s.choose_event_option("A")
    store.save("g", s)
    s = store.load("g")
    s.end_command()
    persisted = s.snapshot()

    assert persisted == reference


def _played_session(seed: int) -> GameSession:
    session = GameSession.from_path(SCENARIO, seed=seed)
    session.open_round()
    session.choose_event_option("A")
    return session
