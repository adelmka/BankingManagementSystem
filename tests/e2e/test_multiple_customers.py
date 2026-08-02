"""
============================================================
End-to-End Tests

Multiple Customers

These tests simulate a small bank with many
customers and accounts operating simultaneously.

No mocks are used.
============================================================
"""

import pytest

# Scenario 1 — Multiple Customers

# ============================================================
# Multiple Customers
# ============================================================

def test_create_multiple_customers(

    customer_service,

):

    for i in range(100):

        customer_service.create_customer(

            customer_id=f"CUST{i:03}",

            first_name=f"First{i}",

            last_name=f"Last{i}",

            email=f"user{i}@bank.com",

            phone=f"+966500{i:05}",

        )

    for i in range(100):

        customer = customer_service.find_customer(

            f"CUST{i:03}"

        )

        assert customer.customer_id == f"CUST{i:03}"

# Scenario 2 — Multiple Accounts

# ============================================================
# Multiple Accounts
# ============================================================

def test_multiple_accounts(

    customer_service,

    account_service,

):

    for i in range(20):

        customer_service.create_customer(

            customer_id=f"CUST{i:03}",

            first_name="John",

            last_name="Smith",

            email=f"user{i}@bank.com",

            phone=f"+966500{i:05}",

        )

        account_service.open_savings_account(

            customer_id=f"CUST{i:03}",

            account_number=f"SAV{i:03}",

            opening_balance=1000,

        )

    for i in range(20):

        account = account_service.find_account(

            f"SAV{i:03}"

        )

        assert account.account_number == f"SAV{i:03}"

# Scenario 3 — Deposit To Every Account

# ============================================================
# Bulk Deposits
# ============================================================

def test_bulk_deposit(

    customer_service,

    account_service,

):

    for i in range(10):

        customer_service.create_customer(

            customer_id=f"CUST{i:03}",

            first_name="John",

            last_name="Smith",

            email=f"user{i}@bank.com",

            phone=f"+966500{i:05}",

        )

        account_service.open_savings_account(

            f"CUST{i:03}",

            f"SAV{i:03}",

            1000,

        )

        account_service.deposit(

            f"SAV{i:03}",

            500,

        )

    for i in range(10):

        assert (

            account_service.get_balance(

                f"SAV{i:03}"

            )

            == 1500

        )

# Scenario 4 — Withdraw From Every Account

# ============================================================
# Bulk Withdrawals
# ============================================================

def test_bulk_withdrawal(

    customer_service,

    account_service,

):

    for i in range(10):

        customer_service.create_customer(

            customer_id=f"CUST{i:03}",

            first_name="John",

            last_name="Smith",

            email=f"user{i}@bank.com",

            phone=f"+966500{i:05}",

        )

        account_service.open_savings_account(

            f"CUST{i:03}",

            f"SAV{i:03}",

            1000,

        )

        account_service.withdraw(

            f"SAV{i:03}",

            250,

        )

    for i in range(10):

        assert (

            account_service.get_balance(

                f"SAV{i:03}"

            )

            == 750

        )

# Scenario 5 — Mixed Operations

# ============================================================
# Mixed Banking Operations
# ============================================================

def test_mixed_operations(

    customer_service,

    account_service,

):

    for i in range(15):

        customer_service.create_customer(

            customer_id=f"CUST{i:03}",

            first_name="John",

            last_name="Smith",

            email=f"user{i}@bank.com",

            phone=f"+966500{i:05}",

        )

        account_service.open_savings_account(

            f"CUST{i:03}",

            f"SAV{i:03}",

            1000,

        )

    for i in range(15):

        account_service.deposit(

            f"SAV{i:03}",

            100,

        )

        account_service.withdraw(

            f"SAV{i:03}",

            50,

        )

    for i in range(15):

        assert (

            account_service.get_balance(

                f"SAV{i:03}"

            )

            == 1050

        )

# Scenario 6 — Repository Restart

# ============================================================
# Restart Bank
# ============================================================

def test_restart_multiple_customers(

    customer_service,

    reload_customer_repository,

):

    for i in range(25):

        customer_service.create_customer(

            customer_id=f"CUST{i:03}",

            first_name="John",

            last_name="Smith",

            email=f"user{i}@bank.com",

            phone=f"+966500{i:05}",

        )

    repository = reload_customer_repository()

    for i in range(25):

        customer = repository.find_by_id(

            f"CUST{i:03}"

        )

        assert customer.customer_id == f"CUST{i:03}"

# Scenario 7 — Large Dataset

# ============================================================
# Large Dataset
# ============================================================

def test_large_bank_dataset(

    customer_service,

    account_service,

):

    for i in range(100):

        customer_service.create_customer(

            customer_id=f"CUST{i:03}",

            first_name="John",

            last_name="Smith",

            email=f"user{i}@bank.com",

            phone=f"+966500{i:05}",

        )

        account_service.open_savings_account(

            f"CUST{i:03}",

            f"SAV{i:03}",

            100,

        )

    for i in range(100):

        account = account_service.find_account(

            f"SAV{i:03}"

        )

        assert account.customer_id == f"CUST{i:03}"
