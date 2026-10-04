"""H130 summary: random-effects pools over units, clock comparison (P6), the summary figure, and per_period_estimates rows.

    uv run python hypotheses/H130-ou-private-wells-51/analysis/summarize.py
Output: results/summary.json, figures/summary_obs_col.{pdf,png}; rows in per_period_estimates (hypothesis H130).
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "2")

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
import h130lib as L  # noqa: E402
import run_units as R  # noqa: E402

ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "infra/shared"))
RES = L.DATA / "results"
FIG = HERE.parent / "figures"


def pools(d: pl.DataFrame) -> dict:
    out = {}
    for (m, v), g in d.group_by(["model", "variant"], maintain_order=True):
        k = f"{m}|{v}"
        lr = np.log(g["rho"].to_numpy()); se = g["se_lnrho"].to_numpy()
        ok = np.isfinite(lr) & np.isfinite(se) & (se > 0)
        mu, s, t2, i2 = L.dl_pool(lr[ok], se[ok])
        J = L.dl_pool(g["J"].to_numpy(), g["se_J"].to_numpy())
        Jp = L.dl_pool(g["J_pair"].to_numpy(), g["se_J_pair"].to_numpy())
        la = L.dl_pool(np.log(g["g_auto"].to_numpy()), g["se_lng_auto"].to_numpy())
        lgk = np.log(g["g_kick"].to_numpy()); kse = np.array([np.diff(np.log(np.clip(json.loads(c), 1e-6, None)))[0] / 3.92
                                                              for c in g["ci_kick"]])
        okk = np.isfinite(lgk) & np.isfinite(kse) & (kse > 0)
        lk = L.dl_pool(lgk[okk], kse[okk])
        big = g.filter(pl.col("n_days") >= 3)
        out[k] = {"rho": float(np.exp(mu)), "rho_ci90": [float(np.exp(mu - 1.645 * s)), float(np.exp(mu + 1.645 * s))],
                  "rho_ci95": [float(np.exp(mu - 1.96 * s)), float(np.exp(mu + 1.96 * s))], "rho_I2": i2, "rho_units": int(ok.sum()),
                  "J": J[0], "J_ci": [J[0] - 1.96 * J[1], J[0] + 1.96 * J[1]], "J_I2": J[3],
                  "J_pos_units_ge3d": int(sum(json.loads(c)[0] > 0 for c in big["ci_J"])), "n_units_ge3d": big.height,
                  "J_pair": Jp[0], "J_pair_ci": [Jp[0] - 1.96 * Jp[1], Jp[0] + 1.96 * Jp[1]],
                  "g_auto": float(np.exp(la[0])), "g_auto_ci": [float(np.exp(la[0] - 1.96 * la[1])), float(np.exp(la[0] + 1.96 * la[1]))],
                  "g_auto_I2": la[3], "g_kick": float(np.exp(lk[0])),
                  "g_kick_ci": [float(np.exp(lk[0] - 1.96 * lk[1])), float(np.exp(lk[0] + 1.96 * lk[1]))],
                  "g_auto_s_med": float(g["g_auto_s"].median()), "g_cross_s_med": float(g["g_cross_s"].drop_nans().median())}
        gx = g["g_cross_s"].to_numpy(); gs = g["g_auto_s"].to_numpy()
        okx = np.isfinite(gx) & np.isfinite(gs) & (gs > 0)
        out[k]["gx_over_gauto_s_med"] = float(np.median(gx[okx] / gs[okx])) if okx.any() else np.nan
        out[k]["gx_over_gauto_s_in_range"] = int(np.sum((gx[okx] / gs[okx] >= 0.4) & (gx[okx] / gs[okx] <= 2)))
        out[k]["gx_units"] = int(okx.sum())
    return out


def clock_compare() -> dict:
    """P6: reduced chi2 of the drive-corrected autocorrelation fit on the call clock vs the seconds clock, per unit."""
    D = L.load("bge_small", "style_resid_period")
    pu = pl.read_parquet(L.SH / "period_units.parquet").filter((pl.col("goal_no") == 51) & ~pl.col("holdout"))
    out = {}
    for u in sorted(pu["unit_id"].to_list()):
        Du = R.subset(D, [u])
        X = np.where(Du.ok[:, None], Du.Z - np.nan_to_num(Du.H), 0.0)
        cx = L.cross_corr(Du, X)
        t, m, s, n = L.profile(cx)
        fn = L.auto_rate(L.autocorr_corrected(Du, X, t, m, "n"))
        fs = L.auto_rate(L.autocorr_corrected(Du, X, t, m, "s"))
        rn = fn.get("chi2", np.nan) / max(fn.get("nbins", 4) - 3, 1)
        rs = fs.get("chi2", np.nan) / max(fs.get("nbins", 4) - 3, 1)
        out[u] = {"chi2r_calls": rn, "chi2r_secs": rs, "calls_better": bool(rn <= rs)}
    out["calls_better_share"] = float(np.mean([v["calls_better"] for v in out.values() if isinstance(v, dict)]))
    return out


def figure(nat: dict, d: pl.DataFrame):
    p = nat["pooled|bge_small"]
    fig, ax = plt.subplots(1, 2, figsize=(7.0, 2.7))
    C = np.array(p["C_prof"], float); Ct = np.array(p["C_tau"], float)
    b = np.array(p["beta"], float)[1:7]; bs = np.array(p["beta_se"], float)[1:7]; bt = np.array(p["dose_tau"], float)[1:7]
    m = np.isfinite(C) & (Ct > 0)
    ax[0].plot(Ct[m], C[m] / C[m][0], "o-", color="#2a78d6", label="own autocorrelation (drive-corrected)")
    tt = np.maximum(bt, 0.5)
    ax[0].errorbar(tt, b / b[0], yerr=bs / abs(b[0]), fmt="s-", color="#d03b3b", label="sender-specific kick (dose)")
    xs = np.logspace(-0.3, 3, 100)
    ax[0].plot(xs, np.exp(-p["g_auto"] * xs), ":", color="#2a78d6", lw=1)
    ax[0].set_xscale("log"); ax[0].axhline(0, color="k", lw=0.5)
    ax[0].set_xlabel("lag τ (calls of the reader)"); ax[0].set_ylabel("normalized response")
    ax[0].legend(fontsize=6, frameon=False); ax[0].set_title("pooled #51 (bge, style-resid)", fontsize=8)
    g = d.filter((pl.col("model") == "bge_small") & (pl.col("variant") == "style_resid_period")).sort("unit")
    x = np.arange(g.height)
    ca = np.array([json.loads(c) for c in g["ci_auto"]]); ck = np.array([json.loads(c) for c in g["ci_kick"]])
    ax[1].errorbar(x - 0.15, g["g_auto"], yerr=[g["g_auto"] - ca[:, 0], ca[:, 1] - g["g_auto"]], fmt="o", color="#2a78d6",
                   label="γ_auto", ms=3)
    gk = np.clip(g["g_kick"].to_numpy(), 1e-4, None)
    ax[1].errorbar(x + 0.15, gk, yerr=[np.clip(gk - ck[:, 0], 0, None), np.clip(ck[:, 1] - gk, 0, None)], fmt="s",
                   color="#d03b3b", label="γ_kick", ms=3)
    ax[1].set_yscale("log"); ax[1].set_xticks(x); ax[1].set_xticklabels(g["unit"].to_list(), fontsize=6, rotation=60)
    ax[1].set_ylabel("rate per call"); ax[1].legend(fontsize=6, frameon=False)
    ax[1].set_title("per unit (95% agent-day bootstrap)", fontsize=8)
    fig.tight_layout()
    FIG.mkdir(exist_ok=True)
    fig.savefig(FIG / "summary_obs_col.pdf"); fig.savefig(FIG / "summary_obs_col.png", dpi=150)


def estimates(d: pl.DataFrame, pl_: dict, nat: dict, cm: dict):
    import estimates as E
    rows = []
    for r in d.filter(pl.col("variant") == "style_resid_period").iter_rows(named=True):
        ch = f"content:{r['model']}:style_resid_period"
        base = dict(period_unit=r["unit"], goal_no=51, channel=ch, role="replication", n=float(r["n_ad"]), n_kind="agent-days",
                    ci_level=0.95, ci_kind="percentile", source="data/processed/H130-ou-private-wells-51/results/units.parquet")
        cJ = json.loads(r["ci_J"]); ca = json.loads(r["ci_auto"]); ck = json.loads(r["ci_kick"]); cr = json.loads(r["ci_rho95"])
        rows += [
            base | dict(statistic="H130 read jump J_K (read minus in-flight kick projection)", estimate=r["J"], ci_lo=cJ[0], ci_hi=cJ[1],
                        method="mean x_B.u_m read at the producing call (mirror window) minus in-flight messages; agent-day bootstrap",
                        null="in-flight placebo (matched posting age)"),
            base | dict(statistic="H130 well relaxation rate gamma_auto (per call, drive-corrected)", estimate=r["g_auto"],
                        ci_lo=ca[0], ci_hi=ca[1], method="A exp(-g tau)+B fit to own autocorrelation minus cross-agent covariance (A1)",
                        null="synthetic OU skeleton (recovery 0.0098-0.0109 at 0.01)"),
            base | dict(statistic="H130 kick decay rate gamma_kick (per call, sender-specific dose)", estimate=r["g_kick"],
                        ci_lo=ck[0], ci_hi=ck[1], method="A exp(-g tau) fit to pair x reader-day FE dose coefficients (A1)",
                        null="synthetic OU skeleton"),
            base | dict(statistic="H130 rate ratio rho_gamma = gamma_kick/gamma_auto", estimate=r["rho"], ci_lo=cr[0], ci_hi=cr[1],
                        method="paired agent-day bootstrap of both rates", null="OU one-rate prediction rho = 1 (kill outside [0.5, 2])"),
        ]
    for k, v in pl_.items():
        m, var = k.split("|")
        if var != "style_resid_period":
            continue
        base = dict(period_unit="local:51-nonholdout", unit_local="51a-51l", goal_no=51, first_day="2026-07-06",
                    last_day="2026-09-04", channel=f"content:{m}:style_resid_period", role="replication", n=12.0,
                    n_kind="units", ci_level=0.95, ci_kind="se_z", source="data/processed/H130-ou-private-wells-51/results/summary.json")
        rows += [base | dict(statistic="H130 pooled read jump J_K", estimate=v["J"], ci_lo=v["J_ci"][0], ci_hi=v["J_ci"][1],
                             method="DerSimonian-Laird pool of unit J_K", null="in-flight placebo"),
                 base | dict(statistic="H130 pooled rate ratio rho_gamma", estimate=v["rho"], ci_lo=v["rho_ci95"][0],
                             ci_hi=v["rho_ci95"][1], method="DL pool of ln rho over units", null="rho in [0.5, 2] (OU one rate)"),
                 base | dict(statistic="H130 pooled well rate gamma_auto (per call)", estimate=v["g_auto"], ci_lo=v["g_auto_ci"][0],
                             ci_hi=v["g_auto_ci"][1], method="DL pool of ln gamma_auto over units", null="none")]
        c = cm.get(k, {}).get("pool")
        if c:
            rows.append(base | dict(statistic="H130 pooled co-movement slope on log reads beta_R", estimate=c["beta_R"],
                                    ci_lo=c["ci"][0], ci_hi=c["ci"][1], method="J^c ~ log(1+reads/day) + same lab, agent jackknife, DL pool",
                                    null="cross-day surrogate in J^c; slope 0"))
    for model in ("bge_small", "gte_modernbert"):
        p = nat.get(f"pooled|{model}")
        n1 = nat.get(f"N1|{model}")
        n3 = nat.get(f"N3|{model}")
        base = dict(period_unit="local:51-nonholdout", unit_local="51a-51l", goal_no=51, first_day="2026-07-06",
                    last_day="2026-09-04", channel=f"content:{model}:style_resid_period", role="native", ci_level=0.95,
                    ci_kind="percentile", source="data/processed/H130-ou-private-wells-51/results/natives.json")
        if p and "ci_R_K" in p:
            rows.append(base | dict(statistic="H130 NE41 erasure ratio of kicks R_K (crossed/within, lag 4-39 calls)",
                                    estimate=p["R_K"], ci_lo=p["ci_R_K"][0], ci_hi=p["ci_R_K"][1], n=float(p["n_ad"]),
                                    n_kind="agent-days", method="dose coefficients split by an intervening forced reset",
                                    null="OU: ratio 1 (>= 0.5)", notes="NE41 native"))
            rows.append(base | dict(statistic="H130 NE41 erasure ratio of own autocorrelation R_C", estimate=p["R_C"],
                                    ci_lo=p["ci_R_C"][0], ci_hi=p["ci_R_C"][1], n=float(p["n_ad"]), n_kind="agent-days",
                                    method="drive-corrected autocorrelation split by an intervening forced reset",
                                    null="OU: ratio 1 (>= 0.5)", notes="NE41 native"))
        if n1:
            rows.append(base | dict(statistic="H130 N1 rival/other kick ratio", estimate=n1["ratio"], ci_lo=n1["ci_ratio"][0],
                                    ci_hi=n1["ci_ratio"][1], n=n1["rival_reads_0_63"], n_kind="rival reads",
                                    method="summed dose coefficients (bins 0-63 calls), rival vs other senders",
                                    null="isotropic kappa: ratio in [0.5, 2]"))
        if n3 and np.isfinite(n3.get("gamma_J", np.nan)):
            rows.append(base | dict(statistic="H130 N3 joiner relaxation rate gamma_J (per call)", estimate=n3["gamma_J"],
                                    ci_lo=n3["ci_gamma_J"][0], ci_hi=n3["ci_gamma_J"][1], n=float(len(n3["joiners"])),
                                    n_kind="joiners", method="d(n) = A exp(-g n) + B on day-1 own-well projection",
                                    null="OU: gamma_J within x2 of gamma_auto"))
    E.write_estimates(rows, hypothesis="H130")
    return len(rows)


def main():
    d = pl.read_parquet(RES / "units.parquet")
    nat = json.loads((RES / "natives.json").read_text())
    cm = json.loads((RES / "comove.json").read_text())
    pl_ = pools(d)
    clk = clock_compare()
    figure(nat, d)
    n = estimates(d, pl_, nat, cm)
    out = {"pools": pl_, "clock": clk, "comove": {k: v["pool"] for k, v in cm.items()}, "n_estimate_rows": n}
    (RES / "summary.json").write_text(json.dumps(out, indent=1, default=float))
    print(json.dumps(out, indent=1, default=float))


if __name__ == "__main__":
    main()
