"""Compatibility exports for canonical NRDR radar report generation."""

from openpilot.nrdr.tools.radar_re.report import (
    _circularity_note,
    _window_label,
    generate_json,
    generate_markdown,
    write_report,
)


__all__ = (
    "_circularity_note",
    "_window_label",
    "generate_json",
    "generate_markdown",
    "write_report",
)
