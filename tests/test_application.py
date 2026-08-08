"""
Tests for application/application.py.

These tests target the current Application contract without requiring
the real DependencyContainer or BankService to be constructed.
"""

from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from application.application import Application

from config import Config


@pytest.fixture
def config():
    """Return a minimal configuration object for isolated Application tests."""
    return SimpleNamespace(
        APP_NAME="Banking Management System",
    )

@pytest.fixture
def logger():
    """Return a mocked application logger."""
    return MagicMock()

class TestApplicationContainer:
    """Test fixtures and helpers for Application."""

    @pytest.fixture
    def config(self):
        return SimpleNamespace(APP_NAME="Banking Management System")

    @pytest.fixture
    def container(self):
        container = MagicMock()
        container.bank_service = MagicMock(name="bank_service")
        container.validate.return_value = True
        return container

    @pytest.fixture
    def logger(self):
        return MagicMock()

    @pytest.fixture
    def application(self, monkeypatch, config, container, logger):
        monkeypatch.setattr(
            "application.application.DependencyContainer.build",
            MagicMock(return_value=container),
        )
        monkeypatch.setattr(
            "application.application.get_logger",
            MagicMock(return_value=logger),
        )

        return Application(config=config)


def test_default_config_is_used_when_no_config_is_supplied(
    monkeypatch,
):
    container = MagicMock()
    logger = MagicMock()

    monkeypatch.setattr(
        "application.application.DependencyContainer.build",
        MagicMock(return_value=container),
    )
    monkeypatch.setattr(
        "application.application.get_logger",
        MagicMock(return_value=logger),
    )

    application = Application()

    assert application.config is Config


def test_supplied_config_is_retained(application, test_config):
    assert application.config is test_config


def test_container_is_built_with_supplied_config(
    monkeypatch,
    config,
    container,
    logger,
):
    build = MagicMock(return_value=container)

    monkeypatch.setattr(
        "application.application.DependencyContainer.build",
        build,
    )
    monkeypatch.setattr(
        "application.application.get_logger",
        MagicMock(return_value=logger),
    )

    Application(config=config)

    build.assert_called_once_with(config=config)


def test_logger_is_created_for_application_module(
    monkeypatch,
    config,
    container,
    logger,
):
    get_logger = MagicMock(return_value=logger)

    monkeypatch.setattr(
        "application.application.DependencyContainer.build",
        MagicMock(return_value=container),
    )
    monkeypatch.setattr(
        "application.application.get_logger",
        get_logger,
    )

    Application(config=config)

    get_logger.assert_called_once_with("application.application")


def test_initialization_logs_completion(
    application,
    logger,
):
    logger.info.assert_any_call("Application initialized.")


def test_bank_returns_container_bank_service(
    application,
    container,
):
    assert application.bank is container.bank_service


def test_bank_returns_same_facade_each_time(
    application,
):
    assert application.bank is application.bank


def test_config_returns_supplied_config(
    application,
    config,
):
    assert application.config is config


def test_is_running_delegates_to_container_validation(
    application,
    container,
):
    container.validate.reset_mock()
    container.validate.return_value = True

    assert application.is_running is True
    container.validate.assert_called_once_with()


def test_is_running_returns_false_when_container_validation_fails(
    application,
    container,
):
    container.validate.reset_mock()
    container.validate.return_value = False

    assert application.is_running is False
    container.validate.assert_called_once_with()


def test_shutdown_delegates_to_container(
    application,
    container,
):
    container.shutdown.reset_mock()

    application.shutdown()

    container.shutdown.assert_called_once_with()


def test_shutdown_logs_completion(
    application,
    container,
    logger,
):
    container.shutdown.reset_mock()
    logger.info.reset_mock()

    application.shutdown()

    logger.info.assert_called_once_with(
        "Application shutdown completed."
    )


def test_shutdown_does_not_rebuild_container(
    monkeypatch,
    config,
    container,
    logger,
):
    build = MagicMock(return_value=container)

    monkeypatch.setattr(
        "application.application.DependencyContainer.build",
        build,
    )
    monkeypatch.setattr(
        "application.application.get_logger",
        MagicMock(return_value=logger),
    )

    application = Application(config=config)
    application.shutdown()

    build.assert_called_once_with(config=config)


def test_bank_access_does_not_rebuild_container(
    monkeypatch,
    config,
    container,
    logger,
):
    build = MagicMock(return_value=container)

    monkeypatch.setattr(
        "application.application.DependencyContainer.build",
        build,
    )
    monkeypatch.setattr(
        "application.application.get_logger",
        MagicMock(return_value=logger),
    )

    application = Application(config=config)

    _ = application.bank
    _ = application.bank

    build.assert_called_once_with(config=config)


def test_config_access_does_not_rebuild_container(
    monkeypatch,
    config,
    container,
    logger,
):
    build = MagicMock(return_value=container)

    monkeypatch.setattr(
        "application.application.DependencyContainer.build",
        build,
    )
    monkeypatch.setattr(
        "application.application.get_logger",
        MagicMock(return_value=logger),
    )

    application = Application(config=config)

    _ = application.config
    _ = application.config

    build.assert_called_once_with(config=config)


def test_is_running_delegates_every_time_it_is_accessed(
    application,
    container,
):
    container.validate.reset_mock()
    container.validate.side_effect = [True, False]

    assert application.is_running is True
    assert application.is_running is False

    assert container.validate.call_count == 2


def test_shutdown_can_be_called_more_than_once(
    application,
    container,
):
    container.shutdown.reset_mock()

    application.shutdown()
    application.shutdown()

    assert container.shutdown.call_count == 2


def test_shutdown_propagates_container_shutdown_exception(
    application,
    container,
):
    container.shutdown.reset_mock()
    container.shutdown.side_effect = RuntimeError("shutdown failed")

    with pytest.raises(
        RuntimeError,
        match="shutdown failed",
    ):
        application.shutdown()


def test_initialization_propagates_container_build_exception(
    monkeypatch,
    config,
    logger,
):
    monkeypatch.setattr(
        "application.application.get_logger",
        MagicMock(return_value=logger),
    )
    monkeypatch.setattr(
        "application.application.DependencyContainer.build",
        MagicMock(
            side_effect=RuntimeError("build failed")
        ),
    )

    with pytest.raises(
        RuntimeError,
        match="build failed",
    ):
        Application(config=config)


def test_is_running_propagates_validation_exception(
    application,
    container,
):
    container.validate.reset_mock()
    container.validate.side_effect = RuntimeError(
        "validation failed"
    )

    with pytest.raises(
        RuntimeError,
        match="validation failed",
    ):
        _ = application.is_running


def test_repr_uses_class_name_and_running_state(
    application,
    container,
):
    container.validate.reset_mock()
    container.validate.return_value = True

    assert repr(application) == "Application(running=True)"
    container.validate.assert_called_once_with()


def test_repr_reflects_not_running_state(
    application,
    container,
):
    container.validate.reset_mock()
    container.validate.return_value = False

    assert repr(application) == "Application(running=False)"
    container.validate.assert_called_once_with()


def test_str_returns_application_name(
    application,
    config,
):
    assert str(application) == config.APP_NAME


def test_str_reflects_custom_application_name(
    monkeypatch,
    container,
    logger,
):
    config = SimpleNamespace(APP_NAME="Custom BMS")

    monkeypatch.setattr(
        "application.application.DependencyContainer.build",
        MagicMock(return_value=container),
    )
    monkeypatch.setattr(
        "application.application.get_logger",
        MagicMock(return_value=logger),
    )

    application = Application(config=config)

    assert str(application) == "Custom BMS"


def test_application_retains_private_container_reference(
    application,
    container,
):
    assert application._container is container


def test_application_retains_private_logger_reference(
    application,
    logger,
):
    assert application._logger is logger


def test_application_initialization_order_builds_container_before_log(
    monkeypatch,
    config,
    container,
):
    events = []
    logger = MagicMock()

    def build(*, config):
        events.append("build")
        return container

    def info(message):
        events.append(("log", message))

    monkeypatch.setattr(
        "application.application.DependencyContainer.build",
        build,
    )
    monkeypatch.setattr(
        "application.application.get_logger",
        MagicMock(return_value=logger),
    )
    logger.info.side_effect = info

    Application(config=config)

    assert events == [
        "build",
        ("log", "Application initialized."),
    ]


def test_shutdown_logs_only_after_container_shutdown(
    application,
    container,
    logger,
):
    events = []

    def shutdown():
        events.append("shutdown")

    def info(message):
        events.append(("log", message))

    container.shutdown.reset_mock()
    container.shutdown.side_effect = shutdown
    logger.info.reset_mock()
    logger.info.side_effect = info

    application.shutdown()

    assert events == [
        "shutdown",
        ("log", "Application shutdown completed."),
    ]


def test_bank_property_exposes_bank_service_facade_only(
    application,
    container,
):
    assert application.bank is container.bank_service
    assert not hasattr(application, "customer_service")
    assert not hasattr(application, "account_service")
    assert not hasattr(application, "transaction_service")


def test_application_is_independent_of_container_bank_service_type(
    application,
    container,
):
    custom_facade = object()
    container.bank_service = custom_facade

    assert application.bank is custom_facade


def test_custom_config_object_can_be_used_without_mutation(
    monkeypatch,
    container,
    logger,
):
    config = SimpleNamespace(APP_NAME="Test Banking App")
    original_name = config.APP_NAME

    monkeypatch.setattr(
        "application.application.DependencyContainer.build",
        MagicMock(return_value=container),
    )
    monkeypatch.setattr(
        "application.application.get_logger",
        MagicMock(return_value=logger),
    )

    application = Application(config=config)

    assert application.config is config
    assert config.APP_NAME == original_name
    assert str(application) == original_name
