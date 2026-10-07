"""Single-column version of the H15 context-erasure profile (panel a of F4_context_erasure.pdf) for writeup/paper.

    uv run python writeup/paper/figs/make_h15_col.py

Imports hypotheses/H15-semantic-information-scrambles/analysis/figures.py read-only (it loads the processed H15 outputs
at import) and draws its f4 profile panel alone, in the writeup style (vstyle). Output: writeup/paper/figs/h15_erasure_col.pdf/png.
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "writeup/visuals"))
sys.path.insert(0, str(ROOT / "hypotheses/H15-semantic-information-scrambles/analysis"))

import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import vstyle as vs  # noqa: E402

vs.use()
import figures as F  # noqa: E402  (H15's module; reads consolidation_profile.parquet and results.json)

vs.use()
fig, ax = plt.subplots(figsize=(vs.W["single"], 2.2))
_dummy_fig, dummy = plt.subplots()
F.f4(ax, dummy)
plt.close(_dummy_fig)
# writeup look: fixed colors (forced = vermillion, voluntary = blue), plain title
for line, col in zip(ax.get_lines()[:2], (vs.C["red"], vs.COUPLING)):
    line.set_color(col)
    line.set_markersize(2.4)
ax.set_title("")
ax.set_xlabel("call relative to the erasure (− before, + after)")
ax.set_ylabel("work commits per call")
ax.axvspan(0.5, 10.5, color=vs.NULL, alpha=0.25, lw=0, zorder=0)
ax.text(5.5, ax.get_ylim()[1] * 0.97, "next 10 calls", ha="center", va="top", fontsize=6.3, color=vs.INK2)
ax.legend(frameon=False, fontsize=6.5, loc="lower right", title=None)
fig.tight_layout()
vs.save(fig, HERE / "h15_erasure_col")
plt.close(fig)
print("wrote", HERE / "h15_erasure_col.pdf")
