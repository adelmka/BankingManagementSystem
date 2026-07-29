"""
===============================================================================
Banking Management System (BMS)

File        : transaction.py
Description : Banking Transaction Entity.

Author      : Adel Alawiyat / ChatGPT
Version     : 2.1.0
Python      : 3.13+

===============================================================================
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from models.base_entity import BaseEntity
from models.value_objects.money import Money

from utils.constants import (
    TransactionStatus,
    TransactionType,
)

from utils.validators import Validator


class Transaction(BaseEntity):
    """
    Represents a single immutable banking transaction.

    Every financial event in the banking system is represented by a
    Transaction.
    """

    # ------------------------------------------------------------------
    # Constructor
    # ------------------------------------------------------------------

    def __init__(
        self,
        transaction_number: str,
        transaction_type: TransactionType,
        amount: Money,
        source_account: str | None,
        destination_account: str | None,
        initiated_by: str,
        description: str = "",
        reference_number: str | None = None,
    ) -> None:

        super().__init__()

        Validator.required(
            transaction_number,
            "Transaction Number",
        )

        if not isinstance(
            transaction_type,
            TransactionType,
        ):
            raise TypeError(
                "transaction_type must be a TransactionType."
            )

        if not isinstance(amount, Money):
            raise TypeError(
                "amount must be a Money object."
            )

        Validator.required(
            initiated_by,
            "Initiated By",
        )

        self._transaction_number = (
            transaction_number.strip().upper()
        )

        self._reference_number = (
            reference_number.strip().upper()
            if reference_number
            else ""
        )

        self._transaction_type = transaction_type
        self._transaction_status = (
            TransactionStatus.COMPLETED
        )

        self._amount = amount

        self._source_account = (
            source_account.strip().upper()
            if source_account
            else ""
        )

        self._destination_account = (
            destination_account.strip().upper()
            if destination_account
            else ""
        )

        self._transaction_date = (
            datetime.now(UTC)
        )

        self._description = description.strip()

        self._initiated_by = (
            initiated_by.strip()
        )

        self._approved_by = ""

        self._remarks = ""

# PART 2

    # ------------------------------------------------------------------
    # Transaction Number
    # ------------------------------------------------------------------

    @property
    def transaction_number(self) -> str:
        """
        Return the unique transaction number.
        """

        return self._transaction_number

    # ------------------------------------------------------------------
    # Reference Number
    # ------------------------------------------------------------------

    @property
    def reference_number(self) -> str:
        """
        Return the business reference number.
        """

        return self._reference_number

    # ------------------------------------------------------------------
    # Transaction Type
    # ------------------------------------------------------------------

    @property
    def transaction_type(self) -> TransactionType:
        """
        Return the transaction type.
        """

        return self._transaction_type

    # ------------------------------------------------------------------
    # Transaction Status
    # ------------------------------------------------------------------

    @property
    def transaction_status(self) -> TransactionStatus:
        """
        Return the current transaction status.
        """

        return self._transaction_status

    @transaction_status.setter
    def transaction_status(
        self,
        value: TransactionStatus,
    ) -> None:

        if not isinstance(
            value,
            TransactionStatus,
        ):
            raise TypeError(
                "transaction_status must be a "
                "TransactionStatus."
            )

        self._transaction_status = value

        self.touch()

    # ------------------------------------------------------------------
    # Amount
    # ------------------------------------------------------------------

    @property
    def amount(self) -> Money:
        """
        Return the transaction amount.
        """

        return self._amount

    # ------------------------------------------------------------------
    # Source Account
    # ------------------------------------------------------------------

    @property
    def source_account(self) -> str:
        """
        Return the source account number.
        """

        return self._source_account

    # ------------------------------------------------------------------
    # Destination Account
    # ------------------------------------------------------------------

    @property
    def destination_account(self) -> str:
        """
        Return the destination account number.
        """

        return self._destination_account

    # ------------------------------------------------------------------
    # Transaction Date
    # ------------------------------------------------------------------

    @property
    def transaction_date(self) -> datetime:
        """
        Return the transaction timestamp.
        """

        return self._transaction_date

    # ------------------------------------------------------------------
    # Description
    # ------------------------------------------------------------------

    @property
    def description(self) -> str:
        """
        Return the transaction description.
        """

        return self._description

    # ------------------------------------------------------------------
    # Initiated By
    # ------------------------------------------------------------------

    @property
    def initiated_by(self) -> str:
        """
        Return the user who initiated the transaction.
        """

        return self._initiated_by

    # ------------------------------------------------------------------
    # Approved By
    # ------------------------------------------------------------------

    @property
    def approved_by(self) -> str:
        """
        Return the approving user.
        """

        return self._approved_by

    @approved_by.setter
    def approved_by(
        self,
        value: str,
    ) -> None:

        self._approved_by = value.strip()

        self.touch()

    # ------------------------------------------------------------------
    # Remarks
    # ------------------------------------------------------------------

    @property
    def remarks(self) -> str:
        """
        Return transaction remarks.
        """

        return self._remarks

    @remarks.setter
    def remarks(
        self,
        value: str,
    ) -> None:

        self._remarks = value.strip()

        self.touch()

    # ------------------------------------------------------------------
    # Status Helpers
    # ------------------------------------------------------------------

    def mark_completed(self) -> None:
        """
        Mark the transaction as completed.
        """

        self.transaction_status = (
            TransactionStatus.COMPLETED
        )

    # ------------------------------------------------------------------

    def mark_pending(self) -> None:
        """
        Mark the transaction as pending.
        """

        self.transaction_status = (
            TransactionStatus.PENDING
        )

    # ------------------------------------------------------------------

    def mark_failed(self) -> None:
        """
        Mark the transaction as failed.
        """

        self.transaction_status = (
            TransactionStatus.FAILED
        )

    # ------------------------------------------------------------------

    def mark_reversed(self) -> None:
        """
        Mark the transaction as reversed.
        """

        self.transaction_status = (
            TransactionStatus.REVERSED
        )

    # ------------------------------------------------------------------
    # Approval Helpers
    # ------------------------------------------------------------------

    def approve(
        self,
        approved_by: str,
    ) -> None:
        """
        Approve the transaction.
        """

        Validator.required(
            approved_by,
            "Approved By",
        )

        self.approved_by = approved_by

        self.mark_completed()

    # ------------------------------------------------------------------
    # Convenience Methods
    # ------------------------------------------------------------------

    def is_completed(self) -> bool:
        return (
            self.transaction_status
            == TransactionStatus.COMPLETED
        )

    # ------------------------------------------------------------------

    def is_pending(self) -> bool:
        return (
            self.transaction_status
            == TransactionStatus.PENDING
        )

    # ------------------------------------------------------------------

    def is_failed(self) -> bool:
        return (
            self.transaction_status
            == TransactionStatus.FAILED
        )

    # ------------------------------------------------------------------

    def is_reversed(self) -> bool:
        return (
            self.transaction_status
            == TransactionStatus.REVERSED
        )

    # ------------------------------------------------------------------

    def is_transfer(self) -> bool:
        return (
            self.transaction_type
            == TransactionType.TRANSFER
        )

    # ------------------------------------------------------------------

    def is_deposit(self) -> bool:
        return (
            self.transaction_type
            == TransactionType.DEPOSIT
        )

    # ------------------------------------------------------------------

    def is_withdrawal(self) -> bool:
        return (
            self.transaction_type
            == TransactionType.WITHDRAWAL
        )

# PART 3

    # ------------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        """
        Convert the transaction into a dictionary suitable for CSV
        persistence.
        """

        return {
            # ---------- BaseEntity ----------

            "entity_id":
                str(self.entity_id),

            "created_at":
                self.created_at.isoformat(),

            "updated_at":
                self.updated_at.isoformat(),

            "is_active":
                self.is_active,

            "version":
                self.version,

            # ---------- Transaction ----------

            "transaction_number":
                self.transaction_number,

            "reference_number":
                self.reference_number,

            "transaction_type":
                self.transaction_type.value,

            "transaction_status":
                self.transaction_status.value,

            "amount":
                str(self.amount.amount),

            "currency":
                self.amount.currency,

            "source_account":
                self.source_account,

            "destination_account":
                self.destination_account,

            "transaction_date":
                self.transaction_date.isoformat(),

            "description":
                self.description,

            "initiated_by":
                self.initiated_by,

            "approved_by":
                self.approved_by,

            "remarks":
                self.remarks,
        }

    # ------------------------------------------------------------------

    @classmethod
    def from_dict(
        cls,
        data: dict[str, Any],
    ) -> "Transaction":
        """
        Reconstruct a Transaction from persisted data.
        """

        transaction = cls(
            transaction_number=data["transaction_number"],

            transaction_type=TransactionType(
                data["transaction_type"]
            ),

            amount=Money(
                amount=Decimal(data["amount"]),
                currency=data["currency"],
            ),

            source_account=(
                data["source_account"] or None
            ),

            destination_account=(
                data["destination_account"] or None
            ),

            initiated_by=data["initiated_by"],

            description=data["description"],

            reference_number=(
                data["reference_number"] or None
            ),

            transaction_status=TransactionStatus(
                data["transaction_status"]
            ),
        )

        transaction._transaction_date = (
            datetime.fromisoformat(
                data["transaction_date"]
            )
        )

        transaction._approved_by = (
            data["approved_by"]
        )

        transaction._remarks = (
            data["remarks"]
        )

        # ---------- Restore BaseEntity ----------

        transaction._entity_id = UUID(
            data["entity_id"]
        )

        transaction._created_at = (
            datetime.fromisoformat(
                data["created_at"]
            )
        )

        transaction._updated_at = (
            datetime.fromisoformat(
                data["updated_at"]
            )
        )

        transaction._is_active = (
            str(data["is_active"])
            .strip()
            .lower()
            == "true"
        )

        transaction._version = int(
            data["version"]
        )

        return transaction

    # ------------------------------------------------------------------
    # Reporting Helpers
    # ------------------------------------------------------------------

    def summary(self) -> dict[str, Any]:
        """
        Return a concise summary suitable for UI presentation.
        """

        return {
            "transaction_number":
                self.transaction_number,

            "reference_number":
                self.reference_number,

            "type":
                self.transaction_type.value,

            "status":
                self.transaction_status.value,

            "amount":
                str(self.amount),

            "date":
                self.transaction_date.isoformat(),

            "source":
                self.source_account,

            "destination":
                self.destination_account,
        }

    # ------------------------------------------------------------------

    def audit_summary(self) -> dict[str, Any]:
        """
        Return detailed audit information.
        """

        return {
            "transaction_number":
                self.transaction_number,

            "reference_number":
                self.reference_number,

            "initiated_by":
                self.initiated_by,

            "approved_by":
                self.approved_by,

            "transaction_date":
                self.transaction_date.isoformat(),

            "status":
                self.transaction_status.value,

            "remarks":
                self.remarks,

            "entity_id":
                str(self.entity_id),

            "version":
                self.version,
        }

    # ------------------------------------------------------------------

    def affects_account(
        self,
        account_number: str,
    ) -> bool:
        """
        Determine whether this transaction involves the specified
        account.
        """

        Validator.required(
            account_number,
            "Account Number",
        )

        account_number = (
            account_number.strip().upper()
        )

        return (
            account_number == self.source_account
            or
            account_number == self.destination_account
        )

# PART 4

    # ------------------------------------------------------------------
    # Classification Helpers
    # ------------------------------------------------------------------

    def is_credit(self) -> bool:
        """
        Determine whether this transaction credits an account.
        """

        return self.transaction_type in (
            TransactionType.DEPOSIT,
            TransactionType.INTEREST,
            TransactionType.TRANSFER_IN,
        )

    # ------------------------------------------------------------------

    def is_debit(self) -> bool:
        """
        Determine whether this transaction debits an account.
        """

        return self.transaction_type in (
            TransactionType.WITHDRAWAL,
            TransactionType.FEE,
            TransactionType.PENALTY,
            TransactionType.TRANSFER_OUT,
        )

    # ------------------------------------------------------------------

    def is_internal_transfer(self) -> bool:
        """
        Determine whether this is an internal account transfer.
        """

        return (
            self.transaction_type == TransactionType.TRANSFER
            and bool(self.source_account)
            and bool(self.destination_account)
        )

    # ------------------------------------------------------------------

    def is_external_transaction(self) -> bool:
        """
        Determine whether this transaction involves only one account.

        Examples:
            Deposit
            Withdrawal
            Fee
            Interest
            Penalty
        """

        return not self.is_internal_transfer()

    # ------------------------------------------------------------------

    def can_reverse(self) -> bool:
        """
        Determine whether this transaction is eligible for reversal.
        """

        return (
            self.is_completed()
            and not self.is_reversed()
        )

    # ------------------------------------------------------------------

    def requires_approval(self) -> bool:
        """
        Determine whether the transaction requires approval.

        Version 1.0:
            Always returns False.

        Future versions may implement configurable approval limits.
        """

        return False

    # ------------------------------------------------------------------

    def is_financial_transaction(self) -> bool:
        """
        Return True if the transaction affects account balances.
        """

        return self.transaction_type in (
            TransactionType.DEPOSIT,
            TransactionType.WITHDRAWAL,
            TransactionType.TRANSFER,
            TransactionType.TRANSFER_IN,
            TransactionType.TRANSFER_OUT,
            TransactionType.INTEREST,
            TransactionType.FEE,
            TransactionType.PENALTY,
        )

    # ------------------------------------------------------------------
    # Display Helpers
    # ------------------------------------------------------------------

    def display_name(self) -> str:
        """
        Return a user-friendly transaction name.
        """

        return (
            self.transaction_type.value
            .replace("_", " ")
            .title()
        )

    # ------------------------------------------------------------------

    def display_amount(self) -> str:
        """
        Return the formatted transaction amount.
        """

        return str(self.amount)

    # ------------------------------------------------------------------

    def display_status(self) -> str:
        """
        Return a user-friendly transaction status.
        """

        return self.transaction_status.value.replace(
            "_",
            " ",
        ).title()

    # ------------------------------------------------------------------

    def display_summary(self) -> str:
        """
        Return a concise one-line transaction summary.
        """

        return (
            f"{self.transaction_number} | "
            f"{self.display_name()} | "
            f"{self.display_amount()} | "
            f"{self.display_status()}"
        )

    # ------------------------------------------------------------------
    # Display
    # ------------------------------------------------------------------

    def __str__(self) -> str:
        """
        Human-readable representation.
        """

        return self.display_summary()

    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        """
        Developer-friendly representation.
        """

        return (
            "Transaction("
            f"transaction_number='{self.transaction_number}', "
            f"type={self.transaction_type.name}, "
            f"status={self.transaction_status.name}, "
            f"amount={self.amount}, "
            f"source='{self.source_account}', "
            f"destination='{self.destination_account}')"
        )

# PART 5

    # ------------------------------------------------------------------
    # Equality
    # ------------------------------------------------------------------

    def __eq__(
        self,
        other: object,
    ) -> bool:
        """
        Compare two transactions.

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

    # ------------------------------------------------------------------
    # Utility Methods
    # ------------------------------------------------------------------

    def clone_for_reversal(
        self,
        transaction_number: str,
        initiated_by: str,
    ) -> "Transaction":
        """
        Create a reversal transaction.

        The new transaction references the original transaction through
        the same reference number. The AccountService is responsible for
        applying the financial effects and persisting both records.
        """

        reference = (
            self.reference_number
            if self.reference_number
            else self.transaction_number
        )

        reversal = Transaction(
            transaction_number=transaction_number,
            transaction_type=self.transaction_type,
            amount=self.amount,
            source_account=self.destination_account,
            destination_account=self.source_account,
            initiated_by=initiated_by,
            description=(
                f"Reversal of transaction "
                f"{self.transaction_number}"
            ),
            reference_number=reference,
            transaction_status=TransactionStatus.PENDING,
        )

        reversal.remarks = (
            f"Automatically generated reversal for "
            f"{self.transaction_number}"
        )

        return reversal


# ----------------------------------------------------------------------
# End of File
# ----------------------------------------------------------------------
