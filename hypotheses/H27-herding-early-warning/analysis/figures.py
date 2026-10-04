"""H27 figures (synthetic validation, real-data onsets and indicators, summary observable, one-page summary).

Usage: uv run python hypotheses/H27-herding-early-warning/analysis/figures.py [synthetic|real|summary|all]
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ews_core as E  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
HYP = ROOT / "hypotheses/H27-herding-early-warning"
FIG = HYP / "figures"
DATA = ROOT / "data/processed/H27-herding-early-warning"
# reference categorical palette (dataviz skill), fixed order
C1, C2, C3, C4, C5, C6, C7, C8 = "#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#4a3aa7", "#e34948"
INK, INK2, GRID = "#0b0b0b", "#52514e", "#e2e1dc"
plt.rcParams.update({"font.size": 8, "axes.edgecolor": INK2, "axes.labelcolor": INK, "xtick.color": INK2, "ytick.color": INK2,
                     "axes.spines.top": False, "axes.spines.right": False, "axes.grid": True, "grid.color": GRID,
                     "grid.linewidth": 0.5, "legend.frameon": False, "pdf.fonttype": 42})

SC_SHORT = {"S0": "null", "S0drift": "drift null", "SF_slow": "fold slow", "SF_fast": "fold fast", "SN": "noise flip",
            "SS": "field step", "SF_compete": "fold+compet.", "SF_clean12": "fold N=12\nclean", "SF_big": "fold N=200\nclean"}
SC_LABEL = {"S0": "S0 null", "S0drift": "S0 drifting fields", "SF_slow": "fold, slow ramp", "SF_fast": "fold, fast ramp",
            "SN": "noise-induced", "SS": "field step", "SF_compete": "fold + competitors", "SF_clean12": "fold, N=12 clean",
            "SF_big": "fold, N=200 clean"}
IND_LABEL = {"composite": "τ_AR1+τ_SD", "tau_ar1": "τ_AR1", "tau_sd": "τ_SD", "tau_sd_binom": "τ_SD (binomial)",
             "tau_skew": "τ_skew", "tau_flick": "τ_flicker", "flick_level": "flicker count", "mean_last4": "share (last 1 h)"}


def synthetic():
    S = json.loads((DATA / "synthetic/synthetic_summary.json").read_text())
    summ, meta = S["summary"], S["meta"]
    ex = json.loads((DATA / "synthetic/synthetic_examples.json").read_text())
    fig = plt.figure(figsize=(7.2, 6.4))
    gs = fig.add_gridspec(3, 3, height_ratios=[1, 1, 1.3], hspace=0.6, wspace=0.35)
    for i, nm in enumerate(["SF_big", "SF_slow", "SN", "SS", "SF_compete", "S0drift"]):
        ax = fig.add_subplot(gs[i // 3, i % 3])
        cands = [r for r in ex[nm] if any(o["project"] == 0 for o in r["onsets"] + r.get("onsets_slow", []))]
        r = cands[0] if cands else ex[nm][0]
        k, n = np.array(r["k"]), np.array(r["n"])
        x = E.shares(k, n)
        t = np.arange(len(n)) * 0.25
        for a in range(x.shape[1]):
            ax.plot(t, x[:, a], color=[C1, C2, C3, C4, C5][a], lw=1.0 if a else 1.6, alpha=1 if a == 0 else 0.6)
        ax.plot(t, r["true_xA"], color=INK, lw=0.8, ls=":", label="true share of A")
        for o in r["onsets"]:
            ax.axvline(o["w0"] * 0.25, color=[C1, C2, C3, C4, C5][o["project"]], lw=0.8, ls="--")
        if r["t_event"] is not None:
            ax.axvline(r["t_event"] / 60, color=C8, lw=0.8, alpha=0.6)
        for d in range(1, 5):
            ax.axvline(4 * d, color=GRID, lw=1.5, zorder=0)
        ax.set_ylim(-0.02, 1.02)
        ax.set_title(SC_LABEL[nm], fontsize=8)
        ax.set_xlabel("active hours")
        if i % 3 == 0:
            ax.set_ylabel("project share x_a")
    ax = fig.add_subplot(gs[2, :])
    order = ["S0drift", "SS", "SN", "SF_compete", "SF_fast", "SF_slow", "SF_clean12", "SF_big"]
    keys = ["composite", "tau_ar1", "tau_sd", "tau_sd_binom", "tau_flick", "mean_last4"]
    cols = [C1, C2, C3, C4, C5, C7]
    w = 0.13
    for j, kk in enumerate(keys):
        for i, nm in enumerate(order):
            for rule, mk, off in (("O1", "o", -0.03), ("O1slow", "s", 0.03)):
                A = summ[nm][rule]["auc"]["4"][kk]
                if A["auc"] is None or A["auc"] != A["auc"]:
                    continue
                xx = i + (j - 2.5) * w + off
                ax.plot([xx, xx], A["ci"], color=cols[j], lw=0.8, alpha=0.7)
                ax.plot(xx, A["auc"], mk, color=cols[j], ms=3.2 if rule == "O1" else 2.6,
                        mfc=cols[j] if rule == "O1" else "white", label=(IND_LABEL[kk] if (i == 0 and rule == "O1") else None))
    ax.axhline(0.5, color=INK2, lw=0.8)
    ax.set_xticks(range(len(order)))
    ax.set_xticklabels([f"{SC_SHORT[nm]}\nn={summ[nm]['O1']['auc']['4']['n_onset_segments']}/{summ[nm]['O1slow']['auc']['4']['n_onset_segments']}"
                        for nm in order], fontsize=6.5)
    ax.set_ylabel("AUC, onset vs placebo (lead 1 h)")
    ax.set_ylim(0.2, 1.02)
    ax.legend(ncol=6, fontsize=6.5, loc="lower center", bbox_to_anchor=(0.5, -0.42))
    ax.set_title(f"Discrimination at village sampling (filled: O1 rule; open: O1-slow; n = evaluable onsets); τ* = {meta['tau_star']:.2f}", fontsize=8)
    fig.suptitle("H27 synthetic validation: kinetic mean-field Potts at village sampling (W = 15 min, 5 × 4-h days)", fontsize=9)
    fig.savefig(FIG / "synthetic_validation.pdf", bbox_inches="tight")
    plt.close(fig)
    print("wrote", FIG / "synthetic_validation.pdf")




def _period(g, W=15):
    import explore as X
    k, n, win, day, s = X.load_series(g, W)
    p = E.P0 if W == 15 else E.P_W30
    on = E.find_onsets(k, n, win, day, p)
    ind = E.all_window_indicators(k, n, p)
    tau = X.load_tau_star()
    al_e, watch = E.alarms(ind, k, "ews", tau, p)
    al_l, _ = E.alarms(ind, k, "level", tau, p)
    projs = pl.read_parquet(DATA / f"G{g:02d}" / f"projects_w{W}.parquet")
    names = {lab: E.display_project(x, lab) for lab, x in zip(projs["label"].to_list(), projs["project"].to_list())}
    return k, n, day, on, ind, al_e, al_l, names


def real():
    R = json.loads((DATA / "results_round1.json").read_text())
    gs = [ps["goal"] for ps in R["W15"]["period_summaries"] if ps["n_onsets"] > 0]
    fig, axes = plt.subplots(len(gs), 1, figsize=(7.2, 1.25 * len(gs) + 0.4), squeeze=False)
    for ax, g in zip(axes[:, 0], gs):
        k, n, day, on, ind, al_e, al_l, names = _period(g)
        x = ind["x"]
        t = np.arange(len(n)) * 0.25
        projs = sorted({o["project"] for o in on})
        cols = [C1, C2, C3, C4, C5, C6, C7, C8]
        for j, a in enumerate(projs):
            c = cols[j % 8]
            ax.plot(t, x[:, a], color=c, lw=1.0, label=names.get(a + 1, "?")[:28])
            for o in on:
                if o["project"] == a:
                    ax.axvline(o["w0"] * 0.25, color=c, ls="--", lw=0.9)
            ea = np.where(al_e[:, a])[0]
            la = np.where(al_l[:, a])[0]
            ax.plot(ea * 0.25, np.full(len(ea), 1.06 + 0.05 * j), "|", color=c, ms=4, mew=1.0)
            ax.plot(la * 0.25, np.full(len(la), -0.08 - 0.05 * j), "|", color=c, ms=4, mew=1.0, alpha=0.6)
        for d in np.where(np.diff(day) != 0)[0]:
            ax.axvline((d + 1) * 0.25, color=GRID, lw=1.6, zorder=0)
        ax.set_ylim(-0.25, 1.3)
        ax.set_ylabel(f"#{g}\nshare", fontsize=7)
        ax.legend(fontsize=5.5, loc="upper left", ncol=min(4, len(projs)), bbox_to_anchor=(0.0, 1.32))
    axes[-1, 0].set_xlabel("active hours (grey lines: day boundaries)")
    fig.suptitle("H27 real data (W = 15 min): onset-project shares, onsets (dashed), EWS alarms (ticks above), level alarms (ticks below)",
                 fontsize=8)
    fig.tight_layout()
    fig.savefig(FIG / "real_onsets.pdf", bbox_inches="tight")
    plt.close(fig)
    print("wrote", FIG / "real_onsets.pdf")


def _auc_panel(ax, S, R):
    keys = ["tau_ar1", "tau_sd", "composite", "tau_flick", "mean_last4"]
    lab = {"tau_ar1": "τ_AR1", "tau_sd": "τ_SD", "composite": "τ_AR1\n+τ_SD", "tau_flick": "τ_flick-\nering", "mean_last4": "share\nlevel"}
    series = [("synthetic fold, N=12", S["summary"]["SF_slow"]["O1"]["auc"]["4"], C7, "o"),
              ("synthetic fold, N=200", S["summary"]["SF_big"]["O1slow"]["auc"]["4"], C3, "s"),
              (f"village, 15 min (n={R['W15']['auc']['4']['n_onset_segments']})", R["W15"]["auc"]["4"], C1, "D"),
              (f"village, 30 min (n={R['W30']['auc']['4']['n_onset_segments']})", R["W30"]["auc"]["4"], C2, "^")]
    for j, (nm, A, c, mk) in enumerate(series):
        for i, kk in enumerate(keys):
            xx = i + (j - 1.5) * 0.18
            ax.plot([xx, xx], A[kk]["ci"], color=c, lw=0.9)
            ax.plot(xx, A[kk]["auc"], mk, color=c, ms=4, label=nm if i == 0 else None)
    ax.axhline(0.5, color=INK2, lw=0.8)
    ax.set_xticks(range(len(keys)))
    ax.set_xticklabels([lab[k] for k in keys])
    ax.set_ylabel("AUC, onset vs placebo (lead 1 h)")
    ax.set_ylim(0.0, 1.05)
    ax.legend(fontsize=6, loc="lower left", ncol=2)


def _operator_panel(ax, R, Aop):
    ops = Aop["W15"]["operator"]
    days = R["W15"]["operator"]["ews"]["days"]
    lab = {"ews": "EWS (τ_AR1, τ_SD > τ*)", "level": "share ≥ 0.3", "momentum": "+2 agents in 30 min"}
    cols = {"ews": C1, "level": C2, "momentum": C3}
    for rule in ("ews", "level", "momentum"):
        o = ops[rule]
        fa = (o["alarms"] - o["alarms"] * o["ppv"]) / days
        ax.plot(fa, o["hits"], "o", color=cols[rule], ms=6, label=lab[rule])
        ax.plot(fa, o["N2_mean_hits"], "o", mfc="white", color=cols[rule], ms=6)
        ax.plot([fa, fa], [o["N2_mean_hits"], o["hits"]], color=cols[rule], lw=0.8)
    ax.set_xlabel("false alarms per active day (all projects)")
    ax.set_ylabel(f"onsets warned within 3 h (of {ops['ews']['onsets']})")
    ax.set_ylim(0, 10)
    ax.set_xlim(0, 6.5)
    ax.legend(fontsize=6, loc="upper left")
    ax.text(0.98, 0.04, "open: same alarm rate, shifted in time", transform=ax.transAxes, ha="right", fontsize=6, color=INK2)


def summary():
    S = json.loads((DATA / "synthetic/synthetic_summary.json").read_text())
    R = json.loads((DATA / "results_round1.json").read_text())
    Aop = json.loads((DATA / "assemble_round1.json").read_text())
    fig, axes = plt.subplots(1, 2, figsize=(7.0, 2.6), gridspec_kw=dict(width_ratios=[1.45, 1]))
    _auc_panel(axes[0], S, R)
    axes[0].set_title("(a) Early-warning discrimination", fontsize=8, loc="left")
    _operator_panel(axes[1], R, Aop)
    axes[1].set_title("(b) Operator alarms, village 15 min", fontsize=8, loc="left")
    fig.tight_layout()
    fig.savefig(FIG / "summary_obs.pdf", bbox_inches="tight")
    fig.savefig(FIG / "summary_obs.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    print("wrote", FIG / "summary_obs.pdf")


def onepage():
    S = json.loads((DATA / "synthetic/synthetic_summary.json").read_text())
    R = json.loads((DATA / "results_round1.json").read_text())
    Aop = json.loads((DATA / "assemble_round1.json").read_text())
    fig = plt.figure(figsize=(8.0, 10.2))
    gs = fig.add_gridspec(4, 2, height_ratios=[1, 1, 1, 0.9], hspace=0.55, wspace=0.3)
    # (a) synthetic composite AUC by scenario
    ax = fig.add_subplot(gs[0, :])
    order = ["S0", "S0drift", "SS", "SN", "SF_compete", "SF_fast", "SF_slow", "SF_clean12", "SF_big"]
    for i, nm in enumerate(order):
        for rule, c, off in (("O1", C1, -0.1), ("O1slow", C2, 0.1)):
            A = S["summary"][nm][rule]["auc"]["4"]
            for kk, mk, o2 in (("composite", "o", 0), ("mean_last4", "s", 0.05)):
                if A[kk]["auc"] is None or A[kk]["auc"] != A[kk]["auc"]:
                    continue
                ax.plot([i + off + o2] * 2, A[kk]["ci"], color=c, lw=0.8, alpha=0.8)
                ax.plot(i + off + o2, A[kk]["auc"], mk, color=c, ms=4, mfc=c if kk == "composite" else "white",
                        label=(f"{'τ_AR1+τ_SD' if kk == 'composite' else 'share level'}, {rule}" if i == 0 else None))
    ax.axhline(0.5, color=INK2, lw=0.8)
    ax.set_xticks(range(len(order)))
    ax.set_xticklabels([SC_SHORT[nm] for nm in order], fontsize=6.5)
    ax.set_ylabel("AUC (lead 1 h)")
    ax.set_ylim(0.3, 1.02)
    ax.legend(fontsize=6, ncol=4, loc="upper left")
    ax.set_title("(a) Synthetic kinetic Potts at village sampling: only a large clean swarm approaching a fold warns", fontsize=8, loc="left")
    # (b) #31 example
    ax = fig.add_subplot(gs[1, :])
    k, n, day, on, ind, al_e, al_l, names = _period(31)
    t = np.arange(len(n)) * 0.25
    projs = sorted({o["project"] for o in on})
    for j, a in enumerate(projs):
        c = [C1, C2, C3, C4][j % 4]
        ax.plot(t, ind["x"][:, a], color=c, lw=1.0, label=names.get(a + 1, "?")[:30])
        for o in on:
            if o["project"] == a:
                ax.axvline(o["w0"] * 0.25, color=c, ls="--", lw=0.9)
        ea = np.where(al_e[:, a])[0]
        ax.plot(ea * 0.25, np.full(len(ea), 1.05 + 0.05 * j), "|", color=c, ms=4)
    for d in np.where(np.diff(day) != 0)[0]:
        ax.axvline((d + 1) * 0.25, color=GRID, lw=1.6, zorder=0)
    ax.set_ylim(-0.05, 1.3)
    ax.set_xlabel("active hours")
    ax.set_ylabel("share of labeled agents")
    ax.legend(fontsize=6, ncol=4, loc="upper right")
    ax.set_title("(b) #31 free week: four herding onsets (dashed); EWS alarms as ticks; two onsets come too early for 6 h of history",
                 fontsize=8, loc="left")
    # (c) AUC panel
    ax = fig.add_subplot(gs[2, 0])
    _auc_panel(ax, S, R)
    ax.set_title("(c) Indicators: no AR1 rise anywhere", fontsize=8, loc="left")
    # (d) operator
    ax = fig.add_subplot(gs[2, 1])
    _operator_panel(ax, R, Aop)
    ax.set_title("(d) Operator alarms vs rate-matched null", fontsize=8, loc="left")
    # (e) precursor categories
    ax = fig.add_subplot(gs[3, 0])
    pr = Aop["W15"]["precursors"]
    tr = Aop["W15"]["triggers_posthoc"]
    cats = [("onsets", pr["total"]), ("project never\nseen before", pr["never_seen"]), ("evaluable at\n1 h lead", R["W15"]["auc"]["4"]["n_onset_segments"]),
            ("chat link to it\nin prior 30 min", tr["link"]["onsets_with"]), ("human message\nin prior 30 min", tr["human"]["onsets_with"])]
    ax.bar(range(len(cats)), [c[1] for c in cats], color=[INK2, C8, C1, C3, C4], width=0.6)
    ax.plot([3], [tr["link"]["perm_mean"]], "_", color=INK, ms=18, mew=1.5)
    ax.plot([4], [tr["human"]["perm_mean"]], "_", color=INK, ms=18, mew=1.5)
    for i, c in enumerate(cats):
        ax.text(i, c[1] + 0.3, str(c[1]), ha="center", fontsize=7)
    ax.set_xticks(range(len(cats)))
    ax.set_xticklabels([c[0] for c in cats], fontsize=5.5)
    ax.set_ylabel("count (15-min arm)")
    ax.set_title("(e) What precedes onsets (black bars: within-period chance)", fontsize=8, loc="left")
    # (f) table
    ax = fig.add_subplot(gs[3, 1])
    ax.axis("off")
    e, lv = Aop["W15"]["operator"]["ews"], Aop["W15"]["operator"]["level"]
    rows = [["", "EWS alarm", "share ≥ 0.3"],
            ["hits / onsets", f"{e['hits']}/{e['onsets']}", f"{lv['hits']}/{lv['onsets']}"],
            ["alarm rate (per window)", f"{100 * e['alarm_rate']:.1f}%", f"{100 * lv['alarm_rate']:.1f}%"],
            ["precision (PPV)", f"{100 * e['ppv']:.1f}%", f"{100 * lv['ppv']:.1f}%"],
            ["base rate", f"{100 * e['base_rate']:.2f}%", f"{100 * lv['base_rate']:.2f}%"],
            ["rate-matched null hits", f"{e['N2_mean_hits']:.1f} (p {R['W15']['operator']['ews']['N2_p']:.2f})", f"{lv['N2_mean_hits']:.1f} (p {lv['N2_p']:.2f})"],
            ["median lead of hits", f"{R['W15']['operator']['ews']['median_lead_h']:.2f} h", f"{R['W15']['operator']['level']['median_lead_h']:.2f} h"],
            ["30-min arm hits", f"{Aop['W30']['operator']['ews']['hits']}/{Aop['W30']['operator']['ews']['onsets']}",
             f"{Aop['W30']['operator']['level']['hits']}/{Aop['W30']['operator']['level']['onsets']}"]]
    tb = ax.table(cellText=rows, loc="center", cellLoc="center", colWidths=[0.5, 0.27, 0.23])
    tb.auto_set_font_size(False)
    tb.set_fontsize(6.0)
    tb.scale(1, 1.25)
    for (r, c), cell in tb.get_celld().items():
        cell.set_edgecolor(GRID)
        if r == 0:
            cell.set_text_props(weight="bold")
    ax.set_title("(f) Operating characteristics (15 min, 3-h horizon)", fontsize=8, loc="left", pad=14)
    fig.suptitle("H27 round 1: critical slowing down does not warn of herding onsets in the AI Village", fontsize=10, y=0.995)
    fig.savefig(FIG / "H27_round1_summary.pdf", bbox_inches="tight")
    plt.close(fig)
    print("wrote", FIG / "H27_round1_summary.pdf")


def synth_compact():
    S = json.loads((DATA / "synthetic/synthetic_summary.json").read_text())
    fig, ax = plt.subplots(figsize=(3.6, 2.0))
    order = ["S0", "S0drift", "SS", "SN", "SF_compete", "SF_fast", "SF_slow", "SF_clean12", "SF_big"]
    short = {"S0": "null", "S0drift": "drift", "SS": "field\nstep", "SN": "noise\nflip", "SF_compete": "fold+\ncompet.",
             "SF_fast": "fold\nfast", "SF_slow": "fold\nslow", "SF_clean12": "fold\nN=12\nclean", "SF_big": "fold\nN=200"}
    for i, nm in enumerate(order):
        rule = "O1slow" if nm == "SF_big" else "O1"
        A = S["summary"][nm][rule]["auc"]["4"]
        for kk, c, mk, off in (("composite", C1, "o", -0.12), ("mean_last4", C2, "s", 0.12)):
            ax.plot([i + off] * 2, A[kk]["ci"], color=c, lw=0.8)
            ax.plot(i + off, A[kk]["auc"], mk, color=c, ms=3.5, mfc=c if kk == "composite" else "white",
                    label=("τ_AR1+τ_SD trend" if kk == "composite" else "share level, last 1 h") if i == 0 else None)
    ax.axhline(0.5, color=INK2, lw=0.8)
    ax.set_xticks(range(len(order)))
    ax.set_xticklabels([short[n] for n in order], fontsize=5.5)
    ax.set_ylabel("AUC (lead 1 h)", fontsize=7)
    ax.set_ylim(0.35, 1.02)
    ax.tick_params(labelsize=6)
    ax.legend(fontsize=6, loc="upper left")
    fig.tight_layout()
    fig.savefig(FIG / "summary_synth.pdf", bbox_inches="tight")
    plt.close(fig)
    print("wrote", FIG / "summary_synth.pdf")


if __name__ == "__main__":
    what = sys.argv[1] if len(sys.argv) > 1 else "all"
    if what in ("synthetic", "all"):
        synthetic()
    if what in ("real", "all"):
        real()
    if what in ("summary", "all"):
        summary()
        onepage()
        synth_compact()
