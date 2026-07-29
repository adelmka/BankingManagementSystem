"""
Transaction Commands

CLI command handlers for transaction-related operations.

Responsibilities:
    - Receive transaction-related CLI actions.
    - Collect user input.
    - Delegate operations to TransactionService.
    - Display transaction results.

Architecture:

CLI Layer
    |
    v
TransactionCommands
    |
    v
TransactionService
    |
    v
TransactionRepository
"""

from services.transaction_service import TransactionService

from utils.logger import get_logger


class TransactionCommands:
    """
    Transaction command handler.

    Provides CLI operations related to transactions.
    """

    def __init__(
        self,
        transaction_service: TransactionService,
        input_handler,
        menu_renderer,
    ) -> None:
        """
        Initialize transaction commands.

        Args:
            transaction_service:
                Transaction business service.

            input_handler:
                CLI input collector.

            menu_renderer:
                CLI output renderer.
        """

        self.transaction_service = transaction_service
        self.input_handler = input_handler
        self.menu_renderer = menu_renderer

        self.logger = get_logger(__name__)


    def view_transaction(self) -> None:
        """
        Retrieve a transaction by identifier.
        """

        try:

            transaction_id = (
                self.input_handler.get_value(
                    "Enter transaction ID: "
                )
            )

            transaction = (
                self.transaction_service.get_transaction(
                    transaction_id
                )
            )

            self.menu_renderer.display_object(
                transaction
            )

        except Exception as exc:

            self.logger.exception(
                "Failed to retrieve transaction: %s",
                exc,
            )

            self.menu_renderer.display_error(
                str(exc)
            )


    def list_transactions(self) -> None:
        """
        Display all transactions.
        """

        try:

            transactions = (
                self.transaction_service
                .get_all_transactions()
            )

            self.menu_renderer.display_list(
                transactions
            )

        except Exception as exc:

            self.logger.exception(
                "Failed to list transactions: %s",
                exc,
            )

            self.menu_renderer.display_error(
                str(exc)
            )


    def list_account_transactions(self) -> None:
        """
        Display transactions for an account.
        """

        try:

            account_number = (
                self.input_handler.get_value(
                    "Enter account number: "
                )
            )

            transactions = (
                self.transaction_service
                .get_account_transactions(
                    account_number
                )
            )

            self.menu_renderer.display_list(
                transactions
            )

        except Exception as exc:

            self.logger.exception(
                "Failed to retrieve account transactions: %s",
                exc,
            )

            self.menu_renderer.display_error(
                str(exc)
            )


    def list_customer_transactions(self) -> None:
        """
        Display transactions for a customer.
        """

        try:

            customer_id = (
                self.input_handler.get_value(
                    "Enter customer ID: "
                )
            )

            transactions = (
                self.transaction_service
                .get_customer_transactions(
                    customer_id
                )
            )

            self.menu_renderer.display_list(
                transactions
            )

        except Exception as exc:

            self.logger.exception(
                "Failed to retrieve customer transactions: %s",
                exc,
            )

            self.menu_renderer.display_error(
                str(exc)
            )


    def create_deposit_transaction(self) -> None:
        """
        Create a deposit transaction record.
        """

        try:

            account_number = (
                self.input_handler.get_value(
                    "Enter account number: "
                )
            )

            amount = (
                self.input_handler.get_money(
                    "Enter amount: "
                )
            )

            description = (
                self.input_handler.get_optional_value(
                    "Description: "
                )
            )

            transaction = (
                self.transaction_service
                .create_deposit_transaction(
                    account_number,
                    amount,
                    description,
                )
            )

            self.menu_renderer.display_message(
                "Deposit transaction created."
            )

            self.menu_renderer.display_object(
                transaction
            )

        except Exception as exc:

            self.logger.exception(
                "Failed to create deposit transaction: %s",
                exc,
            )

            self.menu_renderer.display_error(
                str(exc)
            )


    def create_withdrawal_transaction(self) -> None:
        """
        Create a withdrawal transaction record.
        """

        try:

            account_number = (
                self.input_handler.get_value(
                    "Enter account number: "
                )
            )

            amount = (
                self.input_handler.get_money(
                    "Enter amount: "
                )
            )

            description = (
                self.input_handler.get_optional_value(
                    "Description: "
                )
            )

            transaction = (
                self.transaction_service
                .create_withdrawal_transaction(
                    account_number,
                    amount,
                    description,
                )
            )

            self.menu_renderer.display_message(
                "Withdrawal transaction created."
            )

            self.menu_renderer.display_object(
                transaction
            )

        except Exception as exc:

            self.logger.exception(
                "Failed to create withdrawal transaction: %s",
                exc,
            )

            self.menu_renderer.display_error(
                str(exc)
            )


    def create_transfer_transaction(self) -> None:
        """
        Create a transfer transaction.

        Note:
            Actual account balance movement belongs
            to the service layer, not this command.
        """

        try:

            source_account = (
                self.input_handler.get_value(
                    "Source account: "
                )
            )

            destination_account = (
                self.input_handler.get_value(
                    "Destination account: "
                )
            )

            amount = (
                self.input_handler.get_money(
                    "Transfer amount: "
                )
            )

            description = (
                self.input_handler.get_optional_value(
                    "Description: "
                )
            )

            transaction = (
                self.transaction_service
                .create_transfer_transaction(
                    source_account,
                    destination_account,
                    amount,
                    description,
                )
            )

            self.menu_renderer.display_message(
                "Transfer transaction created."
            )

            self.menu_renderer.display_object(
                transaction
            )

        except Exception as exc:

            self.logger.exception(
                "Failed to create transfer transaction: %s",
                exc,
            )

            self.menu_renderer.display_error(
                str(exc)
            )