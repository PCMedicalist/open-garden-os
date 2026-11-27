# Hardware Compatibility Guide

**Scope:** what can actually feed Open Garden OS contracts. This is a **buyer's map, not a shopping list** — no product is endorsed, no prices quoted (they change), and nothing here is required for the software demo (which runs on synthetic data).

## Compatibility principle

Our contracts care about **data shape**, not brand:

| Contract field | Required data | Hardware class that produces it |
|---|---|---|
| `GroundMoisture(depth_cm, volumetric_pct)` | volumetric water content (%) at a known depth | capacitive soil-moisture sensor at that depth |
| `AirHumidity(relative_pct, temperature_c)` | relative humidity % + optional temp | digital humidity/temperature sensor (DHT22-class, SHT-class, or weather station) |
| `WeatherInput(rainfall_forecast_mm, evapotranspiration_mm, humidity_pct)` | forecast/ET figures | **external weather data source** (API or manual entry) — not a local sensor |
| `GeoLocation(latitude, longitude, elevation_m, timezone)` | coordinates | GPS module or manual entry |
| `CameraOverlay(image_ref, annotations)` | images + bbox labels | any camera (USB/RPi camera/phone) + local inference |
| `VirtualizationManifest(model_ref, camera_poses)` | digital-twin scene | local compute (see tiers) |

**Important:** a sensor is compatible if it can produce a numeric value in the contract's units and an ISO timestamp. Our validators check ranges and IDs; they do not care about the vendor.

## Tier-by-tier builds

### Seed — no hardware
- A phone or laptop. Manual logs and the seasonal calendar helpers.
- Weather figures entered by hand. Zero cost, zero privacy exposure.

### Sprout — sensing + watering plans
Typical parts (class-level, verify availability/pricing yourself):
- **Controller**: ESP32-class MCU (Espressif ESP32 family — [official](https://www.espressif.com/en/products/socs/esp32)) or Raspberry Pi-class SBC. ESP32 Wi-Fi is enough to publish JSON to a local file/broker; no cloud needed.
- **Soil moisture**: capacitive (not resistive) sensors to avoid corrosion — e.g. the Adafruit STEMMA Soil Sensor, I2C capacitive ([product page](https://www.adafruit.com/product/4026), verified 200). Place at known depths (our fixture uses 10 cm and 30 cm) so `depth_cm` is meaningful.
- **Air humidity/temperature**: DHT22-class or better digital sensor; outputs `relative_pct` + `temperature_c`.
- **Weather forecast**: a local feed or manual entry. This is data, not a device.
- **Optional actuation**: our software does NOT drive pumps or valves. If you add hardware control, put it behind a separate, human-reviewed safety layer.

### Canopy — growth + virtualization
- **Camera**: USB webcam, Raspberry Pi camera module, or phone images copied locally. Our `CameraOverlay` stores image *references* and bbox annotations — not raw images — protecting privacy.
- **Local inference**: a small vision model on a local machine to produce `canopy_cover_pct` and bbox labels. Our LLM monitor needs a local model with at least `WateringPolicy.required_context` (default 8192) tokens of verified context.
- **Digital twin**: a local scene renderer (three.js or local MuJoCo per our manifest) with `camera_poses` in a defined coordinate frame (fixture uses ENU).

## Compatibility checklist (before you buy)

1. Can it output **volumetric %** (or can you calibrate raw ADC to %)? Our `GroundMoisture` rejects out-of-range values.
2. Can you assign a **stable sensor_id** and an ISO timestamp? Both are mandatory fields.
3. Does it work **locally** (no mandatory cloud account)? Our privacy model requires this.
4. Can you mount it at a **known depth** for soil sensors? Depth is part of the record.
5. Is calibration documented? Capacitive sensors still need soil-specific calibration.

## What we do NOT support yet

- Direct GPIO/pump/valve control (safety-gated layer is future work).
- Proprietary clouds or account-bound sensors as the only data path.
- Commercial farm machinery, drones, or satellite imagery ingest (research only).
- Any claim that a specific product is "certified compatible" — we validate data shape, not devices.

## Research note

Datasheets and calibration notes matter more than brand: a cheaper capacitive sensor with a documented calibration curve is more compatible (in the data-quality sense) than an expensive uncalibrated one.

© 2026 PCMedicalist — All Rights Reserved
