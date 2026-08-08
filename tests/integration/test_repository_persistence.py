"""Integration tests for CSV repository persistence and reload behavior."""

from decimal import Decimal

from models.savings_account import SavingsAccount
from models.transaction import Transaction
from models.value_objects.money import Money
from utils.constants import TransactionType
from tests.integration.conftest import make_customer


def register_customer(customer_service, index=1):
    return customer_service.register_customer(
        make_customer(f"CUST{index:03}", index)
    )


def open_account(account_service, index=1, balance="1000"):
    return account_service.open_account(
        SavingsAccount(
            account_number=f"SAV{index:03}",
            customer_id=f"CUST{index:03}",
            opening_balance=Money(balance),
            interest_rate=Decimal("0.025"),
            minimum_balance=Money("0"),
        )
    )


def make_transaction(number, account_number):
    return Transaction(
        transaction_number=number,
        transaction_type=TransactionType.DEPOSIT,
        amount=Money("250"),
        source_account=None,
        destination_account=account_number,
        initiated_by="integration-test",
        description="Persistence test",
    )


def test_customer_repository_persistence(customer_service, reload_customer_repository):
    register_customer(customer_service)
    repository = reload_customer_repository()
    customer = repository.find_by_customer_number("CUST001")
    assert customer is not None
    assert customer.customer_id == "CUST001"
    assert customer.first_name == "John"


def test_account_repository_persistence(
    customer_service,
    account_service,
    reload_account_repository,
):
    register_customer(customer_service)
    open_account(account_service)
    repository = reload_account_repository()
    account = repository.find_by_account_number("SAV001")
    assert account is not None
    assert account.account_number == "SAV001"


def test_transaction_repository_persistence(
    customer_service,
    account_service,
    transaction_service,
    reload_transaction_repository,
):
    register_customer(customer_service)
    open_account(account_service)
    transaction_service.record_transaction(make_transaction("TXN001", "SAV001"))
    repository = reload_transaction_repository()
    transactions = list(repository)
    assert len(transactions) == 1
    assert transactions[0].transaction_number == "TXN001"


def test_persist_multiple_customers(customer_service, reload_customer_repository):
    for i in range(1, 51):
        register_customer(customer_service, i)
    repository = reload_customer_repository()
    assert len(list(repository)) == 50
    for i in range(1, 51):
        assert repository.find_by_customer_number(f"CUST{i:03}") is not None


def test_persist_multiple_accounts(
    customer_service,
    account_service,
    reload_account_repository,
):
    register_customer(customer_service)
    for i in range(1, 31):
        open_account(account_service, i)
        # Account ownership requires the matching customer, so register it first.
