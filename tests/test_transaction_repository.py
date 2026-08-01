"""
============================================================
Transaction Repository Tests
Part 1
------------------------------------------------------------
Coverage

• Repository construction
• Empty repository
• Transaction insertion
• Duplicate detection
• Invalid object handling
============================================================
"""

import pytest

from repositories.transaction_repository import TransactionRepository

from models.customer import Customer
from models.savings_account import SavingsAccount
from models.transaction import Transaction

from models.value_objects.address import Address
from models.value_objects.email import EmailAddress
from models.value_objects.money import Money
from models.value_objects.phone import PhoneNumber

# ============================================================
# Fixtures
# ============================================================

@pytest.fixture
def repository(tmp_path):

    return TransactionRepository(
        storage_path=tmp_path / "transactions.csv"
    )


@pytest.fixture
def customer():

    return Customer(
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


@pytest.fixture
def account(customer):

    return SavingsAccount(
        account_number="SA100001",
        customer=customer,
        opening_balance=Money("1000"),
    )


@pytest.fixture
def transaction(account):

    return Transaction(
        transaction_number="TXN000001",
        account=account,
        transaction_type="DEPOSIT",
        amount=Money("250"),
    )

# ============================================================
# Repository Construction
# ============================================================

def test_repository_created(repository):

    assert repository is not None


def test_repository_empty(repository):

    assert repository.count() == 0


def test_repository_storage_path(repository):

    assert repository.storage_path.exists() is False


def test_get_all_empty(repository):

    assert repository.get_all() == []


def test_repository_summary_empty(repository):

    summary = repository.repository_summary()

    assert summary["total_transactions"] == 0

# ============================================================
# Add Transaction
# ============================================================

def test_add_transaction(
    repository,
    transaction,
):

    repository.add(transaction)

    assert repository.count() == 1


def test_get_transaction(
    repository,
    transaction,
):

    repository.add(transaction)

    found = repository.get(
        transaction.transaction_number
    )

    assert found == transaction


def test_exists(
    repository,
    transaction,
):

    repository.add(transaction)

    assert repository.exists(
        transaction.transaction_number
    )

# ============================================================
# Duplicate Detection
# ============================================================

def test_duplicate_transaction_number(
    repository,
    transaction,
):

    repository.add(transaction)

    with pytest.raises(ValueError):

        repository.add(transaction)


def test_duplicate_different_object(
    repository,
    account,
):

    repository.add(

        Transaction(

            transaction_number="TXN001",

            account=account,

            transaction_type="DEPOSIT",

            amount=Money("100"),

        )

    )

    duplicate = Transaction(

        transaction_number="TXN001",

        account=account,

        transaction_type="WITHDRAWAL",

        amount=Money("50"),

    )

    with pytest.raises(ValueError):

        repository.add(duplicate)

# ============================================================
# Invalid Objects
# ============================================================

def test_add_none(repository):

    with pytest.raises(TypeError):

        repository.add(None)


def test_add_invalid_type(repository):

    with pytest.raises(TypeError):

        repository.add("invalid")


def test_add_dictionary(repository):

    with pytest.raises(TypeError):

        repository.add({})

# ============================================================
# Multiple Transactions
# ============================================================

def test_multiple_transactions(
    repository,
    account,
):

    for i in range(10):

        repository.add(

            Transaction(

                transaction_number=f"TXN{i:05}",

                account=account,

                transaction_type="DEPOSIT",

                amount=Money("100"),

            )
        )

    assert repository.count() == 10


def test_repository_contains_all(
    repository,
    account,
):

    for i in range(5):

        repository.add(

            Transaction(

                transaction_number=f"TXN{i}",

                account=account,

                transaction_type="DEPOSIT",

                amount=Money("10"),

            )
        )

    assert len(repository.get_all()) == 5

# PART 2

# ============================================================
# Multiple Transactions
# ============================================================

def test_multiple_transactions(
    repository,
    account,
):

    for i in range(10):

        repository.add(

            Transaction(

                transaction_number=f"TXN{i:05}",

                account=account,

                transaction_type="DEPOSIT",

                amount=Money("100"),

            )
        )

    assert repository.count() == 10


def test_repository_contains_all(
    repository,
    account,
):

    for i in range(5):

        repository.add(

            Transaction(

                transaction_number=f"TXN{i}",

                account=account,

                transaction_type="DEPOSIT",

                amount=Money("10"),

            )
        )

    assert len(repository.get_all()) == 5

# ============================================================
# Account Index
# ============================================================

def test_get_transactions_by_account(
    repository,
    account,
):

    t1 = Transaction(
        transaction_number="TXN001",
        account=account,
        transaction_type="DEPOSIT",
        amount=Money("100"),
    )

    t2 = Transaction(
        transaction_number="TXN002",
        account=account,
        transaction_type="WITHDRAWAL",
        amount=Money("50"),
    )

    repository.add(t1)
    repository.add(t2)

    transactions = repository.get_by_account(
        account.account_number
    )

    assert len(transactions) == 2


def test_unknown_account(repository):

    assert (
        repository.get_by_account(
            "UNKNOWN"
        )
        == []
    )

# ============================================================
# Customer Index
# ============================================================

def test_get_transactions_by_customer(
    repository,
    account,
):

    for i in range(3):

        repository.add(

            Transaction(

                transaction_number=f"TXN{i}",

                account=account,

                transaction_type="DEPOSIT",

                amount=Money("100"),

            )
        )

    results = repository.get_by_customer(

        account.customer.customer_id

    )

    assert len(results) == 3


def test_unknown_customer(repository):

    assert (

        repository.get_by_customer(

            "UNKNOWN"

        )

        == []

    )

# ============================================================
# Transaction Type Filtering
# ============================================================

def test_find_deposits(
    repository,
    account,
):

    repository.add(

        Transaction(

            transaction_number="TXN1",

            account=account,

            transaction_type="DEPOSIT",

            amount=Money("100"),

        )
    )

    repository.add(

        Transaction(

            transaction_number="TXN2",

            account=account,

            transaction_type="WITHDRAWAL",

            amount=Money("50"),

        )
    )

    deposits = repository.find_by_type(
        "DEPOSIT"
    )

    assert len(deposits) == 1


def test_find_withdrawals(
    repository,
    account,
):

    repository.add(

        Transaction(

            transaction_number="TXN3",

            account=account,

            transaction_type="WITHDRAWAL",

            amount=Money("75"),

        )
    )

    withdrawals = repository.find_by_type(
        "WITHDRAWAL"
    )

    assert len(withdrawals) == 1


def test_unknown_transaction_type(repository):

    assert repository.find_by_type(
        "UNKNOWN"
    ) == []

# ============================================================
# Status Filtering
# ============================================================

def test_find_completed_transactions(
    repository,
    transaction,
):

    repository.add(transaction)

    results = repository.find_completed()

    assert transaction in results


def test_find_failed_transactions(repository):

    assert repository.find_failed() == []

# ============================================================
# Date Filtering
# ============================================================

from datetime import date, timedelta


def test_find_today_transactions(
    repository,
    transaction,
):

    repository.add(transaction)

    results = repository.find_by_date(
        date.today()
    )

    assert transaction in results


def test_find_date_range(
    repository,
    transaction,
):

    repository.add(transaction)

    results = repository.find_between_dates(

        date.today() - timedelta(days=1),

        date.today() + timedelta(days=1),

    )

    assert transaction in results

# ============================================================
# Chronological Ordering
# ============================================================

def test_transactions_chronological(
    repository,
    account,
):

    for i in range(5):

        repository.add(

            Transaction(

                transaction_number=f"TXN{i}",

                account=account,

                transaction_type="DEPOSIT",

                amount=Money("10"),

            )
        )

    txns = repository.get_all()

    numbers = [

        t.transaction_number

        for t in txns

    ]

    assert numbers == sorted(numbers)

# ============================================================
# Lookup Consistency
# ============================================================

def test_same_instance_returned(
    repository,
    transaction,
):

    repository.add(transaction)

    by_number = repository.get(

        transaction.transaction_number

    )

    by_account = repository.get_by_account(

        transaction.account.account_number

    )[0]

    assert by_number is by_account


def test_repository_contains_all(
    repository,
    account,
):

    for i in range(4):

        repository.add(

            Transaction(

                transaction_number=f"T{i}",

                account=account,

                transaction_type="DEPOSIT",

                amount=Money("25"),

            )
        )

    assert len(repository.get_all()) == 4

# PART 3

# ============================================================
# Lookup Consistency
# ============================================================

def test_same_instance_returned(
    repository,
    transaction,
):

    repository.add(transaction)

    by_number = repository.get(

        transaction.transaction_number

    )

    by_account = repository.get_by_account(

        transaction.account.account_number

    )[0]

    assert by_number is by_account


def test_repository_contains_all(
    repository,
    account,
):

    for i in range(4):

        repository.add(

            Transaction(

                transaction_number=f"T{i}",

                account=account,

                transaction_type="DEPOSIT",

                amount=Money("25"),

            )
        )

    assert len(repository.get_all()) == 4

# ============================================================
# Delete Operations
# ============================================================

def test_remove_transaction(
    repository,
    transaction,
):

    repository.add(transaction)

    repository.remove(
        transaction.transaction_number
    )

    assert repository.count() == 0


def test_removed_transaction_not_found(
    repository,
    transaction,
):

    repository.add(transaction)

    repository.remove(
        transaction.transaction_number
    )

    assert (
        repository.get(
            transaction.transaction_number
        )
        is None
    )


def test_remove_unknown_transaction(repository):

    with pytest.raises(KeyError):

        repository.remove("UNKNOWN")


def test_delete_removes_account_index(
    repository,
    transaction,
):

    repository.add(transaction)

    repository.remove(
        transaction.transaction_number
    )

    assert (
        repository.get_by_account(
            transaction.account.account_number
        )
        == []
    )

# ============================================================
# Save Operations
# ============================================================

def test_save_repository(
    repository,
    transaction,
):

    repository.add(transaction)

    repository.save()

    assert repository.storage_path.exists()


def test_save_empty_repository(repository):

    repository.save()

    assert repository.storage_path.exists()


def test_multiple_save_calls(
    repository,
    transaction,
):

    repository.add(transaction)

    repository.save()

    repository.save()

    repository.save()

    assert repository.storage_path.exists()

# ============================================================
# Load Operations
# ============================================================

def test_save_then_reload(
    tmp_path,
    transaction,
):

    path = tmp_path / "transactions.csv"

    repo1 = TransactionRepository(
        storage_path=path
    )

    repo1.add(transaction)

    repo1.save()

    repo2 = TransactionRepository(
        storage_path=path
    )

    repo2.load()

    loaded = repo2.get(
        transaction.transaction_number
    )

    assert loaded == transaction


def test_reload_preserves_count(
    tmp_path,
    account,
):

    path = tmp_path / "transactions.csv"

    repo = TransactionRepository(
        storage_path=path
    )

    for i in range(3):

        repo.add(

            Transaction(

                transaction_number=f"TXN{i}",

                account=account,

                transaction_type="DEPOSIT",

                amount=Money("100"),

            )
        )

    repo.save()

    repo2 = TransactionRepository(
        storage_path=path
    )

    repo2.load()

    assert repo2.count() == 3

# ============================================================
# CSV Recovery
# ============================================================

def test_load_missing_csv(tmp_path):

    repo = TransactionRepository(
        storage_path=tmp_path / "missing.csv"
    )

    repo.load()

    assert repo.count() == 0


def test_load_empty_csv(tmp_path):

    path = tmp_path / "transactions.csv"

    path.write_text("")

    repo = TransactionRepository(
        storage_path=path
    )

    repo.load()

    assert repo.count() == 0


def test_load_corrupted_csv(tmp_path):

    path = tmp_path / "transactions.csv"

    path.write_text(
        "corrupted,data\n"
        "invalid,row"
    )

    repo = TransactionRepository(
        storage_path=path
    )

    with pytest.raises(Exception):

        repo.load()

# ============================================================
# Persistence Integrity
# ============================================================

def test_reload_preserves_amount(
    tmp_path,
    transaction,
):

    path = tmp_path / "transactions.csv"

    repo = TransactionRepository(
        storage_path=path
    )

    repo.add(transaction)

    repo.save()

    repo2 = TransactionRepository(
        storage_path=path
    )

    repo2.load()

    restored = repo2.get(
        transaction.transaction_number
    )

    assert restored.amount == Money("250")


def test_reload_preserves_transaction_type(
    tmp_path,
    transaction,
):

    path = tmp_path / "transactions.csv"

    repo = TransactionRepository(
        storage_path=path
    )

    repo.add(transaction)

    repo.save()

    repo2 = TransactionRepository(
        storage_path=path
    )

    repo2.load()

    restored = repo2.get(
        transaction.transaction_number
    )

    assert (
        restored.transaction_type
        == transaction.transaction_type
    )

# ============================================================
# Repository Consistency
# ============================================================

def test_update_then_save_then_reload(
    tmp_path,
    transaction,
):

    path = tmp_path / "transactions.csv"

    repo = TransactionRepository(
        storage_path=path
    )

    repo.add(transaction)

    transaction.description = "Salary Deposit"

    repo.update(transaction)

    repo.save()

    repo2 = TransactionRepository(
        storage_path=path
    )

    repo2.load()

    restored = repo2.get(
        transaction.transaction_number
    )

    assert restored.description == "Salary Deposit"


def test_delete_then_save_then_reload(
    tmp_path,
    transaction,
):

    path = tmp_path / "transactions.csv"

    repo = TransactionRepository(
        storage_path=path
    )

    repo.add(transaction)

    repo.remove(
        transaction.transaction_number
    )

    repo.save()

    repo2 = TransactionRepository(
        storage_path=path
    )

    repo2.load()

    assert repo2.count() == 0

# PART 4

# ============================================================
# Repository Consistency
# ============================================================

def test_update_then_save_then_reload(
    tmp_path,
    transaction,
):

    path = tmp_path / "transactions.csv"

    repo = TransactionRepository(
        storage_path=path
    )

    repo.add(transaction)

    transaction.description = "Salary Deposit"

    repo.update(transaction)

    repo.save()

    repo2 = TransactionRepository(
        storage_path=path
    )

    repo2.load()

    restored = repo2.get(
        transaction.transaction_number
    )

    assert restored.description == "Salary Deposit"


def test_delete_then_save_then_reload(
    tmp_path,
    transaction,
):

    path = tmp_path / "transactions.csv"

    repo = TransactionRepository(
        storage_path=path
    )

    repo.add(transaction)

    repo.remove(
        transaction.transaction_number
    )

    repo.save()

    repo2 = TransactionRepository(
        storage_path=path
    )

    repo2.load()

    assert repo2.count() == 0

# ============================================================
# Transaction Type Statistics
# ============================================================

def test_deposit_count(
    repository,
    account,
):

    repository.add(
        Transaction(
            transaction_number="D001",
            account=account,
            transaction_type="DEPOSIT",
            amount=Money("100"),
        )
    )

    assert repository.deposit_count() == 1


def test_withdrawal_count(
    repository,
    account,
):

    repository.add(
        Transaction(
            transaction_number="W001",
            account=account,
            transaction_type="WITHDRAWAL",
            amount=Money("50"),
        )
    )

    assert repository.withdrawal_count() == 1


def test_transfer_count(
    repository,
    account,
):

    repository.add(
        Transaction(
            transaction_number="T001",
            account=account,
            transaction_type="TRANSFER",
            amount=Money("75"),
        )
    )

    assert repository.transfer_count() == 1

# ============================================================
# Batch Operations
# ============================================================

def test_add_many_transactions(
    repository,
    account,
):

    transactions = []

    for i in range(10):

        transactions.append(

            Transaction(

                transaction_number=f"TXN{i:04}",

                account=account,

                transaction_type="DEPOSIT",

                amount=Money("100"),

            )
        )

    repository.add_many(transactions)

    assert repository.count() == 10


def test_clear_repository(
    repository,
    transaction,
):

    repository.add(transaction)

    repository.clear()

    assert repository.count() == 0

    assert repository.get_all() == []

# ============================================================
# Boundary Conditions
# ============================================================

def test_zero_amount_transaction(
    repository,
    account,
):

    txn = Transaction(

        transaction_number="ZERO001",

        account=account,

        transaction_type="DEPOSIT",

        amount=Money.zero(),

    )

    repository.add(txn)

    assert repository.count() == 1


def test_large_amount_transaction(
    repository,
    account,
):

    txn = Transaction(

        transaction_number="BIG001",

        account=account,

        transaction_type="DEPOSIT",

        amount=Money("999999999.99"),

    )

    repository.add(txn)

    assert repository.get(
        txn.transaction_number
    ).amount == Money("999999999.99")


def test_empty_search(repository):

    assert repository.search_transaction_number("") == []


def test_whitespace_search(repository):

    assert repository.search_transaction_number("   ") == []

# ============================================================
# Large Repository
# ============================================================

def test_large_repository(
    repository,
    account,
):

    for i in range(1000):

        repository.add(

            Transaction(

                transaction_number=f"TXN{i:05}",

                account=account,

                transaction_type="DEPOSIT",

                amount=Money("10"),

            )
        )

    assert repository.count() == 1000

# ============================================================
# Index Consistency
# ============================================================

def test_account_index_after_clear(
    repository,
    transaction,
):

    repository.add(transaction)

    repository.clear()

    assert repository.get_by_account(
        transaction.account.account_number
    ) == []


def test_customer_index_after_reload(
    tmp_path,
    transaction,
):

    path = tmp_path / "transactions.csv"

    repo = TransactionRepository(
        storage_path=path
    )

    repo.add(transaction)

    repo.save()

    repo2 = TransactionRepository(
        storage_path=path
    )

    repo2.load()

    results = repo2.get_by_customer(
        transaction.account.customer.customer_id
    )

    assert len(results) == 1

    assert results[0] == transaction

# ============================================================
# Repository Iteration
# ============================================================

def test_repository_iteration(
    repository,
    account,
):

    for i in range(5):

        repository.add(

            Transaction(

                transaction_number=f"TXN{i}",

                account=account,

                transaction_type="DEPOSIT",

                amount=Money("20"),

            )
        )

    count = 0

    for _ in repository:

        count += 1

    assert count == repository.count()


def test_repository_length(repository):

    assert len(repository) == repository.count()


def test_repository_boolean(
    repository,
    transaction,
):

    assert bool(repository) is False

    repository.add(transaction)

    assert bool(repository) is True

# ============================================================
# Copy / Export
# ============================================================

def test_repository_copy(
    repository,
    transaction,
):

    repository.add(transaction)

    copied = repository.copy()

    assert copied.count() == repository.count()

    assert copied.get(
        transaction.transaction_number
    ) == transaction


def test_export_then_import(
    tmp_path,
    transaction,
):

    path = tmp_path / "transactions.csv"

    repo = TransactionRepository(
        storage_path=path
    )

    repo.add(transaction)

    repo.export_csv()

    imported = TransactionRepository(
        storage_path=path
    )

    imported.import_csv()

    assert imported.count() == 1

