# Part 1 — Imports, Test Repository & Fixtures

from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest

from exceptions import (
    EntityAlreadyExistsError,
    EntityNotFoundError,
)

from models.customer import Customer
from models.savings_account import SavingsAccount
from models.value_objects.address import Address
from models.value_objects.money import Money

from repositories.account_repository import AccountRepository

from utils.constants import (
    AccountStatus,
    AccountType,
    Gender,
)

from decimal import Decimal


class InMemoryAccountRepository(AccountRepository):
    """
    Test implementation using temporary CSV storage.
    """

    def __init__(self, csv_file: Path):

        self.CSV_FILE = csv_file

        super().__init__()


# ------------------------------------------------------------------
# Fixtures
# ------------------------------------------------------------------


@pytest.fixture
def address():

    return Address(
        address_line_1="123 Main Street",
        city="Riyadh",
        state_or_province="Riyadh",
        postal_code="12345",
        country="Saudi Arabia",
    )


@pytest.fixture
def customer(address):

    return Customer(
        customer_id="C000001",
        first_name="John",
        last_name="Smith",
        date_of_birth=date(1990, 1, 1),
        gender=Gender.MALE,
        national_id="1234567890",
        email="john@example.com",
        phone_number="+966500000001",
        address=address,
    )


@pytest.fixture
def account(customer):

    return SavingsAccount(
        account_number="SA000001",
        customer_id=customer.customer_id,
        opening_balance=Money(
            Decimal("1000.00"),
            "SAR",
        ),
        interest_rate=Decimal("2.50"),
        minimum_balance=Money(
            Decimal("100.00"),
            "SAR",
        ),
    )

@pytest.fixture
def repository(tmp_path):

    return InMemoryAccountRepository(
        tmp_path / "accounts.csv"
    )


@pytest.fixture
def repository_with_account(
    repository,
    account,
):

    repository.add(account)

    return repository

# Part 2 — Core Repository Operations

# ------------------------------------------------------------------
# Core repository operations
# ------------------------------------------------------------------


# ------------------------------------------------------------------
# Lookup methods
# ------------------------------------------------------------------


def test_find_by_account_number(
    repository_with_account,
    account,
):
    found = (
        repository_with_account
        .find_by_account_number(
            account.account_number
        )
    )

    assert found is account


def test_find_by_unknown_account_number(
    repository,
):
    assert (
        repository.find_by_account_number(
            "SA999999"
        )
        is None
    )


def test_exists_account_number(
    repository_with_account,
    account,
):
    assert (
        repository_with_account
        .exists_account_number(
            account.account_number
        )
        is True
    )


def test_exists_account_number_false(
    repository,
):
    assert (
        repository.exists_account_number(
            "SA999999"
        )
        is False
    )


def test_find_by_customer(
    repository_with_account,
    account,
):
    accounts = (
        repository_with_account
        .find_by_customer(
            account.customer_id
        )
    )

    assert len(accounts) == 1
    assert accounts[0] is account


def test_find_by_customer_unknown(
    repository,
):
    accounts = (
        repository.find_by_customer(
            "C999999"
        )
    )

    assert accounts == []


# ------------------------------------------------------------------
# Active / inactive
# ------------------------------------------------------------------


def test_find_active_accounts(
    repository_with_account,
    account,
):
    accounts = (
        repository_with_account
        .find_active_accounts()
    )

    assert len(accounts) == 1
    assert accounts[0] is account


def test_find_inactive_accounts(
    repository_with_account,
    account,
):
    account.deactivate()

    repository_with_account.update(
        account
    )

    accounts = (
        repository_with_account
        .find_inactive_accounts()
    )

    assert len(accounts) == 1
    assert accounts[0] is account


def test_customer_has_accounts(
    repository_with_account,
    account,
):
    assert (
        repository_with_account
        .customer_has_accounts(
            account.customer_id
        )
        is True
    )


def test_customer_has_accounts_false(
    repository,
):
    assert (
        repository.customer_has_accounts(
            "C999999"
        )
        is False
    )


def test_active_account_count(
    repository_with_account,
):
    assert (
        repository_with_account
        .active_account_count()
        == 1
    )


def test_statistics(
    repository_with_account,
):
    stats = (
        repository_with_account
        .statistics()
    )

    assert (
        stats["total_accounts"]
        == 1
    )

    assert (
        stats["active_accounts"]
        == 1
    )
    
# Part 3 — Account Classification & Filtering

# ------------------------------------------------------------------
# Account classification
# ------------------------------------------------------------------


def test_find_by_account_type(
    repository_with_account,
    account,
):
    accounts = (
        repository_with_account
        .find_by_account_type(
            account.account_type
        )
    )

    assert len(accounts) == 1
    assert accounts[0] is account


def test_savings_accounts(
    repository_with_account,
    account,
):
    accounts = (
        repository_with_account
        .savings_accounts()
    )

    assert len(accounts) == 1
    assert accounts[0] is account


def test_current_accounts_empty(
    repository_with_account,
):
    assert (
        repository_with_account
        .current_accounts()
        == []
    )


def test_time_deposit_accounts_empty(
    repository_with_account,
):
    assert (
        repository_with_account
        .time_deposit_accounts()
        == []
    )


# ------------------------------------------------------------------
# Currency
# ------------------------------------------------------------------


def test_find_by_currency(
    repository_with_account,
    account,
):
    accounts = (
        repository_with_account
        .find_by_currency(
            account.balance.currency
        )
    )

    assert len(accounts) == 1
    assert accounts[0] is account


def test_find_by_unknown_currency(
    repository_with_account,
):
    assert (
        repository_with_account
        .find_by_currency(
            "USD"
        )
        == []
    )


# ------------------------------------------------------------------
# Status
# ------------------------------------------------------------------


def test_find_by_status_active(
    repository_with_account,
    account,
):
    accounts = (
        repository_with_account
        .find_by_status(
            AccountStatus.ACTIVE
        )
    )

    assert len(accounts) == 1
    assert accounts[0] is account


def test_find_frozen_accounts(
    repository_with_account,
):
    assert (
        repository_with_account
        .find_frozen_accounts()
        == []
    )


def test_find_closed_accounts(
    repository_with_account,
):
    assert (
        repository_with_account
        .find_closed_accounts()
        == []
    )


def test_find_dormant_accounts(
    repository_with_account,
):
    assert (
        repository_with_account
        .find_dormant_accounts()
        == []
    )


def test_dormant_account_count(
    repository_with_account,
):
    assert (
        repository_with_account
        .dormant_account_count()
        == 0
    )


def test_frozen_account_count(
    repository_with_account,
):
    assert (
        repository_with_account
        .frozen_account_count()
        == 0
    )


# ------------------------------------------------------------------
# Balance filtering
# ------------------------------------------------------------------


def test_find_positive_balance_accounts(
    repository_with_account,
    account,
):
    accounts = (
        repository_with_account
        .find_positive_balance_accounts()
    )

    assert len(accounts) == 1
    assert accounts[0] is account


def test_find_zero_balance_accounts(
    repository_with_account,
):
    assert (
        repository_with_account
        .find_zero_balance_accounts()
        == []
    )


def test_find_negative_balance_accounts(
    repository_with_account,
):
    assert (
        repository_with_account
        .find_negative_balance_accounts()
        == []
    )


def test_find_overdrawn_accounts(
    repository_with_account,
):
    assert (
        repository_with_account
        .find_overdrawn_accounts()
        == []
    )

# PART 4
# ------------------------------------------------------------------
# Balance range
# ------------------------------------------------------------------


def test_find_by_balance_range(
    repository_with_account,
    account,
):
    accounts = (
        repository_with_account
        .find_by_balance_range(
            Decimal("100.00"),
            Decimal("1000.00"),
        )
    )

    assert len(accounts) == 1
    assert accounts[0] is account


def test_find_by_balance_range_no_matches(
    repository_with_account,
):
    accounts = (
        repository_with_account
        .find_by_balance_range(
            Decimal("5000.00"),
            Decimal("10000.00"),
        )
    )

    assert accounts == []


# ------------------------------------------------------------------
# Opening date
# ------------------------------------------------------------------


def test_find_opened_between(
    repository_with_account,
    account,
):
    accounts = (
        repository_with_account
        .find_opened_between(
            account.opened_date,
            account.opened_date,
        )
    )

    assert len(accounts) == 1
    assert accounts[0] is account


def test_find_opened_between_no_match(
    repository_with_account,
):
    accounts = (
        repository_with_account
        .find_opened_between(
            date(2000, 1, 1),
            date(2000, 12, 31),
        )
    )

    assert accounts == []

# ------------------------------------------------------------------
# Customer statistics
# ------------------------------------------------------------------


def test_customer_account_count(
    repository_with_account,
    account,
):
    assert (
        repository_with_account
        .customer_account_count(
            account.customer_id
        )
        == 1
    )


def test_customer_account_count_unknown_customer(
    repository,
):
    assert (
        repository.customer_account_count(
            "C999999"
        )
        == 0
    )


def test_customer_total_balance(
    repository_with_account,
    account,
):
    total = (
        repository_with_account
        .customer_total_balance(
            account.customer_id
        )
    )

    assert total == account.balance.amount


def test_customer_total_balance_unknown_customer(
    repository,
):
    total = (
        repository.customer_total_balance(
            "C999999"
        )
    )

    assert total == Decimal("0.00")


def test_customer_accounts_by_type(
    repository_with_account,
    account,
):
    accounts = (
        repository_with_account
        .customer_accounts_by_type(
            account.customer_id,
            account.account_type,
        )
    )

    assert len(accounts) == 1
    assert accounts[0] is account


def test_customer_accounts_by_type_unknown_customer(
    repository,
):
    accounts = (
        repository.customer_accounts_by_type(
            "C999999",
            AccountType.SAVINGS,
        )
    )

    assert accounts == []

# PART 5

# ------------------------------------------------------------------
# Validation
# ------------------------------------------------------------------


def test_account_exists(
    repository_with_account,
    account,
):
    assert (
        repository_with_account
        .account_exists(
            account.account_number
        )
        is True
    )


def test_account_exists_false(
    repository,
):
    assert (
        repository.account_exists(
            "SA999999"
        )
        is False
    )


def test_get_or_raise(
    repository_with_account,
    account,
):
    found = (
        repository_with_account
        .get_or_raise(
            account.account_number
        )
    )

    assert found is account


def test_get_or_raise_not_found(
    repository,
):
    with pytest.raises(
        EntityNotFoundError
    ):
        repository.get_or_raise(
            "SA999999"
        )


def test_validate_unique_account_duplicate(
    repository_with_account,
    account,
):
    with pytest.raises(
        EntityAlreadyExistsError
    ):
        repository_with_account.validate_unique_account(
            account
        )


# ------------------------------------------------------------------
# Persistence
# ------------------------------------------------------------------


def test_add_account(
    repository,
    account,
):
    repository.add_account(
        account
    )

    found = (
        repository.find_by_account_number(
            account.account_number
        )
    )

    assert found is account


def test_save_account(
    repository,
    account,
):
    repository.save_account(
        account
    )

    repository.reload()

    found = (
        repository.find_by_account_number(
            account.account_number
        )
    )

    assert found is not None
    assert (
        found.account_number
        == account.account_number
    )


def test_remove_account(
    repository_with_account,
    account,
):
    removed = (
        repository_with_account.remove_account(
            account.account_number
        )
    )

    assert removed is True

    # Active lookup should no longer find it.
    assert (
        repository_with_account.find_by_account_number(
            account.account_number
        )
        is None
    )

    # It should still exist as an inactive account.
    inactive = (
        repository_with_account.find_inactive_accounts()
    )

    # assert len(inactive) == 1
    # assert inactive[0] is account
    
    assert inactive[0].account_number == account.account_number

# ---added to do regression test
def test_find_by_account_number_ignores_inactive_accounts(
    repository_with_account,
    account,
):
    account.deactivate()
    repository_with_account.update(account)

    assert (
        repository_with_account.find_by_account_number(
            account.account_number
        )
        is None
    )

    inactive = repository_with_account.find_inactive_accounts()

    assert inactive[0] is account
    
# ------------------------------------------------------------------
# String representation
# ------------------------------------------------------------------


def test_str(
    repository_with_account,
):
    text = str(
        repository_with_account
    )

    assert (
        "AccountRepository"
        in text
    )


def test_repr(
    repository_with_account,
):
    text = repr(
        repository_with_account
    )

    assert (
        "AccountRepository"
        in text
    )

    assert (
        "count=1"
        in text
    )
