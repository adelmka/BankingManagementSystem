from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal

import pytest

from exceptions.banking_exceptions import ValidationError
from models.transaction import Transaction
from models.value_objects.money import Money
from utils.constants import (
    Currency,
    TransactionStatus,
    TransactionType,
)


# ==========================================================
# Fixtures
# ==========================================================

@pytest.fixture
def amount():

    return Money(
        Decimal("250.00"),
        Currency.SAR,
    )


@pytest.fixture
def transaction(
    amount,
):

    return Transaction(
        transaction_number="TXN000001",
        transaction_type=TransactionType.DEPOSIT,
        amount=amount,
        source_account="",
        destination_account="SA000001",
        initiated_by="admin",
        description="Initial deposit",
        reference_number="REF000001",
    )


# ==========================================================
# Constructor
# ==========================================================

def test_create_transaction(
    transaction,
):

    assert transaction.transaction_number == "TXN000001"

    assert (
        transaction.transaction_type
        == TransactionType.DEPOSIT
    )

    assert (
        transaction.transaction_status
        == TransactionStatus.COMPLETED
    )

    assert (
        transaction.amount.amount
        == Decimal("250.00")
    )

    assert (
        transaction.destination_account
        == "SA000001"
    )

    assert transaction.source_account == ""

    assert transaction.reference_number == "REF000001"

    assert transaction.description == "Initial deposit"

    assert transaction.initiated_by == "admin"

    assert transaction.approved_by == ""

    assert transaction.remarks == ""

    assert isinstance(
        transaction.transaction_date,
        datetime,
    )


def test_transaction_number_is_uppercase(
    amount,
):

    transaction = Transaction(
        transaction_number="txn123",
        transaction_type=TransactionType.DEPOSIT,
        amount=amount,
        source_account="",
        destination_account="SA000001",
        initiated_by="admin",
    )

    assert transaction.transaction_number == "TXN123"


def test_reference_number_is_uppercase(
    amount,
):

    transaction = Transaction(
        transaction_number="TXN000002",
        transaction_type=TransactionType.DEPOSIT,
        amount=amount,
        source_account="",
        destination_account="SA000001",
        initiated_by="admin",
        reference_number="ref123",
    )

    assert transaction.reference_number == "REF123"


def test_empty_reference_number_defaults_to_empty_string(
    amount,
):

    transaction = Transaction(
        transaction_number="TXN000003",
        transaction_type=TransactionType.DEPOSIT,
        amount=amount,
        source_account="",
        destination_account="SA000001",
        initiated_by="admin",
    )

    assert transaction.reference_number == ""


def test_source_account_defaults_to_empty_string(
    amount,
):

    transaction = Transaction(
        transaction_number="TXN000004",
        transaction_type=TransactionType.DEPOSIT,
        amount=amount,
        source_account=None,
        destination_account="SA000001",
        initiated_by="admin",
    )

    assert transaction.source_account == ""


def test_destination_account_defaults_to_empty_string(
    amount,
):

    transaction = Transaction(
        transaction_number="TXN000005",
        transaction_type=TransactionType.WITHDRAWAL,
        amount=amount,
        source_account="SA000001",
        destination_account=None,
        initiated_by="admin",
    )

    assert transaction.destination_account == ""


def test_created_status_is_completed(
    transaction,
):

    assert (
        transaction.transaction_status
        == TransactionStatus.COMPLETED
    )


def test_transaction_date_defaults_to_now(
    transaction,
):

    now = datetime.now(UTC)

    delta = abs(
        (
            now
            - transaction.transaction_date
        ).total_seconds()
    )

    assert delta < 5


# ==========================================================
# Constructor Validation
# ==========================================================

def test_transaction_number_required(
    amount,
):

    with pytest.raises(ValidationError):

        Transaction(
            transaction_number="",
            transaction_type=TransactionType.DEPOSIT,
            amount=amount,
            source_account="",
            destination_account="SA000001",
            initiated_by="admin",
        )


def test_transaction_type_must_be_enum(
    amount,
):

    with pytest.raises(TypeError):

        Transaction(
            transaction_number="TXN000010",
            transaction_type="Deposit",
            amount=amount,
            source_account="",
            destination_account="SA000001",
            initiated_by="admin",
        )


def test_amount_must_be_money():

    with pytest.raises(TypeError):

        Transaction(
            transaction_number="TXN000011",
            transaction_type=TransactionType.DEPOSIT,
            amount=Decimal("25.00"),
            source_account="",
            destination_account="SA000001",
            initiated_by="admin",
        )


def test_initiated_by_required(
    amount,
):

    with pytest.raises(ValidationError):

        Transaction(
            transaction_number="TXN000012",
            transaction_type=TransactionType.DEPOSIT,
            amount=amount,
            source_account="",
            destination_account="SA000001",
            initiated_by="",
        )

# Part 2 – Property & Status Tests

# ==========================================================
# Part 2 - Property Tests
# ==========================================================

def test_transaction_number_property(transaction):

    assert transaction.transaction_number == "TXN000001"


def test_reference_number_property(transaction):

    assert transaction.reference_number == "REF000001"


def test_transaction_type_property(transaction):

    assert (
        transaction.transaction_type
        == TransactionType.DEPOSIT
    )


def test_transaction_status_property(transaction):

    assert (
        transaction.transaction_status
        == TransactionStatus.COMPLETED
    )


def test_amount_property(transaction):

    assert (
        transaction.amount.amount
        == Decimal("250.00")
    )


def test_source_account_property(transaction):

    assert transaction.source_account == ""


def test_destination_account_property(transaction):

    assert transaction.destination_account == "SA000001"


def test_description_property(transaction):

    assert (
        transaction.description
        == "Initial deposit"
    )


def test_initiated_by_property(transaction):

    assert transaction.initiated_by == "admin"


def test_approved_by_property(transaction):

    assert transaction.approved_by == ""


def test_remarks_property(transaction):

    assert transaction.remarks == ""


def test_transaction_date_property(transaction):

    assert isinstance(
        transaction.transaction_date,
        datetime,
    )

# Part 3 – Setter Validation & Version Tracking

# ==========================================================
# Part 3 - Setter Validation
# ==========================================================

def test_change_transaction_status(transaction):

    version = transaction.version

    transaction.transaction_status = (
        TransactionStatus.PENDING
    )

    assert (
        transaction.transaction_status
        == TransactionStatus.PENDING
    )

    assert transaction.version == version + 1


def test_invalid_transaction_status(transaction):

    with pytest.raises(TypeError):

        transaction.transaction_status = "Completed"


def test_change_approved_by(transaction):

    version = transaction.version

    transaction.approved_by = " manager "

    assert transaction.approved_by == "manager"

    assert transaction.version == version + 1


def test_change_remarks(transaction):

    version = transaction.version

    transaction.remarks = " processed "

    assert transaction.remarks == "processed"

    assert transaction.version == version + 1

# Part 4 – Status Transition Methods

# ==========================================================
# Part 4 - Status Methods
# ==========================================================

def test_mark_pending(transaction):

    transaction.mark_pending()

    assert transaction.is_pending()


def test_mark_completed(transaction):

    transaction.mark_pending()

    transaction.mark_completed()

    assert transaction.is_completed()


def test_mark_failed(transaction):

    transaction.mark_failed()

    assert transaction.is_failed()


def test_mark_reversed(transaction):

    transaction.mark_reversed()

    assert transaction.is_reversed()

# Part 5 – Approval Behavior

# ==========================================================
# Part 5 - Approval
# ==========================================================

def test_approve_transaction(transaction):

    transaction.mark_pending()

    transaction.approve("Supervisor")

    assert (
        transaction.approved_by
        == "Supervisor"
    )

    assert transaction.is_completed()


def test_approve_requires_user(transaction):

    with pytest.raises(Exception):

        transaction.approve("")

# Part 6 – Serialization / Deserialization

# ==========================================================
# Part 6 - Serialization
# ==========================================================

# ==========================================================
# Serialization
# ==========================================================

def test_to_dict(transaction):

    data = transaction.to_dict()

    assert data["transaction_number"] == "TXN000001"

    assert (
        data["transaction_type"]
        == TransactionType.DEPOSIT.value
    )

    assert (
        data["transaction_status"]
        == TransactionStatus.COMPLETED.value
    )

    assert data["amount"] == "250.00"

    assert data["currency"] == Currency.SAR

    assert data["source_account"] == ""

    assert data["destination_account"] == "SA000001"

    assert data["description"] == "Initial deposit"

    assert data["initiated_by"] == "admin"

    assert data["approved_by"] == ""

    assert data["remarks"] == ""

    assert data["reference_number"] == "REF000001"

    assert "transaction_date" in data

    assert "entity_id" in data

    assert "created_at" in data

    assert "updated_at" in data

    assert "version" in data

    assert "is_active" in data

def test_from_dict(transaction):

    data = transaction.to_dict()

    restored = Transaction.from_dict(data)

    assert (
        restored.transaction_number
        == transaction.transaction_number
    )

    assert (
        restored.reference_number
        == transaction.reference_number
    )

    assert (
        restored.transaction_type
        == transaction.transaction_type
    )

    assert (
        restored.transaction_status
        == transaction.transaction_status
    )

    assert (
        restored.amount
        == transaction.amount
    )

    assert (
        restored.source_account
        == transaction.source_account
    )

    assert (
        restored.destination_account
        == transaction.destination_account
    )

    assert (
        restored.description
        == transaction.description
    )

    assert (
        restored.initiated_by
        == transaction.initiated_by
    )

    assert (
        restored.approved_by
        == transaction.approved_by
    )

    assert (
        restored.remarks
        == transaction.remarks
    )

    assert (
        restored.entity_id
        == transaction.entity_id
    )

    assert (
        restored.version
        == transaction.version
    )

    assert (
        restored.created_at
        == transaction.created_at
    )

    assert (
        restored.updated_at
        == transaction.updated_at
    )

# Part 7 – Classification Methods

# ==========================================================
# Part 7 - Classification
# ==========================================================

def test_is_credit(transaction):

    assert transaction.is_credit()


def test_is_debit():

    txn = Transaction(
        transaction_number="TXN000002",
        transaction_type=TransactionType.WITHDRAWAL,
        amount=Money(
            Decimal("500.00"),
            Currency.SAR,
        ),
        source_account="SA-100001",
        destination_account=None,
        initiated_by="admin",
    )

    assert txn.is_debit()


def test_internal_transfer():

    txn = Transaction(
        transaction_number="TXN000003",
        transaction_type=TransactionType.INTERNAL_TRANSFER,
        amount=Money(
            Decimal("250.00"),
            Currency.SAR,
        ),
        source_account="SA-1",
        destination_account="SA-2",
        initiated_by="admin",
    )

    assert txn.is_internal_transfer()
    assert not txn.is_external_transaction()


def test_external_transaction(transaction):

    assert transaction.is_external_transaction()


def test_can_reverse(transaction):

    assert transaction.can_reverse()


def test_requires_approval(transaction):

    assert not transaction.requires_approval()


def test_financial_transaction(transaction):

    assert transaction.is_financial_transaction()

# Part 8 – Display Helpers & Reversal

# ==========================================================
# Part 8 - Display Helpers
# ==========================================================

def test_display_name(transaction):

    assert transaction.display_name() == "Deposit"


def test_display_amount(transaction):

    assert str(transaction.amount) == transaction.display_amount()


def test_display_status(transaction):

    assert transaction.display_status() == "Completed"


def test_display_summary(transaction):

    summary = transaction.display_summary()

    assert "TXN000001" in summary
    assert "Deposit" in summary
    assert "Completed" in summary


def test_string_representation(transaction):

    assert str(transaction) == transaction.display_summary()

# Part 9 - Reversal Transaction

# ==========================================================
# Part 9 - Reversal
# ==========================================================

def test_clone_for_reversal(transaction):

    reversal = transaction.clone_for_reversal(
        transaction_number="TXN999999",
        initiated_by="manager",
    )

    assert reversal.transaction_number == "TXN999999"

    assert reversal.reference_number == (
        transaction.transaction_number
    )

    assert reversal.source_account == (
        transaction.destination_account
    )

    assert reversal.destination_account == (
        transaction.source_account
    )

    assert (
        transaction.transaction_number
        in reversal.description
    )

