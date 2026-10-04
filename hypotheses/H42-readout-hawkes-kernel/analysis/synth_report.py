"""Score the synthetic validation (G1) and draw figures/synthetic_compact.pdf.

Usage: uv run python hypotheses/H42-readout-hawkes-kernel/analysis/synth_report.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

import h42lib as L  # noqa: E402

FIG = HERE.parent / "figures"
INK, INK2, GRID = "#0b0b0b", "#52514e", "#e4e3df"
C1, C2, C3 = "#2a78d6", "#eb6834", "#1baf7a"
WORLD_SPECS = {"pr": ["S0", "A", "A_g", "B", "C"], "A": ["S0", "A", "B_t"], "B": ["S0", "B", "A_g", "C_g"]}


def selected(r, w):
    specs = WORLD_SPECS[w]
    v = {s: r.get(f"{w}:{s}:cv") for s in specs}
    return max(v, key=lambda s: -np.inf if v[s] is None else v[s])


def main():
    df = pl.read_parquet(L.DATA / "synthetic/synthetic.parquet")
    rows = df.to_dicts()
    out = {"n": len(rows), "units": sorted(set(r["unit_id"] for r in rows))}
    for truth in ("B", "A", "0"):
        sub = [r for r in rows if r["truth"] == truth]
        d = {"n": len(sub)}
        for w in ("pr", "A", "B"):
            sel = [selected(r, w) for r in sub]
            d[f"{w}:selected"] = {s: sel.count(s) for s in set(sel)}
        if truth == "B":
            d["pr:B_or_C_selected"] = np.mean([selected(r, "pr") in ("B", "C") for r in sub])
            d["B:B_or_Cg_selected"] = np.mean([selected(r, "B") in ("B", "C_g") for r in sub])
            d["A:Bt_selected"] = np.mean([selected(r, "A") == "B_t" for r in sub])
            for w, s in (("pr", "B"), ("B", "B"), ("A", "A"), ("A", "B_t"), ("B", "A_g"), ("pr", "A_g")):
                rel = [r[f"{w}:{s}:nx"] / r["n_x_true"] - 1 for r in sub]
                d[f"{w}:{s}:rel_err_median"] = float(np.median(rel))
                d[f"{w}:{s}:within25"] = float(np.mean(np.abs(rel) <= 0.25))
            d["B:B:share01_median"] = float(np.median([r["B:B:share01"] for r in sub]))
            d["B:C_g:Bshare_median"] = float(np.median([r["B:C_g:Bshare"] for r in sub]))
            d["pr:C:Bshare_median"] = float(np.median([r["pr:C:Bshare"] for r in sub]))
            d["B:B_gt_null_q95"] = float(np.mean([r["B:B:nx"] > r["B:B:null_q95"] for r in sub]))
            d["B:B_gt_db_max"] = float(np.mean([r["B:B:nx"] > (r["B:B:db_max"] if r["B:B:db_max"] == r["B:B:db_max"] else 0) for r in sub]))
            d["B:null_mean_median"] = float(np.median([r["B:B:null_mean"] for r in sub]))
            d["B:db_mean_median"] = float(np.nanmedian([r["B:B:db_mean"] for r in sub]))
        if truth == "A":
            d["pr:B_not_over_A"] = np.mean([r["pr:A:cv"] > r["pr:B:cv"] for r in sub])
            d["B:Ag_over_B"] = np.mean([r["B:A_g:cv"] > r["B:B:cv"] for r in sub])
            d["A:A_over_Bt"] = np.mean([r["A:A:cv"] > r["A:B_t:cv"] for r in sub])
            for w, s in (("A", "A"), ("B", "B"), ("B", "A_g"), ("pr", "B")):
                rel = [r[f"{w}:{s}:nx"] / r["n_x_true"] - 1 for r in sub]
                d[f"{w}:{s}:rel_err_median"] = float(np.median(rel))
        if truth == "0":
            for w, s in (("pr", "B"), ("A", "A"), ("B", "B")):
                d[f"{w}:{s}:nx_median"] = float(np.median([r[f"{w}:{s}:nx"] for r in sub]))
                d[f"{w}:{s}:nx_max"] = float(np.max([r[f"{w}:{s}:nx"] for r in sub]))
                d[f"{w}:{s}:within_shift_q95"] = float(np.mean([r[f"{w}:{s}:nx"] <= r[f"{w}:{s}:null_q95"] + 1e-9 for r in sub]))
                dbm = [r[f"{w}:{s}:db_max"] for r in sub]
                d[f"{w}:{s}:within_db_max"] = float(np.mean([r[f"{w}:{s}:nx"] <= (x if x == x else np.inf) + 1e-9
                                                            for r, x in zip(sub, dbm)]))
            d["B:gainB_pos"] = float(np.mean([r["B:B:cv"] > r["B:S0:cv"] for r in sub]))
            d["A:gainA_pos"] = float(np.mean([r["A:A:cv"] > r["A:S0:cv"] for r in sub]))
            d["pr:gainB_pos"] = float(np.mean([r["pr:B:cv"] > r["pr:S0:cv"] for r in sub]))
        out[truth] = d
    (L.DATA / "synthetic/synthetic_summary.json").write_text(json.dumps(out, indent=1, default=float))
    print(json.dumps(out, indent=1, default=float))

    # figure: estimated vs true n_x for each world's own cross spec, by truth
    FIG.mkdir(exist_ok=True)
    fig, axes = plt.subplots(1, 3, figsize=(7.0, 2.3), sharey=True)
    specs = [("pr", "B", "world pr: B"), ("A", "A", "world A: A"), ("B", "B", "world B: B")]
    marks = {"B": ("o", C1, "read-out truth"), "A": ("s", C2, "exponential truth"), "0": ("^", C3, "no cross truth")}
    for ax, (w, s, title) in zip(axes, specs):
        ax.plot([0, 0.65], [0, 0.65], color=INK2, lw=0.8, ls=":")
        for truth, (m, c, lab) in marks.items():
            sub = [r for r in rows if r["truth"] == truth]
            ax.scatter([r["n_x_true"] for r in sub], [r[f"{w}:{s}:nx"] for r in sub], s=22, marker=m,
                       facecolor=c, edgecolor="white", linewidth=0.8, label=lab, zorder=3)
        ax.set_title(title, fontsize=8, color=INK)
        ax.set_xlim(-0.02, 0.4); ax.set_ylim(-0.02, 0.65)
        ax.set_xlabel("planted $n_x$ (realized)", fontsize=7, color=INK2)
        ax.tick_params(labelsize=6.5, colors=INK2)
        ax.grid(color=GRID, lw=0.5)
        for sp_ in ax.spines.values():
            sp_.set_color(GRID)
    axes[0].set_ylabel("estimated $n_x$", fontsize=7, color=INK2)
    axes[0].legend(fontsize=6, frameon=False, loc="upper left")
    fig.tight_layout(pad=0.4)
    fig.savefig(FIG / "synthetic_compact.pdf")
    print("figure written")


if __name__ == "__main__":
    main()
