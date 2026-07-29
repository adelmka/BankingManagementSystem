"""
====================================================================
Banking Management System (BMS)

Package     : cli
Description : Command-Line Interface Package

Provides the public interface to the Banking Management System's
presentation layer.

Author      : Adel Alawiyat / ChatGPT
Python      : 3.13+
====================================================================
"""

from .application_cli import ApplicationCLI
from .command_dispatcher import CommandDispatcher
from .input_handler import InputHandler
from .menu import (
    MenuDefinition,
    MenuOption,
    MENU_REGISTRY,
    get_menu,
)
from .menu_renderer import MenuRenderer

__all__ = (
    "ApplicationCLI",
    "CommandDispatcher",
    "InputHandler",
    "MenuRenderer",
    "MenuDefinition",
    "MenuOption",
    "MENU_REGISTRY",
    "get_menu",
)