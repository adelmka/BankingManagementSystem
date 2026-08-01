"""
============================================================
Transaction Service Tests
Part 1
------------------------------------------------------------
Coverage

• Service construction
• Dependency injection
• Transaction creation
• Deposit transaction recording
• Withdrawal transaction recording
• Transfer transaction recording
• Transaction retrieval
============================================================
"""

import pytest

from services.transaction_service import TransactionService

from repositories.transaction_repository import TransactionRepository
from repositories.account_repository import AccountRepository
from repositories.customer_repository import CustomerRepository

from models.customer import Customer
from models.savings_account import SavingsAccount
from models.transaction import Transaction

from models.value_objects.money import Money
from models.value_objects.email import EmailAddress
from models.value_objects.phone import PhoneNumber
from models.value_objects.address import Address

from exceptions.banking_exceptions import (
    ValidationError,
    DuplicateTransactionError,
)

test_transaction_service.py

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
def transaction_repository(tmp_path):

    return TransactionRepository(
        storage_path=tmp_path / "transactions.csv"
    )


@pytest.fixture
def service(
    transaction_repository,
    account_repository,
):

    return TransactionService(
        transaction_repository=transaction_repository,
        account_repository=account_repository,
    )


@pytest.fixture
def customer(customer_repository):

    customer = Customer(

        customer_id="CUST000001",

        first_name="John",

        middle_name="",

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


@pytest.fixture
def account(
    account_repository,
    customer,
):

    account = SavingsAccount(

        account_number="SA100001",

        customer_id=customer.customer_id,

        balance=Money("5000"),

    )

    account_repository.add(account)

    return account

# ============================================================
# Service Construction
# ============================================================

def test_service_created(service):

    assert service is not None


def test_transaction_repository_injected(
    service,
    transaction_repository,
):

    assert (
        service.transaction_repository
        is transaction_repository
    )


def test_account_repository_injected(
    service,
    account_repository,
):

    assert (
        service.account_repository
        is account_repository
    )


def test_empty_repository(service):

    assert service.transaction_count() == 0

# ============================================================
# Deposit Transactions
# ============================================================

def test_record_deposit(
    service,
    account,
):

    transaction = service.record_deposit(

        account.account_number,

        Money("1000"),

    )

    assert isinstance(
        transaction,
        Transaction,
    )

    assert (
        service.transaction_count() == 1
    )


def test_record_deposit_amount(
    service,
    account,
):

    transaction = service.record_deposit(

        account.account_number,

        Money("250"),

    )

    assert transaction.amount == Money("250")

# ============================================================
# Withdrawal Transactions
# ============================================================

def test_record_withdrawal(
    service,
    account,
):

    transaction = service.record_withdrawal(

        account.account_number,

        Money("300"),

    )

    assert isinstance(
        transaction,
        Transaction,
    )


def test_record_withdrawal_amount(
    service,
    account,
):

    transaction = service.record_withdrawal(

        account.account_number,

        Money("500"),

    )

    assert transaction.amount == Money("500")

# ============================================================
# Transfer Transactions
# ============================================================

def test_record_transfer(
    service,
    account_repository,
    account,
):

    destination = SavingsAccount(

        account_number="SA200001",

        customer_id=account.customer_id,

        balance=Money("1000"),

    )

    account_repository.add(destination)

    transaction = service.record_transfer(

        account.account_number,

        destination.account_number,

        Money("750"),

    )

    assert isinstance(
        transaction,
        Transaction,
    )


def test_transfer_transaction_amount(
    service,
    account_repository,
    account,
):

    destination = SavingsAccount(

        account_number="SA200002",

        customer_id=account.customer_id,

        balance=Money("1000"),

    )

    account_repository.add(destination)

    transaction = service.record_transfer(

        account.account_number,

        destination.account_number,

        Money("600"),

    )

    assert transaction.amount == Money("600")

# ============================================================
# Retrieval
# ============================================================

def test_get_transaction(
    service,
    account,
):

    transaction = service.record_deposit(

        account.account_number,

        Money("100"),

    )

    found = service.get_transaction(
        transaction.transaction_id
    )

    assert found == transaction


def test_transaction_exists(
    service,
    account,
):

    transaction = service.record_deposit(

        account.account_number,

        Money("100"),

    )

    assert service.transaction_exists(
        transaction.transaction_id
    )

# PART 2

# ============================================================
# Validation
# ============================================================

def test_record_zero_deposit(
    service,
    account,
):

    with pytest.raises(
        ValidationError
    ):

        service.record_deposit(

            account.account_number,

            Money.zero(),

        )


def test_record_negative_deposit(
    service,
    account,
):

    with pytest.raises(
        ValidationError
    ):

        service.record_deposit(

            account.account_number,

            Money("-100"),

        )


def test_record_zero_withdrawal(
    service,
    account,
):

    with pytest.raises(
        ValidationError
    ):

        service.record_withdrawal(

            account.account_number,

            Money.zero(),

        )


def test_record_negative_withdrawal(
    service,
    account,
):

    with pytest.raises(
        ValidationError
    ):

        service.record_withdrawal(

            account.account_number,

            Money("-25"),

        )


def test_unknown_account_deposit(
    service,
):

    with pytest.raises(KeyError):

        service.record_deposit(

            "UNKNOWN",

            Money("100"),

        )


def test_unknown_account_withdrawal(
    service,
):

    with pytest.raises(KeyError):

        service.record_withdrawal(

            "UNKNOWN",

            Money("100"),

        )

# ============================================================
# Duplicate Transactions
# ============================================================

def test_duplicate_transaction_not_allowed(
    service,
    account,
):

    transaction = service.record_deposit(

        account.account_number,

        Money("500"),

    )

    with pytest.raises(
        DuplicateTransactionError
    ):

        service.transaction_repository.add(
            transaction
        )

# ============================================================
# Retrieval
# ============================================================

def test_unknown_transaction_returns_none(
    service,
):

    assert (
        service.get_transaction(
            "UNKNOWN"
        )
        is None
    )


def test_transaction_not_exists(
    service,
):

    assert (
        service.transaction_exists(
            "UNKNOWN"
        )
        is False
    )

# ============================================================
# Search by Account
# ============================================================

def test_get_transactions_for_account(
    service,
    account,
):

    service.record_deposit(

        account.account_number,

        Money("100"),

    )

    service.record_withdrawal(

        account.account_number,

        Money("50"),

    )

    transactions = service.get_transactions_by_account(

        account.account_number

    )

    assert len(transactions) == 2


def test_empty_transaction_history(
    service,
    account,
):

    history = service.get_transactions_by_account(

        account.account_number

    )

    assert history == []

# ============================================================
# Filter by Transaction Type
# ============================================================

def test_filter_deposits(
    service,
    account,
):

    service.record_deposit(

        account.account_number,

        Money("100"),

    )

    service.record_withdrawal(

        account.account_number,

        Money("50"),

    )

    deposits = service.get_transactions_by_type(
        "DEPOSIT"
    )

    assert len(deposits) == 1


def test_filter_withdrawals(
    service,
    account,
):

    service.record_withdrawal(

        account.account_number,

        Money("25"),

    )

    withdrawals = service.get_transactions_by_type(
        "WITHDRAWAL"
    )

    assert len(withdrawals) == 1

# ============================================================
# Date Filtering
# ============================================================

def test_filter_today_transactions(
    service,
    account,
):

    service.record_deposit(

        account.account_number,

        Money("100"),

    )

    today = date.today()

    results = service.get_transactions_by_date(
        today
    )

    assert len(results) >= 1


def test_empty_date_filter(
    service,
):

    results = service.get_transactions_by_date(
        date(1999, 1, 1)
    )

    assert results == []

# ============================================================
# Repository Synchronization
# ============================================================

def test_repository_count_matches_service(
    service,
    account,
):

    service.record_deposit(

        account.account_number,

        Money("100"),

    )

    service.record_withdrawal(

        account.account_number,

        Money("50"),

    )

    assert (

        service.transaction_repository.count()

        ==

        service.transaction_count()

    )


def test_repository_contains_transaction(
    service,
    account,
):

    transaction = service.record_deposit(

        account.account_number,

        Money("250"),

    )

    stored = service.transaction_repository.get(

        transaction.transaction_id

    )

    assert stored == transaction

# PART 3

# ============================================================
# Repository Synchronization
# ============================================================

def test_repository_count_matches_service(
    service,
    account,
):

    service.record_deposit(

        account.account_number,

        Money("100"),

    )

    service.record_withdrawal(

        account.account_number,

        Money("50"),

    )

    assert (

        service.transaction_repository.count()

        ==

        service.transaction_count()

    )


def test_repository_contains_transaction(
    service,
    account,
):

    transaction = service.record_deposit(

        account.account_number,

        Money("250"),

    )

    stored = service.transaction_repository.get(

        transaction.transaction_id

    )

    assert stored == transaction

# ============================================================
# Chronological Ordering
# ============================================================

def test_transactions_are_chronological(
    service,
    account,
):

    service.record_deposit(

        account.account_number,

        Money("100"),

    )

    service.record_withdrawal(

        account.account_number,

        Money("50"),

    )

    history = service.get_transactions_by_account(

        account.account_number

    )

    timestamps = [

        tx.transaction_date

        for tx in history

    ]

    assert timestamps == sorted(timestamps)


def test_latest_transaction_last(
    service,
    account,
):

    service.record_deposit(

        account.account_number,

        Money("10"),

    )

    service.record_deposit(

        account.account_number,

        Money("20"),

    )

    history = service.get_transactions_by_account(

        account.account_number

    )

    assert (

        history[-1].amount

        == Money("20")

    )

# ============================================================
# Running Balance
# ============================================================

def test_running_balance_sequence(
    service,
    account,
):

    service.record_deposit(

        account.account_number,

        Money("100"),

    )

    service.record_withdrawal(

        account.account_number,

        Money("50"),

    )

    service.record_deposit(

        account.account_number,

        Money("25"),

    )

    history = service.get_transactions_by_account(

        account.account_number

    )

    assert len(history) == 3


def test_running_balance_not_empty(
    service,
    account,
):

    service.record_deposit(

        account.account_number,

        Money("500"),

    )

    statement = service.generate_statement(

        account.account_number

    )

    assert statement is not None

# ============================================================
# Save / Load
# ============================================================

def test_save_transactions(
    service,
    account,
):

    service.record_deposit(

        account.account_number,

        Money("100"),

    )

    service.save()

    assert (

        service.transaction_repository.storage_path.exists()

    )


def test_load_transactions(
    tmp_path,
    account_repository,
    account,
):

    path = tmp_path / "transactions.csv"

    repository = TransactionRepository(

        storage_path=path

    )

    service1 = TransactionService(

        transaction_repository=repository,

        account_repository=account_repository,

    )

    service1.record_deposit(

        account.account_number,

        Money("500"),

    )

    service1.save()

    repository2 = TransactionRepository(

        storage_path=path

    )

    service2 = TransactionService(

        transaction_repository=repository2,

        account_repository=account_repository,

    )

    service2.load()

    assert service2.transaction_count() == 1

# ============================================================
# Reload Integrity
# ============================================================

def test_reload_preserves_transactions(
    tmp_path,
    account_repository,
    account,
):

    path = tmp_path / "transactions.csv"

    repository = TransactionRepository(

        storage_path=path

    )

    service = TransactionService(

        repository,

        account_repository,

    )

    service.record_deposit(

        account.account_number,

        Money("100"),

    )

    service.record_withdrawal(

        account.account_number,

        Money("50"),

    )

    service.save()

    repository2 = TransactionRepository(

        storage_path=path

    )

    service2 = TransactionService(

        repository2,

        account_repository,

    )

    service2.load()

    assert (

        service2.transaction_count()

        == 2

    )

# ============================================================
# Export / Import
# ============================================================

def test_export_csv(
    service,
    account,
):

    service.record_deposit(

        account.account_number,

        Money("200"),

    )

    service.export_csv()

    assert (

        service.transaction_repository.storage_path.exists()

    )


def test_import_csv(
    tmp_path,
    account_repository,
    account,
):

    path = tmp_path / "transactions.csv"

    repository = TransactionRepository(

        storage_path=path

    )

    service1 = TransactionService(

        repository,

        account_repository,

    )

    service1.record_deposit(

        account.account_number,

        Money("300"),

    )

    service1.export_csv()

    repository2 = TransactionRepository(

        storage_path=path

    )

    service2 = TransactionService(

        repository2,

        account_repository,

    )

    service2.import_csv()

    assert (

        service2.transaction_count()

        == 1

    )

# ============================================================
# Repository Synchronization
# ============================================================

def test_repository_matches_statement(
    service,
    account,
):

    service.record_deposit(

        account.account_number,

        Money("100"),

    )

    service.record_withdrawal(

        account.account_number,

        Money("20"),

    )

    statement = service.generate_statement(

        account.account_number

    )

    repository = service.transaction_repository.get_all()

    assert (

        len(repository)

        ==

        len(statement.transactions)

    )

# PART 4

# ============================================================
# Repository Synchronization
# ============================================================

def test_repository_matches_statement(
    service,
    account,
):

    service.record_deposit(

        account.account_number,

        Money("100"),

    )

    service.record_withdrawal(

        account.account_number,

        Money("20"),

    )

    statement = service.generate_statement(

        account.account_number

    )

    repository = service.transaction_repository.get_all()

    assert (

        len(repository)

        ==

        len(statement.transactions)

    )

# ============================================================
# Reporting
# ============================================================

def test_transaction_summary_empty(service):

    summary = service.transaction_summary()

    assert isinstance(summary, dict)
    assert summary["total_transactions"] == 0


def test_transaction_summary_single(
    service,
    account,
):

    service.record_deposit(

        account.account_number,

        Money("100"),

    )

    summary = service.transaction_summary()

    assert summary["total_transactions"] == 1


def test_transaction_summary_multiple(
    service,
    account,
):

    service.record_deposit(
        account.account_number,
        Money("100"),
    )

    service.record_withdrawal(
        account.account_number,
        Money("50"),
    )

    summary = service.transaction_summary()

    assert summary["total_transactions"] == 2

# ============================================================
# Helper Methods
# ============================================================

def test_service_length(
    service,
    account,
):

    service.record_deposit(

        account.account_number,

        Money("100"),

    )

    assert len(service) == 1


def test_service_boolean_empty(
    service,
):

    assert bool(service) is False


def test_service_boolean_non_empty(
    service,
    account,
):

    service.record_deposit(

        account.account_number,

        Money("100"),

    )

    assert bool(service) is True

# ============================================================
# Iterator Support
# ============================================================

def test_iteration(
    service,
    account,
):

    for _ in range(10):

        service.record_deposit(

            account.account_number,

            Money("5"),

        )

    count = 0

    for transaction in service:

        assert transaction is not None
        count += 1

    assert count == 10

# ============================================================
# Stress Testing
# ============================================================

def test_create_100_transactions(
    service,
    account,
):

    for _ in range(100):

        service.record_deposit(

            account.account_number,

            Money("1"),

        )

    assert service.transaction_count() == 100


def test_large_transaction_history(
    service,
    account,
):

    for _ in range(200):

        service.record_deposit(

            account.account_number,

            Money("2"),

        )

    history = service.get_transactions_by_account(

        account.account_number

    )

    assert len(history) == 200


def test_high_volume_mixed_transactions(
    service,
    account,
):

    for _ in range(50):

        service.record_deposit(

            account.account_number,

            Money("20"),

        )

        service.record_withdrawal(

            account.account_number,

            Money("10"),

        )

    assert service.transaction_count() == 100

# ============================================================
# Stress Testing
# ============================================================

def test_create_100_transactions(
    service,
    account,
):

    for _ in range(100):

        service.record_deposit(

            account.account_number,

            Money("1"),

        )

    assert service.transaction_count() == 100


def test_large_transaction_history(
    service,
    account,
):

    for _ in range(200):

        service.record_deposit(

            account.account_number,

            Money("2"),

        )

    history = service.get_transactions_by_account(

        account.account_number

    )

    assert len(history) == 200


def test_high_volume_mixed_transactions(
    service,
    account,
):

    for _ in range(50):

        service.record_deposit(

            account.account_number,

            Money("20"),

        )

        service.record_withdrawal(

            account.account_number,

            Money("10"),

        )

    assert service.transaction_count() == 100

# ============================================================
# Edge Cases
# ============================================================

def test_empty_service_transactions(
    service,
):

    assert service.get_all_transactions() == []


def test_empty_transaction_count(
    service,
):

    assert service.transaction_count() == 0


def test_clear_service(
    service,
    account,
):

    for _ in range(5):

        service.record_deposit(

            account.account_number,

            Money("100"),

        )

    service.clear()

    assert service.transaction_count() == 0

# ============================================================
# Integrity Checks
# ============================================================

def test_transaction_ids_are_unique(
    service,
    account,
):

    ids = set()

    for _ in range(20):

        tx = service.record_deposit(

            account.account_number,

            Money("10"),

        )

        assert tx.transaction_id not in ids

        ids.add(tx.transaction_id)


def test_all_transactions_have_timestamp(
    service,
    account,
):

    for _ in range(10):

        tx = service.record_deposit(

            account.account_number,

            Money("5"),

        )

        assert tx.transaction_date is not None

