"""H37 figures: summary observable (summary page), one-page figure summary, per-period figures. Reads results JSON only.

Usage: uv run python hypotheses/H37-stance-spins/analysis/figures.py
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

os.environ.setdefault("OMP_NUM_THREADS", "2")
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = Path(__file__).resolve().parent
H37 = HERE.parent
DATA = H37.parents[1] / "data/processed/H37-stance-spins"
FIG = H37 / "figures"
GP = H37 / "goalperiod-subhypotheses"
STANCE, TOPIC, GRAY, INK, MUTED = "#2a78d6", "#eb6834", "#9a9893", "#0b0b0b", "#52514e"

plt.rcParams.update({"font.size": 8, "axes.spines.top": False, "axes.spines.right": False, "axes.edgecolor": MUTED,
                     "axes.labelcolor": INK, "xtick.color": MUTED, "ytick.color": MUTED, "axes.titlesize": 8.5,
                     "axes.titleweight": "bold", "legend.frameon": False, "font.family": "DejaVu Sans"})


def load(p):
    return json.loads((DATA / p).read_text())


def panel_auc_by_phase(ax, R12):
    phases = [("pre", "before\nspeeches"), ("deb", "during\ndebate"), ("post", "after\nverdict")]
    x = np.arange(3)
    s = [R12["primary"][p]["auc_stance"] for p, _ in phases]
    t = [R12["primary"][p]["auc_topic"] for p, _ in phases]
    ax.axhline(0.5, color=GRAY, lw=1, ls="--")
    ax.text(1.5, 0.505, "chance", color=MUTED, fontsize=6.5, ha="center", va="bottom")
    ax.plot(x - 0.06, s, "o-", color=STANCE, lw=2, ms=7, mec="white", mew=1.5, label="stance (Jev)")
    ax.plot(x + 0.06, t, "s-", color=TOPIC, lw=2, ms=7, mec="white", mew=1.5, label="topic (embedding cosine)")
    ax.set_xticks(x, [l for _, l in phases])
    ax.set_ylim(0.4, 0.8)
    ax.set_ylabel("AUC: same vs opposite team\n(agent effects removed)")
    ax.text(1 + 0.1, s[1] - 0.005, f"{s[1]:.2f}", color=INK, fontsize=7, ha="left", va="top")
    ax.text(1 + 0.12, t[1] - 0.035, f"{t[1]:.2f}", color=INK, fontsize=7, ha="left")
    ax.legend(loc="upper left", fontsize=6.5)
    ax.set_title("(a) #12 debates: team signal", loc="left")


def panel_classes(ax, R51):
    cls = [("SR", "same-role\nrivals"), ("OP", "opposed\n(Prankster)"), ("SY", "support\nroles"), ("NC", "media\nniche")]
    x = np.arange(len(cls))
    for k, (mod, col, off, mk) in enumerate([("stance", STANCE, -0.12, "o"), ("topic", TOPIC, 0.12, "s")]):
        fa = R51["primary"][mod]["family_adjusted"]
        T = np.array([fa[c]["T"] for c, _ in cls]); sd = np.array([fa[c]["null_sd"] for c, _ in cls])
        ax.errorbar(x + off, np.zeros_like(T), yerr=1.96 * sd, fmt="none", ecolor=GRAY, elinewidth=5, alpha=0.35, capsize=0)
        ax.plot(x + off, T, mk, color=col, ms=7, mec="white", mew=1.5, label=mod, ls="none")
    ax.axhline(0, color=MUTED, lw=0.8)
    ax.set_xticks(x, [l for _, l in cls])
    ax.set_ylabel("class mean − unrelated pairs\n(same-lab adjusted)")
    n = [R51["primary"]["stance"]["family_adjusted"][c]["n"] for c, _ in cls]
    for xi, nn in zip(x, n):
        ax.text(xi, ax.get_ylim()[0] if False else -0.33, f"{nn} pairs", ha="center", fontsize=6, color=MUTED)
    ax.set_ylim(-0.36, 0.3)
    ax.legend(loc="upper right", fontsize=6.5, ncol=2)
    ax.set_title("(b) #51 role classes vs unrelated pairs", loc="left")


def summary_obs(R12, R51):
    fig, axs = plt.subplots(1, 2, figsize=(7.2, 2.5), gridspec_kw={"wspace": 0.38})
    panel_auc_by_phase(axs[0], R12)
    panel_classes(axs[1], R51)
    fig.savefig(FIG / "summary_obs.pdf", bbox_inches="tight")
    fig.savefig(FIG / "summary_obs.png", dpi=160, bbox_inches="tight")
    plt.close(fig)


def full_summary(R12, R51, R26, R40, V, SY):
    fig, axs = plt.subplots(2, 3, figsize=(10.5, 6.2), gridspec_kw={"hspace": 0.6, "wspace": 0.45})
    # (a) validation
    ax = axs[0, 0]
    M = np.array(V["reweighted"]["P_obs_given_true_rows_true_neg_neu_pos"])
    ax.imshow(M, cmap="Blues", vmin=0, vmax=1)
    for i in range(3):
        for j in range(3):
            ax.text(j, i, f"{M[i, j]:.2f}", ha="center", va="center", color="white" if M[i, j] > 0.5 else INK, fontsize=7.5)
    ax.set_xticks(range(3), ["−", "0", "+"]); ax.set_yticks(range(3), ["−", "0", "+"])
    ax.set_xlabel("Jev label"); ax.set_ylabel("Claude blind label (truth)")
    ax.set_title(f"(a) label noise: κ_sign {V['random60']['kappa_sign']:.2f} (random 60),\n{V['enriched45']['kappa_sign']:.2f} (enriched 45); Jev '−' precision {V['precision_by_jev_class']['-1']['precision']:.2f}", loc="left")
    # (b) synthetic S1
    ax = axs[0, 1]
    cells = SY["S1"]["cells"]
    D = [0.0, 0.25, 0.5, 1.0]
    for cn, ls in (("perfect", "--"), ("jev", "-")):
        ax.plot(D, [cells[f"Delta={d}|{cn}"]["power_gamma_p01"] for d in D], ls, color=STANCE, marker="o", ms=5, label=f"γ test power ({cn})")
        ax.plot(D, [cells[f"Delta={d}|{cn}"]["acc_mean"] for d in D], ls, color=TOPIC, marker="s", ms=5, label=f"team accuracy ({cn})")
    ax.axhline(0.7, color=GRAY, lw=1, ls=":"); ax.text(0.62, 0.62, "chance accuracy", fontsize=6, color=MUTED)
    ax.set_xlabel("camp coupling Δ (logit)"); ax.set_ylim(0, 1.05)
    ax.legend(fontsize=5.8, loc="lower right")
    ax.set_title("(b) synthetic #12 (real reply graph):\ndetectable from Δ ≈ 0.5 with Jev noise", loc="left")
    # (c) AUC by phase
    panel_auc_by_phase(axs[0, 2], R12)
    axs[0, 2].set_title("(c) #12: stance vs topic by phase", loc="left")
    # (d) per-debate recovery
    ax = axs[1, 0]
    per = R12["primary"]["deb"]["recovery"]["per_debate"]
    x = np.arange(len(per))
    ax.bar(x - 0.2, [p["acc_stance"] for p in per], 0.38, color=STANCE, label="stance graph")
    ax.bar(x + 0.2, [p["acc_topic"] for p in per], 0.38, color=TOPIC, label="topic graph")
    ax.axhline(per[0]["chance_mean"], color=GRAY, ls="--", lw=1)
    ax.set_xticks(x, [str(p["debate"]) for p in per]); ax.set_xlabel("debate (replies: " + ", ".join(str(p["n_replies"]) for p in per[:3]) + ", …)")
    ax.set_ylim(0.4, 1.18); ax.set_ylabel("team-recovery accuracy")
    ax.legend(fontsize=6, loc="upper left", ncol=2)
    rc = R12["primary"]["deb"]["recovery"]
    ax.set_title(f"(d) #12 factions: stance {rc['acc_stance']:.2f} (exact {rc['exact_recovery_stance']}/10),\ntopic {rc['acc_topic']:.2f}, chance {rc['chance']:.2f}", loc="left")
    # (e) #51 classes
    panel_classes(axs[1, 1], R51)
    axs[1, 1].set_title("(e) #51 role classes (stance and topic)", loc="left")
    # (f) detector across periods
    ax = axs[1, 2]
    CAL = load("calibration.json")
    rows = [("#12 all", R12["detector"], "G12"), ("#26", R26["detector"], "G26"), ("#40", R40["primary"], "G40"), ("#51", R51["detector"], "G51")]
    y = np.arange(len(rows))[::-1]
    for yy, (lab, d, gk) in zip(y, rows):
        lo, hi = d["f_neg_ci90_dayboot"]
        ax.plot([lo, hi], [yy, yy], color=STANCE, lw=3, alpha=0.5)
        ax.plot(d["f_neg"], yy, "o", color=STANCE, ms=7, mec="white", mew=1.5)
        c = CAL[gk]
        ax.text(0.33, yy, f"neg. pairs {c['n_sig_neg_obs']} (null {c['n_sig_neg_null_mean']:.1f}); camps p {c['p_faction_calibrated']:.2f}",
                va="center", fontsize=6.2, color=INK)
    # #12 opposite-team debate replies as the reference
    fo = {x["rel"]: x for x in R12["primary"]["deb"]["by_relation"]}["opposite"]["f_neg"]
    ax.axvline(fo, color=GRAY, ls="--", lw=1); ax.text(fo, len(rows) - 0.4, "#12 opponents", fontsize=6, color=MUTED, ha="center")
    M = np.array(V["reweighted"]["P_obs_given_true_rows_true_neg_neu_pos"]); ts = np.array(V["reweighted"]["true_shares"])
    floor = (M[1, 0] * ts[1] + M[2, 0] * ts[2]) / (ts[1] + ts[2])  # Jev '-' rate with no true negatives
    ax.axvline(floor, color=GRAY, ls=":", lw=1); ax.text(floor, -0.75, "label-noise floor", fontsize=6, color=MUTED, ha="center")
    ax.set_yticks(y, [r[0] for r in rows]); ax.set_xlim(0, 0.75); ax.set_ylim(-1, len(rows))
    ax.set_xlabel("share of replies labelled oppose/undermine")
    ax.set_title("(f) detector: conflict level, negative pairs\nand camps (calibrated agent-field null)", loc="left")
    fig.suptitle("H37 round 1: stance spins (Jev reply labels) as a conflict and faction detector", x=0.01, ha="left", fontsize=10, fontweight="bold")
    fig.savefig(FIG / "summary.pdf", bbox_inches="tight")
    plt.close(fig)


def per_period(R12, R51, R26, R40):
    # G12: mean stance by relation and phase
    fig, ax = plt.subplots(figsize=(4.2, 2.6))
    phases = ["pre", "deb", "post"]
    for rel, col, mk in (("same", STANCE, "o"), ("opposite", TOPIC, "s")):
        v = [{x["rel"]: x for x in R12["primary"][p]["by_relation"]}[rel]["s_mean"] for p in phases]
        ax.plot(range(3), v, mk + "-", color=col, lw=2, ms=7, mec="white", mew=1.5, label=f"{rel}-team replies")
    ax.axhline(0, color=MUTED, lw=0.8)
    ax.set_xticks(range(3), ["before speeches", "during debate", "after verdict"]); ax.set_ylabel("mean soft stance")
    ax.legend(fontsize=7); ax.set_title("#12: stance by team relation and phase", loc="left")
    fig.savefig(GP / "G12/figures/g12_stance_by_phase.pdf", bbox_inches="tight"); plt.close(fig)
    # G51
    fig, ax = plt.subplots(figsize=(4.4, 2.7))
    panel_classes(ax, R51)
    fig.savefig(GP / "G51/figures/g51_role_classes.pdf", bbox_inches="tight"); plt.close(fig)
    # G26: per-day stance toward the winner (descriptive) and Mantel numbers
    fig, ax = plt.subplots(figsize=(4.2, 2.5))
    w = R26["primary"]["stance_toward_winner_by_day"]
    ax.bar(range(len(w)), [x["s_mean"] for x in w], color=STANCE, width=0.6)
    for k, x in enumerate(w):
        ax.text(k, x["s_mean"] + 0.01, f"n={x['n']}", ha="center", fontsize=6, color=MUTED)
    ax.set_xticks(range(len(w)), [x["pt_date"][5:] for x in w]); ax.set_ylabel("mean stance toward\nthe eventual winner")
    m = R26["primary"]["mantel_stance"]
    ax.set_title(f"#26: stance vs ballot similarity r = {m['r']:.2f} (p = {m['p_greater']:.2f})", loc="left")
    fig.savefig(GP / "G26/figures/g26_winner_stance.pdf", bbox_inches="tight"); plt.close(fig)
    # G40: class shares vs #12 opponents
    fig, ax = plt.subplots(figsize=(4.2, 2.4))
    labs = ["agree", "support", "neutral", "oppose", "undermine"]
    sh40 = R40["primary"]["shares"]
    ax.barh(range(5)[::-1], [sh40[k] for k in labs], color=STANCE, height=0.6)
    ax.set_yticks(range(5)[::-1], labs); ax.set_xlabel("share of #40 replies (Jev)")
    ax.set_title("#40: Jev class shares in a cooperative week", loc="left")
    fig.savefig(GP / "G40/figures/g40_shares.pdf", bbox_inches="tight"); plt.close(fig)


def summary_obsb(SY):
    """Page-2 figure: synthetic power at #12 (real reply graph) and detector false alarms, sign-shuffle vs calibrated."""
    fig, axs = plt.subplots(1, 2, figsize=(7.2, 2.3), gridspec_kw={"wspace": 0.42})
    ax = axs[0]
    cells = SY["S1"]["cells"]; Dl = [0.0, 0.25, 0.5, 1.0]
    for cn, ls, lab in (("jev", "-", "Jev noise"), ("perfect", "--", "perfect labels")):
        ax.plot(Dl, [cells[f"Delta={d}|{cn}"]["power_gamma_p01"] for d in Dl], ls, color=STANCE, marker="o", ms=5, label=f"team-contrast power, {lab}")
        ax.plot(Dl, [cells[f"Delta={d}|{cn}"]["acc_mean"] for d in Dl], ls, color=TOPIC, marker="s", ms=5, label=f"camp accuracy, {lab}")
    ax.axhline(0.7, color=GRAY, lw=1, ls=":"); ax.text(0.98, 0.62, "chance accuracy", fontsize=6, color=MUTED, ha="right")
    ax.set_xlabel("camp coupling Δ (logit)"); ax.set_ylim(0, 1.05); ax.legend(fontsize=5.6, loc="lower right")
    ax.set_title("(a) synthetic #12 (real reply graph)", loc="left")
    ax = axs[1]
    chk = load("calibration_check.json")
    s6 = SY["S6"]["cells"]
    groups = [("#40", "40"), ("#51", "51")]
    x = np.arange(len(groups)); w = 0.26
    ss = [s6[f"{g}|fields"]["rate_faction_p05"] for _, g in groups]
    cal = [chk[f"G{g}|fields"]["rate_p_faction_lt05"] for _, g in groups]
    pw = [chk.get(f"G{g}|mattis0.5", {}).get("rate_p_faction_lt05", np.nan) for _, g in groups]
    ax.bar(x - w, ss, w, color=GRAY, label="false alarm, sign-shuffle null")
    ax.bar(x, cal, w, color=STANCE, label="false alarm, calibrated null")
    ax.bar(x + w, pw, w, color=TOPIC, label="power, camps ±0.5 logit (calibrated)")
    ax.axhline(0.05, color=MUTED, lw=0.8, ls="--"); ax.text(-0.5, 0.07, "5%", fontsize=6, color=MUTED, ha="left")
    for xi, v in zip(x - w, ss):
        ax.text(xi, v + 0.02, f"{v:.2f}", ha="center", fontsize=6, color=INK)
    for xi, v in zip(x, cal):
        ax.text(xi, v + 0.02, f"{v:.2f}", ha="center", fontsize=6, color=INK)
    ax.set_xticks(x, [g for g, _ in groups]); ax.set_ylim(0, 1.75); ax.set_yticks([0, 0.25, 0.5, 0.75, 1.0]); ax.set_ylabel("rate of camp alarm (p < 0.05)")
    ax.legend(fontsize=5.6, loc="upper left")
    ax.set_title("(b) camp detector: false alarms and power", loc="left")
    fig.savefig(FIG / "summary_obsb.pdf", bbox_inches="tight")
    plt.close(fig)


def main():
    FIG.mkdir(exist_ok=True)
    R12, R51, R26, R40 = (load(f"G{g}/results.json") for g in ("12", "51", "26", "40"))
    V = load("validation/results.json")
    SY = load("synthetic/results.json")
    summary_obs(R12, R51)
    full_summary(R12, R51, R26, R40, V, SY)
    per_period(R12, R51, R26, R40)
    if (DATA / "calibration_check.json").exists():
        summary_obsb(SY)
    print("figures written")


if __name__ == "__main__":
    main()
