"""Farmers' Almanac / Old Farmer's Almanac — source registry and user-entered seasonal context.

NO SCRAPING, NO COPIED CONTENT. This module stores citations and dates the user
enters themselves from a source they consulted. It never downloads or redistributes
almanac text, forecasts, or planting tables.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime


@dataclass(frozen=True)
class AlmanacSource:
    label: str
    url: str
    publisher: str
    api: str
    licence_note: str


# Verified 2026-11-27 (HTTP status checked). No public JSON API was found;
# /api and /feed paths on almanac.com returned 404. farmersalmanac.com/feed is RSS.
SOURCES = (
    AlmanacSource(
        label="Farmers' Almanac",
        url="https://www.farmersalmanac.com/",
        publisher="Almanac Publishing Co.",
        api="none found (RSS at /feed)",
        licence_note="Site terms include restrictive copying language; contact publisher before reusing content.",
    ),
    AlmanacSource(
        label="The Old Farmer's Almanac",
        url="https://www.almanac.com/",
        publisher="Yankee Publishing Inc.",
        api="none found (no public JSON API)",
        licence_note="2026 Planting Calendar by ZIP code is published on-site; cite, do not copy.",
    ),
)


@dataclass(frozen=True)
class SeasonalContext:
    """Local frost-free window the user transcribed from a source they consulted."""

    frost_free_start: date
    frost_free_end: date
    source_label: str
    source_url: str
    user_entered: bool = True

    def __post_init__(self) -> None:
        if not self.user_entered:
            raise ValueError("seasonal context must be user-entered; no scraping or copied content")
        if self.frost_free_end <= self.frost_free_start:
            raise ValueError("frost_free_end must be after frost_free_start")
        if not self.source_label or not self.source_url.startswith("https://"):
            raise ValueError("source citation required (https URL)")

    def status(self, on: date) -> str:
        """Informational status only — never a planting instruction."""
        if self.frost_free_start <= on <= self.frost_free_end:
            return f"Within user-entered frost-free window ({self.source_label})."
        return f"Outside user-entered frost-free window ({self.source_label})."

    def public_dict(self) -> dict:
        return {
            "frost_free_start": self.frost_free_start.isoformat(),
            "frost_free_end": self.frost_free_end.isoformat(),
            "source_label": self.source_label,
            "source_url": self.source_url,
            "user_entered": self.user_entered,
            "status_note": "informational only — not agronomic advice",
        }


def source_by_label(label: str) -> AlmanacSource:
    for s in SOURCES:
        if s.label.lower() == label.lower():
            return s
    raise ValueError(f"unknown almanac source: {label}")
