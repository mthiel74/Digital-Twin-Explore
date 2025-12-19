# Python modules

Most commands are invoked from the repo root like:

```bash
cd python
python -m twin.run_twin_stream --model msd --filter ekf --log out/run.jsonl
python -m eval.evaluate_log --log out/run.jsonl --out_prefix out/run
```
