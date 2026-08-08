"""
Tests for application/storage_initializer.py.

These tests target the current StorageInitializer public contract while
isolating filesystem configuration, logging, and storage schema discovery.
No production architecture is changed by this test suite.
"""

import csv
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from application.storage_initializer import StorageInitializer


@pytest.fixture
def logger():
    return MagicMock()


@pytest.fixture
def storage_definitions(tmp_path):
    return [
        SimpleNamespace(
            path=tmp_path / "customers.csv",
            headers=["customer_id", "first_name", "last_name"],
        ),
        SimpleNamespace(
            path=tmp_path / "accounts.csv",
            headers=["account_number", "customer_id", "balance"],
        ),
        SimpleNamespace(
            path=tmp_path / "transactions.csv",
            headers=[],
        ),
    ]


@pytest.fixture
def config(tmp_path):
    return SimpleNamespace(
        create_directories=MagicMock(name="create_directories"),
    )


@pytest.fixture
def initializer(config, logger, storage_definitions):
    with patch(
        "application.storage_initializer.get_logger",
        return_value=logger,
    ), patch(
        "application.storage_initializer.all_storage",
        return_value=storage_definitions,
    ):
        return StorageInitializer(config=config)


def test_default_config_is_accepted():
    with patch("application.storage_initializer.get_logger"), patch(
        "application.storage_initializer.all_storage",
        return_value=[],
    ):
        initializer = StorageInitializer()

    assert initializer._config is not None


def test_supplied_config_is_retained(config, logger, storage_definitions):
    with patch(
        "application.storage_initializer.get_logger",
        return_value=logger,
    ), patch(
        "application.storage_initializer.all_storage",
        return_value=storage_definitions,
    ):
        initializer = StorageInitializer(config=config)

    assert initializer._config is config
    assert initializer._logger is logger


def test_logger_is_created_for_storage_initializer(config, logger, storage_definitions):
    with patch(
        "application.storage_initializer.get_logger",
        return_value=logger,
    ) as get_logger, patch(
        "application.storage_initializer.all_storage",
        return_value=storage_definitions,
    ):
        initializer = StorageInitializer(config=config)

    get_logger.assert_called_once_with("application.storage_initializer")
    assert initializer._logger is logger


def test_files_are_built_from_storage_definitions(initializer, storage_definitions):
    expected = {
        definition.path: definition.headers
        for definition in storage_definitions
    }

    assert initializer.files == expected


def test_file_count_matches_storage_definitions(initializer, storage_definitions):
    assert initializer.file_count == len(storage_definitions)


def test_files_property_returns_internal_file_mapping(initializer):
    assert initializer.files is initializer._files


def test_initialize_creates_directories(initializer, config):
    initializer.initialize()

    config.create_directories.assert_called_once_with()


def test_initialize_creates_missing_csv_files(initializer, storage_definitions):
    initializer.initialize()

    for definition in storage_definitions:
        assert definition.path.exists()


def test_initialize_writes_headers_to_missing_csv_files(
    initializer,
    storage_definitions,
):
    initializer.initialize()

    for definition in storage_definitions:
        with definition.path.open(
            mode="r",
            newline="",
            encoding="utf-8",
        ) as csv_file:
            rows = list(csv.reader(csv_file))

        if definition.headers:
            assert rows == [definition.headers]
        else:
            assert rows == []


def test_initialize_does_not_overwrite_existing_files(
    initializer,
    storage_definitions,
):
    existing = storage_definitions[0].path
    existing.parent.mkdir(parents=True, exist_ok=True)
    existing.write_text("existing,data\n", encoding="utf-8")

    initializer.initialize()

    assert existing.read_text(encoding="utf-8") == "existing,data\n"


def test_initialize_creates_only_missing_files(
    initializer,
    storage_definitions,
):
    existing = storage_definitions[0].path
    existing.parent.mkdir(parents=True, exist_ok=True)
    existing.write_text("existing,data\n", encoding="utf-8")

    initializer.initialize()

    assert existing.read_text(encoding="utf-8") == "existing,data\n"
    assert storage_definitions[1].path.exists()
    assert storage_definitions[2].path.exists()


def test_initialize_calls_create_directories_before_csv_creation(
    initializer,
    config,
    storage_definitions,
):
    calls = []
    config.create_directories.side_effect = lambda: calls.append("directories")

    original_create = initializer._create_csv_files
    initializer._create_csv_files = lambda: (
        calls.append("csv"),
        original_create(),
    )[1]

    initializer.initialize()

    assert calls[:2] == ["directories", "csv"]


def test_create_csv_files_writes_no_row_when_header_is_empty(
    initializer,
    storage_definitions,
):
    path = storage_definitions[2].path

    initializer._create_csv_files()

    assert path.exists()
    assert path.read_text(encoding="utf-8") == ""


def test_create_csv_files_skips_existing_path(
    initializer,
    storage_definitions,
):
    path = storage_definitions[0].path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("preserved\n", encoding="utf-8")

    initializer._create_csv_files()

    assert path.read_text(encoding="utf-8") == "preserved\n"


def test_create_csv_files_logs_each_new_file(initializer, logger, storage_definitions):
    initializer._create_csv_files()

    messages = [call.args[0] for call in logger.info.call_args_list]

    for definition in storage_definitions:
        assert f"Creating {definition.path.name}" in messages


def test_initialize_logs_start_and_completion(initializer, logger):
    initializer.initialize()

    messages = [call.args[0] for call in logger.info.call_args_list]

    assert "Initializing application storage..." in messages
    assert "Storage initialization completed." in messages


def test_validate_returns_true_when_all_files_exist(
    initializer,
    storage_definitions,
):
    initializer.initialize()

    assert initializer.validate() is True


def test_validate_returns_false_when_file_is_missing(
    initializer,
    storage_definitions,
):
    initializer.initialize()
    storage_definitions[1].path.unlink()

    assert initializer.validate() is False


def test_validate_logs_each_missing_file(
    initializer,
    logger,
    storage_definitions,
):
    initializer.initialize()
    logger.reset_mock()
    storage_definitions[0].path.unlink()
    storage_definitions[1].path.unlink()

    assert initializer.validate() is False

    errors = [call.args[0] for call in logger.error.call_args_list]
    assert f"Missing storage file: {storage_definitions[0].path}" in errors
    assert f"Missing storage file: {storage_definitions[1].path}" in errors


def test_validate_does_not_log_error_when_storage_is_complete(
    initializer,
    logger,
):
    initializer.initialize()
    logger.reset_mock()

    assert initializer.validate() is True
    logger.error.assert_not_called()


def test_file_count_is_zero_when_no_storage_definitions_are_returned(
    config,
    logger,
):
    with patch(
        "application.storage_initializer.get_logger",
        return_value=logger,
    ), patch(
        "application.storage_initializer.all_storage",
        return_value=[],
    ):
        initializer = StorageInitializer(config=config)

    assert initializer.file_count == 0
    assert initializer.files == {}
    assert initializer.validate() is True


def test_repr_reports_file_count(initializer):
    assert repr(initializer) == f"StorageInitializer(files={initializer.file_count})"


def test_repr_uses_class_name(config, logger, storage_definitions):
    class CustomStorageInitializer(StorageInitializer):
        pass

    with patch(
        "application.storage_initializer.get_logger",
        return_value=logger,
    ), patch(
        "application.storage_initializer.all_storage",
        return_value=storage_definitions,
    ):
        initializer = CustomStorageInitializer(config=config)

    assert repr(initializer) == (
        f"CustomStorageInitializer(files={len(storage_definitions)})"
    )


def test_initialize_is_idempotent_for_existing_storage(
    initializer,
    storage_definitions,
):
    initializer.initialize()
    contents_before = {
        definition.path: definition.path.read_text(encoding="utf-8")
        for definition in storage_definitions
    }

    initializer.initialize()

    contents_after = {
        definition.path: definition.path.read_text(encoding="utf-8")
        for definition in storage_definitions
    }

    assert contents_after == contents_before


def test_validate_only_checks_configured_storage_paths(
    initializer,
    tmp_path,
):
    unrelated = tmp_path / "unrelated.csv"
    unrelated.write_text("anything\n", encoding="utf-8")

    assert initializer.validate() is False


def test_initialize_preserves_header_order(
    initializer,
    storage_definitions,
):
    initializer.initialize()

    path = storage_definitions[0].path
    with path.open(mode="r", newline="", encoding="utf-8") as csv_file:
        row = next(csv.reader(csv_file))

    assert row == storage_definitions[0].headers


def test_initialize_uses_utf8_csv_encoding(
    initializer,
    storage_definitions,
):
    storage_definitions[0].headers[:] = ["customer_id", "nom_prénom", "مدينة"]

    initializer.initialize()

    with storage_definitions[0].path.open(
        mode="r",
        newline="",
        encoding="utf-8",
    ) as csv_file:
        row = next(csv.reader(csv_file))

    assert row == ["customer_id", "nom_prénom", "مدينة"]


def test_validate_returns_boolean_for_complete_storage(initializer):
    initializer.initialize()

    result = initializer.validate()

    assert isinstance(result, bool)
    assert result is True


def test_validate_returns_boolean_for_missing_storage(
    initializer,
    storage_definitions,
):
    initializer.initialize()
    storage_definitions[0].path.unlink()

    result = initializer.validate()

    assert isinstance(result, bool)
    assert result is False
