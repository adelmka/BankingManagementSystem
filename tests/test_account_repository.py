"""
============================================================
Account Repository Tests
Part 1
------------------------------------------------------------
Coverage

• Repository construction
• Empty repository
• Repository metadata
• Account insertion
• Duplicate detection
• Invalid object handling
============================================================
"""

import pytest

from repositories.account_repository import AccountRepository

from models.customer import Customer
from models.savings_account import SavingsAccount
from models.current_account import CurrentAccount
from models.time_deposit_account import TimeDepositAccount

from models.value_objects.address import Address
from models.value_objects.email import EmailAddress
from models.value_objects.money import Money
from models.value_objects.phone import PhoneNumber

# ============================================================
# Fixtures
# ============================================================

@pytest.fixture
def repository(tmp_path):

    return AccountRepository(
        storage_path=tmp_path / "accounts.csv"
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
def savings(customer):

    return SavingsAccount(
        account_number="SA100001",
        customer=customer,
        opening_balance=Money("1000"),
    )


@pytest.fixture
def current(customer):

    return CurrentAccount(
        account_number="CA100001",
        customer=customer,
        opening_balance=Money("500"),
    )


@pytest.fixture
def time_deposit(customer):

    return TimeDepositAccount(
        account_number="TD100001",
        customer=customer,
        opening_balance=Money("5000"),
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

    assert summary["total_accounts"] == 0

# ============================================================
# Savings Account
# ============================================================

def test_add_savings_account(repository, savings):

    repository.add(savings)

    assert repository.count() == 1


def test_get_savings_account(repository, savings):

    repository.add(savings)

    assert (
        repository.get(savings.account_number)
        == savings
    )


def test_savings_exists(repository, savings):

    repository.add(savings)

    assert repository.exists(
        savings.account_number
    )

# ============================================================
# Current Account
# ============================================================

def test_add_current_account(repository, current):

    repository.add(current)

    assert repository.count() == 1


def test_get_current_account(repository, current):

    repository.add(current)

    assert (
        repository.get(current.account_number)
        == current
    )

# ============================================================
# Time Deposit
# ============================================================

def test_add_time_deposit(repository, time_deposit):

    repository.add(time_deposit)

    assert repository.count() == 1


def test_get_time_deposit(repository, time_deposit):

    repository.add(time_deposit)

    assert (
        repository.get(
            time_deposit.account_number
        )
        == time_deposit
    )

# ============================================================
# Duplicate Detection
# ============================================================

def test_duplicate_account_number(
    repository,
    savings,
):

    repository.add(savings)

    with pytest.raises(ValueError):

        repository.add(savings)


def test_duplicate_different_object_same_number(
    repository,
    customer,
):

    repository.add(
        SavingsAccount(
            account_number="SA100001",
            customer=customer,
            opening_balance=Money("100"),
        )
    )

    duplicate = SavingsAccount(
        account_number="SA100001",
        customer=customer,
        opening_balance=Money("200"),
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
# Mixed Repository
# ============================================================

def test_repository_multiple_account_types(
    repository,
    savings,
    current,
    time_deposit,
):

    repository.add(savings)

    repository.add(current)

    repository.add(time_deposit)

    assert repository.count() == 3


def test_all_accounts_returned(
    repository,
    savings,
    current,
):

    repository.add(savings)

    repository.add(current)

    accounts = repository.get_all()

    assert len(accounts) == 2

# PART 2

# ============================================================
# Retrieval by Account Number
# ============================================================

def test_get_by_account_number(repository, savings):

    repository.add(savings)

    found = repository.get(
        savings.account_number
    )

    assert found == savings


def test_get_unknown_account(repository):

    assert repository.get("UNKNOWN") is None


def test_exists_true(repository, savings):

    repository.add(savings)

    assert repository.exists(
        savings.account_number
    )


def test_exists_false(repository):

    assert repository.exists("UNKNOWN") is False

# ============================================================
# Customer Index
# ============================================================

def test_get_accounts_by_customer(
    repository,
    customer,
):

    s1 = SavingsAccount(
        account_number="SA100001",
        customer=customer,
        opening_balance=Money("1000"),
    )

    s2 = CurrentAccount(
        account_number="CA100001",
        customer=customer,
        opening_balance=Money("500"),
    )

    repository.add(s1)

    repository.add(s2)

    accounts = repository.get_by_customer(
        customer.customer_id
    )

    assert len(accounts) == 2


def test_customer_without_accounts(repository):

    accounts = repository.get_by_customer(
        "UNKNOWN"
    )

    assert accounts == []

# ============================================================
# Account Type Searches
# ============================================================

def test_find_savings_accounts(
    repository,
    savings,
):

    repository.add(savings)

    accounts = repository.find_savings_accounts()

    assert savings in accounts


def test_find_current_accounts(
    repository,
    current,
):

    repository.add(current)

    accounts = repository.find_current_accounts()

    assert current in accounts


def test_find_time_deposits(
    repository,
    time_deposit,
):

    repository.add(time_deposit)

    accounts = repository.find_time_deposit_accounts()

    assert time_deposit in accounts

# ============================================================
# Active / Closed Accounts
# ============================================================

def test_find_active_accounts(
    repository,
    savings,
):

    repository.add(savings)

    active = repository.find_active_accounts()

    assert savings in active


def test_find_closed_accounts(
    repository,
    savings,
):

    repository.add(savings)

    savings.close_account()

    repository.update(savings)

    closed = repository.find_closed_accounts()

    assert savings in closed

# ============================================================
# Balance Aggregation
# ============================================================

def test_total_balance_single_account(
    repository,
    savings,
):

    repository.add(savings)

    total = repository.total_balance()

    assert total == Money("1000")


def test_total_balance_multiple_accounts(
    repository,
    savings,
    current,
):

    repository.add(savings)

    repository.add(current)

    total = repository.total_balance()

    assert total == Money("1500")


def test_customer_total_balance(
    repository,
    customer,
):

    repository.add(

        SavingsAccount(
            account_number="SA1",
            customer=customer,
            opening_balance=Money("100"),
        )
    )

    repository.add(

        CurrentAccount(
            account_number="CA1",
            customer=customer,
            opening_balance=Money("300"),
        )
    )

    total = repository.customer_total_balance(
        customer.customer_id
    )

    assert total == Money("400")

# ============================================================
# Repository Searches
# ============================================================

def test_find_by_account_prefix(
    repository,
    savings,
):

    repository.add(savings)

    results = repository.search_account_number(
        "SA"
    )

    assert savings in results


def test_partial_account_number(
    repository,
    savings,
):

    repository.add(savings)

    results = repository.search_account_number(
        "100"
    )

    assert savings in results


def test_unknown_account_search(repository):

    results = repository.search_account_number(
        "XYZ"
    )

    assert results == []

# ============================================================
# Repository Ordering
# ============================================================

def test_repository_order(repository):

    numbers = []

    for i in range(5):

        acc = SavingsAccount(

            account_number=f"SA{i}",

            customer=customer(),

            opening_balance=Money("100"),
        )

        repository.add(acc)

        numbers.append(acc.account_number)

    retrieved = [

        a.account_number

        for a in repository.get_all()

    ]

    assert retrieved == numbers

# ============================================================
# Index Consistency
# ============================================================

def test_same_instance_returned(
    repository,
    savings,
):

    repository.add(savings)

    by_number = repository.get(
        savings.account_number
    )

    by_customer = repository.get_by_customer(
        savings.customer.customer_id
    )[0]

    assert by_number is by_customer


def test_repository_contains_all_accounts(
    repository,
    savings,
    current,
):

    repository.add(savings)

    repository.add(current)

    accounts = repository.get_all()

    assert savings in accounts

    assert current in accounts

# PART 3

# ============================================================
# Update Operations
# ============================================================

def test_update_account(repository, savings):

    repository.add(savings)

    savings.nickname = "Emergency Fund"

    repository.update(savings)

    updated = repository.get(
        savings.account_number
    )

    assert updated.nickname == "Emergency Fund"


def test_update_balance(repository, savings):

    repository.add(savings)

    savings.deposit(Money("250"))

    repository.update(savings)

    updated = repository.get(
        savings.account_number
    )

    assert updated.balance == Money("1250")


def test_update_rebuilds_customer_index(
    repository,
    savings,
):

    repository.add(savings)

    accounts = repository.get_by_customer(
        savings.customer.customer_id
    )

    assert len(accounts) == 1

    repository.update(savings)

    accounts = repository.get_by_customer(
        savings.customer.customer_id
    )

    assert len(accounts) == 1


def test_update_unknown_account(
    repository,
    savings,
):

    with pytest.raises(KeyError):

        repository.update(savings)

# ============================================================
# Delete Operations
# ============================================================

def test_remove_account(repository, savings):

    repository.add(savings)

    repository.remove(savings.account_number)

    assert repository.count() == 0


def test_removed_account_not_found(
    repository,
    savings,
):

    repository.add(savings)

    repository.remove(savings.account_number)

    assert (
        repository.get(
            savings.account_number
        )
        is None
    )


def test_remove_unknown_account(repository):

    with pytest.raises(KeyError):

        repository.remove("UNKNOWN")


def test_delete_removes_customer_index(
    repository,
    savings,
):

    repository.add(savings)

    repository.remove(savings.account_number)

    accounts = repository.get_by_customer(
        savings.customer.customer_id
    )

    assert accounts == []

# ============================================================
# Save Operations
# ============================================================

def test_save_repository(
    repository,
    savings,
):

    repository.add(savings)

    repository.save()

    assert repository.storage_path.exists()


def test_save_empty_repository(repository):

    repository.save()

    assert repository.storage_path.exists()


def test_multiple_save_calls(
    repository,
    savings,
):

    repository.add(savings)

    repository.save()

    repository.save()

    repository.save()

    assert repository.storage_path.exists()

# ============================================================
# Load Operations
# ============================================================

def test_save_then_reload(
    tmp_path,
    savings,
):

    path = tmp_path / "accounts.csv"

    repo1 = AccountRepository(
        storage_path=path
    )

    repo1.add(savings)

    repo1.save()

    repo2 = AccountRepository(
        storage_path=path
    )

    repo2.load()

    loaded = repo2.get(
        savings.account_number
    )

    assert loaded == savings


def test_reload_preserves_count(
    tmp_path,
    customer,
):

    path = tmp_path / "accounts.csv"

    repo = AccountRepository(
        storage_path=path
    )

    for i in range(3):

        repo.add(

            SavingsAccount(
                account_number=f"SA{i}",
                customer=customer,
                opening_balance=Money("100"),
            )
        )

    repo.save()

    repo2 = AccountRepository(
        storage_path=path
    )

    repo2.load()

    assert repo2.count() == 3

# ============================================================
# CSV Recovery
# ============================================================

def test_load_missing_csv(tmp_path):

    repo = AccountRepository(

        storage_path=tmp_path / "missing.csv"

    )

    repo.load()

    assert repo.count() == 0


def test_load_empty_csv(tmp_path):

    path = tmp_path / "accounts.csv"

    path.write_text("")

    repo = AccountRepository(
        storage_path=path
    )

    repo.load()

    assert repo.count() == 0


def test_load_corrupted_csv(tmp_path):

    path = tmp_path / "accounts.csv"

    path.write_text(

        "corrupted,data\n"

        "invalid,row"

    )

    repo = AccountRepository(
        storage_path=path
    )

    with pytest.raises(Exception):

        repo.load()

# ============================================================
# Persistence Integrity
# ============================================================

def test_reload_preserves_account_type(
    tmp_path,
    savings,
):

    path = tmp_path / "accounts.csv"

    repo = AccountRepository(
        storage_path=path
    )

    repo.add(savings)

    repo.save()

    repo2 = AccountRepository(
        storage_path=path
    )

    repo2.load()

    restored = repo2.get(
        savings.account_number
    )

    assert isinstance(
        restored,
        SavingsAccount,
    )


def test_reload_preserves_balance(
    tmp_path,
    savings,
):

    path = tmp_path / "accounts.csv"

    repo = AccountRepository(
        storage_path=path
    )

    repo.add(savings)

    repo.save()

    repo2 = AccountRepository(
        storage_path=path
    )

    repo2.load()

    restored = repo2.get(
        savings.account_number
    )

    assert restored.balance == Money("1000")

# ============================================================
# Repository Consistency
# ============================================================

def test_update_then_save_then_reload(
    tmp_path,
    savings,
):

    path = tmp_path / "accounts.csv"

    repo = AccountRepository(
        storage_path=path
    )

    repo.add(savings)

    savings.deposit(Money("500"))

    repo.update(savings)

    repo.save()

    repo2 = AccountRepository(
        storage_path=path
    )

    repo2.load()

    restored = repo2.get(
        savings.account_number
    )

    assert restored.balance == Money("1500")


def test_delete_then_save_then_reload(
    tmp_path,
    savings,
):

    path = tmp_path / "accounts.csv"

    repo = AccountRepository(
        storage_path=path
    )

    repo.add(savings)

    repo.remove(savings.account_number)

    repo.save()

    repo2 = AccountRepository(
        storage_path=path
    )

    repo2.load()

    assert repo2.count() == 0

# PART 4

# ============================================================
# Repository Statistics
# ============================================================

def test_repository_summary(repository):

    summary = repository.repository_summary()

    assert isinstance(summary, dict)


def test_repository_summary_empty(repository):

    summary = repository.repository_summary()

    assert summary["total_accounts"] == 0


def test_repository_summary_after_insert(
    repository,
    savings,
):

    repository.add(savings)

    summary = repository.repository_summary()

    assert summary["total_accounts"] == 1


def test_total_balance_empty(repository):

    assert repository.total_balance() == Money.zero()


def test_total_balance_multiple_types(
    repository,
    savings,
    current,
    time_deposit,
):

    repository.add(savings)
    repository.add(current)
    repository.add(time_deposit)

    assert repository.total_balance() == Money("6500")

# ============================================================
# Account Type Statistics
# ============================================================

def test_savings_account_count(
    repository,
    savings,
):

    repository.add(savings)

    assert repository.savings_account_count() == 1


def test_current_account_count(
    repository,
    current,
):

    repository.add(current)

    assert repository.current_account_count() == 1


def test_time_deposit_count(
    repository,
    time_deposit,
):

    repository.add(time_deposit)

    assert repository.time_deposit_account_count() == 1


def test_active_account_count(
    repository,
    savings,
):

    repository.add(savings)

    assert repository.active_account_count() == 1

# ============================================================
# Batch Operations
# ============================================================

def test_add_many_accounts(
    repository,
    customer,
):

    accounts = []

    for i in range(10):

        accounts.append(

            SavingsAccount(

                account_number=f"SA{i:04}",

                customer=customer,

                opening_balance=Money("100"),

            )
        )

    repository.add_many(accounts)

    assert repository.count() == 10


def test_clear_repository(
    repository,
    savings,
):

    repository.add(savings)

    repository.clear()

    assert repository.count() == 0

    assert repository.get_all() == []

# ============================================================
# Boundary Conditions
# ============================================================

def test_zero_balance_account(
    repository,
    customer,
):

    account = SavingsAccount(

        account_number="ZERO001",

        customer=customer,

        opening_balance=Money.zero(),

    )

    repository.add(account)

    assert repository.count() == 1


def test_large_balance_account(
    repository,
    customer,
):

    account = SavingsAccount(

        account_number="BIG001",

        customer=customer,

        opening_balance=Money("999999999.99"),

    )

    repository.add(account)

    assert repository.get(

        account.account_number

    ).balance == Money("999999999.99")


def test_empty_account_search(repository):

    assert repository.search_account_number("") == []


def test_whitespace_account_search(repository):

    assert repository.search_account_number("   ") == []

# ============================================================
# Large Repository
# ============================================================

def test_large_repository(
    repository,
    customer,
):

    for i in range(1000):

        repository.add(

            SavingsAccount(

                account_number=f"SA{i:05}",

                customer=customer,

                opening_balance=Money("100"),

            )
        )

    assert repository.count() == 1000

# ============================================================
# Index Consistency
# ============================================================

def test_customer_index_after_clear(
    repository,
    savings,
):

    repository.add(savings)

    repository.clear()

    assert (

        repository.get_by_customer(

            savings.customer.customer_id

        )

        == []

    )


def test_repository_indexes_after_reload(
    tmp_path,
    savings,
):

    path = tmp_path / "accounts.csv"

    repo = AccountRepository(

        storage_path=path

    )

    repo.add(savings)

    repo.save()

    repo2 = AccountRepository(

        storage_path=path

    )

    repo2.load()

    assert (

        repo2.get_by_customer(

            savings.customer.customer_id

        )[0]

        == savings

    )

# ============================================================
# Index Consistency
# ============================================================

def test_customer_index_after_clear(
    repository,
    savings,
):

    repository.add(savings)

    repository.clear()

    assert (

        repository.get_by_customer(

            savings.customer.customer_id

        )

        == []

    )


def test_repository_indexes_after_reload(
    tmp_path,
    savings,
):

    path = tmp_path / "accounts.csv"

    repo = AccountRepository(

        storage_path=path

    )

    repo.add(savings)

    repo.save()

    repo2 = AccountRepository(

        storage_path=path

    )

    repo2.load()

    assert (

        repo2.get_by_customer(

            savings.customer.customer_id

        )[0]

        == savings

    )

# ============================================================
# Repository Iteration
# ============================================================

def test_repository_iteration(
    repository,
    customer,
):

    for i in range(5):

        repository.add(

            SavingsAccount(

                account_number=f"SA{i}",

                customer=customer,

                opening_balance=Money("100"),

            )
        )

    count = 0

    for _ in repository:

        count += 1

    assert count == repository.count()


def test_repository_length(
    repository,
):

    assert len(repository) == repository.count()


def test_repository_boolean(
    repository,
    savings,
):

    assert bool(repository) is False

    repository.add(savings)

    assert bool(repository) is True

# ============================================================
# Copy / Export
# ============================================================

def test_repository_copy(
    repository,
    savings,
):

    repository.add(savings)

    copied = repository.copy()

    assert copied.count() == repository.count()

    assert (

        copied.get(

            savings.account_number

        )

        == savings

    )


def test_export_then_import(
    tmp_path,
    savings,
):

    path = tmp_path / "accounts.csv"

    repo = AccountRepository(

        storage_path=path

    )

    repo.add(savings)

    repo.export_csv()

    imported = AccountRepository(

        storage_path=path

    )

    imported.import_csv()

    assert imported.count() == 1

