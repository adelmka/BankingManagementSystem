"""
====================================================================
Banking Management System (BMS)

File        : conftest.py
Description : Shared pytest Fixtures

Provides reusable fixtures for the Banking Management System
test suite.

Responsibilities
----------------
• Create temporary storage
• Build isolated DependencyContainer instances
• Build isolated Application instances
• Create reusable domain objects
• Prevent tests from modifying production data

Author      : Adel Alawiyat / ChatGPT
Python      : 3.13+
====================================================================
"""
from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from decimal import Decimal

from datetime import date

import pytest

from application.application import Application
from application.bootstrap import Bootstrap
from application.dependency_container import DependencyContainer

from models.customer import Customer
from models.current_account import CurrentAccount
from models.savings_account import SavingsAccount
from models.time_deposit_account import TimeDepositAccount

from models.value_objects.address import Address

from utils.constants import (
    Gender,
    CustomerStatus,
)


# ================================================================
# Temporary Storage
# ================================================================

@pytest.fixture
def temporary_storage(tmp_path):
    """
    Returns an isolated temporary storage directory.
    """

    return tmp_path


# ================================================================
# Dependency Container
# ================================================================

@pytest.fixture
def container(
    temporary_storage,
) -> DependencyContainer:
    """
    Returns a fully initialized DependencyContainer
    configured to use temporary storage.
    """

    bootstrap = Bootstrap(
        storage_directory=temporary_storage,
    )

    application = bootstrap.initialize()

    return application.container


# ================================================================
# Application
# ================================================================

@pytest.fixture
def application(
    temporary_storage,
) -> Application:
    """
    Returns a fully initialized Application.
    """

    bootstrap = Bootstrap(
        storage_directory=temporary_storage,
    )

    return bootstrap.initialize()


# ================================================================
# Services
# ================================================================

@pytest.fixture
def bank_service(container):

    return container.bank_service


@pytest.fixture
def customer_service(container):

    return container.customer_service


@pytest.fixture
def account_service(container):

    return container.account_service


@pytest.fixture
def transaction_service(container):

    return container.transaction_service


# ================================================================
# Sample Address
# ================================================================

@pytest.fixture
def sample_address():

    return Address(
        address_line_1="123 Main Street",
        address_line_2="",
        city="Riyadh",
        state_or_province="Riyadh",
        postal_code="12345",
        country="Saudi Arabia",
    )


# ================================================================
# Sample Customer
# ================================================================

@pytest.fixture
def sample_customer(
    sample_address,
):

    return Customer(
        customer_id="C000001",
        first_name="John",
        last_name="Smith",
        date_of_birth=date(
            1990,
            1,
            15,
        ),
        gender=Gender.MALE,
        national_id="1234567890",
        email="john.smith@example.com",
        phone_number="+966500000001",
        address=sample_address,
        middle_name="",
        customer_status=CustomerStatus.ACTIVE,
        registration_date=date.today(),
        kyc_completed=True,
    )

# ================================================================
# Sample Savings Account
# ================================================================

@pytest.fixture
def savings_account():

    return SavingsAccount(
        account_number="SA100001",
        customer_id="C000001",
        opening_balance=Decimal("1000.00"),
    )


# ================================================================
# Sample Current Account
# ================================================================

@pytest.fixture
def current_account():

    return CurrentAccount(
        account_number="CA100001",
        customer_id="C000001",
        opening_balance=Decimal("2500.00"),
    )


# ================================================================
# Sample Time Deposit
# ================================================================

@pytest.fixture
def time_deposit_account():

    return TimeDepositAccount(
        account_number="TD100001",
        customer_id="C000001",
        opening_balance=Decimal("10000.00"),
    )


# ================================================================
# Seeded Application
# ================================================================

@pytest.fixture
def seeded_application(
    application,
    sample_customer,
):

    application.bank_service.create_customer(
        sample_customer
    )

    return application
