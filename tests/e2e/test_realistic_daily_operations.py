"""
End-to-End Tests

Realistic Daily Banking Operations

These tests exercise the real application services and persistence
repositories through realistic banking workflows. No mocks are used.
"""

from datetime import date
from decimal import Decimal

import pytest

from application.bootstrap import Bootstrap
from repositories.account_repository import AccountRepository
from repositories.customer_repository import CustomerRepository
from repositories.transaction_repository import TransactionRepository

from models.customer import Customer
from models.current_account import CurrentAccount
from models.savings_account import SavingsAccount
from models.value_objects.address import Address
from models.value_objects.money import Money

from utils.constants import Gender, CustomerStatus


@pytest.fixture
def e2e_application(test_config, monkeypatch):
    """
    Return an application whose repositories use isolated temporary storage.

    The shared test fixtures intentionally remain unchanged. This fixture
    establishes repository isolation before Bootstrap constructs the real
    application dependency graph, preventing E2E tests from reading or
    modifying production CSV files.
    """

    monkeypatch.setattr(
        CustomerRepository,
        "CSV_FILE",
        test_config.CUSTOMERS_FILE,
    )
    monkeypatch.setattr(
        AccountRepository,
        "CSV_FILE",
        test_config.ACCOUNTS_FILE,
    )
    monkeypatch.setattr(
        TransactionRepository,
        "CSV_FILE",
        test_config.TRANSACTIONS_FILE,
    )

    return Bootstrap(config=test_config).initialize()


@pytest.fixture
def e2e_customer_service(e2e_application):
    """Return the real customer service for an isolated E2E application."""

    return e2e_application._container.customer_service


@pytest.fixture
def e2e_account_service(e2e_application):
    """Return the real account service for an isolated E2E application."""

    return e2e_application._container.account_service


def create_customer(customer_service, customer_number: str):
    """Create and register a complete customer through the service layer."""

    # The application validator accepts numeric national IDs of exactly
    # 10 or 12 digits. The final three digits keep each test customer unique.
    numeric_id = "100000000" + customer_number[-3:]

    # CustomerRepository enforces mobile-number uniqueness. Generate a
    # deterministic unique mobile number for each E2E customer.
    mobile_suffix = int(customer_number[-3:])
    phone_number = f"+966501000{mobile_suffix:03d}"

    customer = customer_service.register_customer(
        Customer(
            customer_id=customer_number,
            first_name="John",
            last_name="Smith",
            date_of_birth=date(1990, 1, 15),
            gender=Gender.MALE,
            national_id=numeric_id,
            email=f"{customer_number.lower()}@bank.com",
            phone_number=phone_number,
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
    )

    return customer


def open_savings_account(
    account_service,
    customer_number: str,
    account_number: str,
    opening_balance: str,
):
    """Open a savings account through the real account service."""

    account = SavingsAccount(
        account_number=account_number,
        customer_id=customer_number,
        opening_balance=Money(opening_balance),
        interest_rate=Decimal("0.025"),
        minimum_balance=Money("0"),
    )

    return account_service.open_account(account)


def open_current_account(
    account_service,
    customer_number: str,
    account_number: str,
    opening_balance: str,
):
    """Open a current account through the real account service."""

    account = CurrentAccount(
        account_number=account_number,
        customer_id=customer_number,
        opening_balance=Money(opening_balance),
        overdraft_limit=Money("0"),
        maintenance_fee=Money("0"),
        overdraft_fee=Money("0"),
    )

    return account_service.open_account(account)


def test_morning_opening(e2e_customer_service, e2e_account_service):
    """Open 20 customers and savings accounts for the morning opening."""

    for i in range(20):
        customer_id = f"CUST{i:03}"
        account_number = f"SAV{i:03}"

        create_customer(e2e_customer_service, customer_id)
        open_savings_account(
            e2e_account_service,
            customer_id,
            account_number,
            "1000",
        )

    for i in range(20):
        account = e2e_account_service.get_account(f"SAV{i:03}")
        assert account.account_number == f"SAV{i:03}"
        assert account.balance.amount == Decimal("1000.00")


def test_morning_deposits(e2e_customer_service, e2e_account_service):
    """Process 25 deposits of 100 and verify the resulting balance."""

    create_customer(e2e_customer_service, "CUST001")
    open_savings_account(e2e_account_service, "CUST001", "SAV001", "1000")

    for _ in range(25):
        e2e_account_service.deposit("SAV001", Money("100"))

    assert e2e_account_service.balance("SAV001").amount == Decimal("3500.00")


def test_afternoon_withdrawals(e2e_customer_service, e2e_account_service):
    """Process 20 withdrawals of 100 and verify the resulting balance."""

    create_customer(e2e_customer_service, "CUST001")
    open_savings_account(e2e_account_service, "CUST001", "SAV001", "5000")

    for _ in range(20):
        e2e_account_service.withdraw("SAV001", Money("100"))

    assert e2e_account_service.balance("SAV001").amount == Decimal("3000.00")


def test_transfer_session(e2e_customer_service, e2e_account_service):
    """Transfer 100 ten times from savings to current."""

    create_customer(e2e_customer_service, "CUST001")
    open_savings_account(e2e_account_service, "CUST001", "SAV001", "5000")
    open_current_account(e2e_account_service, "CUST001", "CUR001", "1000")

    for _ in range(10):
        e2e_account_service.transfer(
            "SAV001",
            "CUR001",
            Money("100"),
        )

    assert e2e_account_service.balance("SAV001").amount == Decimal("4000.00")
    assert e2e_account_service.balance("CUR001").amount == Decimal("2000.00")


def test_mixed_customer_activity(e2e_customer_service, e2e_account_service):
    """Run mixed deposit/withdrawal activity for ten customers."""

    for i in range(10):
        customer_id = f"CUST{i:03}"
        account_number = f"SAV{i:03}"

        create_customer(e2e_customer_service, customer_id)
        open_savings_account(
            e2e_account_service,
            customer_id,
            account_number,
            "1000",
        )

    for i in range(10):
        e2e_account_service.deposit(f"SAV{i:03}", Money("200"))
        e2e_account_service.withdraw(f"SAV{i:03}", Money("50"))

    for i in range(10):
        assert (
            e2e_account_service.balance(f"SAV{i:03}").amount
            == Decimal("1150.00")
        )


def test_end_of_day_balances(e2e_customer_service, e2e_account_service):
    """Verify the expected balance after a sequence of daily operations."""

    create_customer(e2e_customer_service, "CUST001")
    open_savings_account(e2e_account_service, "CUST001", "SAV001", "1000")

    e2e_account_service.deposit("SAV001", Money("500"))
    e2e_account_service.withdraw("SAV001", Money("250"))

    assert e2e_account_service.balance("SAV001").amount == Decimal("1250.00")


def test_end_of_day_restart(
    e2e_customer_service,
    e2e_account_service,
    e2e_application,
):
    """Verify that customer and account data survive application restart."""

    create_customer(e2e_customer_service, "CUST001")
    open_savings_account(e2e_account_service, "CUST001", "SAV001", "1000")
    e2e_account_service.deposit("SAV001", Money("500"))

    restarted_application = Bootstrap(
        config=e2e_application._container.config
    ).initialize()

    customer = restarted_application._container.customer_repository.find_by_customer_number(
        "CUST001"
    )
    account = restarted_application._container.account_repository.find_by_account_number(
        "SAV001"
    )

    assert customer is not None
    assert customer.customer_id == "CUST001"
    assert account is not None
    assert account.account_number == "SAV001"
    assert account.balance.amount == Decimal("1500.00")


def test_complete_banking_day(e2e_customer_service, e2e_account_service):
    """Execute the complete planned banking-day sequence."""

    create_customer(e2e_customer_service, "CUST001")
    open_savings_account(e2e_account_service, "CUST001", "SAV001", "1000")

    e2e_account_service.deposit("SAV001", Money("500"))
    e2e_account_service.withdraw("SAV001", Money("100"))
    e2e_account_service.deposit("SAV001", Money("250"))
    e2e_account_service.withdraw("SAV001", Money("50"))

    assert e2e_account_service.balance("SAV001").amount == Decimal("1600.00")
