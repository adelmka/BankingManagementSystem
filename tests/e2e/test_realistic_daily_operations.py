"""
End-to-End Tests

Realistic Daily Banking Operations

These tests exercise the real application services and persistence
repositories through realistic banking workflows. No mocks are used.
"""

from datetime import date
from decimal import Decimal

from application.bootstrap import Bootstrap
from repositories.account_repository import AccountRepository
from repositories.customer_repository import CustomerRepository

from models.customer import Customer
from models.current_account import CurrentAccount
from models.savings_account import SavingsAccount
from models.value_objects.address import Address
from models.value_objects.money import Money

from utils.constants import Gender, CustomerStatus


def create_customer(customer_service, customer_number: str):
    """Create and register a complete customer through the service layer."""

    numeric_id = "100000000000" + customer_number[-3:]

    customer = customer_service.register_customer(
        Customer(
            customer_id=customer_number,
            first_name="John",
            last_name="Smith",
            date_of_birth=date(1990, 1, 15),
            gender=Gender.MALE,
            national_id=numeric_id,
            email=f"{customer_number.lower()}@bank.com",
            phone_number="+966501111111",
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


def test_morning_opening(customer_service, account_service):
    """Open 20 customers and savings accounts for the morning opening."""

    for i in range(20):
        customer_id = f"CUST{i:03}"
        account_number = f"SAV{i:03}"

        create_customer(customer_service, customer_id)
        open_savings_account(
            account_service,
            customer_id,
            account_number,
            "1000",
        )

    for i in range(20):
        account = account_service.get_account(f"SAV{i:03}")
        assert account.account_number == f"SAV{i:03}"
        assert account.balance.amount == Decimal("1000.00")


def test_morning_deposits(customer_service, account_service):
    """Process 25 deposits of 100 and verify the resulting balance."""

    create_customer(customer_service, "CUST001")
    open_savings_account(account_service, "CUST001", "SAV001", "1000")

    for _ in range(25):
        account_service.deposit("SAV001", Money("100"))

    assert account_service.balance("SAV001").amount == Decimal("3500.00")


def test_afternoon_withdrawals(customer_service, account_service):
    """Process 20 withdrawals of 100 and verify the resulting balance."""

    create_customer(customer_service, "CUST001")
    open_savings_account(account_service, "CUST001", "SAV001", "5000")

    for _ in range(20):
        account_service.withdraw("SAV001", Money("100"))

    assert account_service.balance("SAV001").amount == Decimal("3000.00")


def test_transfer_session(customer_service, account_service):
    """Transfer 100 ten times from savings to current."""

    create_customer(customer_service, "CUST001")
    open_savings_account(account_service, "CUST001", "SAV001", "5000")
    open_current_account(account_service, "CUST001", "CUR001", "1000")

    for _ in range(10):
        account_service.transfer(
            "SAV001",
            "CUR001",
            Money("100"),
        )

    assert account_service.balance("SAV001").amount == Decimal("4000.00")
    assert account_service.balance("CUR001").amount == Decimal("2000.00")


def test_mixed_customer_activity(customer_service, account_service):
    """Run mixed deposit/withdrawal activity for ten customers."""

    for i in range(10):
        customer_id = f"CUST{i:03}"
        account_number = f"SAV{i:03}"

        create_customer(customer_service, customer_id)
        open_savings_account(
            account_service,
            customer_id,
            account_number,
            "1000",
        )

    for i in range(10):
        account_service.deposit(f"SAV{i:03}", Money("200"))
        account_service.withdraw(f"SAV{i:03}", Money("50"))

    for i in range(10):
        assert (
            account_service.balance(f"SAV{i:03}").amount
            == Decimal("1150.00")
        )


def test_end_of_day_balances(customer_service, account_service):
    """Verify the expected balance after a sequence of daily operations."""

    create_customer(customer_service, "CUST001")
    open_savings_account(account_service, "CUST001", "SAV001", "1000")

    account_service.deposit("SAV001", Money("500"))
    account_service.withdraw("SAV001", Money("250"))

    assert account_service.balance("SAV001").amount == Decimal("1250.00")


def test_end_of_day_restart(
    customer_service,
    account_service,
    test_config,
    monkeypatch,
):
    """Verify that customer and account data survive application restart."""

    create_customer(customer_service, "CUST001")
    open_savings_account(account_service, "CUST001", "SAV001", "1000")
    account_service.deposit("SAV001", Money("500"))

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

    restarted_application = Bootstrap(
        config=test_config
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


def test_complete_banking_day(customer_service, account_service):
    """Execute the complete planned banking-day sequence."""

    create_customer(customer_service, "CUST001")
    open_savings_account(account_service, "CUST001", "SAV001", "1000")

    account_service.deposit("SAV001", Money("500"))
    account_service.withdraw("SAV001", Money("100"))
    account_service.deposit("SAV001", Money("250"))
    account_service.withdraw("SAV001", Money("50"))

    assert account_service.balance("SAV001").amount == Decimal("1600.00")
