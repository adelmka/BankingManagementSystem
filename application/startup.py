"""
====================================================================
Banking Management System (BMS)

File        : startup.py
Description : Application Startup

Provides the entry point for creating and starting the Banking
Management System.

Responsibilities
----------------
• Create the Bootstrap object
• Initialize the application
• Return the running Application instance

This module intentionally contains no presentation logic.

Author      : Adel Alawiyat / ChatGPT
Python      : 3.13+
====================================================================
"""

from __future__ import annotations

from config import Config

from application.application import Application
from application.bootstrap import Bootstrap

from utils.logger import get_logger


_logger = get_logger(__name__)


def start_application(
    config: type[Config] = Config
) -> Application:
    """
    Create and start the Banking Management System.

    Parameters
    ----------
    config
        Application configuration.

    Returns
    -------
    Application
        Fully initialized application.
    """

    _logger.info(
        "Launching Banking Management System..."
    )

    bootstrap = Bootstrap(config=config)

    application = bootstrap.initialize()

    _logger.info(
        "Banking Management System started successfully."
    )

    return application


def shutdown_application(
    application: Application
) -> None:
    """
    Shutdown the Banking Management System gracefully.
    """

    application.shutdown()

    _logger.info(
        "Banking Management System stopped."
    )


__all__ = (
    "start_application",
    "shutdown_application",
)