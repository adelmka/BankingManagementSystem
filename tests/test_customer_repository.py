# Part 1 — tests/test_customer_repository.py
from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest

from exceptions import (
    EntityAlreadyExistsError,
    EntityNotFoundError,
)

from models.customer import Customer
from models.value_objects.address import Address

from repositories.customer_repository import (
    CustomerRepository,
)

from utils.constants import (
    CustomerStatus,
    Gender,
)


# ==========================================================
# Test Repository
# ==========================================================


class InMemoryCustomerRepository(CustomerRepository):

    def __init__(self, csv_file: Path):

        self.CSV_FILE = csv_file

        super().__init__()


# ==========================================================
# Fixtures
# ==========================================================


@pytest.fixture
def address():

    return Address(
        address_line_1="123 Main Street",
        city="Riyadh",
        state_or_province="Riyadh",
        postal_code="12345",
        country="Saudi Arabia",
    )


@pytest.fixture
def customer(address):

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
    )


@pytest.fixture
def repository(tmp_path):

    return InMemoryCustomerRepository(
        tmp_path / "customers.csv"
    )


@pytest.fixture
def repository_with_customer(
    repository,
    customer,
):

    repository.add(customer)
    """
    print(customer.entity_id)
    print(id(customer))
    """

    return repository


# ==========================================================
# Constructor
# ==========================================================


def test_repository_initializes(repository):

    assert repository.count == 0

    assert repository.is_empty()

    assert repository.file_exists


def test_repository_name(repository):

    assert (
        repository.repository_name
        == "InMemoryCustomerRepository"
    )


def test_entity_type(repository):

    assert repository.entity_type is Customer


# ==========================================================
# find_by_customer_id
# ==========================================================


def test_find_by_customer_id(
    repository_with_customer,
    customer,
):

    result = (
        repository_with_customer
        .find_by_customer_number(
            customer.customer_id
        )
    )

    assert result is customer


def test_find_by_customer_id_returns_none(
    repository_with_customer,
):

    assert (
        repository_with_customer
        .find_by_customer_number(
            "UNKNOWN"
        )
        is None
    )


# ==========================================================
# exists_customer_id
# ==========================================================


def test_exists_customer_id_true(
    repository_with_customer,
    customer,
):

    assert (
        repository_with_customer
        .exists_customer_number(
            customer.customer_id
        )
    )


def test_exists_customer_id_false(
    repository_with_customer,
):

    assert (
        not repository_with_customer
        .exists_customer_number(
            "UNKNOWN"
        )
    )


# ==========================================================
# National ID
# ==========================================================


def test_find_by_national_id(
    repository_with_customer,
    customer,
):

    result = (
        repository_with_customer
        .find_by_national_id(
            customer.national_id
        )
    )

    assert result is customer


def test_find_by_national_id_returns_none(
    repository_with_customer,
):

    assert (
        repository_with_customer
        .find_by_national_id(
            "9999999999"
        )
        is None
    )


def test_exists_national_id_true(
    repository_with_customer,
    customer,
):

    assert (
        repository_with_customer
        .exists_national_id(
            customer.national_id
        )
    )


def test_exists_national_id_false(
    repository_with_customer,
):

    assert (
        not repository_with_customer
        .exists_national_id(
            "9999999999"
        )
    )


# ==========================================================
# Email
# ==========================================================


def test_find_by_email(
    repository_with_customer,
    customer,
):

    result = (
        repository_with_customer
        .find_by_email(
            customer.email
        )
    )

    assert result is customer


def test_find_by_email_case_insensitive(
    repository_with_customer,
    customer,
):

    result = (
        repository_with_customer
        .find_by_email(
            customer.email.upper()
        )
    )

    assert result is customer


def test_find_by_email_returns_none(
    repository_with_customer,
):

    assert (
        repository_with_customer
        .find_by_email(
            "missing@example.com"
        )
        is None
    )


def test_exists_email_true(
    repository_with_customer,
    customer,
):

    assert (
        repository_with_customer
        .exists_email(
            customer.email
        )
    )


def test_exists_email_false(
    repository_with_customer,
):

    assert (
        not repository_with_customer
        .exists_email(
            "missing@example.com"
        )
    )

# PART 2

# ==========================================================
# Phone Number
# ==========================================================


def test_find_by_phone_number(
    repository_with_customer,
    customer,
):

    result = (
        repository_with_customer
        .find_by_mobile_number(
            customer.phone_number
        )
    )

    assert result is customer


def test_find_by_phone_number_returns_none(
    repository_with_customer,
):

    assert (
        repository_with_customer
        .find_by_mobile_number(
            "+966599999999"
        )
        is None
    )


def test_exists_phone_number_true(
    repository_with_customer,
    customer,
):

    assert (
        repository_with_customer
        .exists_mobile_number(
            customer.phone_number
        )
    )


def test_exists_phone_number_false(
    repository_with_customer,
):

    assert (
        not repository_with_customer
        .exists_mobile_number(
            "+966599999999"
        )
    )


# ==========================================================
# Active / Inactive Customers
# ==========================================================


def test_find_active_customers(
    repository_with_customer,
    customer,
):

    customers = (
        repository_with_customer
        .find_active_customers()
    )

    assert len(customers) == 1

    assert customers[0] is customer


def test_find_inactive_customers(
    repository_with_customer,
    customer,
):

    customer.deactivate()

    customers = (
        repository_with_customer
        .find_inactive_customers()
    )

    assert len(customers) == 1

    assert customers[0] is customer


def test_has_active_customers_true(
    repository_with_customer,
):

    assert (
        repository_with_customer
        .has_active_customers()
    )


def test_has_active_customers_false(
    repository_with_customer,
    customer,
):

    customer.deactivate()

    assert (
        not repository_with_customer
        .has_active_customers()
    )


def test_active_customer_count(
    repository_with_customer,
):

    assert (
        repository_with_customer
        .active_customer_count()
        == 1
    )


def test_inactive_customer_count(
    repository_with_customer,
    customer,
):

    customer.deactivate()

    assert (
        repository_with_customer
        .inactive_customer_count()
        == 1
    )


# ==========================================================
# Name Searches
# ==========================================================


def test_find_by_first_name(
    repository_with_customer,
    customer,
):

    results = (
        repository_with_customer
        .find_by_first_name(
            "John"
        )
    )

    assert len(results) == 1

    assert results[0] is customer


def test_find_by_last_name(
    repository_with_customer,
    customer,
):

    results = (
        repository_with_customer
        .find_by_last_name(
            "Smith"
        )
    )

    assert len(results) == 1

    assert results[0] is customer


def test_find_by_full_name(
    repository_with_customer,
    customer,
):

    results = (
        repository_with_customer
        .find_by_full_name(
            customer.full_name
        )
    )

    assert len(results) == 1

    assert results[0] is customer


def test_find_by_first_name_case_insensitive(
    repository_with_customer,
    customer,
):

    results = (
        repository_with_customer
        .find_by_first_name(
            "john"
        )
    )

    assert customer in results


def test_find_by_last_name_case_insensitive(
    repository_with_customer,
    customer,
):

    results = (
        repository_with_customer
        .find_by_last_name(
            "smith"
        )
    )

    assert customer in results


def test_find_by_full_name_case_insensitive(
    repository_with_customer,
    customer,
):

    results = (
        repository_with_customer
        .find_by_full_name(
            customer.full_name.lower()
        )
    )

    assert customer in results


def test_find_by_first_name_not_found(
    repository_with_customer,
):

    assert (
        repository_with_customer
        .find_by_first_name(
            "Michael"
        )
        == []
    )


def test_find_by_last_name_not_found(
    repository_with_customer,
):

    assert (
        repository_with_customer
        .find_by_last_name(
            "Jordan"
        )
        == []
    )


def test_find_by_full_name_not_found(
    repository_with_customer,
):

    assert (
        repository_with_customer
        .find_by_full_name(
            "Unknown Person"
        )
        == []
    )

# PART 3

# ==========================================================
# Find by National ID
# ==========================================================

def test_find_by_national_id(
    repository_with_customer,
    sample_customer,
):
    customer = repository_with_customer.find_by_national_id(
        sample_customer.national_id
    )

    assert customer.customer_id == sample_customer.customer_id


def test_find_by_national_id_not_found(
    repository_with_customer,
):
    assert (
        repository_with_customer.find_by_national_id(
            "9999999999"
        )
        is None
    )


def test_exists_national_id(
    repository_with_customer,
    sample_customer,
):
    assert repository_with_customer.exists_national_id(
        sample_customer.national_id
    )


def test_exists_national_id_false(
    repository_with_customer,
):
    assert not repository_with_customer.exists_national_id(
        "9999999999"
    )


# ==========================================================
# Email
# ==========================================================

def test_find_by_email(
    repository_with_customer,
    sample_customer,
):
    customer = repository_with_customer.find_by_email(
        sample_customer.email
    )

    assert customer.customer_id == sample_customer.customer_id


def test_find_by_email_case_insensitive(
    repository_with_customer,
    sample_customer,
):
    customer = repository_with_customer.find_by_email(
        sample_customer.email.upper()
    )

    assert customer is sample_customer


def test_exists_email(
    repository_with_customer,
    sample_customer,
):
    assert repository_with_customer.exists_email(
        sample_customer.email
    )


def test_exists_email_false(
    repository_with_customer,
):
    assert not repository_with_customer.exists_email(
        "missing@example.com"
    )


# ==========================================================
# Mobile Number
# ==========================================================

def test_find_by_mobile_number(
    repository_with_customer,
    customer,
):
    found = (
        repository_with_customer.find_by_mobile_number(
            customer.phone_number
        )
    )

    assert found is customer


def test_find_by_mobile_number_not_found(
    repository_with_customer,
):
    assert (
        repository_with_customer.find_by_mobile_number(
            "+966599999999"
        )
        is None
    )


def test_exists_mobile_number(
    repository_with_customer,
    sample_customer,
):
    assert repository_with_customer.exists_mobile_number(
        sample_customer.phone_number
    )


def test_exists_mobile_number_false(
    repository_with_customer,
):
    assert not repository_with_customer.exists_mobile_number(
        "+966599999999"
    )


# ==========================================================
# Active / Inactive
# ==========================================================

def test_find_active_customers(
    repository_with_customer,
):
    customers = (
        repository_with_customer.find_active_customers()
    )

    assert len(customers) == 1

def test_find_inactive_customers(
    repository_with_customer,
    customer,
):
    customer.deactivate()

    repository_with_customer.update(customer)

    customers = repository_with_customer.find_inactive_customers()

    assert len(customers) == 1
    assert customers[0] is customer
"""
def test_find_inactive_customers(
    repository_with_customer,
    sample_customer,
):
    sample_customer.deactivate()
    # print(sample_customer.entity_id)

    # print(repository_with_customer.find_all(active_only=False)[0].entity_id)
    
    repository_with_customer.update(
        sample_customer
    )

    customers = (
        repository_with_customer.find_inactive_customers()
    )

    assert len(customers) == 1
    assert customers[0] is sample_customer
"""

def test_has_active_customers(
    repository_with_customer,
):
    assert repository_with_customer.has_active_customers()


def test_active_customer_count(
    repository_with_customer,
):
    assert (
        repository_with_customer.active_customer_count()
        == 1
    )


def test_inactive_customer_count(
    repository_with_customer,
):
    assert (
        repository_with_customer.inactive_customer_count()
        == 0
    )

# PART 4

# ============================================================
# Statistics & Search
# ============================================================

def test_customer_statistics(
    repository_with_customer,
):

    stats = repository_with_customer.customer_statistics()

    assert stats["total_customers"] == 1
    assert stats["active_customers"] == 1
    assert stats["inactive_customers"] == 0


def test_statistics_alias(
    repository_with_customer,
):

    stats = repository_with_customer.statistics()

    assert stats["total_customers"] == 1
    assert stats["active_customers"] == 1
    assert stats["inactive_customers"] == 0


def test_search_by_first_name(
    repository_with_customer,
):

    results = repository_with_customer.search("john")

    assert len(results) == 1


def test_search_by_last_name(
    repository_with_customer,
):

    results = repository_with_customer.search("smith")

    assert len(results) == 1


def test_search_by_email(
    repository_with_customer,
):

    results = repository_with_customer.search(
        "john.smith@example.com"
    )

    assert len(results) == 1


def test_search_by_national_id(
    repository_with_customer,
    sample_customer,
):

    results = repository_with_customer.search(
        sample_customer.national_id
    )

    assert len(results) == 1


def test_search_by_city(
    repository_with_customer,
):

    results = repository_with_customer.search("riyadh")

    assert len(results) == 1


def test_search_returns_empty_when_not_found(
    repository_with_customer,
):

    assert (
        repository_with_customer.search("does-not-exist")
        == []
    )


# ============================================================
# Validation & Add Customer
# ============================================================

def test_validate_unique_customer_success(
    repository,
    sample_customer,
):

    repository.validate_unique_customer(
        sample_customer
    )


def test_validate_duplicate_customer_id(
    repository_with_customer,
    sample_customer,
):

    duplicate = sample_customer

    with pytest.raises(
        EntityAlreadyExistsError,
    ):
        repository_with_customer.validate_unique_customer(
            duplicate
        )


def test_add_customer(
    repository,
    sample_customer,
):

    repository.add_customer(sample_customer)

    assert repository.count == 1


def test_add_duplicate_customer(
    repository_with_customer,
    sample_customer,
):

    with pytest.raises(
        EntityAlreadyExistsError,
    ):
        repository_with_customer.add_customer(
            sample_customer
        )


def test_customer_exists(
    repository_with_customer,
    sample_customer,
):

    assert repository_with_customer.customer_exists(
        sample_customer.customer_id
    )


def test_customer_exists_false(
    repository,
):

    assert (
        repository.customer_exists(
            "UNKNOWN"
        )
        is False
    )


# ============================================================
# Get or Raise
# ============================================================

def test_get_or_raise_success(
    repository_with_customer,
    sample_customer,
):

    customer = (
        repository_with_customer.get_or_raise(
            sample_customer.customer_id
        )
    )

    assert customer.customer_id == sample_customer.customer_id


def test_get_or_raise_not_found(
    repository,
):

    with pytest.raises(
        EntityNotFoundError,
    ):
        repository.get_or_raise(
            "UNKNOWN"
        )

# PART 5

# ============================================================
# String Representation
# ============================================================

def test_str(
    repository_with_customer,
):

    text = str(
        repository_with_customer
    )

    assert "CustomerRepository" in text
    assert "customers=1" in text


def test_repr(
    repository_with_customer,
):

    text = repr(
        repository_with_customer
    )

    assert "CustomerRepository" in text
    assert "count=1" in text
    assert "customers.csv" in text


# ============================================================
# Edge Cases
# ============================================================

def test_find_by_email_case_insensitive(
    repository_with_customer,
):

    customer = (
        repository_with_customer.find_by_email(
            "JOHN.SMITH@EXAMPLE.COM"
        )
    )

    assert customer is not None


def test_find_by_first_name_case_insensitive(
    repository_with_customer,
):

    customers = (
        repository_with_customer.find_by_first_name(
            "JOHN"
        )
    )

    assert len(customers) == 1


def test_find_by_last_name_case_insensitive(
    repository_with_customer,
):

    customers = (
        repository_with_customer.find_by_last_name(
            "SMITH"
        )
    )

    assert len(customers) == 1


def test_find_by_city_case_insensitive(
    repository_with_customer,
):

    customers = (
        repository_with_customer.find_by_city(
            "RIYADH"
        )
    )

    assert len(customers) == 1


def test_find_by_country_case_insensitive(
    repository_with_customer,
):

    customers = (
        repository_with_customer.find_by_country(
            "SAUDI ARABIA"
        )
    )

    assert len(customers) == 1


def test_search_case_insensitive(
    repository_with_customer,
):

    results = (
        repository_with_customer.search(
            "SMITH"
        )
    )

    assert len(results) == 1


def test_repository_starts_empty(
    repository,
):

    assert repository.count == 0
    assert repository.is_empty()


def test_repository_not_empty_after_add(
    repository,
    sample_customer,
):

    repository.add_customer(
        sample_customer
    )

    assert repository.count == 1
    assert not repository.is_empty()


def test_active_customer_count_empty(
    repository,
):

    assert (
        repository.active_customer_count()
        == 0
    )


def test_inactive_customer_count_empty(
    repository,
):

    assert (
        repository.inactive_customer_count()
        == 0
    )
