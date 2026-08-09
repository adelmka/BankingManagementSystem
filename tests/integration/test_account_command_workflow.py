"""Integration coverage for the AccountCommands -> AccountService workflow."""

from unittest.mock import MagicMock

from cli.commands.account_commands import AccountCommands
from cli.menu_renderer import MenuRenderer


def test_account_command_dependencies_are_wired(account_service):
    input_handler = MagicMock()
    renderer = MagicMock(spec=MenuRenderer)

    commands = AccountCommands(
        account_service=account_service,
        input_handler=input_handler,
        menu_renderer=renderer,
    )

    assert commands.account_service is account_service
    assert commands.input_handler is input_handler
    assert commands.menu_renderer is renderer
