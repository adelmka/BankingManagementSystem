"""
============================================================
Integration Test Fixtures

These fixtures provide real repositories and services
backed by temporary CSV files.

No mocks are used.

Each test receives a completely isolated banking system.
============================================================
"""

from pathlib import Path

import pytest

from repositories.customer_repository import CustomerRepository
from repositories.account_repository import AccountRepository
from repositories.transaction_repository import TransactionRepository

from services.customer_service import CustomerService
from services.account_service import AccountService
from services.transaction_service import TransactionService

# ============================================================
# Temporary Data Directory
# ============================================================

@pytest.fixture
def data_directory(tmp_path):

    """
    Creates a temporary data directory for each test.

    pytest automatically removes it afterwards.
    """

    data = tmp_path / "data"

    data.mkdir()

    return data

# ============================================================
# CSV Files
# ============================================================

@pytest.fixture
def customer_csv(data_directory):

    return data_directory / "customers.csv"


@pytest.fixture
def account_csv(data_directory):

    return data_directory / "accounts.csv"


@pytest.fixture
def transaction_csv(data_directory):

    return data_directory / "transactions.csv"

# ============================================================
# Customer Repository
# ============================================================

@pytest.fixture
def customer_repository(customer_csv):

    repository = CustomerRepository(

        file_path=customer_csv

    )

    repository.load()

    return repository

# ============================================================
# Account Repository
# ============================================================

@pytest.fixture
def account_repository(account_csv):

    repository = AccountRepository(

        file_path=account_csv

    )

    repository.load()

    return repository

# ============================================================
# Transaction Repository
# ============================================================

@pytest.fixture
def transaction_repository(transaction_csv):

    repository = TransactionRepository(

        file_path=transaction_csv

    )

    repository.load()

    return repository

# ============================================================
# Customer Service
# ============================================================

@pytest.fixture
def customer_service(

    customer_repository,

):

    return CustomerService(

        customer_repository,

    )

# ============================================================
# Account Service
# ============================================================

@pytest.fixture
def account_service(

    account_repository,

    customer_repository,

    transaction_repository,

):

    return AccountService(

        account_repository,

        customer_repository,

        transaction_repository,

    )

# ============================================================
# Transaction Service
# ============================================================

@pytest.fixture
def transaction_service(

    transaction_repository,

    account_repository,

):

    return TransactionService(

        transaction_repository,

        account_repository,

    )

# ============================================================
# Banking System
# ============================================================

@pytest.fixture
def banking_system(

    customer_service,

    account_service,

    transaction_service,

):

    return {

        "customer_service": customer_service,

        "account_service": account_service,

        "transaction_service": transaction_service,

    }

# ============================================================
# Sample Customer
# ============================================================

@pytest.fixture
def sample_customer(

    customer_service,

):

    return customer_service.create_customer(

        customer_id="CUST001",

        first_name="John",

        last_name="Smith",

        email="john@test.com",

        phone="+966501111111",

    )

# ============================================================
# Sample Savings Account
# ============================================================

@pytest.fixture
def sample_account(

    account_service,

    sample_customer,

):

    return account_service.open_savings_account(

        customer_id="CUST001",

        account_number="SAV001",

        opening_balance=1000,

    )

# ============================================================
# Reload Repositories
# ============================================================

@pytest.fixture
def reload_customer_repository(customer_csv):

    def factory():

        repo = CustomerRepository(

            file_path=customer_csv

        )

        repo.load()

        return repo

    return factory

@pytest.fixture
def reload_account_repository(account_csv):

    def factory():

        repo = AccountRepository(

            file_path=account_csv

        )

        repo.load()

        return repo

    return factory

@pytest.fixture
def reload_transaction_repository(transaction_csv):

    def factory():

        repo = TransactionRepository(

            file_path=transaction_csv

        )

        repo.load()

        return repo

    return factory

