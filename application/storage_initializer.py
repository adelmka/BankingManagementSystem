"""
====================================================================
Banking Management System (BMS)

File        : storage_initializer.py
Description : Application Storage Initialization

This module prepares the application's storage environment before
the Banking Management System starts.

Responsibilities
----------------
• Create required directories
• Create missing CSV data files
• Initialize CSV headers
• Validate storage readiness
• Report initialization status

This module contains no business logic.

Author      : Adel Alawiyat / ChatGPT
Python      : 3.13+
====================================================================
"""

from __future__ import annotations

import csv
from pathlib import Path

from config import Config
from utils.logger import get_logger
from utils.storage_schema import all_storage

class StorageInitializer:
    """
    Initializes the application's storage subsystem.
    """

    #################################################################
    # Construction
    #################################################################

    def __init__(
        self,
        config: type[Config] = Config
    ) -> None:

        self._config = config

        self._logger = get_logger(__name__)

        self._files = {
            definition.path: definition.headers
            for definition in all_storage()
        }

    #################################################################
    # Initialization
    #################################################################

    def initialize(self) -> None:
        """
        Initialize the complete storage subsystem.
        """

        self._logger.info(
            "Initializing application storage..."
        )

        self._config.create_directories()

        self._create_csv_files()

        self._logger.info(
            "Storage initialization completed."
        )

    #################################################################
    # CSV Creation
    #################################################################

    def _create_csv_files(self) -> None:

        for file_path, header in self._files.items():

            if file_path.exists():
                continue

            self._logger.info(
                f"Creating {file_path.name}"
            )

            with open(
                file_path,
                mode="w",
                newline="",
                encoding="utf-8"
            ) as csv_file:

                writer = csv.writer(csv_file)

                if header:
                    writer.writerow(header)

    #################################################################
    # Validation
    #################################################################

    def validate(self) -> bool:
        """
        Validate that all required storage exists.
        """

        missing = [
            path
            for path in self._files
            if not path.exists()
        ]

        if missing:

            for file in missing:

                self._logger.error(
                    f"Missing storage file: {file}"
                )

            return False

        return True

    #################################################################
    # Information
    #################################################################

    @property
    def file_count(self) -> int:

        return len(self._files)

    @property
    def files(self) -> dict[Path, list[str]]:

        return self._files

    #################################################################
    # Representation
    #################################################################

    def __repr__(self) -> str:

        return (
            f"{self.__class__.__name__}"
            f"(files={self.file_count})"
        )