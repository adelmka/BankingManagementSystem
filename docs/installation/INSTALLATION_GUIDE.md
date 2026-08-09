# Banking Management System — Installation Guide

## 1. Purpose

This guide describes how to prepare a development/test environment for the Banking Management System (BMS), install its Python dependencies, configure the application, initialize runtime storage, and validate the installation.

The guide is based on the current repository implementation and is intended primarily for Windows/Python development environments. It does not assume a separate packaged executable or installer.

## 2. Validated Environment

The current project baseline was validated with:

| Component | Baseline |
|---|---|
| Operating system | Windows |
| Python | 3.13.9 |
| pytest | 8.4.2 |
| Full test suite | 1,439 passed |
| Reporting suite | 70 passed |

The repository's `requirements.txt` specifies Python 3.13 and the current runtime/test dependencies, including Flask, Flask-Login, Flask-WTF, Werkzeug, bcrypt, pandas, python-dotenv, openpyxl, pytest, pytest-cov, requests, python-dateutil, email-validator, WTForms, Jinja2, MarkupSafe, itsdangerous, click, colorama, tabulate, and rich.

## 3. Prerequisites

Install:

- Python 3.13 or later
- Git
- PowerShell or another supported terminal
- Internet access for package installation

A virtual environment is strongly recommended.

## 4. Verify Python and pip

From PowerShell:

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

The activated prompt should normally show `(.venv)`.

If PowerShell blocks activation, use the organization's approved Python/PowerShell policy or another supported shell rather than unnecessarily changing system security settings.

## 7. Install Dependencies

Upgrade pip:

```powershell
python -m pip install --upgrade pip
```

Install the project's declared dependencies:

```powershell
python -m pip install -r requirements.txt
```

`requirements.txt` is the authoritative dependency list for the current repository.

Verify dependency consistency:

```powershell
python -m pip check
```

Verify pytest:

```powershell
pytest --version
```

## 8. Configuration

Application configuration is centralized in `config.py` through the `Config` class and environment-specific configuration classes.

The configuration covers application and bank identity, filesystem locations, CSV files, interest rates, fees, authentication, logging, pagination, and date/time settings. The module also loads `.env` values when present.

If environment variables are required, create a local `.env` file using the names expected by the current configuration implementation. Never commit secrets, credentials, private keys, or sensitive production values.

## 9. Runtime Storage

The current persistence implementation uses CSV files. Configuration defines the locations of data files and runtime directories such as data, logs, and backups.

The project's startup/bootstrap and storage-initialization components prepare required filesystem resources. Do not manually create or alter runtime files unless the current execution path or an administrative/recovery procedure requires it.

For a new development environment:

1. Use the configured data directory.
2. Allow the project's storage initialization to prepare required resources.
3. Do not copy production data into development unless explicitly intended.
4. Never commit sensitive banking data to the repository.

## 10. Verify Configuration Import

From the repository root:

```powershell
python -c "import config; print(config.Config.APP_NAME); print(config.Config.APP_VERSION)"
```

The current configuration identifies application version **2.1.0**.

If this fails, inspect the first traceback for an environment, dependency, import/export, or configuration-path problem before modifying application code.

## 11. Validate the Installation

The primary installation test is the complete automated suite:

```powershell
pytest
```

Current validated result:

```text
1,439 passed in 10.35s
```

This validates the installed environment across unit, integration, reporting, and end-to-end tests.

## 12. Validate Reporting

```powershell
pytest tests/reporting
```

Current validated result:

```text
70 passed in 0.55s
```

## 13. Validate Integration and E2E Tests

```powershell
pytest tests/integration -v
pytest tests/e2e -v
```

These tests validate workflows across multiple application layers.

## 14. Starting the Application

The repository contains application startup/bootstrap components rather than a documented standalone executable installer.

Use the application entry point defined by the current repository when launching BMS. The startup path prepares dependencies and required storage before normal application use.

Do **not** assume a command such as `python main.py` unless the corresponding entry-point file exists in the current repository. When the entry point changes, update this guide, the README, and User Guide together.

## 15. First-Run Verification

Use this sequence after a fresh installation:

```text
1. Confirm Python version
2. Activate the virtual environment
3. Install requirements.txt
4. Run pip check
5. Verify configuration import
6. Run pytest tests/reporting
7. Run pytest
8. Start the application using its current entry point
9. Confirm storage initialization succeeds
10. Confirm the main application interface appears
```

The principal development acceptance criterion is a green complete test suite.

## 16. Windows PowerShell Quick Setup

```powershell
git clone https://github.com/adelmka/BankingManagementSystem.git
cd BankingManagementSystem
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip check
pytest
```

Expected final validation:

```text
1,439 passed
```

## 17. Updating an Existing Installation

Before updating:

```powershell
git status
git pull
```

Refresh dependencies:

```powershell
python -m pip install -r requirements.txt
python -m pip check
pytest
```

If the dependency environment becomes inconsistent, recreate the virtual environment:

```powershell
deactivate
Remove-Item -Recurse -Force .venv
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
pytest
```

## 18. Troubleshooting

### Python is not recognized

Verify that Python is installed and available on PATH. On Windows, also check the Python launcher if applicable.

### Dependency installation fails

Check the Python version, active virtual environment, package-index connectivity, and the first meaningful pip error. Do not immediately modify application code to solve a dependency installation problem.

### Pytest cannot import project modules

Run pytest from the repository root, verify the virtual environment, and inspect the first import traceback. Check package exports and project paths before changing application code.

### Tests fail because of stale data

Check local CSV/runtime artifacts and use the project's fixtures and storage initialization mechanisms. Avoid manually modifying application data to make a test pass.

### Configuration attributes appear to be missing

Check whether the consumer expects a `Config` class attribute or one of the module-level compatibility attributes exposed by the current configuration implementation.

### Several tests fail after one change

Look for a common root cause before fixing failures individually. Typical causes include a changed constructor signature, package export, repository contract, configuration path, or service API.

## 19. Development vs. Production

This guide primarily describes development/test installation. Production deployment additionally requires appropriate secret management, filesystem permissions, runtime identity, backup/recovery, logging retention, data protection, network exposure controls, authentication configuration, monitoring, and deployment-specific configuration.

These concerns should be handled by the deployment environment without weakening application validation.

## 20. Security Considerations

Never commit:

- Passwords
- API keys
- Secret keys
- Production credentials
- Private certificates or keys
- Production customer data
- Production transaction data
- Sensitive `.env` files

Because the application uses CSV persistence, operating-system filesystem permissions are an important part of protecting stored banking data.

## 21. Reproducibility Checklist

- [ ] Correct Python version installed
- [ ] Repository cloned
- [ ] Virtual environment created and activated
- [ ] `requirements.txt` installed
- [ ] `pip check` passes
- [ ] Configuration imports successfully
- [ ] Runtime storage can be initialized
- [ ] Reporting tests pass
- [ ] Integration tests pass
- [ ] E2E tests pass
- [ ] Full test suite passes
- [ ] No secrets or runtime banking data are committed

## 22. Current Validation Baseline

```text
Python 3.13.9
pytest 8.4.2

pytest tests/reporting
70 passed in 0.55s

pytest
1,439 passed in 10.35s
```

Future dependency, configuration, or startup changes should be validated against a fresh environment where practical and should preserve or explicitly update the regression baseline.

## 23. Related Documentation

- [`README.md`](../../README.md) — project overview
- [`Architecture Guide`](../architecture/ARCHITECTURE_GUIDE.md) — architecture and design
- [`User Guide`](../user/USER_GUIDE.md) — user workflows
- [`Developer Guide`](../developer/DEVELOPER_GUIDE.md) — development practices
- `docs/api/API_REFERENCE.md` — API reference
- `docs/diagrams/CLASS_DIAGRAMS.md` — class diagrams
- `docs/diagrams/SEQUENCE_DIAGRAMS.md` — sequence diagrams

## 24. Source of Truth

Installation commands, dependency declarations, configuration names, and startup procedures must remain synchronized with the repository.

When this guide conflicts with implementation, `requirements.txt`, `config.py`, startup/bootstrap code, and automated tests are authoritative. Update this guide as part of the same change that alters installation or startup behavior.
