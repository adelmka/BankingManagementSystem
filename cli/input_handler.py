"""
====================================================================
Banking Management System (BMS)

File        : input_handler.py
Description : CLI Input Handling

Provides validated user input services for the command-line interface.

Responsibilities
----------------
• Read user input
• Validate numeric input
• Validate decimal input
• Validate confirmation prompts
• Validate non-empty text input
• Provide reusable input utilities

This module contains no business logic.

Author      : Adel Alawiyat / ChatGPT
Python      : 3.13+
====================================================================
"""

from __future__ import annotations

from decimal import Decimal
from decimal import InvalidOperation
from datetime import datetime

from cli.menu_renderer import MenuRenderer


class InputHandler:
    """
    Handles all validated CLI input.
    """

    #################################################################
    # Construction
    #################################################################

    def __init__(
        self,
        renderer: MenuRenderer,
    ) -> None:

        self._renderer = renderer

    #################################################################
    # String Input
    #################################################################

    def read_string(
        self,
        prompt: str,
        *,
        required: bool = True,
    ) -> str:
        """
        Read a string from the user.
        """

        while True:

            value = input(f"{prompt}: ").strip()

            if value:
                return value

            if not required:
                return ""

            self._renderer.error(
                "Input cannot be empty."
            )

    #################################################################
    # Integer Input
    #################################################################

    def read_integer(
        self,
        prompt: str,
        *,
        minimum: int | None = None,
        maximum: int | None = None,
    ) -> int:
        """
        Read an integer.
        """

        while True:

            value = input(f"{prompt}: ").strip()

            try:
                number = int(value)

            except ValueError:

                self._renderer.error(
                    "Please enter a valid integer."
                )

                continue

            if minimum is not None and number < minimum:

                self._renderer.error(
                    f"Value must be at least {minimum}."
                )

                continue

            if maximum is not None and number > maximum:

                self._renderer.error(
                    f"Value must not exceed {maximum}."
                )

                continue

            return number

    #################################################################
    # Decimal Input
    #################################################################

    def read_decimal(
        self,
        prompt: str,
        *,
        minimum: Decimal | None = None,
        maximum: Decimal | None = None,
    ) -> Decimal:
        """
        Read a decimal value.
        """

        while True:

            value = input(f"{prompt}: ").strip()

            try:

                amount = Decimal(value)

            except InvalidOperation:

                self._renderer.error(
                    "Please enter a valid decimal value."
                )

                continue

            if minimum is not None and amount < minimum:

                self._renderer.error(
                    f"Minimum value is {minimum}."
                )

                continue

            if maximum is not None and amount > maximum:

                self._renderer.error(
                    f"Maximum value is {maximum}."
                )

                continue

            return amount

    #################################################################
    # Date Input
    #################################################################

    def read_date(
        self,
        prompt: str,
        *,
        date_format: str = "%Y-%m-%d",
    ) -> datetime:
        """
        Read a date.
        """

        while True:

            value = input(
                f"{prompt} ({date_format}): "
            ).strip()

            try:

                return datetime.strptime(
                    value,
                    date_format,
                )

            except ValueError:

                self._renderer.error(
                    "Invalid date."
                )

    #################################################################
    # Confirmation
    #################################################################

    def confirm(
        self,
        prompt: str,
    ) -> bool:
        """
        Ask for user confirmation.
        """

        while True:

            value = input(
                f"{prompt} (Y/N): "
            ).strip().lower()

            if value in ("y", "yes"):

                return True

            if value in ("n", "no"):

                return False

            self._renderer.error(
                "Please enter Y or N."
            )

    #################################################################
    # Menu Selection
    #################################################################

    def read_menu_selection(
        self,
        valid_choices: set[str],
    ) -> str:
        """
        Read a menu selection.
        """

        while True:

            selection = input(
                "Selection: "
            ).strip()

            if selection in valid_choices:

                return selection

            self._renderer.error(
                "Invalid menu selection."
            )

    #################################################################
    # Pause
    #################################################################

    def pause(self) -> None:
        """
        Wait for the user before continuing.
        """

        input(
            "\nPress ENTER to continue..."
        )

    #################################################################
    # Representation
    #################################################################

    def __repr__(self) -> str:

        return (
            f"{self.__class__.__name__}()"
        )

    def __str__(self) -> str:

        return "CLI Input Handler"