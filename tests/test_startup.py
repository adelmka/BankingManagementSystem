"""
Tests for application/startup.py.

These tests target the current startup public contract and isolate
startup/shutdown orchestration by mocking Bootstrap, Application, and
the module-level logger. No production architecture is changed by this
 test suite.
"""

from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from application.startup import shutdown_application, start_application


@pytest.fixture
def config():
    """Return a minimal configuration object for startup tests."""
    return SimpleNamespace(APP_NAME="Banking Management System")


@pytest.fixture
def logger():
    return MagicMock()


@pytest.fixture
def application():
    return MagicMock(name="application")


def test_start_application_uses_supplied_config(config, application, logger):
    with patch("application.startup._logger", logger), patch(
        "application.startup.Bootstrap"
    ) as bootstrap_cls:
        bootstrap_cls.return_value.initialize.return_value = application

        result = start_application(config=config)

    assert result is application
    bootstrap_cls.assert_called_once_with(config=config)
    bootstrap_cls.return_value.initialize.assert_called_once_with()


def test_start_application_returns_exact_application_instance(application, logger):
    with patch("application.startup._logger", logger), patch(
        "application.startup.Bootstrap"
    ) as bootstrap_cls:
        bootstrap_cls.return_value.initialize.return_value = application

        result = start_application()

    assert result is application


def test_start_application_creates_bootstrap_with_default_config(logger, application):
    with patch("application.startup._logger", logger), patch(
        "application.startup.Bootstrap"
    ) as bootstrap_cls:
        bootstrap_cls.return_value.initialize.return_value = application

        start_application()

    bootstrap_cls.assert_called_once()
    assert "config" in bootstrap_cls.call_args.kwargs


def test_start_application_initializes_bootstrap_once(config, application, logger):
    with patch("application.startup._logger", logger), patch(
        "application.startup.Bootstrap"
    ) as bootstrap_cls:
        bootstrap_cls.return_value.initialize.return_value = application

        start_application(config=config)

    bootstrap_cls.return_value.initialize.assert_called_once_with()


def test_start_application_logs_launch_message(config, application, logger):
    with patch("application.startup._logger", logger), patch(
        "application.startup.Bootstrap"
    ) as bootstrap_cls:
        bootstrap_cls.return_value.initialize.return_value = application

        start_application(config=config)

    messages = [call.args[0] for call in logger.info.call_args_list]
    assert "Launching Banking Management System..." in messages


def test_start_application_logs_success_message(config, application, logger):
    with patch("application.startup._logger", logger), patch(
        "application.startup.Bootstrap"
    ) as bootstrap_cls:
        bootstrap_cls.return_value.initialize.return_value = application

        start_application(config=config)

    messages = [call.args[0] for call in logger.info.call_args_list]
    assert "Banking Management System started successfully." in messages


def test_start_application_logs_launch_before_success(config, application, logger):
    with patch("application.startup._logger", logger), patch(
        "application.startup.Bootstrap"
    ) as bootstrap_cls:
        bootstrap_cls.return_value.initialize.return_value = application

        start_application(config=config)

    messages = [call.args[0] for call in logger.info.call_args_list]
    launch_index = messages.index("Launching Banking Management System...")
    success_index = messages.index(
        "Banking Management System started successfully."
    )
    assert launch_index < success_index


def test_start_application_does_not_log_success_when_initialization_fails(
    config,
    logger,
):
    with patch("application.startup._logger", logger), patch(
        "application.startup.Bootstrap"
    ) as bootstrap_cls:
        bootstrap_cls.return_value.initialize.side_effect = RuntimeError(
            "startup failure"
        )

        with pytest.raises(RuntimeError, match="startup failure"):
            start_application(config=config)

    messages = [call.args[0] for call in logger.info.call_args_list]
    assert "Launching Banking Management System..." in messages
    assert "Banking Management System started successfully." not in messages


def test_start_application_propagates_bootstrap_exception(config, logger):
    with patch("application.startup._logger", logger), patch(
        "application.startup.Bootstrap"
    ) as bootstrap_cls:
        bootstrap_cls.return_value.initialize.side_effect = ValueError(
            "invalid startup state"
        )

        with pytest.raises(ValueError, match="invalid startup state"):
            start_application(config=config)


def test_start_application_does_not_construct_application_directly(
    config,
    application,
    logger,
):
    with patch("application.startup._logger", logger), patch(
        "application.startup.Bootstrap"
    ) as bootstrap_cls, patch(
        "application.startup.Application"
    ) as application_cls:
        bootstrap_cls.return_value.initialize.return_value = application

        result = start_application(config=config)

    assert result is application
    application_cls.assert_not_called()


def test_shutdown_application_calls_application_shutdown(application, logger):
    with patch("application.startup._logger", logger):
        result = shutdown_application(application)

    assert result is None
    application.shutdown.assert_called_once_with()


def test_shutdown_application_logs_stopped_message(application, logger):
    with patch("application.startup._logger", logger):
        shutdown_application(application)

    messages = [call.args[0] for call in logger.info.call_args_list]
    assert "Banking Management System stopped." in messages


def test_shutdown_application_logs_after_shutdown(application, logger):
    events = []
    application.shutdown.side_effect = lambda: events.append("shutdown")
    logger.info.side_effect = lambda message: events.append(message)

    with patch("application.startup._logger", logger):
        shutdown_application(application)

    assert events == [
        "shutdown",
        "Banking Management System stopped.",
    ]


def test_shutdown_application_propagates_shutdown_exception(application, logger):
    application.shutdown.side_effect = RuntimeError("shutdown failure")

    with patch("application.startup._logger", logger):
        with pytest.raises(RuntimeError, match="shutdown failure"):
            shutdown_application(application)

    logger.info.assert_not_called()


def test_shutdown_application_does_not_swallow_application_errors(
    application,
    logger,
):
    application.shutdown.side_effect = ValueError("application error")

    with patch("application.startup._logger", logger):
        with pytest.raises(ValueError, match="application error"):
            shutdown_application(application)


def test_shutdown_application_accepts_application_like_object(logger):
    application = SimpleNamespace(shutdown=MagicMock())

    with patch("application.startup._logger", logger):
        shutdown_application(application)

    application.shutdown.assert_called_once_with()


def test_start_application_passes_same_config_object_to_bootstrap(
    config,
    application,
    logger,
):
    with patch("application.startup._logger", logger), patch(
        "application.startup.Bootstrap"
    ) as bootstrap_cls:
        bootstrap_cls.return_value.initialize.return_value = application

        start_application(config=config)

    assert bootstrap_cls.call_args.args == ()
    assert bootstrap_cls.call_args.kwargs["config"] is config


def test_start_application_constructs_bootstrap_before_initialize(
    config,
    application,
    logger,
):
    events = []

    def construct_bootstrap(*, config):
        events.append(("bootstrap", config))
        bootstrap = MagicMock()
        bootstrap.initialize.side_effect = lambda: (
            events.append(("initialize",)) or application
        )
        return bootstrap

    with patch("application.startup._logger", logger), patch(
        "application.startup.Bootstrap",
        side_effect=construct_bootstrap,
    ):
        result = start_application(config=config)

    assert result is application
    assert events == [
        ("bootstrap", config),
        ("initialize",),
    ]


def test_start_application_returns_initialized_application_even_if_logger_is_mocked(
    config,
    application,
):
    logger = MagicMock()

    with patch("application.startup._logger", logger), patch(
        "application.startup.Bootstrap"
    ) as bootstrap_cls:
        bootstrap_cls.return_value.initialize.return_value = application

        result = start_application(config=config)

    assert result is application


def test_shutdown_application_returns_none(application, logger):
    with patch("application.startup._logger", logger):
        assert shutdown_application(application) is None


def test_start_application_success_log_is_not_emitted_before_initialize(
    config,
    application,
    logger,
):
    events = []
    logger.info.side_effect = lambda message: events.append(message)

    def initialize():
        events.append("initialize")
        return application

    with patch("application.startup._logger", logger), patch(
        "application.startup.Bootstrap"
    ) as bootstrap_cls:
        bootstrap_cls.return_value.initialize.side_effect = initialize
        start_application(config=config)

    assert events == [
        "Launching Banking Management System...",
        "initialize",
        "Banking Management System started successfully.",
    ]
