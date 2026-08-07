from datetime import date
from decimal import Decimal

import pytest

from models.current_account import CurrentAccount
from models.value_objects.money import Money

from utils.constants import (
    AccountType,
    Currency,
)


@pytest.fixture
def opening_balance():

    return Money(
        Decimal("5000.00"),
        Currency.SAR,
    )


@pytest.fixture
def overdraft_limit():

    return Money(
        Decimal("2000.00"),
        Currency.SAR,
    )


@pytest.fixture
def maintenance_fee():

    return Money(
        Decimal("25.00"),
        Currency.SAR,
    )


@pytest.fixture
def overdraft_fee():

    return Money(
        Decimal("75.00"),
        Currency.SAR,
    )


@pytest.fixture
def current_account(
    opening_balance,
    overdraft_limit,
    maintenance_fee,
    overdraft_fee,
):

    return CurrentAccount(
        account_number="CA-300001",
        customer_id="CUST000001",
        opening_balance=opening_balance,
        overdraft_limit=overdraft_limit,
        maintenance_fee=maintenance_fee,
        overdraft_fee=overdraft_fee,
        currency=Currency.SAR,
    )

# PART 2

def test_constructor_sets_account_type(
    current_account,
):

    assert (
        current_account.account_type
        == AccountType.CURRENT
    )


def test_constructor_sets_overdraft_limit(
    current_account,
    overdraft_limit,
):

    assert (
        current_account.overdraft_limit
        == overdraft_limit
    )


def test_constructor_sets_maintenance_fee(
    current_account,
    maintenance_fee,
):

    assert (
        current_account.maintenance_fee
        == maintenance_fee
    )


def test_constructor_sets_overdraft_fee(
    current_account,
    overdraft_fee,
):

    assert (
        current_account.overdraft_fee
        == overdraft_fee
    )


def test_default_overdraft_enabled(
    current_account,
):

    assert current_account.overdraft_enabled


def test_default_last_fee_date(
    current_account,
):

    assert (
        current_account.last_fee_date
        == date.today()
    )

# PART 3.1

def test_change_overdraft_limit(
    current_account,
):

    version = current_account.version

    new_limit = Money(
        Decimal("3000.00"),
        Currency.SAR,
    )

    current_account.overdraft_limit = new_limit

    assert (
        current_account.overdraft_limit
        == new_limit
    )

    assert current_account.version == version + 1


def test_invalid_overdraft_limit_type(
    current_account,
):

    with pytest.raises(TypeError):

        current_account.overdraft_limit = Decimal(
            "1000.00"
        )


def test_negative_overdraft_limit(
    current_account,
):

    with pytest.raises(ValueError):

        current_account.overdraft_limit = Money(
            Decimal("-1.00"),
            Currency.SAR,
        )


def test_overdraft_limit_currency_mismatch(
    current_account,
):

    with pytest.raises(ValueError):

        current_account.overdraft_limit = Money(
            Decimal("1000.00"),
            Currency.USD,
        )

# PART 3.2

def test_change_maintenance_fee(
    current_account,
):

    version = current_account.version

    fee = Money(
        Decimal("50.00"),
        Currency.SAR,
    )

    current_account.maintenance_fee = fee

    assert (
        current_account.maintenance_fee
        == fee
    )

    assert current_account.version == version + 1


def test_invalid_maintenance_fee_type(
    current_account,
):

    with pytest.raises(TypeError):

        current_account.maintenance_fee = Decimal(
            "25.00"
        )


def test_negative_maintenance_fee(
    current_account,
):

    with pytest.raises(ValueError):

        current_account.maintenance_fee = Money(
            Decimal("-5.00"),
            Currency.SAR,
        )


def test_maintenance_fee_currency_mismatch(
    current_account,
):

    with pytest.raises(ValueError):

        current_account.maintenance_fee = Money(
            Decimal("25.00"),
            Currency.USD,
        )


# PART 3.3

def test_change_overdraft_fee(
    current_account,
):

    version = current_account.version

    fee = Money(
        Decimal("100.00"),
        Currency.SAR,
    )

    current_account.overdraft_fee = fee

    assert (
        current_account.overdraft_fee
        == fee
    )

    assert current_account.version == version + 1


def test_invalid_overdraft_fee_type(
    current_account,
):

    with pytest.raises(TypeError):

        current_account.overdraft_fee = Decimal(
            "75.00"
        )


def test_negative_overdraft_fee(
    current_account,
):

    with pytest.raises(ValueError):

        current_account.overdraft_fee = Money(
            Decimal("-10.00"),
            Currency.SAR,
        )


def test_overdraft_fee_currency_mismatch(
    current_account,
):

    with pytest.raises(ValueError):

        current_account.overdraft_fee = Money(
            Decimal("10.00"),
            Currency.USD,
        )

# PART 3.4

def test_disable_overdraft(
    current_account,
):

    version = current_account.version

    current_account.overdraft_enabled = False

    assert not current_account.overdraft_enabled

    assert current_account.version == version + 1


def test_enable_overdraft(
    current_account,
):

    current_account.overdraft_enabled = False

    version = current_account.version

    current_account.overdraft_enabled = True

    assert current_account.overdraft_enabled

    assert current_account.version == version + 1


def test_invalid_overdraft_enabled_type(
    current_account,
):

    with pytest.raises(TypeError):

        current_account.overdraft_enabled = "Yes"

# PART 3.5

def test_change_last_fee_date(
    current_account,
):

    version = current_account.version

    previous = date(
        2025,
        1,
        1,
    )

    current_account.last_fee_date = previous

    assert (
        current_account.last_fee_date
        == previous
    )

    assert current_account.version == version + 1


def test_invalid_last_fee_date(
    current_account,
):

    with pytest.raises(Exception):

        current_account.last_fee_date = date(
            2100,
            1,
            1,
        )

# PART 4.1

def test_withdraw_within_balance(
    current_account,
):

    current_account.withdraw(
        Money(
            Decimal("1000.00"),
            Currency.SAR,
        )
    )

    assert (
        current_account.balance.amount
        == Decimal("4000.00")
    )

    assert (
        not current_account.is_using_overdraft()
    )

# PART 4.2

def test_withdraw_into_overdraft(
    current_account,
):

    current_account.withdraw(
        Money(
            Decimal("6000.00"),
            Currency.SAR,
        )
    )

    assert (
        current_account.balance.amount
        == Decimal("-1000.00")
    )

    assert current_account.is_using_overdraft()

# PART 4.3

def test_withdraw_to_overdraft_limit(
    current_account,
):

    current_account.withdraw(
        Money(
            Decimal("7000.00"),
            Currency.SAR,
        )
    )

    assert (
        current_account.balance.amount
        == Decimal("-2000.00")
    )

    assert (
        current_account.is_using_overdraft()
    )

    assert (
        current_account.remaining_overdraft().amount
        == Decimal("0.00")
    )

# PART 4.4

def test_withdraw_beyond_overdraft_limit(
    current_account,
):

    with pytest.raises(ValueError):

        current_account.withdraw(
            Money(
                Decimal("7000.01"),
                Currency.SAR,
            )
        )

# PART 4.5

def test_withdraw_when_overdraft_disabled(
    current_account,
):

    current_account.overdraft_enabled = False

    with pytest.raises(ValueError):

        current_account.withdraw(
            Money(
                Decimal("6000.00"),
                Currency.SAR,
            )
        )

# PART 4.6

def test_deposit_reduces_overdraft(
    current_account,
):

    current_account.withdraw(
        Money(
            Decimal("6000.00"),
            Currency.SAR,
        )
    )

    current_account.deposit(
        Money(
            Decimal("500.00"),
            Currency.SAR,
        )
    )

    assert (
        current_account.balance.amount
        == Decimal("-500.00")
    )

    assert (
        current_account.is_using_overdraft()
    )

# PART 4.7

def test_deposit_clears_overdraft(
    current_account,
):

    current_account.withdraw(
        Money(
            Decimal("6000.00"),
            Currency.SAR,
        )
    )

    current_account.deposit(
        Money(
            Decimal("1500.00"),
            Currency.SAR,
        )
    )

    assert (
        current_account.balance.amount
        == Decimal("500.00")
    )

    assert (
        not current_account.is_using_overdraft()
    )

# PART 4.8

def test_multiple_withdrawals_within_limit(
    current_account,
):

    current_account.withdraw(
        Money(
            Decimal("3000.00"),
            Currency.SAR,
        )
    )

    current_account.withdraw(
        Money(
            Decimal("3000.00"),
            Currency.SAR,
        )
    )

    assert (
        current_account.balance.amount
        == Decimal("-1000.00")
    )

    assert (
        current_account.is_using_overdraft()
    )

# PART 4.9

def test_multiple_withdrawals_exceed_limit(
    current_account,
):

    current_account.withdraw(
        Money(
            Decimal("6000.00"),
            Currency.SAR,
        )
    )

    with pytest.raises(ValueError):

        current_account.withdraw(
            Money(
                Decimal("1500.00"),
                Currency.SAR,
            )
        )

# PART 4.10

def test_deposit_restores_remaining_overdraft(
    current_account,
):

    current_account.withdraw(
        Money(
            Decimal("6500.00"),
            Currency.SAR,
        )
    )

    assert (
        current_account.remaining_overdraft().amount
        == Decimal("500.00")
    )

    current_account.deposit(
        Money(
            Decimal("300.00"),
            Currency.SAR,
        )
    )

    assert (
        current_account.remaining_overdraft().amount
        == Decimal("800.00")
    )

# PART 5.1

def test_is_using_overdraft_false(
    current_account,
):

    assert (
        not current_account.is_using_overdraft()
    )


def test_is_using_overdraft_true(
    current_account,
):

    current_account.withdraw(
        Money(
            Decimal("6000.00"),
            Currency.SAR,
        )
    )

    assert (
        current_account.is_using_overdraft()
    )

# PART 5.2


def test_available_funds(
    current_account,
):

    funds = current_account.available_funds()

    assert (
        funds.amount
        == Decimal("7000.00")
    )

    assert (
        funds.currency
        == Currency.SAR
    )

def test_available_funds_after_overdraft(
    current_account,
):

    current_account.withdraw(
        Money(
            Decimal("6000.00"),
            Currency.SAR,
        )
    )

    funds = current_account.available_funds()

    assert (
        funds.amount
        == Decimal("1000.00")
    )

# PART 5.3

def test_remaining_overdraft_full(
    current_account,
):

    remaining = (
        current_account.remaining_overdraft()
    )

    assert (
        remaining.amount
        == Decimal("2000.00")
    )

def test_remaining_overdraft_partial(
    current_account,
):

    current_account.withdraw(
        Money(
            Decimal("6000.00"),
            Currency.SAR,
        )
    )

    remaining = (
        current_account.remaining_overdraft()
    )

    assert (
        remaining.amount
        == Decimal("1000.00")
    )

def test_remaining_overdraft_zero(
    current_account,
):

    current_account.withdraw(
        Money(
            Decimal("7000.00"),
            Currency.SAR,
        )
    )

    remaining = (
        current_account.remaining_overdraft()
    )

    assert (
        remaining.amount
        == Decimal("0.00")
    )

# PART 5.4

def test_has_available_overdraft_true(
    current_account,
):

    assert (
        current_account.has_available_overdraft()
    )

def test_has_available_overdraft_false(
    current_account,
):

    current_account.withdraw(
        Money(
            Decimal("7000.00"),
            Currency.SAR,
        )
    )

    assert (
        not current_account.has_available_overdraft()
    )

# PART 5.5

def test_update_overdraft_limit(
    current_account,
):

    limit = Money(
        Decimal("3000.00"),
        Currency.SAR,
    )

    current_account.update_overdraft_limit(
        limit
    )

    assert (
        current_account.overdraft_limit
        == limit
    )

def test_update_maintenance_fee(
    current_account,
):

    fee = Money(
        Decimal("50.00"),
        Currency.SAR,
    )

    current_account.update_maintenance_fee(
        fee
    )

    assert (
        current_account.maintenance_fee
        == fee
    )

def test_update_overdraft_fee(
    current_account,
):

    fee = Money(
        Decimal("100.00"),
        Currency.SAR,
    )

    current_account.update_overdraft_fee(
        fee
    )

    assert (
        current_account.overdraft_fee
        == fee
    )

# PART 5.6

def test_record_fee_application(
    current_account,
):

    application_date = date(
        2025,
        6,
        1,
    )

    current_account.record_fee_application(
        application_date
    )

    assert (
        current_account.last_fee_date
        == application_date
    )

def test_record_fee_application_default(
    current_account,
):

    current_account.record_fee_application()

    assert (
        current_account.last_fee_date
        == date.today()
    )

# PART 6.1

def test_calculate_maintenance_fee(
    current_account,
):

    fee = (
        current_account.calculate_maintenance_fee()
    )

    assert fee == current_account.maintenance_fee

# PART 6.2

def test_calculate_overdraft_fee_not_overdrawn(
    current_account,
):

    fee = (
        current_account.calculate_overdraft_fee()
    )

    assert fee.amount == Decimal("0.00")

    assert fee.currency == Currency.SAR

# PART 6.3

def test_calculate_overdraft_fee_overdrawn(
    current_account,
):

    current_account.withdraw(
        Money(
            Decimal("6000.00"),
            Currency.SAR,
        )
    )

    fee = (
        current_account.calculate_overdraft_fee()
    )

    assert fee == current_account.overdraft_fee

# PART 6.4

def test_calculate_total_fee_positive_balance(
    current_account,
):

    fee = current_account.calculate_fee()

    assert (
        fee.amount
        == current_account.maintenance_fee.amount
    )

    assert fee.currency == Currency.SAR


# PART 6.5

def test_calculate_total_fee_using_overdraft(
    current_account,
):

    current_account.withdraw(
        Money(
            Decimal("6000.00"),
            Currency.SAR,
        )
    )

    fee = current_account.calculate_fee()

    expected = (
        current_account.maintenance_fee.amount
        + current_account.overdraft_fee.amount
    )

    assert fee.amount == expected

    assert fee.currency == Currency.SAR

# PART 6.6

def test_fee_calculation_does_not_change_balance(
    current_account,
):

    original = current_account.balance

    current_account.calculate_fee()

    assert current_account.balance == original

# PART 6.7

def test_overdraft_fee_does_not_change_balance(
    current_account,
):

    current_account.withdraw(
        Money(
            Decimal("6000.00"),
            Currency.SAR,
        )
    )

    original = current_account.balance

    current_account.calculate_overdraft_fee()

    assert current_account.balance == original

# PART 6.8

def test_maintenance_fee_does_not_change_balance(
    current_account,
):

    original = current_account.balance

    current_account.calculate_maintenance_fee()

    assert current_account.balance == original

# PART 7.1

def test_to_dict_contains_required_keys(
    current_account,
):

    data = current_account.to_dict()

    expected = {
        "account_number",
        "customer_id",
        "account_type",
        "balance",
        "currency",
        "status",
        "opened_date",
        "closed_date",
        "overdraft_limit",
        "maintenance_fee",
        "overdraft_fee",
        "overdraft_enabled",
        "last_fee_date",
    }

    assert expected.issubset(data.keys())

# PART 7.2

def test_to_dict_values(
    current_account,
):

    data = current_account.to_dict()

    assert (
        data["account_number"]
        == "CA-300001"
    )

    assert (
        data["customer_id"]
        == "CUST000001"
    )

    assert (
        data["account_type"]
        == AccountType.CURRENT.value
    )

    assert (
        data["balance"]
        == "5000.00"
    )

    assert (
        data["currency"]
        == Currency.SAR.value
    )

    assert (
        data["overdraft_limit"]
        == "2000.00"
    )

    assert (
        data["maintenance_fee"]
        == "25.00"
    )

    assert (
        data["overdraft_fee"]
        == "75.00"
    )

    assert (
        data["overdraft_enabled"]
        is True
    )

# PART 7.3

def test_from_dict(
    current_account,
):

    data = current_account.to_dict()

    restored = (
        CurrentAccount.from_dict(data)
    )

    assert (
        restored.account_number
        == current_account.account_number
    )

    assert (
        restored.customer_id
        == current_account.customer_id
    )

    assert (
        restored.balance
        == current_account.balance
    )

    assert (
        restored.overdraft_limit
        == current_account.overdraft_limit
    )

    assert (
        restored.maintenance_fee
        == current_account.maintenance_fee
    )

    assert (
        restored.overdraft_fee
        == current_account.overdraft_fee
    )

    assert (
        restored.overdraft_enabled
        == current_account.overdraft_enabled
    )

    assert (
        restored.last_fee_date
        == current_account.last_fee_date
    )

# PART 7.4

def test_serialization_round_trip(
    current_account,
):

    restored = CurrentAccount.from_dict(
        current_account.to_dict()
    )

    assert (
        restored.to_dict()
        == current_account.to_dict()
    )

# PART 7.5

def test_entity_state_restored(
    current_account,
):

    current_account.touch()

    data = current_account.to_dict()

    restored = (
        CurrentAccount.from_dict(data)
    )

    assert (
        restored.entity_id
        == current_account.entity_id
    )

    assert (
        restored.created_at
        == current_account.created_at
    )

    assert (
        restored.updated_at
        == current_account.updated_at
    )

    assert (
        restored.version
        == current_account.version
    )

    assert (
        restored.is_active
        == current_account.is_active
    )

# PART 7.6

def test_to_dict_returns_new_dictionary(
    current_account,
):

    data1 = current_account.to_dict()
    data2 = current_account.to_dict()

    assert data1 is not data2
    assert data1 == data2
