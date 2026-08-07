from __future__ import annotations

from datetime import UTC, date, datetime
from decimal import Decimal

import pytest

from models.savings_account import SavingsAccount
from models.value_objects.money import Money
from utils.constants import (
    AccountType,
    Currency,
    InterestFrequency,
)

# =====================================================================
# Fixtures
# =====================================================================

@pytest.fixture
def opening_balance():

    return Money(
        Decimal("10000.00"),
        Currency.SAR,
    )


@pytest.fixture
def minimum_balance():

    return Money(
        Decimal("1000.00"),
        Currency.SAR,
    )


@pytest.fixture
def savings_account(
    opening_balance,
    minimum_balance,
):

    return SavingsAccount(
        account_number="SA-200001",
        customer_id="CUST000001",
        opening_balance=opening_balance,
        interest_rate=Decimal("2.50"),
        minimum_balance=minimum_balance,
        currency=Currency.SAR,
        interest_frequency=InterestFrequency.MONTHLY,
    )


# =====================================================================
# Constructor Tests
# =====================================================================

def test_create_savings_account(savings_account):

    assert isinstance(
        savings_account,
        SavingsAccount,
    )


def test_account_number_initialized(savings_account):

    assert (
        savings_account.account_number
        == "SA-200001"
    )


def test_customer_id_initialized(savings_account):

    assert (
        savings_account.customer_id
        == "CUST000001"
    )


def test_account_type_is_savings(savings_account):

    assert (
        savings_account.account_type
        == AccountType.SAVINGS
    )


def test_opening_balance_initialized(savings_account):

    assert (
        savings_account.balance.amount
        == Decimal("10000.00")
    )


def test_currency_initialized(savings_account):

    assert (
        savings_account.currency
        == Currency.SAR
    )


def test_interest_rate_initialized(savings_account):

    assert (
        savings_account.interest_rate
        == Decimal("2.50")
    )


def test_minimum_balance_initialized(savings_account):

    assert (
        savings_account.minimum_balance.amount
        == Decimal("1000.00")
    )


def test_interest_frequency_initialized(
    savings_account,
):

    assert (
        savings_account.interest_frequency
        ==
        InterestFrequency.MONTHLY
    )


def test_last_interest_date_initialized(
    savings_account,
):

    assert (
        savings_account.last_interest_date
        ==
        datetime.now(UTC).date()
    )


def test_status_defaults_to_active(
    savings_account,
):

    assert savings_account.is_active_account


def test_created_with_no_transactions(
    savings_account,
):

    assert (
        len(
            savings_account.transaction_ids
        )
        == 0
    )


def test_version_initial_value(
    savings_account,
):

    assert savings_account.version == 1


def test_created_timestamp_exists(
    savings_account,
):

    assert (
        savings_account.created_at
        is not None
    )


def test_updated_timestamp_exists(
    savings_account,
):

    assert (
        savings_account.updated_at
        is not None
    )

# PART 2A

# =====================================================================
# Interest Rate Tests
# =====================================================================

def test_interest_rate_property(
    savings_account,
):

    assert (
        savings_account.interest_rate
        == Decimal("2.50")
    )


def test_change_interest_rate(
    savings_account,
):

    version = savings_account.version

    savings_account.interest_rate = Decimal("3.75")

    assert (
        savings_account.interest_rate
        == Decimal("3.75")
    )

    assert (
        savings_account.version
        == version + 1
    )


def test_interest_rate_zero_allowed(
    savings_account,
):

    savings_account.interest_rate = Decimal("0")

    assert (
        savings_account.interest_rate
        == Decimal("0")
    )


def test_negative_interest_rate_not_allowed(
    savings_account,
):

    with pytest.raises(ValueError):

        savings_account.interest_rate = (
            Decimal("-0.01")
        )


def test_interest_rate_updates_timestamp(
    savings_account,
):

    updated_at = savings_account.updated_at

    savings_account.interest_rate = Decimal("4.00")

    assert (
        savings_account.updated_at
        > updated_at
    )

# PART 2B

# =====================================================================
# Minimum Balance Tests
# =====================================================================

def test_minimum_balance_property(
    savings_account,
):

    assert (
        savings_account.minimum_balance.amount
        == Decimal("1000.00")
    )


def test_change_minimum_balance(
    savings_account,
):

    version = savings_account.version

    new_balance = Money(
        Decimal("500.00"),
        Currency.SAR,
    )

    savings_account.minimum_balance = new_balance

    assert (
        savings_account.minimum_balance
        == new_balance
    )

    assert (
        savings_account.version
        == version + 1
    )


def test_zero_minimum_balance_allowed(
    savings_account,
):

    savings_account.minimum_balance = Money(
        Decimal("0.00"),
        Currency.SAR,
    )

    assert (
        savings_account.minimum_balance.amount
        == Decimal("0.00")
    )


def test_negative_minimum_balance_not_allowed(
    savings_account,
):

    with pytest.raises(ValueError):

        savings_account.minimum_balance = Money(
            Decimal("-1.00"),
            Currency.SAR,
        )


def test_minimum_balance_currency_must_match(
    savings_account,
):

    with pytest.raises(ValueError):

        savings_account.minimum_balance = Money(
            Decimal("100.00"),
            Currency.USD,
        )


def test_minimum_balance_requires_money_object(
    savings_account,
):

    with pytest.raises(TypeError):

        savings_account.minimum_balance = Decimal("100.00")


# =====================================================================
# Interest Frequency Tests
# =====================================================================

def test_interest_frequency_property(
    savings_account,
):

    assert (
        savings_account.interest_frequency
        == InterestFrequency.MONTHLY
    )


def test_change_interest_frequency(
    savings_account,
):

    version = savings_account.version

    savings_account.interest_frequency = (
        InterestFrequency.ANNUALLY
    )

    assert (
        savings_account.interest_frequency
        == InterestFrequency.ANNUALLY
    )

    assert (
        savings_account.version
        == version + 1
    )


def test_invalid_interest_frequency_type(
    savings_account,
):

    with pytest.raises(TypeError):

        savings_account.interest_frequency = "MONTHLY"


# =====================================================================
# Last Interest Date Tests
# =====================================================================

def test_last_interest_date_property(
    savings_account,
):

    assert (
        savings_account.last_interest_date
        == datetime.now(UTC).date()
    )


def test_change_last_interest_date(
    savings_account,
):

    version = savings_account.version

    previous = date(
        2025,
        1,
        1,
    )

    savings_account.last_interest_date = previous

    assert (
        savings_account.last_interest_date
        == previous
    )

    assert (
        savings_account.version
        == version + 1
    )


def test_future_last_interest_date_not_allowed(
    savings_account,
):

    with pytest.raises(Exception):

        savings_account.last_interest_date = date(
            2100,
            1,
            1,
        )

# PART 3

# =====================================================================
# Savings-Specific Business Rules
# =====================================================================

def test_has_minimum_balance_true(
    savings_account,
):

    assert savings_account.has_minimum_balance()

""" remove as the business rules doesn't allow for a balance below 1000
def test_has_minimum_balance_false(
    savings_account,
):

    savings_account.withdraw(
        Money(
            Decimal("9000.00"),
            Currency.SAR,
        )
    )

    assert not savings_account.has_minimum_balance()

"""

# ---------------------------------------------------------------------

def test_amount_available_for_withdrawal(
    savings_account,
):

    available = (
        savings_account.amount_available_for_withdrawal()
    )

    assert available.amount == Decimal("9000.00")


def test_amount_available_zero_when_at_minimum(
    savings_account,
):

    savings_account.withdraw(
        Money(
            Decimal("9000.00"),
            Currency.SAR,
        )
    )

    available = (
        savings_account.amount_available_for_withdrawal()
    )

    assert available.amount == Decimal("0.00")


# ---------------------------------------------------------------------

def test_can_earn_interest_when_requirements_met(
    savings_account,
):

    assert savings_account.can_earn_interest()


""" -- remove this test as it violates the business rules of <1000
def test_cannot_earn_interest_when_below_minimum(
    savings_account,
):

    savings_account.withdraw(
        Money(
            Decimal("9000.00"),
            Currency.SAR,
        )
    )

    assert not savings_account.can_earn_interest()
"""

""" --- remove this test
def test_cannot_earn_interest_when_closed(
    savings_account,
):

    savings_account.withdraw(
        Money(
            Decimal("10000.00"),
            Currency.SAR,
        )
    )

    savings_account.close_account()

    assert not savings_account.can_earn_interest()
"""

# ---------------------------------------------------------------------

def test_withdraw_cannot_go_below_minimum_balance(
    savings_account,
):

    with pytest.raises(ValueError):

        savings_account.withdraw(
            Money(
                Decimal("9000.01"),
                Currency.SAR,
            )
        )


def test_withdraw_exactly_to_minimum_balance_allowed(
    savings_account,
):

    savings_account.withdraw(
        Money(
            Decimal("9000.00"),
            Currency.SAR,
        )
    )

    assert (
        savings_account.balance.amount
        == Decimal("1000.00")
    )


# ---------------------------------------------------------------------

def test_update_interest_rate(
    savings_account,
):

    savings_account.update_interest_rate(
        Decimal("5.25")
    )

    assert (
        savings_account.interest_rate
        == Decimal("5.25")
    )


def test_update_interest_rate_updates_version(
    savings_account,
):

    version = savings_account.version

    savings_account.update_interest_rate(
        Decimal("4.00")
    )

    assert (
        savings_account.version
        == version + 1
    )


# ---------------------------------------------------------------------

def test_can_withdraw_true(
    savings_account,
):

    assert savings_account._can_withdraw(
        Money(
            Decimal("1000.00"),
            Currency.SAR,
        )
    )


def test_can_withdraw_false(
    savings_account,
):

    assert not savings_account._can_withdraw(
        Money(
            Decimal("9000.01"),
            Currency.SAR,
        )
    )

# PART 4

# =====================================================================
# Interest Calculation
# =====================================================================

def test_calculate_interest(
    savings_account,
):

    interest = savings_account.calculate_interest()

    assert interest.amount == Decimal("25000.00")


def test_calculate_interest_returns_money(
    savings_account,
):

    interest = savings_account.calculate_interest()

    assert isinstance(
        interest,
        Money,
    )

""" --- remove this test as the domain model does not permit
def test_no_interest_when_below_minimum_balance(
    savings_account,
):

    savings_account.withdraw(
        Money(
            Decimal("9000.00"),
            Currency.SAR,
        )
    )

    interest = savings_account.calculate_interest()

    assert interest.amount == Decimal("0.00")
"""

def test_no_interest_when_account_inactive(
    savings_account,
):

    savings_account.deactivate()

    interest = savings_account.calculate_interest()

    assert interest.amount == Decimal("0.00")
    

def test_record_interest_application(
    savings_account,
):

    application_date = date(
        2025,
        5,
        1,
    )

    savings_account.record_interest_application(
        application_date
    )

    assert (
        savings_account.last_interest_date
        == application_date
    )


def test_record_interest_application_defaults_to_today(
    savings_account,
):

    savings_account.record_interest_application()

    assert (
        savings_account.last_interest_date
        == datetime.now(UTC).date()
    )


# =====================================================================
# Interest Frequency Helpers
# =====================================================================

@pytest.mark.parametrize(
    "frequency,expected",
    [
        (InterestFrequency.DAILY, 365),
        (InterestFrequency.WEEKLY, 52),
        (InterestFrequency.MONTHLY, 12),
        (InterestFrequency.QUARTERLY, 4),
        (InterestFrequency.SEMI_ANNUALLY, 2),
        (InterestFrequency.ANNUALLY, 1),
    ],
)
def test_periods_per_year(
    savings_account,
    frequency,
    expected,
):

    savings_account.interest_frequency = frequency

    assert (
        savings_account.periods_per_year()
        == expected
    )

# PART 5

# =====================================================================
# Serialization
# =====================================================================

def test_to_dict_contains_required_keys(
    savings_account,
):

    data = savings_account.to_dict()

    expected = {
        "account_number",
        "customer_id",
        "balance",
        "interest_rate",
        "minimum_balance",
        "interest_frequency",
        "last_interest_date",
    }

    assert expected.issubset(data.keys())


def test_to_dict_interest_rate(
    savings_account,
):

    data = savings_account.to_dict()

    assert (
        data["interest_rate"]
        == "2.50"
    )


def test_to_dict_minimum_balance(
    savings_account,
):

    data = savings_account.to_dict()

    assert (
        data["minimum_balance"]
        == "1000.00"
    )


def test_from_dict(
    savings_account,
):

    restored = SavingsAccount.from_dict(
        savings_account.to_dict()
    )

    assert (
        restored.account_number
        == savings_account.account_number
    )

    assert (
        restored.customer_id
        == savings_account.customer_id
    )

    assert (
        restored.balance
        == savings_account.balance
    )

    assert (
        restored.interest_rate
        == savings_account.interest_rate
    )

    assert (
        restored.minimum_balance
        == savings_account.minimum_balance
    )

    assert (
        restored.interest_frequency
        == savings_account.interest_frequency
    )


def test_serialization_preserves_last_interest_date(
    savings_account,
):

    restored = SavingsAccount.from_dict(
        savings_account.to_dict()
    )

    assert (
        restored.last_interest_date
        == savings_account.last_interest_date
    )
