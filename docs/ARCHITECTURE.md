# Architecture (public build v0.1.0)

## Layers

```
data/synthetic-field.json ─► garden_os.contracts (typed, validated)
                                      │
                    ┌─────────────────┴─────────────────┐
                    ▼                                   ▼
          baseline_schedule (rule)         WateringMonitor (optional local LLM)
                    │                                   │
                    └────────► WateringDecision ◄────────┘
                              (measured=false, evidence cited)
```

## Data model

`FieldSnapshot` binds together:
- `GeoLocation` — lat/lon/elevation/timezone, range-validated
- `WeatherInput` — forecast rain, humidity, evapotranspiration
- `AirHumidity` / `GroundMoisture` — sensor readings with IDs and timestamps
- `GrowthMonitor` + `VirtualizationManifest` — digital-twin scene reference
- `CameraOverlay` — growth-stage / moisture-heatmap annotations with validated bboxes

## Safety gates (why this is not just a chatbot)

1. **Provenance required** — every decision must cite evidence IDs that resolve to entities in the snapshot. Unknown IDs raise `ValueError`.
2. **Bounds enforced** — duration and volume capped by `WateringPolicy`.
3. **No measured claims** — a schedule is a plan; `measured=True` is rejected at construction.
4. **Model honesty** — the LLM path verifies the local model's architectural context window; missing/inadequate models fail loudly, never silently degrade.
5. **Synthetic default** — the shipped fixture is explicitly labelled synthetic and the prompt tells the model not to give real-world agronomic advice.

## Tiers

Seed (storage + calendar), Sprout (sensors + plans), Canopy (camera + twin) all use the same contracts — tier is a function of which fields you populate, not a different code path.

## Non-goals

No irrigation hardware control, no agronomic advice, no cloud pipeline, no user accounts, no telemetry.

© 2026 PCMedicalist — All Rights Reserved
