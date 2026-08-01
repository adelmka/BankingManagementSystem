"""
====================================================================
Banking Management System (BMS)

File        : test_models.py
Description : Unit Tests for Domain Models (Part 1)

Tests:
    • BaseEntity
    • Person

Author      : Adel Alawiyat / ChatGPT
Python      : 3.13+
====================================================================
"""

from __future__ import annotations

from datetime import UTC, date, datetime
from uuid import uuid4

from decimal import Decimal

import pytest

from models.base_entity import BaseEntity
from models.person import Person
from models.value_objects.address import Address

from models.value_objects.money import Money

# ============================================================
# Customer
# ============================================================

from models.customer import Customer

from exceptions.banking_exceptions import (
    CustomerAlreadyExistsError,
    CustomerInactiveError,
    InvalidNameError,
)


# ============================================================
# Account
# ============================================================

from models.account import Account

from exceptions.banking_exceptions import (
    AccountClosedError,
    InvalidAmountError,
    InvalidCurrencyError,
)

# ============================================================
# SavingsAccount
# ============================================================

from models.savings_account import SavingsAccount
from utils.constants import InterestFrequency


# ============================================================
# CurrentAccount
# ============================================================

from models.current_account import CurrentAccount


# ============================================================
# TimeDepositAccount
# ============================================================

from models.time_deposit_account import TimeDepositAccount


# ============================================================
# Transaction
# ============================================================


from models.transaction import Transaction

from utils.constants import (
    TransactionStatus,
    TransactionType,
)


class DummyEntity(BaseEntity):
    """
    Concrete implementation used only for testing BaseEntity.
    """

    def to_dict(self):
        return {}

    @classmethod
    def from_dict(cls, data):
        return cls()

# ============================================================
# BaseEntity
# ============================================================

def test_base_entity_initialization():

    entity = DummyEntity()

    assert entity.entity_id is not None
    assert entity.version == 1
    assert entity.is_active is True
    assert isinstance(entity.created_at, datetime)
    assert isinstance(entity.updated_at, datetime)


def test_touch_updates_version():

    entity = DummyEntity()

    version = entity.version

    entity.touch()

    assert entity.version == version + 1


def test_touch_updates_timestamp():

    entity = DummyEntity()

    original = entity.updated_at

    entity.touch()

    assert entity.updated_at >= original


def test_activate():

    entity = DummyEntity()

    entity.deactivate()

    entity.activate()

    assert entity.is_active is True


def test_deactivate():

    entity = DummyEntity()

    entity.deactivate()

    assert entity.is_active is False


def test_entity_equality():

    entity1 = DummyEntity()
    entity2 = DummyEntity()

    entity2._entity_id = entity1.entity_id

    assert entity1 == entity2


def test_entity_inequality():

    entity1 = DummyEntity()
    entity2 = DummyEntity()

    assert entity1 != entity2


def test_hash():

    entity = DummyEntity()

    assert hash(entity)


def test_repr():

    entity = DummyEntity()

    assert "DummyEntity" in repr(entity)


def test_str():

    entity = DummyEntity()

    assert str(entity)


def test_base_entity_is_abstract():

    with pytest.raises(TypeError):
        BaseEntity()

# ============================================================
# Fixtures
# ============================================================

@pytest.fixture
def address():

    return Address(
        street="King Fahd Road",
        city="Riyadh",
        state="Riyadh",
        postal_code="11564",
        country="Saudi Arabia",
    )


@pytest.fixture
def person(address):

    return Person(
        first_name="Adel",
        last_name="Alawiyat",
        email="adel@example.com",
        phone="+966500000000",
        address=address,
    )

# ============================================================
# Person Construction
# ============================================================

def test_create_person(person):

    assert person.first_name == "Adel"
    assert person.last_name == "Alawiyat"
    assert person.email == "adel@example.com"
    assert person.phone == "+966500000000"


def test_person_has_entity_id(person):

    assert person.entity_id is not None


def test_person_created_at(person):

    assert isinstance(person.created_at, datetime)


def test_person_updated_at(person):

    assert isinstance(person.updated_at, datetime)


def test_person_version(person):

    assert person.version == 1

# ============================================================
# Property Updates
# ============================================================

def test_change_first_name(person):

    version = person.version

    person.first_name = "Ahmed"

    assert person.first_name == "Ahmed"
    assert person.version == version + 1


def test_change_last_name(person):

    version = person.version

    person.last_name = "Ali"

    assert person.last_name == "Ali"
    assert person.version == version + 1


def test_change_email(person):

    version = person.version

    person.email = "new@email.com"

    assert person.email == "new@email.com"
    assert person.version == version + 1


def test_change_phone(person):

    version = person.version

    person.phone = "+966511111111"

    assert person.phone == "+966511111111"
    assert person.version == version + 1


def test_change_address(person):

    version = person.version

    new_address = Address(
        street="Olaya",
        city="Riyadh",
        state="Riyadh",
        postal_code="12211",
        country="Saudi Arabia",
    )

    person.address = new_address

    assert person.address == new_address
    assert person.version == version + 1

# ============================================================
# Validation
# ============================================================

def test_invalid_first_name(person):

    with pytest.raises(InvalidNameError):
        person.first_name = ""


def test_invalid_last_name(person):

    with pytest.raises(InvalidNameError):
        person.last_name = ""


def test_invalid_email(person):

    with pytest.raises(InvalidEmailError):
        person.email = "invalid"


def test_invalid_phone(person):

    with pytest.raises(InvalidPhoneError):
        person.phone = "abc"


def test_invalid_address(person):

    with pytest.raises(ValueError):
        person.address = None

# ============================================================
# Serialization
# ============================================================

def test_person_to_dict(person):

    data = person.to_dict()

    assert isinstance(data, dict)


def test_person_from_dict(person):

    data = person.to_dict()

    restored = Person.from_dict(data)

    assert restored == person

# ============================================================
# Equality / Representation
# ============================================================

def test_person_equality(person):

    clone = Person.from_dict(person.to_dict())

    clone._entity_id = person.entity_id

    assert clone == person


def test_person_repr(person):

    assert "Person" in repr(person)


def test_person_str(person):

    assert str(person)

# PART 2

# ============================================================
# Fixtures
# ============================================================

@pytest.fixture
def customer(address):

    return Customer(
        first_name="Adel",
        last_name="Alawiyat",
        email="adel@example.com",
        phone="+966500000000",
        address=address,
    )


@pytest.fixture
def savings_account(customer):

    return SavingsAccount(
        customer_id=customer.customer_id,
        account_number="SA100001",
        balance=Money("1000.00"),
    )

# ============================================================
# Customer Construction
# ============================================================

def test_create_customer(customer):

    assert customer.customer_id is not None
    assert customer.first_name == "Adel"
    assert customer.last_name == "Alawiyat"


def test_customer_is_active(customer):

    assert customer.is_active is True


def test_customer_initial_version(customer):

    assert customer.version == 1


def test_customer_created_timestamp(customer):

    assert isinstance(customer.created_at, datetime)


def test_customer_updated_timestamp(customer):

    assert isinstance(customer.updated_at, datetime)

# ============================================================
# Aggregate Behaviour
# ============================================================

def test_customer_initially_has_no_accounts(customer):

    assert len(customer.accounts) == 0


def test_add_account(customer, savings_account):

    customer.add_account(savings_account)

    assert len(customer.accounts) == 1


def test_added_account_exists(customer, savings_account):

    customer.add_account(savings_account)

    assert savings_account in customer.accounts


def test_remove_account(customer, savings_account):

    customer.add_account(savings_account)

    customer.remove_account(savings_account.account_number)

    assert len(customer.accounts) == 0

# ============================================================
# Versioning
# ============================================================

def test_add_account_updates_version(customer, savings_account):

    version = customer.version

    customer.add_account(savings_account)

    assert customer.version == version + 1


def test_remove_account_updates_version(customer, savings_account):

    customer.add_account(savings_account)

    version = customer.version

    customer.remove_account(savings_account.account_number)

    assert customer.version == version + 1

# ============================================================
# Duplicate Accounts
# ============================================================

def test_duplicate_account(customer, savings_account):

    customer.add_account(savings_account)

    with pytest.raises(Exception):
        customer.add_account(savings_account)

# ============================================================
# Lifecycle
# ============================================================

def test_deactivate_customer(customer):

    customer.deactivate()

    assert customer.is_active is False


def test_activate_customer(customer):

    customer.deactivate()

    customer.activate()

    assert customer.is_active is True

# ============================================================
# Serialization
# ============================================================

def test_customer_to_dict(customer):

    data = customer.to_dict()

    assert isinstance(data, dict)


def test_customer_from_dict(customer):

    data = customer.to_dict()

    restored = Customer.from_dict(data)

    assert restored == customer

# ============================================================
# Equality
# ============================================================

def test_customer_equality(customer):

    clone = Customer.from_dict(customer.to_dict())

    clone._entity_id = customer.entity_id

    assert clone == customer


def test_customer_not_equal(customer):

    another = Customer.from_dict(customer.to_dict())

    assert customer != another

# ============================================================
# Representation
# ============================================================

def test_customer_repr(customer):

    assert "Customer" in repr(customer)


def test_customer_str(customer):

    assert str(customer)

# ============================================================
# Validation
# ============================================================

def test_invalid_customer_first_name(customer):

    with pytest.raises(InvalidNameError):
        customer.first_name = ""


def test_invalid_customer_last_name(customer):

    with pytest.raises(InvalidNameError):
        customer.last_name = ""


# Part 3A

# ============================================================
# Fixtures
# ============================================================

@pytest.fixture
def account(customer):

    return SavingsAccount(
        account_number="SA-100001",
        customer_id=customer.customer_id,
        opening_balance=Money("1000.00"),
        interest_rate=Decimal("2.50"),
        minimum_balance=Money("100.00"),
    )

# ============================================================
# Construction
# ============================================================

def test_account_number(account):

    assert account.account_number == "SA-100001"


def test_customer_id(account, customer):

    assert account.customer_id == customer.customer_id


def test_opening_balance(account):

    assert account.balance == Money("1000.00")


def test_currency(account):

    assert account.currency.code == "SAR"


def test_account_active(account):

    assert account.is_active is True


def test_account_version(account):

    assert account.version == 1


def test_created_timestamp(account):

    assert account.created_at is not None


def test_updated_timestamp(account):

    assert account.updated_at is not None

# ============================================================
# Property Validation
# ============================================================

def test_invalid_account_number(customer):

    with pytest.raises(Exception):

        SavingsAccount(
            account_number="",
            customer_id=customer.customer_id,
            opening_balance=Money("100"),
            interest_rate=Decimal("2"),
            minimum_balance=Money("10"),
        )


def test_invalid_customer_id():

    with pytest.raises(Exception):

        SavingsAccount(
            account_number="SA100",
            customer_id="",
            opening_balance=Money("100"),
            interest_rate=Decimal("2"),
            minimum_balance=Money("10"),
        )

# ============================================================
# Currency
# ============================================================

def test_default_currency(account):

    assert account.currency.code == "SAR"


def test_custom_currency(customer):

    account = SavingsAccount(
        account_number="SA200",
        customer_id=customer.customer_id,
        opening_balance=Money("100"),
        interest_rate=Decimal("2"),
        minimum_balance=Money("10"),
        currency="USD",
    )

    assert account.currency.code == "USD"

# ============================================================
# Lifecycle
# ============================================================

def test_close_account(account):

    account.close()

    assert account.is_active is False


def test_reopen_account(account):

    account.close()

    account.activate()

    assert account.is_active is True


def test_close_updates_version(account):

    version = account.version

    account.close()

    assert account.version == version + 1


def test_close_updates_timestamp(account):

    original = account.updated_at

    account.close()

    assert account.updated_at >= original

# ============================================================
# Audit
# ============================================================

def test_touch_updates_version(account):

    version = account.version

    account.touch()

    assert account.version == version + 1


def test_touch_updates_timestamp(account):

    timestamp = account.updated_at

    account.touch()

    assert account.updated_at >= timestamp

# ============================================================
# Initial State
# ============================================================

def test_account_has_zero_transactions(account):

    assert len(account.transactions) == 0


def test_account_has_open_date(account):

    assert account.opened_date is not None


def test_account_not_closed(account):

    assert account.closed_date is None


# ============================================================
# Closed Account Protection
# ============================================================

def test_closed_account_cannot_receive_operations(account):

    account.close()

    with pytest.raises(AccountClosedError):

        account.deposit(Money("100"))

# ============================================================
# Version Consistency
# ============================================================

def test_new_account_version(account):

    assert account.version == 1


def test_version_increases_after_close(account):

    version = account.version

    account.close()

    assert account.version == version + 1


# Part 3B

# ============================================================
# Deposit Operations
# ============================================================

def test_successful_deposit(account):

    original = account.balance

    account.deposit(Money("500.00"))

    assert account.balance == original + Money("500.00")


def test_deposit_updates_version(account):

    version = account.version

    account.deposit(Money("100"))

    assert account.version == version + 1


def test_deposit_updates_timestamp(account):

    updated = account.updated_at

    account.deposit(Money("25"))

    assert account.updated_at >= updated


def test_invalid_deposit_amount(account):

    with pytest.raises(InvalidAmountError):
        account.deposit(Money("-10"))


def test_zero_deposit(account):

    with pytest.raises(InvalidAmountError):
        account.deposit(Money("0"))

# ============================================================
# Withdrawal Operations
# ============================================================

def test_successful_withdrawal(account):

    original = account.balance

    account.withdraw(Money("100"))

    assert account.balance == original - Money("100")


def test_withdrawal_updates_version(account):

    version = account.version

    account.withdraw(Money("50"))

    assert account.version == version + 1


def test_withdrawal_updates_timestamp(account):

    timestamp = account.updated_at

    account.withdraw(Money("10"))

    assert account.updated_at >= timestamp


def test_insufficient_funds(account):

    with pytest.raises(InsufficientFundsError):

        account.withdraw(Money("1000000"))

# ============================================================
# Transfer Operations
# ============================================================

@pytest.fixture
def second_account(customer):

    return SavingsAccount(
        account_number="SA200001",
        customer_id=customer.customer_id,
        opening_balance=Money("500"),
        interest_rate=Decimal("2.5"),
        minimum_balance=Money("100"),
    )


def test_transfer(account, second_account):

    account.transfer(
        second_account,
        Money("200")
    )

    assert account.balance == Money("800")
    assert second_account.balance == Money("700")


def test_transfer_same_account(account):

    with pytest.raises(Exception):

        account.transfer(
            account,
            Money("100")
        )


def test_transfer_invalid_amount(account, second_account):

    with pytest.raises(InvalidAmountError):

        account.transfer(
            second_account,
            Money("-1")
        )

# ============================================================
# Transaction History
# ============================================================

def test_transaction_added_after_deposit(account):

    initial = len(account.transactions)

    account.deposit(Money("100"))

    assert len(account.transactions) == initial + 1


def test_transaction_added_after_withdraw(account):

    initial = len(account.transactions)

    account.withdraw(Money("50"))

    assert len(account.transactions) == initial + 1


def test_transactions_are_list(account):

    assert isinstance(account.transactions, list)

# ============================================================
# Serialization
# ============================================================

def test_account_to_dict(account):

    data = account.to_dict()

    assert isinstance(data, dict)


def test_account_from_dict(account):

    data = account.to_dict()

    restored = SavingsAccount.from_dict(data)

    assert restored == account


def test_serialization_preserves_balance(account):

    restored = SavingsAccount.from_dict(
        account.to_dict()
    )

    assert restored.balance == account.balance


def test_serialization_preserves_account_number(account):

    restored = SavingsAccount.from_dict(
        account.to_dict()
    )

    assert restored.account_number == account.account_number

# ============================================================
# Reporting
# ============================================================

def test_account_summary(account):

    summary = account.account_summary()

    assert isinstance(summary, dict)


def test_balance_information_present(account):

    summary = account.account_summary()

    assert "balance" in summary


def test_account_number_present(account):

    summary = account.account_summary()

    assert "account_number" in summary

# ============================================================
# Equality
# ============================================================

def test_account_equality(account):

    clone = SavingsAccount.from_dict(
        account.to_dict()
    )

    clone._entity_id = account.entity_id

    assert clone == account


def test_account_hash(account):

    assert hash(account)


def test_account_not_equal(account):

    another = SavingsAccount.from_dict(
        account.to_dict()
    )

    assert another != account

# ============================================================
# Representation
# ============================================================

def test_account_repr(account):

    assert "Account" in repr(account)


def test_account_str(account):

    assert account.account_number in str(account)

# ============================================================
# Persistence
# ============================================================

def test_restore_state(account):

    data = account.to_dict()

    restored = SavingsAccount.from_dict(data)

    assert restored.account_number == account.account_number

    assert restored.balance == account.balance

    assert restored.customer_id == account.customer_id

# ============================================================
# Boundary Cases
# ============================================================

def test_large_deposit(account):

    account.deposit(Money("100000000"))

    assert account.balance > Money("100000000")


def test_small_decimal_deposit(account):

    account.deposit(Money("0.01"))

    assert account.balance == Money("1000.01")


def test_small_decimal_withdraw(account):

    account.withdraw(Money("0.01"))

    assert account.balance == Money("999.99")


# PART 4A

# ============================================================
# Fixtures
# ============================================================

@pytest.fixture
def savings_account(customer):

    return SavingsAccount(
        account_number="SA100001",
        customer_id=customer.customer_id,
        opening_balance=Money("5000.00"),
        interest_rate=Decimal("0.05"),
        minimum_balance=Money("1000.00"),
    )

# ============================================================
# Construction
# ============================================================

def test_create_savings_account(savings_account):

    assert savings_account.account_number == "SA100001"


def test_interest_rate_initialized(savings_account):

    assert savings_account.interest_rate == Decimal("0.05")


def test_minimum_balance_initialized(savings_account):

    assert savings_account.minimum_balance == Money("1000.00")


def test_default_interest_frequency(savings_account):

    assert (
        savings_account.interest_frequency
        == InterestFrequency.MONTHLY
    )


def test_last_interest_date_initialized(savings_account):

    assert savings_account.last_interest_date is not None

# ============================================================
# Validation
# ============================================================

def test_negative_interest_rate(savings_account):

    with pytest.raises(ValueError):

        savings_account.interest_rate = Decimal("-0.01")


def test_invalid_minimum_balance_type(savings_account):

    with pytest.raises(TypeError):

        savings_account.minimum_balance = Decimal("100")


def test_negative_minimum_balance(savings_account):

    with pytest.raises(ValueError):

        savings_account.minimum_balance = Money("-1")


def test_invalid_interest_frequency(savings_account):

    with pytest.raises(TypeError):

        savings_account.interest_frequency = "MONTHLY"

# ============================================================
# Minimum Balance Rules
# ============================================================

def test_has_minimum_balance_true(savings_account):

    assert savings_account.has_minimum_balance()


def test_available_for_withdrawal(savings_account):

    amount = savings_account.amount_available_for_withdrawal()

    assert amount == Money("4000.00")


def test_can_withdraw_within_limit(savings_account):

    assert savings_account._can_withdraw(
        Money("3000")
    )


def test_cannot_withdraw_below_minimum(savings_account):

    assert (
        savings_account._can_withdraw(
            Money("4500")
        )
        is False
    )

# ============================================================
# Interest Eligibility
# ============================================================

def test_can_earn_interest(savings_account):

    assert savings_account.can_earn_interest()


def test_no_interest_when_balance_below_minimum(savings_account):

    savings_account.withdraw(Money("4500"))

    assert (
        savings_account.can_earn_interest()
        is False
    )

# ============================================================
# Interest Calculation
# ============================================================

def test_calculate_interest(savings_account):

    interest = savings_account.calculate_interest()

    assert isinstance(interest, Money)


def test_zero_interest_when_not_eligible(savings_account):

    savings_account.withdraw(Money("4500"))

    interest = savings_account.calculate_interest()

    assert interest.amount == Decimal("0.00")

# ============================================================
# Administration
# ============================================================

def test_update_interest_rate(savings_account):

    savings_account.update_interest_rate(
        Decimal("0.06")
    )

    assert savings_account.interest_rate == Decimal("0.06")


def test_record_interest_application(savings_account):

    today = datetime.now(UTC).date()

    savings_account.record_interest_application(today)

    assert (
        savings_account.last_interest_date
        == today
    )

# ============================================================
# Interest Frequency
# ============================================================

@pytest.mark.parametrize(
    "frequency,periods",
    [
        (InterestFrequency.DAILY,365),
        (InterestFrequency.WEEKLY,52),
        (InterestFrequency.MONTHLY,12),
        (InterestFrequency.QUARTERLY,4),
        (InterestFrequency.SEMI_ANNUALLY,2),
        (InterestFrequency.ANNUALLY,1),
    ]
)
def test_periods_per_year(
    savings_account,
    frequency,
    periods
):

    savings_account.interest_frequency = frequency

    assert (
        savings_account.periods_per_year()
        == periods
    )

# ============================================================
# Serialization
# ============================================================

def test_to_dict(savings_account):

    data = savings_account.to_dict()

    assert isinstance(data, dict)


def test_from_dict(savings_account):

    restored = SavingsAccount.from_dict(
        savings_account.to_dict()
    )

    assert restored == savings_account


def test_serialization_preserves_interest_rate(
    savings_account
):

    restored = SavingsAccount.from_dict(
        savings_account.to_dict()
    )

    assert (
        restored.interest_rate
        == savings_account.interest_rate
    )

# ============================================================
# Reporting
# ============================================================

def test_savings_summary(savings_account):

    summary = savings_account.savings_summary()

    assert isinstance(summary, dict)


def test_summary_contains_interest_rate(savings_account):

    summary = savings_account.savings_summary()

    assert "interest_rate" in summary


def test_summary_contains_frequency(savings_account):

    summary = savings_account.savings_summary()

    assert "interest_frequency" in summary


def test_summary_contains_eligibility(savings_account):

    summary = savings_account.savings_summary()

    assert "eligible_for_interest" in summary

# ============================================================
# Representation
# ============================================================

def test_str(savings_account):

    assert "Savings" in str(savings_account)


def test_repr(savings_account):

    assert "SavingsAccount" in repr(savings_account)


def test_hash(savings_account):

    assert hash(savings_account)


def test_equality(savings_account):

    clone = SavingsAccount.from_dict(
        savings_account.to_dict()
    )

    clone._entity_id = savings_account.entity_id

    assert clone == savings_account

# ============================================================
# Boundary Cases
# ============================================================

def test_balance_equals_minimum(savings_account):

    savings_account.withdraw(Money("4000"))

    assert savings_account.has_minimum_balance()


def test_withdrawable_zero_at_minimum(savings_account):

    savings_account.withdraw(Money("4000"))

    assert (
        savings_account.amount_available_for_withdrawal()
        == Money.zero(savings_account.currency)
    )


def test_interest_after_rate_change(savings_account):

    savings_account.update_interest_rate(
        Decimal("0.10")
    )

    interest = savings_account.calculate_interest()

    assert interest.amount > Decimal("0")


# Part 4B

# ============================================================
# Fixtures
# ============================================================

@pytest.fixture
def current_account(customer):

    return CurrentAccount(
        account_number="CA100001",
        customer_id=customer.customer_id,
        opening_balance=Money("2500.00"),
        overdraft_limit=Money("5000.00"),
        maintenance_fee=Money("25.00"),
        overdraft_fee=Money("100.00"),
    )

# ============================================================
# Construction
# ============================================================

def test_create_current_account(current_account):

    assert current_account.account_number == "CA100001"


def test_overdraft_limit_initialized(current_account):

    assert current_account.overdraft_limit == Money("5000.00")


def test_maintenance_fee_initialized(current_account):

    assert current_account.maintenance_fee == Money("25.00")


def test_overdraft_fee_initialized(current_account):

    assert current_account.overdraft_fee == Money("100.00")


def test_overdraft_enabled_default(current_account):

    assert current_account.overdraft_enabled is True


def test_last_fee_date_initialized(current_account):

    assert current_account.last_fee_date is not None

# ============================================================
# Validation
# ============================================================

def test_negative_overdraft_limit(current_account):

    with pytest.raises(ValueError):

        current_account.overdraft_limit = Money("-1")


def test_negative_maintenance_fee(current_account):

    with pytest.raises(ValueError):

        current_account.maintenance_fee = Money("-10")


def test_negative_overdraft_fee(current_account):

    with pytest.raises(ValueError):

        current_account.overdraft_fee = Money("-50")

# ============================================================
# Overdraft Behaviour
# ============================================================

def test_available_funds(current_account):

    available = current_account.available_funds()

    assert available == Money("7500.00")


def test_remaining_overdraft(current_account):

    remaining = current_account.remaining_overdraft()

    assert remaining == Money("5000.00")


def test_has_available_overdraft(current_account):

    assert current_account.has_available_overdraft()


def test_not_using_overdraft_initially(current_account):

    assert current_account.is_using_overdraft() is False

# ============================================================
# Withdrawal Rules
# ============================================================

def test_can_withdraw_using_overdraft(current_account):

    assert current_account._can_withdraw(
        Money("7000")
    )


def test_cannot_exceed_overdraft(current_account):

    assert (
        current_account._can_withdraw(
            Money("8000")
        )
        is False
    )

# ============================================================
# Fee Calculations
# ============================================================

def test_calculate_maintenance_fee(current_account):

    fee = current_account.calculate_maintenance_fee()

    assert fee == Money("25.00")


def test_calculate_overdraft_fee(current_account):

    fee = current_account.calculate_overdraft_fee()

    assert fee == Money("100.00")


def test_calculate_fee(current_account):

    fee = current_account.calculate_fee()

    assert isinstance(fee, Money)

# ============================================================
# Administrative Updates
# ============================================================

def test_update_overdraft_limit(current_account):

    current_account.update_overdraft_limit(
        Money("7000")
    )

    assert current_account.overdraft_limit == Money("7000")


def test_update_maintenance_fee(current_account):

    current_account.update_maintenance_fee(
        Money("35")
    )

    assert current_account.maintenance_fee == Money("35")


def test_update_overdraft_fee(current_account):

    current_account.update_overdraft_fee(
        Money("150")
    )

    assert current_account.overdraft_fee == Money("150")

# ============================================================
# Fee Recording
# ============================================================

def test_record_fee_application(current_account):

    today = datetime.now(UTC).date()

    current_account.record_fee_application(today)

    assert current_account.last_fee_date == today

# ============================================================
# Serialization
# ============================================================

def test_current_account_to_dict(current_account):

    data = current_account.to_dict()

    assert isinstance(data, dict)


def test_current_account_from_dict(current_account):

    restored = CurrentAccount.from_dict(
        current_account.to_dict()
    )

    assert restored == current_account


def test_serialization_preserves_overdraft(current_account):

    restored = CurrentAccount.from_dict(
        current_account.to_dict()
    )

    assert (
        restored.overdraft_limit
        == current_account.overdraft_limit
    )

# ============================================================
# Reporting
# ============================================================

def test_current_account_summary(current_account):

    summary = current_account.current_account_summary()

    assert isinstance(summary, dict)


def test_account_health(current_account):

    health = current_account.account_health()

    assert isinstance(health, dict)


def test_summary_contains_overdraft(current_account):

    summary = current_account.current_account_summary()

    assert "overdraft_limit" in summary

# ============================================================
# Representation
# ============================================================

def test_current_account_str(current_account):

    assert "Current" in str(current_account)


def test_current_account_repr(current_account):

    assert "CurrentAccount" in repr(current_account)


def test_current_account_hash(current_account):

    assert hash(current_account)


def test_current_account_equality(current_account):

    clone = CurrentAccount.from_dict(
        current_account.to_dict()
    )

    clone._entity_id = current_account.entity_id

    assert clone == current_account

# ============================================================
# Boundary Cases
# ============================================================

def test_full_overdraft_usage(current_account):

    current_account.withdraw(Money("7500"))

    assert current_account.balance == Money("-5000")


def test_remaining_overdraft_after_usage(current_account):

    current_account.withdraw(Money("3000"))

    assert (
        current_account.remaining_overdraft()
        == Money("4500")
    )


def test_using_overdraft_after_large_withdrawal(current_account):

    current_account.withdraw(Money("3000"))

    assert current_account.is_using_overdraft()


# Part 4C

# ============================================================
# Fixtures
# ============================================================

@pytest.fixture
def time_deposit_account(customer):

    return TimeDepositAccount(
        account_number="TD100001",
        customer_id=customer.customer_id,
        opening_balance=Money("10000.00"),
        interest_rate=Decimal("0.05"),
        term_months=12,
        early_withdrawal_penalty_rate=Decimal("0.10"),
    )

# ============================================================
# Construction
# ============================================================

def test_create_time_deposit(time_deposit_account):

    assert time_deposit_account.account_number == "TD100001"


def test_principal_initialized(time_deposit_account):

    assert time_deposit_account.principal == Money("10000.00")


def test_interest_rate_initialized(time_deposit_account):

    assert time_deposit_account.interest_rate == Decimal("0.05")


def test_term_initialized(time_deposit_account):

    assert time_deposit_account.term_months == 12


def test_penalty_rate_initialized(time_deposit_account):

    assert (
        time_deposit_account.early_withdrawal_penalty_rate
        == Decimal("0.10")
    )


def test_auto_renew_default(time_deposit_account):

    assert time_deposit_account.auto_renew is False

# ============================================================
# Validation
# ============================================================

def test_negative_interest_rate(time_deposit_account):

    with pytest.raises(ValueError):
        time_deposit_account.interest_rate = Decimal("-0.01")


def test_invalid_term():

    with pytest.raises(ValueError):

        TimeDepositAccount(
            account_number="TD2",
            customer_id="C1",
            opening_balance=Money("1000"),
            interest_rate=Decimal("0.05"),
            term_months=0,
            early_withdrawal_penalty_rate=Decimal("0.10"),
        )


def test_penalty_rate_above_100(time_deposit_account):

    with pytest.raises(ValueError):
        time_deposit_account.early_withdrawal_penalty_rate = Decimal("1.10")

# ============================================================
# Maturity
# ============================================================

def test_term_days(time_deposit_account):

    assert time_deposit_account.term_days == 360


def test_maturity_date(time_deposit_account):

    assert isinstance(
        time_deposit_account.maturity_date,
        date,
    )


def test_is_not_matured_initially(time_deposit_account):

    assert isinstance(
        time_deposit_account.is_matured(),
        bool,
    )


def test_can_close_matches_maturity(time_deposit_account):

    assert (
        time_deposit_account.can_close()
        == time_deposit_account.is_matured()
    )

# ============================================================
# Withdrawal Rules
# ============================================================

def test_cannot_withdraw_before_maturity(time_deposit_account):

    assert (
        time_deposit_account._can_withdraw(
            Money("1000")
        )
        is False
    )

# ============================================================
# Interest
# ============================================================

def test_calculate_interest(time_deposit_account):

    interest = time_deposit_account.calculate_interest()

    assert isinstance(interest, Money)


def test_maturity_value(time_deposit_account):

    value = time_deposit_account.calculate_maturity_value()

    assert value > time_deposit_account.principal

# ============================================================
# Early Withdrawal Penalty
# ============================================================

def test_penalty_calculation(time_deposit_account):

    penalty = (
        time_deposit_account
        .calculate_early_withdrawal_penalty()
    )

    assert isinstance(penalty, Money)


def test_apply_penalty(time_deposit_account):

    penalty = (
        time_deposit_account
        .apply_early_withdrawal_penalty()
    )

    assert isinstance(penalty, Money)

# ============================================================
# Administration
# ============================================================

def test_update_interest_rate(time_deposit_account):

    time_deposit_account.update_interest_rate(
        Decimal("0.06")
    )

    assert (
        time_deposit_account.interest_rate
        == Decimal("0.06")
    )


def test_update_penalty_rate(time_deposit_account):

    time_deposit_account.update_penalty_rate(
        Decimal("0.15")
    )

    assert (
        time_deposit_account
        .early_withdrawal_penalty_rate
        == Decimal("0.15")
    )


def test_enable_auto_renew(time_deposit_account):

    time_deposit_account.update_auto_renew(True)

    assert time_deposit_account.auto_renew

# ============================================================
# Interest Recording
# ============================================================

def test_record_interest_application(time_deposit_account):

    today = datetime.now(UTC).date()

    time_deposit_account.record_interest_application(today)

    assert (
        time_deposit_account.last_interest_date
        == today
    )

# ============================================================
# Serialization
# ============================================================

def test_to_dict(time_deposit_account):

    data = time_deposit_account.to_dict()

    assert isinstance(data, dict)


def test_from_dict(time_deposit_account):

    restored = TimeDepositAccount.from_dict(
        time_deposit_account.to_dict()
    )

    assert restored == time_deposit_account


def test_serialization_preserves_principal(
    time_deposit_account
):

    restored = TimeDepositAccount.from_dict(
        time_deposit_account.to_dict()
    )

    assert (
        restored.principal
        == time_deposit_account.principal
    )

# ============================================================
# Reporting
# ============================================================

def test_maturity_summary(time_deposit_account):

    summary = time_deposit_account.maturity_summary()

    assert isinstance(summary, dict)


def test_investment_summary(time_deposit_account):

    summary = time_deposit_account.investment_summary()

    assert isinstance(summary, dict)


def test_summary_contains_maturity_value(
    time_deposit_account
):

    summary = time_deposit_account.maturity_summary()

    assert "maturity_value" in summary

# ============================================================
# Representation
# ============================================================

def test_time_deposit_str(time_deposit_account):

    assert "Time Deposit" in str(time_deposit_account)


def test_time_deposit_repr(time_deposit_account):

    assert "TimeDepositAccount" in repr(time_deposit_account)


def test_hash(time_deposit_account):

    assert hash(time_deposit_account)


def test_equality(time_deposit_account):

    clone = TimeDepositAccount.from_dict(
        time_deposit_account.to_dict()
    )

    clone._entity_id = time_deposit_account.entity_id

    assert clone == time_deposit_account

# ============================================================
# Boundary Cases
# ============================================================

def test_large_term_interest():

    account = TimeDepositAccount(
        account_number="TD999",
        customer_id="C1",
        opening_balance=Money("100000"),
        interest_rate=Decimal("0.10"),
        term_months=60,
        early_withdrawal_penalty_rate=Decimal("0.10"),
    )

    assert account.calculate_interest() > Money("0")


def test_zero_penalty_allowed(time_deposit_account):

    time_deposit_account.update_penalty_rate(
        Decimal("0.00")
    )

    assert (
        time_deposit_account
        .early_withdrawal_penalty_rate
        == Decimal("0.00")
    )

# Part 5

# ============================================================
# Fixtures
# ============================================================

@pytest.fixture
def transaction():

    return Transaction(
        transaction_number="TXN000001",
        transaction_type=TransactionType.DEPOSIT,
        amount=Money("500.00"),
        source_account=None,
        destination_account="SA100001",
        initiated_by="tester",
        description="Initial Deposit",
        reference_number="REF001",
    )

# ============================================================
# Construction
# ============================================================

def test_create_transaction(transaction):

    assert transaction.transaction_number == "TXN000001"


def test_transaction_amount(transaction):

    assert transaction.amount == Money("500.00")


def test_transaction_type(transaction):

    assert transaction.transaction_type == TransactionType.DEPOSIT


def test_transaction_status_default(transaction):

    assert transaction.transaction_status == TransactionStatus.COMPLETED


def test_reference_number(transaction):

    assert transaction.reference_number == "REF001"


def test_transaction_date_initialized(transaction):

    assert transaction.transaction_date is not None

# ============================================================
# Validation
# ============================================================

def test_invalid_transaction_type():

    with pytest.raises(TypeError):

        Transaction(
            transaction_number="TXN1",
            transaction_type="DEPOSIT",
            amount=Money("10"),
            source_account=None,
            destination_account="A1",
            initiated_by="tester",
        )


def test_invalid_amount():

    with pytest.raises(TypeError):

        Transaction(
            transaction_number="TXN1",
            transaction_type=TransactionType.DEPOSIT,
            amount=Decimal("10"),
            source_account=None,
            destination_account="A1",
            initiated_by="tester",
        )


def test_missing_initiated_by():

    with pytest.raises(ValueError):

        Transaction(
            transaction_number="TXN1",
            transaction_type=TransactionType.DEPOSIT,
            amount=Money("10"),
            source_account=None,
            destination_account="A1",
            initiated_by="",
        )

# ============================================================
# Status Helpers
# ============================================================

def test_mark_pending(transaction):

    transaction.mark_pending()

    assert transaction.is_pending()


def test_mark_completed(transaction):

    transaction.mark_completed()

    assert transaction.is_completed()


def test_mark_failed(transaction):

    transaction.mark_failed()

    assert transaction.is_failed()


def test_mark_reversed(transaction):

    transaction.mark_reversed()

    assert transaction.is_reversed()

# ============================================================
# Approval
# ============================================================

def test_approve(transaction):

    transaction.mark_pending()

    transaction.approve("manager")

    assert transaction.approved_by == "manager"

    assert transaction.is_completed()

# ============================================================
# Classification
# ============================================================

def test_is_deposit(transaction):

    assert transaction.is_deposit()


def test_is_credit(transaction):

    assert transaction.is_credit()


def test_is_financial(transaction):

    assert transaction.is_financial_transaction()


def test_requires_approval(transaction):

    assert transaction.requires_approval() is False

# ============================================================
# Account Helpers
# ============================================================

def test_affects_destination_account(transaction):

    assert transaction.affects_account("SA100001")


def test_not_affect_other_account(transaction):

    assert transaction.affects_account("SA999999") is False

# ============================================================
# Serialization
# ============================================================

def test_to_dict(transaction):

    data = transaction.to_dict()

    assert isinstance(data, dict)


def test_from_dict(transaction):

    restored = Transaction.from_dict(
        transaction.to_dict()
    )

    assert restored == transaction


def test_serialization_preserves_amount(transaction):

    restored = Transaction.from_dict(
        transaction.to_dict()
    )

    assert restored.amount == transaction.amount

# ============================================================
# Reporting
# ============================================================

def test_summary(transaction):

    summary = transaction.summary()

    assert isinstance(summary, dict)


def test_audit_summary(transaction):

    audit = transaction.audit_summary()

    assert isinstance(audit, dict)


def test_summary_contains_status(transaction):

    summary = transaction.summary()

    assert "status" in summary

# ============================================================
# Display
# ============================================================

def test_display_name(transaction):

    assert isinstance(
        transaction.display_name(),
        str,
    )


def test_display_amount(transaction):

    assert isinstance(
        transaction.display_amount(),
        str,
    )


def test_display_status(transaction):

    assert isinstance(
        transaction.display_status(),
        str,
    )


def test_display_summary(transaction):

    assert isinstance(
        transaction.display_summary(),
        str,
    )

# ============================================================
# Reversal
# ============================================================

def test_can_reverse(transaction):

    assert transaction.can_reverse()


def test_clone_for_reversal(transaction):

    reversal = transaction.clone_for_reversal(
        transaction_number="TXN000002",
        initiated_by="admin",
    )

    assert reversal.reference_number == "REF001"

    assert reversal.source_account == transaction.destination_account

    assert (
        reversal.destination_account
        == transaction.source_account
    )

# ============================================================
# Representation
# ============================================================

def test_transaction_str(transaction):

    assert "TXN000001" in str(transaction)


def test_transaction_repr(transaction):

    assert "Transaction(" in repr(transaction)


def test_transaction_hash(transaction):

    assert hash(transaction)


def test_transaction_equality(transaction):

    clone = Transaction.from_dict(
        transaction.to_dict()
    )

    clone._entity_id = transaction.entity_id

    assert clone == transaction

# ============================================================
# Boundary Cases
# ============================================================

def test_large_amount():

    tx = Transaction(
        transaction_number="BIG1",
        transaction_type=TransactionType.DEPOSIT,
        amount=Money("999999999.99"),
        source_account=None,
        destination_account="ACC1",
        initiated_by="tester",
    )

    assert tx.amount.amount > Decimal("1000000")


def test_zero_amount():

    tx = Transaction(
        transaction_number="ZERO1",
        transaction_type=TransactionType.DEPOSIT,
        amount=Money.zero(),
        source_account=None,
        destination_account="ACC1",
        initiated_by="tester",
    )

    assert tx.amount.amount == Decimal("0")


