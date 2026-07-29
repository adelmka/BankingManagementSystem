"""
Account Commands

CLI command handlers for account-related operations.

Responsibilities:
    - Receive account-related CLI actions.
    - Collect user input.
    - Delegate operations to AccountService.
    - Display results through the CLI renderer.

The command layer is an adapter between:

CLI Layer
    |
    v
Account Service Layer
"""

from services.account_service import AccountService

from utils.logger import get_logger


class AccountCommands:
    """
    Account command handler.

    Provides CLI operations related to bank accounts.
    """

    def __init__(
        self,
        account_service: AccountService,
        input_handler,
        menu_renderer,
    ) -> None:
        """
        Initialize account commands.

        Args:
            account_service:
                Account business service.

            input_handler:
                CLI input collector.

            menu_renderer:
                CLI output renderer.
        """

        self.account_service = account_service
        self.input_handler = input_handler
        self.menu_renderer = menu_renderer

        self.logger = get_logger(__name__)


    def create_account(self) -> None:
        """
        Create a new account.
        """

        try:

            account_data = self._collect_account_data()

            account = (
                self.account_service.create_account(
                    account_data
                )
            )

            self.menu_renderer.display_message(
                "Account created successfully."
            )

            self.menu_renderer.display_object(
                account
            )

        except Exception as exc:

            self.logger.exception(
                "Failed to create account: %s",
                exc,
            )

            self.menu_renderer.display_error(
                str(exc)
            )


    def view_account(self) -> None:
        """
        Retrieve account details.
        """

        try:

            account_number = (
                self.input_handler.get_value(
                    "Enter account number: "
                )
            )

            account = (
                self.account_service.get_account(
                    account_number
                )
            )

            self.menu_renderer.display_object(
                account
            )

        except Exception as exc:

            self.logger.exception(
                "Failed to retrieve account: %s",
                exc,
            )

            self.menu_renderer.display_error(
                str(exc)
            )


    def list_accounts(self) -> None:
        """
        Display all accounts.
        """

        try:

            accounts = (
                self.account_service.get_all_accounts()
            )

            self.menu_renderer.display_list(
                accounts
            )

        except Exception as exc:

            self.logger.exception(
                "Failed to list accounts: %s",
                exc,
            )

            self.menu_renderer.display_error(
                str(exc)
            )


    def deposit(self) -> None:
        """
        Deposit funds into an account.
        """

        try:

            account_number = (
                self.input_handler.get_value(
                    "Enter account number: "
                )
            )

            amount = (
                self.input_handler.get_money(
                    "Enter deposit amount: "
                )
            )

            account = (
                self.account_service.deposit(
                    account_number,
                    amount,
                )
            )

            self.menu_renderer.display_message(
                "Deposit completed successfully."
            )

            self.menu_renderer.display_object(
                account
            )

        except Exception as exc:

            self.logger.exception(
                "Deposit failed: %s",
                exc,
            )

            self.menu_renderer.display_error(
                str(exc)
            )


    def withdraw(self) -> None:
        """
        Withdraw funds from an account.
        """

        try:

            account_number = (
                self.input_handler.get_value(
                    "Enter account number: "
                )
            )

            amount = (
                self.input_handler.get_money(
                    "Enter withdrawal amount: "
                )
            )

            account = (
                self.account_service.withdraw(
                    account_number,
                    amount,
                )
            )

            self.menu_renderer.display_message(
                "Withdrawal completed successfully."
            )

            self.menu_renderer.display_object(
                account
            )

        except Exception as exc:

            self.logger.exception(
                "Withdrawal failed: %s",
                exc,
            )

            self.menu_renderer.display_error(
                str(exc)
            )


    def apply_interest(self) -> None:
        """
        Apply interest to an account.
        """

        try:

            account_number = (
                self.input_handler.get_value(
                    "Enter account number: "
                )
            )

            account = (
                self.account_service.apply_interest(
                    account_number
                )
            )

            self.menu_renderer.display_message(
                "Interest applied successfully."
            )

            self.menu_renderer.display_object(
                account
            )

        except Exception as exc:

            self.logger.exception(
                "Interest application failed: %s",
                exc,
            )

            self.menu_renderer.display_error(
                str(exc)
            )


    def apply_fee(self) -> None:
        """
        Apply account fee.
        """

        try:

            account_number = (
                self.input_handler.get_value(
                    "Enter account number: "
                )
            )

            fee_amount = (
                self.input_handler.get_money(
                    "Enter fee amount: "
                )
            )

            account = (
                self.account_service.apply_fee(
                    account_number,
                    fee_amount,
                )
            )

            self.menu_renderer.display_message(
                "Fee applied successfully."
            )

            self.menu_renderer.display_object(
                account
            )

        except Exception as exc:

            self.logger.exception(
                "Fee application failed: %s",
                exc,
            )

            self.menu_renderer.display_error(
                str(exc)
            )


    def close_account(self) -> None:
        """
        Close an account.
        """

        try:

            account_number = (
                self.input_handler.get_value(
                    "Enter account number: "
                )
            )

            confirmation = (
                self.input_handler.get_confirmation(
                    "Confirm account closure?"
                )
            )

            if not confirmation:
                return

            self.account_service.close_account(
                account_number
            )

            self.menu_renderer.display_message(
                "Account closed successfully."
            )

        except Exception as exc:

            self.logger.exception(
                "Account closure failed: %s",
                exc,
            )

            self.menu_renderer.display_error(
                str(exc)
            )


    def _collect_account_data(self) -> dict:
        """
        Collect account creation data.

        Returns:
            Account creation payload.
        """

        return {
            "customer_id": self.input_handler.get_value(
                "Customer ID: "
            ),
            "account_type": self.input_handler.get_value(
                "Account type: "
            ),
            "initial_deposit": self.input_handler.get_money(
                "Initial deposit: "
            ),
        }