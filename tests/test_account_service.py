"""
==============================================================================
Banking Management System (BMS)

File        : test_account_service.py
Description : Unit tests for AccountService.

These tests exercise the current AccountService contract without requiring
changes to the production architecture. Repository dependencies are mocked so
that the service layer is tested in isolation.
==============================================================================
"""

from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from exceptions import (
    EntityAlreadyExistsError,
    ValidationError,
)
from models.value_objects.money import Money
from services.account_service import AccountService


ACCOUNT_NUMBER = "SA-100001"
SECOND_ACCOUNT_NUMBER = "SA-100002"
CUSTOMER_NUMBER = "CUST000001"


def money(amount: str, currency: str = "SAR") -> Money:
    """Create a Money value for service-level tests."""
    return Money(
        amount=Decimal(amount),
        currency=currency,
    )


def make_account(
    account_number: str = ACCOUNT_NUMBER,
    customer_number: str = CUSTOMER_NUMBER,
    balance: str = "1000.00",
    currency: str = "SAR",
    active: bool = True,
    frozen: bool = False,
    deleted: bool = False,
):
    """Create a lightweight account test double."""
    account = MagicMock()
    account.account_number = account_number
    account.customer_number = customer_number
    account.balance = money(balance, currency)
    account.currency = currency
    account.is_active = active
    account.is_frozen = frozen
    account.is_deleted = deleted
    account.created_on = "2026-08-08"
    account.entity_id = f"ENTITY-{account_number}"
    account.account_type = SimpleNamespace(value="Savings")
    return account


@pytest.fixture
def account_repository():
    repository = MagicMock()
    repository.auto_save = True
    repository.count = 0
    repository.__len__.return_value = 0
    repository.__iter__.return_value = iter(())
    repository.statistics.return_value = {"count": 0}
    return repository


@pytest.fixture
def customer_repository():
    return MagicMock()


@pytest.fixture
def transaction_repository():
    return MagicMock()


@pytest.fixture
def service(
    account_repository,
    customer_repository,
    transaction_repository,
):
    return AccountService(
        account_repository=account_repository,
        customer_repository=customer_repository,
        transaction_repository=transaction_repository,
    )


@pytest.fixture
def account():
    return make_account()


@pytest.fixture
def customer():
    customer = MagicMock()
    customer.customer_id = CUSTOMER_NUMBER
    customer.is_active = True
    customer.is_deleted = False
    return customer


# ---------------------------------------------------------------------------
# Construction and lookup
# ---------------------------------------------------------------------------


def test_constructor_wires_repositories(
    service,
    account_repository,
    customer_repository,
    transaction_repository,
):
    assert service.repository is account_repository
    assert service._customer_repository is customer_repository
    assert service._transaction_repository is transaction_repository


def test_get_account_delegates_to_repository(
    service,
    account_repository,
    account,
):
    account_repository.get_or_raise.return_value = account

    result = service.get_account(ACCOUNT_NUMBER)

    assert result is account
    account_repository.get_or_raise.assert_called_once_with(ACCOUNT_NUMBER)


def test_account_exists_delegates_to_repository(
    service,
    account_repository,
):
    account_repository.account_exists.return_value = True

    assert service.account_exists(ACCOUNT_NUMBER) is True
    account_repository.account_exists.assert_called_once_with(ACCOUNT_NUMBER)


def test_get_customer_delegates_to_customer_repository(
    service,
    customer_repository,
    customer,
):
    customer_repository.get_or_raise.return_value = customer

    result = service.get_customer(CUSTOMER_NUMBER)

    assert result is customer
    customer_repository.get_or_raise.assert_called_once_with(CUSTOMER_NUMBER)


def test_customer_is_eligible_when_customer_is_active_and_not_deleted(
    service,
    customer_repository,
    customer,
):
    customer_repository.get_or_raise.return_value = customer

    assert service.customer_is_eligible(CUSTOMER_NUMBER) is True


def test_customer_is_ineligible_when_customer_is_inactive(
    service,
    customer_repository,
    customer,
):
    customer.is_active = False
    customer_repository.get_or_raise.return_value = customer

    assert service.customer_is_eligible(CUSTOMER_NUMBER) is False


def test_customer_is_ineligible_when_customer_is_inactive(
    service,
    customer_repository,
    customer,
):
    customer.is_active = False
    customer_repository.get_or_raise.return_value = customer

    assert service.customer_is_eligible(CUSTOMER_NUMBER) is False


def test_all_accounts_returns_repository_accounts(
    service,
    account_repository,
    account,
):
    account_repository.__iter__.return_value = iter([account])

    result = service.all_accounts()

    assert result == [account]


# ---------------------------------------------------------------------------
# Account opening and validation
# ---------------------------------------------------------------------------


def test_open_account_adds_account(
    service,
    account_repository,
    customer_repository,
    account,
):
    customer_repository.get_or_raise.return_value = SimpleNamespace(
        is_active=True,
        is_deleted=False,
    )
    account_repository.account_exists.return_value = False

    result = service.open_account(account)

    assert result is account
    account_repository.add_account.assert_called_once_with(account)


def test_open_account_rejects_ineligible_customer(
    service,
    account_repository,
    customer_repository,
    account,
):
    customer_repository.get_or_raise.return_value = SimpleNamespace(
        is_active=False,
        is_deleted=False,
    )

    with pytest.raises(ValidationError, match="not eligible"):
        service.open_account(account)

    account_repository.add_account.assert_not_called()


def test_open_account_rejects_duplicate_account(
    service,
    account_repository,
    customer_repository,
    account,
):
    customer_repository.get_or_raise.return_value = SimpleNamespace(
        is_active=True,
        is_deleted=False,
    )
    account_repository.account_exists.return_value = True

    with pytest.raises(EntityAlreadyExistsError, match="already exists"):
        service.open_account(account)

    account_repository.add_account.assert_not_called()


def test_open_account_with_positive_initial_deposit_calls_deposit(
    service,
    account_repository,
    customer_repository,
    account,
    monkeypatch,
):
    customer_repository.get_or_raise.return_value = SimpleNamespace(
        is_active=True,
        is_deleted=False,
    )
    account_repository.account_exists.return_value = False
    deposit = money("250.00")
    deposit_mock = MagicMock(return_value=account)
    monkeypatch.setattr(service, "deposit", deposit_mock)

    result = service.open_account(account, initial_deposit=deposit)

    assert result is account
    deposit_mock.assert_called_once_with(
        ACCOUNT_NUMBER,
        deposit,
        description="Initial Deposit",
    )


def test_open_account_does_not_deposit_zero_initial_amount(
    service,
    account_repository,
    customer_repository,
    account,
    monkeypatch,
):
    customer_repository.get_or_raise.return_value = SimpleNamespace(
        is_active=True,
        is_deleted=False,
    )
    account_repository.account_exists.return_value = False
    deposit_mock = MagicMock()
    monkeypatch.setattr(service, "deposit", deposit_mock)

    service.open_account(account, initial_deposit=money("0.00"))

    deposit_mock.assert_not_called()


def test_validate_account_returns_active_account(
    service,
    account_repository,
    account,
):
    account_repository.get_or_raise.return_value = account

    assert service.validate_account(ACCOUNT_NUMBER) is account


def test_validate_account_rejects_inactive_account(
    service,
    account_repository,
    account,
):
    account.is_active = False
    account_repository.get_or_raise.return_value = account

    with pytest.raises(ValidationError, match="inactive"):
        service.validate_account(ACCOUNT_NUMBER)


# ---------------------------------------------------------------------------
# Customer account queries
# ---------------------------------------------------------------------------


def test_customer_accounts_delegates_to_repository(
    service,
    account_repository,
    account,
):
    account_repository.find_by_customer.return_value = [account]

    result = service.customer_accounts(CUSTOMER_NUMBER)

    assert result == [account]
    account_repository.find_by_customer.assert_called_once_with(CUSTOMER_NUMBER)


def test_customer_account_count_returns_number_of_accounts(
    service,
    monkeypatch,
):
    monkeypatch.setattr(service, "customer_accounts", lambda _: [1, 2, 3])

    assert service.customer_account_count(CUSTOMER_NUMBER) == 3


def test_customer_has_accounts_true_when_customer_owns_accounts(
    service,
    monkeypatch,
):
    monkeypatch.setattr(service, "customer_account_count", lambda _: 1)

    assert service.customer_has_accounts(CUSTOMER_NUMBER) is True


def test_customer_has_accounts_false_when_customer_has_no_accounts(
    service,
    monkeypatch,
):
    monkeypatch.setattr(service, "customer_account_count", lambda _: 0)

    assert service.customer_has_accounts(CUSTOMER_NUMBER) is False


# ---------------------------------------------------------------------------
# Internal balance operations
# ---------------------------------------------------------------------------


def test_credit_account_deposits_positive_amount(
    service,
    account_repository,
    account,
):
    amount = money("100.00")

    service._credit_account(account, amount)

    account.deposit.assert_called_once_with(amount)
    account_repository.save_account.assert_called_once_with(account)


def test_credit_account_rejects_non_positive_amount(
    service,
    account,
):
    with pytest.raises(ValidationError, match="greater than zero"):
        service._credit_account(account, money("0.00"))

    account.deposit.assert_not_called()


def test_debit_account_withdraws_positive_amount(
    service,
    account_repository,
    account,
):
    amount = money("100.00")

    service._debit_account(account, amount)

    account.withdraw.assert_called_once_with(amount)
    account_repository.save_account.assert_called_once_with(account)


def test_debit_account_rejects_non_positive_amount(
    service,
    account,
):
    with pytest.raises(ValidationError, match="greater than zero"):
        service._debit_account(account, money("0.00"))

    account.withdraw.assert_not_called()


# ---------------------------------------------------------------------------
# Deposit, withdrawal, and transfer
# ---------------------------------------------------------------------------


def test_deposit_validates_account_and_credits_it(
    service,
    account,
    monkeypatch,
):
    monkeypatch.setattr(service, "validate_account", lambda _: account)
    amount = money("125.00")

    result = service.deposit(ACCOUNT_NUMBER, amount)

    assert result is account
    account.deposit.assert_called_once_with(amount)


def test_withdraw_validates_account_and_debits_it(
    service,
    account,
    monkeypatch,
):
    monkeypatch.setattr(service, "validate_account", lambda _: account)
    amount = money("125.00")

    result = service.withdraw(ACCOUNT_NUMBER, amount)

    assert result is account
    account.withdraw.assert_called_once_with(amount)


def test_transfer_moves_amount_between_two_accounts(
    service,
    account_repository,
    monkeypatch,
):
    source = make_account(ACCOUNT_NUMBER, balance="1000.00")
    destination = make_account(SECOND_ACCOUNT_NUMBER, balance="500.00")
    accounts = {
        ACCOUNT_NUMBER: source,
        SECOND_ACCOUNT_NUMBER: destination,
    }
    monkeypatch.setattr(service, "validate_account", lambda n: accounts[n])
    amount = money("200.00")

    result = service.transfer(
        ACCOUNT_NUMBER,
        SECOND_ACCOUNT_NUMBER,
        amount,
    )

    assert result == (source, destination)
    source.withdraw.assert_called_once_with(amount)
    destination.deposit.assert_called_once_with(amount)
    assert account_repository.save_account.call_count == 2


def test_transfer_rejects_same_source_and_destination(
    service,
    account,
    monkeypatch,
):
    monkeypatch.setattr(service, "validate_account", lambda _: account)

    with pytest.raises(ValidationError, match="different"):
        service.transfer(
            ACCOUNT_NUMBER,
            ACCOUNT_NUMBER,
            money("100.00"),
        )


def test_transfer_rejects_non_positive_amount(
    service,
    account,
    monkeypatch,
):
    other = make_account(SECOND_ACCOUNT_NUMBER)
    monkeypatch.setattr(
        service,
        "validate_account",
        lambda n: account if n == ACCOUNT_NUMBER else other,
    )

    with pytest.raises(ValidationError, match="greater than zero"):
        service.transfer(
            ACCOUNT_NUMBER,
            SECOND_ACCOUNT_NUMBER,
            money("0.00"),
        )


# ---------------------------------------------------------------------------
# Balance queries and lifecycle
# ---------------------------------------------------------------------------


def test_balance_returns_account_balance(
    service,
    account,
    monkeypatch,
):
    monkeypatch.setattr(service, "validate_account", lambda _: account)

    assert service.balance(ACCOUNT_NUMBER) == account.balance


def test_close_account_closes_zero_balance_account(
    service,
    account_repository,
    account,
    monkeypatch,
):
    account.balance = money("0.00")
    monkeypatch.setattr(service, "validate_account", lambda _: account)

    result = service.close_account(ACCOUNT_NUMBER)

    assert result is account
    account.close.assert_called_once_with()
    account_repository.save_account.assert_called_once_with(account)


def test_freeze_account_freezes_and_persists(
    service,
    account_repository,
    account,
    monkeypatch,
):
    monkeypatch.setattr(service, "validate_account", lambda _: account)

    result = service.freeze_account(ACCOUNT_NUMBER)

    assert result is account
    account.freeze.assert_called_once_with()
    account_repository.save_account.assert_called_once_with(account)


def test_unfreeze_account_unfreezes_and_persists(
    service,
    account_repository,
    account,
):
    account_repository.get_or_raise.return_value = account

    result = service.unfreeze_account(ACCOUNT_NUMBER)

    assert result is account
    account.unfreeze.assert_called_once_with()
    account_repository.save_account.assert_called_once_with(account)


# ---------------------------------------------------------------------------
# Account queries and summaries
# ---------------------------------------------------------------------------


def test_accounts_for_customer_delegates_to_repository(
    service,
    account_repository,
    account,
):
    account_repository.find_by_customer.return_value = [account]

    assert service.accounts_for_customer(CUSTOMER_NUMBER) == [account]


def test_active_accounts_delegates_to_repository(
    service,
    account_repository,
    account,
):
    account_repository.find_active_accounts.return_value = [account]

    assert service.active_accounts() == [account]


def test_inactive_accounts_delegates_to_repository(
    service,
    account_repository,
    account,
):
    account_repository.find_inactive_accounts.return_value = [account]

    assert service.inactive_accounts() == [account]


def test_account_summary_returns_expected_fields(
    service,
    account,
    monkeypatch,
):
    monkeypatch.setattr(service, "get_account", lambda _: account)

    result = service.account_summary(ACCOUNT_NUMBER)

    assert result == {
        "account_number": ACCOUNT_NUMBER,
        "customer_number": CUSTOMER_NUMBER,
        "account_type": "Savings",
        "currency": "SAR",
        "balance": account.balance,
        "active": account.is_active,
        "frozen": account.is_frozen,
        "closed": account.is_deleted,
        "created_on": account.created_on,
    }


def test_account_count_uses_entity_count(
    service,
    account_repository,
):
    account_repository.__len__.return_value = 3

    assert service.account_count() == 3


def test_active_account_count_returns_active_count(
    service,
    monkeypatch,
):
    monkeypatch.setattr(service, "active_accounts", lambda: [1, 2])

    assert service.active_account_count() == 2


def test_inactive_account_count_returns_inactive_count(
    service,
    monkeypatch,
):
    monkeypatch.setattr(service, "inactive_accounts", lambda: [1])

    assert service.inactive_account_count() == 1


def test_total_balance_aggregates_active_accounts(
    service,
    monkeypatch,
):
    accounts = [
        make_account("A1", balance="100.00"),
        make_account("A2", balance="250.00"),
    ]
    monkeypatch.setattr(service, "active_accounts", lambda: accounts)

    result = service.total_balance("SAR")

    assert result.amount == Decimal("350.00")
    assert result.currency == "SAR"


def test_total_balance_filters_by_currency(
    service,
    monkeypatch,
):
    accounts = [
        make_account("A1", balance="100.00", currency="SAR"),
        make_account("A2", balance="250.00", currency="USD"),
    ]
    monkeypatch.setattr(service, "active_accounts", lambda: accounts)

    result = service.total_balance("SAR")

    assert result.amount == Decimal("100.00")
    assert result.currency == "SAR"


def test_average_balance_returns_zero_when_no_accounts(
    service,
    monkeypatch,
):
    monkeypatch.setattr(service, "active_accounts", lambda: [])

    result = service.average_balance("SAR")

    assert result.amount == Decimal("0.00")
    assert result.currency == "SAR"


def test_average_balance_calculates_average(
    service,
    monkeypatch,
):
    accounts = [
        make_account("A1", balance="100.00"),
        make_account("A2", balance="300.00"),
    ]
    monkeypatch.setattr(service, "active_accounts", lambda: accounts)

    result = service.average_balance("SAR")

    assert result.amount == Decimal("200.00")
    assert result.currency == "SAR"


def test_statistics_returns_account_counts(
    service,
    monkeypatch,
):
    monkeypatch.setattr(service, "account_count", lambda: 4)
    monkeypatch.setattr(service, "active_account_count", lambda: 3)
    monkeypatch.setattr(service, "inactive_account_count", lambda: 1)

    assert service.statistics() == {
        "total_accounts": 4,
        "active_accounts": 3,
        "inactive_accounts": 1,
    }


def test_has_accounts_true_when_accounts_exist(
    service,
    monkeypatch,
):
    monkeypatch.setattr(service, "account_count", lambda: 1)

    assert service.has_accounts() is True


def test_has_accounts_false_when_no_accounts_exist(
    service,
    monkeypatch,
):
    monkeypatch.setattr(service, "account_count", lambda: 0)

    assert service.has_accounts() is False


def test_customer_total_balance_returns_zero_when_customer_has_no_accounts(
    service,
    monkeypatch,
):
    monkeypatch.setattr(service, "accounts_for_customer", lambda _: [])

    result = service.customer_total_balance(CUSTOMER_NUMBER)

    assert result.amount == Decimal("0.00")
    assert result.currency == "USD"


def test_customer_total_balance_aggregates_customer_accounts(
    service,
    monkeypatch,
):
    accounts = [
        make_account("A1", balance="100.00"),
        make_account("A2", balance="250.00"),
    ]
    monkeypatch.setattr(service, "accounts_for_customer", lambda _: accounts)

    result = service.customer_total_balance(CUSTOMER_NUMBER)

    assert result.amount == Decimal("350.00")
    assert result.currency == "SAR"


def test_account_listing_returns_summary_for_each_account(
    service,
    account,
    monkeypatch,
):
    monkeypatch.setattr(service, "all_accounts", lambda: [account])
    summary = {"account_number": ACCOUNT_NUMBER}
    monkeypatch.setattr(service, "account_summary", lambda _: summary)

    assert service.account_listing() == [summary]


def test_customer_account_listing_returns_summary_for_each_customer_account(
    service,
    account,
    monkeypatch,
):
    monkeypatch.setattr(service, "accounts_for_customer", lambda _: [account])
    summary = {"account_number": ACCOUNT_NUMBER}
    monkeypatch.setattr(service, "account_summary", lambda _: summary)

    assert service.customer_account_listing(CUSTOMER_NUMBER) == [summary]


# ---------------------------------------------------------------------------
# Repository operations and status helpers
# ---------------------------------------------------------------------------


def test_refresh_delegates_to_repository_reload(
    service,
    account_repository,
):
    service.refresh()
    account_repository.reload.assert_called_once_with()


def test_save_changes_delegates_to_repository_flush(
    service,
    account_repository,
):
    service.save_changes()
    account_repository.flush.assert_called_once_with()


def test_repository_statistics_delegates_to_repository(
    service,
    account_repository,
):
    expected = {"count": 2}
    account_repository.statistics.return_value = expected

    assert service.repository_statistics() == expected


def test_validate_repository_returns_true_when_count_matches_length(
    service,
    account_repository,
):
    account_repository.count = 2
    account_repository.__len__.return_value = 2

    assert service.validate_repository() is True


def test_validate_repository_returns_false_when_count_differs_from_length(
    service,
    account_repository,
):
    account_repository.count = 3
    account_repository.__len__.return_value = 2

    assert service.validate_repository() is False


def test_is_account_active_returns_account_active_state(
    service,
    account,
    monkeypatch,
):
    monkeypatch.setattr(service, "validate_account", lambda _: account)

    assert service.is_account_active(ACCOUNT_NUMBER) is True


def test_is_account_frozen_returns_account_frozen_state(
    service,
    account_repository,
    account,
):
    account.is_frozen = True
    account_repository.get_or_raise.return_value = account

    assert service.is_account_frozen(ACCOUNT_NUMBER) is True


def test_is_account_closed_returns_account_deleted_state(
    service,
    account_repository,
    account,
):
    account.is_deleted = True
    account_repository.get_or_raise.return_value = account

    assert service.is_account_closed(ACCOUNT_NUMBER) is True


# ---------------------------------------------------------------------------
# String representations
# ---------------------------------------------------------------------------


def test_str_representation_contains_service_name_and_account_count(
    service,
    monkeypatch,
):
    monkeypatch.setattr(service, "account_count", lambda: 2)

    assert str(service) == "AccountService(accounts=2)"


def test_repr_representation_contains_repository_name_and_account_count(
    service,
    account_repository,
    monkeypatch,
):
    monkeypatch.setattr(service, "account_count", lambda: 2)

    result = repr(service)

    assert "AccountService" in result
    assert "accounts=2" in result
    assert account_repository.__class__.__name__ in result
