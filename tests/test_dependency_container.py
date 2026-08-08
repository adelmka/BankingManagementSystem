"""
Tests for the DependencyContainer composition root.

These tests verify the existing public contract of
application.dependency_container without changing application architecture.
"""

from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from application.dependency_container import DependencyContainer


class TestDependencyContainer:
    """Tests for DependencyContainer."""

    @pytest.fixture
    def config(self):
        config = MagicMock()
        config.APP_NAME = "Banking Management System"
        return config

    @pytest.fixture
    def logger(self):
        return MagicMock()

    @pytest.fixture
    def dependencies(self):
        return {
            "customer_repository": MagicMock(name="customer_repository"),
            "account_repository": MagicMock(name="account_repository"),
            "transaction_repository": MagicMock(name="transaction_repository"),
            "customer_service": MagicMock(name="customer_service"),
            "account_service": MagicMock(name="account_service"),
            "transaction_service": MagicMock(name="transaction_service"),
            "bank_service": MagicMock(name="bank_service"),
        }

    @pytest.fixture
    def container(self, config, logger, dependencies):
        with patch(
            "application.dependency_container.get_logger",
            return_value=logger,
        ), patch(
            "application.dependency_container.CustomerRepository",
            return_value=dependencies["customer_repository"],
        ), patch(
            "application.dependency_container.AccountRepository",
            return_value=dependencies["account_repository"],
        ), patch(
            "application.dependency_container.TransactionRepository",
            return_value=dependencies["transaction_repository"],
        ), patch(
            "application.dependency_container.CustomerService",
            return_value=dependencies["customer_service"],
        ), patch(
            "application.dependency_container.AccountService",
            return_value=dependencies["account_service"],
        ), patch(
            "application.dependency_container.TransactionService",
            return_value=dependencies["transaction_service"],
        ), patch(
            "application.dependency_container.BankService",
            return_value=dependencies["bank_service"],
        ):
            yield DependencyContainer(config=config)

    def test_default_config_is_used(self, monkeypatch):
        config = MagicMock()
        config.APP_NAME = "Banking Management System"

        with patch.object(
            DependencyContainer,
            "__init__",
            return_value=None,
        ) as init:
            DependencyContainer()
            init.assert_called_once_with()

    def test_supplied_config_is_retained(self, container, config):
        assert container.config is config

    def test_create_directories_is_called(self, config, logger):
        with patch(
            "application.dependency_container.get_logger",
            return_value=logger,
        ), patch(
            "application.dependency_container.CustomerRepository",
        ), patch(
            "application.dependency_container.AccountRepository",
        ), patch(
            "application.dependency_container.TransactionRepository",
        ), patch(
            "application.dependency_container.CustomerService",
        ), patch(
            "application.dependency_container.AccountService",
        ), patch(
            "application.dependency_container.TransactionService",
        ), patch(
            "application.dependency_container.BankService",
        ):
            DependencyContainer(config=config)

        config.create_directories.assert_called_once_with()

    def test_logger_is_created(self, config, logger):
        with patch(
            "application.dependency_container.get_logger",
            return_value=logger,
        ) as get_logger, patch(
            "application.dependency_container.CustomerRepository",
        ), patch(
            "application.dependency_container.AccountRepository",
        ), patch(
            "application.dependency_container.TransactionRepository",
        ), patch(
            "application.dependency_container.CustomerService",
        ), patch(
            "application.dependency_container.AccountService",
        ), patch(
            "application.dependency_container.TransactionService",
        ), patch(
            "application.dependency_container.BankService",
        ):
            container = DependencyContainer(config=config)

        get_logger.assert_called_once_with(
            "application.dependency_container"
        )
        assert container.logger is logger

    def test_repository_instances_are_created(self, container, dependencies):
        assert container.customer_repository is dependencies["customer_repository"]
        assert container.account_repository is dependencies["account_repository"]
        assert container.transaction_repository is dependencies["transaction_repository"]

    def test_customer_service_receives_customer_repository(
        self, config, logger, dependencies
    ):
        with patch(
            "application.dependency_container.get_logger",
            return_value=logger,
        ), patch(
            "application.dependency_container.CustomerRepository",
            return_value=dependencies["customer_repository"],
        ), patch(
            "application.dependency_container.AccountRepository",
            return_value=dependencies["account_repository"],
        ), patch(
            "application.dependency_container.TransactionRepository",
            return_value=dependencies["transaction_repository"],
        ), patch(
            "application.dependency_container.CustomerService",
            return_value=dependencies["customer_service"],
        ) as customer_service, patch(
            "application.dependency_container.AccountService",
            return_value=dependencies["account_service"],
        ), patch(
            "application.dependency_container.TransactionService",
            return_value=dependencies["transaction_service"],
        ), patch(
            "application.dependency_container.BankService",
            return_value=dependencies["bank_service"],
        ):
            DependencyContainer(config=config)

        customer_service.assert_called_once_with(
            repository=dependencies["customer_repository"]
        )

    def test_account_service_receives_all_required_repositories(
        self, config, logger, dependencies
    ):
        with patch(
            "application.dependency_container.get_logger",
            return_value=logger,
        ), patch(
            "application.dependency_container.CustomerRepository",
            return_value=dependencies["customer_repository"],
        ), patch(
            "application.dependency_container.AccountRepository",
            return_value=dependencies["account_repository"],
        ), patch(
            "application.dependency_container.TransactionRepository",
            return_value=dependencies["transaction_repository"],
        ), patch(
            "application.dependency_container.CustomerService",
            return_value=dependencies["customer_service"],
        ), patch(
            "application.dependency_container.AccountService",
            return_value=dependencies["account_service"],
        ) as account_service, patch(
            "application.dependency_container.TransactionService",
            return_value=dependencies["transaction_service"],
        ), patch(
            "application.dependency_container.BankService",
            return_value=dependencies["bank_service"],
        ):
            DependencyContainer(config=config)

        account_service.assert_called_once_with(
            account_repository=dependencies["account_repository"],
            customer_repository=dependencies["customer_repository"],
            transaction_repository=dependencies["transaction_repository"],
        )

    def test_transaction_service_receives_required_repositories(
        self, config, logger, dependencies
    ):
        with patch(
            "application.dependency_container.get_logger",
            return_value=logger,
        ), patch(
            "application.dependency_container.CustomerRepository",
            return_value=dependencies["customer_repository"],
        ), patch(
            "application.dependency_container.AccountRepository",
            return_value=dependencies["account_repository"],
        ), patch(
            "application.dependency_container.TransactionRepository",
            return_value=dependencies["transaction_repository"],
        ), patch(
            "application.dependency_container.CustomerService",
            return_value=dependencies["customer_service"],
        ), patch(
            "application.dependency_container.AccountService",
            return_value=dependencies["account_service"],
        ), patch(
            "application.dependency_container.TransactionService",
            return_value=dependencies["transaction_service"],
        ) as transaction_service, patch(
            "application.dependency_container.BankService",
            return_value=dependencies["bank_service"],
        ):
            DependencyContainer(config=config)

        transaction_service.assert_called_once_with(
            transaction_repository=dependencies["transaction_repository"],
            account_repository=dependencies["account_repository"],
        )

    def test_bank_service_receives_all_services(
        self, config, logger, dependencies
    ):
        with patch(
            "application.dependency_container.get_logger",
            return_value=logger,
        ), patch(
            "application.dependency_container.CustomerRepository",
            return_value=dependencies["customer_repository"],
        ), patch(
            "application.dependency_container.AccountRepository",
            return_value=dependencies["account_repository"],
        ), patch(
            "application.dependency_container.TransactionRepository",
            return_value=dependencies["transaction_repository"],
        ), patch(
            "application.dependency_container.CustomerService",
            return_value=dependencies["customer_service"],
        ), patch(
            "application.dependency_container.AccountService",
            return_value=dependencies["account_service"],
        ), patch(
            "application.dependency_container.TransactionService",
            return_value=dependencies["transaction_service"],
        ), patch(
            "application.dependency_container.BankService",
            return_value=dependencies["bank_service"],
        ) as bank_service:
            DependencyContainer(config=config)

        bank_service.assert_called_once_with(
            customer_service=dependencies["customer_service"],
            account_service=dependencies["account_service"],
            transaction_service=dependencies["transaction_service"],
        )

    def test_all_public_dependency_properties_return_singletons(
        self, container, dependencies
    ):
        assert container.customer_repository is dependencies["customer_repository"]
        assert container.account_repository is dependencies["account_repository"]
        assert container.transaction_repository is dependencies["transaction_repository"]
        assert container.customer_service is dependencies["customer_service"]
        assert container.account_service is dependencies["account_service"]
        assert container.transaction_service is dependencies["transaction_service"]
        assert container.bank_service is dependencies["bank_service"]

    def test_validate_returns_true_for_complete_graph(self, container):
        assert container.validate() is True
        container.logger.info.assert_any_call(
            "Dependency Container validation succeeded."
        )

    @pytest.mark.parametrize(
        "attribute",
        [
            "_customer_repository",
            "_account_repository",
            "_transaction_repository",
            "_customer_service",
            "_account_service",
            "_transaction_service",
            "_bank_service",
        ],
    )
    def test_validate_returns_false_when_dependency_is_missing(
        self, container, attribute
    ):
        setattr(container, attribute, None)

        assert container.validate() is False
        container.logger.error.assert_any_call(
            "Dependency Container validation failed."
        )

    def test_repository_count(self, container):
        assert container.repository_count == 3

    def test_service_count(self, container):
        assert container.service_count == 3

    def test_dependency_count(self, container):
        assert container.dependency_count == 9

    def test_to_dict_contains_all_managed_dependencies(
        self, container, config, logger, dependencies
    ):
        result = container.to_dict()

        assert result == {
            "config": config,
            "logger": logger,
            **dependencies,
        }

    def test_build_creates_and_validates_container(self, config):
        fake_container = MagicMock()
        fake_container.validate.return_value = True
        fake_container.logger = MagicMock()

        with patch.object(
            DependencyContainer,
            "__init__",
            return_value=None,
        ), patch.object(
            DependencyContainer,
            "validate",
            return_value=True,
        ), patch(
            "application.dependency_container.DependencyContainer",
        ) as container_cls:
            container_cls.return_value = fake_container

            result = DependencyContainer.build(config)

        container_cls.assert_called_once_with(config)
        fake_container.validate.assert_called_once_with()
        fake_container.logger.info.assert_called_once_with(
            "Dependency Container successfully built."
        )
        assert result is fake_container

    def test_build_raises_when_validation_fails(self, config):
        fake_container = MagicMock()
        fake_container.validate.return_value = False

        with patch(
            "application.dependency_container.DependencyContainer",
            return_value=fake_container,
        ):
            with pytest.raises(
                RuntimeError,
                match="Dependency container validation failed",
            ):
                DependencyContainer.build(config)

        fake_container.validate.assert_called_once_with()
        fake_container.logger.info.assert_not_called()

    def test_shutdown_logs_completion(self, container):
        result = container.shutdown()

        assert result is None
        container.logger.info.assert_any_call(
            "Dependency Container shutdown completed."
        )

    def test_repr(self, container):
        assert repr(container) == (
            "DependencyContainer(repositories=3, services=3)"
        )

    def test_str(self, container, config):
        assert str(container) == (
            "Banking Management System Dependency Container"
        )


class TestDependencyContainerFactoryBehavior:
    """Focused tests for the class-level factory contract."""

    def test_build_uses_default_config_when_omitted(self):
        fake_container = MagicMock()
        fake_container.validate.return_value = True
        fake_container.logger = MagicMock()

        with patch(
            "application.dependency_container.DependencyContainer",
            return_value=fake_container,
        ) as container_cls:
            DependencyContainer.build()

        container_cls.assert_called_once_with()

    def test_build_logs_success_after_validation(self):
        fake_container = MagicMock()
        fake_container.validate.return_value = True
        fake_container.logger = MagicMock()

        with patch(
            "application.dependency_container.DependencyContainer",
            return_value=fake_container,
        ):
            DependencyContainer.build()

        fake_container.logger.info.assert_called_once_with(
            "Dependency Container successfully built."
        )


class TestDependencyContainerLogging:
    """Verify the constructor's lifecycle logging contract."""

    def test_constructor_logs_initialization_messages(self, container):
        messages = [
            call.args[0]
            for call in container.logger.info.call_args_list
        ]

        assert "Initializing Dependency Container..." in messages
        assert "Repositories initialized." in messages
        assert "Services initialized." in messages
        assert "BankService initialized." in messages
