from __future__ import annotations

from datetime import UTC, date, datetime, timedelta
from decimal import Decimal

import pytest

from exceptions.banking_exceptions import ValidationError

from models.time_deposit_account import (
    TimeDepositAccount,
)
from models.value_objects.money import Money
from utils.constants import (
    AccountStatus,
    AccountType,
    Currency,
)


# ==========================================================
# Fixtures
# ==========================================================

@pytest.fixture
def opening_balance():

    return Money(
        Decimal("10000.00"),
        Currency.SAR,
    )


@pytest.fixture
def principal():

    return Money(
        Decimal("10000.00"),
        Currency.SAR,
    )


@pytest.fixture
def time_deposit_account(
    opening_balance,
):

    return TimeDepositAccount(
        account_number="TD-300001",
        customer_id="CUST000001",
        opening_balance=opening_balance,
        interest_rate=Decimal("0.05"),
        term_months=12,
        early_withdrawal_penalty_rate=Decimal("0.10"),
        currency=Currency.SAR,
        auto_renew=False,
    )


@pytest.fixture
def matured_time_deposit():

    return TimeDepositAccount(
        account_number="TD-300002",
        customer_id="CUST000002",
        opening_balance=Money(
            Decimal("10000.00"),
            Currency.SAR,
        ),
        interest_rate=Decimal("0.05"),
        term_months=12,
        early_withdrawal_penalty_rate=Decimal("0.10"),
        currency=Currency.SAR,
        auto_renew=False,
        opened_date=date(2024, 1, 1),
    )


# ==========================================================
# Constructor
# ==========================================================

def test_constructor(
    time_deposit_account,
):

    assert (
        time_deposit_account.account_number
        == "TD-300001"
    )

    assert (
        time_deposit_account.customer_id
        == "CUST000001"
    )

    assert (
        time_deposit_account.account_type
        == AccountType.TIME_DEPOSIT
    )


def test_default_balance(
    time_deposit_account,
):

    assert (
        time_deposit_account.balance.amount
        == Decimal("10000.00")
    )


def test_default_principal(
    time_deposit_account,
):

    assert (
        time_deposit_account.principal.amount
        == Decimal("10000.00")
    )


def test_default_interest_rate(
    time_deposit_account,
):

    assert (
        time_deposit_account.interest_rate
        == Decimal("0.05")
    )


def test_default_term_months(
    time_deposit_account,
):

    assert (
        time_deposit_account.term_months
        == 12
    )


def test_default_term_days(
    time_deposit_account,
):

    assert (
        time_deposit_account.term_days
        == 360
    )


def test_default_penalty_rate(
    time_deposit_account,
):

    assert (
        time_deposit_account
        .early_withdrawal_penalty_rate
        == Decimal("0.10")
    )


def test_default_auto_renew(
    time_deposit_account,
):

    assert (
        time_deposit_account.auto_renew
        is False
    )


def test_default_status(
    time_deposit_account,
):

    assert (
        time_deposit_account.status
        == AccountStatus.ACTIVE
    )


def test_default_last_interest_date(
    time_deposit_account,
):

    assert (
        time_deposit_account.last_interest_date
        == date.today()
    )


def test_default_opened_date(
    time_deposit_account,
):

    assert (
        time_deposit_account.opened_date
        == date.today()
    )


def test_principal_equals_opening_balance(
    time_deposit_account,
):

    assert (
        time_deposit_account.principal
        == time_deposit_account.balance
    )


def test_account_is_active(
    time_deposit_account,
):

    assert (
        time_deposit_account.is_active_account
    )


def test_default_not_using_overdraft(
    time_deposit_account,
):

    assert (
        time_deposit_account.balance.amount
        > Decimal("0.00")
    )


# PART 2

# ==========================================================
# Property Validation
# ==========================================================

def test_change_interest_rate(
    time_deposit_account,
):

    version = time_deposit_account.version

    time_deposit_account.interest_rate = Decimal("0.08")

    assert (
        time_deposit_account.interest_rate
        == Decimal("0.08")
    )

    assert (
        time_deposit_account.version
        == version + 1
    )


def test_interest_rate_cannot_be_negative(
    time_deposit_account,
):

    with pytest.raises(ValueError):

        time_deposit_account.interest_rate = (
            Decimal("-0.01")
        )


def test_interest_rate_must_be_decimal(
    time_deposit_account,
):

    with pytest.raises(TypeError):

        time_deposit_account.interest_rate = 0.05


# ----------------------------------------------------------


def test_change_term_months(
    time_deposit_account,
):

    version = time_deposit_account.version

    time_deposit_account.term_months = 24

    assert (
        time_deposit_account.term_months
        == 24
    )

    assert (
        time_deposit_account.version
        == version + 1
    )


def test_term_months_must_be_integer(
    time_deposit_account,
):

    with pytest.raises(TypeError):

        time_deposit_account.term_months = "12"


def test_term_months_cannot_be_zero(
    time_deposit_account,
):

    with pytest.raises(ValueError):

        time_deposit_account.term_months = 0


def test_term_months_cannot_be_negative(
    time_deposit_account,
):

    with pytest.raises(ValueError):

        time_deposit_account.term_months = -6


# ----------------------------------------------------------


def test_enable_auto_renew(
    time_deposit_account,
):

    version = time_deposit_account.version

    time_deposit_account.auto_renew = True

    assert (
        time_deposit_account.auto_renew
        is True
    )

    assert (
        time_deposit_account.version
        == version + 1
    )


def test_disable_auto_renew(
    time_deposit_account,
):

    time_deposit_account.auto_renew = False

    assert (
        time_deposit_account.auto_renew
        is False
    )


def test_auto_renew_must_be_boolean(
    time_deposit_account,
):

    with pytest.raises(TypeError):

        time_deposit_account.auto_renew = "yes"


# ----------------------------------------------------------


def test_change_penalty_rate(
    time_deposit_account,
):

    version = time_deposit_account.version

    time_deposit_account.early_withdrawal_penalty_rate = (
        Decimal("0.20")
    )

    assert (
        time_deposit_account
        .early_withdrawal_penalty_rate
        == Decimal("0.20")
    )

    assert (
        time_deposit_account.version
        == version + 1
    )


def test_penalty_rate_cannot_be_negative(
    time_deposit_account,
):

    with pytest.raises(ValueError):

        time_deposit_account.early_withdrawal_penalty_rate = (
            Decimal("-0.01")
        )


def test_penalty_rate_cannot_exceed_one(
    time_deposit_account,
):

    with pytest.raises(ValueError):

        time_deposit_account.early_withdrawal_penalty_rate = (
            Decimal("1.01")
        )


def test_penalty_rate_must_be_decimal(
    time_deposit_account,
):

    with pytest.raises(TypeError):

        time_deposit_account.early_withdrawal_penalty_rate = (
            "0.10"
        )


# ----------------------------------------------------------


def test_change_last_interest_date(
    time_deposit_account,
):

    version = time_deposit_account.version

    previous = date(
        2025,
        1,
        1,
    )

    time_deposit_account.last_interest_date = (
        previous
    )

    assert (
        time_deposit_account.last_interest_date
        == previous
    )

    assert (
        time_deposit_account.version
        == version + 1
    )


def test_last_interest_date_cannot_be_future(
    time_deposit_account,
):

    future = (
        date.today()
        + timedelta(days=30)
    )

    with pytest.raises(ValidationError):

        time_deposit_account.last_interest_date = (
            future
        )


# ----------------------------------------------------------
# Computed Properties
# ----------------------------------------------------------

def test_term_days_updates_when_term_changes(
    time_deposit_account,
):

    time_deposit_account.term_months = 18

    assert (
        time_deposit_account.term_days
        == 540
    )


def test_maturity_date_is_date(
    time_deposit_account,
):

    assert isinstance(
        time_deposit_account.maturity_date,
        date,
    )


def test_maturity_date_after_opened_date(
    time_deposit_account,
):

    assert (
        time_deposit_account.maturity_date
        > time_deposit_account.opened_date
    )

# PART 3

# ==========================================================
# Business Rules
# ==========================================================

def test_account_not_matured_by_default(
    time_deposit_account,
):

    assert not time_deposit_account.is_matured()


def test_account_is_matured_when_opened_long_ago():

    account = TimeDepositAccount(
        account_number="TD-200002",
        customer_id="CUST000002",
        opening_balance=Money(
            Decimal("10000.00"),
            Currency.SAR,
        ),
        interest_rate=Decimal("0.05"),
        term_months=12,
        early_withdrawal_penalty_rate=Decimal("0.10"),
        currency=Currency.SAR,
        opened_date=date(
            2020,
            1,
            1,
        ),
    )

    assert account.is_matured()


# ----------------------------------------------------------


def test_can_close_false_before_maturity(
    time_deposit_account,
):

    assert not time_deposit_account.can_close()


def test_can_close_true_after_maturity():

    account = TimeDepositAccount(
        account_number="TD-200003",
        customer_id="CUST000003",
        opening_balance=Money(
            Decimal("10000.00"),
            Currency.SAR,
        ),
        interest_rate=Decimal("0.05"),
        term_months=6,
        early_withdrawal_penalty_rate=Decimal("0.10"),
        currency=Currency.SAR,
        opened_date=date(
            2020,
            1,
            1,
        ),
    )

    assert account.can_close()


# ----------------------------------------------------------


def test_cannot_withdraw_before_maturity(
    time_deposit_account,
):

    with pytest.raises(ValueError):

        time_deposit_account.withdraw(
            Money(
                Decimal("1000.00"),
                Currency.SAR,
            )
        )


def test_can_withdraw_after_maturity():

    account = TimeDepositAccount(
        account_number="TD-200004",
        customer_id="CUST000004",
        opening_balance=Money(
            Decimal("10000.00"),
            Currency.SAR,
        ),
        interest_rate=Decimal("0.05"),
        term_months=6,
        early_withdrawal_penalty_rate=Decimal("0.10"),
        currency=Currency.SAR,
        opened_date=date(
            2020,
            1,
            1,
        ),
    )

    account.withdraw(
        Money(
            Decimal("1000.00"),
            Currency.SAR,
        )
    )

    assert (
        account.balance.amount
        == Decimal("9000.00")
    )


def test_cannot_withdraw_more_than_balance_after_maturity():

    account = TimeDepositAccount(
        account_number="TD-200005",
        customer_id="CUST000005",
        opening_balance=Money(
            Decimal("10000.00"),
            Currency.SAR,
        ),
        interest_rate=Decimal("0.05"),
        term_months=6,
        early_withdrawal_penalty_rate=Decimal("0.10"),
        currency=Currency.SAR,
        opened_date=date(
            2020,
            1,
            1,
        ),
    )

    with pytest.raises(ValueError):

        account.withdraw(
            Money(
                Decimal("20000.00"),
                Currency.SAR,
            )
        )


# ----------------------------------------------------------


def test_principal_remains_original_after_withdrawal():

    account = TimeDepositAccount(
        account_number="TD-200006",
        customer_id="CUST000006",
        opening_balance=Money(
            Decimal("10000.00"),
            Currency.SAR,
        ),
        interest_rate=Decimal("0.05"),
        term_months=6,
        early_withdrawal_penalty_rate=Decimal("0.10"),
        currency=Currency.SAR,
        opened_date=date(
            2020,
            1,
            1,
        ),
    )

    account.withdraw(
        Money(
            Decimal("1000.00"),
            Currency.SAR,
        )
    )

    assert (
        account.principal.amount
        == Decimal("10000.00")
    )

    assert (
        account.balance.amount
        == Decimal("9000.00")
    )


# ----------------------------------------------------------


def test_balance_changes_but_principal_does_not():

    account = TimeDepositAccount(
        account_number="TD-200007",
        customer_id="CUST000007",
        opening_balance=Money(
            Decimal("10000.00"),
            Currency.SAR,
        ),
        interest_rate=Decimal("0.05"),
        term_months=12,
        early_withdrawal_penalty_rate=Decimal("0.10"),
        currency=Currency.SAR,
        opened_date=date(
            2020,
            1,
            1,
        ),
    )

    account.deposit(
        Money(
            Decimal("500.00"),
            Currency.SAR,
        )
    )

    assert (
        account.balance.amount
        == Decimal("10500.00")
    )

    assert (
        account.principal.amount
        == Decimal("10000.00")
    )


# ----------------------------------------------------------


def test_maturity_date_after_opening_date(
    time_deposit_account,
):

    assert (
        time_deposit_account.maturity_date
        > time_deposit_account.opened_date
    )


def test_term_days_matches_term_months(
    time_deposit_account,
):

    assert (
        time_deposit_account.term_days
        == time_deposit_account.term_months * 30
    )

# PART 4

# ==========================================================
# Interest & Penalty Calculations
# ==========================================================

def test_calculate_interest(
    time_deposit_account,
):

    interest = (
        time_deposit_account.calculate_interest()
    )

    expected = (
        Decimal("10000.00")
        * Decimal("0.05")
        * Decimal("12")
        / Decimal("12")
    )

    assert (
        interest.amount
        == expected.quantize(
            Decimal("0.01")
        )
    )

    assert (
        interest.currency
        == Currency.SAR
    )


# ----------------------------------------------------------


def test_calculate_maturity_value(
    time_deposit_account,
):

    maturity_value = (
        time_deposit_account
        .calculate_maturity_value()
    )

    expected = (
        Decimal("10000.00")
        + Decimal("500.00")
    )

    assert (
        maturity_value.amount
        == expected
    )


# ----------------------------------------------------------


def test_calculate_early_withdrawal_penalty_before_maturity(
    time_deposit_account,
):

    penalty = (
        time_deposit_account
        .calculate_early_withdrawal_penalty()
    )

    expected = (
        Decimal("10000.00")
        * Decimal("0.10")
    )

    assert (
        penalty.amount
        == expected.quantize(
            Decimal("0.01")
        )
    )


def test_apply_early_withdrawal_penalty_returns_same_value(
    time_deposit_account,
):

    penalty = (
        time_deposit_account
        .apply_early_withdrawal_penalty()
    )

    expected = (
        Decimal("10000.00")
        * Decimal("0.10")
    )

    assert (
        penalty.amount
        == expected.quantize(
            Decimal("0.01")
        )
    )


# ----------------------------------------------------------


def test_no_penalty_after_maturity():

    account = TimeDepositAccount(
        account_number="TD-300001",
        customer_id="CUST300001",
        opening_balance=Money(
            Decimal("10000.00"),
            Currency.SAR,
        ),
        interest_rate=Decimal("0.05"),
        term_months=6,
        early_withdrawal_penalty_rate=Decimal("0.10"),
        currency=Currency.SAR,
        opened_date=date(
            2020,
            1,
            1,
        ),
    )

    penalty = (
        account.calculate_early_withdrawal_penalty()
    )

    assert (
        penalty.amount
        == Decimal("0.00")
    )


def test_apply_penalty_after_maturity_returns_zero():

    account = TimeDepositAccount(
        account_number="TD-300002",
        customer_id="CUST300002",
        opening_balance=Money(
            Decimal("10000.00"),
            Currency.SAR,
        ),
        interest_rate=Decimal("0.05"),
        term_months=6,
        early_withdrawal_penalty_rate=Decimal("0.10"),
        currency=Currency.SAR,
        opened_date=date(
            2020,
            1,
            1,
        ),
    )

    penalty = (
        account.apply_early_withdrawal_penalty()
    )

    assert (
        penalty.amount
        == Decimal("0.00")
    )


# ----------------------------------------------------------


def test_interest_does_not_modify_balance(
    time_deposit_account,
):

    balance = (
        time_deposit_account.balance.amount
    )

    _ = time_deposit_account.calculate_interest()

    assert (
        time_deposit_account.balance.amount
        == balance
    )


def test_maturity_value_does_not_modify_balance(
    time_deposit_account,
):

    balance = (
        time_deposit_account.balance.amount
    )

    _ = (
        time_deposit_account
        .calculate_maturity_value()
    )

    assert (
        time_deposit_account.balance.amount
        == balance
    )


def test_penalty_does_not_modify_balance(
    time_deposit_account,
):

    balance = (
        time_deposit_account.balance.amount
    )

    _ = (
        time_deposit_account
        .calculate_early_withdrawal_penalty()
    )

    assert (
        time_deposit_account.balance.amount
        == balance
    )


# ----------------------------------------------------------


def test_interest_returns_money(
    time_deposit_account,
):

    interest = (
        time_deposit_account.calculate_interest()
    )

    assert isinstance(
        interest,
        Money,
    )


def test_maturity_value_returns_money(
    time_deposit_account,
):

    value = (
        time_deposit_account
        .calculate_maturity_value()
    )

    assert isinstance(
        value,
        Money,
    )


def test_penalty_returns_money(
    time_deposit_account,
):

    penalty = (
        time_deposit_account
        .calculate_early_withdrawal_penalty()
    )

    assert isinstance(
        penalty,
        Money,
    )

# PART 5

# ==========================================================
# Administrative Operations
# ==========================================================

def test_update_interest_rate(
    time_deposit_account,
):

    version = time_deposit_account.version

    time_deposit_account.update_interest_rate(
        Decimal("0.08")
    )

    assert (
        time_deposit_account.interest_rate
        == Decimal("0.08")
    )

    assert (
        time_deposit_account.version
        == version + 1
    )


# ----------------------------------------------------------


def test_update_penalty_rate(
    time_deposit_account,
):

    version = time_deposit_account.version

    time_deposit_account.update_penalty_rate(
        Decimal("0.20")
    )

    assert (
        time_deposit_account
        .early_withdrawal_penalty_rate
        == Decimal("0.20")
    )

    assert (
        time_deposit_account.version
        == version + 1
    )


# ----------------------------------------------------------


def test_update_auto_renew_true(
    time_deposit_account,
):

    version = time_deposit_account.version

    time_deposit_account.update_auto_renew(
        True,
    )

    assert (
        time_deposit_account.auto_renew
        is True
    )

    assert (
        time_deposit_account.version
        == version + 1
    )


def test_update_auto_renew_false(
    time_deposit_account,
):

    time_deposit_account.update_auto_renew(
        True,
    )

    version = time_deposit_account.version

    time_deposit_account.update_auto_renew(
        False,
    )

    assert (
        time_deposit_account.auto_renew
        is False
    )

    assert (
        time_deposit_account.version
        == version + 1
    )


# ----------------------------------------------------------


def test_record_interest_application_today(
    time_deposit_account,
):

    time_deposit_account.record_interest_application()

    assert (
        time_deposit_account.last_interest_date
        == date.today()
    )


def test_record_interest_application_specific_date(
    time_deposit_account,
):

    application_date = date(
        2025,
        6,
        30,
    )

    time_deposit_account.record_interest_application(
        application_date,
    )

    assert (
        time_deposit_account.last_interest_date
        == application_date
    )


# ----------------------------------------------------------


def test_update_interest_rate_invalid_value(
    time_deposit_account,
):

    with pytest.raises(ValueError):

        time_deposit_account.update_interest_rate(
            Decimal("-0.01")
        )


def test_update_penalty_rate_invalid_value(
    time_deposit_account,
):

    with pytest.raises(ValueError):

        time_deposit_account.update_penalty_rate(
            Decimal("1.50")
        )


def test_update_auto_renew_invalid_type(
    time_deposit_account,
):

    with pytest.raises(TypeError):

        time_deposit_account.update_auto_renew(
            "yes",
        )


# ----------------------------------------------------------


def test_record_interest_application_increments_version(
    time_deposit_account,
):

    version = time_deposit_account.version

    time_deposit_account.record_interest_application()

    assert (
        time_deposit_account.version
        == version + 1
    )

# PART 6

# ==========================================================
# Serialization
# ==========================================================

def test_to_dict_returns_dictionary(
    time_deposit_account,
):

    data = time_deposit_account.to_dict()

    assert isinstance(
        data,
        dict,
    )


# ----------------------------------------------------------


def test_to_dict_contains_expected_values(
    time_deposit_account,
):

    data = time_deposit_account.to_dict()

    assert data["account_number"] == "TD-300001"
    assert data["customer_id"] == "CUST000001"
    assert data["account_type"] == AccountType.TIME_DEPOSIT.value

    assert data["principal"] == "10000.00"
    assert data["balance"] == "10000.00"

    assert data["interest_rate"] == "0.05"
    assert data["term_months"] == 12

    assert data["auto_renew"] is False

    assert (
        data["early_withdrawal_penalty_rate"]
        == "0.10"
    )

    assert (
        data["last_interest_date"]
        == time_deposit_account.last_interest_date.isoformat()
    )


# ----------------------------------------------------------


def test_from_dict_returns_time_deposit_account(
    time_deposit_account,
):

    data = time_deposit_account.to_dict()

    restored = TimeDepositAccount.from_dict(
        data,
    )

    assert isinstance(
        restored,
        TimeDepositAccount,
    )


# ----------------------------------------------------------


def test_from_dict_restores_basic_fields(
    time_deposit_account,
):

    restored = TimeDepositAccount.from_dict(
        time_deposit_account.to_dict(),
    )

    assert restored.account_number == time_deposit_account.account_number
    assert restored.customer_id == time_deposit_account.customer_id

    assert restored.account_type == AccountType.TIME_DEPOSIT

    assert restored.currency == Currency.SAR


# ----------------------------------------------------------


def test_from_dict_restores_principal(
    time_deposit_account,
):

    restored = TimeDepositAccount.from_dict(
        time_deposit_account.to_dict(),
    )

    assert (
        restored.principal
        == time_deposit_account.principal
    )


def test_from_dict_restores_balance(
    time_deposit_account,
):

    restored = TimeDepositAccount.from_dict(
        time_deposit_account.to_dict(),
    )

    assert (
        restored.balance
        == time_deposit_account.balance
    )


# ----------------------------------------------------------


def test_from_dict_restores_interest_rate(
    time_deposit_account,
):

    restored = TimeDepositAccount.from_dict(
        time_deposit_account.to_dict(),
    )

    assert (
        restored.interest_rate
        == time_deposit_account.interest_rate
    )


def test_from_dict_restores_term(
    time_deposit_account,
):

    restored = TimeDepositAccount.from_dict(
        time_deposit_account.to_dict(),
    )

    assert (
        restored.term_months
        == time_deposit_account.term_months
    )


def test_from_dict_restores_penalty_rate(
    time_deposit_account,
):

    restored = TimeDepositAccount.from_dict(
        time_deposit_account.to_dict(),
    )

    assert (
        restored.early_withdrawal_penalty_rate
        ==
        time_deposit_account
        .early_withdrawal_penalty_rate
    )


def test_from_dict_restores_auto_renew(
    time_deposit_account,
):

    restored = TimeDepositAccount.from_dict(
        time_deposit_account.to_dict(),
    )

    assert (
        restored.auto_renew
        == time_deposit_account.auto_renew
    )


def test_from_dict_restores_last_interest_date(
    time_deposit_account,
):

    restored = TimeDepositAccount.from_dict(
        time_deposit_account.to_dict(),
    )

    assert (
        restored.last_interest_date
        ==
        time_deposit_account
        .last_interest_date
    )


# ----------------------------------------------------------


def test_to_dict_round_trip(
    time_deposit_account,
):

    first = time_deposit_account.to_dict()

    restored = TimeDepositAccount.from_dict(
        first,
    )

    second = restored.to_dict()

    assert first == second

# PART 7

# ==========================================================
# Part 7 - Edge Cases & Final Coverage
# ==========================================================

def test_update_interest_rate(
    time_deposit_account,
):

    version = time_deposit_account.version

    time_deposit_account.update_interest_rate(
        Decimal("0.075")
    )

    assert (
        time_deposit_account.interest_rate
        == Decimal("0.075")
    )

    assert (
        time_deposit_account.version
        == version + 1
    )


# ----------------------------------------------------------


def test_update_penalty_rate(
    time_deposit_account,
):

    version = time_deposit_account.version

    time_deposit_account.update_penalty_rate(
        Decimal("0.15")
    )

    assert (
        time_deposit_account
        .early_withdrawal_penalty_rate
        == Decimal("0.15")
    )

    assert (
        time_deposit_account.version
        == version + 1
    )


# ----------------------------------------------------------


def test_update_auto_renew_true(
    time_deposit_account,
):

    version = time_deposit_account.version

    time_deposit_account.update_auto_renew(
        True,
    )

    assert (
        time_deposit_account.auto_renew
        is True
    )

    assert (
        time_deposit_account.version
        == version + 1
    )


# ----------------------------------------------------------


def test_update_auto_renew_false(
    time_deposit_account,
):

    time_deposit_account.auto_renew = True

    version = time_deposit_account.version

    time_deposit_account.update_auto_renew(
        False,
    )

    assert (
        time_deposit_account.auto_renew
        is False
    )

    assert (
        time_deposit_account.version
        == version + 1
    )


# ----------------------------------------------------------


def test_record_interest_application_default(
    time_deposit_account,
):

    today = date.today()

    time_deposit_account.record_interest_application()

    assert (
        time_deposit_account.last_interest_date
        == today
    )


# ----------------------------------------------------------


def test_record_interest_application_specific_date(
    time_deposit_account,
):

    application_date = date(
        2025,
        6,
        30,
    )

    time_deposit_account.record_interest_application(
        application_date,
    )

    assert (
        time_deposit_account.last_interest_date
        == application_date
    )


# ----------------------------------------------------------


def test_maturity_value_greater_than_principal(
    time_deposit_account,
):

    assert (
        time_deposit_account
        .calculate_maturity_value()
        >
        time_deposit_account.principal
    )


# ----------------------------------------------------------


def test_zero_penalty_when_matured(
    matured_time_deposit,
):

    penalty = (
        matured_time_deposit
        .calculate_early_withdrawal_penalty()
    )

    assert penalty.amount == Decimal("0.00")


# ----------------------------------------------------------


def test_apply_penalty_returns_money(
    time_deposit_account,
):

    penalty = (
        time_deposit_account
        .apply_early_withdrawal_penalty()
    )

    assert isinstance(
        penalty,
        Money,
    )


# ----------------------------------------------------------


def test_can_close_after_maturity(
    matured_time_deposit,
):

    assert (
        matured_time_deposit
        .can_close()
    )


# ----------------------------------------------------------


def test_cannot_close_before_maturity(
    time_deposit_account,
):

    assert (
        not time_deposit_account.can_close()
    )


# ----------------------------------------------------------


def test_term_days_for_one_year(
    time_deposit_account,
):

    assert (
        time_deposit_account.term_days
        == 360
    )


# ----------------------------------------------------------


def test_interest_is_money(
    time_deposit_account,
):

    interest = (
        time_deposit_account
        .calculate_interest()
    )

    assert isinstance(
        interest,
        Money,
    )


# ----------------------------------------------------------


def test_maturity_value_is_money(
    time_deposit_account,
):

    value = (
        time_deposit_account
        .calculate_maturity_value()
    )

    assert isinstance(
        value,
        Money,
    )


# ----------------------------------------------------------


def test_penalty_is_money(
    time_deposit_account,
):

    penalty = (
        time_deposit_account
        .calculate_early_withdrawal_penalty()
    )

    assert isinstance(
        penalty,
        Money,
    )

# PART 8

# ==========================================================
# Part 8 - Boundary Conditions & Invariants
# ==========================================================

def test_principal_never_changes_after_interest_rate_update(
    time_deposit_account,
):

    original = time_deposit_account.principal

    time_deposit_account.update_interest_rate(
        Decimal("0.08")
    )

    assert (
        time_deposit_account.principal
        == original
    )


# ----------------------------------------------------------


def test_principal_never_changes_after_penalty_update(
    time_deposit_account,
):

    original = time_deposit_account.principal

    time_deposit_account.update_penalty_rate(
        Decimal("0.20")
    )

    assert (
        time_deposit_account.principal
        == original
    )


# ----------------------------------------------------------


def test_maturity_value_equals_principal_plus_interest(
    time_deposit_account,
):

    maturity = (
        time_deposit_account
        .calculate_maturity_value()
    )

    expected = (
        time_deposit_account.principal
        + time_deposit_account.calculate_interest()
    )

    assert maturity == expected


# ----------------------------------------------------------


def test_interest_is_non_negative(
    time_deposit_account,
):

    assert (
        time_deposit_account
        .calculate_interest()
        .amount
        >= Decimal("0.00")
    )


# ----------------------------------------------------------


def test_penalty_is_non_negative(
    time_deposit_account,
):

    assert (
        time_deposit_account
        .calculate_early_withdrawal_penalty()
        .amount
        >= Decimal("0.00")
    )


# ----------------------------------------------------------


def test_maturity_value_is_greater_or_equal_balance(
    time_deposit_account,
):

    assert (
        time_deposit_account
        .calculate_maturity_value()
        >= time_deposit_account.balance
    )


# ----------------------------------------------------------


def test_term_days_updates_with_term_change(
    time_deposit_account,
):

    time_deposit_account.term_months = 24

    assert (
        time_deposit_account.term_days
        == 720
    )


# ----------------------------------------------------------


def test_auto_renew_default_false(
    time_deposit_account,
):

    assert (
        time_deposit_account.auto_renew
        is False
    )


# ----------------------------------------------------------


def test_interest_rate_update_preserves_balance(
    time_deposit_account,
):

    balance = time_deposit_account.balance

    time_deposit_account.update_interest_rate(
        Decimal("0.09")
    )

    assert (
        time_deposit_account.balance
        == balance
    )


# ----------------------------------------------------------


def test_penalty_rate_update_preserves_balance(
    time_deposit_account,
):

    balance = time_deposit_account.balance

    time_deposit_account.update_penalty_rate(
        Decimal("0.30")
    )

    assert (
        time_deposit_account.balance
        == balance
    )


# ----------------------------------------------------------


def test_auto_renew_update_preserves_balance(
    time_deposit_account,
):

    balance = time_deposit_account.balance

    time_deposit_account.update_auto_renew(
        True,
    )

    assert (
        time_deposit_account.balance
        == balance
    )


# ----------------------------------------------------------


def test_to_dict_contains_all_expected_keys(
    time_deposit_account,
):

    data = time_deposit_account.to_dict()

    expected = {
        "account_number",
        "customer_id",
        "account_type",
        "currency",
        "balance",
        "opened_date",
        "principal",
        "interest_rate",
        "term_months",
        "auto_renew",
        "early_withdrawal_penalty_rate",
        "last_interest_date",
    }

    assert expected.issubset(
        data.keys()
    )

