"""
Tests for application/application.py.

These tests target the current Application contract without requiring
the real DependencyContainer or BankService to be constructed.
"""

from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from application.application import Application
from config import Config


@pytest.fixture
def config():
    """Return a minimal configuration object for isolated Application tests."""
    return SimpleNamespace(APP_NAME="Banking Management System")


@pytest.fixture