"""
====================================================================
Banking Management System (BMS)

File        : constants.py
Description : Enumerations and application-wide constants

Author      : Adel Alawiyat / ChatGPT
Python      : 3.13+
====================================================================
"""

from __future__ import annotations

from decimal import Decimal
from enum import Enum, IntEnum, auto


# ==================================================================
# Application
# ==================================================================

class Environment(str, Enum):
    """Application execution environments."""

    DEVELOPMENT = "development"
    TESTING = "testing"
    PRODUCTION = "production"


# ==================================================================
# Currency
# ==================================================================

class Currency(str, Enum):
    """Supported currencies."""

    SAR = "SAR"
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"
    AED = "AED"
    KWD = "KWD"
    BHD = "BHD"
    QAR = "QAR"
    OMR = "OMR"


# ==================================================================
# Account Types
# ==================================================================

class AccountType(str, Enum):
    """Supported bank account types."""

    SAVINGS = "Savings"
    CURRENT = "Current"
    TIME_DEPOSIT = "Time Deposit"


# ==================================================================
# InterestFrequency -- added bacuse it is used in import savings_account
# ==================================================================

class InterestFrequency(str, Enum):
    """Supported bank account types."""

    DAILY = 365
    WEEKLY = 52
    MONTHLY = 12
    QUARTERLY = 4
    SEMI_ANNUALLY = 2
    ANNUALLY = 1


# ==================================================================
# Account Status
# ==================================================================

class AccountStatus(str, Enum):
    """Account lifecycle status."""

    PENDING = "Pending"

    ACTIVE = "Active"

    DORMANT = "Dormant"

    FROZEN = "Frozen"

    CLOSED = "Closed"

    SUSPENDED = "Suspended"


# ==================================================================
# Customer Status
# ==================================================================

class CustomerStatus(str, Enum):

    ACTIVE = "Active"

    INACTIVE = "Inactive"

    BLACKLISTED = "Blacklisted"

    DECEASED = "Deceased"


# ==================================================================
# Employee Roles
# ==================================================================

class EmployeeRole(str, Enum):

    ADMINISTRATOR = "Administrator"

    BRANCH_MANAGER = "Branch Manager"

    TELLER = "Teller"

    CUSTOMER_SERVICE = "Customer Service"

    AUDITOR = "Auditor"

    SYSTEM_ADMIN = "System Administrator"


# ==================================================================
# Transaction Types
# ==================================================================

class TransactionType(str, Enum):

    DEPOSIT = "Deposit"

    WITHDRAWAL = "Withdrawal"

    INTERNAL_TRANSFER = "Internal Transfer"

    EXTERNAL_TRANSFER = "External Transfer"

    INTEREST = "Interest"

    FEE = "Fee"

    PENALTY = "Penalty"

    REVERSAL = "Reversal"

    ADJUSTMENT = "Adjustment"


# ==================================================================
# Transaction Status
# ==================================================================

class TransactionStatus(str, Enum):

    PENDING = "Pending"

    PROCESSING = "Processing"

    COMPLETED = "Completed"

    FAILED = "Failed"

    CANCELLED = "Cancelled"

    REVERSED = "Reversed"


# ==================================================================
# Transfer Types
# ==================================================================

class TransferType(str, Enum):

    INTERNAL = "Internal"

    EXTERNAL = "External"


# ==================================================================
# Fee Types
# ==================================================================

class FeeType(str, Enum):

    ACCOUNT_OPENING = "Account Opening"

    MONTHLY_MAINTENANCE = "Monthly Maintenance"

    ATM = "ATM"

    TRANSFER = "Transfer"

    OVERDRAFT = "Overdraft"

    EARLY_WITHDRAWAL = "Early Withdrawal"

    REPLACEMENT_CARD = "Replacement Card"


# ==================================================================
# Interest Calculation Method
# ==================================================================

class InterestMethod(str, Enum):

    SIMPLE = "Simple"

    COMPOUND = "Compound"

    DAILY = "Daily"

    MONTHLY = "Monthly"

    YEARLY = "Yearly"


# ==================================================================
# User Status
# ==================================================================

class UserStatus(str, Enum):

    ACTIVE = "Active"

    LOCKED = "Locked"

    DISABLED = "Disabled"

    PASSWORD_EXPIRED = "Password Expired"


# ==================================================================
# Gender
# ==================================================================

class Gender(str, Enum):

    MALE = "Male"

    FEMALE = "Female"

    OTHER = "Other"

    NOT_SPECIFIED = "Not Specified"


# ==================================================================
# Authentication
# ==================================================================

class LoginResult(str, Enum):

    SUCCESS = "Success"

    INVALID_PASSWORD = "Invalid Password"

    USER_NOT_FOUND = "User Not Found"

    ACCOUNT_LOCKED = "Account Locked"

    ACCOUNT_DISABLED = "Account Disabled"


# ==================================================================
# Report Types
# ==================================================================

class ReportType(str, Enum):

    CUSTOMER = "Customer"

    ACCOUNT = "Account"

    TRANSACTION = "Transaction"

    INTEREST = "Interest"

    FEES = "Fees"

    AUDIT = "Audit"

    BANK_SUMMARY = "Bank Summary"


# ==================================================================
# Log Levels
# ==================================================================

class LogLevel(str, Enum):

    DEBUG = "DEBUG"

    INFO = "INFO"

    WARNING = "WARNING"

    ERROR = "ERROR"

    CRITICAL = "CRITICAL"


# ==================================================================
# HTTP Methods
# ==================================================================

class HttpMethod(str, Enum):

    GET = "GET"

    POST = "POST"

    PUT = "PUT"

    DELETE = "DELETE"

    PATCH = "PATCH"


# ==================================================================
# Pagination Defaults
# ==================================================================

DEFAULT_PAGE_SIZE = 25

MAX_PAGE_SIZE = 500


# ==================================================================
# Money
# ==================================================================

ZERO = Decimal("0.00")

ONE_CENT = Decimal("0.01")

HUNDRED = Decimal("100.00")


# ==================================================================
# Banking
# ==================================================================

ACCOUNT_NUMBER_LENGTH = 12

CUSTOMER_NUMBER_LENGTH = 8

EMPLOYEE_NUMBER_LENGTH = 8

TRANSACTION_NUMBER_LENGTH = 14

IBAN_MIN_LENGTH = 15

IBAN_MAX_LENGTH = 34

SWIFT_LENGTH = 8


# ==================================================================
# Validation
# ==================================================================

MIN_PASSWORD_LENGTH = 8

MAX_LOGIN_ATTEMPTS = 5

MAX_NAME_LENGTH = 100

MAX_EMAIL_LENGTH = 254

PHONE_LENGTH = 15


# ==================================================================
# Date Formats
# ==================================================================

DATE_FORMAT = "%Y-%m-%d"

TIME_FORMAT = "%H:%M:%S"

DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"


# ==================================================================
# Legal Adult Age
# ==================================================================

LEGAL_ADULT_AGE = 18
