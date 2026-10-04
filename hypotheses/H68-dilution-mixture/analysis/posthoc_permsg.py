"""POST HOC (2026-10-04, after the round-1 real run): per-agent exponents with H18's per-message mention factor.

The pre-registered model applies the mention factor once per (talk, sender) unit (e^{gamma m_j}). H18's M_pow applies
it per pending message: hazard theta * (n_j - n_ment + n_ment e^gamma) * k^-beta. With the per-message factor the
pooled exponent reproduces H18 exactly (G51 0.609, G38 0.685). This script refits every agent that way (gamma profiled
per agent on a grid) and repeats the period mixture tests, to check that H68's verdicts do not depend on the choice.
Writes data/processed/H68-dilution-mixture/posthoc_permsg.json.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h68lib as L  # noqa: E402

D = HERE.parents[2] / "data/processed/H68-dilution-mixture"
GRID = np.arange(0.0, 3.51, 0.25)


def fit_agent(g):
    y = g["resp"].to_numpy()
    n = g["n"].to_numpy().astype(float)
    m = g["n_ment"].to_numpy().astype(float)
    best = None
    for G in GRID:
        r = L.fit_cll(y, -g["logk"].to_numpy()[:, None], np.log(n - m + m * np.exp(G)), g["day"].to_numpy())
        if best is None or r["ll"] > best[1]["ll"]:
            best = (G, r)
    return float(best[1]["b"][0]), float(best[1]["se"][0])


def main():
    out = {}
    for p in json.loads((D / "results.json").read_text())["periods"]:
        u = pl.read_parquet(D / p / "units.parquet")
        b, s, ags = [], [], []
        for (a,), g in u.group_by(["agent"], maintain_order=True):
            if L.eligible(g, "resp"):
                bb, ss = fit_agent(g)
                b.append(bb), s.append(ss), ags.append(int(a))
        if len(b) < 4:
            continue
        b, s = np.array(b), np.array(s)
        mt = L.mixture_test(b, s, B=200, seed=int(p[1:]))
        lo, hi = L.tau_profile_ci(b, s)
        out[p] = dict(n=len(b), mu=mt["U"]["mu"], tau=mt["U"]["tau"], tau_ci=[lo, hi], p=mt["p"], p1=L.p1_pass(mt),
                      modes=[mt["M2"]["m_lo"], mt["M2"]["m_hi"]], beta_range=[float(b.min()), float(b.max())],
                      agents=dict(zip(ags, b.tolist())))
        print(p, {k: (round(v, 3) if isinstance(v, float) else v) for k, v in out[p].items() if k != "agents"}, flush=True)
    (D / "posthoc_permsg.json").write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
