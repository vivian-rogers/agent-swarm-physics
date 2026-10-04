"""H16 per-goal-period pipeline: (a) dwell law, (b) landscape / Kramers closure, (c) kick dose laws, (d) swarm bistability.

Reads data/processed/H16-metastable-traps-kramers/<period>/ (built by scheme/build.py) and writes
results.json there plus hypotheses/H16-metastable-traps-kramers/<period>/figures/period.pdf.
Pre-registered estimators and thresholds are on the card ("Observables", "Prediction").

Usage: uv run python hypotheses/H16-metastable-traps-kramers/analysis/run_period.py --period G38 [--boot 100]
       (also importable: analyze(folder, regime, ...) is reused by confirm.py)
       ... run_period.py --period G38 --r1b   round 1b (improved data): reads <OUT>/r1b/<period>/ (built by
       scheme/build.py --r1b), skips the unchanged landscape (b) and swarm (d) blocks, adds TS5/TS6 window traps.
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h16lib as L  # noqa: E402

import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402
from scipy import stats  # noqa: E402

EL_EDGES = np.array([3, 5, 10, 20, 40, 80, 240]) * 60.0
DEEP_S = 600.0            # trap regime: elapsed >= 10 min
BAND = 0.3                # |slope| <= BAND: memoryless (Kramers-compatible), synthetic-calibrated
MIN_RC_MIN = 1500         # minutes after burn-in for an agent-level landscape cell


def t0log(t0, *a):
    print(f"[{time.time() - t0:6.1f}s]", *a, flush=True)


def kicks_dict(kk: pl.DataFrame) -> dict:
    K = {}
    for (a, c), g in kk.group_by(["agent", "kclass"]):
        K.setdefault(int(a), {})[c] = np.sort(g["ts"].to_numpy())
    return K


def subset(H, m):
    return {k: v[m] for k, v in H.items()}


def slope_fit(y, el, g, extra=None, link="cloglog"):
    X = [np.log(el / 60.0)]
    if extra is not None:
        X += list(extra.T)
    return L.glm_fe(y, np.stack(X, 1), g, link)


def boot_slope(H, rng, B, units, link="cloglog"):
    """Day-block bootstrap of the agent-FE slope on ln elapsed (first coefficient)."""
    bs = []
    for idx in L.day_bootstrap(units, rng, B):
        f = slope_fit(H["y"][idx], H["elapsed"][idx], H["agent"][idx], link=link)
        bs.append(f["beta"][0])
    bs = np.array(bs, float)
    bs = bs[np.isfinite(bs)]
    return (float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))) if len(bs) > 10 else (np.nan, np.nan)


def verdict_slope(b, lo, hi):
    if not np.isfinite(b):
        return "n/a"
    if lo >= -BAND and hi <= BAND:
        return "memoryless"
    if hi < -BAND:
        return "aging"
    if lo > BAND:
        return "timer-like"
    if b < -BAND:
        return "aging (CI overlaps band)"
    if b > BAND:
        return "timer-like (CI overlaps band)"
    return "memoryless (CI overlaps band edge)"


# =================================================================================== (a) dwell law

def dwell_ts1(ts1: pl.DataFrame, rng, B, tag):
    ts1 = ts1.filter(pl.col("first_act_s") >= 0)
    if ts1.height < 30:
        return {"ok": False, "n": ts1.height}
    H = L.ts1_hazard_rows(ts1, None)
    day = np.array(ts1["pt_date"].to_list())[H["spell"]]
    out = {"ok": True, "n_spells": ts1.height, "censored_frac": float(ts1["censored"].mean()),
           "n_with_pause_frac": float((ts1["n_pause"] > 0).mean()),
           "km_median_min": L.km_median(ts1["dwell_s"].to_numpy() / 60, ts1["censored"].to_numpy()),
           "exp_mle_mean_min": float(ts1["dwell_s"].sum() / 60 / max((~ts1["censored"]).sum(), 1)),
           "naive_completed_mean_min": float(ts1.filter(~pl.col("censored"))["dwell_s"].mean() / 60),
           "hazard_curve_per_30s": L.hazard_curve(H["y"], H["elapsed"], EL_EDGES)}
    for lo, hi, nm in ((DEEP_S, 1e9, "deep"), (180.0, DEEP_S, "early")):
        m = (H["elapsed"] >= lo) & (H["elapsed"] < hi)
        Hs = subset(H, m)
        if Hs["y"].sum() < 15:
            out[nm] = {"ok": False, "events": int(Hs["y"].sum())}
            continue
        f = slope_fit(Hs["y"], Hs["elapsed"], Hs["agent"])
        fp = slope_fit(Hs["y"], Hs["elapsed"], None)
        lo_, hi_ = boot_slope(Hs, rng, B, day[m]) if nm == "deep" else (f["beta"][0] - 1.96 * f["se"][0], f["beta"][0] + 1.96 * f["se"][0])
        out[nm] = {"ok": True, "beta_agentFE": float(f["beta"][0]), "se": float(f["se"][0]), "ci": [lo_, hi_],
                   "ci_wald": [float(f["beta"][0] - 1.96 * f["se"][0]), float(f["beta"][0] + 1.96 * f["se"][0])],
                   "beta_pooled": float(fp["beta"][0]), "events": f["n_events"], "rows": f["n"],
                   "verdict": verdict_slope(f["beta"][0], lo_, hi_),
                   "verdict_wald": verdict_slope(f["beta"][0], f["beta"][0] - 1.96 * f["se"][0], f["beta"][0] + 1.96 * f["se"][0])}
    # split: spells containing a declared idle event (PAUSE/WAIT) vs silent spells
    for kind, cond in (("declared_idle", (pl.col("n_pause") + pl.col("n_wait")) > 0), ("silent", (pl.col("n_pause") + pl.col("n_wait")) == 0)):
        sub = ts1.filter(cond)
        if sub.height < 30:
            out[f"deep_{kind}"] = {"ok": False, "n": sub.height}
            continue
        Hk = L.ts1_hazard_rows(sub, None)
        m = Hk["elapsed"] >= DEEP_S
        if Hk["y"][m].sum() < 15:
            out[f"deep_{kind}"] = {"ok": False, "events": int(Hk["y"][m].sum())}
            continue
        f = slope_fit(Hk["y"][m], Hk["elapsed"][m], Hk["agent"][m])
        out[f"deep_{kind}"] = {"ok": True, "n_spells": sub.height, "beta_agentFE": float(f["beta"][0]), "se": float(f["se"][0]),
                               "events": f["n_events"]}
    return out


def ts2_robust_view(ts2: pl.DataFrame) -> pl.DataFrame:
    """TS2r view: same gate rows, glance-robust outcome / chain / k (amendment 2026-10-03)."""
    if ts2.height == 0 or "outcome_r" not in ts2.columns:
        return ts2.head(0)
    return ts2.drop("outcome", "chain", "k", "next_declared_s").rename(
        {"outcome_r": "outcome", "chain_r": "chain", "k_r": "k", "next_declared_r_s": "next_declared_s"})


def dwell_ts2(ts2: pl.DataFrame, rng, B):
    if ts2.height < 30:
        return {"ok": False, "n": ts2.height}
    g = ts2.filter(pl.col("outcome") != "censored")
    if (g["outcome"] == "repause").sum() < 10:
        return {"ok": False, "n_gates": g.height, "n_repause": int((g["outcome"] == "repause").sum()),
                "reason": "fewer than 10 re-pauses: chains do not exist under this definition"}
    y = (g["outcome"] != "repause").to_numpy().astype(int)
    k = g["k"].to_numpy().astype(float)
    d = g["declared_s"].fill_null(np.nan).to_numpy()
    okd = np.isfinite(d) & (d > 0)
    out = {"ok": True, "n_gates": g.height, "n_chains": int(g.select(pl.struct("pt_date", "agent", "chain").n_unique()).item()),
           "frac_censored_gates": float((ts2["outcome"] == "censored").mean()),
           "frac_early": float((g["outcome"] == "early").mean()),
           "p_escape_by_k": [{"k": kk, "n": int((np.minimum(k, 6) == kk).sum()), "p": float(y[np.minimum(k, 6) == kk].mean()) if (np.minimum(k, 6) == kk).any() else np.nan}
                             for kk in range(1, 7)]}
    X = np.stack([np.log(k[okd]), np.log(d[okd])], 1)
    f = L.glm_fe(y[okd], X, g["agent"].to_numpy()[okd], "logit")
    fp = L.glm_fe(y[okd], X, None, "logit")
    days = np.array(g["pt_date"].to_list())[okd]
    bs = []
    for idx in L.day_bootstrap(days, rng, B):
        bs.append(L.glm_fe(y[okd][idx], X[idx], g["agent"].to_numpy()[okd][idx], "logit")["beta"][0])
    bs = np.array(bs, float); bs = bs[np.isfinite(bs)]
    ci = (float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))) if len(bs) > 10 else (np.nan, np.nan)
    out.update({"beta_lnk_agentFE": float(f["beta"][0]), "se": float(f["se"][0]), "ci": list(ci),
                "ci_wald": [float(f["beta"][0] - 1.96 * f["se"][0]), float(f["beta"][0] + 1.96 * f["se"][0])],
                "beta_lnd_agentFE": float(f["beta"][1]), "beta_lnk_pooled": float(fp["beta"][0]), "events": f["n_events"],
                "verdict": verdict_slope(f["beta"][0], *ci),
                "verdict_wald": verdict_slope(f["beta"][0], f["beta"][0] - 1.96 * f["se"][0], f["beta"][0] + 1.96 * f["se"][0])})
    # trap deepening: declared duration along re-pause chains
    rp = ts2.filter((pl.col("outcome") == "repause") & pl.col("declared_s").is_not_null() & pl.col("next_declared_s").is_not_null()
                    & (pl.col("declared_s") > 0) & (pl.col("next_declared_s") > 0))
    if rp.height >= 20:
        lr = np.log(rp["next_declared_s"].to_numpy() / rp["declared_s"].to_numpy())
        out["deepening"] = {"n": rp.height, "median_log_ratio_next_over_current": float(np.median(lr)),
                            "frac_longer": float((lr > 0).mean()), "frac_shorter": float((lr < 0).mean())}
    return out


def dwell_loops(tl: pl.DataFrame, rng, B, kmin):
    if tl.height < 30:
        return {"ok": False, "n": tl.height}
    g = tl.filter(~pl.col("censored"))
    k = g["k"].to_numpy().astype(float); y = g["y"].to_numpy()
    out = {"ok": True, "n_rows": g.height, "n_runs_reaching_kmin": int(tl.filter(pl.col("k") == kmin).height),
           "p_break_by_k": [{"k": kk, "n": int((np.minimum(k, 8) == kk).sum()), "p": float(y[np.minimum(k, 8) == kk].mean()) if (np.minimum(k, 8) == kk).any() else np.nan}
                            for kk in range(1, 9)]}
    m = k >= kmin
    if y[m].sum() < 15:
        out["deep"] = {"ok": False, "events": int(y[m].sum())}
        return out
    X = np.log(k[m])[:, None]
    f = L.glm_fe(y[m], X, g["agent"].to_numpy()[m], "cloglog")
    fp = L.glm_fe(y[m], X, None, "cloglog")
    days = np.array(g["pt_date"].to_list())[m]
    bs = []
    for idx in L.day_bootstrap(days, rng, B):
        bs.append(L.glm_fe(y[m][idx], X[idx], g["agent"].to_numpy()[m][idx], "cloglog")["beta"][0])
    bs = np.array(bs, float); bs = bs[np.isfinite(bs)]
    ci = (float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))) if len(bs) > 10 else (np.nan, np.nan)
    out["deep"] = {"ok": True, "beta_agentFE": float(f["beta"][0]), "se": float(f["se"][0]), "ci": list(ci),
                   "ci_wald": [float(f["beta"][0] - 1.96 * f["se"][0]), float(f["beta"][0] + 1.96 * f["se"][0])],
                   "beta_pooled": float(fp["beta"][0]), "events": f["n_events"], "verdict": verdict_slope(f["beta"][0], *ci),
                   "verdict_wald": verdict_slope(f["beta"][0], f["beta"][0] - 1.96 * f["se"][0], f["beta"][0] + 1.96 * f["se"][0])}
    return out


# =================================================================================== (b) landscape

def landscape_period(mins: pl.DataFrame, ts1r: pl.DataFrame):
    if mins.height == 0:
        return {"ok": False}
    series, acts = {}, {}
    for (d, a), g in mins.sort("pt_date", "agent", "minute").group_by(["pt_date", "agent"], maintain_order=True):
        A = g["a"].to_numpy().astype(float)
        series.setdefault(int(a), []).append(L.ewma(A[None, :])[0])
        acts.setdefault(int(a), []).append(A)
    allser = [s for v in series.values() for s in v]
    allact = [s for v in acts.values() for s in v]
    out = {"ok": True, "pooled": L.rc_cell(allser, acts=allact)}
    # robustness: EWMA tau
    for tau in (3.0, 10.0):
        ser_t = [L.ewma(a[None, :], tau)[0] for a in allact]
        c = L.rc_cell(ser_t, acts=allact)
        out[f"pooled_tau{int(tau)}"] = {k: c.get(k) for k in ("ok", "n", "mfpt_1d", "mfpt_msm", "mfpt_msm2", "obs")} | \
            {"double_well": c.get("landscape", {}).get("double_well"), "dG": c.get("landscape", {}).get("dG")}
    cells = []
    t1r = ts1r.filter(pl.col("first_act_s") >= 0)
    for a in series:
        n_after = sum(max(len(s) - L.BURN_MIN, 0) for s in series[a])
        if n_after < MIN_RC_MIN:
            continue
        c = L.rc_cell(series[a], acts=acts[a])
        ls = c.get("landscape", {})
        rec = {"agent": a, "n_min": n_after, "double_well": bool(ls.get("double_well", False)), "reason": ls.get("reason"),
               "active_frac": float(np.mean(np.concatenate(acts[a])))}
        sp = t1r.filter(pl.col("agent") == a)
        if sp.height:
            k_, ev_, ex_ = L.deep_rate(sp)
            if ev_ >= 5:
                rec["k_ts1r"] = k_
            rec["n_ts1r_deep_events"] = ev_
        if rec["double_well"]:
            rec.update({"dG": ls["dG"], "xa": ls["xa"], "xs": ls["xs"], "xb": ls["xb"], "k_obs": c["obs"]["k"],
                        "n_pass": c["obs"]["n_events"], "mfpt_1d": c["mfpt_1d"], "mfpt_kramers": c["mfpt_kramers"],
                        "mfpt_msm": c["mfpt_msm"], "mfpt_msm2": c["mfpt_msm2"], "T_eff_well": c["T_eff_well"],
                        "dU_over_T_drift": c["dU_over_T_drift"]})
        cells.append(rec)
    out["cells"] = cells
    C = pl.DataFrame(cells) if cells else pl.DataFrame()
    out["n_cells"] = len(cells)
    out["frac_double_well"] = float(C["double_well"].mean()) if len(cells) else np.nan

    def mal(pred_col):
        if not len(cells) or pred_col not in C.columns:
            return {"n": 0}
        D = C.filter(pl.col("double_well") & pl.col("k_obs").is_not_null() & (pl.col("n_pass") >= 15) & pl.col(pred_col).is_not_null())
        if D.height == 0:
            return {"n": 0}
        lr = np.log(D["k_obs"].to_numpy()) - np.log(1 / D[pred_col].to_numpy())
        lr = lr[np.isfinite(lr)]
        return {"n": int(len(lr)), "median_ln_obs_over_pred": float(np.median(lr)) if len(lr) else np.nan,
                "median_abs_ln_ratio": float(np.median(np.abs(lr))) if len(lr) else np.nan}
    out["closure"] = {p: mal(p) for p in ("mfpt_1d", "mfpt_kramers", "mfpt_msm", "mfpt_msm2")}
    if len(cells) and "dG" in C.columns:
        D = C.filter(pl.col("double_well") & pl.col("k_ts1r").is_not_null() & pl.col("dG").is_not_null())
        if D.height >= 4:
            b, a = np.polyfit(D["dG"].to_numpy(), np.log(D["k_ts1r"].to_numpy()), 1)
            out["arrhenius_ln_kts1r_on_dG"] = {"n": D.height, "slope": float(b), "intercept": float(a),
                                               "spearman": float(stats.spearmanr(D["dG"].to_numpy(), D["k_ts1r"].to_numpy())[0])}
    return out


# =================================================================================== (c) kicks

GROUPS = {"directed": ("A_men", "H_men", "N_tgt"), "undirected": ("A_und", "H_und")}


def _grp(H, prefix, classes):
    return np.sum([H[f"{prefix}_{c}"] for c in classes], axis=0)


def kick_models(H: dict, link="cloglog"):
    """Per-class HR (any kick of the class in the fast window) and dose laws for directed / undirected groups."""
    el = np.log(H["elapsed"] / 60.0)
    out = {}
    cls = [c for c in L.KCLASSES if H[f"f_{c}"].sum() > 0]
    X = np.stack([el] + [(H[f"f_{c}"] > 0).astype(float) for c in cls], 1)
    f = L.glm_fe(H["y"], X, H["agent"], link)
    out["per_class"] = {c: {"lnHR": float(f["beta"][i + 1]), "se": float(f["se"][i + 1]),
                            "n_bins": int((H[f"f_{c}"] > 0).sum()), "events": int(H["y"][H[f"f_{c}"] > 0].sum())}
                        for i, c in enumerate(cls)}
    gd = _grp(H, "f", GROUPS["directed"]); gu = _grp(H, "f", GROUPS["undirected"])
    X2 = np.stack([el] + list(L.dose_dummies(gd).T) + list(L.dose_dummies(gu).T), 1)
    f2 = L.glm_fe(H["y"], X2, H["agent"], link)
    for j, (nm, gv) in enumerate((("directed", gd), ("undirected", gu))):
        sl = slice(1 + 3 * j, 4 + 3 * j)
        lhr = f2["beta"][sl].copy(); cov = f2["cov"][sl, sl]
        for k_ in range(3):
            if H["y"][np.minimum(gv, 3) == k_ + 1].sum() < 5:
                lhr[k_] = np.nan
        n3 = gv[gv >= 3]
        dl = L.dose_law(lhr, cov, [1, 2, float(n3.mean()) if len(n3) else 3.0])
        ev2 = int(H["y"][gv >= 2].sum())
        out[f"dose_{nm}"] = {"lhr": [float(v) for v in lhr], "se": [float(v) for v in f2["se"][sl]],
                             "n_bins": [int((np.minimum(gv, 3) == k).sum()) for k in range(4)],
                             "events": [int(H["y"][np.minimum(gv, 3) == k].sum()) for k in range(4)],
                             "events_dose_ge2": ev2, "powered": ev2 >= 30,
                             "best": dl.get("best_aic"), "aic": dl.get("aic"), "kappa": dl.get("kappa")}
    # main any-directed / any-undirected HRs
    X3 = np.stack([el, (gd > 0).astype(float), (gu > 0).astype(float)], 1)
    f3 = L.glm_fe(H["y"], X3, H["agent"], link)
    out["any_directed_lnHR"] = float(f3["beta"][1]); out["any_directed_se"] = float(f3["se"][1])
    out["any_undirected_lnHR"] = float(f3["beta"][2]); out["any_undirected_se"] = float(f3["se"][2])
    # slow window for nudges to the target
    if "s_N_tgt" in H and (H["s_N_tgt"] > 0).sum() > 0:
        X4 = np.stack([el, (gd > 0).astype(float), (gu > 0).astype(float), (H["s_N_tgt"] > 0).astype(float)], 1)
        f4 = L.glm_fe(H["y"], X4, H["agent"], link)
        out["nudge_slow15_lnHR"] = float(f4["beta"][3]); out["nudge_slow15_se"] = float(f4["se"][3])
        out["nudge_slow15_bins"] = int((H["s_N_tgt"] > 0).sum())
    # aging after conditioning on kicks (a2): slope on ln elapsed in the deep window, with and without kick terms
    m = H["elapsed"] >= DEEP_S
    if H["y"][m].sum() >= 15:
        fa = L.glm_fe(H["y"][m], el[m][:, None], H["agent"][m], link)
        fb = L.glm_fe(H["y"][m], X3[m], H["agent"][m], link)
        out["a2_deep_slope_without_kicks"] = float(fa["beta"][0])
        out["a2_deep_slope_with_kicks"] = float(fb["beta"][0])
        out["a2_se"] = float(fb["se"][0])
    return out


def dayswap_kicks(K: dict, W: dict, rng):
    """Each agent-day's kicks replaced by the same agent's kicks from another day of the period, same window offset."""
    days = sorted(W)
    Kx = {}
    for a, cl in K.items():
        for c, arr in cl.items():
            parts = []
            for d in days:
                lo, hi = W[d]["t0"], W[d]["t1"]
                dd = days[int(rng.integers(len(days)))]
                if len(days) > 1:
                    while dd == d:
                        dd = days[int(rng.integers(len(days)))]
                src = arr[(arr >= W[dd]["t0"]) & (arr < W[dd]["t1"] + 1)]
                parts.append(src - W[dd]["t0"] + lo)
            Kx.setdefault(a, {})[c] = np.sort(np.concatenate(parts)) if parts else np.zeros(0)
    return Kx


def kicks_ts1(ts1, K, W, rng, n_null, tag):
    ts1 = ts1.filter(pl.col("first_act_s") >= 0)
    if ts1.height < 30:
        return {"ok": False}
    H = L.ts1_hazard_rows(ts1, K)
    out = {"ok": True, "rows": int(len(H["y"])), "events": int(H["y"].sum())}
    out.update(kick_models(H))
    # A2 (post hoc sensitivity): exact-time counting-process rows, dose constant within intervals
    I = L.ts1_interval_rows(ts1, K)
    if len(I["y"]) and I["y"].sum() >= 15:
        el = np.log(np.maximum(I["elapsed"], 1.0) / 60.0)
        Xa = np.stack([el, (I["directed"] > 0).astype(float), (I["undirected"] > 0).astype(float)], 1)
        fa = L.glm_fe(I["y"], Xa, I["agent"], "cloglog", offset=np.log(I["dt"] / 60.0))
        Xd = np.stack([el] + list(L.dose_dummies(I["directed"]).T) + list(L.dose_dummies(I["undirected"]).T), 1)
        fd = L.glm_fe(I["y"], Xd, I["agent"], "cloglog", offset=np.log(I["dt"] / 60.0))
        a2 = {"directed_lnHR": float(fa["beta"][1]), "directed_se": float(fa["se"][1]),
              "undirected_lnHR": float(fa["beta"][2]), "undirected_se": float(fa["se"][2]),
              "intervals": int(len(I["y"])), "events": int(I["y"].sum())}
        for j, (nm, gv) in enumerate((("directed", I["directed"]), ("undirected", I["undirected"]))):
            sl = slice(1 + 3 * j, 4 + 3 * j)
            lhr = fd["beta"][sl].copy(); cov = fd["cov"][sl, sl]
            for k_ in range(3):
                if I["y"][np.minimum(gv, 3) == k_ + 1].sum() < 5:
                    lhr[k_] = np.nan
            n3 = gv[gv >= 3]
            dl = L.dose_law(lhr, cov, [1, 2, float(n3.mean()) if len(n3) else 3.0])
            ev2 = int(I["y"][gv >= 2].sum())
            a2[f"dose_{nm}"] = {"lhr": [float(v) for v in lhr], "events": [int(I["y"][np.minimum(gv, 3) == k].sum()) for k in range(4)],
                                "events_dose_ge2": ev2, "powered": ev2 >= 30, "best": dl.get("best_aic"), "kappa": dl.get("kappa")}
        out["A2_exact_time"] = a2
    nd, nu = [], []
    for s in range(n_null):
        Kx = dayswap_kicks(K, W, rng)
        Hx = L.ts1_hazard_rows(ts1, Kx)
        gd = _grp(Hx, "f", GROUPS["directed"]); gu = _grp(Hx, "f", GROUPS["undirected"])
        X = np.stack([np.log(Hx["elapsed"] / 60.0), (gd > 0).astype(float), (gu > 0).astype(float)], 1)
        f = L.glm_fe(Hx["y"], X, Hx["agent"], "cloglog")
        nd.append(f["beta"][1]); nu.append(f["beta"][2])
        if "A2_exact_time" in out and s < 20:
            Ix = L.ts1_interval_rows(ts1, Kx)
            elx = np.log(np.maximum(Ix["elapsed"], 1.0) / 60.0)
            Xx = np.stack([elx, (Ix["directed"] > 0).astype(float), (Ix["undirected"] > 0).astype(float)], 1)
            fx = L.glm_fe(Ix["y"], Xx, Ix["agent"], "cloglog", offset=np.log(Ix["dt"] / 60.0))
            out.setdefault("_a2null_d", []).append(float(fx["beta"][1])); out.setdefault("_a2null_u", []).append(float(fx["beta"][2]))
    nd, nu = np.array(nd, float), np.array(nu, float)
    out["null_directed_lnHR_p95"] = float(np.nanpercentile(nd, 95)) if n_null else np.nan
    out["null_directed_lnHR_median"] = float(np.nanmedian(nd)) if n_null else np.nan
    out["null_undirected_lnHR_p95"] = float(np.nanpercentile(nu, 95)) if n_null else np.nan
    out["null_undirected_lnHR_median"] = float(np.nanmedian(nu)) if n_null else np.nan
    out["null_undirected_lnHR_p05"] = float(np.nanpercentile(nu, 5)) if n_null else np.nan
    if "_a2null_d" in out:
        out["A2_exact_time"]["null_directed_p95"] = float(np.nanpercentile(out.pop("_a2null_d"), 95))
        out["A2_exact_time"]["null_undirected_p95"] = float(np.nanpercentile(out.pop("_a2null_u"), 95))
    return out


def kicks_ts2(ts2):
    if ts2.height < 30:
        return {"ok": False}
    g = ts2.filter((pl.col("outcome") != "censored") & pl.col("declared_s").is_not_null() & (pl.col("declared_s") > 0))
    y = (g["outcome"] != "repause").to_numpy().astype(int)
    if (y == 0).sum() < 10:
        return {"ok": False, "reason": "fewer than 10 re-pauses", "n_gates": g.height}
    gd = np.sum([g[f"n_{c}"].to_numpy() for c in GROUPS["directed"]], axis=0)
    gu = np.sum([g[f"n_{c}"].to_numpy() for c in GROUPS["undirected"]], axis=0)
    base = [np.log(g["k"].to_numpy().astype(float)), np.log(g["declared_s"].to_numpy())]
    out = {"ok": True, "n_gates": g.height}
    X = np.stack(base + list(L.dose_dummies(gd).T) + list(L.dose_dummies(gu).T), 1)
    f = L.glm_fe(y, X, g["agent"].to_numpy(), "logit")
    for j, (nm, gv) in enumerate((("directed", gd), ("undirected", gu))):
        sl = slice(2 + 3 * j, 5 + 3 * j)
        lhr = f["beta"][sl].copy(); cov = f["cov"][sl, sl]
        for k_ in range(3):
            if y[np.minimum(gv, 3) == k_ + 1].sum() < 5:
                lhr[k_] = np.nan
        n3 = gv[gv >= 3]
        dl = L.dose_law(lhr, cov, [1, 2, float(n3.mean()) if len(n3) else 3.0])
        out[f"dose_{nm}"] = {"lnOR": [float(v) for v in lhr], "se": [float(v) for v in f["se"][sl]],
                             "n_gates": [int((np.minimum(gv, 3) == k).sum()) for k in range(4)],
                             "events": [int(y[np.minimum(gv, 3) == k].sum()) for k in range(4)],
                             "events_dose_ge2": int(y[gv >= 2].sum()), "powered": int(y[gv >= 2].sum()) >= 30,
                             "best": dl.get("best_aic"), "kappa": dl.get("kappa")}
    cls = [c for c in L.KCLASSES if (g[f"n_{c}"].to_numpy() > 0).sum() >= 5]
    Xc = np.stack(base + [(g[f"n_{c}"].to_numpy() > 0).astype(float) for c in cls], 1)
    fc = L.glm_fe(y, Xc, g["agent"].to_numpy(), "logit")
    out["per_class"] = {c: {"lnOR": float(fc["beta"][i + 2]), "se": float(fc["se"][i + 2]),
                            "n_gates": int((g[f"n_{c}"].to_numpy() > 0).sum())} for i, c in enumerate(cls)}
    return out


def kicks_loops(tl):
    if tl.height < 30:
        return {"ok": False}
    g = tl.filter(~pl.col("censored"))
    y = g["y"].to_numpy()
    gd = np.sum([g[f"n_{c}"].to_numpy() for c in GROUPS["directed"]], axis=0)
    gu = np.sum([g[f"n_{c}"].to_numpy() for c in GROUPS["undirected"]], axis=0)
    X = np.stack([np.log(g["k"].to_numpy().astype(float)), (gd > 0).astype(float), (gu > 0).astype(float)], 1)
    f = L.glm_fe(y, X, g["agent"].to_numpy(), "cloglog")
    return {"ok": True, "directed_lnHR": float(f["beta"][1]), "directed_se": float(f["se"][1]), "directed_rows": int((gd > 0).sum()),
            "undirected_lnHR": float(f["beta"][2]), "undirected_se": float(f["se"][2]), "undirected_rows": int((gu > 0).sum())}


# =================================================================================== driver

def outage_intervals(MA: dict, W: dict, min_len=10):
    """Village-off intervals (epoch s): runs of >= min_len minutes in which no present agent has an active minute."""
    out = []
    for d, (ag, A) in MA.items():
        K = A.sum(0)
        z = np.r_[0, (K == 0).astype(int), 0]
        dz = np.diff(z); st = np.nonzero(dz == 1)[0]; en = np.nonzero(dz == -1)[0]
        for a, b in zip(st, en):
            if b - a >= min_len:
                out.append((W[d]["t0"] + a * 60.0, W[d]["t0"] + b * 60.0))
    return sorted(out)


def censor_outages(ts: pl.DataFrame, outages):
    """Censor spells at the start of an overlapping outage; drop spells that start inside one."""
    if ts.height == 0:
        return ts
    t0 = ts["t0"].to_numpy(); t1 = ts["t1"].to_numpy().copy(); c = ts["censored"].to_numpy().copy()
    keep = np.ones(len(t0), bool)
    for a, b in outages:
        inside = (t0 >= a) & (t0 < b)
        keep &= ~inside
        cut = (t0 < a) & (t1 > a)
        t1[cut] = a; c[cut] = True
    return ts.with_columns(pl.Series("t1", t1), pl.Series("censored", c),
                           pl.Series("dwell_s", (t1 - t0).astype(np.float32))).filter(pl.Series(keep))


def analyze(folder: Path, regime: str, rng, B=100, n_null=40, n_sur=200, fig_dir: Path | None = None, label="",
            parts=("a", "b", "c", "d")):
    t0 = time.time()
    rd = lambda n: pl.read_parquet(folder / f"{n}.parquet")
    ts1, ts1r, ts2, ts3, ts4, mins, kk = (rd(n) for n in ("ts1", "ts1r", "ts2", "ts3", "ts4", "minutes", "kicks"))
    days = sorted(mins["pt_date"].unique().to_list()) if mins.height else []
    W = L.windows(days)
    K = kicks_dict(kk) if kk.height else {}
    R = {"label": label, "regime": regime, "n_days": len(days), "days": days,
         "n_agents": int(mins["agent"].n_unique()) if mins.height else 0,
         "counts": {"ts1": ts1.height, "ts1r": ts1r.height, "ts2_gates": ts2.height, "ts3_rows": ts3.height, "ts4_rows": ts4.height,
                    "kicks": {c: int((kk["kclass"] == c).sum()) for c in L.KCLASSES} if kk.height else {}}}
    t0log(t0, label, "a: dwell")
    R["a"] = {"TS1r": dwell_ts1(ts1r, rng, B, "ts1r"), "TS1": dwell_ts1(ts1, rng, max(B // 2, 20), "ts1"),
              "TS2": dwell_ts2(ts2, rng, B) if regime == "III" else {"ok": False, "reason": "regime"},
              "TS2r": dwell_ts2(ts2_robust_view(ts2), rng, B) if regime == "III" else {"ok": False, "reason": "regime"},
              "TS3": dwell_loops(ts3, rng, B, L.LOOP_MIN), "TS4": dwell_loops(ts4, rng, B, L.LOOP_MIN)}
    t0log(t0, label, "b: landscape")
    R["b"] = landscape_period(mins, ts1r) if "b" in parts else {"ok": False, "reason": "skipped (inputs unchanged in round 1b)"}
    t0log(t0, label, "c: kicks")
    R["c"] = {"TS1": kicks_ts1(ts1, K, W, rng, n_null, "ts1"), "TS1r": kicks_ts1(ts1r, K, W, rng, 0, "ts1r"),
              "TS2": kicks_ts2(ts2) if regime == "III" else {"ok": False, "reason": "regime"},
              "TS2r": kicks_ts2(ts2_robust_view(ts2)) if regime == "III" else {"ok": False, "reason": "regime"},
              "TS3": kicks_loops(ts3), "TS4": kicks_loops(ts4)}
    if "d" not in parts:
        R["d"] = {"skipped": "inputs unchanged in round 1b"}
        t0log(t0, label, "done")
        return R
    t0log(t0, label, "d: swarm")
    MA = {}
    for (d,), g in mins.sort("pt_date", "agent", "minute").group_by(["pt_date"], maintain_order=True):
        ag = np.sort(g["agent"].unique().to_numpy())
        n_min = int(g["minute"].max()) + 1
        A = np.zeros((len(ag), n_min), np.int8)
        A[np.searchsorted(ag, g["agent"].to_numpy()), g["minute"].to_numpy()] = g["a"].to_numpy()
        MA[d] = (ag, A)
    R["d"] = {"all": L.swarm_analysis(MA, rng, n_sur=n_sur), "no_stalls": L.swarm_analysis(MA, rng, n_sur=n_sur, exclude_stalls=True),
              "A4_circ_no_stalls": L.swarm_analysis(MA, rng, n_sur=n_sur, exclude_stalls=True, null="circ")}
    # A3 (post hoc): village-off outages (all present agents silent >= 10 min) censor TS1/TS1r spells
    outages = outage_intervals(MA, W)
    R["A3_outages"] = {"n": len(outages), "minutes": float(sum((b - a) / 60 for a, b in outages))}
    if outages:
        t1c = censor_outages(ts1, outages); t1rc = censor_outages(ts1r, outages)
        R["A3_outages"]["TS1r"] = dwell_ts1(t1rc, rng, B, "ts1r")
        R["A3_outages"]["TS1_kicks"] = kicks_ts1(t1c, K, W, rng, 0, "ts1")
        keep_days = sorted(set(days) - {d for d in days if any(W[d]["t0"] <= a < W[d]["t1"] for a, _ in outages)})
        R["A3_outages"]["b_without_outage_days"] = {k: v for k, v in landscape_period(mins.filter(pl.col("pt_date").is_in(keep_days)), t1rc).items() if k != "cells"} if keep_days else None
    t0log(t0, label, "done")
    if fig_dir is not None:
        period_figure(R, fig_dir / "period.pdf", label)
    return R


def period_figure(R, path: Path, label):
    plt.rcParams.update({"font.family": "serif", "font.size": 6.5, "axes.linewidth": 0.5, "pdf.fonttype": 42})
    fig, ax = plt.subplots(2, 3, figsize=(7.2, 4.4))
    a = R["a"]
    for nm, st in (("TS1r", "o-"), ("TS1", "s--")):
        if a[nm].get("ok"):
            hc = a[nm]["hazard_curve_per_30s"]
            x = [0.5 * (h["lo"] + h["hi"]) / 60 for h in hc]
            ax[0, 0].plot(x, [h["h"] for h in hc], st, ms=3, label=nm)
    ax[0, 0].set_xscale("log"); ax[0, 0].set_yscale("log"); ax[0, 0].axvline(10, lw=0.4, c="grey")
    ax[0, 0].set_xlabel("elapsed in inactive spell (min)"); ax[0, 0].set_ylabel("escape hazard per 30 s"); ax[0, 0].legend(fontsize=5)
    ax[0, 0].set_title("(a) TS1 hazard")
    for nm, key, st in (("TS2 per gate", "TS2", "o-"), ("TS3 error loop", "TS3", "s-"), ("TS4 cmd loop", "TS4", "^-")):
        if a[key].get("ok"):
            arr = a[key].get("p_escape_by_k") or a[key].get("p_break_by_k")
            ax[0, 1].plot([z["k"] for z in arr], [z["p"] for z in arr], st, ms=3, label=nm)
    ax[0, 1].set_xlabel("gate / loop turn index k"); ax[0, 1].set_ylabel("P(escape at k | reached k)"); ax[0, 1].legend(fontsize=5)
    ax[0, 1].set_title("(a) discrete traps")
    b = R["b"]
    if b.get("ok") and b["pooled"].get("ok"):
        ls = b["pooled"]["landscape"]
        ax[0, 2].plot(ls["centers"], ls["G"], "k-", lw=1, label="pooled")
        for c in b.get("cells", [])[:0]:
            pass
        ax[0, 2].set_xlabel("x = EWMA(active minute), tau 5 min"); ax[0, 2].set_ylabel("G(x) = -ln P(x)")
        ax[0, 2].set_title(f"(b) landscape; double well {b.get('frac_double_well', np.nan):.2f} of agents")
    c = R["c"]["TS1"]
    if c.get("ok"):
        pc = c["per_class"]
        ks = list(pc)
        ax[1, 0].errorbar(range(len(ks)), [pc[k]["lnHR"] for k in ks], yerr=[1.96 * pc[k]["se"] for k in ks], fmt="o", ms=3)
        ax[1, 0].axhline(0, lw=0.4, c="grey")
        ax[1, 0].axhspan(c.get("null_undirected_lnHR_p05", 0), c.get("null_undirected_lnHR_p95", 0), color="grey", alpha=0.2, lw=0)
        ax[1, 0].set_xticks(range(len(ks))); ax[1, 0].set_xticklabels(ks, fontsize=5)
        ax[1, 0].set_ylabel("ln HR (kick in prior 2 min)"); ax[1, 0].set_title("(c) kick classes, TS1 (grey: day-swap null, undirected)")
    for nm, st in (("directed", "o-"), ("undirected", "s-")):
        dd = c.get(f"dose_{nm}") if c.get("ok") else None
        if dd:
            ax[1, 1].errorbar([1, 2, 3], dd["lhr"], yerr=1.96 * np.array(dd["se"]), fmt=st, ms=3, label=f"{nm}: {dd['best']}")
    ax[1, 1].set_xlabel("kick dose in prior 2 min (3 = 3+)"); ax[1, 1].set_ylabel("ln HR vs dose 0"); ax[1, 1].legend(fontsize=5)
    ax[1, 1].set_title("(c) dose law, TS1")
    d = R["d"]["all"]
    if d.get("ok"):
        n = len(d["hist_obs"])
        x = (np.arange(n) + 0.5) / n
        ax[1, 2].bar(x, np.array(d["hist_obs"]) / sum(d["hist_obs"]), width=1 / n, alpha=0.5, label="observed")
        ax[1, 2].plot(x, np.array(d["hist_null"]) / sum(d["hist_null"]), "k-", lw=0.8, label="day-swap null")
        ax[1, 2].set_xlabel("swarm active fraction m"); ax[1, 2].legend(fontsize=5)
        ax[1, 2].set_title(f"(d) betaJ0 {d['betaJ0']:.2f}; p(valley) {d['p_valley']:.2f}")
    fig.suptitle(f"H16 x {label}", fontsize=8)
    fig.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path)
    plt.close(fig)


def main():
    args = sys.argv[1:]
    period = args[args.index("--period") + 1]
    B = int(args[args.index("--boot") + 1]) if "--boot" in args else 100
    n_null = int(args[args.index("--null") + 1]) if "--null" in args else 40
    sys.path.insert(0, str(L.HDIR / "scheme"))
    from build import PERIODS  # noqa: E402
    regime = PERIODS[period]["regime"]
    rng = np.random.default_rng(L.SEED + int(period[1:3]))
    if "--r1b" in args:
        import r1blib as RB  # noqa: E402
        folder = L.OUT / "r1b" / period
        days = sorted(pl.read_parquet(folder / "minutes.parquet")["pt_date"].unique().to_list())
        L.assert_no_holdout(days)
        R = analyze(folder, regime, rng, B=B, n_null=n_null, fig_dir=None, label=period + " r1b", parts=("a", "c"))
        R["a"]["TS5"] = RB.dwell_windows(pl.read_parquet(folder / "ts5.parquet"), rng, B)
        R["a"]["TS6"] = RB.dwell_windows(pl.read_parquet(folder / "ts6.parquet"), rng, B)
        L.jdump(R, folder / "results.json")
        return
    folder = L.OUT / period
    days = sorted(pl.read_parquet(folder / "minutes.parquet")["pt_date"].unique().to_list())
    L.assert_no_holdout(days)
    R = analyze(folder, regime, rng, B=B, n_null=n_null, fig_dir=L.HDIR / period / "figures", label=period)
    # NE17 split sensitivity for G38 (primary TS1r deep slope and TS2 slope on each side)
    if period == "G38":
        R["split_NE17"] = {}
        for side, cond in (("before_0414", pl.col("pt_date") < "2026-04-14"), ("from_0414", pl.col("pt_date") >= "2026-04-14")):
            t1r = pl.read_parquet(folder / "ts1r.parquet").filter(cond)
            t2 = pl.read_parquet(folder / "ts2.parquet").filter(cond)
            R["split_NE17"][side] = {"TS1r": dwell_ts1(t1r, rng, 50, "ts1r").get("deep"),
                                     "TS2": {k: v for k, v in dwell_ts2(t2, rng, 50).items() if k in ("beta_lnk_agentFE", "se", "ci", "verdict", "n_gates")},
                                     "TS2r": {k: v for k, v in dwell_ts2(ts2_robust_view(t2), rng, 50).items() if k in ("beta_lnk_agentFE", "se", "ci", "verdict", "n_gates")}}
    L.jdump(R, folder / "results.json")


if __name__ == "__main__":
    main()
