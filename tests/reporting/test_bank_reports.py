"""Tests for reporting.bank_reports."""

from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import MagicMock

from reporting.bank_reports import BankReports
from utils.constants import AccountType, CustomerStatus, TransactionType


def account(number, account_type=AccountType.SAVINGS, balance="100.00", active=True):
    return SimpleNamespace(
        account_number=number,
        account_type=account_type,
        balance=Decimal(balance),
        is_active=active,
    )


def customer(active=True):
    return SimpleNamespace(is_active=active, status=CustomerStatus.ACTIVE if active else CustomerStatus.INACTIVE)


def transaction(transaction_type):
    return SimpleNamespace(transaction_type=transaction_type)


def make_reports(customers=None, accounts=None, transactions=None):
    bank = MagicMock()
    bank.list_customers.return_value = customers or []
    bank.list_accounts.return_value = accounts or []
    bank.list_transactions.return_value = transactions or []
    return BankReports(bank), bank


def rows_by_metric(report):
    return dict(report.rows)


def test_bank_summary_aggregates_counts_and_balance():
    reports, bank = make_reports(
        customers=[customer(), customer(False)],
        accounts=[account("A1", balance="100.00"), account("A2", AccountType.CURRENT, "250.00")],
        transactions=[transaction(TransactionType.DEPOSIT), transaction(TransactionType.WITHDRAWAL)],
    )

    report = reports.bank_summary()

    assert rows_by_metric(report) == {
        "Total Customers": 2,
        "Total Accounts": 2,
        "Total Transactions": 2,
        "Total Portfolio Balance": Decimal("350.00"),
    }
    bank.list_customers.assert_called_once()
    bank.list_accounts.assert_called_once()
    bank.list_transactions.assert_called_once()


def test_bank_summary_handles_empty_bank():
    reports, _ = make_reports()

    assert rows_by_metric(reports.bank_summary()) == {
        "Total Customers": 0,
        "Total Accounts": 0,
        "Total Transactions": 0,
        "Total Portfolio Balance": 0,
    }


def test_customer_statistics_counts_active_and_inactive_customers():
    reports, _ = make_reports(customers=[customer(True), customer(False), customer(True)])

    assert rows_by_metric(reports.customer_statistics()) == {
        "Total Customers": 3,
        "Active Customers": 2,
        "Inactive Customers": 1,
    }


def test_customer_statistics_handles_no_customers():
    reports, _ = make_reports()

    assert rows_by_metric(reports.customer_statistics()) == {
        "Total Customers": 0,
        "Active Customers": 0,
        "Inactive Customers": 0,
    }


def test_account_statistics_counts_types_and_active_accounts():
    reports, _ = make_reports(accounts=[
        account("S1", AccountType.SAVINGS, active=True),
        account("S2", AccountType.SAVINGS, active=False),
        account("C1", AccountType.CURRENT, active=True),
        account("T1", AccountType.TIME_DEPOSIT, active=True),
    ])

    assert rows_by_metric(reports.account_statistics()) == {
        "Total Accounts": 4,
        "Savings Accounts": 2,
        "Current Accounts": 1,
        "Time Deposit Accounts": 1,
        "Active Accounts": 3,
    }


def test_account_statistics_handles_no_accounts():
    reports, _ = make_reports()

    assert rows_by_metric(reports.account_statistics()) == {
        "Total Accounts": 0,
        "Savings Accounts": 0,
        "Current Accounts": 0,
        "Time Deposit Accounts": 0,
        "Active Accounts": 0,
    }


def test_transaction_statistics_counts_transaction_types():
    reports, _ = make_reports(transactions=[
        transaction(TransactionType.DEPOSIT),
        transaction(TransactionType.DEPOSIT),
        transaction(TransactionType.WITHDRAWAL),
        transaction(TransactionType.INTERNAL_TRANSFER),
        transaction(TransactionType.EXTERNAL_TRANSFER),
    ])

    values = rows_by_metric(reports.transaction_statistics())

    assert values == {
        "Total Transactions": 5,
        "Deposits": 2,
        "Withdrawals": 1,
        "Transfers": 2,
    }


def test_portfolio_summary_aggregates_total_and_average_balance():
    reports, _ = make_reports(accounts=[
        account("A1", balance="100.00"),
        account("A2", balance="300.00"),
    ])

    assert rows_by_metric(reports.portfolio_summary()) == {
        "Total Portfolio Balance": Decimal("400.00"),
        "Average Account Balance": Decimal("200.00"),
        "Number of Accounts": 2,
    }


def test_portfolio_summary_returns_zero_for_empty_account_set():
    reports, _ = make_reports()

    assert rows_by_metric(reports.portfolio_summary()) == {
        "Total Portfolio Balance": Decimal("0.00"),
        "Average Account Balance": Decimal("0.00"),
        "Number of Accounts": 0,
    }


def test_portfolio_summary_preserves_decimal_precision():
    reports, _ = make_reports(accounts=[
        account("A1", balance="100.01"),
        account("A2", balance="200.03"),
    ])

    values = rows_by_metric(reports.portfolio_summary())

    assert values["Total Portfolio Balance"] == Decimal("300.04")
    assert values["Average Account Balance"] == Decimal("150.02")


def test_bank_reports_have_expected_string_representations():
    reports, _ = make_reports()

    assert str(reports) == "Bank Reports"
    assert repr(reports) == "BankReports()"
