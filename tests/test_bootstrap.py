"""
Tests for application/bootstrap.py.

These tests target the current Bootstrap public contract and isolate
startup orchestration by mocking StorageInitializer and Application.
No production architecture is changed by this test suite.
"""

from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from application.bootstrap import Bootstrap


@pytest.fixture
def config():
    """Return a minimal configuration object for Bootstrap tests."""
    return SimpleNamespace(APP_NAME="Banking Management System")


@pytest.fixture
def logger():
    return MagicMock()


@pytest.fixture
def storage_initializer():
    initializer = MagicMock()
    initializer.validate.return_value = True
    return initializer


@pytest.fixture
def application():
    return MagicMock(name="application")


@pytest.fixture
def bootstrap(config, logger, storage_initializer):
    with patch(
        "application.bootstrap.get_logger",
        return_value=logger,
    ), patch(
        "application.bootstrap.StorageInitializer",
        return_value=storage_initializer,
    ):
        instance = Bootstrap(config=config)

    return instance


def test_default_config_is_retained():
    with patch("application.bootstrap.get_logger"), patch(
        "application.bootstrap.StorageInitializer"
    ) as initializer_cls:
        bootstrap = Bootstrap()

    assert bootstrap._config is not None
    initializer_cls.assert_called_once()
    assert initializer_cls.call_args.kwargs["config"] is bootstrap._config


def test_supplied_config_is_retained(config, logger, storage_initializer):
    with patch(
        "application.bootstrap.get_logger",
        return_value=logger,
    ), patch(
        "application.bootstrap.StorageInitializer",
        return_value=storage_initializer,
    ):
        bootstrap = Bootstrap(config=config)

    assert bootstrap._config is config
    assert bootstrap._storage_initializer is storage_initializer


def test_storage_initializer_receives_supplied_config(
    config,
    logger,
):
    with patch(
        "application.bootstrap.get_logger",
        return_value=logger,
    ), patch(
        "application.bootstrap.StorageInitializer"
    ) as initializer_cls:
        Bootstrap(config=config)

    initializer_cls.assert_called_once_with(config=config)


def test_logger_is_created_for_bootstrap(logger, config, storage_initializer):
    with patch(
        "application.bootstrap.get_logger",
        return_value=logger,
    ) as get_logger, patch(
        "application.bootstrap.StorageInitializer",
        return_value=storage_initializer,
    ):
        bootstrap = Bootstrap(config=config)

    get_logger.assert_called_once_with("application.bootstrap")
    assert bootstrap._logger is logger


def test_initialize_returns_application(
    bootstrap,
    application,
    storage_initializer,
):
    with patch(
        "application.bootstrap.Application",
        return_value=application,
    ) as application_cls:
        result = bootstrap.initialize()

    assert result is application
    storage_initializer.initialize.assert_called_once_with()
    storage_initializer.validate.assert_called_once_with()
    application_cls.assert_called_once_with(config=bootstrap._config)


def test_initialize_initializes_storage_before_validation(
    bootstrap,
    application,
    storage_initializer,
):
    calls = []
    storage_initializer.initialize.side_effect = lambda: calls.append("initialize")
    storage_initializer.validate.side_effect = lambda: calls.append("validate") or True

    with patch(
        "application.bootstrap.Application",
        return_value=application,
    ):
        bootstrap.initialize()

    assert calls == ["initialize", "validate"]


def test_initialize_constructs_application_after_storage_validation(
    bootstrap,
    application,
    storage_initializer,
):
    calls = []
    storage_initializer.initialize.side_effect = lambda: calls.append("initialize")
    storage_initializer.validate.side_effect = lambda: calls.append("validate") or True

    def construct_application(*, config):
        calls.append("application")
        return application

    with patch(
        "application.bootstrap.Application",
        side_effect=construct_application,
    ):
        result = bootstrap.initialize()

    assert result is application
    assert calls == ["initialize", "validate", "application"]


def test_initialize_raises_when_storage_validation_fails(
    bootstrap,
    storage_initializer,
):
    storage_initializer.validate.return_value = False

    with patch("application.bootstrap.Application") as application_cls:
        with pytest.raises(
            RuntimeError,
            match="Application storage validation failed",
        ):
            bootstrap.initialize()

    storage_initializer.initialize.assert_called_once_with()
    storage_initializer.validate.assert_called_once_with()
    application_cls.assert_not_called()


def test_initialize_does_not_construct_application_when_storage_initialization_raises(
    bootstrap,
    storage_initializer,
):
    storage_initializer.initialize.side_effect = RuntimeError("storage failure")

    with patch("application.bootstrap.Application") as application_cls:
        with pytest.raises(RuntimeError, match="storage failure"):
            bootstrap.initialize()

    storage_initializer.validate.assert_not_called()
    application_cls.assert_not_called()


def test_initialize_propagates_storage_validation_exception(
    bootstrap,
    storage_initializer,
):
    storage_initializer.validate.side_effect = RuntimeError("validation failure")

    with patch("application.bootstrap.Application") as application_cls:
        with pytest.raises(RuntimeError, match="validation failure"):
            bootstrap.initialize()

    application_cls.assert_not_called()


def test_initialize_logs_start_and_completion(
    bootstrap,
    application,
    storage_initializer,
):
    with patch(
        "application.bootstrap.Application",
        return_value=application,
    ):
        bootstrap.initialize()

    messages = [call.args[0] for call in bootstrap._logger.info.call_args_list]

    assert "Starting Banking Management System..." in messages
    assert "Application bootstrap completed." in messages


def test_initialize_does_not_log_completion_on_validation_failure(
    bootstrap,
    storage_initializer,
):
    storage_initializer.validate.return_value = False

    with pytest.raises(RuntimeError):
        bootstrap.initialize()

    messages = [call.args[0] for call in bootstrap._logger.info.call_args_list]

    assert "Starting Banking Management System..." in messages
    assert "Application bootstrap completed." not in messages


def test_repr_reports_ready_state(bootstrap):
    assert repr(bootstrap) == "Bootstrap(ready=True)"


def test_str_uses_config_application_name(bootstrap, config):
    assert str(bootstrap) == "Banking Management System Bootstrap"


def test_initialize_passes_same_config_to_application(
    bootstrap,
    application,
):
    with patch(
        "application.bootstrap.Application",
        return_value=application,
    ) as application_cls:
        bootstrap.initialize()

    application_cls.assert_called_once_with(config=bootstrap._config)


def test_initialize_returns_exact_application_instance(
    bootstrap,
    application,
):
    with patch(
        "application.bootstrap.Application",
        return_value=application,
    ):
        assert bootstrap.initialize() is application
