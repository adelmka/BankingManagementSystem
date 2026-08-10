"""
===============================================================================
Banking Management System (BMS)

File        : account_service.py
Description : Account Application Service.

===============================================================================
"""

from __future__ import annotations

from decimal import Decimal

from models.account import Account
from models.customer import Customer
from models.value_objects.money import Money
from models.transaction import Transaction

from repositories.account_repository import AccountRepository
from repositories.customer_repository import CustomerRepository
from repositories.transaction_repository import TransactionRepository

from services.base_service import BaseService

from exceptions import (
    EntityAlreadyExistsError,
    ValidationError,
)

from utils.constants import TransactionType
from utils.generators import IDGenerator


class AccountService(BaseService[Account]):
    """Application service responsible for account-related operations."""

    def __init__(
        self,
        account_repository: AccountRepository,
        customer_repository: CustomerRepository,
        transaction_repository: TransactionRepository,
    ) -> None:
        super().__init__(repository=account_repository)
        self._customer_repository = customer_repository
        self._transaction_repository = transaction_repository

    def get_account(self, account_number: str) -> Account:
        return self._repository.get_or_raise(account_number)

    def account_exists(self, account_number: str) -> bool:
        return self._repository.account_exists(account_number)

    def get_customer(self, customer_number: str) -> Customer:
        return self._customer_repository.get_or_raise(customer_number)

    def customer_is_eligible(self, customer_number: str) -> bool:
        return self.get_customer(customer_number).is_active

    def all_accounts(self) -> list[Account]:
        return list(self._repository)

    def open_account(
        self,
        account: Account,
        initial_deposit: Money | None = None,
    ) -> Account:
        self._before_operation("open_account")
        self._validate(account)

        if not self.customer_is_eligible(account.customer_id):
            raise ValidationError("Customer is not eligible to open an account.")

        if self.account_exists(account.account_number):
            raise EntityAlreadyExistsError("Account already exists.")

        with self._operation_scope():
            self._repository.add_account(account)
            if initial_deposit is not None and initial_deposit.amount > Decimal("0.00"):
                self.deposit(
                    account.account_number,
                    initial_deposit,
                    description="Initial Deposit",
                )

        self._after_operation("open_account")
        return account

    def validate_account(self, account_number: str) -> Account:
        account = self.get_account(account_number)
        if not account.is_active:
            raise ValidationError("Account is inactive.")
        return account

    def customer_accounts(self, customer_number: str) -> list[Account]:
        return self._repository.find_by_customer(customer_number)

    def customer_account_count(self, customer_number: str) -> int:
        return len(self.customer_accounts(customer_number))

    def customer_has_accounts(self, customer_number: str) -> bool:
        return self.customer_account_count(customer_number) > 0

    def _credit_account(self, account: Account, amount: Money) -> None:
        if amount.amount <= Decimal("0.00"):
            raise ValidationError("Credit amount must be greater than zero.")
        account.deposit(amount)
        self._repository.save_account(account)

    def _debit_account(self, account: Account, amount: Money) -> None:
        if amount.amount <= Decimal("0.00"):
            raise ValidationError("Debit amount must be greater than zero.")
        account.withdraw(amount)
        self._repository.save_account(account)

    def _record_account_transaction(
        self,
        account: Account,
        amount: Money,
        transaction_type: TransactionType,
        description: str,
    ) -> Transaction:
        """Persist the immutable transaction for a single-account operation."""
        if transaction_type == TransactionType.DEPOSIT:
            source_account = None
            destination_account = account.account_number
        elif transaction_type == TransactionType.WITHDRAWAL:
            source_account = account.account_number
            destination_account = None
        else:
            raise ValidationError("Unsupported account transaction type.")

        transaction = Transaction(
            transaction_number=IDGenerator.transaction_number(),
            transaction_type=transaction_type,
            amount=amount,
            source_account=source_account,
            destination_account=destination_account,
            initiated_by="SYSTEM",
            description=description or transaction_type.value,
        )
        self._transaction_repository.add_transaction(transaction)
        return transaction

    def deposit(
        self,
        account_number: str,
        amount: Money,
        description: str = "Deposit",
    ) -> Account:
        account = self.validate_account(account_number)
        self._before_operation("deposit")
        try:
            with self._operation_scope():
                self._credit_account(account, amount)
                self._record_account_transaction(
                    account,
                    amount,
                    TransactionType.DEPOSIT,
                    description,
                )
        except Exception as ex:
            self._operation_failed("deposit", ex)
            raise
        else:
            self._after_operation("deposit")
        return account

    def withdraw(
        self,
        account_number: str,
        amount: Money,
        description: str = "Withdrawal",
    ) -> Account:
        account = self.validate_account(account_number)
        self._before_operation("withdraw")
        try:
            with self._operation_scope():
                self._debit_account(account, amount)
                self._record_account_transaction(
                    account,
                    amount,
                    TransactionType.WITHDRAWAL,
                    description,
                )
        except Exception as ex:
            self._operation_failed("withdraw", ex)
            raise
        else:
            self._after_operation("withdraw")
        return account

    def _record_transfer_transaction(
        self,
        source: Account,
        destination: Account,
        amount: Money,
        description: str,
    ) -> Transaction:
        """Persist the single immutable transaction representing a transfer."""
        transaction = Transaction(
            transaction_number=IDGenerator.transaction_number(),
            transaction_type=TransactionType.INTERNAL_TRANSFER,
            amount=amount,
            source_account=source.account_number,
            destination_account=destination.account_number,
            initiated_by="SYSTEM",
            description=description or "Transfer",
        )
        self._transaction_repository.add_transaction(transaction)
        return transaction

    def transfer(
        self,
        from_account_number: str,
        to_account_number: str,
        amount: Money,
        description: str = "Transfer",
    ) -> tuple[Account, Account]:
        if from_account_number.strip().upper() == to_account_number.strip().upper():
            raise ValidationError("Source and destination accounts must be different.")

        source = self.validate_account(from_account_number)
        destination = self.validate_account(to_account_number)

        self._before_operation("transfer")
        try:
            with self._operation_scope():
                self._debit_account(source, amount)
                self._credit_account(destination, amount)
                self._record_transfer_transaction(
                    source,
                    destination,
                    amount,
                    description,
                )
        except Exception as ex:
            self._operation_failed("transfer", ex)
            raise
        else:
            self._after_operation("transfer")

        return source, destination

    def balance(self, account_number: str) -> Money:
        return self.validate_account(account_number).balance
