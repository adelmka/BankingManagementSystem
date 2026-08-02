"""
============================================================
Integration Tests

Account Workflow

Verifies interaction between

CustomerService
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
# Helper
# ============================================================

def create_customer(customer_service):

    return customer_service.create_customer(

        customer_id="CUST001",

        first_name="John",

        last_name="Smith",

        email="john@test.com",

        phone="+966501111111",

    )

# ============================================================
# Savings Account
# ============================================================

def test_open_savings_account(

    customer_service,

    account_service,

):

    create_customer(customer_service)

    account = account_service.open_savings_account(

        customer_id="CUST001",

        account_number="SAV001",

        opening_balance=1000,

    )

    assert account.account_number == "SAV001"

# ============================================================
# Find Account
# ============================================================

def test_find_account(

    customer_service,

    account_service,

):

    create_customer(customer_service)

    account_service.open_savings_account(

        "CUST001",

        "SAV001",

        1000,

    )

    account = account_service.find_account(

        "SAV001"

    )

    assert account.account_number == "SAV001"

# ============================================================
# Deposit
# ============================================================

def test_deposit(

    customer_service,

    account_service,

):

    create_customer(customer_service)

    account_service.open_savings_account(

        "CUST001",

        "SAV001",

        1000,

    )

    account_service.deposit(

        "SAV001",

        500,

    )

    balance = account_service.get_balance(

        "SAV001"

    )

    assert balance == 1500

# ============================================================
# Withdraw
# ============================================================

def test_withdraw(

    customer_service,

    account_service,

):

    create_customer(customer_service)

    account_service.open_savings_account(

        "CUST001",

        "SAV001",

        1000,

    )

    account_service.withdraw(

        "SAV001",

        300,

    )

    balance = account_service.get_balance(

        "SAV001"

    )

    assert balance == 700

# ============================================================
# Transfer
# ============================================================

def test_transfer(

    customer_service,

    account_service,

):

    create_customer(customer_service)

    account_service.open_savings_account(

        "CUST001",

        "SAV001",

        1000,

    )

    account_service.open_current_account(

        "CUST001",

        "CUR001",

        500,

    )

    account_service.transfer(

        "SAV001",

        "CUR001",

        250,

    )

    assert (

        account_service.get_balance(

            "SAV001"

        )

        == 750

    )

    assert (

        account_service.get_balance(

            "CUR001"

        )

        == 750

    )

# ============================================================
# Close Account
# ============================================================

def test_close_account(

    customer_service,

    account_service,

):

    create_customer(customer_service)

    account_service.open_savings_account(

        "CUST001",

        "SAV001",

        1000,

    )

    account_service.close_account(

        "SAV001"

    )

    with pytest.raises(

        AccountNotFoundError

    ):

        account_service.find_account(

            "SAV001"

        )

# ============================================================
# Validation
# ============================================================

def test_invalid_account(

    customer_service,

    account_service,

):

    create_customer(customer_service)

    with pytest.raises(

        ValidationError

    ):

        account_service.open_savings_account(

            "CUST001",

            "",

            1000,

        )

# ============================================================
# Insufficient Funds
# ============================================================

def test_insufficient_funds(

    customer_service,

    account_service,

):

    create_customer(customer_service)

    account_service.open_savings_account(

        "CUST001",

        "SAV001",

        100,

    )

    with pytest.raises(

        InsufficientFundsError

    ):

        account_service.withdraw(

            "SAV001",

            500,

        )

# ============================================================
# Persistence
# ============================================================

def test_account_persistence(

    customer_service,

    account_service,

    reload_account_repository,

):

    create_customer(customer_service)

    account_service.open_savings_account(

        "CUST001",

        "SAV001",

        1000,

    )

    repository = reload_account_repository()

    account = repository.find_by_account_number(

        "SAV001"

    )

    assert account.account_number == "SAV001"

# ============================================================
# Repository Restart
# ============================================================

def test_account_repository_restart(

    customer_service,

    account_service,

    reload_account_repository,

):

    create_customer(customer_service)

    account_service.open_current_account(

        "CUST001",

        "CUR001",

        2000,

    )

    repository = reload_account_repository()

    account = repository.find_by_account_number(

        "CUR001"

    )

    assert account.account_number == "CUR001"

# ============================================================
# Complete Lifecycle
# ============================================================

def test_account_lifecycle(

    customer_service,

    account_service,

):

    create_customer(customer_service)

    account_service.open_savings_account(

        "CUST001",

        "SAV001",

        1000,

    )

    account_service.deposit(

        "SAV001",

        500,

    )

    account_service.withdraw(

        "SAV001",

        200,

    )

    balance = account_service.get_balance(

        "SAV001"

    )

    assert balance == 1300

    account_service.close_account(

        "SAV001"

    )

    with pytest.raises(

        AccountNotFoundError

    ):

        account_service.find_account(

            "SAV001"

        )

