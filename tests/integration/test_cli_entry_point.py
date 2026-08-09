"""Integration tests for the executable BMS CLI entry point."""

from __future__ import annotations

import main


class _FakeBank:
    """Minimal bank facade used to exercise CLI startup/shutdown."""


class _FakeCustomerCommands:
    """Minimal customer command adapter used by the entry-point test."""

    def create_customer(self) -> None:
        pass


class _FakeAccountCommands:
    """Minimal account command adapter used by the entry-point test."""

    def create_account(self) -> None:
        pass


class _FakeApplication:
    """Minimal application object used by the entry-point test."""

    def __init__(self) -> None:
        self.bank = _FakeBank()
        self.shutdown_called = False
        self.command_adapters_created = False

    def create_cli_commands(self, *, input_handler, menu_renderer):
        self.command_adapters_created = True
        return {
            "customer": _FakeCustomerCommands(),
            "account": _FakeAccountCommands(),
        }

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

    assert application.command_adapters_created is True
    assert application.shutdown_called is True


def test_main_menu_exposes_customer_and_account_creation() -> None:
    """The executable menu must expose the two primary setup operations."""

    menu = dict(main.MAIN_MENU)

    assert menu["1"] == "Create customer"
    assert menu["3"] == "Open account"
    assert menu["0"] == "Exit"
