"""
===============================================================================
Banking Management System (BMS)

File        : test_transaction_service.py
Description : Unit tests for TransactionService.

These tests exercise the current TransactionService contract using mocked
repositories.  They intentionally do not introduce architectural changes.
===============================================================================
"""

from datetime import date, datetime, time
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from exceptions import PersistenceError
from models.value_objects.money import Money
from services.transaction_service import TransactionService


ACCOUNT_NUMBER = "SA-100001"
DESTINATION_ACCOUNT = "CA-200001"
CUSTOMER_NUMBER = "C000001"
TRANSACTION_NUMBER = "TX-000001"


def make_type(
    value="Deposit",
    *,
    is_debit=False,
    is_credit=True,
):
    return SimpleNamespace(
        value=value,
        is_debit=is_debit,
        is_credit=is_credit,
    )


def make_transaction(
    number=TRANSACTION_NUMBER,
    *,
    account_number=ACCOUNT_NUMBER,
    customer_number=CUSTOMER_NUMBER,
    amount="100.00",
    transaction_type=None,
    transaction_date=None,
    transaction_time=None,
    description="Test transaction",
):
    return SimpleNamespace(
        transaction_number=number,
        account_number=account_number,
        customer_number=customer_number,
        amount=Money(
            amount=Decimal(amount),
            currency="SAR",
        ),
        transaction_type=(
            transaction_type
            or make_type()
        ),
        transaction_date=(
            transaction_date
            or date(2026, 8, 7)
        ),
        transaction_time=(
            transaction_time
            or time(10, 0, 0)
        ),
        description=description,
    )


def make_account(
    account_number=ACCOUNT_NUMBER,
    *,
    currency="SAR",
):
    return SimpleNamespace(
        account_number=account_number,
        currency=currency,
    )


@pytest.fixture
def transaction_repository():
    repository = MagicMock()
    repository.auto_save = True
    transactions = []

    repository.__iter__.side_effect = (
        lambda: iter(transactions)
    )
    repository.__len__.side_effect = (
        lambda: len(transactions)
    )
    return repository


@pytest.fixture
def account_repository():
    return MagicMock()


@pytest.fixture
def service(
    transaction_repository,
    account_repository,
):
    return TransactionService(
        transaction_repository=transaction_repository,
        account_repository=account_repository,
    )


# ---------------------------------------------------------------------------
# Constructor
# ---------------------------------------------------------------------------

def test_constructor_stores_repositories(
    service,
    transaction_repository,
    account_repository,
):
    assert service.repository is transaction_repository
    assert service._account_repository is account_repository


def test_repository_property_returns_transaction_repository(
    service,
    transaction_repository,
):
    assert service.repository is transaction_repository


# ---------------------------------------------------------------------------
# Recording
# ---------------------------------------------------------------------------

def test_record_transaction_returns_same_transaction(
    service,
    transaction_repository,
):
    transaction = make_transaction()

    result = service.record_transaction(
        transaction
    )

    assert result is transaction
    transaction_repository.add_transaction.assert_called_once_with(
        transaction
    )
    transaction_repository.flush.assert_called_once()


def test_record_transaction_propagates_repository_error(
    service,
    transaction_repository,
):
    transaction = make_transaction()
    error = RuntimeError("database failure")

    transaction_repository.add_transaction.side_effect = error

    with pytest.raises(RuntimeError, match="database failure"):
        service.record_transaction(transaction)

    transaction_repository.add_transaction.assert_called_once_with(
        transaction
    )



# ---------------------------------------------------------------------------
# Lookup and basic queries
# ---------------------------------------------------------------------------

def test_get_transaction_delegates_to_repository(
    service,
    transaction_repository,
):
    transaction = make_transaction()

    transaction_repository.get_or_raise.return_value = (
        transaction
    )

    result = service.get_transaction(
        TRANSACTION_NUMBER
    )

    assert result is transaction
    transaction_repository.get_or_raise.assert_called_once_with(
        TRANSACTION_NUMBER
    )


def test_transaction_exists_delegates_to_repository(
    service,
    transaction_repository,
):
    transaction_repository.transaction_exists.return_value = True

    assert service.transaction_exists(
        TRANSACTION_NUMBER
    ) is True

    transaction_repository.transaction_exists.assert_called_once_with(
        TRANSACTION_NUMBER
    )


def test_all_transactions_returns_repository_contents(
    service,
    transaction_repository,
):
    transactions = [
        make_transaction("TX-000001"),
        make_transaction("TX-000002"),
    ]
    transaction_repository.__iter__.side_effect = (
        lambda: iter(transactions)
    )

    assert service.all_transactions() == transactions


def test_account_delegates_to_account_repository(
    service,
    account_repository,
):
    account = make_account()
    account_repository.get_or_raise.return_value = account

    result = service.account(
        ACCOUNT_NUMBER
    )

    assert result is account
    account_repository.get_or_raise.assert_called_once_with(
        ACCOUNT_NUMBER
    )


# ---------------------------------------------------------------------------
# Search operations
# ---------------------------------------------------------------------------

def test_account_transactions_validates_account_then_queries_repository(
    service,
    transaction_repository,
    account_repository,
):
    account_repository.get_or_raise.return_value = (
        make_account()
    )
    transactions = [make_transaction()]
    transaction_repository.find_by_account.return_value = (
        transactions
    )

    result = service.account_transactions(
        ACCOUNT_NUMBER
    )

    assert result == transactions
    account_repository.get_or_raise.assert_called_once_with(
        ACCOUNT_NUMBER
    )
    transaction_repository.find_by_account.assert_called_once_with(
        ACCOUNT_NUMBER
    )


def test_customer_transactions_delegates_to_repository(
    service,
    transaction_repository,
):
    transactions = [make_transaction()]
    transaction_repository.find_by_customer.return_value = (
        transactions
    )

    result = service.customer_transactions(
        CUSTOMER_NUMBER
    )

    assert result == transactions
    transaction_repository.find_by_customer.assert_called_once_with(
        CUSTOMER_NUMBER
    )


def test_transactions_by_type_delegates_to_repository(
    service,
    transaction_repository,
):
    transaction_type = make_type("Deposit")
    expected = [make_transaction(transaction_type=transaction_type)]

    transaction_repository.find_by_type.return_value = expected

    assert service.transactions_by_type(
        transaction_type
    ) == expected

    transaction_repository.find_by_type.assert_called_once_with(
        transaction_type
    )


def test_transactions_between_delegates_to_repository(
    service,
    transaction_repository,
):
    start = date(2026, 8, 1)
    end = date(2026, 8, 7)
    expected = [make_transaction()]

    transaction_repository.find_between_dates.return_value = expected

    assert service.transactions_between(
        start,
        end,
    ) == expected

    transaction_repository.find_between_dates.assert_called_once_with(
        start,
        end,
    )


def test_recent_transactions_sorts_newest_first(
    service,
    transaction_repository,
):
    older = make_transaction(
        "TX-000001",
        transaction_date=date(2026, 8, 6),
        transaction_time=time(10, 0),
    )
    newer = make_transaction(
        "TX-000002",
        transaction_date=date(2026, 8, 7),
        transaction_time=time(9, 0),
    )

    transaction_repository.__iter__.side_effect = (
        lambda: iter([older, newer])
    )

    result = service.recent_transactions()

    assert result == [newer, older]


def test_recent_transactions_respects_limit(
    service,
    transaction_repository,
):
    transactions = [
        make_transaction(
            f"TX-{index:06d}",
            transaction_date=date(2026, 8, 7),
            transaction_time=time(index, 0),
        )
        for index in range(1, 6)
    ]

    transaction_repository.__iter__.side_effect = (
        lambda: iter(transactions)
    )

    result = service.recent_transactions(
        limit=2
    )

    assert len(result) == 2
    assert result[0] is transactions[-1]
    assert result[1] is transactions[-2]


def test_transaction_count_uses_repository_length(
    service,
    transaction_repository,
):
    transaction_repository.__len__.side_effect = lambda: 3

    assert service.transaction_count() == 3


def test_has_transactions_is_false_when_empty(
    service,
    transaction_repository,
):
    transaction_repository.__len__.side_effect = lambda: 0

    assert service.has_transactions() is False


def test_has_transactions_is_true_when_not_empty(
    service,
    transaction_repository,
):
    transaction_repository.__len__.side_effect = lambda: 1

    assert service.has_transactions() is True


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------

def test_account_statement_returns_simplified_rows(
    service,
    transaction_repository,
    account_repository,
):
    account_repository.get_or_raise.return_value = (
        make_account()
    )

    transaction = make_transaction(
        description="Salary",
    )
    transaction_repository.find_by_account.return_value = [
        transaction
    ]

    result = service.account_statement(
        ACCOUNT_NUMBER
    )

    assert result == [
        {
            "transaction_number": TRANSACTION_NUMBER,
            "date": transaction.transaction_date,
            "time": transaction.transaction_time,
            "type": "Deposit",
            "amount": transaction.amount,
            "description": "Salary",
        }
    ]


def test_transaction_summary_returns_expected_fields(
    service,
    transaction_repository,
):
    transaction = make_transaction()
    transaction_repository.get_or_raise.return_value = transaction

    result = service.transaction_summary(
        TRANSACTION_NUMBER
    )

    assert result == {
        "transaction_number": TRANSACTION_NUMBER,
        "account_number": ACCOUNT_NUMBER,
        "transaction_type": "Deposit",
        "amount": transaction.amount,
        "currency": "SAR",
        "date": transaction.transaction_date,
        "time": transaction.transaction_time,
        "description": "Test transaction",
    }


def test_transaction_listing_returns_transaction_summaries(
    service,
    transaction_repository,
):
    transaction = make_transaction()

    transaction_repository.__iter__.side_effect = (
        lambda: iter([transaction])
    )
    transaction_repository.get_or_raise.return_value = transaction

    result = service.transaction_listing()

    assert len(result) == 1
    assert result[0]["transaction_number"] == TRANSACTION_NUMBER
    assert result[0]["account_number"] == ACCOUNT_NUMBER


# ---------------------------------------------------------------------------
# Financial statistics
# ---------------------------------------------------------------------------

def test_debit_total_sums_debit_transactions(
    service,
    transaction_repository,
    account_repository,
):
    account_repository.get_or_raise.return_value = (
        make_account()
    )

    debit = make_transaction(
        "TX-000001",
        amount="100.00",
        transaction_type=make_type(
            "Withdrawal",
            is_debit=True,
            is_credit=False,
        ),
    )
    credit = make_transaction(
        "TX-000002",
        amount="50.00",
        transaction_type=make_type(
            "Deposit",
            is_debit=False,
            is_credit=True,
        ),
    )

    transaction_repository.find_by_account.return_value = [
        debit,
        credit,
    ]

    result = service.debit_total(
        ACCOUNT_NUMBER
    )

    assert result.amount == Decimal("100.00")
    assert result.currency == "SAR"


def test_credit_total_sums_credit_transactions(
    service,
    transaction_repository,
    account_repository,
):
    account_repository.get_or_raise.return_value = (
        make_account()
    )

    debit = make_transaction(
        "TX-000001",
        amount="100.00",
        transaction_type=make_type(
            "Withdrawal",
            is_debit=True,
            is_credit=False,
        ),
    )
    credit = make_transaction(
        "TX-000002",
        amount="50.00",
        transaction_type=make_type(
            "Deposit",
            is_debit=False,
            is_credit=True,
        ),
    )

    transaction_repository.find_by_account.return_value = [
        debit,
        credit,
    ]

    result = service.credit_total(
        ACCOUNT_NUMBER
    )

    assert result.amount == Decimal("50.00")
    assert result.currency == "SAR"


def test_statistics_returns_total_transaction_count(
    service,
    transaction_repository,
):
    transaction_repository.__len__.side_effect = lambda: 4

    assert service.statistics() == {
        "total_transactions": 4,
    }


def test_account_statistics_returns_expected_values(
    service,
    transaction_repository,
    account_repository,
):
    account_repository.get_or_raise.return_value = (
        make_account()
    )

    debit = make_transaction(
        "TX-000001",
        amount="100.00",
        transaction_type=make_type(
            "Withdrawal",
            is_debit=True,
            is_credit=False,
        ),
    )
    credit = make_transaction(
        "TX-000002",
        amount="50.00",
        transaction_type=make_type(
            "Deposit",
            is_debit=False,
            is_credit=True,
        ),
    )

    transaction_repository.find_by_account.return_value = [
        debit,
        credit,
    ]

    result = service.account_statistics(
        ACCOUNT_NUMBER
    )

    assert result["account_number"] == ACCOUNT_NUMBER
    assert result["transaction_count"] == 2
    assert result["total_debits"].amount == Decimal("100.00")
    assert result["total_credits"].amount == Decimal("50.00")


def test_average_transaction_amount_returns_zero_when_empty(
    service,
    transaction_repository,
    account_repository,
):
    account_repository.get_or_raise.return_value = (
        make_account()
    )
    transaction_repository.find_by_account.return_value = []

    result = service.average_transaction_amount(
        ACCOUNT_NUMBER
    )

    assert result.amount == Decimal("0.00")
    assert result.currency == "SAR"


def test_average_transaction_amount_returns_average(
    service,
    transaction_repository,
    account_repository,
):
    account_repository.get_or_raise.return_value = (
        make_account()
    )

    transactions = [
        make_transaction(
            "TX-000001",
            amount="100.00",
        ),
        make_transaction(
            "TX-000002",
            amount="300.00",
        ),
    ]
    transaction_repository.find_by_account.return_value = transactions

    result = service.average_transaction_amount(
        ACCOUNT_NUMBER
    )

    assert result.amount == Decimal("200.00")
    assert result.currency == "SAR"


def test_largest_transaction_returns_largest_amount(
    service,
    transaction_repository,
    account_repository,
):
    account_repository.get_or_raise.return_value = (
        make_account()
    )

    smaller = make_transaction(
        "TX-000001",
        amount="100.00",
    )
    larger = make_transaction(
        "TX-000002",
        amount="500.00",
    )
    transaction_repository.find_by_account.return_value = [
        smaller,
        larger,
    ]

    assert service.largest_transaction(
        ACCOUNT_NUMBER
    ) is larger


def test_largest_transaction_returns_none_when_empty(
    service,
    transaction_repository,
    account_repository,
):
    account_repository.get_or_raise.return_value = (
        make_account()
    )
    transaction_repository.find_by_account.return_value = []

    assert service.largest_transaction(
        ACCOUNT_NUMBER
    ) is None


def test_customer_statistics_returns_customer_count(
    service,
    transaction_repository,
):
    transactions = [
        make_transaction("TX-000001"),
        make_transaction("TX-000002"),
    ]
    transaction_repository.find_by_customer.return_value = transactions

    assert service.customer_statistics(
        CUSTOMER_NUMBER
    ) == {
        "customer_number": CUSTOMER_NUMBER,
        "transaction_count": 2,
    }


def test_repository_statistics_delegates_to_repository(
    service,
    transaction_repository,
):
    expected = {
        "total_transactions": 5,
        "completed_transactions": 4,
    }
    transaction_repository.statistics.return_value = expected

    assert service.repository_statistics() == expected


# ---------------------------------------------------------------------------
# Repository operations
# ---------------------------------------------------------------------------

def test_refresh_delegates_to_repository_reload(
    service,
    transaction_repository,
):
    service.refresh()

    transaction_repository.reload.assert_called_once()


def test_save_changes_delegates_to_repository_flush(
    service,
    transaction_repository,
):
    service.save_changes()

    transaction_repository.flush.assert_called_once()


def test_validate_repository_returns_true_when_count_matches_length(
    service,
    transaction_repository,
):
    transaction_repository.count = 3
    transaction_repository.__len__.side_effect = lambda: 3

    assert service.validate_repository() is True


def test_validate_repository_returns_false_when_count_differs(
    service,
    transaction_repository,
):
    transaction_repository.count = 3
    transaction_repository.__len__.side_effect = lambda: 2

    assert service.validate_repository() is False


def test_ensure_repository_is_valid_does_not_raise_when_valid(
    service,
    transaction_repository,
):
    transaction_repository.count = 2
    transaction_repository.__len__.side_effect = lambda: 2

    service.ensure_repository_is_valid()


def test_ensure_repository_is_valid_raises_when_invalid(
    service,
    transaction_repository,
):
    transaction_repository.count = 2
    transaction_repository.__len__.side_effect = lambda: 1

    with pytest.raises(
        PersistenceError,
        match="integrity validation failed",
    ):
        service.ensure_repository_is_valid()


# ---------------------------------------------------------------------------
# Date reporting helpers
# ---------------------------------------------------------------------------

def test_transactions_on_returns_matching_date(
    service,
    transaction_repository,
):
    target = date(2026, 8, 7)
    matching = make_transaction(
        "TX-000001",
        transaction_date=target,
    )
    other = make_transaction(
        "TX-000002",
        transaction_date=date(2026, 8, 6),
    )

    transaction_repository.__iter__.side_effect = (
        lambda: iter([matching, other])
    )

    assert service.transactions_on(target) == [matching]


def test_transactions_before_returns_older_transactions(
    service,
    transaction_repository,
):
    cutoff = date(2026, 8, 7)
    older = make_transaction(
        "TX-000001",
        transaction_date=date(2026, 8, 6),
    )
    newer = make_transaction(
        "TX-000002",
        transaction_date=date(2026, 8, 8),
    )

    transaction_repository.__iter__.side_effect = (
        lambda: iter([older, newer])
    )

    assert service.transactions_before(cutoff) == [older]


def test_transactions_after_returns_newer_transactions(
    service,
    transaction_repository,
):
    cutoff = date(2026, 8, 7)
    older = make_transaction(
        "TX-000001",
        transaction_date=date(2026, 8, 6),
    )
    newer = make_transaction(
        "TX-000002",
        transaction_date=date(2026, 8, 8),
    )

    transaction_repository.__iter__.side_effect = (
        lambda: iter([older, newer])
    )

    assert service.transactions_after(cutoff) == [newer]


# ---------------------------------------------------------------------------
# Chronological helpers
# ---------------------------------------------------------------------------

def test_latest_transaction_returns_latest(
    service,
    transaction_repository,
    account_repository,
):
    account_repository.get_or_raise.return_value = (
        make_account()
    )

    older = make_transaction(
        "TX-000001",
        transaction_date=date(2026, 8, 6),
        transaction_time=time(12, 0),
    )
    newer = make_transaction(
        "TX-000002",
        transaction_date=date(2026, 8, 7),
        transaction_time=time(9, 0),
    )

    transaction_repository.find_by_account.return_value = [
        older,
        newer,
    ]

    assert service.latest_transaction(
        ACCOUNT_NUMBER
    ) is newer


def test_latest_transaction_returns_none_when_empty(
    service,
    transaction_repository,
    account_repository,
):
    account_repository.get_or_raise.return_value = (
        make_account()
    )
    transaction_repository.find_by_account.return_value = []

    assert service.latest_transaction(
        ACCOUNT_NUMBER
    ) is None


def test_first_transaction_returns_earliest(
    service,
    transaction_repository,
    account_repository,
):
    account_repository.get_or_raise.return_value = (
        make_account()
    )

    older = make_transaction(
        "TX-000001",
        transaction_date=date(2026, 8, 6),
        transaction_time=time(12, 0),
    )
    newer = make_transaction(
        "TX-000002",
        transaction_date=date(2026, 8, 7),
        transaction_time=time(9, 0),
    )

    transaction_repository.find_by_account.return_value = [
        newer,
        older,
    ]

    assert service.first_transaction(
        ACCOUNT_NUMBER
    ) is older


def test_first_transaction_returns_none_when_empty(
    service,
    transaction_repository,
    account_repository,
):
    account_repository.get_or_raise.return_value = (
        make_account()
    )
    transaction_repository.find_by_account.return_value = []

    assert service.first_transaction(
        ACCOUNT_NUMBER
    ) is None


# ---------------------------------------------------------------------------
# Display
# ---------------------------------------------------------------------------

def test_str_contains_transaction_count(
    service,
    transaction_repository,
):
    transaction_repository.__len__.side_effect = lambda: 3

    assert str(service) == (
        "TransactionService(transactions=3)"
    )


def test_repr_contains_repository_and_count(
    service,
    transaction_repository,
):
    transaction_repository.__len__.side_effect = lambda: 2

    result = repr(service)

    assert "TransactionService" in result
    assert "repository=MagicMock" in result
    assert "transactions=2" in result
