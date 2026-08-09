# Banking Management System — Developer Guide

## Purpose

This guide is for developers maintaining, testing, or extending the Banking Management System (BMS). It documents the current repository structure, development practices, testing strategy, and extension guidelines without introducing an architectural redesign.

## Functional Baseline

The current regression baseline is **1,439 tests passed, 0 failed, 0 errors**. The reporting subsystem independently passes 70 tests. Production-code changes should preserve the passing baseline unless a requirement intentionally changes.

## Repository Structure

```text
BankingManagementSystem/
├── config.py
├── requirements.txt
├── models/
├── repositories/
├── services/
├── exceptions/
├── application/
├── cli/
├── reporting/
├── utils/
├── data/
├── logs/
├── tests/
└── docs/
```

- `models/` — domain entities and value objects.
- `repositories/` — persistence abstractions and CSV-backed repositories.
- `services/` — business/application services and workflow rules.
- `exceptions/` — domain and application exceptions.
- `application/` — startup, orchestration, and dependency composition.
- `cli/` — menus, commands, input handling, dispatching, and rendering.
- `reporting/` — report generation and export.
- `utils/` — cross-cutting utilities such as logging, generators, and validation.
- `tests/` — unit, integration, reporting, and E2E tests.
- `docs/` — project documentation.

## Configuration

`config.py` contains the base `Config` class plus `DevelopmentConfig`, `TestingConfig`, and `ProductionConfig`. It loads `.env` values and centralizes application, bank, filesystem, CSV, interest-rate, fee, authentication, logging, pagination, and date/time settings.

Environment-specific and sensitive values should be supplied through environment variables or a local `.env` file and should not be committed as secrets.

## Dependency Injection

`application/dependency_container.py` is the composition root. `DependencyContainer` creates the shared repositories, services, `BankService` façade, logger, and configuration, and validates the resulting object graph.

```text
Config
  │
  ├── CustomerRepository
  ├── AccountRepository
  └── TransactionRepository
          │
          ▼
  CustomerService
  AccountService
  TransactionService
          │
          ▼
     BankService
```

New application-level code should use the established dependency graph rather than creating parallel service/repository instances without a clear reason.

## Layering Rules

### Models

Represent domain state and behavior. Do not add CLI interaction or unrelated repository orchestration to domain entities.

### Repositories

Handle persistence operations. Keep business workflow rules in services.

### Services

Coordinate repositories, validation, domain operations, and business rules. Do not contain presentation formatting.

### CLI

Collect input, invoke application/service operations, and present results or errors. Do not duplicate service-layer business rules.

### Reporting

Transform application/domain data into report structures and export representations. Keep core banking rules outside reporting.

### Configuration

Keep environment-dependent values centralized rather than scattering hard-coded settings throughout the application.

## Adding or Modifying a Domain Model

1. Identify domain state and invariants.
2. Follow existing inheritance/composition conventions.
3. Reuse existing value objects and validators where applicable.
4. Add or update model tests.
5. Update persistence serialization/deserialization if needed.
6. Update affected services.
7. Update CLI commands only if the user workflow changes.
8. Add integration/E2E coverage when boundaries are crossed.
9. Update API and diagram documentation when public structure changes.

Keep constructors and public signatures synchronized with their tests and consumers.

## Repository Development

When adding repository behavior:

1. Confirm the persistence requirement.
2. Follow the base repository conventions.
3. Preserve existing CSV formats unless a migration is intentional.
4. Add success and failure unit tests.
5. Add persistence/integration coverage.
6. Verify test fixtures isolate data.

Do not move banking workflow orchestration into repositories.

## Service Development

Services are the primary location for workflow-level business logic. When changing a service:

1. Identify the affected rule.
2. Identify all repositories involved.
3. Preserve validation and exception semantics.
4. Consider balance and transaction consistency for financial operations.
5. Add unit tests.
6. Run relevant integration/E2E tests.
7. Run the full suite before committing.

## CLI Development

The CLI menu definitions are maintained in `cli/menu.py`. The current top-level areas are Customer Management, Account Management, Transaction Management, Reporting, Administration, and System Information.

CLI changes should normally include command tests and, when appropriate, input/validation, dispatcher/application, integration, and E2E coverage.

## Reporting Development

The reporting subsystem covers account, bank, customer, and transaction reports, report generation, and export. A new report should define its purpose, inputs, columns, row transformation, empty-data behavior, ordering/filtering behavior, export representation, and tests.

Run:

```powershell
pytest tests/reporting -v
```

## Testing Strategy

The repository uses pytest at several levels:

- **Unit tests** — individual models, repositories, services, utilities, CLI components, and application components.
- **Integration tests** — multi-component workflows and persistence.
- **Reporting tests** — report generation and export.
- **E2E tests** — realistic end-to-end banking workflows.

Recommended development sequence:

```powershell
pytest tests/test_<changed_component>.py -v
pytest tests/integration -v
pytest tests/reporting -v
pytest tests/e2e -v
pytest
```

Not every targeted command is required for every change; choose the relevant scope, then use the complete suite as the regression gate for production-code changes.

## Test Isolation and Debugging

Tests should use controlled fixtures and temporary data rather than a developer's persistent runtime data. A test should be repeatable regardless of execution order.

When failures occur:

1. Read the first meaningful traceback.
2. Identify the failing layer/boundary.
3. Check imports and package exports.
4. Check constructor and method signatures.
5. Check configuration and paths.
6. Check fixtures and persistent test data.
7. Look for a common root cause across failures.
8. Fix the root cause.
9. Re-run affected tests.
10. Re-run the complete suite.

## Exception Handling

Use the existing exception hierarchy for expected domain/application failures. New exceptions should have a specific business meaning, reside in the appropriate module, be exported according to package conventions, be raised from the layer owning the rule, and have corresponding tests.

Avoid replacing specific domain exceptions with generic `Exception` when callers need to distinguish failure types.

## Persistence and Data Files

CSV files are the implemented persistence mechanism and their locations are configuration-driven. Do not commit local runtime data, generated logs, secrets, or environment-specific artifacts unless they are intentionally part of the source distribution.

When changing a CSV schema, consider compatibility and update repository tests, fixtures, and documentation.

## Logging and Code Quality

Use the project's logging utilities rather than ad-hoc diagnostic `print()` calls. Logging must not expose secrets or unnecessary personal data.

Follow existing conventions: Python 3.13+ syntax, clear responsibilities, useful type annotations, descriptive names, public docstrings, small testable methods, explicit domain exceptions, and minimal duplication of business rules.

Avoid unrelated broad refactoring while maintaining a validated feature.

## Feature Development Workflow

```text
Requirement
    ↓
Domain model / value object
    ↓
Repository persistence
    ↓
Service business workflow
    ↓
Application / dependency graph
    ↓
CLI or other interface
    ↓
Reporting (if required)
    ↓
Unit + Integration + E2E tests
    ↓
Documentation
```

Not every feature requires every layer. Do not create abstractions solely to fit the diagram.

## Documentation Maintenance

Update documentation when changes affect user workflows, public APIs, configuration, installation, architecture, CLI menus, reports, persistence formats, or supported behavior.

The planned documentation set is:

```text
README.md
docs/architecture/ARCHITECTURE_GUIDE.md
docs/user/USER_GUIDE.md
docs/developer/DEVELOPER_GUIDE.md
docs/installation/INSTALLATION_GUIDE.md
docs/api/API_REFERENCE.md
docs/diagrams/CLASS_DIAGRAMS.md
docs/diagrams/SEQUENCE_DIAGRAMS.md
```

Documentation must describe implemented behavior, not deferred ideas.

## Git and Commit Practices

Keep commits focused on one logical change. Before committing:

1. Review changed files.
2. Run targeted tests.
3. Run the full suite for production-code changes.
4. Confirm no secrets or runtime data are included.
5. Update affected documentation.

## Current Architectural Constraints

The project intentionally retains its current CSV persistence, repository/service boundaries, dependency container, CLI architecture, reporting structure, domain model hierarchy, and automated test organization. Changes to these areas should require an explicit requirement or architectural review.

## Developer Checklist

- [ ] Requirement understood
- [ ] Existing architecture reviewed
- [ ] Appropriate layer selected
- [ ] Existing APIs preserved where possible
- [ ] Unit tests added/updated
- [ ] Integration tests considered
- [ ] E2E tests considered
- [ ] Reporting tests run when affected
- [ ] Full pytest suite passes
- [ ] Documentation updated
- [ ] No secrets/runtime data committed
- [ ] Git diff reviewed

## Current Validation

```text
pytest tests/reporting
70 passed in 0.55s

pytest
1,439 passed in 10.35s
```

These are the current regression results. If future changes add tests or intentionally change behavior, establish and document the new passing baseline.

## Related Documentation

- [`README.md`](../../README.md) — project overview
- [`Architecture Guide`](../architecture/ARCHITECTURE_GUIDE.md) — architecture and design
- [`User Guide`](../user/USER_GUIDE.md) — end-user workflows
- `docs/installation/INSTALLATION_GUIDE.md` — installation
- `docs/api/API_REFERENCE.md` — API reference
- `docs/diagrams/CLASS_DIAGRAMS.md` — class diagrams
- `docs/diagrams/SEQUENCE_DIAGRAMS.md` — sequence diagrams
