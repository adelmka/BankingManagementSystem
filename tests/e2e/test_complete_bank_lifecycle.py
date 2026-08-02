"""
============================================================
End-to-End Tests

Complete Banking Lifecycle

These tests execute realistic banking workflows using
the real application stack.

No mocks are used.
============================================================
"""

import pytest

from exceptions.banking_exceptions import (
    AccountNotFoundError,
    CustomerNotFoundError,
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


# Scenario 1 — Complete Customer Lifecycle

# ============================================================
# Customer Lifecycle
# ============================================================

def test_complete_customer_lifecycle(

    customer_service,

):

    create_customer(customer_service)

    customer = customer_service.find_customer(

        "CUST001"

    )

    assert customer.customer_id == "CUST001"

    customer_service.update_customer(

        customer_id="CUST001",

        first_name="Johnny",

        last_name="Smith",

        email="johnny@test.com",

        phone="+966501111111",

    )

    customer = customer_service.find_customer(

        "CUST001"

    )

    assert customer.first_name == "Johnny"

    customer_service.delete_customer(

        "CUST001"

    )

    with pytest.raises(

        CustomerNotFoundError

    ):

        customer_service.find_customer(

            "CUST001"

        )

# Scenario 2 — Savings Account Lifecycle

# ============================================================
# Savings Account Lifecycle
# ============================================================

def test_complete_savings_account_lifecycle(

    customer_service,

    account_service,

):

    create_customer(customer_service)

    account_service.open_savings_account(

        customer_id="CUST001",

        account_number="SAV001",

        opening_balance=1000,

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

# Scenario 3 — Transfer Between Accounts

# ============================================================
# Transfer Workflow
# ============================================================

def test_complete_transfer_workflow(

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

# Scenario 4 — Restart Application

# ============================================================
# Restart Application
# ============================================================

def test_application_restart(

    customer_service,

    account_service,

    transaction_service,

    reload_customer_repository,

    reload_account_repository,

    reload_transaction_repository,

):

    create_customer(customer_service)

    account_service.open_savings_account(

        "CUST001",

        "SAV001",

        1000,

    )

    transaction_service.deposit(

        "SAV001",

        500,

    )

    customer_repo = reload_customer_repository()

    account_repo = reload_account_repository()

    transaction_repo = reload_transaction_repository()

    assert customer_repo.find_by_id(

        "CUST001"

    ) is not None

    assert account_repo.find_by_account_number(

        "SAV001"

    ) is not None

    assert len(

        transaction_repo.get_all()

    ) == 1

# Scenario 5 — Customer Owns Multiple Accounts

# ============================================================
# Multiple Accounts
# ============================================================

def test_customer_multiple_accounts(

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

    savings = account_service.find_account(

        "SAV001"

    )

    current = account_service.find_account(

        "CUR001"

    )

    assert savings.customer_id == "CUST001"

    assert current.customer_id == "CUST001"

# Scenario 6 — Long Banking Session

# ============================================================
# Long Banking Session
# ============================================================

def test_long_banking_session(

    customer_service,

    account_service,

):

    create_customer(customer_service)

    account_service.open_savings_account(

        "CUST001",

        "SAV001",

        1000,

    )

    for _ in range(20):

        account_service.deposit(

            "SAV001",

            100,

        )

        account_service.withdraw(

            "SAV001",

            50,

        )

    balance = account_service.get_balance(

        "SAV001"

    )

    assert balance == 2000

# Scenario 7 — Full Bank Lifecycle

# ============================================================
# Full Lifecycle
# ============================================================

def test_complete_bank_lifecycle(

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

        1000,

    )

    account_service.withdraw(

        "SAV001",

        500,

    )

    account_service.close_account(

        "SAV001"

    )

    customer_service.delete_customer(

        "CUST001"

    )

    with pytest.raises(

        CustomerNotFoundError

    ):

        customer_service.find_customer(

            "CUST001"
        )

