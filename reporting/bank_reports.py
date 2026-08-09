"""
====================================================================
Banking Management System (BMS)

File        : bank_reports.py
Description : Bank Reporting

Generates bank-wide operational and financial reports.

Responsibilities
----------------
• Bank summary report
• Customer statistics
• Account statistics
• Transaction statistics
• Portfolio summary

Author      : Adel Alawiyat / ChatGPT
Python      : 3.13+
====================================================================
"""

from __future__ import annotations

from decimal import Decimal

from reporting.report_generator import (
    Report,
    ReportGenerator,
)

from services.bank_service import BankService

from utils.constants import (
    AccountType,
    TransactionType,
)


class BankReports:
    """
    Generates institution-wide reports.
    """

    #################################################################
    # Construction
    #################################################################

    def __init__(
        self,
        bank_service: BankService,
    ) -> None:

        self._bank = bank_service

    #################################################################
    # Bank Summary
    #################################################################

    def bank_summary(self) -> Report:
        """
        Generate an overall bank summary.
        """

        customers = self._bank.list_customers()
        accounts = self._bank.list_accounts()
        transactions = self._bank.list_transactions()

        total_balance = sum(
            account.balance
            for account in accounts
        )

        report = ReportGenerator.create_report(
            title="Bank Summary Report",
            columns=(
                "Metric",
                "Value",
            ),
        )

        report.add_row("Total Customers", len(customers))
        report.add_row("Total Accounts", len(accounts))
        report.add_row("Total Transactions", len(transactions))
        report.add_row("Total Portfolio Balance", total_balance)

        return report

    #################################################################
    # Customer Statistics
    #################################################################

    def customer_statistics(self) -> Report:
        """Generate customer statistics."""

        customers = self._bank.list_customers()

        active = sum(
            customer.is_active
            for customer in customers
        )

        inactive = len(customers) - active

        report = ReportGenerator.create_report(
            title="Customer Statistics",
            columns=("Statistic", "Value"),
        )

        report.add_row("Total Customers", len(customers))
        report.add_row("Active Customers", active)
        report.add_row("Inactive Customers", inactive)

        return report

    #################################################################
    # Account Statistics
    #################################################################

    def account_statistics(self) -> Report:
        """Generate account statistics."""

        accounts = self._bank.list_accounts()

        report = ReportGenerator.create_report(
            title="Account Statistics",
            columns=("Statistic", "Value"),
        )

        report.add_row("Total Accounts", len(accounts))
        report.add_row(
            "Savings Accounts",
            sum(account.account_type == AccountType.SAVINGS for account in accounts),
        )
        report.add_row(
            "Current Accounts",
            sum(account.account_type == AccountType.CURRENT for account in accounts),
        )
        report.add_row(
            "Time Deposit Accounts",
            sum(account.account_type == AccountType.TIME_DEPOSIT for account in accounts),
        )
        report.add_row(
            "Active Accounts",
            sum(account.is_active for account in accounts),
        )

        return report

    #################################################################
    # Transaction Statistics
    #################################################################

    def transaction_statistics(self) -> Report:
        """Generate transaction statistics."""

        transactions = self._bank.list_transactions()

        report = ReportGenerator.create_report(
            title="Transaction Statistics",
            columns=("Statistic", "Value"),
        )

        report.add_row("Total Transactions", len(transactions))
        report.add_row(
            "Deposits",
            sum(
                transaction.transaction_type == TransactionType.DEPOSIT
                for transaction in transactions
            ),
        )
        report.add_row(
            "Withdrawals",
            sum(
                transaction.transaction_type == TransactionType.WITHDRAWAL
                for transaction in transactions
            ),
        )
        report.add_row(
            "Transfers",
            sum(
                transaction.transaction_type in (
                    TransactionType.INTERNAL_TRANSFER,
                    TransactionType.EXTERNAL_TRANSFER,
                )
                for transaction in transactions
            ),
        )

        return report

    #################################################################
    # Portfolio Summary
    #################################################################

    def portfolio_summary(self) -> Report:
        """Generate the bank portfolio summary."""

        accounts = self._bank.list_accounts()

        total_balance = Decimal("0.00")

        for account in accounts:
            total_balance += account.balance

        average_balance = (
            total_balance / len(accounts)
            if accounts
            else Decimal("0.00")
        )

        report = ReportGenerator.create_report(
            title="Portfolio Summary",
            columns=("Metric", "Value"),
        )

        report.add_row("Total Portfolio Balance", total_balance)
        report.add_row("Average Account Balance", average_balance)
        report.add_row("Number of Accounts", len(accounts))

        return report

    #################################################################
    # Representation
    #################################################################

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}()"

    def __str__(self) -> str:
        return "Bank Reports"
