"""Tests for reporting.account_reports."""

from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import MagicMock

from reporting.account_reports import AccountReports
from reporting.report_generator import Report
from utils.constants import AccountStatus, AccountType


def make_account(number, account_type, status=AccountStatus.ACTIVE, active=True, balance="100.00"):
    return SimpleNamespace(
        account_number=number,
        customer_id="CUST-1",
        account_type=account_type,
        balance=Decimal(balance),
        status=status,
        is_active=active,
    )


def make_reports(accounts):
    bank = MagicMock()
    bank.list_accounts.return_value = accounts
    return AccountReports(bank), bank


def test_account_summary_returns_expected_columns_and_rows():
    reports, _ = make_reports([make_account("A1", AccountType.SAVINGS)])

    report = reports.account_summary()

    assert isinstance(report, Report)
    assert report.metadata.title == "Account Summary Report"
    assert report.columns == ("Account Number", "Customer ID", "Account Type", "Balance", "Status")
    assert report.as_dicts() == [{
        "Account Number": "A1",
        "Customer ID": "CUST-1",
        "Account Type": "SAVINGS",
        "Balance": Decimal("100.00"),
        "Status": "ACTIVE",
    }]


def test_account_summary_returns_empty_report_when_no_accounts():
    reports, _ = make_reports([])

    report = reports.account_summary()

    assert report.row_count == 0


def test_account_summary_includes_zero_balance_account():
    reports, _ = make_reports([
        make_account("A1", AccountType.SAVINGS, balance="0.00"),
    ])

    assert reports.account_summary().rows[0][3] == Decimal("0.00")


def test_savings_accounts_filters_by_account_type():
    reports, _ = make_reports([
        make_account("S1", AccountType.SAVINGS),
        make_account("C1", AccountType.CURRENT),
        make_account("T1", AccountType.TIME_DEPOSIT),
    ])

    report = reports.savings_accounts()

    assert report.metadata.title == "Savings Account Report"
    assert report.row_count == 1
    assert report.rows[0][0] == "S1"


def test_current_accounts_filters_by_account_type():
    reports, _ = make_reports([
        make_account("S1", AccountType.SAVINGS),
        make_account("C1", AccountType.CURRENT),
    ])

    report = reports.current_accounts()

    assert report.row_count == 1
    assert report.rows[0][0] == "C1"


def test_time_deposit_accounts_filters_by_account_type():
    reports, _ = make_reports([
        make_account("T1", AccountType.TIME_DEPOSIT),
        make_account("S1", AccountType.SAVINGS),
    ])

    report = reports.time_deposit_accounts()

    assert report.row_count == 1
    assert report.rows[0][0] == "T1"


def test_type_report_is_empty_when_no_matching_accounts():
    reports, _ = make_reports([make_account("S1", AccountType.SAVINGS)])

    assert reports.current_accounts().row_count == 0
    assert reports.time_deposit_accounts().row_count == 0


def test_active_accounts_filters_active_accounts():
    reports, _ = make_reports([
        make_account("A1", AccountType.SAVINGS, active=True),
        make_account("A2", AccountType.CURRENT, status=AccountStatus.CLOSED, active=False),
    ])

    report = reports.active_accounts()

    assert report.metadata.title == "Active Accounts"
    assert report.row_count == 1
    assert report.rows[0][0] == "A1"


def test_closed_accounts_filters_inactive_accounts():
    reports, _ = make_reports([
        make_account("A1", AccountType.SAVINGS, active=True),
        make_account("A2", AccountType.CURRENT, status=AccountStatus.CLOSED, active=False),
    ])

    report = reports.closed_accounts()

    assert report.metadata.title == "Closed Accounts"
    assert report.row_count == 1
    assert report.rows[0][0] == "A2"


def test_active_accounts_returns_empty_when_all_accounts_inactive():
    reports, _ = make_reports([
        make_account("A1", AccountType.SAVINGS, active=False),
    ])

    assert reports.active_accounts().row_count == 0


def test_closed_accounts_returns_empty_when_all_accounts_active():
    reports, _ = make_reports([
        make_account("A1", AccountType.SAVINGS, active=True),
    ])

    assert reports.closed_accounts().row_count == 0


def test_account_reports_delegate_account_retrieval_to_bank_service():
    reports, bank = make_reports([])

    reports.account_summary()
    reports.savings_accounts()
    reports.current_accounts()
    reports.time_deposit_accounts()
    reports.active_accounts()
    reports.closed_accounts()

    assert bank.list_accounts.call_count == 6


def test_account_reports_have_expected_string_representations():
    reports, _ = make_reports([])

    assert str(reports) == "Account Reports"
    assert repr(reports) == "AccountReports()"
