"""
============================================================
Integration Tests

Customer Workflow

These tests verify the interaction between

CustomerService
↓

CustomerRepository
↓

CSV Persistence

No mocks are used.
============================================================
"""

import pytest

from exceptions.banking_exceptions import (
    CustomerAlreadyExistsError,
    CustomerNotFoundError,
    ValidationError,
)

# ============================================================
# Customer Creation
# ============================================================

def test_create_customer(

    customer_service,

):

    customer = customer_service.create_customer(

        customer_id="CUST001",

        first_name="John",

        last_name="Smith",

        email="john@test.com",

        phone="+966501111111",

    )

    assert customer is not None

    assert customer.customer_id == "CUST001"

# ============================================================
# Find Customer
# ============================================================

def test_find_customer(

    customer_service,

):

    customer_service.create_customer(

        customer_id="CUST001",

        first_name="John",

        last_name="Smith",

        email="john@test.com",

        phone="+966501111111",

    )

    customer = customer_service.find_customer(

        "CUST001"

    )

    assert customer.customer_id == "CUST001"

# ============================================================
# Update Customer
# ============================================================

def test_update_customer(

    customer_service,

):

    customer_service.create_customer(

        customer_id="CUST001",

        first_name="John",

        last_name="Smith",

        email="john@test.com",

        phone="+966501111111",

    )

    customer_service.update_customer(

        customer_id="CUST001",

        first_name="Johnny",

        last_name="Smith",

        email="johnny@test.com",

        phone="+966501111111",

    )

    customer = customer_service.find_customer(

        "CUST001"

    )

    assert customer.first_name == "Johnny"

    assert customer.email == "johnny@test.com"

# ============================================================
# Delete Customer
# ============================================================

def test_delete_customer(

    customer_service,

):

    customer_service.create_customer(

        customer_id="CUST001",

        first_name="John",

        last_name="Smith",

        email="john@test.com",

        phone="+966501111111",

    )

    customer_service.delete_customer(

        "CUST001"

    )

    with pytest.raises(

        CustomerNotFoundError

    ):

        customer_service.find_customer(

            "CUST001"

        )

# ============================================================
# Duplicate Customer
# ============================================================

def test_duplicate_customer(

    customer_service,

):

    customer_service.create_customer(

        customer_id="CUST001",

        first_name="John",

        last_name="Smith",

        email="john@test.com",

        phone="+966501111111",

    )

    with pytest.raises(

        CustomerAlreadyExistsError

    ):

        customer_service.create_customer(

            customer_id="CUST001",

            first_name="John",

            last_name="Smith",

            email="john@test.com",

            phone="+966501111111",

        )

# ============================================================
# Validation
# ============================================================

def test_invalid_customer(

    customer_service,

):

    with pytest.raises(

        ValidationError

    ):

        customer_service.create_customer(

            customer_id="",

            first_name="",

            last_name="",

            email="bad",

            phone="",

        )

# ============================================================
# Persistence
# ============================================================

def test_customer_persistence(

    customer_service,

    reload_customer_repository,

):

    customer_service.create_customer(

        customer_id="CUST001",

        first_name="John",

        last_name="Smith",

        email="john@test.com",

        phone="+966501111111",

    )

    repository = reload_customer_repository()

    customer = repository.find_by_id(

        "CUST001"

    )

    assert customer.customer_id == "CUST001"

# ============================================================
# Multiple Customers
# ============================================================

def test_multiple_customers(

    customer_service,

):

    for i in range(25):

        customer_service.create_customer(

            customer_id=f"CUST{i:03}",

            first_name="John",

            last_name="Smith",

            email=f"user{i}@test.com",

            phone=f"+9665000{i:04}",

        )

    for i in range(25):

        customer = customer_service.find_customer(

            f"CUST{i:03}"

        )

        assert customer.customer_id == f"CUST{i:03}"

# ============================================================
# Repository Restart
# ============================================================

def test_repository_restart(

    customer_service,

    reload_customer_repository,

):

    customer_service.create_customer(

        customer_id="CUST001",

        first_name="John",

        last_name="Smith",

        email="john@test.com",

        phone="+966501111111",

    )

    repository = reload_customer_repository()

    customer = repository.find_by_id(

        "CUST001"

    )

    assert customer.customer_id == "CUST001"

# ============================================================
# Complete Lifecycle
# ============================================================

def test_customer_lifecycle(

    customer_service,

):

    customer_service.create_customer(

        customer_id="CUST001",

        first_name="John",

        last_name="Smith",

        email="john@test.com",

        phone="+966501111111",

    )

    customer_service.update_customer(

        customer_id="CUST001",

        first_name="Johnny",

        last_name="Smith",

        email="johnny@test.com",

        phone="+966501111111",

    )

    customer = customer_service.find_customer(

        "CUST001"

    )

    assert customer.first_name == "Johnny"

    customer_service.delete_customer(

        "CUST001"

    )

    with pytest.raises(

        CustomerNotFoundError

    ):

        customer_service.find_customer(

            "CUST001"

        )

