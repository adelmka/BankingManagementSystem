"""
====================================================================
Banking Management System (BMS)

File        : report_generator.py
Description : Reporting Framework

Provides the common reporting infrastructure used throughout the
Banking Management System.

Responsibilities
----------------
• Create report metadata
• Generate report headers
• Store report records
• Produce formatted report objects

This module contains no banking-specific business logic.

Author      : Adel Alawiyat / ChatGPT
Python      : 3.13+
====================================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass(frozen=True, slots=True)
class ReportMetadata:
    """
    Metadata describing a generated report.
    """

    title: str
    generated_at: datetime
    generated_by: str = "Banking Management System"
    version: str = "1.0"


@dataclass(slots=True)
class Report:
    """
    Represents a generated report.
    """

    metadata: ReportMetadata
    columns: tuple[str, ...]
    rows: list[tuple[Any, ...]] = field(default_factory=list)

    @property
    def row_count(self) -> int:
        """
        Return the number of report rows.
        """
        return len(self.rows)

    def add_row(
        self,
        *values: Any,
    ) -> None:
        """
        Add a row to the report.

        Raises
        ------
        ValueError
            If the number of supplied values does not match the
            number of report columns.
        """

        if len(values) != len(self.columns):
            raise ValueError(
                "Row length does not match report columns."
            )

        self.rows.append(tuple(values))

    def as_dicts(self) -> list[dict[str, Any]]:
        """
        Convert report rows into dictionaries.
        """

        return [
            dict(zip(self.columns, row))
            for row in self.rows
        ]

    def clear(self) -> None:
        """
        Remove all report rows.
        """

        self.rows.clear()


class ReportGenerator:
    """
    Base report generation helper.
    """

    @staticmethod
    def create_report(
        *,
        title: str,
        columns: tuple[str, ...],
        generated_by: str = "Banking Management System",
        version: str = "1.0",
    ) -> Report:
        """
        Create an empty report.
        """

        metadata = ReportMetadata(
            title=title,
            generated_at=datetime.now(),
            generated_by=generated_by,
            version=version,
        )

        return Report(
            metadata=metadata,
            columns=columns,
        )