"""
====================================================================
Banking Management System (BMS)

File        : money.py
Description : Immutable Money Value Object

Author      : Adel Alawiyat / ChatGPT
Version     : 1.0.0
Python      : 3.13+

Implements:
    • Immutable Money object
    • Currency safety
    • Decimal precision
    • Arithmetic operators
    • Comparisons
    • Serialization
====================================================================
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_EVEN, InvalidOperation
from typing import Union

from utils.constants import Currency

Number = Union[str, int, float, Decimal]


@dataclass(frozen=True, slots=True)
class Money:
    """
    Immutable representation of a monetary amount.

    All arithmetic returns a NEW Money instance.

    Example
    -------
    >>> balance = Money("1250.75", Currency.SAR)
    >>> deposit = Money("200", Currency.SAR)
    >>> balance = balance + deposit
    """

    amount: Decimal
    currency: Currency = Currency.SAR

    PRECISION = Decimal("0.01")

    # ---------------------------------------------------------
    # Construction
    # ---------------------------------------------------------

    def __init__(
        self,
        amount: Number,
        currency: Currency | str = Currency.SAR,
    ):
        object.__setattr__(
            self,
            "amount",
            self._normalize(amount),
        )

        # Account models historically expose currency as an ISO string
        # (for example, "SAR"), while Money's domain contract requires the
        # Currency enum. Normalize at this value-object boundary so Money
        # remains internally type-safe regardless of the caller's input.
        object.__setattr__(
            self,
            "currency",
            self._normalize_currency(currency),
        )

    # ---------------------------------------------------------
    # Internal
    # ---------------------------------------------------------

    @staticmethod
    def _normalize_currency(currency: Currency | str) -> Currency:
        """Normalize a currency value to the Currency enum."""
        if isinstance(currency, Currency):
            return currency

        try:
            return Currency(str(currency).strip().upper())
        except (ValueError, TypeError) as exc:
            raise ValueError(
                f"Unsupported currency: {currency}"
            ) from exc

    @classmethod
    def _normalize(cls, value: Number) -> Decimal:
        """
        Convert to Decimal and round using bankers' rounding.
        """
        try:
            decimal_value = Decimal(str(value))
            return decimal_value.quantize(
                cls.PRECISION,
                rounding=ROUND_HALF_EVEN,
            )
        except InvalidOperation as ex:
            raise ValueError(
                f"Invalid monetary value: {value}"
            ) from ex

    def _assert_currency(self, other: "Money") -> None:
        """
        Ensure both Money objects use the same currency.
        """
        if self.currency != other.currency:
            raise ValueError(
                f"Currency mismatch "
                f"({self.currency} != {other.currency})"
            )

    # ---------------------------------------------------------
    # Arithmetic
    # ---------------------------------------------------------

    def __add__(self, other: "Money") -> "Money":
        self._assert_currency(other)
        return Money(
            self.amount + other.amount,
            self.currency,
        )

    def __sub__(self, other: "Money") -> "Money":
        self._assert_currency(other)
        return Money(
            self.amount - other.amount,
            self.currency,
        )

    def __mul__(self, value: Number) -> "Money":
        return Money(
            self.amount * Decimal(str(value)),
            self.currency,
        )

    def __truediv__(self, value: Number) -> "Money":
        return Money(
            self.amount / Decimal(str(value)),
            self.currency,
        )

    def __neg__(self) -> "Money":
        return Money(
            -self.amount,
            self.currency,
        )

    def __abs__(self) -> "Money":
        return Money(
            abs(self.amount),
            self.currency,
        )

    # ---------------------------------------------------------
    # Comparisons
    # ---------------------------------------------------------

    def __lt__(self, other: "Money") -> bool:
        self._assert_currency(other)
        return self.amount < other.amount

    def __le__(self, other: "Money") -> bool:
        self._assert_currency(other)
        return self.amount <= other.amount

    def __gt__(self, other: "Money") -> bool:
        self._assert_currency(other)
        return self.amount > other.amount

    def __ge__(self, other: "Money") -> bool:
        self._assert_currency(other)
        return self.amount >= other.amount

    # ---------------------------------------------------------
    # Truthiness
    # ---------------------------------------------------------

    def __bool__(self) -> bool:
        return not self.is_zero

    # ---------------------------------------------------------
    # Properties
    # ---------------------------------------------------------

    @property
    def is_zero(self) -> bool:
        return self.amount == Decimal("0.00")

    @property
    def is_positive(self) -> bool:
        return self.amount > Decimal("0.00")

    @property
    def is_negative(self) -> bool:
        return self.amount < Decimal("0.00")

    # ---------------------------------------------------------
    # Utility
    # ---------------------------------------------------------

    def percentage(self, percent: Number) -> "Money":
        """
        Calculate percentage.

        Example:
            interest = balance.percentage(2.5)
        """
        return Money(
            self.amount * Decimal(str(percent)) / Decimal("100"),
            self.currency,
        )

    def allocate(self, parts: int) -> list["Money"]:
        """
        Split money evenly.

        Any remainder is distributed starting
        from the first allocation.
        """
        if parts <= 0:
            raise ValueError("parts must be positive")

        cents = int(self.amount * 100)
        base = cents // parts
        remainder = cents % parts
        result = []

        for index in range(parts):
            share = base
            if index < remainder:
                share += 1
            result.append(
                Money(
                    Decimal(share) / Decimal("100"),
                    self.currency,
                )
            )

        return result

    # ---------------------------------------------------------
    # Serialization
    # ---------------------------------------------------------

    def to_dict(self) -> dict:
        return {
            "amount": str(self.amount),
            "currency": self.currency.value,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Money":
        return cls(
            data["amount"],
            Currency(data["currency"]),
        )

    # ---------------------------------------------------------
    # String
    # ---------------------------------------------------------

    def __str__(self):
        return f"{self.amount:,.2f} {self.currency.value}"

    def __repr__(self):
        return (
            f"Money("
            f"amount={self.amount}, "
            f"currency={self.currency.value})"
        )

    # ---------------------------------------------------------
    # Factory Methods
    # ---------------------------------------------------------

    @classmethod
    def zero(
        cls,
        currency: Currency = Currency.SAR,
    ) -> "Money":
        return cls("0.00", currency)

    @classmethod
    def one(
        cls,
        currency: Currency = Currency.SAR,
    ) -> "Money":
        return cls("1.00", currency)
