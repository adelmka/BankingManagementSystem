# Part 1 will establish the reusable fixtures and cover service initialization plus customer registration

from __future__ import annotations

from datetime import date

import pytest

from exceptions import (
    EntityAlreadyExistsError,
    ValidationError,
)

from models.customer import Customer
from models.value_objects.address import Address

from repositories.customer_repository import CustomerRepository

from services.customer_service import CustomerService

from utils.constants import (
    CustomerStatus,
    Gender,
)


# ============================================================================
# Test Repository Helper
# ============================================================================


class ServiceCustomerRepository(CustomerRepository):
    """
    Concrete repository helper used by CustomerService tests.

    The class name intentionally does not begin with "Test" so pytest
    does not attempt to collect it as a test class.
    """

    def __init__(self, csv_file) -> None:
        self.CSV_FILE = csv_file
        super().__init__()


# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def repository(tmp_path):
    """
    Return an isolated customer repository for the current test.
    """

    repository = ServiceCustomerRepository(
        tmp_path / "customers.csv"
    )

    return repository


@pytest.fixture
def service(repository):
    """
    Return a CustomerService using the isolated repository.
    """

    return CustomerService(repository)


@pytest.fixture
def address():
    """
    Return a valid address.
    """

    return Address(
        address_line_1="123 Main Street",
        city="Riyadh",
        state_or_province="Riyadh",
        postal_code="12345",
        country="Saudi Arabia",
    )


@pytest.fixture
def customer(address):
    """
    Return a valid customer.
    """

    return Customer(
        customer_id="C000001",
        first_name="John",
        last_name="Smith",
        date_of_birth=date(1990, 1, 1),
        gender=Gender.MALE,
        national_id="1234567890",
        email="john.smith@example.com",
        phone_number="+966500000001",
        address=address,
        customer_status=CustomerStatus.ACTIVE,
        registration_date=date(2026, 1, 1),
        kyc_completed=True,
    )


@pytest.fixture
def second_customer():
    """
    Return a second valid customer.
    """

    address = Address(
        address_line_1="456 King Fahd Road",
        city="Dammam",
        state_or_province="Eastern Province",
        postal_code="31411",
        country="Saudi Arabia",
    )

    return Customer(
        customer_id="C000002",
        first_name="Jane",
        last_name="Doe",
        date_of_birth=date(1992, 5, 15),
        gender=Gender.FEMALE,
        national_id="2234567890",
        email="jane.doe@example.com",
        phone_number="+966500000002",
        address=address,
        customer_status=CustomerStatus.ACTIVE,
        registration_date=date(2026, 1, 2),
        kyc_completed=True,
    )


@pytest.fixture
def repository_with_customer(repository, customer):
    """
    Return a repository containing one customer.
    """

    repository.add_customer(customer)

    return repository


@pytest.fixture
def service_with_customer(repository_with_customer):
    """
    Return a CustomerService backed by a repository containing one
    customer.
    """

    return CustomerService(repository_with_customer)


# ============================================================================
# Service Initialization
# ============================================================================


def test_service_initialization(
    service,
    repository,
):
    """
    CustomerService should retain the supplied repository.
    """

    assert service.repository is repository


def test_service_entity_count_initially_zero(
    service,
):
    """
    A newly initialized service should report zero entities.
    """

    assert service.entity_count == 0


def test_service_repository_property(
    service,
    repository,
):
    """
    The inherited repository property should expose the same repository
    supplied during construction.
    """

    assert service.repository is repository


# ============================================================================
# Customer Registration
# ============================================================================


def test_register_customer(
    service,
    repository,
    customer,
):
    """
    register_customer() should persist a valid customer and return
    the same Customer instance.
    """

    result = service.register_customer(customer)

    assert result is customer
    assert service.entity_count == 1

    found = repository.find_by_customer_number(
        customer.customer_id
    )

    assert found is not None
    assert found.customer_id == customer.customer_id


def test_register_customer_returns_same_instance(
    service,
    customer,
):
    """
    register_customer() should return the customer supplied by the caller.
    """

    result = service.register_customer(customer)

    assert result is customer


def test_register_customer_increases_entity_count(
    service,
    customer,
):
    """
    Successful registration should increase the service entity count.
    """

    assert service.entity_count == 0

    service.register_customer(customer)

    assert service.entity_count == 1


def test_register_multiple_customers(
    service,
    customer,
    second_customer,
):
    """
    Multiple valid customers should be registered successfully.
    """

    first_result = service.register_customer(customer)
    second_result = service.register_customer(second_customer)

    assert first_result is customer
    assert second_result is second_customer
    assert service.entity_count == 2


def test_register_duplicate_customer_id_raises(
    service,
    customer,
):
    """
    Registering the same customer identifier twice should raise the
    repository's duplicate-entity exception.
    """

    service.register_customer(customer)

    with pytest.raises(EntityAlreadyExistsError):
        service.register_customer(customer)


def test_register_duplicate_national_id_raises(
    service,
    customer,
    second_customer,
):
    """
    Two customers with the same national ID should not be registered.
    """

    service.register_customer(customer)

    second_customer.national_id = customer.national_id

    with pytest.raises(EntityAlreadyExistsError):
        service.register_customer(second_customer)


def test_register_duplicate_email_raises(
    service,
    customer,
    second_customer,
):
    """
    Two customers with the same email address should not be registered.
    """

    service.register_customer(customer)

    second_customer.email = customer.email

    with pytest.raises(EntityAlreadyExistsError):
        service.register_customer(second_customer)


def test_register_duplicate_phone_number_raises(
    service,
    customer,
    second_customer,
):
    """
    Two customers with the same phone number should not be registered.
    """

    service.register_customer(customer)

    second_customer.phone_number = customer.phone_number

    with pytest.raises(EntityAlreadyExistsError):
        service.register_customer(second_customer)


# ============================================================================
# Registration Validation
# ============================================================================


def test_register_none_customer_raises_validation_error(
    service,
):
    """
    register_customer() should reject None before persistence.
    """

    with pytest.raises(ValidationError):
        service.register_customer(None)


def test_failed_registration_does_not_add_customer(
    service,
):
    """
    A failed validation should not create a repository entity.
    """

    with pytest.raises(ValidationError):
        service.register_customer(None)

    assert service.entity_count == 0


def test_failed_duplicate_registration_does_not_increase_count(
    service,
    customer,
):
    """
    A duplicate registration should leave the entity count unchanged.
    """

    service.register_customer(customer)

    with pytest.raises(EntityAlreadyExistsError):
        service.register_customer(customer)

    assert service.entity_count == 1


# ============================================================================
# Registration Persistence
# ============================================================================


def test_registered_customer_can_be_retrieved(
    service,
    customer,
):
    """
    A successfully registered customer should subsequently be retrievable
    through the service.
    """

    service.register_customer(customer)

    found = service.find_customer(
        customer.customer_id
    )

    assert found is not None
    assert found.customer_id == customer.customer_id


def test_register_customer_preserves_customer_data(
    service,
    customer,
):
    """
    Registration should preserve the customer's core business data.
    """

    service.register_customer(customer)

    found = service.find_customer(
        customer.customer_id
    )

    assert found is not None
    assert found.first_name == customer.first_name
    assert found.last_name == customer.last_name
    assert found.national_id == customer.national_id
    assert found.email == customer.email
    assert found.phone_number == customer.phone_number
    assert found.customer_status == customer.customer_status
    assert found.registration_date == customer.registration_date
    assert found.kyc_completed == customer.kyc_completed


# ============================================================================
# End of Part 1
# ============================================================================


# ============================================================================
# Part 2 — Lookup, Collection, Maintenance, and Lifecycle Operations
# ============================================================================


# ============================================================================
# Customer Lookup
# ============================================================================


def test_find_customer_returns_customer(
    service_with_customer,
    customer,
):
    """
    find_customer() should return the registered customer.
    """

    found = service_with_customer.find_customer(
        customer.customer_id
    )

    assert found is not None
    assert found.customer_id == customer.customer_id


def test_find_customer_returns_none_for_unknown_customer(
    service,
):
    """
    find_customer() should return None when the customer does not exist.
    """

    result = service.find_customer("C999999")

    assert result is None


def test_get_customer_returns_customer(
    service_with_customer,
    customer,
):
    """
    get_customer() should return the requested customer.
    """

    found = service_with_customer.get_customer(
        customer.customer_id
    )

    assert found is not None
    assert found.customer_id == customer.customer_id


def test_get_customer_raises_for_unknown_customer(
    service,
):
    """
    get_customer() should raise when the requested customer does not exist.
    """

    with pytest.raises(Exception):
        service.get_customer("C999999")


# ============================================================================
# Customer Existence
# ============================================================================


def test_customer_exists_returns_true(
    service_with_customer,
    customer,
):
    """
    customer_exists() should return True for a registered customer.
    """

    assert (
        service_with_customer.customer_exists(
            customer.customer_id
        )
        is True
    )


def test_customer_exists_returns_false(
    service,
):
    """
    customer_exists() should return False for an unknown customer.
    """

    assert (
        service.customer_exists("C999999")
        is False
    )


# ============================================================================
# Customer Collection
# ============================================================================


def test_all_customers_returns_registered_customers(
    service,
    customer,
    second_customer,
):
    """
    all_customers() should return the registered customers.
    """

    service.register_customer(customer)
    service.register_customer(second_customer)

    customers = service.all_customers()

    assert len(customers) == 2

    customer_ids = {
        item.customer_id
        for item in customers
    }

    assert customer.customer_id in customer_ids
    assert second_customer.customer_id in customer_ids


def test_all_customers_empty_service(
    service,
):
    """
    all_customers() should return an empty collection when no customers
    have been registered.
    """

    customers = service.all_customers()

    assert customers == []


# ============================================================================
# Customer Update
# ============================================================================


def test_update_customer_persists_changes(
    service_with_customer,
    customer,
):
    """
    update_customer() should persist changes to an existing customer.
    """

    customer.email = "updated.email@example.com"

    result = service_with_customer.update_customer(
        customer
    )

    assert result is customer

    found = service_with_customer.find_customer(
        customer.customer_id
    )

    assert found is not None
    assert found.email == "updated.email@example.com"


def test_update_customer_preserves_customer_identity(
    service_with_customer,
    customer,
):
    """
    update_customer() should retain the customer's business identifier.
    """

    original_id = customer.customer_id

    service_with_customer.update_customer(
        customer
    )

    found = service_with_customer.find_customer(
        original_id
    )

    assert found is not None
    assert found.customer_id == original_id


def test_update_unknown_customer_raises(
    service,
    customer,
):
    """
    Updating a customer that is not registered should raise an exception.
    """

    with pytest.raises(Exception):
        service.update_customer(customer)


# ============================================================================
# Customer Activation
# ============================================================================


def test_activate_customer(
    service_with_customer,
    customer,
):
    """
    activate_customer() should activate an inactive customer.
    """

    customer.close_customer()

    service_with_customer.update_customer(
        customer
    )

    result = service_with_customer.activate_customer(
        customer.customer_id
    )

    assert result is not None
    assert result.customer_status == CustomerStatus.ACTIVE
    assert result.is_active is True


def test_activate_customer_not_found(
    service,
):
    """
    Activating an unknown customer should raise an exception.
    """

    with pytest.raises(Exception):
        service.activate_customer("C999999")


# ============================================================================
# Customer Deactivation
# ============================================================================


def test_deactivate_customer(
    service_with_customer,
    customer,
):
    """
    deactivate_customer() should close an active customer
    and mark the entity as inactive.
    """

    result = service_with_customer.deactivate_customer(
        customer.customer_id,
    )

    assert result is not None
    assert result.customer_id == customer.customer_id
    assert result.customer_status == CustomerStatus.INACTIVE
    assert result.is_active is False

    def test_deactivate_customer_persists_state(
        service_with_customer,
        customer,
    ):
        """
        Deactivation should persist the changed customer state.
        """

        service_with_customer.deactivate_customer(
            customer.customer_id
        )

        found = service_with_customer.find_customer(
            customer.customer_id,
            active_only=False,
        )

        assert found is not None
        assert found.customer_status == CustomerStatus.INACTIVE
        assert found.is_active is False


def test_deactivate_customer_not_found(
    service,
):
    """
    Deactivating an unknown customer should raise an exception.
    """

    with pytest.raises(Exception):
        service.deactivate_customer("C999999")


# ============================================================================
# Customer Reactivation
# ============================================================================


def test_reactivate_customer(
    service_with_customer,
    customer,
):
    """
    reactivate_customer() should restore an inactive customer to active
    status.
    """

    service_with_customer.deactivate_customer(
        customer.customer_id
    )

    result = service_with_customer.reactivate_customer(
        customer.customer_id
    )

    assert result is not None
    assert result.customer_id == customer.customer_id
    assert result.customer_status == CustomerStatus.ACTIVE


def test_reactivate_customer_persists_state(
    service_with_customer,
    customer,
):
    """
    Reactivation should persist the customer's active state.
    """

    service_with_customer.deactivate_customer(
        customer.customer_id
    )

    service_with_customer.reactivate_customer(
        customer.customer_id
    )

    found = service_with_customer.find_customer(
        customer.customer_id
    )

    assert found is not None
    assert found.customer_status == CustomerStatus.ACTIVE


def test_reactivate_customer_not_found(
    service,
):
    """
    Reactivating an unknown customer should raise an exception.
    """

    with pytest.raises(Exception):
        service.reactivate_customer("C999999")


# ============================================================================
# Customer Archival
# ============================================================================


def test_archive_customer(
    service_with_customer,
    customer,
):
    """
    archive_customer() should transition an existing customer
    out of the active state.
    """

    result = service_with_customer.archive_customer(
        customer.customer_id
    )

    assert result is True

    archived = service_with_customer.find_customer(
        customer.customer_id,
        active_only=False,
    )

    assert archived is not None
    assert archived.customer_id == customer.customer_id
    assert archived.is_active is False

def test_archive_customer_persists_state(
    service_with_customer,
    customer,
):
    """
    Archiving should persist the resulting customer state.
    """

    service_with_customer.archive_customer(
        customer.customer_id
    )

    found = service_with_customer.find_customer(
        customer.customer_id,
        active_only=False,
    )

    assert found is not None
    assert found.customer_id == customer.customer_id
    assert found.is_active is False


def test_archive_customer_not_found(
    service,
):
    """
    Archiving an unknown customer should raise an exception.
    """

    with pytest.raises(Exception):
        service.archive_customer("C999999")


# ============================================================================
# Lifecycle Sequence
# ============================================================================


def test_customer_lifecycle_deactivate_reactivate(
    service_with_customer,
    customer,
):
    """
    A customer should support the normal deactivate/reactivate lifecycle.
    """

    service_with_customer.deactivate_customer(
        customer.customer_id
    )

    inactive = service_with_customer.find_customer(
        customer.customer_id,
        active_only=False,
    )

    assert inactive is not None
    assert inactive.customer_id == customer.customer_id
    assert inactive.customer_status == CustomerStatus.INACTIVE
    assert inactive.is_active is False
    

def test_customer_lifecycle_preserves_customer_id(
    service_with_customer,
    customer,
):
    """
    Customer lifecycle operations should never change customer_id.
    """

    customer_id = customer.customer_id

    service_with_customer.deactivate_customer(
        customer_id
    )

    service_with_customer.reactivate_customer(
        customer_id
    )

    found = service_with_customer.find_customer(
        customer_id
    )

    assert found is not None
    assert found.customer_id == customer_id


# ============================================================================
# End of Part 2
# ============================================================================


