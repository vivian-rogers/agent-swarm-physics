"""H100 figures: summary_obs.pdf (decomposition per period + movers) and summary_synthetic.pdf."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h100lib as L  # noqa: E402

FIG = HERE.parent / "figures"
C1, C2, C3, GR, INK, MUT = "#2a78d6", "#eb6834", "#1baf7a", "#a9a8a1", "#0b0b0b", "#52514e"
plt.rcParams.update({"font.size": 7.5, "axes.spines.top": False, "axes.spines.right": False, "axes.edgecolor": MUT,
                     "axes.labelcolor": INK, "xtick.color": MUT, "ytick.color": MUT, "font.family": "DejaVu Sans"})
NAMES = {"20": "Opus 4.6", "21": "Sonnet 4.6", "22": "Gemini 3.1 Pro", "23": "GPT-5.4"}


def obs():
    R = json.loads((L.DATA / "results/raw_all.json").read_text())
    p, g = R["bge_small/style_resid"], R["gte_modernbert/style_resid"]
    fig, (a, b) = plt.subplots(1, 2, figsize=(7.0, 2.5), gridspec_kw={"width_ratios": [1.25, 1]})
    Ps = [36, 37, 38, 39, 41, 42, 44]
    x = np.arange(len(Ps))
    fc = [max(p["periods"][f"G{P}"]["f_comp"], 0) for P in Ps]
    ff = [max(p["periods"][f"G{P}"]["f_field"], 0) for P in Ps]
    fs = [max(1 - c - f, 0) for c, f in zip(fc, ff)]
    a.bar(x, fc, 0.62, color=C1, label="composition f_comp", edgecolor="white", linewidth=1)
    a.bar(x, ff, 0.62, bottom=fc, color=C2, label="operator field f_field", edgecolor="white", linewidth=1)
    a.bar(x, fs, 0.62, bottom=np.add(fc, ff), color=C3, label="spontaneous f_spont", edgecolor="white", linewidth=1)
    for i, P in enumerate(Ps):
        q, pv = p["periods"][f"G{P}"]["Q_spont"], p["periods"][f"G{P}"]["p_spont"]
        qg, pg = g["periods"][f"G{P}"]["Q_spont"], g["periods"][f"G{P}"]["p_spont"]
        a.text(i, 1.03, f"{q:.1f}{'*' if pv < 0.05 else ''}\n{qg:.1f}{'*' if pg < 0.05 else ''}", ha="center", va="bottom",
               fontsize=6.3, color=INK)
    a.set_xticks(x, [f"#{P}" + ("\nfield" if P in L.FIELDED else "") for P in Ps])
    a.set_ylim(0, 1.32); a.set_yticks([0, 0.5, 1]); a.set_ylabel("share of room separation S")
    a.text(-0.6, 1.24, "Q_spont bge / gte (* p<0.05)", fontsize=6.3, color=MUT)
    a.legend(loc="lower left", bbox_to_anchor=(0, -0.42), ncol=3, frameon=False, fontsize=6.3)
    a.set_title("(a) decomposition of #best–#rest separation (bge)", fontsize=7.5, loc="left")
    # movers
    rows = []
    for bnd, mv in p["movers"].items():
        for k, m in mv["movers"].items():
            rows.append((f"{NAMES[k]}\n{bnd}", m, g["movers"][bnd]["movers"][k]))
    y = np.arange(len(rows))[::-1]
    b.axvspan(-1.5, 1.5, color="#f0efec", zorder=0)
    b.axvline(1, color=C3, lw=1, ls=":"); b.axvline(-1, color=C1, lw=1, ls=":")
    for yi, (lab, m, mg) in zip(y, rows):
        pre, post = np.clip(m["phi_pre"], -4, 4), np.clip(m["phi_post"], -4, 4)
        ok = m["C_post_p"] < 0.05
        b.annotate("", xy=(post, yi), xytext=(pre, yi), arrowprops=dict(arrowstyle="->", color=INK if ok else GR, lw=1.2))
        b.plot([pre], [yi], "o", ms=4, color=MUT, zorder=3)
        b.plot([np.clip(m.get("phi_comp", np.nan), -4, 4)], [yi], "D", ms=4, mfc="white", mec=C2, zorder=3)
        b.plot([np.clip(mg["phi_post"], -4, 4)], [yi - 0.22], "s", ms=3, color=C3 if mg["C_post_p"] < 0.05 else GR)
    b.set_yticks(y, [r[0] for r in rows], fontsize=6.3)
    b.set_xlim(-4.3, 4.3); b.set_xlabel("mover index φ (−1 old room, +1 new room)", fontsize=6.5)
    b.set_title("(b) moved agents: before → after", fontsize=7.5, loc="left")
    fig.tight_layout()
    fig.savefig(FIG / "summary_obs.pdf"); plt.close(fig)


def synth():
    S = json.loads((L.DATA / "synthetic/synthetic_summary.json").read_text())["worlds"]
    fig, (a, b) = plt.subplots(1, 2, figsize=(7.0, 2.1))
    worlds = [("comp_rho1.0", "comp."), ("field_rho1.0", "field"), ("spont_rho1.0", "spont."),
              ("carry_rho1.0", "carry"), ("mixed_rho1.0", "mixed")]
    x = np.arange(len(worlds))
    for j, (k, c, lab) in enumerate([("f_comp_med", C1, "f_comp"), ("f_field_fielded_med", C2, "f_field (#38, #44)"),
                                     ("f_spont_med", C3, "f_spont")]):
        a.bar(x + (j - 1) * 0.25, [S[w][k] if S[w][k] is not None and not np.isnan(S[w][k]) else 0 for w, _ in worlds],
              0.23, color=c, label=lab)
    a.set_xticks(x, [w[1] for w in worlds], fontsize=6.3); a.set_ylim(0, 1.05); a.set_ylabel("recovered share (median)")
    a.legend(frameon=False, fontsize=6, ncol=3, loc="upper center", bbox_to_anchor=(0.5, 1.2))
    a.set_title("(a) shares recovered, ρ = 1", fontsize=7.5, loc="left", pad=14)
    rhos = [0.1, 0.3, 1.0]
    for w, c, lab in [("spont", C3, "room-held movers"), ("carry", C1, "carried movers"), ("comp", C2, "composition")]:
        b.plot(rhos, [S[f"{w}_rho{r}"]["P5_rule_rate"] for r in rhos], "-o", color=c, ms=4, lw=2, label=lab)
    b.axhline(0.8, color=GR, ls="--", lw=1)
    b.set_xscale("log"); b.set_xticks(rhos, ["0.1", "0.3", "1"]); b.set_ylim(-0.03, 1.03)
    b.set_xlabel("room effect ρ = |b_best − b_rest|² / E|a_i − a_j|²"); b.set_ylabel("P5 rule pass rate")
    b.legend(frameon=False, fontsize=6); b.set_title("(b) mover test power (5 real moves)", fontsize=7.5, loc="left")
    fig.tight_layout(); fig.savefig(FIG / "summary_synthetic.pdf"); plt.close(fig)


if __name__ == "__main__":
    FIG.mkdir(exist_ok=True)
    obs(); synth()
    print("figures written")
