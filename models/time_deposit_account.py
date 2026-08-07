"""
===============================================================================
Banking Management System (BMS)

File        : time_deposit_account.py
Description : Time Deposit (Fixed Deposit) Account.

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


class TimeDepositAccount(Account):
    """
    Represents a fixed-term deposit account.

    Funds are normally unavailable until the maturity date.
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
        term_months: int,
        early_withdrawal_penalty_rate: Decimal,
        currency: str = "SAR",
        auto_renew: bool = False,
        opened_date: date | None = None,
    ) -> None:

        super().__init__(
            account_number=account_number,
            customer_id=customer_id,
            account_type=AccountType.TIME_DEPOSIT,
            opening_balance=opening_balance,
            currency=currency,
            opened_date=opened_date,
        )

        self._initializing = True

        try:

            self._principal = opening_balance
            self._interest_rate = Decimal("0.00")
            self._term_months = 0
            self._auto_renew = auto_renew
            self._early_withdrawal_penalty_rate = (
                Decimal("0.00")
            )
            self._last_interest_date = self._last_interest_date = date.today()

            self.interest_rate = interest_rate
            self.term_months = term_months
            self.early_withdrawal_penalty_rate = (
                early_withdrawal_penalty_rate
            )

        finally:

            self._initializing = False

# PART 2

    # ------------------------------------------------------------------
    # Principal
    # ------------------------------------------------------------------

    @property
    def principal(self) -> Money:
        """
        Return the original deposited principal.
        """

        return self._principal

    # ------------------------------------------------------------------
    # Interest Rate
    # ------------------------------------------------------------------

    @property
    def interest_rate(self) -> Decimal:
        """
        Annual interest rate expressed as a decimal.

        Example:
            Decimal("0.045") = 4.5%
        """

        return self._interest_rate

    @interest_rate.setter
    def interest_rate(
        self,
        value: Decimal,
    ) -> None:

        if not isinstance(value, Decimal):
            raise TypeError(
                "interest_rate must be a Decimal."
            )

        if value < Decimal("0.00"):
            raise ValueError(
                "Interest rate cannot be negative."
            )

        self._interest_rate = value

        self.touch()

    # ------------------------------------------------------------------
    # Deposit Term
    # ------------------------------------------------------------------

    @property
    def term_months(self) -> int:
        """
        Return the deposit term in months.
        """

        return self._term_months

    @term_months.setter
    def term_months(
        self,
        value: int,
    ) -> None:

        if not isinstance(value, int):
            raise TypeError(
                "term_months must be an integer."
            )

        if value <= 0:
            raise ValueError(
                "Term must be greater than zero."
            )

        self._term_months = value

        self.touch()

    # ------------------------------------------------------------------
    # Computed Helpers
    # ------------------------------------------------------------------

    @property
    def term_days(self) -> int:
        """
        Approximate deposit term expressed in days.

        Intended for reporting and interest calculations where an
        approximate day count is acceptable.
        """

        return self.term_months * 30

    # ------------------------------------------------------------------

    @property
    def maturity_date(self) -> date:
        """
        Return the computed maturity date.

        The maturity date is calculated from the opening date and the
        configured term.
        """

        year = self.opened_date.year
        month = self.opened_date.month + self.term_months
        day = self.opened_date.day

        while month > 12:
            month -= 12
            year += 1

        # Handle months with fewer days.
        while True:
            try:
                return date(year, month, day)
            except ValueError:
                day -= 1

    # ------------------------------------------------------------------
    # Auto Renewal
    # ------------------------------------------------------------------

    @property
    def auto_renew(self) -> bool:
        """
        Determine whether the deposit automatically renews at maturity.
        """

        return self._auto_renew

    @auto_renew.setter
    def auto_renew(
        self,
        value: bool,
    ) -> None:

        if not isinstance(value, bool):
            raise TypeError(
                "auto_renew must be a bool."
            )

        self._auto_renew = value

        self.touch()

    # ------------------------------------------------------------------
    # Early Withdrawal Penalty
    # ------------------------------------------------------------------

    @property
    def early_withdrawal_penalty_rate(self) -> Decimal:
        """
        Return the penalty rate applied to early withdrawals.
        """

        return self._early_withdrawal_penalty_rate

    @early_withdrawal_penalty_rate.setter
    def early_withdrawal_penalty_rate(
        self,
        value: Decimal,
    ) -> None:

        if not isinstance(value, Decimal):
            raise TypeError(
                "Penalty rate must be a Decimal."
            )

        if value < Decimal("0.00"):
            raise ValueError(
                "Penalty rate cannot be negative."
            )

        if value > Decimal("1.00"):
            raise ValueError(
                "Penalty rate cannot exceed 100%."
            )

        self._early_withdrawal_penalty_rate = value

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

        Validator.date_not_future(
            value,
            "Last Interest Date",
        )

        self._last_interest_date = value

        self.touch()

# PART 3

    # ------------------------------------------------------------------
    # Business Rules
    # ------------------------------------------------------------------

    def is_matured(self) -> bool:
        """
        Determine whether the time deposit has reached its maturity date.
        """

        return date.today() >= self.maturity_date

    # ------------------------------------------------------------------

    def _can_withdraw(
        self,
        amount: Money,
    ) -> bool:
        """
        Determine whether the requested withdrawal is permitted.

        Withdrawals are only allowed after maturity.
        """

        if not self.is_matured():
            return False

        return self.balance >= amount

    # ------------------------------------------------------------------

    def can_close(self) -> bool:
        """
        Determine whether the account can be closed.
        """

        return self.is_matured()

    # ------------------------------------------------------------------
    # Interest
    # ------------------------------------------------------------------

    def calculate_interest(self) -> Money:
        """
        Calculate the interest earned over the deposit term.

        The interest is calculated but not credited.
        """

        interest_amount = (
            self.principal.amount
            * self.interest_rate
            * Decimal(self.term_months)
            / Decimal("12")
        )

        return Money(
            amount=interest_amount.quantize(
                Decimal("0.01")
            ),
            currency=self.currency,
        )

    # ------------------------------------------------------------------

    def calculate_maturity_value(self) -> Money:
        """
        Return the value of the investment at maturity.
        """

        return (
            self.principal
            + self.calculate_interest()
        )

    # ------------------------------------------------------------------
    # Early Withdrawal
    # ------------------------------------------------------------------

    def calculate_early_withdrawal_penalty(
        self,
    ) -> Money:
        """
        Calculate the penalty for an early withdrawal.

        If the account has matured, no penalty applies.
        """

        if self.is_matured():
            return Money.zero(self.currency)

        penalty_amount = (
            self.principal.amount
            * self.early_withdrawal_penalty_rate
        )

        return Money(
            amount=penalty_amount.quantize(
                Decimal("0.01")
            ),
            currency=self.currency,
        )

    # ------------------------------------------------------------------

    def apply_early_withdrawal_penalty(
        self,
    ) -> Money:
        """
        Return the penalty amount that should be applied.

        The AccountService is responsible for deducting the penalty,
        recording the transaction, and persisting the changes.
        """

        return self.calculate_early_withdrawal_penalty()

    # ------------------------------------------------------------------
    # Administrative Operations
    # ------------------------------------------------------------------

    def update_interest_rate(
        self,
        new_rate: Decimal,
    ) -> None:
        """
        Administrative operation used to change the annual interest rate.
        """

        self.interest_rate = new_rate

    # ------------------------------------------------------------------

    def update_penalty_rate(
        self,
        new_rate: Decimal,
    ) -> None:
        """
        Administrative operation used to change the early withdrawal
        penalty rate.
        """

        self.early_withdrawal_penalty_rate = new_rate

    # ------------------------------------------------------------------

    def update_auto_renew(
        self,
        enabled: bool,
    ) -> None:
        """
        Enable or disable automatic renewal.
        """

        self.auto_renew = enabled

    # ------------------------------------------------------------------

    def record_interest_application(
        self,
        application_date: date | None = None,
    ) -> None:
        """
        Record the last interest application date.
        """

        self.last_interest_date = (
            application_date
            if application_date is not None
            else date.today()
        )

# PART 4

    # ------------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        """
        Convert the time deposit account into a dictionary suitable for
        CSV persistence.
        """

        data = self._base_account_dict()

        data.update(
            {
                "principal":
                    str(self.principal.amount),
                "interest_rate":
                    str(self.interest_rate),
                "term_months":
                    self.term_months,
                "auto_renew":
                    self.auto_renew,
                "early_withdrawal_penalty_rate":
                    str(
                        self.early_withdrawal_penalty_rate
                    ),
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
    ) -> "TimeDepositAccount":
        """
        Reconstruct a TimeDepositAccount from persisted data.
        """

        account = cls(
            account_number=data["account_number"],
            customer_id=data["customer_id"],
            opening_balance=Money(
                amount=Decimal(
                    data["principal"]
                ),
                currency=data["currency"],
            ),
            interest_rate=Decimal(
                data["interest_rate"]
            ),
            term_months=int(
                data["term_months"]
            ),
            early_withdrawal_penalty_rate=Decimal(
                data[
                    "early_withdrawal_penalty_rate"
                ]
            ),
            currency=data["currency"],
            auto_renew=(
                str(data["auto_renew"])
                .strip()
                .lower()
                == "true"
            ),
            opened_date=date.fromisoformat(
                data["opened_date"]
            ),
        )

        # Restore current balance if interest or adjustments
        # have already been applied.

        account._balance = Money(
            amount=Decimal(data["balance"]),
            currency=data["currency"],
        )

        account.last_interest_date = (
            date.fromisoformat(
                data["last_interest_date"]
            )
        )

        account._restore_entity_state(data)

        return account

    # ------------------------------------------------------------------
    # Reporting Helpers
    # ------------------------------------------------------------------

    def maturity_summary(self) -> dict[str, Any]:
        """
        Return maturity information for presentation layers.
        """

        return {
            "account_number":
                self.account_number,
            "principal":
                str(self.principal),
            "interest_rate":
                f"{self.interest_rate * Decimal('100'):.2f}%",
            "term_months":
                self.term_months,
            "maturity_date":
                self.maturity_date.isoformat(),
            "maturity_value":
                str(
                    self.calculate_maturity_value()
                ),
            "auto_renew":
                self.auto_renew,
            "is_matured":
                self.is_matured(),
        }

    # ------------------------------------------------------------------

    def investment_summary(self) -> dict[str, Any]:
        """
        Return investment information for dashboards and reports.
        """

        summary = self.account_summary()

        summary.update(
            {
                "principal":
                    str(self.principal),
                "interest_earned":
                    str(
                        self.calculate_interest()
                    ),
                "maturity_value":
                    str(
                        self.calculate_maturity_value()
                    ),
                "maturity_date":
                    self.maturity_date.isoformat(),
                "remaining_term_days":
                    max(
                        0,
                        (
                            self.maturity_date
                            - date.today()
                        ).days,
                    ),
                "auto_renew":
                    self.auto_renew,
            }
        )

        return summary

# PART 5

    # ------------------------------------------------------------------
    # Display Helpers
    # ------------------------------------------------------------------

    def __str__(self) -> str:
        """
        Return a human-readable representation of the time deposit
        account.
        """

        return (
            f"{self.account_number} "
            f"[Time Deposit] "
            f"{self.balance}"
        )

    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        """
        Return a developer-friendly representation.
        """

        return (
            f"TimeDepositAccount("
            f"account_number='{self.account_number}', "
            f"customer_id='{self.customer_id}', "
            f"principal={self.principal}, "
            f"balance={self.balance}, "
            f"interest_rate={self.interest_rate}, "
            f"term_months={self.term_months}, "
            f"maturity_date={self.maturity_date.isoformat()}, "
            f"auto_renew={self.auto_renew})"
        )

    # ------------------------------------------------------------------
    # Equality
    # ------------------------------------------------------------------

    def __eq__(
        self,
        other: object,
    ) -> bool:
        """
        Equality is based on the immutable entity identifier inherited
        from BaseEntity.
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
