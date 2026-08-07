"""
===============================================================================
Banking Management System (BMS)

File        : address.py
Description : Immutable Address Value Object.

Author      : Adel Alawiyat / ChatGPT
Version     : 2.1.0
Python      : 3.13+

Address is a Domain-Driven Design (DDD) Value Object.

Characteristics
---------------
• Immutable
• Hashable
• Comparable by value
• Serializable
• Reusable
• Memory optimized (slots=True)

Used by

    • Customer
    • Employee
    • Branch
    • Bank

===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from utils.validators import Validator


@dataclass(frozen=True, slots=True)
class Address:
    """
    Immutable postal address.

    Equality is value-based rather than identity-based.
    """

    address_line_1: str

    address_line_2: str = ""

    city: str = ""

    state_or_province: str = ""

    postal_code: str = ""

    country: str = ""

    def __post_init__(self) -> None:
        """
        Validate address fields after initialization.
        """

        Validator.required(
            self.address_line_1,
            "Address Line 1",
        )

        Validator.max_length(
            self.address_line_1,
            100,
            "Address Line 1",
        )

        if self.address_line_2:
            Validator.max_length(
                self.address_line_2,
                100,
                "Address Line 2",
            )

        Validator.max_length(
            self.city,
            100,
            "City",
        )

        Validator.max_length(
            self.state_or_province,
            100,
            "State / Province",
        )

        Validator.max_length(
            self.postal_code,
            20,
            "Postal Code",
        )

        Validator.max_length(
            self.country,
            100,
            "Country",
        )

    # ------------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        """
        Convert the address into a dictionary suitable for CSV persistence.
        """

        return {
            "address_line_1": self.address_line_1,
            "address_line_2": self.address_line_2,
            "city": self.city,
            "state_or_province": self.state_or_province,
            "postal_code": self.postal_code,
            "country": self.country,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Address":
        """
        Reconstruct an Address from persisted data.
        """

        return cls(
            address_line_1=data.get("address_line_1", ""),
            address_line_2=data.get("address_line_2", ""),
            city=data.get("city", ""),
            state_or_province=data.get("state_or_province", ""),
            postal_code=data.get("postal_code", ""),
            country=data.get("country", ""),
        )

    # ------------------------------------------------------------------
    # Formatting
    # ------------------------------------------------------------------

    def as_single_line(self) -> str:
        """
        Return the address formatted as a single line.
        """

        parts = [
            self.address_line_1,
            self.address_line_2,
            self.city,
            self.state_or_province,
            self.postal_code,
            self.country,
        ]

        return ", ".join(
            part for part in parts if part
        )

    def __str__(self) -> str:
        """
        Human-readable representation.
        """

        return self.as_single_line()
