"""Tests for the CLI menu definitions and registry."""

from dataclasses import FrozenInstanceError

import pytest

from cli.menu import (
    ACCOUNT_MENU,
    ADMINISTRATION_MENU,
    ALL_MENUS,
    CUSTOMER_MENU,
    MAIN_MENU,
    MENU_REGISTRY,
    REPORTING_MENU,
    SYSTEM_MENU,
    TRANSACTION_MENU,
    MenuDefinition,
    MenuOption,
    get_menu,
)


class TestMenuOption:
    def test_stores_key_and_description(self):
        option = MenuOption("1", "Example")
        assert option.key == "1"
        assert option.description == "Example"

    def test_is_frozen(self):
        option = MenuOption("1", "Example")
        with pytest.raises(FrozenInstanceError):
            option.key = "2"

    def test_is_hashable(self):
        option = MenuOption("1", "Example")
        assert hash(option) == hash(MenuOption("1", "Example"))

    def test_equality_is_value_based(self):
        assert MenuOption("1", "Example") == MenuOption("1", "Example")
        assert MenuOption("1", "Example") != MenuOption("2", "Example")


class TestMenuDefinition:
    def test_stores_title_and_options(self):
        option = MenuOption("1", "Example")
        menu = MenuDefinition("Example Menu", (option,))
        assert menu.title == "Example Menu"
        assert menu.options == (option,)

    def test_options_are_tuple(self):
        menu = MenuDefinition("Example Menu", (MenuOption("1", "Example"),))
        assert isinstance(menu.options, tuple)

    def test_is_frozen(self):
        menu = MenuDefinition("Example Menu", ())
        with pytest.raises(FrozenInstanceError):
            menu.title = "Changed"

    def test_is_hashable(self):
        menu = MenuDefinition("Example Menu", ())
        assert hash(menu) == hash(MenuDefinition("Example Menu", ()))

    def test_equality_is_value_based(self):
        assert MenuDefinition("Example", ()) == MenuDefinition("Example", ())
        assert MenuDefinition("Example", ()) != MenuDefinition("Other", ())


class TestMainMenu:
    def test_title(self):
        assert MAIN_MENU.title == "Main Menu"

    def test_options(self):
        assert MAIN_MENU.options == (
            MenuOption("1", "Customer Management"),
            MenuOption("2", "Account Management"),
            MenuOption("3", "Transaction Management"),
            MenuOption("4", "Reporting"),
            MenuOption("5", "Administration"),
            MenuOption("6", "System Information"),
            MenuOption("0", "Exit"),
        )


@pytest.mark.parametrize(
    ("menu", "title", "options"),
    [
        (
            CUSTOMER_MENU,
            "Customer Management",
            (
                ("1", "Create Customer"),
                ("2", "View Customer"),
                ("3", "Update Customer"),
                ("4", "Delete Customer"),
                ("5", "List Customers"),
                ("0", "Back"),
            ),
        ),
        (
            ACCOUNT_MENU,
            "Account Management",
            (
                ("1", "Open Account"),
                ("2", "View Account"),
                ("3", "Close Account"),
                ("4", "List Customer Accounts"),
                ("5", "Change Interest Rate"),
                ("6", "Configure Fees"),
                ("0", "Back"),
            ),
        ),
        (
            TRANSACTION_MENU,
            "Transaction Management",
            (
                ("1", "Deposit"),
                ("2", "Withdraw"),
                ("3", "Transfer Between Accounts"),
                ("4", "Transfer to External Bank"),
                ("5", "View Transaction History"),
                ("0", "Back"),
            ),
        ),
        (
            REPORTING_MENU,
            "Reporting",
            (
                ("1", "Customer Report"),
                ("2", "Account Report"),
                ("3", "Transaction Report"),
                ("4", "Bank Summary"),
                ("0", "Back"),
            ),
        ),
        (
            ADMINISTRATION_MENU,
            "Administration",
            (
                ("1", "Backup Data"),
                ("2", "Restore Data"),
                ("3", "Application Settings"),
                ("0", "Back"),
            ),
        ),
        (
            SYSTEM_MENU,
            "System Information",
            (
                ("1", "Application Information"),
                ("2", "Storage Status"),
                ("3", "Configuration"),
                ("0", "Back"),
            ),
        ),
    ],
)
def test_menu_definition_matches_current_contract(menu, title, options):
    assert menu.title == title
    assert menu.options == tuple(MenuOption(key, description) for key, description in options)


def test_all_menus_contains_each_defined_menu():
    assert ALL_MENUS == (
        MAIN_MENU,
        CUSTOMER_MENU,
        ACCOUNT_MENU,
        TRANSACTION_MENU,
        REPORTING_MENU,
        ADMINISTRATION_MENU,
        SYSTEM_MENU,
    )


def test_all_menus_has_no_duplicates():
    assert len(ALL_MENUS) == len(set(ALL_MENUS))


def test_menu_registry_contains_expected_logical_names():
    assert MENU_REGISTRY == {
        "main": MAIN_MENU,
        "customer": CUSTOMER_MENU,
        "account": ACCOUNT_MENU,
        "transaction": TRANSACTION_MENU,
        "reporting": REPORTING_MENU,
        "administration": ADMINISTRATION_MENU,
        "system": SYSTEM_MENU,
    }


@pytest.mark.parametrize(
    ("name", "expected"),
    [
        ("main", MAIN_MENU),
        ("customer", CUSTOMER_MENU),
        ("account", ACCOUNT_MENU),
        ("transaction", TRANSACTION_MENU),
        ("reporting", REPORTING_MENU),
        ("administration", ADMINISTRATION_MENU),
        ("system", SYSTEM_MENU),
    ],
)
def test_get_menu_returns_registered_menu(name, expected):
    assert get_menu(name) is expected


def test_get_menu_unknown_name_raises_value_error():
    with pytest.raises(ValueError, match="Unknown menu: 'missing'"):
        get_menu("missing")


def test_get_menu_error_preserves_key_error_as_cause():
    with pytest.raises(ValueError) as exc_info:
        get_menu("missing")
    assert isinstance(exc_info.value.__cause__, KeyError)


def test_menu_options_are_immutable():
    assert isinstance(MAIN_MENU.options, tuple)
    with pytest.raises(AttributeError):
        MAIN_MENU.options.append(MenuOption("9", "Invalid"))


def test_menu_option_fields_are_immutable():
    option = MAIN_MENU.options[0]
    with pytest.raises(FrozenInstanceError):
        option.description = "Changed"


def test_menu_keys_are_unique_within_each_menu():
    for menu in ALL_MENUS:
        keys = [option.key for option in menu.options]
        assert len(keys) == len(set(keys)), menu.title


def test_every_menu_has_back_or_exit_option():
    assert MAIN_MENU.options[-1] == MenuOption("0", "Exit")
    for menu in ALL_MENUS[1:]:
        assert menu.options[-1] == MenuOption("0", "Back")


def test_every_non_main_menu_has_nonzero_actions():
    for menu in ALL_MENUS[1:]:
        assert any(option.key != "0" for option in menu.options)


def test_all_menu_options_are_menu_option_instances():
    for menu in ALL_MENUS:
        assert all(isinstance(option, MenuOption) for option in menu.options)


def test_all_menu_definitions_are_menu_definition_instances():
    assert all(isinstance(menu, MenuDefinition) for menu in ALL_MENUS)


def test_registry_values_match_all_menus():
    assert set(MENU_REGISTRY.values()) == set(ALL_MENUS)


def test_registry_keys_are_strings():
    assert all(isinstance(name, str) for name in MENU_REGISTRY)


def test_menu_titles_are_non_empty():
    assert all(menu.title.strip() for menu in ALL_MENUS)


def test_menu_option_keys_are_non_empty():
    assert all(option.key.strip() for menu in ALL_MENUS for option in menu.options)


def test_menu_option_descriptions_are_non_empty():
    assert all(
        option.description.strip()
        for menu in ALL_MENUS
        for option in menu.options
    )


def test_menu_zero_option_is_last():
    for menu in ALL_MENUS:
        assert menu.options[-1].key == "0"


def test_main_menu_has_seven_options():
    assert len(MAIN_MENU.options) == 7


def test_customer_menu_has_six_options():
    assert len(CUSTOMER_MENU.options) == 6


def test_account_menu_has_seven_options():
    assert len(ACCOUNT_MENU.options) == 7


def test_transaction_menu_has_six_options():
    assert len(TRANSACTION_MENU.options) == 6


def test_reporting_menu_has_five_options():
    assert len(REPORTING_MENU.options) == 5


def test_administration_menu_has_four_options():
    assert len(ADMINISTRATION_MENU.options) == 4


def test_system_menu_has_four_options():
    assert len(SYSTEM_MENU.options) == 4
