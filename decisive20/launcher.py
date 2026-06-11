from __future__ import annotations

"""Windows-friendly launcher for the Decisive 20 web UI."""

import argparse
import os
import socket
import sys
import threading
import time
import urllib.request
import webbrowser
from pathlib import Path


DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8765
APP_DIR_NAME = "Decisive20"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Launch the Decisive 20 Web UI.")
    parser.add_argument("--host", default=DEFAULT_HOST)
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("--no-browser", action="store_true")
    args = parser.parse_args(argv)

    _configure_runtime_environment()
    port = _find_available_port(args.host, args.port)

    # Import after DECISIVE20_DB is configured because web.app reads it at import time.
    import uvicorn
    from decisive20.web import create_app

    url = f"http://{args.host}:{port}"
    config = uvicorn.Config(
        create_app(),
        host=args.host,
        port=port,
        log_level="info",
        access_log=False,
    )
    server = uvicorn.Server(config)
    thread = threading.Thread(target=server.run, daemon=True)

    print(f"Starting Decisive 20 at {url}")
    print(f"Game data: {os.environ['DECISIVE20_DB']}")
    thread.start()

    if not _wait_for_health(f"{url}/api/healthz"):
        print("Server did not become ready in time.", file=sys.stderr)
        server.should_exit = True
        thread.join(timeout=5)
        return 1

    if not args.no_browser:
        webbrowser.open(url)

    print("Close this window or press Ctrl+C to stop the game server.")
    try:
        while thread.is_alive():
            thread.join(timeout=0.5)
    except KeyboardInterrupt:
        print("\nStopping Decisive 20...")
        server.should_exit = True
        thread.join(timeout=10)
    return 0


def _configure_runtime_environment() -> None:
    data_dir = _local_app_data_dir()
    data_dir.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault("DECISIVE20_DB", str(data_dir / "decisive20_games.db"))


def _local_app_data_dir() -> Path:
    root = os.environ.get("LOCALAPPDATA")
    if root:
        return Path(root) / APP_DIR_NAME
    return Path.home() / "AppData" / "Local" / APP_DIR_NAME


def _find_available_port(host: str, preferred_port: int) -> int:
    for port in range(preferred_port, preferred_port + 100):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(0.2)
            if sock.connect_ex((host, port)) != 0:
                return port
    raise RuntimeError(f"No available port found from {preferred_port} to {preferred_port + 99}")


def _wait_for_health(url: str, timeout_seconds: float = 20.0) -> bool:
    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=1.0) as response:
                if response.status == 200:
                    return True
        except OSError:
            time.sleep(0.25)
    return False


if __name__ == "__main__":
    raise SystemExit(main())
