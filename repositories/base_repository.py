"""
===============================================================================
Banking Management System (BMS)

File        : base_repository.py
Description : Generic CSV Repository.

Author      : Adel Alawiyat / ChatGPT
Version     : 2.1.0
Python      : 3.13+

===============================================================================
"""

from __future__ import annotations

import csv
from abc import ABC
from pathlib import Path
from typing import Generic, TypeVar

from uuid import UUID

from models.base_entity import BaseEntity

from exceptions import (
    EntityAlreadyExistsError,
    EntityNotFoundError,
)

T = TypeVar(
    "T",
    bound=BaseEntity,
)


class BaseRepository(
    ABC,
    Generic[T],
):
    """
    Generic CSV repository.

    Concrete repositories inherit from this class and provide the
    entity class and CSV file location.
    """

    ENTITY_CLASS: type[T]

    CSV_FILE: Path

    # ------------------------------------------------------------------
    # Constructor
    # ------------------------------------------------------------------

    def __init__(self) -> None:

        self._entities: dict[str, T] = {}

        self._ensure_storage_exists()

        self.load()

    # ------------------------------------------------------------------
    # Storage Initialization
    # ------------------------------------------------------------------

    def _ensure_storage_exists(self) -> None:
        """
        Ensure that the repository storage exists.

        Creates parent directories and the CSV file if necessary.
        """

        self.CSV_FILE.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        if not self.CSV_FILE.exists():

            self.CSV_FILE.touch()

    # ------------------------------------------------------------------
    # Repository Information
    # ------------------------------------------------------------------

    @property
    def count(self) -> int:
        """
        Return the number of loaded entities.
        """

        return len(self._entities)

    # ------------------------------------------------------------------

    def is_empty(self) -> bool:
        """
        Determine whether the repository contains any entities.
        """

        return self.count == 0

# PART 2

    # ------------------------------------------------------------------
    # Lookup Operations
    # ------------------------------------------------------------------

    def find_by_id(
        self,
        entity_id: UUID,
    ) -> T | None:
        """
        Return the entity with the specified identifier.

        Returns None if the entity does not exist.
        """

        return self._entities.get(entity_id)

    # ------------------------------------------------------------------

    def find_all(
        self,
        *,
        active_only: bool = True,
    ) -> list[T]:
        """
        Return all entities.

        Parameters
        ----------
        active_only:
            If True, only active entities are returned.
        """

        if active_only:

            return [
                entity
                for entity in self._entities.values()
                if entity.is_active
            ]

        return list(self._entities.values())

    # ------------------------------------------------------------------

    def exists(
        self,
        entity_id: UUID,
    ) -> bool:
        """
        Determine whether an entity exists.
        """

        return entity_id in self._entities

    # ------------------------------------------------------------------
    # CRUD Operations
    # ------------------------------------------------------------------

    def add(
        self,
        entity: T,
    ) -> None:
        """
        Add a new entity.

        Raises
        ------
        ValueError
            If the entity already exists.
        """

        if self.exists(entity.entity_id):

            raise ValueError(
                f"{entity.__class__.__name__} already exists."
            )

        self._entities[entity.entity_id] = entity

    # ------------------------------------------------------------------

    def update(
        self,
        entity: T,
    ) -> None:
        """
        Update an existing entity.
        """
        # print(entity.entity_id)
        # print(id(entity))
        # print(self._entities.keys())
        # print(entity.entity_id in self._entities)

        if not self.exists(entity.entity_id):

            raise ValueError(
                f"{entity.__class__.__name__} does not exist."
            )

        entity.touch()

        self._entities[entity.entity_id] = entity

    # ------------------------------------------------------------------

    def remove(
        self,
        entity_id: UUID,
    ) -> bool:
        """
        Soft-delete an entity.

        Returns
        -------
        bool
            True if the entity existed.
        """

        entity = self.find_by_id(entity_id)

        if entity is None:
            return False

        entity.deactivate()

        return True

    # ------------------------------------------------------------------

    def restore(
        self,
        entity_id: UUID,
    ) -> bool:
        """
        Restore a previously deactivated entity.
        """

        entity = self.find_by_id(entity_id)

        if entity is None:
            return False

        entity.activate()

        return True

    # ------------------------------------------------------------------

    def clear_cache(self) -> None:
        """
        Remove all entities from the in-memory cache.

        Does not modify persistent storage.
        """

        self._entities.clear()

    # ------------------------------------------------------------------

    def __len__(self) -> int:
        """
        Return the number of cached entities.
        """

        return self.count

    # ------------------------------------------------------------------

    def __contains__(
        self,
        entity_id: UUID,
    ) -> bool:
        """
        Support the 'in' operator.
        """

        return self.exists(entity_id)

# PART 3

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def load(self) -> None:
        """
        Load all entities from the CSV file into memory.
        """

        self.clear_cache()

        if (
            not self.CSV_FILE.exists()
            or self.CSV_FILE.stat().st_size == 0
        ):
            return

        with self.CSV_FILE.open(
            mode="r",
            newline="",
            encoding="utf-8",
        ) as csv_file:

            reader = csv.DictReader(csv_file)

            for row in reader:

                entity = self.ENTITY_CLASS.from_dict(row)

                self._entities[
                    entity.entity_id
                ] = entity

    # ------------------------------------------------------------------

    def save(self) -> None:
        """
        Persist all cached entities to the CSV file.
        """

        entities = list(self._entities.values())

        with self.CSV_FILE.open(
            mode="w",
            newline="",
            encoding="utf-8",
        ) as csv_file:

            # Empty repository
            if not entities:

                csv_file.write("")

                return

            fieldnames = list(
                entities[0].to_dict().keys()
            )

            writer = csv.DictWriter(
                csv_file,
                fieldnames=fieldnames,
            )

            writer.writeheader()

            for entity in entities:

                writer.writerow(
                    entity.to_dict()
                )

    # ------------------------------------------------------------------

    def reload(self) -> None:
        """
        Discard the current cache and reload the repository from disk.
        """

        self.load()

    # ------------------------------------------------------------------

    def flush(self) -> None:
        """
        Persist the current cache to storage.

        This method is provided as an alias for save() to better express
        intent when called by service classes.
        """

        self.save()

    # ------------------------------------------------------------------

    def refresh(self) -> None:
        """
        Synchronize the repository with persistent storage.

        Current implementation reloads from disk.
        """

        self.reload()

    # ------------------------------------------------------------------

    @property
    def file_exists(self) -> bool:
        """
        Determine whether the repository storage file exists.
        """

        return self.CSV_FILE.exists()

    # ------------------------------------------------------------------

    @property
    def storage_path(self) -> Path:
        """
        Return the CSV storage path.
        """

        return self.CSV_FILE

# PART 4

    # ------------------------------------------------------------------
    # Query Operations
    # ------------------------------------------------------------------

    def find_first(
        self,
        predicate,
        *,
        active_only: bool = True,
    ) -> T | None:
        """
        Return the first entity matching the supplied predicate.

        Returns None if no matching entity exists.
        """

        for entity in self.find_all(
            active_only=active_only,
        ):
            if predicate(entity):
                return entity

        return None

    # ------------------------------------------------------------------

    def find_where(
        self,
        predicate,
        *,
        active_only: bool = True,
    ) -> list[T]:
        """
        Return all entities matching the supplied predicate.
        """

        return [
            entity
            for entity in self.find_all(
                active_only=active_only,
            )
            if predicate(entity)
        ]

    # ------------------------------------------------------------------

    def count_where(
        self,
        predicate,
        *,
        active_only: bool = True,
    ) -> int:
        """
        Count entities matching the supplied predicate.
        """

        return len(
            self.find_where(
                predicate,
                active_only=active_only,
            )
        )

    # ------------------------------------------------------------------

    def any_match(
        self,
        predicate,
        *,
        active_only: bool = True,
    ) -> bool:
        """
        Determine whether any entity satisfies the predicate.
        """

        return any(
            predicate(entity)
            for entity in self.find_all(
                active_only=active_only,
            )
        )

    # ------------------------------------------------------------------

    def all_match(
        self,
        predicate,
        *,
        active_only: bool = True,
    ) -> bool:
        """
        Determine whether all entities satisfy the predicate.
        """

        entities = self.find_all(
            active_only=active_only,
        )

        if not entities:
            return False

        return all(
            predicate(entity)
            for entity in entities
        )

    # ------------------------------------------------------------------

    def sort(
        self,
        *,
        key,
        reverse: bool = False,
        active_only: bool = True,
    ) -> list[T]:
        """
        Return entities sorted using the supplied key function.
        """

        return sorted(
            self.find_all(
                active_only=active_only,
            ),
            key=key,
            reverse=reverse,
        )

    # ------------------------------------------------------------------

    def first(
        self,
        *,
        active_only: bool = True,
    ) -> T | None:
        """
        Return the first entity in the repository.
        """

        entities = self.find_all(
            active_only=active_only,
        )

        return entities[0] if entities else None

    # ------------------------------------------------------------------

    def last(
        self,
        *,
        active_only: bool = True,
    ) -> T | None:
        """
        Return the last entity in the repository.
        """

        entities = self.find_all(
            active_only=active_only,
        )

        return entities[-1] if entities else None

# PART 5

    # ------------------------------------------------------------------
    # Administrative Operations
    # ------------------------------------------------------------------

    def save_entity(
        self,
        entity: T,
    ) -> None:
        """
        Add or update an entity, then persist the repository.
        """

        if self.exists(entity.entity_id):
            self.update(entity)
        else:
            self.add(entity)

        self.save()

    # ------------------------------------------------------------------

    def delete_entity(
        self,
        entity_id: UUID,
    ) -> bool:
        """
        Soft-delete an entity and persist the repository.

        Returns
        -------
        bool
            True if the entity existed.
        """

        removed = self.remove(entity_id)

        if removed:
            self.save()

        return removed

    # ------------------------------------------------------------------

    def purge_inactive(self) -> int:
        """
        Permanently remove inactive entities from the repository.

        Returns
        -------
        int
            Number of entities removed.
        """

        inactive_ids = [
            entity.entity_id
            for entity in self._entities.values()
            if not entity.is_active
        ]

        for entity_id in inactive_ids:
            del self._entities[entity_id]

        if inactive_ids:
            self.save()

        return len(inactive_ids)

    # ------------------------------------------------------------------

    def repository_summary(self) -> dict[str, object]:
        """
        Return summary information about the repository.
        """

        total = len(self._entities)
        active = len(self.find_all(active_only=True))

        return {
            "repository": self.__class__.__name__,
            "entity_type": self.ENTITY_CLASS.__name__,
            "storage_file": str(self.CSV_FILE),
            "total_entities": total,
            "active_entities": active,
            "inactive_entities": total - active,
        }

    # ------------------------------------------------------------------
    # Iteration
    # ------------------------------------------------------------------

    def __iter__(self):
        """
        Iterate over all active entities.
        """

        return iter(self.find_all())

    # ------------------------------------------------------------------

    def __str__(self) -> str:
        """
        Human-readable repository representation.
        """

        return (
            f"{self.__class__.__name__}"
            f"(entities={self.count})"
        )

    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        """
        Developer-friendly repository representation.
        """

        return (
            f"{self.__class__.__name__}("
            f"entity_type={self.ENTITY_CLASS.__name__}, "
            f"count={self.count}, "
            f"file='{self.CSV_FILE}')"
        )

# PART 6

    # ------------------------------------------------------------------
    # Auto Save
    # ------------------------------------------------------------------

    @property
    def auto_save(self) -> bool:
        """
        Return whether automatic persistence is enabled.
        """

        return getattr(self, "_auto_save", True)

    # ------------------------------------------------------------------

    @auto_save.setter
    def auto_save(
        self,
        value: bool,
    ) -> None:
        """
        Enable or disable automatic persistence.
        """

        self._auto_save = bool(value)

    # ------------------------------------------------------------------

    def commit(self) -> None:
        """
        Persist pending changes.

        Alias for flush() to provide terminology familiar to developers
        accustomed to database transaction semantics.
        """

        self.flush()

    # ------------------------------------------------------------------
    # Context Manager Support
    # ------------------------------------------------------------------

    def __enter__(self) -> "BaseRepository[T]":
        """
        Enter the repository context.
        """

        return self

    # ------------------------------------------------------------------

    def __exit__(
        self,
        exc_type,
        exc_value,
        traceback,
    ) -> bool:
        """
        Automatically persist changes when leaving the context if no
        exception occurred and auto-save is enabled.
        """

        if (
            exc_type is None
            and self.auto_save
        ):
            self.flush()

        return False

    # ------------------------------------------------------------------
    # Utility Methods
    # ------------------------------------------------------------------

    def close(self) -> None:
        """
        Flush pending changes.

        Included for API symmetry and future extensibility.
        """

        if self.auto_save:
            self.flush()

    # ------------------------------------------------------------------

    @property
    def entity_type(self) -> type[T]:
        """
        Return the entity class managed by this repository.
        """

        return self.ENTITY_CLASS

    # ------------------------------------------------------------------

    @property
    def repository_name(self) -> str:
        """
        Return the repository class name.
        """

        return self.__class__.__name__


# ----------------------------------------------------------------------
# End of File
# ----------------------------------------------------------------------
