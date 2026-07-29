"""
Application CLI

Main command-line application controller.

Responsible for:
    - Starting the CLI application.
    - Managing the application lifecycle.
    - Coordinating menu rendering, input handling,
      and command dispatching.

The CLI layer communicates with the service layer
only through command modules.

Architecture:

User
 |
 v
ApplicationCLI
 |
 +--> MenuRenderer
 |
 +--> InputHandler
 |
 +--> CommandDispatcher
 |
 +--> Command Modules
 |
 +--> Services
"""

from typing import Optional

from cli.command_dispatcher import CommandDispatcher
from cli.input_handler import InputHandler
from cli.menu_renderer import MenuRenderer

from utils.logger import get_logger


class ApplicationCLI:
    """
    Main CLI application controller.

    This class coordinates the interaction between
    the user interface components.

    It is intentionally unaware of:
        - Domain models
        - Repositories
        - Business rules
    """

    def __init__(
        self,
        menu_renderer: MenuRenderer,
        input_handler: InputHandler,
        command_dispatcher: CommandDispatcher,
    ) -> None:
        """
        Initialize CLI application.

        Args:
            menu_renderer:
                Component responsible for displaying menus.

            input_handler:
                Component responsible for user input.

            command_dispatcher:
                Component responsible for command execution.
        """

        self.menu_renderer = menu_renderer
        self.input_handler = input_handler
        self.command_dispatcher = command_dispatcher

        self.logger = get_logger(__name__)

        self._running = False


    def start(self) -> None:
        """
        Start CLI application loop.
        """

        self.logger.info(
            "Starting Banking Management System CLI."
        )

        self._running = True

        try:
            self._run_loop()

        except Exception as exc:
            self.logger.exception(
                "Unexpected CLI failure: %s",
                exc,
            )

            raise

        finally:
            self.stop()


    def stop(self) -> None:
        """
        Stop CLI application.
        """

        self._running = False

        self.logger.info(
            "Banking Management System CLI stopped."
        )


    def _run_loop(self) -> None:
        """
        Main application loop.

        Continues until the user exits.
        """

        while self._running:

            self.menu_renderer.display_main_menu()

            command = (
                self.input_handler.get_command()
            )

            if self._is_exit_command(command):
                self.stop()
                continue

            self._execute_command(command)


    def _execute_command(
        self,
        command: str,
    ) -> None:
        """
        Dispatch selected command.

        Args:
            command:
                User-selected command.
        """

        try:

            self.command_dispatcher.dispatch(
                command
            )

        except ValueError as exc:

            self.logger.warning(
                "Invalid command: %s",
                exc,
            )

            self.menu_renderer.display_message(
                str(exc)
            )


    @staticmethod
    def _is_exit_command(
        command: Optional[str],
    ) -> bool:
        """
        Determine whether command exits application.

        Args:
            command:
                User command.

        Returns:
            True when exit requested.
        """

        if command is None:
            return True

        return command.strip().lower() in {
            "exit",
            "quit",
            "0",
        }