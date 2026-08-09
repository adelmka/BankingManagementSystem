"""Tests for business identifier generators."""

import re

from utils.generators import IDGenerator


def test_customer_id_respects_domain_maximum_length():
    customer_id = IDGenerator.customer_id()

    assert customer_id.startswith("C")
    assert len(customer_id) <= 20
    assert re.fullmatch(r"C\d{17}", customer_id)


def test_customer_id_is_unique_across_sequential_calls():
    first = IDGenerator.customer_id()
    second = IDGenerator.customer_id()

    assert first != second
