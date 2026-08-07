"""
===============================================================================
Banking Management System (BMS)

File        : account_service.py
Description : Account Application Service.

Author      : Adel Alawiyat / ChatGPT
Version     : 2.1.0
Python      : 3.13+

===============================================================================
"""

from __future__ import annotations

from decimal import Decimal

from models.account import Account
from models.customer import Customer
from models.value_objects.money import Money
from models.transaction import Transaction

from repositories.account_repository import (
    AccountRepository,
)
from repositories.customer_repository import (
    CustomerRepository,
)
from repositories.transaction_repository import (
    TransactionRepository,
)

from services.base_service import BaseService

from exceptions import (
    EntityAlreadyExistsError,
    ValidationError,
)


class AccountService(
    BaseService[Account],
):
    """
    Application service responsible for account-related business
    operations.
    """

    # ------------------------------------------------------------------
    # Constructor
    # ------------------------------------------------------------------

    def __init__(
        self,
        account_repository: AccountRepository,
        customer_repository: CustomerRepository,
        transaction_repository: TransactionRepository,
    ) -> None:
        """
        Initialize the account service.
        """

        super().__init__(
            repository=account_repository
        )

        self._customer_repository = (
            customer_repository
        )

        self._transaction_repository = (
            transaction_repository
        )

    # ------------------------------------------------------------------
    # Lookup
    # ------------------------------------------------------------------

    def get_account(
        self,
        account_number: str,
    ) -> Account:
        """
        Return an account or raise an exception.
        """

        return (
            self._repository
            .get_or_raise(
                account_number
            )
        )

    # ------------------------------------------------------------------

    def account_exists(
        self,
        account_number: str,
    ) -> bool:
        """
        Determine whether an account exists.
        """

        return (
            self._repository
            .account_exists(
                account_number
            )
        )

    # ------------------------------------------------------------------

    def get_customer(
        self,
        customer_number: str,
    ) -> Customer:
        """
        Return a customer or raise an exception.
        """

        return (
            self._customer_repository
            .get_or_raise(
                customer_number
            )
        )

    # ------------------------------------------------------------------

    def customer_is_eligible(
        self,
        customer_number: str,
    ) -> bool:
        """
        Determine whether the customer may own accounts.
        """

        customer = self.get_customer(
            customer_number
        )

        return (
            customer.is_active
            and not customer.is_deleted
        )

    # ------------------------------------------------------------------

    def all_accounts(
        self,
    ) -> list[Account]:
        """
        Return all active accounts.
        """

        return list(
            self._repository
        )
# PART 2

    # ------------------------------------------------------------------
    # Account Opening
    # ------------------------------------------------------------------

    def open_account(
        self,
        account: Account,
        initial_deposit: Money | None = None,
    ) -> Account:
        """
        Open a new bank account.

        Optionally perform an initial deposit after the account has
        been successfully created.
        """

        self._before_operation(
            "open_account"
        )

        self._validate(
            account
        )

        if not self.customer_is_eligible(
            account.customer_number
        ):
            raise ValidationError(
                "Customer is not eligible to open an account."
            )

        if self.account_exists(
            account.account_number
        ):
            raise EntityAlreadyExistsError(
                "Account already exists."
            )

        with self._operation_scope():

            self._repository.add_account(
                account
            )

            if (
                initial_deposit is not None
                and initial_deposit.amount > Decimal("0.00")
            ):

                self.deposit(
                    account.account_number,
                    initial_deposit,
                    description="Initial Deposit",
                )

        self._after_operation(
            "open_account"
        )

        return account

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def validate_account(
        self,
        account_number: str,
    ) -> Account:
        """
        Validate that an account exists and is active.
        """

        account = self.get_account(
            account_number
        )

        if not account.is_active:

            raise ValidationError(
                "Account is inactive."
            )

        if account.is_deleted:

            raise ValidationError(
                "Account has been closed."
            )

        return account

    # ------------------------------------------------------------------

    def customer_accounts(
        self,
        customer_number: str,
    ) -> list[Account]:
        """
        Return all accounts owned by a customer.
        """

        return (
            self._repository
            .find_by_customer(
                customer_number
            )
        )

    # ------------------------------------------------------------------

    def customer_account_count(
        self,
        customer_number: str,
    ) -> int:
        """
        Return the number of accounts owned by a customer.
        """

        return len(
            self.customer_accounts(
                customer_number
            )
        )

    # ------------------------------------------------------------------

    def customer_has_accounts(
        self,
        customer_number: str,
    ) -> bool:
        """
        Determine whether a customer owns any accounts.
        """

        return (
            self.customer_account_count(
                customer_number
            )
            > 0
        )

# Part 3

    # ------------------------------------------------------------------
    # Internal Balance Operations
    # ------------------------------------------------------------------

    def _credit_account(
        self,
        account: Account,
        amount: Money,
    ) -> None:
        """
        Credit an account balance.

        Internal helper used by business operations.
        """

        if amount.amount <= Decimal("0.00"):

            raise ValidationError(
                "Credit amount must be greater than zero."
            )

        account.deposit(
            amount
        )

        self._repository.save_account(
            account
        )

    # ------------------------------------------------------------------

    def _debit_account(
        self,
        account: Account,
        amount: Money,
    ) -> None:
        """
        Debit an account balance.

        Internal helper used by business operations.
        """

        if amount.amount <= Decimal("0.00"):

            raise ValidationError(
                "Debit amount must be greater than zero."
            )

        account.withdraw(
            amount
        )

        self._repository.save_account(
            account
        )

    # ------------------------------------------------------------------
    # Deposits
    # ------------------------------------------------------------------

    def deposit(
        self,
        account_number: str,
        amount: Money,
        description: str = "Deposit",
    ) -> Account:
        """
        Deposit funds into an account.
        """

        account = self.validate_account(
            account_number
        )

        self._before_operation(
            "deposit"
        )

        try:

            with self._operation_scope():

                self._credit_account(
                    account,
                    amount,
                )

                # Transaction creation will be delegated to
                # TransactionService in Version 2.0.
                # For Version 1.0, create and persist the
                # Transaction here.

        except Exception as ex:

            self._operation_failed(
                "deposit",
                ex,
            )

            raise

        else:

            self._after_operation(
                "deposit"
            )

        return account

    # ------------------------------------------------------------------
    # Withdrawals
    # ------------------------------------------------------------------

    def withdraw(
        self,
        account_number: str,
        amount: Money,
        description: str = "Withdrawal",
    ) -> Account:
        """
        Withdraw funds from an account.
        """

        account = self.validate_account(
            account_number
        )

        self._before_operation(
            "withdraw"
        )

        try:

            with self._operation_scope():

                self._debit_account(
                    account,
                    amount,
                )

                # Transaction creation follows the same
                # pattern as deposits.

        except Exception as ex:

            self._operation_failed(
                "withdraw",
                ex,
            )

            raise

        else:

            self._after_operation(
                "withdraw"
            )

        return account

# PART 4

    # ------------------------------------------------------------------
    # Transfers
    # ------------------------------------------------------------------

    def transfer(
        self,
        source_account_number: str,
        destination_account_number: str,
        amount: Money,
        description: str = "Transfer",
    ) -> tuple[Account, Account]:
        """
        Transfer funds between two accounts.
        """

        self._before_operation(
            "transfer"
        )

        source = self.validate_account(
            source_account_number
        )

        destination = self.validate_account(
            destination_account_number
        )

        if (
            source.account_number
            == destination.account_number
        ):

            raise ValidationError(
                "Source and destination accounts must be different."
            )

        if amount.amount <= Decimal("0.00"):

            raise ValidationError(
                "Transfer amount must be greater than zero."
            )

        if source.currency != destination.currency:

            raise ValidationError(
                "Cross-currency transfers are not supported."
            )

        try:

            with self._operation_scope():

                self._debit_account(
                    source,
                    amount,
                )

                self._credit_account(
                    destination,
                    amount,
                )

                self._repository.save_account(
                    source
                )

                self._repository.save_account(
                    destination
                )

                # Version 1.0:
                # Create and persist a transfer transaction.

                # Version 2.0:
                # Delegate transaction creation to
                # TransactionService.

        except Exception as ex:

            self._operation_failed(
                "transfer",
                ex,
            )

            raise

        else:

            self._after_operation(
                "transfer"
            )

        return (
            source,
            destination,
        )

    # ------------------------------------------------------------------
    # Balance Queries
    # ------------------------------------------------------------------

    def balance(
        self,
        account_number: str,
    ) -> Money:
        """
        Return the current account balance.
        """

        account = self.validate_account(
            account_number
        )

        return account.balance

    # ------------------------------------------------------------------

    def available_balance(
        self,
        account_number: str,
    ) -> Money:
        """
        Return the available balance.

        Current implementation returns the ledger balance.
        Future versions may consider holds, pending
        transactions, and reserved funds.
        """

        account = self.validate_account(
            account_number
        )

        return account.balance

    # ------------------------------------------------------------------

    def has_sufficient_funds(
        self,
        account_number: str,
        amount: Money,
    ) -> bool:
        """
        Determine whether the account has sufficient funds.
        """

        account = self.validate_account(
            account_number
        )

        return (
            account.balance.amount
            >= amount.amount
        )

# PART 5

    # ------------------------------------------------------------------
    # Account Lifecycle
    # ------------------------------------------------------------------

    def close_account(
        self,
        account_number: str,
    ) -> Account:
        """
        Close an account.

        The account must have a zero balance before it may be closed.
        """

        account = self.validate_account(
            account_number
        )

        if account.balance.amount != Decimal("0.00"):

            raise ValidationError(
                "Account balance must be zero before closing."
            )

        self._before_operation(
            "close_account"
        )

        try:

            with self._operation_scope():

                account.close()

                self._repository.save_account(
                    account
                )

        except Exception as ex:

            self._operation_failed(
                "close_account",
                ex,
            )

            raise

        else:

            self._after_operation(
                "close_account"
            )

        return account

    # ------------------------------------------------------------------

    def freeze_account(
        self,
        account_number: str,
    ) -> Account:
        """
        Freeze an account.
        """

        account = self.validate_account(
            account_number
        )

        account.freeze()

        self._repository.save_account(
            account
        )

        return account

    # ------------------------------------------------------------------

    def unfreeze_account(
        self,
        account_number: str,
    ) -> Account:
        """
        Unfreeze an account.
        """

        account = self.get_account(
            account_number
        )

        account.unfreeze()

        self._repository.save_account(
            account
        )

        return account

    # ------------------------------------------------------------------
    # Customer Queries
    # ------------------------------------------------------------------

    def accounts_for_customer(
        self,
        customer_number: str,
    ) -> list[Account]:
        """
        Return all accounts belonging to a customer.
        """

        return (
            self._repository.find_by_customer(
                customer_number
            )
        )

    # ------------------------------------------------------------------

    def active_accounts(
        self,
    ) -> list[Account]:
        """
        Return all active accounts.
        """

        return (
            self._repository.find_active_accounts()
        )

    # ------------------------------------------------------------------

    def inactive_accounts(
        self,
    ) -> list[Account]:
        """
        Return all inactive accounts.
        """

        return (
            self._repository.find_inactive_accounts()
        )

    # ------------------------------------------------------------------
    # Account Summary
    # ------------------------------------------------------------------

    def account_summary(
        self,
        account_number: str,
    ) -> dict[str, object]:
        """
        Return a business summary for an account.
        """

        account = self.get_account(
            account_number
        )

        return {
            "account_number": account.account_number,
            "customer_number": account.customer_number,
            "account_type": account.account_type.value,
            "currency": account.currency,
            "balance": account.balance,
            "active": account.is_active,
            "frozen": account.is_frozen,
            "closed": account.is_deleted,
            "created_on": account.created_on,
        }

# PART 6

    # ------------------------------------------------------------------
    # Statistics
    # ------------------------------------------------------------------

    def account_count(
        self,
    ) -> int:
        """
        Return the total number of accounts.
        """

        return self.entity_count

    # ------------------------------------------------------------------

    def active_account_count(
        self,
    ) -> int:
        """
        Return the number of active accounts.
        """

        return len(
            self.active_accounts()
        )

    # ------------------------------------------------------------------

    def inactive_account_count(
        self,
    ) -> int:
        """
        Return the number of inactive accounts.
        """

        return len(
            self.inactive_accounts()
        )

    # ------------------------------------------------------------------

    def total_balance(
        self,
        currency: str | None = None,
    ) -> Money:
        """
        Return the aggregate balance of all active accounts.

        When a currency is supplied, only matching accounts are included.
        """

        total = Money.zero(
            currency or "USD"
        )

        for account in self.active_accounts():

            if (
                currency is not None
                and account.currency != currency
            ):
                continue

            total += account.balance

        return total

    # ------------------------------------------------------------------

    def average_balance(
        self,
        currency: str | None = None,
    ) -> Money:
        """
        Return the average balance of active accounts.
        """

        accounts = [
            account
            for account in self.active_accounts()
            if currency is None
            or account.currency == currency
        ]

        if not accounts:

            return Money.zero(
                currency or "USD"
            )

        total = self.total_balance(
            currency
        )

        return Money(
            amount=(
                total.amount
                / Decimal(
                    len(accounts)
                )
            ),
            currency=total.currency,
        )

    # ------------------------------------------------------------------

    def statistics(
        self,
    ) -> dict[str, object]:
        """
        Return account statistics.
        """

        return {
            "total_accounts":
                self.account_count(),

            "active_accounts":
                self.active_account_count(),

            "inactive_accounts":
                self.inactive_account_count(),
        }

    # ------------------------------------------------------------------
    # Convenience Operations
    # ------------------------------------------------------------------

    def has_accounts(
        self,
    ) -> bool:
        """
        Determine whether any accounts exist.
        """

        return (
            self.account_count()
            > 0
        )

    # ------------------------------------------------------------------

    def customer_total_balance(
        self,
        customer_number: str,
    ) -> Money:
        """
        Return the customer's aggregate balance.

        All customer accounts must use the same currency.
        """

        accounts = self.accounts_for_customer(
            customer_number
        )

        if not accounts:

            return Money.zero("USD")

        total = Money.zero(
            accounts[0].currency
        )

        for account in accounts:

            total += account.balance

        return total

# Part 7

    # ------------------------------------------------------------------
    # Repository Operations
    # ------------------------------------------------------------------

    def refresh(
        self,
    ) -> None:
        """
        Reload account data from persistent storage.
        """

        self._refresh()

    # ------------------------------------------------------------------

    def save_changes(
        self,
    ) -> None:
        """
        Persist pending repository changes.
        """

        self._flush()

    # ------------------------------------------------------------------

    def repository_statistics(
        self,
    ) -> dict[str, object]:
        """
        Return repository statistics.
        """

        return self._repository.statistics()

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
        Raise an exception if the repository is inconsistent.
        """

        if not self.validate_repository():

            raise PersistenceError(
                "Account repository integrity validation failed."
            )

    # ------------------------------------------------------------------
    # Reporting Helpers
    # ------------------------------------------------------------------

    def account_listing(
        self,
    ) -> list[dict[str, object]]:
        """
        Return a simplified listing of all accounts.
        """

        return [
            self.account_summary(
                account.account_number
            )
            for account in self.all_accounts()
        ]

    # ------------------------------------------------------------------

    def customer_account_listing(
        self,
        customer_number: str,
    ) -> list[dict[str, object]]:
        """
        Return summaries for every account owned by a customer.
        """

        return [
            self.account_summary(
                account.account_number
            )
            for account in self.accounts_for_customer(
                customer_number
            )
        ]

    # ------------------------------------------------------------------
    # Utility Helpers
    # ------------------------------------------------------------------

    def is_account_active(
        self,
        account_number: str,
    ) -> bool:
        """
        Determine whether an account is active.
        """

        return self.validate_account(
            account_number
        ).is_active

    # ------------------------------------------------------------------

    def is_account_frozen(
        self,
        account_number: str,
    ) -> bool:
        """
        Determine whether an account is frozen.
        """

        return self.get_account(
            account_number
        ).is_frozen

    # ------------------------------------------------------------------

    def is_account_closed(
        self,
        account_number: str,
    ) -> bool:
        """
        Determine whether an account is closed.
        """

        return self.get_account(
            account_number
        ).is_deleted

# Part 8

    # ------------------------------------------------------------------
    # Display
    # ------------------------------------------------------------------

    def __str__(
        self,
    ) -> str:
        """
        Return a human-readable representation of the service.
        """

        return (
            f"{self.__class__.__name__}("
            f"accounts={self.account_count()})"
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
            f"accounts={self.account_count()})"
        )


# ----------------------------------------------------------------------
# End of File
# ----------------------------------------------------------------------
