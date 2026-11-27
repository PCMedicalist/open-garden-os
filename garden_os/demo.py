"""Run the synthetic-field demo — no hardware, no network, no cloud."""
import json
from pathlib import Path

from garden_os.contracts import (
    FieldSnapshot, WateringPolicy, baseline_schedule,
)

FIXTURE = Path(__file__).resolve().parents[1] / "data" / "synthetic-field.json"


def main() -> None:
    snapshot = FieldSnapshot.from_dict(json.loads(FIXTURE.read_text(encoding="utf-8")))
    decision = baseline_schedule(snapshot, WateringPolicy())
    print("Open Garden OS — synthetic demo (no real garden, no advice)")
    print(f"field: {snapshot.field_id}  synthetic={snapshot.synthetic}")
    print(f"mean soil moisture: {snapshot.average_moisture():.1f}%")
    print(f"plan: {decision.duration_min} min / {decision.volume_l} L")
    print(f"rationale: {decision.rationale}")
    print(f"evidence: {', '.join(decision.evidence)}")
    print("status: PLAN ONLY (measured=false). Not agronomic advice.")


if __name__ == "__main__":
    main()
