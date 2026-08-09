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

T = TypeVar("T", bound=BaseEntity)


class BaseRepository(ABC, Generic[T]):
    """Generic CSV repository."""

    ENTITY_CLASS: type[T]
    CSV_FILE: Path

    def __init__(self) -> None:
        self._entities: dict[str, T] = {}
        self._ensure_storage_exists()
        self.load()

    @property
    def entity_type(self) -> type[T]:
        """Return the concrete entity class managed by this repository."""
        return self.ENTITY_CLASS

    def _ensure_storage_exists(self) -> None:
        """Ensure that the repository storage exists."""
        self.CSV_FILE.parent.mkdir(parents=True, exist_ok=True)
        if not self.CSV_FILE.exists():
            self.CSV_FILE.touch()

    @property
    def count(self) -> int:
        return len(self._entities)

    def is_empty(self) -> bool:
        return self.count == 0

    def find_by_id(self, entity_id: UUID) -> T | None:
        return self._entities.get(entity_id)

    def find_all(self, *, active_only: bool = True) -> list[T]:
        if active_only:
            return [entity for entity in self._entities.values() if entity.is_active]
        return list(self._entities.values())

    def exists(self, entity_id: UUID) -> bool:
        return entity_id in self._entities

    def add(self, entity: T) -> None:
        if self.exists(entity.entity_id):
            raise ValueError(f"{entity.__class__.__name__} already exists.")
        self._entities[entity.entity_id] = entity

    def update(self, entity: T) -> None:
        if not self.exists(entity.entity_id):
            raise ValueError(f"{entity.__class__.__name__} does not exist.")
        entity.touch()
        self._entities[entity.entity_id] = entity

    def remove(self, entity_id: UUID) -> bool:
        entity = self.find_by_id(entity_id)
        if entity is None:
            return False
        entity.deactivate()
        return True

    def restore(self, entity_id: UUID) -> bool:
        entity = self.find_by_id(entity_id)
        if entity is None:
            return False
        entity.activate()
        return True

    def clear_cache(self) -> None:
        self._entities.clear()

    def __len__(self) -> int:
        return self.count

    def __contains__(self, entity_id: UUID) -> bool:
        return self.exists(entity_id)

    def load(self) -> None:
        """Load all entities from the CSV file into memory."""
        self.clear_cache()
        if not self.CSV_FILE.exists() or self.CSV_FILE.stat().st_size == 0:
            return

        with self.CSV_FILE.open(mode="r", newline="", encoding="utf-8") as csv_file:
            reader = csv.DictReader(csv_file)
            for row in reader:
                entity = self.ENTITY_CLASS.from_dict(row)
                self._entities[entity.entity_id] = entity

    def save(self) -> None:
        """
        Persist all cached entities to the CSV file.

        The repository may contain different concrete subclasses of the
        declared entity type. Build the CSV schema from the union of all
        serialized fields so subclass-specific fields are not rejected when
        heterogeneous entities are persisted together.
        """
        entities = list(self._entities.values())

        with self.CSV_FILE.open(mode="w", newline="", encoding="utf-8") as csv_file:
            if not entities:
                csv_file.write("")
                return

            rows = [entity.to_dict() for entity in entities]

            fieldnames: list[str] = []
            for row in rows:
                for field in row:
                    if field not in fieldnames:
                        fieldnames.append(field)

            writer = csv.DictWriter(
                csv_file,
                fieldnames=fieldnames,
                restval="",
            )
            writer.writeheader()
            writer.writerows(rows)

    def reload(self) -> None:
        self.load()

    def flush(self) -> None:
        self.save()

    def refresh(self) -> None:
        self.reload()

    @property
    def file_exists(self) -> bool:
        return self.CSV_FILE.exists()

    @property
    def storage_path(self) -> Path:
        return self.CSV_FILE

    def find_first(self, predicate, *, active_only: bool = True) -> T | None:
        for entity in self.find_all(active_only=active_only):
            if predicate(entity):
                return entity
        return None

    def find_where(self, predicate, *, active_only: bool = True) -> list[T]:
        return [
            entity
            for entity in self.find_all(active_only=active_only)
            if predicate(entity)
        ]

    def count_where(self, predicate, *, active_only: bool = True) -> int:
        return len(self.find_where(predicate, active_only=active_only))

    def any_match(self, predicate, *, active_only: bool = True) -> bool:
        return any(
            predicate(entity)
            for entity in self.find_all(active_only=active_only)
        )

    def all_match(self, predicate, *, active_only: bool = True) -> bool:
        entities = self.find_all(active_only=active_only)
        if not entities:
            return False
        return all(predicate(entity) for entity in entities)

    def sort(self, *, key, reverse: bool = False, active_only: bool = True) -> list[T]:
        return sorted(
            self.find_all(active_only=active_only),
            key=key,
            reverse=reverse,
        )

    def first(self, *, active_only: bool = True) -> T | None:
        entities = self.find_all(active_only=active_only)
        return entities[0] if entities else None

    def last(self, *, active_only: bool = True) -> T | None:
        entities = self.find_all(active_only=active_only)
        return entities[-1] if entities else None

    def save_entity(self, entity: T) -> None:
        if self.exists(entity.entity_id):
            self.update(entity)
        else:
            self.add(entity)
        self.save()

    def delete_entity(self, entity_id: UUID) -> bool:
        removed = self.remove(entity_id)
        if removed:
            self.save()
        return removed

    def purge_inactive(self) -> int:
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

    def repository_summary(self) -> dict[str, object]:
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

    def __iter__(self):
        return iter(self.find_all())

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(entities={self.count})"

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"entity_type={self.ENTITY_CLASS.__name__}, "
            f"count={self.count}, "
            f"file='{self.CSV_FILE}')"
        )

    @property
    def auto_save(self) -> bool:
        return getattr(self, "_auto_save", True)

    @auto_save.setter
    def auto_save(self, value: bool) -> None:
        self._auto_save = bool(value)

    def commit(self) -> None:
        self.flush()

    def __enter__(self) -> "BaseRepository[T]":
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> bool:
        if exc_type is None and self.auto_save:
            self.flush()
        return False

    def close(self) -> None:
        if self.auto_save:
            self.flush()

    def validate_entity(self, entity: T) -> None:
        if not isinstance(entity, self.ENTITY_CLASS):
            raise TypeError(
                f"Expected {self.ENTITY_CLASS.__name__}, "
                f"got {entity.__class__.__name__}."
            )

    def get_or_raise(self, entity_id: UUID) -> T:
        entity = self.find_by_id(entity_id)
        if entity is None:
            raise EntityNotFoundError(
                f"{self.ENTITY_CLASS.__name__} not found."
            )
        return entity

    def add_or_update(self, entity: T) -> None:
        if self.exists(entity.entity_id):
            self.update(entity)
        else:
            self.add(entity)
        self.save()

    def save_all(self, entities: list[T]) -> None:
        for entity in entities:
            if self.exists(entity.entity_id):
                self.update(entity)
            else:
                self.add(entity)
        self.save()

    def count_active(self) -> int:
        return len(self.find_all(active_only=True))

    def count_inactive(self) -> int:
        return len(self.find_all(active_only=False)) - self.count_active()

    def deactivate_all(self) -> None:
        for entity in self._entities.values():
            entity.deactivate()
        self.save()

    def activate_all(self) -> None:
        for entity in self._entities.values():
            entity.activate()
        self.save()

    def save_if_auto(self) -> None:
        if self.auto_save:
            self.save()

    def save_and_refresh(self) -> None:
        self.save()
        self.reload()

    def storage_size(self) -> int:
        if not self.CSV_FILE.exists():
            return 0
        return self.CSV_FILE.stat().st_size

    def clear(self) -> None:
        self.clear_cache()
        self.save()
