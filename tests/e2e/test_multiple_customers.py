"""
============================================================
End-to-End Tests

Multiple Customers

These tests simulate a small bank with many
customers and accounts operating simultaneously.

No mocks are used.
============================================================
"""

from datetime import date
from decimal import Decimal

import pytest

from models.customer import Customer
from models.savings_account import SavingsAccount
from models.value_objects.address import Address
from models.value_objects.money import Money
from repositories.account_repository import AccountRepository
from repositories.customer_repository import CustomerRepository
from repositories.transaction_repository import TransactionRepository
from services.account_service import AccountService
from services.customer_service import CustomerService
from utils.constants import CustomerStatus, Gender


# ============================================================
# Test-data and isolation helpers
# ============================================================


@pytest.fixture
def e2e_repositories(tmp_path, monkeypatch):
    """Build repositories against private CSV files for this test."""

    data_dir = tmp_path / "data"
    data_dir.mkdir(parents=True, exist_ok=True)

    customer_file = data_dir / "customers.csv"
    account_file = data_dir / "accounts.csv"
    transaction_file = data_dir / "transactions.csv"

    monkeypatch.setattr(CustomerRepository, "CSV_FILE", customer_file)
    monkeypatch.setattr(AccountRepository, "CSV_FILE", account_file)
    monkeypatch.setattr(TransactionRepository, "CSV_FILE", transaction_file)

    return {
        "customer": CustomerRepository(),
        "account": AccountRepository(),
        "transaction": TransactionRepository(),
    }


@pytest.fixture
def customer_service(e2e_repositories):
    """Customer service using only this test's private repository."""

    return CustomerService(e2e_repositories["customer"])


@pytest.fixture
def account_service(e2e_repositories):
    """Account service using this test's private repositories."""

    return AccountService(
        account_repository=e2e_repositories["account"],
        customer_repository=e2e_repositories["customer"],
        transaction_repository=e2e_repositories["transaction"],
    )


def customer_number(index: int) -> str:
    """Return a test-specific customer number."""

    return f"E2EMC{index:03}"


def account_number(index: int) -> str:
    """Return a test-specific account number."""

    return f"E2ESA{index:03}"


def national_id(index: int) -> str:
    """Return a unique 12-digit national ID for test data."""

    return f"700000000{index:03}"


def make_customer(index: int) -> Customer:
    """Build a complete, unique customer using the current domain model."""

    return Customer(
        customer_id=customer_number(index),
        first_name=f"First{index}",
        last_name=f"Last{index}",
        date_of_birth=date(1990, 1, 15),
        gender=Gender.MALE,
        national_id=national_id(index),
        email=f"e2e-multiple-{index}@bank.com",
        phone_number=f"+966501000{index:03}",
        address=Address(
            address_line_1="123 Main Street",
            address_line_2="",
            city="Riyadh",
            state_or_province="Riyadh",
            postal_code="12345",
            country="Saudi Arabia",
        ),
        middle_name="",
        customer_status=CustomerStatus.ACTIVE,
        registration_date=date.today(),
        kyc_completed=True,
    )


def register_customer(customer_service, index: int) -> Customer:
    """Register a complete customer through the current service API."""

    return customer_service.register_customer(make_customer(index))


def open_savings_account(
    account_service,
    index: int,
    opening_balance: str,
):
    """Open a savings account through the current account-service API."""

    account = SavingsAccount(
        account_number=account_number(index),
        customer_id=customer_number(index),
        opening_balance=Money(opening_balance),
        interest_rate=Decimal("0.025"),
        minimum_balance=Money("0"),
    )

    return account_service.open_account(account)


# ============================================================
# Scenario 1 — Multiple Customers
# ============================================================


def test_create_multiple_customers(customer_service):
    """Create and retrieve 100 customers through the real service layer."""

    for i in range(100):
        register_customer(customer_service, i)

    for i in range(100):
        customer = customer_service.find_customer(customer_number(i))
        assert customer is not None
        assert customer.customer_id == customer_number(i)


# ============================================================
# Scenario 2 — Multiple Accounts
# ============================================================


def test_multiple_accounts(customer_service, account_service):
    """Create 20 customers and one savings account for each."""

    for i in range(20):
        register_customer(customer_service, i)
        open_savings_account(account_service, i, "1000")

    for i in range(20):
        account = account_service.get_account(account_number(i))
        assert account.account_number == account_number(i)
        assert account.customer_id == customer_number(i)


# ============================================================
# Scenario 3 — Deposit To Every Account
# ============================================================


def test_bulk_deposit(customer_service, account_service):
    """Deposit 500 into each of ten savings accounts."""

    for i in range(10):
        register_customer(customer_service, i)
        open_savings_account(account_service, i, "1000")
        account_service.deposit(account_number(i), Money("500"))

    for i in range(10):
        account = account_service.get_account(account_number(i))
        assert account.balance.amount == Decimal("1500.00")


# ============================================================
# Scenario 4 — Withdraw From Every Account
# ============================================================


def test_bulk_withdrawal(customer_service, account_service):
    """Withdraw 250 from each of ten savings accounts."""

    for i in range(10):
        register_customer(customer_service, i)
        open_savings_account(account_service, i, "1000")
        account_service.withdraw(account_number(i), Money("250"))

    for i in range(10):
        account = account_service.get_account(account_number(i))
        assert account.balance.amount == Decimal("750.00")


# ============================================================
# Scenario 5 — Mixed Operations
# ============================================================


def test_mixed_operations(customer_service, account_service):
    """Deposit and withdraw across 15 customer accounts."""

    for i in range(15):
        register_customer(customer_service, i)
        open_savings_account(account_service, i, "1000")

    for i in range(15):
        account_service.deposit(account_number(i), Money("100"))
        account_service.withdraw(account_number(i), Money("50"))

    for i in range(15):
        account = account_service.get_account(account_number(i))
        assert account.balance.amount == Decimal("1050.00")


# ============================================================
# Scenario 6 — Repository Restart
# ============================================================


def test_restart_multiple_customers(customer_service, e2e_repositories):
    """Verify that 25 customers can be reloaded from persistent storage."""

    for i in range(25):
        register_customer(customer_service, i)

    storage_file = e2e_repositories["customer"].CSV_FILE
    restarted_repository = CustomerRepository()
    assert restarted_repository.CSV_FILE == storage_file

    for i in range(25):
        customer = restarted_repository.find_by_customer_number(
            customer_number(i)
        )
        assert customer is not None
        assert customer.customer_id == customer_number(i)


# ============================================================
# Scenario 7 — Large Dataset
# ============================================================


def test_large_bank_dataset(customer_service, account_service):
    """Create 100 customers and 100 associated savings accounts."""

    for i in range(100):
        register_customer(customer_service, i)
        open_savings_account(account_service, i, "100")

    for i in range(100):
        account = account_service.get_account(account_number(i))
        assert account.customer_id == customer_number(i)
