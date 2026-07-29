# PART 1
"""
===============================================================================
Banking Management System (BMS)

File        : account.py
Description : Abstract Account Entity.

Author      : Adel Alawiyat / ChatGPT
Version     : 2.1.0
Python      : 3.13+

Every banking account inherits from this class.

Derived Classes
---------------
    • SavingsAccount
    • CurrentAccount
    • TimeDepositAccount

===============================================================================
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import UTC, date, datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from models.base_entity import BaseEntity
from models.value_objects.money import Money

from utils.constants import (
    AccountStatus,
    AccountType,
)

from utils.validators import Validator


class Account(BaseEntity, ABC):
    """
    Abstract banking account.
    """

    # ------------------------------------------------------------------
    # Constructor
    # ------------------------------------------------------------------

    def __init__(
        self,
        account_number: str,
        customer_id: str,
        account_type: AccountType,
        opening_balance: Money,
        currency: str = "SAR",
        opened_date: date | None = None,
        status: AccountStatus = AccountStatus.ACTIVE,
    ) -> None:

        super().__init__()

        self._initializing = True

        try:

            self._account_number = ""
            self._customer_id = ""
            self._account_type = account_type
            self._currency = currency.upper()
            self._validate_opening_balance(opening_balance) # added later
            self._balance = opening_balance
            self._status = status

            self._opened_date = (
                opened_date or datetime.now(UTC).date()
            )

            self._closed_date: date | None = None

            self._transaction_ids: list[str] = []

            self.account_number = account_number
            self.customer_id = customer_id
            self.account_type = account_type
            self.status = status

        finally:
            self._initializing = False


    def _validate_opening_balance(
        self,
        opening_balance: Money,
    ) -> None:
        """
        Validate the opening balance.

        Derived classes may override this method.
        """

        self._validate_money(opening_balance)

        if opening_balance.amount < Decimal("0.00"):
            raise ValueError(
                "Opening balance cannot be negative."
            )

    # ------------------------------------------------------------------
    # Account Number
    # ------------------------------------------------------------------

    @property
    def account_number(self) -> str:
        return self._account_number

    @account_number.setter
    def account_number(self, value: str) -> None:

        Validator.required(value, "Account Number")
        Validator.max_length(value, 30, "Account Number")

        self._account_number = value.strip().upper()

        self.touch()

    # ------------------------------------------------------------------
    # Customer ID
    # ------------------------------------------------------------------

    @property
    def customer_id(self) -> str:
        return self._customer_id

    @customer_id.setter
    def customer_id(self, value: str) -> None:

        Validator.required(value, "Customer ID")

        self._customer_id = value.strip().upper()

        self.touch()

    # ------------------------------------------------------------------
    # Account Type
    # ------------------------------------------------------------------

    @property
    def account_type(self) -> AccountType:
        return self._account_type

    @account_type.setter
    def account_type(
        self,
        value: AccountType,
    ) -> None:

        if not isinstance(value, AccountType):
            raise TypeError(
                "account_type must be AccountType."
            )

        self._account_type = value

        self.touch()

# PART 2

    # ------------------------------------------------------------------
    # Account Status
    # ------------------------------------------------------------------

    @property
    def status(self) -> AccountStatus:
        """
        Return the account status.
        """
        return self._status

    @status.setter
    def status(
        self,
        value: AccountStatus,
    ) -> None:
        """
        Set the account status.
        """

        if not isinstance(value, AccountStatus):
            raise TypeError(
                "status must be an AccountStatus."
            )

        self._status = value

        self.touch()

    # ------------------------------------------------------------------
    # Currency
    # ------------------------------------------------------------------

    @property
    def currency(self) -> str:
        """
        Return the account currency.
        """
        return self._currency

    @currency.setter
    def currency(self, value: str) -> None:
        """
        Set the account currency.
        """

        Validator.required(value, "Currency")

        value = value.strip().upper()

        Validator.max_length(
            value,
            3,
            "Currency",
        )

        self._currency = value

        self.touch()

    # ------------------------------------------------------------------
    # Balance
    # ------------------------------------------------------------------

    @property
    def balance(self) -> Money:
        """
        Return the current account balance.
        """

        return self._balance

    @property
    def available_balance(self) -> Money:
        """
        Return the available balance.

        Derived classes may override this property to account for
        holds, overdraft limits, or reserved funds.
        """

        return self._balance

    @property
    def balance_amount(self) -> Decimal::
        """
        Return the numeric balance amount.
        """

        return self._balance.amount

    @property
    def is_overdrawn(self) -> bool:
        """
        Determine whether the account balance is below zero.
        """

        return self.balance_amount < Decimal("0.00")

    @property
    def has_positive_balance(self) -> bool:
        """
        Determine whether the account has a positive balance.
        """

        return self.balance_amount > Decimal("0.00")

    @property
    def is_zero_balance(self) -> bool:
        """
        Determine whether the account balance is zero.
        """

        return self.balance_amount == Decimal("0.00")

    # ------------------------------------------------------------------
    # Important Dates
    # ------------------------------------------------------------------

    @property
    def opened_date(self) -> date:
        """
        Return the account opening date.
        """

        return self._opened_date

    @opened_date.setter
    def opened_date(
        self,
        value: date,
    ) -> None:
        """
        Set the account opening date.
        """

        Validator.date_not_in_future(
            value,
            "Opened Date",
        )

        self._opened_date = value

        self.touch()

    @property
    def closed_date(self) -> date | None:
        """
        Return the account closing date.
        """

        return self._closed_date

    # ------------------------------------------------------------------
    # Transaction History
    # ------------------------------------------------------------------

    @property
    def transaction_ids(self) -> tuple[str, ...]:
        """
        Return an immutable collection of transaction identifiers.
        """

        return tuple(self._transaction_ids)

    @property
    def transaction_count(self) -> int:
        """
        Return the number of recorded transactions.
        """

        return len(self._transaction_ids)

    def add_transaction(
        self,
        transaction_id: str,
    ) -> None:
        """
        Associate a transaction with this account.
        """

        Validator.required(
            transaction_id,
            "Transaction ID",
        )

        transaction_id = transaction_id.strip().upper()

        if transaction_id in self._transaction_ids:
            raise ValueError(
                f"Transaction '{transaction_id}' already exists."
            )

        self._transaction_ids.append(transaction_id)

        self.touch()

    def remove_transaction(
        self,
        transaction_id: str,
    ) -> None:
        """
        Remove a transaction association.
        """

        transaction_id = transaction_id.strip().upper()

        if transaction_id not in self._transaction_ids:
            raise ValueError(
                f"Transaction '{transaction_id}' was not found."
            )

        self._transaction_ids.remove(transaction_id)

        self.touch()

    def has_transaction(
        self,
        transaction_id: str,
    ) -> bool:
        """
        Determine whether a transaction belongs to this account.
        """

        return (
            transaction_id.strip().upper()
            in self._transaction_ids
        )

    # ------------------------------------------------------------------
    # Status Helpers
    # ------------------------------------------------------------------

    @property
    def is_active_account(self) -> bool:
        """
        Determine whether the account is active.
        """

        return (
            self.status == AccountStatus.ACTIVE
            and self.is_active
        )

    @property
    def is_closed(self) -> bool:
        """
        Determine whether the account has been closed.
        """

        return self.status == AccountStatus.CLOSED

# PART 3

    # ------------------------------------------------------------------
    # Business Operations
    # ------------------------------------------------------------------

    def deposit(
        self,
        amount: Money,
    ) -> None:
        """
        Deposit funds into the account.

        Parameters
        ----------
        amount : Money
            Amount to deposit.

        Raises
        ------
        ValueError
            If the amount is invalid.
        """

        self._validate_active_account()

        self._validate_money(amount)

        self._balance = self._balance + amount

        self.touch()

    # ------------------------------------------------------------------

    def withdraw(
        self,
        amount: Money,
    ) -> None:
        """
        Withdraw funds from the account.

        Derived classes may override the available balance rules by
        implementing _can_withdraw().
        """

        self._validate_active_account()

        self._validate_money(amount)

        if not self._can_withdraw(amount):
            raise ValueError(
                "Insufficient available balance."
            )

        self._balance = self._balance - amount

        self.touch()

    # ------------------------------------------------------------------

    def transfer_to(
        self,
        destination: "Account",
        amount: Money,
    ) -> None:
        """
        Transfer funds to another account.

        Notes
        -----
        This method performs only the domain operation.

        Transaction recording, persistence, notifications,
        auditing and external integrations are handled by
        the AccountService.
        """

        if destination is self:
            raise ValueError(
                "Cannot transfer to the same account."
            )

        self.withdraw(amount)

        destination.deposit(amount)

    # ------------------------------------------------------------------
    # Account Lifecycle
    # ------------------------------------------------------------------

    def open_account(self) -> None:
        """
        Activate an account.
        """

        self.status = AccountStatus.ACTIVE

        self.activate()

    # ------------------------------------------------------------------

    def close_account(self) -> None:
        """
        Close the account.

        Business Rule
        -------------
        An account may only be closed when the balance is zero.
        """

        if not self.is_zero_balance:
            raise ValueError(
                "Account cannot be closed while a balance exists."
            )

        self.status = AccountStatus.CLOSED

        self._closed_date = datetime.now(UTC).date()

        self.deactivate()

    # ------------------------------------------------------------------
    # Validation Helpers
    # ------------------------------------------------------------------

    def _validate_money(
        self,
        amount: Money,
    ) -> None:
        """
        Validate a monetary amount.
        """

        if not isinstance(amount, Money):
            raise TypeError(
                "amount must be a Money object."
            )

        if amount.currency != self.currency:
            raise ValueError(
                "Currency mismatch."
            )

        if amount.amount <= Decimal("0.00"):
            raise ValueError(
                "Amount must be greater than zero."
            )

    # ------------------------------------------------------------------

    def _validate_active_account(self) -> None:
        """
        Ensure the account is active.
        """

        if not self.is_active_account:
            raise ValueError(
                "Account is not active."
            )

    # ------------------------------------------------------------------
    # Extension Hooks
    # ------------------------------------------------------------------

    def _can_withdraw(
        self,
        amount: Money,
    ) -> bool:
        """
        Determine whether a withdrawal is permitted.

        Derived classes may override this method.
        """

        return self.available_balance >= amount

    # ------------------------------------------------------------------

    def calculate_interest(
        self,
    ) -> Money:
        """
        Default interest calculation.

        Most account types override this implementation.
        """

        return Money.zero(self.currency)

    # ------------------------------------------------------------------

    def calculate_fee(
        self,
    ) -> Money:
        """
        Default fee calculation.

        Derived classes override as necessary.
        """

        return Money.zero(self.currency)

# PART 4

    # ------------------------------------------------------------------
    # Transaction Serialization Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _serialize_transaction_ids(
        transaction_ids: list[str],
    ) -> str:
        """
        Convert the transaction identifier collection into a
        pipe-separated string suitable for CSV persistence.
        """

        if not transaction_ids:
            return ""

        return "|".join(transaction_ids)

    # ------------------------------------------------------------------

    @staticmethod
    def _deserialize_transaction_ids(
        value: str,
    ) -> list[str]:
        """
        Convert a pipe-separated transaction string into a list.
        """

        if not value:
            return []

        return [
            transaction_id.strip().upper()
            for transaction_id in value.split("|")
            if transaction_id.strip()
        ]

    # ------------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------------

    def _base_account_dict(self) -> dict[str, Any]:
        """
        Return the common Account data.

        Derived classes should extend this dictionary when implementing
        their own to_dict() methods.
        """

        return {
            # ---------- BaseEntity ----------
            "entity_id": str(self.entity_id),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "is_active": self.is_active,
            "version": self.version,

            # ---------- Account ----------
            "account_number": self.account_number,
            "customer_id": self.customer_id,
            "account_type": self.account_type.value,
            "status": self.status.value,
            "currency": self.currency,
            "balance": str(self.balance.amount),
            "opened_date": self.opened_date.isoformat(),
            "closed_date": (
                self.closed_date.isoformat()
                if self.closed_date
                else ""
            ),
            "transaction_ids":
                self._serialize_transaction_ids(
                    self._transaction_ids
                ),
        }

    # ------------------------------------------------------------------
    # Display Helpers
    # ------------------------------------------------------------------

    def account_summary(self) -> dict[str, Any]:
        """
        Return a summary suitable for UI presentation.
        """

        return {
            "account_number": self.account_number,
            "customer_id": self.customer_id,
            "account_type": self.account_type.value,
            "status": self.status.value,
            "currency": self.currency,
            "balance": str(self.balance.amount),
            "transactions": self.transaction_count,
            "opened_date": self.opened_date.isoformat(),
        }

    # ------------------------------------------------------------------

    def display_name(self) -> str:
        """
        Return a concise display string.
        """

        return (
            f"{self.account_number} "
            f"({self.account_type.value})"
        )

    # ------------------------------------------------------------------

    def __str__(self) -> str:
        """
        Human-readable representation.
        """

        return (
            f"{self.account_number} - "
            f"{self.balance}"
        )

    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        """
        Developer-friendly representation.
        """

        return (
            f"{self.__class__.__name__}("
            f"account_number='{self.account_number}', "
            f"customer_id='{self.customer_id}', "
            f"balance={self.balance}, "
            f"status='{self.status.value}')"
        )

    # ------------------------------------------------------------------
    # Abstract Persistence Interface
    # ------------------------------------------------------------------

    @abstractmethod
    def to_dict(self) -> dict[str, Any]:
        """
        Convert the account into a dictionary suitable for persistence.
        """
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def from_dict(
        cls,
        data: dict[str, Any],
    ) -> "Account":
        """
        Reconstruct an account from persisted data.
        """
        raise NotImplementedError

# PART 5

    # ------------------------------------------------------------------
    # Comparison Helpers
    # ------------------------------------------------------------------

    def has_same_account_number(
        self,
        other: "Account",
    ) -> bool:
        """
        Determine whether another account has the same account number.
        """

        if not isinstance(other, Account):
            return False

        return (
            self.account_number.upper()
            == other.account_number.upper()
        )

    # ------------------------------------------------------------------

    def belongs_to_customer(
        self,
        customer_id: str,
    ) -> bool:
        """
        Determine whether this account belongs to the specified customer.
        """

        Validator.required(
            customer_id,
            "Customer ID",
        )

        return (
            self.customer_id
            == customer_id.strip().upper()
        )

    # ------------------------------------------------------------------

    def has_transactions(self) -> bool:
        """
        Determine whether any transactions have been recorded.
        """

        return self.transaction_count > 0

    # ------------------------------------------------------------------
    # Balance Helpers
    # ------------------------------------------------------------------

    def credit(
        self,
        amount: Money,
    ) -> None:
        """
        Alias for deposit().

        Primarily used by transfer and settlement services.
        """

        self.deposit(amount)

    # ------------------------------------------------------------------

    def debit(
        self,
        amount: Money,
    ) -> None:
        """
        Alias for withdraw().

        Primarily used by transfer and settlement services.
        """

        self.withdraw(amount)

    # ------------------------------------------------------------------

    def reset_transaction_history(self) -> None:
        """
        Remove all recorded transaction identifiers.

        Intended for testing and administrative maintenance.
        """

        self._transaction_ids.clear()

        self.touch()

    # ------------------------------------------------------------------
    # Lifecycle Helpers
    # ------------------------------------------------------------------

    def reopen(self) -> None:
        """
        Reopen a previously closed account.
        """

        self._closed_date = None

        self.status = AccountStatus.ACTIVE

        self.activate()

    # ------------------------------------------------------------------

    def suspend(self) -> None:
        """
        Suspend the account.
        """

        self.status = AccountStatus.SUSPENDED

    # ------------------------------------------------------------------

    def reactivate(self) -> None:
        """
        Reactivate a suspended account.
        """

        self.status = AccountStatus.ACTIVE

    # ------------------------------------------------------------------
    # Display Helpers
    # ------------------------------------------------------------------

    def as_display_dict(self) -> dict[str, str]:
        """
        Return a lightweight dictionary for presentation layers.
        """

        return {
            "account_number": self.account_number,
            "customer_id": self.customer_id,
            "account_type": self.account_type.value,
            "status": self.status.value,
            "currency": self.currency,
            "balance": str(self.balance),
            "opened_date": self.opened_date.isoformat(),
            "transaction_count": str(
                self.transaction_count
            ),
        }

    # ------------------------------------------------------------------

    def statement_header(self) -> dict[str, str]:
        """
        Return account information commonly displayed at the top of an
        account statement.
        """

        return {
            "account_number": self.account_number,
            "customer_id": self.customer_id,
            "account_type": self.account_type.value,
            "currency": self.currency,
            "current_balance": str(self.balance),
            "status": self.status.value,
        }

    # ------------------------------------------------------------------
    # Business Rule Helpers
    # ------------------------------------------------------------------

    def can_accept_deposit(self) -> bool:
        """
        Determine whether deposits are currently permitted.
        """

        return self.is_active_account

    # ------------------------------------------------------------------

    def can_accept_withdrawal(self) -> bool:
        """
        Determine whether withdrawals are currently permitted.
        """

        return self.is_active_account

    # ------------------------------------------------------------------

    def can_transfer(self) -> bool:
        """
        Determine whether transfers are currently permitted.
        """

        return (
            self.can_accept_deposit()
            and self.can_accept_withdrawal()
        )

# PART 6

    # ------------------------------------------------------------------
    # Persistence Restoration Helper
    # ------------------------------------------------------------------

    def _restore_entity_state(
        self,
        data: dict[str, Any],
    ) -> None:
        """
        Restore the persisted BaseEntity and Account state.

        This helper is intended to be called by derived classes from
        their from_dict() implementations after the account has been
        constructed.
        """

        # ---------- BaseEntity ----------

        self._entity_id = UUID(data["entity_id"])

        self._created_at = datetime.fromisoformat(
            data["created_at"]
        )

        self._updated_at = datetime.fromisoformat(
            data["updated_at"]
        )

        self._is_active = (
            str(data["is_active"]).strip().lower()
            == "true"
        )

        self._version = int(data["version"])

        # ---------- Account ----------

        closed_date = data.get("closed_date", "")

        self._closed_date = (
            date.fromisoformat(closed_date)
            if closed_date
            else None
        )

        self._transaction_ids = (
            self._deserialize_transaction_ids(
                data.get("transaction_ids", "")
            )
        )

    # ------------------------------------------------------------------
    # Equality Helpers
    # ------------------------------------------------------------------

    def __eq__(
        self,
        other: object,
    ) -> bool:
        """
        Accounts are equal when their entity identifiers match.
        """

        return super().__eq__(other)

    # ------------------------------------------------------------------

    def __hash__(self) -> int:
        """
        Hash using the immutable entity identifier.
        """

        return super().__hash__()

# ----------------------------------------------------------------------
# End of File
# ----------------------------------------------------------------------

