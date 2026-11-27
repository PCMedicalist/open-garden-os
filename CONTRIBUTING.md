# Contributing

Welcome! Keep it local-first, honest, and testable.

## Ground rules

1. **No personal data** — no real coordinates, addresses, identifiable photos, or `_env`/credential files in commits. Use synthetic fixtures (`data/synthetic-field.json` is the model).
2. **No advice claims** — contributions must not present schedules as agronomic advice or as measured outcomes. `measured=True` on a plan is rejected.
3. **No cloud dependency** — default paths must work offline with stdlib Python. An optional local LLM client is fine; a required API key is not.
4. **Tests required** — run `python3 -m unittest discover -s tests -v` before opening a PR.
5. **Attribution** — Apache-2.0 governs; keep the PCMedicalist notice.

## Adding a variety or sensor type

Extend the typed contracts in `garden_os/contracts.py` with validation (ranges, IDs), add a synthetic example to the fixture, and add a test that proves invalid data is rejected. Do not add real garden data.

## Reporting issues

Include: Python version, the (synthetic) fixture used, and the exact error. Never paste your real location or sensor tokens.

© 2026 PCMedicalist — All Rights Reserved
