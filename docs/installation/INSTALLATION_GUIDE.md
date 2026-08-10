# Banking Management System — Installation Guide

## 1. Purpose

This guide describes how to prepare a development/test environment for the Banking Management System (BMS), install its Python dependencies, configure the application, initialize runtime storage, start the executable command-line application, and validate the installation.

The guide is based on the current repository implementation and is intended primarily for Windows/Python development environments. It does not assume a packaged executable or installer.

## 2. Validated Environment

The latest supplied project baseline was validated with:

| Component | Baseline |
|---|---|
| Operating system | Windows |
| Python | 3.13.9 |
| pytest | 8.4.2 |
| Full test suite | 1,419 passed |

The repository's `requirements.txt` is the authoritative dependency specification.

## 3. Prerequisites

Install:

- Python 3.13 or later
- Git
- PowerShell or another supported terminal
- Internet access for package installation

A virtual environment is strongly recommended.

## 4. Verify Python and pip

```powershell
python --version
python -m pip --version
```

The validated environment reports Python 3.13.9 and pytest 8.4.2.

## 5. Clone the Repository

```powershell
git clone https://github.com/adelmka/BankingManagementSystem.git
cd BankingManagementSystem
git status
```

Run installation and tests from the repository root because project-relative paths and pytest configuration assume that context.

## 6. Create a Virtual Environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

## 7. Install Dependencies

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip check
pytest --version
```

`requirements.txt` is the authoritative dependency list for the current repository.

## 8. Configuration

Application configuration is centralized in `config.py` through the `Config` class and environment-specific configuration classes. Configuration covers application and bank identity, filesystem locations, CSV files, interest rates, fees, authentication, logging, pagination, and date/time settings.

If environment variables are required, create a local `.env` file using the names expected by the current configuration implementation. Never commit secrets, credentials, private keys, or sensitive production values.

## 9. Runtime Storage

The current persistence implementation uses CSV files. Configuration defines the locations of data files and runtime directories such as data, logs, and backups.

The startup/bootstrap and storage-initialization components prepare required filesystem resources. Do not manually create or alter runtime files unless the current execution path or an administrative/recovery procedure requires it.

## 10. Verify Configuration Import

From the repository root:

```powershell
python -c "import config; print(config.Config.APP_NAME); print(config.Config.APP_VERSION)"
```

The current configuration identifies application version **2.1.0**.

## 11. Validate the Installation

The primary installation test is the complete automated suite:

```powershell
pytest -x
```

Latest supplied result:

```text
1,419 passed in 9.39s
```

This validates the installed environment across unit, integration, reporting, and end-to-end tests.

## 12. Validate Reporting and Targeted Areas

Use the relevant targeted commands when needed:

```powershell
pytest tests/reporting -v
pytest tests/integration -v
pytest tests/e2e -v
```

The complete suite remains the primary regression gate.

## 13. Starting the Application

The executable BMS command-line entry point is `main.py` in the repository root.

From the repository root:

```powershell
python main.py
```

The entry point starts the existing application bootstrap, initializes and validates runtime storage, obtains the configured `BankService`, creates the current CLI command adapters, and starts the interactive console using the existing rendering and input components.

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

Select **0 — Exit** to shut down normally. `Ctrl+C` is also handled as a user interruption and triggers application shutdown.

The executable startup path is covered by `tests/integration/test_cli_entry_point.py`.

## 14. First-Run Verification

Use this sequence after a fresh installation:

```text
1. Confirm Python version
2. Activate the virtual environment
3. Install requirements.txt
4. Run pip check
5. Verify configuration import
6. Run pytest -x
7. Run python main.py
8. Confirm storage initialization succeeds
9. Confirm the BMS main menu appears
10. Create a test customer
11. Open a test account
12. Verify a basic account operation if required
13. Select 0 to verify clean shutdown
```

The principal development acceptance criterion is a green complete test suite.

## 15. Windows PowerShell Quick Setup

```powershell
git clone https://github.com/adelmka/BankingManagementSystem.git
cd BankingManagementSystem
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip check
pytest -x
python main.py
```

Expected supplied automated validation baseline:

```text
1,419 passed in 9.39s
```

## 16. Updating an Existing Installation

Before updating:

```powershell
git status
git pull
```

Refresh dependencies and validate:

```powershell
python -m pip install -r requirements.txt
python -m pip check
pytest -x
```

## 17. Troubleshooting

### Python is not recognized

Verify that Python is installed and available on PATH.

### Dependency installation fails

Check the Python version, active virtual environment, package-index connectivity, and the first meaningful pip error. Do not immediately modify application code to solve a dependency installation problem.

### Pytest cannot import project modules

Run pytest from the repository root, verify the virtual environment, and inspect the first import traceback. Check package exports and project paths before changing application code.

### `python main.py` fails during startup

Run the command from the repository root and inspect the first traceback. Verify dependencies are installed and runtime storage initialization can create the configured directories/files.

### Tests fail because of stale data

Check local CSV/runtime artifacts and use the project's fixtures and storage initialization mechanisms. Avoid manually modifying application data to make a test pass.

### Configuration attributes appear to be missing

Check whether the consumer expects a `Config` class attribute or one of the module-level compatibility attributes exposed by the current configuration implementation.

### Several tests fail after one change

Look for a common root cause before fixing failures individually. Typical causes include a changed constructor signature, package export, repository contract, configuration path, or service API.

## 18. Development vs. Production

This guide primarily describes development/test installation. Production deployment additionally requires appropriate secret management, filesystem permissions, runtime identity, backup/recovery, logging retention, data protection, network exposure controls, authentication configuration, monitoring, and deployment-specific configuration.

## 19. Security Considerations

Never commit passwords, API keys, secret keys, production credentials, private certificates or keys, production customer data, production transaction data, or sensitive `.env` files.

Because the application uses CSV persistence, operating-system filesystem permissions are an important part of protecting stored banking data.

## 20. Reproducibility Checklist

- [ ] Correct Python version installed
- [ ] Repository cloned
- [ ] Virtual environment created and activated
- [ ] `requirements.txt` installed
- [ ] `pip check` passes
- [ ] Configuration imports successfully
- [ ] Runtime storage can be initialized
- [ ] Integration tests pass
- [ ] E2E tests pass
- [ ] Full test suite passes
- [ ] `python main.py` starts the CLI
- [ ] Customer creation can be initiated
- [ ] Account opening can be initiated
- [ ] `python main.py` exits cleanly through menu option 0
- [ ] No secrets or runtime banking data are committed

## 21. Current Validation Baseline

```text
Python 3.13.9
pytest 8.4.2

pytest -x
1,419 passed in 9.39s
```

The executable entry point is additionally covered by `tests/integration/test_cli_entry_point.py`. A manual CLI workflow has also been confirmed successfully for customer creation and subsequent account workflow.

## 22. Related Documentation

- [`README.md`](../../README.md) — project overview
- [`User Guide`](../user/USER_GUIDE.md) — user workflows
- [`Architecture Guide`](../architecture/ARCHITECTURE_GUIDE.md) — architecture and design
- [`Developer Guide`](../developer/DEVELOPER_GUIDE.md) — development practices
- [`API Reference`](../api/API_REFERENCE.md) — API reference
- [`Class Diagrams`](../diagrams/CLASS_DIAGRAMS.md) — class diagrams
- [`Sequence Diagrams`](../diagrams/SEQUENCE_DIAGRAMS.md) — sequence diagrams
- [`Documentation Validation`](../validation/DOCUMENTATION_VALIDATION.md) — documentation consistency baseline

## 23. Source of Truth

Installation commands, dependency declarations, configuration names, and startup procedures must remain synchronized with the repository.

When this guide conflicts with implementation, `requirements.txt`, `config.py`, startup/bootstrap code, `main.py`, and automated tests are authoritative. Update this guide as part of the same change that alters installation or startup behavior.