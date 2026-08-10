"""Tests for the executable CLI entry point."""

from types import SimpleNamespace
from unittest.mock import MagicMock

from main import _account_type_display, _list_accounts


def test_account_type_display_accepts_enum_like_value():
    account = SimpleNamespace(account_type=SimpleNamespace(value="Savings"))

    assert _account_type_display(account) == "Savings"


def test_account_type_display_accepts_persisted_string():
    account = SimpleNamespace(account_type="Savings")

    assert _account_type_display(account) == "Savings"


def test_list_accounts_displays_string_account_type_without_error():
    application = SimpleNamespace(
        bank=SimpleNamespace(
            accounts=lambda: [
                SimpleNamespace(
                    account_number="S000001",
                    customer_id="C000001",
                    account_type="Savings",
                    balance="2000.00 SAR",
                )
            ]
        )
    )
    renderer = MagicMock()

    _list_accounts(application, renderer)

    rows = list(renderer.render_table.call_args.args[0])
    assert rows == [
        (
            "S000001",
            "C000001",
            "Savings",
            "2000.00 SAR",
        )
    ]
