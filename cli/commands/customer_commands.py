"""
Customer Commands

CLI command handlers for customer-related operations.

Responsibilities:
    - Receive customer-related CLI actions.
    - Collect user input.
    - Delegate operations to CustomerService.
    - Present results to the user.

The command layer acts as an adapter between:

CLI Layer
    |
    v
Service Layer
"""

from typing import Optional

from services.customer_service import CustomerService

from utils.logger import get_logger


class CustomerCommands:
    """
    Customer command handler.

    Provides CLI operations related to customers.
    """

    def __init__(
        self,
        customer_service: CustomerService,
        input_handler,
        menu_renderer,
    ) -> None:
        """
        Initialize customer commands.

        Args:
            customer_service:
                Customer business service.

            input_handler:
                CLI input collector.

            menu_renderer:
                CLI output renderer.
        """

        self.customer_service = customer_service
        self.input_handler = input_handler
        self.menu_renderer = menu_renderer

        self.logger = get_logger(__name__)


    def create_customer(self) -> None:
        """
        Create a new customer.
        """

        try:

            customer_data = self._collect_customer_data()

            customer = (
                self.customer_service.create_customer(
                    customer_data
                )
            )

            self.menu_renderer.display_message(
                "Customer created successfully."
            )

            self.menu_renderer.display_object(
                customer
            )

        except Exception as exc:

            self.logger.exception(
                "Failed to create customer: %s",
                str(exc),
            )

            self.menu_renderer.display_error(
                str(exc)
            )


    def view_customer(self) -> None:
        """
        Retrieve and display customer details.
        """

        try:

            customer_id = (
                self.input_handler.get_value(
                    "Enter customer ID: "
                )
            )

            customer = (
                self.customer_service.get_customer(
                    customer_id
                )
            )

            self.menu_renderer.display_object(
                customer
            )

        except Exception as exc:

            self.logger.exception(
                "Failed to retrieve customer: %s",
                str(exc),
            )

            self.menu_renderer.display_error(
                str(exc)
            )


    def list_customers(self) -> None:
        """
        Display all customers.
        """

        try:

            customers = (
                self.customer_service.get_all_customers()
            )

            self.menu_renderer.display_list(
                customers
            )

        except Exception as exc:

            self.logger.exception(
                "Failed to list customers: %s",
                str(exc),
            )

            self.menu_renderer.display_error(
                str(exc)
            )


    def update_customer(self) -> None:
        """
        Update customer information.
        """

        try:

            customer_id = (
                self.input_handler.get_value(
                    "Enter customer ID: "
                )
            )

            updates = (
                self._collect_customer_updates()
            )

            customer = (
                self.customer_service.update_customer(
                    customer_id,
                    updates,
                )
            )

            self.menu_renderer.display_message(
                "Customer updated successfully."
            )

            self.menu_renderer.display_object(
                customer
            )

        except Exception as exc:

            self.logger.exception(
                "Failed to update customer: %s",
                str(exc),
            )

            self.menu_renderer.display_error(
                str(exc)
            )


    def delete_customer(self) -> None:
        """
        Delete a customer.
        """

        try:

            customer_id = (
                self.input_handler.get_value(
                    "Enter customer ID: "
                )
            )

            confirmation = (
                self.input_handler.get_confirmation(
                    "Confirm customer deletion?"
                )
            )

            if not confirmation:
                return

            self.customer_service.delete_customer(
                customer_id
            )

            self.menu_renderer.display_message(
                "Customer deleted successfully."
            )

        except Exception as exc:

            self.logger.exception(
                "Failed to delete customer: %s",
                str(exc),
            )

            self.menu_renderer.display_error(
                str(exc)
            )


    def _collect_customer_data(self) -> dict:
        """
        Collect customer creation data.

        Returns:
            Customer data dictionary.
        """

        return {
            "first_name": self.input_handler.get_value(
                "First name: "
            ),
            "last_name": self.input_handler.get_value(
                "Last name: "
            ),
            "email": self.input_handler.get_value(
                "Email: "
            ),
            "phone": self.input_handler.get_value(
                "Phone: "
            ),
        }


    def _collect_customer_updates(self) -> dict:
        """
        Collect customer update fields.

        Returns:
            Update dictionary.
        """

        return {
            "email": self.input_handler.get_optional_value(
                "New email: "
            ),
            "phone": self.input_handler.get_optional_value(
                "New phone: "
            ),
        }
