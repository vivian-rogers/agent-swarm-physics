"""H136 round-1 figure: structural precondition counts and synthetic O1 power (no real freeze time is used).

  uv run python hypotheses/H136-freeze-at-first-kickoff-read/analysis/figures.py  ->  figures/h136_obs.pdf
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

HERE = Path(__file__).resolve().parents[1]
D = HERE.parents[1] / "data/processed/H136-freeze-at-first-kickoff-read"
BLUE, ORANGE, GRAY, INK2 = "#2a78d6", "#eb6834", "#b8b7b2", "#52514e"


def main():
    u = json.loads((D / "structure/units.json").read_text())["units"]
    s = json.loads((D / "synthetic/synthetic.json").read_text())["units"]
    fig, ax = plt.subplots(1, 2, figsize=(7.0, 2.9), gridspec_kw={"width_ratios": [1.7, 1]})
    names = [x["unit"].replace("best", " #b").replace("rest", " #r") for x in u]
    y = np.arange(len(u))
    nr = [x["n_readers"] for x in u]
    nd = [x["n_delayed"] for x in u]
    na = [x["n_delayed_active_readers"] for x in u]
    a = ax[0]
    a.barh(y + 0.27, nr, height=0.25, color=GRAY, label="kickoff readers")
    a.barh(y, nd, height=0.25, color=BLUE, label=r"delayed ($D_r\geq2$ min)")
    a.barh(y - 0.27, na, height=0.25, color=ORANGE, label="delayed active readers")
    a.axvline(5, color=INK2, lw=1, ls="--")
    a.text(5.2, -0.6, "precondition 5", fontsize=6.5, color=INK2)
    a.set_yticks(y, names, fontsize=6.5)
    a.invert_yaxis()
    a.set_xlabel("agents per kickoff unit", fontsize=7)
    a.tick_params(axis="x", labelsize=6.5)
    a.legend(fontsize=6, frameon=False, loc="lower left", bbox_to_anchor=(0, 1.0), ncol=3)
    for sp in ("top", "right"):
        a.spines[sp].set_visible(False)
    b = ax[1]
    su = list(s)
    x = np.arange(len(su))
    pw_all = [s[k]["pass_rule_all"]["o1_power_W1"] for k in su]
    sz_all = [s[k]["pass_rule_all"]["o1_size_W2"] for k in su]
    pw_dar = [s[k]["pass_rule_dar"]["o1_power_W1"] for k in su]
    b.bar(x - 0.2, pw_dar, width=0.36, color=ORANGE, label="power, card sample")
    b.bar(x + 0.2, pw_all, width=0.36, color=BLUE, label="power, all readers")
    b.scatter(x + 0.2, sz_all, color="k", s=10, zorder=3, label="size (W2), all readers")
    b.axhline(0.8, color=INK2, lw=1, ls="--")
    b.set_xticks(x, [k.replace("best", "#b") for k in su], fontsize=6.5)
    b.set_ylim(0, 1.05)
    b.set_ylabel("O1 read-lock call rate", fontsize=7)
    b.tick_params(axis="y", labelsize=6.5)
    b.legend(fontsize=5.5, frameon=False, loc="upper right")
    for sp in ("top", "right"):
        b.spines[sp].set_visible(False)
    fig.tight_layout()
    out = HERE / "figures"
    out.mkdir(exist_ok=True)
    fig.savefig(out / "h136_obs.pdf")
    fig.savefig(out / "h136_obs.png", dpi=150)


if __name__ == "__main__":
    main()
