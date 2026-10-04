"""H82 visuals: the previous goal leaves a day-1 trace that does not decay within 5 days.

fig.pdf/png  (a) remanence excess dgamma_d (previous-centroid loading minus the median placebo-centroid loading) on days
             1-5 of a new goal, mean over 25 boundaries with a boundary-bootstrap 95% CI, both embeddings, against the
             synthetic no-remanence null (S0 95th percentile, gray band) and the HH's decaying-remanence prediction
             (tau_R = 1 and 5 active days, anchored at the day-1 value); (b) day-1 loadings on the past, future and
             placebo centroids (time asymmetry); (c) post hoc PH2: the trace disappears once the agent's own previous
             content is a regressor.

Inputs (read-only): data/processed/H82-remanence-endogenous-field/replication/{boundary_rows.parquet,
replication.json}, posthoc/posthoc.json.
Usage: uv run python writeup/visuals/H82-remanence-endogenous-field/make.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
VIS = HERE.parent
ROOT = VIS.parents[1]
sys.path.insert(0, str(VIS))

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402
import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

import vstyle as vs  # noqa: E402

D = ROOT / "data/processed/H82-remanence-endogenous-field"
MODELS = [("bge_small", "bge", vs.FIELD, "o", True), ("gte_modernbert", "gte", vs.INK2, "s", False)]


def boot_mean(v, B=4000, seed=0):
    v = np.asarray(v, float); v = v[np.isfinite(v)]
    rng = np.random.default_rng(seed)
    bs = rng.choice(v, (B, len(v))).mean(1)
    return float(v.mean()), float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5)), len(v)


def main():
    vs.use()
    rows = pl.read_parquet(D / "replication/boundary_rows.parquet").filter(
        (pl.col("config") == "primary") & (pl.col("term") == "e"))
    rep = json.load(open(D / "replication/replication.json"))["primary"]
    ph = json.load(open(D / "posthoc/posthoc.json"))
    fig = plt.figure(figsize=(vs.W["double"], 2.45))
    gs = fig.add_gridspec(1, 3, width_ratios=[1.35, 1.0, 0.8], wspace=0.42)
    a0, a1, a2 = (fig.add_subplot(gs[0, i]) for i in range(3))
    out = {}

    # (a) day profile
    q95 = max(rep[m]["all"]["S0_q95_mean_dg1"] for m, *_ in MODELS)
    a0.axhspan(-0.02, q95, color=vs.NULL, alpha=0.35, lw=0, zorder=0)
    a0.text(5.35, q95 - 0.004, "no-remanence null\n(S0, 95th pct)", fontsize=5.8, color=vs.INK2, ha="right", va="top")
    d = np.arange(1, 6)
    for j, (m, lab, col, mk, filled) in enumerate(MODELS):
        st = [boot_mean(rows.filter((pl.col("model") == m) & (pl.col("d") == k))["dgamma"].to_numpy(), seed=k + 10 * j)
              for k in d]
        st = np.array(st)
        out[m] = st
        off = -0.07 if j == 0 else 0.07
        a0.errorbar(d + off, st[:, 0], yerr=[st[:, 0] - st[:, 1], st[:, 2] - st[:, 0]], fmt=mk + "-", color=col,
                    mfc=col if filled else "white", mec=vs.INK, mew=0.5, ms=4, lw=1.3, capsize=1.5,
                    label=f"village {lab}")
    g1 = out["bge_small"][0, 0]
    dd = np.linspace(1, 5, 100)
    for tau, ls in ((1.0, "--"), (5.0, ":")):
        a0.plot(dd, g1 * np.exp(-(dd - 1) / tau), color=vs.C["green"], lw=1.0, ls=ls,
                label=fr"decaying remanence, $\tau_R$ = {tau:.0f} d")
    a0.axhline(0, color=vs.INK2, lw=0.5)
    a0.set_xticks(d); a0.set_xlim(0.6, 5.45); a0.set_ylim(-0.02, 0.26)
    a0.set_xlabel("active day of the new goal")
    a0.set_ylabel(r"remanence excess $\Delta\gamma_d$")
    a0.legend(loc="upper right", fontsize=5.6, borderaxespad=0.2, ncol=2, columnspacing=0.8, handlelength=1.6)
    a0.set_title("(a) the trace does not fade", loc="left")

    # (b) past vs future vs placebo centroids (day 1)
    d1 = rows.filter(pl.col("d") == 1)
    cats = [("gamma_prev", "past\n(P−1)"), ("gamma_next", "future\n(P+1)"), ("gamma_placebo_med", "placebo\n(median)")]
    for j, (m, lab, col, mk, filled) in enumerate(MODELS):
        for i, (c, _) in enumerate(cats):
            mu, lo, hi, n = boot_mean(d1.filter(pl.col("model") == m)[c].to_numpy(), seed=100 + i + 7 * j)
            x = i + (-0.17 if j == 0 else 0.17)
            a1.bar([x], [mu], width=0.32, color=col if filled else "white", edgecolor=vs.INK, lw=0.6,
                   label=lab if i == 0 else None)
            a1.errorbar([x], [mu], yerr=[[mu - lo], [hi - mu]], color=vs.INK, lw=0.8, capsize=1.5)
    a1.axhline(0, color=vs.INK2, lw=0.5)
    a1.set_xticks(range(3)); a1.set_xticklabels([t for _, t in cats], fontsize=6.3)
    a1.set_ylabel(r"day-1 loading $\gamma$ on the centroid")
    a1.legend(loc="upper right", fontsize=5.8, borderaxespad=0.2)
    a1.grid(axis="x", visible=False)
    a1.set_title("(b) past beats future", loc="left")

    # (c) PH2 own past vs village
    for j, (m, lab, col, mk, filled) in enumerate(MODELS):
        vals = [ph[m]["primary_mean_dg1"], ph[m]["PH2_own_prev_mean_dg1"]]
        xs = np.arange(2) + (-0.17 if j == 0 else 0.17)
        a2.bar(xs, vals, width=0.32, color=col if filled else "white", edgecolor=vs.INK, lw=0.6, label=lab)
        for x, v in zip(xs, vals):
            a2.text(x, v + (0.006 if v >= 0 else -0.006), f"{v:+.3f}".replace("-", "−"), ha="center",
                    va="bottom" if v >= 0 else "top", fontsize=5.0)
    a2.axhspan(-0.09, q95, color=vs.NULL, alpha=0.35, lw=0, zorder=0)
    a2.axhline(0, color=vs.INK2, lw=0.5)
    a2.set_xticks([0, 1]); a2.set_xticklabels(["village\ncentroid", "+ agent's own\nprevious content"], fontsize=6.3)
    a2.set_ylim(-0.09, 0.2)
    a2.set_ylabel(r"day-1 excess $\Delta\gamma_1$")
    a2.legend(loc="upper right", fontsize=5.8, borderaxespad=0.2)
    a2.grid(axis="x", visible=False)
    a2.set_title("(c) carried by members", loc="left")

    vs.save(fig, HERE / "fig")
    plt.close(fig)
    for m in out:
        print(m, "dgamma_d means", np.round(out[m][:, 0], 3).tolist(), "S0 q95", rep[m]["all"]["S0_q95_mean_dg1"])
    print({m: (ph[m]["primary_mean_dg1"], ph[m]["PH2_own_prev_mean_dg1"]) for m, *_ in MODELS})


if __name__ == "__main__":
    main()
