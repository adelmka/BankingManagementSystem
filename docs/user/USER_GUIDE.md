# Banking Management System — User Guide

## 1. Purpose

This guide explains how an end user operates the Banking Management System (BMS) through its command-line interface (CLI). It focuses on the workflows exposed by the current application rather than on internal implementation details.

The current CLI is organized around these areas: Customer Management, Account Management, Transaction Management, Reporting, Administration, System Information, and Exit.

## 2. Starting the Application

Use the application entry point provided by the current project. The startup implementation prepares storage, validates storage readiness, constructs the application dependency graph, and returns a running application instance.

At startup, the system initializes the required filesystem resources and validates the dependency graph before normal operations are exposed.

## 3. Main Menu

The main menu provides:

| Option | Function |
|---|---|
| 1 | Customer Management |
| 2 | Account Management |
| 3 | Transaction Management |
| 4 | Reporting |
| 5 | Administration |
| 6 | System Information |
| 0 | Exit |

Select the numeric option corresponding to the required function.

## 4. Customer Management

| Option | Function |
|---|---|
| 1 | Create Customer |
| 2 | View Customer |
| 3 | Update Customer |
| 4 | Delete Customer |
| 5 | List Customers |
| 0 | Back |

### Create a Customer

Select **Customer Management → Create Customer**. The current CLI collects first name, last name, email, and phone. The command layer passes the information to the customer service. On success, the system displays a confirmation and the created customer.

### View a Customer

Select **View Customer** and enter the customer ID when prompted. The system retrieves and displays the customer.

### Update a Customer

Select **Update Customer**, enter the customer ID, and provide the optional fields requested by the interface. The current command implementation supports updating email and phone.

### Delete a Customer

Select **Delete Customer**, enter the customer ID, and confirm the deletion when prompted. If confirmation is not given, the operation is cancelled.

### List Customers

Select **List Customers** to retrieve and display all customers available through the customer service.

## 5. Account Management

| Option | Function |
|---|---|
| 1 | Open Account |
| 2 | View Account |
| 3 | Close Account |
| 4 | List Customer Accounts |
| 5 | Change Interest Rate |
| 6 | Configure Fees |
| 0 | Back |

The domain model includes savings, current, and time-deposit account types.

### Open an Account

Select **Open Account** and provide the information requested by the current interface. Account creation is handled by the account service, which coordinates the repositories and applies the implemented business rules.

### View an Account

Select **View Account** and provide the account number requested by the interface.

### Close an Account

Select **Close Account** and identify the account. The service layer validates the operation before persistence is updated.

### List Customer Accounts

Select **List Customer Accounts** and identify the customer when prompted. The system retrieves accounts associated with that customer.

### Interest Rates and Fees

The Account Management menu exposes options for changing interest rates and configuring fees. Use the values and prompts presented by the current application rather than assuming a particular rate or fee.

## 6. Transaction Management

| Option | Function |
|---|---|
| 1 | Deposit |
| 2 | Withdraw |
| 3 | Transfer Between Accounts |
| 4 | Transfer to External Bank |
| 5 | View Transaction History |
| 0 | Back |

### Deposit

Select **Deposit**, identify the target account, and enter the requested amount and description. The account service applies the implemented validation and records the resulting transaction.

### Withdraw

Select **Withdraw**, identify the account, and enter the requested amount and description. The service layer validates the operation, including rules applicable to the account and available balance.

### Transfer Between Accounts

Select **Transfer Between Accounts** and provide the source account, destination account, amount, and requested description. The account and transaction services coordinate the operation and transaction records.

### External-Bank Transfer

The current menu exposes **Transfer to External Bank**. This menu label should not be interpreted as evidence of an external banking integration unless such an integration is explicitly implemented by the current command/service code.

### Transaction History

Select **View Transaction History** to retrieve transaction activity. The application also supports transaction listings, account statements, recent transactions, and date-range transaction queries through its service façade.

## 7. Reporting

| Option | Function |
|---|---|
| 1 | Customer Report |
| 2 | Account Report |
| 3 | Transaction Report |
| 4 | Bank Summary |
| 0 | Back |

The reporting subsystem is independently validated by **70 passing tests** and includes customer, account, transaction, and bank reporting plus report generation and export functionality.

### Customer Report

Use the Customer Report to produce customer-oriented report data supported by the reporting implementation.

### Account Report

Use the Account Report for account-level information supported by the reporting implementation.

### Transaction Report

Use the Transaction Report for transaction-oriented reporting.

### Bank Summary

Use the Bank Summary for aggregated banking information provided by the reporting subsystem.

### Report Output

Reports are represented using report metadata, columns, and rows. Report records can be converted to dictionaries and exported through the reporting/export functionality.

## 8. Administration

| Option | Function |
|---|---|
| 1 | Backup Data |
| 2 | Restore Data |
| 3 | Application Settings |
| 0 | Back |

These options are part of the current CLI menu definition. Their detailed behavior should follow the current command handlers and configuration implementation.

## 9. System Information

| Option | Function |
|---|---|
| 1 | Application Information |
| 2 | Storage Status |
| 3 | Configuration |
| 0 | Back |

Use these options to inspect information about the running application, storage state, and active configuration as exposed by the current interface.

## 10. Data Persistence

The implemented persistence layer uses CSV files. Application configuration determines the locations of data files and related runtime directories.

Users should not manually edit CSV files while the application is operating unless the procedure is explicitly required for an administrative or recovery task. Manual changes can violate domain validation rules or create inconsistent data.

## 11. Identifiers and Data Entry

When the interface requests a customer ID, account number, or transaction number, enter the identifier exactly as displayed by the application.

For monetary values, use the numeric format accepted by the current input handler and the application's configured currency. For dates, follow the format requested by the current prompt.

## 12. Error Handling

The CLI command layer catches operational exceptions and presents an error message through the menu renderer. Users should read the displayed error carefully before retrying an operation.

Common failure categories include invalid input, missing customer or account, duplicate entity, invalid account state, invalid transaction, insufficient available funds, persistence/storage problems, and business-rule violations.

Do not repeatedly retry an operation that reports a business-rule violation without correcting the underlying input or account state.

## 13. Typical Daily Workflow

```text
Start Application
       |
       v
Customer Management
       |
       +--> Create / View / Update Customer
       |
       v
Account Management
       |
       +--> Open Account
       |
       v
Transaction Management
       |
       +--> Deposit
       +--> Withdraw
       +--> Transfer
       +--> Review History
       |
       v
Reporting
       |
       +--> Customer / Account / Transaction / Bank Report
       |
       v
Exit
```

## 14. Safe Operating Practices

1. Verify customer and account identifiers before financial operations.
2. Verify transaction amounts before confirming operations.
3. Review the destination account before a transfer.
4. Use reporting and transaction history to verify completed activity.
5. Do not delete or modify runtime CSV files without an appropriate administrative or recovery procedure.
6. Back up application data before manual maintenance or recovery operations.
7. Protect configuration and runtime data from unauthorized access.

## 15. Functional Validation Status

The current project baseline has been validated with the complete automated test suite:

```text
1,439 passed in 10.35s
```

The reporting suite was also executed independently:

```text
70 passed in 0.55s
```

These results validate behavior represented by the current automated tests. They do not imply that every menu label represents a separately implemented external integration.

## 16. Related Documentation

- [`README.md`](../../README.md) — project overview and quick start
- [`Architecture Guide`](../architecture/ARCHITECTURE_GUIDE.md) — system architecture and design
- `docs/installation/INSTALLATION_GUIDE.md` — installation and environment setup
- `docs/developer/DEVELOPER_GUIDE.md` — development and extension guidance
- `docs/api/API_REFERENCE.md` — public API reference
- `docs/diagrams/CLASS_DIAGRAMS.md` — class diagrams
- `docs/diagrams/SEQUENCE_DIAGRAMS.md` — sequence diagrams

## 17. Scope of This Guide

This guide documents the current CLI menu structure and implemented banking workflows at the user level. It intentionally avoids inventing detailed prompts or behavior that cannot be established from the current implementation.

The source code and automated tests remain authoritative when a discrepancy exists between this guide and the running application. Documentation validation will be performed after all planned documentation deliverables are completed.
