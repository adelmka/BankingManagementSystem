"""
====================================================================
Banking Management System (BMS)

File        : generators.py
Description : Centralized generators for business identifiers,
              references, passwords and security tokens.

Author      : Adel Alawiyat / ChatGPT
Version     : 1.0.0
Python      : 3.13+
====================================================================
"""

from __future__ import annotations

import secrets
import string
from datetime import datetime
from pathlib import Path


class IDGenerator:
    """
    Generates business identifiers.

    NOTE:
    -----
    The current implementation generates IDs in memory.

    In a future database implementation these methods can
    query the database sequence or repository to guarantee
    uniqueness across distributed systems.

    With CSV persistence the Repository Layer will verify
    uniqueness before committing records.
    """

    CUSTOMER_PREFIX = "C"
    EMPLOYEE_PREFIX = "E"
    ACCOUNT_PREFIX = "A"
    TRANSACTION_PREFIX = "T"
    BANK_PREFIX = "B"

    @staticmethod
    def _timestamp() -> str:
        """
        Current timestamp.

        Format:
            YYYYMMDDHHMMSSffffff
        """

        return datetime.now().strftime("%Y%m%d%H%M%S%f")

    @classmethod
    def customer_id(cls) -> str:
        """
        Example:
            C20260723211500123456
        """

        return f"{cls.CUSTOMER_PREFIX}{cls._timestamp()}"

    @classmethod
    def employee_id(cls) -> str:

        return f"{cls.EMPLOYEE_PREFIX}{cls._timestamp()}"

    @classmethod
    def account_number(cls) -> str:

        return f"{cls.ACCOUNT_PREFIX}{cls._timestamp()}"

    @classmethod
    def transaction_number(cls) -> str:

        return f"{cls.TRANSACTION_PREFIX}{cls._timestamp()}"

    @classmethod
    def bank_id(cls) -> str:

        return f"{cls.BANK_PREFIX}{cls._timestamp()}"


class ReferenceGenerator:
    """
    Generates references used in banking operations.
    """

    @staticmethod
    def transfer_reference() -> str:
        """
        Example:

            TRF-20260723-AB12CD34
        """

        random_part = secrets.token_hex(4).upper()

        return (
            f"TRF-"
            f"{datetime.now():%Y%m%d}-"
            f"{random_part}"
        )

    @staticmethod
    def receipt_number() -> str:
        """
        Example:

            RCP-20260723230512345678
        """

        return (
            "RCP-"
            f"{datetime.now():%Y%m%d%H%M%S%f}"
        )

    @staticmethod
    def audit_reference() -> str:
        """
        Example:

            AUD-20260723230601
        """

        return (
            "AUD-"
            f"{datetime.now():%Y%m%d%H%M%S}"
        )


class SecurityGenerator:
    """
    Security-related generators.
    """

    DEFAULT_PASSWORD_LENGTH = 12

    @staticmethod
    def temporary_password(
        length: int = DEFAULT_PASSWORD_LENGTH
    ) -> str:
        """
        Generate a secure temporary password.

        Contains:

            Uppercase

            Lowercase

            Numbers

            Symbols
        """

        if length < 8:
            raise ValueError(
                "Password length must be at least 8."
            )

        alphabet = (
            string.ascii_letters
            + string.digits
            + "!@#$%&*?"
        )

        while True:

            password = "".join(
                secrets.choice(alphabet)
                for _ in range(length)
            )

            if (
                any(c.isupper() for c in password)
                and any(c.islower() for c in password)
                and any(c.isdigit() for c in password)
                and any(c in "!@#$%&*?" for c in password)
            ):

                return password

    @staticmethod
    def api_token(length: int = 32) -> str:
        """
        Generate secure API token.
        """

        return secrets.token_hex(length)

    @staticmethod
    def session_token() -> str:
        """
        Generate session identifier.
        """

        return secrets.token_urlsafe(32)


class FileGenerator:
    """
    Generates filenames for exports and backups.
    """

    @staticmethod
    def backup_filename() -> str:

        return (
            "backup_"
            f"{datetime.now():%Y%m%d_%H%M%S}.zip"
        )

    @staticmethod
    def report_filename(
        report_name: str,
        extension: str = "pdf"
    ) -> str:

        return (
            f"{report_name}_"
            f"{datetime.now():%Y%m%d_%H%M%S}."
            f"{extension}"
        )

    @staticmethod
    def export_filename(
        dataset: str,
        extension: str = "csv"
    ) -> str:

        return (
            f"{dataset}_"
            f"{datetime.now():%Y%m%d_%H%M%S}."
            f"{extension}"
        )


class DirectoryGenerator:
    """
    Creates project folders when needed.
    """

    @staticmethod
    def create(path: Path) -> None:

        path.mkdir(
            parents=True,
            exist_ok=True
        )

# ------------------------------------------------------------------
# Backward Compatibility
# ------------------------------------------------------------------

class Generator:
    """
    Compatibility wrapper for legacy code.
    """

    @staticmethod
    def customer_id():
        return IDGenerator.customer_id()

    @staticmethod
    def employee_id():
        return IDGenerator.employee_id()

    @staticmethod
    def account_number():
        return IDGenerator.account_number()

    @staticmethod
    def transaction_number():
        return IDGenerator.transaction_number()

    @staticmethod
    def bank_id():
        return IDGenerator.bank_id()

    @staticmethod
    def transfer_reference():
        return ReferenceGenerator.transfer_reference()

    @staticmethod
    def receipt_number():
        return ReferenceGenerator.receipt_number()

    @staticmethod
    def audit_reference():
        return ReferenceGenerator.audit_reference()

    @staticmethod
    def temporary_password(length=12):
        return SecurityGenerator.temporary_password(length)

    @staticmethod
    def api_token(length=32):
        return SecurityGenerator.api_token(length)

    @staticmethod
    def session_token():
        return SecurityGenerator.session_token()
