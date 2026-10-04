"""H98 summary: per-period estimate rows (write_estimates), figures for the card and the two-page summary.

    uv run python hypotheses/H98-random-field-51/analysis/summarize.py
Reads data/processed/H98-random-field-51/results/{units.parquet, pooled.json, natives.json, niche_pairs.parquet} and
synthetic/{summary.json, niche_A1.json}. Writes figures/ and per_period_estimates rows.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h98lib as L  # noqa: E402

sys.path.insert(0, str(L.ROOT / "infra/shared"))
import estimates as E  # noqa: E402

RES = L.DATA / "results"
FIG = HERE.parent / "figures"
SRC = "data/processed/H98-random-field-51/results/units.parquet"
CONTRAST = ("38a", "39", "40", "41")
COUNTED = ("51c", "51d", "51f", "51g", "51h")


def rows_for(df: pl.DataFrame) -> list[dict]:
    rows = []
    for r in df.iter_rows(named=True):
        g, u = r["goal_no"], r["unit"]
        ch = f"content ({r['var']}, {r['model']})"
        base = {"period_unit": u, "goal_no": g, "channel": ch, "role": "replication", "source": SRC,
                "n_kind": "agents"}
        if r.get("R") is not None and np.isfinite(r["R"]):
            lo, hi = r.get("R_lo"), r.get("R_hi")
            rows.append({**base, "statistic": "disorder_ratio_R", "estimate": r["R"], "ci_lo": lo, "ci_hi": hi,
                         "ci_kind": "percentile" if lo is not None else "none", "ci_level": 0.95, "n": r["N_R"],
                         "method": "random-field share of the static field: Delta^2/(Delta^2+M^2), leave-own-period-out reference (H98 A0)",
                         "null": "none (descriptive; agent bootstrap)"})
        if r.get("b_ex") is not None and np.isfinite(r["b_ex"]):
            lo, hi = r.get("b_lo"), r.get("b_hi")
            ok = lo is not None and np.isfinite(lo)
            rows.append({**base, "statistic": "meanfield_gain_b_ex", "estimate": r["b_ex"], "ci_lo": lo if ok else None,
                         "ci_hi": hi if ok else None, "ci_kind": "percentile" if ok else "none", "ci_level": 0.95,
                         "n": r.get("n_windows"), "n_kind": "agent-windows",
                         "method": "slope of agent-day-centred 30-min content on the leave-one-out room mean, minus cross-day surrogate",
                         "null": "cross-day surrogate"})
        if r.get("W") is not None and np.isfinite(r.get("W") or np.nan):
            rows.append({**base, "statistic": "overlap_synchrony_W", "estimate": r["W"], "ci_kind": "none", "n": r["n_pairs"],
                         "n_kind": "day pairs", "method": "lag-residualized variance of q(d,d') / per-agent circular day-shift null (H22 O6)",
                         "null": f"per-agent circular day shift (p = {r['p_W']:.3f})"})
            rows.append({**base, "statistic": "overlap_bimodality_BC", "estimate": r["bc"], "ci_kind": "none", "n": r["n_pairs"],
                         "n_kind": "day pairs", "method": "bimodality coefficient of P(q) over day pairs", "null": "0.555 (uniform)"})
            rows.append({**base, "statistic": "overlap_q_inf", "estimate": r["qinf"], "ci_kind": "none", "n": r["n_pairs"],
                         "n_kind": "day pairs", "method": "mean q(d,d') at lags >= D/2 (EA-like plateau)", "null": "0 (no frozen field)"})
        for k, stat, meth in (("beta_n", "niche_slope_beta_n", "OLS slope of J^c on squared role-text niche overlap, non-rival pairs, covariates same lab + log reads (H98 A1)"),
                              ("G", "niche_mediation_gap_G", "T_SR - beta_n x (mean niche^2 SR - mean niche^2 U)"),
                              ("T_SR", "rival_excess_T_SR", "mean J^c(same-role rivals) - mean J^c(unrelated)"),
                              ("beta_s", "stance_niche_slope", "OLS slope of soft stance coupling on linear niche overlap, non-rival pairs")):
            v, se = r.get(k), r.get(f"{k}_se")
            if v is None or se is None or not np.isfinite(v) or not np.isfinite(se):
                continue
            rows.append({**base, "statistic": stat, "estimate": v, "se": se, "ci_lo": v - 1.96 * se, "ci_hi": v + 1.96 * se,
                         "ci_kind": "jackknife_z", "ci_level": 0.95, "n": r.get("n_pairs_J"), "n_kind": "agent pairs",
                         "method": meth, "null": "0 (leave-one-agent-out jackknife)"})
    return rows


def native_rows(nat: dict) -> list[dict]:
    rows = []
    src = "data/processed/H98-random-field-51/results/natives.json"
    for r in nat["NE32"]:
        if "N1a_mean_pct" in r:
            rows.append({"period_unit": "51b", "goal_no": 51, "statistic": "NE32_rival_alignment_percentile",
                         "channel": f"content ({r['var']}, {r['model']})", "estimate": r["N1a_mean_pct"], "ci_kind": "none",
                         "n": r["N1a_k"], "n_kind": "newcomers", "role": "native", "source": src,
                         "method": "isolated newcomer state vs incumbent rival's 51a static field: percentile among incumbents",
                         "null": f"uniform rank (exact), p = {r['N1a_p']:.3f}"})
        if "N1b_mean_change" in r:
            rows.append({"period_unit": "51c", "goal_no": 51, "statistic": "NE32_alignment_change_after_merge",
                         "channel": f"content ({r['var']}, {r['model']})", "estimate": r["N1b_mean_change"], "ci_kind": "none",
                         "n": r["N1b_k"], "n_kind": "newcomers", "role": "native", "source": src,
                         "method": "51c static-field alignment with the rival minus the isolated-interval alignment",
                         "null": "0 (no build-up by reading)"})
    for r in nat["focus"]:
        for a, m in r["Nb_movers"].items():
            if m.get("delta") is None:
                continue
            rows.append({"period_unit": "51g", "goal_no": 51, "statistic": f"focus_mover{a}_pull_change",
                         "channel": f"content ({r['var']}, {r['model']})", "estimate": m["delta"], "ci_kind": "none", "n": 2,
                         "n_kind": "units (51f, 51g)", "role": "native", "source": src,
                         "method": "agent pull toward the #general mean, 51g minus 51f (surrogate-corrected)",
                         "null": f"stayers' median change {r['Nb_stayers_median_delta']:.3f}"})
    return rows


def figures(df: pl.DataFrame, nat: dict):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    FIG.mkdir(parents=True, exist_ok=True)
    p = df.filter((pl.col("var") == "style_resid_period") & (pl.col("model") == "bge_small"))
    # Fig 1: phase diagram (R, b_ex) per replication unit
    fig, ax = plt.subplots(1, 2, figsize=(7.0, 2.7))
    rep = p.filter(pl.col("unit").is_in(list(COUNTED) + list(CONTRAST)))
    for r in rep.iter_rows(named=True):
        c = "#c0392b" if r["unit"].startswith("51") else "#2c3e50"
        xe = [[r["R"] - r["R_lo"]], [r["R_hi"] - r["R"]]] if r.get("R_lo") is not None else None
        ye = [[r["b_ex"] - r["b_lo"]], [r["b_hi"] - r["b_ex"]]] if r.get("b_lo") is not None and np.isfinite(r["b_lo"]) else None
        ax[0].errorbar(r["R"], r["b_ex"], xerr=xe, yerr=ye, fmt="o", color=c, ms=4, lw=0.8, capsize=1.5)
        off = {"51c": (4, 3), "51d": (-14, 6), "51f": (-12, -9), "51g": (4, 4), "51h": (4, -8)}.get(r["unit"], (3, 2))
        ax[0].annotate(r["unit"], (r["R"], r["b_ex"]), fontsize=5.5, xytext=off, textcoords="offset points")
    ax[0].set_xlabel("disorder ratio R (random-field share)", fontsize=7)
    ax[0].set_ylabel("mean-field gain $b_{ex}$", fontsize=7)
    ax[0].axhline(0, color="0.7", lw=0.5)
    ax[0].tick_params(labelsize=6)
    ax[0].set_title("units on the RF phase diagram (red: #51)", fontsize=7)
    # Fig 1b: niche scatter (pairs of all niche units, primary)
    f = RES / "niche_pairs.parquet"
    if f.exists():
        P = pl.read_parquet(f).filter(pl.col("niche2").is_not_null())
        U = P.filter(pl.col("cls").is_null())
        S = P.filter(pl.col("cls") == "SR")
        ax[1].scatter(U["niche2"], U["J"], s=3, color="0.6", alpha=0.5, label="other pairs")
        ax[1].scatter(S["niche2"], S["J"], s=14, color="#c0392b", label="same-role rivals")
        # binned means of other pairs
        bins = np.quantile(U["niche2"].to_numpy(), np.linspace(0, 1, 7))
        x = U["niche2"].to_numpy()
        y = U["J"].to_numpy()
        mids, means = [], []
        for lo, hi in zip(bins[:-1], bins[1:]):
            m = (x >= lo) & (x <= hi)
            if m.sum() > 5:
                mids.append(x[m].mean())
                means.append(y[m].mean())
        ax[1].plot(mids, means, "-o", color="#2c3e50", ms=3, lw=1, label="binned mean (others)")
        ax[1].set_xlabel("squared role-text niche overlap $n_{ij}^2$", fontsize=7)
        ax[1].set_ylabel("content co-movement $J^c_{ij}$", fontsize=7)
        ax[1].legend(fontsize=5.5, frameon=False)
        ax[1].tick_params(labelsize=6)
        ax[1].set_title("pairs in #51 niche units", fontsize=7)
    fig.tight_layout()
    fig.savefig(FIG / "summary_obs_col.pdf")
    fig.savefig(FIG / "summary_obs_col.png", dpi=160)
    plt.close(fig)
    # Fig 2: niche slope per unit, without (A: lab) and with reads + replies (B), bge and gte, plus RE pools
    fig, ax = plt.subplots(1, 1, figsize=(3.4, 2.1))
    units = ["51a", "51c", "51d", "51e", "51f", "51g", "51h"]
    for k, (model, col) in enumerate((("bge_small", "#c0392b"), ("gte_modernbert", "#2c3e50"))):
        q = df.filter((pl.col("var") == "style_resid_period") & (pl.col("model") == model) & pl.col("unit").is_in(units)).sort("unit")
        y = np.arange(q.height)
        for tag, mk, dy in (("_A", "o", -0.12), ("_B", "s", 0.12)):
            ax.errorbar(q[f"beta_n{tag}"], y + dy + 0.3 * k - 0.15, xerr=1.96 * q[f"beta_n_se{tag}"], fmt=mk, ms=2.5,
                        color=col, alpha=1.0 if tag == "_A" else 0.5, lw=0.6, capsize=0)
        a = L.re_pool(q["beta_n_A"].to_numpy(), q["beta_n_se_A"].to_numpy())
        b = L.re_pool(q["beta_n_B"].to_numpy(), q["beta_n_se_B"].to_numpy())
        for est, mk, dy, al in ((a, "D", -0.12, 1.0), (b, "D", 0.12, 0.5)):
            ax.errorbar(est["est"], len(units) + dy + 0.3 * k - 0.15, xerr=[[est["est"] - est["lo"]], [est["hi"] - est["est"]]],
                        fmt=mk, ms=3.5, color=col, alpha=al, lw=0.9)
    ax.set_yticks(list(range(len(units))) + [len(units)], units + ["RE pool"], fontsize=6)
    ax.axvline(0, color="0.6", lw=0.5)
    ax.set_xlabel(r"niche slope $\beta_n$ (co-movement per unit $n_{ij}^2$)", fontsize=6.5)
    ax.tick_params(labelsize=6)
    ax.set_xlim(-0.35, 0.6)
    ax.set_ylim(-0.6, len(units) + 3.4)
    from matplotlib.lines import Line2D
    h = [Line2D([], [], color="#c0392b", marker="o", ls="", ms=3, label="bge, lab only"),
         Line2D([], [], color="#c0392b", marker="s", ls="", ms=3, alpha=0.5, label="bge, + reads + replies"),
         Line2D([], [], color="#2c3e50", marker="o", ls="", ms=3, label="gte, lab only")]
    ax.legend(handles=h, fontsize=5, frameon=True, framealpha=0.9, loc="upper right")
    fig.tight_layout()
    fig.savefig(FIG / "niche_mediation_col.pdf")
    fig.savefig(FIG / "niche_mediation_col.png", dpi=160)
    plt.close(fig)


def main():
    df = pl.read_parquet(RES / "units.parquet")
    nat = json.loads((RES / "natives.json").read_text()) if (RES / "natives.json").exists() else None
    rows = rows_for(df)
    if nat:
        rows += native_rows(nat)
    E.write_estimates(rows, hypothesis="H98")
    print("estimates rows:", len(rows))
    figures(df, nat)


if __name__ == "__main__":
    main()
