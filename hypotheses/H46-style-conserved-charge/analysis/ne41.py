"""H46 native test on NE41: does a forced context erasure move style, content, both or neither? (O4)

Consecutive eligible chat messages of one agent on one PT day (regime III); forced / voluntary pairs straddle one
consolidation; within pairs straddle none. Each crossing pair is ranked among within pairs of the same agent, unit
and time-gap bin (0.05 decades, Amendment 2); fallback: unit x gap bin. Distances: style ||x - x'||^2 (type-controlled, raw);
content 1 - cos (DQ5 style-residualized, raw whitened).
Outputs: data/processed/H46-style-conserved-charge/NE41/{ne41.json, ne41_pct.parquet}
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import numpy as np
import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h46lib as L  # noqa: E402

OUT = L.DATA / "NE41"


def run(dedup: bool, channels: list[str], msgs: pl.DataFrame, n_rand=20000):
    pr = pl.read_parquet(L.DATA / "ne41_pairs.parquet").filter(pl.col("dedup") == dedup)
    pr = pr.filter(pl.col("label") != "other")
    idx = {k: i for i, k in enumerate(msgs["msg"].to_list())}
    i1 = np.array([idx[k] for k in pr["msg"].to_list()])
    i2 = np.array([idx[k] for k in pr["msg2"].to_list()])
    mats = {"style": L.style_matrix(msgs, "tc"), "style_raw": L.style_matrix(msgs, "raw"),
            "content": L.content_matrix(msgs, "resid"), "content_white": L.content_matrix(msgs, "white")}
    lab = pr["label"].to_numpy()
    ag = pr["agent"].to_numpy()
    un = pr["unit2"].to_numpy()
    gap = np.maximum(pr["gap_s"].to_numpy().astype(float), 1.0)
    gb = np.floor(np.log10(gap) / L.GAP_BIN).astype(int)
    S1 = np.array([f"{a}|{u}|{g}" for a, u, g in zip(ag, un, gb)])
    S2 = np.array([f"{u}|{g}" for u, g in zip(un, gb)])
    out = {"n_pairs": {k: int((lab == k).sum()) for k in ("within", "forced", "voluntary")},
           "median_gap_s": {k: float(np.median(gap[lab == k])) for k in ("within", "forced", "voluntary")}}
    pct_cols = {}
    for ch in channels:
        X = mats[ch]
        if ch.startswith("style"):
            d = ((X[i1] - X[i2]) ** 2).sum(1)
        else:
            d = 1 - (X[i1] * X[i2]).sum(1)
        p, npl = L.pair_percentiles(lab, d, S1, S2)
        pct_cols[ch] = p
        res = {}
        for k in ("forced", "voluntary"):
            f = lab == k
            res[k] = L.mean_pct_test(p[f], npl[f], ag[f], n_rand=n_rand)
            # per unit
            res[k]["per_unit"] = {}
            for u in np.unique(un[f]):
                g = f & (un == u)
                ok = ~np.isnan(p[g])
                if ok.sum() >= 30:
                    res[k]["per_unit"][u] = {"T": float(np.nanmean(p[g])), "n": int(ok.sum())}
            # naive (gap-unmatched): percentile among all within pairs of the same agent
            nv = []
            for a in np.unique(ag[f]):
                wd = np.sort(d[(lab == "within") & (ag == a)])
                if len(wd) >= 5:
                    nv.append(np.searchsorted(wd, d[f & (ag == a)]) / len(wd))
            res[k]["T_naive_unmatched"] = float(np.concatenate(nv).mean()) if nv else np.nan
            # effect size: stratified mean difference / within SD
            res[k]["mean_d_cross"] = float(np.mean(d[f]))
        res["mean_d_within"] = float(np.mean(d[lab == "within"]))
        out[ch] = res
        print(dedup, ch, {k: (round(res[k]["T"], 4), round(res[k]["lo"], 4), round(res[k]["hi"], 4),
                             res[k]["p_rand"], round(res[k]["T_naive_unmatched"], 3)) for k in ("forced", "voluntary")},
              flush=True)
    return out, pr.select("agent", "unit2", "label", "gap_s").with_columns(
        *[pl.Series(f"pct_{k}", v.astype(np.float32)) for k, v in pct_cols.items()])


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    msgs = pl.read_parquet(L.DATA / "messages.parquet").filter(pl.col("main") & (pl.col("regime") == "III"))
    res = {}
    res["dedup"], tab = run(True, ["style", "style_raw", "content", "content_white"], msgs)
    res["all_messages"], _ = run(False, ["style", "content"], msgs, n_rand=5000)
    tab.write_parquet(OUT / "ne41_pct.parquet")
    (OUT / "ne41.json").write_text(json.dumps(res, indent=1, default=float))


if __name__ == "__main__":
    main()
