"""
====================================================================
Banking Management System (BMS)

File        : account_reports.py
Description : Account Reporting

Generates account-related reports.

Responsibilities
----------------
• Account summary report
• Savings account report
• Current account report
• Time deposit report
• Active account report
• Closed account report

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

from utils.constants import AccountType


class AccountReports:
    """
    Generates account reports.
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
    # Account Summary
    #################################################################

    def account_summary(self) -> Report:
        """
        Generate an account summary report.
        """

        report = ReportGenerator.create_report(
            title="Account Summary Report",
            columns=(
                "Account Number",
                "Customer ID",
                "Account Type",
                "Balance",
                "Status",
            ),
        )

        accounts = self._bank.list_accounts()

        for account in accounts:

            report.add_row(
                account.account_number,
                account.customer_id,
                account.account_type.name,
                account.balance,
                account.status.name,
            )

        return report

    #################################################################
    # Savings Accounts
    #################################################################

    def savings_accounts(self) -> Report:
        """
        Generate a savings account report.
        """

        return self._accounts_by_type(
            AccountType.SAVINGS,
            "Savings Account Report",
        )

    #################################################################
    # Current Accounts
    #################################################################

    def current_accounts(self) -> Report:
        """
        Generate a current account report.
        """

        return self._accounts_by_type(
            AccountType.CURRENT,
            "Current Account Report",
        )

    #################################################################
    # Time Deposit Accounts
    #################################################################

    def time_deposit_accounts(self) -> Report:
        """
        Generate a time deposit account report.
        """

        return self._accounts_by_type(
            AccountType.TIME_DEPOSIT,
            "Time Deposit Report",
        )

    #################################################################
    # Active Accounts
    #################################################################

    def active_accounts(self) -> Report:
        """
        Generate a report of active accounts.
        """

        report = ReportGenerator.create_report(
            title="Active Accounts",
            columns=(
                "Account Number",
                "Customer ID",
                "Account Type",
                "Balance",
            ),
        )

        for account in self._bank.list_accounts():

            if account.is_active:

                report.add_row(
                    account.account_number,
                    account.customer_id,
                    account.account_type.name,
                    account.balance,
                )

        return report

    #################################################################
    # Closed Accounts
    #################################################################

    def closed_accounts(self) -> Report:
        """
        Generate a report of closed accounts.
        """

        report = ReportGenerator.create_report(
            title="Closed Accounts",
            columns=(
                "Account Number",
                "Customer ID",
                "Account Type",
                "Balance",
            ),
        )

        for account in self._bank.list_accounts():

            if not account.is_active:

                report.add_row(
                    account.account_number,
                    account.customer_id,
                    account.account_type.name,
                    account.balance,
                )

        return report

    #################################################################
    # Internal Helpers
    #################################################################

    def _accounts_by_type(
        self,
        account_type: AccountType,
        title: str,
    ) -> Report:
        """
        Generate a report for a specific account type.
        """

        report = ReportGenerator.create_report(
            title=title,
            columns=(
                "Account Number",
                "Customer ID",
                "Balance",
                "Status",
            ),
        )

        for account in self._bank.list_accounts():

            if account.account_type == account_type:

                report.add_row(
                    account.account_number,
                    account.customer_id,
                    account.balance,
                    account.status.name,
                )

        return report

    #################################################################
    # Representation
    #################################################################

    def __repr__(self) -> str:

        return (
            f"{self.__class__.__name__}()"
        )

    def __str__(self) -> str:

        return "Account Reports"