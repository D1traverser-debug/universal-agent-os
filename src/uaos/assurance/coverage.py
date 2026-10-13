from __future__ import annotations

from .models import CoverageEntry


def coverage_map(entries: tuple[CoverageEntry, ...]) -> dict[str, dict[str, CoverageEntry]]:
    """Group coverage by semantic subject type instead of raw test count."""
    result: dict[str, dict[str, CoverageEntry]] = {}
    for entry in entries:
        group = result.setdefault(entry.subject_type, {})
        if entry.subject_id in group:
            raise ValueError(f"duplicate coverage subject: {entry.subject_type}:{entry.subject_id}")
        group[entry.subject_id] = entry
    return result
