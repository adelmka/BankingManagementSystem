# Banking Management System

A Python-based Banking Management System (BMS) implementing core retail-banking operations using object-oriented design, service and repository layers, CSV persistence, a command-line/application interface, and reporting capabilities.

## Project Status

**Current status: Functionally validated and documentation-synchronized**

The current local test-suite baseline contains **1,419 tests**, and the complete suite passes:

```text
1,419 passed in 9.39s
```

The latest manual validation also confirmed the primary CLI workflow for customer creation and account opening/operations. The test baseline above is the current supplied local validation evidence.

## Key Capabilities

The system supports the principal banking workflows implemented in the current application, including:

- Customer management
- Savings accounts
- Current accounts
- Time-deposit accounts
- Deposits
- Withdrawals
- Account-to-account transfers
- Transactions and transaction persistence
- Interest-rate configuration
- Banking fees
- CSV-based data persistence
- Reporting and report generation
- Report export
- Application and command-line workflows
- Validation and domain exceptions
- Automated unit, integration, reporting, and end-to-end testing

## Technology Stack

- **Python:** 3.13+
- **Flask:** web/application framework components
- **Pandas:** data and reporting operations
- **CSV:** primary persistence format for the implemented data store
- **pytest:** automated testing
- **python-dotenv:** environment configuration
- **openpyxl:** spreadsheet-related support
- **bcrypt:** password hashing support
- **Jinja2 / WTForms / Flask-WTF:** web interface components
- **Rich / tabulate:** formatted terminal output

See [`requirements.txt`](requirements.txt) for the complete dependency specification.

## High-Level Structure

The application is organized around separation of responsibilities between domain models, repositories, services, application/CLI components, reporting, configuration, and tests.

```text
BankingManagementSystem/
│
├── main.py               # Executable CLI entry point
├── config.py
├── requirements.txt
│
├── models/              # Domain entities and value objects
├── repositories/        # Persistence and repository abstractions
├── services/            # Business/application services
├── exceptions/          # Domain and application exceptions
├── cli/                 # Command-line interaction and commands
├── application/         # Application orchestration/bootstrap components
├── reporting/           # Reports and export functionality
├── utils/               # Shared utilities, validation, logging, etc.
├── data/                # Runtime CSV data
├── logs/                # Runtime logs
├── tests/               # Unit, integration, reporting, and E2E tests
└── docs/                # Project documentation
```

The exact implementation remains the authoritative source for module names and APIs.

## Configuration

Application configuration is centralized in `config.py` through the `Config` class and environment-specific configuration classes. Important configuration areas include application identity, bank identification, currency, data and log directories, CSV data-file locations, interest rates, banking fees, authentication, logging, and reporting settings.

## Installation

### Prerequisites

- Python 3.13 or later
- Git
- A virtual environment is recommended

### Setup

```powershell
git clone https://github.com/adelmka/BankingManagementSystem.git
cd BankingManagementSystem
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Detailed procedures are maintained in [`docs/installation/INSTALLATION_GUIDE.md`](docs/installation/INSTALLATION_GUIDE.md).

## Starting the Application

From the repository root:

```powershell
python main.py
```

`main.py` is the executable composition root. It starts the existing application bootstrap, obtains the configured `BankService`, creates the CLI command adapters, and presents the interactive console using `MenuRenderer` and `InputHandler`.

The current main menu is:

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

The application can be terminated through **0 — Exit** or with `Ctrl+C`.

The executable entry point is covered by `tests/integration/test_cli_entry_point.py`.

## Running Tests

Run the complete test suite from the repository root:

```powershell
pytest
```

Latest supplied validation:

```text
1,419 passed in 9.39s
```

Useful targeted commands include:

```powershell
pytest tests/integration -v
pytest tests/e2e -v
pytest tests/test_account_service.py -v
pytest tests/test_customer_service.py -v
pytest tests/test_transaction_service.py -v
```

## Test Coverage Areas

The test suite covers domain models, value objects, repositories and persistence, services and business workflows, CLI commands and application components, dependency management and startup, reporting/export functionality, integration workflows, and end-to-end banking workflows.

## Reporting

The reporting subsystem is independently covered by the reporting tests in `tests/reporting/` and includes account, bank, customer, and transaction reporting, report generation, and export functionality.

## Documentation

| Document | Location | Status |
|---|---|---|
| README | `README.md` | Synchronized |
| Architecture Guide | `docs/architecture/ARCHITECTURE_GUIDE.md` | Current |
| User Guide | `docs/user/USER_GUIDE.md` | Synchronized |
| Developer Guide | `docs/developer/DEVELOPER_GUIDE.md` | Synchronized |
| Installation Guide | `docs/installation/INSTALLATION_GUIDE.md` | Synchronized |
| API Reference | `docs/api/API_REFERENCE.md` | Current |
| Class Diagrams | `docs/diagrams/CLASS_DIAGRAMS.md` | Current |
| Sequence Diagrams | `docs/diagrams/SEQUENCE_DIAGRAMS.md` | Current |
| Documentation Validation | `docs/validation/DOCUMENTATION_VALIDATION.md` | Synchronized |

All documentation is intended to describe the implementation that exists in the repository. It does not introduce architectural changes or document deferred functionality as implemented.

## Design Approach

The project uses object-oriented programming and separation of responsibilities across the application, including encapsulation, abstraction, inheritance, polymorphism, composition, repository-based persistence, service-layer business logic, application/CLI orchestration, reporting separation, centralized configuration, and domain-specific exception handling.

## Data Persistence

The current implementation uses CSV files as the primary persistent data representation. File locations are centralized through application configuration under the project `data/` directory.

Runtime data and logs should be treated as environment-specific artifacts rather than source-code assets.

## Version

The application configuration currently identifies the application version as **2.1.0**.

## Development Principles

1. Preserve the existing architecture unless a verified defect requires a change.
2. Treat the passing test suite as the current functional baseline.
3. Document the implementation that actually exists in the repository.
4. Keep examples consistent with the current public APIs and workflows.
5. Avoid documenting speculative or deferred enhancements as implemented functionality.

## License

No project license has been specified in the repository documentation at this stage.

## Documentation Roadmap

The documentation phase is complete and synchronized with the current implementation:

1. README — project entry point
2. Architecture Guide — architecture, layers, responsibilities, and design decisions
3. User Guide — current executable CLI workflows
4. Developer Guide — development and extension guidance
5. Installation Guide — environment and setup procedures
6. API Reference — public API reference
7. Class Diagrams — static system/domain relationships
8. Sequence Diagrams — major runtime workflows
9. Documentation Validation — consistency check against the current source and test baseline

The next activity, if desired, is the previously deferred independent final project audit.