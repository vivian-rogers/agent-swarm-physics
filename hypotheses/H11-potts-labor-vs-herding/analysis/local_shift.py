"""Post-hoc (added 2026-10-03 after seeing round-1 O2): local-shift null for βJ_PL.

Each agent's within-day sequence is shifted by a random nonzero offset of at most ±1 or ±2 windows (30-60 min).
This keeps within-day trends slower than ~1 h, so a z that survives it reflects alignment at the 30-min scale
rather than slow common within-day drift. Also gives descriptive O1/O2 for #13 (below the minimum-data rule).
"""
from __future__ import annotations
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scheme"))
import h11common as HC  # noqa
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
import potts_core as P
from h11data import load_period
from explore import zscore, cw_block

out = {}
for g in [13, 18, 19, 20, 24, 25, 26, 30, 31, 37, 38, 39, 40, 41, 42]:
    rng = np.random.default_rng(777 + g)
    s, _ = load_period(g)
    obs = P.fit_pl(s, "agent")["bj"]
    r = dict(bj_pl=obs)
    for ms in (1, 2):
        nl = [P.fit_pl(P.shift_snap(s, rng, max_shift=ms), "agent")["bj"] for _ in range(99)]
        z, p, m, sd = zscore(obs, nl)
        r[f"z_local{ms}"] = z
        r[f"local{ms}_mean"] = m
    if g == 13:
        c = cw_block(s)
        n2 = [P.fit_pl(P.shift_snap(s, rng), "agent")["bj"] for _ in range(99)]
        z, p, m, sd = zscore(obs, n2)
        r.update(desc_bj_cw=c["bj"], desc_se_cw=c["se"], desc_t_cw=c["t"], desc_z_N2=z, desc_N2_mean=m,
                 blocks3=int((s.N >= 3).sum()), n_obs=int(len(s.label)))
    out[g] = r
    print(g, {k: round(v, 2) if isinstance(v, float) else v for k, v in r.items()})
(HC.OUT / "local_shift_posthoc.json").write_text(json.dumps(out, indent=1, default=float))
