"""
Customer Commands

CLI command handlers for customer-related operations.

The command layer collects and validates presentation-layer input,
constructs domain objects, and delegates business operations to
CustomerService.
"""

from __future__ import annotations

from datetime import date, datetime

from cli.input_handler import InputHandler
from cli.menu_renderer import MenuRenderer
from models.customer import Customer
from models.value_objects.address import Address
from services.customer_service import CustomerService
from utils.constants import Gender
from utils.generators import IDGenerator
from utils.logger import get_logger


class CustomerCommands:
    """CLI operations for customers."""

    def __init__(
        self,
        customer_service: CustomerService,
        input_handler: InputHandler,
        menu_renderer: MenuRenderer,
    ) -> None:
        self.customer_service = customer_service
        self.input_handler = input_handler
        self.menu_renderer = menu_renderer
        self.logger = get_logger(__name__)

    # ------------------------------------------------------------------
    # Creation
    # ------------------------------------------------------------------

    def create_customer(self) -> None:
        """Collect customer data, construct a Customer, and register it."""
        try:
            customer = self._collect_customer_data()
            self.customer_service.ensure_customer_not_exists(customer)
            customer = self.customer_service.register_customer(customer)

            self.menu_renderer.display_message(
                "Customer created successfully."
            )
            self.menu_renderer.display_object(customer)

        except Exception as exc:
            self.logger.exception(
                "Failed to create customer: %s",
                str(exc),
            )
            self.menu_renderer.display_error(str(exc))

    # ------------------------------------------------------------------
    # Retrieval
    # ------------------------------------------------------------------

    def view_customer(self) -> None:
        """Retrieve and display a customer."""
        try:
            customer_id = self.input_handler.get_value("Enter customer ID: ")
            customer = self.customer_service.get_customer(customer_id)
            self.menu_renderer.display_object(customer)

        except Exception as exc:
            self.logger.exception(
                "Failed to retrieve customer: %s",
                str(exc),
            )
            self.menu_renderer.display_error(str(exc))

    def list_customers(self) -> None:
        """Display all active customers."""
        try:
            customers = self.customer_service.all_customers()
            self.menu_renderer.display_list(customers)

        except Exception as exc:
            self.logger.exception(
                "Failed to list customers: %s",
                str(exc),
            )
            self.menu_renderer.display_error(str(exc))

    # ------------------------------------------------------------------
    # Maintenance
    # ------------------------------------------------------------------

    def update_customer(self) -> None:
        """Update mutable customer contact information."""
        try:
            customer_id = self.input_handler.get_value("Enter customer ID: ")
            customer = self.customer_service.get_customer(customer_id)

            email = self.input_handler.get_optional_value("New email: ")
            phone = self.input_handler.get_optional_value("New phone: ")

            if email:
                customer.email = email
            if phone:
                customer.phone_number = phone

            customer = self.customer_service.update_customer(customer)

            self.menu_renderer.display_message(
                "Customer updated successfully."
            )
            self.menu_renderer.display_object(customer)

        except Exception as exc:
            self.logger.exception(
                "Failed to update customer: %s",
                str(exc),
            )
            self.menu_renderer.display_error(str(exc))

    def delete_customer(self) -> None:
        """Archive a customer after explicit confirmation."""
        try:
            customer_id = self.input_handler.get_value("Enter customer ID: ")

            confirmation = self.input_handler.get_confirmation(
                "Confirm customer deletion?"
            )
            if not confirmation:
                return

            self.customer_service.archive_customer(customer_id)
            self.menu_renderer.display_message(
                "Customer archived successfully."
            )

        except Exception as exc:
            self.logger.exception(
                "Failed to delete customer: %s",
                str(exc),
            )
            self.menu_renderer.display_error(str(exc))

    # ------------------------------------------------------------------
    # Input / Domain Construction
    # ------------------------------------------------------------------

    def _collect_customer_data(self) -> Customer:
        """Collect all required fields and construct a Customer entity."""
        first_name = self.input_handler.get_value("First name: ")
        middle_name = self.input_handler.get_optional_value("Middle name: ")
        last_name = self.input_handler.get_value("Last name: ")

        date_of_birth = self.input_handler.get_date(
            "Date of birth",
            date_format="%Y-%m-%d",
        )
        if isinstance(date_of_birth, datetime):
            date_of_birth = date_of_birth.date()

        gender = self._collect_gender()
        national_id = self.input_handler.get_value("National ID: ")
        email = self.input_handler.get_value("Email: ")
        phone_number = self.input_handler.get_value("Phone number: ")

        address = Address(
            address_line_1=self.input_handler.get_value("Address line 1: "),
            address_line_2=self.input_handler.get_optional_value(
                "Address line 2: "
            ),
            city=self.input_handler.get_value("City: "),
            state_or_province=self.input_handler.get_value(
                "State / Province: "
            ),
            postal_code=self.input_handler.get_value("Postal code: "),
            country=self.input_handler.get_value("Country: "),
        )

        kyc_completed = self.input_handler.get_confirmation(
            "Has KYC been completed?"
        )

        return Customer(
            customer_id=IDGenerator.customer_id(),
            first_name=first_name,
            middle_name=middle_name,
            last_name=last_name,
            date_of_birth=date_of_birth,
            gender=gender,
            national_id=national_id,
            email=email,
            phone_number=phone_number,
            address=address,
            kyc_completed=kyc_completed,
        )

    def _collect_gender(self) -> Gender:
        """Collect and normalize a Gender enum value."""
        value = self.input_handler.get_value(
            "Gender (Male/Female/Other/Not Specified): "
        )
        normalized = value.strip().lower()

        for gender in Gender:
            if normalized in {
                gender.value.lower(),
                gender.name.lower().replace("_", " "),
            }:
                return gender

        raise ValueError(
            "Invalid gender. Use Male, Female, Other, or Not Specified."
        )

    def _collect_customer_updates(self) -> dict[str, str | None]:
        """Collect optional contact updates for compatibility with callers."""
        return {
            "email": self.input_handler.get_optional_value("New email: "),
            "phone": self.input_handler.get_optional_value("New phone: "),
        }
