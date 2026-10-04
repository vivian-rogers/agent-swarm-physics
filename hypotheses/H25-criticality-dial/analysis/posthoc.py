"""H25 post hoc analyses (labelled; chosen AFTER seeing the exploratory results, not verdict-bearing).

PH1  Size scaling of the dial. Mean field writes VR - 1 = (N - 1) rho_bar, rho_bar the mean pairwise correlation of the
     drive-removed spins. Three readings predict different exponents alpha in rho_bar ~ (N - 1)^(-alpha):
       Curie-Weiss with J0/N coupling (size-independent loop gain): alpha = 1, g flat in N;
       attention dilution (H18: per-pair coupling ~ N^-0.6):        alpha = 0.6;
       a common field, or constant per-pair coupling:                alpha = 0, g grows with N.
     Fit alpha per channel on period-level medians (bootstrap over periods), and within #51 across days (roster growth).
     LOPO comparison of the three fixed-alpha models for period-level g.
PH2  Heterogeneity (P5) with the uninflated bootstrap SEs (sensitivity to the x1.5 calibration).
PH3  Combined stall mask: auto stalls OR H38 scheduled-off minutes (activity, talk).
PH4  Edge trimming at agent level (H38's finding that regime-III co-activation is mostly agents starting and stopping
     together): each agent's minutes before its first and after its last logged event of the day carry no signal
     (set to the agent's block mean over its available minutes), on top of PH3's mask.
Output: data/processed/H25-criticality-dial/results/posthoc.json, posthoc_mask.parquet.
"""
from __future__ import annotations

import hashlib
import json
import sys
from multiprocessing import Pool
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h25common as C  # noqa: E402
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402
from scipy import stats  # noqa: E402

import dial as D  # noqa: E402
import explore as E  # noqa: E402

_G: dict = {}


def rho_bar(df):
    return df.with_columns(((pl.col("VR") - 1) / (pl.col("N") - 1)).alias("rho"))


def fit_alpha(N, rho, rng, nboot=2000):
    ok = (rho > 0) & np.isfinite(rho) & (N > 1)
    x, y = np.log(N[ok] - 1), np.log(rho[ok])
    b = np.polyfit(x, y, 1)[0]
    bs = []
    for _ in range(nboot):
        i = rng.integers(0, ok.sum(), ok.sum())
        if np.ptp(x[i]) > 0:
            bs.append(np.polyfit(x[i], y[i], 1)[0])
    return {"alpha": float(-b), "lo90": float(-np.quantile(bs, 0.95)), "hi90": float(-np.quantile(bs, 0.05)), "n": int(ok.sum()),
            "n_dropped_nonpositive": int((~ok).sum())}


def lopo_models(N, g):
    """LOPO squared error of period-level g under fixed-alpha mean-field models (one free scale c each)."""
    out = {}
    for name, alpha in (("CW_J0/N_alpha1", 1.0), ("dilution_alpha0.6", 0.6), ("field_alpha0", 0.0)):
        x = (N - 1) ** (1 - alpha)  # (N-1) rho with rho = c (N-1)^-alpha  =>  VR - 1 = c x
        vr1 = 1 / (1 - g) - 1
        err = []
        for i in range(len(g)):
            m = np.arange(len(g)) != i
            c = np.sum(x[m] * vr1[m]) / np.sum(x[m] ** 2)
            pred = c * x[i] / (1 + c * x[i])
            err.append((g[i] - pred) ** 2)
        out[name] = float(np.sum(err))
    return out


def ph1(daily, per) -> dict:
    rng = np.random.default_rng(C.SEED)
    res = {}
    prim = {"activity": "auto", "talk": "auto", "content": "F2"}
    for ch, v in prim.items():
        d = rho_bar(daily.filter((pl.col("channel") == ch) & (pl.col("variant") == v) & (pl.col("flag") == "ok")))
        pm = d.group_by("goal_no").agg(pl.col("rho").median(), pl.col("N").median(), pl.col("g").median())
        res[ch] = {"period_alpha": fit_alpha(pm["N"].to_numpy(), pm["rho"].to_numpy(), rng),
                   "spearman_g_N_period": float(stats.spearmanr(pm["N"], pm["g"])[0]),
                   "spearman_rho_N_period": float(stats.spearmanr(pm["N"], pm["rho"])[0]),
                   "median_rho": float(d["rho"].median()), "lopo_sse": lopo_models(pm["N"].to_numpy().astype(float), pm["g"].to_numpy())}
        d51 = d.filter(pl.col("goal_no") == 51)
        if d51.height > 10:
            res[ch]["G51_days_alpha"] = fit_alpha(d51["N"].to_numpy(), d51["rho"].to_numpy(), rng)
            res[ch]["G51_spearman_g_N"] = float(stats.spearmanr(d51["N"], d51["g"])[0])
    return res


def ph2(daily) -> dict:
    out = {}
    for ch, v in (("activity", "auto"), ("talk", "auto"), ("content", "F2")):
        d = daily.filter((pl.col("channel") == ch) & (pl.col("variant") == v) & (pl.col("flag") == "ok"))
        sig, n = 0, 0
        for _, x in d.group_by("goal_no"):
            if x.height >= 5:
                a = D.aggregate_days(x["g"].to_numpy(), x["se"].to_numpy() / D.SE_INFLATE)
                n += 1; sig += a["p_Q"] < 0.05
        out[ch] = {"n_periods": n, "n_Q_sig_raw_se": int(sig), "frac": sig / n if n else None}
    return out


def job(day):
    spins, h38 = _G["spins"], _G["h38"]
    rng = np.random.default_rng(E.seed_of("H25", day))  # same seed as explore: same auto stall threshold
    sp = spins.filter(pl.col("pt_date") == day)
    minute, agents, St = E.day_matrices(sp)
    active, talk, anyev = St >= 3, St == 4, St >= 2
    nact, ntalk = active.sum(0), talk.sum(0)
    popA = nact >= E.MIN_ACT
    m_auto, _ = D.find_stalls(anyev[:, popA], minute) if popA.sum() else (np.zeros(len(minute), bool), None)
    sch = set(h38.filter((pl.col("pt_date") == day) & pl.col("sched"))["minute"].to_list()) if h38 is not None else set()
    valid = ~(m_auto | np.isin(minute, list(sch)))
    rows = []
    # agent availability: between the agent's first and last logged event (any state >= 2) of the day
    T = len(minute)
    first = np.argmax(anyev, axis=0); last = T - 1 - np.argmax(anyev[::-1], axis=0)
    avail = (np.arange(T)[:, None] >= first[None, :]) & (np.arange(T)[:, None] <= last[None, :]) & anyev.any(0)[None, :]
    for ch, X, cnt, thr in (("activity", active, nact, E.MIN_ACT), ("talk", talk, ntalk, E.MIN_TALK)):
        pop = cnt >= thr
        if pop.sum() < 3:
            continue
        S = np.where(X[:, pop], 1.0, -1.0)
        r = D.binary_day(S, minute, valid=valid, rng=np.random.default_rng(E.seed_of("ph3", day, ch)))
        if r:
            rows.append({"pt_date": day, "channel": ch, "variant": "auto+h38_sched", "g": r.g, "se": r.se, "lo": r.lo, "hi": r.hi,
                         "N": r.N, "masked_min": int((~valid).sum())})
        # PH4: block means over available minutes; unavailable agent-minutes set to that mean (zero after centering)
        A = avail[:, pop]
        blk = D._blocks(minute, 30)
        Cm = np.zeros_like(S)
        for b in np.unique(blk):
            m = blk == b
            num = (S[m] * A[m]).sum(0); den = A[m].sum(0)
            mu = np.where(den > 0, num / np.maximum(den, 1), S[m].mean(0))
            Cm[m] = mu
        S4 = np.where(A, S, Cm)
        r4 = D.binary_day(S4, minute, valid=valid, center=Cm, rng=np.random.default_rng(E.seed_of("ph4", day, ch)))
        if r4:
            rows.append({"pt_date": day, "channel": ch, "variant": "auto+h38_sched+edges", "g": r4.g, "se": r4.se, "lo": r4.lo,
                         "hi": r4.hi, "N": r4.N, "masked_min": int((~valid).sum()), "unavail_frac": float(1 - A.mean())})
    return rows


def init(d):
    _G.update(d)


def main():
    daily = pl.read_parquet(C.OUT / "dial_daily.parquet")
    per = pl.read_parquet(C.OUT / "dial_period.parquet")
    res = {"PH1_size_scaling": ph1(daily, per), "PH2_heterogeneity_raw_se": ph2(daily)}
    spins = pl.read_parquet(C.OUT / "inputs/spins.parquet")
    h38 = pl.read_parquet(C.OUT / "inputs/h38_masks.parquet")
    days = spins["pt_date"].unique().sort().to_list()
    with Pool(2, initializer=init, initargs=({"spins": spins, "h38": h38},)) as pool:
        rows = [r for rr in pool.imap(job, days, chunksize=4) for r in rr]
    m = pl.DataFrame(rows).join(daily.select("pt_date", "goal_no").unique(), on="pt_date")
    m.write_parquet(C.OUT / "posthoc_mask.parquet")
    res["PH4_edges"] = {ch: {"median_g": float(m.filter((pl.col("channel") == ch) & (pl.col("variant") == "auto+h38_sched+edges"))["g"].median()),
                             "by_regime": m.filter((pl.col("channel") == ch) & (pl.col("variant") == "auto+h38_sched+edges"))
                             .join(daily.select("pt_date", "regime").unique(), on="pt_date").group_by("regime").agg(pl.col("g").median()).to_dicts(),
                             "median_unavail_frac": float(m.filter((pl.col("channel") == ch) & (pl.col("variant") == "auto+h38_sched+edges"))["unavail_frac"].median())}
                        for ch in ("activity", "talk")}
    m3 = m.filter(pl.col("variant") == "auto+h38_sched")
    res["PH3_combined_mask"] = {ch: {"median_g": float(m3.filter(pl.col("channel") == ch)["g"].median()),
                                     "median_g_auto": float(daily.filter((pl.col("channel") == ch) & (pl.col("variant") == "auto") & (pl.col("flag") == "ok"))["g"].median()),
                                     "median_g_none": float(daily.filter((pl.col("channel") == ch) & (pl.col("variant") == "none") & (pl.col("flag") == "ok"))["g"].median())}
                                for ch in ("activity", "talk")}
    (C.OUT / "results/posthoc.json").write_text(json.dumps(res, indent=1, default=float))
    C.write_provenance("posthoc", "hypotheses/H25-criticality-dial/analysis/posthoc.py", ["(H25 outputs)"], {"labelled": "post hoc"})
    print(json.dumps(res, indent=1, default=float))


if __name__ == "__main__":
    main()
