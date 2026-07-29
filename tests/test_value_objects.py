"""
====================================================================
Banking Management System (BMS)

File        : test_value_objects.py
Description : Unit Tests for Value Objects

Tests the immutable value objects used throughout the Banking
Management System.

Author      : Adel Alawiyat / ChatGPT
Python      : 3.13+
====================================================================
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from models.value_objects.address import Address
from models.value_objects.money import Money


# ================================================================
# Address Tests
# ================================================================

def test_create_address():
    """
    Verify that an Address can be created successfully.
    """

    address = Address(
        street="123 Main Street",
        city="Riyadh",
        state="Riyadh",
        postal_code="12345",
        country="Saudi Arabia",
    )

    assert address.street == "123 Main Street"
    assert address.city == "Riyadh"
    assert address.state == "Riyadh"
    assert address.postal_code == "12345"
    assert address.country == "Saudi Arabia"


def test_address_equality():
    """
    Verify that two identical addresses are equal.
    """

    address1 = Address(
        "123 Main Street",
        "Riyadh",
        "Riyadh",
        "12345",
        "Saudi Arabia",
    )

    address2 = Address(
        "123 Main Street",
        "Riyadh",
        "Riyadh",
        "12345",
        "Saudi Arabia",
    )

    assert address1 == address2


def test_address_inequality():
    """
    Verify that different addresses are not equal.
    """

    address1 = Address(
        "123 Main Street",
        "Riyadh",
        "Riyadh",
        "12345",
        "Saudi Arabia",
    )

    address2 = Address(
        "456 King Fahd Road",
        "Jeddah",
        "Makkah",
        "54321",
        "Saudi Arabia",
    )

    assert address1 != address2


# ================================================================
# Money Tests
# ================================================================

def test_create_money():
    """
    Verify Money creation.
    """

    money = Money(Decimal("100.50"))

    assert money.amount == Decimal("100.50")


def test_money_equality():
    """
    Verify Money equality.
    """

    assert (
        Money(Decimal("500.00"))
        ==
        Money(Decimal("500.00"))
    )


def test_money_inequality():
    """
    Verify Money inequality.
    """

    assert (
        Money(Decimal("500.00"))
        !=
        Money(Decimal("400.00"))
    )


def test_money_addition():
    """
    Verify Money addition.
    """

    result = (
        Money(Decimal("125.50"))
        +
        Money(Decimal("74.50"))
    )

    assert result.amount == Decimal("200.00")


def test_money_subtraction():
    """
    Verify Money subtraction.
    """

    result = (
        Money(Decimal("500.00"))
        -
        Money(Decimal("150.00"))
    )

    assert result.amount == Decimal("350.00")


def test_money_multiplication():
    """
    Verify Money multiplication.
    """

    result = (
        Money(Decimal("25.00"))
        * 4
    )

    assert result.amount == Decimal("100.00")


def test_money_division():
    """
    Verify Money division.
    """

    result = (
        Money(Decimal("100.00"))
        / 4
    )

    assert result.amount == Decimal("25.00")


def test_money_comparisons():
    """
    Verify comparison operators.
    """

    assert (
        Money(Decimal("100"))
        >
        Money(Decimal("50"))
    )

    assert (
        Money(Decimal("50"))
        <
        Money(Decimal("100"))
    )

    assert (
        Money(Decimal("100"))
        >=
        Money(Decimal("100"))
    )

    assert (
        Money(Decimal("100"))
        <=
        Money(Decimal("100"))
    )


def test_negative_money():
    """
    Verify negative values are supported
    when permitted by the implementation.
    """

    money = Money(Decimal("-50.00"))

    assert money.amount == Decimal("-50.00")


def test_money_repr():
    """
    Verify developer representation.
    """

    money = Money(Decimal("123.45"))

    assert "Money" in repr(money)


def test_money_str():
    """
    Verify string representation.
    """

    money = Money(Decimal("123.45"))

    assert str(money)


# ================================================================
# Immutability Tests
# ================================================================

def test_address_is_immutable():
    """
    Verify Address cannot be modified.
    """

    address = Address(
        "123 Main Street",
        "Riyadh",
        "Riyadh",
        "12345",
        "Saudi Arabia",
    )

    with pytest.raises(Exception):
        address.city = "Dammam"


def test_money_is_immutable():
    """
    Verify Money cannot be modified.
    """

    money = Money(Decimal("100"))

    with pytest.raises(Exception):
        money.amount = Decimal("200")