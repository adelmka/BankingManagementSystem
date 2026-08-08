"""Integration tests for AccountService and account persistence."""

from decimal import Decimal

import pytest

from exceptions.banking_exceptions import (
    EntityNotFoundError,
    ValidationError,
)
from models.savings_account import SavingsAccount
from models.value_objects.money import Money
from tests.integration.conftest import make_customer


def register_customer(customer_service):
    return customer_service.register_customer(make_customer())


def open_savings(account_service, customer_id="CUST001", number="SAV001", balance="1000"):
    return account_service.open_account(
        SavingsAccount(
            account_number=number,
            customer_id=customer_id,
            opening_balance=Money(balance),
            interest_rate=Decimal("0.025"),
            minimum_balance=Money("0"),
        )
    )


def test_open_savings_account(customer_service, account_service):
    register_customer(customer_service)
    account = open_savings(account_service)
    assert account.account_number == "SAV001"
    assert account.customer_id == "CUST001"


def test_get_account(customer_service, account_service):
    register_customer(customer_service)
    open_savings(account_service)
    account = account_service.get_account("SAV001")
    assert account.account_number == "SAV001"


def test_deposit(customer_service, account_service):
    register_customer(customer_service)
    open_savings(account_service)
    account_service.deposit("SAV001", Money("500"))
    assert account_service.balance("SAV001").amount == Decimal("1500.00")


def test_withdraw(customer_service, account_service):
    register_customer(customer_service)
    open_savings(account_service)
    account_service.withdraw("SAV001", Money("300"))
    assert account_service.balance("SAV001").amount == Decimal("700.00")


def test_transfer(customer_service, account_service):
    register_customer(customer_service)
    open_savings(account_service, number="SAV001", balance="1000")
    open_savings(account_service, number="SAV002", balance="500")
    account_service.transfer("SAV001", "SAV002", Money("250"))
    assert account_service.balance("SAV001").amount == Decimal("750.00")
    assert account_service.balance("SAV002").amount == Decimal("750.00")


def test_customer_accounts(customer_service, account_service):
    register_customer(customer_service)
    open_savings(account_service, number="SAV001")
    open_savings(account_service, number="SAV002")
    accounts = account_service.customer_accounts("CUST001")
    assert len(accounts) == 2
    assert account_service.customer_account_count("CUST001") == 2


def test_invalid_account(customer_service, account_service):
    register_customer(customer_service)
    with pytest.raises(ValidationError):
        SavingsAccount(
            account_number="",
            customer_id="CUST001",
            opening_balance=Money("1000"),
            interest_rate=Decimal("0.025"),
            minimum_balance=Money("0"),
        )


def test_insufficient_funds(customer_service, account_service):
    register_customer(customer_service)
    open_savings(account_service, balance="100")
    with pytest.raises(ValueError, match="Insufficient available balance"):
        account_service.withdraw("SAV001", Money("500"))


def test_account_persistence(customer_service, account_service, reload_account_repository):
    register_customer(customer_service)
    open_savings(account_service)
    repository = reload_account_repository()
    account = repository.find_by_account_number("SAV001")
    assert account is not None
    assert account.account_number == "SAV001"


def test_account_restart(customer_service, account_service, reload_account_repository):
    register_customer(customer_service)
    open_savings(account_service, number="SAV001", balance="2000")
    restarted = reload_account_repository()
    account = restarted.find_by_account_number("SAV001")
    assert account is not None
    assert account.balance.amount == Decimal("2000.00")


def test_missing_account(account_service):
    with pytest.raises(EntityNotFoundError):
        account_service.get_account("UNKNOWN")
