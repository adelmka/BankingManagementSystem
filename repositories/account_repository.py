"""
===============================================================================
Banking Management System (BMS)

File        : account_repository.py
Description : Account Repository.

Author      : Adel Alawiyat / ChatGPT
Version     : 2.1.0
Python      : 3.13+

===============================================================================
"""

from __future__ import annotations

from pathlib import Path

import config

from models.account import Account

from repositories.base_repository import BaseRepository

from exceptions import (
    EntityAlreadyExistsError,
    EntityNotFoundError,
)

from models.current_account import CurrentAccount
from models.savings_account import SavingsAccount
from models.time_deposit_account import TimeDepositAccount

# from utils.constants import AccountType
from utils.constants import (
    AccountStatus,
    AccountType,
    Gender,
)

import csv

from decimal import Decimal
from datetime import date

class AccountRepository(
    BaseRepository[Account],
):
    """
    Repository responsible for Account persistence and retrieval.
    """

    ENTITY_CLASS = Account

    CSV_FILE: Path = config.ACCOUNTS_FILE

    # ------------------------------------------------------------------
    # Constructor
    # ------------------------------------------------------------------

    def __init__(self) -> None:
        """
        Initialize the account repository.
        """

        super().__init__()

    # ------------------------------------------------------------------
    # Internal Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _normalize(value: str) -> str:
        """
        Normalize string values used in repository lookups.
        """

        return value.strip().upper()

    # ------------------------------------------------------------------
    # Account Number
    # ------------------------------------------------------------------

    def find_by_account_number(
        self,
        account_number: str,
    ) -> Account | None:
        """
        Return the account with the specified account number.
        """

        account_number = self._normalize(
            account_number
        )

        return self.find_first(
            lambda account:
            self._normalize(
                account.account_number
            )
            == account_number
        )

    # ------------------------------------------------------------------

    def exists_account_number(
        self,
        account_number: str,
    ) -> bool:
        """
        Determine whether an account number already exists.
        """

        return (
            self.find_by_account_number(
                account_number
            )
            is not None
        )

    # ------------------------------------------------------------------
    # Customer
    # ------------------------------------------------------------------

    def find_by_customer(
        self,
        customer_id: str,
    ) -> list[Account]:
        """
        Return all accounts belonging to the specified customer.
        """

        customer_id = self._normalize(
            customer_id
        )

        return self.find_where(
            lambda account:
            self._normalize(
                account.customer_id
            )
            == customer_id
        )

    # ------------------------------------------------------------------

    def customer_has_accounts(
        self,
        customer_id: str,
    ) -> bool:
        """
        Determine whether the customer owns any accounts.
        """

        return (
            len(
                self.find_by_customer(
                    customer_id
                )
            )
            > 0
        )

    # PART 2

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def load(self) -> None:
        """
        Load all accounts from persistent storage.

        Because Account is abstract, this method performs polymorphic
        deserialization based on the persisted account type.
        """

        self.clear_cache()

        if (
            not self.CSV_FILE.exists()
            or self.CSV_FILE.stat().st_size == 0
        ):
            return

        with self.CSV_FILE.open(
            mode="r",
            newline="",
            encoding="utf-8",
        ) as csv_file:

            reader = csv.DictReader(csv_file)

            for row in reader:

                account_type = AccountType(
                    row["account_type"]
                )

                if account_type == AccountType.SAVINGS:

                    account = (
                        SavingsAccount.from_dict(
                            row
                        )
                    )

                elif account_type == AccountType.CURRENT:

                    account = (
                        CurrentAccount.from_dict(
                            row
                        )
                    )

                elif (
                    account_type
                    == AccountType.TIME_DEPOSIT
                ):

                    account = (
                        TimeDepositAccount.from_dict(
                            row
                        )
                    )

                else:

                    raise ValueError(
                        "Unsupported account type: "
                        f"{account_type}"
                    )

                self._entities[
                    account.entity_id
                ] = account

    # ------------------------------------------------------------------
    # Account Type
    # ------------------------------------------------------------------

    def find_by_account_type(
        self,
        account_type: AccountType,
    ) -> list[Account]:
        """
        Return all accounts of the specified type.
        """

        return self.find_where(
            lambda account:
            account.account_type == account_type
        )

    # ------------------------------------------------------------------

    def savings_accounts(
        self,
    ) -> list[Account]:
        """
        Return all savings accounts.
        """

        return self.find_by_account_type(
            AccountType.SAVINGS
        )

    # ------------------------------------------------------------------

    def current_accounts(
        self,
    ) -> list[Account]:
        """
        Return all current accounts.
        """

        return self.find_by_account_type(
            AccountType.CURRENT
        )

    # ------------------------------------------------------------------

    def time_deposit_accounts(
        self,
    ) -> list[Account]:
        """
        Return all time deposit accounts.
        """

        return self.find_by_account_type(
            AccountType.TIME_DEPOSIT
        )

    # ------------------------------------------------------------------
    # Currency
    # ------------------------------------------------------------------

    def find_by_currency(
        self,
        currency: str,
    ) -> list[Account]:
        """
        Return all accounts using the specified currency.
        """

        currency = self._normalize(currency)

        return self.find_where(
            lambda account:
            self._normalize(
                account.currency
            )
            == currency
        )

# PART 3

    # ------------------------------------------------------------------
    # Account Status
    # ------------------------------------------------------------------

    def find_by_status(
        self,
        account_status: AccountStatus,
    ) -> list[Account]:
        """
        Return all accounts having the specified status.
        """

        return self.find_where(
            lambda account:
            account.status == account_status
        )

    # ------------------------------------------------------------------

    def find_active_accounts(
        self,
    ) -> list[Account]:
        """
        Return all active accounts.
        """

        return self.find_by_status(
            AccountStatus.ACTIVE
        )

    # ------------------------------------------------------------------

    def find_inactive_accounts(
        self,
    ) -> list[Account]:
        """
        Return all inactive accounts.
        """

        return self.find_where(
            lambda account:
            not account.is_active,
            active_only=False,
        )

    # ------------------------------------------------------------------

    def find_frozen_accounts(
        self,
    ) -> list[Account]:
        """
        Return all frozen accounts.
        """

        return self.find_by_status(
            AccountStatus.FROZEN
        )

    # ------------------------------------------------------------------

    def find_closed_accounts(
        self,
    ) -> list[Account]:
        """
        Return all closed accounts.
        """

        return self.find_by_status(
            AccountStatus.CLOSED
        )

    # ------------------------------------------------------------------

    def find_dormant_accounts(
        self,
    ) -> list[Account]:
        """
        Return all dormant accounts.
        """

        return self.find_by_status(
            AccountStatus.DORMANT
        )

    # ------------------------------------------------------------------
    # Balance Queries
    # ------------------------------------------------------------------

    def find_negative_balance_accounts(
        self,
    ) -> list[Account]:
        """
        Return all accounts with a negative balance.
        """

        return self.find_where(
            lambda account:
            account.balance.amount < 0
        )

    # ------------------------------------------------------------------

    def find_zero_balance_accounts(
        self,
    ) -> list[Account]:
        """
        Return all accounts with a zero balance.
        """

        return self.find_where(
            lambda account:
            account.balance.amount == 0
        )

    # ------------------------------------------------------------------

    def find_positive_balance_accounts(
        self,
    ) -> list[Account]:
        """
        Return all accounts with a positive balance.
        """

        return self.find_where(
            lambda account:
            account.balance.amount > 0
        )

    # ------------------------------------------------------------------

    def find_overdrawn_accounts(
        self,
    ) -> list[Account]:
        """
        Return current accounts operating below zero.
        """

        return self.find_where(
            lambda account:
            (
                account.account_type
                == AccountType.CURRENT
            )
            and
            (
                account.balance.amount < 0
            )
        )

    # ------------------------------------------------------------------
    # Counts
    # ------------------------------------------------------------------

    def active_account_count(
        self,
    ) -> int:
        """
        Return the number of active accounts.
        """

        return len(
            self.find_active_accounts()
        )

    # ------------------------------------------------------------------

    def dormant_account_count(
        self,
    ) -> int:
        """
        Return the number of dormant accounts.
        """

        return len(
            self.find_dormant_accounts()
        )

    # ------------------------------------------------------------------

    def frozen_account_count(
        self,
    ) -> int:
        """
        Return the number of frozen accounts.
        """

        return len(
            self.find_frozen_accounts()
        )

# PART 4

    # ------------------------------------------------------------------
    # Balance Queries
    # ------------------------------------------------------------------

    def find_by_balance_range(
        self,
        minimum: Decimal,
        maximum: Decimal,
    ) -> list[Account]:
        """
        Return all accounts whose balance falls within the specified range.
        """

        return self.find_where(
            lambda account:
            minimum
            <= account.balance.amount
            <= maximum
        )

    # ------------------------------------------------------------------
    # Date Queries
    # ------------------------------------------------------------------

    def find_opened_between(
        self,
        start_date: date,
        end_date: date,
    ) -> list[Account]:
        """
        Return accounts opened within the specified date range.
        """

        return self.find_where(
            lambda account:
            start_date
            <= account.opened_date
            <= end_date
        )

    # ------------------------------------------------------------------
    # Customer Portfolio
    # ------------------------------------------------------------------

    def customer_account_count(
        self,
        customer_id: str,
    ) -> int:
        """
        Return the number of accounts owned by a customer.
        """

        return len(
            self.find_by_customer(
                customer_id
            )
        )

    # ------------------------------------------------------------------

    def customer_total_balance(
        self,
        customer_id: str,
    ) -> Decimal:
        """
        Return the customer's total balance across all accounts.
        """

        accounts = self.find_by_customer(
            customer_id
        )

        return sum(
            (
                account.balance.amount
                for account in accounts
            ),
            Decimal("0.00"),
        )

    # ------------------------------------------------------------------

    def customer_accounts_by_type(
        self,
        customer_id: str,
        account_type: AccountType,
    ) -> list[Account]:
        """
        Return all customer accounts of the specified type.
        """

        return [
            account
            for account in self.find_by_customer(
                customer_id
            )
            if account.account_type
            == account_type
        ]

    # ------------------------------------------------------------------
    # Statistics
    # ------------------------------------------------------------------

    def statistics(self) -> dict[str, int]:
        """
        Return repository statistics.
        """

        return {
            "total_accounts": self.count,
            "active_accounts": self.active_account_count(),
            "inactive_accounts": len(
                self.find_inactive_accounts()
            ),
            "savings_accounts": len(
                self.savings_accounts()
            ),
            "current_accounts": len(
                self.current_accounts()
            ),
            "time_deposit_accounts": len(
                self.time_deposit_accounts()
            ),
            "dormant_accounts": self.dormant_account_count(),
            "frozen_accounts": self.frozen_account_count(),
        }

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def validate_unique_account(
        self,
        account: Account,
    ) -> None:
        """
        Validate that the account number is unique.
        """

        if self.exists_account_number(
            account.account_number
        ):
            raise EntityAlreadyExistsError(
                "Account number already exists."
            )

    # ------------------------------------------------------------------

    def add_account(
        self,
        account: Account,
    ) -> None:
        """
        Validate and persist a new account.
        """

        self.validate_unique_account(
            account
        )

        self.save_entity(account)

# Part 5

    # ------------------------------------------------------------------
    # Convenience Methods
    # ------------------------------------------------------------------

    def account_exists(
        self,
        account_number: str,
    ) -> bool:
        """
        Determine whether an account exists.
        """

        return self.exists_account_number(
            account_number
        )

    # ------------------------------------------------------------------

    def get_or_raise(
        self,
        account_number: str,
    ) -> Account:
        """
        Return the account having the specified account number.

        Raises
        ------
        EntityNotFoundError
            If the account does not exist.
        """

        account = self.find_by_account_number(
            account_number
        )

        if account is None:

            raise EntityNotFoundError(
                f"Account '{account_number}' was not found."
            )

        return account

    # ------------------------------------------------------------------

    def save_account(
        self,
        account: Account,
    ) -> None:
        """
        Save an account.

        Adds a new account or updates an existing one.
        """

        self.save_entity(account)

    # ------------------------------------------------------------------

    def remove_account(
        self,
        account_number: str,
    ) -> bool:
        """
        Soft-delete an account using its business identifier.

        Returns
        -------
        bool
            True if the account existed.
        """

        account = self.find_by_account_number(
            account_number
        )

        if account is None:
            return False

        return self.delete_entity(
            account.entity_id
        )

    # ------------------------------------------------------------------
    # Display
    # ------------------------------------------------------------------

    def __str__(self) -> str:
        """
        Human-readable repository representation.
        """

        return (
            f"AccountRepository("
            f"accounts={self.count})"
        )

    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        """
        Developer-friendly repository representation.
        """

        return (
            f"AccountRepository("
            f"count={self.count}, "
            f"file='{self.CSV_FILE}')"
        )


# ----------------------------------------------------------------------
# End of File
# ----------------------------------------------------------------------
