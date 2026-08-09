"""Tests for the reporting framework."""

from datetime import datetime

import pytest

from reporting.report_generator import Report, ReportGenerator, ReportMetadata


def test_report_metadata_defaults_are_applied():
    generated_at = datetime(2026, 8, 9, 20, 0, 0)

    metadata = ReportMetadata(title="Test", generated_at=generated_at)

    assert metadata.title == "Test"
    assert metadata.generated_at == generated_at
    assert metadata.generated_by == "Banking Management System"
    assert metadata.version == "1.0"


def test_report_metadata_accepts_explicit_values():
    generated_at = datetime(2026, 8, 9, 20, 0, 0)

    metadata = ReportMetadata(
        title="Test",
        generated_at=generated_at,
        generated_by="Tester",
        version="2.1",
    )

    assert metadata.generated_by == "Tester"
    assert metadata.version == "2.1"


def test_report_metadata_is_immutable():
    metadata = ReportMetadata("Test", datetime.now())

    with pytest.raises(AttributeError):
        metadata.title = "Changed"


def test_report_starts_empty():
    report = Report(
        metadata=ReportMetadata("Test", datetime.now()),
        columns=("A", "B"),
    )

    assert report.rows == []
    assert report.row_count == 0


def test_add_row_appends_valid_row():
    report = Report(
        ReportMetadata("Test", datetime.now()),
        ("A", "B"),
    )

    report.add_row(1, "two")

    assert report.rows == [(1, "two")]
    assert report.row_count == 1


def test_add_row_preserves_multiple_rows_in_order():
    report = Report(ReportMetadata("Test", datetime.now()), ("A",))

    report.add_row(1)
    report.add_row(2)

    assert report.rows == [(1,), (2,)]
    assert report.row_count == 2


@pytest.mark.parametrize("values", [(), (1, 2, 3)])
def test_add_row_rejects_wrong_column_count(values):
    report = Report(ReportMetadata("Test", datetime.now()), ("A", "B"))

    with pytest.raises(ValueError, match="Row length"):
        report.add_row(*values)


def test_as_dicts_returns_empty_list_for_empty_report():
    report = Report(ReportMetadata("Test", datetime.now()), ("A", "B"))

    assert report.as_dicts() == []


def test_as_dicts_maps_columns_to_values():
    report = Report(ReportMetadata("Test", datetime.now()), ("A", "B"))
    report.add_row(1, "two")
    report.add_row(3, "four")

    assert report.as_dicts() == [
        {"A": 1, "B": "two"},
        {"A": 3, "B": "four"},
    ]


def test_clear_removes_all_rows():
    report = Report(ReportMetadata("Test", datetime.now()), ("A",))
    report.add_row(1)
    report.add_row(2)

    report.clear()

    assert report.rows == []
    assert report.row_count == 0


def test_clear_on_empty_report_is_safe():
    report = Report(ReportMetadata("Test", datetime.now()), ("A",))

    report.clear()

    assert report.row_count == 0


def test_create_report_builds_empty_report_with_metadata():
    report = ReportGenerator.create_report(
        title="Generated",
        columns=("A", "B"),
        generated_by="Tester",
        version="2.1",
    )

    assert isinstance(report, Report)
    assert report.metadata.title == "Generated"
    assert report.metadata.generated_by == "Tester"
    assert report.metadata.version == "2.1"
    assert isinstance(report.metadata.generated_at, datetime)
    assert report.columns == ("A", "B")
    assert report.row_count == 0
