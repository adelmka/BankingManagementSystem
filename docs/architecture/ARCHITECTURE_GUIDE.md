# Banking Management System — Architecture Guide

**Version:** 2.1.0  
**Python:** 3.13+  
**Repository:** `adelmka/BankingManagementSystem`  
**Status:** Architecture documentation for the current validated implementation

---

## 1. Purpose

This guide describes the architecture that is implemented in the current Banking Management System (BMS) repository.

It is intentionally an **implementation guide**, not a proposed redesign. The source code and passing test suite are the authoritative references for current behavior.

The current project has a strong layered structure built around:

- Domain models and value objects
- Repository-based persistence
- Application services
- A banking façade
- Dependency injection and composition
- Application bootstrap and lifecycle management
- CLI/application interaction
- Reporting and export
- Centralized configuration
- Domain/application exceptions
- Automated unit, integration, reporting, and end-to-end tests

---

## 2. Architectural Goals

The architecture is designed to achieve the following goals:

1. **Separate domain state from persistence.**
2. **Keep business operations in services rather than in presentation code.**
3. **Provide reusable repository abstractions for CSV persistence.**
4. **Centralize application composition and dependency construction.**
5. **Expose a high-level `BankService` façade for banking operations.**
6. **Keep startup/bootstrap responsibilities separate from application lifetime management.**
7. **Provide a dedicated reporting subsystem independent of banking-specific business logic where possible.**
8. **Support automated testing at multiple levels.**
9. **Centralize configuration and filesystem locations.**
10. **Use domain entities with behavior, validation, lifecycle state, and serialization contracts.**

---

## 3. Architectural Overview

At a high level, the system follows this dependency direction:

```text
                         User / External Caller
                                  │
                                  ▼
                         CLI / Application Layer
                                  │
                                  ▼
                           BankService Façade
                                  │
                 ┌────────────────┼────────────────┐
                 ▼                ▼                ▼
          CustomerService   AccountService   TransactionService
                 │                │                │
                 └────────────────┼────────────────┘
                                  │
                                  ▼
                           Repository Layer
                                  │
                                  ▼
                         CSV Persistent Storage
```

Cross-cutting and supporting components surround these layers:

```text
                    ┌──────────────────────────────┐
                    │          Configuration       │
                    │            config.py         │
                    └──────────────┬───────────────┘
                                   │
       ┌───────────────────────────┼───────────────────────────┐
       │                           │                           │
       ▼                           ▼                           ▼
   Exceptions                  Utilities                 Logging
       │                           │                           │
       └───────────────────────────┼───────────────────────────┘
                                   │
                                   ▼
                           Application Runtime
```

The application composition root is `application/dependency_container.py`. It creates repositories, creates services using those repositories, and creates `BankService` using the services.

---

## 4. Architectural Layers

### 4.1 Presentation / Interaction Layer

The CLI and application-facing components provide interaction and orchestration for users or callers.

Typical responsibilities include:

- Receiving commands or user input
- Formatting output
- Invoking application operations
- Avoiding direct manipulation of persistent CSV files
- Delegating business behavior to services

The presentation layer should not become the owner of domain rules or persistence behavior.

---

### 4.2 Application Layer

The `application/` package coordinates startup, dependency construction, application lifetime, and storage initialization.

Key components include:

| Component | Responsibility |
|---|---|
| `Application` | Represents a running BMS instance and exposes the `BankService` façade |
| `DependencyContainer` | Composition root; constructs shared repositories and services |
| `Bootstrap` | Coordinates storage preparation and application construction |
| `StorageInitializer` | Prepares and validates application storage |
| `startup.py` | Public startup/shutdown entry points |

The application layer does not own banking domain rules.

For example, `Application` constructs a dependency container and exposes its `BankService` façade, while `Bootstrap` prepares storage before constructing the application. fileciteturn12file0 fileciteturn19file0

---

### 4.3 Service Layer

The service layer contains application-level banking operations and coordinates domain objects with repositories.

The principal services are:

- `CustomerService`
- `AccountService`
- `TransactionService`
- `BankService`

`BaseService[T]` provides common repository access, persistence helpers, validation hooks, operation scopes, and lifecycle hooks for concrete services. fileciteturn8file0

#### `BankService`

`BankService` is the application's banking façade. It aggregates the customer, account, and transaction services and delegates operations to them.

Examples include:

- Adding and finding customers
- Opening and finding accounts
- Depositing and withdrawing funds
- Transferring funds
- Retrieving balances and summaries
- Recording and retrieving transactions
- Producing transaction listings and statements
- Refreshing and saving service state
- Returning application-wide statistics

The façade therefore provides a convenient high-level API without moving the underlying business implementation into the façade itself. fileciteturn14file0

#### `AccountService`

`AccountService` coordinates account operations and collaborates with account, customer, and transaction repositories. It validates account/customer eligibility and performs multi-step account operations within repository operation scopes. fileciteturn7file0

---

### 4.4 Domain Model Layer

The `models/` package contains the domain entities and value objects used by the banking system.

The central entity hierarchy includes:

```text
BaseEntity
    │
    └── Account (abstract)
            │
            ├── SavingsAccount
            ├── CurrentAccount
            └── TimeDepositAccount
```

Other domain entities include customer/person and transaction-related models.

#### `BaseEntity`

`BaseEntity` is the abstract foundation for domain entities. It provides:

- UUID-based entity identity
- Creation and update timestamps
- Active/inactive state
- Entity versioning
- Equality based on entity identity
- Hashing based on entity identity
- Serialization contracts through `to_dict()` and `from_dict()`

The class intentionally uses behavior and mutable domain state rather than being a passive data structure. fileciteturn10file0

#### `Account`

`Account` is an abstract domain entity. It contains common account state and behavior, including:

- Account number
- Customer association
- Account type
- Currency
- Balance
- Account status
- Opening/closing dates
- Transaction associations
- Deposit and withdrawal operations
- Transfer behavior
- Lifecycle operations
- Interest and fee extension hooks
- Serialization support

Concrete account types inherit from `Account` and can specialize withdrawal, interest, fee, or other account-specific rules. fileciteturn11file0

---

## 5. Object-Oriented Design

The BMS architecture makes direct use of core OOP principles.

### 5.1 Encapsulation

Domain state is held through protected/private-style attributes and exposed through properties and methods.

For example, account balance changes are performed through domain operations such as `deposit()` and `withdraw()` rather than by exposing a writable balance field.

### 5.2 Abstraction

Abstract base classes define contracts shared by concrete implementations.

Examples include:

- `BaseEntity`
- `Account`
- `BaseRepository`
- `BaseService`

`BaseEntity` requires concrete entities to implement serialization through `to_dict()` and `from_dict()`. `Account` defines extension points such as withdrawal eligibility and interest/fee calculation.

### 5.3 Inheritance

Concrete domain classes inherit common behavior from abstract and base classes.

Examples:

```text
BaseEntity
   └── Account
          ├── SavingsAccount
          ├── CurrentAccount
          └── TimeDepositAccount
```

Services and repositories similarly inherit common infrastructure behavior from their base classes.

### 5.4 Polymorphism

The architecture allows concrete account types to specialize behavior defined by `Account`. Extension hooks such as `_can_withdraw()`, `calculate_interest()`, and `calculate_fee()` provide polymorphic behavior.

Repositories and services also use generic base classes so common infrastructure can operate against different entity types.

### 5.5 Composition

The application relies heavily on composition rather than placing all behavior in a single class.

For example:

```text
Application
    └── DependencyContainer
          ├── CustomerRepository
          ├── AccountRepository
          ├── TransactionRepository
          ├── CustomerService
          ├── AccountService
          ├── TransactionService
          └── BankService
```

This composition is constructed centrally by `DependencyContainer`. fileciteturn13file0

---

## 6. Repository Architecture

The repository layer isolates persistence from domain and service logic.

`BaseRepository[T]` is a generic repository for `BaseEntity` subclasses. It maintains an in-memory entity collection and persists that collection to CSV storage. fileciteturn9file0

### Repository responsibilities

- Ensure the configured CSV file exists
- Load entities from CSV
- Maintain an in-memory entity cache
- Find entities
- Add and update entities
- Soft-delete/deactivate entities
- Restore entities
- Persist entities to CSV
- Reload persisted data
- Provide filtering and sorting helpers
- Provide repository summaries
- Support explicit and scoped persistence operations

### Persistence flow

```text
Service
   │
   ▼
Repository
   │
   ├── In-memory entity collection
   │
   ▼
CSV serialization
   │
   ▼
Data directory
```

Entities provide their serialization representation through `to_dict()` and can be reconstructed through `from_dict()`.

The repository builds CSV field names from the union of serialized fields so heterogeneous subclasses can be persisted through a common repository when required. fileciteturn9file0

---

## 7. Dependency Injection and Composition Root

`DependencyContainer` is the application's composition root.

It creates:

1. Configuration context
2. Logger
3. Customer repository
4. Account repository
5. Transaction repository
6. Customer service
7. Account service
8. Transaction service
9. `BankService` façade

The dependency graph is therefore assembled in one place instead of being recreated throughout the application.

```text
Config
  │
  ▼
DependencyContainer
  │
  ├── CustomerRepository ──► CustomerService ──┐
  │                                             │
  ├── AccountRepository ───► AccountService ───┼──► BankService
  │                                             │
  └── TransactionRepository ► TransactionService┘
```

The container also validates that the required dependencies have been constructed successfully. fileciteturn13file0

---

## 8. Application Startup and Lifecycle

Startup is separated into explicit stages.

```text
start_application()
       │
       ▼
    Bootstrap
       │
       ▼
StorageInitializer
       │
       ▼
Storage validation
       │
       ▼
  Application
       │
       ▼
DependencyContainer.build()
       │
       ▼
Repositories + Services + BankService
```

`startup.py` exposes `start_application()` and `shutdown_application()`. `Bootstrap` prepares storage and validates it before creating `Application`. `Application` owns the running application's lifetime and provides the `bank` façade. fileciteturn18file0 fileciteturn19file0 fileciteturn12file0

---

## 9. Reporting Architecture

Reporting is implemented as a dedicated subsystem under `reporting/`.

The reporting framework separates generic report representation from banking-specific report construction.

`ReportGenerator` creates reports containing:

- Report metadata
- Column definitions
- Rows
- Row counts
- Dictionary representations

The generic report infrastructure deliberately contains no banking-specific business rules. fileciteturn15file0

The reporting area also contains specialized report modules for account, customer, bank, and transaction reporting, together with export functionality.

### Reporting flow

```text
Banking data / services
          │
          ▼
   Specialized reports
          │
          ▼
     Report object
          │
          ▼
     Export service
          │
          ▼
     External report
```

The reporting test suite currently validates this subsystem with **70 passing tests**.

---

## 10. Configuration Architecture

Configuration is centralized in `config.py`.

The base `Config` class defines application-wide settings, including:

- Application identity and version
- Host and port
- Bank identity
- Currency
- Runtime directories
- CSV storage paths
- Interest rates
- Fees
- Authentication parameters
- Logging parameters
- Reporting parameters
- Date/time formats

Environment-specific subclasses are provided for development, testing, and production.

```text
Config
  ├── DevelopmentConfig
  ├── TestingConfig
  └── ProductionConfig
```

Environment variables are loaded from `.env` where applicable. The configuration also retains module-level aliases for backward compatibility with existing consumers. fileciteturn5file0

---

## 11. Exception and Validation Architecture

The system uses dedicated exception modules and validation utilities to keep invalid states and business-rule violations explicit.

Typical validation occurs at several levels:

```text
Input
  │
  ▼
Validators / Value Objects
  │
  ▼
Domain Entity Validation
  │
  ▼
Service Business Rules
  │
  ▼
Repository Persistence
```

This provides multiple protection points rather than assuming that only the presentation layer will supply valid data.

Examples include validation of required fields, account status, account eligibility, monetary amounts, currencies, duplicate entities, and missing entities.

---

## 12. Transaction and Account Operation Model

Account operations are coordinated by `AccountService`, while the domain `Account` entity remains responsible for core account state transitions.

For example, a deposit follows this conceptual path:

```text
Caller
  │
  ▼
BankService.deposit()
  │
  ▼
AccountService.deposit()
  │
  ├── validate account
  │
  ├── enter operation scope
  │
  ├── Account.deposit()
  │
  └── repository persistence
  │
  ▼
Updated Account
```

A transfer is a multi-account operation:

```text
AccountService.transfer()
        │
        ├── validate source
        ├── validate destination
        │
        ▼
   operation scope
        │
        ├── debit source
        └── credit destination
        │
        ▼
   repository flush
```

The service layer therefore coordinates application-level operations while the account entity enforces its own domain invariants. fileciteturn7file0 fileciteturn11file0

---

## 13. Persistence and State Management Strategy

The repository architecture uses an in-memory cache backed by CSV files.

The normal lifecycle is:

```text
CSV file
   │
   ▼
Repository.load()
   │
   ▼
In-memory entities
   │
   ├── read/query
   ├── add/update/remove
   │
   ▼
Repository.save()/flush()
   │
   ▼
CSV file
```

For multi-step operations, services can temporarily disable repository auto-save and flush the operation at completion. `BaseService._operation_scope()` encapsulates this behavior. fileciteturn8file0

This design provides simple persistence appropriate to the current project's CSV storage requirement without introducing a database dependency.

---

## 14. Architectural Boundaries

The following boundaries should be preserved during future development.

### Presentation → Service

Presentation components should call application services or the `BankService` façade rather than implementing banking rules.

### Service → Repository

Services should use repositories for persistence and retrieval rather than manipulating CSV files directly.

### Service → Domain

Services coordinate domain operations; domain entities remain responsible for their own invariants and state transitions.

### Repository → CSV

Repositories own CSV serialization and persistence details.

### Application → Composition

Application startup and dependency construction belong in the application/bootstrap/container components.

### Reporting → Report Representation

Reporting components should generate report representations from supplied domain/application data without absorbing core banking business rules.

---

## 15. Testing Architecture

The repository uses multiple testing levels.

```text
                    Test Suite
                        │
          ┌─────────────┼─────────────┐
          ▼             ▼             ▼
       Unit Tests   Integration     E2E Tests
                        │
                        ▼
                  Reporting Tests
```

The current validation baseline is:

```text
1,439 tests collected
1,439 passed
0 failed
0 errors
```

The dedicated reporting suite is:

```text
70 tests
70 passed
```

Testing covers domain models, repositories, services, application components, CLI components, reporting, persistence workflows, and realistic end-to-end banking operations.

The passing suite establishes the current functional baseline; it does not eliminate the need for architectural, security, operational, or code-quality review during the final project audit.

---

## 16. Architectural Strengths

Based on the current implementation, the principal architectural strengths are:

- Clear separation between domain, persistence, service, and application responsibilities
- Generic repository and service infrastructure
- Explicit domain entities with behavior and invariants
- Dependency construction centralized in one composition root
- High-level banking façade
- Dedicated reporting subsystem
- Centralized configuration
- Explicit startup/bootstrap lifecycle
- Multi-level automated testing
- CSV persistence isolated behind repositories
- Extension points for specialized account behavior

---

## 17. Architectural Constraints

The current architecture also has intentional constraints that should be understood by developers.

### CSV persistence

CSV is the persistence mechanism rather than a relational or transactional database. This keeps the project simple and aligned with its current requirements but does not provide the concurrency, transaction isolation, indexing, or referential-integrity capabilities of a database system.

### In-memory repository cache

Repositories load persisted entities into memory and write the collection back to CSV. Large datasets would therefore require a different persistence strategy.

### Application-level operation scopes

Multi-step operations rely on repository operation scopes and controlled flushing rather than database transactions.

### Façade scope

`BankService` is a convenience façade over the three principal banking services. It should remain a delegating application interface rather than becoming a second business-logic layer.

These are architectural characteristics of the current system, not defects that should automatically trigger refactoring.

---

## 18. Extension Guidelines

Future changes should follow these rules unless a deliberate architectural decision is made.

### Add a new domain entity

1. Derive from `BaseEntity` where appropriate.
2. Define domain invariants and behavior in the entity.
3. Implement `to_dict()` and `from_dict()`.
4. Add the corresponding repository.
5. Add or extend the appropriate service.
6. Register the repository/service in `DependencyContainer` if it is an application-wide dependency.
7. Expose façade operations through `BankService` only when the operation belongs to the public banking application API.
8. Add unit, integration, and E2E tests as appropriate.

### Add a new account type

1. Derive from `Account`.
2. Reuse common account state and behavior.
3. Override only the rules that are account-type specific.
4. Implement serialization/deserialization for additional state.
5. Add dedicated tests.
6. Update diagrams and API documentation.

### Add a new report

1. Keep generic report infrastructure in `reporting/report_generator.py`.
2. Put banking-specific report construction in a specialized reporting module.
3. Use the existing report representation.
4. Reuse the export service where appropriate.
5. Add reporting tests.

---

## 19. Architectural Decision Summary

| Decision | Current implementation | Rationale |
|---|---|---|
| Domain model | Behavior-rich OOP entities | Keep business invariants close to domain state |
| Persistence | CSV | Satisfies the project's current persistence requirement |
| Repository pattern | Generic `BaseRepository[T]` | Isolate storage and reuse persistence behavior |
| Service layer | Generic `BaseService[T]` plus concrete services | Centralize application/business workflows |
| Façade | `BankService` | Provide a simple application-facing banking API |
| Composition | `DependencyContainer` | Centralize dependency construction |
| Startup | `Bootstrap` + `startup.py` | Separate environment preparation from runtime ownership |
| Reporting | Dedicated reporting package | Separate report representation/generation from core banking rules |
| Configuration | `Config` hierarchy + environment variables | Centralize runtime configuration |
| Testing | Unit + integration + reporting + E2E | Validate behavior at multiple levels |

---

## 20. Architecture and Future Changes

The current architecture should be treated as the baseline for the remainder of the project documentation and final audit.

Potential future enhancements may include database-backed persistence, stronger transaction semantics, broader web/API exposure, and additional operational concerns. Such enhancements are **not part of the current architecture unless implemented and tested**.

The documentation phase should therefore distinguish clearly between:

- **Implemented:** present in the current repository and covered by the current implementation/tests.
- **Deferred:** potentially useful future enhancements that are intentionally outside the current scope.
- **Not implemented:** functionality that should not be described as available merely because it was discussed during design.

---

## 21. Source-of-Truth Files

The following files are particularly important when maintaining this architecture documentation:

| Area | Source file(s) |
|---|---|
| Configuration | `config.py` |
| Base domain entity | `models/base_entity.py` |
| Account hierarchy | `models/account.py`, concrete account modules |
| Base repository | `repositories/base_repository.py` |
| Base service | `services/base_service.py` |
| Account service | `services/account_service.py` |
| Banking façade | `services/bank_service.py` |
| Dependency injection | `application/dependency_container.py` |
| Startup | `application/startup.py` |
| Bootstrap | `application/bootstrap.py` |
| Application runtime | `application/application.py` |
| Reporting framework | `reporting/report_generator.py` |
| Tests | `tests/` |

---

## 22. Validation Status

This Architecture Guide is based on the current repository implementation inspected during the documentation phase and the current test baseline reported for the project.

**Functional baseline:**

```text
1,439 / 1,439 tests passing
```

**Reporting baseline:**

```text
70 / 70 reporting tests passing
```

The architecture guide should be revisited during the final documentation validation step if source code changes occur after this document is committed.
