# Banking Management System

A Python-based Banking Management System (BMS) implementing core retail-banking operations using object-oriented design, service and repository layers, CSV persistence, a command-line/application interface, and reporting capabilities.

## Project Status

**Current status: Functionally validated and documentation-complete**

The current local test-suite baseline contains **1,439 tests**, and the complete suite passes:

```text
1,439 passed in 10.35s
```

The dedicated reporting suite also passes independently:

```text
70 passed in 0.55s
```

These results represent the current local validation baseline. The documentation set has now been completed and cross-checked against the repository structure and implementation.

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

The exact implementation remains the authoritative source for module names and APIs. Documentation is derived from the validated current codebase rather than from an earlier design draft.

## Configuration

Application configuration is centralized in `config.py` through the `Config` class and environment-specific configuration classes. The application supports development, testing, and production configuration profiles.

Environment-specific settings can be supplied through a `.env` file. Sensitive or environment-specific values should not be committed to source control.

Important configuration areas include:

- Application name and version
- Host and port
- Bank identification
- Currency
- Data, log, backup, static, template, and documentation directories
- CSV data-file locations
- Interest rates
- Banking fees
- Authentication settings
- Logging
- Reporting and pagination settings

## Installation

### Prerequisites

- Python 3.13 or later
- Git
- A virtual environment is recommended

### Setup

Clone the repository and enter the project directory:

```bash
git clone https://github.com/adelmka/BankingManagementSystem.git
cd BankingManagementSystem
```

Create and activate a virtual environment. For Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install the dependencies:

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Detailed installation procedures are maintained in [`docs/installation/INSTALLATION_GUIDE.md`](docs/installation/INSTALLATION_GUIDE.md).

## Running Tests

Run the complete test suite from the repository root:

```powershell
pytest
```

Run the reporting tests independently:

```powershell
pytest tests/reporting
```

Useful targeted commands include:

```powershell
pytest tests/integration -v
pytest tests/e2e -v
pytest tests/test_account_service.py -v
pytest tests/test_customer_service.py -v
pytest tests/test_transaction_service.py -v
```

The full test suite is the primary functional validation baseline.

## Test Coverage Areas

The test suite currently covers:

- Domain models and entities
- Value objects
- Repositories and persistence
- Services and business workflows
- CLI commands and application components
- Dependency management and bootstrap/startup behavior
- Reporting and export functionality
- Integration workflows
- End-to-end banking workflows

## Reporting

The reporting subsystem is independently validated by 70 passing tests covering:

- Account reports
- Bank reports
- Customer reports
- Transaction reports
- Report generation
- Export service functionality

## Documentation

The documentation set is complete and is organized as follows:

| Document | Location | Status |
|---|---|---|
| README | `README.md` | Complete |
| Architecture Guide | `docs/architecture/ARCHITECTURE_GUIDE.md` | Complete |
| User Guide | `docs/user/USER_GUIDE.md` | Complete |
| Developer Guide | `docs/developer/DEVELOPER_GUIDE.md` | Complete |
| Installation Guide | `docs/installation/INSTALLATION_GUIDE.md` | Complete |
| API Reference | `docs/api/API_REFERENCE.md` | Complete |
| Class Diagrams | `docs/diagrams/CLASS_DIAGRAMS.md` | Complete |
| Sequence Diagrams | `docs/diagrams/SEQUENCE_DIAGRAMS.md` | Complete |
| Documentation Validation | `docs/validation/DOCUMENTATION_VALIDATION.md` | Complete |

All documentation is intended to describe the implementation that exists in the repository. It does not introduce architectural changes or document deferred functionality as implemented.

## Design Approach

The project uses object-oriented programming and separation of responsibilities across the application. The documentation set describes the implemented architecture, including:

- Encapsulation
- Abstraction
- Inheritance
- Polymorphism
- Composition and collaboration between domain objects
- Repository-based persistence
- Service-layer business logic
- Application/CLI orchestration
- Reporting separation
- Centralized configuration
- Domain-specific exception handling

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

No project license has been specified in the repository documentation at this stage. Licensing information should be added when a project license is formally selected.

## Documentation Roadmap

The documentation phase is complete:

1. README — project entry point and documentation index
2. Architecture Guide — architecture, layers, responsibilities, and design decisions
3. User Guide — operational workflows
4. Developer Guide — development and extension guidance
5. Installation Guide — environment and setup procedures
6. API Reference — public classes, services, repositories, and interfaces
7. Class Diagrams — static system/domain relationships
8. Sequence Diagrams — major runtime workflows
9. Documentation Validation — consistency check against the current source and test baseline

The next project activity can be the independent final project audit, if desired.
