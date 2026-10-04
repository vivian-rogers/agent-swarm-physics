"""H31 round-1 figures.

  uv run python hypotheses/H31-consensus-time-spectral-gap/analysis/figures.py
Writes figures/summary_obs.pdf (+ .png), figures/H31_round1_summary.pdf, figures/synthetic_validation.pdf.
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
import h31lib as L  # noqa: E402

FIG = L.HYP / "figures"
C1, C2, C3 = "#2a78d6", "#eb6834", "#1baf7a"
INK, INK2, GRID = "#0b0b0b", "#52514e", "#e6e5e0"
plt.rcParams.update({"font.size": 8, "axes.edgecolor": INK2, "axes.labelcolor": INK, "xtick.color": INK2,
                     "ytick.color": INK2, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6, "legend.frameon": False,
                     "font.family": "DejaVu Sans"})
MODEL_LABEL = {"M0": "constant (field)", "M_l2_sym": r"$\lambda_2$ slope 1 (H31)", "M_l2_sym_free": r"$\lambda_2$ free slope",
               "M_N": r"$N^a$", "M_ul2_rw": r"reading rate $u\,\lambda_2^{rw}$", "M_l2_sym_core": r"$\lambda_2$ core agents",
               "M_g_tr": r"time-respecting $\gamma_{tr}$", "M_tau_V": "voter on schedule", "M_tau_wave": "herding wave"}


def load():
    ep = pl.read_parquet(L.DATA / "events_ep_w30.parquet")
    cross = json.loads((L.DATA / "cross_period_w30.json").read_text())
    rob = json.loads((L.DATA / "robustness_w30.json").read_text())
    syn = json.loads((L.DATA / "synthetic" / "synthetic_results.json").read_text())
    ec = pl.read_parquet(L.DATA / "events_ec.parquet")
    e26 = json.loads((L.DATA / "ev26.json").read_text())
    return ep, cross, rob, syn, ec, e26


def panel_tau_l2(ax, ep, cross, show_legend=True):
    unc = ep.filter(pl.col("consensus") & ~pl.col("frozen"))
    inst = ep.filter(pl.col("consensus") & pl.col("frozen") & (pl.col("t0_h") > 0.75 + 1e-6))
    for reg, col, lab in (("I", C1, "regime I"), ("III", C2, "regime II/III")):
        m = (unc["regime"] == "I") if reg == "I" else (unc["regime"] != "I")
        u = unc.filter(m)
        ax.scatter(u["l2_sym"], u["tau_h"], s=22, color=col, edgecolor="white", linewidth=0.8, zorder=3,
                   label=f"{lab}: gradual (n = {u.height})")
    ax.scatter(inst["l2_sym"], np.full(inst.height, 0.25), s=22, facecolor="none", edgecolor=INK2, linewidth=0.9,
               zorder=3, marker="v", label=f"instant, ≤ 0.5 h (n = {inst.height}; censored)")
    xs = np.geomspace(1.2, 130, 50)
    rule = json.loads((L.DATA / "frozen_rule.json").read_text())
    ax.plot(xs, np.exp(rule["lambda_rule"]["log_c"]) / xs, color=INK2, ls="--", lw=1.2, label=r"H31: $\tau \propto 1/\lambda_2$ (calibrated)")
    fr = rule["lambda_free_rule_posthoc"]
    ax.plot(xs, np.exp(fr["log_c"]) * xs ** (-fr["b"]), color=INK, lw=1.6, label=rf"fit: $\tau \propto \lambda_2^{{-{fr['b']:.2f}}}$")
    ax.axhline(np.exp(rule["constant_rule"]["log_c"]), color=C3, lw=1.4, ls=":", label="constant (field)")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel(r"exposure spectral gap $\lambda_2^{w,\mathrm{sym}}$ (1/active h)")
    ax.set_ylabel("consensus time τ_P (active h)")
    ax.set_ylim(0.15, 60)
    t1 = cross["T1_slopes_period"]["l2_sym"]
    ax.set_title(rf"(a) Project consensus vs $\lambda_2$: slope {t1['b']:.2f} [{t1['lo']:.2f}, {t1['hi']:.2f}]", loc="left",
                 fontsize=8.5, color=INK)
    if show_legend:
        ax.legend(fontsize=6.2, loc="upper center", bbox_to_anchor=(0.5, -0.22), ncol=2, handlelength=1.6,
                  columnspacing=1.0)


def panel_lopo(ax, cross, title="(b) Leave-one-period-out error"):
    rm = cross["T3_lopo_rmse"]
    order = ["M0", "M_l2_sym_free", "M_N", "M_ul2_rw", "M_l2_sym_core", "M_l2_sym", "M_tau_V", "M_tau_wave", "M_g_tr"]
    order = [k for k in order if k in rm]
    vals = [rm[k] for k in order]
    y = np.arange(len(order))[::-1]
    cols = [C3 if k == "M0" else (INK if k == "M_l2_sym_free" else C1) for k in order]
    ax.barh(y, vals, color=cols, height=0.62, edgecolor="white", linewidth=1.5)
    ax.axvline(rm["M0"], color=C3, lw=1, ls=":")
    for yi, v in zip(y, vals):
        ax.text(v + 0.03, yi, f"{v:.2f}", va="center", fontsize=6.5, color=INK2)
    ax.set_yticks(y)
    ax.set_yticklabels([MODEL_LABEL[k] for k in order], fontsize=6.8)
    ax.set_xlabel("RMSE of log τ_P (lower is better)")
    ax.set_xlim(0, max(vals) * 1.18)
    ax.grid(axis="y", visible=False)
    ax.set_title(title, loc="left", fontsize=8.5, color=INK)


def panel_synth_slopes(ax, syn, cross):
    pw = syn["S2_power"]
    models = ["F", "V", "H", "A", "D"]
    names = {"F": "F field", "V": "V voter", "H": "H herding", "A": "A fraction", "D": "D count (H31)"}
    for i, m in enumerate(models):
        k = [x for x in pw if x.startswith(m + "|n=2")][0]
        v = pw[k]["l2_sym"]
        ax.plot([v["b_q10"], v["b_q90"]], [i, i], color=C1, lw=2.2, solid_capstyle="round")
        ax.plot(v["b_med"], i, "o", color=C1, ms=5, mec="white")
    t1 = cross["T1_slopes_period"]["l2_sym"]
    ax.axvspan(t1["lo"], t1["hi"], color=C2, alpha=0.18, lw=0)
    ax.axvline(t1["b"], color=C2, lw=1.6, label=f"village: {t1['b']:.2f} [{t1['lo']:.2f}, {t1['hi']:.2f}]")
    ax.axvline(1, color=INK2, ls="--", lw=1, label="H31 theory slope 1")
    ax.set_yticks(range(len(models)))
    ax.set_yticklabels([names[m] for m in models], fontsize=7)
    ax.set_xlabel(r"slope of $\log\tau$ on $\log(1/\lambda_2^{w,\mathrm{sym}})$")
    ax.set_title("(c) Synthetic truths on the real schedules (q10–q90)", loc="left", fontsize=8.5, color=INK)
    ax.legend(fontsize=6.3, loc="lower right")
    ax.grid(axis="y", visible=False)


def panel_N(ax, ep, cross):
    unc = ep.filter(pl.col("consensus") & ~pl.col("frozen"))
    for reg, col in (("I", C1), ("III", C2)):
        m = (unc["regime"] == "I") if reg == "I" else (unc["regime"] != "I")
        u = unc.filter(m)
        ax.scatter(u["N_b"], u["tau_h"], s=20, color=col, edgecolor="white", linewidth=0.8)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xticks([3, 5, 8, 12])
    ax.set_xticklabels(["3", "5", "8", "12"])
    t2 = cross["T2_N"]
    ax.set_xlabel("room size N_b")
    ax.set_ylabel("τ_P (active h)")
    ax.set_title(f"(d) vs room size: slope {t2['b']:.2f} [{t2['lo']:.2f}, {t2['hi']:.2f}]", loc="left", fontsize=8.5, color=INK)


def panel_content(ax, ec):
    dv = ec.filter(pl.col("kind") == "divergence")
    ax.scatter(dv["A0"], dv["Ainf"], s=24, color=C1, edgecolor="white", linewidth=0.8, zorder=3)
    ax.plot([0, 1], [0, 1], color=INK2, lw=0.8, ls="--")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_xlabel("alignment at kickoff A₀")
    ax.set_ylabel("plateau A∞")
    kinds = {k: int(v) for k, v in ec.group_by("kind").len().rows()}
    ax.set_title(f"(e) Content: {kinds.get('divergence', 0)} divergence, {kinds.get('convergence', 0)} convergence, "
                 f"{kinds.get('none', 0)} none", loc="left", fontsize=8.5, color=INK)
    ax.text(0.03, 0.93, "below the diagonal: alignment decays", fontsize=6.5, color=INK2, transform=ax.transAxes)


def panel_vote(ax, e26):
    tr = e26["trajectory"]
    t = np.array([a[0] for a in tr])
    sh = np.array([a[1] for a in tr])
    n = np.array([a[2] for a in tr])
    ok = n >= 3
    ax.step(t[ok], sh[ok], where="post", color=C1, lw=1.6)
    ax.axhline(0.5, color=INK2, ls="--", lw=0.8)
    if e26.get("t_cons_h"):
        ax.axvline(e26["t_cons_h"], color=C2, lw=1)
    ax.set_xlabel("active h since period start")
    ax.set_ylabel("winner's declared share")
    ax.set_ylim(0, 1.02)
    ax.set_title(f"(f) #26 runoff: rise in {e26.get('rise_posthoc_h', float('nan')):.2f} h (post hoc)", loc="left",
                 fontsize=8.5, color=INK)


def nominor(ax):
    from matplotlib.ticker import NullFormatter
    ax.xaxis.set_minor_formatter(NullFormatter())
    ax.yaxis.set_minor_formatter(NullFormatter())


def summary_obs(ep, cross):
    fig, axs = plt.subplots(1, 2, figsize=(7.2, 3.5), gridspec_kw={"width_ratios": [1.25, 1]})
    panel_tau_l2(axs[0], ep, cross)
    nominor(axs[0])
    panel_lopo(axs[1], cross)
    fig.tight_layout(w_pad=1.2)
    fig.savefig(FIG / "summary_obs.pdf")
    fig.savefig(FIG / "summary_obs.png", dpi=180)
    plt.close(fig)


def round1_summary(ep, cross, rob, syn, ec, e26):
    fig, axs = plt.subplots(3, 2, figsize=(8.0, 10.2))
    panel_tau_l2(axs[0, 0], ep, cross)
    panel_lopo(axs[0, 1], cross)
    panel_synth_slopes(axs[1, 0], syn, cross)
    panel_N(axs[1, 1], ep, cross)
    for a in (axs[0, 0], axs[1, 1]):
        nominor(a)
    panel_content(axs[2, 0], ec)
    panel_vote(axs[2, 1], e26)
    k = cross["T4_kick"]
    fs = rob["frozen_split"]
    fig.suptitle("H31 round 1: consensus time vs the exposure graph's spectral gap (non-holdout, W = 30 min)",
                 fontsize=10, color=INK, x=0.02, ha="left")
    fig.text(0.02, 0.005,
             f"E-P: {cross['ep_counts']['consensus']} consensus events = {fs['frozen_at_start']} frozen at kickoff + "
             f"{fs['instant_mid_period']} instant (one-window) + {cross['ep_counts']['uncensored']} gradual, from 14 periods. "
             f"Kick-locked {k['K_obs']:.2f} vs placebo {k['K_placebo']:.2f} (all from kickoff-frozen events; gradual "
             f"{rob['kick_locked_uncensored']:.2f}, instant {rob['kick_locked_instant']:.2f}).",
             fontsize=6.6, color=INK2, wrap=True)
    fig.tight_layout(rect=(0, 0.02, 1, 0.98), h_pad=1.6)
    fig.savefig(FIG / "H31_round1_summary.pdf")
    plt.close(fig)


def synthetic_fig(syn):
    s0 = pl.read_parquet(L.DATA / "synthetic" / "s0_generic.parquet")
    fig, axs = plt.subplots(1, 3, figsize=(10, 3.4))
    ax = axs[0]
    ok = s0["g_tr"] > 0
    ax.scatter(s0.filter(ok)["l2_rw"] * 30, s0.filter(ok)["g_tr"], s=18, color=C1, edgecolor="white")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel(r"$u\,\lambda_2^{rw}$ (1/h)")
    ax.set_ylabel(r"time-respecting $\gamma_{tr}$ (1/h)")
    ax.set_title(rf"(a) S0: $\gamma_{{tr}}$ tracks $u\lambda_2^{{rw}}$ (r = {syn['S0']['corr_log_gtr_log_u_l2rw']:.2f})", loc="left", fontsize=8.5)
    ax = axs[1]
    ax.scatter(s0["l2_sym"], s0["t50_D"], s=18, color=C2, edgecolor="white", label="50%")
    ax.scatter(s0["l2_sym"], s0["t90_D"], s=18, color=C3, edgecolor="white", label="90%")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel(r"$\lambda_2^{w,\mathrm{sym}}$ (1/h)")
    ax.set_ylabel("count-contagion consensus time (h)")
    ax.legend(fontsize=6.5)
    ax.set_title(f"(b) S0: slope {syn['S0']['slope_logt50_D_on_log_inv_l2sym']:.2f} (50%), "
                 f"{syn['S0']['slope_logt90_D_on_log_inv_l2sym']:.2f} (90%)", loc="left", fontsize=8.5)
    ax = axs[2]
    pw = syn["S2_power"]
    models = ["D", "A", "V", "H", "F"]
    cats = ["M0", "M_l2_sym", "M_l2_sym_core", "M_ul2_rw", "other"]
    colors = {"M0": C3, "M_l2_sym": C2, "M_l2_sym_core": "#eda100", "M_ul2_rw": C1, "other": "#c3c2b7"}
    left = np.zeros(len(models))
    for c in cats:
        vals = []
        for m in models:
            k = [x for x in pw if x.startswith(m + "|n=2")][0]
            f = pw[k]["best_model_freq"]
            vals.append(sum(v for kk, v in f.items() if kk not in cats[:-1]) if c == "other" else f.get(c, 0))
        ax.barh(range(len(models)), vals, left=left, color=colors[c], edgecolor="white", linewidth=1.5,
                label=MODEL_LABEL.get(c, c))
        left += np.array(vals)
    ax.set_yticks(range(len(models)))
    ax.set_yticklabels(["D count", "A fraction", "V voter", "H herding", "F field"])
    ax.set_xlabel("share of synthetic datasets won (LOPO)")
    ax.legend(fontsize=6, loc="lower center", bbox_to_anchor=(0.5, 1.12), ncol=3)
    ax.set_title("(c) S2: which model wins, by truth", loc="left", fontsize=8.5, y=1.3)
    ax.grid(axis="y", visible=False)
    for a in axs[:2]:
        nominor(a)
    fig.tight_layout()
    fig.savefig(FIG / "synthetic_validation.pdf")
    plt.close(fig)


def summary_obs_b(syn, cross):
    fig, ax = plt.subplots(figsize=(3.6, 2.15))
    panel_synth_slopes(ax, syn, cross)
    ax.set_title("Slope under each synthetic truth (q10–q90)", loc="left", fontsize=8, color=INK)
    fig.tight_layout()
    fig.savefig(FIG / "summary_obs_b.pdf")
    plt.close(fig)


def main():
    FIG.mkdir(exist_ok=True)
    ep, cross, rob, syn, ec, e26 = load()
    summary_obs(ep, cross)
    summary_obs_b(syn, cross)
    round1_summary(ep, cross, rob, syn, ec, e26)
    synthetic_fig(syn)
    print("figures written to", FIG)


if __name__ == "__main__":
    main()
