"""
===============================================================================
Banking Management System (BMS)

File        : test_base_service.py
Description : Unit tests for the BaseService class.
Author      : Adel Alawiyat / ChatGPT
Python      : 3.13+
===============================================================================
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from exceptions import EntityNotFoundError
from services.base_service import BaseService


class ConcreteService(BaseService):
    """Concrete test implementation of the abstract service base."""

    pass


@pytest.fixture
def repository():
    """Return a lightweight repository double for BaseService tests."""

    repo = MagicMock()
    repo.__len__.return_value = 3
    repo.auto_save = True
    repo.find_by_id.return_value = None
    repo.repository_summary.return_value = {
        "entity_count": 3,
        "auto_save": True,
    }
    return repo


@pytest.fixture
def service(repository):
    """Return a concrete BaseService instance."""

    return ConcreteService(repository)


def test_initialization_stores_repository(service, repository):
    """BaseService should retain the repository supplied at construction."""

    assert service.repository is repository


def test_entity_count_delegates_to_repository_length(service, repository):
    """entity_count should reflect the repository length."""

    repository.__len__.return_value = 7

    assert service.entity_count == 7


def test_reload_delegates_to_repository(service, repository):
    """reload should delegate to repository.reload()."""

    service.reload()

    repository.reload.assert_called_once_with()


def test_save_delegates_to_repository_flush(service, repository):
    """save should persist repository contents through flush()."""

    service.save()

    repository.flush.assert_called_once_with()


def test_summary_delegates_to_repository(service, repository):
    """summary should return the repository summary unchanged."""

    expected = {
        "entity_count": 3,
        "auto_save": True,
    }
    repository.repository_summary.return_value = expected

    result = service.summary()

    assert result == expected
    repository.repository_summary.assert_called_once_with()


def test_exists_delegates_to_repository(service, repository):
    """_exists should delegate to repository.exists()."""

    entity_id = "entity-001"
    repository.exists.return_value = True

    assert service._exists(entity_id) is True
    repository.exists.assert_called_once_with(entity_id)


def test_get_by_id_returns_repository_result(service, repository):
    """_get_by_id should return the repository lookup result."""

    entity = object()
    entity_id = "entity-001"
    repository.find_by_id.return_value = entity

    result = service._get_by_id(entity_id)

    assert result is entity
    repository.find_by_id.assert_called_once_with(entity_id)


def test_get_by_id_returns_none_when_entity_is_missing(service, repository):
    """_get_by_id should return None when the repository finds nothing."""

    entity_id = "missing-entity"
    repository.find_by_id.return_value = None

    assert service._get_by_id(entity_id) is None


def test_get_by_id_or_raise_returns_entity(service, repository):
    """_get_by_id_or_raise should return an existing entity."""

    entity = object()
    entity_id = "entity-001"
    repository.find_by_id.return_value = entity

    result = service._get_by_id_or_raise(entity_id)

    assert result is entity
    repository.find_by_id.assert_called_once_with(entity_id)


def test_get_by_id_or_raise_raises_entity_not_found(service, repository):
    """_get_by_id_or_raise should raise when the entity does not exist."""

    entity_id = "missing-entity"
    repository.find_by_id.return_value = None

    with pytest.raises(
        EntityNotFoundError,
        match="Entity 'missing-entity' was not found",
    ):
        service._get_by_id_or_raise(entity_id)

    repository.find_by_id.assert_called_once_with(entity_id)


def test_save_entity_delegates_to_repository(service, repository):
    """_save_entity should delegate entity persistence."""

    entity = object()

    service._save_entity(entity)

    repository.save_entity.assert_called_once_with(entity)


def test_delete_entity_returns_repository_result(service, repository):
    """_delete_entity should return the repository deletion result."""

    entity_id = "entity-001"
    repository.delete_entity.return_value = True

    result = service._delete_entity(entity_id)

    assert result is True
    repository.delete_entity.assert_called_once_with(entity_id)


def test_refresh_delegates_to_repository_reload(service, repository):
    """_refresh should delegate to repository.reload()."""

    service._refresh()

    repository.reload.assert_called_once_with()


def test_flush_delegates_to_repository_flush(service, repository):
    """_flush should delegate to repository.flush()."""

    service._flush()

    repository.flush.assert_called_once_with()


def test_summary_helper_delegates_to_repository(service, repository):
    """_summary should return repository summary information."""

    expected = {"entity_count": 3}
    repository.repository_summary.return_value = expected

    result = service._summary()

    assert result == expected
    repository.repository_summary.assert_called_once_with()


def test_validate_is_noop_by_default(service):
    """The base validation hook should accept an entity unchanged."""

    entity = object()

    assert service._validate(entity) is None


def test_begin_operation_disables_auto_save_and_returns_previous_state(
    service,
    repository,
):
    """_begin_operation should disable auto-save and preserve its prior state."""

    repository.auto_save = True

    previous_state = service._begin_operation()

    assert previous_state is True
    assert repository.auto_save is False


def test_begin_operation_preserves_disabled_auto_save_state(
    service,
    repository,
):
    """_begin_operation should preserve an already-disabled auto-save state."""

    repository.auto_save = False

    previous_state = service._begin_operation()

    assert previous_state is False
    assert repository.auto_save is False


def test_end_operation_flushes_and_restores_auto_save(
    service,
    repository,
):
    """_end_operation should flush when committing and restore auto-save."""

    repository.auto_save = False

    service._end_operation(previous_state=True)

    repository.flush.assert_called_once_with()
    assert repository.auto_save is True


def test_end_operation_without_commit_does_not_flush(
    service,
    repository,
):
    """_end_operation(commit=False) should restore state without flushing."""

    repository.auto_save = False

    service._end_operation(previous_state=True, commit=False)

    repository.flush.assert_not_called()
    assert repository.auto_save is True


def test_operation_scope_disables_auto_save_during_operation(
    service,
    repository,
):
    """_operation_scope should disable auto-save while the body executes."""

    repository.auto_save = True
    observed_states = []

    with service._operation_scope():
        observed_states.append(repository.auto_save)

    assert observed_states == [False]
    assert repository.auto_save is True
    repository.flush.assert_called_once_with()


def test_operation_scope_flushes_on_success_and_restores_state(
    service,
    repository,
):
    """A successful operation scope should flush and restore auto-save."""

    repository.auto_save = True

    with service._operation_scope():
        pass

    repository.flush.assert_called_once_with()
    assert repository.auto_save is True


def test_operation_scope_restores_state_after_exception(
    service,
    repository,
):
    """An exception should restore auto-save without committing the operation."""

    repository.auto_save = True

    with pytest.raises(RuntimeError, match="operation failed"):
        with service._operation_scope():
            assert repository.auto_save is False
            raise RuntimeError("operation failed")

    repository.flush.assert_not_called()
    assert repository.auto_save is True


def test_operation_scope_preserves_initially_disabled_auto_save(
    service,
    repository,
):
    """Operation scope should restore an initially disabled auto-save state."""

    repository.auto_save = False

    with service._operation_scope():
        assert repository.auto_save is False

    repository.flush.assert_called_once_with()
    assert repository.auto_save is False


def test_before_operation_hook_is_noop(service):
    """The default pre-operation hook should do nothing."""

    assert service._before_operation("test_operation") is None


def test_after_operation_hook_is_noop(service):
    """The default post-operation hook should do nothing."""

    assert service._after_operation("test_operation") is None


def test_operation_failed_hook_is_noop(service):
    """The default failure hook should do nothing."""

    exception = RuntimeError("failure")

    assert (
        service._operation_failed(
            "test_operation",
            exception,
        )
        is None
    )


def test_string_representation_reports_class_and_entity_count(
    service,
    repository,
):
    """__str__ should identify the concrete service and entity count."""

    repository.__len__.return_value = 4

    assert str(service) == "ConcreteService(entities=4)"


def test_repr_reports_class_and_repository_type(service, repository):
    """__repr__ should identify the concrete service and repository class."""

    repository.__class__.__name__ = "FakeRepository"

    assert repr(service) == (
        "ConcreteService(repository=FakeRepository)"
    )
