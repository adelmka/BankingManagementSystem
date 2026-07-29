"""
====================================================================
Banking Management System (BMS)

File        : customer_reports.py
Description : Customer Reporting

Generates customer-related reports.

Responsibilities
----------------
• Customer summary report
• Active customer report
• Inactive customer report
• Customer account summary report

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


class CustomerReports:
    """
    Generates customer reports.
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
    # Customer Summary
    #################################################################

    def customer_summary(self) -> Report:
        """
        Generate a customer summary report.
        """

        report = ReportGenerator.create_report(
            title="Customer Summary Report",
            columns=(
                "Customer ID",
                "Full Name",
                "Email",
                "Phone",
                "Status",
                "Accounts",
            ),
        )

        customers = self._bank.list_customers()

        for customer in customers:

            report.add_row(
                customer.customer_id,
                customer.full_name,
                customer.email,
                customer.phone_number,
                customer.status.name,
                len(customer.accounts),
            )

        return report

    #################################################################
    # Active Customers
    #################################################################

    def active_customers(self) -> Report:
        """
        Generate a report of active customers.
        """

        report = ReportGenerator.create_report(
            title="Active Customers",
            columns=(
                "Customer ID",
                "Full Name",
                "Email",
            ),
        )

        customers = self._bank.list_customers()

        for customer in customers:

            if customer.is_active:

                report.add_row(
                    customer.customer_id,
                    customer.full_name,
                    customer.email,
                )

        return report

    #################################################################
    # Inactive Customers
    #################################################################

    def inactive_customers(self) -> Report:
        """
        Generate a report of inactive customers.
        """

        report = ReportGenerator.create_report(
            title="Inactive Customers",
            columns=(
                "Customer ID",
                "Full Name",
                "Email",
            ),
        )

        customers = self._bank.list_customers()

        for customer in customers:

            if not customer.is_active:

                report.add_row(
                    customer.customer_id,
                    customer.full_name,
                    customer.email,
                )

        return report

    #################################################################
    # Customer Account Summary
    #################################################################

    def customer_account_summary(
        self,
        customer_id: str,
    ) -> Report:
        """
        Generate an account summary for a single customer.
        """

        customer = self._bank.get_customer(customer_id)

        report = ReportGenerator.create_report(
            title=f"Customer Account Summary ({customer.customer_id})",
            columns=(
                "Account Number",
                "Account Type",
                "Balance",
                "Status",
            ),
        )

        for account in customer.accounts:

            report.add_row(
                account.account_number,
                account.account_type.name,
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

        return "Customer Reports"