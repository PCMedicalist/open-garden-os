"""Agriculture watering-system tests (stdlib unittest, no network)."""
import copy
import json
import unittest
from pathlib import Path

from garden_os.contracts import (
    CameraOverlay, FieldSnapshot, GeoLocation, GrowthMonitor, VirtualizationManifest,
    WateringDecision, WateringMonitor, WateringPolicy, baseline_schedule, validate_decision,
)

FIXTURE = Path(__file__).resolve().parents[1] / "data" / "synthetic-field.json"


class FakeClient:
    def __init__(self, replies, context=32768, installed=True):
        self.replies = list(replies)
        self.context = context
        self.installed = installed

    def verify_context(self, model, required):
        if not self.installed:
            raise RuntimeError("model not installed")
        if self.context < required:
            raise RuntimeError("context too small")

    def chat(self, model, prompt, num_ctx=None):
        return self.replies.pop(0)


def snapshot():
    return FieldSnapshot.from_dict(json.loads(FIXTURE.read_text()))


class SnapshotTests(unittest.TestCase):
    def test_fixture_parses_and_is_explicitly_synthetic(self):
        s = snapshot()
        self.assertTrue(s.synthetic)
        self.assertEqual(s.field_id, "demo-field-01")

    def test_all_requested_capabilities_are_represented(self):
        s = snapshot()
        self.assertIsInstance(s.location, GeoLocation)  # geo location
        self.assertGreater(s.weather.rainfall_forecast_mm, 0)  # weather inputs
        self.assertTrue(s.air_humidity)  # water humidity level
        self.assertEqual(len(s.ground_moisture), 2)  # ground moisture sensors
        self.assertTrue(s.growth)  # growth monitors
        self.assertTrue(s.virtualization.camera_poses)  # virtualization
        self.assertTrue(all(isinstance(c, CameraOverlay) for c in s.camera_overlays))  # image overlay

    def test_duplicate_ids_rejected(self):
        d = json.loads(FIXTURE.read_text())
        d["ground_moisture"][1]["sensor_id"] = "soil-10cm"
        with self.assertRaises(ValueError):
            FieldSnapshot.from_dict(d)

    def test_growth_must_reference_virtualization_scene(self):
        d = json.loads(FIXTURE.read_text())
        d["growth"][0]["virtualization_ref"] = "unknown-twin"
        with self.assertRaises(ValueError):
            FieldSnapshot.from_dict(d)

    def test_invalid_camera_bbox_rejected(self):
        d = json.loads(FIXTURE.read_text())
        d["camera_overlays"][0]["annotations"][0]["bbox"] = [-1, 0, 10, 10]
        with self.assertRaises(ValueError):
            FieldSnapshot.from_dict(d)

    def test_decision_cannot_be_marked_measured(self):
        with self.assertRaises(ValueError):
            WateringDecision(field_id="x", duration_min=1, volume_l=1, rationale="r",
                             evidence=["soil-10cm"], model="m", source="baseline", measured=True)


class ScheduleTests(unittest.TestCase):
    def test_baseline_uses_weather_and_moisture(self):
        s = snapshot()
        d = baseline_schedule(s)
        self.assertEqual(d.source, "baseline")
        self.assertFalse(d.measured)
        self.assertIn("weather:synthetic-weather-station", d.evidence)
        self.assertIn("soil-10cm", d.evidence)

    def test_heavy_rain_defers_watering(self):
        s = snapshot()
        d = copy.copy(s.weather)
        object.__setattr__(d, 'rainfall_forecast_mm', 5.0)
        s2 = copy.copy(s)
        s2.weather = d
        decision = baseline_schedule(s2)
        self.assertEqual(decision.duration_min, 0)
        self.assertIn("Forecast", decision.rationale)

    def test_decision_rejects_unknown_evidence(self):
        s = snapshot()
        d = baseline_schedule(s)
        bad = copy.copy(d)
        object.__setattr__(bad, "evidence", ["sensor-that-does-not-exist"])
        with self.assertRaises(ValueError):
            validate_decision(bad, s, WateringPolicy())


class MonitorTests(unittest.TestCase):
    def test_monitor_validates_llm_output_and_evidence(self):
        s = snapshot()
        reply = json.dumps({"duration_min": 12, "volume_l": 36, "rationale": "synthetic demo",
                            "evidence": ["soil-10cm", "weather:synthetic-weather-station"]})
        monitor = WateringMonitor(FakeClient([reply]), "pcmedicalist:9b")
        d = monitor.decide(s)
        self.assertEqual(d.source, "llm")
        self.assertEqual(d.model, "pcmedicalist:9b")

    def test_hallucinated_evidence_fails_loudly(self):
        s = snapshot()
        reply = json.dumps({"duration_min": 12, "volume_l": 36, "rationale": "x", "evidence": ["fake-sensor"]})
        with self.assertRaises(ValueError):
            WateringMonitor(FakeClient([reply]), "pcmedicalist:9b").decide(s)

    def test_out_of_bounds_schedule_fails_loudly(self):
        s = snapshot()
        reply = json.dumps({"duration_min": 999, "volume_l": 9999, "rationale": "x", "evidence": ["soil-10cm"]})
        with self.assertRaises(ValueError):
            WateringMonitor(FakeClient([reply]), "pcmedicalist:9b").decide(s)

    def test_invalid_json_fails_loudly(self):
        s = snapshot()
        with self.assertRaises(ValueError):
            WateringMonitor(FakeClient(["not json"]), "pcmedicalist:9b").decide(s)

    def test_inadequate_model_context_fails_loudly(self):
        s = snapshot()
        monitor = WateringMonitor(FakeClient([], context=4096), "pcmedicalist:9b")
        with self.assertRaises(RuntimeError):
            monitor.decide(s)

    def test_prompt_marks_synthetic_data(self):
        s = snapshot()
        prompt = WateringMonitor(FakeClient([]), "pcmedicalist:9b").build_prompt(s, baseline_schedule(s))
        self.assertIn("SYNTHETIC", prompt)
        self.assertIn("Do not give real-world agronomic advice", prompt)


if __name__ == "__main__":
    unittest.main(verbosity=2)
