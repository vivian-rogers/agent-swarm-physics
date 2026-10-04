"""H32 figures (matplotlib, PDF). Palette: the dataviz reference categorical order (blue, orange, aqua) for up to three
series, recessive gray for nulls and axes; text in ink colors, never series colors.

  synthetic   figures/synthetic_validation.pdf
  periods     goalperiod-subhypotheses/G<NN>/figures/currents.pdf
  summary     figures/summary_obs.pdf (summary page) and figures/summary.pdf (one-page figure summary)

Usage: uv run python hypotheses/H32-information-current-leaders/analysis/figures.py [synthetic|periods|summary|all]
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

HERE = Path(__file__).resolve().parent
HYP = HERE.parent
ROOT = HYP.parents[1]
DATA = ROOT / "data/processed/H32-information-current-leaders"
FIG = HYP / "figures"
S1, S2, S3, S4 = "#2a78d6", "#eb6834", "#1baf7a", "#eda100"
INK, INK2, MUTED, GRID = "#0b0b0b", "#52514e", "#85847e", "#c9c7c0"
plt.rcParams.update({"font.size": 7.5, "axes.edgecolor": GRID, "axes.labelcolor": INK2, "xtick.color": INK2,
                     "ytick.color": INK2, "axes.spines.top": False, "axes.spines.right": False, "axes.titlesize": 8,
                     "axes.titlecolor": INK, "legend.frameon": False, "pdf.fonttype": 42})
SKCOL = {"26": S1, "13": S2, "44": S3}
SKLAB = {"26": "#26: 1 room, 10 agents", "13": "#13: 1 room, 6 agents", "44": "#44: 2 rooms, 16 agents"}


def fig_synthetic():
    d = json.loads((DATA / "synthetic" / "synthetic_summary.json").read_text())["summary"]
    fig, axs = plt.subplots(1, 3, figsize=(7.2, 2.3))
    ax = axs[0]
    xs = {"S0": 0, "S1a": 0.5, "S1b": 2, "S1c": 5}
    for g in ("26", "13", "44"):
        y = [d[f"G{g}_{s}"]["top1_L_out"] for s in xs]
        ax.plot(list(xs.values()), y, "-o", color=SKCOL[g], lw=2, ms=4, label=SKLAB[g])
    ax.set_xlabel("leader share of followers' variance ψ (%)"); ax.set_ylabel("leader ranked top by Out")
    ax.set_ylim(-0.03, 1.05); ax.set_title("(a) leader recovery", loc="left")
    ax.legend(fontsize=6, loc="lower right", bbox_to_anchor=(1.0, 0.02), handlelength=1.2)
    ax.grid(axis="y", color=GRID, lw=0.4)
    ax = axs[1]
    scen = [("S0", "null"), ("S1b", "leader ψ=2%"), ("S2", "fast responder"), ("S3", "leader+fast"), ("S4", "distributed")]
    w = 0.26
    for k, g in enumerate(("26", "13", "44")):
        ident = [d[f"G{g}_{s}"].get("ident_v1", np.nan) for s, _ in scen]
        ax.bar(np.arange(len(scen)) + (k - 1) * w, ident, w * 0.9, color=SKCOL[g])
    ax.set_xticks(range(len(scen))); ax.set_xticklabels([l for _, l in scen], rotation=30, ha="right")
    ax.set_ylabel("a leader is called (standout p < 0.05)"); ax.set_ylim(0, 1.05)
    ax.axhline(0.05, color=MUTED, lw=0.8, ls=":"); ax.set_title("(b) leader calls by scenario", loc="left")
    ax.grid(axis="y", color=GRID, lw=0.4)
    ax = axs[2]
    for k, g in enumerate(("26", "13", "44")):
        ph = [d[f"G{g}_{s}"].get("phi_nullvar_median", np.nan) for s, _ in scen[1:]]
        ax.plot(np.arange(1, len(scen)) + (k - 1) * 0.12, ph, "o", color=SKCOL[g], ms=5)
    ax.set_xticks(range(1, len(scen))); ax.set_xticklabels([l for _, l in scen[1:]], rotation=30, ha="right")
    ax.set_ylabel("centralization Φ (median)"); ax.axhline(0, color=MUTED, lw=0.8)
    ax.set_title("(c) order parameter", loc="left"); ax.grid(axis="y", color=GRID, lw=0.4)
    fig.tight_layout(pad=0.4)
    FIG.mkdir(exist_ok=True)
    fig.savefig(FIG / "synthetic_validation.pdf")
    plt.close(fig)


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "all"
    if cmd in ("synthetic", "all"):
        fig_synthetic()


# ================================================================================================ real data
MODECOL = {"C": S1, "I": S2, "F": S2, "K": S3, "M": S3}
MODELAB = {S1: "mode C (shared objective)", S2: "mode I / F (individual, free)", S3: "mode K / M (competition, teams)"}


def load_explore():
    E = json.loads((DATA / "explore.json").read_text())["periods"]
    return {int(k): v for k, v in E.items()}


def fig_periods():
    E = load_explore()
    for g, r in E.items():
        d = HYP / "goalperiod-subhypotheses" / f"G{g:02d}" / "figures"
        d.mkdir(parents=True, exist_ok=True)
        o = np.array(r["out"], float) * 100; i_ = np.array(r["in"], float) * 100
        order = np.argsort(-np.nan_to_num(o, nan=-9))
        names = [r["names"][k] for k in order]
        n = len(order)
        fig, ax = plt.subplots(figsize=(4.2, 0.22 * n + 0.9))
        y = np.arange(n)
        ax.barh(y - 0.2, o[order], 0.38, color=S1, label="Out (outflow)")
        ax.barh(y + 0.2, i_[order], 0.38, color=S2, label="In (inflow)")
        if r.get("human") and r["human"].get("out") is not None and np.isfinite(r["human"]["out"]):
            ax.axvline(r["human"]["out"] * 100, color=MUTED, lw=1, ls="--")
            ax.text(r["human"]["out"] * 100, -0.9, " humans", color=INK2, fontsize=6, va="center")
        ax.axvline(0, color=GRID, lw=0.8)
        ax.set_yticks(y); ax.set_yticklabels(names, fontsize=6); ax.invert_yaxis()
        ax.set_xlabel("ΔG, % of held-out residual variance (mean over partners)")
        ax.set_title(f"G{g:02d}: T = {r['T'] * 100:+.3f}% (p = {r['p_T']:.3f}); standout p = {r['p_standout']:.3f}", loc="left",
                     fontsize=7)
        ax.legend(fontsize=6, loc="lower right")
        fig.tight_layout(pad=0.3)
        fig.savefig(d / "currents.pdf")
        plt.close(fig)


def gt_rows(E, seg):
    """Ground-truth placements: (label, rank, n, kind) with rank 1 = top source."""
    rows = []
    for g, r in sorted(E.items()):
        h = r.get("human")
        if h and h.get("n_msgs", 0) >= 15 and h.get("rank_out") is not None:
            rows.append((f"humans #{g}", h["rank_out"], len(r["nodes"]) + 1, "human"))
    if seg:
        post = seg["G26_post"]
        srt = sorted(post, key=lambda a: -np.nan_to_num(post[a]["dG"], nan=-9))
        rows.append(("DeepSeek #26 post-election", srt.index("17") + 1, len(srt), "leader"))
        b = seg["G44_best_0528_29"]
        srt = sorted(b, key=lambda a: -np.nan_to_num(b[a]["dG"], nan=-9))
        rows.append(("operator #44 #best", srt.index("100") + 1, len(srt), "leader"))
        ag = [a for a in srt if a != "100"]
        rows.append(("temp. leader #44 (expect low)", ag.index("28") + 1, len(ag), "installed"))
    return rows


def panel_T(ax, E, legend_loc="lower left"):
    gs = sorted(E)
    for k, g in enumerate(gs):
        r = E[g]; c = MODECOL.get(r["meta"]["mode"], MUTED)
        both = r["p_T"] < 0.05 and r.get("withinday", {}).get("p_T", 1) < 0.05
        one = r["p_T"] < 0.05
        ax.plot([k, k], [r["T_null_q"][0] * 100, r["T_null_q"][2] * 100], color=GRID, lw=2.5, solid_capstyle="butt")
        if both:
            ax.plot(k, r["T"] * 100, "o", ms=5, color=c)
        elif one:
            ax.plot(k, r["T"] * 100, "o", ms=5, mfc="white", mec=c, mew=1.4)
        else:
            ax.plot(k, r["T"] * 100, "o", ms=3, mfc="white", mec=MUTED, mew=0.8)
    ax.axhline(0, color=MUTED, lw=0.6)
    ax.set_xticks(range(len(gs))); ax.set_xticklabels([f"{g}" for g in gs], fontsize=5.5, rotation=90)
    ax.set_xlabel("goal period"); ax.set_ylabel("total transfer T (%)")
    for c, l in MODELAB.items():
        ax.plot([], [], "o", color=c, ms=4, label=l)
    ax.plot([], [], "o", color=INK2, ms=4, label="p < 0.05, both nulls")
    ax.plot([], [], "o", mfc="white", mec=INK2, ms=4, label="cross-day null only")
    ax.plot([], [], "o", mfc="white", mec=MUTED, ms=3, label="neither")
    ax.plot([], [], color=GRID, lw=2.5, label="cross-day null 5–95%")
    ax.legend(fontsize=5, loc=legend_loc, ncol=2 if legend_loc == "lower left" else 3, handletextpad=0.3, columnspacing=0.8)


def panel_gt(ax, E, seg):
    rows = gt_rows(E, seg)
    for k, (lab, rk, n, kind) in enumerate(rows):
        x = (rk - 1) / max(n - 1, 1)
        c = {"human": S1, "leader": S2, "installed": S3}[kind]
        ax.plot([0, 1], [k, k], color=GRID, lw=0.6)
        ax.plot(x, k, "o", color=c, ms=5)
        ax.text(1.03, k, f"{rk}/{n}", va="center", fontsize=5.5, color=INK2)
    ax.set_yticks(range(len(rows))); ax.set_yticklabels([r[0] for r in rows], fontsize=5.5); ax.invert_yaxis()
    ax.set_xlim(-0.05, 1.15); ax.set_xticks([0, 0.5, 1]); ax.set_xticklabels(["top", "middle", "bottom"])
    ax.axvline(0.5, color=MUTED, lw=0.6, ls=":")
    ax.set_xlabel("rank by outflow (known sources)")


def fig_summary_obs():
    E = load_explore()
    seg = json.loads((DATA / "segments.json").read_text()) if (DATA / "segments.json").exists() else {}
    fig, axs = plt.subplots(1, 2, figsize=(7.0, 2.5), gridspec_kw={"width_ratios": [1.6, 1]})
    panel_T(axs[0], E); axs[0].set_title("(a) content transfer per goal period", loc="left")
    panel_gt(axs[1], E, seg); axs[1].set_title("(b) known sources", loc="left")
    fig.tight_layout(pad=0.4)
    fig.savefig(FIG / "summary_obs.pdf"); plt.close(fig)


def fig_summary():
    E = load_explore()
    seg = json.loads((DATA / "segments.json").read_text()) if (DATA / "segments.json").exists() else {}
    ne = json.loads((DATA / "ne42.json").read_text()) if (DATA / "ne42.json").exists() else {}
    d = json.loads((DATA / "synthetic" / "synthetic_summary.json").read_text())["summary"]
    fig = plt.figure(figsize=(7.4, 10.4))
    gsp = fig.add_gridspec(4, 2, hspace=0.6, wspace=0.5, height_ratios=[1, 1, 1.55, 1])
    # (a) synthetic recovery
    ax = fig.add_subplot(gsp[0, 0])
    xs = {"S0": 0, "S1a": 0.5, "S1b": 2, "S1c": 5}
    for g in ("26", "13", "44"):
        ax.plot(list(xs.values()), [d[f"G{g}_{s}"]["top1_L_out"] for s in xs], "-o", color=SKCOL[g], lw=2, ms=4, label=SKLAB[g])
    ax.set_xlabel("leader share of followers' variance ψ (%)"); ax.set_ylabel("leader ranked top")
    ax.set_title("(a) synthetic: leader recovery", loc="left"); ax.legend(fontsize=5.5, loc="lower right"); ax.set_ylim(-0.03, 1.05)
    # (b) synthetic calls by scenario
    ax = fig.add_subplot(gsp[0, 1])
    scen = [("S0", "null"), ("S1b", "leader"), ("S2", "fast resp."), ("S3", "leader+fast"), ("S4", "distributed")]
    for k, g in enumerate(("26", "13", "44")):
        ax.bar(np.arange(len(scen)) + (k - 1) * 0.26, [d[f"G{g}_{s}"]["ident_v1"] for s, _ in scen], 0.24, color=SKCOL[g])
    ax.set_xticks(range(len(scen))); ax.set_xticklabels([l for _, l in scen], rotation=25, ha="right", fontsize=6)
    ax.set_ylabel("a leader is called"); ax.set_ylim(0, 1.05); ax.axhline(0.05, color=MUTED, lw=0.6, ls=":")
    ax.set_title("(b) synthetic: leader calls", loc="left")
    # (c) T per period
    ax = fig.add_subplot(gsp[1, :]); panel_T(ax, E, "lower center"); ax.set_title("(c) real: total content transfer T per goal period", loc="left")
    # (d) known sources
    ax = fig.add_subplot(gsp[2, 0]); panel_gt(ax, E, seg); ax.set_title("(d) real: known sources", loc="left")
    # (e) Phi vs T
    ax = fig.add_subplot(gsp[2, 1])
    for g, r in E.items():
        if r["p_T"] < 0.05 and np.isfinite(r["cent_nullvar"]["phi"]):
            c = MODECOL.get(r["meta"]["mode"], MUTED)
            ax.plot(r["T"] * 100, r["cent_nullvar"]["phi"], "o", color=c, ms=4.5,
                    mfc=c if r["p_standout"] < 0.05 else "white")
            ax.text(r["T"] * 100, r["cent_nullvar"]["phi"], f" {g}", fontsize=5, color=INK2, va="center")
    ax.axhline(0, color=MUTED, lw=0.6)
    ax.set_xlabel("total transfer T (%)"); ax.set_ylabel("centralization Φ")
    ax.set_title("(e) real: phase plane (filled: leader called;\nΦ > 1 when some agents have negative outflow)", loc="left", fontsize=6.5)
    # (f) split-half
    ax = fig.add_subplot(gsp[3, 0])
    sh = [(g, r["split_half"]["rho_out"]) for g, r in sorted(E.items()) if r.get("split_half") and r["split_half"].get("rho_out") is not None]
    ax.bar(range(len(sh)), [x for _, x in sh], color=[MODECOL.get(E[g]["meta"]["mode"], MUTED) for g, _ in sh], width=0.7)
    ax.set_xticks(range(len(sh))); ax.set_xticklabels([str(g) for g, _ in sh], fontsize=5.5, rotation=90)
    ax.axhline(0, color=MUTED, lw=0.6); ax.set_ylabel("split-half ρ(Out)"); ax.set_xlabel("goal period")
    ax.set_title("(f) real: stability of the outflow ranking", loc="left")
    # (g) exposure contrast + NE42
    ax = fig.add_subplot(gsp[3, 1])
    labs, vals, cis = [], [], []
    for g, r in sorted(E.items()):
        if "pairs_same_room" in r and r["pairs_same_room"].get("mean") is not None and r["pairs_cross_room_unseen"].get("mean") is not None:
            for key, lab in (("pairs_same_room", "same"), ("pairs_cross_room_unseen", "cross")):
                labs.append(f"{g} {lab}"); vals.append(r[key]["mean"] * 100); cis.append(np.array(r[key]["ci90"]) * 100)
    y = np.arange(len(labs))
    for k in range(len(labs)):
        c = S1 if labs[k].endswith("same") else S2
        ax.plot(cis[k], [k, k], color=c, lw=1.2); ax.plot(vals[k], k, "o", color=c, ms=3.5)
    ax.axvline(0, color=MUTED, lw=0.6)
    ax.set_yticks(y); ax.set_yticklabels(labs, fontsize=5); ax.invert_yaxis()
    ax.set_xlabel("pair ΔG (%), 90% CI")
    t = "(g) real: same-room (seen) vs cross-room (unseen) pairs"
    if ne.get("split_pairs", {}).get("n"):
        t += f"\nNE42 split pairs: #40 − #39/41 = {ne['split_pairs']['mean_diff'] * 100:+.3f}% (sign p = {ne['split_pairs']['p_sign']:.2f})"
    ax.set_title(t, loc="left", fontsize=6.5)
    fig.savefig(FIG / "summary.pdf", bbox_inches="tight"); plt.close(fig)


if __name__ == "__main__" and len(sys.argv) > 1 and sys.argv[1] in ("periods", "summary", "all"):
    if sys.argv[1] in ("periods", "all"):
        fig_periods()
    if sys.argv[1] in ("summary", "all"):
        fig_summary_obs(); fig_summary()
