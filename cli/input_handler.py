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

from datetime import datetime
from decimal import Decimal, InvalidOperation

from cli.menu_renderer import MenuRenderer
from models.value_objects.money import Money


class InputHandler:
    """Handles all validated CLI input."""

    def __init__(self, renderer: MenuRenderer) -> None:
        self._renderer = renderer

    def read_string(self, prompt: str, *, required: bool = True) -> str:
        """Read a string from the user."""
        while True:
            value = input(f"{prompt}: ").strip()
            if value:
                return value
            if not required:
                return ""
            self._renderer.error("Input cannot be empty.")

    def read_integer(
        self,
        prompt: str,
        *,
        minimum: int | None = None,
        maximum: int | None = None,
    ) -> int:
        """Read an integer."""
        while True:
            value = input(f"{prompt}: ").strip()
            try:
                number = int(value)
            except ValueError:
                self._renderer.error("Please enter a valid integer.")
                continue
            if minimum is not None and number < minimum:
                self._renderer.error(f"Value must be at least {minimum}.")
                continue
            if maximum is not None and number > maximum:
                self._renderer.error(f"Value must not exceed {maximum}.")
                continue
            return number

    def read_decimal(
        self,
        prompt: str,
        *,
        minimum: Decimal | None = None,
        maximum: Decimal | None = None,
    ) -> Decimal:
        """Read a decimal value."""
        while True:
            value = input(f"{prompt}: ").strip()
            try:
                amount = Decimal(value)
            except InvalidOperation:
                self._renderer.error("Please enter a valid decimal value.")
                continue
            if minimum is not None and amount < minimum:
                self._renderer.error(f"Minimum value is {minimum}.")
                continue
            if maximum is not None and amount > maximum:
                self._renderer.error(f"Maximum value is {maximum}.")
                continue
            return amount

    def read_date(
        self,
        prompt: str,
        *,
        date_format: str = "%Y-%m-%d",
    ) -> datetime:
        """Read a date."""
        while True:
            value = input(f"{prompt} ({date_format}): ").strip()
            try:
                return datetime.strptime(value, date_format)
            except ValueError:
                self._renderer.error("Invalid date.")

    def confirm(self, prompt: str) -> bool:
        """Ask for user confirmation."""
        while True:
            value = input(f"{prompt} (Y/N): ").strip().lower()
            if value in ("y", "yes"):
                return True
            if value in ("n", "no"):
                return False
            self._renderer.error("Please enter Y or N.")

    def read_menu_selection(self, valid_choices: set[str]) -> str:
        """Read a menu selection."""
        while True:
            selection = input("Selection: ").strip()
            if selection in valid_choices:
                return selection
            self._renderer.error("Invalid menu selection.")

    def get_value(self, prompt: str, *, required: bool = True) -> str:
        """Compatibility alias used by command adapters."""
        return self.read_string(prompt, required=required)

    def get_optional_value(self, prompt: str) -> str:
        """Read an optional string value."""
        return self.read_string(prompt, required=False)

    def get_money(self, prompt: str) -> Money:
        """Read a validated monetary amount as the domain Money value object."""
        amount = self.read_decimal(prompt, minimum=Decimal("0"))
        return Money(amount)

    def get_confirmation(self, prompt: str) -> bool:
        """Compatibility alias for confirmation input."""
        return self.confirm(prompt)

    def get_integer(
        self,
        prompt: str,
        *,
        minimum: int | None = None,
        maximum: int | None = None,
    ) -> int:
        """Compatibility alias for integer input."""
        return self.read_integer(prompt, minimum=minimum, maximum=maximum)

    def get_date(self, prompt: str, *, date_format: str = "%Y-%m-%d") -> datetime:
        """Compatibility alias for date input."""
        return self.read_date(prompt, date_format=date_format)

    def get_command(self, valid_choices: set[str] | None = None) -> str:
        """Read a command selection."""
        if valid_choices is not None:
            return self.read_menu_selection(valid_choices)
        return self.read_string("Selection")

    def pause(self) -> None:
        """Wait for the user before continuing."""
        input("\nPress ENTER to continue...")

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}()"

    def __str__(self) -> str:
        return "CLI Input Handler"
