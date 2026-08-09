"""Integration tests for the executable BMS CLI entry point."""

from __future__ import annotations

import main


class _FakeBank:
    """Minimal bank façade used to exercise CLI startup/shutdown."""


class _FakeApplication:
    """Minimal application object used by the entry-point test."""

    def __init__(self) -> None:
        self.bank = _FakeBank()
        self.shutdown_called = False

    def shutdown(self) -> None:
        self.shutdown_called = True


def test_run_starts_and_shuts_down_cleanly(monkeypatch) -> None:
    """The executable entry point must initialize and exit cleanly."""

    application = _FakeApplication()

    monkeypatch.setattr(
        main,
        "start_application",
        lambda: application,
    )

    monkeypatch.setattr(
        "builtins.input",
        lambda _prompt="": "0",
    )

    main.run()

    assert application.shutdown_called is True
