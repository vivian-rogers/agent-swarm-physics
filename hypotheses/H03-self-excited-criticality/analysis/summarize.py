"""Summaries and prediction tests for H03 (exploratory, non-holdout). Prints markdown tables; writes
data/processed/H03-self-excited-criticality/period_table.parquet and summary.json.
Run: uv run python hypotheses/H03-self-excited-criticality/analysis/summarize.py
"""
from __future__ import annotations

import json

import numpy as np
import polars as pl
from scipy import stats

from common import DATA, write_provenance

F_GOALS = [2, 3, 5, 7, 11, 16, 31, 37]


def q(x, a):
    x = np.asarray(x, float)
    x = x[np.isfinite(x)]
    return float(np.quantile(x, a)) if len(x) else np.nan


def load_all():
    fits = pl.read_parquet(DATA / "period_fits.parquet")
    cv = pl.read_parquet(DATA / "period_cv.parquet")
    boot = pl.read_parquet(DATA / "period_boot.parquet") if (DATA / "period_boot.parquet").exists() else None
    return fits, cv, boot


def period_table(fits, cv, boot):
    def col(model, c, alias):
        return fits.filter(pl.col("model") == model).select("goal_no", "set", pl.col(c).alias(alias))

    sc = fits.filter(pl.col("model") == "M3_sc").select(
        "goal_no", "set",
        n_self_fast=pl.col("self_10") + pl.col("self_30") + pl.col("self_100") + pl.col("self_300"),
        n_cross_fast=(pl.col("cross_10") + pl.col("cross_30") + pl.col("cross_100") + pl.col("cross_300")) * (pl.col("m_bar") - 1),
        n_c_pair_fast=pl.col("cross_10") + pl.col("cross_30") + pl.col("cross_100") + pl.col("cross_300"))
    base = fits.filter(pl.col("model") == "M1_B2").select(
        "goal_no", "set", "mode", "regime", "n_days", "N_active", "hours", "n_events", "n", "tau_s",
        "n_prof_lo", "n_prof_hi", "ks_D", "ks_p", "ll", "exo_total")
    for model, c, alias in [("M1_B2_t30", "n", "n_t30"), ("M1_B2_t30", "tau_s", "tau_t30"),
                            ("M1_B2_t30", "n_prof_lo", "n_t30_prof_lo"), ("M1_B2_t30", "n_prof_hi", "n_t30_prof_hi"),
                            ("M1_B0", "n", "n_B0"), ("M1_B1", "n", "n_B1"), ("M1_B3_2h", "n", "n_B3_2h"),
                            ("M1_B3", "n", "n_B3"), ("M1_B2_noexo", "n", "n_noexo"),
                            ("M2_grid", "n", "n_grid"), ("M2_grid", "n_fast300", "n_grid_fast300"),
                            ("M2_grid", "tau_mean_s", "tau_grid"), ("M2_pl", "theta", "theta_pl"),
                            ("M2_pl", "n", "n_pl"),
                            ("M3_sc", "n_self", "n_self"), ("M3_sc", "n_cross", "n_cross"),
                            ("M3_sc", "n_c_pair", "n_c_pair"), ("M3_sc", "n", "rho_sc"),
                            ("M3_sc", "tau_self_s", "tau_self"), ("M3_sc", "tau_cross_s", "tau_cross"),
                            ("P_B2", "ll", "ll_P_B2"), ("P_B2", "ks_D", "ks_D_P"), ("P_B2", "ks_p", "ks_p_P"),
                            ("M1_B3", "ll", "ll_B3"), ("P_B3", "ll", "ll_P_B3"),
                            ("M3_sc", "ll", "ll_sc"), ("M3_self", "ll", "ll_self"), ("P_B2a", "ll", "ll_P_B2a"),
                            ("M2_grid", "ll", "ll_grid"), ("M2_pl", "ll", "ll_pl")]:
        base = base.join(col(model, c, alias), on=["goal_no", "set"], how="left")
    base = base.join(sc, on=["goal_no", "set"], how="left")
    # in-sample LR / AIC: Hawkes adds (alpha, beta) = 2 params over the Poisson null with the same baseline
    base = base.with_columns(
        dAIC_B2=-2 * (pl.col("ll") - pl.col("ll_P_B2")) + 4,
        dAIC_B3=-2 * (pl.col("ll_B3") - pl.col("ll_P_B3")) + 4,
        dAIC_cross=-2 * (pl.col("ll_sc") - pl.col("ll_self")) + 12,      # 6 cross weights
        dAIC_grid_vs_exp=-2 * (pl.col("ll_grid") - pl.col("ll")) + 2 * (6 - 2),
    )
    # CV: held-out log-lik per test event, Hawkes minus null with the same baseline
    cvs = cv.group_by("goal_no", "set", "model").agg(pl.col("ll_test").sum(), pl.col("n_test").sum())
    piv = cvs.pivot(on="model", index=["goal_no", "set"], values="ll_test")
    nt = cvs.filter(pl.col("model") == "P_B2").select("goal_no", "set", pl.col("n_test"))
    piv = piv.join(nt, on=["goal_no", "set"])
    piv = piv.select("goal_no", "set", "n_test",
                     cv_B2=(pl.col("M1_B2") - pl.col("P_B2")) / pl.col("n_test"),
                     cv_B2_t30=(pl.col("M1_B2_t30") - pl.col("P_B2")) / pl.col("n_test"),
                     cv_B1=(pl.col("M1_B1") - pl.col("P_B1")) / pl.col("n_test"),
                     cv_B3=(pl.col("M1_B3") - pl.col("P_B3")) / pl.col("n_test"),
                     cv_B3_2h=(pl.col("M1_B3_2h") - pl.col("P_B3_2h")) / pl.col("n_test"),
                     cv_grid_vs_exp=(pl.col("M2_grid") - pl.col("M1_B2")) / pl.col("n_test"),
                     cv_cross=(pl.col("M3_sc") - pl.col("M3_self")) / pl.col("n_test"),
                     cv_self_vs_P=(pl.col("M3_self") - pl.col("P_B2a")) / pl.col("n_test"))
    base = base.join(piv, on=["goal_no", "set"], how="left")
    if boot is not None:
        bs = boot.group_by("goal_no", "set", "model").agg(
            lo=pl.col("n").quantile(0.025), hi=pl.col("n").quantile(0.975), B=pl.len(),
            xlo=pl.col("n_cross").quantile(0.025), xhi=pl.col("n_cross").quantile(0.975),
            slo=pl.col("n_self").quantile(0.025), shi=pl.col("n_self").quantile(0.975),
            xflo=pl.col("n_cross_fast300").quantile(0.025), xfhi=pl.col("n_cross_fast300").quantile(0.975))
        for model, cols in [("M1_B2", {"lo": "n_boot_lo", "hi": "n_boot_hi", "B": "B_boot"}),
                            ("M1_B2_t30", {"lo": "n_t30_boot_lo", "hi": "n_t30_boot_hi"}),
                            ("M2_grid", {"lo": "n_grid_boot_lo", "hi": "n_grid_boot_hi"}),
                            ("M3_sc", {"xlo": "n_cross_boot_lo", "xhi": "n_cross_boot_hi",
                                       "slo": "n_self_boot_lo", "shi": "n_self_boot_hi",
                                       "xflo": "n_cross_fast_boot_lo", "xfhi": "n_cross_fast_boot_hi"})]:
            sub = bs.filter(pl.col("model") == model).select("goal_no", "set", *[pl.col(k).alias(v) for k, v in cols.items()])
            base = base.join(sub, on=["goal_no", "set"], how="left")
    return base.sort("set", "goal_no")


def ols(y, X, names):
    X = np.column_stack([np.ones(len(y)), X])
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    resid = y - X @ beta
    dof = len(y) - X.shape[1]
    s2 = resid @ resid / dof
    se = np.sqrt(np.diag(s2 * np.linalg.inv(X.T @ X)))
    return {nm: {"coef": float(b), "se": float(e), "t": float(b / e), "p": float(2 * stats.t.sf(abs(b / e), dof))}
            for nm, b, e in zip(["const"] + names, beta, se)} | {"_dof": dof, "_R2": float(1 - resid @ resid / ((y - y.mean()) @ (y - y.mean())))}


def tests(tab, ncol="n", tag=""):
    out = {}
    for s in ("TALK", "ALL"):
        t = tab.filter((pl.col("set") == s) & (pl.col("goal_no") != 51))
        nF = t.filter(pl.col("mode") == "F")[ncol].to_numpy()
        nC = t.filter(pl.col("mode") == "C")[ncol].to_numpy()
        mw = stats.mannwhitneyu(nC, nF, alternative="greater")
        r = {"median_F": float(np.median(nF)), "n_F_ge_0.5": int((nF >= 0.5).sum()), "N_F": len(nF),
             "median_C": float(np.median(nC)), "N_C": len(nC), "MW_C_gt_F_p": float(mw.pvalue),
             "MW_U": float(mw.statistic),
             "median_by_mode": {m: float(np.median(t.filter(pl.col("mode") == m)[ncol].to_numpy()))
                                for m in ("F", "I", "K", "M", "C")}}
        r["P1_pass"] = r["median_F"] < 0.5 and r["n_F_ge_0.5"] <= 2
        r["P2_pass"] = r["median_C"] > r["median_F"] and r["MW_C_gt_F_p"] < 0.05
        r["P3_pass"] = r["median_C"] >= 0.7
        # P4 regression: n ~ log N + hours + regime + mode (F reference), #51 excluded
        modes = ["C", "I", "K", "M"]
        X = [np.log(t["N_active"].to_numpy()), t["hours"].to_numpy(),
             (t["regime"] == "II").to_numpy().astype(float), (t["regime"] == "III").to_numpy().astype(float)]
        X += [(t["mode"] == m).to_numpy().astype(float) for m in modes]
        reg = ols(t[ncol].to_numpy(), np.column_stack(X), ["logN", "hours", "regII", "regIII"] + [f"mode_{m}" for m in modes])
        r["P4_regression"] = reg
        r["P4_pass"] = reg["mode_C"]["coef"] > 0 and abs(reg["mode_C"]["t"]) >= 2
        # simple correlations with N and hours
        r["spearman_n_logN"] = [float(v) for v in stats.spearmanr(t[ncol].to_numpy(), t["N_active"].to_numpy())]
        r["spearman_n_hours"] = [float(v) for v in stats.spearmanr(t[ncol].to_numpy(), t["hours"].to_numpy())]
        out[s] = r
    # P7: ALL vs TALK
    w = tab.pivot(on="set", index="goal_no", values=ncol)
    out["P7_frac_ALL_gt_TALK"] = float((w["ALL"] > w["TALK"]).mean())
    out["P7_pass"] = out["P7_frac_ALL_gt_TALK"] > 0.5
    return out


def p6(tab):
    out = {}
    for s in ("TALK", "ALL"):
        t = tab.filter((pl.col("set") == s) & (pl.col("goal_no") != 51))
        xF = t.filter(pl.col("mode") == "F")["n_cross"].to_numpy()
        xC = t.filter(pl.col("mode") == "C")["n_cross"].to_numpy()
        sF = t.filter(pl.col("mode") == "F")["n_self"].to_numpy()
        sC = t.filter(pl.col("mode") == "C")["n_self"].to_numpy()
        fF = t.filter(pl.col("mode") == "F")["n_cross_fast"].to_numpy()
        fC = t.filter(pl.col("mode") == "C")["n_cross_fast"].to_numpy()
        out.setdefault(s + "_fast", {})
        out[s + "_fast"] = {"median_cross_fast_F": float(np.median(fF)), "median_cross_fast_C": float(np.median(fC)),
                            "MW_p": float(stats.mannwhitneyu(fC, fF, alternative="greater").pvalue),
                            "median_by_mode": {m: float(t.filter(pl.col("mode") == m)["n_cross_fast"].median())
                                               for m in ("F", "I", "K", "M", "C")},
                            "spearman_vs_N": [float(v) for v in stats.spearmanr(t["n_cross_fast"].to_numpy(), t["N_active"].to_numpy())],
                            "spearman_pair_vs_N": [float(v) for v in stats.spearmanr(t["n_c_pair_fast"].to_numpy(), t["N_active"].to_numpy())],
                            "spearman_self_fast_vs_N": [float(v) for v in stats.spearmanr(t["n_self_fast"].to_numpy(), t["N_active"].to_numpy())]}
        out[s] = {"median_cross_F": float(np.median(xF)), "median_cross_C": float(np.median(xC)),
                  "MW_p": float(stats.mannwhitneyu(xC, xF, alternative="greater").pvalue),
                  "median_self_F": float(np.median(sF)), "median_self_C": float(np.median(sC)),
                  "frac_cross_of_rho_median": float(np.median(t["n_cross"].to_numpy() / np.maximum(t["rho_sc"].to_numpy(), 1e-9))),
                  "P6_pass": float(np.median(xC)) > float(np.median(xF))}
    return out


def guard_summary():
    p = DATA / "synthetic_guard.parquet"
    if not p.exists():
        return None, None
    g = pl.read_parquet(p)
    s = g.group_by("set", "scenario", "model").agg(
        median=pl.col("n_hat").median(), q10=pl.col("n_hat").quantile(0.1), q90=pl.col("n_hat").quantile(0.9),
        mean_err=(pl.col("n_hat") - pl.col("n_true")).mean(), n_true=pl.col("n_true").first(), fits=pl.len(),
        frac_within_0p1=((pl.col("n_hat") - pl.col("n_true")).abs() <= 0.1).mean()).sort("set", "scenario", "model")
    return g, s


def rolling_summary():
    p = DATA / "rolling51.parquet"
    if not p.exists():
        return None
    r = pl.read_parquet(p)
    out = {}
    rb = pl.read_parquet(DATA / "rolling51_boot.parquet") if (DATA / "rolling51_boot.parquet").exists() else None
    for s in ("TALK", "ALL"):
        blk = r.filter((pl.col("kind") == "block") & (pl.col("set") == s))
        b1 = blk.filter(pl.col("model") == "M1_B2").sort("w0")
        b3 = blk.filter(pl.col("model") == "M3_sc").sort("w0")
        rho = stats.spearmanr(b1["n"].to_numpy(), b1["N_active"].to_numpy())
        rho_x = stats.spearmanr(b3["n_cross"].to_numpy(), b3["N_active"].to_numpy())
        rows = []
        for row in b1.iter_rows(named=True):
            ci = (np.nan, np.nan)
            if rb is not None:
                bb = rb.filter((pl.col("set") == s) & (pl.col("w0") == row["w0"]) & (pl.col("model") == "M1_B2"))["n"].to_numpy()
                ci = (q(bb, 0.025), q(bb, 0.975))
            xr = b3.filter(pl.col("w0") == row["w0"])
            rows.append({"first_date": row["first_date"], "N_active": row["N_active"], "n": row["n"],
                         "ci": ci, "tau_s": row["tau_s"], "n_self": xr["n_self"][0], "n_cross": xr["n_cross"][0]})
        roll = r.filter((pl.col("kind") == "rolling") & (pl.col("set") == s) & (pl.col("model") == "M1_B2")).sort("w0")
        rho_roll = stats.spearmanr(roll["n"].to_numpy(), roll["N_active"].to_numpy())
        last = b1["n"].to_numpy()[-2:]
        out[s] = {"blocks": rows, "spearman_block": [float(rho.statistic), float(rho.pvalue)],
                  "spearman_block_cross": [float(rho_x.statistic), float(rho_x.pvalue)],
                  "spearman_rolling_(autocorrelated)": [float(rho_roll.statistic), float(rho_roll.pvalue)],
                  "N_range": [float(roll["N_active"].min()), float(roll["N_active"].max())],
                  "n_range": [float(roll["n"].min()), float(roll["n"].max())],
                  "last_blocks_n": [float(v) for v in last],
                  "P5_pass": bool(rho.statistic > 0 and rho.pvalue < 0.05 and np.all(last >= 0.9))}
    return out


def cascade_summary(tab):
    p = DATA / "cascades.parquet"
    if not p.exists():
        return None
    c = pl.read_parquet(p)
    out = {}
    # reconstructed: tail exponent (discrete MLE approx, s >= smin) pooled by n class
    rec = c.filter(pl.col("source") == "reconstructed").join(
        tab.select("goal_no", "set", "n"), on=["goal_no", "set"])
    rec = rec.with_columns(ncls=pl.when(pl.col("n") < 0.5).then(pl.lit("n<0.5"))
                           .when(pl.col("n") < 0.65).then(pl.lit("0.5-0.65")).otherwise(pl.lit(">=0.65")))
    for (s, cls), sub in rec.group_by("set", "ncls"):
        sizes = np.repeat(sub["size"].to_numpy(), sub["count"].to_numpy())
        res = {"N_cascades": int(len(sizes)), "mean": float(sizes.mean()), "max": int(sizes.max()),
               "P(s>=10)": float((sizes >= 10).mean())}
        for smin in (2, 5):
            x = sizes[sizes >= smin]
            if len(x) > 50:
                res[f"alpha_mle_smin{smin}"] = float(1 + len(x) / np.sum(np.log(x / (smin - 0.5))))
        out[f"reconstructed/{s}/{cls}"] = res
    # bursts: data vs sims (pooled across periods)
    for (s, gap), sub in c.filter(pl.col("source") != "reconstructed").group_by("set", "gap"):
        r = {}
        for src in ("data", "sim_hawkes", "sim_poisson"):
            x = sub.filter(pl.col("source") == src)
            sizes = np.repeat(x["size"].to_numpy(), x["count"].to_numpy())
            r[src] = {"mean": float(sizes.mean()), "P(s>=10)": float((sizes >= 10).mean()),
                      "P(s>=30)": float((sizes >= 30).mean()), "q99": float(np.quantile(sizes, 0.99))}
        out[f"bursts/{s}/gap{int(gap)}"] = r
    # per-period: is the data burst tail closer to Hawkes or Poisson simulation?
    per = []
    for (g, s, gap), sub in c.filter(pl.col("source") != "reconstructed").group_by("goal_no", "set", "gap"):
        v = {}
        for src in ("data", "sim_hawkes", "sim_poisson"):
            x = sub.filter(pl.col("source") == src)
            sizes = np.repeat(x["size"].to_numpy(), x["count"].to_numpy())
            v[src] = (sizes >= 10).mean()
        per.append({"goal_no": g, "set": s, "gap": gap, **v})
    per = pl.DataFrame(per)
    out["burst_tail_closer_to_hawkes_frac"] = {
        f"{s}/gap{int(gap)}": float((((sub["data"] - sub["sim_hawkes"]).abs()) < ((sub["data"] - sub["sim_poisson"]).abs())).mean())
        for (s, gap), sub in per.group_by("set", "gap")}
    out["burst_data_minus_hawkes_median"] = {
        f"{s}/gap{int(gap)}": float((sub["data"] - sub["sim_hawkes"]).median()) for (s, gap), sub in per.group_by("set", "gap")}
    return out


def jitter_summary():
    p = DATA / "jitter_test.parquet"
    if not p.exists():
        return None, None
    j = pl.read_parquet(p)
    rows = []
    for (g, st), sub in j.group_by("goal_no", "set"):
        r = {"goal_no": g, "set": st}
        real = sub.filter(pl.col("kind") == "real")
        for m, col, key in [("M1_B2_t5", "n", "t5"), ("M2_grid", "n_fast300", "grid_fast")]:
            rv = real.filter(pl.col("model") == m)[col][0]
            r[f"{key}_real"] = rv
            for kind in ("jit600", "jit120"):
                v = sub.filter((pl.col("kind") == kind) & (pl.col("model") == m))[col].to_numpy()
                r[f"{key}_{kind}_mean"] = float(v.mean()); r[f"{key}_{kind}_max"] = float(v.max())
        rv = real.filter(pl.col("model") == "M3_sc")
        sh = sub.filter(pl.col("kind") == "shift")
        for col in ("n_cross_fast300", "n_cross", "n_self_fast300"):
            r[f"{col}_real"] = rv[col][0]
            r[f"{col}_shift_mean"] = float(sh[col].mean()); r[f"{col}_shift_max"] = float(sh[col].max())
        rows.append(r)
    t = pl.DataFrame(rows).sort("set", "goal_no")
    out = {}
    for st in ("TALK", "ALL"):
        x = t.filter(pl.col("set") == st)
        o = {}
        for key in ("t5", "grid_fast"):
            for kind in ("jit600", "jit120"):
                d = (x[f"{key}_real"] - x[f"{key}_{kind}_mean"]).to_numpy()
                o[f"{key}_{kind}"] = {"median_real": float(x[f"{key}_real"].median()),
                                      "median_surrogate": float(x[f"{key}_{kind}_mean"].median()),
                                      "median_excess": float(np.median(d)),
                                      "frac_real_gt_all_surrogates": float((x[f"{key}_real"] > x[f"{key}_{kind}_max"]).mean()),
                                      "wilcoxon_p_greater": float(stats.wilcoxon(d, alternative="greater").pvalue)}
        for col in ("n_cross_fast300", "n_cross"):
            d = (x[f"{col}_real"] - x[f"{col}_shift_mean"]).to_numpy()
            o[f"{col}_shift"] = {"median_real": float(x[f"{col}_real"].median()),
                                 "median_surrogate": float(x[f"{col}_shift_mean"].median()),
                                 "median_excess": float(np.median(d)),
                                 "frac_real_gt_all_surrogates": float((x[f"{col}_real"] > x[f"{col}_shift_max"]).mean()),
                                 "wilcoxon_p_greater": float(stats.wilcoxon(d, alternative="greater").pvalue)}
        out[st] = o
    return t, out


def dersimonian_laird(est, se):
    est, se = np.asarray(est, float), np.asarray(se, float)
    ok = np.isfinite(est) & np.isfinite(se) & (se > 0)
    est, se = est[ok], se[ok]
    k = len(est)
    if k < 2:
        return None
    w = 1 / se ** 2
    mu_f = (w * est).sum() / w.sum()
    Q = float((w * (est - mu_f) ** 2).sum())
    df = k - 1
    tau2 = max(0.0, (Q - df) / (w.sum() - (w ** 2).sum() / w.sum()))
    wr = 1 / (se ** 2 + tau2)
    mu = float((wr * est).sum() / wr.sum())
    I2 = max(0.0, (Q - df) / Q) if Q > 0 else 0.0
    shr = (est / se ** 2 + (mu / tau2 if tau2 > 0 else 0)) / (1 / se ** 2 + (1 / tau2 if tau2 > 0 else np.inf))
    shr = np.where(tau2 > 0, shr, mu)
    return {"k": k, "mu_RE": mu, "se_mu": float(np.sqrt(1 / wr.sum())), "tau": float(np.sqrt(tau2)), "Q": Q, "df": df,
            "p_Q": float(stats.chi2.sf(Q, df)), "I2": float(I2), "shrunk": shr, "mask": ok}


def segment_summary(tab):
    p = DATA / "segments.parquet"
    if not p.exists():
        return None, None
    sg = pl.read_parquet(p)
    sb = pl.read_parquet(DATA / "segments_boot.parquet") if (DATA / "segments_boot.parquet").exists() else None
    m1 = sg.filter(pl.col("model") == "M1_B2").select(
        "goal_no", "seg", "set", "mode", "regime", "first_date", "last_date", "n_days", "N_active", "hours",
        "n_events", "n", "tau_s", "n_prof_lo", "n_prof_hi", pl.col("ll").alias("ll_H"))
    pB = sg.filter(pl.col("model") == "P_B2").select("goal_no", "seg", "set", pl.col("ll").alias("ll_P"))
    m3 = sg.filter(pl.col("model") == "M3_sc").select(
        "goal_no", "seg", "set", "n_self", "n_cross",
        n_self_fast=pl.col("self_10") + pl.col("self_30") + pl.col("self_100") + pl.col("self_300"),
        n_cross_fast=(pl.col("cross_10") + pl.col("cross_30") + pl.col("cross_100") + pl.col("cross_300")) * (pl.col("m_bar") - 1))
    t = m1.join(pB, on=["goal_no", "seg", "set"], how="left").join(m3, on=["goal_no", "seg", "set"], how="left")
    t = t.with_columns(dAIC=-2 * (pl.col("ll_H") - pl.col("ll_P")) + 4)
    if sb is not None and sb.height:
        bs = sb.group_by("goal_no", "seg", "set").agg(se_boot=pl.col("n").std(), boot_lo=pl.col("n").quantile(0.025),
                                                       boot_hi=pl.col("n").quantile(0.975), B=pl.len())
        t = t.join(bs, on=["goal_no", "seg", "set"], how="left")
    else:
        t = t.with_columns(se_boot=pl.lit(None, pl.Float64), boot_lo=pl.lit(None, pl.Float64), boot_hi=pl.lit(None, pl.Float64))
    se_prof = (pl.col("n_prof_hi") - pl.col("n_prof_lo")) / 3.92
    t = t.with_columns(se_prof=pl.when(pl.col("n_prof_hi").is_finite()).then(se_prof).otherwise(None))
    # SE: day-level bootstrap SD where available (>= 3 days), else profile-likelihood width (event-level, too small)
    t = t.with_columns(se=pl.when(pl.col("se_boot").is_not_null() & (pl.col("se_boot") > 0))
                       .then(pl.max_horizontal("se_boot", "se_prof")).otherwise("se_prof"),
                       se_kind=pl.when(pl.col("se_boot").is_not_null()).then(pl.lit("boot")).otherwise(pl.lit("profile")))
    out = {"n_segments": int(t.filter(pl.col("set") == "TALK").height),
           "n_split_periods": int(t.filter(pl.col("set") == "TALK").group_by("goal_no").len().filter(pl.col("len") > 1).height)}
    shrunk_rows = []
    within = {}
    for (g, st), sub in t.sort("seg").group_by("goal_no", "set"):
        if sub.height < 2:
            continue
        r = dersimonian_laird(sub["n"].to_numpy(), sub["se"].to_numpy())
        if r is None:
            continue
        segs = sub["seg"].to_numpy()[r["mask"]]
        for sgi, v in zip(segs, r["shrunk"]):
            shrunk_rows.append({"goal_no": g, "set": st, "seg": int(sgi), "n_shrunk": float(v), "n_period_RE": r["mu_RE"]})
        within[f"{st}/#{g}"] = {k: v for k, v in r.items() if k not in ("shrunk", "mask")}
    if shrunk_rows:
        t = t.join(pl.DataFrame(shrunk_rows), on=["goal_no", "set", "seg"], how="left")
    out["within_period"] = within
    for st in ("TALK", "ALL"):
        w = {k: v for k, v in within.items() if k.startswith(st)}
        out[f"within_{st}_summary"] = {"periods": len(w), "median_I2": float(np.median([v["I2"] for v in w.values()])) if w else None,
                                       "frac_pQ_lt_0.05": float(np.mean([v["p_Q"] < 0.05 for v in w.values()])) if w else None}
    # across periods (period-level fits, bootstrap SE when available)
    across = {}
    for st in ("TALK", "ALL"):
        x = tab.filter((pl.col("set") == st) & (pl.col("goal_no") != 51)).sort("goal_no")
        se = ((x["n_boot_hi"] - x["n_boot_lo"]) / 3.92).to_numpy() if "n_boot_hi" in x.columns else None
        if se is None:
            continue
        se = np.where(np.isfinite(se) & (se > 0), se, ((x["n_prof_hi"] - x["n_prof_lo"]) / 3.92).to_numpy())
        r = dersimonian_laird(x["n"].to_numpy(), se)
        across[st] = {"all_periods": {k: v for k, v in r.items() if k not in ("shrunk", "mask")}}
        for m in ("F", "C", "I"):
            mm = (x["mode"] == m).to_numpy()
            rr = dersimonian_laird(x["n"].to_numpy()[mm], se[mm])
            if rr:
                across[st][f"mode_{m}"] = {k: v for k, v in rr.items() if k not in ("shrunk", "mask")}
        # adjacent non-holdout periods in time order
        n_ = x["n"].to_numpy(); z = np.diff(n_) / np.sqrt(se[1:] ** 2 + se[:-1] ** 2)
        z = z[np.isfinite(z)]
        across[st]["adjacent"] = {"pairs": int(len(z)), "frac_|z|>1.96": float((np.abs(z) > 1.96).mean()),
                                  "median_|dn|": float(np.median(np.abs(np.diff(n_))))}
    out["across_periods"] = across
    # mode tests on segment points and on period RE means
    for st in ("TALK", "ALL"):
        x = t.filter((pl.col("set") == st) & (pl.col("goal_no") != 51))
        nF = x.filter(pl.col("mode") == "F")["n"].to_numpy(); nC = x.filter(pl.col("mode") == "C")["n"].to_numpy()
        xF = x.filter(pl.col("mode") == "F")["n_cross_fast"].drop_nulls().to_numpy()
        xC = x.filter(pl.col("mode") == "C")["n_cross_fast"].drop_nulls().to_numpy()
        out[f"mode_segments_{st}"] = {
            "median_F": float(np.median(nF)), "median_C": float(np.median(nC)), "k_F": len(nF), "k_C": len(nC),
            "MW_C_gt_F_p": float(stats.mannwhitneyu(nC, nF, alternative="greater").pvalue),
            "median_cross_fast_F": float(np.median(xF)), "median_cross_fast_C": float(np.median(xC)),
            "MW_cross_C_gt_F_p": float(stats.mannwhitneyu(xC, xF, alternative="greater").pvalue),
            "spearman_n_N": [float(v) for v in stats.spearmanr(x["n"].to_numpy(), x["N_active"].to_numpy())]}
        s51 = t.filter((pl.col("set") == st) & (pl.col("goal_no") == 51)).sort("seg")
        rho = stats.spearmanr(s51["n"].to_numpy(), s51["N_active"].to_numpy())
        ok = s51["se"].is_finite() & s51["se"].is_not_null()
        xx = s51.filter(ok)
        wls = np.polyfit(xx["N_active"].to_numpy(), xx["n"].to_numpy(), 1, w=1 / xx["se"].to_numpy())
        out[f"seg51_{st}"] = {"spearman_n_N": [float(rho.statistic), float(rho.pvalue)], "wls_slope_per_agent": float(wls[0]),
                              "N_range": [float(s51["N_active"].min()), float(s51["N_active"].max())],
                              "n_by_seg": [(r["seg"], r["first_date"], round(r["N_active"], 1), round(r["n"], 3),
                                            None if r["se"] is None else round(r["se"], 3)) for r in s51.iter_rows(named=True)]}
    t.write_parquet(DATA / "segment_table.parquet", compression="zstd")
    return t, out


def fmt(x, d=2):
    if x is None or (isinstance(x, float) and not np.isfinite(x)):
        return "–" if not (isinstance(x, float) and np.isinf(x)) else "∞"
    return f"{x:.{d}f}"


def main():
    fits, cv, boot = load_all()
    tab = period_table(fits, cv, boot)
    tab.write_parquet(DATA / "period_table.parquet", compression="zstd")
    res = {"primary_M1_B2": tests(tab, "n"), "variant_M1_B2_t30": tests(tab, "n_t30"),
           "variant_M2_grid_fast300": tests(tab, "n_grid_fast300"), "P6": p6(tab)}
    for c in ("n_B0", "n_B1", "n", "n_t30", "n_B3_2h", "n_B3", "n_noexo", "n_grid"):
        res.setdefault("ladder_median", {})[c] = {s: float(tab.filter(pl.col("set") == s)[c].median()) for s in ("TALK", "ALL")}
    res["cv"] = {s: {c: {"median": float(tab.filter(pl.col("set") == s)[c].drop_nulls().median()),
                         "frac_pos": float((tab.filter(pl.col("set") == s)[c].drop_nulls() > 0).mean()),
                         "N": int(tab.filter(pl.col("set") == s)[c].drop_nulls().len())}
                     for c in ("cv_B2", "cv_B2_t30", "cv_B1", "cv_B3", "cv_B3_2h", "cv_grid_vs_exp", "cv_cross", "cv_self_vs_P")}
                 for s in ("TALK", "ALL")}
    res["aic"] = {s: {c: {"median": float(tab.filter(pl.col("set") == s)[c].median()),
                          "frac_hawkes_better": float((tab.filter(pl.col("set") == s)[c] < 0).mean())}
                      for c in ("dAIC_B2", "dAIC_B3", "dAIC_cross", "dAIC_grid_vs_exp")} for s in ("TALK", "ALL")}
    res["ks"] = {s: {"median_D_hawkes": float(tab.filter(pl.col("set") == s)["ks_D"].median()),
                     "median_D_poisson": float(tab.filter(pl.col("set") == s)["ks_D_P"].median()),
                     "frac_D_hawkes_lt_poisson": float((tab.filter(pl.col("set") == s)["ks_D"] < tab.filter(pl.col("set") == s)["ks_D_P"]).mean()),
                     "frac_hawkes_ks_p_gt_0.05": float((tab.filter(pl.col("set") == s)["ks_p"] > 0.05).mean()),
                     "frac_poisson_ks_p_gt_0.05": float((tab.filter(pl.col("set") == s)["ks_p_P"] > 0.05).mean())}
                 for s in ("TALK", "ALL")}
    g, gs = guard_summary()
    if gs is not None:
        res["guard"] = gs.to_dicts()
    jt, jres = jitter_summary()
    if jt is not None:
        jt.write_parquet(DATA / "jitter_table.parquet", compression="zstd")
        res["jitter"] = jres
    st_, sres = segment_summary(tab)
    if sres is not None:
        res["segments"] = sres
    res["rolling51"] = rolling_summary()
    res["cascades"] = cascade_summary(tab)
    (DATA / "summary.json").write_text(json.dumps(res, indent=1, default=str))
    write_provenance({"period_table.parquet": {"built_by": "analysis/summarize.py"},
                      "summary.json": {"built_by": "analysis/summarize.py"}})

    # ---- markdown
    pl.Config.set_tbl_rows(100)
    for s in ("TALK", "ALL"):
        print(f"\n### {s}\n")
        print("| # | mode | reg | d | N | h | events | n (B2) | 95% boot | 95% prof | τ s | n τ≤30m | n B0 | n B3-2h | n B3 | n_self | n_cross (≤300 s) | CV Δℓ/ev | KS D H/P |")
        print("|" + "---|" * 19)
        for r in tab.filter(pl.col("set") == s).iter_rows(named=True):
            print(f"| {r['goal_no']} | {r['mode']} | {r['regime']} | {r['n_days']} | {r['N_active']:.1f} | {r['hours']:.0f} | {r['n_events']} | "
                  f"**{fmt(r['n'])}** | {fmt(r.get('n_boot_lo'))}–{fmt(r.get('n_boot_hi'))} | {fmt(r['n_prof_lo'])}–{fmt(r['n_prof_hi'])} | "
                  f"{r['tau_s']:.0f} | {fmt(r['n_t30'])} | {fmt(r['n_B0'])} | {fmt(r['n_B3_2h'])} | {fmt(r['n_B3'])} | {fmt(r['n_self'])} | {fmt(r['n_cross'], 2)} ({fmt(r['n_cross_fast'], 2)}) | "
                  f"{fmt(r['cv_B2'], 3)} | {fmt(r['ks_D'], 3)}/{fmt(r['ks_D_P'], 3)} |")
    print(json.dumps({k: v for k, v in res.items() if k not in ("guard",)}, indent=1, default=str)[:20000])
    if gs is not None:
        print(gs)


if __name__ == "__main__":
    main()
