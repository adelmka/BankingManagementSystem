"""Unit tests for the CLI CommandDispatcher."""

from unittest.mock import MagicMock, patch

import pytest

from cli.command_dispatcher import CommandDispatcher


@pytest.fixture
def logger():
    return MagicMock(name="logger")


@pytest.fixture
def dispatcher(logger):
    with patch(
        "cli.command_dispatcher.get_logger",
        return_value=logger,
    ):
        instance = CommandDispatcher()
    return instance


@pytest.fixture
def handler():
    return MagicMock(name="handler", return_value="result")


class TestCommandDispatcher:
    def test_constructor_initializes_empty_registry(self, dispatcher):
        assert dispatcher.get_registered_commands() == []

    def test_constructor_initializes_logger(self, dispatcher, logger):
        assert dispatcher.logger is logger

    def test_register_command_adds_handler(self, dispatcher, handler):
        dispatcher.register_command("deposit", handler)
        assert dispatcher.has_command("deposit") is True
        assert dispatcher.get_registered_commands() == ["deposit"]

    def test_register_command_normalizes_name(self, dispatcher, handler):
        dispatcher.register_command("  DePoSiT  ", handler)
        assert dispatcher.has_command("deposit") is True
        assert dispatcher.get_registered_commands() == ["deposit"]

    def test_register_command_logs_registration(self, dispatcher, handler, logger):
        dispatcher.register_command("deposit", handler)
        logger.debug.assert_called_once_with(
            "Registered CLI command: %s", "deposit"
        )

    def test_register_command_rejects_empty_name(self, dispatcher, handler):
        with pytest.raises(ValueError, match="Command name cannot be empty"):
            dispatcher.register_command("", handler)

    def test_register_command_rejects_non_callable_handler(self, dispatcher):
        with pytest.raises(TypeError, match="Command handler must be callable"):
            dispatcher.register_command("deposit", object())

    def test_register_command_rejects_duplicate_name(self, dispatcher, handler):
        dispatcher.register_command("deposit", handler)
        with pytest.raises(ValueError, match="Command already registered: deposit"):
            dispatcher.register_command("DEPOSIT", MagicMock())

    def test_duplicate_registration_keeps_original_handler(self, dispatcher, handler):
        dispatcher.register_command("deposit", handler)
        with pytest.raises(ValueError):
            dispatcher.register_command("deposit", MagicMock())
        dispatcher.dispatch("deposit")
        handler.assert_called_once_with()

    def test_unregister_command_removes_registered_command(self, dispatcher, handler):
        dispatcher.register_command("deposit", handler)
        dispatcher.unregister_command("deposit")
        assert dispatcher.has_command("deposit") is False
        assert dispatcher.get_registered_commands() == []

    def test_unregister_command_normalizes_name(self, dispatcher, handler):
        dispatcher.register_command("deposit", handler)
        dispatcher.unregister_command("  DEPOSIT  ")
        assert dispatcher.has_command("deposit") is False

    def test_unregister_unknown_command_is_noop(self, dispatcher):
        dispatcher.unregister_command("missing")
        assert dispatcher.get_registered_commands() == []

    def test_dispatch_executes_registered_handler(self, dispatcher, handler):
        dispatcher.register_command("deposit", handler)
        assert dispatcher.dispatch("deposit") == "result"
        handler.assert_called_once_with()

    def test_dispatch_normalizes_command_name(self, dispatcher, handler):
        dispatcher.register_command("deposit", handler)
        dispatcher.dispatch("  DEPOSIT  ")
        handler.assert_called_once_with()

    def test_dispatch_forwards_positional_arguments(self, dispatcher, handler):
        dispatcher.register_command("transfer", handler)
        dispatcher.dispatch("transfer", "A001", "A002", 100)
        handler.assert_called_once_with("A001", "A002", 100)

    def test_dispatch_forwards_keyword_arguments(self, dispatcher, handler):
        dispatcher.register_command("transfer", handler)
        dispatcher.dispatch(
            "transfer", source="A001", destination="A002", amount=100
        )
        handler.assert_called_once_with(
            source="A001", destination="A002", amount=100
        )

    def test_dispatch_returns_handler_result(self, dispatcher):
        handler = MagicMock(return_value={"status": "ok"})
        dispatcher.register_command("status", handler)
        assert dispatcher.dispatch("status") == {"status": "ok"}

    def test_dispatch_logs_execution(self, dispatcher, handler, logger):
        dispatcher.register_command("deposit", handler)
        logger.reset_mock()
        dispatcher.dispatch("deposit")
        logger.debug.assert_called_once_with(
            "Executing CLI command: %s", "deposit"
        )

    def test_dispatch_unknown_command_raises_value_error(self, dispatcher):
        with pytest.raises(ValueError, match="Unknown command: missing"):
            dispatcher.dispatch("missing")

    def test_dispatch_unknown_command_does_not_log_execution(self, dispatcher, logger):
        with pytest.raises(ValueError):
            dispatcher.dispatch("missing")
        logger.debug.assert_not_called()

    def test_dispatch_propagates_handler_exception(self, dispatcher):
        handler = MagicMock(side_effect=RuntimeError("handler failed"))
        dispatcher.register_command("deposit", handler)
        with pytest.raises(RuntimeError, match="handler failed"):
            dispatcher.dispatch("deposit")

    @pytest.mark.parametrize("command", ["deposit", "DEPOSIT", " deposit "])
    def test_has_command_is_case_and_whitespace_insensitive(
        self, dispatcher, handler, command
    ):
        dispatcher.register_command("deposit", handler)
        assert dispatcher.has_command(command) is True

    @pytest.mark.parametrize("command", ["withdraw", "", "missing"])
    def test_has_command_returns_false_for_unregistered_command(
        self, dispatcher, command
    ):
        assert dispatcher.has_command(command) is False

    def test_get_registered_commands_preserves_registration_order(self, dispatcher):
        dispatcher.register_command("first", MagicMock())
        dispatcher.register_command("second", MagicMock())
        dispatcher.register_command("third", MagicMock())
        assert dispatcher.get_registered_commands() == [
            "first", "second", "third"
        ]

    def test_get_registered_commands_returns_copy(self, dispatcher, handler):
        dispatcher.register_command("deposit", handler)
        commands = dispatcher.get_registered_commands()
        commands.append("injected")
        assert dispatcher.get_registered_commands() == ["deposit"]

    def test_clear_commands_removes_all_commands(self, dispatcher):
        dispatcher.register_command("deposit", MagicMock())
        dispatcher.register_command("withdraw", MagicMock())
        dispatcher.clear_commands()
        assert dispatcher.get_registered_commands() == []
        assert dispatcher.has_command("deposit") is False
        assert dispatcher.has_command("withdraw") is False

    def test_clear_commands_can_be_called_when_empty(self, dispatcher):
        dispatcher.clear_commands()
        assert dispatcher.get_registered_commands() == []

    def test_commands_can_be_registered_after_clear(self, dispatcher, handler):
        dispatcher.register_command("deposit", handler)
        dispatcher.clear_commands()
        dispatcher.register_command("withdraw", handler)
        assert dispatcher.get_registered_commands() == ["withdraw"]
        assert dispatcher.dispatch("withdraw") == "result"

    def test_unregister_one_command_leaves_other_commands_intact(self, dispatcher):
        first = MagicMock(return_value="first")
        second = MagicMock(return_value="second")
        dispatcher.register_command("first", first)
        dispatcher.register_command("second", second)
        dispatcher.unregister_command("first")
        assert dispatcher.get_registered_commands() == ["second"]
        assert dispatcher.dispatch("second") == "second"
