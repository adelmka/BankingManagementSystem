# Part 1 — tests/test_customer_repository.py

from __future__ import annotations

from pathlib import Path

import pytest

import config

from exceptions import (
    EntityAlreadyExistsError,
    EntityNotFoundError,
)

from repositories.customer_repository import (
    CustomerRepository,
)

from models.customer import Customer


# ---------------------------------------------------------
# Fixtures
# ---------------------------------------------------------

@pytest.fixture
def repository(
    tmp_path,
    monkeypatch,
):
    """
    Create an isolated repository using a temporary CSV file.
    """

    csv_file = tmp_path / "customers.csv"

    monkeypatch.setattr(
        config,
        "CUSTOMERS_FILE",
        csv_file,
    )

    CustomerRepository.CSV_FILE = csv_file

    return CustomerRepository()


@pytest.fixture
def repository_with_customer(
    repository,
    sample_customer,
):
    repository.add(sample_customer)
    return repository


# ---------------------------------------------------------
# Construction
# ---------------------------------------------------------

def test_repository_initializes_empty(
    repository,
):

    assert repository.count == 0

    assert repository.is_empty()


def test_entity_class(
    repository,
):

    assert repository.ENTITY_CLASS is Customer


def test_csv_file_created(
    repository,
):

    assert repository.CSV_FILE.exists()


# ---------------------------------------------------------
# Customer Number
# ---------------------------------------------------------

def test_find_by_customer_number(
    repository_with_customer,
    sample_customer,
):

    customer = (
        repository_with_customer
        .find_by_customer_number(
            sample_customer.customer_id
        )
    )

    assert customer == sample_customer


def test_find_by_customer_number_not_found(
    repository,
):

    assert (
        repository.find_by_customer_number(
            "CUST999999"
        )
        is None
    )


def test_exists_customer_number_true(
    repository_with_customer,
    sample_customer,
):

    assert repository_with_customer.exists_customer_number(
        sample_customer.customer_id
    )


def test_exists_customer_number_false(
    repository,
):

    assert not repository.exists_customer_number(
        "CUST999999"
    )

# Part 2 — Identity & Contact Lookup Tests

# ---------------------------------------------------------
# National ID
# ---------------------------------------------------------

def test_find_by_national_id(
    repository_with_customer,
    sample_customer,
):

    customer = (
        repository_with_customer.find_by_national_id(
            sample_customer.national_id
        )
    )

    assert customer == sample_customer


def test_find_by_national_id_not_found(
    repository,
):

    assert (
        repository.find_by_national_id(
            "9999999999"
        )
        is None
    )


def test_exists_national_id_true(
    repository_with_customer,
    sample_customer,
):

    assert repository_with_customer.exists_national_id(
        sample_customer.national_id
    )


def test_exists_national_id_false(
    repository,
):

    assert not repository.exists_national_id(
        "9999999999"
    )


# ---------------------------------------------------------
# Passport Number
# ---------------------------------------------------------
""" --- remove the passport test entirely
def test_find_by_passport_number(
    repository_with_customer,
    sample_customer,
):

    customer = (
        repository_with_customer.find_by_passport_number(
            sample_customer.passport_number
        )
    )

    assert customer == sample_customer


def test_find_by_passport_number_not_found(
    repository,
):

    assert (
        repository.find_by_passport_number(
            "P9999999"
        )
        is None
    )


def test_exists_passport_number_true(
    repository_with_customer,
    sample_customer,
):

    assert repository_with_customer.exists_passport_number(
        sample_customer.passport_number
    )


def test_exists_passport_number_false(
    repository,
):

    assert not repository.exists_passport_number(
        "P9999999"
    )

"""

# ---------------------------------------------------------
# Email
# ---------------------------------------------------------

def test_find_by_email(
    repository_with_customer,
    sample_customer,
):

    customer = (
        repository_with_customer.find_by_email(
            sample_customer.email
        )
    )

    assert customer == sample_customer


def test_find_by_email_case_insensitive(
    repository_with_customer,
    sample_customer,
):

    customer = (
        repository_with_customer.find_by_email(
            sample_customer.email.upper()
        )
    )

    assert customer == sample_customer


def test_exists_email_true(
    repository_with_customer,
    sample_customer,
):

    assert repository_with_customer.exists_email(
        sample_customer.email
    )


def test_exists_email_false(
    repository,
):

    assert not repository.exists_email(
        "missing@example.com"
    )


# ---------------------------------------------------------
# Mobile Number
# ---------------------------------------------------------

def test_find_by_mobile_number(
    repository_with_customer,
    sample_customer,
):

    customer = (
        repository_with_customer.find_by_mobile_number(
            sample_customer.phone_number
        )
    )

    assert customer == sample_customer


def test_find_by_mobile_number_not_found(
    repository,
):

    assert (
        repository.find_by_mobile_number(
            "0500000000"
        )
        is None
    )


def test_exists_mobile_number_true(
    repository_with_customer,
    sample_customer,
):

    assert repository_with_customer.exists_mobile_number(
        sample_customer.phone_number
    )


def test_exists_mobile_number_false(
    repository,
):

    assert not repository.exists_mobile_number(
        "0500000000"
    )


# ---------------------------------------------------------
# Active / Inactive Customers
# ---------------------------------------------------------

def test_find_active_customers(
    repository_with_customer,
    sample_customer,
):

    customers = (
        repository_with_customer.find_active_customers()
    )

    assert len(customers) == 1

    assert customers[0] == sample_customer


def test_find_inactive_customers(
    repository_with_customer,
    sample_customer,
):

    sample_customer.deactivate()

    customers = (
        repository_with_customer.find_inactive_customers()
    )

    assert len(customers) == 1

    assert customers[0] == sample_customer


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
    sample_customer,
):

    sample_customer.deactivate()

    assert (
        repository_with_customer.inactive_customer_count()
        == 1
    )

# Part 3 — Name, Address & Search Tests

# ---------------------------------------------------------
# Name Searches
# ---------------------------------------------------------

def test_find_by_first_name(
    repository_with_customer,
    sample_customer,
):

    customers = (
        repository_with_customer.find_by_first_name(
            sample_customer.first_name
        )
    )

    assert len(customers) == 1
    assert customers[0] == sample_customer


def test_find_by_last_name(
    repository_with_customer,
    sample_customer,
):

    customers = (
        repository_with_customer.find_by_last_name(
            sample_customer.last_name
        )
    )

    assert len(customers) == 1
    assert customers[0] == sample_customer


def test_find_by_full_name(
    repository_with_customer,
    sample_customer,
):

    customers = (
        repository_with_customer.find_by_full_name(
            sample_customer.full_name
        )
    )

    assert len(customers) == 1
    assert customers[0] == sample_customer


def test_find_by_first_name_case_insensitive(
    repository_with_customer,
    sample_customer,
):

    customers = (
        repository_with_customer.find_by_first_name(
            sample_customer.first_name.lower()
        )
    )

    assert len(customers) == 1


def test_find_by_last_name_case_insensitive(
    repository_with_customer,
    sample_customer,
):

    customers = (
        repository_with_customer.find_by_last_name(
            sample_customer.last_name.upper()
        )
    )

    assert len(customers) == 1


def test_find_by_full_name_case_insensitive(
    repository_with_customer,
    sample_customer,
):

    customers = (
        repository_with_customer.find_by_full_name(
            sample_customer.full_name.lower()
        )
    )

    assert len(customers) == 1


# ---------------------------------------------------------
# Address Searches
# ---------------------------------------------------------

def test_find_by_city(
    repository_with_customer,
    sample_customer,
):

    customers = (
        repository_with_customer.find_by_city(
            sample_customer.address.city
        )
    )

    assert len(customers) == 1
    assert customers[0] == sample_customer


def test_find_by_country(
    repository_with_customer,
    sample_customer,
):

    customers = (
        repository_with_customer.find_by_country(
            sample_customer.address.country
        )
    )

    assert len(customers) == 1
    assert customers[0] == sample_customer


def test_find_by_city_case_insensitive(
    repository_with_customer,
    sample_customer,
):

    customers = (
        repository_with_customer.find_by_city(
            sample_customer.address.city.lower()
        )
    )

    assert len(customers) == 1


def test_find_by_country_case_insensitive(
    repository_with_customer,
    sample_customer,
):

    customers = (
        repository_with_customer.find_by_country(
            sample_customer.address.country.upper()
        )
    )

    assert len(customers) == 1


# ---------------------------------------------------------
# Search
# ---------------------------------------------------------

@pytest.mark.parametrize(
    "search_text",
    [
        lambda c: c.customer_id,
        lambda c: c.first_name,
        lambda c: c.last_name,
        lambda c: c.full_name,
        lambda c: c.email,
        lambda c: c.phone_number,
        lambda c: c.national_id,
        lambda c: c.address.city,
        lambda c: c.address.country,
    ],
)
def test_search_matches_fields(
    repository_with_customer,
    sample_customer,
    search_text,
):

    results = repository_with_customer.search(
        search_text(sample_customer)
    )

    assert len(results) == 1
    assert results[0] == sample_customer


def test_search_case_insensitive(
    repository_with_customer,
    sample_customer,
):

    results = repository_with_customer.search(
        sample_customer.email.upper()
    )

    assert len(results) == 1


def test_search_partial_match(
    repository_with_customer,
    sample_customer,
):

    results = repository_with_customer.search(
        sample_customer.first_name[:3]
    )

    assert len(results) == 1


def test_search_returns_empty_list(
    repository,
):

    assert repository.search(
        "THIS-DOES-NOT-EXIST"
    ) == []

# Part 4 — Validation, Statistics & Customer Management

# ---------------------------------------------------------
# Statistics
# ---------------------------------------------------------

def test_customer_statistics_empty(
    repository,
):

    stats = repository.customer_statistics()

    assert stats["total_customers"] == 0
    assert stats["active_customers"] == 0
    assert stats["inactive_customers"] == 0


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


# ---------------------------------------------------------
# customer_exists()
# ---------------------------------------------------------

def test_customer_exists_true(
    repository_with_customer,
    sample_customer,
):

    assert repository_with_customer.customer_exists(
        sample_customer.customer_id
    )


def test_customer_exists_false(
    repository,
):

    assert not repository.customer_exists(
        "CUST999999"
    )


# ---------------------------------------------------------
# get_or_raise()
# ---------------------------------------------------------

def test_get_or_raise_returns_customer(
    repository_with_customer,
    sample_customer,
):

    customer = repository_with_customer.get_or_raise(
        sample_customer.customer_id
    )

    assert customer == sample_customer


def test_get_or_raise_not_found(
    repository,
):

    with pytest.raises(
        EntityNotFoundError,
    ):
        repository.get_or_raise(
            "CUST999999"
        )


# ---------------------------------------------------------
# validate_unique_customer()
# ---------------------------------------------------------

def test_validate_unique_customer_passes(
    repository,
    sample_customer,
):

    repository.validate_unique_customer(
        sample_customer
    )


def test_validate_unique_customer_duplicate_customer_number(
    repository_with_customer,
    sample_customer,
):

    with pytest.raises(
        EntityAlreadyExistsError,
    ):
        repository_with_customer.validate_unique_customer(
            sample_customer
        )


def test_validate_unique_customer_duplicate_national_id(
    repository_with_customer,
    sample_customer,
    sample_address,
):

    duplicate = Customer(
        customer_id="CUST999999",
        first_name="Jane",
        last_name="Smith",
        national_id=sample_customer.national_id,
        email="jane@example.com",
        phone_number="0509999999",
        address=sample_address,
    )

    with pytest.raises(
        EntityAlreadyExistsError,
    ):
        repository_with_customer.validate_unique_customer(
            duplicate
        )


def test_validate_unique_customer_duplicate_email(
    repository_with_customer,
    sample_customer,
    sample_address,
):

    duplicate = Customer(
        customer_id="CUST999998",
        first_name="Jane",
        last_name="Smith",
        national_id="9999999999",
        email=sample_customer.email,
        phone_number="0509999998",
        address=sample_address,
    )

    with pytest.raises(
        EntityAlreadyExistsError,
    ):
        repository_with_customer.validate_unique_customer(
            duplicate
        )


# ---------------------------------------------------------
# add_customer()
# ---------------------------------------------------------

def test_add_customer(
    repository,
    sample_customer,
):

    repository.add_customer(
        sample_customer
    )

    assert repository.count == 1

    assert repository.exists_customer_number(
        sample_customer.customer_id
    )


def test_add_customer_duplicate(
    repository_with_customer,
    sample_customer,
):

    with pytest.raises(
        EntityAlreadyExistsError,
    ):
        repository_with_customer.add_customer(
            sample_customer
        )


def test_add_customer_persists(
    repository,
    sample_customer,
):

    repository.add_customer(
        sample_customer
    )

    repository.reload()

    assert repository.count == 1

    assert repository.exists_customer_number(
        sample_customer.customer_id
    )

# Part 5 — Remaining Validation, String Representation & Edge Cases

# ---------------------------------------------------------
# Remaining Duplicate Validation
# ---------------------------------------------------------
"""
def test_validate_unique_customer_duplicate_passport_number(
    repository_with_customer,
    sample_customer,
    sample_address,
):

    duplicate = Customer(
        customer_id="CUST999997",
        first_name="John",
        last_name="Doe",
        national_id="9999999997",
        passport_number=sample_customer.passport_number,
        email="john997@example.com",
        phone_number="0509999997",
        address=sample_address,
    )

    with pytest.raises(
        EntityAlreadyExistsError,
    ):
        repository_with_customer.validate_unique_customer(
            duplicate
        )
"""

def test_validate_unique_customer_duplicate_mobile_number(
    repository_with_customer,
    sample_customer,
    sample_address,
):

    duplicate = Customer(
        customer_id="CUST999996",
        first_name="John",
        last_name="Doe",
        national_id="9999999996",
        email="john996@example.com",
        phone_number=sample_customer.phone_number,
        address=sample_address,
    )

    with pytest.raises(
        EntityAlreadyExistsError,
    ):
        repository_with_customer.validate_unique_customer(
            duplicate
        )


# ---------------------------------------------------------
# Repository Properties
# ---------------------------------------------------------

def test_repository_name(
    repository,
):

    assert (
        repository.repository_name
        == "CustomerRepository"
    )


def test_entity_type(
    repository,
):

    assert repository.entity_type is Customer


# ---------------------------------------------------------
# __str__
# ---------------------------------------------------------

def test_str(
    repository,
):

    text = str(repository)

    assert "CustomerRepository" in text

    assert "customers=" in text


# ---------------------------------------------------------
# __repr__
# ---------------------------------------------------------

def test_repr(
    repository,
):

    text = repr(repository)

    assert "CustomerRepository" in text

    assert "count=" in text

    assert "file=" in text


# ---------------------------------------------------------
# Search Edge Cases
# ---------------------------------------------------------

def test_search_empty_string(
    repository_with_customer,
):

    results = repository_with_customer.search(
        ""
    )

    assert len(results) == 1


def test_search_whitespace(
    repository_with_customer,
):

    results = repository_with_customer.search(
        "   "
    )

    assert len(results) == 1


def test_search_unknown_value(
    repository,
):

    results = repository.search(
        "NO_MATCH_FOUND"
    )

    assert results == []


# ---------------------------------------------------------
# Active / Inactive After State Change
# ---------------------------------------------------------

def test_active_customer_count_after_deactivate(
    repository_with_customer,
    sample_customer,
):

    sample_customer.deactivate()

    assert (
        repository_with_customer.active_customer_count()
        == 0
    )

    assert (
        repository_with_customer.inactive_customer_count()
        == 1
    )


def test_find_active_customers_after_deactivate(
    repository_with_customer,
    sample_customer,
):

    sample_customer.deactivate()

    assert (
        repository_with_customer.find_active_customers()
        == []
    )


def test_find_inactive_customers_after_deactivate(
    repository_with_customer,
    sample_customer,
):

    sample_customer.deactivate()

    customers = (
        repository_with_customer.find_inactive_customers()
    )

    assert len(customers) == 1

    assert customers[0] == sample_customer
    
