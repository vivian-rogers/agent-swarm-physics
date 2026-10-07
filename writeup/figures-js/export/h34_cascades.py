"""H34 idea cascades (Fig. cascades): (a) #51 cascade-size CCDF vs one branching law and the critical law, other
periods as thin lines; (b) idea branching ratio per period vs room size.

    uv run python writeup/figures-js/export/h34_cascades.py

Reuses writeup/visuals/H34-idea-cascades/make.py (load, ccdf, wilson; the old fig_col.pdf) and H34's GW-NB size law
(hypotheses/H34-idea-cascades/analysis/h34stats.py), both imported read-only, with the same seeds (band: 34; x
jitter in (b): 7 per regime), so every drawn value equals the old figure's. Inputs are round-1b, non-reserved by
construction (make.load asserts no reserved goal period).
"""
from __future__ import annotations

import importlib.util
import sys

import numpy as np
import polars as pl

from common import ROOT, write

sys.path.insert(0, str(ROOT / "writeup/visuals"))
sys.path.insert(0, str(ROOT / "hypotheses/H34-idea-cascades/analysis"))
# make.py does `from common import load_holdout` (infra/shared/common.py); give it that module while it loads
_ours = sys.modules["common"]
_sc = importlib.util.spec_from_file_location("common", ROOT / "infra/shared/common.py")
sys.modules["common"] = importlib.util.module_from_spec(_sc)
_sc.loader.exec_module(sys.modules["common"])
_spec = importlib.util.spec_from_file_location("h34make", ROOT / "writeup/visuals/H34-idea-cascades/make.py")
M = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(M)
sys.modules["common"] = _ours
import h34stats as HS  # noqa: E402

D = M.D


def main():
    p = M.load()                       # asserts no reserved period
    others = []
    for g in p["goal"].to_list():
        if g == 51:
            continue
        sz = pl.read_parquet(D / f"G{g:02d}/trees.parquet")["size"].to_numpy()
        s, c, _, _ = M.ccdf(sz, int(sz.max()))
        others.append(dict(goal=g, s=s, c=c))
    r = p.filter(pl.col("goal") == 51).to_dicts()[0]
    sz = pl.read_parquet(D / "G51/trees.parquet")["size"].to_numpy()
    N = max(int(r["N_room"]), int(sz.max()))
    pm = HS.nb_gw_pmf_trunc(r["R"], r["k"], N)
    rng = np.random.default_rng(34)
    sims = rng.multinomial(len(sz), pm, size=2000)
    cc = np.cumsum(sims[:, ::-1], axis=1)[:, ::-1] / len(sz)
    lo, hi = np.percentile(cc, [2.5, 97.5], axis=0)
    law = np.cumsum(pm[::-1])[::-1]
    s, c, k, n = M.ccdf(sz, int(sz.max()))
    wl, wh = M.wilson(k, n)
    obs = [dict(s=int(a), c=float(b), lo=float(x), hi=float(y)) for a, b, x, y, kk in zip(s, c, wl, wh, k) if kk > 0]
    band = [dict(s=int(i + 1), lo=float(a), hi=float(b), law=float(m)) for i, (a, b, m) in enumerate(zip(lo, hi, law))]

    per = []
    for rg in ("I", "II", "III"):
        v = p.filter(pl.col("regime") == rg)
        xN = v["N_room"].to_numpy() * np.exp(np.random.default_rng(7).uniform(-0.04, 0.04, v.height))
        for row, xj in zip(v.iter_rows(named=True), xN):
            per.append(dict(goal=row["goal"], regime=rg, N=row["N_room"], x=float(xj), R=row["R"], lo=row["R_lo"], hi=row["R_hi"]))
    med = float(p["R"].median())
    summ = dict(n_periods=p.height, n_upper_below1=int((p["R_hi"] < 1).sum()), R_min=float(p["R"].min()),
                R_max=float(p["R"].max()), R_median=med, R51=float(r["R"]), k51=float(r["k"]), N51=int(r["N_room"]),
                trees51=int(len(sz)), smax51=int(sz.max()))
    print(summ)
    # numbers printed in the paper: R-hat 0.09-0.40 (median 0.22), 32/32 upper bounds < 1, #51 R-hat 0.23, 31 others
    assert f"{summ['R_min']:.2f}" == "0.09" and f"{summ['R_max']:.2f}" == "0.40" and f"{med:.2f}" == "0.22", summ
    assert summ["n_periods"] == 32 and summ["n_upper_below1"] == 32 and f"{summ['R51']:.2f}" == "0.23", summ
    write("h34_cascades", dict(others=others, obs=obs, band=band, periods=per, summary=summ),
          "writeup/figures-js/export/h34_cascades.py",
          ["data/processed/H34-idea-cascades/r1b/results/period_table.parquet",
           "data/processed/H34-idea-cascades/r1b/G<NN>/trees.parquet",
           "data/processed/H67-lagged-criticality-dial/results/periods.parquet"],
          dict(band_sims=2000, band_seed=34, jitter_seed=7, cls="ALL"))


if __name__ == "__main__":
    main()
