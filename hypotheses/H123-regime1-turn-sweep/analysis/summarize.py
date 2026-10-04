"""H123: summary numbers, per_period_estimates rows and figures from results/{audit,ep,snapshot}.parquet and
synthetic/summary.parquet. Read-only on data except the estimates table and figures.

Usage: uv run python hypotheses/H123-regime1-turn-sweep/analysis/summarize.py [--no-estimates]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h123lib as L  # noqa: E402

sys.path.insert(0, str(L.ROOT / "infra/shared"))
FIG = L.ROOT / "hypotheses/H123-regime1-turn-sweep/figures"
C1, C2, C3, C4 = "#2a78d6", "#eb6834", "#1baf7a", "#eda100"
INK, INK2 = "#0b0b0b", "#52514e"
SRC = "data/processed/H123-regime1-turn-sweep/results"


def load():
    R = L.OUT / "results"
    return (pl.read_parquet(R / "audit.parquet"), pl.read_parquet(R / "ep.parquet"),
            pl.read_parquet(R / "snapshot.parquet"), pl.read_parquet(L.OUT / "synthetic/summary.parquet"))


def numbers(A, E, S):
    a1 = A.filter((pl.col("subset") == "all") & (pl.col("regime") == "I"))
    out = {"audit_units_I": a1.height, "class_counts_I": dict(a1.group_by("class").len().iter_rows()),
           "eta_med": a1["eta"].median(), "eta_max": a1["eta"].max(), "eta_shuf_med": a1["eta_shuf"].median(),
           "cvgap_med": a1["cv_gap"].median(), "cvgap_shuf_med": a1["cv_gap_shuf"].median(),
           "rratio_med": a1["r_ratio"].median(), "rratio_range": [a1["r_ratio"].min(), a1["r_ratio"].max()],
           "kappa_med": a1["kappa_par"].median(), "kappa_min": a1["kappa_par"].min(),
           "Lname_med": a1["L_name"].median(), "Lname_max": a1["L_name"].max(),
           "Lname_ci_above1": int(a1.filter(pl.col("L_name_lo") > 1).height),
           "Lname_with_ci": int(a1.filter(pl.col("L_name_lo").is_not_null()).height),
           "Lname_ge_1_5": int(a1.filter(pl.col("L_name") >= 1.5).height)}
    ac = A.filter((pl.col("subset") == "chat") & (pl.col("regime") == "I"))
    out.update({"chat_class_counts_I": dict(ac.group_by("class").len().iter_rows()), "chat_eta_max": ac["eta"].max(),
                "chat_cv_min": ac["cv_gap"].min()})
    e1 = E.filter(pl.col("regime") == "I")
    for ch in ("talk", "mode"):
        x = e1.filter(pl.col("channel") == ch)
        out[f"ep_units_{ch}"] = x.height
        for lag in L.LAGS:
            out[f"above{lag}_{ch}"] = int(x[f"above{lag}"].sum())
            out[f"sweep{lag}_{ch}_absmax"] = float(x[f"sweep_x{lag}"].abs().max())
            out[f"sweepminusrand{lag}_{ch}_med"] = float((x[f"sweep_x{lag}"] - x[f"rand_x{lag}"]).median())
            out[f"sweepminusrand{lag}_{ch}_range"] = [float((x[f"sweep_x{lag}"] - x[f"rand_x{lag}"]).min()),
                                                      float((x[f"sweep_x{lag}"] - x[f"rand_x{lag}"]).max())]
        ab = x.filter(pl.col("above2") | pl.col("above4"))
        out[f"above_units_{ch}"] = [{"unit": r["unit"], "x1": r["x1"], "x2": r["x2"], "x4": r["x4"],
                                     "above1": r["above1"], "sweep_x2": r["sweep_x2"], "ratio_x2":
                                     r["x2"] / max(abs(r["sweep_x2"] - r["rand_x2"]), 1e-6)} for r in ab.iter_rows(named=True)]
        out[f"rmsJs_{ch}_med"] = float(x["rms_Js"].median())
    s = S.group_by("regime", "channel").agg(pl.col("rho2_med").median().alias("m"), pl.len().alias("n"))
    out["rho2"] = {f"{r['regime']}_{r['channel']}": [r["m"], r["n"]] for r in s.iter_rows(named=True)}
    # natives
    def get(u, ch):
        x = E.filter((pl.col("unit") == u) & (pl.col("channel") == ch))
        return x.to_dicts()[0] if x.height else None
    out["NE09"] = {u: {k: get(u, "talk")[k] for k in ("rms_Js", "rms_Js_ci", "x1", "x2", "x4", "above1", "above2",
                                                       "above4", "sweep_x2", "rand_x2")} for u in ("23", "24")}
    out["NE14"] = {u: {"talk": {k: get(u, "talk")[k] for k in ("x2", "above2", "sweep_x2", "rand_x2", "rms_Js")},
                       "kappa": A.filter((pl.col("unit") == u) & (pl.col("subset") == "all"))["kappa_par"][0],
                       "class": A.filter((pl.col("unit") == u) & (pl.col("subset") == "all"))["class"][0],
                       "eta": A.filter((pl.col("unit") == u) & (pl.col("subset") == "all"))["eta"][0]}
                   for u in ("33", "35", "36b", "36c", "37")}
    return out


def estimates(A, E, S):
    import estimates as ES
    pu = pl.read_parquet(L.ROOT / "data/processed/shared/period_units.parquet")
    gmap = dict(zip(pu["unit_id"], pu["goal_no"]))
    role_of = lambda u: "native" if u in ("33", "35", "36a", "36b", "36c", "37") else "replication"  # noqa: E731
    rows = []
    for r in A.filter(pl.col("subset") == "all").iter_rows(named=True):
        u = r["unit"]
        base = {"period_unit": u, "goal_no": gmap[u], "role": role_of(u), "source": f"{SRC}/audit.parquet",
                "n": float(r["n_steps"]), "n_kind": "calls"}
        rows.append({**base, "statistic": "order_predictability_eta", "channel": "calls", "estimate": r["eta"],
                     "ci_lo": None, "ci_hi": None, "ci_kind": "none", "method": "plug-in conditional entropy",
                     "null": f"within-day actor shuffle mean {r['eta_shuf']:.4f}", "notes": f"class={r['class']}"})
        rows.append({**base, "statistic": "return_gap_cv", "channel": "calls", "estimate": r["cv_gap"],
                     "ci_lo": r["cv_gap_shuf_q_lo"], "ci_hi": r["cv_gap_shuf_q_hi"], "ci_kind": "none",
                     "method": "pooled per-agent CV of other-agent steps between own calls",
                     "null": "interval = within-day shuffle 95% range (not a CI)", "notes": "round robin = 0"})
        rows.append({**base, "statistic": "call_concurrency_kappa", "channel": "calls", "estimate": r["kappa_par"],
                     "ci_lo": None, "ci_hi": None, "ci_kind": "none", "method": "share of calls starting inside "
                     "another agent's in-flight call", "null": "one-at-a-time pointer = 0"})
        if r.get("L_name") is not None:
            rows.append({**base, "statistic": "named_next_lift", "channel": "calls", "estimate": r["L_name"],
                         "ci_lo": r["L_name_lo"], "ci_hi": r["L_name_hi"],
                         "ci_kind": "percentile" if r["L_name_lo"] == r["L_name_lo"] else "none",
                         "method": "Mantel-Haenszel rate ratio, day bootstrap 200",
                         "null": f"naming-mask shuffle within day, p={r['L_name_p']}"})
    for r in E.iter_rows(named=True):
        u = r["unit"]
        base = {"period_unit": u, "goal_no": gmap[u], "role": role_of(u), "source": f"{SRC}/ep.parquet",
                "n": float(r["T"]), "n_kind": "steps", "channel": f"event_{r['channel']}"}
        for lag in L.LAGS:
            se = r[f"x{lag}_se"]
            lo, hi = ES.ci_from_se(r[f"x{lag}"], se, df=r["n_days"] - 1) if se == se else (None, None)
            rows.append({**base, "statistic": f"sigma_cross_lag{lag}", "estimate": r[f"x{lag}"], "ci_lo": lo,
                         "ci_hi": hi, "ci_kind": "se_t", "se": se,
                         "method": "held-out Newton (ep_newton, c=1, family blocks), nats/step",
                         "null": f"block-flip q95 {r[f'floor{lag}_q95']:.2e}; sigma_rand q95 {r[f'rand_x{lag}_q95']:.2e}",
                         "notes": f"above={r[f'above{lag}']}"})
            rows.append({**base, "statistic": f"sigma_sweep_minus_rand_lag{lag}",
                         "estimate": r[f"sweep_x{lag}"] - r[f"rand_x{lag}"],
                         "ci_lo": None, "ci_hi": None, "ci_kind": "none", "se": float(np.hypot(
                             r[f"sweep_x{lag}_sd"], r[f"rand_x{lag}_sd"]) / np.sqrt(20)),
                         "method": "symmetric fitted J simulated on real vs shuffled order (20 reps), same estimator",
                         "null": "0 = scheduler makes no EP"})
        rows.append({**base, "statistic": "rms_J_sym", "estimate": r["rms_Js"],
                     "ci_lo": json.loads(r["rms_Js_ci"])[0], "ci_hi": json.loads(r["rms_Js_ci"])[1],
                     "ci_kind": "percentile", "method": "heat-bath logistic ML, day bootstrap 50", "null": "none"})
    for r in S.iter_rows(named=True):
        rows.append({"period_unit": r["unit"], "goal_no": r["goal_no"], "role": "replication",
                     "source": f"{SRC}/snapshot.parquet", "statistic": "pairwise_sufficiency_rho2_N4",
                     "channel": f"1min_{r['channel']}", "estimate": r["rho2_med"], "ci_lo": r["rho2_q25"],
                     "ci_hi": r["rho2_q75"], "ci_kind": "none", "n": float(r["n_subsets"]), "n_kind": "subsets",
                     "method": "I2/IN, IPF pairwise max-ent, median over random 4-agent subsets (IQR as interval)",
                     "null": "Roudi 2009: trivially high at small N"})
    w = ES.write_estimates(rows, hypothesis="H123")
    print("estimates rows:", w.height)


def figures(A, E, Ssyn):
    FIG.mkdir(exist_ok=True)
    plt.rcParams.update({"font.size": 8, "axes.edgecolor": INK2, "axes.labelcolor": INK, "xtick.color": INK2,
                         "ytick.color": INK2, "axes.spines.top": False, "axes.spines.right": False})
    a1 = A.filter((pl.col("subset") == "all")).sort("regime", "unit")
    fig, ax = plt.subplots(1, 3, figsize=(7.2, 2.4))
    reg = a1["regime"].to_numpy()
    col = np.where(reg == "I", C1, C2)
    ix = np.arange(a1.height)
    ax[0].scatter(ix, a1["eta"], s=10, c=col)
    ax[0].scatter(ix, a1["eta_shuf_q_hi"], s=6, marker="_", color=INK2)
    ax[0].axhline(0.5, color=C4, lw=1)
    ax[0].text(1, 0.52, "sweep threshold 0.5", color=INK2, fontsize=7)
    ax[0].set(ylim=(0, 0.6), xlabel="unit (time order; dash = shuffle q97.5)", ylabel="order predictability η_ord")
    ax[1].scatter(a1["cv_gap_shuf"], a1["cv_gap"], s=10, c=col)
    ax[1].plot([0, 2.2], [0, 2.2], color=INK2, lw=0.8, ls=":")
    ax[1].axhline(0.5, color=C4, lw=1)
    ax[1].set(xlim=(0, 2.2), ylim=(0, 2.2), xlabel="return-gap CV, shuffled", ylabel="return-gap CV, real")
    x = a1.filter(pl.col("L_name_lo").is_not_null())
    ax[2].errorbar(np.arange(x.height), x["L_name"], yerr=[x["L_name"] - x["L_name_lo"], x["L_name_hi"] - x["L_name"]],
                   fmt="o", ms=2.5, color=C1, lw=0.8)
    ax[2].axhline(1, color=INK2, lw=0.8, ls=":")
    ax[2].axhline(1.5, color=C4, lw=1)
    ax[2].set(xlabel="unit (time order)", ylabel="named-next lift L_name")
    ax[0].scatter([], [], c=C1, s=10, label="regime I")
    ax[0].scatter([], [], c=C2, s=10, label="regime II/III (NE14)")
    ax[0].legend(frameon=False, fontsize=7, loc="center right")
    fig.tight_layout()
    fig.savefig(FIG / "audit.pdf")
    plt.close(fig)
    # EP: real vs floor and sweep-minus-rand, talk
    e = E.filter(pl.col("channel") == "talk").sort("regime", "unit")
    fig, ax = plt.subplots(1, 2, figsize=(7.2, 2.5))
    xs = np.arange(e.height)
    for k, lag in enumerate((1, 4)):
        ax[k].errorbar(xs, e[f"x{lag}"] * 1e3, yerr=1.96 * e[f"x{lag}_se"].to_numpy() * 1e3, fmt="o", ms=2.5,
                       color=C1, lw=0.7, label="real σ×")
        ax[k].plot(xs, e[f"floor{lag}_q95"] * 1e3, "_", color=INK2, ms=6, label="block-flip q95")
        ax[k].plot(xs, (e[f"sweep_x{lag}"] - e[f"rand_x{lag}"]) * 1e3, "s", ms=2.5, color=C2,
                   label="σ_sweep − σ_rand")
        ax[k].axhline(0, color=INK2, lw=0.6)
        ax[k].set(xlabel="unit (regime I, then NE14 units)", ylabel=f"σ×({lag}) [10⁻³ nats/step]",
                  title=f"talk spin, lag {lag}")
    ax[0].legend(frameon=False, fontsize=7)
    fig.tight_layout()
    fig.savefig(FIG / "ep_talk.pdf")
    plt.close(fig)
    # synthetic signature
    s = Ssyn.filter(~pl.col("asym"))
    fig, ax = plt.subplots(1, 3, figsize=(7.2, 2.2), sharey=True)
    for k, o in enumerate(("round_robin", "random", "real_G27")):
        x = s.filter(pl.col("order") == o).sort("J0")
        for lag, c in zip(L.LAGS, (C1, C2, C3)):
            ax[k].errorbar(x["J0"] + 0.03 * lag, x[f"x{lag}_mean"] * 1e3, yerr=x[f"x{lag}_sd"] * 1e3, fmt="o-",
                           ms=3, lw=1, color=c, label=f"lag {lag}")
        ax[k].axhline(0, color=INK2, lw=0.6)
        ax[k].set(title={"round_robin": "round robin", "random": "random order", "real_G27": "real G27 order"}[o],
                  xlabel="J₀ (symmetric)")
    ax[0].set_ylabel("σ× [10⁻³ nats/step]")
    ax[0].legend(frameon=False, fontsize=7)
    fig.tight_layout()
    fig.savefig(FIG / "synthetic.pdf")
    plt.close(fig)


def compact(A, E, Ssyn):
    """Two-panel figures for the 2-page summary (about 4 in wide)."""
    a1 = A.filter(pl.col("subset") == "all").sort("regime", "unit")
    e = E.filter(pl.col("channel") == "talk").sort("regime", "unit")
    fig, ax = plt.subplots(1, 2, figsize=(4.2, 2.0))
    ix = np.arange(a1.height)
    col = np.where(a1["regime"].to_numpy() == "I", C1, C2)
    ax[0].scatter(ix, a1["eta"], s=7, c=col)
    ax[0].axhline(0.5, color=C4, lw=1)
    ax[0].text(1, 0.53, "sweep ≥ 0.5", color=INK2, fontsize=6)
    ax[0].set(ylim=(0, 0.6), xlabel="unit (time order)", ylabel="order predictability η_ord")
    ax[0].set_title("(a) audit", fontsize=7)
    xs = np.arange(e.height)
    ax[1].errorbar(xs, e["x4"] * 1e3, yerr=1.96 * e["x4_se"].to_numpy() * 1e3, fmt="o", ms=2, color=C1, lw=0.6,
                   label="real σ×(4)")
    ax[1].plot(xs, e["floor4_q95"] * 1e3, "_", color=INK2, ms=4, label="floor q95")
    ax[1].plot(xs, (e["sweep_x4"] - e["rand_x4"]) * 1e3, "s", ms=2, color=C2, label="σ_sweep − σ_rand")
    ax[1].axhline(0, color=INK2, lw=0.5)
    ax[1].set(xlabel="unit", ylabel="10⁻³ nats per call")
    ax[1].set_title("(b) talk EP, lag 4", fontsize=7)
    ax[1].legend(frameon=False, fontsize=5.5, loc="lower right")
    for a_ in ax:
        a_.tick_params(labelsize=6)
        a_.xaxis.label.set_size(6.5)
        a_.yaxis.label.set_size(6.5)
    fig.tight_layout()
    fig.savefig(FIG / "summary_obs.pdf")
    plt.close(fig)
    s = Ssyn.filter(~pl.col("asym"))
    fig, ax = plt.subplots(1, 2, figsize=(4.2, 1.8), sharey=True)
    for k, o in enumerate(("round_robin", "real_G27")):
        x = s.filter(pl.col("order") == o).sort("J0")
        for lag, c in zip(L.LAGS, (C1, C2, C3)):
            ax[k].errorbar(x["J0"] + 0.03 * lag, x[f"x{lag}_mean"] * 1e3, yerr=x[f"x{lag}_sd"] * 1e3, fmt="o-",
                           ms=2.5, lw=0.9, color=c, label=f"lag {lag}")
        ax[k].axhline(0, color=INK2, lw=0.5)
        ax[k].set_title({"round_robin": "(a) exact round robin", "real_G27": "(b) real G27 call order"}[o], fontsize=7)
        ax[k].set_xlabel("symmetric J₀", fontsize=6.5)
        ax[k].tick_params(labelsize=6)
    ax[0].set_ylabel("σ× [10⁻³ nats/call]", fontsize=6.5)
    ax[0].legend(frameon=False, fontsize=5.5)
    fig.tight_layout()
    fig.savefig(FIG / "summary_synth.pdf")
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-estimates", action="store_true")
    args = ap.parse_args()
    A, E, S, Ssyn = load()
    n = numbers(A, E, S)
    (L.OUT / "results/summary.json").write_text(json.dumps(n, indent=1, default=float))
    print(json.dumps(n, indent=1, default=float))
    figures(A, E, Ssyn)
    compact(A, E, Ssyn)
    if not args.no_estimates:
        estimates(A, E, S)


if __name__ == "__main__":
    main()
