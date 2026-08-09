"""Tests for reporting.export_service."""

import csv
from datetime import datetime
from pathlib import Path

import pytest

from reporting.export_service import ExportService
from reporting.report_generator import Report, ReportMetadata


def make_report(rows=None):
    report = Report(
        metadata=ReportMetadata("Export Test", datetime(2026, 8, 9, 12, 0)),
        columns=("Account", "Balance"),
    )
    for row in rows or []:
        report.add_row(*row)
    return report


def test_constructor_creates_output_directory(tmp_path):
    output = tmp_path / "nested" / "reports"

    service = ExportService(output)

    assert output.is_dir()
    assert service.output_directory == output


def test_constructor_uses_default_reports_directory(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)

    service = ExportService()

    assert service.output_directory == Path("reports")
    assert (tmp_path / "reports").is_dir()


def test_export_csv_creates_file_and_returns_path(tmp_path):
    service = ExportService(tmp_path / "reports")

    path = service.export_csv(make_report([("A1", "100.00")]), "accounts.csv")

    assert path == tmp_path / "reports" / "accounts.csv"
    assert path.is_file()


def test_export_csv_writes_header_and_rows(tmp_path):
    service = ExportService(tmp_path)

    path = service.export_csv(
        make_report([("A1", "100.00"), ("A2", "250.00")]),
        "accounts.csv",
    )

    with path.open(newline="", encoding="utf-8") as file:
        rows = list(csv.reader(file))

    assert rows == [
        ["Account", "Balance"],
        ["A1", "100.00"],
        ["A2", "250.00"],
    ]


def test_export_csv_writes_header_for_empty_report(tmp_path):
    service = ExportService(tmp_path)

    path = service.export_csv(make_report(), "empty.csv")

    with path.open(newline="", encoding="utf-8") as file:
        rows = list(csv.reader(file))

    assert rows == [["Account", "Balance"]]


def test_export_csv_preserves_column_order(tmp_path):
    service = ExportService(tmp_path)
    report = Report(
        ReportMetadata("Test", datetime.now()),
        ("Third", "First", "Second"),
    )
    report.add_row("3", "1", "2")

    path = service.export_csv(report, "ordered.csv")

    with path.open(newline="", encoding="utf-8") as file:
        rows = list(csv.reader(file))

    assert rows[0] == ["Third", "First", "Second"]
    assert rows[1] == ["3", "1", "2"]


def test_export_csv_round_trip_preserves_persisted_content(tmp_path):
    service = ExportService(tmp_path)
    report = make_report([("A1", "100.00"), ("A2", "250.50")])

    path = service.export_csv(report, "round_trip.csv")

    with path.open(newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        persisted = list(reader)

    assert persisted == [
        {"Account": "A1", "Balance": "100.00"},
        {"Account": "A2", "Balance": "250.50"},
    ]


def test_export_csv_supports_unicode_content(tmp_path):
    service = ExportService(tmp_path)
    report = make_report([("حساب-1", "100.00")])

    path = service.export_csv(report, "unicode.csv")

    assert "حساب-1" in path.read_text(encoding="utf-8")


def test_export_csv_overwrites_existing_file(tmp_path):
    service = ExportService(tmp_path)
    path = service.export_csv(make_report([("A1", "100.00")]), "accounts.csv")

    service.export_csv(make_report([("A2", "250.00")]), "accounts.csv")

    with path.open(newline="", encoding="utf-8") as file:
        rows = list(csv.reader(file))

    assert rows == [["Account", "Balance"], ["A2", "250.00"]]


def test_export_csv_rejects_missing_parent_directory_when_filename_contains_nested_path(tmp_path):
    service = ExportService(tmp_path)

    with pytest.raises(FileNotFoundError):
        service.export_csv(make_report(), "nested/report.csv")


def test_output_directory_property_returns_path(tmp_path):
    service = ExportService(tmp_path)

    assert isinstance(service.output_directory, Path)
    assert service.output_directory == tmp_path


def test_export_service_has_expected_string_representations(tmp_path):
    service = ExportService(tmp_path)

    assert str(service) == "Report Export Service"
    assert repr(service) == f"ExportService(output_directory='{tmp_path}')"
