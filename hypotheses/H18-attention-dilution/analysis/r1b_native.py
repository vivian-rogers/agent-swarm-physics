"""H18 round-1b native tests (predictions written before this run in the period folders):

  uv run python hypotheses/H18-attention-dilution/analysis/r1b_native.py

Data: the round-1b ledger scheme (data/processed/H18-attention-dilution/r1b/G<NN>/, scheme/build_ledger.py).
1. NE42 A-B-A (#39 -> #40 -> #41), merged agents (not GPT-5): per side k-bar, per-pair uptake p-bar, S per talk, beta;
   N2c = one joint fit over the three sides with agent x day propensities: the #40-vs-flanks contrast of the mean
   log-propensity under M_const (no k) vs M_pow (k in the model), day bootstrap.
2. G51 N sweep: per `period_units` segment (51a-51l, non-holdout), p-bar, B-hat (senders responded to per talk turn),
   mean room size, beta (M_pow) with a day bootstrap; Spearman across segments.
3. NE03 (#10a vs #10b): per-pair uptake by the sender's newest-message rank (<= 3, > 10), beta per side.
Responses: resp_reply (reply parent among the sender's pending messages; primary) and resp (mention; secondary).
Writes data/processed/H18-attention-dilution/r1b/native.json.
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "2")

import json
import sys
from pathlib import Path

import numpy as np
import polars as pl
from scipy.stats import spearmanr

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from h18lib import Units, fit  # noqa: E402

ROOT = HERE.parents[2]
R1B = ROOT / "data/processed/H18-attention-dilution/r1b"
SH = ROOT / "data/processed/shared"


def load(gp, resp):
    t = pl.read_parquet(R1B / gp / "talks.parquet")
    p = pl.read_parquet(R1B / gp / "pending.parquet")
    if resp != "resp":
        p = p.with_columns(pl.col(resp).alias("resp"))
    return t, p


def summ(v):
    v = np.asarray([x for x in v if np.isfinite(x)], float)
    return [float(np.quantile(v, 0.025)), float(np.quantile(v, 0.975))] if len(v) > 5 else None


# ------------------------------------------------------------------------------------------ NE42
def ne42(resp, rng, B=200):
    ros = pl.read_parquet(SH / "roster.parquet")
    gpt5 = int(ros.filter(pl.col("name") == "GPT-5")["agent"][0])
    T, P = {}, {}
    off = 0
    for gp in ("G39", "G40", "G41"):
        t, p = load(gp, resp)
        t = t.with_columns((pl.col("talk_id") + off).alias("talk_id"), pl.lit(gp).alias("side"))
        p = p.with_columns((pl.col("talk_id") + off).alias("talk_id"))
        off += 10 ** 6
        T[gp], P[gp] = t, p
    merged = sorted(set.intersection(*[set(T[g]["agent"].unique().to_list()) for g in T]) - {gpt5})
    out = {"merged_agents": merged, "sides": {}}
    for gp in T:
        t = T[gp].filter(pl.col("agent").is_in(merged))
        U = Units(t, P[gp], "talk_id")
        u = U.df
        S = u.group_by("talk_id").agg(pl.col("r").sum().alias("S"))
        tk = t.filter(pl.col("k") >= 1)
        out["sides"][gp] = {"kbar": float(tk["k"].mean()), "pbar": float(u["r"].cast(pl.Float64).mean()),
                            "Sbar": float(S["S"].cast(pl.Float64).mean()), "beta": fit("pow", U)["params"]["beta"],
                            "n_units": U.n, "nroom": float(tk["n_room"].mean())}
    s = out["sides"]
    out["k_ratio_40_over"] = {g: s["G40"]["kbar"] / s[g]["kbar"] for g in ("G39", "G41")}
    out["p_ratio_40_over"] = {g: s["G40"]["pbar"] / s[g]["pbar"] for g in ("G39", "G41")}
    # day bootstrap of p-bar ratios
    for g in ("G39", "G41"):
        ua = Units(T[g].filter(pl.col("agent").is_in(merged)), P[g], "talk_id").df
        ub = Units(T["G40"].filter(pl.col("agent").is_in(merged)), P["G40"], "talk_id").df
        da = ua.group_by("pt_date").agg(pl.col("r").cast(pl.Float64).sum().alias("rs"), pl.len().alias("n"))
        db = ub.group_by("pt_date").agg(pl.col("r").cast(pl.Float64).sum().alias("rs"), pl.len().alias("n"))
        bs = []
        for _ in range(2000):
            ia = rng.integers(da.height, size=da.height); ib = rng.integers(db.height, size=db.height)
            bs.append((db["rs"].to_numpy()[ib].sum() / db["n"].to_numpy()[ib].sum()) /
                      (da["rs"].to_numpy()[ia].sum() / da["n"].to_numpy()[ia].sum()))
        out[f"p_ratio_40_over_{g}_ci"] = summ(bs)
    # N2c: joint fit, side contrast of log propensities with and without k
    t_all = pl.concat([T[g].filter(pl.col("agent").is_in(merged)) for g in T], how="diagonal_relaxed")
    p_all = pl.concat([P[g] for g in P], how="diagonal_relaxed")
    side_of_day = dict(zip(t_all["pt_date"].to_list(), t_all["side"].to_list()))
    U = Units(t_all, p_all, "talk_id")

    def contrast(Ux, model):
        f = fit(model, Ux)
        u = f["u"]
        day = (Ux.ckeys[:len(u)] % 10000).astype(int)
        sides = np.array([side_of_day[Ux.days[d]] for d in day])
        w = np.bincount(Ux.c, minlength=len(u)).astype(float)
        m = {g: float(np.average(u[sides == g], weights=w[sides == g])) for g in ("G39", "G40", "G41") if (sides == g).any()}
        return m["G40"] - 0.5 * (m["G39"] + m["G41"]), m
    c0, m0 = contrast(U, "const")
    c1, m1 = contrast(U, "pow")
    out["N2c"] = {"contrast_const": c0, "contrast_pow": c1, "shrink": (1 - c1 / c0) if c0 else None,
                  "side_means_const": m0, "side_means_pow": m1}
    # simple day bootstrap of the contrasts (re-fit on resampled days, sides kept by day label)
    days = np.array(U.days)
    dsides = np.array([side_of_day[d] for d in days])
    bc0, bc1 = [], []
    for _ in range(B):
        pick = np.concatenate([rng.choice(np.where(dsides == g)[0], size=(dsides == g).sum()) for g in ("G39", "G40", "G41")])
        keep_days = set(days[np.unique(pick)])
        Us = U.subset(np.isin(U.days[U.day], list(keep_days)))
        try:
            bc0.append(contrast(Us, "const")[0]); bc1.append(contrast(Us, "pow")[0])
        except Exception:
            pass
    out["N2c"]["contrast_const_ci"] = summ(bc0)
    out["N2c"]["contrast_pow_ci"] = summ(bc1)
    out["N2c"]["note"] = "bootstrap = day subsampling within side (unique days of a with-replacement draw)"
    out["verdict_inputs"] = {"N2a": all(v >= 1.3 for v in out["k_ratio_40_over"].values()),
                             "N2b": all(v < 1 for v in out["p_ratio_40_over"].values()),
                             "N2c": (out["N2c"]["shrink"] or 0) >= 0.5}
    return out


# ------------------------------------------------------------------------------------------ G51 N sweep
def nsweep(resp, rng, B=30):
    pu = pl.read_parquet(SH / "period_units.parquet").filter((pl.col("goal_no") == 51) & ~pl.col("holdout")).sort("seq")
    t, p = load("G51", resp)
    U = Units(t, p, "talk_id")
    tl = U.df.group_by("talk_id").agg(pl.col("r").sum().alias("S"), pl.col("pt_date").first())
    nr = t.select("talk_id", "n_room", "k")
    tl = tl.join(nr, on="talk_id")
    rows = []
    for r in pu.iter_rows(named=True):
        days = [d for d in r["days"]]
        m = np.isin(U.days[U.day], days)
        if m.sum() < 500:
            rows.append({"unit": r["unit_id"], "days": days, "n_units": int(m.sum()), "beta": None})
            continue
        Us = U.subset(m)
        fp = fit("pow", Us)
        bs = []
        if len(days) >= 2:
            for _ in range(B):
                Ub = Us.resample_days(rng)
                if Ub.r.sum() >= 5:
                    bs.append(fit("pow", Ub, start=[fp["params"]["g"], fp["params"]["beta"]])["params"]["beta"])
        ts = tl.filter(pl.col("pt_date").is_in(days))
        rows.append({"unit": r["unit_id"], "days": [days[0], days[-1], len(days)], "n_units": int(Us.n),
                     "pbar": float(Us.r.mean()), "Bhat": float(ts["S"].cast(pl.Float64).mean()),
                     "nroom": float(ts["n_room"].mean()), "kbar": float(ts.filter(pl.col("k") >= 1)["k"].mean()),
                     "beta": fp["params"]["beta"], "beta_ci": summ(bs), "n_agents": int(r["n_agents"])})
    ok = [x for x in rows if x.get("beta") is not None]
    nroom = [x["nroom"] for x in ok]
    res = {"segments": rows,
           "rho_pbar_nroom": float(spearmanr(nroom, [x["pbar"] for x in ok]).statistic) if len(ok) >= 4 else None,
           "rho_Bhat_nroom": float(spearmanr(nroom, [x["Bhat"] for x in ok]).statistic) if len(ok) >= 4 else None,
           "cv_pbar": float(np.std([x["pbar"] for x in ok]) / np.mean([x["pbar"] for x in ok])) if ok else None,
           "cv_Bhat": float(np.std([x["Bhat"] for x in ok]) / np.mean([x["Bhat"] for x in ok])) if ok else None}
    big = [x for x in ok if x["n_units"] >= 1000]
    res["beta_pos_share"] = (sum(1 for x in big if x["beta_ci"] and x["beta_ci"][0] > 0) / len(big)) if big else None
    res["n_big"] = len(big)
    return res


# ------------------------------------------------------------------------------------------ NE03
def ne03(resp, rng, B=300):
    t, p = load("G10", resp)
    U = Units(t, p, "talk_id")
    u = U.df.with_columns(pl.when(pl.col("pt_date") < "2025-08-20").then(pl.lit("10a")).otherwise(pl.lit("10b")).alias("side"))
    out = {}
    for s_ in ("10a", "10b"):
        us_ = u.filter(pl.col("side") == s_)
        row = {"n_units": us_.height, "rate": float(us_["r"].cast(pl.Float64).mean())}
        for lab, cond in (("rmin_le3", pl.col("rmin") <= 3), ("rmin_gt10", pl.col("rmin") > 10)):
            x = us_.filter(cond)["r"].cast(pl.Float64).to_numpy()
            row[lab] = {"n": int(len(x)), "rate": float(x.mean()) if len(x) else None,
                        "ci": summ([x[rng.integers(len(x), size=len(x))].mean() for _ in range(B)]) if len(x) >= 10 else None}
        m = np.isin(U.days[U.day], us_["pt_date"].unique().to_list())
        Us = U.subset(m)
        try:
            row["beta"] = fit("pow", Us)["params"]["beta"]
        except Exception:
            row["beta"] = None
        row["kq90"] = float(t.filter(pl.col("pt_date").is_in(us_["pt_date"].unique().to_list()) & (pl.col("k") >= 1))["k"].quantile(0.9))
        out[s_] = row
    a, b = out["10a"], out["10b"]
    out["N3a_gt10_ratio_b_over_a"] = (b["rmin_gt10"]["rate"] / a["rmin_gt10"]["rate"]) if (a["rmin_gt10"]["rate"] and b["rmin_gt10"]["rate"] is not None) else None
    out["N3a_le3_ratio_b_over_a"] = (b["rmin_le3"]["rate"] / a["rmin_le3"]["rate"]) if (a["rmin_le3"]["rate"] and b["rmin_le3"]["rate"] is not None) else None
    out["N3b_beta_diff"] = (b["beta"] - a["beta"]) if (a.get("beta") is not None and b.get("beta") is not None) else None
    out["underpowered"] = min(a["rmin_gt10"]["n"], b["rmin_gt10"]["n"]) < 30
    return out


def main():
    rng = np.random.default_rng(18)
    res = {}
    for resp in ("resp_reply", "resp"):
        res[resp] = {"NE42": ne42(resp, rng), "G51_Nsweep": nsweep(resp, rng), "NE03": ne03(resp, rng)}
        print(resp, json.dumps({"NE42": res[resp]["NE42"]["verdict_inputs"], "N2c": res[resp]["NE42"]["N2c"],
                                "p_ratio": res[resp]["NE42"]["p_ratio_40_over"], "k_ratio": res[resp]["NE42"]["k_ratio_40_over"],
                                "nsweep": {k: v for k, v in res[resp]["G51_Nsweep"].items() if k != "segments"},
                                "ne03": {k: v for k, v in res[resp]["NE03"].items() if k not in ("10a", "10b")}}, default=float, indent=0), flush=True)
    (R1B / "native.json").write_text(json.dumps(res, indent=1, default=float))


if __name__ == "__main__":
    main()
