"""Unit tests for the current CLI InputHandler contract."""

from datetime import datetime
from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest

from cli.input_handler import InputHandler


@pytest.fixture
def renderer():
    return MagicMock(name="renderer")


@pytest.fixture
def handler(renderer):
    return InputHandler(renderer)


class TestInputHandler:
    def test_constructor_retains_renderer(self, handler, renderer):
        assert handler._renderer is renderer

    def test_read_string_returns_trimmed_value(self, handler):
        with patch("builtins.input", return_value="  Adel  "):
            assert handler.read_string("Name") == "Adel"

    def test_read_string_retries_required_empty_input(self, handler, renderer):
        with patch("builtins.input", side_effect=["   ", "Adel"]):
            assert handler.read_string("Name") == "Adel"
        renderer.error.assert_called_once_with("Input cannot be empty.")

    def test_read_string_allows_empty_when_not_required(self, handler, renderer):
        with patch("builtins.input", return_value="   "):
            assert handler.read_string("Middle name", required=False) == ""
        renderer.error.assert_not_called()

    def test_read_integer_returns_integer(self, handler):
        with patch("builtins.input", return_value=" 42 "):
            assert handler.read_integer("Age") == 42

    def test_read_integer_retries_invalid_input(self, handler, renderer):
        with patch("builtins.input", side_effect=["abc", "42"]):
            assert handler.read_integer("Age") == 42
        renderer.error.assert_called_once_with("Please enter a valid integer.")

    def test_read_integer_enforces_minimum(self, handler, renderer):
        with patch("builtins.input", side_effect=["4", "5"]):
            assert handler.read_integer("Age", minimum=5) == 5
        renderer.error.assert_called_once_with("Value must be at least 5.")

    def test_read_integer_enforces_maximum(self, handler, renderer):
        with patch("builtins.input", side_effect=["11", "10"]):
            assert handler.read_integer("Age", maximum=10) == 10
        renderer.error.assert_called_once_with("Value must not exceed 10.")

    def test_read_integer_accepts_boundaries(self, handler):
        with patch("builtins.input", return_value="5"):
            assert handler.read_integer("Value", minimum=5, maximum=5) == 5

    def test_read_decimal_returns_decimal(self, handler):
        with patch("builtins.input", return_value=" 125.50 "):
            assert handler.read_decimal("Amount") == Decimal("125.50")

    def test_read_decimal_retries_invalid_input(self, handler, renderer):
        with patch("builtins.input", side_effect=["abc", "12.50"]):
            assert handler.read_decimal("Amount") == Decimal("12.50")
        renderer.error.assert_called_once_with("Please enter a valid decimal value.")

    def test_read_decimal_enforces_minimum(self, handler, renderer):
        with patch("builtins.input", side_effect=["9.99", "10.00"]):
            assert handler.read_decimal("Amount", minimum=Decimal("10.00")) == Decimal("10.00")
        renderer.error.assert_called_once_with("Minimum value is 10.00.")

    def test_read_decimal_enforces_maximum(self, handler, renderer):
        with patch("builtins.input", side_effect=["10.01", "10.00"]):
            assert handler.read_decimal("Amount", maximum=Decimal("10.00")) == Decimal("10.00")
        renderer.error.assert_called_once_with("Maximum value is 10.00.")

    def test_read_decimal_accepts_boundaries(self, handler):
        with patch("builtins.input", return_value="10.00"):
            assert handler.read_decimal(
                "Amount",
                minimum=Decimal("10.00"),
                maximum=Decimal("10.00"),
            ) == Decimal("10.00")

    def test_read_date_returns_datetime(self, handler):
        with patch("builtins.input", return_value="2026-08-08"):
            assert handler.read_date("Date") == datetime(2026, 8, 8)

    def test_read_date_retries_invalid_input(self, handler, renderer):
        with patch("builtins.input", side_effect=["2026-99-99", "2026-08-08"]):
            assert handler.read_date("Date") == datetime(2026, 8, 8)
        renderer.error.assert_called_once_with("Invalid date.")

    def test_read_date_supports_custom_format(self, handler):
        with patch("builtins.input", return_value="08/08/2026"):
            assert handler.read_date("Date", date_format="%d/%m/%Y") == datetime(2026, 8, 8)

    @pytest.mark.parametrize("value", ["y", "Y", "yes", "YES", " Yes "])
    def test_confirm_accepts_yes_values(self, handler, value):
        with patch("builtins.input", return_value=value):
            assert handler.confirm("Continue") is True

    @pytest.mark.parametrize("value", ["n", "N", "no", "NO", " No "])
    def test_confirm_accepts_no_values(self, handler, value):
        with patch("builtins.input", return_value=value):
            assert handler.confirm("Continue") is False

    def test_confirm_retries_invalid_response(self, handler, renderer):
        with patch("builtins.input", side_effect=["maybe", "y"]):
            assert handler.confirm("Continue") is True
        renderer.error.assert_called_once_with("Please enter Y or N.")

    def test_read_menu_selection_returns_valid_choice(self, handler):
        with patch("builtins.input", return_value="2"):
            assert handler.read_menu_selection({"1", "2", "3"}) == "2"

    def test_read_menu_selection_retries_invalid_choice(self, handler, renderer):
        with patch("builtins.input", side_effect=["9", "2"]):
            assert handler.read_menu_selection({"1", "2", "3"}) == "2"
        renderer.error.assert_called_once_with("Invalid menu selection.")

    def test_read_menu_selection_strips_input(self, handler, renderer):
        with patch("builtins.input", return_value=" 2 "):
            assert handler.read_menu_selection({"2"}) == "2"
        renderer.error.assert_not_called()

    def test_pause_waits_for_enter(self, handler):
        with patch("builtins.input", return_value="") as mocked_input:
            assert handler.pause() is None
        mocked_input.assert_called_once_with("\nPress ENTER to continue...")

    def test_read_string_uses_expected_prompt(self, handler):
        with patch("builtins.input", return_value="Adel") as mocked_input:
            handler.read_string("Name")
        mocked_input.assert_called_once_with("Name: ")

    def test_read_integer_uses_expected_prompt(self, handler):
        with patch("builtins.input", return_value="42") as mocked_input:
            handler.read_integer("Age")
        mocked_input.assert_called_once_with("Age: ")

    def test_read_decimal_uses_expected_prompt(self, handler):
        with patch("builtins.input", return_value="10.00") as mocked_input:
            handler.read_decimal("Amount")
        mocked_input.assert_called_once_with("Amount: ")

    def test_read_date_uses_expected_prompt(self, handler):
        with patch("builtins.input", return_value="2026-08-08") as mocked_input:
            handler.read_date("Date")
        mocked_input.assert_called_once_with("Date (%Y-%m-%d): ")

    def test_confirm_uses_expected_prompt(self, handler):
        with patch("builtins.input", return_value="y") as mocked_input:
            handler.confirm("Continue")
        mocked_input.assert_called_once_with("Continue (Y/N): ")

    def test_repr(self, handler):
        assert repr(handler) == "InputHandler()"

    def test_str(self, handler):
        assert str(handler) == "CLI Input Handler"
