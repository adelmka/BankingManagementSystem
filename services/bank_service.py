"""
===============================================================================
Banking Management System (BMS)

File        : bank_service.py
Description : Banking Application Facade.

Author      : Adel Alawiyat / ChatGPT
Version     : 2.1.0
Python      : 3.13+

===============================================================================
"""

from __future__ import annotations


from services.customer_service import (
    CustomerService,
)

from services.account_service import (
    AccountService,
)

from services.transaction_service import (
    TransactionService,
)


class BankService:
    """
    Application façade coordinating all banking services.
    """

    # ------------------------------------------------------------------
    # Constructor
    # ------------------------------------------------------------------

    def __init__(
        self,
        customer_service: CustomerService,
        account_service: AccountService,
        transaction_service: TransactionService,
    ) -> None:
        self._customer_service = customer_service
        self._account_service = account_service
        self._transaction_service = transaction_service

       
    # ------------------------------------------------------------------
    # Customer Delegation
    # ------------------------------------------------------------------

    def add_customer(
        self,
        customer,
    ):
        """
        Delegate customer creation.
        """

        return (
            self._customer_service.add_customer(
                customer
            )
        )

    # ------------------------------------------------------------------

    def get_customer(
        self,
        customer_number: str,
    ):
        """
        Delegate customer lookup.
        """

        return (
            self._customer_service.get_customer(
                customer_number
            )
        )

    # ------------------------------------------------------------------

    def customers(
        self,
    ):
        """
        Return all customers.
        """

        return (
            self._customer_service.all_customers()
        )

# PART 2

    # ------------------------------------------------------------------
    # Customer Operations
    # ------------------------------------------------------------------

    def update_customer(
        self,
        customer,
    ):
        """
        Delegate customer update.
        """

        return (
            self._customer_service.update_customer(
                customer
            )
        )

    # ------------------------------------------------------------------

    def activate_customer(
        self,
        customer_number: str,
    ):
        """
        Delegate customer activation.
        """

        return (
            self._customer_service.activate_customer(
                customer_number
            )
        )

    # ------------------------------------------------------------------

    def deactivate_customer(
        self,
        customer_number: str,
    ):
        """
        Delegate customer deactivation.
        """

        return (
            self._customer_service.deactivate_customer(
                customer_number
            )
        )

    # ------------------------------------------------------------------

    def archive_customer(
        self,
        customer_number: str,
    ):
        """
        Delegate customer archival.
        """

        return (
            self._customer_service.archive_customer(
                customer_number
            )
        )

    # ------------------------------------------------------------------

    def customer_statistics(
        self,
    ) -> dict[str, object]:
        """
        Return customer statistics.
        """

        return (
            self._customer_service.statistics()
        )

    # ------------------------------------------------------------------

    def find_customer_by_email(
        self,
        email: str,
    ):
        """
        Delegate customer email lookup.
        """

        return (
            self._customer_service.find_by_email(
                email
            )
        )

    # ------------------------------------------------------------------

    def find_customer_by_national_id(
        self,
        national_id: str,
    ):
        """
        Delegate national ID lookup.
        """

        return (
            self._customer_service.find_by_national_id(
                national_id
            )
        )

    # ------------------------------------------------------------------

    def search_customers(
        self,
        search_text: str,
    ):
        """
        Delegate customer name search.
        """

        return (
            self._customer_service.search_by_name(
                search_text
            )
        )

    # ------------------------------------------------------------------
    # Account Operations
    # ------------------------------------------------------------------

    def open_account(
        self,
        account,
        initial_deposit=None,
    ):
        """
        Delegate account opening.
        """

        return (
            self._account_service.open_account(
                account,
                initial_deposit,
            )
        )

    # ------------------------------------------------------------------

    def get_account(
        self,
        account_number: str,
    ):
        """
        Delegate account lookup.
        """

        return (
            self._account_service.get_account(
                account_number
            )
        )

    # ------------------------------------------------------------------

    def accounts(
        self,
    ):
        """
        Return all accounts.
        """

        return (
            self._account_service.all_accounts()
        )

# PART 3

    # ------------------------------------------------------------------
    # Account Operations
    # ------------------------------------------------------------------

    def deposit(
        self,
        account_number: str,
        amount,
        description: str = "Deposit",
    ):
        """
        Delegate deposit operation.
        """

        return (
            self._account_service.deposit(
                account_number,
                amount,
                description,
            )
        )

    # ------------------------------------------------------------------

    def withdraw(
        self,
        account_number: str,
        amount,
        description: str = "Withdrawal",
    ):
        """
        Delegate withdrawal operation.
        """

        return (
            self._account_service.withdraw(
                account_number,
                amount,
                description,
            )
        )

    # ------------------------------------------------------------------

    def transfer(
        self,
        source_account_number: str,
        destination_account_number: str,
        amount,
        description: str = "Transfer",
    ):
        """
        Delegate transfer operation.
        """

        return (
            self._account_service.transfer(
                source_account_number,
                destination_account_number,
                amount,
                description,
            )
        )

    # ------------------------------------------------------------------

    def close_account(
        self,
        account_number: str,
    ):
        """
        Delegate account closure.
        """

        return (
            self._account_service.close_account(
                account_number
            )
        )

    # ------------------------------------------------------------------

    def freeze_account(
        self,
        account_number: str,
    ):
        """
        Delegate account freeze.
        """

        return (
            self._account_service.freeze_account(
                account_number
            )
        )

    # ------------------------------------------------------------------

    def unfreeze_account(
        self,
        account_number: str,
    ):
        """
        Delegate account unfreeze.
        """

        return (
            self._account_service.unfreeze_account(
                account_number
            )
        )

    # ------------------------------------------------------------------

    def account_balance(
        self,
        account_number: str,
    ):
        """
        Return the account balance.
        """

        return (
            self._account_service.balance(
                account_number
            )
        )

    # ------------------------------------------------------------------

    def available_balance(
        self,
        account_number: str,
    ):
        """
        Return the available account balance.
        """

        return (
            self._account_service.available_balance(
                account_number
            )
        )

    # ------------------------------------------------------------------

    def account_summary(
        self,
        account_number: str,
    ) -> dict[str, object]:
        """
        Return an account summary.
        """

        return (
            self._account_service.account_summary(
                account_number
            )
        )

    # ------------------------------------------------------------------

    def account_statistics(
        self,
    ) -> dict[str, object]:
        """
        Return account statistics.
        """

        return (
            self._account_service.statistics()
        )

    # ------------------------------------------------------------------

    def customer_accounts(
        self,
        customer_number: str,
    ):
        """
        Return all accounts owned by a customer.
        """

        return (
            self._account_service.accounts_for_customer(
                customer_number
            )
        )

# PART 4

    # ------------------------------------------------------------------
    # Transaction Operations
    # ------------------------------------------------------------------

    def record_transaction(
        self,
        transaction,
    ):
        """
        Delegate transaction recording.
        """

        return (
            self._transaction_service.record_transaction(
                transaction
            )
        )

    # ------------------------------------------------------------------

    def get_transaction(
        self,
        transaction_number: str,
    ):
        """
        Delegate transaction lookup.
        """

        return (
            self._transaction_service.get_transaction(
                transaction_number
            )
        )

    # ------------------------------------------------------------------

    def account_transactions(
        self,
        account_number: str,
    ):
        """
        Return all transactions for an account.
        """

        return (
            self._transaction_service.account_transactions(
                account_number
            )
        )

    # ------------------------------------------------------------------

    def customer_transactions(
        self,
        customer_number: str,
    ):
        """
        Return all transactions belonging to a customer.
        """

        return (
            self._transaction_service.customer_transactions(
                customer_number
            )
        )

    # ------------------------------------------------------------------

    def account_statement(
        self,
        account_number: str,
    ) -> list[dict[str, object]]:
        """
        Return an account statement.
        """

        return (
            self._transaction_service.account_statement(
                account_number
            )
        )

    # ------------------------------------------------------------------

    def transaction_summary(
        self,
        transaction_number: str,
    ) -> dict[str, object]:
        """
        Return a transaction summary.
        """

        return (
            self._transaction_service.transaction_summary(
                transaction_number
            )
        )

    # ------------------------------------------------------------------

    def transaction_statistics(
        self,
    ) -> dict[str, object]:
        """
        Return transaction statistics.
        """

        return (
            self._transaction_service.statistics()
        )

    # ------------------------------------------------------------------

    def recent_transactions(
        self,
        limit: int = 10,
    ):
        """
        Return the most recent transactions.
        """

        return (
            self._transaction_service.recent_transactions(
                limit
            )
        )

    # ------------------------------------------------------------------

    def transaction_listing(
        self,
    ):
        """
        Return summaries for all transactions.
        """

        return (
            self._transaction_service.transaction_listing()
        )

    # ------------------------------------------------------------------

    def transactions_between(
        self,
        start_date,
        end_date,
    ):
        """
        Return transactions within a date range.
        """

        return (
            self._transaction_service.transactions_between(
                start_date,
                end_date,
            )
        )

# PART 5

    # ------------------------------------------------------------------
    # Application Lifecycle
    # ------------------------------------------------------------------

    def refresh(
        self,
    ) -> None:
        """
        Refresh all repositories.
        """

        self._customer_service.refresh()
        self._account_service.refresh()
        self._transaction_service.refresh()

    # ------------------------------------------------------------------

    def save_changes(
        self,
    ) -> None:
        """
        Persist all pending changes.
        """

        self._customer_service.save_changes()
        self._account_service.save_changes()
        self._transaction_service.save_changes()

    # ------------------------------------------------------------------

    def statistics(
        self,
    ) -> dict[str, object]:
        """
        Return application-wide statistics.
        """

        return {
            "customers":
                self._customer_service.statistics(),

            "accounts":
                self._account_service.statistics(),

            "transactions":
                self._transaction_service.statistics(),
        }

    # ------------------------------------------------------------------

    def shutdown(
        self,
    ) -> None:
        """
        Perform an orderly application shutdown.
        """

        self.save_changes()

    # ------------------------------------------------------------------
    # Display
    # ------------------------------------------------------------------

    def __str__(
        self,
    ) -> str:
        """
        Return a human-readable representation.
        """

        return (
            f"{self.__class__.__name__}("
            f"customers={self._customer_service.customer_count()}, "
            f"accounts={self._account_service.account_count()}, "
            f"transactions={self._transaction_service.transaction_count()})"
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
            f"customer_repository="
            f"{self._customer_service.__class__.__name__}, "
            f"account_repository="
            f"{self._account_service.__class__.__name__}, "
            f"transaction_repository="
            f"{self._transaction_service.__class__.__name__})"
        )


# ----------------------------------------------------------------------
# End of File
# ----------------------------------------------------------------------
