"""HTTP backend for Decisive 20, wrapping the headless GameSession."""

from decisive20.web.app import app, create_app

__all__ = ["app", "create_app"]
