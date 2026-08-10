"""Regression tests for internal transfer transaction recording and lookup."""

from decimal import Decimal
from unittest.mock import MagicMock

from models.transaction import Transaction
from models.value_objects.money import Money
from services.account_service import AccountService
from services.transaction_service import TransactionService
from utils.constants import TransactionType


def money(value: str) -> Money:
    return Money(amount=Decimal(value), currency="SAR")


def account(number: str) -> MagicMock:
    value = MagicMock()
    value.account_number = number
    value.customer_id = "CUST001"
    value.is_active = True
    value.balance = money("1000.00")
    value.currency = "SAR"
    return value


def test_transfer_records_single_internal_transfer_transaction():
    account_repository = MagicMock()
    customer_repository = MagicMock()
    transaction_repository = MagicMock()

    source = account("A-SOURCE")
    destination = account("A-DEST")
    accounts = {
        source.account_number: source,
        destination.account_number: destination,
    }
    account_repository.get_or_raise.side_effect = accounts.__getitem__
    account_repository.account_exists.return_value = False

    service = AccountService(
        account_repository=account_repository,
        customer_repository=customer_repository,
        transaction_repository=transaction_repository,
    )

    service.transfer(
        "A-SOURCE",
        "A-DEST",
        money("500.00"),
        description="Testing transfer",
    )

    transaction_repository.add_transaction.assert_called_once()
    transaction = transaction_repository.add_transaction.call_args.args[0]

    assert isinstance(transaction, Transaction)
    assert transaction.transaction_type is TransactionType.INTERNAL_TRANSFER
    assert transaction.amount == money("500.00")
    assert transaction.source_account == "A-SOURCE"
    assert transaction.destination_account == "A-DEST"
    assert transaction.description == "Testing transfer"


def test_account_transaction_history_includes_both_transfer_participants():
    transaction_repository = MagicMock()
    account_repository = MagicMock()

    source = account("A-SOURCE")
    destination = account("A-DEST")
    account_repository.get_or_raise.side_effect = {
        "A-SOURCE": source,
        "A-DEST": destination,
    }.__getitem__

    transaction = Transaction(
        transaction_number="T-001",
        transaction_type=TransactionType.INTERNAL_TRANSFER,
        amount=money("500.00"),
        source_account="A-SOURCE",
        destination_account="A-DEST",
        initiated_by="SYSTEM",
        description="Testing transfer",
    )

    # The repository's iterator must be fresh for each service query.
    # A one-shot iterator would be exhausted after the source-account lookup.
    transaction_repository.__iter__.side_effect = lambda: iter([transaction])

    service = TransactionService(
        transaction_repository=transaction_repository,
        account_repository=account_repository,
    )

    assert service.account_transactions("A-SOURCE") == [transaction]
    assert service.account_transactions("A-DEST") == [transaction]
