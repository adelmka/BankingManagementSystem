"""
===============================================================================
Banking Management System (BMS)

File        : transaction_service.py
Description : Transaction Application Service.

===============================================================================
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from models.account import Account
from models.transaction import Transaction
from models.value_objects.money import Money

from repositories.account_repository import AccountRepository
from repositories.transaction_repository import TransactionRepository

from services.base_service import BaseService
from exceptions import PersistenceError


class TransactionService(BaseService[Transaction]):
    """Application service responsible for transaction-related operations."""

    def __init__(
        self,
        transaction_repository: TransactionRepository,
        account_repository: AccountRepository,
    ) -> None:
        super().__init__(repository=transaction_repository)
        self._account_repository = account_repository

    def record_transaction(self, transaction: Transaction) -> Transaction:
        self._before_operation("record_transaction")
        self._validate(transaction)
        try:
            with self._operation_scope():
                self._repository.add_transaction(transaction)
        except Exception as ex:
            self._operation_failed("record_transaction", ex)
            raise
        else:
            self._after_operation("record_transaction")
        return transaction

    def get_transaction(self, transaction_number: str) -> Transaction:
        return self._repository.get_or_raise(transaction_number)

    def transaction_exists(self, transaction_number: str) -> bool:
        return self._repository.transaction_exists(transaction_number)

    def all_transactions(self) -> list[Transaction]:
        return list(self._repository)

    def account(self, account_number: str) -> Account:
        return self._account_repository.get_or_raise(account_number)

    def account_transactions(self, account_number: str) -> list[Transaction]:
        """
        Return transactions that affect the specified account.

        Transfers contain both source_account and destination_account,
        so both sides of an internal transfer must appear in either
        account's transaction history.
        """
        self.account(account_number)
        normalized = account_number.strip().upper()

        return [
            transaction
            for transaction in self.all_transactions()
            if transaction.source_account.strip().upper() == normalized
            or transaction.destination_account.strip().upper() == normalized
        ]

    def customer_transactions(self, customer_number: str) -> list[Transaction]:
        return self._repository.find_by_customer(customer_number)

    def transactions_by_type(self, transaction_type) -> list[Transaction]:
        return self._repository.find_by_type(transaction_type)

    def transactions_between(self, start_date: date, end_date: date) -> list[Transaction]:
        return self._repository.find_between_dates(start_date, end_date)

    def recent_transactions(self, limit: int = 10) -> list[Transaction]:
        transactions = sorted(
            self.all_transactions(),
            key=lambda transaction: (
                transaction.transaction_date,
                transaction.transaction_time,
            ),
            reverse=True,
        )
        return transactions[:limit]

    def transaction_count(self) -> int:
        return self.entity_count

    def has_transactions(self) -> bool:
        return self.transaction_count() > 0

    def account_statement(self, account_number: str) -> list[dict[str, object]]:
        transactions = sorted(
            self.account_transactions(account_number),
            key=lambda transaction: (
                transaction.transaction_date,
                transaction.transaction_time,
            ),
        )
        return [
            {
                "transaction_number": transaction.transaction_number,
                "date": transaction.transaction_date,
                "time": transaction.transaction_time,
                "type": transaction.transaction_type.value,
                "amount": transaction.amount,
                "description": transaction.description,
            }
            for transaction in transactions
        ]

    def transaction_summary(self, transaction_number: str) -> dict[str, object]:
        transaction = self.get_transaction(transaction_number)
        return {
            "transaction_number": transaction.transaction_number,
            "account_number": transaction.source_account,
            "transaction_type": transaction.transaction_type.value,
            "amount": transaction.amount,
            "currency": transaction.amount.currency,
            "date": transaction.transaction_date,
            "time": transaction.transaction_time,
            "description": transaction.description,
        }

    def transaction_listing(self) -> list[dict[str, object]]:
        return [
            self.transaction_summary(transaction.transaction_number)
            for transaction in self.all_transactions()
        ]

    def debit_total(self, account_number: str) -> Money:
        transactions = self.account_transactions(account_number)
        account = self.account(account_number)
        total = Money.zero(account.currency)
        for transaction in transactions:
            if transaction.transaction_type.is_debit:
                total += transaction.amount
        return total

    def credit_total(self, account_number: str) -> Money:
        transactions = self.account_transactions(account_number)
        account = self.account(account_number)
        total = Money.zero(account.currency)
        for transaction in transactions:
            if transaction.transaction_type.is_credit:
                total += transaction.amount
        return total

    def statistics(self) -> dict[str, object]:
        return {"total_transactions": self.transaction_count()}

    def account_statistics(self, account_number: str) -> dict[str, object]:
        transactions = self.account_transactions(account_number)
        return {
            "account_number": account_number,
            "transaction_count": len(transactions),
            "total_debits": self.debit_total(account_number),
            "total_credits": self.credit_total(account_number),
        }

    def average_transaction_amount(self, account_number: str) -> Money:
        transactions = self.account_transactions(account_number)
        account = self.account(account_number)
        if not transactions:
            return Money.zero(account.currency)
        total = Money.zero(account.currency)
        for transaction in transactions:
            total += transaction.amount
        return Money(
            amount=total.amount / Decimal(len(transactions)),
            currency=account.currency,
        )

    def largest_transaction(self, account_number: str) -> Transaction | None:
        transactions = self.account_transactions(account_number)
        if not transactions:
            return None
        return max(transactions, key=lambda transaction: transaction.amount.amount)

    def customer_statistics(self, customer_number: str) -> dict[str, object]:
        transactions = self.customer_transactions(customer_number)
        return {
            "customer_number": customer_number,
            "transaction_count": len(transactions),
        }

    def repository_statistics(self) -> dict[str, object]:
        return self._repository.statistics()

    def refresh(self) -> None:
        self._refresh()

    def save_changes(self) -> None:
        self._flush()

    def validate_repository(self) -> bool:
        return self._repository.count == len(self._repository)

    def ensure_repository_is_valid(self) -> None:
        if not self.validate_repository():
            raise PersistenceError("Transaction repository integrity validation failed.")

    def transactions_on(self, transaction_date: date) -> list[Transaction]:
        return [
            transaction
            for transaction in self.all_transactions()
            if transaction.transaction_date == transaction_date
        ]

    def transactions_before(self, transaction_date: date) -> list[Transaction]:
        return [
            transaction
            for transaction in self.all_transactions()
            if transaction.transaction_date < transaction_date
        ]

    def transactions_after(self, transaction_date: date) -> list[Transaction]:
        return [
            transaction
            for transaction in self.all_transactions()
            if transaction.transaction_date > transaction_date
        ]

    def latest_transaction(self, account_number: str) -> Transaction | None:
        transactions = self.account_transactions(account_number)
        if not transactions:
            return None
        return max(
            transactions,
            key=lambda transaction: (
                transaction.transaction_date,
                transaction.transaction_time,
            ),
        )

    def first_transaction(self, account_number: str) -> Transaction | None:
        transactions = self.account_transactions(account_number)
        if not transactions:
            return None
        return min(
            transactions,
            key=lambda transaction: (
                transaction.transaction_date,
                transaction.transaction_time,
            ),
        )

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(transactions={self.transaction_count()})"

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"repository={self._repository.__class__.__name__}, "
            f"transactions={self.transaction_count()})"
        )
