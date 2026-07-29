"""
====================================================================
Banking Management System (BMS)

File        : storage_schema.py
Description : CSV Storage Schema Definitions

This module defines the canonical storage schema for every CSV file
used by the Banking Management System.

Responsibilities
----------------
• Define CSV headers
• Define storage metadata
• Provide a single source of truth for persistence

No business logic exists in this module.

Author      : Adel Alawiyat / ChatGPT
Python      : 3.13+
====================================================================
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from config import Config


@dataclass(frozen=True, slots=True)
class StorageDefinition:
    """
    Immutable definition of a storage file.
    """

    path: Path
    headers: tuple[str, ...]
    description: str
    required: bool = True


STORAGE_SCHEMA: dict[str, StorageDefinition] = {

    "customers": StorageDefinition(
        path=Config.CUSTOMERS_FILE,
        description="Customer master records.",
        headers=(
            "customer_id",
            "first_name",
            "middle_name",
            "last_name",
            "date_of_birth",
            "gender",
            "nationality",
            "national_id",
            "email",
            "mobile_number",
            "status",
        ),
    ),

    "accounts": StorageDefinition(
        path=Config.ACCOUNTS_FILE,
        description="Bank account master records.",
        headers=(
            "account_number",
            "customer_id",
            "account_type",
            "currency",
            "balance",
            "status",
            "opened_date",
        ),
    ),

    "transactions": StorageDefinition(
        path=Config.TRANSACTIONS_FILE,
        description="Financial transaction records.",
        headers=(
            "transaction_id",
            "account_number",
            "transaction_type",
            "amount",
            "currency",
            "transaction_date",
            "description",
        ),
    ),

    "users": StorageDefinition(
        path=Config.USERS_FILE,
        description="Application users.",
        headers=(),
    ),

    "employees": StorageDefinition(
        path=Config.EMPLOYEES_FILE,
        description="Employee records.",
        headers=(),
    ),

    "fees": StorageDefinition(
        path=Config.FEES_FILE,
        description="Bank fee configuration.",
        headers=(),
    ),

    "interest": StorageDefinition(
        path=Config.INTEREST_FILE,
        description="Interest rate configuration.",
        headers=(),
    ),

    "settings": StorageDefinition(
        path=Config.SETTINGS_FILE,
        description="Application settings.",
        headers=(),
    ),

    "audit": StorageDefinition(
        path=Config.AUDIT_FILE,
        description="Audit log.",
        headers=(),
    ),

    "banks": StorageDefinition(
        path=Config.BANKS_FILE,
        description="Bank information.",
        headers=(),
    ),
}

#####################################################################
# Public Helper Functions
#####################################################################

def get_storage_definition(name: str) -> StorageDefinition:
    """
    Return the storage definition for a named storage object.

    Parameters
    ----------
    name:
        Logical storage name (for example, "customers").

    Raises
    ------
    ValueError
        If the requested storage definition does not exist.
    """

    try:
        return STORAGE_SCHEMA[name]

    except KeyError as exc:
        raise ValueError(
            f"Unknown storage definition: '{name}'."
        ) from exc


def required_storage() -> tuple[StorageDefinition, ...]:
    """
    Return all required storage definitions.
    """

    return tuple(
        definition
        for definition in STORAGE_SCHEMA.values()
        if definition.required
    )


def optional_storage() -> tuple[StorageDefinition, ...]:
    """
    Return all optional storage definitions.
    """

    return tuple(
        definition
        for definition in STORAGE_SCHEMA.values()
        if not definition.required
    )


def all_storage() -> tuple[StorageDefinition, ...]:
    """
    Return every storage definition.
    """

    return tuple(STORAGE_SCHEMA.values())


def storage_names() -> tuple[str, ...]:
    """
    Return the logical names of all storage definitions.
    """

    return tuple(STORAGE_SCHEMA.keys())


def storage_count() -> int:
    """
    Return the total number of storage definitions.
    """

    return len(STORAGE_SCHEMA)