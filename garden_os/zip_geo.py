"""Keyless US ZIP-code geocoding via zippopotam.us.

No account, no API key. Used only to resolve a ZIP to coordinates for a weather
request; the ZIP itself is never stored or logged by our code.
"""
from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Callable

BASE = "https://api.zippopotam.us/us"


@dataclass(frozen=True)
class ZipLocation:
    zip_code: str
    place: str
    state: str
    latitude: float
    longitude: float

    def public_dict(self) -> dict:
        return {
            "zip_code": self.zip_code,
            "place": self.place,
            "state": self.state,
            "latitude": self.latitude,
            "longitude": self.longitude,
        }


def parse_zip_response(payload: dict) -> ZipLocation:
    """Convert a zippopotam.us payload; fail loudly on malformed data."""
    places = payload.get("places") or []
    if not places:
        raise ValueError("no places returned for ZIP code")
    p = places[0]
    try:
        lat, lon = float(p["latitude"]), float(p["longitude"])
    except (KeyError, TypeError, ValueError) as e:
        raise ValueError("ZIP payload missing valid coordinates") from e
    if not (-90 <= lat <= 90 and -180 <= lon <= 180):
        raise ValueError("ZIP payload coordinates out of range")
    return ZipLocation(
        zip_code=str(payload.get("post code", "")),
        place=str(p.get("place name", "")),
        state=str(p.get("state abbreviation", "")),
        latitude=lat,
        longitude=lon,
    )


def resolve_zip(zip_code: str, fetch: Callable[[str], str] | None = None) -> ZipLocation:
    """Resolve a 5-digit US ZIP. `fetch` is injectable so tests stay offline."""
    code = zip_code.strip()
    if len(code) != 5 or not code.isdigit():
        raise ValueError("ZIP code must be exactly 5 digits")
    url = f"{BASE}/{urllib.parse.quote(code)}"
    if fetch is None:
        try:
            with urllib.request.urlopen(url, timeout=10) as resp:
                raw = resp.read().decode("utf-8")
        except urllib.error.HTTPError as e:
            if e.code == 404:
                raise ValueError(f"ZIP code {code} not found") from e
            raise
        return parse_zip_response(json.loads(raw))
    return parse_zip_response(json.loads(fetch(url)))
