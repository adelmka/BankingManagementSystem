"""
====================================================================
Banking Management System (BMS)

File        : test_base_entity.py
Description : Unit tests for BaseEntity

Author      : Adel Alawiyat / ChatGPT
Version     : 2.0.0
Python      : 3.13+
====================================================================
"""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

import pytest

from models.base_entity import BaseEntity


# ====================================================================
# Test Helper
# ====================================================================

class DummyEntity(BaseEntity):
    """
    Minimal concrete implementation used for testing BaseEntity.
    """

    def __init__(self):
        super().__init__()

    def get_identifier(self) -> str:
        return "DUMMY001"

    def to_dict(self) -> dict:
        return {
            "identifier": self.get_identifier(),
            "entity_id": str(self.entity_id),
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls()


# ====================================================================
# Fixtures
# ====================================================================

@pytest.fixture
def entity() -> DummyEntity:
    """
    Return a fresh entity for each test.
    """
    return DummyEntity()


# ====================================================================
# Constructor
# ====================================================================

def test_entity_initialization(entity):
    """
    Verify a newly created entity has the expected defaults.
    """

    assert entity.is_active is True
    assert entity.version == 1


def test_entity_has_uuid(entity):
    """
    Entity must have a UUID identifier.
    """

    assert isinstance(entity.entity_id, UUID)


def test_entity_has_creation_timestamp(entity):
    """
    Entity should have a creation timestamp.
    """

    assert isinstance(entity.created_at, datetime)


def test_entity_has_updated_timestamp(entity):
    """
    Entity should have an updated timestamp.
    """

    assert isinstance(entity.updated_at, datetime)


def test_created_and_updated_match_initially(entity):
    """
    Initially both timestamps should be identical.
    """

    assert entity.created_at == entity.updated_at


# ====================================================================
# UUID
# ====================================================================

def test_entity_ids_are_unique():
    """
    Every entity receives a unique identifier.
    """

    first = DummyEntity()
    second = DummyEntity()

    assert first.entity_id != second.entity_id


def test_entity_id_is_immutable_type(entity):
    """
    Identifier should remain UUID type.
    """

    assert type(entity.entity_id) is UUID


# ====================================================================
# Timestamp
# ====================================================================

def test_created_timestamp_is_timezone_aware(entity):
    """
    created_at must use UTC.
    """

    assert entity.created_at.tzinfo == UTC


def test_updated_timestamp_is_timezone_aware(entity):
    """
    updated_at must use UTC.
    """

    assert entity.updated_at.tzinfo == UTC


def test_updated_not_before_created(entity):
    """
    updated_at should never precede created_at.
    """

    assert entity.updated_at >= entity.created_at


# ====================================================================
# Initial State
# ====================================================================

def test_entity_is_active_by_default(entity):
    """
    Entities are active after construction.
    """

    assert entity.is_active


def test_initial_version_is_one(entity):
    """
    Version numbering starts at one.
    """

    assert entity.version == 1


def test_initializing_flag_is_false(entity):
    """
    Initialization flag should be cleared once construction completes.
    """

    assert entity.initializing is False


# ====================================================================
# Activation
# ====================================================================

def test_deactivate_sets_entity_inactive(entity):
    """
    Verify deactivate() marks the entity inactive.
    """

    entity.deactivate()

    assert entity.is_active is False


def test_activate_sets_entity_active(entity):
    """
    Verify activate() marks the entity active.
    """

    entity.deactivate()

    entity.activate()

    assert entity.is_active is True


def test_activate_increments_version(entity):
    """
    activate() should update audit information.
    """

    version = entity.version

    entity.activate()

    assert entity.version == version + 1

# PART 2

# ============================================================
# Version handling
# ============================================================

def test_touch_increments_version(entity):

    version = entity.version

    entity.touch()

    assert entity.version == version + 1


def test_multiple_touch_calls(entity):

    version = entity.version

    entity.touch()
    entity.touch()
    entity.touch()

    assert entity.version == version + 3


# ============================================================
# Active / inactive state
# ============================================================

def test_deactivate_entity(entity):

    entity.deactivate()

    assert entity.is_active is False


def test_activate_entity(entity):

    entity.deactivate()
    entity.activate()

    assert entity.is_active is True


def test_deactivate_increments_version(entity):

    version = entity.version

    entity.deactivate()

    assert entity.version == version + 1


def test_activate_increments_version(entity):

    entity.deactivate()

    version = entity.version

    entity.activate()

    assert entity.version == version + 1


# ============================================================
# Equality
# ============================================================

def test_entity_equals_itself(entity):

    assert entity == entity


def test_entities_are_not_equal():

    entity1 = DummyEntity()
    entity2 = DummyEntity()

    assert entity1 != entity2


def test_entity_hash():

    entity = DummyEntity()

    assert hash(entity) == hash(entity.entity_id)


# ============================================================
# String representation
# ============================================================

def test_repr_contains_class_name(entity):

    representation = repr(entity)

    assert "DummyEntity" in representation


def test_str_returns_identifier(entity):

    text = str(entity)

    assert isinstance(text, str)

    assert len(text) > 0


# ============================================================
# Identifier
# ============================================================

def test_get_identifier(entity):

    assert entity.get_identifier() == "DUMMY001"


# ============================================================
# Dictionary conversion
# ============================================================

def test_to_dict(entity):

    data = entity.to_dict()

    assert isinstance(data, dict)

    assert data["identifier"] == entity.get_identifier()


def test_from_dict():

    entity = DummyEntity.from_dict({})

    assert isinstance(entity, DummyEntity)
