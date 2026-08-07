"""
==============================================================
Tests for Person
==============================================================
"""

from datetime import UTC, date, datetime

import pytest

from models.person import Person
from models.value_objects.address import Address

from utils.constants import Gender


# ============================================================
# Concrete implementation for testing
# ============================================================

class ConcretePerson(Person):

    def get_identifier(self) -> str:
        return "PERSON001"

    def to_dict(self) -> dict:
        return {}

    @classmethod
    def from_dict(cls, data: dict):
        raise NotImplementedError


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
def person(address):

    return ConcretePerson(
        first_name="Adel",
        middle_name="",
        last_name="Alawiyat",
        date_of_birth=date(1990, 1, 1),
        gender=Gender.MALE,
        national_id="1234567890",
        email="adel@example.com",
        phone_number="+966500000000",
        address=address,
    )


# ============================================================
# Constructor
# ============================================================

def test_create_person(person):

    assert person.first_name == "Adel"
    assert person.last_name == "Alawiyat"
    assert person.email == "adel@example.com"
    assert person.phone_number == "+966500000000"

    assert person.address.city == "Riyadh"


def test_person_is_active(person):

    assert person.is_active is True


def test_person_initial_version(person):

    assert person.version == 1


def test_created_timestamp(person):

    assert isinstance(person.created_at, datetime)


def test_updated_timestamp(person):

    assert isinstance(person.updated_at, datetime)


# ============================================================
# Name properties
# ============================================================

def test_change_first_name(person):

    version = person.version

    person.first_name = "Ahmed"

    assert person.first_name == "Ahmed"
    assert person.version == version + 1


def test_change_middle_name(person):

    version = person.version

    person.middle_name = "Mohammed"

    assert person.middle_name == "Mohammed"
    assert person.version == version + 1


def test_change_last_name(person):

    version = person.version

    person.last_name = "Al-Qahtani"

    assert person.last_name == "Al-Qahtani"
    assert person.version == version + 1

# PART 2

# ============================================================
# Address
# ============================================================

def test_change_address(person):

    version = person.version

    new_address = Address(
        address_line_1="Olaya Street",
        address_line_2="Tower A",
        city="Riyadh",
        state_or_province="Riyadh",
        postal_code="12211",
        country="Saudi Arabia",
    )

    person.address = new_address

    assert person.address == new_address
    assert person.version == version + 1


# ============================================================
# Email
# ============================================================

def test_change_email(person):

    version = person.version

    person.email = "new@email.com"

    assert person.email == "new@email.com"
    assert person.version == version + 1


# ============================================================
# Phone
# ============================================================

def test_change_phone_number(person):

    version = person.version

    person.phone_number = "+966511111111"

    assert person.phone_number == "+966511111111"
    assert person.version == version + 1


# ============================================================
# National ID
# ============================================================

def test_change_national_id(person):

    version = person.version

    person.national_id = "9876543210"

    assert person.national_id == "9876543210"
    assert person.version == version + 1


# ============================================================
# Gender
# ============================================================

def test_change_gender(person):

    version = person.version

    person.gender = Gender.FEMALE

    assert person.gender == Gender.FEMALE
    assert person.version == version + 1


# ============================================================
# Date of Birth
# ============================================================

def test_change_date_of_birth(person):

    version = person.version

    new_date = date(1992, 5, 10)

    person.date_of_birth = new_date

    assert person.date_of_birth == new_date
    assert person.version == version + 1


# ============================================================
# Audit
# ============================================================

def test_property_update_changes_timestamp(person):

    timestamp = person.updated_at

    person.first_name = "Ahmed"

    assert person.updated_at >= timestamp


def test_multiple_updates_increment_version(person):

    version = person.version

    person.first_name = "Ahmed"
    person.last_name = "Saleh"
    person.email = "a@test.com"

    assert person.version == version + 3


# ============================================================
# Representation
# ============================================================

def test_repr_contains_name(person):

    text = repr(person)

    assert isinstance(text, str)

    assert "Adel" in text


def test_str_returns_string(person):

    assert isinstance(str(person), str)

# PART 3

# ============================================================
# Validation
# ============================================================

import pytest

from exceptions.banking_exceptions import ValidationError


def test_empty_first_name(person):

    with pytest.raises(ValidationError):
        person.first_name = ""


def test_empty_last_name(person):

    with pytest.raises(ValidationError):
        person.last_name = ""


def test_first_name_too_long(person):

    with pytest.raises(ValidationError):
        person.first_name = "A" * 51


def test_last_name_too_long(person):

    with pytest.raises(ValidationError):
        person.last_name = "A" * 51


def test_invalid_email(person):

    with pytest.raises(Exception):
        person.email = "not-an-email"


def test_invalid_phone(person):

    with pytest.raises(Exception):
        person.phone_number = "12345"


def test_future_birth_date(person):

    from datetime import timedelta

    future = date.today() + timedelta(days=1)

    with pytest.raises(ValidationError):
        person.date_of_birth = future


def test_none_address(person):

    with pytest.raises(Exception):
        person.address = None


def test_none_gender(person):

    with pytest.raises(Exception):
        person.gender = None


# ============================================================
# Normalization
# ============================================================

def test_first_name_is_normalized(person):

    person.first_name = "   adel   "

    assert person.first_name == "Adel"


def test_last_name_is_normalized(person):

    person.last_name = "   alawiyat   "

    assert person.last_name == "Alawiyat"


# ============================================================
# Computed properties (only if implemented)
# ============================================================

def test_full_name_property(person):

    if hasattr(person, "full_name"):

        assert person.full_name == "Adel Alawiyat"


def test_age_property(person):

    if hasattr(person, "age"):

        assert person.age >= 18


# ============================================================
# Equality
# ============================================================

def test_person_equals_self(person):

    assert person == person


def test_person_not_equal_different_instance(address):

    person1 = ConcretePerson(
        first_name="Adel",
        middle_name="",
        last_name="Alawiyat",
        date_of_birth=date(1990, 1, 1),
        gender=Gender.MALE,
        national_id="1234567890",
        email="adel@example.com",
        phone_number="+966500000000",
        address=address,
    )

    person2 = ConcretePerson(
        first_name="Ahmed",
        middle_name="",
        last_name="Saleh",
        date_of_birth=date(1992, 1, 1),
        gender=Gender.MALE,
        national_id="9876543210",
        email="ahmed@example.com",
        phone_number="+966511111111",
        address=address,
    )

    assert person1 != person2


# ============================================================
# Identifier
# ============================================================

def test_get_identifier(person):

    assert person.get_identifier() == "PERSON001"


# ============================================================
# Dictionary conversion
# ============================================================

def test_to_dict(person):

    data = person.to_dict()

    assert isinstance(data, dict)