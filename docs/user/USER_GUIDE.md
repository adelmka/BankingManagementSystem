# Banking Management System — User Guide

## 1. Purpose

This guide explains how an end user operates the Banking Management System (BMS) through its current executable command-line interface (CLI). It focuses on the workflows exposed by `main.py` and the current command adapters rather than on internal implementation details.

## 2. Starting the Application

From the repository root, run:

```powershell
python main.py
```

The application initializes and validates runtime storage, constructs the application dependency graph, and starts the interactive CLI.

## 3. Main Menu

The current executable main menu is:

| Option | Function |
|---|---|
| 1 | Create customer |
| 2 | List customers |
| 3 | Open account |
| 4 | List accounts |
| 5 | Deposit funds |
| 6 | Withdraw funds |
| 7 | Transfer between accounts |
| 8 | View account transactions |
| 9 | Customer statistics |
| 10 | Account statistics |
| 11 | Bank statistics |
| 0 | Exit |

Select the numeric option corresponding to the required operation.

## 4. Customer Operations

### Create a Customer

Select **1 — Create customer**. The current CLI collects the customer's name, date of birth, gender, national ID, email, phone number, address, and KYC status. Optional middle name and address line 2 can be supplied when prompted. On success, the system displays the generated customer ID and customer name.

### List Customers

Select **2 — List customers**. The system retrieves customers through the application banking façade and displays the available customer records. If no customers exist, the CLI reports that no customers were found.

## 5. Account Operations

### Open an Account

Select **3 — Open account**. The current account command adapter collects the customer ID, account type, opening parameters, and account-specific settings required by the selected account type. The account service then applies the implemented business rules and persists the account.

The supported domain account types are:

- Savings account
- Current account
- Time-deposit account

Monetary input is represented internally by the `Money` value object. Enter amounts using the numeric format accepted by the prompt.

### List Accounts

Select **4 — List accounts**. The application displays available accounts, including account number, customer association, account type, and balance.

## 6. Financial Operations

### Deposit Funds

Select **5 — Deposit funds**, enter the account number, and enter a positive monetary amount. The banking façade validates the operation, updates the account, and records the resulting transaction.

### Withdraw Funds

Select **6 — Withdraw funds**, enter the account number, and enter the withdrawal amount. Account-specific eligibility and available-balance rules are applied by the domain/service layers.

### Transfer Between Accounts

Select **7 — Transfer between accounts**. Enter the source account, destination account, transfer amount, and description. The operation is coordinated through the banking façade and account/transaction services.

The current executable CLI exposes **internal account-to-account transfer only**. It does not claim an external-bank integration.

### View Account Transactions

Select **8 — View account transactions** and enter the account number. The system retrieves transaction activity for that account and displays the available transaction records. If no transactions exist, the CLI reports that no transactions were found.

## 7. Statistics and Reporting

### Customer Statistics

Select **9 — Customer statistics** to display customer-level aggregate statistics such as total, active, and inactive customers.

### Account Statistics

Select **10 — Account statistics** to display account-level aggregates, including total, active, inactive, savings, current, time-deposit, dormant, and frozen accounts where supplied by the current banking façade.

### Bank Statistics

Select **11 — Bank statistics** to display the aggregate statistics returned by `BankService.statistics()`.

The repository also contains a dedicated reporting subsystem for customer, account, transaction, and bank reports plus report generation and export. Those reporting components are covered by the reporting test suite.

## 8. Data Persistence

The implemented persistence layer uses CSV files. Application configuration determines the locations of data files and related runtime directories.

Users should not manually edit CSV files while the application is operating unless an administrative or recovery procedure explicitly requires it.

## 9. Identifiers and Data Entry

When the interface requests a customer ID or account number, enter the identifier exactly as displayed by the application.

For monetary values, enter a non-negative numeric value in the format accepted by the prompt. Financial operations such as deposits, withdrawals, and transfers apply their own minimum/eligibility rules.

For dates, follow the format shown by the current prompt, normally `%Y-%m-%d`.

For gender, use one of the values accepted by the current customer command adapter: Male, Female, Other, or Not Specified.

## 10. Error Handling

The CLI command/application boundary catches operational failures and presents an error through the menu renderer. Read the complete error before retrying an operation.

Common failure categories include invalid input, missing customer or account, duplicate entity, invalid account state, invalid transaction, insufficient funds, persistence/storage problems, and business-rule violations.

## 11. Typical Daily Workflow

```text
Start Application
       |
       +--> Create customer
       |
       +--> Open account
       |
       +--> Deposit / Withdraw
       |
       +--> Transfer between accounts
       |
       +--> View account transactions
       |
       +--> Review customer/account/bank statistics
       |
       v
Exit
```

## 12. Safe Operating Practices

1. Verify customer and account identifiers before financial operations.
2. Verify transaction amounts before confirming operations.
3. Review the destination account before a transfer.
4. Use transaction history and statistics to verify completed activity.
5. Do not delete or modify runtime CSV files without an appropriate administrative or recovery procedure.
6. Back up application data before manual maintenance or recovery operations.
7. Protect configuration and runtime data from unauthorized access.

## 13. Functional Validation Status

The latest supplied local validation baseline is:

```text
pytest -x
1,419 passed in 9.39s
```

A manual CLI workflow was also confirmed successfully for customer creation and subsequent account workflow. The automated baseline is the primary regression evidence.

## 14. Related Documentation

- [`README.md`](../../README.md) — project overview and quick start
- [`Architecture Guide`](../architecture/ARCHITECTURE_GUIDE.md) — system architecture and design
- [`Installation Guide`](../installation/INSTALLATION_GUIDE.md) — installation and environment setup
- [`Developer Guide`](../developer/DEVELOPER_GUIDE.md) — development and extension guidance
- [`API Reference`](../api/API_REFERENCE.md) — public API reference
- [`Class Diagrams`](../diagrams/CLASS_DIAGRAMS.md) — class diagrams
- [`Sequence Diagrams`](../diagrams/SEQUENCE_DIAGRAMS.md) — sequence diagrams

## 15. Scope of This Guide

This guide documents the current executable CLI menu and the implemented banking workflows at the user level. It intentionally avoids inventing capabilities not established by the current implementation.

The source code and automated tests remain authoritative when a discrepancy exists between this guide and the running application.