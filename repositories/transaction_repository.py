"""
===============================================================================
Banking Management System (BMS)

File        : transaction_repository.py
Description : Transaction Repository.

Author      : Adel Alawiyat / ChatGPT
Version     : 2.1.2
Python      : 3.13+

===============================================================================
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from pathlib import Path

import config

from models.transaction import Transaction

from repositories.base_repository import BaseRepository

from utils.constants import (
    TransactionStatus,
    TransactionType,
)

from exceptions import (
    EntityAlreadyExistsError,
    UnsupportedOperationError,
)


class TransactionRepository(
    BaseRepository[Transaction],
):
    """
    Repository responsible for transaction persistence and retrieval.

    Transactions are immutable business records. Once persisted,
    they must not be modified or physically deleted.
    """

    ENTITY_CLASS = Transaction

    CSV_FILE: Path = config.TRANSACTIONS_FILE

    def __init__(self) -> None:
        super().__init__()

    @staticmethod
    def _normalize(value: str) -> str:
        """Normalize string values for lookups."""
        return value.strip().upper()

    def find_by_transaction_number(
        self,
        transaction_number: str,
    ) -> Transaction | None:
        """Return the transaction having the specified transaction number."""
        transaction_number = self._normalize(transaction_number)
        return self.find_first(
            lambda transaction: self._normalize(
                transaction.transaction_number
            ) == transaction_number
        )

    def get_or_raise(self, transaction_number: str) -> Transaction:
        """Return a transaction by its business transaction number."""
        transaction = self.find_by_transaction_number(transaction_number)
        if transaction is None:
            from exceptions import EntityNotFoundError
            raise EntityNotFoundError("Transaction not found.")
        return transaction

    def exists_transaction_number(
        self,
        transaction_number: str,
    ) -> bool:
        """Determine whether a transaction number exists."""
        return self.find_by_transaction_number(transaction_number) is not None

    def transaction_exists(
        self,
        transaction_number: str,
    ) -> bool:
        """Compatibility alias for checking transaction-number existence."""
        return self.exists_transaction_number(transaction_number)

    def find_by_account(
        self,
        account_number: str,
    ) -> list[Transaction]:
        """
        Return all transactions involving an account.

        An account can participate in a transaction either as the source
        account or as the destination account. Transaction intentionally
        does not expose a single ``account_number`` attribute because an
        internal transfer has two account participants.
        """
        account_number = self._normalize(account_number)

        return self.find_where(
            lambda transaction: transaction.affects_account(account_number)
        )

    def account_has_transactions(
        self,
        account_number: str,
    ) -> bool:
        """Determine whether an account has any transactions."""
        return len(self.find_by_account(account_number)) > 0

    def find_by_customer(
        self,
        customer_number: str,
    ) -> list[Transaction]:
        """Return all transactions belonging to the specified customer."""
        customer_number = self._normalize(customer_number)
        return self.find_where(
            lambda transaction: self._normalize(
                transaction.customer_number
            ) == customer_number
        )

    def find_by_type(
        self,
        transaction_type: TransactionType,
    ) -> list[Transaction]:
        """Return transactions matching the supplied transaction type."""
        return self.find_where(
            lambda transaction: transaction.transaction_type == transaction_type
        )

    def deposits(self) -> list[Transaction]:
        """Return all deposit transactions."""
        return self.find_by_type(TransactionType.DEPOSIT)

    def withdrawals(self) -> list[Transaction]:
        """Return all withdrawal transactions."""
        return self.find_by_type(TransactionType.WITHDRAWAL)

    def transfers(self) -> list[Transaction]:
        """Return all internal and external transfer transactions."""
        return self.find_where(
            lambda transaction: transaction.transaction_type
            in (
                TransactionType.INTERNAL_TRANSFER,
                TransactionType.EXTERNAL_TRANSFER,
            )
        )

    def find_by_status(
        self,
        status: TransactionStatus,
    ) -> list[Transaction]:
        """Return transactions matching the supplied transaction status."""
        return self.find_where(
            lambda transaction: transaction.transaction_status == status
        )

    def completed_transactions(self) -> list[Transaction]:
        """Return all completed transactions."""
        return self.find_by_status(TransactionStatus.COMPLETED)

    def pending_transactions(self) -> list[Transaction]:
        """Return all pending transactions."""
        return self.find_by_status(TransactionStatus.PENDING)

    def failed_transactions(self) -> list[Transaction]:
        """Return all failed transactions."""
        return self.find_by_status(TransactionStatus.FAILED)

    def transaction_count(self) -> int:
        """Return the total number of persisted transactions."""
        return self.count

    def completed_transaction_count(self) -> int:
        """Return the number of completed transactions."""
        return len(self.completed_transactions())

    def pending_transaction_count(self) -> int:
        """Return the number of pending transactions."""
        return len(self.pending_transactions())

    def failed_transaction_count(self) -> int:
        """Return the number of failed transactions."""
        return len(self.failed_transactions())

    def find_by_date_range(
        self,
        start_date: date,
        end_date: date,
    ) -> list[Transaction]:
        """Return transactions whose transaction date falls within the range."""
        if start_date > end_date:
            raise ValueError("Start date cannot be after end date.")
        return self.find_where(
            lambda transaction: start_date
            <= transaction.transaction_date
            <= end_date
        )

    def find_by_amount_range(
        self,
        minimum_amount: Decimal,
        maximum_amount: Decimal,
    ) -> list[Transaction]:
        """Return transactions whose amounts fall within the supplied range."""
        if minimum_amount > maximum_amount:
            raise ValueError("Minimum amount cannot exceed maximum amount.")
        return self.find_where(
            lambda transaction: minimum_amount
            <= transaction.amount.amount
            <= maximum_amount
        )

    def transaction_history(
        self,
        account_number: str,
    ) -> list[Transaction]:
        """Return chronological transaction history for an account."""
        return sorted(
            self.find_by_account(account_number),
            key=lambda transaction: (
                transaction.transaction_date,
                transaction.transaction_time,
            ),
        )

    def customer_transaction_history(
        self,
        customer_number: str,
    ) -> list[Transaction]:
        """Return chronological transaction history for a customer."""
        return sorted(
            self.find_by_customer(customer_number),
            key=lambda transaction: (
                transaction.transaction_date,
                transaction.transaction_time,
            ),
        )

    def account_transaction_count(self, account_number: str) -> int:
        """Return the number of transactions involving an account."""
        return len(self.find_by_account(account_number))

    def customer_transaction_count(self, customer_number: str) -> int:
        """Return the number of transactions belonging to a customer."""
        return len(self.find_by_customer(customer_number))

    def account_transactions_by_type(
        self,
        account_number: str,
        transaction_type: TransactionType,
    ) -> list[Transaction]:
        """Return account transactions filtered by type."""
        return [
            transaction
            for transaction in self.find_by_account(account_number)
            if transaction.transaction_type == transaction_type
        ]

    def account_transactions_by_status(
        self,
        account_number: str,
        status: TransactionStatus,
    ) -> list[Transaction]:
        """Return account transactions filtered by status."""
        return [
            transaction
            for transaction in self.find_by_account(account_number)
            if transaction.transaction_status == status
        ]

    def add(self, entity: Transaction) -> Transaction:
        """Persist a transaction, rejecting duplicate transaction numbers."""
        if self.exists_transaction_number(entity.transaction_number):
            raise EntityAlreadyExistsError(
                f"Transaction already exists: {entity.transaction_number}"
            )
        super().add(entity)
        self.save()
        return entity

    def add_transaction(self, transaction: Transaction) -> Transaction:
        """Compatibility alias for persisting a transaction."""
        return self.add(transaction)

    def update(self, entity: Transaction) -> Transaction:
        """Transactions are immutable and cannot be updated."""
        raise UnsupportedOperationError(
            "Transactions are immutable and cannot be updated."
        )

    def delete(self, entity_id: str) -> None:
        """Transactions are immutable and cannot be deleted."""
        raise UnsupportedOperationError(
            "Transactions are immutable and cannot be deleted."
        )

    def __str__(self) -> str:
        """Return the transaction-specific repository summary."""
        return f"TransactionRepository(transactions={self.count})"

    def __repr__(self) -> str:
        """Return a transaction-specific developer representation."""
        return (
            f"TransactionRepository("
            f"entity_type={self.ENTITY_CLASS.__name__}, "
            f"count={self.count}, "
            f"file='{self.CSV_FILE}')"
        )
