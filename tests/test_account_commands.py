"""Tests for the current CLI AccountCommands contract."""

from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest

from cli.commands.account_commands import AccountCommands
from models.current_account import CurrentAccount
from models.savings_account import SavingsAccount
from models.time_deposit_account import TimeDepositAccount
from utils.constants import AccountType, InterestFrequency


@pytest.fixture
def account_service():
    return MagicMock(name="account_service")


@pytest.fixture
def input_handler():
    return MagicMock(name="input_handler")


@pytest.fixture
def menu_renderer():
    return MagicMock(name="menu_renderer")


@pytest.fixture
def logger():
    return MagicMock(name="logger")


@pytest.fixture
def commands(account_service, input_handler, menu_renderer, logger):
    with patch(
        "cli.commands.account_commands.get_logger",
        return_value=logger,
    ):
        return AccountCommands(account_service, input_handler, menu_renderer)


def test_constructor_retains_dependencies(commands, account_service, input_handler, menu_renderer):
    assert commands.account_service is account_service
    assert commands.input_handler is input_handler
    assert commands.menu_renderer is menu_renderer


def test_create_account_builds_savings_account_and_opens_it(
    commands, account_service, input_handler, menu_renderer
):
    input_handler.get_value.side_effect = [
        "C000001",
        "savings",
        "0.035",
        "monthly",
    ]
    input_handler.get_money.side_effect = ["1000.00", "500.00"]
    account_service.open_account.side_effect = lambda account: account

    with patch(
        "cli.commands.account_commands.IDGenerator.account_number",
        return_value="A000001",
    ):
        commands.create_account()

    account_service.open_account.assert_called_once()
    account = account_service.open_account.call_args.args[0]
    assert isinstance(account, SavingsAccount)
    assert account.account_number == "A000001"
    assert account.customer_id == "C000001"
    assert account.interest_rate == Decimal("0.035")
    assert account.minimum_balance.amount == Decimal("500.00")
    assert account.interest_frequency is InterestFrequency.MONTHLY
    assert account.balance.amount == Decimal("1000.00")
    menu_renderer.display_message.assert_called_once_with(
        "Account created successfully."
    )
    menu_renderer.display_object.assert_called_once_with(account)


def test_create_account_builds_current_account_and_opens_it(
    commands, account_service
):
    commands.input_handler.get_value.side_effect = [
        "C000001",
        "current",
    ]
    commands.input_handler.get_money.side_effect = [
        "1000.00",
        "5000.00",
        "25.00",
        "50.00",
    ]
    commands.input_handler.get_confirmation.return_value = True
    account_service.open_account.side_effect = lambda account: account

    with patch(
        "cli.commands.account_commands.IDGenerator.account_number",
        return_value="A000002",
    ):
        commands.create_account()

    account = account_service.open_account.call_args.args[0]
    assert isinstance(account, CurrentAccount)
    assert account.overdraft_limit.amount == Decimal("5000.00")
    assert account.maintenance_fee.amount == Decimal("25.00")
    assert account.overdraft_fee.amount == Decimal("50.00")
    assert account.overdraft_enabled is True


def test_create_account_builds_time_deposit_and_opens_it(
    commands, account_service
):
    commands.input_handler.get_value.side_effect = [
        "C000001",
        "time deposit",
        "0.045",
        "12",
        "0.02",
    ]
    commands.input_handler.get_money.return_value = "10000.00"
    commands.input_handler.get_confirmation.return_value = False
    account_service.open_account.side_effect = lambda account: account

    with patch(
        "cli.commands.account_commands.IDGenerator.account_number",
        return_value="A000003",
    ):
        commands.create_account()

    account = account_service.open_account.call_args.args[0]
    assert isinstance(account, TimeDepositAccount)
    assert account.interest_rate == Decimal("0.045")
    assert account.term_months == 12
    assert account.early_withdrawal_penalty_rate == Decimal("0.02")
    assert account.auto_renew is False


def test_create_account_handles_error(commands, account_service, menu_renderer, logger):
    account_service.open_account.side_effect = ValueError("bad account")
    commands.input_handler.get_value.side_effect = ["C000001", "savings"]
    commands.input_handler.get_money.return_value = "1000.00"
    commands.input_handler.get_value.side_effect = [
        "C000001", "savings", "0.035", "monthly"
    ]
    commands.input_handler.get_money.side_effect = ["1000.00", "500.00"]

    commands.create_account()

    menu_renderer.display_error.assert_called_once_with("bad account")
    logger.exception.assert_called_once()


def test_collect_account_type_accepts_common_aliases(commands):
    commands.input_handler.get_value.return_value = "fixed deposit"
    assert commands._collect_account_type() is AccountType.TIME_DEPOSIT


def test_collect_invalid_account_type_raises(commands):
    commands.input_handler.get_value.return_value = "investment"
    with pytest.raises(ValueError, match="Invalid account type"):
        commands._collect_account_type()


def test_view_account_delegates(commands, account_service, input_handler, menu_renderer):
    account = MagicMock(name="account")
    input_handler.get_value.return_value = "A000001"
    account_service.get_account.return_value = account

    commands.view_account()

    account_service.get_account.assert_called_once_with("A000001")
    menu_renderer.display_object.assert_called_once_with(account)


def test_list_accounts_delegates_to_current_service(commands, account_service, menu_renderer):
    accounts = [MagicMock(name="account")]
    account_service.all_accounts.return_value = accounts

    commands.list_accounts()

    account_service.all_accounts.assert_called_once_with()
    menu_renderer.display_list.assert_called_once_with(accounts)


def test_deposit_delegates(commands, account_service, menu_renderer):
    commands.input_handler.get_value.return_value = "A000001"
    commands.input_handler.get_money.return_value = MagicMock(name="money")
    account = MagicMock(name="account")
    account_service.deposit.return_value = account

    commands.deposit()

    account_service.deposit.assert_called_once_with(
        "A000001", commands.input_handler.get_money.return_value
    )
    menu_renderer.display_object.assert_called_once_with(account)


def test_withdraw_delegates(commands, account_service, menu_renderer):
    commands.input_handler.get_value.return_value = "A000001"
    commands.input_handler.get_money.return_value = MagicMock(name="money")
    account = MagicMock(name="account")
    account_service.withdraw.return_value = account

    commands.withdraw()

    account_service.withdraw.assert_called_once_with(
        "A000001", commands.input_handler.get_money.return_value
    )
    menu_renderer.display_object.assert_called_once_with(account)


def test_close_account_requires_confirmation(commands, account_service):
    commands.input_handler.get_value.return_value = "A000001"
    commands.input_handler.get_confirmation.return_value = False

    commands.close_account()

    account_service.close_account.assert_not_called()
