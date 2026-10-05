"""H05 round 2 summary figure (no new analysis): reads data/processed/H05-rooms-cut/r2/r2_results.json.
(a) R1: co-edit share of pair-days, within vs cross room, per two-room window, and NE42 cut pairs.
(b) R2: room-size dilution exponents vs H18's 0.45, and NE42 stay-pair talk coupling vs the dilution prediction.
(c) R3: conductance per exposure (excess adoptions within 2 h over the matched placebo rate).
Usage: uv run python hypotheses/H05-rooms-cut/analysis/r2_figure.py -> figures/r2_summary.pdf
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
D = json.loads((ROOT / "data/processed/H05-rooms-cut/r2/r2_results.json").read_text())
OUT = Path(__file__).resolve().parents[1] / "figures/r2_summary.pdf"
BLUE, ORANGE, GRAY = "#2a78d6", "#eb6834", "#8a8984"
INK, INK2 = "#0b0b0b", "#52514e"
plt.rcParams.update({"font.size": 6.5, "axes.edgecolor": INK2, "axes.labelcolor": INK, "xtick.color": INK2,
                     "ytick.color": INK2, "axes.spines.top": False, "axes.spines.right": False, "font.family": "sans-serif",
                     "pdf.fonttype": 42})


def main():
    fig, axs = plt.subplots(2, 2, figsize=(6.8, 3.6))
    ax = [axs[0, 0], axs[0, 1], axs[1, 0], axs[1, 1]]
    # (a)
    w = D["R1"]["P1_windows"]
    gs = [g for g in w]
    x = range(len(gs))
    ax[0].bar([i - 0.2 for i in x], [w[g]["within_share"] for g in gs], 0.38, color=BLUE, label="same room")
    ax[0].bar([i + 0.2 for i in x], [w[g]["cross_share"] for g in gs], 0.38, color=ORANGE, label="different rooms")
    ax[0].set_xticks(list(x)); ax[0].set_xticklabels([f"#{g}" for g in gs])
    ax[0].set_ylabel("pair-days co-editing a repo"); ax[0].legend(frameon=False, fontsize=5.5, loc="upper center", ncol=2)
    ax[0].set_ylim(0, 1.0)
    n42 = D["R1"]["P1_NE42_cut_pairs_coedit_share"]
    ax[0].set_title(f"(a) artifacts follow rooms (NE42 cut pairs #39/#40/#41: {n42['39']:.2f} / {n42['40']:.2f} / {n42['41']:.2f})", fontsize=6, loc="left")
    # (b) exponents
    R2 = D["R2"]
    est = [("κ_x pooled", R2["P1_kappa_none"]["beta_hat"], R2["P1_kappa_none"]["beta_ci95"], GRAY),
           ("uptake pooled*", R2["P2_uptake_mention"]["beta_u"], R2["P2_uptake_mention"]["beta_ci95"], GRAY),
           ("uptake #37–#44", R2["P2_uptake_mention_two_room_era"]["beta_u"], R2["P2_uptake_mention_two_room_era"]["beta_ci95"], BLUE),
           ("reply #37–#44", R2["posthoc_uptake"]["reply_two_room_era"]["beta_u"], R2["posthoc_uptake"]["reply_two_room_era"]["beta_ci95"], BLUE)]
    for k, (lab, b, ci, c) in enumerate(est):
        ax[1].errorbar(b, k, xerr=[[b - ci[0]], [ci[1] - b]], fmt="o", color=c, ms=3, lw=1, capsize=1.5)
    ax[1].axvline(0.45, color=ORANGE, lw=1, ls="--"); ax[1].axvline(0, color=INK2, lw=0.5)
    ax[1].set_yticks(range(len(est))); ax[1].set_yticklabels([e[0] for e in est]); ax[1].invert_yaxis()
    ax[1].set_xlabel("dilution exponent β (dashed: H18 0.45)")
    ax[1].set_title("(b) room-size dilution", fontsize=6, loc="left")
    # (b2) NE42 levels
    n = R2["P3_NE42"]
    ax[2].plot([0, 1, 2], [n["kappa_39"], n["kappa_40"], n["kappa_41"]], "o-", color=BLUE, ms=3, lw=1, label="observed")
    ax[2].plot([0, 1, 2], [n["kappa_39"], n["pred_40_dilution"], n["kappa_39"]], "s--", color=ORANGE, ms=3, lw=1, label="dilution (β 0.45)")
    ax[2].set_xticks([0, 1, 2]); ax[2].set_xticklabels(["#39", "#40\nmerged", "#41"])
    ax[2].set_ylabel("stay pairs' talk κ_x"); ax[2].legend(frameon=False, fontsize=5.5, loc="upper left")
    ax[2].set_title("(c) NE42: coupling moves more than dilution", fontsize=6, loc="left")
    # (c) conductance
    R3 = D["R3"]
    rows = [("output, cross-room", R3["P1_output_cross"], ORANGE), ("search, cross-room", R3["P1_search_cross"], ORANGE),
            ("chat read, same room", R3["chat_within"], BLUE), ("output, same room", R3["output_within_reference"], BLUE)]
    for k, (lab, r, c) in enumerate(rows):
        ax[3].errorbar(r["excess"], k, xerr=[[r["excess"] - r["excess_ci95"][0]], [r["excess_ci95"][1] - r["excess"]]],
                       fmt="o", color=c, ms=3, lw=1, capsize=1.5)
        ax[3].text(0.62, k, f"n={r['n_exposures']}", va="center", fontsize=5, color=INK2)
    ax[3].axvline(0, color=INK2, lw=0.5); ax[3].set_xlim(-0.05, 0.75)
    ax[3].set_yticks(range(len(rows))); ax[3].set_yticklabels([r[0] for r in rows]); ax[3].invert_yaxis()
    ax[3].set_xlabel("adoptions per exposure over placebo (2 h)")
    ax[3].set_title("(d) leak conductance", fontsize=6, loc="left")
    fig.tight_layout(w_pad=1.0, h_pad=1.0)
    fig.savefig(OUT)
    print("wrote", OUT)


if __name__ == "__main__":
    main()
