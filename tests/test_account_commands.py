"""Tests for the current CLI AccountCommands contract."""

from unittest.mock import MagicMock, patch

import pytest

from cli.commands.account_commands import AccountCommands


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
        return AccountCommands(
            account_service=account_service,
            input_handler=input_handler,
            menu_renderer=menu_renderer,
        )


def test_constructor_retains_dependencies(
    commands,
    account_service,
    input_handler,
    menu_renderer,
):
    assert commands.account_service is account_service
    assert commands.input_handler is input_handler
    assert commands.menu_renderer is menu_renderer


def test_constructor_creates_logger(commands, logger):
    assert commands.logger is logger


def test_create_account_collects_data_calls_service_and_displays_result(
    commands,
    account_service,
    input_handler,
    menu_renderer,
):
    account = MagicMock(name="account")
    input_handler.get_value.side_effect = ["C000001", "savings"]
    input_handler.get_money.return_value = "1000.00"
    account_service.create_account.return_value = account

    commands.create_account()

    expected = {
        "customer_id": "C000001",
        "account_type": "savings",
        "initial_deposit": "1000.00",
    }
    account_service.create_account.assert_called_once_with(expected)
    menu_renderer.display_message.assert_called_once_with(
        "Account created successfully."
    )
    menu_renderer.display_object.assert_called_once_with(account)


def test_create_account_handles_service_error(
    commands,
    account_service,
    menu_renderer,
    logger,
):
    account_service.create_account.side_effect = ValueError("bad account")

    commands.create_account()

    menu_renderer.display_error.assert_called_once_with("bad account")
    logger.exception.assert_called_once()


def test_view_account_gets_number_and_displays_account(
    commands,
    input_handler,
    account_service,
    menu_renderer,
):
    account = MagicMock(name="account")
    input_handler.get_value.return_value = "SA100001"
    account_service.get_account.return_value = account

    commands.view_account()

    input_handler.get_value.assert_called_once_with("Enter account number: ")
    account_service.get_account.assert_called_once_with("SA100001")
    menu_renderer.display_object.assert_called_once_with(account)


def test_view_account_handles_error(
    commands,
    account_service,
    menu_renderer,
    logger,
):
    account_service.get_account.side_effect = ValueError("not found")

    commands.view_account()

    menu_renderer.display_error.assert_called_once_with("not found")
    logger.exception.assert_called_once()


def test_list_accounts_gets_all_accounts_and_displays_list(
    commands,
    account_service,
    menu_renderer,
):
    accounts = [MagicMock(name="account1"), MagicMock(name="account2")]
    account_service.get_all_accounts.return_value = accounts

    commands.list_accounts()

    account_service.get_all_accounts.assert_called_once_with()
    menu_renderer.display_list.assert_called_once_with(accounts)


def test_list_accounts_handles_error(
    commands,
    account_service,
    menu_renderer,
    logger,
):
    account_service.get_all_accounts.side_effect = RuntimeError("repository failure")

    commands.list_accounts()

    menu_renderer.display_error.assert_called_once_with("repository failure")
    logger.exception.assert_called_once()


def test_deposit_collects_number_and_amount_and_displays_result(
    commands,
    input_handler,
    account_service,
    menu_renderer,
):
    account = MagicMock(name="account")
    input_handler.get_value.return_value = "SA100001"
    input_handler.get_money.return_value = "250.00"
    account_service.deposit.return_value = account

    commands.deposit()

    input_handler.get_value.assert_called_once_with("Enter account number: ")
    input_handler.get_money.assert_called_once_with("Enter deposit amount: ")
    account_service.deposit.assert_called_once_with("SA100001", "250.00")
    menu_renderer.display_message.assert_called_once_with(
        "Deposit completed successfully."
    )
    menu_renderer.display_object.assert_called_once_with(account)


def test_deposit_handles_error(
    commands,
    account_service,
    menu_renderer,
    logger,
):
    account_service.deposit.side_effect = ValueError("invalid deposit")

    commands.deposit()

    menu_renderer.display_error.assert_called_once_with("invalid deposit")
    logger.exception.assert_called_once()


def test_withdraw_collects_number_and_amount_and_displays_result(
    commands,
    input_handler,
    account_service,
    menu_renderer,
):
    account = MagicMock(name="account")
    input_handler.get_value.return_value = "SA100001"
    input_handler.get_money.return_value = "100.00"
    account_service.withdraw.return_value = account

    commands.withdraw()

    input_handler.get_value.assert_called_once_with("Enter account number: ")
    input_handler.get_money.assert_called_once_with("Enter withdrawal amount: ")
    account_service.withdraw.assert_called_once_with("SA100001", "100.00")
    menu_renderer.display_message.assert_called_once_with(
        "Withdrawal completed successfully."
    )
    menu_renderer.display_object.assert_called_once_with(account)


def test_withdraw_handles_error(
    commands,
    account_service,
    menu_renderer,
    logger,
):
    account_service.withdraw.side_effect = ValueError("insufficient funds")

    commands.withdraw()

    menu_renderer.display_error.assert_called_once_with("insufficient funds")
    logger.exception.assert_called_once()


def test_apply_interest_gets_number_and_displays_result(
    commands,
    input_handler,
    account_service,
    menu_renderer,
):
    account = MagicMock(name="account")
    input_handler.get_value.return_value = "SA100001"
    account_service.apply_interest.return_value = account

    commands.apply_interest()

    input_handler.get_value.assert_called_once_with("Enter account number: ")
    account_service.apply_interest.assert_called_once_with("SA100001")
    menu_renderer.display_message.assert_called_once_with(
        "Interest applied successfully."
    )
    menu_renderer.display_object.assert_called_once_with(account)


def test_apply_interest_handles_error(
    commands,
    account_service,
    menu_renderer,
    logger,
):
    account_service.apply_interest.side_effect = ValueError("interest failed")

    commands.apply_interest()

    menu_renderer.display_error.assert_called_once_with("interest failed")
    logger.exception.assert_called_once()


def test_apply_fee_collects_number_and_fee_and_displays_result(
    commands,
    input_handler,
    account_service,
    menu_renderer,
):
    account = MagicMock(name="account")
    input_handler.get_value.return_value = "SA100001"
    input_handler.get_money.return_value = "5.00"
    account_service.apply_fee.return_value = account

    commands.apply_fee()

    input_handler.get_value.assert_called_once_with("Enter account number: ")
    input_handler.get_money.assert_called_once_with("Enter fee amount: ")
    account_service.apply_fee.assert_called_once_with("SA100001", "5.00")
    menu_renderer.display_message.assert_called_once_with(
        "Fee applied successfully."
    )
    menu_renderer.display_object.assert_called_once_with(account)


def test_apply_fee_handles_error(
    commands,
    account_service,
    menu_renderer,
    logger,
):
    account_service.apply_fee.side_effect = ValueError("fee failed")

    commands.apply_fee()

    menu_renderer.display_error.assert_called_once_with("fee failed")
    logger.exception.assert_called_once()


def test_close_account_returns_without_service_call_when_not_confirmed(
    commands,
    input_handler,
    account_service,
    menu_renderer,
):
    input_handler.get_value.return_value = "SA100001"
    input_handler.get_confirmation.return_value = False

    commands.close_account()

    input_handler.get_value.assert_called_once_with("Enter account number: ")
    input_handler.get_confirmation.assert_called_once_with(
        "Confirm account closure?"
    )
    account_service.close_account.assert_not_called()
    menu_renderer.display_message.assert_not_called()
    menu_renderer.display_error.assert_not_called()


def test_close_account_closes_confirmed_account(
    commands,
    input_handler,
    account_service,
    menu_renderer,
):
    input_handler.get_value.return_value = "SA100001"
    input_handler.get_confirmation.return_value = True

    commands.close_account()

    account_service.close_account.assert_called_once_with("SA100001")
    menu_renderer.display_message.assert_called_once_with(
        "Account closed successfully."
    )


def test_close_account_handles_error(
    commands,
    input_handler,
    account_service,
    menu_renderer,
    logger,
):
    input_handler.get_value.return_value = "SA100001"
    input_handler.get_confirmation.return_value = True
    account_service.close_account.side_effect = ValueError("cannot close account")

    commands.close_account()

    menu_renderer.display_error.assert_called_once_with("cannot close account")
    logger.exception.assert_called_once()


def test_collect_account_data_returns_expected_payload(
    commands,
    input_handler,
):
    input_handler.get_value.side_effect = ["C000001", "current"]
    input_handler.get_money.return_value = "500.00"

    result = commands._collect_account_data()

    assert result == {
        "customer_id": "C000001",
        "account_type": "current",
        "initial_deposit": "500.00",
    }
    assert input_handler.get_value.call_args_list[0].args == (
        "Customer ID: ",
    )
    assert input_handler.get_value.call_args_list[1].args == (
        "Account type: ",
    )
    input_handler.get_money.assert_called_once_with("Initial deposit: ")


@pytest.mark.parametrize(
    ("method_name", "service_method", "error_message"),
    [
        ("view_account", "get_account", "view failed"),
        ("list_accounts", "get_all_accounts", "list failed"),
        ("deposit", "deposit", "deposit failed"),
        ("withdraw", "withdraw", "withdraw failed"),
        ("apply_interest", "apply_interest", "interest failed"),
        ("apply_fee", "apply_fee", "fee failed"),
        ("close_account", "close_account", "close failed"),
    ],
)
def test_command_handlers_convert_exceptions_to_display_errors(
    commands,
    input_handler,
    account_service,
    menu_renderer,
    logger,
    method_name,
    service_method,
    error_message,
):
    account_service_method = getattr(account_service, service_method)
    account_service_method.side_effect = RuntimeError(error_message)

    if method_name == "close_account":
        input_handler.get_confirmation.return_value = True
    if method_name != "list_accounts":
        input_handler.get_value.return_value = "SA100001"
    if method_name in {"deposit", "withdraw", "apply_fee"}:
        input_handler.get_money.return_value = "10.00"

    getattr(commands, method_name)()

    menu_renderer.display_error.assert_called_once_with(error_message)
    logger.exception.assert_called_once()
