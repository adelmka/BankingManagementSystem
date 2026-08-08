"""
============================================================
End-to-End Tests

Complete Banking Lifecycle

These tests execute realistic banking workflows using
the real application stack.

No mocks are used.
============================================================
"""

from datetime import date
from decimal import Decimal

import pytest

from models.current_account import CurrentAccount
from models.customer import Customer
from models.savings_account import SavingsAccount
from models.transaction import Transaction
from models.value_objects.address import Address
from models.value_objects.money import Money
from repositories.account_repository import AccountRepository
from repositories.customer_repository import CustomerRepository
from repositories.transaction_repository import TransactionRepository
from services.account_service import AccountService
from services.customer_service import CustomerService
from services.transaction_service import TransactionService
from utils.constants import CustomerStatus, Gender, TransactionType


# ============================================================
# Test-data and isolation helpers
# ============================================================


@pytest.fixture
def e2e_repositories(tmp_path, monkeypatch):
    """Build all repositories against private CSV files for this test."""

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
    """Customer service using this test's private repository."""

    return CustomerService(e2e_repositories["customer"])


@pytest.fixture
def account_service(e2e_repositories):
    """Account service using this test's private repositories."""

    return AccountService(
        account_repository=e2e_repositories["account"],
        customer_repository=e2e_repositories["customer"],
        transaction_repository=e2e_repositories["transaction"],
    )


@pytest.fixture
def transaction_service(e2e_repositories):
    """Transaction service using this test's private repositories."""

    return TransactionService(
        transaction_repository=e2e_repositories["transaction"],
        account_repository=e2e_repositories["account"],
    )


def make_customer(
    customer_id: str = "E2ELC001",
    national_id: str = "710000000001",
    email: str = "e2e-lifecycle-001@bank.com",
    phone_number: str = "+966502000001",
) -> Customer:
    """Build a complete customer using the current domain model."""

    return Customer(
        customer_id=customer_id,
        first_name="John",
        last_name="Smith",
        date_of_birth=date(1990, 1, 15),
        gender=Gender.MALE,
        national_id=national_id,
        email=email,
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


def register_customer(customer_service, **kwargs) -> Customer:
    """Register a complete customer through the current service API."""

    return customer_service.register_customer(make_customer(**kwargs))


def open_savings_account(
    account_service,
    customer_id: str,
    account_number: str,
    opening_balance: str,
):
    """Open a savings account through the current account-service API."""

    account = SavingsAccount(
        account_number=account_number,
        customer_id=customer_id,
        opening_balance=Money(opening_balance),
        interest_rate=Decimal("0.025"),
        minimum_balance=Money("0"),
    )

    return account_service.open_account(account)


def open_current_account(
    account_service,
    customer_id: str,
    account_number: str,
    opening_balance: str,
):
    """Open a current account through the current account-service API."""

    account = CurrentAccount(
        account_number=account_number,
        customer_id=customer_id,
        opening_balance=Money(opening_balance),
        overdraft_limit=Money("1000"),
        maintenance_fee=Money("10"),
        overdraft_fee=Money("25"),
    )

    return account_service.open_account(account)


# ============================================================
# Scenario 1 — Complete Customer Lifecycle
# ============================================================


def test_complete_customer_lifecycle(customer_service):
    """Register, update, archive, and verify a customer."""

    register_customer(customer_service)

    customer = customer_service.find_customer("E2ELC001")
    assert customer is not None
    assert customer.customer_id == "E2ELC001"

    customer.first_name = "Johnny"
    customer.email = "johnny@bank.com"
    customer_service.update_customer(customer)

    customer = customer_service.find_customer("E2ELC001")
    assert customer is not None
    assert customer.first_name == "Johnny"
    assert customer.email == "johnny@bank.com"

    assert customer_service.archive_customer("E2ELC001") is True
    assert customer_service.find_customer("E2ELC001") is None


# ============================================================
# Scenario 2 — Savings Account Lifecycle
# ============================================================


def test_complete_savings_account_lifecycle(
    customer_service,
    account_service,
    e2e_repositories,
):
    """Open, fund, transact on, and close a savings account."""

    register_customer(customer_service)
    open_savings_account(
        account_service,
        "E2ELC001",
        "E2ESAV001",
        "1000",
    )

    account_service.deposit("E2ESAV001", Money("500"))
    account_service.withdraw("E2ESAV001", Money("200"))

    account = account_service.get_account("E2ESAV001")
    assert account.balance.amount == Decimal("1300.00")

    # AccountService does not currently expose close_account().
    # Use the domain lifecycle operation and persist through the
    # repository, without changing production architecture.
    account_service.withdraw("E2ESAV001", Money("1300"))
    account = account_service.get_account("E2ESAV001")
    account.close_account()
    e2e_repositories["account"].save_account(account)

    closed_account = account_service.get_account("E2ESAV001")
    assert closed_account.is_closed
    assert closed_account.closed_date is not None


# ============================================================
# Scenario 3 — Transfer Between Accounts
# ============================================================


def test_complete_transfer_workflow(
    customer_service,
    account_service,
):
    """Transfer funds between two accounts owned by one customer."""

    register_customer(customer_service)
    open_savings_account(
        account_service,
        "E2ELC001",
        "E2ESAV001",
        "1000",
    )
    open_current_account(
        account_service,
        "E2ELC001",
        "E2ECUR001",
        "500",
    )

    account_service.transfer(
        "E2ESAV001",
        "E2ECUR001",
        Money("300"),
    )

    assert (
        account_service.get_account("E2ESAV001").balance.amount
        == Decimal("700.00")
    )
    assert (
        account_service.get_account("E2ECUR001").balance.amount
        == Decimal("800.00")
    )


# ============================================================
# Scenario 4 — Restart Application
# ============================================================


def test_application_restart(
    customer_service,
    account_service,
    transaction_service,
):
    """Verify customers, accounts, and explicitly recorded transactions survive a reload."""

    register_customer(customer_service)
    open_savings_account(
        account_service,
        "E2ELC001",
        "E2ESAV001",
        "1000",
    )

    account_service.deposit("E2ESAV001", Money("500"))

    # AccountService currently changes balances but deliberately does
    # not persist Transaction entities. Record one explicitly through
    # the supported TransactionService API so this test can verify the
    # transaction persistence/reload contract without changing production code.
    transaction = Transaction(
        transaction_number="E2ETXN001",
        transaction_type=TransactionType.DEPOSIT,
        amount=Money("500"),
        source_account=None,
        destination_account="E2ESAV001",
        initiated_by="E2E-TEST",
        description="E2E restart transaction",
    )
    transaction_service.record_transaction(transaction)

    customer_repo = CustomerRepository()
    account_repo = AccountRepository()
    transaction_repo = TransactionRepository()

    assert customer_repo.find_by_customer_number("E2ELC001") is not None
    assert account_repo.find_by_account_number("E2ESAV001") is not None
    assert len(list(transaction_repo)) == 1

    restarted_transaction_service = TransactionService(
        transaction_repository=transaction_repo,
        account_repository=account_repo,
    )
    assert len(restarted_transaction_service.all_transactions()) == 1
    assert restarted_transaction_service.get_transaction("E2ETXN001").amount.amount == Decimal("500.00")


# ============================================================
# Scenario 5 — Customer Owns Multiple Accounts
# ============================================================


def test_customer_multiple_accounts(
    customer_service,
    account_service,
):
    """Verify that one customer can own savings and current accounts."""

    register_customer(customer_service)
    open_savings_account(
        account_service,
        "E2ELC001",
        "E2ESAV001",
        "1000",
    )
    open_current_account(
        account_service,
        "E2ELC001",
        "E2ECUR001",
        "500",
    )

    savings = account_service.get_account("E2ESAV001")
    current = account_service.get_account("E2ECUR001")

    assert savings.customer_id == "E2ELC001"
    assert current.customer_id == "E2ELC001"
    assert len(account_service.customer_accounts("E2ELC001")) == 2


# ============================================================
# Scenario 6 — Long Banking Session
# ============================================================


def test_long_banking_session(
    customer_service,
    account_service,
):
    """Execute repeated deposits and withdrawals in one session."""

    register_customer(customer_service)
    open_savings_account(
        account_service,
        "E2ELC001",
        "E2ESAV001",
        "1000",
    )

    for _ in range(20):
        account_service.deposit("E2ESAV001", Money("100"))
        account_service.withdraw("E2ESAV001", Money("50"))

    account = account_service.get_account("E2ESAV001")
    assert account.balance.amount == Decimal("2000.00")

    # Transaction entities are not currently created by AccountService;
    # transaction_count therefore measures explicitly associated domain
    # transaction IDs, not the number of balance operations.
    assert account.transaction_count == 0


# ============================================================
# Scenario 7 — Full Bank Lifecycle
# ============================================================


def test_complete_bank_lifecycle(
    customer_service,
    account_service,
    e2e_repositories,
):
    """Execute a complete customer-to-account banking lifecycle."""

    register_customer(customer_service)
    open_savings_account(
        account_service,
        "E2ELC001",
        "E2ESAV001",
        "1000",
    )

    account_service.deposit("E2ESAV001", Money("1000"))
    account_service.withdraw("E2ESAV001", Money("500"))

    # Close the account through the current domain API after bringing
    # the balance to zero, then persist the updated account.
    account_service.withdraw("E2ESAV001", Money("1500"))
    account = account_service.get_account("E2ESAV001")
    account.close_account()
    e2e_repositories["account"].save_account(account)

    assert account_service.get_account("E2ESAV001").is_closed
    assert customer_service.archive_customer("E2ELC001") is True
    assert customer_service.find_customer("E2ELC001") is None
