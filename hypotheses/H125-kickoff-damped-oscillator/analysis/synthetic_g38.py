"""H125 N3 size check (post hoc, after the real G38 result; labelled as such in the card): rate at which M_osc beats
M_fade with zeta_fit < 1 on #38's 10-day skeleton under no-inertia worlds (W_fade, W_drift, W_tod) and an inertial world.
Writes data/processed/H125-kickoff-damped-oscillator/synthetic/g38_n3_size.json."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h125lib as L  # noqa: E402
import synthetic as SY  # noqa: E402

cal = json.loads((L.DATA / "synthetic/calibration.json").read_text())
out = {}
sk = [s for s in SY.skeletons() if s["kr"]["design"] == "T38"][0]
for cfg in ("bge_white", "gte_white"):
    cache = {}
    for w in ("W_fade_3", "W_fade_8", "W_drift", "W_tod", "W_osc_0.5"):
        rng = np.random.default_rng(38)
        hits = []
        for rep in range(100):
            y = SY.draw(w, sk, cal[cfg], rng)
            r = L.analyze_kickoff(sk["st"], sk["kr"], y, None, fitter_cache=cache, fit_days=10)
            hits.append((r["dsse"] or -1) > 0 and r["zeta_fit"] < 1)
        out[f"{cfg}|{w}"] = float(np.mean(hits))
        print(cfg, w, out[f"{cfg}|{w}"], flush=True)
(L.DATA / "synthetic/g38_n3_size.json").write_text(json.dumps(out, indent=1))
