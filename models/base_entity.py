"""
===============================================================================
Banking Management System (BMS)

File        : base_entity.py
Description : Base abstract entity for all domain entities.

Author      : Adel Alawiyat / ChatGPT
Version     : 2.1.0
Python      : 3.13+

Every domain entity inherits from BaseEntity.

Responsibilities
----------------
• Internal unique identifier
• Audit information
• Entity versioning
• Active/inactive status
• Serialization contract
• Equality
• Hashing

This class intentionally does NOT use @dataclass because domain entities
contain behavior, validation, encapsulation and mutable state.

===============================================================================
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from utils.generators import Generator


class BaseEntity(ABC):
    """
    Abstract base class for every domain entity.
    """

    # ------------------------------------------------------------------
    # Constructor
    # ------------------------------------------------------------------

    def __init__(self) -> None:
        """
        Initialize a new entity.
        """

        self._entity_id: UUID = Generator.uuid()

        self._created_at: datetime = datetime.now()

        self._updated_at: datetime = self._created_at

        self._is_active: bool = True

        self._version: int = 1


    # ------------------------------------------------------------------
    # Internal State
    # ------------------------------------------------------------------

        self._initializing: bool = False

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def entity_id(self) -> UUID:
        """
        Internal immutable entity identifier.
        """
        return self._entity_id

    @property
    def created_at(self) -> datetime:
        """
        Entity creation timestamp.
        """
        return self._created_at

    @property
    def updated_at(self) -> datetime:
        """
        Last update timestamp.
        """
        return self._updated_at

    @property
    def is_active(self) -> bool:
        """
        Indicates whether the entity is active.
        """
        return self._is_active

    @property
    def version(self) -> int:
        """
        Entity version.
        """
        return self._version

    @property
    def initializing(self) -> bool:
        """
        Initializing state.
        """
        return self._initializing

    # ------------------------------------------------------------------
    # State Management
    # ------------------------------------------------------------------

    def activate(self) -> None:
        """
        Activate the entity.
        """
        self._is_active = True
        self.touch()

    def deactivate(self) -> None:
        """
        Deactivate the entity.
        """
        self._is_active = False
        self.touch()


    def touch(self) -> None:
        """
         Update audit information.

         During object construction, audit information is not updated.
         This prevents property setters from incrementing the version
         while the entity is still being initialized.
        """

        if self._initializing:
            return

        self._updated_at = datetime.now(UTC)

        self._version += 1

    # ------------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------------

    @abstractmethod
    def to_dict(self) -> dict[str, Any]:
        """
        Convert entity into a dictionary suitable for persistence.
        """
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def from_dict(cls, data: dict[str, Any]) -> "BaseEntity":
        """
        Reconstruct an entity from persisted data.
        """
        raise NotImplementedError

    # ------------------------------------------------------------------
    # Equality
    # ------------------------------------------------------------------

    def __eq__(self, other: object) -> bool:
        """
        Two entities are equal when their internal IDs match.
        """
        if not isinstance(other, BaseEntity):
            return NotImplemented

        return self.entity_id == other.entity_id

    def __hash__(self) -> int:
        """
        Hash based on immutable entity ID.
        """
        return hash(self.entity_id)

    # ------------------------------------------------------------------
    # Representation
    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        """
        Developer-friendly representation.
        """
        return (
            f"{self.__class__.__name__}("
            f"entity_id='{self.entity_id}', "
            f"active={self.is_active})"
        )

    def __str__(self) -> str:
        """
        Human-readable representation.
        """
        return (
            f"{self.__class__.__name__}"
            f"[{self.entity_id}]"
        )
