"""
===============================================================================
Banking Management System (BMS)

File        : customer_repository.py
Description : Customer Repository.

Author      : Adel Alawiyat / ChatGPT
Version     : 2.1.0
Python      : 3.13+

===============================================================================
"""

from __future__ import annotations

from pathlib import Path

import config

from models.customer import Customer

from repositories.base_repository import BaseRepository

from exceptions import (
    EntityAlreadyExistsError,
    EntityNotFoundError,
)

class CustomerRepository(
    BaseRepository[Customer],
):
    """
    Repository responsible for Customer persistence and retrieval.
    """

    ENTITY_CLASS = Customer

    CSV_FILE: Path = config.CUSTOMERS_FILE

    # ------------------------------------------------------------------
    # Constructor
    # ------------------------------------------------------------------

    def __init__(self) -> None:
        """
        Initialize the customer repository.
        """

        super().__init__()

    # ---------------------------------------------------------

    @staticmethod
    def _normalize(
        value: str,
    ) -> str:
        """
        Normalize text for case-insensitive comparisons.
        """

        return value.strip().upper()

    # ---------------------------------------------------------
    
    # ------------------------------------------------------------------
    # Customer Number
    # ------------------------------------------------------------------

    def find_by_customer_number(
        self,
        customer_number: str,
        *,
        active_only: bool = True,
    ) -> Customer | None:
        """
        Find a customer using the customer number.
        """

        customer_number = (
            customer_number.strip().upper()
        )

        return self.find_first(
            lambda customer:
            customer.customer_id
            == customer_number,
            active_only=active_only,
        )

    # ------------------------------------------------------------------

    def exists_customer_number(
        self,
        customer_number: str,
    ) -> bool:
        """
        Determine whether a customer number already exists.
        """

        return (
            self.find_by_customer_number(
                customer_number
            )
            is not None
        )

    # ------------------------------------------------------------------
    # National ID
    # ------------------------------------------------------------------

    def find_by_national_id(
        self,
        national_id: str,
    ) -> Customer | None:
        """
        Find a customer using the national ID.
        """

        national_id = (
            national_id.strip()
        )

        return self.find_first(
            lambda customer:
            customer.national_id
            == national_id
        )

    # ------------------------------------------------------------------

    def exists_national_id(
        self,
        national_id: str,
    ) -> bool:
        """
        Determine whether a national ID already exists.
        """

        return (
            self.find_by_national_id(
                national_id
            )
            is not None
        )

    # ------------------------------------------------------------------
    # Passport Number
    # ------------------------------------------------------------------
    """ --- remove because it doesn't exist in the customer model
    def find_by_passport_number(
        self,
        passport_number: str,
    ) -> Customer | None:
        
        Find a customer using the passport number.
        

        passport_number = (
            passport_number.strip().upper()
        )

        return self.find_first(
            lambda customer:
            customer.passport_number
            == passport_number
        )
     """
        
# PART 2

    # ------------------------------------------------------------------
    # Passport Number
    # ------------------------------------------------------------------
    """ --- remove because it doesn't exist in the customer model
    def exists_passport_number(
        self,
        passport_number: str,
    ) -> bool:
        
        Determine whether a passport number already exists.
        

        return (
            self.find_by_passport_number(
                passport_number
            )
            is not None
        )
    """
    # ------------------------------------------------------------------
    # Email Address
    # ------------------------------------------------------------------

    def find_by_email(
        self,
        email: str,
    ) -> Customer | None:
        """
        Find a customer using the email address.
        """

        email = self._normalize(email)

        return self.find_first(
            lambda customer:
            self._normalize(customer.email)
            == email
        )

    # ------------------------------------------------------------------

    def exists_email(
        self,
        email: str,
    ) -> bool:
        """
        Determine whether an email address already exists.
        """

        return (
            self.find_by_email(email)
            is not None
        )

    # ------------------------------------------------------------------
    # Mobile Number
    # ------------------------------------------------------------------

    def find_by_mobile_number(
        self,
        mobile_number: str,
    ) -> Customer | None:
        """
        Find a customer using the mobile number.
        """

        mobile_number = mobile_number.strip()

        return self.find_first(
            lambda customer:
            customer.phone_number.strip()
            == mobile_number
        )

    # ------------------------------------------------------------------

    def exists_mobile_number(
        self,
        mobile_number: str,
    ) -> bool:
        """
        Determine whether a mobile number already exists.
        """

        return (
            self.find_by_mobile_number(
                mobile_number
            )
            is not None
        )

    # ------------------------------------------------------------------
    # Active Customers
    # ------------------------------------------------------------------

    def find_active_customers(
        self,
    ) -> list[Customer]:
        """
        Return all active customers.
        """

        return self.find_all(
            active_only=True
        )

    # ------------------------------------------------------------------

    def find_inactive_customers(
        self,
    ) -> list[Customer]:
        """
        Return all inactive customers.
        """

        return self.find_where( 
              lambda customer: 
              not customer.is_active, 
              active_only=False,
        )

    # ------------------------------------------------------------------
    # Status Queries
    # ------------------------------------------------------------------

    def has_active_customers(
        self,
    ) -> bool:
        """
        Determine whether the repository contains active customers.
        """

        return self.any_match(
            lambda customer:
            customer.is_active
        )

    # ------------------------------------------------------------------

    def active_customer_count(
        self,
    ) -> int:
        """
        Return the number of active customers.
        """

        return self.count_where(
            lambda customer:
            customer.is_active
        )

    # ------------------------------------------------------------------

    def inactive_customer_count(
        self,
    ) -> int:
        """
        Return the number of inactive customers.
        """

        return self.count_where(
            lambda customer:
            not customer.is_active,
            active_only=False,
        )

# PART 3

    # ------------------------------------------------------------------
    # Name Searches
    # ------------------------------------------------------------------

    def find_by_first_name(
        self,
        first_name: str,
    ) -> list[Customer]:
        """
        Return all customers with the specified first name.
        """

        first_name = self._normalize(first_name)

        return self.find_where(
            lambda customer:
            self._normalize(customer.first_name)
            == first_name
        )

    # ------------------------------------------------------------------

    def find_by_last_name(
        self,
        last_name: str,
    ) -> list[Customer]:
        """
        Return all customers with the specified last name.
        """

        last_name = self._normalize(last_name)

        return self.find_where(
            lambda customer:
            self._normalize(customer.last_name)
            == last_name
        )

    # ------------------------------------------------------------------

    def find_by_full_name(
        self,
        full_name: str,
    ) -> list[Customer]:
        """
        Return customers whose full name matches.
        """

        full_name = self._normalize(full_name)

        return self.find_where(
            lambda customer:
            self._normalize(customer.full_name)
            == full_name
        )

    # ------------------------------------------------------------------
    # Address Searches
    # ------------------------------------------------------------------

    def find_by_city(
        self,
        city: str,
    ) -> list[Customer]:
        """
        Return customers residing in the specified city.
        """

        city = self._normalize(city)

        return self.find_where(
            lambda customer:
            self._normalize(customer.address.city)
            == city
        )

    # ------------------------------------------------------------------

    def find_by_country(
        self,
        country: str,
    ) -> list[Customer]:
        """
        Return customers residing in the specified country.
        """

        country = self._normalize(country)

        return self.find_where(
            lambda customer:
            self._normalize(customer.address.country)
            == country
        )

    # ------------------------------------------------------------------
    # General Search
    # ------------------------------------------------------------------

    def search(
        self,
        text: str,
    ) -> list[Customer]:
        """
        Perform a case-insensitive search across common customer fields.
        -- this was removed or text in self._normalize(customer.passport_number)
        from below checks.
        """

        text = self._normalize(text)

        return self.find_where(
            lambda customer:
                text in self._normalize(customer.customer_id)
                or text in self._normalize(customer.first_name)
                or text in self._normalize(customer.last_name)
                or text in self._normalize(customer.full_name)
                or text in self._normalize(customer.email)
                or text in self._normalize(customer.phone_number)
                or text in self._normalize(customer.national_id)
                or text in self._normalize(customer.address.city)
                or text in self._normalize(customer.address.country)
        )

    # ------------------------------------------------------------------
    # Statistics
    # ------------------------------------------------------------------

    def customer_statistics(
        self,
    ) -> dict[str, int]:
        """
        Return high-level customer statistics.
        """

        total = self.count

        active = self.active_customer_count()

        inactive = self.inactive_customer_count()

        return {
            "total_customers": total,
            "active_customers": active,
            "inactive_customers": inactive,
        }

# PART 4

    # ------------------------------------------------------------------
    # Statistics
    # ------------------------------------------------------------------

    def statistics(self) -> dict[str, int]:
        """
        Return customer-specific statistics.
        """

        return {
            "total_customers": self.count,
            "active_customers": self.active_customer_count(),
            "inactive_customers": self.inactive_customer_count(),
        }

    # ------------------------------------------------------------------
    # Convenience Methods
    # ------------------------------------------------------------------

    def customer_exists(
        self,
        customer_number: str,
    ) -> bool:
        """
        Determine whether the specified customer exists.
        """

        return self.exists_customer_number(
            customer_number
        )

    # ------------------------------------------------------------------

    def get_or_raise(
        self,
        customer_number: str,
        *,
        active_only: bool = True,
    ) -> Customer:
        """
        Return the customer with the specified customer number.

        Raises
        ------
        EntityNotFoundError
            If the customer does not exist.
        """

        customer = self.find_by_customer_number(
            customer_number,
            active_only=active_only,
        )

        if customer is None:
            raise EntityNotFoundError(
                f"Customer '{customer_number}' was not found."
            )

        return customer

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def validate_unique_customer(
        self,
        customer: Customer,
    ) -> None:
        """
        Validate that all unique customer identifiers are available.

        Raises
        ------
        EntityAlreadyExistsError
            If any unique identifier already exists.
        """

        if self.exists_customer_number(
            customer.customer_id
        ):
            raise EntityAlreadyExistsError(
                "Customer number already exists."
            )

        if customer.national_id and self.exists_national_id(
            customer.national_id
        ):
            raise EntityAlreadyExistsError(
                "National ID already exists."
            )
        
        """ --- remove because it doesn't exist in the customer model
        if customer.passport_number and self.exists_passport_number(
            customer.passport_number
        ):
            raise EntityAlreadyExistsError(
                "Passport number already exists."
            )
        """
        if customer.email and self.exists_email(
            customer.email
        ):
            raise EntityAlreadyExistsError(
                "Email address already exists."
            )

        if customer.phone_number and self.exists_mobile_number(
            customer.phone_number
        ):
            raise EntityAlreadyExistsError(
                "Mobile number already exists."
            )

    # ------------------------------------------------------------------

    def add_customer(
        self,
        customer: Customer,
    ) -> None:
        """
        Validate and persist a new customer.
        """

        self.validate_unique_customer(
            customer
        )

        self.save_entity(customer)

    # ------------------------------------------------------------------
    # Display
    # ------------------------------------------------------------------

    def __str__(self) -> str:
        """
        Human-readable representation.
        """

        return (
            f"CustomerRepository("
            f"customers={self.count})"
        )

    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        """
        Developer-friendly representation.
        """

        return (
            f"CustomerRepository("
            f"count={self.count}, "
            f"file='{self.CSV_FILE}')"
        )


# ----------------------------------------------------------------------
# End of File
# ----------------------------------------------------------------------
