from __future__ import annotations

"""Runtime path helpers for source and PyInstaller builds."""

import sys
from pathlib import Path


def runtime_root() -> Path:
    """Return the project/data root in source or PyInstaller runtime."""
    frozen_root = getattr(sys, "_MEIPASS", None)
    if frozen_root:
        return Path(frozen_root)
    return Path(__file__).resolve().parents[1]


def scenarios_dir() -> Path:
    return runtime_root() / "scenarios"


def static_dir() -> Path:
    return Path(__file__).resolve().parent / "web" / "static"
