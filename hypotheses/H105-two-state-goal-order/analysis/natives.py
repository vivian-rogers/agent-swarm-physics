"""H105 natives (predictions in the folder READMEs, written before running):
  N1 G51   own-goal occupancy under private fields: no collective switching (per unit 51a-51l)
  N2 G12   the DQ6 debate-phase schedule as a scheduled field in #12a
  N3 NE38  a field on one spin: Opus 5's own occupancy vs the others' occupancy along its new goal (DiD)
Writes data/processed/H105-two-state-goal-order/natives/{G51,G12,NE38}.json.
"""
from __future__ import annotations

import datetime as dt
import json
import sys
from pathlib import Path

import numpy as np
import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h105lib as L  # noqa: E402

OUT = L.DATA / "natives"
OPUS5 = 40
NE38_T = dt.datetime(2026, 7, 29, 16, 51, tzinfo=dt.timezone.utc)
ROOT = L.ROOT


def own_onflags(st, pr, thr, model, variant="white", q=95, exclude=()):
    """On-goal flag of each statement along its author's own goal direction (nan-free; False if no direction)."""
    ag = st["agent"].to_numpy()
    on = np.zeros(st.height, bool)
    has = np.zeros(st.height, bool)
    for a in np.unique(ag):
        key = f"agent_{a}|{model}|{variant}"
        if key not in pr.files or a in exclude:
            continue
        m = ag == a
        on[m] = pr[key][m] > L.threshold(thr, f"agent_{a}", model, variant, q)
        has[m] = True
    return on, has


def seg_g(S, days, n_boot=500, seed=0):
    s = L.seg_stats(S)
    rng = np.random.default_rng(seed)
    bs = []
    for _ in range(n_boot):
        ix = L.block_indices(days, rng)
        bs.append(L.seg_stats(S[ix])["R"])
    bs = np.array(bs, float)
    return dict(p=s["p"], R=s["R"], g=s["g"], R_lo=float(np.nanpercentile(bs, 5)), R_hi=float(np.nanpercentile(bs, 95)),
                N=int(S.shape[1]), T=int(S.shape[0]))


def g51(model="bge_small"):
    st, pr, thr = L.load("G51")
    # Opus 5's first goal (game dev, 07-24..07-29) has no vector: drop its statements before NE38
    keep = ~((st["agent"] == OPUS5) & (st["t"] < NE38_T)).to_numpy()
    st = st.filter(pl.Series(keep))
    pr = {k: pr[k][keep] for k in pr.files}
    pr["files"] = list(pr)

    class P(dict):
        files = list(pr)
    prd = P(pr)
    on_own, has = own_onflags(st, prd, thr, model)
    on_sh = prd[f"shared|{model}|white"] > L.threshold(thr, "shared", model, "white", 95)
    res = []
    for unit in sorted(st["seg"].unique().to_list()):
        m = (st["seg"] == unit).to_numpy() & has
        if m.sum() < 50:
            continue
        sub = st.filter(pl.Series(m)).with_columns(pl.lit("X").alias("seg"))
        To = L.spin_tables(sub, on_own[m], "X"); Ts = L.spin_tables(sub, on_sh[m], "X")
        ag = [a for j, a in enumerate(To["agents"]) if np.isfinite(To["S"][:, j]).sum() >= L.MIN_WINDOWS]
        if len(ag) < 8:
            continue
        To = L.restrict(To, ag); Ts = L.restrict(Ts, ag)
        if To["S"].shape[0] < 8:
            continue
        o = seg_g(To["S"], To["days"], seed=1); s = seg_g(Ts["S"], Ts["days"], seed=2)
        res.append(dict(unit=unit, N=len(ag), T=o["T"], p_own=o["p"], R_own=o["R"], R_own_lo=o["R_lo"], R_own_hi=o["R_hi"],
                        g_own=o["g"], p_shared=s["p"], R_shared=s["R"], g_shared=s["g"]))
    df = pl.DataFrame(res)
    med_own = float(df["g_own"].median()); med_sh = float(df["g_shared"].median())
    ci1 = float((df["R_own_lo"] <= 1).mean())
    return dict(model=model, units=res, median_g_own=med_own, median_g_shared=med_sh, frac_units_R_ci_contains1=ci1,
                frac_units_g_own_below_shared=float((df["g_own"] < df["g_shared"]).mean()),
                prediction_N1=bool(med_own < 0.2 and med_own < med_sh))


def g12(model="bge_small"):
    st, pr, thr = L.load("P11_12")
    y = pr[f"goal|{model}|white"]; on = y > L.threshold(thr, "goal", model, "white", 95)
    F = L.spin_tables(st, on, "F"); A = L.spin_tables(st, on, "A")
    ag = L.common_agents(F, A); F = L.restrict(F, ag); A = L.restrict(A, ag)
    core = L.pair_core(F["S"], A["S"])
    gt = pl.read_parquet(ROOT / "data/processed/shared/ground_truth_labels.parquet").filter(
        (pl.col("goal_no") == 12) & (pl.col("label_kind") == "phase") & pl.col("preferred") & ~pl.col("holdout"))
    # window times: win30 index within the day -> need the day's window start; recover from statement times
    w = st.filter(pl.col("seg") == "A").group_by("pt_date", "win30").agg(pl.col("t").min().alias("t0"), pl.col("t").max().alias("t1"))
    wmap = {(r["pt_date"], r["win30"]): (r["t0"], r["t1"]) for r in w.iter_rows(named=True)}
    deb = gt.filter(pl.col("value") == "deb").select("t_valid_from", "t_valid_to").rows()
    # A's window order is (pt_date, win30) sorted; rebuild it as spin_tables does
    g = st.filter(pl.col("seg") == "A").group_by("pt_date", "win30").agg(pl.len()).sort("pt_date", "win30")
    keys = [(r["pt_date"], r["win30"]) for r in g.iter_rows(named=True)]
    Afull = L.spin_tables(st, on, "A")
    keep = np.isfinite(L.restrict(Afull, ag)["S"]).sum(1) >= 0  # same filtering as restrict
    Ar = L.restrict(Afull, ag)
    # map restricted rows back to keys
    full_rows = L.restrict(dict(Afull, days=np.array([f"{k[0]}|{k[1]}" for k in keys])), ag)["days"]
    share = []
    for kk in full_rows:
        d, wi = kk.split("|"); t0, t1 = wmap[(d, int(wi))]
        span = max((t1 - t0).total_seconds(), 60.0)
        ov = sum(max(0.0, (min(t1, b) - max(t0, a)).total_seconds()) for a, b in deb)
        share.append(min(ov / span, 1.0))
    share = np.array(share)
    s = L.seg_stats(Ar["S"])
    pres = np.isfinite(Ar["S"]); p_t = np.nanmean(Ar["S"], 1)
    mu_t = np.nanmean(np.where(pres, s["p_i"][None, :], np.nan), 1)
    dev = p_t - mu_t
    X = np.c_[np.ones_like(share), share]
    beta, *_ = np.linalg.lstsq(X, dev, rcond=None)
    resid = dev - X @ beta
    V_obs = float(np.mean(dev ** 2)); V_res = float(np.mean((resid - resid.mean()) ** 2) + resid.mean() ** 2)
    excess = V_obs - core["VA_pred"]
    removed = (V_obs - V_res) / excess if excess > 0 else np.nan
    return dict(model=model, V_obs=V_obs, V_pred=core["VA_pred"], V_resid=V_res, excess=excess, frac_excess_removed=float(removed),
                phase_coef=float(beta[1]), mean_phase_share=float(share.mean()), n_windows=int(len(share)),
                prediction_N2=(bool(removed >= 0.3) if np.isfinite(removed) else None))


def ne38(model="bge_small", n_boot=1000):
    st, pr, thr = L.load("NE38")
    dirs = sorted({k.split("|")[0] for k in pr.files if k.startswith("agent_")})
    th = {d: L.threshold(thr, d, model, "white", 95) for d in dirs}
    ag = st["agent"].to_numpy(); seg = st["seg"].to_numpy()

    def occ(direction, who_mask):
        on = pr[f"{direction}|{model}|white"] > th[direction]
        out = {}
        for s in ("pre", "post"):
            m = who_mask & (seg == s)
            sub = st.filter(pl.Series(m))
            T = L.spin_tables(sub, on[m], s)
            out[s] = T
        return out

    d40 = f"agent_{OPUS5}"
    own = occ(d40, ag == OPUS5)
    p_own = {s: float(np.nanmean(own[s]["S"])) for s in own}
    oth = occ(d40, (ag != OPUS5))
    p_oth = {s: float(np.nanmean(oth[s]["S"])) for s in oth}
    d_target = p_oth["post"] - p_oth["pre"]
    plac = []
    for d in dirs:
        a = int(d.split("_")[1])
        if a == OPUS5:
            continue
        o = occ(d, (ag != OPUS5) & (ag != a))
        plac.append(float(np.nanmean(o["post"]["S"]) - np.nanmean(o["pre"]["S"])))
    plac = np.array(plac)
    did = d_target - float(np.nanmean(plac))
    # bootstrap over windows (others) for the target-direction change
    rng = np.random.default_rng(4)
    bs = []
    for _ in range(n_boot):
        vals = []
        for s in ("pre", "post"):
            S = oth[s]["S"]; ix = L.block_indices(oth[s]["days"], rng)
            vals.append(np.nanmean(S[ix]))
        bs.append(vals[1] - vals[0] - np.nanmean(plac))
    lo, hi = float(np.nanpercentile(bs, 5)), float(np.nanpercentile(bs, 95))
    return dict(model=model, opus5_pre=p_own["pre"], opus5_post=p_own["post"], opus5_rise=p_own["post"] - p_own["pre"],
                others_pre=p_oth["pre"], others_post=p_oth["post"], placebo_change_mean=float(np.nanmean(plac)),
                placebo_change_sd=float(np.nanstd(plac)), did=did, did_lo=lo, did_hi=hi,
                prediction_N3=bool((p_own["post"] - p_own["pre"]) > 0.3 and abs(did) < 0.02))


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for name, fn in (("G51", g51), ("G12", g12), ("NE38", ne38)):
        res = {m: fn(m) for m in ("bge_small", "gte_modernbert")}
        (OUT / f"{name}.json").write_text(json.dumps(res, indent=1, default=float))
        print(name, json.dumps(res, default=float)[:1200])


if __name__ == "__main__":
    main()
