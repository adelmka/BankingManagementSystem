"""
====================================================================
Banking Management System (BMS)

File        : config.py
Description : Centralized application configuration

Author      : Adel Alawiyat / ChatGPT
Python      : 3.13+
====================================================================
"""

from pathlib import Path
from dotenv import load_dotenv
import os

# ------------------------------------------------------------------
# Load .env
# ------------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent

load_dotenv(BASE_DIR / ".env")


class Config:
    """
    Base configuration shared by all environments.
    """

    # --------------------------------------------------------------
    # Application
    # --------------------------------------------------------------

    APP_NAME = "Banking Management System"

    APP_VERSION = "1.0.0"

    SECRET_KEY = os.getenv(
        "SECRET_KEY",
        "CHANGE_THIS_SECRET_KEY"
    )

    DEBUG = False

    TESTING = False

    HOST = os.getenv("HOST", "127.0.0.1")

    PORT = int(os.getenv("PORT", 5000))

    # --------------------------------------------------------------
    # Bank
    # --------------------------------------------------------------

    BANK_NAME = os.getenv(
        "BANK_NAME",
        "Python National Bank"
    )

    BANK_CODE = os.getenv("BANK_CODE", "PNB")

    BANK_SWIFT = os.getenv(
        "BANK_SWIFT",
        "PNBUS33"
    )

    COUNTRY = os.getenv(
        "COUNTRY",
        "Saudi Arabia"
    )

    DEFAULT_CURRENCY = os.getenv(
        "DEFAULT_CURRENCY",
        "SAR"
    )

    CURRENCY_SYMBOL = os.getenv(
        "CURRENCY_SYMBOL",
        "SR"
    )

    # --------------------------------------------------------------
    # Paths
    # --------------------------------------------------------------

    BASE_DIR = BASE_DIR

    DATA_DIR = BASE_DIR / "data"

    LOG_DIR = BASE_DIR / "logs"

    STATIC_DIR = BASE_DIR / "static"

    TEMPLATE_DIR = BASE_DIR / "templates"

    DOCUMENTATION_DIR = BASE_DIR / "documentation"

    TEST_DIR = BASE_DIR / "tests"

    BACKUP_DIR = BASE_DIR / "backup"

    # --------------------------------------------------------------
    # CSV Files
    # --------------------------------------------------------------

    CUSTOMERS_FILE = DATA_DIR / "customers.csv"

    ACCOUNTS_FILE = DATA_DIR / "accounts.csv"

    TRANSACTIONS_FILE = DATA_DIR / "transactions.csv"

    USERS_FILE = DATA_DIR / "users.csv"

    EMPLOYEES_FILE = DATA_DIR / "employees.csv"

    FEES_FILE = DATA_DIR / "fees.csv"

    INTEREST_FILE = DATA_DIR / "interest_rates.csv"

    SETTINGS_FILE = DATA_DIR / "settings.csv"

    AUDIT_FILE = DATA_DIR / "audit_log.csv"

    BANKS_FILE = DATA_DIR / "banks.csv"

    # --------------------------------------------------------------
    # Interest Rates
    # --------------------------------------------------------------

    SAVINGS_INTEREST = float(
        os.getenv("SAVINGS_INTEREST", "2.5")
    )

    CURRENT_INTEREST = float(
        os.getenv("CURRENT_INTEREST", "0")
    )

    TIME_DEPOSIT_INTEREST = float(
        os.getenv("TIME_DEPOSIT_INTEREST", "5.5")
    )

    # --------------------------------------------------------------
    # Fees
    # --------------------------------------------------------------

    TRANSFER_FEE = float(
        os.getenv("TRANSFER_FEE", "5")
    )

    WITHDRAWAL_FEE = float(
        os.getenv("WITHDRAWAL_FEE", "1")
    )

    ATM_FEE = float(
        os.getenv("ATM_FEE", "2")
    )

    OVERDRAFT_FEE = float(
        os.getenv("OVERDRAFT_FEE", "35")
    )

    EARLY_WITHDRAWAL_FEE = float(
        os.getenv("EARLY_WITHDRAWAL_FEE", "100")
    )

    # --------------------------------------------------------------
    # Authentication
    # --------------------------------------------------------------

    SESSION_TIMEOUT = int(
        os.getenv("SESSION_TIMEOUT", "30")
    )

    PASSWORD_HASH_ROUNDS = int(
        os.getenv("PASSWORD_HASH_ROUNDS", "12")
    )

    MAX_LOGIN_ATTEMPTS = int(
        os.getenv("MAX_LOGIN_ATTEMPTS", "5")
    )

    # --------------------------------------------------------------
    # Logging
    # --------------------------------------------------------------

    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

    APPLICATION_LOG = LOG_DIR / "application.log"

    ERROR_LOG = LOG_DIR / "error.log"

    AUDIT_LOG = LOG_DIR / "audit.log"

    # --------------------------------------------------------------
    # Miscellaneous
    # --------------------------------------------------------------

    PAGE_SIZE = int(os.getenv("PAGE_SIZE", "25"))

    REPORT_PAGE_SIZE = int(
        os.getenv("REPORT_PAGE_SIZE", "100")
    )

    DATE_FORMAT = "%Y-%m-%d"

    TIME_FORMAT = "%H:%M:%S"

    DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"

    @classmethod
    def create_directories(cls):
        """
        Create all required folders.
        """

        directories = [
            cls.DATA_DIR,
            cls.LOG_DIR,
            cls.STATIC_DIR,
            cls.TEMPLATE_DIR,
            cls.DOCUMENTATION_DIR,
            cls.TEST_DIR,
            cls.BACKUP_DIR
        ]

        for directory in directories:
            directory.mkdir(
                parents=True,
                exist_ok=True
            )


# ------------------------------------------------------------------
# Development
# ------------------------------------------------------------------

class DevelopmentConfig(Config):

    DEBUG = True


# ------------------------------------------------------------------
# Testing
# ------------------------------------------------------------------

class TestingConfig(Config):

    TESTING = True

    DEBUG = True


# ------------------------------------------------------------------
# Production
# ------------------------------------------------------------------

class ProductionConfig(Config):

    DEBUG = False


config = {

    "development": DevelopmentConfig,

    "testing": TestingConfig,

    "production": ProductionConfig,

    "default": DevelopmentConfig

}
