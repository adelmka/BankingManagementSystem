"""
Bank Commands

CLI command handlers for bank-wide workflows.

This module provides operations that coordinate multiple
application services through BankService.

It intentionally does not duplicate functionality already
provided by CustomerCommands, AccountCommands, or
TransactionCommands.

Architecture:

CLI
    |
    v
BankCommands
    |
    v
BankService
    |
    +--> CustomerService
    +--> AccountService
    +--> TransactionService
"""

from services.bank_service import BankService
from utils.logger import get_logger


class BankCommands:
    """
    CLI command adapter for bank-wide operations.

    This class contains only orchestration commands
    involving multiple business services.
    """

    def __init__(
        self,
        bank_service: BankService,
        input_handler,
        menu_renderer,
    ) -> None:
        self.bank_service = bank_service
        self.input_handler = input_handler
        self.menu_renderer = menu_renderer

        self.logger = get_logger(__name__)

    def open_customer_account(self) -> None:
        """
        Register a new customer and create the
        customer's initial bank account.
        """

        try:

            customer_data = {
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

            account_data = {
                "account_type": self.input_handler.get_value(
                    "Account type: "
                ),
                "initial_deposit": self.input_handler.get_money(
                    "Initial deposit: "
                ),
            }

            result = self.bank_service.open_customer_account(
                customer_data=customer_data,
                account_data=account_data,
            )

            self.menu_renderer.display_message(
                "Customer and account created successfully."
            )

            self.menu_renderer.display_object(result)

        except Exception as exc:
            self.logger.exception(
                "Failed to open customer account: %s",
                exc,
            )
            self.menu_renderer.display_error(str(exc))

    def transfer_funds(self) -> None:
        """
        Transfer funds between two accounts.

        The complete transfer workflow is delegated
        to BankService.
        """

        try:

            source_account = self.input_handler.get_value(
                "Source account: "
            )

            destination_account = self.input_handler.get_value(
                "Destination account: "
            )

            amount = self.input_handler.get_money(
                "Transfer amount: "
            )

            description = self.input_handler.get_optional_value(
                "Description: "
            )

            result = self.bank_service.transfer_funds(
                source_account_number=source_account,
                destination_account_number=destination_account,
                amount=amount,
                description=description,
            )

            self.menu_renderer.display_message(
                "Transfer completed successfully."
            )

            self.menu_renderer.display_object(result)

        except Exception as exc:
            self.logger.exception(
                "Transfer failed: %s",
                exc,
            )
            self.menu_renderer.display_error(str(exc))

    def bank_summary(self) -> None:
        """
        Display a summary of the banking system.
        """

        try:

            summary = self.bank_service.get_bank_summary()

            self.menu_renderer.display_object(summary)

        except Exception as exc:
            self.logger.exception(
                "Unable to retrieve bank summary: %s",
                exc,
            )
            self.menu_renderer.display_error(str(exc))

    def bank_statistics(self) -> None:
        """
        Display bank statistics.
        """

        try:

            statistics = self.bank_service.get_bank_statistics()

            self.menu_renderer.display_object(statistics)

        except Exception as exc:
            self.logger.exception(
                "Unable to retrieve bank statistics: %s",
                exc,
            )
            self.menu_renderer.display_error(str(exc))