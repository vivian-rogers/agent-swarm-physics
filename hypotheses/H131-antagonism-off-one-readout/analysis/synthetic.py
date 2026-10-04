"""H131 synthetic validation (axis F), run BEFORE any outcome statistic: planted stance worlds on the real #12 (and
#26) reply skeletons (speakers, targets, phases, read status, post-read call index, times); the real flags are not read.

Worlds: W0 none; W1 read-gated quench (kappa -> 0); W2 clock-gated at the verdict instant; W3_<s> clock with a common
delay; W4_<k> remanence over k post-read talk calls; W5_<s> clock decay; W6 relation-bound (no settlement effect);
WON2 switch-on builds up over 3 talk calls. Open-rival latent rate 0.3, baseline 0.03, speaker/target effects sd 0.4,
labeller recall U(0.55, 0.65), false-positive rate U(0.004, 0.006).
Output: data/processed/H131-antagonism-off-one-readout/synthetic/{g12,g26}.parquet, summary.json
Usage: uv run python hypotheses/H131-antagonism-off-one-readout/analysis/synthetic.py [--R 200]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h131lib as L  # noqa: E402

ROOT = HERE.parents[2]
D = ROOT / "data/processed/H131-antagonism-off-one-readout"
OUT = D / "synthetic"
WORLDS = ["W0", "W1", "W2", "W3_120", "W3_300", "W4_3", "W4_6", "W5_300", "W6", "WON2"]


def skeleton():
    rep = pl.read_parquet(D / "replies.parquet").drop("y", "p_disagree", "s2_soft")
    rep = rep.with_columns(pl.lit(0, dtype=pl.Int8).alias("y"))   # placeholder; real flags are never loaded here
    reads = pl.read_parquet(D / "reads.parquet")
    return rep, reads


def rules(g, y, rng, Bp=500):
    d, gs, go = L.g12_did(g, y)
    _, null, p = L.g12_perm(g, rng, B=Bp, y=y)
    bs = L.cluster_boot(g, lambda idx: L.did_idx(g, idx, y), rng, B=300)
    lo, hi = np.percentile(bs[:, 1], [2.5, 97.5])
    p1 = bool(d > 0 and p < 0.05 and lo <= 0 <= hi and abs(gs) < 0.5 * abs(go))
    out = dict(delta=d, g_set=gs, g_open=go, p_perm=p, gset_lo=lo, gset_hi=hi, P1=p1)
    if g.period == "12":
        kt = L.kernel_tests(g, rng, B=Bp, y=y)
        n2 = bool(kt["d_k1_k2_lo"] <= 0 <= kt["d_k1_k2_hi"] and kt["p_open_gt_k1"] < 0.05)
        n2_fail = bool(kt["r_k1"] >= kt["r_open"])
        so = L.switch_on_tests(g, rng, y=y)
        n3 = bool(so["d_on_lo"] <= 0 or so["d_on"] >= 0) if np.isfinite(so["d_on_lo"]) else False
        n3 = bool(not (so["d_on_hi"] < 0))
        out.update(N2=n2, N2_fail=n2_fail, N3=n3, d_k1_k2=kt["d_k1_k2"], p_open_gt_k1=kt["p_open_gt_k1"],
                   d_on=so["d_on"], d_on_hi=so["d_on_hi"])
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--R", type=int, default=200)
    a = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    rep, reads = skeleton()
    g12 = L.G12(rep, reads, "y", "12")
    g26 = L.G12(rep, reads, "y", "26")
    # structural: replies whose read-gated and clock-gated prize state differ
    o_read = g12.open
    o_clock = g12.tB < g12.tv
    summ = {"g12_n": int(len(g12.y)), "g12_read_vs_clock_disagree": int(np.sum(o_read != o_clock)),
            "g26_read_vs_clock_disagree": int(np.sum(g26.open != (g26.tB < g26.tv)))}
    rows = []
    rng = np.random.default_rng(20261004)
    for w in WORLDS:
        for r in range(a.R):
            y = L.simulate_g12(g12, w, rng)
            rows.append(dict(period="12", world=w, rep=r, **rules(g12, y, rng)))
    pl.DataFrame(rows).write_parquet(OUT / "g12.parquet")
    rows26 = []
    for w in ("W0", "W1", "W6"):
        for r in range(a.R):
            y = L.simulate_g12(g26, w, rng)
            rows26.append(dict(period="26", world=w, rep=r, **rules(g26, y, rng)))
    pl.DataFrame(rows26).write_parquet(OUT / "g26.parquet")
    df = pl.DataFrame(rows)
    agg = df.group_by("world").agg(pl.col("P1").mean(), pl.col("N2").mean(), pl.col("N2_fail").mean(), pl.col("N3").mean(),
                                   pl.col("delta").median(), pl.col("d_k1_k2").median()).sort("world")
    agg26 = pl.DataFrame(rows26).group_by("world").agg(pl.col("P1").mean(), pl.col("delta").median()).sort("world")
    summ["g12"] = agg.to_dicts()
    summ["g26"] = agg26.to_dicts()
    (OUT / "summary.json").write_text(json.dumps(summ, indent=1, default=float))
    print(json.dumps(summ, indent=1, default=float))


if __name__ == "__main__":
    main()
