"""
Command Dispatcher

Responsible for routing CLI commands to their corresponding command handlers.

The dispatcher belongs to the presentation layer and must remain unaware
of business rules, repositories, or domain implementation details.

Flow:

User Input
    |
InputHandler
    |
CommandDispatcher
    |
Command Module
    |
Service Layer
"""

from typing import Any, Callable, Dict, Optional

from utils.logger import get_logger


class CommandDispatcher:
    """
    Routes CLI commands to registered command handlers.

    Responsibilities:
        - Register command handlers.
        - Dispatch commands.
        - Validate command existence.
        - Provide centralized command execution logging.

    Non-responsibilities:
        - Business logic.
        - Data validation.
        - User input collection.
        - Menu rendering.
        - Repository access.
    """

    def __init__(self) -> None:
        """
        Initialize command registry.
        """

        self._commands: Dict[str, Callable[..., Any]] = {}

        self.logger = get_logger(__name__)


    def register_command(
        self,
        command_name: str,
        handler: Callable[..., Any],
    ) -> None:
        """
        Register a command handler.

        Args:
            command_name:
                Unique command identifier.

            handler:
                Callable command implementation.
        """

        if not command_name:
            raise ValueError(
                "Command name cannot be empty."
            )

        if not callable(handler):
            raise TypeError(
                "Command handler must be callable."
            )

        normalized_name = command_name.strip().lower()

        if normalized_name in self._commands:
            raise ValueError(
                f"Command already registered: {normalized_name}"
            )

        self._commands[normalized_name] = handler

        self.logger.debug(
            "Registered CLI command: %s",
            normalized_name,
        )


    def unregister_command(
        self,
        command_name: str,
    ) -> None:
        """
        Remove a registered command.

        Args:
            command_name:
                Command identifier.
        """

        normalized_name = command_name.strip().lower()

        self._commands.pop(
            normalized_name,
            None,
        )


    def dispatch(
        self,
        command_name: str,
        *args,
        **kwargs,
    ) -> Any:
        """
        Execute a registered command.

        Args:
            command_name:
                Command identifier.

            args:
                Positional arguments forwarded
                to command handler.

            kwargs:
                Keyword arguments forwarded
                to command handler.

        Returns:
            Command execution result.
        """

        normalized_name = command_name.strip().lower()

        handler = self._commands.get(
            normalized_name
        )

        if handler is None:
            raise ValueError(
                f"Unknown command: {command_name}"
            )

        self.logger.debug(
            "Executing CLI command: %s",
            normalized_name,
        )

        return handler(
            *args,
            **kwargs,
        )


    def has_command(
        self,
        command_name: str,
    ) -> bool:
        """
        Check whether a command exists.

        Args:
            command_name:
                Command identifier.

        Returns:
            True if command exists.
        """

        return (
            command_name.strip().lower()
            in self._commands
        )


    def get_registered_commands(
        self,
    ) -> list[str]:
        """
        Return registered command names.

        Returns:
            List of available commands.
        """

        return list(
            self._commands.keys()
        )


    def clear_commands(
        self,
    ) -> None:
        """
        Remove all registered commands.
        """

        self._commands.clear()