# Banking Management System — Class Diagrams

## 1. Purpose

This document provides the principal structural class diagrams for the current Banking Management System (BMS). The diagrams are written in Mermaid so they remain version-controlled Markdown artifacts and can be rendered by compatible GitHub/documentation viewers.

The diagrams describe the implemented architectural relationships at a useful level of abstraction. The Python source remains authoritative for exact signatures and implementation details.

## 2. Domain Model

The central domain hierarchy demonstrates the project's OOP use of abstraction, inheritance, encapsulation, and polymorphism.

```mermaid
classDiagram
    class BaseEntity {
        <<abstract/common>>
        +UUID entity_id
        +datetime created_at
        +datetime updated_at
        +bool is_active
        +int version
        +activate()
        +deactivate()
        +touch()
    }

    class Person {
        <<abstract>>
        +str first_name
        +str middle_name
        +str last_name
        +date date_of_birth
        +Gender gender
        +str national_id
        +str email
        +str phone_number
        +Address address
        +str full_name
        +int age
        +bool is_adult
        +display_name()
        +initials()
        +update_name()
        +update_contact_information()
        +update_personal_information()
        +get_identifier()*
        +to_dict()*
        +from_dict()*
    }

    class Customer {
        +str customer_id
        +CustomerStatus customer_status
        +date registration_date
        +bool kyc_completed
        +tuple accounts
        +int account_count
        +bool has_accounts
        +add_account()
        +remove_account()
        +has_account()
        +clear_accounts()
        +activate_customer()
        +suspend_customer()
        +close_customer()
        +complete_kyc()
        +revoke_kyc()
        +can_open_new_account()
        +can_transact()
        +customer_summary()
        +get_identifier()
        +to_dict()
        +from_dict()
    }

    class Employee {
        <<future/other Person specialization>>
    }

    BaseEntity <|-- Person
    Person <|-- Customer
    Person <|-- Employee
```

### Interpretation

- `BaseEntity` supplies common entity identity and lifecycle state.
- `Person` is abstract and contains information common to people represented by the system.
- `Customer` specializes `Person` with banking-specific identity, KYC, status, and account associations.
- `Employee` is represented by the existing `Person` abstraction as another possible specialization; the exact implementation should remain synchronized with the source tree.

## 3. Account Hierarchy

```mermaid
classDiagram
    class BaseEntity {
        <<common>>
        +UUID entity_id
        +datetime created_at
        +datetime updated_at
        +bool is_active
        +int version
        +activate()
        +deactivate()
        +touch()
    }

    class Account {
        <<abstract>>
        +str account_number
        +str customer_id
        +AccountType account_type
        +AccountStatus status
        +str currency
        +Money balance
        +Money available_balance
        +Decimal balance_amount
        +bool is_overdrawn
        +bool is_active_account
        +bool is_closed
        +date opened_date
        +date closed_date
        +tuple transaction_ids
        +int transaction_count
        +deposit(amount)
        +withdraw(amount)
        +transfer_to(destination, amount)
        +open_account()
        +close_account()
        +add_transaction(transaction_id)
        +remove_transaction(transaction_id)
        +has_transaction(transaction_id)
        +calculate_interest() Money
        +calculate_fee() Money
        +_can_withdraw(amount) bool
    }

    class SavingsAccount {
        <<concrete>>
        +savings-specific rules
    }

    class CurrentAccount {
        <<concrete>>
        +current-account rules
    }

    class TimeDepositAccount {
        <<concrete>>
        +term-deposit rules
    }

    class Money {
        <<value object>>
        +Decimal amount
        +Currency currency
        +bool is_zero
        +bool is_positive
        +bool is_negative
        +percentage(percent)
        +allocate(parts)
        +to_dict()
    }

    BaseEntity <|-- Account
    Account <|-- SavingsAccount
    Account <|-- CurrentAccount
    Account <|-- TimeDepositAccount
    Account --> Money : balance
```

### Interpretation

`Account` defines the common banking-account contract. Concrete account types specialize rules such as withdrawal eligibility, interest, fees, or term behavior. The service layer is responsible for coordinating account operations with transaction persistence.

## 4. Customer–Account Relationship

```mermaid
classDiagram
    class Customer {
        +str customer_id
        +CustomerStatus customer_status
        +bool kyc_completed
        +tuple accounts
        +add_account(account_number)
        +remove_account(account_number)
        +can_open_new_account()
        +can_transact()
    }

    class Account {
        <<abstract>>
        +str account_number
        +str customer_id
        +Money balance
        +AccountStatus status
    }

    Customer "1" --> "0..*" Account : owns
```

The implementation stores account identifiers on `Customer` and the owning customer identifier on `Account`. This provides the association without making either object responsible for persistence of the other.

## 5. Transaction Relationships

```mermaid
classDiagram
    class Account {
        +str account_number
        +str customer_id
        +Money balance
        +tuple transaction_ids
        +add_transaction(transaction_id)
    }

    class Transaction {
        +str transaction_id
        +str account_number
        +TransactionType transaction_type
        +Money amount
        +date transaction_date
        +str description
    }

    Account "1" --> "0..*" Transaction : records
```

The account retains transaction identifiers while the transaction entity contains the transaction record. The transaction repository provides persistence for the transaction records.

## 6. Value Objects

```mermaid
classDiagram
    class Money {
        <<immutable value object>>
        +Decimal amount
        +Currency currency
        +is_zero
        +is_positive
        +is_negative
        +percentage(percent)
        +allocate(parts)
        +to_dict()
    }

    class Address {
        <<value object>>
        +str street
        +str city
        +str state
        +str postal_code
        +str country
        +to_dict()
        +from_dict(data)
    }

    class Customer {
        +Address address
        +Money account balances via Account
    }

    class Account {
        +Money balance
    }

    Customer --> Address : has
    Account --> Money : has
```

Value objects encapsulate validation and representation of concepts that should not be treated as primitive strings or numbers throughout the domain.

## 7. Service Layer

```mermaid
classDiagram
    class CustomerRepository {
        <<repository>>
        +persistence operations
    }

    class AccountRepository {
        <<repository>>
        +persistence operations
    }

    class TransactionRepository {
        <<repository>>
        +persistence operations
    }

    class CustomerService {
        +register_customer(customer)
        +get_customer(customer_number)
        +find_customer(customer_number)
        +update_customer(customer)
        +activate_customer(customer_number)
        +deactivate_customer(customer_number)
        +all_customers()
        +search_by_name(search_text)
        +validate_customer_for_account_opening(customer_number)
    }

    class AccountService {
        +open_account(account, initial_deposit)
        +get_account(account_number)
        +customer_accounts(customer_number)
        +deposit(account_number, amount, description)
        +withdraw(account_number, amount, description)
        +transfer(from_account_number, to_account_number, amount, description)
        +balance(account_number)
    }

    class TransactionService {
        +record_transaction(transaction)
        +get_transaction(transaction_number)
        +account_transactions(account_number)
        +customer_transactions(customer_number)
        +transactions_between(start_date, end_date)
        +account_statement(account_number)
        +recent_transactions(limit)
    }

    CustomerService --> CustomerRepository : uses
    AccountService --> AccountRepository : uses
    AccountService --> CustomerRepository : uses
    AccountService --> TransactionRepository : uses
    TransactionService --> TransactionRepository : uses
    TransactionService --> AccountRepository : uses
```

### Responsibility boundary

- Repositories persist and retrieve data.
- Services enforce workflow-level rules and coordinate repositories.
- Domain entities own domain state and domain operations.
- CLI components should call services rather than bypassing them for banking workflows.

## 8. Dependency Container

```mermaid
classDiagram
    class DependencyContainer {
        +Config config
        +CustomerRepository customer_repository
        +AccountRepository account_repository
        +TransactionRepository transaction_repository
        +CustomerService customer_service
        +AccountService account_service
        +TransactionService transaction_service
        +BankService bank_service
        +validate()
    }

    class Config {
        +application settings
        +bank settings
        +storage settings
        +CSV paths
        +interest rates
        +fees
        +logging settings
    }

    class CustomerService
    class AccountService
    class TransactionService
    class BankService
    class CustomerRepository
    class AccountRepository
    class TransactionRepository

    DependencyContainer --> Config
    DependencyContainer --> CustomerRepository
    DependencyContainer --> AccountRepository
    DependencyContainer --> TransactionRepository
    DependencyContainer --> CustomerService
    DependencyContainer --> AccountService
    DependencyContainer --> TransactionService
    DependencyContainer --> BankService
```

The dependency container acts as the composition root. It ensures application components share the same configured repository and service instances rather than constructing disconnected graphs.

## 9. Reporting Model

```mermaid
classDiagram
    class ReportMetadata {
        <<frozen dataclass>>
        +str title
        +datetime generated_at
        +str generated_by
        +str version
    }

    class Report {
        +ReportMetadata metadata
        +tuple columns
        +list rows
        +int row_count
        +add_row(*values)
        +as_dicts()
        +clear()
    }

    class ReportGenerator {
        <<factory>>
        +create_report(title, columns, generated_by, version) Report
    }

    class CustomerReports {
        +customer reporting operations
    }

    class AccountReports {
        +account reporting operations
    }

    class TransactionReports {
        +transaction reporting operations
    }

    class BankReports {
        +bank reporting operations
    }

    class ExportService {
        +export operations
    }

    Report --> ReportMetadata
    ReportGenerator ..> Report : creates
    CustomerReports ..> Report : produces
    AccountReports ..> Report : produces
    TransactionReports ..> Report : produces
    BankReports ..> Report : produces
    ExportService ..> Report : exports
```

## 10. CLI and Application Boundary

```mermaid
classDiagram
    class Application {
        +run()
        +start()
        +shutdown()
    }

    class CommandDispatcher {
        +dispatch(command)
    }

    class InputHandler {
        +read_input()
        +read_integer()
        +read_decimal()
        +confirm()
    }

    class Menu {
        +display()
        +select()
    }

    class MenuRenderer {
        +render_menu()
        +render_result()
        +render_error()
    }

    class CustomerCommands
    class AccountCommands
    class TransactionCommands
    class ReportingCommands

    class DependencyContainer

    Application --> DependencyContainer : uses
    Application --> Menu : runs
    Menu --> InputHandler : reads input
    Menu --> MenuRenderer : renders
    CommandDispatcher --> CustomerCommands
    CommandDispatcher --> AccountCommands
    CommandDispatcher --> TransactionCommands
    CommandDispatcher --> ReportingCommands
    CustomerCommands --> CustomerService : calls
    AccountCommands --> AccountService : calls
    TransactionCommands --> TransactionService : calls
    ReportingCommands --> Report : consumes
```

## 11. Overall Component/Class Relationship

The following simplified diagram combines the principal layers without showing every method.

```mermaid
classDiagram
    class CLI
    class Application
    class DependencyContainer
    class CustomerService
    class AccountService
    class TransactionService
    class BankService
    class CustomerRepository
    class AccountRepository
    class TransactionRepository
    class Customer
    class Account
    class SavingsAccount
    class CurrentAccount
    class TimeDepositAccount
    class Transaction
    class Money

    CLI --> Application
    Application --> DependencyContainer

    DependencyContainer --> CustomerService
    DependencyContainer --> AccountService
    DependencyContainer --> TransactionService
    DependencyContainer --> BankService

    CustomerService --> CustomerRepository
    AccountService --> AccountRepository
    AccountService --> CustomerRepository
    AccountService --> TransactionRepository
    TransactionService --> TransactionRepository
    TransactionService --> AccountRepository

    CustomerService --> Customer
    AccountService --> Account
    TransactionService --> Transaction

    Account <|-- SavingsAccount
    Account <|-- CurrentAccount
    Account <|-- TimeDepositAccount
    Account --> Money
    Customer "1" --> "0..*" Account
    Account "1" --> "0..*" Transaction
```

## 12. Design Principles Illustrated

### Abstraction

`Person` and `Account` expose abstract contracts while concrete domain classes provide specialized implementations.

### Encapsulation

Domain state is managed through properties and domain methods rather than unrestricted direct mutation.

### Inheritance

`Customer` derives from `Person`; concrete account classes derive from `Account`.

### Polymorphism

Concrete account classes can specialize account operations such as withdrawal eligibility, interest, fees, and other account-specific behavior.

### Composition

Services compose repositories; the dependency container composes the service/repository graph; domain objects compose value objects such as `Money` and `Address`.

## 13. Diagram Maintenance Rules

Update these diagrams when a change affects:

- Class inheritance
- Major class composition
- Service/repository relationships
- Domain associations
- Dependency injection
- Reporting architecture
- CLI/application boundaries

Do not change a diagram merely to represent a proposed future architecture. The diagrams must describe the implemented system.

When exact method signatures are needed, consult [`API_REFERENCE.md`](../api/API_REFERENCE.md) and the Python source.

## 14. Validation

The diagrams are documentation artifacts and do not replace automated tests. The current functional baseline is:

```text
pytest tests/reporting
70 passed in 0.55s

pytest
1,439 passed in 10.35s
```

## 15. Related Documentation

- [`README.md`](../../README.md)
- [`Architecture Guide`](../architecture/ARCHITECTURE_GUIDE.md)
- [`User Guide`](../user/USER_GUIDE.md)
- [`Developer Guide`](../developer/DEVELOPER_GUIDE.md)
- [`Installation Guide`](../installation/INSTALLATION_GUIDE.md)
- [`API Reference`](../api/API_REFERENCE.md)
- `SEQUENCE_DIAGRAMS.md`
