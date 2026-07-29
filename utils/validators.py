"""
====================================================================
Banking Management System (BMS)

File        : validators.py
Description : Centralized validation utilities.

Author      : Adel Alawiyat / ChatGPT
Version     : 1.0.0
Python      : 3.13+
====================================================================
"""

from __future__ import annotations

import re
from datetime import date, datetime
from decimal import Decimal
from email.utils import parseaddr
from typing import Any

from exceptions.banking_exceptions import (
    InvalidAmountError,
    InvalidEmailError,
    InvalidNameError,
    InvalidNationalIDError,
    InvalidPhoneError,
    ValidationError,
)
from models.value_objects.money import Money


class Validator:
    """
    Centralized validation utilities.

    Every method raises a custom ValidationError on failure and returns
    True on success.
    """

    NAME_PATTERN = re.compile(r"^[A-Za-z\s\-']{2,100}$")

    EMAIL_PATTERN = re.compile(
        r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
    )

    PHONE_PATTERN = re.compile(r"^\+?[0-9]{8,15}$")

    ACCOUNT_PATTERN = re.compile(r"^[A-Z0-9]{8,30}$")

    SWIFT_PATTERN = re.compile(r"^[A-Z]{6}[A-Z0-9]{2}([A-Z0-9]{3})?$")

    IBAN_PATTERN = re.compile(r"^[A-Z]{2}[0-9A-Z]{13,32}$")

    # -------------------------------------------------------------
    # Generic
    # -------------------------------------------------------------

    @staticmethod
    def not_none(value: Any, field_name: str) -> bool:
        if value is None:
            raise ValidationError(f"{field_name} cannot be None.")
        return True

    @staticmethod
    def not_empty(value: str, field_name: str) -> bool:
        if not value or not value.strip():
            raise ValidationError(f"{field_name} cannot be empty.")
        return True

    # -------------------------------------------------------------
    # Name
    # -------------------------------------------------------------

    @classmethod
    def name(cls, value: str) -> bool:
        cls.not_empty(value, "Name")

        if not cls.NAME_PATTERN.fullmatch(value.strip()):
            raise InvalidNameError("Invalid name.")

        return True

    # -------------------------------------------------------------
    # Email
    # -------------------------------------------------------------

    @classmethod
    def email(cls, value: str) -> bool:
        cls.not_empty(value, "Email")

        _, parsed = parseaddr(value)

        if not parsed:
            raise InvalidEmailError("Invalid email address.")

        if not cls.EMAIL_PATTERN.fullmatch(parsed):
            raise InvalidEmailError("Invalid email format.")

        return True

    # -------------------------------------------------------------
    # Phone
    # -------------------------------------------------------------

    @classmethod
    def phone(cls, value: str) -> bool:
        cls.not_empty(value, "Phone")

        if not cls.PHONE_PATTERN.fullmatch(value):
            raise InvalidPhoneError("Invalid phone number.")

        return True

    # -------------------------------------------------------------
    # National ID
    # -------------------------------------------------------------

    @staticmethod
    def national_id(value: str) -> bool:
        if not value.isdigit():
            raise InvalidNationalIDError(
                "National ID must contain digits only."
            )

        if len(value) not in (10, 12):
            raise InvalidNationalIDError(
                "National ID length is invalid."
            )

        return True

    # -------------------------------------------------------------
    # Password
    # -------------------------------------------------------------

    @staticmethod
    def password(value: str) -> bool:

        if len(value) < 8:
            raise ValidationError(
                "Password must contain at least 8 characters."
            )

        if not re.search(r"[A-Z]", value):
            raise ValidationError(
                "Password must contain an uppercase letter."
            )

        if not re.search(r"[a-z]", value):
            raise ValidationError(
                "Password must contain a lowercase letter."
            )

        if not re.search(r"\d", value):
            raise ValidationError(
                "Password must contain a digit."
            )

        if not re.search(r"[!@#$%^&*()_\-+=]", value):
            raise ValidationError(
                "Password must contain a special character."
            )

        return True

    # -------------------------------------------------------------
    # Account Number
    # -------------------------------------------------------------

    @classmethod
    def account_number(cls, value: str) -> bool:

        if not cls.ACCOUNT_PATTERN.fullmatch(value):
            raise ValidationError(
                "Invalid account number."
            )

        return True

    # -------------------------------------------------------------
    # SWIFT
    # -------------------------------------------------------------

    @classmethod
    def swift(cls, value: str) -> bool:

        if not cls.SWIFT_PATTERN.fullmatch(value):
            raise ValidationError(
                "Invalid SWIFT code."
            )

        return True

    # -------------------------------------------------------------
    # IBAN
    # -------------------------------------------------------------

    @classmethod
    def iban(cls, value: str) -> bool:

        value = value.replace(" ", "").upper()

        if not cls.IBAN_PATTERN.fullmatch(value):
            raise ValidationError(
                "Invalid IBAN."
            )

        return True

    # -------------------------------------------------------------
    # Decimal
    # -------------------------------------------------------------

    @staticmethod
    def decimal(value: Decimal) -> bool:

        if value < Decimal("0"):
            raise InvalidAmountError(
                "Negative amount is not allowed."
            )

        return True

    # -------------------------------------------------------------
    # Money
    # -------------------------------------------------------------

    @staticmethod
    def money(value: Money) -> bool:

        if value.amount < Decimal("0"):
            raise InvalidAmountError(
                "Money amount cannot be negative."
            )

        return True

    @staticmethod
    def positive_money(value: Money) -> bool:

        Validator.money(value)

        if value.amount == Decimal("0"):
            raise InvalidAmountError(
                "Amount must be greater than zero."
            )

        return True

    # -------------------------------------------------------------
    # Date
    # -------------------------------------------------------------

    @staticmethod
    def date_not_future(value: date) -> bool:

        if value > date.today():
            raise ValidationError(
                "Date cannot be in the future."
            )

        return True

    @staticmethod
    def datetime_not_future(value: datetime) -> bool:

        if value > datetime.now():
            raise ValidationError(
                "Datetime cannot be in the future."
            )

        return True

    # -------------------------------------------------------------
    # Percentage
    # -------------------------------------------------------------

    @staticmethod
    def percentage(value: Decimal) -> bool:

        if value < Decimal("0"):
            raise ValidationError(
                "Percentage cannot be negative."
            )

        if value > Decimal("100"):
            raise ValidationError(
                "Percentage cannot exceed 100."
            )

        return True

    # -------------------------------------------------------------
    # Range
    # -------------------------------------------------------------

    @staticmethod
    def range(
        value: Decimal,
        minimum: Decimal,
        maximum: Decimal,
        field_name: str,
    ) -> bool:

        if value < minimum or value > maximum:

            raise ValidationError(
                f"{field_name} must be between "
                f"{minimum} and {maximum}."
            )

        return True
