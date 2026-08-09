"""
===============================================================================
Banking Management System (BMS)

File        : base_service.py
Description : Base Service Class.

Author      : Adel Alawiyat / ChatGPT
Version     : 2.1.0
Python      : 3.13+

===============================================================================
"""

from __future__ import annotations

from abc import ABC
from typing import Generic
from typing import TypeVar

from contextlib import contextmanager
from collections.abc import Iterator

from repositories.base_repository import BaseRepository

from exceptions import EntityNotFoundError

T = TypeVar("T")


class BaseService(
    ABC,
    Generic[T],
):
    """
    Base class for all application services.

    Provides a common interface for repository access and shared
    service functionality.
    """

    def __init__(
        self,
        repository: BaseRepository[T],
    ) -> None:
        """
        Initialize the service.
        """

        self._repository = repository

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def repository(
        self,
    ) -> BaseRepository[T]:
        """
        Return the associated repository.
        """

        return self._repository

    # ------------------------------------------------------------------

    @property
    def entity_count(
        self,
    ) -> int:
        """
        Return the number of managed entities.
        """

        return len(
            self._repository
        )

    # ------------------------------------------------------------------

    def reload(
        self,
    ) -> None:
        """
        Reload repository contents.
        """

        self._repository.reload()

    # ------------------------------------------------------------------

    def save(
        self,
    ) -> None:
        """
        Persist repository contents.
        """

        self._repository.flush()

    # ------------------------------------------------------------------

    def summary(
        self,
    ) -> dict[str, object]:
        """
        Return repository summary information.
        """

        return (
            self._repository.repository_summary()
        )

    # ------------------------------------------------------------------

    def statistics(
        self,
    ) -> dict[str, object]:
        """
        Return repository statistics.

        Concrete services may override this method when they need to
        expose service-specific statistics. The default implementation
        delegates to the repository statistics contract.
        """

        return self._repository.statistics()

#PART 2

    # ------------------------------------------------------------------
    # Protected Helpers
    # ------------------------------------------------------------------

    def _exists(
        self,
        entity_id,
    ) -> bool:
        """
        Determine whether an entity exists.
        """

        return self._repository.exists(
            entity_id
        )

    # ------------------------------------------------------------------

    def _get_by_id(
        self,
        entity_id,
    ):
        """
        Return an entity by its unique identifier.
        """

        return self._repository.find_by_id(
            entity_id
        )

    # ------------------------------------------------------------------

    def _get_by_id_or_raise(
        self,
        entity_id,
    ):
        """
        Return an entity or raise EntityNotFoundError.
        """

        entity = self._repository.find_by_id(
            entity_id
        )

        if entity is None:
            raise EntityNotFoundError(
                f"Entity '{entity_id}' was not found."
            )

        return entity

    # ------------------------------------------------------------------

    def _save_entity(
        self,
        entity: T,
    ) -> None:
        """
        Persist an entity.
        """

        self._repository.save_entity(
            entity
        )

    # ------------------------------------------------------------------

    def _delete_entity(
        self,
        entity_id,
    ) -> bool:
        """
        Soft-delete an entity.
        """

        return self._repository.delete_entity(
            entity_id
        )

    # ------------------------------------------------------------------

    def _refresh(
        self,
    ) -> None:
        """
        Refresh repository contents from persistent storage.
        """

        self._repository.reload()

    # ------------------------------------------------------------------

    def _flush(
        self,
    ) -> None:
        """
        Persist all pending repository changes.
        """

        self._repository.flush()

    # ------------------------------------------------------------------

    def _summary(
        self,
    ) -> dict[str, object]:
        """
        Return repository summary information.
        """

        return self._repository.repository_summary()

# PART 3

    # ------------------------------------------------------------------
    # Validation Hooks
    # ------------------------------------------------------------------

    def _validate(
        self,
        entity: T,
    ) -> None:
        """
        Validate an entity.

        Concrete services should override this method when additional
        business validation is required.
        """

        return

    # ------------------------------------------------------------------
    # Auto Save Control
    # ------------------------------------------------------------------

    def _begin_operation(
        self,
    ) -> bool:
        """
        Begin a multi-step business operation.

        Returns the previous auto-save state so it can be restored when
        the operation completes.
        """

        previous_state = self._repository.auto_save

        self._repository.auto_save = False

        return previous_state

    # ------------------------------------------------------------------

    def _end_operation(
        self,
        previous_state: bool,
        commit: bool = True,
    ) -> None:
        """
        Complete a multi-step business operation.
        """

        if commit:
            self._repository.flush()

        self._repository.auto_save = previous_state

    # ------------------------------------------------------------------
    # Logging Hooks
    # ------------------------------------------------------------------

    def _before_operation(
        self,
        operation: str,
    ) -> None:
        """
        Hook executed before a business operation.

        Override in derived services to integrate logging or auditing.
        """

        return

    # ------------------------------------------------------------------

    def _after_operation(
        self,
        operation: str,
    ) -> None:
        """
        Hook executed after a successful business operation.

        Override in derived services to integrate logging or auditing.
        """

        return

    # ------------------------------------------------------------------

    def _operation_failed(
        self,
        operation: str,
        exception: Exception,
    ) -> None:
        """
        Hook executed when a business operation fails.

        Override in derived services to integrate logging or auditing.
        """

        return

# PART 4

    # ------------------------------------------------------------------
    # Operation Scope
    # ------------------------------------------------------------------

    @contextmanager
    def _operation_scope(
        self,
    ) -> Iterator[None]:
        """
        Execute a multi-step business operation.

        Auto-save is temporarily disabled while the operation is in
        progress. If the operation completes successfully, pending
        changes are flushed. The repository's previous auto-save state
        is always restored.
        """

        previous_state = self._repository.auto_save

        self._repository.auto_save = False

        try:

            yield

            self._repository.flush()

        finally:

            self._repository.auto_save = previous_state

    # ------------------------------------------------------------------
    # Display
    # ------------------------------------------------------------------

    def __str__(
        self,
    ) -> str:
        """
        Human-readable representation.
        """

        return (
            f"{self.__class__.__name__}"
            f"(entities={self.entity_count})"
        )

    # ------------------------------------------------------------------

    def __repr__(
        self,
    ) -> str:
        """
        Developer-friendly representation.
        """

        return (
            f"{self.__class__.__name__}"
            f"(repository="
            f"{self._repository.__class__.__name__})"
        )


# ----------------------------------------------------------------------
# End of File
# ----------------------------------------------------------------------
