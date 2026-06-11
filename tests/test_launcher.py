from pathlib import Path

from decisive20 import launcher
from decisive20.paths import scenarios_dir


def test_find_available_port_returns_requested_free_port():
    port = launcher._find_available_port("127.0.0.1", 28765)
    assert 28765 <= port < 28865


def test_local_app_data_dir_uses_localappdata(monkeypatch, tmp_path):
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
    assert launcher._local_app_data_dir() == tmp_path / "Decisive20"


def test_configure_runtime_environment_sets_default_db(monkeypatch, tmp_path):
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
    monkeypatch.delenv("DECISIVE20_DB", raising=False)
    launcher._configure_runtime_environment()
    assert Path(launcher.os.environ["DECISIVE20_DB"]) == (
        tmp_path / "Decisive20" / "decisive20_games.db"
    )


def test_scenarios_dir_points_to_bundled_scenarios():
    assert (scenarios_dir() / "taichung_defense_v1.json").is_file()
