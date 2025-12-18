# AGENT Instructions

- Keep the existing `src/digital_twin_pipeline_ekf.py` working.
- Add any new pipeline twin implementations as separate modules.
- Require deterministic golden-run tests.
- Never change public CLI flags without updating `README.md` accordingly.
- Save plots to the `outputs/` directory.
- Use `numpy` and `matplotlib` only for numeric and plotting needs.
- Avoid heavy dependencies unless explicitly justified.
- Write docstrings for new code.
- Ensure `python -m pytest` runs cleanly.
