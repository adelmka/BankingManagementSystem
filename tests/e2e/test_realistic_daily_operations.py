"""
============================================================
End-to-End Tests

Realistic Daily Banking Operations

These tests simulate a complete banking day.

No mocks are used.
============================================================
"""

import pytest

# ============================================================
# Customer Creation
# ============================================================

def create_customer(

    customer_service,

    customer_number,

):

    return customer_service.create_customer(

        customer_id=customer_number,

        first_name="John",

        last_name="Smith",

        email=f"{customer_number.lower()}@bank.com",

        phone="+966501111111",

    )

# ============================================================
# Morning Opening
# ============================================================

def test_morning_opening(

    customer_service,

    account_service,

):

    for i in range(20):

        customer_id = f"CUST{i:03}"

        account_number = f"SAV{i:03}"

        create_customer(

            customer_service,

            customer_id,

        )

        account_service.open_savings_account(

            customer_id,

            account_number,

            1000,

        )

    for i in range(20):

        account = account_service.find_account(

            f"SAV{i:03}"

        )

        assert account.account_number == f"SAV{i:03}"

# ============================================================
# Morning Deposits
# ============================================================

def test_morning_deposits(

    customer_service,

    account_service,

):

    create_customer(

        customer_service,

        "CUST001",

    )

    account_service.open_savings_account(

        "CUST001",

        "SAV001",

        1000,

    )

    for _ in range(25):

        account_service.deposit(

            "SAV001",

            100,

        )

    assert (

        account_service.get_balance(

            "SAV001"

        )

        == 3500

    )

# ============================================================
# Afternoon Withdrawals
# ============================================================

def test_afternoon_withdrawals(

    customer_service,

    account_service,

):

    create_customer(

        customer_service,

        "CUST001",

    )

    account_service.open_savings_account(

        "CUST001",

        "SAV001",

        5000,

    )

    for _ in range(20):

        account_service.withdraw(

            "SAV001",

            100,

        )

    assert (

        account_service.get_balance(

            "SAV001"

        )

        == 3000

    )

# ============================================================
# Transfers
# ============================================================

def test_transfer_session(

    customer_service,

    account_service,

):

    create_customer(

        customer_service,

        "CUST001",

    )

    account_service.open_savings_account(

        "CUST001",

        "SAV001",

        5000,

    )

    account_service.open_current_account(

        "CUST001",

        "CUR001",

        1000,

    )

    for _ in range(10):

        account_service.transfer(

            "SAV001",

            "CUR001",

            100,

        )

    assert (

        account_service.get_balance(

            "SAV001"

        )

        == 4000

    )

    assert (

        account_service.get_balance(

            "CUR001"

        )

        == 2000

    )

# ============================================================
# Mixed Activity
# ============================================================

def test_mixed_customer_activity(

    customer_service,

    account_service,

):

    for i in range(10):

        customer_id = f"CUST{i:03}"

        account_number = f"SAV{i:03}"

        create_customer(

            customer_service,

            customer_id,

        )

        account_service.open_savings_account(

            customer_id,

            account_number,

            1000,

        )

    for i in range(10):

        account_service.deposit(

            f"SAV{i:03}",

            200,

        )

        account_service.withdraw(

            f"SAV{i:03}",

            50,

        )

    for i in range(10):

        assert (

            account_service.get_balance(

                f"SAV{i:03}"

            )

            == 1150

        )

# ============================================================
# End-of-Day Verification
# ============================================================

def test_end_of_day_balances(

    customer_service,

    account_service,

):

    create_customer(

        customer_service,

        "CUST001",

    )

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

        250,

    )

    balance = account_service.get_balance(

        "SAV001"

    )

    assert balance == 1250

# ============================================================
# End-of-Day Restart
# ============================================================

def test_end_of_day_restart(

    customer_service,

    account_service,

    reload_customer_repository,

    reload_account_repository,

):

    create_customer(

        customer_service,

        "CUST001",

    )

    account_service.open_savings_account(

        "CUST001",

        "SAV001",

        1000,

    )

    account_service.deposit(

        "SAV001",

        500,

    )

    customer_repo = reload_customer_repository()

    account_repo = reload_account_repository()

    customer = customer_repo.find_by_id(

        "CUST001"

    )

    account = account_repo.find_by_account_number(

        "SAV001"

    )

    assert customer.customer_id == "CUST001"

    assert account.account_number == "SAV001"

# ============================================================
# Complete Banking Day
# ============================================================

def test_complete_banking_day(

    customer_service,

    account_service,

):

    create_customer(

        customer_service,

        "CUST001",

    )

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

        100,

    )

    account_service.deposit(

        "SAV001",

        250,

    )

    account_service.withdraw(

        "SAV001",

        50,

    )

    balance = account_service.get_balance(

        "SAV001"

    )

    assert balance == 1600

