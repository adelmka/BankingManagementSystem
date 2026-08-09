"""Tests for reporting.transaction_reports."""

from datetime import datetime
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from reporting.transaction_reports import TransactionReports
from utils.constants import TransactionStatus, TransactionType


def make_transaction(transaction_id, account_number="A1", transaction_type=TransactionType.DEPOSIT, amount="100.00"):
    return SimpleNamespace(
        transaction_id=transaction_id,
        transaction_date=datetime(2026, 8, 9, 12, 0),
        account_number=account_number,
        transaction_type=transaction_type,
        amount=Decimal(amount),
        status=TransactionStatus.COMPLETED,
    )


def make_reports(transactions=None):
    bank = MagicMock()
    bank.list_transactions.return_value = transactions or []
    bank.get_account_transactions.return_value = []
    bank.get_customer_transactions.return_value = []
    return TransactionReports(bank), bank


def test_transaction_summary_returns_all_transaction_fields():
    reports, _ = make_reports([
        make_transaction("T1"),
    ])

    report = reports.transaction_summary()

    assert report.metadata.title == "Transaction Summary Report"
    assert report.columns == (
        "Transaction ID", "Date", "Account Number", "Transaction Type", "Amount", "Status",
    )
    assert report.row_count == 1
    assert report.rows[0] == (
        "T1", datetime(2026, 8, 9, 12, 0), "A1", "DEPOSIT", Decimal("100.00"), "COMPLETED",
    )


def test_transaction_summary_returns_empty_report_when_no_transactions():
    reports, _ = make_reports([])

    assert reports.transaction_summary().row_count == 0


def test_deposits_filters_deposit_transactions():
    reports, _ = make_reports([
        make_transaction("D1", transaction_type=TransactionType.DEPOSIT),
        make_transaction("W1", transaction_type=TransactionType.WITHDRAWAL),
    ])

    report = reports.deposits()

    assert report.metadata.title == "Deposit Report"
    assert report.row_count == 1
    assert report.rows[0][0] == "D1"


def test_withdrawals_filters_withdrawal_transactions():
    reports, _ = make_reports([
        make_transaction("D1", transaction_type=TransactionType.DEPOSIT),
        make_transaction("W1", transaction_type=TransactionType.WITHDRAWAL),
    ])

    report = reports.withdrawals()

    assert report.metadata.title == "Withdrawal Report"
    assert report.row_count == 1
    assert report.rows[0][0] == "W1"


def test_type_reports_return_empty_when_no_matching_transactions():
    reports, _ = make_reports([
        make_transaction("D1", transaction_type=TransactionType.DEPOSIT),
    ])

    assert reports.withdrawals().row_count == 0


def test_account_history_delegates_to_bank_and_builds_report():
    reports, bank = make_reports()
    bank.get_account_transactions.return_value = [
        make_transaction("T1", "A1"),
        make_transaction("T2", "A1", TransactionType.WITHDRAWAL, "25.00"),
    ]

    report = reports.account_history("A1")

    bank.get_account_transactions.assert_called_once_with("A1")
    assert report.metadata.title == "Account Transaction History (A1)"
    assert report.row_count == 2
    assert report.rows[0] == (
        "T1", datetime(2026, 8, 9, 12, 0), "DEPOSIT", Decimal("100.00"), "COMPLETED",
    )


def test_account_history_returns_empty_for_account_without_transactions():
    reports, bank = make_reports()
    bank.get_account_transactions.return_value = []

    assert reports.account_history("A1").row_count == 0
    bank.get_account_transactions.assert_called_once_with("A1")


def test_customer_history_delegates_to_bank_and_builds_report():
    reports, bank = make_reports()
    bank.get_customer_transactions.return_value = [
        make_transaction("T1", "A1"),
        make_transaction("T2", "A2", TransactionType.WITHDRAWAL, "50.00"),
    ]

    report = reports.customer_history("C1")

    bank.get_customer_transactions.assert_called_once_with("C1")
    assert report.metadata.title == "Customer Transaction History (C1)"
    assert report.row_count == 2
    assert report.rows[0][2] == "A1"
    assert report.rows[1][2] == "A2"


def test_customer_history_returns_empty_for_customer_without_transactions():
    reports, bank = make_reports()
    bank.get_customer_transactions.return_value = []

    assert reports.customer_history("C1").row_count == 0
    bank.get_customer_transactions.assert_called_once_with("C1")


def test_transfers_exposes_current_transaction_type_contract_mismatch():
    reports, _ = make_reports([])

    # TransactionType currently defines INTERNAL_TRANSFER and EXTERNAL_TRANSFER,
    # while production reporting code requests TransactionType.TRANSFER.
    with pytest.raises(AttributeError, match="TRANSFER"):
        reports.transfers()


def test_transaction_reports_have_expected_string_representations():
    reports, _ = make_reports()

    assert str(reports) == "Transaction Reports"
    assert repr(reports) == "TransactionReports()"
