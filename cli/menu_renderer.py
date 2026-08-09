"""
====================================================================
Banking Management System (BMS)

File        : menu_renderer.py
Description : CLI Rendering Utilities

Provides reusable rendering services for the command-line interface.

Responsibilities
----------------
• Render menus
• Render headings
• Render separators
• Render informational messages
• Render success, warning and error messages
• Render simple tables

This module contains no business logic.

Author      : Adel Alawiyat / ChatGPT
Python      : 3.13+
====================================================================
"""

from __future__ import annotations

import sys

from typing import Iterable
from typing import TextIO

from cli.menu import MenuDefinition


class MenuRenderer:
    """Renders all console output for the CLI."""

    def __init__(self, output: TextIO = sys.stdout, line_width: int = 70) -> None:
        self._output = output
        self._line_width = line_width

    def _write(self, text: str = "") -> None:
        print(text, file=self._output)

    def render_heading(self, title: str) -> None:
        self._write()
        self._write("=" * self._line_width)
        self._write(title.center(self._line_width))
        self._write("=" * self._line_width)

    def render_separator(self) -> None:
        self._write("-" * self._line_width)

    def render_menu(self, menu: MenuDefinition) -> None:
        self.render_heading(menu.title)
        for option in menu.options:
            self._write(f"{option.key:>2}. {option.description}")
        self.render_separator()

    def info(self, message: str) -> None:
        self._write(f"[INFO] {message}")

    def success(self, message: str) -> None:
        self._write(f"[SUCCESS] {message}")

    def warning(self, message: str) -> None:
        self._write(f"[WARNING] {message}")

    def error(self, message: str) -> None:
        self._write(f"[ERROR] {message}")

    def render_table(self, rows: Iterable[Iterable[object]]) -> None:
        for row in rows:
            self._write(" | ".join(str(column) for column in row))
        self.render_separator()

    #################################################################
    # Command Adapter Compatibility
    #################################################################

    def display_message(self, message: object) -> None:
        """Compatibility alias for informational command output."""
        self.info(str(message))

    def display_success(self, message: object) -> None:
        """Compatibility alias for successful command output."""
        self.success(str(message))

    def display_warning(self, message: object) -> None:
        """Compatibility alias for warning command output."""
        self.warning(str(message))

    def display_error(self, message: object) -> None:
        """Compatibility alias for error command output."""
        self.error(str(message))

    def display_object(self, value: object) -> None:
        """Display one object using its string representation."""
        self._write(str(value))

    def display_list(self, values: Iterable[object]) -> None:
        """Display a sequence of values, one item per line."""
        for value in values:
            self._write(str(value))

    def display_main_menu(self, menu: MenuDefinition | None = None) -> None:
        """Render the supplied main menu, defaulting to the project menu."""
        if menu is None:
            from cli.menu import MAIN_MENU
            menu = MAIN_MENU
        self.render_menu(menu)

    @property
    def output(self) -> TextIO:
        return self._output

    @property
    def line_width(self) -> int:
        return self._line_width

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(line_width={self._line_width})"

    def __str__(self) -> str:
        return "CLI Menu Renderer"
