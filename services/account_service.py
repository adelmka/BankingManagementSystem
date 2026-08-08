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
            account.customer_id
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

    # ------------------------------------------------------------------
    # Transfers
    # ------------------------------------------------------------------

    def transfer(
        self,
        from_account_number: str,
        to_account_number: str,
        amount: Money,
        description: str = "Transfer",
    ) -> tuple[Account, Account]:
        """
        Transfer funds between two accounts.
        """

        if (
            from_account_number.strip().upper()
            == to_account_number.strip().upper()
        ):
            raise ValidationError(
                "Source and destination accounts must be different."
            )

        source = self.validate_account(
            from_account_number
        )

        destination = self.validate_account(
            to_account_number
        )

        self._before_operation(
            "transfer"
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

        return source, destination

    # ------------------------------------------------------------------
    # Balance
    # ------------------------------------------------------------------

    def balance(
        self,
        account_number: str,
    ) -> Money:
        """
        Return the current account balance.
        """

        return self.validate_account(
            account_number
        ).balance
