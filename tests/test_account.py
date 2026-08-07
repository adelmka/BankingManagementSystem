"""
Unit tests for models.account.Account
"""

from __future__ import annotations

from datetime import UTC, date, datetime
from decimal import Decimal

import pytest

from models.account import Account
from models.value_objects.money import Money
from utils.constants import AccountStatus, AccountType, Currency


# =====================================================================
# Concrete Test Account
# =====================================================================

class ConcreteAccount(Account):
    """
    Minimal concrete implementation used for testing the Account
    abstract base class.
    """

    def to_dict(self) -> dict:

        return {
            "account_number": self.account_number,
            "customer_id": self.customer_id,
            "account_type": self.account_type.value,
            "status": self.status.value,
            "currency": self.currency,
            "balance": str(self.balance.amount),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ConcreteAccount":

        return cls(
            account_number=data["account_number"],
            customer_id=data["customer_id"],
            account_type=AccountType(data["account_type"]),
            opening_balance=Money(
                Decimal(data["balance"]),
                data["currency"],
            ),
            currency=data["currency"],
            status=AccountStatus(data["status"]),
        )


# =====================================================================
# Fixtures
# =====================================================================

@pytest.fixture
def opening_balance():

    return Money(
        Decimal("1000.00"),
        Currency.SAR,
    )

"""
@pytest.fixture
def zero_balance():

    return Money.zero(Currency.SAR)
"""

@pytest.fixture
def account(opening_balance):

    return ConcreteAccount(
        account_number="SA-100001",
        customer_id="CUST000001",
        account_type=AccountType.SAVINGS,
        opening_balance=opening_balance,
        currency=Currency.SAR,
    )

"""
@pytest.fixture
def zero_balance_account(zero_balance):

    return ConcreteAccount(
        account_number="SA-100002",
        customer_id="CUST000002",
        account_type=AccountType.SAVINGS,
        opening_balance=zero_balance,
        currency=Currency.SAR,
    )
"""

@pytest.fixture
def account_with_zero_balance():

    account = ConcreteAccount(
        account_number="SA-100002",
        customer_id="CUST000002",
        account_type=AccountType.SAVINGS,
        opening_balance=Money(
            Decimal("500.00"),
            Currency.SAR,
        ),
        currency=Currency.SAR,
    )

    account.withdraw(
        Money(
            Decimal("500.00"),
            Currency.SAR,
        )
    )

    return account

@pytest.fixture
def second_account():

    return ConcreteAccount(
        account_number="SA-100003",
        customer_id="CUST000003",
        account_type=AccountType.SAVINGS,
        opening_balance=Money(
            Decimal("500.00"),
            Currency.SAR,
        ),
        currency=Currency.SAR,
    )


# =====================================================================
# Constructor Tests
# =====================================================================

def test_create_account(account):

    assert account.account_number == "SA-100001"

    assert account.customer_id == "CUST000001"

    assert account.account_type == AccountType.SAVINGS

    assert account.balance.amount == Decimal("1000.00")

    assert account.currency == Currency.SAR

    assert account.status == AccountStatus.ACTIVE


def test_default_opened_date(account):

    assert account.opened_date == date.today()


def test_default_closed_date(account):

    assert account.closed_date is None


def test_default_transaction_list(account):

    assert len(account.transaction_ids) == 0


def test_default_version(account):

    assert account.version == 1


def test_default_is_active(account):

    assert account.is_active


def test_entity_id_created(account):

    assert account.entity_id is not None


def test_created_at_initialized(account):

    assert isinstance(account.created_at, datetime)


def test_updated_at_initialized(account):

    assert isinstance(account.updated_at, datetime)


def test_opening_balance_preserved(account):

    assert account.balance == Money(
        Decimal("1000.00"),
        Currency.SAR,
    )


def test_zero_balance_account_creation(account_with_zero_balance):

    assert account_with_zero_balance.balance.amount == Decimal("0.00")


def test_currency_stored(account):

    assert account.currency == Currency.SAR


def test_account_number_stored(account):

    assert account.account_number == "SA-100001"


def test_customer_id_stored(account):

    assert account.customer_id == "CUST000001"


def test_account_type_stored(account):

    assert account.account_type == AccountType.SAVINGS


# =====================================================================
# Opening Balance Tests
# =====================================================================


def test_zero_opening_balance_not_allowed():

    with pytest.raises(ValueError):

        ConcreteAccount(
            account_number="SA-100001",
            customer_id="CUST000001",
            account_type=AccountType.SAVINGS,
            opening_balance=Money(
                Decimal("0.00"),
                Currency.SAR,
            ),
            currency=Currency.SAR,
        )
        
    
# PART 2

# =====================================================================
# Property Tests
# =====================================================================

def test_balance_property(account):

    assert account.balance.amount == Decimal("1000.00")


def test_available_balance_property(account):

    assert account.available_balance == account.balance


def test_balance_amount_property(account):

    assert account.balance_amount == Decimal("1000.00")


def test_currency_property(account):

    assert account.currency == Currency.SAR


def test_status_property(account):

    assert account.status == AccountStatus.ACTIVE


def test_opened_date_property(account):

    assert account.opened_date == date.today()


def test_closed_date_property(account):

    assert account.closed_date is None


def test_transaction_ids_property(account):

    assert len(account.transaction_ids) == 0


def test_account_number_property(account):

    assert account.account_number == "SA-100001"


def test_customer_id_property(account):

    assert account.customer_id == "CUST000001"


def test_account_type_property(account):

    assert account.account_type == AccountType.SAVINGS


# =====================================================================
# Computed Property Tests
# =====================================================================

def test_has_positive_balance(account):

    assert account.has_positive_balance


def test_not_zero_balance(account):

    assert not account.is_zero_balance


def test_not_overdrawn(account):

    assert not account.is_overdrawn


def test_zero_balance_property(account_with_zero_balance):

    assert account_with_zero_balance.is_zero_balance


def test_zero_balance_not_positive(account_with_zero_balance):

    assert not account_with_zero_balance.has_positive_balance


def test_zero_balance_not_overdrawn(account_with_zero_balance):

    assert not account_with_zero_balance.is_overdrawn


# =====================================================================
# Status Setter Tests
# =====================================================================

def test_change_status(account):

    account.status = AccountStatus.SUSPENDED

    assert account.status == AccountStatus.SUSPENDED


def test_status_change_updates_version(account):

    version = account.version

    account.status = AccountStatus.SUSPENDED

    assert account.version == version + 1


def test_status_change_updates_timestamp(account):

    updated = account.updated_at

    account.status = AccountStatus.SUSPENDED

    assert account.updated_at >= updated


def test_restore_status(account):

    account.status = AccountStatus.SUSPENDED

    account.status = AccountStatus.ACTIVE

    assert account.status == AccountStatus.ACTIVE


def test_invalid_status_type(account):

    with pytest.raises(TypeError):

        account.status = "ACTIVE"


# =====================================================================
# Balance State Tests
# =====================================================================

def test_available_balance_equals_balance(account):

    assert account.available_balance.amount == account.balance.amount


def test_balance_is_money_object(account):

    assert isinstance(account.balance, Money)


def test_available_balance_is_money(account):

    assert isinstance(account.available_balance, Money)


def test_balance_amount_is_decimal(account):

    assert isinstance(account.balance_amount, Decimal)


def test_currency_remains_unchanged(account):

    original = account.currency

    account.status = AccountStatus.SUSPENDED

    assert account.currency == original


def test_account_number_remains_constant(account):

    number = account.account_number

    account.status = AccountStatus.SUSPENDED

    assert account.account_number == number


def test_customer_id_remains_constant(account):

    customer = account.customer_id

    account.status = AccountStatus.SUSPENDED

    assert account.customer_id == customer


def test_account_type_remains_constant(account):

    account_type = account.account_type

    account.status = AccountStatus.SUSPENDED

    assert account.account_type == account_type

# PART 3

# =====================================================================
# Deposit Tests
# =====================================================================

def test_deposit_increases_balance(account):

    account.deposit(
        Money(
            Decimal("250.00"),
            Currency.SAR,
        )
    )

    assert account.balance.amount == Decimal("1250.00")


def test_deposit_updates_version(account):

    version = account.version

    account.deposit(
        Money(
            Decimal("100.00"),
            Currency.SAR,
        )
    )

    assert account.version == version + 1


def test_deposit_updates_timestamp(account):

    updated = account.updated_at

    account.deposit(
        Money(
            Decimal("50.00"),
            Currency.SAR,
        )
    )

    assert account.updated_at >= updated


def test_multiple_deposits(account):

    account.deposit(
        Money(
            Decimal("100.00"),
            Currency.SAR,
        )
    )

    account.deposit(
        Money(
            Decimal("200.00"),
            Currency.SAR,
        )
    )

    assert account.balance.amount == Decimal("1300.00")


def test_deposit_to_inactive_account(account):

    account.deactivate()

    with pytest.raises(ValueError):

        account.deposit(
            Money(
                Decimal("100.00"),
                Currency.SAR,
            )
        )


# =====================================================================
# Withdrawal Tests
# =====================================================================

def test_withdraw_reduces_balance(account):

    account.withdraw(
        Money(
            Decimal("250.00"),
            Currency.SAR,
        )
    )

    assert account.balance.amount == Decimal("750.00")


def test_withdraw_updates_version(account):

    version = account.version

    account.withdraw(
        Money(
            Decimal("100.00"),
            Currency.SAR,
        )
    )

    assert account.version == version + 1


def test_withdraw_updates_timestamp(account):

    updated = account.updated_at

    account.withdraw(
        Money(
            Decimal("100.00"),
            Currency.SAR,
        )
    )

    assert account.updated_at >= updated


def test_withdraw_entire_balance(account_with_zero_balance):

    account = ConcreteAccount(
        account_number="SA-999999",
        customer_id="CUST999999",
        account_type=AccountType.SAVINGS,
        opening_balance=Money(
            Decimal("500.00"),
            Currency.SAR,
        ),
        currency=Currency.SAR,
    )

    account.withdraw(
        Money(
            Decimal("500.00"),
            Currency.SAR,
        )
    )

    assert account.is_zero_balance


def test_overdraw_not_allowed(account):

    with pytest.raises(ValueError):

        account.withdraw(
            Money(
                Decimal("1001.00"),
                Currency.SAR,
            )
        )


def test_withdraw_from_inactive_account(account):

    account.deactivate()

    with pytest.raises(ValueError):

        account.withdraw(
            Money(
                Decimal("100.00"),
                Currency.SAR,
            )
        )


# =====================================================================
# Transfer Tests
# =====================================================================

def test_transfer_reduces_source_balance(
    account,
    second_account,
):

    account.transfer_to(
        second_account,
        Money(
            Decimal("200.00"),
            Currency.SAR,
        ),
    )

    assert account.balance.amount == Decimal("800.00")


def test_transfer_increases_destination_balance(
    account,
    second_account,
):

    account.transfer_to(
        second_account,
        Money(
            Decimal("200.00"),
            Currency.SAR,
        ),
    )

    assert second_account.balance.amount == Decimal("700.00")


def test_transfer_preserves_total_balance(
    account,
    second_account,
):

    total_before = (
        account.balance.amount
        + second_account.balance.amount
    )

    account.transfer_to(
        second_account,
        Money(
            Decimal("250.00"),
            Currency.SAR,
        ),
    )

    total_after = (
        account.balance.amount
        + second_account.balance.amount
    )

    assert total_before == total_after


def test_transfer_to_same_account(account):

    with pytest.raises(ValueError):

        account.transfer_to(
            account,
            Money(
                Decimal("100.00"),
                Currency.SAR,
            ),
        )


def test_transfer_insufficient_balance(
    account,
    second_account,
):

    with pytest.raises(ValueError):

        account.transfer_to(
            second_account,
            Money(
                Decimal("5000.00"),
                Currency.SAR,
            ),
        )


def test_transfer_from_inactive_account(
    account,
    second_account,
):

    account.deactivate()

    with pytest.raises(ValueError):

        account.transfer_to(
            second_account,
            Money(
                Decimal("100.00"),
                Currency.SAR,
            ),
        )


def test_transfer_to_inactive_destination(
    account,
    second_account,
):

    second_account.deactivate()

    with pytest.raises(ValueError):

        account.transfer_to(
            second_account,
            Money(
                Decimal("100.00"),
                Currency.SAR,
            ),
        )

# PART 4

# =====================================================================
# Account Lifecycle Tests
# =====================================================================

def test_open_account_changes_status(account):

    account.suspend()

    account.open_account()

    assert account.status == AccountStatus.ACTIVE


def test_open_account_activates_entity(account):

    account.deactivate()

    account.open_account()

    assert account.is_active


def test_open_account_updates_version(account):

    version = account.version

    account.suspend()

    account.open_account()

    assert account.version > version


# =====================================================================
# Close Account
# =====================================================================

def test_close_zero_balance_account(account_with_zero_balance):

    account_with_zero_balance.close_account()

    assert account_with_zero_balance.status == AccountStatus.CLOSED


def test_close_account_sets_closed_date(account_with_zero_balance):

    account_with_zero_balance.close_account()

    assert account_with_zero_balance.closed_date == datetime.now(UTC).date()


def test_close_account_deactivates_entity(account_with_zero_balance):

    account_with_zero_balance.close_account()

    assert not account_with_zero_balance.is_active


def test_close_account_updates_version(account_with_zero_balance):

    version = account_with_zero_balance.version

    account_with_zero_balance.close_account()

    assert account_with_zero_balance.version > version


def test_close_account_requires_zero_balance(account):

    with pytest.raises(ValueError):

        account.close_account()


# =====================================================================
# Reopen Account
# =====================================================================

def test_reopen_closed_account(account_with_zero_balance):

    account_with_zero_balance.close_account()

    account_with_zero_balance.reopen()

    assert account_with_zero_balance.status == AccountStatus.ACTIVE


def test_reopen_clears_closed_date(account_with_zero_balance):

    account_with_zero_balance.close_account()

    account_with_zero_balance.reopen()

    assert account_with_zero_balance.closed_date is None


def test_reopen_activates_entity(account_with_zero_balance):

    account_with_zero_balance.close_account()

    account_with_zero_balance.reopen()

    assert account_with_zero_balance.is_active


def test_reopen_updates_version(account_with_zero_balance):

    account_with_zero_balance.close_account()

    version = account_with_zero_balance.version

    account_with_zero_balance.reopen()

    assert account_with_zero_balance.version > version


# =====================================================================
# Suspend / Reactivate
# =====================================================================

def test_suspend_account(account):

    account.suspend()

    assert account.status == AccountStatus.SUSPENDED


def test_suspend_updates_version(account):

    version = account.version

    account.suspend()

    assert account.version == version + 1


def test_suspend_updates_timestamp(account):

    updated = account.updated_at

    account.suspend()

    assert account.updated_at >= updated


def test_reactivate_account(account):

    account.suspend()

    account.reactivate()

    assert account.status == AccountStatus.ACTIVE


def test_reactivate_updates_version(account):

    account.suspend()

    version = account.version

    account.reactivate()

    assert account.version == version + 1


def test_reactivate_updates_timestamp(account):

    account.suspend()

    updated = account.updated_at

    account.reactivate()

    assert account.updated_at >= updated


# =====================================================================
# Lifecycle Consistency
# =====================================================================

def test_reopen_after_close_results_in_active_account(
    account_with_zero_balance,
):

    account_with_zero_balance.close_account()

    account_with_zero_balance.reopen()

    assert account_with_zero_balance.status == AccountStatus.ACTIVE
    assert account_with_zero_balance.is_active
    assert account_with_zero_balance.closed_date is None


def test_suspend_then_open(account):

    account.suspend()

    account.open_account()

    assert account.status == AccountStatus.ACTIVE


def test_multiple_suspend_reactivate_cycles(account):

    for _ in range(3):

        account.suspend()

        assert account.status == AccountStatus.SUSPENDED

        account.reactivate()

        assert account.status == AccountStatus.ACTIVE

# PART 5

# =====================================================================
# Default Implementation Tests
# =====================================================================

def test_default_calculate_interest(account):

    interest = account.calculate_interest()

    assert isinstance(interest, Money)

    assert interest.amount == Decimal("0.00")

    assert interest.currency == account.currency


def test_default_calculate_fee(account):

    fee = account.calculate_fee()

    assert isinstance(fee, Money)

    assert fee.amount == Decimal("0.00")

    assert fee.currency == account.currency


def test_default_can_withdraw_true(account):

    assert account._can_withdraw(
        Money(
            Decimal("500.00"),
            Currency.SAR,
        )
    )


def test_default_can_withdraw_false(account):

    assert not account._can_withdraw(
        Money(
            Decimal("5000.00"),
            Currency.SAR,
        )
    )


# =====================================================================
# Serialization Tests
# =====================================================================

def test_to_dict_returns_dictionary(account):

    data = account.to_dict()

    assert isinstance(data, dict)


def test_to_dict_contains_required_keys(account):

    data = account.to_dict()

    expected = {
        "account_number",
        "customer_id",
        "account_type",
        "status",
        "currency",
        "balance",
    }

    assert expected.issubset(data.keys())


def test_from_dict_restores_basic_values(account):

    restored = ConcreteAccount.from_dict(
        account.to_dict()
    )

    assert restored.account_number == account.account_number

    assert restored.customer_id == account.customer_id

    assert restored.account_type == account.account_type

    assert restored.balance == account.balance

    assert restored.currency == account.currency

    assert restored.status == account.status


# =====================================================================
# Audit Tests
# =====================================================================

def test_version_initial_value(account):

    assert account.version == 1


def test_created_at_not_none(account):

    assert account.created_at is not None


def test_updated_at_not_none(account):

    assert account.updated_at is not None


def test_created_at_not_after_updated_at(account):

    assert account.created_at <= account.updated_at


def test_touch_after_deposit(account):

    version = account.version

    account.deposit(
        Money(
            Decimal("10.00"),
            Currency.SAR,
        )
    )

    assert account.version > version


def test_touch_after_withdraw(account):

    version = account.version

    account.withdraw(
        Money(
            Decimal("10.00"),
            Currency.SAR,
        )
    )

    assert account.version > version


# =====================================================================
# Miscellaneous Tests
# =====================================================================

def test_repr_returns_string(account):

    assert isinstance(repr(account), str)


def test_str_returns_string(account):

    assert isinstance(str(account), str)


def test_entity_is_hashable(account):

    hash(account)


def test_two_accounts_are_not_equal(
    account,
    second_account,
):

    assert account != second_account


def test_account_equals_itself(account):

    assert account == account


def test_transaction_ids_is_list(account):

    assert isinstance(
        account.transaction_ids,
        tuple,
    )


def test_new_account_has_no_transactions(account):

    assert len(account.transaction_ids) == 0


def test_balance_currency_remains_constant(account):

    account.deposit(
        Money(
            Decimal("100.00"),
            Currency.SAR,
        )
    )

    account.withdraw(
        Money(
            Decimal("50.00"),
            Currency.SAR,
        )
    )

    assert account.balance.currency == Currency.SAR


def test_multiple_operations_preserve_consistency(
    account,
):

    account.deposit(
        Money(
            Decimal("100.00"),
            Currency.SAR,
        )
    )

    account.withdraw(
        Money(
            Decimal("25.00"),
            Currency.SAR,
        )
    )

    account.suspend()

    account.reactivate()

    assert account.balance.amount == Decimal("1075.00")

    assert account.status == AccountStatus.ACTIVE

    assert account.is_active


def test_zero_balance_after_full_withdrawal():

    account = ConcreteAccount(
        account_number="SA-123456",
        customer_id="CUST123456",
        account_type=AccountType.SAVINGS,
        opening_balance=Money(
            Decimal("200.00"),
            Currency.SAR,
        ),
        currency=Currency.SAR,
    )

    account.withdraw(
        Money(
            Decimal("200.00"),
            Currency.SAR,
        )
    )

    assert account.is_zero_balance


def test_positive_balance_after_deposit(
    account_with_zero_balance,
):

    account_with_zero_balance.deposit(
        Money(
            Decimal("1.00"),
            Currency.SAR,
        )
    )

    assert account_with_zero_balance.has_positive_balance


def test_available_balance_matches_balance(account):

    assert (
        account.available_balance.amount
        ==
        account.balance.amount
    )


def test_interest_returns_zero_money(account):

    interest = account.calculate_interest()

    assert interest == Money.zero(
        account.currency
    )


def test_fee_returns_zero_money(account):

    fee = account.calculate_fee()

    assert fee == Money.zero(
        account.currency
    )

