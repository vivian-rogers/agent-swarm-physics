"""Column-width figures for the H50 summary page: (1) the call-cycle kernel and the field/coupling split by regime;
(2) the synthetic validation."""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "data/processed/H50-field-vs-coupling-transfer-lag"
FIG = ROOT / "hypotheses/H50-field-vs-coupling-transfer-lag/figures"
BLUE, ORANGE, AQUA, GRAY, INK = "#2a78d6", "#eb6834", "#1baf7a", "#8a8984", "#0b0b0b"


def ivw(est, se):
    est, se = np.asarray(est, float), np.asarray(se, float)
    ok = np.isfinite(est) & np.isfinite(se) & (se > 0)
    w = 1 / se[ok] ** 2
    m = (w * est[ok]).sum() / w.sum()
    s = 1 / np.sqrt(w.sum())
    return m, m - 1.96 * s, m + 1.96 * s


def style(ax):
    ax.tick_params(labelsize=6)
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)


def main():
    T = pl.read_parquet(OUT / "unit_table.parquet").filter(~pl.col("ne43"))
    R = {}
    for p in OUT.glob("G*/*.json"):
        if p.name != "native.json":
            r = json.loads(p.read_text())
            R[r["unit"]] = r
    fig, axes = plt.subplots(1, 2, figsize=(3.4, 1.9), gridspec_kw=dict(width_ratios=[1.35, 1]))
    ax = axes[0]
    for reg, col, dx in (("I", BLUE, -0.08), ("III", ORANGE, 0.08)):
        us = T.filter(pl.col("regime") == reg)["unit"].to_list()
        K = np.array([R[u]["gate_talk"]["kernel"] for u in us], float)
        SE = np.array([R[u]["gate_talk"]["k_se"] for u in us], float)
        pts = [ivw(K[:, k], SE[:, k]) for k in range(K.shape[1])]
        m = np.r_[0, [p[0] for p in pts]]
        lo = np.r_[0, [p[1] for p in pts]]
        hi = np.r_[0, [p[2] for p in pts]]
        h = np.arange(0, len(m)) + dx
        ax.fill_between(h, lo, hi, color=col, alpha=0.18, lw=0)
        ax.plot(h, m, "o-", color=col, ms=2.5, lw=1, label=f"regime {reg}")
    ax.axhline(0, color=GRAY, lw=0.6)
    ax.set_xticks(range(7))
    ax.set_xlabel("hop (recipient's calls after the message)", fontsize=6)
    ax.set_ylabel("extra P(talk call)", fontsize=6)
    ax.set_title("peer coupling in call cycles", fontsize=6.5)
    ax.legend(fontsize=5.5, frameon=False, loc="upper left")
    style(ax)
    ax = axes[1]
    cols = [("attr_A_full_edges", "activity:\nschedule field", GRAY), ("fC_T_span", "talk:\ncoupling", ORANGE)]
    for i, (c, lab, col) in enumerate(cols):
        for j, (reg, mk) in enumerate((("I", "o"), ("III", "s"))):
            v = T.filter(pl.col("regime") == reg)[c].drop_nulls().drop_nans().to_numpy()
            q = np.percentile(v, [25, 50, 75])
            x = i + (j - 0.5) * 0.3
            ax.plot([x, x], [q[0], q[2]], color=col, lw=1.2)
            ax.plot([x], [q[1]], mk, color=col, ms=3.5, mfc="white" if reg == "I" else col)
    ax.set_xticks([0, 1])
    ax.set_xticklabels([c[1] for c in cols], fontsize=5.5)
    ax.set_ylim(0, 1.3)
    ax.set_ylabel("share of co-movement", fontsize=6)
    ax.set_title("median, IQR (o: I, s: III)", fontsize=6)
    style(ax)
    fig.tight_layout(pad=0.4)
    fig.savefig(FIG / "summary_kernel_split_col.pdf")
    plt.close(fig)
    # ---------------- synthetic validation (column)
    R2 = json.load(open(OUT / "synthetic" / "synthetic_results.json"))
    Ssum = json.load(open(OUT / "synthetic" / "synthetic_summary.json"))
    order = [("S0_null", "null"), ("S1_field", "field"), ("S4_ou", "slow common drive"), ("S5f_field_ou", "field + drive"),
             ("S2_coupling", "coupling"), ("S3_both", "field + coupling"), ("S5_all", "all three"),
             ("S6_edge_clustered", "all, inputs at edges"), ("S7_dead", "coupling, dead time 2"), ("S8_ungated", "ungated coupling")]
    fig, ax = plt.subplots(figsize=(3.4, 2.0))
    for i, (n, lab) in enumerate(order):
        js = [r["gate_talk"]["jumps"][0] for r in R2[n]]
        ax.scatter(js, [i] * len(js), s=8, color=BLUE, alpha=0.65, lw=0, zorder=3)
        ax.scatter([Ssum["scenarios"][n]["truth1"]], [i], marker="|", s=80, color=INK, lw=1.5, zorder=4)
    ax.axvline(0, color=GRAY, lw=0.6)
    ax.set_yticks(range(len(order)))
    ax.set_yticklabels([l for _, l in order], fontsize=5.5)
    ax.invert_yaxis()
    ax.set_xlabel("hop-1 read-out jump $J_1$ in P(talk call)", fontsize=6)
    ax.set_title("synthetic: estimate (dots, 5 seeds) vs planted (bar)", fontsize=6.2)
    style(ax)
    fig.tight_layout(pad=0.4)
    fig.savefig(FIG / "synthetic_col.pdf")
    plt.close(fig)


if __name__ == "__main__":
    main()
