"""
===============================================================================
Banking Management System (BMS)

File        : person.py
Description : Abstract base class for all people in the banking system.

Author      : Adel Alawiyat / ChatGPT
Version     : 2.1.0
Python      : 3.13+

Description
-----------
Person is the abstract superclass for every individual represented in the
Banking Management System.

Derived Classes
---------------
    • Customer
    • Employee

OOP Concepts Demonstrated
-------------------------
✓ Abstraction
✓ Encapsulation
✓ Inheritance
✓ Polymorphism

===============================================================================
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date
from typing import Any

from models.base_entity import BaseEntity
from models.value_objects.address import Address
from utils.constants import Gender, LEGAL_ADULT_AGE
from utils.validators import Validator


class Person(BaseEntity, ABC):
    """
    Abstract representation of a person.

    This class contains only the information common to all people in
    the banking system.
    """

    # ------------------------------------------------------------------
    # Constructor
    # ------------------------------------------------------------------

    def __init__(
        self,
        first_name: str,
        last_name: str,
        date_of_birth: date,
        gender: Gender,
        national_id: str,
        email: str,
        phone_number: str,
        address: Address,
        middle_name: str = "",
    ) -> None:
        """
        Initialize a Person.
        """
        super().__init__()

        self._initializing = True

        try:

            self._first_name = ""
            self._middle_name = ""
            self._last_name = ""
            self._date_of_birth = date.today()
            self._gender = gender
            self._national_id = ""
            self._email = ""
            self._phone_number = ""
            self._address = address

            self.first_name = first_name
            self.middle_name = middle_name
            self.last_name = last_name
            self.date_of_birth = date_of_birth
            self.gender = gender
            self.national_id = national_id
            self.email = email
            self.phone_number = phone_number
            self.address = address

        finally:

            self._initializing = False

    # ------------------------------------------------------------------
    # Name Properties
    # ------------------------------------------------------------------

    @property
    def first_name(self) -> str:
        """Return the person's first name."""
        return self._first_name

    @first_name.setter
    def first_name(self, value: str) -> None:
        Validator.required(value, "First Name")
        Validator.max_length(value, 50, "First Name")

        self._first_name = value.strip().title()
        self.touch()

    @property
    def middle_name(self) -> str:
        """Return the person's middle name."""
        return self._middle_name

    @middle_name.setter
    def middle_name(self, value: str) -> None:
        Validator.max_length(value, 50, "Middle Name")

        self._middle_name = value.strip().title()
        self.touch()

    @property
    def last_name(self) -> str:
        """Return the person's last name."""
        return self._last_name

    @last_name.setter
    def last_name(self, value: str) -> None:
        Validator.required(value, "Last Name")
        Validator.max_length(value, 50, "Last Name")

        self._last_name = value.strip().title()
        self.touch()

    @property
    def full_name(self) -> str:
        """
        Return the person's formatted full name.
        """

        names = [
            self.first_name,
            self.middle_name,
            self.last_name,
        ]

        return " ".join(name for name in names if name)

    # ------------------------------------------------------------------
    # Date of Birth
    # ------------------------------------------------------------------

    @property
    def date_of_birth(self) -> date:
        return self._date_of_birth

    @date_of_birth.setter
    def date_of_birth(self, value: date) -> None:
        Validator.date_not_future(value, "Date of Birth")

        self._date_of_birth = value
        self.touch()

    # ------------------------------------------------------------------
    # Gender
    # ------------------------------------------------------------------

    @property
    def gender(self) -> Gender:
        """
        Return the person's gender.
        """
        return self._gender

    @gender.setter
    def gender(self, value: Gender) -> None:
        """
        Set the person's gender.
        """

        if not isinstance(value, Gender):
            raise TypeError(
                "gender must be an instance of Gender."
            )

        self._gender = value
        self.touch()

    # ------------------------------------------------------------------
    # National ID
    # ------------------------------------------------------------------

    @property
    def national_id(self) -> str:
        """
        Return the national identifier.
        """
        return self._national_id

    @national_id.setter
    def national_id(self, value: str) -> None:
        """
        Set the national identifier.
        """

        Validator.required(
            value,
            "National ID"
        )

        Validator.national_id(value)

        self._national_id = value.strip()

        self.touch()

    # ------------------------------------------------------------------
    # Email
    # ------------------------------------------------------------------

    @property
    def email(self) -> str:
        """
        Return the email address.
        """
        return self._email

    @email.setter
    def email(self, value: str) -> None:
        """
        Set the email address.
        """

        Validator.required(
            value,
            "Email"
        )

        Validator.email(value)

        self._email = value.strip().lower()

        self.touch()

    # ------------------------------------------------------------------
    # Phone Number
    # ------------------------------------------------------------------

    @property
    def phone_number(self) -> str:
        """
        Return the phone number.
        """
        return self._phone_number

    @phone_number.setter
    def phone_number(self, value: str) -> None:
        """
        Set the phone number.
        """

        Validator.required(
            value,
            "Phone Number"
        )

        Validator.phone_number(value)

        self._phone_number = value.strip()

        self.touch()

    # ------------------------------------------------------------------
    # Address
    # ------------------------------------------------------------------

    @property
    def address(self) -> Address:
        """
        Return the postal address.
        """
        return self._address

    @address.setter
    def address(self, value: Address) -> None:
        """
        Set the postal address.
        """

        if not isinstance(value, Address):
            raise TypeError(
                "address must be an Address object."
            )

        self._address = value

        self.touch()

    # ------------------------------------------------------------------
    # Calculated Properties
    # ------------------------------------------------------------------

    @property
    def age(self) -> int:
        """
        Calculate the person's age in years.
        """

        today = date.today()

        years = today.year - self.date_of_birth.year

        if (
            (today.month, today.day)
            <
            (
                self.date_of_birth.month,
                self.date_of_birth.day,
            )
        ):
            years -= 1

        return years

    @property
    def is_adult(self) -> bool:
        """
        Determine whether the person is legally an adult.
        """

        return self.age >= LEGAL_ADULT_AGE

    # ------------------------------------------------------------------
    # Display Helpers
    # ------------------------------------------------------------------

    def display_name(self) -> str:
        """
        Return the preferred display name.

        Subclasses may override this method.
        """

        return self.full_name

    def initials(self) -> str:
        """
        Return the person's initials.

        Example
        -------
        John Adam Smith -> JAS
        """

        letters: list[str] = []

        if self.first_name:
            letters.append(self.first_name[0])

        if self.middle_name:
            letters.append(self.middle_name[0])

        if self.last_name:
            letters.append(self.last_name[0])

        return "".join(letters).upper()

    # ------------------------------------------------------------------
    # Serialization Helpers
    # ------------------------------------------------------------------

    def _base_dict(self) -> dict[str, Any]:
        """
        Return a dictionary containing the common Person attributes.

        This method is intended to be used by subclasses when implementing
        to_dict().
        """

        return {
            # ---------- BaseEntity ----------
            "entity_id": str(self.entity_id),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "is_active": self.is_active,
            "version": self.version,

            # ---------- Person ----------
            "first_name": self.first_name,
            "middle_name": self.middle_name,
            "last_name": self.last_name,
            "date_of_birth": self.date_of_birth.isoformat(),
            "gender": self.gender.value,
            "national_id": self.national_id,
            "email": self.email,
            "phone_number": self.phone_number,

            # ---------- Address ----------
            **self.address.to_dict(),
        }

    # ------------------------------------------------------------------
    # Business Helpers
    # ------------------------------------------------------------------

    def update_contact_information(
        self,
        email: str,
        phone_number: str,
        address: Address,
    ) -> None:
        """
        Update all contact information.

        Validation is automatically performed by the property setters.
        """

        self.email = email
        self.phone_number = phone_number
        self.address = address

    # ------------------------------------------------------------------

    def update_name(
        self,
        first_name: str,
        last_name: str,
        middle_name: str = "",
    ) -> None:
        """
        Update the person's name.
        """

        self.first_name = first_name
        self.middle_name = middle_name
        self.last_name = last_name

    # ------------------------------------------------------------------

    def update_personal_information(
        self,
        first_name: str,
        last_name: str,
        middle_name: str,
        email: str,
        phone_number: str,
        address: Address,
    ) -> None:
        """
        Update the editable personal information.
        """

        self.update_name(
            first_name=first_name,
            last_name=last_name,
            middle_name=middle_name,
        )

        self.update_contact_information(
            email=email,
            phone_number=phone_number,
            address=address,
        )

    # ------------------------------------------------------------------
    # String Representation
    # ------------------------------------------------------------------

    def __str__(self) -> str:
        """
        Human-readable representation.
        """

        return self.full_name

    def __repr__(self) -> str:
        """
        Developer-friendly representation.
        """

        return (
            f"{self.__class__.__name__}("
            f"name='{self.full_name}', "
            f"email='{self.email}')"
        )

    # ------------------------------------------------------------------
    # Abstract Interface
    # ------------------------------------------------------------------

    @abstractmethod
    def get_identifier(self) -> str:
        """
        Return the business identifier.

        Examples
        --------
        Customer -> customer_id

        Employee -> employee_id
        """
        raise NotImplementedError

    @abstractmethod
    def to_dict(self) -> dict[str, Any]:
        """
        Convert the entity into a dictionary suitable for persistence.
        """
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def from_dict(
        cls,
        data: dict[str, Any],
    ) -> "Person":
        """
        Reconstruct the entity from persisted data.
        """
        raise NotImplementedError

    # ------------------------------------------------------------------
    # Comparison Helpers
    # ------------------------------------------------------------------

    def has_same_email(self, other: "Person") -> bool:
        """
        Determine whether another person has the same email address.

        Parameters
        ----------
        other : Person
            The person to compare against.

        Returns
        -------
        bool
            True if both email addresses are identical.
        """

        if not isinstance(other, Person):
            return False

        return self.email.lower() == other.email.lower()

    # ------------------------------------------------------------------

    def has_same_national_id(self, other: "Person") -> bool:
        """
        Determine whether another person has the same national ID.

        Parameters
        ----------
        other : Person
            The person to compare against.

        Returns
        -------
        bool
            True if both national IDs are identical.
        """

        if not isinstance(other, Person):
            return False

        return self.national_id == other.national_id

    # ------------------------------------------------------------------

    def has_same_phone_number(self, other: "Person") -> bool:
        """
        Determine whether another person has the same phone number.

        Parameters
        ----------
        other : Person
            The person to compare against.

        Returns
        -------
        bool
            True if both phone numbers are identical.
        """

        if not isinstance(other, Person):
            return False

        return self.phone_number == other.phone_number

    # ------------------------------------------------------------------
    # Convenience Methods
    # ------------------------------------------------------------------

    def as_display_dict(self) -> dict[str, str]:
        """
        Return a lightweight dictionary suitable for UI display.
        """

        return {
            "identifier": self.get_identifier(),
            "name": self.full_name,
            "email": self.email,
            "phone_number": self.phone_number,
            "city": self.address.city,
            "country": self.address.country,
            "active": "Yes" if self.is_active else "No",
        }

    # ------------------------------------------------------------------

    def __format__(self, format_spec: str) -> str:
        """
        Support custom formatting.

        Format Specifiers
        -----------------
        n : Full name
        e : Email
        i : Business identifier

        Examples
        --------
        format(customer, "n")
        format(customer, "e")
        format(customer, "i")
        """

        match format_spec.lower():

            case "n":
                return self.full_name

            case "e":
                return self.email

            case "i":
                return self.get_identifier()

            case "":
                return str(self)

            case _:
                return str(self)
