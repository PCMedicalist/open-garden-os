# Local Weather Input — Source Research

**Question:** The Weather Channel or Weather Underground for live weather into Open Garden OS?

**Answer (2026-11-27):** Neither is the best fit for a local-first open-source tool. Both require an account/API key with tiered access. Two keyless public sources were tested against the exact fields our `WeatherInput` contract needs, and both returned live data for Austin, TX:

| Source | Key needed | Live test | Fields relevant to `WeatherInput` |
|---|---|---|---|
| **Open-Meteo** (`api.open-meteo.com`) | **No** | 200 — real JSON | temperature °C, relative humidity %, daily precipitation sum mm, elevation, timezone, UTC offset |
| **NWS / weather.gov** (`api.weather.gov`) | **No** (User-Agent required) | 200 — real JSON | temperature, precipitation probability, grid/timezone; humidity was `None` in the tested period |
| Weather Underground / Weather Channel (`developer.weather.com`) | **Yes** — account + API key, tiered plans | docs reachable; `api.weather.com` bare call → 401 | usable with a key, but adds account + quota + terms to a no-account tool |
| OpenWeatherMap | **Yes** | site 200, not tested | viable alternative with key |

## Verified live Open-Meteo call

```
https://api.open-meteo.com/v1/forecast?latitude=30.2672&longitude=-97.7431\
  &current=temperature_2m,relative_humidity_2m\
  &daily=precipitation_sum&forecast_days=1&timezone=America%2FChicago
```

Returned (2026-11-27): `temperature_2m: 3.4 °C`, `relative_humidity_2m: 82 %`, `precipitation_sum: [0.00] mm`, `elevation: 157.0`, `timezone: America/Chicago`. That maps **directly** onto `WeatherInput(temperature_c, humidity_pct, rainfall_forecast_mm)` plus `GeoLocation(elevation_m, timezone)`.

## Recommendation

Default to **Open-Meteo** for Open Garden OS:
- no key, no account, no quota surprise at hobby volumes
- provides all three numeric fields our contract requires
- elevation/timezone in the same response keeps `GeoLocation` consistent

Use **NWS** as a US-only cross-check for forecast precipitation probability. Treat WU / Weather Channel / OpenWeatherMap as **opt-in adapters** for users who already have a key — never a required dependency.

## Privacy note

A weather request sends the garden's coordinates to the provider. Our default fixture is synthetic; for real use, round coordinates to the nearest ~0.01° or enter weather manually if that matters to you. No provider receives sensor data, camera data, or identity.

## Honesty

No prices or current plan limits are quoted — verify on the provider's site before choosing a paid tier. No claim that any provider is "certified"; we validate data shape only.

© 2026 PCMedicalist — All Rights Reserved
