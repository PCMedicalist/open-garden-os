"""Agriculture watering-system contracts — stdlib only.

Covers geolocation, weather, air humidity, ground moisture, growth monitors
(virtualization), camera overlays, and an evidence-bound LLM monitoring loop.

HONESTY: these are data contracts and a demonstration scheduler, not agronomic
advice and not a deployed system. All sample data is labelled synthetic.
Every decision must cite real input IDs present in the snapshot; the LLM
monitor fails loudly on hallucinated references or out-of-bounds proposals.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

ISO_HINT = "YYYY-MM-DDTHH:MM:SS+00:00"


@dataclass(frozen=True)
class GeoLocation:
    latitude: float
    longitude: float
    elevation_m: float = 0.0
    timezone: str = "UTC"

    def __post_init__(self):
        if not -90 <= self.latitude <= 90:
            raise ValueError("latitude out of range")
        if not -180 <= self.longitude <= 180:
            raise ValueError("longitude out of range")
        if not self.timezone:
            raise ValueError("timezone required")


@dataclass(frozen=True)
class WeatherInput:
    observed_at: str
    source: str
    temperature_c: float
    humidity_pct: float
    rainfall_forecast_mm: float
    evapotranspiration_mm: float = 0.0

    def __post_init__(self):
        if not self.observed_at or not self.source:
            raise ValueError("weather requires observed_at and source")
        if not 0 <= self.humidity_pct <= 100:
            raise ValueError("humidity_pct out of range")
        if self.rainfall_forecast_mm < 0 or self.evapotranspiration_mm < 0:
            raise ValueError("rainfall/ET cannot be negative")


@dataclass(frozen=True)
class AirHumidity:
    sensor_id: str
    observed_at: str
    relative_pct: float
    temperature_c: float | None = None

    def __post_init__(self):
        if not self.sensor_id or not self.observed_at:
            raise ValueError("air humidity requires sensor_id and observed_at")
        if not 0 <= self.relative_pct <= 100:
            raise ValueError("relative humidity out of range")


@dataclass(frozen=True)
class GroundMoisture:
    sensor_id: str
    observed_at: str
    depth_cm: float
    volumetric_pct: float

    def __post_init__(self):
        if not self.sensor_id or not self.observed_at:
            raise ValueError("moisture requires sensor_id and observed_at")
        if self.depth_cm <= 0:
            raise ValueError("depth_cm must be positive")
        if not 0 <= self.volumetric_pct <= 100:
            raise ValueError("volumetric moisture out of range")


@dataclass(frozen=True)
class GrowthMonitor:
    monitor_id: str
    stage: str
    canopy_cover_pct: float
    virtualization_ref: str
    observed_at: str

    def __post_init__(self):
        if not self.monitor_id or not self.virtualization_ref or not self.observed_at:
            raise ValueError("growth monitor requires ids and observed_at")
        if not 0 <= self.canopy_cover_pct <= 100:
            raise ValueError("canopy cover out of range")


@dataclass(frozen=True)
class VirtualizationManifest:
    """Digital-twin reference — the model itself lives outside git."""

    scene_id: str
    renderer: str
    model_ref: str
    coordinate_frame: str
    camera_poses: list[dict[str, Any]] = field(default_factory=list)
    synced_at: str = ""

    def __post_init__(self):
        if not all([self.scene_id, self.renderer, self.model_ref, self.coordinate_frame]):
            raise ValueError("virtualization manifest missing required fields")


@dataclass(frozen=True)
class CameraOverlay:
    camera_id: str
    image_ref: str
    overlay_mode: str
    annotations: list[dict[str, Any]]
    calibration_ref: str = ""

    def __post_init__(self):
        if not self.camera_id or not self.image_ref:
            raise ValueError("camera overlay requires camera_id and image_ref")
        if self.overlay_mode not in ("growth-stage", "moisture-heatmap"):
            raise ValueError(f"invalid overlay_mode: {self.overlay_mode}")
        for a in self.annotations:
            bbox = a.get("bbox")
            conf = a.get("confidence")
            if not isinstance(bbox, list) or len(bbox) != 4:
                raise ValueError("annotation bbox must be [x, y, w, h]")
            if bbox[0] < 0 or bbox[1] < 0 or bbox[2] <= 0 or bbox[3] <= 0:
                raise ValueError("annotation bbox has invalid geometry")
            if not isinstance(conf, (int, float)) or not 0 <= conf <= 1:
                raise ValueError("annotation confidence out of range")


@dataclass(frozen=True)
class WateringPolicy:
    """Shared safety bounds for both the baseline rule and the LLM monitor."""

    target_moisture_pct: float = 35.0
    rain_threshold_mm: float = 2.0
    max_duration_min: float = 60.0
    max_liters_per_min: float = 3.0
    required_context: int = 8192

    def __post_init__(self):
        if not 0 <= self.target_moisture_pct <= 100:
            raise ValueError("target moisture out of range")
        if any(v <= 0 for v in (self.rain_threshold_mm, self.max_duration_min, self.max_liters_per_min, self.required_context)):
            raise ValueError("policy bounds must be positive")


@dataclass
class FieldSnapshot:
    field_id: str
    location: GeoLocation
    observed_at: str
    weather: WeatherInput
    air_humidity: list[AirHumidity]
    ground_moisture: list[GroundMoisture]
    growth: list[GrowthMonitor]
    virtualization: VirtualizationManifest
    camera_overlays: list[CameraOverlay]
    synthetic: bool = True  # real data must be explicitly marked false

    def sensor_ids(self) -> set[str]:
        ids = {r.sensor_id for r in self.air_humidity}
        ids |= {r.sensor_id for r in self.ground_moisture}
        ids |= {g.monitor_id for g in self.growth}
        ids |= {c.camera_id for c in self.camera_overlays}
        ids.add(self.virtualization.scene_id)
        return ids

    def __post_init__(self):
        if not self.field_id or not self.observed_at:
            raise ValueError("snapshot requires field_id and observed_at")
        ids = self.sensor_ids()
        counted = (
            len(self.air_humidity) + len(self.ground_moisture)
            + len(self.growth) + len(self.camera_overlays) + 1
        )
        if len(ids) != counted:
            raise ValueError("duplicate sensor/monitor/camera/scene id in snapshot")
        scene = self.virtualization.scene_id
        if any(g.virtualization_ref != scene for g in self.growth):
            raise ValueError("growth monitor references an unknown virtualization scene")
        if not self.ground_moisture:
            raise ValueError("snapshot needs at least one ground moisture sensor")

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "FieldSnapshot":
        d = dict(data)
        d["location"] = GeoLocation(**d["location"])
        d["weather"] = WeatherInput(**d["weather"])
        d["air_humidity"] = [AirHumidity(**x) for x in d["air_humidity"]]
        d["ground_moisture"] = [GroundMoisture(**x) for x in d["ground_moisture"]]
        d["growth"] = [GrowthMonitor(**x) for x in d["growth"]]
        d["virtualization"] = VirtualizationManifest(**d["virtualization"])
        d["camera_overlays"] = [CameraOverlay(**x) for x in d["camera_overlays"]]
        return cls(**d)

    def average_moisture(self) -> float:
        return sum(r.volumetric_pct for r in self.ground_moisture) / len(self.ground_moisture)


@dataclass(frozen=True)
class WateringDecision:
    field_id: str
    duration_min: float
    volume_l: float
    rationale: str
    evidence: list[str]
    model: str
    source: str  # "baseline" | "llm"
    start_at_local: str = ""
    measured: bool = False  # a schedule is a plan, never a measured outcome

    def __post_init__(self):
        if self.source not in ("baseline", "llm"):
            raise ValueError("invalid decision source")
        if self.duration_min < 0 or self.volume_l < 0:
            raise ValueError("negative schedule values")
        if not self.rationale or not self.evidence:
            raise ValueError("decision needs rationale and evidence")
        if self.measured:
            raise ValueError("a schedule cannot be marked measured")

    def public_dict(self) -> dict[str, Any]:
        return asdict(self)


def validate_decision(decision: WateringDecision, snapshot: FieldSnapshot, policy: WateringPolicy) -> None:
    """Every cited input must resolve to a real snapshot entity. Fail loudly."""
    known = snapshot.sensor_ids() | {f"weather:{snapshot.weather.source}"}
    unknown = [e for e in decision.evidence if e not in known]
    if unknown:
        raise ValueError(f"decision cites unknown evidence: {unknown}")
    max_volume = policy.max_duration_min * policy.max_liters_per_min
    if decision.duration_min > policy.max_duration_min or decision.volume_l > max_volume:
        raise ValueError("decision exceeds safety bounds")


def baseline_schedule(snapshot: FieldSnapshot, policy: WateringPolicy | None = None) -> WateringDecision:
    """Demonstration heuristic only — NOT agronomic advice."""
    policy = policy or WateringPolicy()
    avg = snapshot.average_moisture()
    w = snapshot.weather
    evidence = [r.sensor_id for r in snapshot.ground_moisture] + [f"weather:{w.source}"]
    if w.rainfall_forecast_mm >= policy.rain_threshold_mm:
        return WateringDecision(
            field_id=snapshot.field_id, duration_min=0, volume_l=0,
            rationale=f"Forecast {w.rainfall_forecast_mm}mm >= {policy.rain_threshold_mm}mm threshold; defer.",
            evidence=evidence, model="rule-engine", source="baseline",
        )
    if avg >= policy.target_moisture_pct:
        return WateringDecision(
            field_id=snapshot.field_id, duration_min=0, volume_l=0,
            rationale=f"Mean soil moisture {avg:.1f}% at/above target {policy.target_moisture_pct}%.",
            evidence=evidence, model="rule-engine", source="baseline",
        )
    deficit = policy.target_moisture_pct - avg
    duration = min(policy.max_duration_min, round(deficit * 2, 1))  # 2 min per pct point — demo constant
    volume = round(duration * policy.max_liters_per_min, 1)
    decision = WateringDecision(
        field_id=snapshot.field_id, duration_min=duration, volume_l=volume,
        rationale=f"Demo heuristic: deficit {deficit:.1f} pct points at 2 min/point.",
        evidence=evidence, model="rule-engine", source="baseline",
    )
    validate_decision(decision, snapshot, policy)
    return decision


class WateringMonitor:
    """LLM monitoring over a snapshot. Local-first, fail-loud, no silent degrade."""

    def __init__(self, client: Any, model: str, policy: WateringPolicy | None = None):
        self.client = client
        self.model = model
        self.policy = policy or WateringPolicy()

    def check_model(self) -> None:
        self.client.verify_context(self.model, self.policy.required_context)

    def build_prompt(self, snapshot: FieldSnapshot, baseline: WateringDecision) -> str:
        return (
            "You are monitoring a DEMONSTRATION irrigation snapshot. "
            + ("The data is SYNTHETIC. " if snapshot.synthetic else "")
            + "Do not give real-world agronomic advice. Return ONLY JSON with keys: "
            "duration_min (number), volume_l (number), rationale (string), "
            "evidence (array of IDs taken ONLY from the list below). "
            f"Field: {snapshot.field_id}. Location: {snapshot.location.latitude},{snapshot.location.longitude}. "
            f"Weather: {asdict(snapshot.weather)}. "
            f"Air humidity: {[asdict(x) for x in snapshot.air_humidity]}. "
            f"Ground moisture: {[asdict(x) for x in snapshot.ground_moisture]}. "
            f"Growth: {[asdict(x) for x in snapshot.growth]}. "
            f"Camera overlays: {[asdict(x) for x in snapshot.camera_overlays]}. "
            f"Virtualization: {asdict(snapshot.virtualization)}. "
            f"Baseline plan: {baseline.public_dict()}. "
            f"Valid evidence IDs: {sorted(snapshot.sensor_ids() | {f'weather:{snapshot.weather.source}'})}. "
            f"Bounds: duration <= {self.policy.max_duration_min} min; "
            f"volume <= {self.policy.max_duration_min * self.policy.max_liters_per_min} L."
        )

    def decide(self, snapshot: FieldSnapshot) -> WateringDecision:
        self.check_model()  # missing/inadequate model raises — never silently degrades
        baseline = baseline_schedule(snapshot, self.policy)
        raw = self.client.chat(self.model, self.build_prompt(snapshot, baseline), num_ctx=self.policy.required_context)
        try:
            parsed = __import__("json").loads(raw)
        except (ValueError, TypeError) as exc:
            raise ValueError("LLM output is not valid JSON") from exc
        if not isinstance(parsed, dict):
            raise ValueError("LLM output must be a JSON object")
        required = ("duration_min", "volume_l", "rationale", "evidence")
        if any(k not in parsed for k in required):
            raise ValueError(f"LLM output missing keys: {required}")
        decision = WateringDecision(
            field_id=snapshot.field_id,
            duration_min=float(parsed["duration_min"]),
            volume_l=float(parsed["volume_l"]),
            rationale=str(parsed["rationale"]),
            evidence=[str(e) for e in parsed["evidence"]],
            model=self.model,
            source="llm",
        )
        validate_decision(decision, snapshot, self.policy)  # hallucinated IDs / out-of-bounds → raise
        return decision
