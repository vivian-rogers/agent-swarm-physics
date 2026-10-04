"""H121 summary: period pooling and verdicts, regime tests (P1-P6), natives (NE14, NE43, NE42), figures, estimates
rows and period READMEs.

    uv run python hypotheses/H121-daily-boot-quench/analysis/summarize.py [--no-estimates] [--no-readmes]
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "2")

import argparse  # noqa: E402
import json  # noqa: E402
import sys  # noqa: E402
from pathlib import Path  # noqa: E402

import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h121lib as L  # noqa: E402

ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "infra/shared"))
D = ROOT / "data/processed/H121-daily-boot-quench"
RES = D / "results"
HYP = ROOT / "hypotheses/H121-daily-boot-quench"
FIG = HYP / "figures"
COL = {"I": "#2a78d6", "II": "#eb6834", "III": "#1baf7a"}
MK = {"I": "o", "II": "s", "III": "^"}


def ci_txt(x, lo, hi, nd=2):
    f = f"{{:.{nd}f}}"
    return f"{f.format(x)} [{f.format(lo)}, {f.format(hi)}]"


def boot_draws(df: pl.DataFrame, K: int, B: int, seed: int):
    rng = np.random.default_rng(seed)
    by_day = df["day"].n_unique() >= 4
    t, A = [], []
    for _ in range(B):
        f = L.curve_fit_df(L.resample(df, rng, by_day), K)
        if f:
            t.append(f["tau"]); A.append(f["A"])
    return np.array(t), np.array(A)


def load_calls(units, day_offset=True):
    parts = []
    for j, u in enumerate(units):
        d = pl.read_parquet(D / "calls" / f"{u}.parquet")
        parts.append(d.with_columns((pl.col("day").cast(pl.Int32) + 100 * j).alias("day")))
    return pl.concat(parts)


def period_table(U: pl.DataFrame) -> pl.DataFrame:
    rows = []
    for (g,), s in U.filter(pl.col("ok")).group_by(["goal_no"], maintain_order=True):
        lt, st = np.log(s["tau"].to_numpy()), s["ln_tau_se"].to_numpy()
        lk, sk = np.log(np.clip(s["K"].to_numpy(), 1e-6, None)), s["ln_K_se"].to_numpy()
        mt, set_, _ = L.re_pool(lt, np.where(np.isfinite(st) & (st > 0), st, 1.0))
        mk, sek, _ = L.re_pool(lk, np.where(np.isfinite(sk) & (sk > 0), sk, 1.0))
        tau, tlo, thi = np.exp(mt), np.exp(mt - 1.96 * set_), np.exp(mt + 1.96 * set_)
        K, klo, khi = np.exp(mk), np.exp(mk - 1.96 * sek), np.exp(mk + 1.96 * sek)
        cvg = float(np.nanmedian(s["cv_gain"].to_numpy()))
        nad = int(s["n_agentdays"].sum())
        if nad < 8 or thi / tlo > 10:
            v = "descriptive"
        elif klo > 2 or khi < 0.5:
            v = "failed"
        elif 0.5 <= K <= 2 and cvg < 0.10:
            v = "supported"
        else:
            v = "mixed"
        rows.append({"goal_no": g, "regime": "/".join(sorted(set(s["regime"].to_list()))), "units": ", ".join(s["unit_id"].to_list()),
                     "n_units": s.height, "n_agentdays": nad, "N": float(s["N_mean"].mean()), "tau": tau, "tau_lo": tlo,
                     "tau_hi": thi, "K": K, "K_lo": klo, "K_hi": khi, "rho": float(s["rho"].median()),
                     "tau0": float(s["tau0"].median()), "tau_pred": float(s["tau_pred"].median()),
                     "K_ar": float(np.exp(np.nanmean(np.log(np.clip(s["K_ar"].to_numpy(), 1e-6, None))))),
                     "g_lag": float(s["g_lag"].median()), "cv_gain": cvg,
                     "tau_wall_min": float(np.nanmedian(s["tau_wall_min"].to_numpy())) if "tau_wall_min" in s.columns else np.nan,
                     "A": float(s["A"].median()), "minf": float(s["minf"].median()), "verdict": v,
                     "ln_tau": mt, "ln_tau_se": set_})
    return pl.DataFrame(rows)


def natives(U: pl.DataFrame) -> dict:
    out = {}
    meta = pl.read_parquet(D / "unit_meta.parquet")
    gl = {r["unit_id"]: r for r in U.to_dicts()}
    # NE14: 35 + 36a (II) vs 36b + 36c (III)
    sides = {"II": ["35", "36a"], "III": ["36b", "36c"]}
    res = {}
    draws = {}
    for side, us in sides.items():
        df = load_calls(us)
        K = int(min(meta.filter(pl.col("unit_id").is_in(us))["K_max"]))
        g = float(np.mean([gl[u]["g_lag"] for u in us]))
        e = L.unit_estimate(df, K, g, 0.05, B=200, seed=3)
        t, A = boot_draws(df, K, 200, 4)
        draws[side] = (t, A)
        res[side] = {k: e[k] for k in ("tau", "tau_lo", "tau_hi", "A", "rho", "tau0", "tau_pred", "K", "K_lo", "K_hi")} | {"g": g, "K_max": K,
                     "n_agentdays": df.select(pl.struct("agent", "day").n_unique()).item()}
    n = min(len(draws["II"][0]), len(draws["III"][0]))
    rr = draws["III"][0][:n] / draws["II"][0][:n]
    res["ratio_III_II"] = [float(res["III"]["tau"] / res["II"]["tau"]), float(np.percentile(rr, 2.5)), float(np.percentile(rr, 97.5))]
    r = res["ratio_III_II"]
    big = abs(np.log(r[0])) > np.log(1.5)
    small = abs(np.log(r[0])) < np.log(1.25) and all(0.5 <= res[s]["K"] <= 2 for s in ("II", "III"))
    res["verdict_expectation"] = "supported" if big and all(res[s]["K"] > 2 for s in ("II", "III")) else ("failed" if small else "mixed")
    out["NE14"] = res
    # NE43: 51f vs the first 5 days of 51g
    f = pl.read_parquet(D / "calls" / "51f.parquet")
    g51 = pl.read_parquet(D / "calls" / "51g.parquet")
    first5 = sorted(g51["pt_date"].unique().to_list())[:5]
    g5 = g51.filter(pl.col("pt_date").is_in(first5))
    K = int(min(meta.filter(pl.col("unit_id").is_in(["51f", "51g"]))["K_max"]))
    res = {}
    dr = {}
    for nm, df, u in (("before", f, "51f"), ("after", g5, "51g")):
        e = L.unit_estimate(df, K, gl[u]["g_lag"], 0.03, B=200, seed=5)
        dr[nm] = boot_draws(df, K, 200, 6)
        res[nm] = {k: e[k] for k in ("tau", "tau_lo", "tau_hi", "A", "minf", "K", "K_lo", "K_hi")} | {"m0": float(df.filter(pl.col("k") == 0)["Y"].mean()), "days": sorted(df["pt_date"].unique().to_list())}
    n = min(len(dr["before"][0]), len(dr["after"][0]))
    rt = dr["after"][0][:n] / dr["before"][0][:n]
    ra = dr["after"][1][:n] / dr["before"][1][:n]
    res["tau_ratio"] = [res["after"]["tau"] / res["before"]["tau"], float(np.percentile(rt, 2.5)), float(np.percentile(rt, 97.5))]
    res["A_ratio"] = [res["after"]["A"] / res["before"]["A"], float(np.percentile(ra, 2.5)), float(np.percentile(ra, 97.5))]
    res["P_NE43a"] = bool(0.67 <= res["tau_ratio"][0] <= 1.5)
    res["P_NE43b"] = bool(res["A_ratio"][0] <= 0.8)
    out["NE43"] = res
    # NE42
    res = {}
    for u in ("39", "40", "41"):
        x = gl[u]
        res[u] = {"tau": x["tau"], "tau_lo": x["tau_lo"], "tau_hi": x["tau_hi"], "tau0": x["tau0"], "g_lag": x["g_lag"],
                  "tau_over_tau0": x["tau"] / x["tau0"], "lo": x["tau_lo"] / x["tau0"], "hi": x["tau_hi"] / x["tau0"],
                  "pred_ratio": 1 / (1 - x["g_lag"]), "K": x["K"]}
    o = res["40"]["tau_over_tau0"] < min(res["39"]["tau_over_tau0"], res["41"]["tau_over_tau0"])
    against = res["40"]["lo"] > max(res["39"]["tau_over_tau0"], res["41"]["tau_over_tau0"])
    res["order_matches"] = bool(o)
    res["verdict"] = "supported" if o else ("failed" if against else "mixed")
    out["NE42"] = res
    return out


def late_contrast(U: pl.DataFrame) -> dict:
    out = {}
    for reg in ("I", "II", "III"):
        us = U.filter((pl.col("regime") == reg) & pl.col("ok"))["unit_id"].to_list()
        if not us:
            continue
        df = load_calls(us)
        ad = df.select("agent", "day", "cls").unique()
        nl, ns = int((ad["cls"] == 2).sum()), int((ad["cls"] == 1).sum())
        r = {"n_late": nl, "n_sync": ns}
        if nl >= 10:
            K = 200
            fl = L.curve_fit_df(df.filter(pl.col("cls") == 2), K)
            fs = L.curve_fit_df(df.filter(pl.col("cls") == 1), K)
            r.update(tau_late=fl["tau"] if fl else None, tau_sync=fs["tau"] if fs else None)
        r["testable"] = nl >= 30
        out[reg] = r
    return out


def collapse(U: pl.DataFrame, Dd: pl.DataFrame) -> dict:
    out = {}
    for reg in ("I", "II", "III"):
        s = U.filter((pl.col("regime") == reg) & pl.col("ok"))
        if not s.height:
            continue
        tr = float(s["tau"].median())
        dd = Dd.filter((pl.col("regime") == reg) & pl.col("resolved"))
        within = (np.abs(np.log(dd["tau"].to_numpy() / tr)) <= np.log(2)) if dd.height else np.array([])
        nk = dd.filter(~pl.col("kickoff_day"))
        wk = (np.abs(np.log(nk["tau"].to_numpy() / tr)) <= np.log(2)) if nk.height else np.array([])
        out[reg] = {"tau_regime": tr, "n_days": int(Dd.filter(pl.col("regime") == reg).height), "n_resolved": int(dd.height),
                    "share_within_x2": float(within.mean()) if len(within) else None,
                    "share_within_x2_nokick": float(wk.mean()) if len(wk) else None,
                    "holds": bool(len(within) >= 10 and within.mean() >= 0.5) if len(within) >= 10 else None,
                    "I2_median": float(np.nanmedian(s["I2_days"].to_numpy())),
                    "sd_ln_tau_days": float(np.std(np.log(dd["tau"].to_numpy()))) if dd.height > 2 else None}
        sb = s["sd_between_days"].drop_nans().drop_nulls().to_numpy() if "sd_between_days" in s.columns else np.array([])
        out[reg].update({"A1_n_units": int(len(sb)), "A1_sd_between_median": float(np.median(sb)) if len(sb) else None,
                         "A1_share_units_collapse": float(np.mean(sb <= np.log(2) / 1.96)) if len(sb) else None,
                         "A1_holds": bool(np.mean(sb <= np.log(2) / 1.96) >= 0.5) if len(sb) else None})
    return out


def phase_slope(P: pl.DataFrame) -> dict:
    s = P.filter((pl.col("regime") == "III"))
    x = -np.log(1 - np.clip(s["g_lag"].to_numpy(), -0.5, 0.99))
    y = s["ln_tau"].to_numpy() - np.log(s["tau0"].to_numpy())
    w = 1 / np.maximum(s["ln_tau_se"].to_numpy(), 0.05) ** 2
    X = np.c_[np.ones_like(x), x]
    W = np.diag(w)
    b = np.linalg.solve(X.T @ W @ X, X.T @ W @ y)
    rng = np.random.default_rng(0)
    bs = []
    for _ in range(2000):
        i = rng.integers(0, len(x), len(x))
        try:
            bs.append(np.linalg.solve(X[i].T @ np.diag(w[i]) @ X[i], X[i].T @ np.diag(w[i]) @ y[i])[1])
        except np.linalg.LinAlgError:
            pass
    se = float(np.std(bs))
    from scipy.stats import norm
    power = float(norm.cdf(1 / se - 1.96) + norm.cdf(-1 / se - 1.96)) if se > 0 else np.nan
    return {"slope": float(b[1]), "lo": float(np.percentile(bs, 2.5)), "hi": float(np.percentile(bs, 97.5)), "se": se,
            "power_slope1_vs0": power, "n_periods": len(x), "x_range": [float(x.min()), float(x.max())]}


def figures(U, P, Dd):
    FIG.mkdir(exist_ok=True)
    plt.rcParams.update({"font.size": 8, "axes.spines.top": False, "axes.spines.right": False})
    # 1. representative boot curves with fitted and predicted exponentials
    reps = [("27", "I"), ("35", "II"), ("51c", "III")]
    fig, axs = plt.subplots(1, 3, figsize=(7.0, 2.3), sharey=False)
    for ax, (u, reg) in zip(axs, reps):
        r = U.filter(pl.col("unit_id") == u).to_dicts()[0]
        df = pl.read_parquet(D / "calls" / f"{u}.parquet")
        K = int(r["K_max"])
        kc, m, n = L.binned_curve(df, K)
        ok = n > 0
        ax.plot(kc[ok] + 1, m[ok], MK[reg], color=COL[reg], ms=4, label="observed (log bins)")
        kk = np.geomspace(1, K + 1, 200) - 1
        ax.plot(kk + 1, r["minf"] + r["A"] * np.exp(-kk / r["tau"]), color="#0b0b0b", lw=1.5,
                label=f"fit τ = {r['tau']:.0f} calls")
        ax.plot(kk + 1, r["minf"] + r["A"] * np.exp(-kk / r["tau_pred"]), color="#85847e", lw=1.5, ls="--",
                label=f"Glauber τ₀/(1−g) = {r['tau_pred']:.1f}")
        ax.set_xscale("log")
        ax.set_xlabel("call index since boot k + 1")
        ax.set_title(f"unit {u} (regime {reg}, N {r['N_mean']:.0f})", fontsize=8)
        ax.legend(fontsize=6, frameon=False)
    axs[0].set_ylabel("talk share of calls m(k)")
    fig.tight_layout()
    fig.savefig(FIG / "boot_curves_col.pdf")
    fig.savefig(FIG / "boot_curves_col.png", dpi=150)
    plt.close(fig)
    # 2. K_boot per unit vs g_lag
    fig, ax = plt.subplots(figsize=(3.4, 2.6))
    ax.axhspan(0.5, 2, color="#ecebe6", label="kill band [0.5, 2]")
    for reg in ("I", "II", "III"):
        s = U.filter((pl.col("regime") == reg) & pl.col("ok"))
        y = s["K"].to_numpy()
        ax.errorbar(s["g_lag"].to_numpy(), y, yerr=[y - s["K_lo"].to_numpy(), s["K_hi"].to_numpy() - y], fmt=MK[reg],
                    ms=3.5, color=COL[reg], elinewidth=0.6, label=f"regime {reg} units")
    ax.axhline(1, color="#52514e", lw=0.8, ls="--")
    ax.set_yscale("log")
    ax.set_xlabel("H67 read-out gain g_lag (unit)")
    ax.set_ylabel("K_boot = τ_boot / τ_pred")
    ax.legend(fontsize=6, frameon=False, loc="lower center", bbox_to_anchor=(0.5, 1.0), ncol=2)
    fig.tight_layout()
    fig.savefig(FIG / "K_vs_glag_col.pdf")
    fig.savefig(FIG / "K_vs_glag_col.png", dpi=150)
    plt.close(fig)
    # 3. per-day tau relative to the regime tau (collapse)
    fig, ax = plt.subplots(figsize=(3.4, 2.4))
    for reg in ("I", "II", "III"):
        tr = float(U.filter((pl.col("regime") == reg) & pl.col("ok"))["tau"].median())
        dd = Dd.filter((pl.col("regime") == reg) & pl.col("resolved"))
        if dd.height:
            ax.hist(np.log2(dd["tau"].to_numpy() / tr), bins=np.arange(-5, 5.5, 0.5), histtype="step", lw=1.5,
                    color=COL[reg], label=f"regime {reg} ({dd.height} resolved days)")
    ax.axvspan(-1, 1, color="#ecebe6", zorder=0)
    ax.set_xlabel("log₂(τ_day / τ_regime)")
    ax.set_ylabel("days")
    ax.legend(fontsize=6, frameon=False)
    fig.tight_layout()
    fig.savefig(FIG / "collapse_col.pdf")
    fig.savefig(FIG / "collapse_col.png", dpi=150)
    plt.close(fig)


def figure_excess(U):
    """Post hoc: regime-pooled boot excess over the k = 20-60 plateau, with the Glauber prediction from k = 0."""
    ph = json.loads((RES / "posthoc.json").read_text())
    fig, axs = plt.subplots(1, 2, figsize=(7.0, 2.5))
    for reg in ("I", "II", "III"):
        us = U.filter((pl.col("regime") == reg) & pl.col("ok"))["unit_id"].to_list()
        df = load_calls(us).filter(pl.col("k") <= 240)
        g = df.group_by("k").agg(pl.col("Y").mean().alias("m")).sort("k")
        k, m = g["k"].to_numpy(), g["m"].to_numpy()
        r = ph["regimes"][reg]
        e = m - r["m_plat"]
        kb = L.log_bins(240)
        idx = np.searchsorted(kb, k, side="right") - 1
        eb = np.array([e[idx == i].mean() for i in range(len(kb) - 1)])
        kc = np.array([k[idx == i].mean() for i in range(len(kb) - 1)])
        axs[0].plot(kc + 1, eb / r["e0"], MK[reg], color=COL[reg], ms=4, label=f"regime {reg} (excess at k=0: {r['e0']:.2f})")
        kk = np.linspace(0, 10, 200)
        axs[0].plot(kk + 1, np.exp(-kk / r["tau_pred"]), color=COL[reg], lw=1.0, ls="--")
        axs[1].plot(kc + 1, (m[0:1].mean() * 0 + eb + r["m_plat"]) / r["m_ss"] - 1, MK[reg], color=COL[reg], ms=4,
                    label=f"regime {reg}")
    axs[0].axhline(0, color="#85847e", lw=0.6)
    axs[0].set_xscale("log"); axs[0].set_xlim(0.9, 250)
    axs[0].set_xlabel("call index since boot k + 1"); axs[0].set_ylabel("excess / excess at k = 0")
    axs[0].set_title("fast part: dashed = Glauber e^(−k/τ_pred)", fontsize=8)
    axs[0].legend(fontsize=6, frameon=False)
    axs[1].axhline(0, color="#85847e", lw=0.6)
    axs[1].set_xscale("log"); axs[1].set_xlim(0.9, 250); axs[1].set_ylim(-0.5, 1.5)
    axs[1].set_xlabel("call index since boot k + 1"); axs[1].set_ylabel("talk rate / steady state − 1")
    axs[1].set_title("slow part: excess over the steady state", fontsize=8)
    axs[1].legend(fontsize=6, frameon=False)
    fig.tight_layout()
    fig.savefig(FIG / "boot_excess_col.pdf")
    fig.savefig(FIG / "boot_excess_col.png", dpi=150)
    plt.close(fig)


def estimates(U, P, nat):
    import estimates as E
    rows = []
    for r in U.filter(pl.col("ok")).to_dicts():
        base = dict(period_unit=r["unit_id"], goal_no=r["goal_no"], role="replication", n=r["n_agentdays"],
                    n_kind="agent-days (boot replicas)", ci_level=0.95, ci_kind="percentile", channel="talk_call",
                    source="data/processed/H121-daily-boot-quench/results/units.parquet")
        rows.append({**base, "statistic": "boot_tau_calls", "estimate": r["tau"], "ci_lo": r["tau_lo"], "ci_hi": r["tau_hi"],
                     "method": "WLS single exponential on m(k), day-cluster bootstrap", "null": "Glauber tau0/(1-g_lag)"})
        rows.append({**base, "statistic": "boot_K_slowing", "estimate": r["K"], "ci_lo": r["K_lo"], "ci_hi": r["K_hi"],
                     "method": "tau_boot / [max(1,-1/ln rho_self)/(1-g_lag)]", "null": "K = 1 (kill outside [0.5, 2])"})
        rows.append({**base, "statistic": "rho_self_call", "estimate": r["rho"], "ci_lo": r["rho_lo"], "ci_hi": r["rho_hi"],
                     "method": "lag-1 autocorrelation of own talk across consecutive calls, block-centred steady state",
                     "null": "0 (no single-agent memory)"})
    for n_, side in (("NE14", "II"), ("NE14", "III")):
        x = nat["NE14"][side]
        rows.append(dict(period_unit="local:NE14-" + side, goal_no=36 if side == "III" else 35, role="native",
                         statistic="boot_tau_calls", estimate=x["tau"], ci_lo=x["tau_lo"], ci_hi=x["tau_hi"],
                         n=x["n_agentdays"], n_kind="agent-days", ci_level=0.95, ci_kind="percentile", channel="talk_call",
                         method="pooled boot curve, regime side of NE14", null="ratio within x1.25 (mean field)",
                         source="data/processed/H121-daily-boot-quench/results/natives.json"))
    for nm in ("before", "after"):
        x = nat["NE43"][nm]
        rows.append(dict(period_unit="local:NE43-" + nm, goal_no=51, role="native", statistic="boot_tau_calls",
                         estimate=x["tau"], ci_lo=x["tau_lo"], ci_hi=x["tau_hi"], n=len(x["days"]), n_kind="days",
                         ci_level=0.95, ci_kind="percentile", channel="talk_call", first_day=x["days"][0], last_day=x["days"][-1],
                         method="pooled boot curve around 2026-08-05", null="ratio in [0.67, 1.5]",
                         source="data/processed/H121-daily-boot-quench/results/natives.json"))
    E.write_estimates(rows, hypothesis="H121")
    return len(rows)


def readmes(U, P, nat, Dd):
    pdir = HYP / "goalperiod-subhypotheses"
    for r in P.to_dicts():
        f = pdir / f"G{r['goal_no']:02d}" / "README.md"
        if not f.exists():
            continue
        t = f.read_text()
        t = t.replace("**Verdict:** pending", f"**Verdict:** {r['verdict']}", 1)
        us = U.filter(pl.col("goal_no") == r["goal_no"])
        lines = ["| Unit | agent-days | K_max | τ_boot calls [95%] | ρ_self | τ₀ | g_lag | τ_pred | K_boot [95%] | K_AR | CV gain (2-exp) | resolved days |",
                 "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
        for x in us.to_dicts():
            if not x.get("ok"):
                lines.append(f"| {x['unit_id']} | {x['n_agentdays']} | {x['K_max']} | fit failed | | | | | | | | |")
                continue
            lines.append(f"| {x['unit_id']} | {x['n_agentdays']} | {x['K_max']} | {ci_txt(x['tau'], x['tau_lo'], x['tau_hi'], 1)} | "
                         f"{x['rho']:.3f} | {x['tau0']:.2f} | {x['g_lag']:.3f} | {x['tau_pred']:.2f} | {ci_txt(x['K'], x['K_lo'], x['K_hi'], 1)} | "
                         f"{x['K_ar']:.1f} | {x['cv_gain']:.3f} | {x['n_days_resolved']} |")
        res = (f"Period pool (random effects over units): **τ_boot = {ci_txt(r['tau'], r['tau_lo'], r['tau_hi'], 1)} calls**; "
               f"τ_pred (HH form, median over units) = {r['tau_pred']:.2f} calls; **K_boot = {ci_txt(r['K'], r['K_lo'], r['K_hi'], 1)}**; "
               f"m(0) − m_∞ amplitude A = {r['A']:+.3f}, m_∞ = {r['minf']:.3f}; one-exponential CV gain of the double exponential "
               f"(median) = {r['cv_gain']:.3f}.\n\n" + "\n".join(lines) +
               "\n\nData: `data/processed/H121-daily-boot-quench/results/units.parquet`, `days.parquet`.")
        if (RES / "posthoc.json").exists():
            ph = json.loads((RES / "posthoc.json").read_text())["periods"].get(str(r["goal_no"]))
            if ph:
                fmt = lambda v: "n/a" if v is None or not np.isfinite(v) else (f"{v:.2f}" if v < 1e3 else "∞")  # noqa: E731
                res += (f"\n\n*Post hoc (labelled; card \"Post hoc\")*: first-call excess over the k = 20–60 plateau "
                        f"e(0) = {fmt(ph['e0'])} [{fmt(ph['e0_lo'])}, {fmt(ph['e0_hi'])}]; fast relaxation τ_fast = −1/ln[e(1)/e(0)] = "
                        f"{fmt(ph['tau_fast'])} [{fmt(ph['tau_fast_lo'])}, {fmt(ph['tau_fast_hi'])}] calls (K_fast = {fmt(ph['K_fast'])}); "
                        f"slow excess over the steady state at k = 20–240: {fmt(ph['slow_excess'])} [{fmt(ph['slow_excess_lo'])}, {fmt(ph['slow_excess_hi'])}].")
        t = t.replace("## Result\n(pending)", "## Result\n" + res, 1)
        f.write_text(t)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-estimates", action="store_true")
    ap.add_argument("--no-readmes", action="store_true")
    a = ap.parse_args()
    U = pl.read_parquet(RES / "units.parquet")
    Dd = pl.read_parquet(RES / "days.parquet")
    P = period_table(U)
    P.write_parquet(RES / "periods.parquet")
    nat = natives(U)
    (RES / "natives.json").write_text(json.dumps(nat, indent=1, default=float))
    ok = U.filter(pl.col("ok"))
    reg = {}
    for rg in ("I", "II", "III"):
        s = ok.filter(pl.col("regime") == rg)
        if not s.height:
            continue
        lk, sk = np.log(np.clip(s["K"].to_numpy(), 1e-6, None)), s["ln_K_se"].to_numpy()
        mk, sek, t2 = L.re_pool(lk, np.where(np.isfinite(sk) & (sk > 0), sk, 1.0))
        reg[rg] = {"n_units": s.height, "tau_med": float(s["tau"].median()), "tau_q": [float(s["tau"].quantile(0.25)), float(s["tau"].quantile(0.75))],
                   "rho_med": float(s["rho"].median()), "tau0_med": float(s["tau0"].median()), "tau_pred_med": float(s["tau_pred"].median()),
                   "K_pool": float(np.exp(mk)), "K_pool_ci": [float(np.exp(mk - 1.96 * sek)), float(np.exp(mk + 1.96 * sek))],
                   "K_med": float(s["K"].median()), "K_ar_med": float(s["K_ar"].median()),
                   "share_K_in_band": float(s["K"].is_between(0.5, 2).mean()), "share_K_gt2": float((s["K"] > 2).mean()),
                   "share_Klo_gt2": float((s["K_lo"] > 2).mean()),
                   "share_one_exp": float((s["cv_gain"] < 0.10).mean()), "cv_gain_med": float(s["cv_gain"].median()),
                   "tau_wall_med_min": float(np.nanmedian(s["tau_wall_min"].to_numpy())),
                   "K_wall_med": float(np.nanmedian(s["K_wall"].to_numpy())),
                   "tau_nokick_med": float(np.nanmedian(s["tau_nokick"].to_numpy())),
                   "A_med": float(s["A"].median()), "minf_med": float(s["minf"].median()),
                   "m0_med": float(s["m0_obs"].median()), "at_bound": int(s["at_bound"].sum()),
                   "K_unfloored_med": float(np.nanmedian(s["K_unfloored"].to_numpy()))}
    summ = {"regimes": reg, "collapse": collapse(U, Dd), "late": late_contrast(U), "phase_slope": phase_slope(P),
            "verdicts": P.group_by("verdict").len().to_dicts(), "natives": {k: v.get("verdict", v.get("verdict_expectation")) for k, v in nat.items()},
            "n_units_ok": ok.height, "n_units": U.height, "n_periods": P.height,
            "n_agentdays": int(ok["n_agentdays"].sum())}
    if "I" in reg and "III" in reg:
        summ["P5_ratio_III_I"] = reg["III"]["tau_med"] / reg["I"]["tau_med"]
    (RES / "summary.json").write_text(json.dumps(summ, indent=1, default=float))
    print(json.dumps(summ, indent=1, default=float))
    figures(U, P, Dd)
    if (RES / "posthoc.json").exists():
        figure_excess(U)
    if not a.no_estimates:
        print("estimates rows", estimates(U, P, nat))
    if not a.no_readmes:
        readmes(U, P, nat, Dd)


if __name__ == "__main__":
    main()
