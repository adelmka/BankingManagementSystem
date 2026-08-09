# Banking Management System — Sequence Diagrams

## 1. Purpose

This document describes the principal runtime interactions in the current Banking Management System (BMS). The diagrams use Mermaid sequence-diagram syntax so they remain version-controlled and can be rendered by compatible GitHub/Markdown viewers.

The diagrams describe the implemented application flow at the architectural level. They intentionally avoid inventing infrastructure or external integrations that are not part of the current implementation.

## 2. Participants and Layering

The principal runtime boundaries are:

```text
User / CLI
    |
    v
Application / Commands
    |
    v
Service Layer
    |
    +--> Domain Models
    |
    +--> Repository Layer
              |
              v
         CSV Persistence
```

The application bootstrap prepares storage and constructs the `Application`. The `Application` builds the dependency graph and exposes the `BankService` façade. fileciteturn38file0 fileciteturn39file0

---

## 3. Application Startup

Startup is coordinated by `Bootstrap.initialize()`. It initializes storage, validates storage readiness, and then constructs the `Application`. fileciteturn38file0

```mermaid
sequenceDiagram
    autonumber
    actor User
    participant Bootstrap
    participant Storage as StorageInitializer
    participant Application
    participant Container as DependencyContainer
    participant Bank as BankService

    User->>Bootstrap: initialize()
    Bootstrap->>Storage: initialize()
    Storage-->>Bootstrap: storage ready
    Bootstrap->>Storage: validate()
    Storage-->>Bootstrap: valid
    Bootstrap->>Application: Application(config)
    Application->>Container: build(config)
    Container->>Bank: construct service façade
    Container-->>Application: dependency graph ready
    Application-->>Bootstrap: initialized Application
    Bootstrap-->>User: application ready
```

If storage validation fails, bootstrap raises a `RuntimeError` and does not return a running application. fileciteturn38file0

---

## 4. Application Health and Shutdown

The `Application` exposes the bank façade, configuration, running-state check, and graceful shutdown. The running-state check delegates to dependency-container validation. fileciteturn39file0

```mermaid
sequenceDiagram
    autonumber
    participant Caller
    participant Application
    participant Container as DependencyContainer

    Caller->>Application: is_running
    Application->>Container: validate()
    Container-->>Application: validation result
    Application-->>Caller: True / False

    Caller->>Application: shutdown()
    Application->>Container: shutdown()
    Container-->>Application: shutdown complete
    Application-->>Caller: None
```

---

## 5. Customer Registration

Customer registration follows the normal presentation-to-service-to-repository direction. The CLI collects user input; the service validates and persists the customer through the repository.

```mermaid
sequenceDiagram
    autonumber
    actor User
    participant CLI as Customer Command
    participant Service as CustomerService
    participant Repo as CustomerRepository
    participant Customer

    User->>CLI: Enter customer information
    CLI->>Service: register_customer(customer)
    Service->>Service: validate customer
    Service->>Repo: check existing customer
    Repo-->>Service: no duplicate
    Service->>Repo: save customer
    Repo-->>Service: persisted customer
    Service-->>CLI: Customer
    CLI-->>User: Display registration result
```

The exact validation rules and repository method names remain implementation-defined by the current service/repository source.

---

## 6. Account Opening

Account opening is coordinated by the account service. The service validates the customer and account, persists the new account, and can process an optional initial deposit.

```mermaid
sequenceDiagram
    autonumber
    actor User
    participant CLI as Account Command
    participant AccountSvc as AccountService
    participant CustomerRepo as CustomerRepository
    participant AccountRepo as AccountRepository
    participant TxRepo as TransactionRepository
    participant Account

    User->>CLI: Enter account details
    CLI->>AccountSvc: open_account(account, initial_deposit)
    AccountSvc->>CustomerRepo: validate customer
    CustomerRepo-->>AccountSvc: customer
    AccountSvc->>AccountSvc: validate account/business rules
    AccountSvc->>AccountRepo: persist account
    AccountRepo-->>AccountSvc: account persisted

    alt initial deposit supplied
        AccountSvc->>Account: deposit(initial_deposit)
        AccountSvc->>TxRepo: persist deposit transaction
        TxRepo-->>AccountSvc: transaction persisted
    end

    AccountSvc-->>CLI: Account
    CLI-->>User: Display account result
```

The diagram shows the service boundary rather than exposing repository construction or persistence details to the CLI.

---

## 7. Deposit

A deposit changes account state and creates the corresponding transaction record through the application/service workflow.

```mermaid
sequenceDiagram
    autonumber
    actor User
    participant CLI as Transaction Command
    participant AccountSvc as AccountService
    participant AccountRepo as AccountRepository
    participant Account
    participant TxRepo as TransactionRepository

    User->>CLI: Enter account and amount
    CLI->>AccountSvc: deposit(account_number, amount, description)
    AccountSvc->>AccountRepo: get account
    AccountRepo-->>AccountSvc: Account
    AccountSvc->>Account: deposit(amount)
    Account-->>AccountSvc: balance updated
    AccountSvc->>TxRepo: record deposit transaction
    TxRepo-->>AccountSvc: transaction persisted
    AccountSvc->>AccountRepo: save account
    AccountRepo-->>AccountSvc: account persisted
    AccountSvc-->>CLI: updated Account
    CLI-->>User: Display deposit result
```

The transaction and account persistence operations are represented at the service boundary because the service coordinates the financial workflow.

---

## 8. Withdrawal

Withdrawal follows the same general workflow but includes account-level validation of whether the requested amount can be withdrawn.

```mermaid
sequenceDiagram
    autonumber
    actor User
    participant CLI as Transaction Command
    participant AccountSvc as AccountService
    participant AccountRepo as AccountRepository
    participant Account
    participant TxRepo as TransactionRepository

    User->>CLI: Enter account and amount
    CLI->>AccountSvc: withdraw(account_number, amount, description)
    AccountSvc->>AccountRepo: get account
    AccountRepo-->>AccountSvc: Account
    AccountSvc->>Account: validate withdrawal

    alt withdrawal allowed
        AccountSvc->>Account: withdraw(amount)
        Account-->>AccountSvc: balance updated
        AccountSvc->>TxRepo: record withdrawal transaction
        TxRepo-->>AccountSvc: transaction persisted
        AccountSvc->>AccountRepo: save account
        AccountRepo-->>AccountSvc: account persisted
        AccountSvc-->>CLI: updated Account
        CLI-->>User: Display withdrawal result
    else withdrawal rejected
        Account-->>AccountSvc: domain validation error
        AccountSvc-->>CLI: propagate domain exception
        CLI-->>User: Display error
    end
```

---

## 9. Internal Account Transfer

An internal transfer involves a source account and destination account. The service validates both accounts, prevents invalid self-transfers, applies the debit/credit operation, and records the resulting transaction workflow.

```mermaid
sequenceDiagram
    autonumber
    actor User
    participant CLI as Transaction Command
    participant AccountSvc as AccountService
    participant AccountRepo as AccountRepository
    participant Source as Source Account
    participant Destination as Destination Account
    participant TxRepo as TransactionRepository

    User->>CLI: Enter source, destination, amount
    CLI->>AccountSvc: transfer(source, destination, amount, description)
    AccountSvc->>AccountRepo: get source account
    AccountRepo-->>AccountSvc: Source
    AccountSvc->>AccountRepo: get destination account
    AccountRepo-->>AccountSvc: Destination
    AccountSvc->>AccountSvc: validate accounts and transfer
    AccountSvc->>Source: withdraw(amount)
    Source-->>AccountSvc: debit applied
    AccountSvc->>Destination: deposit(amount)
    Destination-->>AccountSvc: credit applied
    AccountSvc->>TxRepo: record transfer transaction(s)
    TxRepo-->>AccountSvc: persisted
    AccountSvc->>AccountRepo: save source/destination
    AccountRepo-->>AccountSvc: persisted
    AccountSvc-->>CLI: updated accounts
    CLI-->>User: Display transfer result
```

If the source and destination identifiers are identical or either account fails validation, the workflow terminates with the relevant domain/application error rather than applying the transfer.

---

## 10. Transaction History / Statement

Transaction history is read through the transaction service and repository. The service can provide account-level transactions, recent transactions, date-range queries, and statement-oriented data.

```mermaid
sequenceDiagram
    autonumber
    actor User
    participant CLI as Transaction Command
    participant TxSvc as TransactionService
    participant TxRepo as TransactionRepository
    participant AccountRepo as AccountRepository

    User->>CLI: Request transaction history
    CLI->>TxSvc: account_transactions(account_number)
    TxSvc->>AccountRepo: validate account
    AccountRepo-->>TxSvc: Account
    TxSvc->>TxRepo: find transactions for account
    TxRepo-->>TxSvc: transactions
    TxSvc-->>CLI: transaction list
    CLI-->>User: Render transaction history
```

---

## 11. Reporting

Reporting reads application/domain data and transforms it into report-oriented structures. The reporting layer is deliberately separated from core banking transaction logic.

```mermaid
sequenceDiagram
    autonumber
    actor User
    participant CLI as Reporting Command
    participant ReportSvc as Report Service
    participant DomainSvc as Domain Service
    participant Generator as ReportGenerator
    participant Report
    participant Export as ExportService

    User->>CLI: Select report
    CLI->>ReportSvc: generate requested report
    ReportSvc->>DomainSvc: retrieve required data
    DomainSvc-->>ReportSvc: domain data
    ReportSvc->>Generator: create_report(...)
    Generator-->>ReportSvc: Report
    ReportSvc->>Report: add rows
    Report-->>ReportSvc: report populated
    ReportSvc-->>CLI: Report
    CLI-->>User: Display report

    opt Export requested
        CLI->>Export: export(report, format)
        Export-->>CLI: exported output
        CLI-->>User: Confirm export
    end
```

---

## 12. Persistence Boundary

The application uses CSV-backed persistence. The important architectural rule is that service operations cross the repository boundary rather than allowing the CLI to manipulate CSV files directly.

```mermaid
sequenceDiagram
    autonumber
    participant Service
    participant Repository
    participant CSV as CSV Storage

    Service->>Repository: save/update entity
    Repository->>CSV: serialize and write
    CSV-->>Repository: write completed
    Repository-->>Service: persistence result

    Service->>Repository: retrieve entity
    Repository->>CSV: read persisted data
    CSV-->>Repository: raw records
    Repository->>Repository: deserialize entities
    Repository-->>Service: domain entities
```

---

## 13. Error Propagation

Expected business failures originate at the layer that owns the relevant rule and propagate upward until the presentation layer can render a useful message.

```mermaid
sequenceDiagram
    autonumber
    actor User
    participant CLI
    participant Service
    participant Domain as Domain Model
    participant Repository

    User->>CLI: Request operation
    CLI->>Service: execute operation
    Service->>Repository: retrieve required data
    Repository-->>Service: entity
    Service->>Domain: apply business rule
    Domain-->>Service: DomainException
    Service-->>CLI: propagate exception
    CLI-->>User: Display actionable error
```

The application should preserve specific domain exceptions instead of converting every failure into a generic exception.

---

## 14. Complete Daily Banking Workflow

The following sequence combines the principal user-facing operations into a realistic workflow.

```mermaid
sequenceDiagram
    autonumber
    actor User
    participant CLI
    participant CustomerSvc as CustomerService
    participant AccountSvc as AccountService
    participant TxSvc as TransactionService
    participant Repos as CSV Repositories
    participant Reports as Reporting

    User->>CLI: Create customer
    CLI->>CustomerSvc: register customer
    CustomerSvc->>Repos: persist customer
    Repos-->>CustomerSvc: saved
    CustomerSvc-->>CLI: customer
    CLI-->>User: confirmation

    User->>CLI: Open account
    CLI->>AccountSvc: open account
    AccountSvc->>Repos: validate/persist account
    Repos-->>AccountSvc: saved
    AccountSvc-->>CLI: account
    CLI-->>User: confirmation

    User->>CLI: Deposit funds
    CLI->>AccountSvc: deposit
    AccountSvc->>Repos: update account + transaction
    Repos-->>AccountSvc: saved
    AccountSvc-->>CLI: result
    CLI-->>User: confirmation

    User->>CLI: Transfer funds
    CLI->>AccountSvc: transfer
    AccountSvc->>Repos: update accounts + transaction
    Repos-->>AccountSvc: saved
    AccountSvc-->>CLI: result
    CLI-->>User: confirmation

    User->>CLI: Review transactions
    CLI->>TxSvc: query history
    TxSvc->>Repos: retrieve transactions
    Repos-->>TxSvc: transactions
    TxSvc-->>CLI: history
    CLI-->>User: display history

    User->>CLI: Generate report
    CLI->>Reports: generate report
    Reports->>Repos: retrieve required data
    Repos-->>Reports: data
    Reports-->>CLI: report
    CLI-->>User: display report
```

---

## 15. Diagram-to-Architecture Mapping

| Workflow | Primary component | Persistence | Main concern |
|---|---|---|---|
| Startup | `Bootstrap` / `Application` | Storage initializer | Runtime readiness |
| Customer registration | `CustomerService` | Customer repository | Customer lifecycle |
| Account opening | `AccountService` | Account/customer repositories | Account eligibility and creation |
| Deposit | `AccountService` | Account/transaction repositories | Credit operation |
| Withdrawal | `AccountService` | Account/transaction repositories | Debit and balance validation |
| Transfer | `AccountService` | Account/transaction repositories | Coordinated debit/credit |
| History | `TransactionService` | Transaction repository | Transaction retrieval |
| Reporting | Reporting services | Domain repositories/services | Transformation and presentation |
| Shutdown | `Application` | Dependency container | Graceful lifecycle termination |

## 16. Design Principles Illustrated

The sequence diagrams demonstrate the following architectural principles:

1. **Separation of concerns** — CLI, services, repositories, domain objects, and reporting have distinct responsibilities.
2. **Dependency inversion through composition** — application startup constructs the dependency graph centrally.
3. **Service orchestration** — multi-step banking workflows are coordinated by services rather than CLI commands.
4. **Domain encapsulation** — account balance operations are performed by domain objects.
5. **Persistence isolation** — CSV storage is accessed through repositories.
6. **Explicit error propagation** — domain/application failures remain distinguishable to callers.
7. **Reporting separation** — reporting transforms data without becoming the owner of banking business rules.

## 17. Source-of-Truth Rule

These diagrams document the current architecture and intended runtime interaction represented by the source code and tests. They must be updated when a workflow's component boundaries, orchestration responsibilities, or persistence behavior materially changes.

The source code remains authoritative when a diagram and implementation disagree.

## 18. Related Documentation

- [`README.md`](../../README.md) — project overview
- [`Architecture Guide`](../architecture/ARCHITECTURE_GUIDE.md) — architecture and design
- [`User Guide`](../user/USER_GUIDE.md) — user workflows
- [`Developer Guide`](../developer/DEVELOPER_GUIDE.md) — development practices
- [`Installation Guide`](../installation/INSTALLATION_GUIDE.md) — installation
- [`API Reference`](../api/API_REFERENCE.md) — public APIs
- [`Class Diagrams`](CLASS_DIAGRAMS.md) — static class relationships
