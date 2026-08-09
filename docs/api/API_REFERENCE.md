# Banking Management System — API Reference

## 1. Purpose

This document is the developer-facing reference for the principal public APIs of the current Banking Management System (BMS). It summarizes the domain entities, value objects, repositories, services, application components, and reporting objects that form the application's public programming surface.

The repository implementation is authoritative. Where a method or signature differs from this document, the current source code takes precedence. The reference is intentionally focused on the principal public APIs rather than reproducing every private helper.

## 2. Conventions

- `str | None` means a string or `None`.
- `list[T]` means a mutable list of `T`.
- `tuple[T, ...]` means an immutable tuple of `T`.
- `Money` represents monetary values and carries currency information.
- Domain-specific exceptions should be handled according to the existing exception hierarchy.

## 3. Core Domain Model

### 3.1 `models.base_entity.BaseEntity`

`BaseEntity` is the common entity foundation used by the domain model. It provides identity and lifecycle state used by concrete entities.

Important public concepts include:

- `entity_id`
- `created_at`
- `updated_at`
- `is_active`
- `version`
- `activate()`
- `deactivate()`
- `touch()`

Concrete entities such as customers and accounts build on this base behavior.

### 3.2 `models.person.Person`

`Person` is the person-oriented domain abstraction from which `Customer` derives.

The person model provides common personal information such as:

- First name
- Middle name
- Last name
- Date of birth
- Gender
- National ID
- Email
- Phone number
- Address

`Customer` specializes this abstraction for banking.

### 3.3 `models.customer.Customer`

Constructor:

```python
Customer(
    customer_id: str,
    first_name: str,
    last_name: str,
    date_of_birth: date,
    gender: Gender,
    national_id: str,
    email: str,
    phone_number: str,
    address: Address,
    middle_name: str = "",
    customer_status: CustomerStatus = CustomerStatus.ACTIVE,
    registration_date: date | None = None,
    kyc_completed: bool = False,
)
```

`Customer` represents a bank customer and extends `Person`.

#### Key properties

- `customer_id: str`
- `customer_status: CustomerStatus`
- `registration_date: date`
- `kyc_completed: bool`
- `accounts: tuple[str, ...]`
- `account_count: int`
- `has_accounts: bool`
- `account_numbers: tuple[str, ...]`

#### Account association

```python
add_account(account_number: str) -> None
remove_account(account_number: str) -> None
has_account(account_number: str) -> bool
clear_accounts() -> None
```

#### Customer lifecycle

```python
activate_customer() -> None
suspend_customer() -> None
close_customer() -> None
```

#### KYC and transaction eligibility

```python
complete_kyc() -> None
revoke_kyc() -> None
is_active_customer() -> bool
can_open_new_account() -> bool
can_transact() -> bool
```

#### Presentation and persistence

```python
get_identifier() -> str
to_dict() -> dict[str, Any]
customer_summary() -> dict[str, Any]
display_name() -> str
```

`from_dict(data)` is a class method that reconstructs a customer from persisted data.

### 3.4 `models.account.Account`

`Account` is the abstract base class for banking accounts.

Constructor:

```python
Account(
    account_number: str,
    customer_id: str,
    account_type: AccountType,
    opening_balance: Money,
    currency: str = "SAR",
    opened_date: date | None = None,
    status: AccountStatus = AccountStatus.ACTIVE,
)
```

Because `Account` is abstract, application code should normally instantiate one of its concrete subclasses:

- `SavingsAccount`
- `CurrentAccount`
- `TimeDepositAccount`

#### Key properties

- `account_number: str`
- `customer_id: str`
- `account_type: AccountType`
- `status: AccountStatus`
- `currency: str`
- `balance: Money`
- `available_balance: Money`
- `balance_amount: Decimal`
- `is_overdrawn: bool`
- `has_positive_balance: bool`
- `is_zero_balance: bool`
- `opened_date: date`
- `closed_date: date | None`
- `transaction_ids: tuple[str, ...]`
- `transaction_count: int`
- `is_active_account: bool`
- `is_closed: bool`

#### Balance operations

```python
deposit(amount: Money) -> None
withdraw(amount: Money) -> None
transfer_to(destination: Account, amount: Money) -> None
```

`deposit()` and `withdraw()` enforce active-account and monetary validation. `transfer_to()` performs the domain balance operation; application-level orchestration, persistence, auditing, and related workflow concerns belong to the service layer.

#### Account lifecycle

```python
open_account() -> None
close_account() -> None
```

The current domain rule requires an account balance of zero before closure.

#### Account and transaction helpers

```python
add_transaction(transaction_id: str) -> None
remove_transaction(transaction_id: str) -> None
has_transaction(transaction_id: str) -> bool
```

#### Extensibility hooks

```python
calculate_interest() -> Money
calculate_fee() -> Money
_can_withdraw(amount: Money) -> bool
```

Concrete account types can override the appropriate behavior.

### 3.5 Concrete account classes

#### `SavingsAccount`

Represents a savings account and specializes `Account` with savings-specific interest and account behavior implemented by the current model.

#### `CurrentAccount`

Represents a current account and specializes `Account` with current-account behavior such as the applicable overdraft/fee rules implemented by the current model.

#### `TimeDepositAccount`

Represents a time-deposit account and specializes `Account` with the term/deposit behavior implemented by the current model.

The concrete constructor signatures and specialized methods should be taken directly from the current class definitions when integrating against a specific account type.

## 4. Value Objects

### 4.1 `models.value_objects.money.Money`

`Money` is an immutable, currency-aware monetary value object.

Constructor:

```python
Money(
    amount: str | int | float | Decimal,
    currency: Currency = Currency.SAR,
)
```

The amount is normalized to two decimal places using `ROUND_HALF_EVEN`.

#### Properties

- `amount: Decimal`
- `currency: Currency`
- `is_zero: bool`
- `is_positive: bool`
- `is_negative: bool`

#### Arithmetic

```python
money_a + money_b
money_a - money_b
money_a * value
money_a / value
-money_a
abs(money_a)
```

Addition, subtraction, and comparisons enforce currency compatibility.

#### Comparison

```python
money_a < money_b
money_a <= money_b
money_a > money_b
money_a >= money_b
```

#### Utility methods

```python
percentage(percent: Number) -> Money
allocate(parts: int) -> list[Money]
to_dict() -> dict
```

#### Factories

```python
Money.zero(currency=Currency.SAR) -> Money
Money.one(currency=Currency.SAR) -> Money
```

`Money` is frozen and slotted; arithmetic returns new instances rather than mutating the existing value.

### 4.2 Other value objects

The project also contains value objects such as `Address`. Their constructors and serialization methods should be used instead of manually constructing their persisted representations.

## 5. Service Layer APIs

### 5.1 `services.customer_service.CustomerService`

Constructor:

```python
CustomerService(repository: CustomerRepository)
```

#### Registration and lookup

```python
register_customer(customer: Customer) -> Customer
find_customer(customer_number: str, *, active_only: bool = True) -> Customer | None
get_customer(customer_number: str) -> Customer
customer_exists(customer_number: str) -> bool
all_customers() -> list[Customer]
```

#### Lifecycle and maintenance

```python
update_customer(customer: Customer) -> Customer
deactivate_customer(customer_number: str) -> Customer
activate_customer(customer_number: str) -> Customer
reactivate_customer(customer_number: str) -> Customer
archive_customer(customer_number: str) -> bool
```

#### Search

```python
find_by_national_id(national_id: str) -> Customer | None
find_by_email(email: str) -> Customer | None
find_by_phone(phone_number: str) -> Customer | None
search_by_name(search_text: str) -> list[Customer]
```

#### Status and statistics

```python
active_customers() -> list[Customer]
inactive_customers() -> list[Customer]
active_customer_count() -> int
inactive_customer_count() -> int
statistics() -> dict[str, int]
customer_count() -> int
has_customers() -> bool
```

#### Business validation

```python
ensure_customer_not_exists(customer: Customer) -> None
ensure_customer_exists(customer_number: str) -> Customer
is_customer_eligible(customer_number: str) -> bool
profile_is_complete(customer_number: str) -> bool
validate_customer_for_account_opening(customer_number: str) -> Customer
```

#### Summaries and persistence helpers

```python
customer_directory() -> list[Customer]
customer_summary(customer_number: str) -> dict[str, object]
customer_listing() -> list[dict[str, object]]
validate_repository() -> bool
repository_statistics() -> dict[str, object]
refresh() -> None
save_changes() -> None
ensure_repository_is_valid() -> None
```

### 5.2 `services.account_service.AccountService`

Constructor:

```python
AccountService(
    account_repository: AccountRepository,
    customer_repository: CustomerRepository,
    transaction_repository: TransactionRepository,
)
```

The service coordinates account persistence with customer and transaction repositories.

#### Lookup

```python
get_account(account_number: str) -> Account
account_exists(account_number: str) -> bool
get_customer(customer_number: str) -> Customer
customer_is_eligible(customer_number: str) -> bool
all_accounts() -> list[Account]
```

#### Account opening and customer relationships

```python
open_account(
    account: Account,
    initial_deposit: Money | None = None,
) -> Account
validate_account(account_number: str) -> Account
customer_accounts(customer_number: str) -> list[Account]
customer_account_count(customer_number: str) -> int
customer_has_accounts(customer_number: str) -> bool
```

`open_account()` can perform an optional positive initial deposit after successful account creation.

#### Financial operations

```python
deposit(
    account_number: str,
    amount: Money,
    description: str = "Deposit",
) -> Account

withdraw(
    account_number: str,
    amount: Money,
    description: str = "Withdrawal",
) -> Account

transfer(
    from_account_number: str,
    to_account_number: str,
    amount: Money,
    description: str = "Transfer",
) -> tuple[Account, Account]

balance(account_number: str) -> Money
```

Transfers reject identical source and destination account numbers and validate both accounts before performing the debit/credit operations.

### 5.3 `services.transaction_service.TransactionService`

Constructor:

```python
TransactionService(
    transaction_repository: TransactionRepository,
    account_repository: AccountRepository,
)
```

#### Recording and lookup

```python
record_transaction(transaction: Transaction) -> Transaction
get_transaction(transaction_number: str) -> Transaction
transaction_exists(transaction_number: str) -> bool
all_transactions() -> list[Transaction]
account(account_number: str) -> Account
```

#### Search

```python
account_transactions(account_number: str) -> list[Transaction]
customer_transactions(customer_number: str) -> list[Transaction]
transactions_by_type(transaction_type) -> list[Transaction]
transactions_between(start_date: date, end_date: date) -> list[Transaction]
recent_transactions(limit: int = 10) -> list[Transaction]
```

#### Statements and summaries

```python
account_statement(account_number: str) -> list[dict[str, object]]
transaction_summary(transaction_number: str) -> dict[str, object]
transaction_listing() -> list[dict[str, object]]
```

#### Statistics

```python
transaction_count() -> int
has_transactions() -> bool
debit_total(account_number: str) -> Money
credit_total(account_number: str) -> Money
statistics() -> dict[str, object]
account_statistics(account_number: str) -> dict[str, object]
average_transaction_amount(account_number: str) -> Money
largest_transaction(account_number: str) -> Transaction | None
customer_statistics(customer_number: str) -> dict[str, object]
repository_statistics() -> dict[str, object]
```

#### Date and repository helpers

```python
transactions_on(transaction_date: date) -> list[Transaction]
transactions_before(transaction_date: date) -> list[Transaction]
transactions_after(transaction_date: date) -> list[Transaction]
latest_transaction(account_number: str) -> Transaction | None
first_transaction(account_number: str) -> Transaction | None
refresh() -> None
save_changes() -> None
validate_repository() -> bool
ensure_repository_is_valid() -> None
```

## 6. Repository APIs

The repository layer provides persistence-oriented APIs. Concrete repositories include:

- `CustomerRepository`
- `AccountRepository`
- `TransactionRepository`

They are consumed primarily through the service layer.

Common repository concepts include:

```python
add_*(entity)
get_or_raise(identifier)
find_*(criteria)
exists(identifier)
delete_entity(entity_id)
save_entity(entity)
statistics()
```

The exact method names are repository-specific. Application code should prefer service APIs for business operations and use repositories directly when implementing persistence-oriented infrastructure or repository tests.

## 7. Reporting API

### 7.1 `reporting.report_generator.ReportMetadata`

Frozen dataclass:

```python
ReportMetadata(
    title: str,
    generated_at: datetime,
    generated_by: str = "Banking Management System",
    version: str = "1.0",
)
```

### 7.2 `reporting.report_generator.Report`

Dataclass:

```python
Report(
    metadata: ReportMetadata,
    columns: tuple[str, ...],
    rows: list[tuple[Any, ...]] = [],
)
```

#### Properties

```python
row_count -> int
```

#### Methods

```python
add_row(*values: Any) -> None
as_dicts() -> list[dict[str, Any]]
clear() -> None
```

`add_row()` raises `ValueError` when the number of supplied values does not match the number of columns.

### 7.3 `reporting.report_generator.ReportGenerator`

Factory helper:

```python
ReportGenerator.create_report(
    *,
    title: str,
    columns: tuple[str, ...],
    generated_by: str = "Banking Management System",
    version: str = "1.0",
) -> Report
```

The generator creates metadata with the current timestamp and returns an empty `Report`.

### 7.4 Domain report services

The reporting package contains specialized reporting services for customer, account, transaction, and bank reports. These services consume application/domain data and produce `Report` objects and exportable representations.

Consult the individual module definitions for specialized method signatures when integrating against a particular report.

## 8. Application and Composition APIs

### `application.dependency_container.DependencyContainer`

The dependency container is the composition root. It constructs shared repositories, services, logging infrastructure, and the application service graph.

Application-level code should obtain services through the container rather than creating competing service graphs.

The startup/bootstrap modules prepare the runtime environment, including required storage directories and dependency validation.

## 9. CLI API Surface

The CLI is composed of menu definitions, command handlers, dispatching, input handling, and rendering.

The current top-level menu areas are:

- Customer Management
- Account Management
- Transaction Management
- Reporting
- Administration
- System Information
- Exit

CLI commands are presentation-layer adapters. They should invoke service/application APIs rather than reproduce domain business rules.

## 10. Exceptions

The project defines a domain/application exception hierarchy exposed through the `exceptions` package. Important categories include:

- `ValidationError`
- `EntityAlreadyExistsError`
- `EntityNotFoundError`
- `PersistenceError`

Additional specialized exceptions may be defined by the banking domain modules.

Use the most specific applicable exception and preserve the established exception semantics when extending the application.

## 11. API Usage Example

A simplified service-oriented workflow is:

```python
customer = customer_service.get_customer(customer_number)

account = account_service.get_account(account_number)

account_service.deposit(
    account.account_number,
    Money("250.00", Currency.SAR),
    description="Cash deposit",
)

balance = account_service.balance(
    account.account_number,
)
```

The example illustrates the intended layering: application code uses services, services coordinate repositories, and domain objects represent banking state.

## 12. Error and Validation Expectations

API callers should expect validation or domain exceptions when:

- Required identifiers are missing or invalid.
- An entity does not exist.
- An entity already exists where uniqueness is required.
- An account is inactive or closed.
- A monetary value is invalid.
- Currency values are incompatible.
- A withdrawal exceeds the applicable available balance.
- A transfer uses the same source and destination account.
- Persistence integrity checks fail.

Callers should not convert all domain exceptions into a generic success/failure flag; preserving the exception meaning makes error handling more precise.

## 13. API Stability Guidance

The current API is the implementation validated by the repository's automated test suite. When changing public constructors or methods:

1. Search the repository for all callers.
2. Update unit and integration tests.
3. Update CLI adapters where applicable.
4. Update reporting consumers where applicable.
5. Update this API Reference.
6. Run the full suite.
7. Update class and sequence diagrams when relationships or workflows change.

Avoid unnecessary signature changes. A constructor or method signature is part of the practical contract between the layers.

## 14. Validation Baseline

The current repository validation baseline is:

```text
pytest tests/reporting
70 passed in 0.55s

pytest
1,439 passed in 10.35s
```

The API reference should remain synchronized with the code that produces this baseline.

## 15. Related Documentation

- [`README.md`](../../README.md) — project overview
- [`Architecture Guide`](../architecture/ARCHITECTURE_GUIDE.md) — architecture and design
- [`User Guide`](../user/USER_GUIDE.md) — end-user workflows
- [`Developer Guide`](../developer/DEVELOPER_GUIDE.md) — development practices
- `docs/installation/INSTALLATION_GUIDE.md` — installation
- `docs/diagrams/CLASS_DIAGRAMS.md` — class diagrams
- `docs/diagrams/SEQUENCE_DIAGRAMS.md` — sequence diagrams

## 16. Source-of-Truth Rule

This reference is intentionally concise enough to remain maintainable. The current Python source, package exports, and automated tests are authoritative for exact implementation behavior. When a future implementation change alters a public API, update this document in the same change set whenever practical.
