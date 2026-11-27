# Privacy & Data Handling

**Rule: your garden stays yours.** Open Garden OS does not phone home.

## What the tool stores

- Sensor readings (moisture, humidity, weather observations)
- Growth stage notes and digital-twin scene references
- Camera annotation coordinates (bounding boxes + labels), not photos by default
- Optional coarse geolocation (latitude/longitude/elevation/timezone)

## What it does NOT do

- No account, no login, no user IDs
- No network calls in the default demo or rule-engine path
- No upload of your coordinates, photos, or schedules
- No telemetry, analytics, or crash reporting
- No cloud LLM unless you explicitly connect one yourself

## Sharing safely

- The shipped `data/synthetic-field.json` is synthetic and safe to share.
- Before filing an issue or contributing a fixture, remove real coordinates, exact addresses, and identifiable images. Use coarse location (e.g. rounded to a city) or none.
- Camera references should be relative paths or handles (`synthetic://...`, `local://...`), never public URLs containing signed tokens.
- Do not commit `.env`, credential files, model weights, or personal notes.

## LLM boundary

If you choose to attach a local model client:
- The monitor sends the *snapshot fields* (sensor values, stage, annotations) to your local model only.
- It requires the reply to cite real sensor IDs; unknown IDs cause a hard failure.
- It never receives your address or identity — only the fields present in the snapshot you choose to supply.

## Licence

Apache-2.0. No warranty; see LICENSE. © 2026 PCMedicalist — All Rights Reserved
