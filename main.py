"""
Banking Management System executable entry point.

This module is intentionally a thin composition root. It starts the existing
application bootstrap, obtains the configured BankService facade, and exposes
core banking operations through the existing CLI rendering/input utilities.

Run from the repository root with:

    python main.py
"""

from __future__ import annotations

from decimal import Decimal

from application.startup import start_application
from cli.input_handler import InputHandler
from cli.menu_renderer import MenuRenderer
from models.value_objects.money import Money


MAIN_MENU: tuple[tuple[str, str], ...] = (
    ("1", "List customers"),
    ("2", "List accounts"),
    ("3", "Deposit funds"),
    ("4", "Withdraw funds"),
    ("5", "Transfer between accounts"),
    ("6", "View account transactions"),
    ("7", "Customer statistics"),
    ("8", "Account statistics"),
    ("9", "Bank statistics"),
    ("0", "Exit"),
)


def _render_main_menu(renderer: MenuRenderer) -> None:
    """Render the executable application's main menu."""

    renderer.render_heading("Banking Management System")

    for key, description in MAIN_MENU:
        print(f"{key:>2}. {description}", file=renderer.output)

    renderer.render_separator()


def _money_input(input_handler: InputHandler, prompt: str) -> Money:
    """Read a positive monetary amount in the configured default currency."""

    amount = input_handler.read_decimal(
        prompt,
        minimum=Decimal("0.01"),
    )
    return Money(amount)


def _list_customers(application, renderer: MenuRenderer) -> None:
    customers = application.bank.customers()

    if not customers:
        renderer.info("No customers found.")
        return

    renderer.render_table(
        (
            customer.customer_id,
            customer.full_name,
            customer.customer_status.value,
        )
        for customer in customers
    )


def _list_accounts(application, renderer: MenuRenderer) -> None:
    accounts = application.bank.accounts()

    if not accounts:
        renderer.info("No accounts found.")
        return

    renderer.render_table(
        (
            account.account_number,
            account.customer_id,
            account.account_type.value,
            account.balance,
        )
        for account in accounts
    )


def _deposit(application, input_handler: InputHandler, renderer: MenuRenderer) -> None:
    account_number = input_handler.read_string("Account number")
    amount = _money_input(input_handler, "Deposit amount")

    account = application.bank.deposit(account_number, amount)
    renderer.success("Deposit completed successfully.")
    renderer.info(str(account))


def _withdraw(application, input_handler: InputHandler, renderer: MenuRenderer) -> None:
    account_number = input_handler.read_string("Account number")
    amount = _money_input(input_handler, "Withdrawal amount")

    account = application.bank.withdraw(account_number, amount)
    renderer.success("Withdrawal completed successfully.")
    renderer.info(str(account))


def _transfer(application, input_handler: InputHandler, renderer: MenuRenderer) -> None:
    source = input_handler.read_string("Source account")
    destination = input_handler.read_string("Destination account")
    amount = _money_input(input_handler, "Transfer amount")
    description = input_handler.read_string("Description (optional)")
    description = description or "Transfer"

    source_account, destination_account = application.bank.transfer(
        source,
        destination,
        amount,
        description,
    )

    renderer.success("Transfer completed successfully.")
    renderer.render_table(
        (
            ("Source", source_account.account_number),
            ("Source balance", source_account.balance),
            ("Destination", destination_account.account_number),
            ("Destination balance", destination_account.balance),
        )
    )


def _account_transactions(
    application,
    input_handler: InputHandler,
    renderer: MenuRenderer,
) -> None:
    account_number = input_handler.read_string("Account number")
    transactions = application.bank.account_transactions(account_number)

    if not transactions:
        renderer.info("No transactions found for this account.")
        return

    renderer.render_table(
        (
            transaction.transaction_number,
            transaction.transaction_type,
            transaction.amount,
            transaction.description,
        )
        for transaction in transactions
    )


def _run_command(application, choice: str, input_handler: InputHandler, renderer: MenuRenderer) -> None:
    """Execute one main-menu operation."""

    commands = {
        "1": lambda: _list_customers(application, renderer),
        "2": lambda: _list_accounts(application, renderer),
        "3": lambda: _deposit(application, input_handler, renderer),
        "4": lambda: _withdraw(application, input_handler, renderer),
        "5": lambda: _transfer(application, input_handler, renderer),
        "6": lambda: _account_transactions(application, input_handler, renderer),
        "7": lambda: renderer.render_table(application.bank.customer_statistics().items()),
        "8": lambda: renderer.render_table(application.bank.account_statistics().items()),
        "9": lambda: renderer.render_table(application.bank.statistics().items()),
    }

    command = commands.get(choice)

    if command is None:
        renderer.error("Invalid menu selection.")
        return

    try:
        command()
    except Exception as exc:
        renderer.error(str(exc))


def run() -> None:
    """Start and run the interactive BMS application."""

    application = start_application()
    renderer = MenuRenderer()
    input_handler = InputHandler(renderer)

    renderer.success("Banking Management System started.")

    try:
        valid_choices = {key for key, _ in MAIN_MENU}

        while True:
            _render_main_menu(renderer)
            choice = input_handler.read_menu_selection(valid_choices)

            if choice == "0":
                renderer.info("Shutting down Banking Management System.")
                break

            _run_command(
                application,
                choice,
                input_handler,
                renderer,
            )

            input_handler.pause()

    except KeyboardInterrupt:
        renderer.info("Application interrupted by user.")
    finally:
        application.shutdown()


if __name__ == "__main__":
    run()
