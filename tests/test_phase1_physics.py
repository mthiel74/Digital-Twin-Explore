import numpy as np

from pipeline_twin.config import load_config, TwinConfig, LeakConfig
from pipeline_twin.simulate import run_simulation
from pipeline_twin.boundaries import pump_profile, valve_profile, initialize_actuators, apply_actuator_dynamics


def test_simulation_stable_and_nonnegative():
    cfg = load_config("configs/default.yaml")
    result = run_simulation(cfg)
    pressures = np.vstack([s.pressure for s in result.states])
    assert np.all(pressures >= 0.0)
    assert np.isfinite(pressures).all()


def test_actuator_profiles_ramp_monotonic():
    from pipeline_twin.config import BoundaryConfig

    cfg = load_config("configs/default.yaml").boundaries
    domain_dt = load_config("configs/default.yaml").domain.dt
    actuator = initialize_actuators(cfg)
    times = np.linspace(0, cfg.pump_ramp, num=5)
    previous = 0.0
    for t in times:
        actuator = apply_actuator_dynamics(actuator, pump_profile(t, cfg), valve_profile(t, cfg), cfg, dt=domain_dt)
        assert actuator.pump >= previous - 1e-6
        previous = actuator.pump
    assert actuator.pump <= cfg.pump_head + 1e-6


def test_leak_reduces_pressure_at_location():
    base_cfg = load_config("configs/default.yaml")
    leak_cfg = LeakConfig(coefficient=0.2, index=10, start_time=None)
    cfg = TwinConfig(domain=base_cfg.domain, boundaries=base_cfg.boundaries, leak=leak_cfg, sensors=base_cfg.sensors, enkf=base_cfg.enkf)
    result = run_simulation(cfg)
    pressures = np.vstack([s.pressure for s in result.states])
    leak_trace = pressures[:, leak_cfg.index]
    assert leak_trace.min() < pressures[:, leak_cfg.index - 1].min() + 1e-3
