"""
====================================================================
Banking Management System (BMS)

File        : bootstrap.py
Description : Application Bootstrap

Coordinates application startup.

Responsibilities
----------------
• Initialize application storage
• Validate storage readiness
• Construct the Application object

Bootstrap is responsible only for startup orchestration.
It does not own the application's lifetime.

Author      : adelmka / ChatGPT
Python      : 3.13+
====================================================================
"""

from __future__ import annotations

from config import Config

from application.application import Application
from application.storage_initializer import StorageInitializer

from utils.logger import get_logger


class Bootstrap:
    """
    Coordinates application startup.

    This class prepares the application's environment and then
    constructs the Application object.

    After initialization completes, Bootstrap has no further
    responsibilities.
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

        self._storage_initializer = StorageInitializer(
            config=self._config
        )

    #################################################################
    # Startup
    #################################################################

    def initialize(self) -> Application:
        """
        Initialize the Banking Management System.

        Returns
        -------
        Application
            Fully initialized application instance.
        """

        self._logger.info(
            "Starting Banking Management System..."
        )

        #
        # Ensure storage exists.
        #
        self._storage_initializer.initialize()

        if not self._storage_initializer.validate():

            raise RuntimeError(
                "Application storage validation failed."
            )

        #
        # Construct the application.
        #
        application = Application(
            config=self._config
        )

        self._logger.info(
            "Application bootstrap completed."
        )

        return application

    #################################################################
    # Representation
    #################################################################

    def __repr__(self) -> str:

        return (
            f"{self.__class__.__name__}"
            "(ready=True)"
        )

    def __str__(self) -> str:

        return (
            f"{self._config.APP_NAME} Bootstrap"
        )
