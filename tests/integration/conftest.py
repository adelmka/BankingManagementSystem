"""Integration-test fixtures for the current BMS service contracts."""

from datetime import date

import pytest

from models.customer import Customer
from models.savings_account import SavingsAccount
from models.value_objects.address import Address
from models.value_objects.money import Money
from repositories.account_repository import AccountRepository
from repositories.customer_repository import CustomerRepository
from repositories.transaction_repository import TransactionRepository
from services.account_service import AccountService
from services.customer_service import CustomerService
from services.transaction_service import TransactionService
from utils.constants import CustomerStatus, Gender


@pytest.fixture
def e2e_repositories(tmp_path, monkeypatch):
    """Create isolated real repositories backed by temporary CSV files."""
    data_dir = tmp_path / "data"
    data_dir.mkdir()

    customer_file = data_dir / "customers.csv"
    account_file = data_dir / "accounts.csv"
    transaction_file = data_dir / "transactions.csv"

    monkeypatch.setattr(CustomerRepository, "CSV_FILE", customer_file)
    monkeypatch.setattr(AccountRepository, "CSV_FILE", account_file)
    monkeypatch.setattr(TransactionRepository, "CSV_FILE", transaction_file)

    return {
        "customer": CustomerRepository(),
        "account": AccountRepository(),
        "transaction": TransactionRepository(),
    }


@pytest.fixture
def customer_repository(e2e_repositories):
    return e2e_repositories["customer"]


@pytest.fixture
def account_repository(e2e_repositories):
    return e2e_repositories["account"]


@pytest.fixture
def transaction_repository(e2e_repositories):
    return e2e_repositories["transaction"]


@pytest.fixture
def customer_service(customer_repository):
    return CustomerService(customer_repository)


@pytest.fixture
def account_service(e2e_repositories):
    return AccountService(
        account_repository=e2e_repositories["account"],
        customer_repository=e2e_repositories["customer"],
        transaction_repository=e2e_repositories["transaction"],
    )


@pytest.fixture
def transaction_service(e2e_repositories):
    return TransactionService(
        transaction_repository=e2e_repositories["transaction"],
        account_repository=e2e_repositories["account"],
    )


@pytest.fixture
def banking_system(customer_service, account_service, transaction_service):
    return {
        "customer_service": customer_service,
        "account_service": account_service,
        "transaction_service": transaction_service,
    }


def make_customer(customer_id="CUST001", index=1):
    return Customer(
        customer_id=customer_id,
        first_name="John",
        last_name="Smith",
        date_of_birth=date(1990, 1, 15),
        gender=Gender.MALE,
        national_id=f"700000000{index:03}",
        email=f"integration-{index}@bank.com",
        phone_number=f"+966501000{index:03}",
        address=Address(
            address_line_1="123 Main Street",
            address_line_2="",
            city="Riyadh",
            state_or_province="Riyadh",
            postal_code="12345",
            country="Saudi Arabia",
        ),
        middle_name="",
        customer_status=CustomerStatus.ACTIVE,
        registration_date=date.today(),
        kyc_completed=True,
    )


@pytest.fixture
def sample_customer(customer_service):
    return customer_service.register_customer(make_customer())


@pytest.fixture
def sample_account(account_service, sample_customer):
    account = SavingsAccount(
        account_number="SAV001",
        customer_id="CUST001",
        opening_balance=Money("1000"),
        interest_rate=0.025,
        minimum_balance=Money("0"),
    )
    return account_service.open_account(account)


@pytest.fixture
def reload_customer_repository(customer_repository):
    def factory():
        repo = CustomerRepository()
        repo.load()
        return repo
    return factory


@pytest.fixture
def reload_account_repository(account_repository):
    def factory():
        repo = AccountRepository()
        repo.load()
        return repo
    return factory


@pytest.fixture
def reload_transaction_repository(transaction_repository):
    def factory():
        repo = TransactionRepository()
        repo.load()
        return repo
    return factory
