"""
Tests for services.bank_service.BankService.

The BankService is an application façade.  These tests therefore focus on:
- correct delegation to the underlying services,
- propagation of delegated return values,
- application lifecycle coordination,
- aggregate statistics,
- string representations.

Business rules are tested in the individual service test suites.
"""

from __future__ import annotations

from datetime import date
from unittest.mock import MagicMock

import pytest

from services.bank_service import BankService


@pytest.fixture
def customer_service():
    return MagicMock(name="CustomerService")


@pytest.fixture
def account_service():
    return MagicMock(name="AccountService")


@pytest.fixture
def transaction_service():
    return MagicMock(name="TransactionService")


@pytest.fixture
def service(
    customer_service,
    account_service,
    transaction_service,
):
    return BankService(
        customer_service=customer_service,
        account_service=account_service,
        transaction_service=transaction_service,
    )


# ------------------------------------------------------------------
# Constructor
# ------------------------------------------------------------------


def test_constructor_stores_services(
    service,
    customer_service,
    account_service,
    transaction_service,
):
    assert service._customer_service is customer_service
    assert service._account_service is account_service
    assert service._transaction_service is transaction_service


# ------------------------------------------------------------------
# Customer delegation
# ------------------------------------------------------------------


def test_add_customer_delegates(service, customer_service):
    customer = object()
    expected = object()
    customer_service.add_customer.return_value = expected

    result = service.add_customer(customer)

    customer_service.add_customer.assert_called_once_with(customer)
    assert result is expected


def test_get_customer_delegates(service, customer_service):
    expected = object()
    customer_service.get_customer.return_value = expected

    result = service.get_customer("C000001")

    customer_service.get_customer.assert_called_once_with("C000001")
    assert result is expected


def test_customers_delegates(service, customer_service):
    expected = [object()]
    customer_service.all_customers.return_value = expected

    result = service.customers()

    customer_service.all_customers.assert_called_once_with()
    assert result is expected


def test_update_customer_delegates(service, customer_service):
    customer = object()
    expected = object()
    customer_service.update_customer.return_value = expected

    result = service.update_customer(customer)

    customer_service.update_customer.assert_called_once_with(customer)
    assert result is expected


def test_activate_customer_delegates(service, customer_service):
    expected = object()
    customer_service.activate_customer.return_value = expected

    result = service.activate_customer("C000001")

    customer_service.activate_customer.assert_called_once_with("C000001")
    assert result is expected


def test_deactivate_customer_delegates(service, customer_service):
    expected = object()
    customer_service.deactivate_customer.return_value = expected

    result = service.deactivate_customer("C000001")

    customer_service.deactivate_customer.assert_called_once_with("C000001")
    assert result is expected


def test_archive_customer_delegates(service, customer_service):
    expected = object()
    customer_service.archive_customer.return_value = expected

    result = service.archive_customer("C000001")

    customer_service.archive_customer.assert_called_once_with("C000001")
    assert result is expected


def test_customer_statistics_delegates(service, customer_service):
    expected = {"total": 1}
    customer_service.statistics.return_value = expected

    result = service.customer_statistics()

    customer_service.statistics.assert_called_once_with()
    assert result is expected


def test_find_customer_by_email_delegates(service, customer_service):
    expected = object()
    customer_service.find_by_email.return_value = expected

    result = service.find_customer_by_email("john@example.com")

    customer_service.find_by_email.assert_called_once_with(
        "john@example.com"
    )
    assert result is expected


def test_find_customer_by_national_id_delegates(
    service,
    customer_service,
):
    expected = object()
    customer_service.find_by_national_id.return_value = expected

    result = service.find_customer_by_national_id("1234567890")

    customer_service.find_by_national_id.assert_called_once_with(
        "1234567890"
    )
    assert result is expected


def test_search_customers_delegates(service, customer_service):
    expected = [object()]
    customer_service.search_by_name.return_value = expected

    result = service.search_customers("John")

    customer_service.search_by_name.assert_called_once_with("John")
    assert result is expected


# ------------------------------------------------------------------
# Account delegation
# ------------------------------------------------------------------


def test_open_account_delegates_with_initial_deposit(
    service,
    account_service,
):
    account = object()
    initial_deposit = object()
    expected = object()
    account_service.open_account.return_value = expected

    result = service.open_account(
        account,
        initial_deposit,
    )

    account_service.open_account.assert_called_once_with(
        account,
        initial_deposit,
    )
    assert result is expected


def test_open_account_delegates_default_initial_deposit(
    service,
    account_service,
):
    account = object()
    expected = object()
    account_service.open_account.return_value = expected

    result = service.open_account(account)

    account_service.open_account.assert_called_once_with(
        account,
        None,
    )
    assert result is expected


def test_get_account_delegates(service, account_service):
    expected = object()
    account_service.get_account.return_value = expected

    result = service.get_account("SA-100001")

    account_service.get_account.assert_called_once_with("SA-100001")
    assert result is expected


def test_accounts_delegates(service, account_service):
    expected = [object()]
    account_service.all_accounts.return_value = expected

    result = service.accounts()

    account_service.all_accounts.assert_called_once_with()
    assert result is expected


def test_deposit_delegates_defaults(
    service,
    account_service,
):
    expected = object()
    account_service.deposit.return_value = expected

    result = service.deposit(
        "SA-100001",
        100,
    )

    account_service.deposit.assert_called_once_with(
        "SA-100001",
        100,
        "Deposit",
    )
    assert result is expected


def test_deposit_delegates_custom_description(
    service,
    account_service,
):
    expected = object()
    account_service.deposit.return_value = expected

    result = service.deposit(
        "SA-100001",
        100,
        "Salary",
    )

    account_service.deposit.assert_called_once_with(
        "SA-100001",
        100,
        "Salary",
    )
    assert result is expected


def test_withdraw_delegates_defaults(
    service,
    account_service,
):
    expected = object()
    account_service.withdraw.return_value = expected

    result = service.withdraw(
        "SA-100001",
        50,
    )

    account_service.withdraw.assert_called_once_with(
        "SA-100001",
        50,
        "Withdrawal",
    )
    assert result is expected


def test_withdraw_delegates_custom_description(
    service,
    account_service,
):
    expected = object()
    account_service.withdraw.return_value = expected

    result = service.withdraw(
        "SA-100001",
        50,
        "ATM withdrawal",
    )

    account_service.withdraw.assert_called_once_with(
        "SA-100001",
        50,
        "ATM withdrawal",
    )
    assert result is expected


def test_transfer_delegates_defaults(
    service,
    account_service,
):
    expected = object()
    account_service.transfer.return_value = expected

    result = service.transfer(
        "SA-100001",
        "CA-200001",
        250,
    )

    account_service.transfer.assert_called_once_with(
        "SA-100001",
        "CA-200001",
        250,
        "Transfer",
    )
    assert result is expected


def test_transfer_delegates_custom_description(
    service,
    account_service,
):
    expected = object()
    account_service.transfer.return_value = expected

    result = service.transfer(
        "SA-100001",
        "CA-200001",
        250,
        "Internal transfer",
    )

    account_service.transfer.assert_called_once_with(
        "SA-100001",
        "CA-200001",
        250,
        "Internal transfer",
    )
    assert result is expected


def test_close_account_delegates(service, account_service):
    expected = object()
    account_service.close_account.return_value = expected

    result = service.close_account("SA-100001")

    account_service.close_account.assert_called_once_with("SA-100001")
    assert result is expected


def test_freeze_account_delegates(service, account_service):
    expected = object()
    account_service.freeze_account.return_value = expected

    result = service.freeze_account("SA-100001")

    account_service.freeze_account.assert_called_once_with("SA-100001")
    assert result is expected


def test_unfreeze_account_delegates(service, account_service):
    expected = object()
    account_service.unfreeze_account.return_value = expected

    result = service.unfreeze_account("SA-100001")

    account_service.unfreeze_account.assert_called_once_with("SA-100001")
    assert result is expected


def test_account_balance_delegates(service, account_service):
    expected = object()
    account_service.balance.return_value = expected

    result = service.account_balance("SA-100001")

    account_service.balance.assert_called_once_with("SA-100001")
    assert result is expected


def test_available_balance_delegates(service, account_service):
    expected = object()
    account_service.available_balance.return_value = expected

    result = service.available_balance("SA-100001")

    account_service.available_balance.assert_called_once_with("SA-100001")
    assert result is expected


def test_account_summary_delegates(service, account_service):
    expected = {"account_number": "SA-100001"}
    account_service.account_summary.return_value = expected

    result = service.account_summary("SA-100001")

    account_service.account_summary.assert_called_once_with(
        "SA-100001"
    )
    assert result is expected


def test_account_statistics_delegates(service, account_service):
    expected = {"total": 1}
    account_service.statistics.return_value = expected

    result = service.account_statistics()

    account_service.statistics.assert_called_once_with()
    assert result is expected


def test_customer_accounts_delegates(service, account_service):
    expected = [object()]
    account_service.accounts_for_customer.return_value = expected

    result = service.customer_accounts("C000001")

    account_service.accounts_for_customer.assert_called_once_with(
        "C000001"
    )
    assert result is expected


# ------------------------------------------------------------------
# Transaction delegation
# ------------------------------------------------------------------


def test_record_transaction_delegates(
    service,
    transaction_service,
):
    transaction = object()
    expected = object()
    transaction_service.record_transaction.return_value = expected

    result = service.record_transaction(transaction)

    transaction_service.record_transaction.assert_called_once_with(
        transaction
    )
    assert result is expected


def test_get_transaction_delegates(
    service,
    transaction_service,
):
    expected = object()
    transaction_service.get_transaction.return_value = expected

    result = service.get_transaction("TXN-000001")

    transaction_service.get_transaction.assert_called_once_with(
        "TXN-000001"
    )
    assert result is expected


def test_account_transactions_delegates(
    service,
    transaction_service,
):
    expected = [object()]
    transaction_service.account_transactions.return_value = expected

    result = service.account_transactions("SA-100001")

    transaction_service.account_transactions.assert_called_once_with(
        "SA-100001"
    )
    assert result is expected


def test_customer_transactions_delegates(
    service,
    transaction_service,
):
    expected = [object()]
    transaction_service.customer_transactions.return_value = expected

    result = service.customer_transactions("C000001")

    transaction_service.customer_transactions.assert_called_once_with(
        "C000001"
    )
    assert result is expected


def test_account_statement_delegates(
    service,
    transaction_service,
):
    expected = [{"transaction": "TXN-000001"}]
    transaction_service.account_statement.return_value = expected

    result = service.account_statement("SA-100001")

    transaction_service.account_statement.assert_called_once_with(
        "SA-100001"
    )
    assert result is expected


def test_transaction_summary_delegates(
    service,
    transaction_service,
):
    expected = {"transaction_number": "TXN-000001"}
    transaction_service.transaction_summary.return_value = expected

    result = service.transaction_summary("TXN-000001")

    transaction_service.transaction_summary.assert_called_once_with(
        "TXN-000001"
    )
    assert result is expected


def test_transaction_statistics_delegates(
    service,
    transaction_service,
):
    expected = {"total": 1}
    transaction_service.statistics.return_value = expected

    result = service.transaction_statistics()

    transaction_service.statistics.assert_called_once_with()
    assert result is expected


def test_recent_transactions_delegates_default_limit(
    service,
    transaction_service,
):
    expected = [object()]
    transaction_service.recent_transactions.return_value = expected

    result = service.recent_transactions()

    transaction_service.recent_transactions.assert_called_once_with(10)
    assert result is expected


def test_recent_transactions_delegates_custom_limit(
    service,
    transaction_service,
):
    expected = [object()]
    transaction_service.recent_transactions.return_value = expected

    result = service.recent_transactions(25)

    transaction_service.recent_transactions.assert_called_once_with(25)
    assert result is expected


def test_transaction_listing_delegates(
    service,
    transaction_service,
):
    expected = [object()]
    transaction_service.transaction_listing.return_value = expected

    result = service.transaction_listing()

    transaction_service.transaction_listing.assert_called_once_with()
    assert result is expected


def test_transactions_between_delegates(
    service,
    transaction_service,
):
    start_date = date(2026, 1, 1)
    end_date = date(2026, 1, 31)
    expected = [object()]
    transaction_service.transactions_between.return_value = expected

    result = service.transactions_between(
        start_date,
        end_date,
    )

    transaction_service.transactions_between.assert_called_once_with(
        start_date,
        end_date,
    )
    assert result is expected


# ------------------------------------------------------------------
# Lifecycle
# ------------------------------------------------------------------


def test_refresh_refreshes_all_services(
    service,
    customer_service,
    account_service,
    transaction_service,
):
    service.refresh()

    customer_service.refresh.assert_called_once_with()
    account_service.refresh.assert_called_once_with()
    transaction_service.refresh.assert_called_once_with()


def test_save_changes_saves_all_services(
    service,
    customer_service,
    account_service,
    transaction_service,
):
    service.save_changes()

    customer_service.save_changes.assert_called_once_with()
    account_service.save_changes.assert_called_once_with()
    transaction_service.save_changes.assert_called_once_with()


def test_statistics_combines_all_service_statistics(
    service,
    customer_service,
    account_service,
    transaction_service,
):
    customer_stats = {"total": 5}
    account_stats = {"total": 8}
    transaction_stats = {"total": 12}

    customer_service.statistics.return_value = customer_stats
    account_service.statistics.return_value = account_stats
    transaction_service.statistics.return_value = transaction_stats

    result = service.statistics()

    assert result == {
        "customers": customer_stats,
        "accounts": account_stats,
        "transactions": transaction_stats,
    }

    customer_service.statistics.assert_called_once_with()
    account_service.statistics.assert_called_once_with()
    transaction_service.statistics.assert_called_once_with()


def test_shutdown_delegates_to_save_changes(
    service,
    monkeypatch,
):
    save_changes = MagicMock()
    monkeypatch.setattr(
        service,
        "save_changes",
        save_changes,
    )

    service.shutdown()

    save_changes.assert_called_once_with()


# ------------------------------------------------------------------
# String representations
# ------------------------------------------------------------------


def test_str_reports_service_counts(
    service,
    customer_service,
    account_service,
    transaction_service,
):
    customer_service.customer_count.return_value = 5
    account_service.account_count.return_value = 8
    transaction_service.transaction_count.return_value = 12

    result = str(service)

    assert result == (
        "BankService("
        "customers=5, "
        "accounts=8, "
        "transactions=12)"
    )

    customer_service.customer_count.assert_called_once_with()
    account_service.account_count.assert_called_once_with()
    transaction_service.transaction_count.assert_called_once_with()


def test_repr_reports_underlying_service_classes(service):
    result = repr(service)

    assert result == (
        "BankService("
        "customer_repository=MagicMock, "
        "account_repository=MagicMock, "
        "transaction_repository=MagicMock)"
    )


# ------------------------------------------------------------------
# Exception propagation
# ------------------------------------------------------------------


@pytest.mark.parametrize(
    "method_name,service_mock_name,args",
    [
        (
            "get_customer",
            "get_customer",
            ("C000001",),
        ),
        (
            "get_account",
            "get_account",
            ("SA-100001",),
        ),
        (
            "get_transaction",
            "get_transaction",
            ("TXN-000001",),
        ),
    ],
)
def test_lookup_exceptions_propagate(
    service,
    customer_service,
    account_service,
    transaction_service,
    method_name,
    service_mock_name,
    args,
):
    error = RuntimeError("lookup failed")

    if method_name == "get_customer":
        customer_service.get_customer.side_effect = error
    elif method_name == "get_account":
        account_service.get_account.side_effect = error
    else:
        transaction_service.get_transaction.side_effect = error

    with pytest.raises(RuntimeError, match="lookup failed"):
        getattr(service, method_name)(*args)
