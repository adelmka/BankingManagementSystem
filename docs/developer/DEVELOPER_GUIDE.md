# Banking Management System — Developer Guide

## Purpose

This guide is for developers maintaining, testing, or extending the Banking Management System (BMS). It documents the current repository structure, development practices, testing strategy, and extension guidelines without introducing an architectural redesign.

## Functional Baseline

The current supplied regression baseline is **1,419 tests passed, 0 failed, 0 errors**. The latest full-suite execution completed in 9.39 seconds. Production-code changes should preserve the passing baseline unless a requirement intentionally changes it.

## Repository Structure

```text
BankingManagementSystem/
├── main.py
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
- `cli/` — command adapters, input handling, dispatching, and rendering.
- `reporting/` — report generation and export.
- `utils/` — cross-cutting utilities such as logging, generators, and validation.
- `tests/` — unit, integration, reporting, and E2E tests.
- `docs/` — project documentation.
- `main.py` — executable CLI composition root.

## Configuration

`config.py` contains the base `Config` class plus environment-specific configuration classes. It centralizes application, bank, filesystem, CSV, interest-rate, fee, authentication, logging, pagination, and date/time settings.

Environment-specific and sensitive values should be supplied through environment variables or a local `.env` file and should not be committed as secrets.

## Dependency Injection

`application/dependency_container.py` is the composition root. `DependencyContainer` creates the shared repositories, services, `BankService` façade, logger, and configuration, and validates the resulting object graph.

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

The executable `main.py` composes the existing application and CLI infrastructure and delegates customer/account creation to the current command adapters.

### Reporting

Transform application/domain data into report structures and export representations. Keep core banking rules outside reporting.

### Configuration

Keep environment-dependent values centralized rather than scattering hard-coded settings throughout the application.

## CLI Development

The executable CLI entry point is `main.py`. Its current main menu is:

```text
1. Create customer
2. List customers
3. Open account
4. List accounts
5. Deposit funds
6. Withdraw funds
7. Transfer between accounts
8. View account transactions
9. Customer statistics
10. Account statistics
11. Bank statistics
0. Exit
```

`main.py` uses the existing `InputHandler`, `MenuRenderer`, and command adapters supplied by `Application.create_cli_commands()`. Customer creation is delegated to `CustomerCommands.create_customer()` and account opening to `AccountCommands.create_account()`.

CLI changes should normally include command tests and, when appropriate, input/validation, application, integration, and E2E coverage.

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
pytest -x
```

Not every targeted command is required for every change; choose the relevant scope, then use the complete suite as the regression gate for production-code changes.

## Test Isolation and Debugging

Tests should use controlled fixtures and temporary data rather than a developer's persistent runtime data. When failures occur:

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

## Persistence and Data Files

CSV files are the implemented persistence mechanism and their locations are configuration-driven. Do not commit local runtime data, generated logs, secrets, or environment-specific artifacts unless intentionally part of the source distribution.

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
CLI command adapter / main.py
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

The maintained documentation set is:

```text
README.md
docs/architecture/ARCHITECTURE_GUIDE.md
docs/user/USER_GUIDE.md
docs/developer/DEVELOPER_GUIDE.md
docs/installation/INSTALLATION_GUIDE.md
docs/api/API_REFERENCE.md
docs/diagrams/CLASS_DIAGRAMS.md
docs/diagrams/SEQUENCE_DIAGRAMS.md
docs/validation/DOCUMENTATION_VALIDATION.md
```

Documentation must describe implemented behavior, not deferred ideas.

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
pytest -x
1,419 passed in 9.39s
```

A manual CLI workflow has also been confirmed successfully for customer creation and subsequent account workflow. The automated suite remains the primary regression gate.

## Related Documentation

- [`README.md`](../../README.md) — project overview
- [`Architecture Guide`](../architecture/ARCHITECTURE_GUIDE.md) — architecture and design
- [`User Guide`](../user/USER_GUIDE.md) — end-user workflows
- [`Installation Guide`](../installation/INSTALLATION_GUIDE.md) — installation
- [`API Reference`](../api/API_REFERENCE.md) — API reference
- [`Class Diagrams`](../diagrams/CLASS_DIAGRAMS.md) — class diagrams
- [`Sequence Diagrams`](../diagrams/SEQUENCE_DIAGRAMS.md) — sequence diagrams
- [`Documentation Validation`](../validation/DOCUMENTATION_VALIDATION.md) — documentation consistency baseline
