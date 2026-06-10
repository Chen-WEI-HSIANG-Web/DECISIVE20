from decisive20.session import GameSession, Phase

SCENARIO = "scenarios/taichung_defense_v1.json"


def _auto_play(seed: int) -> GameSession:
    """Drive a session to completion: always pick option A, never command."""
    session = GameSession.from_path(SCENARIO, seed=seed)
    session.open_round()
    while session.phase != Phase.ENDED:
        session.choose_event_option("A")
        if session.phase == Phase.ENDED:
            break
        session.end_command()
        if session.phase == Phase.SETUP:
            session.open_round()
    return session


def test_session_runs_to_completion():
    session = _auto_play(seed=123)
    assert session.phase == Phase.ENDED
    assert session.ended is True
    assert session.game_state.ending_type in {"victory", "failure", "incomplete"}
    assert session.game_state.rank in {"S", "A", "B", "C", "D"}


def test_session_is_reproducible_under_seed():
    a = _auto_play(seed=999).snapshot()
    b = _auto_play(seed=999).snapshot()
    assert a == b


def test_snapshot_exposes_web_contract():
    session = GameSession.from_path(SCENARIO, seed=7)
    session.open_round()
    snap = session.snapshot()
    assert snap["phase"] == "event"
    assert snap["round"] == 1
    assert snap["scenario_name"] == "台中防衛戰 V1"
    assert {"supply", "intel", "morale", "political_pressure", "enemy_pressure"} <= set(
        snap["resources"]
    )
    assert snap["event"] is not None
    assert all("affordable" in option for option in snap["event"]["options"])
    assert len(snap["zones"]) == 4


def test_phase_guards_reject_out_of_order_calls():
    session = GameSession.from_path(SCENARIO, seed=1)
    session.open_round()  # → EVENT
    # Cannot run a command before the event is resolved.
    try:
        session.command("recon")
    except ValueError:
        pass
    else:  # pragma: no cover
        raise AssertionError("expected ValueError for out-of-phase command")
