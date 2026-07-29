"""
====================================================================
Banking Management System (BMS)

File        : menu.py
Description : CLI Menu Definitions

Defines all menu structures used by the command-line interface.

Responsibilities
----------------
• Define menu metadata
• Define menu options
• Provide immutable menu definitions

This module contains no presentation logic.

Author      : Adel Alawiyat / ChatGPT
Python      : 3.13+
====================================================================
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class MenuOption:
    """
    Represents a single selectable menu option.
    """

    key: str
    description: str


@dataclass(frozen=True, slots=True)
class MenuDefinition:
    """
    Represents an immutable CLI menu.
    """

    title: str
    options: tuple[MenuOption, ...]


# ================================================================
# Main Menu
# ================================================================

MAIN_MENU = MenuDefinition(
    title="Main Menu",
    options=(
        MenuOption("1", "Customer Management"),
        MenuOption("2", "Account Management"),
        MenuOption("3", "Transaction Management"),
        MenuOption("4", "Reporting"),
        MenuOption("5", "Administration"),
        MenuOption("6", "System Information"),
        MenuOption("0", "Exit"),
    ),
)


# ================================================================
# Customer Management
# ================================================================

CUSTOMER_MENU = MenuDefinition(
    title="Customer Management",
    options=(
        MenuOption("1", "Create Customer"),
        MenuOption("2", "View Customer"),
        MenuOption("3", "Update Customer"),
        MenuOption("4", "Delete Customer"),
        MenuOption("5", "List Customers"),
        MenuOption("0", "Back"),
    ),
)


# ================================================================
# Account Management
# ================================================================

ACCOUNT_MENU = MenuDefinition(
    title="Account Management",
    options=(
        MenuOption("1", "Open Account"),
        MenuOption("2", "View Account"),
        MenuOption("3", "Close Account"),
        MenuOption("4", "List Customer Accounts"),
        MenuOption("5", "Change Interest Rate"),
        MenuOption("6", "Configure Fees"),
        MenuOption("0", "Back"),
    ),
)


# ================================================================
# Transaction Management
# ================================================================

TRANSACTION_MENU = MenuDefinition(
    title="Transaction Management",
    options=(
        MenuOption("1", "Deposit"),
        MenuOption("2", "Withdraw"),
        MenuOption("3", "Transfer Between Accounts"),
        MenuOption("4", "Transfer to External Bank"),
        MenuOption("5", "View Transaction History"),
        MenuOption("0", "Back"),
    ),
)


# ================================================================
# Reporting
# ================================================================

REPORTING_MENU = MenuDefinition(
    title="Reporting",
    options=(
        MenuOption("1", "Customer Report"),
        MenuOption("2", "Account Report"),
        MenuOption("3", "Transaction Report"),
        MenuOption("4", "Bank Summary"),
        MenuOption("0", "Back"),
    ),
)


# ================================================================
# Administration
# ================================================================

ADMINISTRATION_MENU = MenuDefinition(
    title="Administration",
    options=(
        MenuOption("1", "Backup Data"),
        MenuOption("2", "Restore Data"),
        MenuOption("3", "Application Settings"),
        MenuOption("0", "Back"),
    ),
)


# ================================================================
# System Information
# ================================================================

SYSTEM_MENU = MenuDefinition(
    title="System Information",
    options=(
        MenuOption("1", "Application Information"),
        MenuOption("2", "Storage Status"),
        MenuOption("3", "Configuration"),
        MenuOption("0", "Back"),
    ),
)


ALL_MENUS: tuple[MenuDefinition, ...] = (
    MAIN_MENU,
    CUSTOMER_MENU,
    ACCOUNT_MENU,
    TRANSACTION_MENU,
    REPORTING_MENU,
    ADMINISTRATION_MENU,
    SYSTEM_MENU,
)

MENU_REGISTRY: dict[str, MenuDefinition] = {
    "main": MAIN_MENU,
    "customer": CUSTOMER_MENU,
    "account": ACCOUNT_MENU,
    "transaction": TRANSACTION_MENU,
    "reporting": REPORTING_MENU,
    "administration": ADMINISTRATION_MENU,
    "system": SYSTEM_MENU,
}

def get_menu(name: str) -> MenuDefinition:
    """
    Return a menu definition by its logical name.

    Raises
    ------
    ValueError
        If the requested menu does not exist.
    """
    try:
        return MENU_REGISTRY[name]
    except KeyError as exc:
        raise ValueError(
            f"Unknown menu: '{name}'."
        ) from exc