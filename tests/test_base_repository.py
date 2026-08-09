# Part 1 — Imports, Test Entity, Test Repository & Fixtures

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

import pytest

from models.base_entity import BaseEntity
from repositories.base_repository import BaseRepository


# ---------------------------------------------------------------------
# Test Entity
# ---------------------------------------------------------------------

class DummyEntity(BaseEntity):

    def __init__(
        self,
        name: str,
    ):
        super().__init__()
        self.name = name

    def to_dict(self):

        return {
            "entity_id": str(self.entity_id),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "is_active": self.is_active,
            "version": self.version,
            "name": self.name,
        }

    @classmethod
    def from_dict(
        cls,
        data,
    ):

        entity = cls(
            name=data["name"],
        )

        entity._entity_id = uuid4().__class__(
            data["entity_id"]
        )

        entity._created_at = datetime.fromisoformat(
            data["created_at"]
        )

        entity._updated_at = datetime.fromisoformat(
            data["updated_at"]
        )

        entity._is_active = (
            str(data["is_active"]).lower()
            == "true"
        )

        entity._version = int(
            data["version"]
        )

        return entity


# ---------------------------------------------------------------------
# Test Repository
# ---------------------------------------------------------------------

class DummyRepository(
    BaseRepository[DummyEntity]
):

    ENTITY_CLASS = DummyEntity

    CSV_FILE = Path(
        "tests/temp/test_dummy_repository.csv"
    )


# ---------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------

@pytest.fixture
def repository():

    repo = DummyRepository()

    repo.clear_cache()

    yield repo

    repo.clear_cache()

    if repo.CSV_FILE.exists():
        repo.CSV_FILE.unlink()


@pytest.fixture
def entity():

    return DummyEntity(
        name="John"
    )


@pytest.fixture
def second_entity():

    return DummyEntity(
        name="Sara"
    )


@pytest.fixture
def populated_repository(
    repository,
    entity,
    second_entity,
):

    repository.add(entity)
    repository.add(second_entity)

    return repository

# Part 2 – Constructor, Initialization & Basic Repository State

# ============================================================
# Part 2 — Constructor & Repository State
# ============================================================


def test_repository_starts_empty(repository):

    assert repository.count == 0
    assert repository.is_empty()


def test_len_returns_entity_count(repository):

    assert len(repository) == 0

    repository.add(DummyEntity("John"))

    assert len(repository) == 1


def test_count_property(repository):

    assert repository.count == 0

    repository.add(DummyEntity("John"))
    repository.add(DummyEntity("Sara"))

    assert repository.count == 2


def test_storage_path(repository):

    assert repository.storage_path == repository.CSV_FILE


def test_file_exists_property(repository):

    assert repository.file_exists
    assert repository.CSV_FILE.exists()


def test_contains_false_for_unknown_entity(
    repository,
):

    unknown = uuid4()

    assert unknown not in repository


def test_contains_true_after_add(
    repository,
    entity,
):

    repository.add(entity)

    assert entity.entity_id in repository


def test_iter_returns_no_entities_when_empty(
    repository,
):

    entities = list(repository)

    assert entities == []


def test_iter_returns_active_entities_only(
    populated_repository,
):

    entities = list(populated_repository)

    assert len(entities) == 2


def test_first_empty_repository(
    repository,
):

    assert repository.first() is None


def test_last_empty_repository(
    repository,
):

    assert repository.last() is None


def test_first_returns_first_entity(
    populated_repository,
):

    first = populated_repository.first()

    assert first is not None
    assert isinstance(first, DummyEntity)


def test_last_returns_last_entity(
    populated_repository,
):

    last = populated_repository.last()

    assert last is not None
    assert isinstance(last, DummyEntity)


def test_str_representation(repository):

    assert (
        str(repository)
        == "DummyRepository(entities=0)"
    )


def test_repr_contains_repository_information(
    repository,
):

    text = repr(repository)

    assert "DummyRepository" in text
    assert "DummyEntity" in text
    assert "count=0" in text


def test_clear_cache(repository):

    repository.add(DummyEntity("John"))

    assert repository.count == 1

    repository.clear_cache()

    assert repository.count == 0
    assert repository.is_empty()


def test_auto_save_defaults_to_true(
    repository,
):

    assert repository.auto_save is True


def test_auto_save_can_be_disabled(
    repository,
):

    repository.auto_save = False

    assert repository.auto_save is False


def test_auto_save_can_be_enabled(
    repository,
):

    repository.auto_save = False
    repository.auto_save = True

    assert repository.auto_save is True


def test_commit_alias(repository):

    repository.add(DummyEntity("John"))

    repository.commit()

    assert repository.file_exists


def test_refresh_alias(
    repository,
):

    repository.refresh()

    assert repository.count == 0


def test_reload_alias(
    repository,
):

    repository.reload()

    assert repository.count == 0


def test_flush_alias(
    repository,
):

    repository.flush()

    assert repository.file_exists

# Part 3 - tests the core CRUD operations of BaseRepository

# ============================================================
# Part 3 — CRUD Operations
# ============================================================


def test_add_entity(
    repository,
    entity,
):

    repository.add(entity)

    assert repository.count == 1
    assert repository.find_by_id(entity.entity_id) is entity


def test_add_multiple_entities(
    repository,
    entity,
    second_entity,
):

    repository.add(entity)
    repository.add(second_entity)

    assert repository.count == 2


def test_add_duplicate_entity_raises_value_error(
    repository,
    entity,
):

    repository.add(entity)

    with pytest.raises(ValueError):
        repository.add(entity)


def test_exists_returns_true(
    repository,
    entity,
):

    repository.add(entity)

    assert repository.exists(entity.entity_id)


def test_exists_returns_false(
    repository,
):

    assert not repository.exists(uuid4())


def test_find_by_id_returns_entity(
    repository,
    entity,
):

    repository.add(entity)

    found = repository.find_by_id(
        entity.entity_id
    )

    assert found is entity


def test_find_by_id_returns_none(
    repository,
):

    assert repository.find_by_id(
        uuid4()
    ) is None


def test_update_existing_entity(
    repository,
    entity,
):

    repository.add(entity)

    entity.name = "Updated"

    previous_version = entity.version

    repository.update(entity)

    updated = repository.find_by_id(
        entity.entity_id
    )

    assert updated.name == "Updated"
    assert updated.version > previous_version


def test_update_missing_entity_raises_value_error(
    repository,
    entity,
):

    with pytest.raises(ValueError):
        repository.update(entity)


def test_remove_existing_entity(
    repository,
    entity,
):

    repository.add(entity)

    result = repository.remove(
        entity.entity_id
    )

    assert result is True
    assert not entity.is_active


def test_remove_unknown_entity_returns_false(
    repository,
):

    assert (
        repository.remove(uuid4())
        is False
    )


def test_restore_existing_entity(
    repository,
    entity,
):

    repository.add(entity)

    repository.remove(
        entity.entity_id
    )

    assert not entity.is_active

    result = repository.restore(
        entity.entity_id
    )

    assert result is True
    assert entity.is_active


def test_restore_unknown_entity_returns_false(
    repository,
):

    assert (
        repository.restore(uuid4())
        is False
    )


def test_save_entity_adds_new_entity(
    repository,
    entity,
):

    repository.save_entity(entity)

    assert repository.count == 1
    assert repository.exists(
        entity.entity_id
    )


def test_save_entity_updates_existing_entity(
    repository,
    entity,
):

    repository.save_entity(entity)

    entity.name = "Modified"

    repository.save_entity(entity)

    loaded = repository.find_by_id(
        entity.entity_id
    )

    assert loaded.name == "Modified"


def test_delete_entity_existing(
    repository,
    entity,
):

    repository.add(entity)

    result = repository.delete_entity(
        entity.entity_id
    )

    assert result is True
    assert not entity.is_active


def test_delete_entity_unknown_returns_false(
    repository,
):

    assert (
        repository.delete_entity(uuid4())
        is False
    )


def test_remove_does_not_reduce_repository_count(
    repository,
    entity,
):

    repository.add(entity)

    repository.remove(
        entity.entity_id
    )

    assert repository.count == 1


def test_restore_preserves_repository_count(
    repository,
    entity,
):

    repository.add(entity)

    repository.remove(
        entity.entity_id
    )

    repository.restore(
        entity.entity_id
    )

    assert repository.count == 1


def test_update_preserves_entity_identity(
    repository,
    entity,
):

    repository.add(entity)

    entity.name = "ABC"

    repository.update(entity)

    loaded = repository.find_by_id(
        entity.entity_id
    )

    assert loaded is entity


def test_multiple_updates(
    repository,
    entity,
):

    repository.add(entity)

    for i in range(5):
        entity.name = f"Name {i}"
        repository.update(entity)

    assert (
        repository.find_by_id(
            entity.entity_id
        ).name
        == "Name 4"
    )


def test_add_after_remove_new_entity(
    repository,
    entity,
):

    repository.add(entity)

    repository.remove(
        entity.entity_id
    )

    second = DummyEntity(
        "Second"
    )

    repository.add(second)

    assert repository.count == 2


def test_find_removed_entity_still_exists(
    repository,
    entity,
):

    repository.add(entity)

    repository.remove(
        entity.entity_id
    )

    loaded = repository.find_by_id(
        entity.entity_id
    )

    assert loaded is entity
    assert not loaded.is_active

# Part 4 – Collection Queries & Predicate Operations

# ============================================================
# Part 4 — Collection Queries
# ============================================================


def test_find_all_returns_active_entities(
    repository,
):

    first = DummyEntity("First")
    second = DummyEntity("Second")

    repository.add(first)
    repository.add(second)

    repository.remove(first.entity_id)

    results = repository.find_all()

    assert len(results) == 1
    assert results[0] is second


def test_find_all_including_inactive(
    repository,
):

    first = DummyEntity("First")
    second = DummyEntity("Second")

    repository.add(first)
    repository.add(second)

    repository.remove(first.entity_id)

    results = repository.find_all(
        active_only=False,
    )

    assert len(results) == 2


def test_find_first_returns_matching_entity(
    repository,
):

    repository.add(DummyEntity("Alice"))
    repository.add(DummyEntity("Bob"))

    found = repository.find_first(
        lambda e: e.name == "Bob"
    )

    assert found is not None
    assert found.name == "Bob"


def test_find_first_returns_none_when_missing(
    repository,
):

    repository.add(DummyEntity("Alice"))

    result = repository.find_first(
        lambda e: e.name == "Charlie"
    )

    assert result is None


def test_find_where_returns_matches(
    repository,
):

    repository.add(DummyEntity("Alice"))
    repository.add(DummyEntity("Bob"))
    repository.add(DummyEntity("Alice"))

    results = repository.find_where(
        lambda e: e.name == "Alice"
    )

    assert len(results) == 2


def test_find_where_returns_empty_list(
    repository,
):

    repository.add(DummyEntity("Alice"))

    results = repository.find_where(
        lambda e: e.name == "Nobody"
    )

    assert results == []


def test_count_where(
    repository,
):

    repository.add(DummyEntity("One"))
    repository.add(DummyEntity("Two"))
    repository.add(DummyEntity("Two"))

    count = repository.count_where(
        lambda e: e.name == "Two"
    )

    assert count == 2


def test_count_where_zero(
    repository,
):

    repository.add(DummyEntity("One"))

    assert (
        repository.count_where(
            lambda e: e.name == "XYZ"
        )
        == 0
    )


def test_any_match_true(
    repository,
):

    repository.add(DummyEntity("Alpha"))

    assert repository.any_match(
        lambda e: e.name == "Alpha"
    )


def test_any_match_false(
    repository,
):

    repository.add(DummyEntity("Alpha"))

    assert not repository.any_match(
        lambda e: e.name == "Beta"
    )


def test_all_match_true(
    repository,
):

    repository.add(DummyEntity("Same"))
    repository.add(DummyEntity("Same"))

    assert repository.all_match(
        lambda e: e.name == "Same"
    )


def test_all_match_false(
    repository,
):

    repository.add(DummyEntity("One"))
    repository.add(DummyEntity("Two"))

    assert not repository.all_match(
        lambda e: e.name == "One"
    )


def test_all_match_empty_repository_returns_false(
    repository,
):

    assert not repository.all_match(
        lambda e: True
    )


def test_sort_ascending(
    repository,
):

    repository.add(DummyEntity("Charlie"))
    repository.add(DummyEntity("Alice"))
    repository.add(DummyEntity("Bob"))

    results = repository.sort(
        key=lambda e: e.name,
    )

    names = [
        e.name
        for e in results
    ]

    assert names == [
        "Alice",
        "Bob",
        "Charlie",
    ]


def test_sort_descending(
    repository,
):

    repository.add(DummyEntity("Charlie"))
    repository.add(DummyEntity("Alice"))
    repository.add(DummyEntity("Bob"))

    results = repository.sort(
        key=lambda e: e.name,
        reverse=True,
    )

    names = [
        e.name
        for e in results
    ]

    assert names == [
        "Charlie",
        "Bob",
        "Alice",
    ]


def test_first_returns_first_active(
    repository,
):

    first = DummyEntity("First")
    second = DummyEntity("Second")

    repository.add(first)
    repository.add(second)

    assert repository.first() is first


def test_first_returns_none_when_empty(
    repository,
):

    assert repository.first() is None


def test_last_returns_last_active(
    repository,
):

    repository.add(DummyEntity("One"))
    last = DummyEntity("Two")

    repository.add(last)

    assert repository.last() is last


def test_last_returns_none_when_empty(
    repository,
):

    assert repository.last() is None


def test_iteration_returns_active_entities(
    repository,
):

    first = DummyEntity("One")
    second = DummyEntity("Two")

    repository.add(first)
    repository.add(second)

    repository.remove(first.entity_id)

    items = list(repository)

    assert items == [second]


def test_iteration_empty_repository(
    repository,
):

    assert list(repository) == []


def test_find_first_ignores_inactive_by_default(
    repository,
):

    entity = DummyEntity("Hidden")

    repository.add(entity)

    repository.remove(entity.entity_id)

    assert (
        repository.find_first(
            lambda e: e.name == "Hidden"
        )
        is None
    )


def test_find_first_including_inactive(
    repository,
):

    entity = DummyEntity("Hidden")

    repository.add(entity)

    repository.remove(entity.entity_id)

    found = repository.find_first(
        lambda e: e.name == "Hidden",
        active_only=False,
    )

    assert found is entity

# Part 5 – Persistence, Context Manager, and Repository Utilities

# ============================================================
# Part 5 — Persistence, Utilities & Context Manager
# ============================================================


def test_repository_summary(
    repository,
    entity,
):

    repository.add(entity)

    summary = repository.repository_summary()

    assert summary["repository"] == "DummyRepository"
    assert summary["entity_type"] == "DummyEntity"
    assert summary["total_entities"] == 1
    assert summary["active_entities"] == 1
    assert summary["inactive_entities"] == 0


def test_purge_inactive(
    repository,
):

    first = DummyEntity("One")
    second = DummyEntity("Two")

    repository.add(first)
    repository.add(second)

    repository.remove(first.entity_id)

    removed = repository.purge_inactive()

    assert removed == 1
    assert repository.count == 1


def test_purge_inactive_empty(
    repository,
):

    assert repository.purge_inactive() == 0


def test_storage_path_property(
    repository,
):

    assert repository.storage_path == repository.CSV_FILE


def test_file_exists_property(
    repository,
):

    assert repository.file_exists


def test_commit_calls_save(
    repository,
    entity,
):

    repository.add(entity)

    repository.commit()

    assert repository.count == 1


def test_flush_calls_save(
    repository,
    entity,
):

    repository.add(entity)

    repository.flush()

    assert repository.count == 1


def test_refresh_calls_reload(
    repository,
    entity,
):

    repository.add(entity)

    repository.save()

    repository.clear_cache()

    assert repository.count == 0

    repository.refresh()

    assert repository.count == 1


def test_reload_restores_saved_entities(
    repository,
    entity,
):

    repository.add(entity)

    repository.save()

    repository.clear_cache()

    repository.reload()

    assert repository.count == 1


def test_close_with_auto_save_enabled(
    repository,
    entity,
):

    repository.add(entity)

    repository.auto_save = True

    repository.close()

    assert repository.count == 1


def test_close_with_auto_save_disabled(
    repository,
    entity,
):

    repository.add(entity)

    repository.auto_save = False

    repository.close()

    assert repository.count == 1


def test_context_manager_returns_repository(
    repository,
):

    with repository as repo:

        assert repo is repository


def test_context_manager_auto_save_enabled(
    repository,
    entity,
):

    repository.auto_save = True

    with repository as repo:

        repo.add(entity)

    assert repository.count == 1


def test_context_manager_auto_save_disabled(
    repository,
    entity,
):

    repository.auto_save = False

    with repository as repo:

        repo.add(entity)

    assert repository.count == 1


def test_string_representation(
    repository,
):

    text = str(repository)

    assert "DummyRepository" in text


def test_repr_representation(
    repository,
):

    text = repr(repository)

    assert "DummyRepository" in text
    assert "DummyEntity" in text


def test_auto_save_default_enabled(
    repository,
):

    assert repository.auto_save is True


def test_auto_save_property(
    repository,
):

    repository.auto_save = False

    assert repository.auto_save is False

    repository.auto_save = True

    assert repository.auto_save is True


def test_clear_cache(
    repository,
    entity,
):

    repository.add(entity)

    repository.clear_cache()

    assert repository.count == 0


def test_load_empty_repository(
    repository,
):

    repository.clear_cache()

    repository.load()

    assert repository.count == 0


def test_save_then_reload_round_trip(
    repository,
):

    first = DummyEntity("One")
    second = DummyEntity("Two")

    repository.add(first)
    repository.add(second)

    repository.save()

    repository.clear_cache()

    repository.reload()

    assert repository.count == 2


def test_len_after_reload(
    repository,
    entity,
):

    repository.add(entity)

    repository.save()

    repository.reload()

    assert len(repository) == 1


def test_repository_summary_after_soft_delete(
    repository,
    entity,
):

    repository.add(entity)

    repository.remove(entity.entity_id)

    summary = repository.repository_summary()

    assert summary["total_entities"] == 1
    assert summary["active_entities"] == 0
    assert summary["inactive_entities"] == 1

