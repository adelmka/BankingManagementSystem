"""Tests for the existing DependencyContainer public contract."""

from unittest.mock import MagicMock, patch

import pytest

from application.dependency_container import DependencyContainer


class TestDependencyContainer:
    """Unit tests for the application composition root."""

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

    def test_supplied_config_is_retained(self, container, config):
        assert container.config is config

    def test_create_directories_is_called(self, config, logger):
        with patch(
            "application.dependency_container.get_logger",
            return_value=logger,
        ), patch("application.dependency_container.CustomerRepository"), patch(
            "application.dependency_container.AccountRepository"
        ), patch("application.dependency_container.TransactionRepository"), patch(
            "application.dependency_container.CustomerService"
        ), patch("application.dependency_container.AccountService"), patch(
            "application.dependency_container.TransactionService"
        ), patch("application.dependency_container.BankService"):
            DependencyContainer(config=config)

        config.create_directories.assert_called_once_with()

    def test_logger_is_created(self, config, logger):
        with patch(
            "application.dependency_container.get_logger",
            return_value=logger,
        ) as get_logger, patch(
            "application.dependency_container.CustomerRepository"
        ), patch("application.dependency_container.AccountRepository"), patch(
            "application.dependency_container.TransactionRepository"
        ), patch("application.dependency_container.CustomerService"), patch(
            "application.dependency_container.AccountService"
        ), patch("application.dependency_container.TransactionService"), patch(
            "application.dependency_container.BankService"
        ):
            container = DependencyContainer(config=config)

        get_logger.assert_called_once_with("application.dependency_container")
        assert container.logger is logger

    def test_repository_instances_are_created(self, container, dependencies):
        assert container.customer_repository is dependencies["customer_repository"]
        assert container.account_repository is dependencies["account_repository"]
        assert container.transaction_repository is dependencies["transaction_repository"]

    def test_customer_service_receives_repository(
        self, config, logger, dependencies
    ):
        with patch("application.dependency_container.get_logger", return_value=logger), patch(
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

    def test_account_service_receives_repositories(
        self, config, logger, dependencies
    ):
        with patch("application.dependency_container.get_logger", return_value=logger), patch(
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

    def test_transaction_service_receives_repositories(
        self, config, logger, dependencies
    ):
        with patch("application.dependency_container.get_logger", return_value=logger), patch(
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

    def test_bank_service_receives_services(self, config, logger, dependencies):
        with patch("application.dependency_container.get_logger", return_value=logger), patch(
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

    def test_public_properties_return_singletons(self, container, dependencies):
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

    def test_to_dict_contains_all_dependencies(
        self, container, config, logger, dependencies
    ):
        assert container.to_dict() == {
            "config": config,
            "logger": logger,
            **dependencies,
        }

    def test_build_validates_and_returns_container(self, config):
        logger = MagicMock()

        class TestContainer(DependencyContainer):
            def __init__(self, supplied_config):
                self._config = supplied_config
                self._logger = logger

            def validate(self):
                return True

        result = TestContainer.build(config)

        assert result.__class__ is TestContainer
        assert result.config is config
        assert result.logger is logger
        result.logger.info.assert_called_once_with(
            "Dependency Container successfully built."
        )

    def test_build_raises_when_validation_fails(self, config):
        logger = MagicMock()

        class TestContainer(DependencyContainer):
            def __init__(self, supplied_config):
                self._config = supplied_config
                self._logger = logger

            def validate(self):
                return False

        with pytest.raises(
            RuntimeError,
            match="Dependency container validation failed",
        ):
            TestContainer.build(config)

        logger.info.assert_not_called()

    def test_shutdown_logs_completion(self, container):
        assert container.shutdown() is None
        container.logger.info.assert_any_call(
            "Dependency Container shutdown completed."
        )

    def test_repr(self, container):
        assert repr(container) == "DependencyContainer(repositories=3, services=3)"

    def test_str(self, container):
        assert str(container) == "Banking Management System Dependency Container"

    def test_constructor_logs_lifecycle_messages(self, container):
        messages = [call.args[0] for call in container.logger.info.call_args_list]

        assert "Initializing Dependency Container..." in messages
        assert "Repositories initialized." in messages
        assert "Services initialized." in messages
        assert "BankService initialized." in messages

    def test_logger_property_returns_shared_logger(self, container, logger):
        assert container.logger is logger

    def test_config_property_returns_supplied_config(self, container, config):
        assert container.config is config

    def test_to_dict_values_match_public_properties(self, container):
        values = container.to_dict()

        assert values["customer_repository"] is container.customer_repository
        assert values["account_repository"] is container.account_repository
        assert values["transaction_repository"] is container.transaction_repository
        assert values["customer_service"] is container.customer_service
        assert values["account_service"] is container.account_service
        assert values["transaction_service"] is container.transaction_service
        assert values["bank_service"] is container.bank_service

    def test_validate_checks_all_required_dependencies(self, container):
        required = [
            "_customer_repository",
            "_account_repository",
            "_transaction_repository",
            "_customer_service",
            "_account_service",
            "_transaction_service",
            "_bank_service",
        ]

        for attribute in required:
            assert getattr(container, attribute) is not None

        assert container.validate() is True
