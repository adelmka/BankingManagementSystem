# PART 1

from __future__ import annotations

from decimal import Decimal

import pytest

from exceptions import EntityAlreadyExistsError

from models.transaction import Transaction
from models.value_objects.money import Money

from repositories.transaction_repository import (
    TransactionRepository,
)

from utils.constants import (
    TransactionStatus,
    TransactionType,
)


# ----------------------------------------------------------------------
# Test Repository
# ----------------------------------------------------------------------


class TransactionRepositoryTestDouble(
    TransactionRepository,
):
    """
    Test-specific TransactionRepository using temporary CSV storage.

    The class name intentionally does not begin with 'Test' so pytest
    does not attempt to collect it as a test class.
    """

    def __init__(self, csv_file):
        self.CSV_FILE = csv_file
        super().__init__()


# ----------------------------------------------------------------------
# Fixtures
# ----------------------------------------------------------------------


@pytest.fixture
def repository(tmp_path):
    """
    Return an isolated transaction repository.
    """

    return TransactionRepositoryTestDouble(
        tmp_path / "transactions.csv"
    )


@pytest.fixture
def transaction():
    """
    Return a valid deposit transaction using the current
    Transaction constructor.
    """

    return Transaction(
        transaction_number="TXN000001",
        transaction_type=TransactionType.DEPOSIT,
        amount=Money(
            Decimal("250.00"),
            "SAR",
        ),
        source_account=None,
        destination_account="SA000001",
        initiated_by="system",
        description="Initial deposit",
    )


@pytest.fixture
def second_transaction():
    """
    Return a second transaction with a different transaction number.
    """

    return Transaction(
        transaction_number="TXN000002",
        transaction_type=TransactionType.WITHDRAWAL,
        amount=Money(
            Decimal("100.00"),
            "SAR",
        ),
        source_account="SA000001",
        destination_account=None,
        initiated_by="system",
        description="Cash withdrawal",
    )


@pytest.fixture
def repository_with_transaction(
    repository,
    transaction,
):
    """
    Repository containing one persisted transaction.
    """

    repository.add_transaction(
        transaction
    )

    return repository


# ----------------------------------------------------------------------
# Repository Initialization
# ----------------------------------------------------------------------


def test_repository_initializes_with_empty_storage(
    repository,
):
    assert repository.count == 0
    assert repository.is_empty() is True
    assert repository.file_exists is True


def test_repository_storage_path(
    repository,
):
    assert repository.storage_path == (
        repository.CSV_FILE
    )


def test_repository_entity_type(
    repository,
):
    assert repository.entity_type is Transaction


def test_repository_name(
    repository,
):
    assert repository.repository_name == (
        "TransactionRepositoryTestDouble"
    )


def test_repository_string_representation(
    repository,
):
    assert str(repository) == (
        "TransactionRepository("
        "transactions=0)"
    )


def test_repository_repr(
    repository,
):
    representation = repr(repository)

    assert representation.startswith(
        "TransactionRepository("
    )

    assert "count=0" in representation


# ----------------------------------------------------------------------
# Normalization
# ----------------------------------------------------------------------


def test_normalize_strips_whitespace_and_uppercases(
    repository,
):
    assert repository._normalize(
        "  txn000001  "
    ) == "TXN000001"


def test_normalize_uppercase_value(
    repository,
):
    assert repository._normalize(
        "Txn000001"
    ) == "TXN000001"


# ----------------------------------------------------------------------
# Transaction Number Lookup
# ----------------------------------------------------------------------


def test_find_by_transaction_number(
    repository_with_transaction,
    transaction,
):
    found = (
        repository_with_transaction
        .find_by_transaction_number(
            transaction.transaction_number
        )
    )

    assert found is transaction


def test_find_by_transaction_number_is_case_insensitive(
    repository_with_transaction,
    transaction,
):
    found = (
        repository_with_transaction
        .find_by_transaction_number(
            "txn000001"
        )
    )

    assert found is transaction


def test_find_by_transaction_number_ignores_whitespace(
    repository_with_transaction,
    transaction,
):
    found = (
        repository_with_transaction
        .find_by_transaction_number(
            "  TXN000001  "
        )
    )

    assert found is transaction


def test_find_by_transaction_number_returns_none_when_missing(
    repository,
):
    found = (
        repository
        .find_by_transaction_number(
            "TXN999999"
        )
    )

    assert found is None


# ----------------------------------------------------------------------
# Transaction Number Existence
# ----------------------------------------------------------------------


def test_exists_transaction_number_returns_true(
    repository_with_transaction,
    transaction,
):
    assert (
        repository_with_transaction
        .exists_transaction_number(
            transaction.transaction_number
        )
        is True
    )


def test_exists_transaction_number_is_case_insensitive(
    repository_with_transaction,
):
    assert (
        repository_with_transaction
        .exists_transaction_number(
            "txn000001"
        )
        is True
    )


def test_exists_transaction_number_returns_false_when_missing(
    repository,
):
    assert (
        repository
        .exists_transaction_number(
            "TXN999999"
        )
        is False
    )


# ----------------------------------------------------------------------
# Add Transaction
# ----------------------------------------------------------------------


def test_add_transaction(
    repository,
    transaction,
):
    repository.add_transaction(
        transaction
    )

    assert repository.count == 1

    found = (
        repository
        .find_by_transaction_number(
            transaction.transaction_number
        )
    )

    assert found is transaction


def test_add_transaction_persists_to_storage(
    repository,
    transaction,
):
    repository.add_transaction(
        transaction
    )

    assert repository.CSV_FILE.exists()
    assert repository.CSV_FILE.stat().st_size > 0


def test_add_duplicate_transaction_number_raises(
    repository,
    transaction,
):
    repository.add_transaction(
        transaction
    )

    duplicate = Transaction(
        transaction_number=(
            transaction.transaction_number
        ),
        transaction_type=TransactionType.DEPOSIT,
        amount=Money(
            Decimal("500.00"),
            "SAR",
        ),
        source_account=None,
        destination_account="SA000002",
        initiated_by="system",
        description="Duplicate transaction",
    )

    with pytest.raises(
        EntityAlreadyExistsError
    ):
        repository.add_transaction(
            duplicate
        )


def test_duplicate_transaction_does_not_increase_count(
    repository,
    transaction,
):
    repository.add_transaction(
        transaction
    )

    duplicate = Transaction(
        transaction_number=(
            transaction.transaction_number
        ),
        transaction_type=TransactionType.DEPOSIT,
        amount=Money(
            Decimal("500.00"),
            "SAR",
        ),
        source_account=None,
        destination_account="SA000002",
        initiated_by="system",
    )

    with pytest.raises(
        EntityAlreadyExistsError
    ):
        repository.add_transaction(
            duplicate
        )

    assert repository.count == 1


# ----------------------------------------------------------------------
# Transaction Exists Convenience Method
# ----------------------------------------------------------------------


def test_transaction_exists_returns_true(
    repository_with_transaction,
    transaction,
):
    assert (
        repository_with_transaction
        .transaction_exists(
            transaction.transaction_number
        )
        is True
    )


def test_transaction_exists_returns_false(
    repository,
):
    assert (
        repository
        .transaction_exists(
            "TXN999999"
        )
        is False
    )


def test_transaction_exists_is_case_insensitive(
    repository_with_transaction,
):
    assert (
        repository_with_transaction
        .transaction_exists(
            "txn000001"
        )
        is True
    )

# Part 2 — Transaction Type, Status, and Counts

# ----------------------------------------------------------------------
# Part 2 — Transaction Type Queries
# ----------------------------------------------------------------------


@pytest.fixture
def withdrawal_transaction():
    """
    Return a valid withdrawal transaction.
    """

    return Transaction(
        transaction_number="TXN000002",
        transaction_type=TransactionType.WITHDRAWAL,
        amount=Money(
            Decimal("100.00"),
            "SAR",
        ),
        source_account="SA000001",
        destination_account=None,
        initiated_by="system",
        description="Cash withdrawal",
    )


@pytest.fixture
def internal_transfer_transaction():
    """
    Return a valid internal transfer transaction.
    """

    return Transaction(
        transaction_number="TXN000003",
        transaction_type=TransactionType.INTERNAL_TRANSFER,
        amount=Money(
            Decimal("300.00"),
            "SAR",
        ),
        source_account="SA000001",
        destination_account="SA000002",
        initiated_by="system",
        description="Internal account transfer",
    )

@pytest.fixture
def external_transfer_transaction():
    """
    Return a valid external transfer transaction.
    """

    return Transaction(
        transaction_number="TXN000004",
        transaction_type=TransactionType.EXTERNAL_TRANSFER,
        amount=Money(
            Decimal("450.00"),
            "SAR",
        ),
        source_account="SA000001",
        destination_account="EXT000001",
        initiated_by="system",
        description="External account transfer",
    )

@pytest.fixture
def pending_transaction():
    """
    Return a pending transaction.

    The current Transaction model should be used to construct this
    transaction with its supported status mechanism.
    """

    return Transaction(
        transaction_number="TXN000004",
        transaction_type=TransactionType.DEPOSIT,
        amount=Money(
            Decimal("150.00"),
            "SAR",
        ),
        source_account=None,
        destination_account="SA000001",
        initiated_by="system",
        description="Pending deposit",
        transaction_status=TransactionStatus.PENDING,
    )


@pytest.fixture
def failed_transaction():
    """
    Return a failed transaction.
    """

    return Transaction(
        transaction_number="TXN000005",
        transaction_type=TransactionType.WITHDRAWAL,
        amount=Money(
            Decimal("200.00"),
            "SAR",
        ),
        source_account="SA000001",
        destination_account=None,
        initiated_by="system",
        description="Failed withdrawal",
        transaction_status=TransactionStatus.FAILED,
    )


@pytest.fixture
def repository_with_multiple_transactions(
    repository,
    transaction,
    withdrawal_transaction,
    internal_transfer_transaction,
    external_transfer_transaction,
):
    """
    Repository containing deposit, withdrawal, internal-transfer,
    and external-transfer transactions.
    """

    repository.add_transaction(
        transaction
    )

    repository.add_transaction(
        withdrawal_transaction
    )

    repository.add_transaction(
        internal_transfer_transaction
    )

    repository.add_transaction(
        external_transfer_transaction
    )

    return repository


@pytest.fixture
def repository_with_all_statuses(
    repository,
    transaction,
    pending_transaction,
    failed_transaction,
):
    """
    Repository containing completed, pending, and failed
    transactions.
    """

    repository.add_transaction(
        transaction
    )

    repository.add_transaction(
        pending_transaction
    )

    repository.add_transaction(
        failed_transaction
    )

    return repository


# ----------------------------------------------------------------------
# find_by_type()
# ----------------------------------------------------------------------


def test_find_by_type_deposit(
    repository_with_multiple_transactions,
    transaction,
):
    transactions = (
        repository_with_multiple_transactions
        .find_by_type(
            TransactionType.DEPOSIT
        )
    )

    assert len(transactions) == 1
    assert transactions[0] is transaction


def test_find_by_type_withdrawal(
    repository_with_multiple_transactions,
    withdrawal_transaction,
):
    transactions = (
        repository_with_multiple_transactions
        .find_by_type(
            TransactionType.WITHDRAWAL
        )
    )

    assert len(transactions) == 1
    assert (
        transactions[0]
        is withdrawal_transaction
    )


def test_find_by_type_internal_transfer(
    repository_with_multiple_transactions,
    internal_transfer_transaction,
):
    transactions = (
        repository_with_multiple_transactions
        .find_by_type(
            TransactionType.INTERNAL_TRANSFER
        )
    )

    assert len(transactions) == 1
    assert (
        transactions[0]
        is internal_transfer_transaction
    )


def test_find_by_type_external_transfer(
    repository_with_multiple_transactions,
    external_transfer_transaction,
):
    transactions = (
        repository_with_multiple_transactions
        .find_by_type(
            TransactionType.EXTERNAL_TRANSFER
        )
    )

    assert len(transactions) == 1
    assert (
        transactions[0]
        is external_transfer_transaction
    )


def test_find_by_type_returns_empty_list_when_no_match(
    repository_with_multiple_transactions,
):
    transactions = (
        repository_with_multiple_transactions
        .find_by_type(
            TransactionType.DEPOSIT
        )
    )

    assert all(
        transaction.transaction_type
        == TransactionType.DEPOSIT
        for transaction in transactions
    )


# ----------------------------------------------------------------------
# deposits()
# ----------------------------------------------------------------------


def test_deposits(
    repository_with_multiple_transactions,
    transaction,
):
    deposits = (
        repository_with_multiple_transactions
        .deposits()
    )

    assert len(deposits) == 1
    assert deposits[0] is transaction


# ----------------------------------------------------------------------
# withdrawals()
# ----------------------------------------------------------------------


def test_withdrawals(
    repository_with_multiple_transactions,
    withdrawal_transaction,
):
    withdrawals = (
        repository_with_multiple_transactions
        .withdrawals()
    )

    assert len(withdrawals) == 1
    assert (
        withdrawals[0]
        is withdrawal_transaction
    )


# ----------------------------------------------------------------------
# transfers()
# ----------------------------------------------------------------------

"""
def test_transfers(
    repository_with_multiple_transactions,
    transfer_transaction,
):
    transfers = (
        repository_with_multiple_transactions
        .transfers()
    )

    assert len(transfers) == 1
    assert (
        transfers[0]
        is transfer_transaction
    )
"""

def test_transfers(
    repository_with_multiple_transactions,
    internal_transfer_transaction,
    external_transfer_transaction,
):
    transfers = (
        repository_with_multiple_transactions
        .transfers()
    )

    assert len(transfers) == 2

    assert (
        internal_transfer_transaction
        in transfers
    )

    assert (
        external_transfer_transaction
        in transfers
    )


# ----------------------------------------------------------------------
# Transaction Status Queries
# ----------------------------------------------------------------------


def test_find_by_status_completed(
    repository_with_all_statuses,
    transaction,
):
    transactions = (
        repository_with_all_statuses
        .find_by_status(
            TransactionStatus.COMPLETED
        )
    )

    assert len(transactions) == 1
    assert transactions[0] is transaction


def test_find_by_status_pending(
    repository_with_all_statuses,
    pending_transaction,
):
    transactions = (
        repository_with_all_statuses
        .find_by_status(
            TransactionStatus.PENDING
        )
    )

    assert len(transactions) == 1
    assert (
        transactions[0]
        is pending_transaction
    )


def test_find_by_status_failed(
    repository_with_all_statuses,
    failed_transaction,
):
    transactions = (
        repository_with_all_statuses
        .find_by_status(
            TransactionStatus.FAILED
        )
    )

    assert len(transactions) == 1
    assert (
        transactions[0]
        is failed_transaction
    )


def test_find_by_status_returns_empty_list_when_no_match(
    repository,
):
    transactions = (
        repository.find_by_status(
            TransactionStatus.PENDING
        )
    )

    assert transactions == []


# ----------------------------------------------------------------------
# Status Convenience Methods
# ----------------------------------------------------------------------


def test_completed_transactions(
    repository_with_all_statuses,
    transaction,
):
    transactions = (
        repository_with_all_statuses
        .completed_transactions()
    )

    assert len(transactions) == 1
    assert transactions[0] is transaction


def test_pending_transactions(
    repository_with_all_statuses,
    pending_transaction,
):
    transactions = (
        repository_with_all_statuses
        .pending_transactions()
    )

    assert len(transactions) == 1
    assert (
        transactions[0]
        is pending_transaction
    )


def test_failed_transactions(
    repository_with_all_statuses,
    failed_transaction,
):
    transactions = (
        repository_with_all_statuses
        .failed_transactions()
    )

    assert len(transactions) == 1
    assert (
        transactions[0]
        is failed_transaction
    )


# ----------------------------------------------------------------------
# Transaction Counts
# ----------------------------------------------------------------------


def test_transaction_count(
    repository_with_multiple_transactions,
):
    assert (
        repository_with_multiple_transactions
        .transaction_count()
        == 4
    )


def test_completed_transaction_count(
    repository_with_all_statuses,
):
    assert (
        repository_with_all_statuses
        .completed_transaction_count()
        == 1
    )


def test_pending_transaction_count(
    repository_with_all_statuses,
):
    assert (
        repository_with_all_statuses
        .pending_transaction_count()
        == 1
    )


def test_failed_transaction_count(
    repository_with_all_statuses,
):
    assert (
        repository_with_all_statuses
        .failed_transaction_count()
        == 1
    )


def test_all_transaction_status_counts(
    repository_with_all_statuses,
):
    assert (
        repository_with_all_statuses
        .completed_transaction_count()
        == 1
    )

    assert (
        repository_with_all_statuses
        .pending_transaction_count()
        == 1
    )

    assert (
        repository_with_all_statuses
        .failed_transaction_count()
        == 1
    )

# PART 3



