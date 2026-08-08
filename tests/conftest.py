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

@pytest.fixture
def test_config(temporary_storage):
    """
    Configuration isolated to pytest's temporary storage.
    """

    class TestConfig:
        APP_NAME = "Banking Management System"
        APP_VERSION = "1.0.0"

        TESTING = True
        DEBUG = True

        BASE_DIR = temporary_storage
        DATA_DIR = temporary_storage / "data"
        LOG_DIR = temporary_storage / "logs"
        STATIC_DIR = temporary_storage / "static"
        TEMPLATE_DIR = temporary_storage / "templates"
        DOCUMENTATION_DIR = temporary_storage / "documentation"
        TEST_DIR = temporary_storage / "tests"
        BACKUP_DIR = temporary_storage / "backup"

        CUSTOMERS_FILE = DATA_DIR / "customers.csv"
        ACCOUNTS_FILE = DATA_DIR / "accounts.csv"
        TRANSACTIONS_FILE = DATA_DIR / "transactions.csv"
        USERS_FILE = DATA_DIR / "users.csv"
        EMPLOYEES_FILE = DATA_DIR / "employees.csv"
        FEES_FILE = DATA_DIR / "fees.csv"
        INTEREST_FILE = DATA_DIR / "interest_rates.csv"
        SETTINGS_FILE = DATA_DIR / "settings.csv"
        AUDIT_FILE = DATA_DIR / "audit_log.csv"
        BANKS_FILE = DATA_DIR / "banks.csv"

        APPLICATION_LOG = LOG_DIR / "application.log"
        ERROR_LOG = LOG_DIR / "error.log"
        AUDIT_LOG = LOG_DIR / "audit.log"

        DEFAULT_CURRENCY = "SAR"

        @classmethod
        def create_directories(cls):
            directories = [
                cls.DATA_DIR,
                cls.LOG_DIR,
                cls.STATIC_DIR,
                cls.TEMPLATE_DIR,
                cls.DOCUMENTATION_DIR,
                cls.TEST_DIR,
                cls.BACKUP_DIR,
            ]

            for directory in directories:
                directory.mkdir(
                    parents=True,
                    exist_ok=True,
                )

    return TestConfig


# Replace the existing `application` and `container` fixtures in tests/conftest.py
# with these versions. No production-code change is required.

@pytest.fixture
def application(test_config) -> Application:
    """Return a fully initialized Application using the test configuration."""
    bootstrap = Bootstrap(config=test_config)
    return bootstrap.initialize()


@pytest.fixture
def container(application) -> DependencyContainer:
    """Return the internally owned dependency container for tests that need it."""
    return application._container

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
