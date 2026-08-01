"""
============================================================
Customer Repository Tests
Part 1
------------------------------------------------------------
Coverage

• Repository construction
• Empty repository
• Repository metadata
• Storage initialization
• Add customer
• Duplicate detection
• Invalid object handling
============================================================
"""

from pathlib import Path

import pytest

from repositories.customer_repository import CustomerRepository
from models.customer import Customer
from models.value_objects.address import Address
from models.value_objects.email import EmailAddress
from models.value_objects.money import Money
from models.value_objects.phone import PhoneNumber
from utils.constants import CustomerStatus

# ============================================================
# Fixtures
# ============================================================

@pytest.fixture
def repository(tmp_path):

    storage = tmp_path / "customers.csv"

    return CustomerRepository(storage_path=storage)


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

# ============================================================
# Repository Construction
# ============================================================

def test_repository_created(repository):

    assert repository is not None


def test_repository_is_empty(repository):

    assert repository.count() == 0


def test_repository_storage_path(repository):

    assert repository.storage_path.exists() is False


def test_repository_returns_empty_collection(repository):

    assert repository.get_all() == []


def test_repository_summary_empty(repository):

    summary = repository.repository_summary()

    assert isinstance(summary, dict)

    assert summary["total_customers"] == 0

# ============================================================
# Add Customer
# ============================================================

def test_add_customer(repository, customer):

    repository.add(customer)

    assert repository.count() == 1


def test_added_customer_exists(repository, customer):

    repository.add(customer)

    assert repository.exists(customer.customer_id)


def test_get_added_customer(repository, customer):

    repository.add(customer)

    found = repository.get(customer.customer_id)

    assert found == customer


def test_repository_contains_added_customer(repository, customer):

    repository.add(customer)

    assert customer in repository.get_all()

# ============================================================
# Duplicate Detection
# ============================================================

def test_duplicate_customer_id(repository, customer):

    repository.add(customer)

    with pytest.raises(ValueError):

        repository.add(customer)


def test_duplicate_national_id(repository, customer):

    repository.add(customer)

    duplicate = Customer(
        customer_id="CUST000002",
        first_name="Jane",
        middle_name="B",
        last_name="Smith",
        national_id=customer.national_id,
        email=EmailAddress("jane@test.com"),
        phone=PhoneNumber("+966511111111"),
        address=customer.address,
    )

    with pytest.raises(ValueError):

        repository.add(duplicate)


def test_duplicate_email(repository, customer):

    repository.add(customer)

    duplicate = Customer(
        customer_id="CUST000003",
        first_name="Alex",
        middle_name="C",
        last_name="Jones",
        national_id="9988776655",
        email=customer.email,
        phone=PhoneNumber("+966522222222"),
        address=customer.address,
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

        repository.add("Not a Customer")


def test_add_dictionary(repository):

    with pytest.raises(TypeError):

        repository.add({})

# ============================================================
# Multiple Customers
# ============================================================

def test_add_multiple_customers(repository):

    for i in range(10):

        customer = Customer(
            customer_id=f"CUST{i:06}",
            first_name=f"First{i}",
            middle_name="A",
            last_name=f"Last{i}",
            national_id=f"{1000000000+i}",
            email=EmailAddress(f"user{i}@test.com"),
            phone=PhoneNumber(f"+966500000{i:03}"),
            address=Address(
                street="Street",
                city="Riyadh",
                state="Riyadh",
                postal_code="12345",
                country="Saudi Arabia",
            ),
        )

        repository.add(customer)

    assert repository.count() == 10


def test_customer_ids_unique(repository):

    ids = set()

    for i in range(5):

        customer = Customer(
            customer_id=f"C{i}",
            first_name="John",
            middle_name="A",
            last_name="Smith",
            national_id=f"{2000000000+i}",
            email=EmailAddress(f"user{i}@mail.com"),
            phone=PhoneNumber(f"+966555000{i:03}"),
            address=Address(
                street="Road",
                city="Jeddah",
                state="Makkah",
                postal_code="22222",
                country="Saudi Arabia",
            ),
        )

        repository.add(customer)

        ids.add(customer.customer_id)

    assert len(ids) == repository.count()

# PART 2

# ============================================================
# Retrieval Operations
# ============================================================

def test_get_by_customer_id(repository, customer):

    repository.add(customer)

    found = repository.get(customer.customer_id)

    assert found == customer


def test_get_nonexistent_customer(repository):

    assert repository.get("UNKNOWN") is None


def test_exists_true(repository, customer):

    repository.add(customer)

    assert repository.exists(customer.customer_id)


def test_exists_false(repository):

    assert repository.exists("UNKNOWN") is False


def test_contains_customer(repository, customer):

    repository.add(customer)

    assert customer in repository.get_all()


def test_get_all_returns_list(repository, customer):

    repository.add(customer)

    customers = repository.get_all()

    assert isinstance(customers, list)

    assert len(customers) == 1

# ============================================================
# Secondary Index Lookups
# ============================================================

def test_get_by_national_id(repository, customer):

    repository.add(customer)

    found = repository.get_by_national_id(
        customer.national_id
    )

    assert found == customer


def test_get_by_email(repository, customer):

    repository.add(customer)

    found = repository.get_by_email(
        customer.email
    )

    assert found == customer


def test_get_by_phone(repository, customer):

    repository.add(customer)

    found = repository.get_by_phone(
        customer.phone
    )

    assert found == customer


def test_unknown_national_id(repository):

    assert (
        repository.get_by_national_id("9999999999")
        is None
    )


def test_unknown_email(repository):

    assert (
        repository.get_by_email(
            EmailAddress("missing@test.com")
        )
        is None
    )


def test_unknown_phone(repository):

    assert (
        repository.get_by_phone(
            PhoneNumber("+966599999999")
        )
        is None
    )

# ============================================================
# Search by Name
# ============================================================

def test_find_by_first_name(repository):

    c1 = Customer(
        customer_id="C1",
        first_name="John",
        middle_name="A",
        last_name="Smith",
        national_id="1000000001",
        email=EmailAddress("john@test.com"),
        phone=PhoneNumber("+966500000001"),
        address=Address(
            street="Road",
            city="Riyadh",
            state="Riyadh",
            postal_code="11111",
            country="Saudi Arabia",
        ),
    )

    repository.add(c1)

    results = repository.find_by_first_name("John")

    assert len(results) == 1


def test_find_by_last_name(repository):

    c1 = Customer(
        customer_id="C2",
        first_name="Ahmed",
        middle_name="A",
        last_name="AlQahtani",
        national_id="1000000002",
        email=EmailAddress("ahmed@test.com"),
        phone=PhoneNumber("+966500000002"),
        address=Address(
            street="Road",
            city="Riyadh",
            state="Riyadh",
            postal_code="11111",
            country="Saudi Arabia",
        ),
    )

    repository.add(c1)

    results = repository.find_by_last_name(
        "AlQahtani"
    )

    assert len(results) == 1

# ============================================================
# Partial Searches
# ============================================================

def test_partial_first_name(repository):

    repository.add(customer())

    results = repository.search_name("Joh")

    assert len(results) == 1


def test_partial_last_name(repository):

    repository.add(customer())

    results = repository.search_name("Smi")

    assert len(results) == 1


def test_search_name_not_found(repository):

    results = repository.search_name("Nobody")

    assert results == []

# ============================================================
# Search by Status
# ============================================================

def test_find_active_customers(repository, customer):

    repository.add(customer)

    results = repository.find_by_status(
        CustomerStatus.ACTIVE
    )

    assert customer in results


def test_find_inactive_customers(repository):

    results = repository.find_by_status(
        CustomerStatus.INACTIVE
    )

    assert results == []

# ============================================================
# Search by City
# ============================================================

def test_find_by_city(repository, customer):

    repository.add(customer)

    results = repository.find_by_city("Riyadh")

    assert len(results) == 1


def test_find_unknown_city(repository):

    results = repository.find_by_city("Dammam")

    assert results == []

# ============================================================
# Multi-Customer Retrieval
# ============================================================

def test_get_all_multiple(repository):

    for i in range(5):

        repository.add(
            Customer(
                customer_id=f"C{i}",
                first_name=f"First{i}",
                middle_name="A",
                last_name="Last",
                national_id=f"{1000000000+i}",
                email=EmailAddress(
                    f"user{i}@mail.com"
                ),
                phone=PhoneNumber(
                    f"+966500000{i:03}"
                ),
                address=Address(
                    street="Street",
                    city="Riyadh",
                    state="Riyadh",
                    postal_code="12345",
                    country="Saudi Arabia",
                ),
            )
        )

    customers = repository.get_all()

    assert len(customers) == 5

# ============================================================
# Index Integrity
# ============================================================

def test_lookup_returns_same_instance(
    repository,
    customer,
):

    repository.add(customer)

    by_id = repository.get(customer.customer_id)

    by_email = repository.get_by_email(
        customer.email
    )

    by_phone = repository.get_by_phone(
        customer.phone
    )

    assert by_id is by_email

    assert by_email is by_phone


def test_repository_order_stable(repository):

    ids = []

    for i in range(5):

        cust = Customer(
            customer_id=f"C{i}",
            first_name="John",
            middle_name="A",
            last_name="Smith",
            national_id=f"{2000000000+i}",
            email=EmailAddress(
                f"user{i}@mail.com"
            ),
            phone=PhoneNumber(
                f"+966511111{i:03}"
            ),
            address=Address(
                street="Road",
                city="Riyadh",
                state="Riyadh",
                postal_code="11111",
                country="Saudi Arabia",
            ),
        )

        repository.add(cust)

        ids.append(cust.customer_id)

    retrieved = [
        c.customer_id
        for c in repository.get_all()
    ]

    assert retrieved == ids

# PART 3

# ============================================================
# Update Operations
# ============================================================

def test_update_customer(repository, customer):

    repository.add(customer)

    customer.first_name = "Michael"

    repository.update(customer)

    updated = repository.get(customer.customer_id)

    assert updated.first_name == "Michael"


def test_update_email_updates_index(repository, customer):

    repository.add(customer)

    old_email = customer.email

    customer.email = EmailAddress("new@email.com")

    repository.update(customer)

    assert repository.get_by_email(old_email) is None

    assert (
        repository.get_by_email(customer.email)
        == customer
    )


def test_update_phone_updates_index(repository, customer):

    repository.add(customer)

    old_phone = customer.phone

    customer.phone = PhoneNumber("+966599999999")

    repository.update(customer)

    assert repository.get_by_phone(old_phone) is None

    assert (
        repository.get_by_phone(customer.phone)
        == customer
    )


def test_update_nonexistent_customer(repository, customer):

    with pytest.raises(KeyError):

        repository.update(customer)

# ============================================================
# Delete Operations
# ============================================================

def test_remove_customer(repository, customer):

    repository.add(customer)

    repository.remove(customer.customer_id)

    assert repository.count() == 0


def test_removed_customer_not_found(repository, customer):

    repository.add(customer)

    repository.remove(customer.customer_id)

    assert (
        repository.get(customer.customer_id)
        is None
    )


def test_remove_unknown_customer(repository):

    with pytest.raises(KeyError):

        repository.remove("UNKNOWN")


def test_delete_removes_secondary_indexes(repository, customer):

    repository.add(customer)

    repository.remove(customer.customer_id)

    assert (
        repository.get_by_email(customer.email)
        is None
    )

    assert (
        repository.get_by_phone(customer.phone)
        is None
    )

    assert (
        repository.get_by_national_id(
            customer.national_id
        )
        is None
    )

# ============================================================
# Save Operations
# ============================================================

def test_save_repository(repository, customer):

    repository.add(customer)

    repository.save()

    assert repository.storage_path.exists()


def test_save_empty_repository(repository):

    repository.save()

    assert repository.storage_path.exists()


def test_multiple_save_calls(repository, customer):

    repository.add(customer)

    repository.save()

    repository.save()

    repository.save()

    assert repository.storage_path.exists()

# ============================================================
# Load Operations
# ============================================================

def test_save_then_reload(tmp_path, customer):

    path = tmp_path / "customers.csv"

    repo1 = CustomerRepository(storage_path=path)

    repo1.add(customer)

    repo1.save()

    repo2 = CustomerRepository(storage_path=path)

    repo2.load()

    loaded = repo2.get(customer.customer_id)

    assert loaded == customer


def test_reload_preserves_count(tmp_path):

    path = tmp_path / "customers.csv"

    repo = CustomerRepository(storage_path=path)

    for i in range(3):

        repo.add(
            Customer(
                customer_id=f"C{i}",
                first_name="John",
                middle_name="A",
                last_name="Smith",
                national_id=f"{1000000000+i}",
                email=EmailAddress(
                    f"user{i}@mail.com"
                ),
                phone=PhoneNumber(
                    f"+966500000{i:03}"
                ),
                address=Address(
                    street="Road",
                    city="Riyadh",
                    state="Riyadh",
                    postal_code="12345",
                    country="Saudi Arabia",
                ),
            )
        )

    repo.save()

    repo2 = CustomerRepository(storage_path=path)

    repo2.load()

    assert repo2.count() == 3

# ============================================================
# CSV Recovery
# ============================================================

def test_load_missing_csv(tmp_path):

    repo = CustomerRepository(
        storage_path=tmp_path / "missing.csv"
    )

    repo.load()

    assert repo.count() == 0


def test_load_empty_csv(tmp_path):

    path = tmp_path / "customers.csv"

    path.write_text("")

    repo = CustomerRepository(storage_path=path)

    repo.load()

    assert repo.count() == 0


def test_load_corrupted_csv(tmp_path):

    path = tmp_path / "customers.csv"

    path.write_text(
        "corrupted,data\n"
        "this,is,not,a,customer"
    )

    repo = CustomerRepository(storage_path=path)

    with pytest.raises(Exception):

        repo.load()

# ============================================================
# Persistence Integrity
# ============================================================

def test_reload_preserves_indexes(tmp_path, customer):

    path = tmp_path / "customers.csv"

    repo = CustomerRepository(storage_path=path)

    repo.add(customer)

    repo.save()

    repo2 = CustomerRepository(storage_path=path)

    repo2.load()

    assert (
        repo2.get_by_email(customer.email)
        == customer
    )

    assert (
        repo2.get_by_phone(customer.phone)
        == customer
    )

    assert (
        repo2.get_by_national_id(
            customer.national_id
        )
        == customer
    )


def test_reload_preserves_object_equality(
    tmp_path,
    customer,
):

    path = tmp_path / "customers.csv"

    repo = CustomerRepository(storage_path=path)

    repo.add(customer)

    repo.save()

    repo2 = CustomerRepository(storage_path=path)

    repo2.load()

    restored = repo2.get(customer.customer_id)

    assert restored == customer

# ============================================================
# Repository Consistency
# ============================================================

def test_update_then_save_then_reload(
    tmp_path,
    customer,
):

    path = tmp_path / "customers.csv"

    repo = CustomerRepository(storage_path=path)

    repo.add(customer)

    customer.last_name = "Johnson"

    repo.update(customer)

    repo.save()

    repo2 = CustomerRepository(storage_path=path)

    repo2.load()

    restored = repo2.get(customer.customer_id)

    assert restored.last_name == "Johnson"


def test_delete_then_save_then_reload(
    tmp_path,
    customer,
):

    path = tmp_path / "customers.csv"

    repo = CustomerRepository(storage_path=path)

    repo.add(customer)

    repo.remove(customer.customer_id)

    repo.save()

    repo2 = CustomerRepository(storage_path=path)

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

    assert summary["total_customers"] == 0


def test_repository_summary_after_insert(repository, customer):

    repository.add(customer)

    summary = repository.repository_summary()

    assert summary["total_customers"] == 1


def test_active_customer_count(repository, customer):

    repository.add(customer)

    assert repository.active_customer_count() == 1


def test_inactive_customer_count(repository, customer):

    customer.status = CustomerStatus.INACTIVE

    repository.add(customer)

    assert repository.inactive_customer_count() == 1

# ============================================================
# Batch Operations
# ============================================================

def test_add_customer_batch(repository):

    customers = []

    for i in range(10):

        customers.append(
            Customer(
                customer_id=f"C{i}",
                first_name=f"First{i}",
                middle_name="A",
                last_name="Last",
                national_id=f"{1000000000+i}",
                email=EmailAddress(f"user{i}@mail.com"),
                phone=PhoneNumber(f"+966500000{i:03}"),
                address=Address(
                    street="Street",
                    city="Riyadh",
                    state="Riyadh",
                    postal_code="12345",
                    country="Saudi Arabia",
                ),
            )
        )

    repository.add_many(customers)

    assert repository.count() == 10


def test_clear_repository(repository, customer):

    repository.add(customer)

    repository.clear()

    assert repository.count() == 0

    assert repository.get_all() == []

# ============================================================
# Boundary Conditions
# ============================================================

def test_unicode_customer_name(repository):

    customer = Customer(
        customer_id="AR001",
        first_name="أحمد",
        middle_name="محمد",
        last_name="العتيبي",
        national_id="3000000000",
        email=EmailAddress("arabic@test.com"),
        phone=PhoneNumber("+966511111111"),
        address=Address(
            street="طريق الملك",
            city="الرياض",
            state="الرياض",
            postal_code="11111",
            country="Saudi Arabia",
        ),
    )

    repository.add(customer)

    assert repository.count() == 1


def test_long_customer_name(repository):

    long_name = "A" * 150

    customer = Customer(
        customer_id="LONG001",
        first_name=long_name,
        middle_name="A",
        last_name="Smith",
        national_id="3000000001",
        email=EmailAddress("long@test.com"),
        phone=PhoneNumber("+966511111112"),
        address=Address(
            street="Road",
            city="Riyadh",
            state="Riyadh",
            postal_code="11111",
            country="Saudi Arabia",
        ),
    )

    repository.add(customer)

    assert repository.get(customer.customer_id) == customer


def test_empty_search(repository):

    assert repository.search_name("") == []


def test_search_whitespace(repository):

    assert repository.search_name("   ") == []

# ============================================================
# Large Repository
# ============================================================

def test_large_repository(repository):

    for i in range(1000):

        repository.add(

            Customer(
                customer_id=f"C{i:05}",
                first_name=f"User{i}",
                middle_name="A",
                last_name="Smith",
                national_id=f"{5000000000+i}",
                email=EmailAddress(
                    f"user{i}@mail.com"
                ),
                phone=PhoneNumber(
                    f"+96655{i:07}"
                ),
                address=Address(
                    street="Street",
                    city="Riyadh",
                    state="Riyadh",
                    postal_code="12345",
                    country="Saudi Arabia",
                ),
            )
        )

    assert repository.count() == 1000

# ============================================================
# Index Consistency
# ============================================================

def test_indexes_after_multiple_updates(
    repository,
    customer,
):

    repository.add(customer)

    customer.email = EmailAddress("updated@test.com")

    customer.phone = PhoneNumber("+966599999998")

    repository.update(customer)

    assert repository.get_by_email(
        EmailAddress("updated@test.com")
    ) == customer

    assert repository.get_by_phone(
        PhoneNumber("+966599999998")
    ) == customer


def test_indexes_after_clear(repository, customer):

    repository.add(customer)

    repository.clear()

    assert repository.count() == 0

    assert (
        repository.get_by_email(customer.email)
        is None
    )

    assert (
        repository.get_by_phone(customer.phone)
        is None
    )

    assert (
        repository.get_by_national_id(
            customer.national_id
        )
        is None
    )

# ============================================================
# Repository Integrity
# ============================================================

def test_repository_iteration(repository):

    for i in range(5):

        repository.add(

            Customer(
                customer_id=f"C{i}",
                first_name="John",
                middle_name="A",
                last_name="Smith",
                national_id=f"{4000000000+i}",
                email=EmailAddress(
                    f"user{i}@mail.com"
                ),
                phone=PhoneNumber(
                    f"+966511000{i:03}"
                ),
                address=Address(
                    street="Road",
                    city="Riyadh",
                    state="Riyadh",
                    postal_code="12345",
                    country="Saudi Arabia",
                ),
            )
        )

    count = 0

    for _ in repository:

        count += 1

    assert count == repository.count()


def test_repository_length(repository):

    assert len(repository) == repository.count()


def test_repository_bool(repository):

    assert bool(repository) is False

    repository.add(customer())

    assert bool(repository) is True

# ============================================================
# Export / Import Helpers
# ============================================================

def test_export_then_import(tmp_path, customer):

    path = tmp_path / "customers.csv"

    repo = CustomerRepository(storage_path=path)

    repo.add(customer)

    repo.export_csv()

    imported = CustomerRepository(storage_path=path)

    imported.import_csv()

    assert imported.count() == 1


def test_repository_copy(repository, customer):

    repository.add(customer)

    copied = repository.copy()

    assert copied.count() == repository.count()

    assert copied.get(customer.customer_id) == customer

