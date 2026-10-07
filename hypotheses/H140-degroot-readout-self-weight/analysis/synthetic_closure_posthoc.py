"""POST HOC (2026-10-07, after the real run): is the closure sum Sigma ~ 1 automatic? O3 on synthetic worlds.

The real data gave Sigma 1.03-1.05 in every k bin. This checks what Sigma the A1 estimator returns when the
generator is not literal DeGroot (W0, W-well, W-field) and when it is (W-DG; its true Sigma is s_self + W_read + 0.1).
Usage: uv run python .../analysis/synthetic_closure_posthoc.py
Output: data/processed/H140-degroot-readout-self-weight/synthetic/closure_posthoc.json
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parent / "scheme"))
import h140lib as L  # noqa: E402
import h140scheme as S  # noqa: E402
import synthetic as Y  # noqa: E402

out = {}
for name in ("51c", "G41"):
    g, units = Y.SKELETONS[name]
    sk = S.build_skeleton(g, only_units=units)
    Gb = {rm: S.orth_projector(S.goal_basis(sk.goal_no, rm if rm >= 0 else None, "bge_small", sk.regime)) for rm in np.unique(sk.rooms)}
    for wn in ("W0", "W-DG", "W-well", "W-field"):
        V = Y.generate(sk, Y.WORLDS[wn], 20, 777)
        sig = []
        for r in range(20):
            gr, _, _ = S.gram_rows(sk, V[r], Gb=Gb, with_items=False, with_sur=False)
            d, G, _ = L.prep(sk.rows, gr)
            f = L.fit(d, G, "A1", B=0)
            cl = L.closure(d, f, "A1")
            sig.append([c["Sigma"] for c in cl])
        m = max(len(x) for x in sig)
        arr = np.array([x + [np.nan] * (m - len(x)) for x in sig])
        out[f"{name}|{wn}"] = {"Sigma_median_by_bin": np.nanmedian(arr, 0).round(3).tolist(),
                               "Sigma_median_all": float(np.nanmedian(arr))}
        print(name, wn, out[f"{name}|{wn}"], flush=True)
(S.ROOT / "data/processed/H140-degroot-readout-self-weight/synthetic/closure_posthoc.json").write_text(json.dumps(out, indent=1))
