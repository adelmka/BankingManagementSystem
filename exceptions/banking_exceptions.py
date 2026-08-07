"""
====================================================================
Banking Management System (BMS)

File        : banking_exceptions.py
Description : Custom exception hierarchy for the Banking Management
              System.

Author      : Adel Alawiyat / ChatGPT
Version     : 1.0.0
Python      : 3.13+
====================================================================
"""

from __future__ import annotations

from typing import Any


# ===================================================================
# Base Exception
# ===================================================================

class BankingError(Exception):
    """
    Base class for all custom banking exceptions.
    """

    def __init__(
        self,
        message: str,
        *,
        error_code: str = "BANK_ERROR",
        details: dict[str, Any] | None = None,
    ) -> None:

        super().__init__(message)

        self.message = message
        self.error_code = error_code
        self.details = details or {}

    def to_dict(self) -> dict[str, Any]:
        """
        Convert exception to a serializable dictionary.
        """

        return {
            "error": self.__class__.__name__,
            "error_code": self.error_code,
            "message": self.message,
            "details": self.details,
        }

    def __str__(self) -> str:
        return f"[{self.error_code}] {self.message}"


# ===================================================================
# Configuration
# ===================================================================

class ConfigurationError(BankingError):
    """Raised when application configuration is invalid."""


# ===================================================================
# Validation
# ===================================================================

class ValidationError(BankingError):
    """Base validation error."""


class InvalidNameError(ValidationError):
    """Invalid customer or employee name."""


class InvalidEmailError(ValidationError):
    """Invalid email address."""


class InvalidPhoneError(ValidationError):
    """Invalid phone number."""


class InvalidNationalIDError(ValidationError):
    """Invalid national ID."""


class InvalidAmountError(ValidationError):
    """Invalid monetary amount."""


class CurrencyMismatchError(ValidationError):
    """Different currencies used in one operation."""

class InvalidCurrencyError(ValidationError):
    """
    Raised when an unsupported or invalid currency is supplied.

    Backward compatibility for legacy models/tests.
    """
    pass

# ===================================================================
# Customer
# ===================================================================

class CustomerError(BankingError):
    """Base customer exception."""


class CustomerAlreadyExistsError(CustomerError):
    """Customer already exists."""


class CustomerNotFoundError(CustomerError):
    """Customer not found."""


class CustomerInactiveError(CustomerError):
    """Customer is inactive."""


# ===================================================================
# Employee
# ===================================================================

class EmployeeError(BankingError):
    """Base employee exception."""


class EmployeeNotFoundError(EmployeeError):
    """Employee not found."""


# ===================================================================
# Account
# ===================================================================

class AccountError(BankingError):
    """Base account exception."""


class AccountNotFoundError(AccountError):
    """Account does not exist."""


class AccountClosedError(AccountError):
    """Account is closed."""


class AccountFrozenError(AccountError):
    """Account is frozen."""


class AccountInactiveError(AccountError):
    """Account is inactive."""


class DuplicateAccountError(AccountError):
    """Duplicate account number."""


class InsufficientFundsError(AccountError):
    """Insufficient balance."""


class OverdraftLimitExceededError(AccountError):
    """Overdraft limit exceeded."""


class MinimumBalanceViolationError(AccountError):
    """Minimum balance violated."""


# ===================================================================
# Deposit
# ===================================================================

class DepositError(AccountError):
    """Deposit operation failed."""


# ===================================================================
# Withdrawal
# ===================================================================

class WithdrawalError(AccountError):
    """Withdrawal operation failed."""


class DailyWithdrawalLimitExceededError(WithdrawalError):
    """Daily withdrawal limit exceeded."""


# ===================================================================
# Transfer
# ===================================================================

class TransferError(BankingError):
    """Base transfer exception."""


class SameAccountTransferError(TransferError):
    """Source and destination are identical."""


class ExternalTransferError(TransferError):
    """External transfer failed."""


class RecipientBankUnavailableError(TransferError):
    """Recipient bank unavailable."""


# ===================================================================
# Transaction
# ===================================================================

class TransactionError(BankingError):
    """Base transaction exception."""


class TransactionNotFoundError(TransactionError):
    """Transaction not found."""


class DuplicateTransactionError(TransactionError):
    """Duplicate transaction detected."""


class TransactionAlreadyReversedError(TransactionError):
    """Transaction already reversed."""


# ===================================================================
# Interest
# ===================================================================

class InterestError(BankingError):
    """Interest calculation error."""


# ===================================================================
# Fee
# ===================================================================

class FeeError(BankingError):
    """Fee processing error."""


# ===================================================================
# Authentication
# ===================================================================

class AuthenticationError(BankingError):
    """Authentication failed."""


class AuthorizationError(BankingError):
    """Authorization failed."""


class InvalidCredentialsError(AuthenticationError):
    """Username or password invalid."""


class AccountLockedError(AuthenticationError):
    """User account locked."""


class PasswordExpiredError(AuthenticationError):
    """Password expired."""


# ===================================================================
# Repository
# ===================================================================

class RepositoryError(BankingError):
    """Repository layer error."""


class CSVReadError(RepositoryError):
    """Unable to read CSV file."""


class CSVWriteError(RepositoryError):
    """Unable to write CSV file."""


class DataIntegrityError(RepositoryError):
    """Repository data integrity failure."""


# ===================================================================
# Reporting
# ===================================================================

class ReportError(BankingError):
    """Report generation error."""


# ===================================================================
# System
# ===================================================================

class AuditError(BankingError):
    """Audit logging failure."""


class BackupError(BankingError):
    """Backup operation failed."""


class ServiceUnavailableError(BankingError):
    """Requested service is unavailable."""


# ===================================================================
# Transactions – added based on code review
# ===================================================================

class EntityAlreadyExistsError(BankingError):
    """Entity Already Exists Error."""


class EntityNotFoundError(BankingError):
    """Entity Not Found Error."""


class UnsupportedOperationError(BankingError):
    """Unsupported Operation Error."""

class PersistenceError(TransactionError):
    """Persistence Error."""
