"""Offline tests for the weather adapter (no network)."""
import json
import unittest
from urllib.parse import parse_qs, urlparse

from garden_os.contracts import WeatherInput
from garden_os.weather import build_url, fetch_weather, to_weather_input

PAYLOAD = {
    "latitude": 30.269146,
    "longitude": -97.75338,
    "timezone": "America/Chicago",
    "elevation": 157.0,
    "current": {"time": "2026-11-27T04:45", "interval": 900, "temperature_2m": 3.4, "relative_humidity_2m": 82},
    "daily": {"time": ["2026-11-27"], "precipitation_sum": [0.0]},
}


class WeatherTests(unittest.TestCase):
    def test_build_url_has_required_params(self):
        q = parse_qs(urlparse(build_url(30.2672, -97.7431, "America/Chicago")).query)
        self.assertEqual(q["latitude"], ["30.2672"])
        self.assertEqual(q["longitude"], ["-97.7431"])
        self.assertIn("temperature_2m", q["current"][0])
        self.assertIn("relative_humidity_2m", q["current"][0])
        self.assertIn("precipitation_sum", q["daily"][0])

    def test_payload_maps_to_contract(self):
        w = to_weather_input(PAYLOAD)
        self.assertIsInstance(w, WeatherInput)
        self.assertEqual(w.temperature_c, 3.4)
        self.assertEqual(w.humidity_pct, 82.0)
        self.assertEqual(w.rainfall_forecast_mm, 0.0)
        self.assertEqual(w.source, "open-meteo")
        self.assertIn("T", w.observed_at)

    def test_missing_field_fails_loudly(self):
        bad = json.loads(json.dumps(PAYLOAD))
        del bad["current"]["relative_humidity_2m"]
        with self.assertRaises(ValueError):
            to_weather_input(bad)

    def test_fetch_uses_injected_fetcher(self):
        captured = {}

        def fake(url):
            captured["url"] = url
            return json.dumps(PAYLOAD)

        w = fetch_weather(30.2672, -97.7431, "America/Chicago", fetch=fake)
        self.assertEqual(w.temperature_c, 3.4)
        self.assertIn("open-meteo.com", captured["url"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
