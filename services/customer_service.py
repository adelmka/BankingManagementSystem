"""
===============================================================================
Banking Management System (BMS)

File        : customer_service.py
Description : Customer Application Service.

Author      : Adel Alawiyat / ChatGPT
Version     : 2.1.0
Python      : 3.13+

===============================================================================
"""

from __future__ import annotations

from typing import Iterable

from models.customer import Customer

from repositories.customer_repository import (
    CustomerRepository,
)

from services.base_service import BaseService

from exceptions import (
    EntityAlreadyExistsError,
    EntityNotFoundError,
    ValidationError,
)

class CustomerService(
    BaseService[Customer],
):
    """
    Application service responsible for customer-related business
    operations.
    """

    # ------------------------------------------------------------------
    # Constructor
    # ------------------------------------------------------------------

    def __init__(
        self,
        repository: CustomerRepository,
    ) -> None:
        """
        Initialize the customer service.
        """

        super().__init__(
            repository=repository,
        )

    # ------------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------------

    def register_customer(
        self,
        customer: Customer,
    ) -> Customer:
        """
        Register a new customer.

        Raises
        ------
        ValidationError
            If business validation fails.

        EntityAlreadyExistsError
            If the customer already exists.
        """

        self._before_operation(
            "register_customer"
        )

        self._validate(
            customer
        )

        with self._operation_scope():

            self._repository.add_customer(
                customer
            )

        self._after_operation(
            "register_customer"
        )

        return customer

    # ------------------------------------------------------------------
    # Lookup
    # ------------------------------------------------------------------

    def find_customer(
        self,
        customer_number: str,
        *,
        active_only: bool = True,
    ) -> Customer | None:
        """
        Return the customer with the specified customer number.

        By default, only active customers are returned.
        Set active_only=False to include inactive customers.
        """

        return (
            self._repository
            .find_by_customer_number(
                customer_number,
                active_only=active_only,
            )
        )

    # ------------------------------------------------------------------

    def get_customer(
        self,
        customer_number: str,
    ) -> Customer:
        """
        Return the specified customer.

        Raises
        ------
        EntityNotFoundError
        """

        return (
            self._repository
            .get_or_raise(
                customer_number
            )
        )

    # ------------------------------------------------------------------

    def customer_exists(
        self,
        customer_number: str,
    ) -> bool:
        """
        Determine whether a customer exists.
        """

        return (
            self._repository
            .customer_exists(
                customer_number
            )
        )

    # ------------------------------------------------------------------

    def all_customers(
        self,
    ) -> list[Customer]:
        """
        Return all active customers.
        """

        return list(
            self._repository
        )

# PART 2

    # ------------------------------------------------------------------
    # Customer Maintenance
    # ------------------------------------------------------------------

    # ------------------------------------------------------------------
    # Customer Lifecycle
    # ------------------------------------------------------------------

    def update_customer(
        self,
        customer: Customer,
    ) -> Customer:
        """
        Persist changes made to an existing customer.
        """

        self._before_operation(
            "update_customer"
        )

        self._validate(
            customer
        )

        if not self._repository.exists(
            customer.entity_id
        ):
            raise EntityNotFoundError(
                f"Customer '{customer.customer_id}' does not exist."
            )

        with self._operation_scope():

            self._repository.save_entity(
                customer
            )

        self._after_operation(
            "update_customer"
        )

        return customer


    # ------------------------------------------------------------------

    def deactivate_customer(
        self,
        customer_number: str,
    ) -> Customer:
        """
        Deactivate an active customer.
        """

        customer = self.get_customer(
            customer_number
        )

        customer.close_customer()

        return self.update_customer(
            customer
        )
        
    # ------------------------------------------------------------------

    def activate_customer(
        self,
        customer_number: str,
    ) -> Customer:
        """
        Activate a previously inactive customer.
        """

        customer = self._repository.get_or_raise(
            customer_number,
            active_only=False,
        )

        customer.activate_customer()

        return self.update_customer(
            customer
        )

    # ------------------------------------------------------------------
    
    def reactivate_customer(
        self,
        customer_number: str,
    ) -> Customer:
        """
        Reactivate a previously inactive customer.
        """

        return self.activate_customer(
            customer_number
        )


    # ------------------------------------------------------------------

    def archive_customer(
        self,
        customer_number: str,
    ) -> bool:
        """
        Soft-delete a customer.
        """

        customer = self.get_customer(
            customer_number
        )

        self._before_operation(
            "archive_customer"
        )

        with self._operation_scope():

            result = self._repository.delete_entity(
                customer.entity_id
            )

        self._after_operation(
            "archive_customer"
        )

        return result

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def _validate(
        self,
        customer: Customer,
    ) -> None:
        """
        Perform business validation before persistence.
        """

        if customer is None:
            raise ValidationError(
                "Customer cannot be None."
            )

# PART 3

    # ------------------------------------------------------------------
    # Search Operations
    # ------------------------------------------------------------------

    def find_by_national_id(
        self,
        national_id: str,
    ) -> Customer | None:
        """
        Return the customer with the specified national ID.
        """

        return (
            self._repository
            .find_by_national_id(
                national_id
            )
        )

    # ------------------------------------------------------------------

    def find_by_email(
        self,
        email: str,
    ) -> Customer | None:
        """
        Return the customer having the specified email address.
        """

        return (
            self._repository
            .find_by_email(
                email
            )
        )

    # ------------------------------------------------------------------

    def find_by_phone(
        self,
        phone_number: str,
    ) -> Customer | None:
        """
        Return the customer having the specified phone number.
        """

        return (
            self._repository
            .find_by_phone(
                phone_number
            )
        )

    # ------------------------------------------------------------------

    def search_by_name(
        self,
        search_text: str,
    ) -> list[Customer]:
        """
        Perform a case-insensitive customer name search.
        """

        return (
            self._repository
            .search_by_name(
                search_text
            )
        )

    # ------------------------------------------------------------------
    # Status Queries
    # ------------------------------------------------------------------

    def active_customers(
        self,
    ) -> list[Customer]:
        """
        Return all active customers.
        """

        return (
            self._repository
            .find_active_customers()
        )

    # ------------------------------------------------------------------

    def inactive_customers(
        self,
    ) -> list[Customer]:
        """
        Return all inactive customers.
        """

        return (
            self._repository
            .find_inactive_customers()
        )

    # ------------------------------------------------------------------

    def active_customer_count(
        self,
    ) -> int:
        """
        Return the number of active customers.
        """

        return len(
            self.active_customers()
        )

    # ------------------------------------------------------------------

    def inactive_customer_count(
        self,
    ) -> int:
        """
        Return the number of inactive customers.
        """

        return len(
            self.inactive_customers()
        )

    # ------------------------------------------------------------------
    # Statistics
    # ------------------------------------------------------------------

    def statistics(
        self,
    ) -> dict[str, int]:
        """
        Return customer statistics.
        """

        return {
            "total_customers":
                self.entity_count,

            "active_customers":
                self.active_customer_count(),

            "inactive_customers":
                self.inactive_customer_count(),
        }

# PART 4

    # ------------------------------------------------------------------
    # Business Rules
    # ------------------------------------------------------------------

    def ensure_customer_not_exists(
        self,
        customer: Customer,
    ) -> None:
        """
        Ensure that the customer does not already exist.

        Duplicate detection is based on business identifiers.
        """

        if self.find_by_national_id(
            customer.national_id
        ) is not None:

            raise EntityAlreadyExistsError(
                "A customer with the same national ID already exists."
            )

        if self.find_by_email(
            customer.email
        ) is not None:

            raise EntityAlreadyExistsError(
                "A customer with the same email already exists."
            )

    # ------------------------------------------------------------------

    def ensure_customer_exists(
        self,
        customer_number: str,
    ) -> Customer:
        """
        Ensure that the specified customer exists.
        """

        return self.get_customer(
            customer_number
        )

    # ------------------------------------------------------------------

    def is_customer_eligible(
        self,
        customer_number: str,
    ) -> bool:
        """
        Determine whether the customer is eligible for banking services.
        """

        customer = self.get_customer(
            customer_number
        )

        return (
            customer.is_active
            and not customer.is_deleted
        )

    # ------------------------------------------------------------------

    def profile_is_complete(
        self,
        customer_number: str,
    ) -> bool:
        """
        Determine whether the customer's profile is complete.
        """

        customer = self.get_customer(
            customer_number
        )

        required_fields = (
            customer.first_name,
            customer.last_name,
            customer.national_id,
            customer.email,
            customer.phone_number,
        )

        return all(
            bool(field)
            for field in required_fields
        )

    # ------------------------------------------------------------------

    def validate_customer_for_account_opening(
        self,
        customer_number: str,
    ) -> Customer:
        """
        Validate that a customer may open a bank account.
        """

        customer = self.ensure_customer_exists(
            customer_number
        )

        if not customer.is_active:

            raise ValidationError(
                "Customer is inactive."
            )

        if customer.is_deleted:

            raise ValidationError(
                "Customer has been archived."
            )

        if not self.profile_is_complete(
            customer_number
        ):

            raise ValidationError(
                "Customer profile is incomplete."
            )

        return customer

    # ------------------------------------------------------------------
    # Export Helpers
    # ------------------------------------------------------------------

    def customer_directory(
        self,
    ) -> list[Customer]:
        """
        Return customers ordered alphabetically.
        """

        return sorted(
            self.all_customers(),
            key=lambda customer: (
                customer.last_name.upper(),
                customer.first_name.upper(),
            ),
        )

# PART 5

    # ------------------------------------------------------------------
    # Summary Operations
    # ------------------------------------------------------------------

    def customer_summary(
        self,
        customer_number: str,
    ) -> dict[str, object]:
        """
        Return a business summary for a customer.
        """

        customer = self.get_customer(
            customer_number
        )

        return {
            "customer_number": customer.customer_number,
            "full_name": customer.full_name,
            "national_id": customer.national_id,
            "email": customer.email,
            "phone_number": customer.phone_number,
            "status": (
                "Active"
                if customer.is_active
                else "Inactive"
            ),
            "archived": customer.is_deleted,
            "created_on": customer.created_on,
        }

    # ------------------------------------------------------------------

    def customer_listing(
        self,
    ) -> list[dict[str, object]]:
        """
        Return a simplified listing of all customers.
        """

        return [
            self.customer_summary(
                customer.customer_number
            )
            for customer in self.customer_directory()
        ]

    # ------------------------------------------------------------------
    # Health / Integrity
    # ------------------------------------------------------------------

    def validate_repository(
        self,
    ) -> bool:
        """
        Perform a simple repository integrity check.
        """

        repository = self._repository

        return (
            repository.count
            == len(repository)
        )

    # ------------------------------------------------------------------

    def repository_statistics(
        self,
    ) -> dict[str, object]:
        """
        Return repository statistics.
        """

        return (
            self._repository.statistics()
        )

    # ------------------------------------------------------------------
    # Convenience Operations
    # ------------------------------------------------------------------

    def refresh(
        self,
    ) -> None:
        """
        Reload customer data from persistent storage.
        """

        self._refresh()

    # ------------------------------------------------------------------

    def save_changes(
        self,
    ) -> None:
        """
        Persist all pending customer changes.
        """

        self._flush()

    # ------------------------------------------------------------------

    def customer_count(
        self,
    ) -> int:
        """
        Return the total number of customers.
        """

        return self.entity_count

    # ------------------------------------------------------------------

    def has_customers(
        self,
    ) -> bool:
        """
        Determine whether any customers exist.
        """

        return (
            self.customer_count()
            > 0
        )

# PART 6

    # ------------------------------------------------------------------
    # Consistency
    # ------------------------------------------------------------------

    def ensure_repository_is_valid(
        self,
    ) -> None:
        """
        Verify that the underlying repository is in a valid state.

        Raises
        ------
        PersistenceError
            If the repository integrity check fails.
        """

        if not self.validate_repository():

            raise PersistenceError(
                "Customer repository integrity validation failed."
            )

    # ------------------------------------------------------------------
    # Display
    # ------------------------------------------------------------------

    def __str__(
        self,
    ) -> str:
        """
        Return a human-readable service representation.
        """

        return (
            f"{self.__class__.__name__}("
            f"customers={self.customer_count()})"
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
            f"customers={self.customer_count()})"
        )


# ----------------------------------------------------------------------
# End of File
# ----------------------------------------------------------------------
