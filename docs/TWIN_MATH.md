# Digital Twin: minimal mathematical core

This is a compact reference for the modelling/estimation layer used throughout the repo.

## Discrete-time state-space model
State:
- \(x_k \in \mathbb{R}^n\)

Inputs/controls:
- \(u_k \in \mathbb{R}^m\)

Measurements:
- \(y_k \in \mathbb{R}^p\)

Dynamics:
\[
x_{k+1} = f(x_k, u_k, t_k; \theta) + w_k,\qquad w_k \sim \mathcal{N}(0,Q)
\]

Measurement model:
\[
y_k = h(x_k, t_k; \theta) + v_k,\qquad v_k \sim \mathcal{N}(0,R)
\]

A “digital twin loop” typically does:
1) predict \(x_{k+1|k}\) via \(f\)
2) update \(x_{k+1|k+1}\) with measurement \(y_{k+1}\) via filter
3) optionally update parameters \(\theta\) via calibration

---

## Parameter calibration (typical)
Given measured series \(\{y_k\}\), choose \(\hat\theta\) to minimize:
\[
\hat\theta = \arg\min_\theta \sum_{k} \|y_k - \hat y_k(\theta)\|^2
\]
with \(\hat y_k(\theta)\) produced by simulating the model (or using the filter’s predicted measurement).

Confidence intervals can be obtained via:
- local linearization / approximate covariance
- bootstrap over time blocks
- Bayesian posterior sampling (optional)

---

## EKF vs UKF (why both)
EKF:
- linearizes \(f,h\) via Jacobians \(F=\partial f/\partial x\), \(H=\partial h/\partial x\)
- fast, but can fail with strong nonlinearities or poor linearization.

UKF:
- uses sigma points to propagate mean/covariance through nonlinear \(f,h\)
- often more robust without explicit Jacobians.

---

## Minimal “twin metrics”
- state RMSE vs ground truth (if available)
- measurement reconstruction error
- prediction error at horizons (1s, 10s, ...)
- anomaly detection ROC / detection delay
- calibration error of \(\theta\) and its uncertainty

