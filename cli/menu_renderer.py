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
    """
    Renders all console output for the CLI.
    """

    #################################################################
    # Construction
    #################################################################

    def __init__(
        self,
        output: TextIO = sys.stdout,
        line_width: int = 70,
    ) -> None:
        """
        Initialize the renderer.

        Parameters
        ----------
        output
            Output stream.

        line_width
            Width used for separators and headings.
        """

        self._output = output
        self._line_width = line_width

    #################################################################
    # Internal Utilities
    #################################################################

    def _write(
        self,
        text: str = "",
    ) -> None:
        """
        Write a line to the configured output stream.
        """

        print(
            text,
            file=self._output,
        )

    #################################################################
    # Headings
    #################################################################

    def render_heading(
        self,
        title: str,
    ) -> None:
        """
        Render a section heading.
        """

        self._write()
        self._write("=" * self._line_width)
        self._write(title.center(self._line_width))
        self._write("=" * self._line_width)

    #################################################################
    # Separators
    #################################################################

    def render_separator(self) -> None:
        """
        Render a horizontal separator.
        """

        self._write("-" * self._line_width)

    #################################################################
    # Menus
    #################################################################

    def render_menu(
        self,
        menu: MenuDefinition,
    ) -> None:
        """
        Render a complete menu.
        """

        self.render_heading(menu.title)

        for option in menu.options:
            self._write(
                f"{option.key:>2}. {option.description}"
            )

        self.render_separator()

    #################################################################
    # Messages
    #################################################################

    def info(
        self,
        message: str,
    ) -> None:
        """
        Render an informational message.
        """

        self._write(f"[INFO] {message}")

    def success(
        self,
        message: str,
    ) -> None:
        """
        Render a success message.
        """

        self._write(f"[SUCCESS] {message}")

    def warning(
        self,
        message: str,
    ) -> None:
        """
        Render a warning message.
        """

        self._write(f"[WARNING] {message}")

    def error(
        self,
        message: str,
    ) -> None:
        """
        Render an error message.
        """

        self._write(f"[ERROR] {message}")

    #################################################################
    # Tables
    #################################################################

    def render_table(
        self,
        rows: Iterable[Iterable[object]],
    ) -> None:
        """
        Render a simple text table.
        """

        for row in rows:
            self._write(
                " | ".join(
                    str(column)
                    for column in row
                )
            )

        self.render_separator()

    #################################################################
    # Properties
    #################################################################

    @property
    def output(self) -> TextIO:
        """
        Return the configured output stream.
        """

        return self._output

    @property
    def line_width(self) -> int:
        """
        Return the configured line width.
        """

        return self._line_width

    #################################################################
    # Representation
    #################################################################

    def __repr__(self) -> str:
        """
        Developer-friendly representation.
        """

        return (
            f"{self.__class__.__name__}"
            f"(line_width={self._line_width})"
        )

    def __str__(self) -> str:
        """
        Human-readable representation.
        """

        return "CLI Menu Renderer"