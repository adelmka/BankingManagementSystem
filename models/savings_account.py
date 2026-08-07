"""
===============================================================================
Banking Management System (BMS)

File        : savings_account.py
Description : Savings Account implementation.

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
    InterestFrequency,
)

from utils.validators import Validator


class SavingsAccount(Account):
    """
    Concrete implementation of a savings account.
    """

    # ------------------------------------------------------------------
    # Constructor
    # ------------------------------------------------------------------

    def __init__(
        self,
        account_number: str,
        customer_id: str,
        opening_balance: Money,
        interest_rate: Decimal,
        minimum_balance: Money,
        currency: str = "SAR",
        interest_frequency: InterestFrequency = (
            InterestFrequency.MONTHLY
        ),
        opened_date: date | None = None,
    ) -> None:

        super().__init__(
            account_number=account_number,
            customer_id=customer_id,
            account_type=AccountType.SAVINGS,
            opening_balance=opening_balance,
            currency=currency,
            opened_date=opened_date,
        )

        self._initializing = True

        try:

            self._interest_rate = Decimal("0.00")
            self._minimum_balance = minimum_balance
            self._interest_frequency = interest_frequency
            self._last_interest_date = (
                datetime.now(UTC).date()
            )

            self.interest_rate = interest_rate
            self.minimum_balance = minimum_balance
            self.interest_frequency = interest_frequency

        finally:

            self._initializing = False

    # ------------------------------------------------------------------
    # Interest Rate
    # ------------------------------------------------------------------

    @property
    def interest_rate(self) -> Decimal:
        """
        Annual interest rate expressed as a decimal.

        Example:
            Decimal("0.035") = 3.5%
        """

        return self._interest_rate

    @interest_rate.setter
    def interest_rate(
        self,
        value: Decimal,
    ) -> None:

        if value < Decimal("0"):
            raise ValueError(
                "Interest rate cannot be negative."
            )

        self._interest_rate = value

        self.touch()

# PART 2

    # ------------------------------------------------------------------
    # Minimum Balance
    # ------------------------------------------------------------------

    @property
    def minimum_balance(self) -> Money:
        """
        Return the minimum balance required for this savings account.
        """

        return self._minimum_balance

    @minimum_balance.setter
    def minimum_balance(
        self,
        value: Money,
    ) -> None:
        """
        Set the minimum balance requirement.
        """

        if not isinstance(value, Money):
            raise TypeError(
                "minimum_balance must be a Money object."
            )

        if value.currency != self.currency:
            raise ValueError(
                "Minimum balance currency must match "
                "the account currency."
            )

        if value.amount < Decimal("0.00"):
            raise ValueError(
                "Minimum balance cannot be negative."
            )

        self._minimum_balance = value

        self.touch()

    # ------------------------------------------------------------------
    # Interest Frequency
    # ------------------------------------------------------------------

    @property
    def interest_frequency(self) -> InterestFrequency:
        """
        Return the interest payment frequency.
        """

        return self._interest_frequency

    @interest_frequency.setter
    def interest_frequency(
        self,
        value: InterestFrequency,
    ) -> None:
        """
        Set the interest payment frequency.
        """

        if not isinstance(value, InterestFrequency):
            raise TypeError(
                "interest_frequency must be an "
                "InterestFrequency."
            )

        self._interest_frequency = value

        self.touch()

    # ------------------------------------------------------------------
    # Last Interest Date
    # ------------------------------------------------------------------

    @property
    def last_interest_date(self) -> date:
        """
        Return the last date on which interest was applied.
        """

        return self._last_interest_date

    @last_interest_date.setter
    def last_interest_date(
        self,
        value: date,
    ) -> None:
        """
        Update the last interest application date.
        """

        Validator.date_not_future(
            value,
            "Last Interest Date",
        )

        self._last_interest_date = value

        self.touch()

    # ------------------------------------------------------------------
    # Savings Business Rules
    # ------------------------------------------------------------------

    def _can_withdraw(
        self,
        amount: Money,
    ) -> bool:
        """
        Savings accounts do not allow withdrawals that would reduce the
        balance below the configured minimum balance.
        """

        remaining_balance = self.balance - amount

        return (
            remaining_balance >= self.minimum_balance
        )

    # ------------------------------------------------------------------

    def has_minimum_balance(self) -> bool:
        """
        Determine whether the current balance satisfies the minimum
        balance requirement.
        """

        return self.balance >= self.minimum_balance

    # ------------------------------------------------------------------

    def amount_available_for_withdrawal(self) -> Money:
        """
        Return the maximum amount that can currently be withdrawn while
        maintaining the required minimum balance.
        """

        if self.balance <= self.minimum_balance:
            return Money.zero(self.currency)

        return self.balance - self.minimum_balance

    # ------------------------------------------------------------------

    def can_earn_interest(self) -> bool:
        """
        Determine whether the account currently qualifies for interest.
        """

        return (
            self.is_active_account
            and self.has_minimum_balance()
        )

    # ------------------------------------------------------------------

    def update_interest_rate(
        self,
        new_rate: Decimal,
    ) -> None:
        """
        Administrative operation used to change the annual interest
        rate.
        """

        self.interest_rate = new_rate

# PART 3

    # ------------------------------------------------------------------
    # Interest Calculation
    # ------------------------------------------------------------------

    def calculate_interest(self) -> Money:
        """
        Calculate the interest currently earned by this savings account.

        Notes
        -----
        This method does not credit the account. It only returns the
        calculated interest amount. Applying the interest is handled by
        the service layer.
        """

        if not self.can_earn_interest():
            return Money.zero(self.currency)

        interest_amount = (
            self.balance.amount
            * self.interest_rate
        )

        return Money(
            amount=interest_amount.quantize(
                Decimal("0.01")
            ),
            currency=self.currency,
        )

    # ------------------------------------------------------------------

    def record_interest_application(
        self,
        application_date: date | None = None,
    ) -> None:
        """
        Record the date on which interest was applied.
        """

        self.last_interest_date = (
            application_date
            if application_date is not None
            else datetime.now(UTC).date()
        )

    # ------------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        """
        Convert the savings account into a dictionary suitable for CSV
        persistence.
        """

        data = self._base_account_dict()

        data.update(
            {
                "interest_rate": str(self.interest_rate),
                "minimum_balance":
                    str(self.minimum_balance.amount),
                "interest_frequency":
                    self.interest_frequency.value,
                "last_interest_date":
                    self.last_interest_date.isoformat(),
            }
        )

        return data

    # ------------------------------------------------------------------

    @classmethod
    def from_dict(
        cls,
        data: dict[str, Any],
    ) -> "SavingsAccount":
        """
        Reconstruct a SavingsAccount from persisted data.
        """

        account = cls(
            account_number=data["account_number"],
            customer_id=data["customer_id"],
            opening_balance=Money(
                amount=Decimal(data["balance"]),
                currency=data["currency"],
            ),
            interest_rate=Decimal(
                data["interest_rate"]
            ),
            minimum_balance=Money(
                amount=Decimal(
                    data["minimum_balance"]
                ),
                currency=data["currency"],
            ),
            currency=data["currency"],
            interest_frequency=InterestFrequency(
                data["interest_frequency"]
            ),
            opened_date=date.fromisoformat(
                data["opened_date"]
            ),
        )

        account.last_interest_date = (
            date.fromisoformat(
                data["last_interest_date"]
            )
        )

        account._restore_entity_state(data)

        return account

# PART 4

    # ------------------------------------------------------------------
    # Interest Frequency Helpers
    # ------------------------------------------------------------------

    def periods_per_year(self) -> int:
        """
        Return the number of interest periods in one calendar year.
        """

        match self.interest_frequency:

            case InterestFrequency.DAILY:
                return 365

            case InterestFrequency.WEEKLY:
                return 52

            case InterestFrequency.MONTHLY:
                return 12

            case InterestFrequency.QUARTERLY:
                return 4

            case InterestFrequency.SEMI_ANNUALLY:
                return 2

            case InterestFrequency.ANNUALLY:
                return 1

            case _:
                return 12

    # ------------------------------------------------------------------
    # Display Helpers
    # ------------------------------------------------------------------

    def savings_summary(self) -> dict[str, Any]:
        """
        Return a summary suitable for UI presentation and reporting.
        """

        summary = self.account_summary()

        summary.update(
            {
                "interest_rate": f"{self.interest_rate * Decimal('100'):.2f}%",
                "minimum_balance": str(self.minimum_balance),
                "interest_frequency": self.interest_frequency.value,
                "last_interest_date":
                    self.last_interest_date.isoformat(),
                "eligible_for_interest":
                    self.can_earn_interest(),
            }
        )

        return summary

    # ------------------------------------------------------------------

    def __str__(self) -> str:
        """
        Human-readable representation.
        """

        return (
            f"{self.account_number} "
            f"[Savings] "
            f"{self.balance}"
        )

    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        """
        Developer-friendly representation.
        """

        return (
            f"SavingsAccount("
            f"account_number='{self.account_number}', "
            f"customer_id='{self.customer_id}', "
            f"balance={self.balance}, "
            f"interest_rate={self.interest_rate}, "
            f"minimum_balance={self.minimum_balance})"
        )

    # ------------------------------------------------------------------
    # Equality
    # ------------------------------------------------------------------

    def __eq__(
        self,
        other: object,
    ) -> bool:
        """
        Compare two savings accounts.
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
