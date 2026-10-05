"""H69 round-2 figure: figures/r2_obs.pdf (forest of the round-2 effects, per period and pooled)."""
from __future__ import annotations

import json
import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
D = ROOT / "data/processed/H69-loops-context-fixed-points"
FIG = HERE.parent / "figures"
COL = {"G38": "#2a78d6", "G39": "#7a5cc4", "G40": "#e3a21a", "G41": "#0ca30c", "G51": "#c43a3a"}

ROWS = [  # label, per-period path to (b, se) or MH dict, pooled key, kind
    ("R1 onset: own tool tokens", ["r1_all", "U_k"], "R1_all_bU", "se"),
    ("R1 onset: own statements (tokens in model)", ["r1_all", "o_ctx"], "R1_all_bO", "se"),
    ("R2 exit: erasure x own tokens removed", ["r2_exit_dose", "dose_c"], "R2_exit_dose", "se"),
    ("R3 erased source in memory vs not", ["r3", "P1"], "R3_P1", "or"),
    ("R3 newly written into memory vs not", ["r3", "P2_new"], "R3_P2_new", "or"),
    ("post hoc: exit after erasure, source not in memory", ["posthoc_exit_mem", "terms", "erased"],
     "POSTHOC_exit_erased", "se"),
    ("post hoc: x looping content in memory", ["posthoc_exit_mem", "terms", "erased_inmem"],
     "POSTHOC_exit_erased_inmem", "se"),
]


def get(o, path):
    for k in path:
        if not isinstance(o, dict):
            return None
        o = o.get(k)
    return o


def main():
    FIG.mkdir(exist_ok=True)
    r = json.loads((D / "results_r2.json").read_text())
    per, po = r["periods"], r["pooled"]
    fig, ax = plt.subplots(figsize=(4.6, 3.0))
    y0 = np.arange(len(ROWS))[::-1]
    for yi, (lab, path, pk, kind) in zip(y0, ROWS):
        for j, p in enumerate(COL):
            d = get(per[p], path)
            if not d:
                continue
            if kind == "se":
                b, s = d.get("b"), d.get("se")
                if b is None or s is None or not (math.isfinite(b) and math.isfinite(s)):
                    continue
                lo, hi = b - 1.96 * s, b + 1.96 * s
            else:
                b, lo, hi = d.get("log_or"), d.get("lo"), d.get("hi")
                if b is None or not all(math.isfinite(v) for v in (b, lo, hi)):
                    continue
            yy = yi + 0.11 * (j - 2)
            ax.plot([max(lo, -4.5), min(hi, 4.9)], [yy, yy], color=COL[p], lw=0.8, alpha=0.7)
            ax.plot(min(max(b, -4.5), 4.9), yy, "o", ms=2.5, color=COL[p])
        q = po.get(pk) or {}
        if q.get("k"):
            ax.plot([max(q["lo"], -4.5), min(q["hi"], 4.9)], [yi - 0.4, yi - 0.4], color="black", lw=1.6)
            ax.plot(q["mean"], yi - 0.4, "D", ms=4, color="black")
    ax.axvline(0, color="gray", lw=0.6)
    ax.axvline(math.log(2), color="gray", lw=0.6, ls=":")
    ax.set_yticks(y0)
    ax.set_yticklabels([x[0] for x in ROWS], fontsize=6.3)
    ax.set_xlabel("log odds ratio (per log unit for R1, R2)", fontsize=7)
    ax.tick_params(axis="x", labelsize=7)
    for p, c in COL.items():
        ax.plot([], [], "o", color=c, ms=3, label=p)
    ax.plot([], [], "D", color="black", ms=3, label="pooled (RE)")
    ax.legend(fontsize=5.3, loc="lower center", frameon=False, ncol=6, bbox_to_anchor=(0.4, 1.0), handletextpad=0.2,
              columnspacing=0.8)
    ax.set_xlim(-4.5, 5.0)
    fig.tight_layout()
    fig.savefig(FIG / "r2_obs.pdf")
    plt.close(fig)


if __name__ == "__main__":
    main()
