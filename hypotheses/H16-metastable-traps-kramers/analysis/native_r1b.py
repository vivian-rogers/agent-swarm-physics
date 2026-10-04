"""H16 round 1b native tests (layer 2; predictions on the card, "Round 1b", written before running).

N1  NE44 (pause default 12 h -> 5 min, 06-11): TS2r gate model before (G37-G44 pooled, period dummies) vs after
    (G51 07-06 -> 08-20): directed-kick x ln k interaction, declared durations, escape at k = 1.
N2  NE43 inside #51: B = 08-07 -> 08-20 (nudges on, bookends gone) vs C = 08-21 -> 09-02 (no nudges): aging on both
    sides; the C indicator in the gate logit.
N3  #27 long debugging traps: read from r1b/G27/results.json (TS3r, TS5, directed kicks on TS3r).
Reads the round-1b tables (scheme/build.py --r1b). Writes data/processed/H16-metastable-traps-kramers/r1b/native_r1b.json.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h16lib as L  # noqa: E402
import run_period as RP  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

R1B = L.OUT / "r1b"
PRE = ["G37", "G38", "G39", "G40", "G41", "G42", "G44"]
DIRECTED = ["n_A_men", "n_H_men", "n_N_tgt"]


def gates(period, d0=None, d1=None):
    g = RP.ts2_robust_view(pl.read_parquet(R1B / period / "ts2.parquet"))
    if d0:
        g = g.filter(pl.col("pt_date") >= d0)
    if d1:
        g = g.filter(pl.col("pt_date") <= d1)
    return g.with_columns(pl.lit(period).alias("period"))


def gate_fit(g, interaction=True, period_dummies=False, extra=None):
    g = g.filter((pl.col("outcome") != "censored") & pl.col("declared_s").is_not_null() & (pl.col("declared_s") > 0))
    y = (g["outcome"] != "repause").to_numpy().astype(int)
    lnk = np.log(g["k"].to_numpy().astype(float))
    lnd = np.log(g["declared_s"].to_numpy().astype(float))
    D = (np.sum([g[c].to_numpy() for c in DIRECTED], axis=0) > 0).astype(float)
    cols, names = [lnk, lnd, D], ["lnk", "lnd", "D"]
    if interaction:
        cols.append(D * lnk)
        names.append("D_x_lnk")
    if extra is not None:
        cols.append(extra(g))
        names.append("extra")
    if period_dummies:
        ps = sorted(g["period"].unique().to_list())
        for p in ps[1:]:
            cols.append((g["period"] == p).to_numpy().astype(float))
            names.append(f"per_{p}")
    X = np.stack(cols, 1)
    f = L.glm_fe(y, X, g["agent"].to_numpy(), "logit")
    out = {"n_gates": int(len(y)), "escapes": int(y.sum()), "repauses": int((y == 0).sum()), "n_directed": int(D.sum())}
    for i, nm in enumerate(names):
        if nm.startswith("per_"):
            continue
        b, se = float(f["beta"][i]), float(f["se"][i])
        out[nm] = {"beta": b, "se": se, "ci": [b - 1.96 * se, b + 1.96 * se]}
    # descriptive escape probabilities
    k = g["k"].to_numpy()
    out["p_escape_k1"] = float(y[k == 1].mean()) if (k == 1).any() else None
    out["p_escape_k1_n"] = int((k == 1).sum())
    out["p_escape_k1_directed"] = float(y[(k == 1) & (D > 0)].mean()) if ((k == 1) & (D > 0)).any() else None
    out["p_escape_k3plus_directed"] = float(y[(k >= 3) & (D > 0)].mean()) if ((k >= 3) & (D > 0)).any() else None
    out["p_escape_k3plus_undirected"] = float(y[(k >= 3) & (D == 0)].mean()) if ((k >= 3) & (D == 0)).any() else None
    return out


def n1_ne44():
    pre = pl.concat([gates(p) for p in PRE], how="diagonal_relaxed")
    post = gates("G51", d1="2026-08-20")
    res = {"pre_periods": PRE, "post": "G51 07-06 -> 08-20"}
    res["pre"] = gate_fit(pre, interaction=True, period_dummies=True)
    res["post"] = gate_fit(post, interaction=True)
    for tag, g in (("pre", pre), ("post", post)):
        d = g.filter(pl.col("declared_s").is_not_null() & (pl.col("declared_s") > 0))["declared_s"].to_numpy()
        res[f"{tag}_declared"] = {"n": int(len(d)), "median_s": float(np.median(d)) if len(d) else None,
                                  "q90_s": float(np.percentile(d, 90)) if len(d) else None,
                                  "null_or_zero": int(g.height - len(d)), "gates": g.height}
    a_pre = res["pre"].get("D_x_lnk", {}).get("ci", [np.nan, np.nan])
    a_post = res["post"].get("D_x_lnk", {}).get("ci", [np.nan, np.nan])
    res["a_holds"] = bool(a_pre[0] <= 0 <= a_pre[1] and a_post[1] < 0)
    mp, mq = res["pre_declared"]["median_s"], res["post_declared"]["median_s"]
    res["b_ratio_median_declared_pre_over_post"] = (mp / mq) if (mp and mq) else None
    res["b_holds"] = bool(res["b_ratio_median_declared_pre_over_post"] is not None and res["b_ratio_median_declared_pre_over_post"] >= 5)
    res["c_holds"] = bool((res["pre"]["p_escape_k1"] or 0) > (res["post"]["p_escape_k1"] or 1))
    return res


def n2_ne43(rng):
    folder = R1B / "G51"
    sides = {"B": ("2026-08-07", "2026-08-20"), "C": ("2026-08-21", "2026-09-02")}
    res = {}
    ts1r = pl.read_parquet(folder / "ts1r.parquet")
    ts2 = pl.read_parquet(folder / "ts2.parquet")
    for s, (a, b) in sides.items():
        cond = (pl.col("pt_date") >= a) & (pl.col("pt_date") <= b)
        d1 = RP.dwell_ts1(ts1r.filter(cond), rng, 100, "ts1r")
        d2 = RP.dwell_ts2(RP.ts2_robust_view(ts2.filter(cond)), rng, 100)
        res[s] = {"days": [a, b], "TS1r_deep": d1.get("deep"), "TS2r": {k: d2.get(k) for k in ("beta_lnk_agentFE", "se", "ci", "ci_wald", "n_gates", "verdict")},
                  "n_kicks_N_tgt": None}
    g = pl.concat([gates("G51", *sides["B"]), gates("G51", *sides["C"])], how="diagonal_relaxed")
    res["gate_C_indicator"] = gate_fit(g, interaction=False, extra=lambda gg: (gg["pt_date"] >= "2026-08-21").to_numpy().astype(float))
    kk = pl.read_parquet(folder / "kicks.parquet")
    for s, (a, b) in sides.items():
        lo = pl.lit(a).str.to_date().dt.epoch("s")
    res["a_holds"] = bool(all((res[s]["TS1r_deep"] or {}).get("beta_agentFE", 0) < -0.3 for s in sides)
                          and all((res[s]["TS2r"].get("beta_lnk_agentFE") or 0) < 0 for s in sides))
    c = res["gate_C_indicator"].get("extra", {})
    res["b_holds"] = bool(c and c["ci"][1] < 0)
    return res


def n3_g27():
    r = json.loads((R1B / "G27" / "results.json").read_text())
    a, c = r["a"], r["c"]
    out = {"TS3r_deep": a["TS3"].get("deep"), "TS5_deep": a["TS5"].get("deep"), "TS5_kicks": a["TS5"].get("kicks"),
           "TS3r_kicks": c.get("TS3"), "TS6_deep": a["TS6"].get("deep")}
    ages = []
    for k in ("TS3r_deep", "TS5_deep"):
        d = out[k] or {}
        if d.get("ok") and d["beta_agentFE"] < -0.3 and d["ci_wald"][1] < 0:
            ages.append(k)
    out["aging"] = ages
    out["holds_aging"] = bool(ages)
    k3 = out["TS3r_kicks"] or {}
    out["holds_no_break"] = bool(k3.get("ok") and (k3["directed_lnHR"] <= 0 or k3["directed_lnHR"] - 1.96 * k3["directed_se"] < 0))
    return out


def main():
    rng = np.random.default_rng(20261004)
    res = {"N1_NE44": n1_ne44(), "N2_NE43": n2_ne43(rng), "N3_G27": n3_g27()}
    L.jdump(res, R1B / "native_r1b.json")
    print(json.dumps(res, indent=1, default=float)[:8000])


if __name__ == "__main__":
    main()
