"""
Unit tests for Customer.

Covers:
- Construction
- Property initialization
- Defaults
- Validation
- Audit/version behavior
"""

from __future__ import annotations

from datetime import date

import pytest

from exceptions.banking_exceptions import (
    ValidationError,
)

from models.customer import Customer
from models.value_objects.address import Address

from utils.constants import (
    CustomerStatus,
    Gender,
)


# ============================================================
# Fixtures
# ============================================================

@pytest.fixture
def address():
    return Address(
        address_line_1="King Fahd Road",
        address_line_2="Building 1",
        city="Riyadh",
        state_or_province="Riyadh",
        postal_code="11564",
        country="Saudi Arabia",
    )


@pytest.fixture
def customer(address):

    return Customer(
        customer_id="CUST000001",
        first_name="Adel",
        last_name="Alawiyat",
        middle_name="Mohammed",
        date_of_birth=date(1990, 1, 1),
        gender=Gender.MALE,
        national_id="1234567890",
        email="adel@example.com",
        phone_number="+966500000000",
        address=address,
        customer_status=CustomerStatus.ACTIVE,
        registration_date=date.today(),
        kyc_completed=True,
    )


# ============================================================
# Constructor
# ============================================================

def test_create_customer(customer):

    assert customer.customer_id == "CUST000001"

    assert customer.first_name == "Adel"

    assert customer.last_name == "Alawiyat"

    assert customer.email == "adel@example.com"

    assert customer.phone_number == "+966500000000"

    assert customer.address.city == "Riyadh"

    assert customer.customer_status == CustomerStatus.ACTIVE

    assert customer.kyc_completed is True


def test_default_registration_date(address):

    customer = Customer(
        customer_id="CUST000002",
        first_name="Sara",
        last_name="Ahmed",
        date_of_birth=date(1995, 5, 10),
        gender=Gender.FEMALE,
        national_id="2234567890",
        email="sara@example.com",
        phone_number="+966511111111",
        address=address,
    )

    assert customer.registration_date == date.today()


def test_default_customer_status(address):

    customer = Customer(
        customer_id="CUST000003",
        first_name="Ali",
        last_name="Saleh",
        date_of_birth=date(1992, 8, 15),
        gender=Gender.MALE,
        national_id="3234567890",
        email="ali@example.com",
        phone_number="+966522222222",
        address=address,
    )

    assert customer.customer_status == CustomerStatus.ACTIVE


def test_default_kyc(address):

    customer = Customer(
        customer_id="CUST000004",
        first_name="Mona",
        last_name="Khalid",
        date_of_birth=date(1991, 7, 7),
        gender=Gender.FEMALE,
        national_id="4234567890",
        email="mona@example.com",
        phone_number="+966533333333",
        address=address,
    )

    assert customer.kyc_completed is False

# PART 2

# ============================================================
# Customer ID
# ============================================================

def test_customer_id(customer):

    assert customer.customer_id == "CUST000001"


def test_get_identifier(customer):

    assert customer.get_identifier() == "CUST000001"


# ============================================================
# Customer Status
# ============================================================

def test_customer_status(customer):

    assert customer.customer_status == CustomerStatus.ACTIVE


def test_change_customer_status(customer):

    version = customer.version

    customer.customer_status = CustomerStatus.BLACKLISTED

    assert customer.customer_status == CustomerStatus.BLACKLISTED

    assert customer.version == version + 1


def test_reactivate_customer(customer):

    customer.customer_status = CustomerStatus.INACTIVE

    customer.customer_status = CustomerStatus.ACTIVE

    assert customer.customer_status == CustomerStatus.ACTIVE


# ============================================================
# Registration Date
# ============================================================

def test_registration_date(customer):

    assert customer.registration_date == date.today()


def test_change_registration_date(customer):

    version = customer.version

    new_date = date(2024, 1, 1)

    customer.registration_date = new_date

    assert customer.registration_date == new_date

    assert customer.version == version + 1


# ============================================================
# KYC
# ============================================================

def test_kyc_completed(customer):

    assert customer.kyc_completed is True


def test_change_kyc_completed(customer):

    version = customer.version

    customer.kyc_completed = False

    assert customer.kyc_completed is False

    assert customer.version == version + 1


def test_enable_kyc(customer):

    customer.kyc_completed = False

    customer.kyc_completed = True

    assert customer.kyc_completed is True


# ============================================================
# Active State
# ============================================================

def test_deactivate_customer(customer):

    customer.deactivate()

    assert customer.is_active is False


def test_activate_customer(customer):

    customer.deactivate()

    customer.activate()

    assert customer.is_active is True


# ============================================================
# Versioning
# ============================================================

def test_customer_version_changes(customer):

    version = customer.version

    customer.customer_status = CustomerStatus.BLACKLISTED

    assert customer.version == version + 1


def test_multiple_updates_increment_version(customer):

    version = customer.version

    customer.customer_status = CustomerStatus.BLACKLISTED

    customer.kyc_completed = False

    customer.customer_status = CustomerStatus.ACTIVE

    assert customer.version == version + 3

# PART 3

# ============================================================
# Dictionary Serialization
# ============================================================

def test_to_dict(customer):

    data = customer.to_dict()

    assert isinstance(data, dict)

    assert data["customer_id"] == "CUST000001"

    assert data["first_name"] == "Adel"

    assert data["last_name"] == "Alawiyat"

    assert data["email"] == "adel@example.com"

    assert data["phone_number"] == "+966500000000"

    assert data["customer_status"] == CustomerStatus.ACTIVE.value

    assert data["kyc_completed"] is True


def test_from_dict(customer):

    data = customer.to_dict()

    restored = Customer.from_dict(data)

    assert restored.customer_id == customer.customer_id

    assert restored.first_name == customer.first_name

    assert restored.last_name == customer.last_name

    assert restored.email == customer.email

    assert restored.phone_number == customer.phone_number

    assert restored.customer_status == customer.customer_status

    assert restored.kyc_completed == customer.kyc_completed


def test_customer_identifier_uniqueness(customer, address):

    another = Customer(
        customer_id="CUST999999",
        first_name="Adel",
        last_name="Alawiyat",
        middle_name="Mohammed",
        date_of_birth=date(1990, 1, 1),
        gender=Gender.MALE,
        national_id="9999999999",
        email="another@example.com",
        phone_number="+966500000001",
        address=address,
    )

    assert customer.customer_id != another.customer_id


# ============================================================
# String Representation
# ============================================================

def test_repr(customer):

    text = repr(customer)

    assert "Customer" in text

    assert customer.customer_id in text


def test_str(customer):

    text = str(customer)

    assert customer.customer_id in text


# ============================================================
# Validation
# ============================================================

def test_invalid_customer_id(address):

    with pytest.raises(ValidationError):

        Customer(
            customer_id="",
            first_name="Adel",
            last_name="Alawiyat",
            date_of_birth=date(1990, 1, 1),
            gender=Gender.MALE,
            national_id="1234567890",
            email="adel@example.com",
            phone_number="+966500000000",
            address=address,
        )


def test_invalid_registration_date(address):

    with pytest.raises(ValidationError):

        Customer(
            customer_id="CUST000020",
            first_name="Adel",
            last_name="Alawiyat",
            date_of_birth=date(1990, 1, 1),
            gender=Gender.MALE,
            national_id="1234567890",
            email="adel@example.com",
            phone_number="+966500000000",
            address=address,
            registration_date=date(2100, 1, 1),
        )


def test_customer_id_cannot_be_empty(customer):

    with pytest.raises(ValidationError):

        customer.customer_id = ""


def test_registration_date_cannot_be_future(customer):

    with pytest.raises(ValidationError):

        customer.registration_date = date(2100, 1, 1)


# ============================================================
# Audit
# ============================================================

def test_touch_updates_timestamp(customer):

    old = customer.updated_at

    customer.touch()

    assert customer.updated_at >= old


def test_touch_updates_version(customer):

    version = customer.version

    customer.touch()

    assert customer.version == version + 1


# ============================================================
# Persistence Consistency
# ============================================================

def test_to_dict_contains_required_keys(customer):

    data = customer.to_dict()

    expected = {
        "customer_id",
        "first_name",
        "middle_name",
        "last_name",
        "date_of_birth",
        "gender",
        "national_id",
        "email",
        "phone_number",

        "address_line_1",
        "address_line_2",
        "city",
        "state_or_province",
        "postal_code",
        "country",

        "customer_status",
        "registration_date",
        "kyc_completed",
        "accounts",
    }
    assert expected.issubset(data.keys())
