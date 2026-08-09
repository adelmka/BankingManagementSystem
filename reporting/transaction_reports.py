"""
====================================================================
Banking Management System (BMS)

File        : transaction_reports.py
Description : Transaction Reporting

Generates transaction-related reports.

Responsibilities
----------------
• Transaction summary report
• Deposit report
• Withdrawal report
• Transfer report
• Account transaction history
• Customer transaction history

Author      : Adel Alawiyat / ChatGPT
Python      : 3.13+
====================================================================
"""

from __future__ import annotations

from reporting.report_generator import (
    Report,
    ReportGenerator,
)

from services.bank_service import BankService

from utils.constants import TransactionType


class TransactionReports:
    """Generates transaction reports."""

    #################################################################
    # Construction
    #################################################################

    def __init__(self, bank_service: BankService) -> None:
        self._bank = bank_service

    #################################################################
    # Transaction Summary
    #################################################################

    def transaction_summary(self) -> Report:
        """Generate a report containing all transactions."""

        report = ReportGenerator.create_report(
            title="Transaction Summary Report",
            columns=(
                "Transaction ID",
                "Date",
                "Account Number",
                "Transaction Type",
                "Amount",
                "Status",
            ),
        )

        for transaction in self._bank.list_transactions():
            report.add_row(
                transaction.transaction_id,
                transaction.transaction_date,
                transaction.account_number,
                transaction.transaction_type.name,
                transaction.amount,
                transaction.status.name,
            )

        return report

    #################################################################
    # Deposit Report
    #################################################################

    def deposits(self) -> Report:
        """Generate a deposit transaction report."""

        return self._transactions_by_type(
            TransactionType.DEPOSIT,
            "Deposit Report",
        )

    #################################################################
    # Withdrawal Report
    #################################################################

    def withdrawals(self) -> Report:
        """Generate a withdrawal transaction report."""

        return self._transactions_by_type(
            TransactionType.WITHDRAWAL,
            "Withdrawal Report",
        )

    #################################################################
    # Transfer Report
    #################################################################

    def transfers(self) -> Report:
        """Generate a report containing internal and external transfers."""

        report = ReportGenerator.create_report(
            title="Transfer Report",
            columns=(
                "Transaction ID",
                "Date",
                "Account Number",
                "Amount",
                "Status",
            ),
        )

        transfer_types = {
            TransactionType.INTERNAL_TRANSFER,
            TransactionType.EXTERNAL_TRANSFER,
        }

        for transaction in self._bank.list_transactions():
            if transaction.transaction_type in transfer_types:
                report.add_row(
                    transaction.transaction_id,
                    transaction.transaction_date,
                    transaction.account_number,
                    transaction.amount,
                    transaction.status.name,
                )

        return report

    #################################################################
    # Account Transaction History
    #################################################################

    def account_history(self, account_number: str) -> Report:
        """Generate the transaction history for an account."""

        report = ReportGenerator.create_report(
            title=f"Account Transaction History ({account_number})",
            columns=(
                "Transaction ID",
                "Date",
                "Transaction Type",
                "Amount",
                "Status",
            ),
        )

        transactions = self._bank.get_account_transactions(account_number)

        for transaction in transactions:
            report.add_row(
                transaction.transaction_id,
                transaction.transaction_date,
                transaction.transaction_type.name,
                transaction.amount,
                transaction.status.name,
            )

        return report

    #################################################################
    # Customer Transaction History
    #################################################################

    def customer_history(self, customer_id: str) -> Report:
        """Generate the transaction history for a customer."""

        report = ReportGenerator.create_report(
            title=f"Customer Transaction History ({customer_id})",
            columns=(
                "Transaction ID",
                "Date",
                "Account Number",
                "Transaction Type",
                "Amount",
                "Status",
            ),
        )

        transactions = self._bank.get_customer_transactions(customer_id)

        for transaction in transactions:
            report.add_row(
                transaction.transaction_id,
                transaction.transaction_date,
                transaction.account_number,
                transaction.transaction_type.name,
                transaction.amount,
                transaction.status.name,
            )

        return report

    #################################################################
    # Internal Helpers
    #################################################################

    def _transactions_by_type(
        self,
        transaction_type: TransactionType,
        title: str,
    ) -> Report:
        """Generate a report for a specific transaction type."""

        report = ReportGenerator.create_report(
            title=title,
            columns=(
                "Transaction ID",
                "Date",
                "Account Number",
                "Amount",
                "Status",
            ),
        )

        for transaction in self._bank.list_transactions():
            if transaction.transaction_type == transaction_type:
                report.add_row(
                    transaction.transaction_id,
                    transaction.transaction_date,
                    transaction.account_number,
                    transaction.amount,
                    transaction.status.name,
                )

        return report

    #################################################################
    # Representation
    #################################################################

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}()"

    def __str__(self) -> str:
        return "Transaction Reports"
