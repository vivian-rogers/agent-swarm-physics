"""H47 figures from data/processed/H47-room-coherence-length/results/*.json.

  figures/coherence_by_period.pdf   (a) rho_w vs rho_c per period; (b) C_B per period by instruction type;
                                    (c) C_B vs between-room separation; (d) tier ratio G (two-room periods and #51 units)
  figures/summary_obs.pdf           summary page 1: C_B per period + NE42 A-B-A r_X
  figures/summary_obs2.pdf          summary page 2: leadership response curves (#38, #41) + detector scores
  figures/leadership.pdf            response curves y(tau) per cohort for the 8 goal changes
  figures/detector.pdf              room-event scores vs multi-room placebo days
  goalperiod-subhypotheses/<P>/figures/<P>_h47.pdf   per-period panel
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h47lib as L  # noqa: E402

import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

RES = L.OUT / "results"
COL = {"identical": "#c05621", "room-specific": "#2b6cb0", "forks": "#2c7a7b", "self-made room": "#718096"}
plt.rcParams.update({"font.size": 8, "axes.spines.top": False, "axes.spines.right": False})


def J(n):
    return json.loads((RES / f"{n}.json").read_text())


def fig_coherence(S):
    P = S["periods"]; gs = list(P)
    fig, ax = plt.subplots(1, 4, figsize=(13, 3.0))
    x = np.arange(len(gs))
    ax[0].bar(x - 0.2, [P[g]["rho_w"] for g in gs], 0.4, label="same room ρ_w", color="#2b6cb0")
    ax[0].bar(x + 0.2, [P[g]["rho_c"] for g in gs], 0.4, label="different rooms ρ_c", color="#a0aec0")
    ax[0].set_xticks(x); ax[0].set_xticklabels(gs, rotation=45); ax[0].legend(frameon=False); ax[0].set_title("(a) per-pair content correlation (w30)")
    for i, g in enumerate(gs):
        c = COL[P[g]["instr"]]
        ax[1].scatter(i, P[g]["C_B"], color=c, s=30, zorder=3)
        if P[g]["C_B_ci"]:
            ax[1].plot([i, i], P[g]["C_B_ci"], color=c, lw=1)
    ax[1].axhline(0.3, ls="--", c="gray", lw=0.8); ax[1].axhline(0, c="k", lw=0.5)
    ax[1].set_xticks(x); ax[1].set_xticklabels(gs, rotation=45); ax[1].set_ylim(-0.5, 1.4)
    ax[1].set_title("(b) room contrast C_B = ρ_c/ρ_w")
    for k, c in COL.items():
        ax[1].scatter([], [], color=c, label=k)
    ax[1].legend(frameon=False, fontsize=6.5, loc="upper left")
    for g in gs:
        if P[g]["sep_median_F"] is not None:
            ax[2].scatter(P[g]["sep_median_F"], P[g]["C_B"], color=COL[P[g]["instr"]], s=30)
            ax[2].annotate(g, (P[g]["sep_median_F"], P[g]["C_B"]), fontsize=6.5, xytext=(3, 2), textcoords="offset points")
    ph = S["posthoc_separation"]
    ax[2].set_xlabel("between-room separation F (median over days)"); ax[2].set_ylabel("C_B")
    ax[2].set_title(f"(c) post hoc: Spearman {ph['spearman']:.2f} (p {ph['p_perm_two_sided']:.3f})")
    ax[3].bar(x, [P[g]["G"] for g in gs], color="#4a5568")
    g51 = S["g51"]["G_single"]
    ax[3].scatter(np.full(len(g51), len(gs) + 0.5), list(g51.values()), color="#718096", s=12)
    ax[3].set_xticks(list(x) + [len(gs) + 0.5]); ax[3].set_xticklabels(gs + ["#51 1-room"], rotation=45)
    ax[3].axhline(0.6, ls="--", c="gray", lw=0.8); ax[3].axhline(1, c="k", lw=0.5)
    ax[3].set_title("(d) tier ratio G = ρ_low-mention/ρ_high-mention")
    fig.tight_layout(); fig.savefig(L.FIG / "coherence_by_period.pdf"); fig.savefig(L.FIG / "coherence_by_period.png", dpi=120)
    plt.close(fig)


def fig_summary(S, lead, det):
    P = S["periods"]; gs = list(P)
    fig, ax = plt.subplots(1, 2, figsize=(3.45, 1.68), gridspec_kw=dict(width_ratios=[1.75, 1]))
    x = np.arange(len(gs))
    for i, g in enumerate(gs):
        c = COL[P[g]["instr"]]
        ax[0].scatter(i, P[g]["C_B"], color=c, s=18, zorder=3)
        if P[g]["C_B_ci"]:
            ax[0].plot([i, i], P[g]["C_B_ci"], color=c, lw=0.8)
    ax[0].axhline(0.3, ls="--", c="gray", lw=0.6); ax[0].axhline(0, c="k", lw=0.4)
    ax[0].set_xticks(x); ax[0].set_xticklabels([g[1:] for g in gs], fontsize=6); ax[0].set_ylim(-0.5, 2.0)
    ax[0].set_ylabel("C_B = ρ_cross/ρ_within", fontsize=6.5); ax[0].set_xlabel("goal period", fontsize=6.5)
    for k, c in COL.items():
        ax[0].scatter([], [], color=c, label=k, s=10)
    ax[0].legend(frameon=False, fontsize=5, loc="upper left", ncol=2, handletextpad=0.1, columnspacing=0.5, borderaxespad=0.1)
    ne = S["ne42"]["r_X"]
    ax[1].plot([0, 1, 2], [ne["39"], ne["40"], ne["41"]], "o-", color="#2b6cb0", ms=4)
    ax[1].axhline(1, c="gray", lw=0.6, ls=":")
    ax[1].set_xticks([0, 1, 2]); ax[1].set_xticklabels(["#39\napart", "#40\nmerged", "#41\napart"], fontsize=5.5)
    ax[1].set_ylabel("r_X (cross / within old rooms)", fontsize=6); ax[1].set_ylim(0, 1.6); ax[1].set_xlim(-0.3, 2.3)
    ax[1].set_title(f"NE42: DiD {S['ne42']['DiD']:.2f}, p {S['ne42']['p_DiD']:.3f}", fontsize=5.5)
    for a in ax:
        a.tick_params(labelsize=6)
    fig.tight_layout(pad=0.3); fig.savefig(L.FIG / "summary_obs.pdf"); fig.savefig(L.FIG / "summary_obs.png", dpi=150)
    plt.close(fig)
    # page 2: leadership curves for two events + detector strip
    fig, ax = plt.subplots(1, 3, figsize=(3.45, 1.75))
    for a, k in zip(ax[:2], ("#38", "#41")):
        yb = np.array(lead[k]["yb"], float); tt = (np.arange(yb.shape[1]) + 0.5) * 15
        a.plot(tt, yb[0], "o-", ms=2.5, color="#2b6cb0", label="#best"); a.plot(tt, yb[1], "s-", ms=2.5, color="#c05621", label="#rest")
        a.set_ylim(-0.3, 1.4); a.axhline(1, c="gray", lw=0.5, ls=":"); a.axhline(0, c="gray", lw=0.5)
        a.set_title(f"{k} L {lead[k]['L']:.2f} (p {lead[k]['p_L']:.2f})", fontsize=5.5); a.set_xlabel("min after kickoff", fontsize=5.5)
        a.tick_params(labelsize=6)
    ax[0].set_ylabel("shift fraction y", fontsize=6); ax[0].legend(frameon=False, fontsize=5, loc="center right")
    dd = pl.read_parquet(RES / "detector_days.parquet")
    pl_ = dd.filter(pl.col("placebo_mr"))
    for j, (s, lab) in enumerate((("R1", "swarm"), ("R1_room", "per-room"), ("R1_loc", "localized"))):
        v = pl_[s].fill_null(np.nan).to_numpy().astype(float)
        ax[2].scatter(np.full(v.size, j) + np.random.default_rng(j).uniform(-0.15, 0.15, v.size), v, s=4, color="#a0aec0")
        for e in det["events"]:
            val = e.get(f"{s}_d0")
            if val is not None and np.isfinite(val):
                ax[2].scatter(j, min(val, 12), marker="*" if not e["goal_confounded"] else "D", s=18 if not e["goal_confounded"] else 9,
                              color="#c53030" if not e["goal_confounded"] else "#2b6cb0", zorder=3)
    ax[2].set_xticks([0, 1, 2]); ax[2].set_xticklabels(["sw.", "room", "loc."], fontsize=5.5)
    ax[2].axhline(3, ls="--", c="gray", lw=0.5); ax[2].set_ylim(-3, 12.5); ax[2].tick_params(labelsize=5.5)
    ax[2].set_title("room events (z)", fontsize=5.5)
    fig.tight_layout(pad=0.3); fig.savefig(L.FIG / "summary_obs2.pdf"); fig.savefig(L.FIG / "summary_obs2.png", dpi=150)
    plt.close(fig)


def fig_leadership(lead):
    ks = [k for k in lead if k.startswith("#")]
    fig, ax = plt.subplots(2, 4, figsize=(11, 4.2), sharey=True)
    for a, k in zip(ax.ravel(), ks):
        yb = np.array(lead[k]["yb"], float); nb = np.array(lead[k]["nb"]); tt = (np.arange(yb.shape[1]) + 0.5) * 15
        a.plot(tt, yb[0], "o-", ms=3, color="#2b6cb0", label=f"#best (n {lead[k]['n_best']})")
        a.plot(tt, yb[1], "s-", ms=3, color="#c05621", label=f"#rest (n {lead[k]['n_rest']})")
        a.axhline(1, c="gray", lw=0.5, ls=":"); a.axhline(0, c="gray", lw=0.5)
        a.set_title(f"{k} ({lead[k]['cohorts']}): L {lead[k]['L']:.2f}, p {lead[k]['p_L']:.2f}", fontsize=7)
        a.legend(frameon=False, fontsize=6); a.set_xlabel("minutes after the room's kickoff")
    ax[0, 0].set_ylabel("shift fraction y"); ax[1, 0].set_ylabel("shift fraction y")
    fig.tight_layout(); fig.savefig(L.FIG / "leadership.pdf"); plt.close(fig)


def fig_detector(det):
    dd = pl.read_parquet(RES / "detector_days.parquet").filter(pl.col("pt_date") >= "2026-03-16")
    fig, ax = plt.subplots(3, 1, figsize=(11, 5.5), sharex=True)
    xs = np.arange(dd.height)
    lab = dd["pt_date"].to_list()
    for a, s in zip(ax, ("R1", "R1_room", "R1_loc")):
        v = dd[s].fill_null(np.nan).to_numpy().astype(float)
        a.plot(xs, np.clip(v, -5, 15), ".-", lw=0.6, ms=3, color="#4a5568")
        pm = dd["placebo_mr"].to_numpy()
        a.scatter(xs[pm], np.clip(v[pm], -5, 15), s=10, color="#a0aec0", zorder=3, label="multi-room placebo")
        for e in det["events"]:
            if e["day0"] in lab:
                i = lab.index(e["day0"])
                a.axvline(i, color="#c53030" if not e["goal_confounded"] else "#2b6cb0", lw=0.8, alpha=0.6)
        a.axhline(3, ls="--", c="gray", lw=0.6); a.set_ylabel(s)
    ax[0].legend(frameon=False)
    step = max(1, len(lab) // 25)
    ax[2].set_xticks(xs[::step]); ax[2].set_xticklabels(lab[::step], rotation=60, fontsize=6)
    fig.suptitle("Room events (red: clean, blue: goal-confounded) and day scores (capped at 15)")
    fig.tight_layout(); fig.savefig(L.FIG / "detector.pdf"); plt.close(fig)


def fig_periods(S, coh, sep, lead):
    GP = L.HYP / "goalperiod-subhypotheses"
    kick = {"G36": "#36", "G37": "#37", "G38": "#38", "G39": "#39", "G41": "#41", "G42": "#42", "G44": "#44"}
    for g, r in coh.items():
        fig, ax = plt.subplots(1, 3, figsize=(9, 2.6))
        pu = r["per_unit"]
        us = list(pu)
        ax[0].bar(np.arange(len(us)) - 0.2, [pu[u]["obs"]["rho_w"] if pu[u] else np.nan for u in us], 0.4, color="#2b6cb0", label="ρ_w")
        ax[0].bar(np.arange(len(us)) + 0.2, [pu[u]["obs"]["rho_c"] if pu[u] else np.nan for u in us], 0.4, color="#a0aec0", label="ρ_c")
        ax[0].set_xticks(range(len(us))); ax[0].set_xticklabels(us); ax[0].legend(frameon=False)
        ax[0].set_title(f"{g}: C_B {r['w30']['obs']['C_B']:.2f} (p {r['w30'].get('p_DB', np.nan):.3f})")
        if g in sep:
            dys = sep[g]["days"]
            ax[1].plot(range(len(dys)), [d["F"] for d in dys], "o-", color="#2c7a7b")
            ax[1].set_xticks(range(len(dys))); ax[1].set_xticklabels([d["day"][5:] for d in dys], rotation=60, fontsize=6)
            ax[1].set_title("between-room separation F per day")
        else:
            ax[1].axis("off")
        k = kick.get(g)
        if k and k in lead:
            yb = np.array(lead[k]["yb"], float); tt = (np.arange(yb.shape[1]) + 0.5) * 15
            ax[2].plot(tt, yb[0], "o-", color="#2b6cb0", label="#best"); ax[2].plot(tt, yb[1], "s-", color="#c05621", label="#rest")
            ax[2].set_title(f"kickoff {k}: L {lead[k]['L']:.2f} (p {lead[k]['p_L']:.2f})"); ax[2].legend(frameon=False)
            ax[2].set_xlabel("min after kickoff")
        else:
            ax[2].axis("off")
        fig.tight_layout()
        (GP / g / "figures").mkdir(parents=True, exist_ok=True)
        fig.savefig(GP / g / "figures" / f"{g}_h47.pdf"); plt.close(fig)
    # NE42 panel
    ne = S["ne42"]
    fig, ax = plt.subplots(1, 2, figsize=(6.5, 2.6))
    ax[0].plot([0, 1, 2], [ne["r_X"]["39"], ne["r_X"]["40"], ne["r_X"]["41"]], "o-")
    ax[0].axhline(1, ls=":", c="gray"); ax[0].set_xticks([0, 1, 2]); ax[0].set_xticklabels(["#39", "#40 merged", "#41"])
    ax[0].set_title(f"r_X: DiD {ne['DiD']:.2f} [{ne['DiD_ci'][0]:.2f}, {ne['DiD_ci'][1]:.2f}], p {ne['p_DiD']:.3f}")
    k = "#40"
    yb = np.array(lead[k]["yb"], float); tt = (np.arange(yb.shape[1]) + 0.5) * 15
    ax[1].plot(tt, yb[0], "o-", label="ex-#best"); ax[1].plot(tt, yb[1], "s-", label="ex-#rest"); ax[1].legend(frameon=False)
    ax[1].set_title(f"#40 kickoff (merge): L {lead[k]['L']:.2f}, p {lead[k]['p_L']:.2f}")
    fig.tight_layout(); (GP / "NE42" / "figures").mkdir(parents=True, exist_ok=True)
    fig.savefig(GP / "NE42" / "figures" / "NE42_h47.pdf"); plt.close(fig)


def main():
    S = J("summary"); lead = J("leadership"); det = J("detector"); coh = J("coherence"); sep = J("separation")
    L.FIG.mkdir(parents=True, exist_ok=True)
    fig_coherence(S); fig_summary(S, lead, det); fig_leadership(lead); fig_detector(det); fig_periods(S, coh, sep, lead)
    print("figures written")


if __name__ == "__main__":
    main()
