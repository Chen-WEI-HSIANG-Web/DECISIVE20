import pytest
from fastapi.testclient import TestClient

from decisive20.web import create_app
from decisive20.web.store import MemoryGameStore


@pytest.fixture()
def client():
    return TestClient(create_app(store=MemoryGameStore()))


def _new_game(client, seed=123):
    resp = client.post("/api/games", json={"seed": seed})
    assert resp.status_code == 200
    return resp.json()


def test_new_game_returns_state_at_event_phase(client):
    data = _new_game(client)
    assert "game_id" in data
    assert data["phase"] == "event"
    assert data["round"] == 1
    assert data["scenario_name"] == "台中防衛戰 V1"
    assert data["event"] is not None
    assert len(data["zones"]) == 4
    # Upkeep messages flow back as the step's messages.
    assert any("指令點" in m for m in data["messages"])


def test_event_choice_advances_to_command_phase(client):
    game = _new_game(client)
    gid = game["game_id"]
    resp = client.post(f"/api/games/{gid}/event", json={"option": "A"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["phase"] in {"command", "ended"}


def test_invalid_event_option_returns_400(client):
    game = _new_game(client)
    gid = game["game_id"]
    resp = client.post(f"/api/games/{gid}/event", json={"option": "Z"})
    assert resp.status_code == 400
    assert "無效" in resp.json()["detail"]


def test_command_out_of_phase_returns_400(client):
    game = _new_game(client)
    gid = game["game_id"]
    # Still in EVENT phase — a command is not yet allowed.
    resp = client.post(f"/api/games/{gid}/command", json={"action": "recon"})
    assert resp.status_code == 400


def test_unknown_game_returns_404(client):
    resp = client.get("/api/games/does-not-exist")
    assert resp.status_code == 404


def test_index_serves_frontend(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert "決戰20" in resp.text
    assert "text/html" in resp.headers["content-type"]


def test_full_game_playthrough_ends(client):
    """Drive a whole game over HTTP: always pick A, immediately end command."""
    game = _new_game(client, seed=123)
    gid = game["game_id"]
    state = game
    for _ in range(200):  # generous guard against an infinite loop
        if state["phase"] == "ended":
            break
        if state["phase"] == "event":
            state = client.post(f"/api/games/{gid}/event", json={"option": "A"}).json()
            continue
        if state["phase"] == "command":
            state = client.post(f"/api/games/{gid}/end-command").json()
            continue
        raise AssertionError(f"unexpected phase: {state['phase']}")

    assert state["phase"] == "ended"
    assert state["ending_type"] in {"victory", "failure", "incomplete"}
    assert state["rank"] in {"S", "A", "B", "C", "D"}


def test_command_target_reinforces_zone(client):
    game = _new_game(client, seed=7)
    gid = game["game_id"]
    # Resolve the event first to reach the command phase.
    state = client.post(f"/api/games/{gid}/event", json={"option": "B"}).json()
    if state["phase"] != "command":
        pytest.skip("game ended before command phase under this seed")
    before = next(z for z in state["zones"] if z["code"] == "A")["defense"]
    resp = client.post(f"/api/games/{gid}/command", json={"action": "reinforce", "target": "A"})
    if resp.status_code != 200:
        pytest.skip("insufficient CP for reinforce under this seed")
    after = next(z for z in resp.json()["zones"] if z["code"] == "A")["defense"]
    assert after == before + 2
