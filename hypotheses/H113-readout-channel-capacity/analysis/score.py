"""H113: per_period_estimates rows and summary figures from results/*.json and synthetic/summary.json.
Usage: uv run python hypotheses/H113-readout-channel-capacity/analysis/score.py [--no-write]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "infra/shared"))
D = ROOT / "data/processed/H113-readout-channel-capacity"
RES = D / "results"
FIG = HERE.parent / "figures"
BLUE, ORANGE, INK, MUTED, AQUA = "#2a78d6", "#eb6834", "#0b0b0b", "#52514e", "#1baf7a"
MODELS = {"bge_small": "bge", "gte_modernbert": "gte"}


def unit_name(g: int) -> str:
    pu = pl.read_parquet(ROOT / "data/processed/shared/period_units.parquet").filter((pl.col("goal_no") == g) & ~pl.col("holdout"))
    return pu["unit_id"][0] if len(pu) == 1 else f"G{g:02d}"


def rows() -> list[dict]:
    per = json.loads((RES / "periods.json").read_text()); nat = json.loads((RES / "natives.json").read_text())
    out = []
    for g, o in per.items():
        g = int(g)
        for m, tag in MODELS.items():
            r = o[m]; f = r.get("fit", {})
            if "b" not in f:
                continue
            base = dict(period_unit=unit_name(g), goal_no=g, channel=f"content uptake at the talk call ({tag}, style_resid32, raw projection)",
                        role="replication", ci_level=0.95, n=f["n"], n_kind="talk calls with k >= 1",
                        status=("identified" if r.get("identified") else "not identified (A1 field rule)") + ("; testable" if r.get("testable") else "; not testable"),
                        source="results/periods.json")
            out.append({**base, "statistic": "readout_capacity_b", "estimate": f["b"], "ci_lo": f["b_lo"], "ci_hi": f["b_hi"],
                        "ci_kind": "percentile", "method": "profile LS of y_perp on k^-b * sum(x_perp) + in-flight sum; agent-day bootstrap 300",
                        "null": "b = 0 (no bottleneck), b = 1 (one-message capacity); field-only synthetic gives b 0.79-0.87"})
            p = r.get("placebo", {})
            if p.get("lo") is not None:
                out.append({**base, "statistic": "readout_placebo_contrast", "estimate": p["contrast"], "ci_lo": p["lo"], "ci_hi": p["hi"],
                            "ci_kind": "percentile", "n": p["n_inflight"], "n_kind": "in-flight items",
                            "method": "per-item pull, read (age <= 120 s) minus in flight, age bins 0-30/30-60/60-120 s", "null": "0 (field only)"})
            out.append({**base, "statistic": "readout_batch_redundancy_r", "estimate": r["redundancy"]["r"], "ci_lo": None, "ci_hi": None,
                        "ci_kind": "none", "method": "slope of ln E|s|^2 on ln k minus 1 (k bins)", "null": "0 independent, 1 identical"})
    for m, tag in MODELS.items():
        w = nat["G51_D2"].get(m, {}).get("wake")
        if w:
            out.append(dict(period_unit="G51", goal_no=51, channel=f"content uptake at timer-wake batches (D2; {tag})", role="native",
                            statistic="readout_capacity_b", estimate=w["b"], ci_lo=w["b_lo"], ci_hi=w["b_hi"], ci_kind="percentile",
                            ci_level=0.95, n=w["n"], n_kind="wake calls with k >= 1", method="as replication, on D2 wake batches (exogenous k)",
                            null="b = 0 / b = 1", source="results/natives.json"))
        for side in ("10a", "10b"):
            s = nat["NE03"].get(m, {}).get(side)
            if s and s.get("b") is not None:
                out.append(dict(period_unit=side, goal_no=10, channel=f"content uptake at the talk call ({tag}); NE03 side", role="native",
                                statistic="readout_capacity_b", estimate=s["b"], ci_lo=s["b_lo"], ci_hi=s["b_hi"], ci_kind="percentile",
                                ci_level=0.95, n=s["n"], n_kind="talk calls with k >= 1", method="as replication, per NE03 side",
                                null="b(10b) = b(10a)", source="results/natives.json", status="underpowered (10a < 300 calls)"))
    return out


def figure():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    per = json.loads((RES / "periods.json").read_text()); nat = json.loads((RES / "natives.json").read_text())
    plt.rcParams.update({"font.size": 7.5, "axes.edgecolor": MUTED, "axes.labelcolor": INK, "xtick.color": MUTED,
                         "ytick.color": MUTED, "axes.spines.top": False, "axes.spines.right": False})
    fig, (ax, bx) = plt.subplots(1, 2, figsize=(7.0, 2.6), gridspec_kw={"width_ratios": [1.8, 1]})
    gs = sorted(int(g) for g, o in per.items() if o.get("testable"))
    for i, g in enumerate(gs):
        for m, dx, mk in (("bge_small", -0.15, "o"), ("gte_modernbert", 0.15, "s")):
            r = per[str(g)][m]; f = r["fit"]
            col = BLUE if r.get("identified") else "#9ec5f4"
            ax.errorbar(i + dx, f["b"], yerr=[[f["b"] - f["b_lo"]], [f["b_hi"] - f["b"]]], fmt=mk, color=col, ms=2.8, lw=0.8,
                        capsize=0, mfc=col if m == "bge_small" else "white")
    x0 = len(gs) + 0.8
    for m, dx, mk in (("bge_small", -0.15, "D"), ("gte_modernbert", 0.15, "D")):
        w = nat["G51_D2"][m]["wake"]
        ax.errorbar(x0 + dx, w["b"], yerr=[[w["b"] - w["b_lo"]], [w["b_hi"] - w["b"]]], fmt=mk, color=ORANGE, ms=3.5, lw=1.1, capsize=0)
    for y, lab in ((0.66, "HH345: a_U 0.34"), (0.50, "H18 D2: a_U 0.50"), (1.0, "one message per call")):
        ax.axhline(y, color=MUTED, lw=0.6, ls="--" if y != 1 else ":")
        ax.text(len(gs) - 0.3, y + 0.01, lab, fontsize=5.6, color=INK, va="bottom", ha="right")
    ax.axhspan(0.79, 0.87, color="#e9e7e1", zorder=0, lw=0)
    ax.text(-0.5, 0.875, "field-only synthetic band", fontsize=5.5, color=MUTED, ha="left", va="bottom")
    ax.set_xticks(list(range(len(gs))) + [x0]); ax.set_xticklabels([f"#{g}" for g in gs] + ["#51 wakes"], fontsize=5.0, rotation=90)
    ax.set_ylabel("capacity exponent b̂\n(per-message uptake ∝ k^−b)"); ax.set_ylim(0.2, 1.12)
    # right: total uptake U(k) on log-log for D2 wakes and G38 talk calls
    for lab, bins, col in (("#51 wakes (D2)", nat["G51_D2"]["bge_small"]["binned"], ORANGE),
                           ("#38 talk calls", None, BLUE)):
        if bins is None:
            continue
        k = np.array([b_["k_mean"] for b_ in bins]); U = np.array([b_["U"] for b_ in bins])
        bx.plot(k, U, "o-", color=col, ms=3, lw=1.2, label=lab)
    k = np.array([1, 40.0]); u0 = nat["G51_D2"]["bge_small"]["binned"][0]["U"]
    for a, ls in ((1.0, ":"), (0.5, "--"), (0.34, "-."), (0.0, "-")):
        bx.plot(k, u0 * k ** a, ls, color=MUTED, lw=0.6)
        bx.text(40, u0 * 40 ** a, f" k^{a}", fontsize=5.5, color=MUTED, va="center")
    from matplotlib.ticker import ScalarFormatter, NullFormatter
    bx.set_xscale("log"); bx.set_yscale("log")
    for axis in (bx.xaxis, bx.yaxis):
        axis.set_major_formatter(ScalarFormatter()); axis.set_minor_formatter(NullFormatter())
    bx.set_xlabel("batch size k"); bx.set_ylabel("total uptake U(k) = k γ_k")
    bx.legend(frameon=False, fontsize=6, loc="upper left")
    fig.tight_layout(); FIG.mkdir(exist_ok=True); fig.savefig(FIG / "summary_obs.pdf"); plt.close(fig)
    # synthetic
    s = json.loads((D / "synthetic/summary.json").read_text())
    fig, ax = plt.subplots(figsize=(3.4, 2.3))
    worlds = ["W0", "W1", "W2", "W3", "W3w", "W6", "W4", "W5"]
    names = {"W0": "none", "W1": "field only", "W2": "b=0", "W3": "b=0.66", "W3w": "b=0.66 weak", "W6": "b=0.66+field",
             "W4": "one item", "W5": "newest item"}
    for k_, w in enumerate(worlds):
        for g, mk in ((18, "o"), (31, "s"), (38, "^"), (51, "v")):
            v = s.get(f"G{g}|{w}", {}).get("b_med_raw")
            if v is not None:
                ax.plot(k_ + (g - 34) / 70, v, mk, color=BLUE, ms=3.2, alpha=0.85)
    for y in (0, 0.66, 1):
        ax.axhline(y, color=MUTED, lw=0.5, ls=":")
    ax.set_xticks(range(len(worlds))); ax.set_xticklabels([names[w] for w in worlds], rotation=35, ha="right", fontsize=5.8)
    ax.set_ylabel("median b̂ (raw projection)"); ax.set_ylim(-0.3, 1.3)
    fig.tight_layout(); fig.savefig(FIG / "summary_synth.pdf"); plt.close(fig)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--no-write", action="store_true"); a = ap.parse_args()
    figure(); rs = rows(); print(len(rs), "rows")
    if not a.no_write:
        import estimates as E
        E.write_estimates(rs, hypothesis="H113")


if __name__ == "__main__":
    main()
