"""H42 round 2 figure (single column): figures/round2_col.pdf.
(a) talk jump per read at the read-out call, regime III and I: cold-named, thread-named, unnamed (random-effects pools,
    95% CI); H67's named value as a band. (b) regime III, call timing: log gap to the next call (x100 = % per read) and
    pause probability (pp per read), excess over the call-skeleton null, named vs unnamed. (c) R3: per-unit n_x with
    round 1's shared baseline vs with the Cox field, world A (exponential) and world B named kernel (per message).
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

import r2lib as L  # noqa: E402

FIG = HERE.parent / "figures"
RED, GRAY, GREEN, BLUE = "#b2182b", "#777777", "#1a9850", "#2166ac"


def main():
    P = pl.read_parquet(L.R2 / "r2_pools.parquet")
    r3 = pl.read_parquet(L.R2 / "r3_units.parquet")
    plt.rcParams.update({"font.size": 6.5, "axes.linewidth": 0.5, "xtick.major.width": 0.5, "ytick.major.width": 0.5,
                         "xtick.major.size": 2, "ytick.major.size": 2})
    fig, ax = plt.subplots(1, 3, figsize=(3.4, 1.75), gridspec_kw={"width_ratios": [1.15, 1.0, 1.05]})
    # (a)
    a = ax[0]
    a.axhspan(0.069, 0.089, color=GRAY, alpha=0.2, lw=0)
    a.text(-0.4, 0.0915, "H67 named", fontsize=5, color=GRAY, ha="left")
    labs = [("cold", "cold"), ("thrn", "thread"), ("un", "un-\nnamed")]
    for j, (reg, col, off) in enumerate((("III", RED, -0.12), ("I", BLUE, 0.12))):
        for k, (X, _) in enumerate(labs):
            q = P.filter((pl.col("regime") == reg) & (pl.col("outcome") == "talk") & (pl.col("spec") == "r1")
                         & (~pl.col("field")) & (pl.col("X") == X))
            if len(q) == 0:
                continue
            r = q.to_dicts()[0]
            a.errorbar(k + off, r["re"], yerr=[[r["re"] - r["re_lo"]], [r["re_hi"] - r["re"]]], fmt="o", ms=2.5,
                       color=col, lw=0.8, capsize=0, label=f"regime {reg}" if k == 0 else None)
    a.axhline(0, color="k", lw=0.4)
    a.set_xticks(range(3)); a.set_xticklabels([l for _, l in labs], fontsize=5.5)
    a.set_ylabel("extra talk per read"); a.set_title("(a) mark", fontsize=6.5, loc="left")
    a.legend(fontsize=5, frameon=False, loc="center right", handletextpad=0.1, borderaxespad=0.1)
    a.set_xlim(-0.5, 2.5)
    # (b)
    b = ax[1]
    items = [("loggap", "named", 100, "gap\nN"), ("loggap", "un", 100, "gap\nU"),
             ("pause", "named", 100, "pause\nN"), ("pause", "un", 100, "pause\nU")]
    for k, (o, X, sc, lab) in enumerate(items):
        q = P.filter((pl.col("regime") == "III") & (pl.col("outcome") == o) & (pl.col("spec") == "r2")
                     & (~pl.col("field")) & (pl.col("X") == X))
        r = q.to_dicts()[0]
        col = RED if r["ex_hi"] < 0 or r["ex_lo"] > 0 else GRAY
        b.errorbar(k, sc * r["ex"], yerr=[[sc * (r["ex"] - r["ex_lo"])], [sc * (r["ex_hi"] - r["ex"])]], fmt="o",
                   ms=2.5, color=col, lw=0.8, capsize=0)
        b.plot(k, sc * r["null_mean"], "x", ms=2.5, color="k", mew=0.6)
    b.axhline(0, color="k", lw=0.4)
    b.set_xticks(range(4)); b.set_xticklabels(["N", "U", "N", "U"], fontsize=5.5)
    b.text(1.05, -4.5, "log gap", ha="center", fontsize=5.5); b.text(2.5, -4.5, "pause", ha="center", fontsize=5.5)
    b.set_ylim(-4.8, 0.8)
    b.set_ylabel("% gap, pp pause per read"); b.set_title("(b) clock, III", fontsize=6.5, loc="left")
    # (c)
    c = ax[2]
    eps = 1e-3
    for col_r1, col_f, colr, lab in (("nxA_r1", "nxA_cox10", GRAY, "exp. (A)"),
                                     ("pn_r1", "pn_fld", RED, "named")):
        x = r3[col_r1].to_numpy().astype(float); y = r3[col_f].to_numpy().astype(float)
        m = np.isfinite(x) & np.isfinite(y)
        c.scatter(np.maximum(x[m], eps), np.maximum(y[m], eps), s=3, color=colr, lw=0, alpha=0.8, label=lab)
    lim = [eps, 1.0]
    c.plot(lim, lim, color="k", lw=0.4)
    c.plot(lim, [v * 0.67 for v in lim], color="k", lw=0.4, ls=":")
    c.set_xscale("log"); c.set_yscale("log"); c.set_xlim(lim); c.set_ylim(lim)
    c.set_xlabel("round-1 baseline", fontsize=6); c.set_ylabel("Cox field", fontsize=6)
    c.set_title("(c) R3, $n_x$", fontsize=6.5, loc="left")
    c.legend(fontsize=5, frameon=False, loc="lower right", handletextpad=0.1, borderaxespad=0.1)
    for axx in ax:
        axx.tick_params(labelsize=5.5)
    fig.tight_layout(pad=0.2, w_pad=0.3)
    FIG.mkdir(exist_ok=True)
    fig.savefig(FIG / "round2_col.pdf")
    print("wrote", FIG / "round2_col.pdf")


if __name__ == "__main__":
    main()
