"""
============================================================
Account Service Tests
Part 1
------------------------------------------------------------
Coverage

• Service construction
• Dependency injection
• Savings account opening
• Current account opening
• Time deposit opening
• Duplicate account prevention
• Customer validation
============================================================
"""

import pytest

from services.account_service import AccountService

from repositories.account_repository import AccountRepository
from repositories.customer_repository import CustomerRepository

from models.customer import Customer
from models.savings_account import SavingsAccount
from models.current_account import CurrentAccount
from models.time_deposit_account import TimeDepositAccount

from models.value_objects.address import Address
from models.value_objects.email import EmailAddress
from models.value_objects.money import Money
from models.value_objects.phone import PhoneNumber

from exceptions.banking_exceptions import (
    DuplicateAccountError,
    CustomerNotFoundError,
    ValidationError,
)

# ============================================================
# Fixtures
# ============================================================

@pytest.fixture
def customer_repository(tmp_path):

    return CustomerRepository(
        storage_path=tmp_path / "customers.csv"
    )


@pytest.fixture
def account_repository(tmp_path):

    return AccountRepository(
        storage_path=tmp_path / "accounts.csv"
    )


@pytest.fixture
def service(
    account_repository,
    customer_repository,
):

    return AccountService(
        account_repository=account_repository,
        customer_repository=customer_repository,
    )


@pytest.fixture
def customer(customer_repository):

    customer = Customer(

        customer_id="CUST000001",

        first_name="John",

        middle_name="A",

        last_name="Smith",

        national_id="1234567890",

        email=EmailAddress("john@test.com"),

        phone=PhoneNumber("+966501234567"),

        address=Address(

            street="King Road",

            city="Riyadh",

            state="Riyadh",

            postal_code="12345",

            country="Saudi Arabia",

        ),
    )

    customer_repository.add(customer)

    return customer

# ============================================================
# Service Construction
# ============================================================

def test_service_created(service):

    assert service is not None


def test_account_repository_injected(
    service,
    account_repository,
):

    assert service.account_repository is account_repository


def test_customer_repository_injected(
    service,
    customer_repository,
):

    assert service.customer_repository is customer_repository


def test_empty_repository(service):

    assert service.account_count() == 0

# ============================================================
# Savings Account Opening
# ============================================================

def test_open_savings_account(
    service,
    customer,
):

    account = service.open_savings_account(

        customer_id=customer.customer_id,

        account_number="SA100001",

        opening_balance=Money("1000"),

    )

    assert isinstance(
        account,
        SavingsAccount,
    )

    assert service.account_count() == 1


def test_open_savings_initial_balance(
    service,
    customer,
):

    account = service.open_savings_account(

        customer.customer_id,

        "SA100002",

        Money("5000"),

    )

    assert account.balance == Money("5000")

# ============================================================
# Current Account Opening
# ============================================================

def test_open_current_account(
    service,
    customer,
):

    account = service.open_current_account(

        customer.customer_id,

        "CA100001",

        Money("2000"),

    )

    assert isinstance(
        account,
        CurrentAccount,
    )


def test_current_account_registered(
    service,
    customer,
):

    account = service.open_current_account(

        customer.customer_id,

        "CA100002",

        Money("1500"),

    )

    stored = service.get_account(
        account.account_number
    )

    assert stored == account

# ============================================================
# Current Account Opening
# ============================================================

def test_open_current_account(
    service,
    customer,
):

    account = service.open_current_account(

        customer.customer_id,

        "CA100001",

        Money("2000"),

    )

    assert isinstance(
        account,
        CurrentAccount,
    )


def test_current_account_registered(
    service,
    customer,
):

    account = service.open_current_account(

        customer.customer_id,

        "CA100002",

        Money("1500"),

    )

    stored = service.get_account(
        account.account_number
    )

    assert stored == account

# ============================================================
# Duplicate Accounts
# ============================================================

def test_duplicate_account_number(
    service,
    customer,
):

    service.open_savings_account(

        customer.customer_id,

        "SA999999",

        Money("1000"),

    )

    with pytest.raises(
        DuplicateAccountError
    ):

        service.open_savings_account(

            customer.customer_id,

            "SA999999",

            Money("500"),

        )

# ============================================================
# Duplicate Accounts
# ============================================================

def test_duplicate_account_number(
    service,
    customer,
):

    service.open_savings_account(

        customer.customer_id,

        "SA999999",

        Money("1000"),

    )

    with pytest.raises(
        DuplicateAccountError
    ):

        service.open_savings_account(

            customer.customer_id,

            "SA999999",

            Money("500"),

        )


# PART 2

# ============================================================
# Deposit Operations
# ============================================================

def test_deposit(
    service,
    customer,
):

    account = service.open_savings_account(

        customer.customer_id,

        "SA100001",

        Money("1000"),

    )

    service.deposit(

        account.account_number,

        Money("500"),

    )

    updated = service.get_account(
        account.account_number
    )

    assert updated.balance == Money("1500")


def test_multiple_deposits(
    service,
    customer,
):

    account = service.open_savings_account(

        customer.customer_id,

        "SA100002",

        Money("1000"),

    )

    service.deposit(
        account.account_number,
        Money("100"),
    )

    service.deposit(
        account.account_number,
        Money("200"),
    )

    service.deposit(
        account.account_number,
        Money("300"),
    )

    assert (
        service.get_account(
            account.account_number
        ).balance
        == Money("1600")
    )


def test_deposit_zero_amount(
    service,
    customer,
):

    account = service.open_savings_account(

        customer.customer_id,

        "SA100003",

        Money("1000"),

    )

    with pytest.raises(
        ValidationError
    ):

        service.deposit(

            account.account_number,

            Money.zero(),

        )


def test_deposit_negative_amount(
    service,
    customer,
):

    account = service.open_savings_account(

        customer.customer_id,

        "SA100004",

        Money("1000"),

    )

    with pytest.raises(
        ValidationError
    ):

        service.deposit(

            account.account_number,

            Money("-100"),

        )

# ============================================================
# Withdrawal Operations
# ============================================================

def test_withdraw(
    service,
    customer,
):

    account = service.open_savings_account(

        customer.customer_id,

        "SA200001",

        Money("1000"),

    )

    service.withdraw(

        account.account_number,

        Money("250"),

    )

    assert (

        service.get_account(

            account.account_number

        ).balance

        == Money("750")

    )


def test_multiple_withdrawals(
    service,
    customer,
):

    account = service.open_savings_account(

        customer.customer_id,

        "SA200002",

        Money("2000"),

    )

    service.withdraw(
        account.account_number,
        Money("100"),
    )

    service.withdraw(
        account.account_number,
        Money("300"),
    )

    service.withdraw(
        account.account_number,
        Money("500"),
    )

    assert (

        service.get_account(

            account.account_number

        ).balance

        == Money("1100")

    )

# ============================================================
# Insufficient Funds
# ============================================================

def test_withdraw_more_than_balance(
    service,
    customer,
):

    account = service.open_savings_account(

        customer.customer_id,

        "SA300001",

        Money("500"),

    )

    with pytest.raises(

        ValueError

    ):

        service.withdraw(

            account.account_number,

            Money("600"),

        )


def test_withdraw_entire_balance(
    service,
    customer,
):

    account = service.open_savings_account(

        customer.customer_id,

        "SA300002",

        Money("500"),

    )

    service.withdraw(

        account.account_number,

        Money("500"),

    )

    assert (

        service.get_account(

            account.account_number

        ).balance

        == Money.zero()

    )

# ============================================================
# Invalid Withdrawals
# ============================================================

def test_withdraw_zero_amount(
    service,
    customer,
):

    account = service.open_savings_account(

        customer.customer_id,

        "SA400001",

        Money("1000"),

    )

    with pytest.raises(
        ValidationError
    ):

        service.withdraw(

            account.account_number,

            Money.zero(),

        )


def test_withdraw_negative_amount(
    service,
    customer,
):

    account = service.open_savings_account(

        customer.customer_id,

        "SA400002",

        Money("1000"),

    )

    with pytest.raises(
        ValidationError
    ):

        service.withdraw(

            account.account_number,

            Money("-10"),

        )


def test_withdraw_unknown_account(
    service,
):

    with pytest.raises(

        KeyError

    ):

        service.withdraw(

            "UNKNOWN",

            Money("100"),

        )

# ============================================================
# Balance Integrity
# ============================================================

def test_balance_after_sequence(
    service,
    customer,
):

    account = service.open_savings_account(

        customer.customer_id,

        "SA500001",

        Money("1000"),

    )

    service.deposit(

        account.account_number,

        Money("300"),

    )

    service.withdraw(

        account.account_number,

        Money("100"),

    )

    service.deposit(

        account.account_number,

        Money("200"),

    )

    service.withdraw(

        account.account_number,

        Money("50"),

    )

    assert (

        service.get_account(

            account.account_number

        ).balance

        == Money("1350")

    )


def test_balance_never_negative(
    service,
    customer,
):

    account = service.open_savings_account(

        customer.customer_id,

        "SA500002",

        Money("100"),

    )

    with pytest.raises(
        ValueError
    ):

        service.withdraw(

            account.account_number,

            Money("200"),

        )

    assert (

        service.get_account(

            account.account_number

        ).balance

        == Money("100")

    )

# ============================================================
# Repository Synchronization
# ============================================================

def test_repository_updated_after_deposit(
    service,
    customer,
):

    account = service.open_savings_account(

        customer.customer_id,

        "SA600001",

        Money("1000"),

    )

    service.deposit(

        account.account_number,

        Money("500"),

    )

    repository_account = service.account_repository.get(

        account.account_number

    )

    assert repository_account.balance == Money("1500")


def test_repository_updated_after_withdrawal(
    service,
    customer,
):

    account = service.open_savings_account(

        customer.customer_id,

        "SA600002",

        Money("1000"),

    )

    service.withdraw(

        account.account_number,

        Money("200"),

    )

    repository_account = service.account_repository.get(

        account.account_number

    )

    assert repository_account.balance == Money("800")

# PART 3

# ============================================================
# Transfer Fixtures
# ============================================================

@pytest.fixture
def source_account(
    service,
    customer,
):

    return service.open_savings_account(

        customer.customer_id,

        "SA700001",

        Money("5000"),

    )


@pytest.fixture
def destination_account(
    service,
    customer,
):

    return service.open_savings_account(

        customer.customer_id,

        "SA700002",

        Money("1000"),

    )

# ============================================================
# Successful Transfers
# ============================================================

def test_transfer_between_accounts(
    service,
    source_account,
    destination_account,
):

    service.transfer(

        source_account.account_number,

        destination_account.account_number,

        Money("500"),

    )

    source = service.get_account(
        source_account.account_number
    )

    destination = service.get_account(
        destination_account.account_number
    )

    assert source.balance == Money("4500")

    assert destination.balance == Money("1500")


def test_multiple_transfers(
    service,
    source_account,
    destination_account,
):

    service.transfer(
        source_account.account_number,
        destination_account.account_number,
        Money("100"),
    )

    service.transfer(
        source_account.account_number,
        destination_account.account_number,
        Money("200"),
    )

    service.transfer(
        source_account.account_number,
        destination_account.account_number,
        Money("300"),
    )

    assert (
        service.get_account(
            source_account.account_number
        ).balance
        == Money("4400")
    )

    assert (
        service.get_account(
            destination_account.account_number
        ).balance
        == Money("1600")
    )

# ============================================================
# Invalid Transfers
# ============================================================

def test_transfer_zero_amount(
    service,
    source_account,
    destination_account,
):

    with pytest.raises(
        ValidationError
    ):

        service.transfer(

            source_account.account_number,

            destination_account.account_number,

            Money.zero(),

        )


def test_transfer_negative_amount(
    service,
    source_account,
    destination_account,
):

    with pytest.raises(
        ValidationError
    ):

        service.transfer(

            source_account.account_number,

            destination_account.account_number,

            Money("-100"),

        )


def test_transfer_to_same_account(
    service,
    source_account,
):

    with pytest.raises(
        ValidationError
    ):

        service.transfer(

            source_account.account_number,

            source_account.account_number,

            Money("100"),

        )

# ============================================================
# Unknown Accounts
# ============================================================

def test_transfer_unknown_source(
    service,
    destination_account,
):

    with pytest.raises(
        KeyError
    ):

        service.transfer(

            "UNKNOWN",

            destination_account.account_number,

            Money("100"),

        )


def test_transfer_unknown_destination(
    service,
    source_account,
):

    with pytest.raises(
        KeyError
    ):

        service.transfer(

            source_account.account_number,

            "UNKNOWN",

            Money("100"),

        )

# ============================================================
# Insufficient Funds
# ============================================================

def test_transfer_insufficient_funds(
    service,
    source_account,
    destination_account,
):

    with pytest.raises(
        ValueError
    ):

        service.transfer(

            source_account.account_number,

            destination_account.account_number,

            Money("10000"),

        )


def test_failed_transfer_preserves_balances(
    service,
    source_account,
    destination_account,
):

    original_source = source_account.balance

    original_destination = destination_account.balance

    with pytest.raises(
        ValueError
    ):

        service.transfer(

            source_account.account_number,

            destination_account.account_number,

            Money("999999"),

        )

    assert (

        service.get_account(
            source_account.account_number
        ).balance

        == original_source

    )

    assert (

        service.get_account(
            destination_account.account_number
        ).balance

        == original_destination

    )

# ============================================================
# Atomicity
# ============================================================

def test_transfer_is_atomic(
    service,
    source_account,
    destination_account,
):

    before_source = source_account.balance

    before_destination = destination_account.balance

    try:

        service.transfer(

            source_account.account_number,

            destination_account.account_number,

            Money("999999"),

        )

    except Exception:

        pass

    after_source = service.get_account(
        source_account.account_number
    ).balance

    after_destination = service.get_account(
        destination_account.account_number
    ).balance

    assert before_source == after_source

    assert before_destination == after_destination

# ============================================================
# Repository Synchronization
# ============================================================

def test_transfer_updates_repository(
    service,
    source_account,
    destination_account,
):

    service.transfer(

        source_account.account_number,

        destination_account.account_number,

        Money("250"),

    )

    source = service.account_repository.get(
        source_account.account_number
    )

    destination = service.account_repository.get(
        destination_account.account_number
    )

    assert source.balance == Money("4750")

    assert destination.balance == Money("1250")

# ============================================================
# Sequential Transfers
# ============================================================

def test_many_small_transfers(
    service,
    source_account,
    destination_account,
):

    for _ in range(20):

        service.transfer(

            source_account.account_number,

            destination_account.account_number,

            Money("10"),

        )

    assert (

        service.get_account(
            source_account.account_number
        ).balance

        == Money("4800")

    )

    assert (

        service.get_account(
            destination_account.account_number
        ).balance

        == Money("1200")

    )

# PART 4

# ============================================================
# Savings Interest
# ============================================================

def test_apply_interest(
    service,
    customer,
):

    account = service.open_savings_account(

        customer.customer_id,

        "SA800001",

        Money("10000"),

    )

    original = account.balance

    service.apply_interest(
        account.account_number
    )

    updated = service.get_account(
        account.account_number
    )

    assert updated.balance > original


def test_interest_never_decreases_balance(
    service,
    customer,
):

    account = service.open_savings_account(

        customer.customer_id,

        "SA800002",

        Money("5000"),

    )

    before = account.balance

    service.apply_interest(
        account.account_number
    )

    after = service.get_account(
        account.account_number
    ).balance

    assert after >= before

# ============================================================
# Service Charges
# ============================================================

def test_apply_service_fee(
    service,
    customer,
):

    account = service.open_current_account(

        customer.customer_id,

        "CA800001",

        Money("2000"),

    )

    before = account.balance

    service.apply_service_fee(
        account.account_number
    )

    after = service.get_account(
        account.account_number
    ).balance

    assert after < before


def test_service_fee_updates_repository(
    service,
    customer,
):

    account = service.open_current_account(

        customer.customer_id,

        "CA800002",

        Money("2000"),

    )

    service.apply_service_fee(
        account.account_number
    )

    repository_account = service.account_repository.get(
        account.account_number
    )

    assert (
        repository_account.balance
        ==
        service.get_account(
            account.account_number
        ).balance
    )

# ============================================================
# Minimum Balance Rules
# ============================================================

def test_cannot_violate_minimum_balance(
    service,
    customer,
):

    account = service.open_savings_account(

        customer.customer_id,

        "SA900001",

        Money("1000"),

    )

    with pytest.raises(
        ValueError
    ):

        service.withdraw(

            account.account_number,

            Money("950"),

        )


def test_minimum_balance_preserved(
    service,
    customer,
):

    account = service.open_savings_account(

        customer.customer_id,

        "SA900002",

        Money("1000"),

    )

    try:

        service.withdraw(

            account.account_number,

            Money("950"),

        )

    except Exception:

        pass

    assert (

        service.get_account(
            account.account_number
        ).balance

        >=

        account.minimum_balance

    )

# ============================================================
# Overdraft Protection
# ============================================================

def test_current_account_overdraft_limit(
    service,
    customer,
):

    account = service.open_current_account(

        customer.customer_id,

        "CA900001",

        Money("1000"),

    )

    with pytest.raises(
        ValueError
    ):

        service.withdraw(

            account.account_number,

            Money("100000"),

        )


def test_savings_account_no_overdraft(
    service,
    customer,
):

    account = service.open_savings_account(

        customer.customer_id,

        "SA900003",

        Money("500"),

    )

    with pytest.raises(
        ValueError
    ):

        service.withdraw(

            account.account_number,

            Money("1000"),

        )

# ============================================================
# Time Deposit Rules
# ============================================================

def test_time_deposit_cannot_withdraw_before_maturity(
    service,
    customer,
):

    account = service.open_time_deposit_account(

        customer.customer_id,

        "TD900001",

        Money("10000"),

        term_months=12,

    )

    with pytest.raises(
        ValueError
    ):

        service.withdraw(

            account.account_number,

            Money("1000"),

        )


def test_time_deposit_maturity_check(
    service,
    customer,
):

    account = service.open_time_deposit_account(

        customer.customer_id,

        "TD900002",

        Money("5000"),

        term_months=6,

    )

    assert (
        account.is_matured()
        is False
    )

# ============================================================
# Interest Consistency
# ============================================================

def test_interest_updates_repository(
    service,
    customer,
):

    account = service.open_savings_account(

        customer.customer_id,

        "SA910001",

        Money("10000"),

    )

    service.apply_interest(
        account.account_number
    )

    repository_account = service.account_repository.get(
        account.account_number
    )

    service_account = service.get_account(
        account.account_number
    )

    assert (
        repository_account.balance
        ==
        service_account.balance
    )


def test_multiple_interest_applications(
    service,
    customer,
):

    account = service.open_savings_account(

        customer.customer_id,

        "SA910002",

        Money("10000"),

    )

    service.apply_interest(
        account.account_number
    )

    first = service.get_account(
        account.account_number
    ).balance

    service.apply_interest(
        account.account_number
    )

    second = service.get_account(
        account.account_number
    ).balance

    assert second >= first

# ============================================================
# Account Integrity
# ============================================================

def test_balance_never_negative_after_fees(
    service,
    customer,
):

    account = service.open_current_account(

        customer.customer_id,

        "CA910001",

        Money("100"),

    )

    try:

        for _ in range(20):

            service.apply_service_fee(
                account.account_number
            )

    except Exception:

        pass

    assert (
        service.get_account(
            account.account_number
        ).balance
        >= Money.zero()
    )

# PART 5

# ============================================================
# Account Closure
# ============================================================

def test_close_savings_account(
    service,
    customer,
):

    account = service.open_savings_account(

        customer.customer_id,

        "SA100001",

        Money("1000"),

    )

    service.close_account(
        account.account_number
    )

    assert (
        service.account_exists(
            account.account_number
        )
        is False
    )


def test_close_current_account(
    service,
    customer,
):

    account = service.open_current_account(

        customer.customer_id,

        "CA100001",

        Money("1500"),

    )

    service.close_account(
        account.account_number
    )

    assert (
        service.account_count() == 0
    )


def test_close_time_deposit_account(
    service,
    customer,
):

    account = service.open_time_deposit_account(

        customer.customer_id,

        "TD100001",

        Money("10000"),

        term_months=12,

    )

    service.close_account(
        account.account_number
    )

    assert (
        service.account_exists(
            account.account_number
        )
        is False
    )

# ============================================================
# Invalid Account Closure
# ============================================================

def test_close_unknown_account(
    service,
):

    with pytest.raises(KeyError):

        service.close_account(
            "UNKNOWN"
        )


def test_close_none_account(
    service,
):

    with pytest.raises(
        ValidationError
    ):

        service.close_account(None)

# ============================================================
# Save / Load
# ============================================================

def test_save_accounts(
    service,
    customer,
):

    service.open_savings_account(

        customer.customer_id,

        "SA200001",

        Money("3000"),

    )

    service.save()

    assert (
        service.account_repository.storage_path.exists()
    )


def test_load_accounts(
    tmp_path,
    customer,
):

    path = tmp_path / "accounts.csv"

    repository = AccountRepository(
        storage_path=path
    )

    service1 = AccountService(
        repository,
        CustomerRepository(
            storage_path=tmp_path / "customers.csv"
        ),
    )

    service1.customer_repository.add(customer)

    service1.open_savings_account(

        customer.customer_id,

        "SA200002",

        Money("5000"),

    )

    service1.save()

    repository2 = AccountRepository(
        storage_path=path
    )

    service2 = AccountService(
        repository2,
        service1.customer_repository,
    )

    service2.load()

    assert service2.account_count() == 1

# ============================================================
# Reload Integrity
# ============================================================

def test_reload_preserves_balance(
    tmp_path,
    customer,
):

    path = tmp_path / "accounts.csv"

    repository = AccountRepository(
        storage_path=path
    )

    customer_repo = CustomerRepository(
        storage_path=tmp_path / "customers.csv"
    )

    customer_repo.add(customer)

    service = AccountService(
        repository,
        customer_repo,
    )

    account = service.open_savings_account(

        customer.customer_id,

        "SA300001",

        Money("2500"),

    )

    service.deposit(
        account.account_number,
        Money("500"),
    )

    service.save()

    repository2 = AccountRepository(
        storage_path=path
    )

    service2 = AccountService(
        repository2,
        customer_repo,
    )

    service2.load()

    loaded = service2.get_account(
        account.account_number
    )

    assert loaded.balance == Money("3000")

# ============================================================
# Persistence after Transactions
# ============================================================

def test_save_after_transfer(
    service,
    customer,
):

    source = service.open_savings_account(

        customer.customer_id,

        "SA400001",

        Money("2000"),

    )

    destination = service.open_savings_account(

        customer.customer_id,

        "SA400002",

        Money("500"),

    )

    service.transfer(

        source.account_number,

        destination.account_number,

        Money("300"),

    )

    service.save()

    assert (
        service.account_repository.storage_path.exists()
    )


def test_save_after_interest(
    service,
    customer,
):

    account = service.open_savings_account(

        customer.customer_id,

        "SA400003",

        Money("10000"),

    )

    service.apply_interest(
        account.account_number
    )

    service.save()

    assert (
        service.account_repository.storage_path.exists()
    )

# ============================================================
# Repository Synchronization
# ============================================================

def test_repository_after_close(
    service,
    customer,
):

    account = service.open_savings_account(

        customer.customer_id,

        "SA500001",

        Money("1000"),

    )

    service.close_account(
        account.account_number
    )

    assert (
        service.account_repository.count()
        == 0
    )


def test_repository_after_save(
    service,
    customer,
):

    account = service.open_savings_account(

        customer.customer_id,

        "SA500002",

        Money("5000"),

    )

    service.save()

    stored = service.account_repository.get(
        account.account_number
    )

    assert stored == account

# ============================================================
# Lifecycle Operations
# ============================================================

def test_open_update_close_cycle(
    service,
    customer,
):

    account = service.open_savings_account(

        customer.customer_id,

        "SA600001",

        Money("1000"),

    )

    service.deposit(
        account.account_number,
        Money("500"),
    )

    service.withdraw(
        account.account_number,
        Money("250"),
    )

    service.close_account(
        account.account_number
    )

    assert service.account_count() == 0


def test_multiple_accounts_lifecycle(
    service,
    customer,
):

    for i in range(5):

        account = service.open_savings_account(

            customer.customer_id,

            f"SA60000{i}",

            Money("1000"),

        )

        service.deposit(
            account.account_number,
            Money("100"),
        )

    service.save()

    assert service.account_count() == 5


# PART 6

# ============================================================
# Reporting
# ============================================================

def test_account_summary_empty(service):

    summary = service.account_summary()

    assert isinstance(summary, dict)

    assert summary["total_accounts"] == 0


def test_account_summary_single_account(
    service,
    customer,
):

    service.open_savings_account(

        customer.customer_id,

        "SA700001",

        Money("1000"),

    )

    summary = service.account_summary()

    assert summary["total_accounts"] == 1


def test_account_summary_multiple_accounts(
    service,
    customer,
):

    service.open_savings_account(
        customer.customer_id,
        "SA700002",
        Money("1000"),
    )

    service.open_current_account(
        customer.customer_id,
        "CA700001",
        Money("2000"),
    )

    service.open_time_deposit_account(
        customer.customer_id,
        "TD700001",
        Money("5000"),
        term_months=12,
    )

    summary = service.account_summary()

    assert summary["total_accounts"] == 3

# ============================================================
# Search Operations
# ============================================================

def test_find_account(
    service,
    customer,
):

    account = service.open_savings_account(

        customer.customer_id,

        "SA800001",

        Money("1000"),

    )

    found = service.get_account(
        account.account_number
    )

    assert found == account


def test_find_unknown_account(
    service,
):

    assert (
        service.get_account("UNKNOWN")
        is None
    )


def test_account_exists(
    service,
    customer,
):

    account = service.open_current_account(

        customer.customer_id,

        "CA800001",

        Money("2000"),

    )

    assert service.account_exists(
        account.account_number
    )


def test_account_not_exists(
    service,
):

    assert (
        service.account_exists(
            "UNKNOWN"
        )
        is False
    )

# ============================================================
# Collection Operations
# ============================================================

def test_get_all_accounts(
    service,
    customer,
):

    for i in range(5):

        service.open_savings_account(

            customer.customer_id,

            f"SA90000{i}",

            Money("1000"),

        )

    accounts = service.get_all_accounts()

    assert len(accounts) == 5


def test_account_count(
    service,
    customer,
):

    service.open_savings_account(

        customer.customer_id,

        "SA900010",

        Money("1000"),

    )

    assert service.account_count() == 1

# ============================================================
# Helper Methods
# ============================================================

def test_service_length(
    service,
    customer,
):

    service.open_savings_account(

        customer.customer_id,

        "SA910001",

        Money("1000"),

    )

    assert len(service) == 1


def test_service_boolean_empty(
    service,
):

    assert bool(service) is False


def test_service_boolean_non_empty(
    service,
    customer,
):

    service.open_current_account(

        customer.customer_id,

        "CA910001",

        Money("500"),

    )

    assert bool(service) is True

# ============================================================
# Iterator Support
# ============================================================

def test_iteration(
    service,
    customer,
):

    for i in range(10):

        service.open_savings_account(

            customer.customer_id,

            f"SA9200{i}",

            Money("100"),

        )

    count = 0

    for account in service:

        assert account is not None
        count += 1

    assert count == 10

# ============================================================
# Stress Testing
# ============================================================

def test_create_100_accounts(
    service,
    customer,
):

    for i in range(100):

        service.open_savings_account(

            customer.customer_id,

            f"SA{i:05}",

            Money("100"),

        )

    assert service.account_count() == 100


def test_mass_deposit(
    service,
    customer,
):

    account = service.open_savings_account(

        customer.customer_id,

        "SA930001",

        Money("0"),

    )

    for _ in range(100):

        service.deposit(

            account.account_number,

            Money("10"),

        )

    assert (

        service.get_account(
            account.account_number
        ).balance

        == Money("1000")

    )


def test_mass_withdrawals(
    service,
    customer,
):

    account = service.open_savings_account(

        customer.customer_id,

        "SA930002",

        Money("1000"),

    )

    for _ in range(20):

        service.withdraw(

            account.account_number,

            Money("10"),

        )

    assert (

        service.get_account(
            account.account_number
        ).balance

        == Money("800")

    )

# ============================================================
# Repository Consistency
# ============================================================

def test_repository_matches_service(
    service,
    customer,
):

    service.open_savings_account(

        customer.customer_id,

        "SA940001",

        Money("1000"),

    )

    assert (

        service.account_repository.count()

        ==

        service.account_count()

    )


def test_repository_get_all_matches_service(
    service,
    customer,
):

    service.open_current_account(

        customer.customer_id,

        "CA940001",

        Money("500"),

    )

    assert (

        service.account_repository.get_all()

        ==

        service.get_all_accounts()

    )

# ============================================================
# Edge Cases
# ============================================================

def test_empty_service_accounts(
    service,
):

    assert service.get_all_accounts() == []


def test_empty_account_count(
    service,
):

    assert service.account_count() == 0


def test_clear_service(
    service,
    customer,
):

    for i in range(5):

        service.open_savings_account(

            customer.customer_id,

            f"SA9500{i}",

            Money("100"),

        )

    service.clear()

    assert service.account_count() == 0

