"""
====================================================================
Banking Management System (BMS)

File        : application.py
Description : Application Root

Represents the running Banking Management System.

Responsibilities
----------------
• Build the dependency graph
• Own the application lifetime
• Expose the BankService facade
• Coordinate graceful shutdown
• Provide the CLI command adapters used by the executable entry point

The DependencyContainer remains an internal implementation detail.

Author      : adelmka / ChatGPT
Python      : 3.13+
====================================================================
"""

from __future__ import annotations

from config import Config

from application.dependency_container import DependencyContainer

from services.bank_service import BankService

from utils.logger import get_logger


class Application:
    """
    Represents a running Banking Management System.
    """

    #################################################################
    # Construction
    #################################################################

    def __init__(
        self,
        config: type[Config] = Config
    ) -> None:

        self._config = config

        self._logger = get_logger(__name__)

        #
        # Build the application's dependency graph.
        #
        self._container = DependencyContainer.build(
            config=self._config
        )

        self._logger.info(
            "Application initialized."
        )

    #################################################################
    # Public API
    #################################################################

    @property
    def bank(self) -> BankService:
        """
        Return the application's BankService facade.
        """

        return self._container.bank_service

    def create_cli_commands(
        self,
        input_handler,
        menu_renderer,
    ) -> dict[str, object]:
        """
        Create the CLI command adapters for the running application.

        The dependency container remains private to the application.
        The executable composition root requests command adapters through
        this method rather than reaching into ``_container`` directly.
        """

        from cli.commands.account_commands import AccountCommands
        from cli.commands.customer_commands import CustomerCommands

        return {
            "customer": CustomerCommands(
                customer_service=self._container.customer_service,
                input_handler=input_handler,
                menu_renderer=menu_renderer,
            ),
            "account": AccountCommands(
                account_service=self._container.account_service,
                input_handler=input_handler,
                menu_renderer=menu_renderer,
            ),
        }

    #################################################################
    # Configuration
    #################################################################

    @property
    def config(self) -> type[Config]:
        """
        Return the active application configuration.
        """

        return self._config

    #################################################################
    # Health
    #################################################################

    @property
    def is_running(self) -> bool:
        """
        Return whether the application is running.
        """

        return self._container.validate()

    #################################################################
    # Lifecycle
    #################################################################

    def shutdown(self) -> None:
        """
        Shutdown the application gracefully.
        """

        self._container.shutdown()

        self._logger.info(
            "Application shutdown completed."
        )

    #################################################################
    # Representation
    #################################################################

    def __repr__(self) -> str:

        return (
            f"{self.__class__.__name__}"
            f"(running={self.is_running})"
        )

    def __str__(self) -> str:

        return (
            f"{self._config.APP_NAME}"
        )
