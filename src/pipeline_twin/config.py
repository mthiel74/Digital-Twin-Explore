"""Configuration utilities for the pipeline digital twin.

The configuration uses lightweight dataclasses and JSON (YAML-compatible) files
to keep simulation and estimation settings transparent and reproducible.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, List
from copy import deepcopy


@dataclass
class DomainConfig:
    length: float = 1000.0
    n_cells: int = 50
    dt: float = 0.2
    total_time: float = 600.0
    wave_speed: float = 300.0
    friction: float = 0.02


@dataclass
class BoundaryConfig:
    pump_head: float = 2.0
    valve_setpoint: float = 1.2
    pump_ramp: float = 10.0
    valve_ramp: float = 10.0
    actuator_tau: float = 5.0


@dataclass
class LeakConfig:
    coefficient: float = 0.0
    index: Optional[int] = None
    start_time: Optional[float] = None


@dataclass
class SensorConfig:
    pressure_noise: float = 0.02
    flow_noise: float = 0.02
    pressure_bias_drift: float = 0.0
    flow_bias_drift: float = 0.0
    latency_steps: int = 0
    sample_every: int = 1
    seed: int = 1


@dataclass
class EnKFConfig:
    ensemble_size: int = 20
    inflation: float = 1.02
    obs_noise_scale: float = 1.0
    parameter_drift: float = 1e-4


@dataclass
class TwinConfig:
    domain: DomainConfig
    boundaries: BoundaryConfig
    leak: LeakConfig
    sensors: SensorConfig
    enkf: EnKFConfig
    hypotheses: Optional[List[int]] = None


def _as_dataclass(cls, data: dict):
    return cls(**{k: v for k, v in data.items() if k in cls.__annotations__})


def load_config(path: str | Path) -> TwinConfig:
    """Load a YAML config file into a :class:`TwinConfig` instance."""
    path = Path(path)
    data = json.loads(path.read_text())

    if "include" in data:
        include_raw = Path(data["include"])
        candidate_paths = []
        if include_raw.is_absolute():
            candidate_paths.append(include_raw)
        candidate_paths.append(path.parent / include_raw)
        candidate_paths.append(Path.cwd() / include_raw)

        base_path = next((p for p in candidate_paths if p.exists()), None)
        if base_path is None:
            raise FileNotFoundError(f"Include file not found: {include_raw}")

        base_cfg = json.loads(base_path.read_text())
        merged = deepcopy(base_cfg)
        merged.update({k: v for k, v in data.items() if k != "include"})
        data = merged
    domain = _as_dataclass(DomainConfig, data.get("domain", {}))
    boundaries = _as_dataclass(BoundaryConfig, data.get("boundaries", {}))
    leak = _as_dataclass(LeakConfig, data.get("leak", {}))
    sensors = _as_dataclass(SensorConfig, data.get("sensors", {}))
    enkf = _as_dataclass(EnKFConfig, data.get("enkf", {}))
    return TwinConfig(domain=domain, boundaries=boundaries, leak=leak, sensors=sensors, enkf=enkf, hypotheses=data.get("hypotheses"))


def save_config(cfg: TwinConfig, path: str | Path) -> None:
    """Write a :class:`TwinConfig` back to YAML."""
    payload = {
        "domain": cfg.domain.__dict__,
        "boundaries": cfg.boundaries.__dict__,
        "leak": cfg.leak.__dict__,
        "sensors": cfg.sensors.__dict__,
        "enkf": cfg.enkf.__dict__,
    }
    if cfg.hypotheses is not None:
        payload["hypotheses"] = cfg.hypotheses
    Path(path).write_text(json.dumps(payload, indent=2))
