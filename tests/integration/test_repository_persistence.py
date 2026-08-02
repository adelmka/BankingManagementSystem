"""
============================================================
Integration Tests

Repository Persistence

Verifies that all repositories correctly persist
their state to CSV files and restore it after
application restart.

No mocks are used.
============================================================
"""

import pytest

# ============================================================
# Customer Repository
# ============================================================

def test_customer_repository_persistence(

    customer_service,

    reload_customer_repository,

):

    customer_service.create_customer(

        customer_id="CUST001",

        first_name="John",

        last_name="Smith",

        email="john@test.com",

        phone="+966501111111",

    )

    repository = reload_customer_repository()

    customer = repository.find_by_id(

        "CUST001"

    )

    assert customer.customer_id == "CUST001"

    assert customer.first_name == "John"

# ============================================================
# Account Repository
# ============================================================

def test_account_repository_persistence(

    customer_service,

    account_service,

    reload_account_repository,

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

    repository = reload_account_repository()

    account = repository.find_by_account_number(

        "SAV001"

    )

    assert account.account_number == "SAV001"

# ============================================================
# Transaction Repository
# ============================================================

def test_transaction_repository_persistence(

    customer_service,

    account_service,

    transaction_service,

    reload_transaction_repository,

):

    customer_service.create_customer(

        customer_id="CUST001",

        first_name="John",

        last_name="Smith",

        email="john@test.com",

        phone="+966501111111",

    )

    account_service.open_savings_account(

        "CUST001",

        "SAV001",

        1000,

    )

    transaction_service.deposit(

        "SAV001",

        250,

    )

    repository = reload_transaction_repository()

    transactions = repository.get_all()

    assert len(transactions) == 1

# ============================================================
# Multiple Customers
# ============================================================

def test_persist_multiple_customers(

    customer_service,

    reload_customer_repository,

):

    for i in range(50):

        customer_service.create_customer(

            customer_id=f"CUST{i:03}",

            first_name="John",

            last_name="Smith",

            email=f"user{i}@test.com",

            phone=f"+9665000{i:04}",

        )

    repository = reload_customer_repository()

    for i in range(50):

        customer = repository.find_by_id(

            f"CUST{i:03}"

        )

        assert customer.customer_id == f"CUST{i:03}"

# ============================================================
# Multiple Accounts
# ============================================================

def test_persist_multiple_accounts(

    customer_service,

    account_service,

    reload_account_repository,

):

    customer_service.create_customer(

        customer_id="CUST001",

        first_name="John",

        last_name="Smith",

        email="john@test.com",

        phone="+966501111111",

    )

    for i in range(30):

        account_service.open_savings_account(

            "CUST001",

            f"SAV{i:03}",

            100,

        )

    repository = reload_account_repository()

    for i in range(30):

        account = repository.find_by_account_number(

            f"SAV{i:03}"

        )

        assert account.account_number == f"SAV{i:03}"

# ============================================================
# Full Restart
# ============================================================

def test_full_system_restart(

    customer_service,

    account_service,

    transaction_service,

    reload_customer_repository,

    reload_account_repository,

    reload_transaction_repository,

):

    customer_service.create_customer(

        customer_id="CUST001",

        first_name="John",

        last_name="Smith",

        email="john@test.com",

        phone="+966501111111",

    )

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

# ============================================================
# Repeated Restart
# ============================================================

def test_repeated_repository_reload(

    customer_service,

    reload_customer_repository,

):

    customer_service.create_customer(

        customer_id="CUST001",

        first_name="John",

        last_name="Smith",

        email="john@test.com",

        phone="+966501111111",

    )

    for _ in range(10):

        repo = reload_customer_repository()

        customer = repo.find_by_id(

            "CUST001"

        )

        assert customer.customer_id == "CUST001"

# ============================================================
# Repository Consistency
# ============================================================

def test_repository_consistency(

    customer_service,

    account_service,

    reload_customer_repository,

    reload_account_repository,

):

    customer_service.create_customer(

        customer_id="CUST001",

        first_name="John",

        last_name="Smith",

        email="john@test.com",

        phone="+966501111111",

    )

    account_service.open_current_account(

        "CUST001",

        "CUR001",

        500,

    )

    customer_repo = reload_customer_repository()

    account_repo = reload_account_repository()

    customer = customer_repo.find_by_id(

        "CUST001"

    )

    account = account_repo.find_by_account_number(

        "CUR001"

    )

    assert customer.customer_id == account.customer_id

