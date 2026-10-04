"""H131 round-1 run on real data (after the synthetic and Amendment A1).

G12: read-gated settlement DiD (P1; flag and soft outcomes), in-flight partition (N1), read-out relaxation kernel (N2:
first post-read rival reply vs later), switch-on kernel (N3). G26: DiD (P1) and the in-flight count (N4).
Output: data/processed/H131-antagonism-off-one-readout/results/results.json
Usage: uv run python hypotheses/H131-antagonism-off-one-readout/analysis/run.py
"""
from __future__ import annotations

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
RES = D / "results"
B_PERM = 5000


def did_block(g, rng, y=None, label="y"):
    y = g.y if y is None else y
    d, gs, go = L.g12_did(g, y)
    _, null, p = L.g12_perm(g, rng, B=B_PERM, y=y)
    bs = L.cluster_boot(g, lambda idx: L.did_idx(g, idx, y), rng, B=1000)
    ci = lambda col: [float(x) for x in np.percentile(bs[:, col], [2.5, 97.5])]  # noqa: E731
    p1 = bool(d > 0 and p < 0.05 and ci(1)[0] <= 0 <= ci(1)[1] and abs(gs) < 0.5 * abs(go))
    # descriptive cell rates
    riv, mate = g.R == 1, g.R == 0
    op, st = g.open, ~g.open
    m = lambda s: float(y[s].mean()) if s.sum() else None  # noqa: E731
    return dict(outcome=label, delta=d, delta_ci=ci(0), g_set=gs, g_set_ci=ci(1), g_open=go, g_open_ci=ci(2),
                p_perm=p, P1=p1, rate_riv_open=m(riv & op), rate_mate_open=m(mate & op), rate_riv_set=m(riv & st),
                rate_mate_set=m(mate & st), n_riv_open=int((riv & op).sum()), n_mate_open=int((mate & op).sum()),
                n_riv_set=int((riv & st).sum()), n_mate_set=int((mate & st).sum()))


def main():
    RES.mkdir(parents=True, exist_ok=True)
    rep = pl.read_parquet(D / "replies.parquet")
    reads = pl.read_parquet(D / "reads.parquet")
    rng = np.random.default_rng(131)
    out = {}
    for per in ("12", "26"):
        g = L.G12(rep, reads, "y", per)
        gs = L.G12(rep, reads, "p_disagree", per)
        r = dict(n=int(len(g.y)), n_flags=int(g.y.sum()))
        r["did_flag"] = did_block(g, rng, label="disagree_validated_agent")
        r["did_soft"] = did_block(gs, rng, label="p_disagree")
        riv_after = (g.R == 1) & (g.tB >= g.tv)
        r["inflight_rival"] = int(np.sum(riv_after & ~g.read))
        r["inflight_all"] = int(np.sum((g.tB >= g.tv) & ~g.read))
        r["N1"] = "untestable" if r["inflight_rival"] < 10 else "testable"
        if per == "12":
            kt = L.kernel_tests(g, rng, B=B_PERM)
            n2_pass = bool(kt["d_k1_k2_lo"] <= 0 <= kt["d_k1_k2_hi"] and kt["p_open_gt_k1"] < 0.05)
            n2_fail = bool(kt["r_k1"] >= kt["r_open"])
            kt["N2"] = "supported" if n2_pass else ("failed" if n2_fail else "inconclusive")
            r["kernel_flag"] = kt
            ks = L.kernel_tests(gs, rng, B=B_PERM)
            r["kernel_soft"] = ks
            so = L.switch_on_tests(g, rng)
            so["N3"] = ("supported" if not (so["d_on_hi"] < 0) else "failed")
            r["switch_on_flag"] = so
            r["switch_on_soft"] = L.switch_on_tests(gs, rng)
            dly = reads.filter(pl.col("goal_no") == 12)
            r["read_delay_s"] = dict(median=float(dly["read_delay_s"].median()), max=float(dly["read_delay_s"].max()),
                                     q90=float(dly["read_delay_s"].quantile(0.9)))
        out[per] = r
    (RES / "results.json").write_text(json.dumps(out, indent=1, default=float))
    print(json.dumps(out, indent=1, default=float))


if __name__ == "__main__":
    main()
