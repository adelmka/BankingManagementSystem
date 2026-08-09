"""
====================================================================
Banking Management System (BMS)

File        : dependency_container.py
Description : Dependency Injection Container

This module is the application's composition root. It creates and
owns every shared dependency required by the Banking Management
System.

Responsibilities
----------------
• Create repositories
• Create services
• Create the BankService façade
• Expose shared singleton instances
• Provide one fully initialized object graph

No business logic should exist in this module.

Author      : adelmka / ChatGPT
Python      : 3.13+
====================================================================
"""

from __future__ import annotations

from typing import Optional

from config import Config

from repositories.customer_repository import CustomerRepository
from repositories.account_repository import AccountRepository
from repositories.transaction_repository import TransactionRepository

from services.customer_service import CustomerService
from services.account_service import AccountService
from services.transaction_service import TransactionService
from services.bank_service import BankService

from utils.logger import get_logger


class DependencyContainer:
    """
    Central dependency injection container.

    The container creates every singleton dependency used by the
    application and provides a single access point for them.

    Lifetime
    --------
    One DependencyContainer instance should exist for the entire
    lifetime of the application.
    """

    #################################################################
    # Construction
    #################################################################

    def __init__(
        self,
        config: type[Config] = Config
    ) -> None:
        """
        Create the application dependency graph.

        Parameters
        ----------
        config:
            Configuration class to be used by the application.
        """

        self._config = config

        #
        # Ensure the application filesystem exists.
        #
        self._config.create_directories()

        #
        # Logger
        #
        self._logger = get_logger(__name__)

        self._logger.info(
            "Initializing Dependency Container..."
        )

        #
        # ----------------------------------------------------------
        # Repository Layer
        # ----------------------------------------------------------
        #

        self._customer_repository = CustomerRepository()

        self._account_repository = AccountRepository()

        self._transaction_repository = (
            TransactionRepository()
        )

        self._logger.info(
            "Repositories initialized."
        )

        #
        # ----------------------------------------------------------
        # Service Layer
        # ----------------------------------------------------------
        #

        self._customer_service = CustomerService(
            repository=self._customer_repository
        )

        self._account_service = AccountService(
            account_repository=self._account_repository,
            customer_repository=self._customer_repository,
            transaction_repository=self._transaction_repository
        )

        self._transaction_service = (
            TransactionService(
                transaction_repository=self._transaction_repository,
                account_repository=self._account_repository
            )
        )

        self._logger.info(
            "Services initialized."
        )

        #
        # ----------------------------------------------------------
        # Application Façade
        # ----------------------------------------------------------
        #

        self._bank_service = BankService(
            customer_service=self._customer_service,
            account_service=self._account_service,
            transaction_service=self._transaction_service
        )

        self._logger.info(
            "BankService initialized."
        )

# PART 2

    #################################################################
    # Configuration
    #################################################################

    @property
    def config(self) -> type[Config]:
        """
        Return the application configuration.
        """
        return self._config

    #################################################################
    # Logger
    #################################################################

    @property
    def logger(self):
        """
        Return the shared application logger.
        """
        return self._logger

    #################################################################
    # Repositories
    #################################################################

    @property
    def customer_repository(self) -> CustomerRepository:
        """
        Return the singleton CustomerRepository.
        """
        return self._customer_repository

    @property
    def account_repository(self) -> AccountRepository:
        """
        Return the singleton AccountRepository.
        """
        return self._account_repository

    @property
    def transaction_repository(self) -> TransactionRepository:
        """
        Return the singleton TransactionRepository.
        """
        return self._transaction_repository

    #################################################################
    # Services
    #################################################################

    @property
    def customer_service(self) -> CustomerService:
        """
        Return the singleton CustomerService.
        """
        return self._customer_service

    @property
    def account_service(self) -> AccountService:
        """
        Return the singleton AccountService.
        """
        return self._account_service

    @property
    def transaction_service(self) -> TransactionService:
        """
        Return the singleton TransactionService.
        """
        return self._transaction_service

    #################################################################
    # Application Façade
    #################################################################

    @property
    def bank_service(self) -> BankService:
        """
        Return the application's BankService façade.
        """
        return self._bank_service

    #################################################################
    # Validation
    #################################################################

    def validate(self) -> bool:
        """
        Validate that the dependency graph has been
        successfully created.

        Returns
        -------
        bool
            True if every dependency exists.
        """

        required_dependencies = (
            self._customer_repository,
            self._account_repository,
            self._transaction_repository,
            self._customer_service,
            self._account_service,
            self._transaction_service,
            self._bank_service,
        )

        valid = all(
            dependency is not None
            for dependency in required_dependencies
        )

        if valid:
            self._logger.info(
                "Dependency Container validation succeeded."
            )
        else:
            self._logger.error(
                "Dependency Container validation failed."
            )

        return valid

    #################################################################
    # Information
    #################################################################

    @property
    def repository_count(self) -> int:
        """
        Number of managed repositories.
        """
        return 3

    @property
    def service_count(self) -> int:
        """
        Number of managed services.
        """
        return 3

    @property
    def dependency_count(self) -> int:
        """
        Total managed singleton dependencies.
        """

        return (
            self.repository_count
            + self.service_count
            + 1          # BankService
            + 1          # Logger
            + 1          # Config
        )

    #################################################################
    # Utility Methods
    #################################################################

    def to_dict(self) -> dict[str, object]:
        """
        Return all managed dependencies as a dictionary.
        """

        return {
            "config": self._config,
            "logger": self._logger,
            "customer_repository": self._customer_repository,
            "account_repository": self._account_repository,
            "transaction_repository": self._transaction_repository,
            "customer_service": self._customer_service,
            "account_service": self._account_service,
            "transaction_service": self._transaction_service,
            "bank_service": self._bank_service,
        }

# PART 3

    #################################################################
    # Factory
    #################################################################

    @classmethod
    def build(
        cls,
        config: type[Config] = Config
    ) -> "DependencyContainer":
        """
        Build and validate a fully initialized dependency container.
        """

        container = cls(config)

        if not container.validate():
            raise RuntimeError(
                "Dependency container validation failed."
            )

        container.logger.info(
            "Dependency Container successfully built."
        )

        return container

    #################################################################
    # Lifecycle
    #################################################################

    def shutdown(self) -> None:
        """
        Perform graceful application shutdown.

        This method is reserved for future cleanup tasks such as:

        - Closing database connections
        - Flushing log handlers
        - Persisting cached state
        - Releasing external resources
        """

        self._logger.info(
            "Dependency Container shutdown completed."
        )

    #################################################################
    # Representation
    #################################################################

    def __repr__(self) -> str:
        """
        Developer-friendly representation.
        """

        return (
            f"{self.__class__.__name__}("
            f"repositories={self.repository_count}, "
            f"services={self.service_count})"
        )

    def __str__(self) -> str:
        """
        Human-readable representation.
        """

        return (
            f"{self.config.APP_NAME} "
            f"Dependency Container"
        )
