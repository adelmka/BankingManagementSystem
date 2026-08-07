"""
===============================================================================
Banking Management System (BMS)

File        : customer.py
Description : Customer domain entity.

Author      : Adel Alawiyat / ChatGPT
Version     : 2.1.0
Python      : 3.13+

Customer is the primary business entity representing a bank customer.

===============================================================================
"""

from __future__ import annotations

from datetime import UTC, date, datetime
from typing import Any
from uuid import UUID

from models.person import Person
from models.value_objects.address import Address
from utils.constants import (
    CustomerStatus,
    Gender,
)
from utils.validators import Validator


class Customer(Person):
    """
    Concrete implementation of a banking customer.
    """

    # ------------------------------------------------------------------
    # Constructor
    # ------------------------------------------------------------------

    def __init__(
        self,
        customer_id: str,
        first_name: str,
        last_name: str,
        date_of_birth: date,
        gender: Gender,
        national_id: str,
        email: str,
        phone_number: str,
        address: Address,
        middle_name: str = "",
        customer_status: CustomerStatus = CustomerStatus.ACTIVE,
        registration_date: date | None = None,
        kyc_completed: bool = False,
    ) -> None:
        """
        Initialize a Customer.
        """

        super().__init__(
            first_name=first_name,
            middle_name=middle_name,
            last_name=last_name,
            date_of_birth=date_of_birth,
            gender=gender,
            national_id=national_id,
            email=email,
            phone_number=phone_number,
            address=address,
        )

        self._initializing = True

        try:
            self._customer_id = ""
            self._customer_status = CustomerStatus.ACTIVE
            self._registration_date = date.today() #datetime.now(UTC).date()
            self._kyc_completed = False
            self._accounts: list[str] = []

            self.customer_id = customer_id
            self.customer_status = customer_status
            self.registration_date = (
                registration_date or date.today() #datetime.now(UTC).date()
            )
            self.kyc_completed = kyc_completed

        finally:
            self._initializing = False

    # ------------------------------------------------------------------
    # Customer ID
    # ------------------------------------------------------------------

    @property
    def customer_id(self) -> str:
        """
        Return the customer identifier.
        """
        return self._customer_id

    @customer_id.setter
    def customer_id(self, value: str) -> None:
        """
        Set the customer identifier.
        """

        Validator.required(value, "Customer ID")
        Validator.max_length(value, 20, "Customer ID")

        self._customer_id = value.strip().upper()

        self.touch()

    # ------------------------------------------------------------------
    # Customer Status
    # ------------------------------------------------------------------

    @property
    def customer_status(self) -> CustomerStatus:
        """
        Return the customer's current status.
        """
        return self._customer_status

    @customer_status.setter
    def customer_status(
        self,
        value: CustomerStatus,
    ) -> None:
        """
        Set the customer status.
        """

        if not isinstance(value, CustomerStatus):
            raise TypeError(
                "customer_status must be a CustomerStatus."
            )

        self._customer_status = value

        self.touch()

    # ------------------------------------------------------------------
    # Registration Date
    # ------------------------------------------------------------------

    @property
    def registration_date(self) -> date:
        """
        Return the customer registration date.
        """
        return self._registration_date

    @registration_date.setter
    def registration_date(self, value: date) -> None:
        """
        Set the customer registration date.
        """
        # print(f"registration_date setter called: {value}")
        
        Validator.date_not_future(
            value,
            "Registration Date",
        )

        self._registration_date = value

        self.touch()

    # ------------------------------------------------------------------
    # KYC Status
    # ------------------------------------------------------------------

    @property
    def kyc_completed(self) -> bool:
        """
        Indicates whether Know Your Customer (KYC) verification has been
        completed.
        """
        return self._kyc_completed

    @kyc_completed.setter
    def kyc_completed(self, value: bool) -> None:
        """
        Update the KYC completion status.
        """

        if not isinstance(value, bool):
            raise TypeError(
                "kyc_completed must be a bool."
            )

        self._kyc_completed = value

        self.touch()

    # ------------------------------------------------------------------
    # Accounts
    # ------------------------------------------------------------------

    @property
    def accounts(self) -> tuple[str, ...]:
        """
        Return a read-only collection of account numbers owned by the customer.
        """

        return tuple(self._accounts)

    @property
    def account_count(self) -> int:
        """
        Return the number of accounts owned by the customer.
        """

        return len(self._accounts)

    # ------------------------------------------------------------------
    # Account Management
    # ------------------------------------------------------------------

    def add_account(
        self,
        account_number: str,
    ) -> None:
        """
        Associate an account with this customer.

        Parameters
        ----------
        account_number : str
            Account number to associate.

        Raises
        ------
        ValueError
            If the account already exists.
        """

        Validator.required(
            account_number,
            "Account Number",
        )

        account_number = account_number.strip().upper()

        if account_number in self._accounts:
            raise ValueError(
                f"Account '{account_number}' is already assigned "
                "to this customer."
            )

        self._accounts.append(account_number)

        self.touch()

    # ------------------------------------------------------------------

    def remove_account(
        self,
        account_number: str,
    ) -> None:
        """
        Remove an account association.

        Raises
        ------
        ValueError
            If the account is not associated with this customer.
        """

        account_number = account_number.strip().upper()

        if account_number not in self._accounts:
            raise ValueError(
                f"Account '{account_number}' does not exist."
            )

        self._accounts.remove(account_number)

        self.touch()

    # ------------------------------------------------------------------

    def has_account(
        self,
        account_number: str,
    ) -> bool:
        """
        Determine whether the customer owns the specified account.
        """

        return (
            account_number.strip().upper()
            in self._accounts
        )

    # ------------------------------------------------------------------

    def clear_accounts(self) -> None:
        """
        Remove all account associations.

        This method is intended primarily for administrative
        maintenance and testing.
        """

        self._accounts.clear()

        self.touch()

    # ------------------------------------------------------------------
    # Business Operations
    # ------------------------------------------------------------------

    def activate_customer(self) -> None:
        """
        Activate the customer.
        """

        self.customer_status = CustomerStatus.ACTIVE

        self.activate()

    # ------------------------------------------------------------------

    def suspend_customer(self) -> None:
        """
        Suspend the customer.
        """

        self.customer_status = CustomerStatus.SUSPENDED

    # ------------------------------------------------------------------

    def close_customer(self) -> None:
        """
        Close the customer.

        Historical information is preserved.
        """

        self.customer_status = CustomerStatus.INACTIVE

        self.deactivate()

    # ------------------------------------------------------------------
    # Person Implementation
    # ------------------------------------------------------------------

    def get_identifier(self) -> str:
        """
        Return the business identifier for this customer.
        """

        return self.customer_id

# PART 3

    # ------------------------------------------------------------------
    # CSV Serialization Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _serialize_accounts(
        accounts: list[str],
    ) -> str:
        """
        Convert the account collection into a pipe-separated string
        suitable for CSV persistence.
        """

        if not accounts:
            return ""

        return "|".join(accounts)

    # ------------------------------------------------------------------

    @staticmethod
    def _deserialize_accounts(
        value: str,
    ) -> list[str]:
        """
        Convert a pipe-separated account string into a list.
        """

        if not value:
            return []

        return [
            account.strip().upper()
            for account in value.split("|")
            if account.strip()
        ]

    # ------------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        """
        Convert the customer into a dictionary suitable
        for CSV persistence.
        """

        data = self._base_dict()

        data.update(
            {
                "customer_id": self.customer_id,
                "customer_status": self.customer_status.value,
                "registration_date":
                    self.registration_date.isoformat(),
                "kyc_completed": self.kyc_completed,
                "accounts":
                    self._serialize_accounts(self._accounts),
            }
        )

        return data

    # ------------------------------------------------------------------

    @classmethod
    def from_dict(
        cls,
        data: dict[str, Any],
    ) -> "Customer":
        """
        Reconstruct a Customer from persisted data.
        """

        customer = cls(
            customer_id=data["customer_id"],
            first_name=data["first_name"],
            middle_name=data.get("middle_name", ""),
            last_name=data["last_name"],
            date_of_birth=date.fromisoformat(
                data["date_of_birth"]
            ),
            gender=Gender(data["gender"]),
            national_id=data["national_id"],
            email=data["email"],
            phone_number=data["phone_number"],
            address=Address.from_dict(data),
            customer_status=CustomerStatus(
                data["customer_status"]
            ),
            registration_date=date.fromisoformat(
                data["registration_date"]
            ),
            kyc_completed=(
                str(data["kyc_completed"]).lower() == "true"
            ),
        )

        customer._accounts = cls._deserialize_accounts(
            data.get("accounts", "")
        )

        return customer

    # ------------------------------------------------------------------
    # Display Helpers
    # ------------------------------------------------------------------

    def customer_summary(self) -> dict[str, Any]:
        """
        Return a summary of the customer's information.

        Intended for UI presentation and reporting.
        """

        return {
            "customer_id": self.customer_id,
            "name": self.full_name,
            "status": self.customer_status.value,
            "email": self.email,
            "phone_number": self.phone_number,
            "accounts": self.account_count,
            "kyc_completed": self.kyc_completed,
            "registration_date":
                self.registration_date.isoformat(),
        }

    # ------------------------------------------------------------------

    def display_name(self) -> str:
        """
        Return the preferred display name.

        Overrides Person.display_name().
        """

        return (
            f"{self.full_name} "
            f"({self.customer_id})"
        )

    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        """
        Developer-friendly representation.
        """

        return (
            f"Customer("
            f"customer_id='{self.customer_id}', "
            f"name='{self.full_name}', "
            f"accounts={self.account_count}, "
            f"status='{self.customer_status.value}')"
        )

# PART 4

        # --------------------------------------------------------------
        # Restore BaseEntity state from persistence
        # --------------------------------------------------------------

        customer._entity_id = UUID(data["entity_id"])

        customer._created_at = datetime.fromisoformat(
            data["created_at"]
        )

        customer._updated_at = datetime.fromisoformat(
            data["updated_at"]
        )

        customer._is_active = (
            str(data["is_active"]).strip().lower()
            == "true"
        )

        customer._version = int(data["version"])

        return customer

    # ------------------------------------------------------------------
    # Utility Methods
    # ------------------------------------------------------------------

    @property
    def has_accounts(self) -> bool:
        """
        Determine whether the customer owns at least one account.
        """

        return self.account_count > 0

    # ------------------------------------------------------------------

    @property
    def account_numbers(self) -> tuple[str, ...]:
        """
        Return the customer's account numbers as an immutable tuple.
        """

        return tuple(self._accounts)

    # ------------------------------------------------------------------

    def complete_kyc(self) -> None:
        """
        Mark the customer's Know Your Customer (KYC) verification as
        completed.
        """

        self.kyc_completed = True

    # ------------------------------------------------------------------

    def revoke_kyc(self) -> None:
        """
        Revoke the customer's KYC verification.

        Intended for administrative use.
        """

        self.kyc_completed = False

    # ------------------------------------------------------------------

    def is_active_customer(self) -> bool:
        """
        Determine whether the customer is currently active.

        Returns
        -------
        bool
        """

        return (
            self.customer_status == CustomerStatus.ACTIVE
            and self.is_active
        )

    # ------------------------------------------------------------------

    def can_open_new_account(self) -> bool:
        """
        Determine whether the customer is permitted to open a new
        account.

        Business Rules
        --------------
        • Customer must be active.
        • KYC must be completed.
        """

        return (
            self.is_active_customer()
            and self.kyc_completed
        )

    # ------------------------------------------------------------------

    def can_transact(self) -> bool:
        """
        Determine whether the customer may perform banking
        transactions.
        """

        return (
            self.is_active_customer()
            and self.kyc_completed
            and self.has_accounts
        )

    # ------------------------------------------------------------------

    def __str__(self) -> str:
        """
        Human-readable representation.
        """

        return (
            f"{self.customer_id} - "
            f"{self.full_name}"
        )

# ----------------------------------------------------------------------
# End of File
# ----------------------------------------------------------------------

