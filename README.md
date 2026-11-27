# Open Garden OS

**A local-first, evidence-bound gardening assistant for homeowners of every caliber.**

> Status: **early public build (v0.1.0)**. This is an informational research tool, not agronomic advice and not an irrigation controller. No cloud account, no subscription, no telemetry about your garden leaves this machine.

## Why

Most home gardening apps need an account, a phone app that phones home, and a subscription. Open Garden OS is different:

- **Local-first** — your garden data stays on your device.
- **Evidence-bound** — every AI suggestion must cite sensor IDs that actually exist in your snapshot; hallucinated or unsafe schedules are rejected.
- **Synthetic-first** — the shipped example uses clearly-labelled synthetic data, so you can try it without owning hardware.
- **Tiered** — start with no hardware; add sensors and cameras only when you want to.

## Three tiers

| Tier | Hardware | What you can do |
|---|---|---|
| **Seed** | none / phone | keep a manual garden log; use the seasonal calendar helpers |
| **Sprout** | soil moisture + air humidity sensors | get watering plans from the local rule engine and optional local LLM monitor |
| **Canopy** | camera + digital twin | growth monitoring, canopy overlay annotations, virtualization manifests |

The storage format, contracts, and validators are the same at every tier — you can upgrade without migrating data.

## Quick start

```bash
git clone https://github.com/PCMedicalist/open-garden-os.git
cd open-garden-os
python3 -m unittest discover -s tests -v          # stdlib only, Python 3.10+
python3 -m garden_os.demo                          # run the synthetic-field demo
```

The demo prints a real baseline watering plan produced from `data/synthetic-field.json`. It uses **synthetic data only** and never waters anything.

### Optional: local LLM monitor

Requires a local Ollama model (e.g. `pcmedicalist:9b`) and the `pcm_ai`-style inference client interface (`verify_context(model, required)` + `chat(model, prompt, num_ctx=...)`). The monitor **fails loudly** if the model is missing, its context window is too small, the reply is not valid JSON, or the reply cites an unknown sensor ID. It never silently falls back to fabricated advice.

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for the data model and safety gates.

## Data & privacy

- **No account. No telemetry. No cloud calls.** Everything runs locally unless you explicitly provide a model client.
- Store only what you need: sensor readings, stage notes, and relative camera annotations.
- **Do not commit** your real coordinates, address, or identifiable photos. The example fixture is synthetic and safe to share.
- Coordinates are validated for range but otherwise stored as given — use coarse location if privacy matters.
- See [PRIVACY.md](PRIVACY.md).

## Research basis

Crop figures and home-garden variety notes in [docs/RESEARCH.md](docs/RESEARCH.md) are sourced from USDA NASS and Texas A&M AgriLife Extension. They are cited facts about what growers reported — not recommendations for your garden. Variety suitability is county- and season-specific; validate locally.

## Contributing

Bug reports and tier-appropriate improvements welcome. Please keep contributions local-first, stdlib Python where possible, and add tests. No secrets, no personal garden data, no proprietary model weights. See [CONTRIBUTING.md](CONTRIBUTING.md).

See [docs/HARDWARE.md](docs/HARDWARE.md) for a tier-by-tier compatible-hardware map (ESP32-class controllers, capacitive soil sensors, humidity sensors, cameras) mapped to the exact contract fields.

## Licence

Apache-2.0 — see [LICENSE](LICENSE). Attribution to PCMedicalist appreciated; the licence terms govern.

© 2026 PCMedicalist — All Rights Reserved
