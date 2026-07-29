"""
===============================================================================
Banking Management System (BMS)

File        : transaction_service.py
Description : Transaction Application Service.

Author      : Adel Alawiyat / ChatGPT
Version     : 2.1.0
Python      : 3.13+

===============================================================================
"""

from __future__ import annotations

from datetime import date

from models.account import Account
from models.transaction import Transaction

from repositories.account_repository import (
    AccountRepository,
)

from repositories.transaction_repository import (
    TransactionRepository,
)

from services.base_service import BaseService

from decimal import Decimal
from models.value_objects.money import Money
from exceptions import PersistenceError

class TransactionService(
    BaseService[Transaction],
):
    """
    Application service responsible for transaction-related
    business operations.
    """

    # ------------------------------------------------------------------
    # Constructor
    # ------------------------------------------------------------------

    def __init__(
        self,
        transaction_repository: TransactionRepository,
        account_repository: AccountRepository,
    ) -> None:
        """
        Initialize the transaction service.
        """

        super().__init__(
            repository=transaction_repository
        )

        self._account_repository = (
            account_repository
        )

    # ------------------------------------------------------------------
    # Recording
    # ------------------------------------------------------------------

    def record_transaction(
        self,
        transaction: Transaction,
    ) -> Transaction:
        """
        Persist a completed transaction.
        """

        self._before_operation(
            "record_transaction"
        )

        self._validate(
            transaction
        )

        try:

            with self._operation_scope():

                self._repository.add_transaction(
                    transaction
                )

        except Exception as ex:

            self._operation_failed(
                "record_transaction",
                ex,
            )

            raise

        else:

            self._after_operation(
                "record_transaction"
            )

        return transaction

    # ------------------------------------------------------------------
    # Lookup
    # ------------------------------------------------------------------

    def get_transaction(
        self,
        transaction_number: str,
    ) -> Transaction:
        """
        Return a transaction or raise an exception.
        """

        return (
            self._repository
            .get_or_raise(
                transaction_number
            )
        )

    # ------------------------------------------------------------------

    def transaction_exists(
        self,
        transaction_number: str,
    ) -> bool:
        """
        Determine whether a transaction exists.
        """

        return (
            self._repository
            .transaction_exists(
                transaction_number
            )
        )

    # ------------------------------------------------------------------

    def all_transactions(
        self,
    ) -> list[Transaction]:
        """
        Return all recorded transactions.
        """

        return list(
            self._repository
        )

    # ------------------------------------------------------------------

    def account(
        self,
        account_number: str,
    ) -> Account:
        """
        Return an account or raise an exception.
        """

        return (
            self._account_repository
            .get_or_raise(
                account_number
            )
        )

# PART 2

    # ------------------------------------------------------------------
    # Search Operations
    # ------------------------------------------------------------------

    def account_transactions(
        self,
        account_number: str,
    ) -> list[Transaction]:
        """
        Return all transactions for an account.
        """

        self.account(
            account_number
        )

        return (
            self._repository
            .find_by_account(
                account_number
            )
        )

    # ------------------------------------------------------------------

    def customer_transactions(
        self,
        customer_number: str,
    ) -> list[Transaction]:
        """
        Return all transactions belonging to a customer.

        The repository resolves customer ownership through the
        associated accounts.
        """

        return (
            self._repository
            .find_by_customer(
                customer_number
            )
        )

    # ------------------------------------------------------------------

    def transactions_by_type(
        self,
        transaction_type,
    ) -> list[Transaction]:
        """
        Return transactions having the specified type.
        """

        return (
            self._repository
            .find_by_type(
                transaction_type
            )
        )

    # ------------------------------------------------------------------

    def transactions_between(
        self,
        start_date: date,
        end_date: date,
    ) -> list[Transaction]:
        """
        Return transactions within the specified date range.
        """

        return (
            self._repository
            .find_between_dates(
                start_date,
                end_date,
            )
        )

    # ------------------------------------------------------------------

    def recent_transactions(
        self,
        limit: int = 10,
    ) -> list[Transaction]:
        """
        Return the most recent transactions.
        """

        transactions = sorted(
            self.all_transactions(),
            key=lambda transaction: (
                transaction.transaction_date,
                transaction.transaction_time,
            ),
            reverse=True,
        )

        return transactions[:limit]

    # ------------------------------------------------------------------

    def transaction_count(
        self,
    ) -> int:
        """
        Return the total number of recorded transactions.
        """

        return self.entity_count

    # ------------------------------------------------------------------

    def has_transactions(
        self,
    ) -> bool:
        """
        Determine whether any transactions exist.
        """

        return (
            self.transaction_count()
            > 0
        )

# Part 3

    # ------------------------------------------------------------------
    # Reporting
    # ------------------------------------------------------------------

    def account_statement(
        self,
        account_number: str,
    ) -> list[dict[str, object]]:
        """
        Return a simplified account statement.
        """

        transactions = sorted(
            self.account_transactions(
                account_number
            ),
            key=lambda transaction: (
                transaction.transaction_date,
                transaction.transaction_time,
            ),
        )

        return [
            {
                "transaction_number":
                    transaction.transaction_number,

                "date":
                    transaction.transaction_date,

                "time":
                    transaction.transaction_time,

                "type":
                    transaction.transaction_type.value,

                "amount":
                    transaction.amount,

                "description":
                    transaction.description,
            }
            for transaction in transactions
        ]

    # ------------------------------------------------------------------

    def transaction_summary(
        self,
        transaction_number: str,
    ) -> dict[str, object]:
        """
        Return a business summary of a transaction.
        """

        transaction = self.get_transaction(
            transaction_number
        )

        return {
            "transaction_number":
                transaction.transaction_number,

            "account_number":
                transaction.account_number,

            "transaction_type":
                transaction.transaction_type.value,

            "amount":
                transaction.amount,

            "currency":
                transaction.amount.currency,

            "date":
                transaction.transaction_date,

            "time":
                transaction.transaction_time,

            "description":
                transaction.description,
        }

    # ------------------------------------------------------------------

    def transaction_listing(
        self,
    ) -> list[dict[str, object]]:
        """
        Return summaries for all transactions.
        """

        return [
            self.transaction_summary(
                transaction.transaction_number
            )
            for transaction in self.all_transactions()
        ]

    # ------------------------------------------------------------------
    # Statistics
    # ------------------------------------------------------------------

    def debit_total(
        self,
        account_number: str,
    ) -> Money:
        """
        Return the total debited from an account.
        """

        transactions = self.account_transactions(
            account_number
        )

        account = self.account(
            account_number
        )

        total = Money.zero(
            account.currency
        )

        for transaction in transactions:

            if transaction.transaction_type.is_debit:

                total += transaction.amount

        return total

    # ------------------------------------------------------------------

    def credit_total(
        self,
        account_number: str,
    ) -> Money:
        """
        Return the total credited to an account.
        """

        transactions = self.account_transactions(
            account_number
        )

        account = self.account(
            account_number
        )

        total = Money.zero(
            account.currency
        )

        for transaction in transactions:

            if transaction.transaction_type.is_credit:

                total += transaction.amount

        return total

# Part 4

    # ------------------------------------------------------------------
    # Statistics
    # ------------------------------------------------------------------

    def statistics(
        self,
    ) -> dict[str, object]:
        """
        Return transaction statistics.
        """

        return {
            "total_transactions":
                self.transaction_count(),
        }

    # ------------------------------------------------------------------

    def account_statistics(
        self,
        account_number: str,
    ) -> dict[str, object]:
        """
        Return statistics for a single account.
        """

        transactions = self.account_transactions(
            account_number
        )

        return {
            "account_number": account_number,
            "transaction_count": len(transactions),
            "total_debits": self.debit_total(account_number),
            "total_credits": self.credit_total(account_number),
        }

    # ------------------------------------------------------------------

    def average_transaction_amount(
        self,
        account_number: str,
    ) -> Money:
        """
        Return the average transaction amount for an account.
        """

        transactions = self.account_transactions(
            account_number
        )

        account = self.account(
            account_number
        )

        if not transactions:

            return Money.zero(
                account.currency
            )

        total = Money.zero(
            account.currency
        )

        for transaction in transactions:

            total += transaction.amount

        return Money(
            amount=(
                total.amount
                / Decimal(
                    len(transactions)
                )
            ),
            currency=account.currency,
        )

    # ------------------------------------------------------------------

    def largest_transaction(
        self,
        account_number: str,
    ) -> Transaction | None:
        """
        Return the largest transaction for an account.
        """

        transactions = self.account_transactions(
            account_number
        )

        if not transactions:

            return None

        return max(
            transactions,
            key=lambda transaction:
                transaction.amount.amount,
        )

    # ------------------------------------------------------------------

    def customer_statistics(
        self,
        customer_number: str,
    ) -> dict[str, object]:
        """
        Return transaction statistics for a customer.
        """

        transactions = self.customer_transactions(
            customer_number
        )

        return {
            "customer_number":
                customer_number,

            "transaction_count":
                len(transactions),
        }

    # ------------------------------------------------------------------

    def repository_statistics(
        self,
    ) -> dict[str, object]:
        """
        Return repository statistics.
        """

        return (
            self._repository.statistics()
        )

# Part 5

    # ------------------------------------------------------------------
    # Repository Operations
    # ------------------------------------------------------------------

    def refresh(
        self,
    ) -> None:
        """
        Reload transaction data from persistent storage.
        """

        self._refresh()

    # ------------------------------------------------------------------

    def save_changes(
        self,
    ) -> None:
        """
        Persist all pending transaction changes.
        """

        self._flush()

    # ------------------------------------------------------------------

    def validate_repository(
        self,
    ) -> bool:
        """
        Validate repository integrity.
        """

        return (
            self._repository.count
            == len(self._repository)
        )

    # ------------------------------------------------------------------

    def ensure_repository_is_valid(
        self,
    ) -> None:
        """
        Raise an exception if repository validation fails.
        """

        if not self.validate_repository():

            raise PersistenceError(
                "Transaction repository integrity validation failed."
            )

    # ------------------------------------------------------------------
    # Reporting Helpers
    # ------------------------------------------------------------------

    def transactions_on(
        self,
        transaction_date: date,
    ) -> list[Transaction]:
        """
        Return all transactions occurring on the specified date.
        """

        return [
            transaction
            for transaction in self.all_transactions()
            if transaction.transaction_date
            == transaction_date
        ]

    # ------------------------------------------------------------------

    def transactions_before(
        self,
        transaction_date: date,
    ) -> list[Transaction]:
        """
        Return all transactions before the specified date.
        """

        return [
            transaction
            for transaction in self.all_transactions()
            if transaction.transaction_date
            < transaction_date
        ]

    # ------------------------------------------------------------------

    def transactions_after(
        self,
        transaction_date: date,
    ) -> list[Transaction]:
        """
        Return all transactions after the specified date.
        """

        return [
            transaction
            for transaction in self.all_transactions()
            if transaction.transaction_date
            > transaction_date
        ]

    # ------------------------------------------------------------------
    # Utility Helpers
    # ------------------------------------------------------------------

    def latest_transaction(
        self,
        account_number: str,
    ) -> Transaction | None:
        """
        Return the most recent transaction for an account.
        """

        transactions = self.account_transactions(
            account_number
        )

        if not transactions:

            return None

        return max(
            transactions,
            key=lambda transaction: (
                transaction.transaction_date,
                transaction.transaction_time,
            ),
        )

    # ------------------------------------------------------------------

    def first_transaction(
        self,
        account_number: str,
    ) -> Transaction | None:
        """
        Return the first recorded transaction for an account.
        """

        transactions = self.account_transactions(
            account_number
        )

        if not transactions:

            return None

        return min(
            transactions,
            key=lambda transaction: (
                transaction.transaction_date,
                transaction.transaction_time,
            ),
        )

# Part 6

    # ------------------------------------------------------------------
    # Display
    # ------------------------------------------------------------------

    def __str__(
        self,
    ) -> str:
        """
        Return a human-readable representation.
        """

        return (
            f"{self.__class__.__name__}("
            f"transactions={self.transaction_count()})"
        )

    # ------------------------------------------------------------------

    def __repr__(
        self,
    ) -> str:
        """
        Return a developer-friendly representation.
        """

        return (
            f"{self.__class__.__name__}("
            f"repository="
            f"{self._repository.__class__.__name__}, "
            f"transactions={self.transaction_count()})"
        )


# ----------------------------------------------------------------------
# End of File
# ----------------------------------------------------------------------
