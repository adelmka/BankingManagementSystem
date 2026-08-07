"""
===============================================================================
Banking Management System (BMS)

File        : transaction_repository.py
Description : Transaction Repository.

Author      : Adel Alawiyat / ChatGPT
Version     : 2.1.0
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
    EntityNotFoundError,
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

    # ------------------------------------------------------------------
    # Constructor
    # ------------------------------------------------------------------

    def __init__(self) -> None:
        super().__init__()

    # ------------------------------------------------------------------
    # Internal Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _normalize(value: str) -> str:
        """
        Normalize string values for lookups.
        """

        return value.strip().upper()

    # ------------------------------------------------------------------
    # Transaction Number
    # ------------------------------------------------------------------

    def find_by_transaction_number(
        self,
        transaction_number: str,
    ) -> Transaction | None:
        """
        Return the transaction having the specified transaction number.
        """

        transaction_number = self._normalize(
            transaction_number
        )

        return self.find_first(
            lambda transaction:
            self._normalize(
                transaction.transaction_number
            )
            == transaction_number
        )

    # ------------------------------------------------------------------

    def exists_transaction_number(
        self,
        transaction_number: str,
    ) -> bool:
        """
        Determine whether a transaction number exists.
        """

        return (
            self.find_by_transaction_number(
                transaction_number
            )
            is not None
        )

    # ------------------------------------------------------------------
    # Account Queries
    # ------------------------------------------------------------------

    def find_by_account(
        self,
        account_number: str,
    ) -> list[Transaction]:
        """
        Return all transactions belonging to an account.
        """

        account_number = self._normalize(
            account_number
        )

        return self.find_where(
            lambda transaction:
            self._normalize(
                transaction.account_number
            )
            == account_number
        )

    # ------------------------------------------------------------------

    def account_has_transactions(
        self,
        account_number: str,
    ) -> bool:
        """
        Determine whether an account has any transactions.
        """

        return (
            len(
                self.find_by_account(
                    account_number
                )
            )
            > 0
        )

# PART 2

    # ------------------------------------------------------------------
    # Customer Queries
    # ------------------------------------------------------------------

    def find_by_customer(
        self,
        customer_number: str,
    ) -> list[Transaction]:
        """
        Return all transactions belonging to the specified customer.
        """

        customer_number = self._normalize(
            customer_number
        )

        return self.find_where(
            lambda transaction:
            self._normalize(
                transaction.customer_number
            )
            == customer_number
        )

    # ------------------------------------------------------------------
    # Transaction Type
    # ------------------------------------------------------------------

    def find_by_type(
        self,
        transaction_type: TransactionType,
    ) -> list[Transaction]:
        """
        Return all transactions of the specified type.
        """

        return self.find_where(
            lambda transaction:
            transaction.transaction_type
            == transaction_type
        )

    # ------------------------------------------------------------------

    def deposits(
        self,
    ) -> list[Transaction]:
        """
        Return all deposit transactions.
        """

        return self.find_by_type(
            TransactionType.DEPOSIT
        )

    # ------------------------------------------------------------------

    def withdrawals(
        self,
    ) -> list[Transaction]:
        """
        Return all withdrawal transactions.
        """

        return self.find_by_type(
            TransactionType.WITHDRAWAL
        )

    # ------------------------------------------------------------------
    """
    def transfers(
        self,
    ) -> list[Transaction]:
       
        # Return all transfer transactions.
       

        return self.find_by_type(
            TransactionType.TRANSFER
        )
    """

    def transfers(self) -> list[Transaction]:
        return self.find_where(
            lambda transaction:
            transaction.transaction_type
            in (
                TransactionType.INTERNAL_TRANSFER,
                TransactionType.EXTERNAL_TRANSFER,
            )
        )


    # ------------------------------------------------------------------
    # Transaction Status
    # ------------------------------------------------------------------

    def find_by_status(
        self,
        transaction_status: TransactionStatus,
    ) -> list[Transaction]:
        """
        Return all transactions having the specified status.
        """

        return self.find_where(
            lambda transaction:
            transaction.transaction_status
            == transaction_status
        )

    # ------------------------------------------------------------------

    def pending_transactions(
        self,
    ) -> list[Transaction]:
        """
        Return all pending transactions.
        """

        return self.find_by_status(
            TransactionStatus.PENDING
        )

    # ------------------------------------------------------------------

    def completed_transactions(
        self,
    ) -> list[Transaction]:
        """
        Return all completed transactions.
        """

        return self.find_by_status(
            TransactionStatus.COMPLETED
        )

    # ------------------------------------------------------------------

    def failed_transactions(
        self,
    ) -> list[Transaction]:
        """
        Return all failed transactions.
        """

        return self.find_by_status(
            TransactionStatus.FAILED
        )

    # ------------------------------------------------------------------
    # Counts
    # ------------------------------------------------------------------

    def transaction_count(
        self,
    ) -> int:
        """
        Return the total number of transactions.
        """

        return self.count

    # ------------------------------------------------------------------

    def completed_transaction_count(
        self,
    ) -> int:
        """
        Return the number of completed transactions.
        """

        return len(
            self.completed_transactions()
        )

    # ------------------------------------------------------------------

    def pending_transaction_count(
        self,
    ) -> int:
        """
        Return the number of pending transactions.
        """

        return len(
            self.pending_transactions()
        )

    # ------------------------------------------------------------------

    def failed_transaction_count(
        self,
    ) -> int:
        """
        Return the number of failed transactions.
        """

        return len(
            self.failed_transactions()
        )

# Part 3



    # ------------------------------------------------------------------
    # Date Queries
    # ------------------------------------------------------------------

    def find_by_date(
        self,
        transaction_date: date,
    ) -> list[Transaction]:
        """
        Return all transactions posted on the specified date.
        """

        return self.find_where(
            lambda transaction:
            transaction.transaction_timestamp.date()
            == transaction_date
        )

    # ------------------------------------------------------------------

    def find_between_dates(
        self,
        start_date: date,
        end_date: date,
    ) -> list[Transaction]:
        """
        Return all transactions whose posting date falls within the
        specified date range.
        """

        return self.find_where(
            lambda transaction:
            start_date
            <= transaction.transaction_timestamp.date()
            <= end_date
        )

    # ------------------------------------------------------------------
    # Amount Queries
    # ------------------------------------------------------------------

    def find_by_amount_range(
        self,
        minimum: Decimal,
        maximum: Decimal,
    ) -> list[Transaction]:
        """
        Return all transactions whose amount falls within the specified
        range.
        """

        return self.find_where(
            lambda transaction:
            minimum
            <= transaction.amount.amount
            <= maximum
        )

    # ------------------------------------------------------------------
    # Chronological Queries
    # ------------------------------------------------------------------

    def transaction_history(
        self,
        account_number: str,
    ) -> list[Transaction]:
        """
        Return the complete transaction history for an account ordered
        chronologically.
        """

        return sorted(
            self.find_by_account(account_number),
            key=lambda transaction:
                transaction.transaction_timestamp
        )

    # ------------------------------------------------------------------

    def latest_transaction(
        self,
        account_number: str,
    ) -> Transaction | None:
        """
        Return the most recent transaction for an account.
        """

        history = self.transaction_history(
            account_number
        )

        return history[-1] if history else None

    # ------------------------------------------------------------------

    def oldest_transaction(
        self,
        account_number: str,
    ) -> Transaction | None:
        """
        Return the earliest transaction for an account.
        """

        history = self.transaction_history(
            account_number
        )

        return history[0] if history else None

    # ------------------------------------------------------------------
    # Daily Summary
    # ------------------------------------------------------------------

    def daily_transaction_count(
        self,
        transaction_date: date,
    ) -> int:
        """
        Return the number of transactions posted on a given date.
        """

        return len(
            self.find_by_date(
                transaction_date
            )
        )

    # ------------------------------------------------------------------

    def daily_transaction_total(
        self,
        transaction_date: date,
    ) -> Decimal:
        """
        Return the total value of all transactions posted on a given
        date.
        """

        transactions = self.find_by_date(
            transaction_date
        )

        return sum(
            (
                transaction.amount.amount
                for transaction in transactions
            ),
            Decimal("0.00"),
        )

# PART 4

    # ------------------------------------------------------------------
    # Account Summaries
    # ------------------------------------------------------------------

    def account_transaction_count(
        self,
        account_number: str,
    ) -> int:
        """
        Return the number of transactions for an account.
        """

        return len(
            self.find_by_account(
                account_number
            )
        )

    # ------------------------------------------------------------------

    def account_transactions_by_type(
        self,
        account_number: str,
        transaction_type: TransactionType,
    ) -> list[Transaction]:
        """
        Return all transactions of the specified type for an account.
        """

        return [
            transaction
            for transaction in self.find_by_account(
                account_number
            )
            if transaction.transaction_type
            == transaction_type
        ]

    # ------------------------------------------------------------------

    def account_transactions_by_status(
        self,
        account_number: str,
        transaction_status: TransactionStatus,
    ) -> list[Transaction]:
        """
        Return all transactions of the specified status for an account.
        """

        return [
            transaction
            for transaction in self.find_by_account(
                account_number
            )
            if transaction.transaction_status
            == transaction_status
        ]

    # ------------------------------------------------------------------
    # Customer Summaries
    # ------------------------------------------------------------------

    def customer_transaction_count(
        self,
        customer_number: str,
    ) -> int:
        """
        Return the number of transactions belonging to a customer.
        """

        return len(
            self.find_by_customer(
                customer_number
            )
        )

    # ------------------------------------------------------------------

    def customer_transactions_by_type(
        self,
        customer_number: str,
        transaction_type: TransactionType,
    ) -> list[Transaction]:
        """
        Return all customer transactions of the specified type.
        """

        return [
            transaction
            for transaction in self.find_by_customer(
                customer_number
            )
            if transaction.transaction_type
            == transaction_type
        ]

    # ------------------------------------------------------------------
    # Statistics
    # ------------------------------------------------------------------

    def statistics(self) -> dict[str, int]:
        """
        Return repository statistics.
        """

        return {
            "total_transactions":
                self.transaction_count(),

            "completed_transactions":
                self.completed_transaction_count(),

            "pending_transactions":
                self.pending_transaction_count(),

            "failed_transactions":
                self.failed_transaction_count(),

            "deposit_transactions":
                len(self.deposits()),

            "withdrawal_transactions":
                len(self.withdrawals()),

            "transfer_transactions":
                len(self.transfers()),
        }

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def validate_unique_transaction(
        self,
        transaction: Transaction,
    ) -> None:
        """
        Validate that the transaction number is unique.
        """

        if self.exists_transaction_number(
            transaction.transaction_number
        ):

            raise EntityAlreadyExistsError(
                "Transaction number already exists."
            )

    # ------------------------------------------------------------------

    def add_transaction(
        self,
        transaction: Transaction,
    ) -> None:
        """
        Validate and persist a transaction.
        """

        self.validate_unique_transaction(
            transaction
        )

        self.save_entity(
            transaction
        )

# PART 5

    # ------------------------------------------------------------------
    # Convenience Methods
    # ------------------------------------------------------------------

    def transaction_exists(
        self,
        transaction_number: str,
    ) -> bool:
        """
        Determine whether a transaction exists.
        """

        return self.exists_transaction_number(
            transaction_number
        )

    # ------------------------------------------------------------------

    def get_or_raise(
        self,
        transaction_number: str,
    ) -> Transaction:
        """
        Return the specified transaction.

        Raises
        ------
        EntityNotFoundError
            If the transaction does not exist.
        """

        transaction = self.find_by_transaction_number(
            transaction_number
        )

        if transaction is None:

            raise EntityNotFoundError(
                f"Transaction '{transaction_number}' was not found."
            )

        return transaction

    # ------------------------------------------------------------------
    # Immutable Repository Operations
    # ------------------------------------------------------------------

    def update(
        self,
        transaction: Transaction,
    ) -> None:
        """
        Transactions are immutable and cannot be updated.
        """

        raise UnsupportedOperationError(
            "Transactions cannot be updated."
        )

    # ------------------------------------------------------------------

    def remove(
        self,
        entity_id,
    ) -> bool:
        """
        Transactions cannot be removed.
        """

        raise UnsupportedOperationError(
            "Transactions cannot be deleted."
        )

    # ------------------------------------------------------------------

    def restore(
        self,
        entity_id,
    ) -> bool:
        """
        Transactions cannot be restored because they are never deleted.
        """

        raise UnsupportedOperationError(
            "Transactions cannot be restored."
        )

    # ------------------------------------------------------------------

    def purge_inactive(
        self,
    ) -> int:
        """
        Transactions cannot be purged.
        """

        raise UnsupportedOperationError(
            "Transactions cannot be purged."
        )

    # ------------------------------------------------------------------
    # Display
    # ------------------------------------------------------------------

    def __str__(self) -> str:
        """
        Human-readable representation.
        """

        return (
            f"TransactionRepository("
            f"transactions={self.count})"
        )

    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        """
        Developer-friendly representation.
        """

        return (
            f"TransactionRepository("
            f"count={self.count}, "
            f"file='{self.CSV_FILE}')"
        )


# ----------------------------------------------------------------------
# End of File
# ----------------------------------------------------------------------
