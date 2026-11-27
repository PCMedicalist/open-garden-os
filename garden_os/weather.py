"""Open-Meteo adapter — maps live weather JSON into our WeatherInput contract.

Stdlib only. No key, no account. Network access happens only when the caller
explicitly supplies a fetcher (default: urllib.request.urlopen).
"""
from __future__ import annotations

import json
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from typing import Any, Callable

from garden_os.contracts import WeatherInput

BASE = "https://api.open-meteo.com/v1/forecast"
Fetcher = Callable[[str], str]


def _default_fetch(url: str) -> str:
    with urllib.request.urlopen(url, timeout=15) as resp:
        return resp.read().decode("utf-8")


def build_url(latitude: float, longitude: float, timezone_name: str = "auto") -> str:
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": "temperature_2m,relative_humidity_2m",
        "daily": "precipitation_sum",
        "forecast_days": "1",
        "timezone": timezone_name,
    }
    return f"{BASE}?{urllib.parse.urlencode(params)}"


def to_weather_input(payload: dict[str, Any], source: str = "open-meteo") -> WeatherInput:
    """Convert an Open-Meteo payload; fail loudly if required fields are absent."""
    current = payload.get("current") or {}
    daily = payload.get("daily") or {}
    temp = current.get("temperature_2m")
    humidity = current.get("relative_humidity_2m")
    precip = (daily.get("precipitation_sum") or [None])[0]
    if temp is None or humidity is None or precip is None:
        raise ValueError("Open-Meteo payload missing temperature/humidity/precipitation")
    observed = current.get("time") or datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    if "T" not in observed:
        observed = f"{observed}T00:00:00+00:00"
    return WeatherInput(
        observed_at=observed,
        source=source,
        temperature_c=float(temp),
        humidity_pct=float(humidity),
        rainfall_forecast_mm=float(precip),
    )


def fetch_weather(latitude: float, longitude: float, timezone_name: str = "auto", fetch: Fetcher | None = None) -> WeatherInput:
    url = build_url(latitude, longitude, timezone_name)
    raw = (fetch or _default_fetch)(url)
    return to_weather_input(json.loads(raw))
