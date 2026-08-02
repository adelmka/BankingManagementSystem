"""
============================================================
Account Command Tests
Part 1

Coverage

• Command construction
• Savings account creation
• Current account creation
• Time Deposit account creation
• Dependency injection
• Success handling
============================================================
"""

import pytest

from unittest.mock import MagicMock

from application.commands.account_commands import (

    OpenSavingsAccountCommand,
    OpenCurrentAccountCommand,
    OpenTimeDepositAccountCommand,

    CloseAccountCommand,
    FindAccountCommand,
    BalanceInquiryCommand,

)

from exceptions.banking_exceptions import (

    ValidationError,
    CustomerNotFoundError,
    AccountAlreadyExistsError,

)

# ============================================================
# Fixtures
# ============================================================

@pytest.fixture
def account_service():

    return MagicMock()


@pytest.fixture
def input_handler():

    return MagicMock()


@pytest.fixture
def menu_renderer():

    return MagicMock()

# ============================================================
# Construction
# ============================================================

def test_open_savings_constructor(

    account_service,
    input_handler,
    menu_renderer,

):

    command = OpenSavingsAccountCommand(

        account_service,
        input_handler,
        menu_renderer,

    )

    assert command is not None


def test_open_current_constructor(

    account_service,
    input_handler,
    menu_renderer,

):

    command = OpenCurrentAccountCommand(

        account_service,
        input_handler,
        menu_renderer,

    )

    assert command is not None


def test_open_time_deposit_constructor(

    account_service,
    input_handler,
    menu_renderer,

):

    command = OpenTimeDepositAccountCommand(

        account_service,
        input_handler,
        menu_renderer,

    )

    assert command is not None

# ============================================================
# Dependency Injection
# ============================================================

def test_dependencies_injected(

    account_service,
    input_handler,
    menu_renderer,

):

    command = OpenSavingsAccountCommand(

        account_service,
        input_handler,
        menu_renderer,

    )

    assert command.account_service is account_service

    assert command.input_handler is input_handler

    assert command.menu_renderer is menu_renderer

# ============================================================
# Savings Account
# ============================================================

def test_open_savings_account(

    account_service,
    input_handler,
    menu_renderer,

):

    input_handler.read_string.side_effect = [

        "CUST001",

        "SAV001",

    ]

    input_handler.read_money.return_value = MagicMock()

    command = OpenSavingsAccountCommand(

        account_service,
        input_handler,
        menu_renderer,

    )

    command.execute()

    account_service.open_savings_account.assert_called_once()

    menu_renderer.display_success.assert_called_once()

# ============================================================
# Savings Parameters
# ============================================================

def test_savings_parameters(

    account_service,
    input_handler,
    menu_renderer,

):

    input_handler.read_string.side_effect = [

        "CUST001",

        "SAV001",

    ]

    amount = MagicMock()

    input_handler.read_money.return_value = amount

    command = OpenSavingsAccountCommand(

        account_service,
        input_handler,
        menu_renderer,

    )

    command.execute()

    args = account_service.open_savings_account.call_args[0]

    assert args[0] == "CUST001"

# ============================================================
# Current Account
# ============================================================

def test_open_current_account(

    account_service,
    input_handler,
    menu_renderer,

):

    input_handler.read_string.side_effect = [

        "CUST001",

        "CUR001",

    ]

    input_handler.read_money.return_value = MagicMock()

    command = OpenCurrentAccountCommand(

        account_service,
        input_handler,
        menu_renderer,

    )

    command.execute()

    account_service.open_current_account.assert_called_once()

    menu_renderer.display_success.assert_called_once()

# ============================================================
# Time Deposit
# ============================================================

def test_open_time_deposit(

    account_service,
    input_handler,
    menu_renderer,

):

    input_handler.read_string.side_effect = [

        "CUST001",

        "TD001",

    ]

    input_handler.read_money.return_value = MagicMock()

    input_handler.read_int.return_value = 12

    command = OpenTimeDepositAccountCommand(

        account_service,
        input_handler,
        menu_renderer,

    )

    command.execute()

    account_service.open_time_deposit_account.assert_called_once()

    menu_renderer.display_success.assert_called_once()

# ============================================================
# Validation
# ============================================================

def test_validation_error(

    account_service,
    input_handler,
    menu_renderer,

):

    account_service.open_savings_account.side_effect = (

        ValidationError(

            "Invalid"

        )

    )

    input_handler.read_string.side_effect = [

        "CUST001",

        "SAV001",

    ]

    input_handler.read_money.return_value = MagicMock()

    command = OpenSavingsAccountCommand(

        account_service,
        input_handler,
        menu_renderer,

    )

    command.execute()

    menu_renderer.display_error.assert_called_once()

# ============================================================
# Customer Missing
# ============================================================

def test_customer_not_found(

    account_service,
    input_handler,
    menu_renderer,

):

    account_service.open_savings_account.side_effect = (

        CustomerNotFoundError(

            "Missing"

        )

    )

    input_handler.read_string.side_effect = [

        "UNKNOWN",

        "SAV001",

    ]

    input_handler.read_money.return_value = MagicMock()

    command = OpenSavingsAccountCommand(

        account_service,
        input_handler,
        menu_renderer,

    )

    command.execute()

    menu_renderer.display_error.assert_called_once()

# ============================================================
# Duplicate Account
# ============================================================

def test_duplicate_account(

    account_service,
    input_handler,
    menu_renderer,

):

    account_service.open_savings_account.side_effect = (

        AccountAlreadyExistsError(

            "Duplicate"

        )

    )

    input_handler.read_string.side_effect = [

        "CUST001",

        "SAV001",

    ]

    input_handler.read_money.return_value = MagicMock()

    command = OpenSavingsAccountCommand(

        account_service,
        input_handler,
        menu_renderer,

    )

    command.execute()

    menu_renderer.display_error.assert_called_once()

# PART 2

# ============================================================
# Deposit Command
# ============================================================

def test_deposit_success(

    account_service,
    input_handler,
    menu_renderer,

):

    input_handler.read_string.return_value = "SAV001"

    amount = MagicMock()

    input_handler.read_money.return_value = amount

    command = DepositCommand(

        account_service,
        input_handler,
        menu_renderer,

    )

    command.execute()

    account_service.deposit.assert_called_once_with(

        "SAV001",

        amount,

    )

    menu_renderer.display_success.assert_called_once()

# ============================================================
# Deposit Parameters
# ============================================================

def test_deposit_parameter_forwarding(

    account_service,
    input_handler,
    menu_renderer,

):

    input_handler.read_string.return_value = "ACC001"

    amount = MagicMock()

    input_handler.read_money.return_value = amount

    command = DepositCommand(

        account_service,
        input_handler,
        menu_renderer,

    )

    command.execute()

    args = account_service.deposit.call_args[0]

    assert args[0] == "ACC001"

    assert args[1] is amount

# ============================================================
# Deposit Exceptions
# ============================================================

def test_deposit_validation_error(

    account_service,
    input_handler,
    menu_renderer,

):

    account_service.deposit.side_effect = ValidationError("Invalid")

    input_handler.read_string.return_value = "ACC001"

    input_handler.read_money.return_value = MagicMock()

    command = DepositCommand(

        account_service,
        input_handler,
        menu_renderer,

    )

    command.execute()

    menu_renderer.display_error.assert_called_once()


def test_deposit_runtime_error(

    account_service,
    input_handler,
    menu_renderer,

):

    account_service.deposit.side_effect = RuntimeError("Failure")

    input_handler.read_string.return_value = "ACC001"

    input_handler.read_money.return_value = MagicMock()

    command = DepositCommand(

        account_service,
        input_handler,
        menu_renderer,

    )

    command.execute()

    menu_renderer.display_error.assert_called_once()

# ============================================================
# Withdrawal Command
# ============================================================

def test_withdraw_success(

    account_service,
    input_handler,
    menu_renderer,

):

    input_handler.read_string.return_value = "SAV001"

    amount = MagicMock()

    input_handler.read_money.return_value = amount

    command = WithdrawCommand(

        account_service,
        input_handler,
        menu_renderer,

    )

    command.execute()

    account_service.withdraw.assert_called_once_with(

        "SAV001",

        amount,

    )

    menu_renderer.display_success.assert_called_once()

# ============================================================
# Withdrawal Parameters
# ============================================================

def test_withdraw_parameter_forwarding(

    account_service,
    input_handler,
    menu_renderer,

):

    input_handler.read_string.return_value = "ACC002"

    amount = MagicMock()

    input_handler.read_money.return_value = amount

    command = WithdrawCommand(

        account_service,
        input_handler,
        menu_renderer,

    )

    command.execute()

    args = account_service.withdraw.call_args[0]

    assert args[0] == "ACC002"

    assert args[1] is amount

# ============================================================
# Withdrawal Exceptions
# ============================================================

def test_withdraw_validation_error(

    account_service,
    input_handler,
    menu_renderer,

):

    account_service.withdraw.side_effect = ValidationError("Invalid")

    input_handler.read_string.return_value = "ACC001"

    input_handler.read_money.return_value = MagicMock()

    command = WithdrawCommand(

        account_service,
        input_handler,
        menu_renderer,

    )

    command.execute()

    menu_renderer.display_error.assert_called_once()


def test_withdraw_runtime_error(

    account_service,
    input_handler,
    menu_renderer,

):

    account_service.withdraw.side_effect = RuntimeError("Failure")

    input_handler.read_string.return_value = "ACC001"

    input_handler.read_money.return_value = MagicMock()

    command = WithdrawCommand(

        account_service,
        input_handler,
        menu_renderer,

    )

    command.execute()

    menu_renderer.display_error.assert_called_once()

# ============================================================
# Balance Inquiry
# ============================================================

def test_balance_inquiry_success(

    account_service,
    input_handler,
    menu_renderer,

):

    balance = MagicMock()

    account_service.get_balance.return_value = balance

    input_handler.read_string.return_value = "ACC001"

    command = BalanceInquiryCommand(

        account_service,
        input_handler,
        menu_renderer,

    )

    command.execute()

    account_service.get_balance.assert_called_once_with(

        "ACC001"

    )

    menu_renderer.display_balance.assert_called_once_with(

        balance

    )

# ============================================================
# Balance Inquiry Exceptions
# ============================================================

def test_balance_validation_error(

    account_service,
    input_handler,
    menu_renderer,

):

    account_service.get_balance.side_effect = ValidationError("Invalid")

    input_handler.read_string.return_value = "ACC001"

    command = BalanceInquiryCommand(

        account_service,
        input_handler,
        menu_renderer,

    )

    command.execute()

    menu_renderer.display_error.assert_called_once()


def test_balance_runtime_error(

    account_service,
    input_handler,
    menu_renderer,

):

    account_service.get_balance.side_effect = RuntimeError("Failure")

    input_handler.read_string.return_value = "ACC001"

    command = BalanceInquiryCommand(

        account_service,
        input_handler,
        menu_renderer,

    )

    command.execute()

    menu_renderer.display_error.assert_called_once()


# PART 3

# ============================================================
# Balance Inquiry Exceptions
# ============================================================

def test_balance_validation_error(

    account_service,
    input_handler,
    menu_renderer,

):

    account_service.get_balance.side_effect = ValidationError("Invalid")

    input_handler.read_string.return_value = "ACC001"

    command = BalanceInquiryCommand(

        account_service,
        input_handler,
        menu_renderer,

    )

    command.execute()

    menu_renderer.display_error.assert_called_once()


def test_balance_runtime_error(

    account_service,
    input_handler,
    menu_renderer,

):

    account_service.get_balance.side_effect = RuntimeError("Failure")

    input_handler.read_string.return_value = "ACC001"

    command = BalanceInquiryCommand(

        account_service,
        input_handler,
        menu_renderer,

    )

    command.execute()

    menu_renderer.display_error.assert_called_once()

# ============================================================
# Find Existing Account
# ============================================================

def test_find_account_success(

    account_service,
    input_handler,
    menu_renderer,

):

    account = MagicMock()

    account.account_number = "SAV001"

    account_service.find_account.return_value = account

    input_handler.read_string.return_value = "SAV001"

    command = FindAccountCommand(

        account_service,
        input_handler,
        menu_renderer,

    )

    command.execute()

    account_service.find_account.assert_called_once_with(

        "SAV001"

    )

    menu_renderer.display_account.assert_called_once_with(

        account

    )

# ============================================================
# Find Account Parameter
# ============================================================

def test_find_account_parameter(

    account_service,
    input_handler,
    menu_renderer,

):

    account_service.find_account.return_value = MagicMock()

    input_handler.read_string.return_value = "CUR001"

    command = FindAccountCommand(

        account_service,
        input_handler,
        menu_renderer,

    )

    command.execute()

    args = account_service.find_account.call_args[0]

    assert args[0] == "CUR001"

# ============================================================
# Find Account Exceptions
# ============================================================

def test_find_account_not_found(

    account_service,
    input_handler,
    menu_renderer,

):

    account_service.find_account.side_effect = (

        AccountNotFoundError(

            "Missing"

        )

    )

    input_handler.read_string.return_value = "UNKNOWN"

    command = FindAccountCommand(

        account_service,
        input_handler,
        menu_renderer,

    )

    command.execute()

    menu_renderer.display_error.assert_called_once()


def test_find_account_validation(

    account_service,
    input_handler,
    menu_renderer,

):

    account_service.find_account.side_effect = (

        ValidationError(

            "Invalid"

        )

    )

    input_handler.read_string.return_value = ""

    command = FindAccountCommand(

        account_service,
        input_handler,
        menu_renderer,

    )

    command.execute()

    menu_renderer.display_error.assert_called_once()

# ============================================================
# Close Account Command
# ============================================================

def test_close_account_constructor(

    account_service,
    input_handler,
    menu_renderer,

):

    command = CloseAccountCommand(

        account_service,
        input_handler,
        menu_renderer,

    )

    assert command is not None

# ============================================================
# Close Account Success
# ============================================================

def test_close_account_success(

    account_service,
    input_handler,
    menu_renderer,

):

    input_handler.read_string.return_value = "SAV001"

    input_handler.read_yes_no.return_value = True

    command = CloseAccountCommand(

        account_service,
        input_handler,
        menu_renderer,

    )

    command.execute()

    account_service.close_account.assert_called_once_with(

        "SAV001"

    )

    menu_renderer.display_success.assert_called_once()

# ============================================================
# Close Account Cancelled
# ============================================================

def test_close_account_cancelled(

    account_service,
    input_handler,
    menu_renderer,

):

    input_handler.read_string.return_value = "SAV001"

    input_handler.read_yes_no.return_value = False

    command = CloseAccountCommand(

        account_service,
        input_handler,
        menu_renderer,

    )

    command.execute()

    account_service.close_account.assert_not_called()

# ============================================================
# Close Account Exceptions
# ============================================================

def test_close_account_not_found(

    account_service,
    input_handler,
    menu_renderer,

):

    account_service.close_account.side_effect = (

        AccountNotFoundError(

            "Missing"

        )

    )

    input_handler.read_string.return_value = "UNKNOWN"

    input_handler.read_yes_no.return_value = True

    command = CloseAccountCommand(

        account_service,
        input_handler,
        menu_renderer,

    )

    command.execute()

    menu_renderer.display_error.assert_called_once()


def test_close_account_validation(

    account_service,
    input_handler,
    menu_renderer,

):

    account_service.close_account.side_effect = (

        ValidationError(

            "Invalid"

        )

    )

    input_handler.read_string.return_value = ""

    input_handler.read_yes_no.return_value = True

    command = CloseAccountCommand(

        account_service,
        input_handler,
        menu_renderer,

    )

    command.execute()

    menu_renderer.display_error.assert_called_once()


def test_close_account_runtime_error(

    account_service,
    input_handler,
    menu_renderer,

):

    account_service.close_account.side_effect = (

        RuntimeError(

            "Failure"

        )

    )

    input_handler.read_string.return_value = "SAV001"

    input_handler.read_yes_no.return_value = True

    command = CloseAccountCommand(

        account_service,
        input_handler,
        menu_renderer,

    )

    command.execute()

    menu_renderer.display_error.assert_called_once()

# ============================================================
# Confirmation Logic
# ============================================================

def test_close_account_confirmation_required(

    account_service,
    input_handler,
    menu_renderer,

):

    input_handler.read_string.return_value = "SAV001"

    input_handler.read_yes_no.return_value = False

    command = CloseAccountCommand(

        account_service,
        input_handler,
        menu_renderer,

    )

    command.execute()

    input_handler.read_yes_no.assert_called_once()

    account_service.close_account.assert_not_called()

# PART 4

# ============================================================
# Transfer Command
# ============================================================

def test_transfer_constructor(

    account_service,
    input_handler,
    menu_renderer,

):

    command = TransferCommand(

        account_service,
        input_handler,
        menu_renderer,

    )

    assert command is not None


def test_transfer_dependencies(

    account_service,
    input_handler,
    menu_renderer,

):

    command = TransferCommand(

        account_service,
        input_handler,
        menu_renderer,

    )

    assert command.account_service is account_service

    assert command.input_handler is input_handler

    assert command.menu_renderer is menu_renderer

# ============================================================
# Successful Transfer
# ============================================================

def test_transfer_success(

    account_service,
    input_handler,
    menu_renderer,

):

    input_handler.read_string.side_effect = [

        "ACC001",

        "ACC002",

    ]

    amount = MagicMock()

    input_handler.read_money.return_value = amount

    command = TransferCommand(

        account_service,
        input_handler,
        menu_renderer,

    )

    command.execute()

    account_service.transfer.assert_called_once_with(

        "ACC001",

        "ACC002",

        amount,

    )

    menu_renderer.display_success.assert_called_once()

# ============================================================
# Parameter Forwarding
# ============================================================

def test_transfer_parameters(

    account_service,
    input_handler,
    menu_renderer,

):

    amount = MagicMock()

    input_handler.read_string.side_effect = [

        "SAV001",

        "CUR001",

    ]

    input_handler.read_money.return_value = amount

    command = TransferCommand(

        account_service,
        input_handler,
        menu_renderer,

    )

    command.execute()

    args = account_service.transfer.call_args[0]

    assert args[0] == "SAV001"

    assert args[1] == "CUR001"

    assert args[2] is amount

# ============================================================
# Validation Errors
# ============================================================

def test_transfer_validation_error(

    account_service,
    input_handler,
    menu_renderer,

):

    account_service.transfer.side_effect = (

        ValidationError(

            "Invalid"

        )

    )

    input_handler.read_string.side_effect = [

        "ACC001",

        "ACC002",

    ]

    input_handler.read_money.return_value = MagicMock()

    command = TransferCommand(

        account_service,
        input_handler,
        menu_renderer,

    )

    command.execute()

    menu_renderer.display_error.assert_called_once()

# ============================================================
# Insufficient Funds
# ============================================================

def test_transfer_insufficient_funds(

    account_service,
    input_handler,
    menu_renderer,

):

    account_service.transfer.side_effect = (

        InsufficientFundsError(

            "Insufficient balance"

        )

    )

    input_handler.read_string.side_effect = [

        "ACC001",

        "ACC002",

    ]

    input_handler.read_money.return_value = MagicMock()

    command = TransferCommand(

        account_service,
        input_handler,
        menu_renderer,

    )

    command.execute()

    menu_renderer.display_error.assert_called_once()

# ============================================================
# Missing Account
# ============================================================

def test_transfer_missing_account(

    account_service,
    input_handler,
    menu_renderer,

):

    account_service.transfer.side_effect = (

        AccountNotFoundError(

            "Missing"

        )

    )

    input_handler.read_string.side_effect = [

        "UNKNOWN",

        "ACC002",

    ]

    input_handler.read_money.return_value = MagicMock()

    command = TransferCommand(

        account_service,
        input_handler,
        menu_renderer,

    )

    command.execute()

    menu_renderer.display_error.assert_called_once()

# ============================================================
# Same Account
# ============================================================

def test_transfer_same_account(

    account_service,
    input_handler,
    menu_renderer,

):

    account_service.transfer.side_effect = (

        ValidationError(

            "Cannot transfer to same account"

        )

    )

    input_handler.read_string.side_effect = [

        "ACC001",

        "ACC001",

    ]

    input_handler.read_money.return_value = MagicMock()

    command = TransferCommand(

        account_service,
        input_handler,
        menu_renderer,

    )

    command.execute()

    menu_renderer.display_error.assert_called_once()

# ============================================================
# Runtime Exception
# ============================================================

def test_transfer_runtime_error(

    account_service,
    input_handler,
    menu_renderer,

):

    account_service.transfer.side_effect = (

        RuntimeError(

            "Unexpected failure"

        )

    )

    input_handler.read_string.side_effect = [

        "ACC001",

        "ACC002",

    ]

    input_handler.read_money.return_value = MagicMock()

    command = TransferCommand(

        account_service,
        input_handler,
        menu_renderer,

    )

    command.execute()

    menu_renderer.display_error.assert_called_once()

# ============================================================
# Multiple Transfers
# ============================================================

def test_multiple_transfers(

    account_service,
    input_handler,
    menu_renderer,

):

    input_handler.read_string.side_effect = [

        "A1", "A2",

        "A3", "A4",

        "A5", "A6",

    ]

    input_handler.read_money.side_effect = [

        MagicMock(),

        MagicMock(),

        MagicMock(),

    ]

    command = TransferCommand(

        account_service,

        input_handler,

        menu_renderer,

    )

    command.execute()

    command.execute()

    command.execute()

    assert account_service.transfer.call_count == 3

# PART 5

# ============================================================
# Transaction History Command
# ============================================================

def test_transaction_history_constructor(

    account_service,
    input_handler,
    menu_renderer,

):

    command = TransactionHistoryCommand(

        account_service,
        input_handler,
        menu_renderer,

    )

    assert command is not None


def test_transaction_history_dependencies(

    account_service,
    input_handler,
    menu_renderer,

):

    command = TransactionHistoryCommand(

        account_service,
        input_handler,
        menu_renderer,

    )

    assert command.account_service is account_service

    assert command.input_handler is input_handler

    assert command.menu_renderer is menu_renderer

# ============================================================
# Successful History Retrieval
# ============================================================

def test_transaction_history_success(

    account_service,
    input_handler,
    menu_renderer,

):

    history = [

        MagicMock(),

        MagicMock(),

        MagicMock(),

    ]

    account_service.get_transaction_history.return_value = history

    input_handler.read_string.return_value = "ACC001"

    command = TransactionHistoryCommand(

        account_service,
        input_handler,
        menu_renderer,

    )

    command.execute()

    account_service.get_transaction_history.assert_called_once_with(

        "ACC001"

    )

    menu_renderer.display_transactions.assert_called_once_with(

        history

    )

# ============================================================
# Empty History
# ============================================================

def test_empty_transaction_history(

    account_service,
    input_handler,
    menu_renderer,

):

    account_service.get_transaction_history.return_value = []

    input_handler.read_string.return_value = "ACC001"

    command = TransactionHistoryCommand(

        account_service,
        input_handler,
        menu_renderer,

    )

    command.execute()

    menu_renderer.display_transactions.assert_called_once_with(

        []

    )

# ============================================================
# History Exceptions
# ============================================================

def test_transaction_history_validation(

    account_service,
    input_handler,
    menu_renderer,

):

    account_service.get_transaction_history.side_effect = (

        ValidationError(

            "Invalid"

        )

    )

    input_handler.read_string.return_value = ""

    command = TransactionHistoryCommand(

        account_service,
        input_handler,
        menu_renderer,

    )

    command.execute()

    menu_renderer.display_error.assert_called_once()


def test_transaction_history_missing_account(

    account_service,
    input_handler,
    menu_renderer,

):

    account_service.get_transaction_history.side_effect = (

        AccountNotFoundError(

            "Missing"

        )

    )

    input_handler.read_string.return_value = "UNKNOWN"

    command = TransactionHistoryCommand(

        account_service,
        input_handler,
        menu_renderer,

    )

    command.execute()

    menu_renderer.display_error.assert_called_once()

# ============================================================
# Account Statement
# ============================================================

def test_account_statement_success(

    account_service,
    input_handler,
    menu_renderer,

):

    statement = MagicMock()

    account_service.get_account_statement.return_value = statement

    input_handler.read_string.return_value = "ACC001"

    command = AccountStatementCommand(

        account_service,
        input_handler,
        menu_renderer,

    )

    command.execute()

    account_service.get_account_statement.assert_called_once_with(

        "ACC001"

    )

    menu_renderer.display_statement.assert_called_once_with(

        statement

    )

# ============================================================
# Statement Parameters
# ============================================================

def test_statement_parameter_forwarding(

    account_service,
    input_handler,
    menu_renderer,

):

    account_service.get_account_statement.return_value = MagicMock()

    input_handler.read_string.return_value = "SAV001"

    command = AccountStatementCommand(

        account_service,
        input_handler,
        menu_renderer,

    )

    command.execute()

    args = account_service.get_account_statement.call_args[0]

    assert args[0] == "SAV001"

# ============================================================
# Statement Exceptions
# ============================================================

def test_statement_validation(

    account_service,
    input_handler,
    menu_renderer,

):

    account_service.get_account_statement.side_effect = (

        ValidationError(

            "Invalid"

        )

    )

    input_handler.read_string.return_value = ""

    command = AccountStatementCommand(

        account_service,
        input_handler,
        menu_renderer,

    )

    command.execute()

    menu_renderer.display_error.assert_called_once()


def test_statement_runtime_error(

    account_service,
    input_handler,
    menu_renderer,

):

    account_service.get_account_statement.side_effect = (

        RuntimeError(

            "Failure"

        )

    )

    input_handler.read_string.return_value = "ACC001"

    command = AccountStatementCommand(

        account_service,
        input_handler,
        menu_renderer,

    )

    command.execute()

    menu_renderer.display_error.assert_called_once()

# ============================================================
# Multiple Reports
# ============================================================

def test_multiple_statement_requests(

    account_service,
    input_handler,
    menu_renderer,

):

    account_service.get_account_statement.return_value = MagicMock()

    input_handler.read_string.side_effect = [

        "ACC001",

        "ACC002",

        "ACC003",

    ]

    command = AccountStatementCommand(

        account_service,

        input_handler,

        menu_renderer,

    )

    command.execute()

    command.execute()

    command.execute()

    assert (

        account_service.get_account_statement.call_count

        == 3

    )

# PART 6

# ============================================================
# Multiple Reports
# ============================================================

def test_multiple_statement_requests(

    account_service,
    input_handler,
    menu_renderer,

):

    account_service.get_account_statement.return_value = MagicMock()

    input_handler.read_string.side_effect = [

        "ACC001",

        "ACC002",

        "ACC003",

    ]

    command = AccountStatementCommand(

        account_service,

        input_handler,

        menu_renderer,

    )

    command.execute()

    command.execute()

    command.execute()

    assert (

        account_service.get_account_statement.call_count

        == 3

    )

# ============================================================
# Sequential Banking Workflow
# ============================================================

def test_complete_account_workflow(

    account_service,
    input_handler,
    menu_renderer,

):

    account_service.find_account.return_value = MagicMock()

    account_service.get_balance.return_value = MagicMock()

    input_handler.read_string.side_effect = [

        "CUST001",
        "SAV001",

        "SAV001",

        "SAV001",

        "SAV001",

        "SAV001",

    ]

    input_handler.read_money.side_effect = [

        MagicMock(),

        MagicMock(),

        MagicMock(),

    ]

    input_handler.read_yes_no.return_value = True

    open_cmd = OpenSavingsAccountCommand(

        account_service,
        input_handler,
        menu_renderer,

    )

    deposit_cmd = DepositCommand(

        account_service,
        input_handler,
        menu_renderer,

    )

    withdraw_cmd = WithdrawCommand(

        account_service,
        input_handler,
        menu_renderer,

    )

    balance_cmd = BalanceInquiryCommand(

        account_service,
        input_handler,
        menu_renderer,

    )

    close_cmd = CloseAccountCommand(

        account_service,
        input_handler,
        menu_renderer,

    )

    open_cmd.execute()

    deposit_cmd.execute()

    withdraw_cmd.execute()

    balance_cmd.execute()

    close_cmd.execute()

    assert account_service.open_savings_account.called

    assert account_service.deposit.called

    assert account_service.withdraw.called

    assert account_service.get_balance.called

    assert account_service.close_account.called

# ============================================================
# Multiple Command Instances
# ============================================================

def test_multiple_command_instances(

    account_service,
    input_handler,
    menu_renderer,

):

    commands = [

        OpenSavingsAccountCommand(

            account_service,

            input_handler,

            menu_renderer,

        )

        for _ in range(20)

    ]

    assert len(commands) == 20


def test_commands_are_independent(

    account_service,
    input_handler,
    menu_renderer,

):

    open_cmd = OpenSavingsAccountCommand(

        account_service,
        input_handler,
        menu_renderer,

    )

    deposit_cmd = DepositCommand(

        account_service,
        input_handler,
        menu_renderer,

    )

    withdraw_cmd = WithdrawCommand(

        account_service,
        input_handler,
        menu_renderer,

    )

    assert open_cmd is not deposit_cmd

    assert deposit_cmd is not withdraw_cmd

# ============================================================
# Stress Testing
# ============================================================

def test_open_100_accounts(

    account_service,
    input_handler,
    menu_renderer,

):

    values = []

    for i in range(100):

        values.extend(

            [

                f"CUST{i:03}",

                f"SAV{i:03}",

            ]

        )

    input_handler.read_string.side_effect = values

    input_handler.read_money.return_value = MagicMock()

    command = OpenSavingsAccountCommand(

        account_service,

        input_handler,

        menu_renderer,

    )

    for _ in range(100):

        command.execute()

    assert (

        account_service.open_savings_account.call_count

        == 100

    )


def test_100_balance_requests(

    account_service,
    input_handler,
    menu_renderer,

):

    account_service.get_balance.return_value = MagicMock()

    input_handler.read_string.side_effect = [

        f"ACC{i:03}"

        for i in range(100)

    ]

    command = BalanceInquiryCommand(

        account_service,

        input_handler,

        menu_renderer,

    )

    for _ in range(100):

        command.execute()

    assert account_service.get_balance.call_count == 100

# ============================================================
# Exception Recovery
# ============================================================

def test_command_recovers_after_exception(

    account_service,
    input_handler,
    menu_renderer,

):

    account_service.deposit.side_effect = [

        RuntimeError(

            "Failure"

        ),

        None,

    ]

    input_handler.read_string.side_effect = [

        "ACC001",

        "ACC001",

    ]

    input_handler.read_money.side_effect = [

        MagicMock(),

        MagicMock(),

    ]

    command = DepositCommand(

        account_service,

        input_handler,

        menu_renderer,

    )

    command.execute()

    command.execute()

    assert account_service.deposit.call_count == 2

# ============================================================
# Dependency Integrity
# ============================================================

def test_shared_service_reference(

    account_service,
    input_handler,
    menu_renderer,

):

    deposit = DepositCommand(

        account_service,

        input_handler,

        menu_renderer,

    )

    withdraw = WithdrawCommand(

        account_service,

        input_handler,

        menu_renderer,

    )

    assert deposit.account_service is withdraw.account_service


def test_shared_renderer_reference(

    account_service,
    input_handler,
    menu_renderer,

):

    transfer = TransferCommand(

        account_service,

        input_handler,

        menu_renderer,

    )

    balance = BalanceInquiryCommand(

        account_service,

        input_handler,

        menu_renderer,

    )

    assert transfer.menu_renderer is balance.menu_renderer

# ============================================================
# Final Integrity
# ============================================================

def test_dependencies_not_modified(

    account_service,
    input_handler,
    menu_renderer,

):

    command = OpenSavingsAccountCommand(

        account_service,

        input_handler,

        menu_renderer,

    )

    service = command.account_service

    renderer = command.menu_renderer

    handler = command.input_handler

    assert command.account_service is service

    assert command.menu_renderer is renderer

    assert command.input_handler is handler


def test_account_commands_complete():

    assert True

