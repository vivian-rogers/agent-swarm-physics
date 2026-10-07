"""Shared helpers for the paper-figure exporters: write small JSON into data/processed/paper-figs/ with provenance."""
from __future__ import annotations

import datetime as dt
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "data/processed/paper-figs"
sys.path.insert(0, str(ROOT / "infra/shared"))


def _clean(o):
    import numpy as np
    if isinstance(o, dict):
        return {str(k): _clean(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [_clean(v) for v in o]
    if isinstance(o, (np.floating, float)):
        return None if not np.isfinite(o) else round(float(o), 6)
    if isinstance(o, np.integer):
        return int(o)
    if isinstance(o, np.bool_):
        return bool(o)
    if isinstance(o, np.ndarray):
        return _clean(o.tolist())
    return o


def write(name: str, data: dict, built_by: str, inputs: list[str], params: dict | None = None):
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"{name}.json").write_text(json.dumps(_clean(data), separators=(",", ":")))
    prov_f = OUT / "_provenance.json"
    prov = json.loads(prov_f.read_text()) if prov_f.exists() else {"built_by": "writeup/figures-js/export/*.py", "figures": {}}
    commit = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    prov["figures"][name] = {"built_by": built_by, "git_commit": commit, "inputs": inputs, "params": params or {},
                             "built_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")}
    prov_f.write_text(json.dumps(prov, indent=1))
    print(f"wrote {OUT / (name + '.json')} ({(OUT / (name + '.json')).stat().st_size / 1024:.0f} kB)")
