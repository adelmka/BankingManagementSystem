"""Tests for reporting.customer_reports."""

from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import MagicMock

from reporting.customer_reports import CustomerReports
from utils.constants import AccountStatus, AccountType, CustomerStatus


def make_account(number, account_type=AccountType.SAVINGS, balance="100.00", status=AccountStatus.ACTIVE):
    return SimpleNamespace(
        account_number=number,
        account_type=account_type,
        balance=Decimal(balance),
        status=status,
    )


def make_customer(customer_id, active=True, accounts=None):
    status = CustomerStatus.ACTIVE if active else CustomerStatus.INACTIVE
    return SimpleNamespace(
        customer_id=customer_id,
        full_name=f"Customer {customer_id}",
        email=f"{customer_id.lower()}@example.com",
        phone_number="0500000000",
        status=status,
        is_active=active,
        accounts=accounts or [],
    )


def make_reports(customers=None):
    bank = MagicMock()
    bank.list_customers.return_value = customers or []
    return CustomerReports(bank), bank


def test_customer_summary_returns_expected_rows():
    reports, _ = make_reports([
        make_customer("C1", accounts=[make_account("A1"), make_account("A2", AccountType.CURRENT)]),
    ])

    report = reports.customer_summary()

    assert report.metadata.title == "Customer Summary Report"
    assert report.columns == ("Customer ID", "Full Name", "Email", "Phone", "Status", "Accounts")
    assert report.as_dicts() == [{
        "Customer ID": "C1",
        "Full Name": "Customer C1",
        "Email": "c1@example.com",
        "Phone": "0500000000",
        "Status": "ACTIVE",
        "Accounts": 2,
    }]


def test_customer_summary_handles_customer_without_accounts():
    reports, _ = make_reports([make_customer("C1")])

    assert reports.customer_summary().rows[0][-1] == 0


def test_customer_summary_returns_empty_report_when_no_customers():
    reports, _ = make_reports([])

    assert reports.customer_summary().row_count == 0


def test_active_customers_filters_active_customers():
    reports, _ = make_reports([
        make_customer("C1", True),
        make_customer("C2", False),
    ])

    report = reports.active_customers()

    assert report.metadata.title == "Active Customers"
    assert report.row_count == 1
    assert report.rows[0][0] == "C1"


def test_inactive_customers_filters_inactive_customers():
    reports, _ = make_reports([
        make_customer("C1", True),
        make_customer("C2", False),
    ])

    report = reports.inactive_customers()

    assert report.metadata.title == "Inactive Customers"
    assert report.row_count == 1
    assert report.rows[0][0] == "C2"


def test_active_customers_returns_empty_when_none_are_active():
    reports, _ = make_reports([make_customer("C1", False)])

    assert reports.active_customers().row_count == 0


def test_inactive_customers_returns_empty_when_none_are_inactive():
    reports, _ = make_reports([make_customer("C1", True)])

    assert reports.inactive_customers().row_count == 0


def test_customer_account_summary_returns_only_requested_customer_accounts():
    customer = make_customer("C1", accounts=[
        make_account("A1"),
        make_account("A2", AccountType.CURRENT, "250.00"),
    ])
    reports, bank = make_reports([customer])
    bank.get_customer.return_value = customer

    report = reports.customer_account_summary("C1")

    bank.get_customer.assert_called_once_with("C1")
    assert report.metadata.title == "Customer Account Summary (C1)"
    assert report.row_count == 2
    assert [row[0] for row in report.rows] == ["A1", "A2"]


def test_customer_account_summary_returns_empty_for_customer_without_accounts():
    customer = make_customer("C1")
    reports, bank = make_reports([customer])
    bank.get_customer.return_value = customer

    report = reports.customer_account_summary("C1")

    assert report.row_count == 0


def test_customer_reports_have_expected_string_representations():
    reports, _ = make_reports()

    assert str(reports) == "Customer Reports"
    assert repr(reports) == "CustomerReports()"
