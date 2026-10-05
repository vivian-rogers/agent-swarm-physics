"""H46 round 2 post-hoc diagnostics (labelled post hoc in the card; written after the pre-registered round-2 results).

PH-R2a  shape of the context-held state: dC(l) for l = 1..8, and dC(1) split by the earlier message's position j in its
        segment (OU from zero predicts dC growing with j; a reset-and-hold offset predicts it flat in j and in l).
        Plus the synthetic SJ world (segment offset) through the same estimator, as the reference shape.
PH-R3a  which function words carry the goal-switch displacement excess (as round-1 PH2).
PH-R3b  per-lab NE41 forced T for tc and fw (scaled).
Output: data/processed/H46-style-conserved-charge/r2/posthoc.json
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import numpy as np
import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h46lib as L  # noqa: E402
import r2lib as R  # noqa: E402
import r2_synthetic as S  # noqa: E402


def dC_by_j(Xc, lp):
    out = {}
    for name, cond in (("j=1", pl.col("pos_elig") == 1), ("j=2", pl.col("pos_elig") == 2),
                       ("j=3-5", pl.col("pos_elig").is_between(3, 5)), ("j>=6", pl.col("pos_elig") >= 6)):
        sub = lp.filter((pl.col("lag") == 1) & ((pl.col("label") == "forced") | cond))
        cp = R.cross_products(Xc, sub, n_boot=300)
        out[name] = {"dC": cp["lags"][1]["dC"], "ci": cp["lags"][1]["dC_ci"], "n_within": cp["lags"][1]["n_within"]}
    return out


def main():
    m = R.load()
    words = R.fw_words(m)
    V = R.variants(m, words)
    sel = m["regime"].to_numpy() == "III"
    m3 = m.filter(pl.Series(sel))
    lp8 = R.lag_pairs(m3, lmax=8)
    res = {}
    Xc = R.unit_center(V["gp"][sel], m3)
    cp8 = R.cross_products(Xc, lp8, n_boot=300)
    res["PH_R2a"] = {"dC_by_lag": {l: (v["dC"], v["dC_ci"], v["n_across"]) for l, v in cp8["lags"].items()},
                     "dC1_by_j": dC_by_j(Xc, lp8),
                     "dC_share_of_trace": cp8["lags"][1]["dC"] / float(V["gp"][sel].var(0).sum())}
    # reference: SJ world (segment offset, 4% of the per-message trace) and S1b (OU phi 0.9) through the same code
    P_ = S.pools(m, L.style_matrix(m, "tc"))
    rng = np.random.default_rng(5)
    segkey = (m3["agent"].cast(pl.Int64) * 100000 + m3["seg"].cast(pl.Int64)).to_numpy()
    _, sinv = np.unique(segkey, return_inverse=True)
    ref = {}
    for scen in ("SJ", "S1b"):
        X = S.base_draw(m, P_, rng)[sel]
        if scen == "SJ":
            X += (rng.standard_normal((sinv.max() + 1, X.shape[1])) * np.sqrt(0.04 * P_[2]))[sinv]
        else:
            X += S.plant_excursion(m3, P_[2], "S1b", rng)
        Xs = R.unit_center(X, m3)
        c = R.cross_products(Xs, lp8, n_boot=50)
        g = R.growth_fit(R.growth(Xs, m3), n_boot=50)
        ref[scen] = {"dC_by_lag": {l: v["dC"] for l, v in c["lags"].items()}, "dbar": g["dbar"],
                     "dC1_by_j": {k: v["dC"] for k, v in dC_by_j(Xs, lp8).items()}}
    res["PH_R2a"]["synthetic_reference"] = ref
    print(json.dumps(res["PH_R2a"], indent=0, default=float)[:3000], flush=True)
    # PH-R3a: function-word excess at goal switches
    keep = m["n_tok"].to_numpy() >= R.MIN_TOK
    mf = m.filter(pl.Series(keep))
    F = V["fw"][keep]
    dt_ = L.day_table(mf, {"fw": F})
    rows = pl.read_parquet(R.R2 / "r3_rows.parquet").filter(pl.col("cls") == "goal")
    look = {(r["agent"], r["pt_date"]): r["row"] for r in dt_.keys.iter_rows(named=True)}
    bi = np.array([look[(a, d)] for a, d in zip(rows["agent"].to_list(), rows["d_pre"].to_list())])
    bj = np.array([look[(a, d)] for a, d in zip(rows["agent"].to_list(), rows["d_post"].to_list())])
    pp = L.placebo_pairs(dt_)
    M = dt_.M["fw"]
    ex = ((M[bi] - M[bj]) ** 2).mean(0) - ((M[pp["i"].to_numpy()] - M[pp["j"].to_numpy()]) ** 2).mean(0)
    order = np.argsort(-ex)
    res["PH_R3a"] = {"top_words": [(words[q][2:], float(ex[q] / ex.sum())) for q in order[:10]],
                     "share_top10": float(ex[order[:10]].sum() / ex.sum())}
    print(res["PH_R3a"], flush=True)
    # PH-R3b: per-lab NE41 forced T (scaled)
    m3f = mf.filter(pl.col("regime") == "III")
    i3 = np.where(mf["regime"].to_numpy() == "III")[0]
    pr, i1, i2 = R.ne41_pairs(m3f)
    labg = dict(zip(m["agent"].to_list(), m["labg"].to_list()))
    lab_of = np.array([labg[a] for a in pr["agent"].to_list()])
    res["PH_R3b"] = {}
    for lg in ("Anthropic", "OpenAI", "Google", "DeepSeek", "other"):
        k = lab_of == lg
        if k.sum() < 200:
            continue
        prl = pr.filter(pl.Series(k))
        res["PH_R3b"][lg] = {c: R.ne41_test(prl, i1[k], i2[k], V[c][keep][i3], n_rand=5000)["forced"]
                             for c in ("gp", "fw")}
        res["PH_R3b"][lg] = {c: {kk: v[kk] for kk in ("T", "lo", "hi", "n", "n_clusters")} for c, v in res["PH_R3b"][lg].items()}
    print(res["PH_R3b"], flush=True)
    (R.R2 / "posthoc.json").write_text(json.dumps(res, indent=1, default=float))


if __name__ == "__main__":
    main()
