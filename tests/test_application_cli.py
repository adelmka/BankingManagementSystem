"""Unit tests for the ApplicationCLI controller."""

from unittest.mock import MagicMock

import pytest

from cli.application_cli import ApplicationCLI


@pytest.fixture
def menu_renderer():
    return MagicMock(name="menu_renderer")


@pytest.fixture
def input_handler():
    return MagicMock(name="input_handler")


@pytest.fixture
def command_dispatcher():
    return MagicMock(name="command_dispatcher")


@pytest.fixture
def logger(monkeypatch):
    mock_logger = MagicMock(name="logger")
    monkeypatch.setattr(
        "cli.application_cli.get_logger",
        MagicMock(return_value=mock_logger),
    )
    return mock_logger


@pytest.fixture
def application_cli(
    menu_renderer,
    input_handler,
    command_dispatcher,
    logger,
):
    return ApplicationCLI(
        menu_renderer=menu_renderer,
        input_handler=input_handler,
        command_dispatcher=command_dispatcher,
    )


class TestApplicationCLI:
    def test_constructor_retains_dependencies(
        self,
        application_cli,
        menu_renderer,
        input_handler,
        command_dispatcher,
    ):
        assert application_cli.menu_renderer is menu_renderer
        assert application_cli.input_handler is input_handler
        assert application_cli.command_dispatcher is command_dispatcher

    def test_constructor_initializes_not_running(self, application_cli):
        assert application_cli._running is False

    def test_constructor_initializes_logger(self, application_cli, logger):
        assert application_cli.logger is logger

    def test_start_sets_running_before_loop(
        self,
        application_cli,
        monkeypatch,
    ):
        states = []

        def run_loop():
            states.append(application_cli._running)

        monkeypatch.setattr(application_cli, "_run_loop", run_loop)
        monkeypatch.setattr(application_cli, "stop", MagicMock())

        application_cli.start()

        assert states == [True]
        application_cli.stop.assert_called_once_with()

    def test_start_logs_launch_message(
        self,
        application_cli,
        logger,
        monkeypatch,
    ):
        monkeypatch.setattr(application_cli, "_run_loop", MagicMock())

        application_cli.start()

        logger.info.assert_any_call(
            "Starting Banking Management System CLI."
        )

    def test_start_always_stops_after_normal_loop(
        self,
        application_cli,
        monkeypatch,
    ):
        monkeypatch.setattr(application_cli, "_run_loop", MagicMock())
        stop = MagicMock()
        monkeypatch.setattr(application_cli, "stop", stop)

        application_cli.start()

        stop.assert_called_once_with()

    def test_start_logs_and_reraises_unexpected_exception(
        self,
        application_cli,
        logger,
        monkeypatch,
    ):
        error = RuntimeError("boom")
        monkeypatch.setattr(
            application_cli,
            "_run_loop",
            MagicMock(side_effect=error),
        )
        stop = MagicMock()
        monkeypatch.setattr(application_cli, "stop", stop)

        with pytest.raises(RuntimeError, match="boom"):
            application_cli.start()

        logger.exception.assert_called_once_with(
            "Unexpected CLI failure: %s",
            error,
        )
        stop.assert_called_once_with()

    def test_stop_sets_not_running(
        self,
        application_cli,
        logger,
    ):
        application_cli._running = True

        application_cli.stop()

        assert application_cli._running is False
        logger.info.assert_called_once_with(
            "Banking Management System CLI stopped."
        )

    def test_run_loop_displays_main_menu(
        self,
        application_cli,
        menu_renderer,
        input_handler,
        monkeypatch,
    ):
        application_cli._running = True
        input_handler.get_command.side_effect = ["exit"]

        application_cli._run_loop()

        menu_renderer.display_main_menu.assert_called_once_with()

    def test_run_loop_gets_command(
        self,
        application_cli,
        input_handler,
        monkeypatch,
    ):
        application_cli._running = True
        input_handler.get_command.side_effect = ["exit"]

        application_cli._run_loop()

        input_handler.get_command.assert_called_once_with()

    @pytest.mark.parametrize("command", ["exit", "EXIT", " exit "])
    def test_exit_command_stops_application(
        self,
        application_cli,
        command,
        monkeypatch,
    ):
        application_cli._running = True
        application_cli.input_handler.get_command.side_effect = [command]
        stop = MagicMock(side_effect=lambda: setattr(application_cli, "_running", False))
        monkeypatch.setattr(application_cli, "stop", stop)

        application_cli._run_loop()

        stop.assert_called_once_with()
        assert application_cli._running is False

    @pytest.mark.parametrize("command", ["quit", "QUIT", " quit ", "0"])
    def test_alternate_exit_commands_stop_application(
        self,
        application_cli,
        command,
        monkeypatch,
    ):
        application_cli._running = True
        application_cli.input_handler.get_command.side_effect = [command]
        stop = MagicMock(side_effect=lambda: setattr(application_cli, "_running", False))
        monkeypatch.setattr(application_cli, "stop", stop)

        application_cli._run_loop()

        stop.assert_called_once_with()
        assert application_cli._running is False

    def test_none_command_is_exit_command(self):
        assert ApplicationCLI._is_exit_command(None) is True

    @pytest.mark.parametrize("command", ["exit", "EXIT", "quit", "QUIT", "0"])
    def test_is_exit_command_recognizes_exit_values(self, command):
        assert ApplicationCLI._is_exit_command(command) is True

    @pytest.mark.parametrize("command", ["", "1", "deposit", "x", "  "])
    def test_is_exit_command_rejects_non_exit_values(self, command):
        assert ApplicationCLI._is_exit_command(command) is False

    def test_normal_command_is_dispatched(
        self,
        application_cli,
        command_dispatcher,
    ):
        application_cli._execute_command("deposit")

        command_dispatcher.dispatch.assert_called_once_with("deposit")

    def test_execute_command_passes_command_unchanged(
        self,
        application_cli,
        command_dispatcher,
    ):
        command = "  deposit  "

        application_cli._execute_command(command)

        command_dispatcher.dispatch.assert_called_once_with(command)

    def test_execute_command_handles_value_error(
        self,
        application_cli,
        command_dispatcher,
        menu_renderer,
        logger,
    ):
        error = ValueError("Unknown command")
        command_dispatcher.dispatch.side_effect = error

        application_cli._execute_command("bad-command")

        logger.warning.assert_called_once_with(
            "Invalid command: %s",
            error,
        )
        menu_renderer.display_message.assert_called_once_with(
            "Unknown command"
        )

    def test_execute_command_suppresses_value_error(
        self,
        application_cli,
        command_dispatcher,
    ):
        command_dispatcher.dispatch.side_effect = ValueError("invalid")

        application_cli._execute_command("invalid")

    def test_execute_command_does_not_catch_unexpected_exception(
        self,
        application_cli,
        command_dispatcher,
    ):
        error = RuntimeError("unexpected")
        command_dispatcher.dispatch.side_effect = error

        with pytest.raises(RuntimeError, match="unexpected"):
            application_cli._execute_command("command")

    def test_run_loop_dispatches_normal_command_then_exits(
        self,
        application_cli,
        command_dispatcher,
        monkeypatch,
    ):
        application_cli._running = True
        application_cli.input_handler.get_command.side_effect = [
            "deposit",
            "exit",
        ]
        stop = MagicMock(side_effect=lambda: setattr(application_cli, "_running", False))
        monkeypatch.setattr(application_cli, "stop", stop)

        application_cli._run_loop()

        command_dispatcher.dispatch.assert_called_once_with("deposit")
        stop.assert_called_once_with()

    def test_run_loop_does_not_dispatch_exit_command(
        self,
        application_cli,
        command_dispatcher,
        monkeypatch,
    ):
        application_cli._running = True
        application_cli.input_handler.get_command.side_effect = ["exit"]
        stop = MagicMock(side_effect=lambda: setattr(application_cli, "_running", False))
        monkeypatch.setattr(application_cli, "stop", stop)

        application_cli._run_loop()

        command_dispatcher.dispatch.assert_not_called()

    def test_run_loop_continues_after_normal_command(
        self,
        application_cli,
        command_dispatcher,
        menu_renderer,
        input_handler,
        monkeypatch,
    ):
        application_cli._running = True
        input_handler.get_command.side_effect = ["deposit", "quit"]
        stop = MagicMock(side_effect=lambda: setattr(application_cli, "_running", False))
        monkeypatch.setattr(application_cli, "stop", stop)

        application_cli._run_loop()

        assert menu_renderer.display_main_menu.call_count == 2
        assert input_handler.get_command.call_count == 2
        command_dispatcher.dispatch.assert_called_once_with("deposit")

    def test_start_calls_run_loop_once(
        self,
        application_cli,
        monkeypatch,
    ):
        run_loop = MagicMock()
        monkeypatch.setattr(application_cli, "_run_loop", run_loop)

        application_cli.start()

        run_loop.assert_called_once_with()

    def test_stop_can_be_called_repeatedly(
        self,
        application_cli,
        logger,
    ):
        application_cli.stop()
        application_cli.stop()

        assert application_cli._running is False
        assert logger.info.call_count == 2

    def test_start_stop_leaves_application_stopped(
        self,
        application_cli,
        monkeypatch,
    ):
        monkeypatch.setattr(application_cli, "_run_loop", MagicMock())

        application_cli.start()

        assert application_cli._running is False
