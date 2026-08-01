"""
============================================================
Customer Service Tests
Part 1
------------------------------------------------------------
Coverage

• Service construction
• Dependency injection
• Customer registration
• Duplicate prevention
• Validation failures
============================================================
"""

import pytest

from services.customer_service import CustomerService

from repositories.customer_repository import CustomerRepository

from models.customer import Customer

from models.value_objects.address import Address
from models.value_objects.email import EmailAddress
from models.value_objects.phone import PhoneNumber

from exceptions.banking_exceptions import (
    DuplicateCustomerError,
    ValidationError,
)

test_customer_service.py

# ============================================================
# Fixtures
# ============================================================

@pytest.fixture
def repository(tmp_path):

    return CustomerRepository(
        storage_path=tmp_path / "customers.csv"
    )


@pytest.fixture
def service(repository):

    return CustomerService(repository)


@pytest.fixture
def customer():

    return Customer(

        customer_id="CUST000001",

        first_name="John",

        middle_name="A",

        last_name="Smith",

        national_id="1234567890",

        email=EmailAddress(
            "john@test.com"
        ),

        phone=PhoneNumber(
            "+966501234567"
        ),

        address=Address(

            street="King Road",

            city="Riyadh",

            state="Riyadh",

            postal_code="12345",

            country="Saudi Arabia",

        ),
    )

# ============================================================
# Customer Registration
# ============================================================

def test_register_customer(
    service,
    customer,
):

    service.register_customer(customer)

    assert (
        service.repository.count()
        == 1
    )


def test_registered_customer_exists(
    service,
    customer,
):

    service.register_customer(customer)

    stored = service.get_customer(

        customer.customer_id

    )

    assert stored == customer

# ============================================================
# Duplicate Prevention
# ============================================================

def test_duplicate_customer_id(
    service,
    customer,
):

    service.register_customer(customer)

    with pytest.raises(

        DuplicateCustomerError

    ):

        service.register_customer(customer)


def test_duplicate_national_id(
    service,
    customer,
):

    service.register_customer(customer)

    duplicate = Customer(

        customer_id="CUST000002",

        first_name="Jane",

        middle_name="",

        last_name="Smith",

        national_id=customer.national_id,

        email=EmailAddress(

            "jane@test.com"

        ),

        phone=PhoneNumber(

            "+966500000000"

        ),

        address=customer.address,

    )

    with pytest.raises(

        DuplicateCustomerError

    ):

        service.register_customer(

            duplicate

        )

# ============================================================
# Validation
# ============================================================

def test_register_none(service):

    with pytest.raises(

        ValidationError

    ):

        service.register_customer(None)


def test_register_invalid_type(service):

    with pytest.raises(

        ValidationError

    ):

        service.register_customer(

            "invalid"

        )


def test_register_dictionary(service):

    with pytest.raises(

        ValidationError

    ):

        service.register_customer({})


def test_register_missing_required_fields(
    service,
):

    with pytest.raises(

        ValidationError

    ):

        service.register_customer(

            Customer()

        )

# ============================================================
# Multiple Customers
# ============================================================

def test_register_multiple_customers(
    service,
):

    for i in range(5):

        customer = Customer(

            customer_id=f"CUST{i:04}",

            first_name="John",

            middle_name="",

            last_name="Smith",

            national_id=f"100000000{i}",

            email=EmailAddress(

                f"user{i}@test.com"

            ),

            phone=PhoneNumber(

                f"+9665000000{i}"

            ),

            address=Address(

                street="Road",

                city="Riyadh",

                state="Riyadh",

                postal_code="12345",

                country="Saudi Arabia",

            ),
        )

        service.register_customer(

            customer

        )

    assert (

        service.repository.count()

        == 5

    )

# PART 2

# ============================================================
# Customer Retrieval
# ============================================================

def test_get_customer(
    service,
    customer,
):

    service.register_customer(customer)

    found = service.get_customer(
        customer.customer_id
    )

    assert found == customer


def test_get_unknown_customer(
    service,
):

    assert (
        service.get_customer(
            "UNKNOWN"
        )
        is None
    )


def test_customer_exists(
    service,
    customer,
):

    service.register_customer(customer)

    assert service.customer_exists(
        customer.customer_id
    )


def test_customer_not_exists(
    service,
):

    assert (
        service.customer_exists(
            "UNKNOWN"
        )
        is False
    )

# ============================================================
# Customer Update
# ============================================================

def test_update_customer(
    service,
    customer,
):

    service.register_customer(customer)

    customer.first_name = "Michael"

    service.update_customer(customer)

    updated = service.get_customer(
        customer.customer_id
    )

    assert updated.first_name == "Michael"


def test_update_customer_phone(
    service,
    customer,
):

    service.register_customer(customer)

    customer.phone = PhoneNumber(
        "+966555555555"
    )

    service.update_customer(customer)

    updated = service.get_customer(
        customer.customer_id
    )

    assert (
        updated.phone == customer.phone
    )


def test_update_unknown_customer(
    service,
    customer,
):

    with pytest.raises(KeyError):

        service.update_customer(customer)

# ============================================================
# Customer Deletion
# ============================================================

def test_delete_customer(
    service,
    customer,
):

    service.register_customer(customer)

    service.delete_customer(
        customer.customer_id
    )

    assert (
        service.customer_exists(
            customer.customer_id
        )
        is False
    )


def test_delete_unknown_customer(
    service,
):

    with pytest.raises(KeyError):

        service.delete_customer(
            "UNKNOWN"
        )


def test_repository_empty_after_delete(
    service,
    customer,
):

    service.register_customer(customer)

    service.delete_customer(
        customer.customer_id
    )

    assert (
        service.repository.count()
        == 0
    )

# ============================================================
# Search Operations
# ============================================================

def test_search_by_customer_id(
    service,
    customer,
):

    service.register_customer(customer)

    results = service.search(
        customer.customer_id
    )

    assert customer in results


def test_search_by_last_name(
    service,
    customer,
):

    service.register_customer(customer)

    results = service.search(
        "Smith"
    )

    assert customer in results


def test_search_by_partial_name(
    service,
    customer,
):

    service.register_customer(customer)

    results = service.search(
        "Joh"
    )

    assert customer in results


def test_search_unknown(
    service,
):

    assert (
        service.search("XYZ")
        == []
    )

# ============================================================
# Filtering
# ============================================================

def test_get_all_customers(
    service,
):

    for i in range(3):

        customer = Customer(

            customer_id=f"CUST{i}",

            first_name="John",

            middle_name="",

            last_name="Smith",

            national_id=f"100000000{i}",

            email=EmailAddress(
                f"user{i}@test.com"
            ),

            phone=PhoneNumber(
                f"+9665000000{i}"
            ),

            address=Address(

                street="Road",

                city="Riyadh",

                state="Riyadh",

                postal_code="12345",

                country="Saudi Arabia",

            ),
        )

        service.register_customer(
            customer
        )

    assert (
        len(
            service.get_all_customers()
        )
        == 3
    )


def test_customer_count(
    service,
    customer,
):

    service.register_customer(customer)

    assert (
        service.customer_count()
        == 1
    )

# ============================================================
# Repository Delegation
# ============================================================

def test_repository_matches_service(
    service,
    customer,
):

    service.register_customer(customer)

    assert (

        service.customer_count()

        ==

        service.repository.count()

    )


def test_get_all_matches_repository(
    service,
    customer,
):

    service.register_customer(customer)

    assert (

        service.get_all_customers()

        ==

        service.repository.get_all()

    )

# ============================================================
# Business Rules
# ============================================================

def test_register_same_email_not_allowed(
    service,
    customer,
):

    service.register_customer(customer)

    duplicate = Customer(

        customer_id="CUST999",

        first_name="Jane",

        middle_name="",

        last_name="Doe",

        national_id="9999999999",

        email=customer.email,

        phone=PhoneNumber(
            "+966599999999"
        ),

        address=customer.address,

    )

    with pytest.raises(
        DuplicateCustomerError
    ):

        service.register_customer(
            duplicate
        )


def test_register_same_phone_not_allowed(
    service,
    customer,
):

    service.register_customer(customer)

    duplicate = Customer(

        customer_id="CUST998",

        first_name="Jane",

        middle_name="",

        last_name="Doe",

        national_id="8888888888",

        email=EmailAddress(
            "another@test.com"
        ),

        phone=customer.phone,

        address=customer.address,

    )

    with pytest.raises(
        DuplicateCustomerError
    ):

        service.register_customer(
            duplicate
        )

# PART 3

# ============================================================
# Customer Reporting
# ============================================================

def test_customer_summary_empty(service):

    summary = service.customer_summary()

    assert isinstance(summary, dict)

    assert summary["total_customers"] == 0


def test_customer_summary_after_registration(
    service,
    customer,
):

    service.register_customer(customer)

    summary = service.customer_summary()

    assert summary["total_customers"] == 1


def test_customer_statistics(
    service,
):

    for i in range(5):

        customer = Customer(

            customer_id=f"CUST{i}",

            first_name="John",

            middle_name="",

            last_name="Smith",

            national_id=f"100000000{i}",

            email=EmailAddress(
                f"user{i}@test.com"
            ),

            phone=PhoneNumber(
                f"+9665000000{i}"
            ),

            address=Address(

                street="Road",

                city="Riyadh",

                state="Riyadh",

                postal_code="12345",

                country="Saudi Arabia",

            ),
        )

        service.register_customer(customer)

    summary = service.customer_summary()

    assert summary["total_customers"] == 5

# ============================================================
# Persistence Operations
# ============================================================

def test_save_customers(
    service,
    customer,
):

    service.register_customer(customer)

    service.save()

    assert service.repository.storage_path.exists()


def test_load_customers(
    tmp_path,
    customer,
):

    path = tmp_path / "customers.csv"

    repository = CustomerRepository(
        storage_path=path
    )

    service1 = CustomerService(repository)

    service1.register_customer(customer)

    service1.save()

    repository2 = CustomerRepository(
        storage_path=path
    )

    service2 = CustomerService(repository2)

    service2.load()

    assert service2.customer_count() == 1


def test_reload_preserves_customer(
    tmp_path,
    customer,
):

    path = tmp_path / "customers.csv"

    repository = CustomerRepository(
        storage_path=path
    )

    service1 = CustomerService(repository)

    service1.register_customer(customer)

    service1.save()

    repository2 = CustomerRepository(
        storage_path=path
    )

    service2 = CustomerService(repository2)

    service2.load()

    loaded = service2.get_customer(
        customer.customer_id
    )

    assert loaded == customer

# ============================================================
# Exception Handling
# ============================================================

def test_delete_none(service):

    with pytest.raises(
        ValidationError
    ):

        service.delete_customer(None)


def test_get_none(service):

    with pytest.raises(
        ValidationError
    ):

        service.get_customer(None)


def test_search_none(service):

    with pytest.raises(
        ValidationError
    ):

        service.search(None)


def test_update_none(service):

    with pytest.raises(
        ValidationError
    ):

        service.update_customer(None)

# ============================================================
# Service Consistency
# ============================================================

def test_register_then_delete(
    service,
    customer,
):

    service.register_customer(customer)

    service.delete_customer(
        customer.customer_id
    )

    assert service.customer_count() == 0


def test_update_then_reload(
    tmp_path,
    customer,
):

    path = tmp_path / "customers.csv"

    repository = CustomerRepository(
        storage_path=path
    )

    service = CustomerService(repository)

    service.register_customer(customer)

    customer.first_name = "Michael"

    service.update_customer(customer)

    service.save()

    repository2 = CustomerRepository(
        storage_path=path
    )

    service2 = CustomerService(repository2)

    service2.load()

    updated = service2.get_customer(
        customer.customer_id
    )

    assert updated.first_name == "Michael"


def test_delete_then_reload(
    tmp_path,
    customer,
):

    path = tmp_path / "customers.csv"

    repository = CustomerRepository(
        storage_path=path
    )

    service = CustomerService(repository)

    service.register_customer(customer)

    service.delete_customer(
        customer.customer_id
    )

    service.save()

    repository2 = CustomerRepository(
        storage_path=path
    )

    service2 = CustomerService(repository2)

    service2.load()

    assert service2.customer_count() == 0

# ============================================================
# Edge Cases
# ============================================================

def test_empty_customer_list(service):

    assert service.get_all_customers() == []


def test_customer_count_empty(service):

    assert service.customer_count() == 0


def test_search_empty_string(service):

    assert service.search("") == []


def test_search_whitespace(service):

    assert service.search("   ") == []

# ============================================================
# Repository Synchronization
# ============================================================

def test_repository_sync_after_update(
    service,
    customer,
):

    service.register_customer(customer)

    customer.last_name = "Johnson"

    service.update_customer(customer)

    repository_customer = service.repository.get(
        customer.customer_id
    )

    assert repository_customer.last_name == "Johnson"


def test_repository_sync_after_delete(
    service,
    customer,
):

    service.register_customer(customer)

    service.delete_customer(
        customer.customer_id
    )

    assert service.repository.count() == 0

# ============================================================
# Repository Synchronization
# ============================================================

def test_repository_sync_after_update(
    service,
    customer,
):

    service.register_customer(customer)

    customer.last_name = "Johnson"

    service.update_customer(customer)

    repository_customer = service.repository.get(
        customer.customer_id
    )

    assert repository_customer.last_name == "Johnson"


def test_repository_sync_after_delete(
    service,
    customer,
):

    service.register_customer(customer)

    service.delete_customer(
        customer.customer_id
    )

    assert service.repository.count() == 0


# PART 4

# ============================================================
# Batch Registration
# ============================================================

def test_register_many_customers(
    service,
):

    for i in range(100):

        customer = Customer(

            customer_id=f"CUST{i:05}",

            first_name="John",

            middle_name="",

            last_name="Smith",

            national_id=f"100000000{i}",

            email=EmailAddress(
                f"user{i}@test.com"
            ),

            phone=PhoneNumber(
                f"+9665{i:08}"
            ),

            address=Address(

                street="King Road",

                city="Riyadh",

                state="Riyadh",

                postal_code="12345",

                country="Saudi Arabia",

            ),
        )

        service.register_customer(customer)

    assert service.customer_count() == 100


def test_clear_all_customers(
    service,
):

    for i in range(10):

        customer = Customer(

            customer_id=f"CUST{i}",

            first_name="John",

            middle_name="",

            last_name="Smith",

            national_id=f"200000000{i}",

            email=EmailAddress(
                f"user{i}@test.com"
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

        service.register_customer(customer)

    service.clear()

    assert service.customer_count() == 0

# ============================================================
# Boundary Conditions
# ============================================================

def test_long_customer_name(
    service,
    customer,
):

    customer.first_name = "A" * 100

    service.register_customer(customer)

    assert (
        service.get_customer(
            customer.customer_id
        ).first_name
        == "A" * 100
    )


def test_unicode_customer_name(
    service,
    customer,
):

    customer.first_name = "محمد"

    service.register_customer(customer)

    stored = service.get_customer(
        customer.customer_id
    )

    assert stored.first_name == "محمد"


def test_special_characters_address(
    service,
    customer,
):

    customer.address.street = (
        "King Fahd Rd., Building #25"
    )

    service.register_customer(customer)

    stored = service.get_customer(
        customer.customer_id
    )

    assert (
        stored.address.street
        == "King Fahd Rd., Building #25"
    )

# ============================================================
# Large Dataset
# ============================================================

def test_large_customer_repository(
    service,
):

    for i in range(1000):

        customer = Customer(

            customer_id=f"CUST{i:05}",

            first_name="John",

            middle_name="",

            last_name="Smith",

            national_id=f"900000000{i}",

            email=EmailAddress(
                f"user{i}@test.com"
            ),

            phone=PhoneNumber(
                f"+9666{i:08}"
            ),

            address=Address(

                street="Road",

                city="Riyadh",

                state="Riyadh",

                postal_code="12345",

                country="Saudi Arabia",

            ),
        )

        service.register_customer(customer)

    assert service.customer_count() == 1000

# ============================================================
# Advanced Business Rules
# ============================================================

def test_customer_id_is_immutable(
    service,
    customer,
):

    service.register_customer(customer)

    customer.customer_id = "NEWID"

    with pytest.raises(
        ValidationError
    ):

        service.update_customer(customer)


def test_national_id_is_unique_after_update(
    service,
):

    customer1 = Customer(
        customer_id="C1",
        first_name="John",
        middle_name="",
        last_name="Smith",
        national_id="1111111111",
        email=EmailAddress("a@test.com"),
        phone=PhoneNumber("+966500000001"),
        address=Address(
            street="Road",
            city="Riyadh",
            state="Riyadh",
            postal_code="12345",
            country="Saudi Arabia",
        ),
    )

    customer2 = Customer(
        customer_id="C2",
        first_name="Jane",
        middle_name="",
        last_name="Smith",
        national_id="2222222222",
        email=EmailAddress("b@test.com"),
        phone=PhoneNumber("+966500000002"),
        address=customer1.address,
    )

    service.register_customer(customer1)
    service.register_customer(customer2)

    customer2.national_id = "1111111111"

    with pytest.raises(
        DuplicateCustomerError
    ):

        service.update_customer(customer2)

# ============================================================
# Iteration Support
# ============================================================

def test_service_iteration(
    service,
):

    for i in range(5):

        customer = Customer(

            customer_id=f"C{i}",

            first_name="John",

            middle_name="",

            last_name="Smith",

            national_id=f"77777777{i}",

            email=EmailAddress(
                f"user{i}@test.com"
            ),

            phone=PhoneNumber(
                f"+966500001{i:03}"
            ),

            address=Address(

                street="Road",

                city="Riyadh",

                state="Riyadh",

                postal_code="12345",

                country="Saudi Arabia",

            ),
        )

        service.register_customer(customer)

    count = 0

    for _ in service:

        count += 1

    assert count == service.customer_count()

# ============================================================
# Iteration Support
# ============================================================

def test_service_iteration(
    service,
):

    for i in range(5):

        customer = Customer(

            customer_id=f"C{i}",

            first_name="John",

            middle_name="",

            last_name="Smith",

            national_id=f"77777777{i}",

            email=EmailAddress(
                f"user{i}@test.com"
            ),

            phone=PhoneNumber(
                f"+966500001{i:03}"
            ),

            address=Address(

                street="Road",

                city="Riyadh",

                state="Riyadh",

                postal_code="12345",

                country="Saudi Arabia",

            ),
        )

        service.register_customer(customer)

    count = 0

    for _ in service:

        count += 1

    assert count == service.customer_count()

