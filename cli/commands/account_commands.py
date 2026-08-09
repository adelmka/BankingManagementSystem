"""CLI command handlers for account-related operations."""

from __future__ import annotations

from datetime import date
from decimal import Decimal, InvalidOperation

from models.current_account import CurrentAccount
from models.savings_account import SavingsAccount
from models.time_deposit_account import TimeDepositAccount
from services.account_service import AccountService
from utils.constants import AccountType, InterestFrequency
from utils.generators import IDGenerator
from utils.logger import get_logger


class AccountCommands:
    """CLI adapter for account-related operations."""

    def __init__(self, account_service: AccountService, input_handler, menu_renderer) -> None:
        self.account_service = account_service
        self.input_handler = input_handler
        self.menu_renderer = menu_renderer
        self.logger = get_logger(__name__)

    def create_account(self) -> None:
        """Collect account data, construct the domain entity, and open it."""
        try:
            account = self._build_account(self._collect_account_data())
            account = self.account_service.open_account(account)
            self.menu_renderer.display_message("Account created successfully.")
            self.menu_renderer.display_object(account)
        except Exception as exc:
            self.logger.exception("Failed to create account: %s", exc)
            self.menu_renderer.display_error(str(exc))

    def view_account(self) -> None:
        try:
            account_number = self.input_handler.get_value("Enter account number: ")
            account = self.account_service.get_account(account_number)
            self.menu_renderer.display_object(account)
        except Exception as exc:
            self.logger.exception("Failed to retrieve account: %s", exc)
            self.menu_renderer.display_error(str(exc))

    def list_accounts(self) -> None:
        try:
            accounts = self.account_service.all_accounts()
            self.menu_renderer.display_list(accounts)
        except Exception as exc:
            self.logger.exception("Failed to list accounts: %s", exc)
            self.menu_renderer.display_error(str(exc))

    def deposit(self) -> None:
        try:
            account_number = self.input_handler.get_value("Enter account number: ")
            amount = self.input_handler.get_money("Enter deposit amount: ")
            account = self.account_service.deposit(account_number, amount)
            self.menu_renderer.display_message("Deposit completed successfully.")
            self.menu_renderer.display_object(account)
        except Exception as exc:
            self.logger.exception("Deposit failed: %s", exc)
            self.menu_renderer.display_error(str(exc))

    def withdraw(self) -> None:
        try:
            account_number = self.input_handler.get_value("Enter account number: ")
            amount = self.input_handler.get_money("Enter withdrawal amount: ")
            account = self.account_service.withdraw(account_number, amount)
            self.menu_renderer.display_message("Withdrawal completed successfully.")
            self.menu_renderer.display_object(account)
        except Exception as exc:
            self.logger.exception("Withdrawal failed: %s", exc)
            self.menu_renderer.display_error(str(exc))

    def apply_interest(self) -> None:
        try:
            account_number = self.input_handler.get_value("Enter account number: ")
            account = self.account_service.apply_interest(account_number)
            self.menu_renderer.display_message("Interest applied successfully.")
            self.menu_renderer.display_object(account)
        except Exception as exc:
            self.logger.exception("Interest application failed: %s", exc)
            self.menu_renderer.display_error(str(exc))

    def apply_fee(self) -> None:
        try:
            account_number = self.input_handler.get_value("Enter account number: ")
            fee_amount = self.input_handler.get_money("Enter fee amount: ")
            account = self.account_service.apply_fee(account_number, fee_amount)
            self.menu_renderer.display_message("Fee applied successfully.")
            self.menu_renderer.display_object(account)
        except Exception as exc:
            self.logger.exception("Fee application failed: %s", exc)
            self.menu_renderer.display_error(str(exc))

    def close_account(self) -> None:
        try:
            account_number = self.input_handler.get_value("Enter account number: ")
            if not self.input_handler.get_confirmation("Confirm account closure?"):
                return
            self.account_service.close_account(account_number)
            self.menu_renderer.display_message("Account closed successfully.")
        except Exception as exc:
            self.logger.exception("Account closure failed: %s", exc)
            self.menu_renderer.display_error(str(exc))

    def _collect_account_data(self) -> dict:
        """Collect common and account-type-specific opening parameters."""
        customer_id = self.input_handler.get_value("Customer ID: ").strip()
        account_type = self._collect_account_type()
        data = {
            "customer_id": customer_id,
            "account_type": account_type,
            "opening_balance": self.input_handler.get_money("Initial deposit: "),
        }

        if account_type is AccountType.SAVINGS:
            data.update(
                interest_rate=self._collect_decimal("Annual interest rate (decimal, e.g. 0.035): "),
                minimum_balance=self.input_handler.get_money("Minimum balance: "),
                interest_frequency=self._collect_interest_frequency(),
            )
        elif account_type is AccountType.CURRENT:
            data.update(
                overdraft_limit=self.input_handler.get_money("Overdraft limit: "),
                maintenance_fee=self.input_handler.get_money("Monthly maintenance fee: "),
                overdraft_fee=self.input_handler.get_money("Overdraft fee: "),
                overdraft_enabled=self.input_handler.get_confirmation("Enable overdraft?"),
            )
        elif account_type is AccountType.TIME_DEPOSIT:
            data.update(
                interest_rate=self._collect_decimal("Annual interest rate (decimal, e.g. 0.045): "),
                term_months=self._collect_integer("Term in months: "),
                early_withdrawal_penalty_rate=self._collect_decimal("Early withdrawal penalty rate (decimal): "),
                auto_renew=self.input_handler.get_confirmation("Enable automatic renewal?"),
            )
        return data

    def _collect_account_type(self) -> AccountType:
        value = self.input_handler.get_value(
            "Account type (Savings/Current/Time Deposit): "
        ).strip().lower()
        aliases = {
            "savings": AccountType.SAVINGS,
            "saving": AccountType.SAVINGS,
            "current": AccountType.CURRENT,
            "checking": AccountType.CURRENT,
            "time deposit": AccountType.TIME_DEPOSIT,
            "time_deposit": AccountType.TIME_DEPOSIT,
            "timedeposit": AccountType.TIME_DEPOSIT,
            "fixed deposit": AccountType.TIME_DEPOSIT,
            "fixed_deposit": AccountType.TIME_DEPOSIT,
        }
        try:
            return aliases[value]
        except KeyError as exc:
            raise ValueError("Invalid account type. Use Savings, Current, or Time Deposit.") from exc

    def _collect_interest_frequency(self) -> InterestFrequency:
        value = self.input_handler.get_value(
            "Interest frequency (Daily/Weekly/Monthly/Quarterly/Semi-Annually/Annually): "
        ).strip().lower()
        aliases = {
            "daily": InterestFrequency.DAILY,
            "weekly": InterestFrequency.WEEKLY,
            "monthly": InterestFrequency.MONTHLY,
            "quarterly": InterestFrequency.QUARTERLY,
            "semi-annually": InterestFrequency.SEMI_ANNUALLY,
            "semi annually": InterestFrequency.SEMI_ANNUALLY,
            "annually": InterestFrequency.ANNUALLY,
            "annual": InterestFrequency.ANNUALLY,
        }
        try:
            return aliases[value]
        except KeyError as exc:
            raise ValueError("Invalid interest frequency.") from exc

    def _collect_decimal(self, prompt: str) -> Decimal:
        value = self.input_handler.get_value(prompt).strip()
        try:
            return Decimal(value)
        except (InvalidOperation, ValueError) as exc:
            raise ValueError(f"Invalid decimal value: {value}") from exc

    def _collect_integer(self, prompt: str) -> int:
        value = self.input_handler.get_value(prompt).strip()
        try:
            return int(value)
        except ValueError as exc:
            raise ValueError(f"Invalid integer value: {value}") from exc

    def _build_account(self, data: dict):
        """Construct the concrete domain account expected by AccountService."""
        common = {
            "account_number": IDGenerator.account_number(),
            "customer_id": data["customer_id"],
            "opening_balance": data["opening_balance"],
            "opened_date": date.today(),
        }
        account_type = data["account_type"]

        if account_type is AccountType.SAVINGS:
            return SavingsAccount(
                **common,
                interest_rate=data["interest_rate"],
                minimum_balance=data["minimum_balance"],
                interest_frequency=data["interest_frequency"],
            )
        if account_type is AccountType.CURRENT:
            return CurrentAccount(
                **common,
                overdraft_limit=data["overdraft_limit"],
                maintenance_fee=data["maintenance_fee"],
                overdraft_fee=data["overdraft_fee"],
                overdraft_enabled=data["overdraft_enabled"],
            )
        if account_type is AccountType.TIME_DEPOSIT:
            return TimeDepositAccount(
                **common,
                interest_rate=data["interest_rate"],
                term_months=data["term_months"],
                early_withdrawal_penalty_rate=data["early_withdrawal_penalty_rate"],
                auto_renew=data["auto_renew"],
            )
        raise ValueError("Unsupported account type.")
