"""Integration tests for TransactionService and transaction persistence."""

from decimal import Decimal

import pytest

from exceptions.banking_exceptions import (
    EntityNotFoundError,
    ValidationError,
)
from models.savings_account import SavingsAccount
from models.transaction import Transaction
from models.value_objects.money import Money
from utils.constants import TransactionType
from tests.integration.conftest import make_customer


def setup_account(customer_service, account_service):
    customer_service.register_customer(make_customer())
    account_service.open_account(
        SavingsAccount(
            account_number="SAV001",
            customer_id="CUST001",
            opening_balance=Money("1000"),
            interest_rate=Decimal("0.025"),
            minimum_balance=Money("0"),
        )
    )


def make_transaction(number="TXN001", amount="250"):
    return Transaction(
        transaction_number=number,
        transaction_type=TransactionType.DEPOSIT,
        amount=Money(amount),
        source_account=None,
        destination_account="SAV001",
        initiated_by="integration-test",
        description="Integration test deposit",
    )


def test_record_transaction(customer_service, account_service, transaction_service):
    setup_account(customer_service, account_service)
    transaction = transaction_service.record_transaction(make_transaction())
    assert transaction.transaction_number == "TXN001"
    assert transaction.is_completed()


def test_get_transaction(customer_service, account_service, transaction_service):
    setup_account(customer_service, account_service)
    transaction_service.record_transaction(make_transaction())
    transaction = transaction_service.get_transaction("TXN001")
    assert transaction.amount.amount == Decimal("250.00")


def test_all_transactions(customer_service, account_service, transaction_service):
    setup_account(customer_service, account_service)
    transaction_service.record_transaction(make_transaction("TXN001", "100"))
    transaction_service.record_transaction(make_transaction("TXN002", "200"))
    assert transaction_service.transaction_count() == 2
    assert len(transaction_service.all_transactions()) == 2


def test_account_transactions(customer_service, account_service, transaction_service):
    setup_account(customer_service, account_service)
    transaction_service.record_transaction(make_transaction())
    transactions = transaction_service.account_transactions("SAV001")
    assert len(transactions) == 1
    assert transactions[0].transaction_number == "TXN001"


def test_customer_transactions(customer_service, account_service, transaction_service):
    setup_account(customer_service, account_service)
    transaction_service.record_transaction(make_transaction())
    transactions = transaction_service.customer_transactions("CUST001")
    assert len(transactions) == 1


def test_transaction_statistics(customer_service, account_service, transaction_service):
    setup_account(customer_service, account_service)
    transaction_service.record_transaction(make_transaction("TXN001", "100"))
    transaction_service.record_transaction(make_transaction("TXN002", "300"))
    statistics = transaction_service.account_statistics("SAV001")
    assert statistics["transaction_count"] == 2
    assert statistics["total_credits"].amount == Decimal("400.00")


def test_transaction_persistence(
    customer_service,
    account_service,
    transaction_service,
    reload_transaction_repository,
):
    setup_account(customer_service, account_service)
    transaction_service.record_transaction(make_transaction())
    repository = reload_transaction_repository()
    transactions = list(repository)
    assert len(transactions) == 1
    assert transactions[0].transaction_number == "TXN001"


def test_transaction_restart(
    customer_service,
    account_service,
    transaction_service,
    reload_transaction_repository,
):
    setup_account(customer_service, account_service)
    transaction_service.record_transaction(make_transaction())
    restarted = reload_transaction_repository()
    transaction_service.refresh()
    assert restarted.transaction_exists("TXN001")


def test_unknown_account(transaction_service):
    with pytest.raises(EntityNotFoundError):
        transaction_service.account_transactions("UNKNOWN")


def test_invalid_transaction(transaction_service):
    invalid = make_transaction()
    invalid._amount = Money("-100")
    with pytest.raises(ValidationError):
        transaction_service.record_transaction(invalid)
