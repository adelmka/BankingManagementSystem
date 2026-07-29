"""
====================================================================
Banking Management System (BMS)

File        : logger.py
Description : Centralized logging configuration

Author      : Adel Alawiyat / ChatGPT
Version     : 1.0.0
Python      : 3.13+
====================================================================
"""

from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from config import Config


class LoggerFactory:
    """
    Creates and configures loggers used throughout the application.
    """

    _initialized = False

    @classmethod
    def initialize(cls) -> None:
        """
        Initialize logging infrastructure.

        This method is safe to call multiple times.
        """

        if cls._initialized:
            return

        Config.create_directories()

        cls._configure_logger(
            "application",
            Config.APPLICATION_LOG
        )

        cls._configure_logger(
            "audit",
            Config.AUDIT_LOG
        )

        cls._configure_logger(
            "error",
            Config.ERROR_LOG
        )

        cls._initialized = True

    @staticmethod
    def _configure_logger(
        name: str,
        logfile: Path
    ) -> logging.Logger:
        """
        Configure a logger.
        """

        logger = logging.getLogger(name)

        if logger.handlers:
            return logger

        logger.setLevel(Config.LOG_LEVEL)

        formatter = logging.Formatter(

            fmt=(
                "%(asctime)s | "
                "%(levelname)-8s | "
                "%(name)-12s | "
                "%(module)s | "
                "%(funcName)s | "
                "%(message)s"
            ),

            datefmt="%Y-%m-%d %H:%M:%S"

        )

        file_handler = RotatingFileHandler(
            logfile,
            maxBytes=5 * 1024 * 1024,
            backupCount=10,
            encoding="utf-8"
        )

        file_handler.setFormatter(formatter)

        logger.addHandler(file_handler)

        if Config.DEBUG:

            console = logging.StreamHandler()

            console.setFormatter(formatter)

            logger.addHandler(console)

        logger.propagate = False

        return logger

    @staticmethod
    def application() -> logging.Logger:
        """
        Return application logger.
        """
        LoggerFactory.initialize()
        return logging.getLogger("application")

    @staticmethod
    def audit() -> logging.Logger:
        """
        Return audit logger.
        """
        LoggerFactory.initialize()
        return logging.getLogger("audit")

    @staticmethod
    def error() -> logging.Logger:
        """
        Return error logger.
        """
        LoggerFactory.initialize()
        return logging.getLogger("error")


# ------------------------------------------------------------------
# Convenience logger instances
# ------------------------------------------------------------------

application_logger = LoggerFactory.application()

audit_logger = LoggerFactory.audit()

error_logger = LoggerFactory.error()
