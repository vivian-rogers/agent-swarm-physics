"""H124: summary numbers, per_period_estimates rows and figures from results/*.json and synthetic/*.parquet.

Usage: uv run python hypotheses/H124-small-n-meanfield-benchmark/analysis/summarize.py [--no-estimates]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import matplotlib.ticker  # noqa: E402,F401
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h124lib as L  # noqa: E402

sys.path.insert(0, str(L.ROOT / "infra/shared"))
FIG = L.ROOT / "hypotheses/H124-small-n-meanfield-benchmark/figures"
COL = {"nMF": "#2a78d6", "TAP": "#eb6834", "MS": "#1baf7a", "nMF|s": "#4a3aa7", "ML": "#52514e"}
INK2 = "#52514e"
GOAL = {"2": 2, "3": 3, "4a": 4, "4c": 4, "5": 5, "6a": 6, "6b": 6, "7": 7, "8": 8}
SRC = "data/processed/H124-small-n-meanfield-benchmark/results"


def load():
    R = L.OUT / "results"
    return (json.loads((R / "percall.json").read_text()), json.loads((R / "grid.json").read_text()),
            json.loads((R / "n1.json").read_text()), json.loads((R / "n2.json").read_text()),
            pl.read_parquet(L.OUT / "synthetic/s4.parquet"), pl.read_parquet(L.OUT / "synthetic/s21.parquet"))


def numbers(pc, gr, n1, n2, s4, s21):
    out = {"units": list(pc)}
    full = lambda r, k: r[k]["cover"] == 1.0  # noqa: E731
    out["informative_units"] = [u for u, r in pc.items() if r["informative"]]
    out["nu_J_range"] = [min(r["nu_J"] for r in pc.values()), max(r["nu_J"] for r in pc.values())]
    for k in ("nMF", "TAP", "MS", "nMF|s"):
        e = [r[k]["epsJ"] for r in pc.values()]
        out[f"percall_{k}_epsJ_med"] = float(np.nanmedian(e))
        out[f"percall_{k}_within10_full"] = [u for u, r in pc.items() if full(r, k) and r[k]["epsJ"] <= 0.10]
        out[f"percall_{k}_within25_full"] = [u for u, r in pc.items() if full(r, k) and r[k]["epsJ"] <= 0.25]
        out[f"percall_{k}_cover"] = {u: r[k]["cover"] for u, r in pc.items()}
    out["maxJii"] = {u: float(max(r["Jii"])) for u, r in pc.items()}
    out["ll_gap_vs_ML"] = {u: {k: r["heldout_ll"][k] - r["heldout_ll"]["ML"] for k in ("nMF", "TAP", "MS", "nMF|s")}
                           for u, r in pc.items()}
    for ch in ("talk", "act"):
        for k in ("nMF", "TAP", "MS"):
            vals = {u: (g[ch][k]["epsJ"], g[ch][k]["cover"]) for u, g in gr.items() if ch in g and "error" not in g[ch]}
            out[f"grid_{ch}_{k}"] = vals
            out[f"grid_{ch}_{k}_within10_full"] = [u for u, (e, c) in vals.items() if c == 1.0 and e <= 0.10]
    out["n1"] = n1
    out["n2"] = n2
    # synthetic ranking agreement (truth vs ML) per cell, plain + stratified methods with full cover
    meth = ["nMF", "MS", "nMF|s", "TAP|s"]
    agree = []
    for df, keys in ((s4, ["schedule", "Jii", "s"]), (s21, ["Jii", "s"])):
        for _, g in df.group_by(keys):
            rt = np.argsort([g[f"{m}_epsJ_true"].median() for m in meth])
            rm = np.argsort([g[f"{m}_epsJ_ml"].median() for m in meth])
            agree.append(int(meth[rt[0]] == meth[rm[0]]))
    out["synthetic_best_method_agree"] = [int(sum(agree)), len(agree)]
    out["s4"] = s4.group_by("schedule", "Jii", "s").agg(
        [pl.col(f"{m}_epsJ_true").median().alias(f"{m}_true") for m in ("ML", "nMF", "MS", "nMF|s")]
        + [pl.col("TAP_cover").mean().alias("TAP_cover")]).sort("schedule", "Jii", "s").to_dicts()
    out["s21"] = s21.group_by("Jii", "s").agg(
        [pl.col(f"{m}_epsJ_true").median().alias(f"{m}_true") for m in ("ML", "nMF", "MS", "nMF|s")]
        + [pl.col(f"{m}_epsJ_ml").median().alias(f"{m}_ml") for m in ("nMF", "MS", "nMF|s")]
        + [pl.col("TAP_cover").mean().alias("TAP_cover")]).sort("Jii", "s").to_dicts()
    return out


def estimates(pc, gr, n2):
    import estimates as ES
    rows = []
    for u, r in pc.items():
        base = {"period_unit": u, "goal_no": GOAL[u], "role": "replication", "source": f"{SRC}/percall.json",
                "n": float(sum(r["n_rows"])), "n_kind": "calls"}
        for k in L.METHODS:
            lo, hi = r[k]["epsJ_ci"]
            rows.append({**base, "statistic": f"epsJ_{k}", "channel": "percall_talk", "estimate": r[k]["epsJ"],
                         "ci_lo": lo, "ci_hi": hi, "ci_kind": "percentile" if lo is not None else "none",
                         "method": "off-diagonal Frobenius error vs exact ML, day bootstrap 200",
                         "null": "ML noise nu_J (median bootstrap) " + f"{r['nu_J']:.2f}",
                         "notes": f"cover={r[k]['cover']}"})
        rows.append({**base, "statistic": "nu_J_ML", "channel": "percall_talk", "estimate": r["nu_J"], "ci_lo": None,
                     "ci_hi": None, "ci_kind": "none", "method": "median day-bootstrap relative change of ML J (off-diag)",
                     "null": "none"})
        rows.append({**base, "statistic": "normJ_off_ML", "channel": "percall_talk", "estimate": r["normJ_off"],
                     "ci_lo": None, "ci_hi": None, "ci_kind": "none", "method": "Frobenius norm of off-diagonal ML J",
                     "null": f"circular-shift null q95 {r['normJ_off_null_q95']:.3f}",
                     "notes": f"informative={r['informative']}"})
        rows.append({**base, "statistic": "Jbar_off_ML", "channel": "percall_talk", "estimate": r["Jbar_off"],
                     "ci_lo": r["Jbar_ci"][0], "ci_hi": r["Jbar_ci"][1], "ci_kind": "percentile",
                     "method": "mean off-diagonal ML coupling, day bootstrap", "null": "0"})
        rows.append({**base, "statistic": "max_self_coupling_Jii", "channel": "percall_talk",
                     "estimate": float(max(r["Jii"])), "ci_lo": None, "ci_hi": None, "ci_kind": "none",
                     "method": "max over agents of ML J_ii (own persistence)", "null": "none"})
        for k in ("nMF", "TAP", "MS", "nMF|s"):
            rows.append({**base, "statistic": f"heldout_ll_gap_{k}", "channel": "percall_talk",
                         "estimate": r["heldout_ll"][k] - r["heldout_ll"]["ML"], "ci_lo": None, "ci_hi": None,
                         "ci_kind": "none", "method": "leave-one-day-out mean log-lik per call minus ML's",
                         "null": "0 = as good as exact ML"})
    for u, g in gr.items():
        for ch, x in g.items():
            if "error" in x:
                continue
            for k in L.METHODS:
                lo, hi = x[k]["epsJ_ci"]
                rows.append({"period_unit": u, "goal_no": GOAL[u], "role": "replication", "source": f"{SRC}/grid.json",
                             "statistic": f"epsJ_{k}", "channel": f"grid1min_{ch}", "estimate": x[k]["epsJ"],
                             "ci_lo": lo, "ci_hi": hi, "ci_kind": "percentile" if lo is not None else "none",
                             "n": float(sum(x["n_rows"]) / 4), "n_kind": "minutes",
                             "method": "off-diagonal error vs exact ML (parallel grid), day bootstrap 100",
                             "null": f"nu_J {x['nu_J']}", "notes": f"cover={x[k]['cover']}"})
    for nd, v in n2.items():
        for k in ("nMF", "TAP", "MS", "nu_full"):
            rows.append({"period_unit": "8", "goal_no": 8, "role": "native", "source": f"{SRC}/n2.json",
                         "statistic": f"n2_{k}_days{nd}", "channel": "percall_talk", "estimate": v[k],
                         "ci_lo": None, "ci_hi": None, "ci_kind": "none", "n": 20.0, "n_kind": "subsamples",
                         "method": "median over 20 day subsamples", "null": "none"})
    w = ES.write_estimates(rows, hypothesis="H124")
    print("estimates rows:", w.height)


def figures(pc, gr, n2, s4, s21):
    FIG.mkdir(exist_ok=True)
    plt.rcParams.update({"font.size": 8, "axes.spines.top": False, "axes.spines.right": False,
                         "axes.edgecolor": INK2, "xtick.color": INK2, "ytick.color": INK2})
    fig, ax = plt.subplots(1, 3, figsize=(7.2, 2.5))
    for k in ("nMF", "TAP", "MS", "nMF|s"):
        xs, ys, hollow = [], [], []
        for u, r in pc.items():
            if r[k]["epsJ"] != r[k]["epsJ"]:
                continue
            xs.append(max(r["Jii"]))
            ys.append(r[k]["epsJ"])
            hollow.append(r[k]["cover"] < 1)
        xs, ys, hollow = map(np.array, (xs, ys, hollow))
        ax[0].scatter(xs[~hollow], ys[~hollow], s=14, color=COL[k], label=k)
        ax[0].scatter(xs[hollow], ys[hollow], s=14, facecolors="none", edgecolors=COL[k])
    ax[0].axhline(0.10, color=INK2, lw=0.8, ls=":")
    ax[0].axhline(0.25, color=INK2, lw=0.8, ls="--")
    ax[0].set(yscale="log", xlabel="max self-coupling J_ii (per-call talk)", ylabel="ε_J vs exact ML",
              title="real units (open = partial cover)")
    ax[0].legend(frameon=False, fontsize=6.5, loc="upper left")
    g = s4.filter(pl.col("schedule") == "4c")
    for k in ("ML", "nMF", "MS", "nMF|s"):
        for jii, ls in ((0.5, "-"), (1.5, "--")):
            x = g.filter(pl.col("Jii") == jii).group_by("s").agg(pl.col(f"{k}_epsJ_true").median()).sort("s")
            ax[1].plot(x["s"], x[f"{k}_epsJ_true"], ls, marker="o", ms=3, color=COL[k], lw=1,
                       label=k if jii == 0.5 else None)
    ax[1].set(yscale="log", xlabel="off-diagonal coupling scale σ_J", ylabel="ε_J vs true J",
              title="synthetic S4 (— J_ii 0.5, -- 1.5)")
    ax[1].legend(frameon=False, fontsize=6.5)
    nd = sorted(int(k) for k in n2)
    for k in ("nMF", "MS"):
        ax[2].plot(nd, [n2[str(d)][k] for d in nd], "o-", ms=3, color=COL[k], label=f"{k} bias vs ML")
    ax[2].plot(nd, [n2[str(d)]["TAP"] for d in nd], "o:", ms=3, color=COL["TAP"], label="TAP (half the rows)")
    ax[2].plot(nd, [n2[str(d)]["nu_full"] for d in nd], "s-", ms=3, color=COL["ML"], label="ML vs full-data ML")
    ax[2].set(xscale="log", yscale="log", xlabel="days used (G08)", ylabel="relative error", title="N2 data length")
    ax[2].set_xticks(nd, [str(d) for d in nd])
    ax[2].xaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
    ax[2].legend(frameon=False, fontsize=5.5, loc="upper right")
    for a_ in ax:
        a_.title.set_fontsize(7.5)
    fig.tight_layout()
    fig.savefig(FIG / "benchmark.pdf")
    plt.close(fig)


def compact(pc, n2, s4, s21):
    """Two-panel figures for the 2-page summary (about 4 in wide)."""
    fig, ax = plt.subplots(1, 2, figsize=(4.2, 2.0))
    for k in ("nMF", "TAP", "MS"):
        xs, ys, hol = [], [], []
        for u, r in pc.items():
            if r[k]["epsJ"] == r[k]["epsJ"]:
                xs.append(max(r["Jii"]))
                ys.append(r[k]["epsJ"])
                hol.append(r[k]["cover"] < 1)
        xs, ys, hol = map(np.array, (xs, ys, hol))
        ax[0].scatter(xs[~hol], ys[~hol], s=10, color=COL[k], label=k)
        ax[0].scatter(xs[hol], ys[hol], s=10, facecolors="none", edgecolors=COL[k])
    ax[0].axhline(0.10, color=INK2, lw=0.7, ls=":")
    ax[0].axhline(0.25, color=INK2, lw=0.7, ls="--")
    ax[0].set(yscale="log")
    ax[0].set_xlabel("max self-coupling J_ii", fontsize=6.5)
    ax[0].set_ylabel("ε_J vs exact ML", fontsize=6.5)
    ax[0].set_title("(a) 9 real N = 4 units", fontsize=7)
    ax[0].legend(frameon=False, fontsize=5.5, loc="upper left")
    for k in ("ML", "nMF", "MS", "nMF|s"):
        x = s21.group_by("Jii").agg(pl.col(f"{k}_epsJ_true").median()).sort("Jii")
        y4 = s4.filter((pl.col("schedule") == "4c") & (pl.col("s") == 0.3)).group_by("Jii") \
            .agg(pl.col(f"{k}_epsJ_true").median()).sort("Jii")
        ax[1].plot(y4["Jii"], y4[f"{k}_epsJ_true"], "o-", ms=2.5, lw=0.9, color=COL[k], label=k)
        ax[1].plot(x["Jii"], x[f"{k}_epsJ_true"], "s--", ms=2.5, lw=0.9, color=COL[k])
    ax[1].set(yscale="log")
    ax[1].set_xlabel("planted J_ii", fontsize=6.5)
    ax[1].set_ylabel("ε_J vs true J", fontsize=6.5)
    ax[1].set_title("(b) synthetic: N = 4 (—), N = 21 (--)", fontsize=7)
    ax[1].legend(frameon=False, fontsize=5.5)
    for a_ in ax:
        a_.tick_params(labelsize=6)
    fig.tight_layout()
    fig.savefig(FIG / "summary_obs.pdf")
    plt.close(fig)
    fig, ax = plt.subplots(figsize=(3.2, 1.9))
    nd = sorted(int(k) for k in n2)
    for k in ("nMF", "MS"):
        ax.plot(nd, [n2[str(d)][k] for d in nd], "o-", ms=2.5, color=COL[k], label=f"{k} vs same-data ML")
    ax.plot(nd, [n2[str(d)]["nu_full"] for d in nd], "s-", ms=2.5, color=COL["ML"], label="ML vs 18-day ML")
    ax.set(xscale="log", yscale="log")
    ax.set_xticks(nd, [str(d) for d in nd])
    ax.xaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
    ax.yaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
    ax.set_xlabel("days used (G08)", fontsize=6.5)
    ax.set_ylabel("relative error", fontsize=6.5)
    ax.tick_params(labelsize=6)
    ax.legend(frameon=False, fontsize=5.5)
    fig.tight_layout()
    fig.savefig(FIG / "summary_n2.pdf")
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-estimates", action="store_true")
    a = ap.parse_args()
    pc, gr, n1, n2, s4, s21 = load()
    n = numbers(pc, gr, n1, n2, s4, s21)
    (L.OUT / "results/summary.json").write_text(json.dumps(n, indent=1, default=float))
    print(json.dumps({k: v for k, v in n.items() if k not in ("s4",)}, indent=1, default=float))
    figures(pc, gr, n2, s4, s21)
    compact(pc, n2, s4, s21)
    if not a.no_estimates:
        estimates(pc, gr, n2)


if __name__ == "__main__":
    main()
