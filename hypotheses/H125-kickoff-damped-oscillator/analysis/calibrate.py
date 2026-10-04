"""H125 noise calibration for the synthetic worlds (instrument, not an outcome).

Uses DECOY directions only (other periods' kickoffs, excess against the remaining decoys), never the own k-hat, so no
statistic of the kickoff response is computed. Per regime and embedding model: variance components of the per-statement
excess alignment in a 4-level model  a = b_i + u_{i,day} + v_{i,30-min window} + e_s.
Writes data/processed/H125-kickoff-damped-oscillator/synthetic/calibration.json.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h125lib as L  # noqa: E402


def components(st: pl.DataFrame, a: np.ndarray) -> dict | None:
    post = (st["seg"] == "post").to_numpy() & np.isfinite(a) & (st["day_idx"].to_numpy() <= 10)
    if post.sum() < 200:
        return None
    df = pl.DataFrame({"i": st["agent"].to_numpy()[post], "d": st["day_idx"].to_numpy()[post],
                       "w": np.floor(st["h"].to_numpy()[post] / 0.5).astype(int), "a": a[post]})
    tot = df["a"].var()
    # statement residual within agent-window
    ww = df.group_by("i", "d", "w").agg(pl.col("a").mean().alias("m"), pl.col("a").var().alias("v"), pl.len().alias("n"))
    s2e = float(ww.filter(pl.col("n") >= 2)["v"].mean())
    # agent-day means and window means
    dd = df.group_by("i", "d").agg(pl.col("a").mean().alias("m"), pl.len().alias("n"))
    wd = ww.join(dd.rename({"m": "md", "n": "nd"}), on=["i", "d"])
    nw = float(wd["n"].mean())
    s2v = max(0.0, float(((wd["m"] - wd["md"]) ** 2).mean()) - s2e / nw)
    ii = dd.group_by("i").agg(pl.col("m").mean().alias("mi"))
    dd2 = dd.join(ii, on="i")
    nwin = float(ww.group_by("i", "d").len()["len"].mean())
    s2u = max(0.0, float(((dd2["m"] - dd2["mi"]) ** 2).mean()) - s2v / nwin - s2e / float(dd["n"].mean()))
    s2b = max(0.0, float(ii["mi"].var()) - s2u / 5)
    return dict(s2_total=float(tot), s2_e=s2e, s2_v=s2v, s2_u=s2u, s2_b=s2b)


def main():
    k = L.kickoffs().filter(pl.col("kind") == "kickoff")
    out = {}
    for cfg in ("bge_white", "gte_white"):
        per = {}
        for kr in k.iter_rows(named=True):
            st = L.stmt(kr["design"])
            _, Pq = L.excess_alignment(st, kr, cfg, with_decoys=True)
            cs = [components(st, Pq[:, q]) for q in range(0, Pq.shape[1], 3)]
            cs = [c for c in cs if c]
            if cs:
                per.setdefault(kr["regime"], []).append({kk: float(np.median([c[kk] for c in cs])) for kk in cs[0]})
        out[cfg] = {rg: {kk: float(np.median([c[kk] for c in v])) for kk in v[0]} | {"n_kickoffs": len(v)} for rg, v in per.items()}
        print(cfg, json.dumps(out[cfg], indent=1))
    (L.DATA / "synthetic").mkdir(parents=True, exist_ok=True)
    (L.DATA / "synthetic/calibration.json").write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
