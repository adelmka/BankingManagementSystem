"""
============================================================
Integration Tests

Transaction Workflow

Verifies

TransactionService
↓

AccountService
↓

Repositories
↓

CSV Persistence

No mocks are used.
============================================================
"""

import pytest

from exceptions.banking_exceptions import (
    AccountNotFoundError,
    InsufficientFundsError,
    ValidationError,
)

# ============================================================
# Test Data
# ============================================================

def setup_accounts(

    customer_service,

    account_service,

):

    customer_service.create_customer(

        customer_id="CUST001",

        first_name="John",

        last_name="Smith",

        email="john@test.com",

        phone="+966501111111",

    )

    account_service.open_savings_account(

        customer_id="CUST001",

        account_number="SAV001",

        opening_balance=1000,

    )

    account_service.open_current_account(

        customer_id="CUST001",

        account_number="CUR001",

        opening_balance=500,

    )

# ============================================================
# Deposit Workflow
# ============================================================

def test_deposit_workflow(

    customer_service,

    account_service,

    transaction_service,

):

    setup_accounts(

        customer_service,

        account_service,

    )

    transaction_service.deposit(

        "SAV001",

        250,

    )

    balance = account_service.get_balance(

        "SAV001"

    )

    assert balance == 1250

# ============================================================
# Withdrawal Workflow
# ============================================================

def test_withdraw_workflow(

    customer_service,

    account_service,

    transaction_service,

):

    setup_accounts(

        customer_service,

        account_service,

    )

    transaction_service.withdraw(

        "SAV001",

        400,

    )

    balance = account_service.get_balance(

        "SAV001"

    )

    assert balance == 600

# ============================================================
# Transfer Workflow
# ============================================================

def test_transfer_workflow(

    customer_service,

    account_service,

    transaction_service,

):

    setup_accounts(

        customer_service,

        account_service,

    )

    transaction_service.transfer(

        "SAV001",

        "CUR001",

        300,

    )

    assert (

        account_service.get_balance(

            "SAV001"

        )

        == 700

    )

    assert (

        account_service.get_balance(

            "CUR001"

        )

        == 800

    )

# ============================================================
# Multiple Transactions
# ============================================================

def test_multiple_transactions(

    customer_service,

    account_service,

    transaction_service,

):

    setup_accounts(

        customer_service,

        account_service,

    )

    transaction_service.deposit(

        "SAV001",

        200,

    )

    transaction_service.withdraw(

        "SAV001",

        150,

    )

    transaction_service.deposit(

        "CUR001",

        500,

    )

    transaction_service.transfer(

        "CUR001",

        "SAV001",

        100,

    )

    assert (

        account_service.get_balance(

            "SAV001"

        )

        == 1150

    )

    assert (

        account_service.get_balance(

            "CUR001"

        )

        == 900

    )

# ============================================================
# Insufficient Funds
# ============================================================

def test_insufficient_funds(

    customer_service,

    account_service,

    transaction_service,

):

    setup_accounts(

        customer_service,

        account_service,

    )

    with pytest.raises(

        InsufficientFundsError

    ):

        transaction_service.withdraw(

            "CUR001",

            5000,

        )

# ============================================================
# Unknown Account
# ============================================================

def test_unknown_account(

    transaction_service,

):

    with pytest.raises(

        AccountNotFoundError

    ):

        transaction_service.deposit(

            "UNKNOWN",

            100,

        )

# ============================================================
# Validation
# ============================================================

def test_invalid_transaction(

    customer_service,

    account_service,

    transaction_service,

):

    setup_accounts(

        customer_service,

        account_service,

    )

    with pytest.raises(

        ValidationError

    ):

        transaction_service.deposit(

            "SAV001",

            -100,

        )

# ============================================================
# Transaction Persistence
# ============================================================

def test_transaction_persistence(

    customer_service,

    account_service,

    transaction_service,

    reload_transaction_repository,

):

    setup_accounts(

        customer_service,

        account_service,

    )

    transaction_service.deposit(

        "SAV001",

        250,

    )

    repository = reload_transaction_repository()

    transactions = repository.get_all()

    assert len(transactions) == 1

# ============================================================
# Repository Restart
# ============================================================

def test_transaction_repository_restart(

    customer_service,

    account_service,

    transaction_service,

    reload_transaction_repository,

):

    setup_accounts(

        customer_service,

        account_service,

    )

    transaction_service.withdraw(

        "SAV001",

        100,

    )

    repository = reload_transaction_repository()

    transactions = repository.get_all()

    assert len(transactions) == 1

# ============================================================
# Complete Transaction Lifecycle
# ============================================================

def test_transaction_lifecycle(

    customer_service,

    account_service,

    transaction_service,

):

    setup_accounts(

        customer_service,

        account_service,

    )

    transaction_service.deposit(

        "SAV001",

        500,

    )

    transaction_service.withdraw(

        "SAV001",

        200,

    )

    transaction_service.transfer(

        "SAV001",

        "CUR001",

        300,

    )

    assert (

        account_service.get_balance(

            "SAV001"

        )

        == 1000

    )

    assert (

        account_service.get_balance(

            "CUR001"

        )

        == 800

    )

