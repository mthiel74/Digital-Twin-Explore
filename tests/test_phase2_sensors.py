import numpy as np

from pipeline_twin.config import SensorConfig
from pipeline_twin.sensors import SensorState, sample_sensors


def test_bias_drift_accumulates_linearly():
    cfg = SensorConfig(pressure_bias_drift=0.01, flow_bias_drift=0.02, latency_steps=0, sample_every=1, seed=0)
    state = SensorState()
    buffers = {}
    rng = np.random.default_rng(cfg.seed)
    for step in range(5):
        sample_sensors(np.zeros(3), np.zeros(2), cfg, state, step_index=step, buffers=buffers, rng=rng)
    assert abs(state.pressure_bias - 0.05) < 1e-8
    assert abs(state.flow_bias - 0.10) < 1e-8


def test_latency_buffer_delays_measurements():
    cfg = SensorConfig(latency_steps=2, sample_every=1, seed=1)
    state = SensorState()
    buffers = {}
    rng = np.random.default_rng(cfg.seed)
    outputs = []
    for step in range(4):
        meas = sample_sensors(np.array([float(step)]), np.array([float(step)]), cfg, state, step_index=step, buffers=buffers, rng=rng)
        outputs.append(meas.get("pressure"))
    assert outputs[0] is not None
    np.testing.assert_allclose(outputs[2], outputs[0])


def test_sampling_skip_respected():
    cfg = SensorConfig(sample_every=2, seed=2)
    state = SensorState()
    buffers = {}
    rng = np.random.default_rng(cfg.seed)
    meas = sample_sensors(np.ones(2), np.ones(1), cfg, state, step_index=1, buffers=buffers, rng=rng)
    assert meas == {}
