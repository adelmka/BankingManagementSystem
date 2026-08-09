"""Integration tests for the CLI infrastructure compatibility contract."""

from decimal import Decimal
from io import StringIO
from unittest.mock import patch

from cli.input_handler import InputHandler
from cli.menu_renderer import MenuRenderer


def test_input_handler_command_adapter_aliases():
    output = StringIO()
    renderer = MenuRenderer(output=output)
    handler = InputHandler(renderer)

    with patch("builtins.input", side_effect=[" Adel ", "25.50", "y"]):
        assert handler.get_value("Name") == "Adel"
        assert handler.get_money("Amount") == Decimal("25.50")
        assert handler.get_confirmation("Continue") is True


def test_menu_renderer_command_adapter_aliases():
    output = StringIO()
    renderer = MenuRenderer(output=output)

    renderer.display_message("hello")
    renderer.display_success("done")
    renderer.display_warning("careful")
    renderer.display_error("failed")
    renderer.display_object("customer")
    renderer.display_list(["one", "two"])

    rendered = output.getvalue()

    assert "[INFO] hello" in rendered
    assert "[SUCCESS] done" in rendered
    assert "[WARNING] careful" in rendered
    assert "[ERROR] failed" in rendered
    assert "customer" in rendered
    assert "one" in rendered
    assert "two" in rendered
