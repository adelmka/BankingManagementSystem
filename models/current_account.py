"""
===============================================================================
Banking Management System (BMS)

File        : current_account.py
Description : Current Account implementation.

Author      : Adel Alawiyat / ChatGPT
Version     : 2.1.0
Python      : 3.13+

===============================================================================
"""

from __future__ import annotations

from datetime import UTC, date, datetime
from decimal import Decimal
from typing import Any

from models.account import Account
from models.value_objects.money import Money

from utils.constants import (
    AccountType,
)

from utils.validators import Validator


class CurrentAccount(Account):
    """
    Concrete implementation of a current (checking) account.
    """

    # ------------------------------------------------------------------
    # Constructor
    # ------------------------------------------------------------------

    def __init__(
        self,
        account_number: str,
        customer_id: str,
        opening_balance: Money,
        overdraft_limit: Money,
        maintenance_fee: Money,
        overdraft_fee: Money,
        currency: str = "SAR",
        overdraft_enabled: bool = True,
        opened_date: date | None = None,
    ) -> None:

        super().__init__(
            account_number=account_number,
            customer_id=customer_id,
            account_type=AccountType.CURRENT,
            opening_balance=opening_balance,
            currency=currency,
            opened_date=opened_date,
        )

        self._initializing = True

        try:

            self._overdraft_limit = overdraft_limit
            self._maintenance_fee = maintenance_fee
            self._overdraft_fee = overdraft_fee
            self._overdraft_enabled = overdraft_enabled
            self._last_fee_date = date.today()

            self.overdraft_limit = overdraft_limit
            self.maintenance_fee = maintenance_fee
            self.overdraft_fee = overdraft_fee
            self.overdraft_enabled = overdraft_enabled

        finally:
            self._initializing = False

    # ------------------------------------------------------------------
    # Overdraft Limit
    # ------------------------------------------------------------------

    @property
    def overdraft_limit(self) -> Money:
        """
        Return the approved overdraft limit.
        """

        return self._overdraft_limit

    @overdraft_limit.setter
    def overdraft_limit(
        self,
        value: Money,
    ) -> None:
        """
        Set the approved overdraft limit.
        """

        if not isinstance(value, Money):
            raise TypeError(
                "overdraft_limit must be a Money object."
            )

        if value.currency != self.currency:
            raise ValueError(
                "Overdraft limit currency must match the account currency."
            )

        if value.amount < Decimal("0.00"):
            raise ValueError(
                "Overdraft limit cannot be negative."
            )

        self._overdraft_limit = value

        self.touch()

# PART 2

    # ------------------------------------------------------------------
    # Maintenance Fee
    # ------------------------------------------------------------------

    @property
    def maintenance_fee(self) -> Money:
        """
        Return the monthly maintenance fee.
        """

        return self._maintenance_fee

    @maintenance_fee.setter
    def maintenance_fee(
        self,
        value: Money,
    ) -> None:
        """
        Set the monthly maintenance fee.
        """

        if not isinstance(value, Money):
            raise TypeError(
                "maintenance_fee must be a Money object."
            )

        if value.currency != self.currency:
            raise ValueError(
                "Maintenance fee currency must match the account currency."
            )

        if value.amount < Decimal("0.00"):
            raise ValueError(
                "Maintenance fee cannot be negative."
            )

        self._maintenance_fee = value

        self.touch()

    # ------------------------------------------------------------------
    # Overdraft Fee
    # ------------------------------------------------------------------

    @property
    def overdraft_fee(self) -> Money:
        """
        Return the overdraft fee.
        """

        return self._overdraft_fee

    @overdraft_fee.setter
    def overdraft_fee(
        self,
        value: Money,
    ) -> None:
        """
        Set the overdraft fee.
        """

        if not isinstance(value, Money):
            raise TypeError(
                "overdraft_fee must be a Money object."
            )

        if value.currency != self.currency:
            raise ValueError(
                "Overdraft fee currency must match the account currency."
            )

        if value.amount < Decimal("0.00"):
            raise ValueError(
                "Overdraft fee cannot be negative."
            )

        self._overdraft_fee = value

        self.touch()

    # ------------------------------------------------------------------
    # Overdraft Enabled
    # ------------------------------------------------------------------

    @property
    def overdraft_enabled(self) -> bool:
        """
        Determine whether overdraft is enabled.
        """

        return self._overdraft_enabled

    @overdraft_enabled.setter
    def overdraft_enabled(
        self,
        value: bool,
    ) -> None:
        """
        Enable or disable overdraft protection.
        """

        if not isinstance(value, bool):
            raise TypeError(
                "overdraft_enabled must be a bool."
            )

        self._overdraft_enabled = value

        self.touch()

    # ------------------------------------------------------------------
    # Last Fee Date
    # ------------------------------------------------------------------

    @property
    def last_fee_date(self) -> date:
        """
        Return the last maintenance/overdraft fee application date.
        """

        return self._last_fee_date

    @last_fee_date.setter
    def last_fee_date(
        self,
        value: date,
    ) -> None:
        """
        Update the last fee application date.
        """

        Validator.date_not_future(
            value,
            "Last Fee Date",
        )

        self._last_fee_date = value

        self.touch()

    # ------------------------------------------------------------------
    # Current Account Business Rules
    # ------------------------------------------------------------------

    def _can_withdraw(
        self,
        amount: Money,
    ) -> bool:
        """
        Determine whether the requested withdrawal is permitted.

        Current accounts may use an approved overdraft facility.
        """

        if not self.overdraft_enabled:
            return self.balance >= amount

        remaining_balance = self.balance - amount

        return (
            remaining_balance.amount
            >= -self.overdraft_limit.amount
        )

    # ------------------------------------------------------------------

    def is_using_overdraft(self) -> bool:
        """
        Determine whether the account is currently using the
        overdraft facility.
        """

        return self.balance.amount < Decimal("0.00")

    # ------------------------------------------------------------------

    def available_funds(self) -> Money:
        """
        Return the total funds available including the approved
        overdraft limit.
        """

        return Money(
            amount=(
                self.balance.amount
                + self.overdraft_limit.amount
            ),
            currency=self.currency,
        )

    # ------------------------------------------------------------------

    def remaining_overdraft(self) -> Money:
        """
        Return the remaining overdraft available to the customer.
        """

        if self.balance.amount >= Decimal("0.00"):
            return self.overdraft_limit

        remaining = (
            self.overdraft_limit.amount
            + self.balance.amount
        )

        return Money(
            amount=max(
                remaining,
                Decimal("0.00"),
            ),
            currency=self.currency,
        )

    # ------------------------------------------------------------------

    def has_available_overdraft(self) -> bool:
        """
        Determine whether additional overdraft funds remain available.
        """

        return (
            self.remaining_overdraft().amount
            > Decimal("0.00")
        )

# PART 3

    # ------------------------------------------------------------------
    # Fee Calculation
    # ------------------------------------------------------------------

    def calculate_maintenance_fee(self) -> Money:
        """
        Return the monthly maintenance fee.

        The fee is calculated but not applied to the account.
        """

        return self.maintenance_fee

    # ------------------------------------------------------------------

    def calculate_overdraft_fee(self) -> Money:
        """
        Return the overdraft fee if the account is currently overdrawn.
        """

        if self.is_using_overdraft():
            return self.overdraft_fee

        return Money.zero(self.currency)

    # ------------------------------------------------------------------

    def calculate_fee(self) -> Money:
        """
        Return the total fee applicable to this account.

        This overrides Account.calculate_fee().
        """

        return (
            self.calculate_maintenance_fee()
            + self.calculate_overdraft_fee()
        )

    # ------------------------------------------------------------------
    # Administrative Operations
    # ------------------------------------------------------------------

    def update_overdraft_limit(
        self,
        new_limit: Money,
    ) -> None:
        """
        Administrative operation used to change the overdraft limit.
        """

        self.overdraft_limit = new_limit

    # ------------------------------------------------------------------

    def update_maintenance_fee(
        self,
        new_fee: Money,
    ) -> None:
        """
        Administrative operation used to change the maintenance fee.
        """

        self.maintenance_fee = new_fee

    # ------------------------------------------------------------------

    def update_overdraft_fee(
        self,
        new_fee: Money,
    ) -> None:
        """
        Administrative operation used to change the overdraft fee.
        """

        self.overdraft_fee = new_fee

    # ------------------------------------------------------------------

    def record_fee_application(
        self,
        application_date: date | None = None,
    ) -> None:
        """
        Record the date on which account fees were applied.
        """

        self.last_fee_date = (
            application_date
            if application_date is not None
            else date.today()
        )

    # ------------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        """
        Convert the current account into a dictionary suitable for CSV
        persistence.
        """

        data = self._base_account_dict()

        data.update(
            {
                "overdraft_limit":
                    str(self.overdraft_limit.amount),
                "maintenance_fee":
                    str(self.maintenance_fee.amount),
                "overdraft_fee":
                    str(self.overdraft_fee.amount),
                "overdraft_enabled":
                    self.overdraft_enabled,
                "last_fee_date":
                    self.last_fee_date.isoformat(),
            }
        )

        return data

    # ------------------------------------------------------------------

    @classmethod
    def from_dict(
        cls,
        data: dict[str, Any],
    ) -> "CurrentAccount":
        """
        Reconstruct a CurrentAccount from persisted data.
        """

        account = cls(
            account_number=data["account_number"],
            customer_id=data["customer_id"],
            opening_balance=Money(
                amount=Decimal(data["balance"]),
                currency=data["currency"],
            ),
            overdraft_limit=Money(
                amount=Decimal(data["overdraft_limit"]),
                currency=data["currency"],
            ),
            maintenance_fee=Money(
                amount=Decimal(data["maintenance_fee"]),
                currency=data["currency"],
            ),
            overdraft_fee=Money(
                amount=Decimal(data["overdraft_fee"]),
                currency=data["currency"],
            ),
            currency=data["currency"],
            overdraft_enabled=(
                str(data["overdraft_enabled"])
                .strip()
                .lower()
                == "true"
            ),
            opened_date=date.fromisoformat(
                data["opened_date"]
            ),
        )

        account.last_fee_date = date.fromisoformat(
            data["last_fee_date"]
        )

        account._restore_entity_state(data)

        return account

# PART 4

    # ------------------------------------------------------------------
    # Display Helpers
    # ------------------------------------------------------------------

    def current_account_summary(self) -> dict[str, Any]:
        """
        Return a summary suitable for UI presentation and reporting.
        """

        summary = self.account_summary()

        summary.update(
            {
                "overdraft_enabled": self.overdraft_enabled,
                "overdraft_limit": str(self.overdraft_limit),
                "maintenance_fee": str(self.maintenance_fee),
                "overdraft_fee": str(self.overdraft_fee),
                "available_funds": str(
                    self.available_funds()
                ),
                "remaining_overdraft": str(
                    self.remaining_overdraft()
                ),
                "using_overdraft": (
                    self.is_using_overdraft()
                ),
                "last_fee_date":
                    self.last_fee_date.isoformat(),
            }
        )

        return summary

    # ------------------------------------------------------------------

    def account_health(self) -> dict[str, Any]:
        """
        Return operational indicators for this account.

        Intended for dashboards, administration and monitoring.
        """

        return {
            "account_number": self.account_number,
            "status": self.status.value,
            "balance": str(self.balance),
            "available_funds": str(
                self.available_funds()
            ),
            "using_overdraft":
                self.is_using_overdraft(),
            "remaining_overdraft":
                str(self.remaining_overdraft()),
            "transaction_count":
                self.transaction_count,
            "is_active":
                self.is_active_account,
        }

    # ------------------------------------------------------------------
    # Display
    # ------------------------------------------------------------------

    def __str__(self) -> str:
        """
        Human-readable representation.
        """

        return (
            f"{self.account_number} "
            f"[Current] "
            f"{self.balance}"
        )

    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        """
        Developer-friendly representation.
        """

        return (
            f"CurrentAccount("
            f"account_number='{self.account_number}', "
            f"customer_id='{self.customer_id}', "
            f"balance={self.balance}, "
            f"overdraft_limit={self.overdraft_limit}, "
            f"overdraft_enabled={self.overdraft_enabled})"
        )

    # ------------------------------------------------------------------
    # Equality
    # ------------------------------------------------------------------

    def __eq__(
        self,
        other: object,
    ) -> bool:
        """
        Compare two current accounts.

        Equality is inherited from BaseEntity.
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
