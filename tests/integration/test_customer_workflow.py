"""Integration tests for CustomerService and CustomerRepository."""

import pytest

from exceptions.banking_exceptions import (
    EntityAlreadyExistsError,
    EntityNotFoundError,
    ValidationError,
)
from tests.integration.conftest import make_customer


def register(customer_service, index=1, customer_id=None):
    return customer_service.register_customer(
        make_customer(customer_id or f"CUST{index:03}", index)
    )


def test_register_customer(customer_service):
    customer = register(customer_service)
    assert customer.customer_id == "CUST001"
    assert customer.first_name == "John"


def test_find_customer(customer_service):
    register(customer_service)
    customer = customer_service.find_customer("CUST001")
    assert customer is not None
    assert customer.customer_id == "CUST001"


def test_get_customer(customer_service):
    register(customer_service)
    assert customer_service.get_customer("CUST001").customer_id == "CUST001"


def test_update_customer(customer_service):
    customer = register(customer_service)
    customer.first_name = "Johnny"
    customer.email = "johnny@test.com"
    updated = customer_service.update_customer(customer)
    assert updated.first_name == "Johnny"
    assert customer_service.get_customer("CUST001").email == "johnny@test.com"


def test_duplicate_customer(customer_service):
    register(customer_service)
    duplicate = make_customer("CUST001", 2)
    with pytest.raises(EntityAlreadyExistsError):
        customer_service.register_customer(duplicate)


def test_invalid_customer(customer_service):
    customer = make_customer("CUST001", 1)
    with pytest.raises(ValidationError, match="First Name cannot be empty"):
        customer.first_name = ""


def test_customer_persistence(customer_service, reload_customer_repository):
    register(customer_service)
    repository = reload_customer_repository()
    customer = repository.find_by_customer_number("CUST001")
    assert customer is not None
    assert customer.first_name == "John"


def test_multiple_customers(customer_service):
    for i in range(1, 26):
        register(customer_service, i)
    assert customer_service.customer_count() == 25
    assert customer_service.active_customer_count() == 25


def test_customer_search_and_statistics(customer_service):
    register(customer_service, 1)
    customer = customer_service.find_by_email("integration-1@bank.com")
    assert customer is not None
    assert customer.customer_id == "CUST001"
    assert customer_service.statistics()["total_customers"] == 1


def test_customer_lifecycle(customer_service):
    register(customer_service)
    assert customer_service.get_customer("CUST001").is_active

    customer_service.deactivate_customer("CUST001")
    inactive_customer = customer_service.find_customer(
        "CUST001",
        active_only=False,
    )
    assert inactive_customer is not None
    assert not inactive_customer.is_active

    customer_service.activate_customer("CUST001")
    assert customer_service.get_customer("CUST001").is_active


def test_missing_customer(customer_service):
    with pytest.raises(EntityNotFoundError):
        customer_service.get_customer("UNKNOWN")
