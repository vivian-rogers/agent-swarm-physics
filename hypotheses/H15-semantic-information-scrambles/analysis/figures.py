"""H15 figures: F1 synthetic validation, F3 event studies, F4 context erasure, F5 value of each store/channel,
F0 one-page summary. Reads synthetic.json, results.json, v_choice.json, consolidation_profile.parquet."""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scheme"))
from h15common import FIG, OUT, V_CANDIDATES  # noqa: E402

import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

plt.rcParams.update({"font.size": 8, "axes.spines.top": False, "axes.spines.right": False})
syn = json.loads((OUT / "synthetic.json").read_text())
res = json.loads((OUT / "results.json").read_text())
vch = json.loads((OUT / "v_choice.json").read_text())
prof = pl.read_parquet(OUT / "consolidation_profile.parquet")
P = res["primary"]
COL = {"kal": "#2a6f97", "ar1": "#61a5c2", "did": "#c9733a"}
VCOL = {"V_out": "#2a6f97", "V_eng": "#c9733a", "V_rel": "#5a8f29", "V_ord": "#8e5ea2", "V_coh": "#888888"}
FIG.mkdir(exist_ok=True)


def f1(ax_bias, ax_pow, ax_turn):
    scen = [("null_rho0.6", "no effect"), ("effect_rho0.6", "effect"), ("select_beta1.5_rho0.6", "selection"),
            ("select_beta1.5_rho0.6_effect", "sel.+effect"), ("select_beta1.5_rho0.3", "sel. ρ=0.3"),
            ("slump0.5_rho0.6", "slump")]
    x = np.arange(len(scen))
    for k, m in enumerate(("kal", "ar1", "did")):
        b = [syn["ML"][s][m]["bias"] for s, _ in scen]
        ax_bias.bar(x + (k - 1) * 0.27, b, 0.27, color=COL[m], label=m)
    ax_bias.axhline(0, color="k", lw=0.5)
    ax_bias.set_xticks(x, [l for _, l in scen], rotation=30, ha="right")
    ax_bias.set_ylabel("bias of ΔV_ML (SD)")
    ax_bias.set_title(f"ML estimator bias ({syn['reps']} reps, real skeleton)")
    ax_bias.legend(frameon=False, fontsize=7)
    items = [("ML −0.41 SD", syn["ML"]["effect_rho0.6"]["kal"]["reject_neg"]),
             ("ML −0.20 SD", syn["ML"]["effect_small_rho0.6"]["kal"]["reject_neg"]),
             ("ML none", syn["ML"]["null_rho0.6"]["kal"]["reject_neg"]),
             ("MN −0.33 SD", syn["MN"]["deficit0.6"]["reject_neg"]),
             ("MN +novelty", syn["MN"]["deficit0.6_novelty0.4"]["reject_neg"]),
             ("CC −0.44 SD", syn["CC"]["cost0.5"]["kal"]["reject_two_sided"]),
             ("CC none", syn["CC"]["null"]["kal"]["reject_two_sided"])]
    ax_pow.barh(range(len(items)), [v for _, v in items], color="#2a6f97")
    ax_pow.set_yticks(range(len(items)), [k for k, _ in items])
    ax_pow.axvline(0.05, color="k", lw=0.5, ls=":")
    ax_pow.set_xlim(0, 1)
    ax_pow.set_xlabel("rejection rate (meta z ≤ −2; CC two-sided)")
    ax_pow.set_title("power at village sample sizes")
    t = syn["turns"]
    lab = ["no effect", "CF cost", "CF cost + dose"]
    keys = ["null", "cf_cost", "cf_cost_dose"]
    xx = np.arange(3)
    ax_turn.bar(xx - 0.27, [t[k]["truth"] for k in keys], 0.27, color="#bbbbbb", label="truth")
    ax_turn.bar(xx, [t[k]["base"]["est"] for k in keys], 0.27, color="#2a6f97", label="vs agent-day base")
    ax_turn.bar(xx + 0.27, [t[k]["pre"]["est"] for k in keys], 0.27, color="#c9733a", label="vs pre-window")
    ax_turn.axhline(0, color="k", lw=0.5)
    ax_turn.set_xticks(xx, lab)
    ax_turn.set_ylabel("dip_CF − dip_CV (writes/turn)")
    ax_turn.set_title("context erasure: voluntary timing bias")
    ax_turn.legend(frameon=False, fontsize=7)


def fig1():
    fig, axs = plt.subplots(1, 3, figsize=(11, 3.4))
    f1(*axs)
    fig.tight_layout()
    fig.savefig(FIG / "F1_synthetic.pdf")
    plt.close(fig)


def f3(ax, V):
    days = np.arange(-5, 6)
    for t, c in (("ML", "#b2182b"), ("MG", "#ef8a62"), ("MR", "#67a9cf"), ("CC", "#2166ac")):
        cur = res["by_V"][V]["types"][t]["curve"]
        n = res["by_V"][V]["types"][t]["n_events"]
        if cur:
            ax.plot(days, cur, "-o", ms=2.5, color=c, label=f"{t} (n={n})")
    ax.axvline(0, color="k", lw=0.5)
    ax.axhline(0, color="k", lw=0.5)
    ax.set_xlabel("active day relative to event")
    ax.set_ylabel(f"mean u ({V})")
    ax.legend(frameon=False, fontsize=6)


def fig3():
    fig, axs = plt.subplots(2, 3, figsize=(11, 6))
    for ax, V in zip(axs.flat, V_CANDIDATES):
        f3(ax, V)
        ax.set_title(V)
    ax = axs.flat[5]
    for V in V_CANDIDATES:
        cur = res["by_V"][V]["MN"]["curve"]
        if cur:
            ax.plot(np.arange(1, len(cur) + 1), cur, "-o", ms=2.5, color=VCOL[V], label=V)
    ax.axhline(0, color="k", lw=0.5)
    ax.axvspan(0.5, 3.5, color="#eeeeee")
    ax.axvspan(5.5, 12.5, color="#f6f6f6")
    ax.set_xlabel("newcomer tenure (active days)")
    ax.set_ylabel("mean u")
    ax.set_title(f"newcomers (n={res['by_V']['V_eng']['MN']['n_events']})")
    ax.legend(frameon=False, fontsize=6)
    fig.suptitle("Event studies: same-day-differenced, period-standardized viability around natural scrambles", fontsize=9)
    fig.tight_layout()
    fig.savefig(FIG / "F3_event_studies.pdf")
    plt.close(fig)


def f4(ax_prof, ax_diff):
    g = prof.group_by("kind", "off").agg((pl.col("w_rate") * pl.col("n")).sum() / pl.col("n").sum()).sort("off")
    for k, c in (("CF", "#b2182b"), ("CV", "#2166ac")):
        d = g.filter(pl.col("kind") == k)
        ax_prof.plot(d["off"].to_numpy(), d["w_rate"].to_numpy(), "-o", ms=2, color=c,
                     label={"CF": "forced (41-turn cap)", "CV": "voluntary"}[k])
    ax_prof.axvline(0, color="k", lw=0.5)
    ax_prof.set_xlabel("turn relative to consolidation (− before, + after)")
    ax_prof.set_ylabel("write turns / turn")
    ax_prof.set_title("context erasure: write rate around consolidations (regime III)")
    ax_prof.legend(frameon=False, fontsize=7)
    k = "diff_base" if res["turn_primary"] == "base" else "diff_pre"
    us = [u for u in res["CTX"] if "write" in res["CTX"][u] and res["CTX"][u]["write"][k]]
    est = [res["CTX"][u]["write"][k]["est"] for u in us]
    lo = [res["CTX"][u]["write"][k]["lo"] for u in us]
    hi = [res["CTX"][u]["write"][k]["hi"] for u in us]
    y = np.arange(len(us))
    ax_diff.errorbar(est, y, xerr=[np.array(est) - np.array(lo), np.array(hi) - np.array(est)], fmt="o",
                     color="#2a6f97", ms=3)
    m = res["CTX_meta"]["write"]
    if m:
        ax_diff.errorbar([m["mu"]], [len(us)], xerr=[[m["mu"] - m["lo"]], [m["hi"] - m["mu"]]], fmt="D", color="k", ms=4)
    ax_diff.set_yticks(list(y) + [len(us)], [f"#{u}" for u in us] + ["meta"])
    ax_diff.axvline(0, color="k", lw=0.5)
    ax_diff.set_xlabel("dip_CF − dip_CV (writes/turn, vs agent-day base)")
    ax_diff.set_title("forced minus voluntary, per period")


def f4rd(ax):
    us = [u for u in res["CTX"] if res["CTX"][u].get("posthoc_rd")]
    for k, (kind, c) in enumerate((("CF", "#b2182b"), ("CV", "#2166ac"))):
        y = np.arange(len(us)) + (k - 0.5) * 0.3
        est = np.array([res["CTX"][u]["posthoc_rd"].get(kind, {}).get("rel_dip", np.nan) for u in us])
        lo = np.array([res["CTX"][u]["posthoc_rd"].get(kind, {}).get("lo", np.nan) for u in us])
        hi = np.array([res["CTX"][u]["posthoc_rd"].get(kind, {}).get("hi", np.nan) for u in us])
        ax.errorbar(est, y, xerr=[est - lo, hi - est], fmt="o", ms=3, color=c,
                    label={"CF": "forced (exogenous timing)", "CV": "voluntary"}[kind])
    ax.set_yticks(np.arange(len(us)), [f"#{u}" for u in us])
    ax.axvline(0, color="k", lw=0.5)
    ax.set_xlabel("relative write dip, turns +1..+10 vs −20..−11")
    ax.set_title("POST-HOC: cost of a context erasure, per period")
    ax.legend(frameon=False, fontsize=6, loc="lower right")


def fig4():
    fig, axs = plt.subplots(1, 3, figsize=(14, 3.6))
    f4(axs[0], axs[1])
    f4rd(axs[2])
    fig.tight_layout()
    fig.savefig(FIG / "F4_context_erasure.pdf")
    plt.close(fig)


def f5(ax):
    rows = []
    for t, lab in (("ML", "memory loss (ML)"), ("MG", "memory glitch (MG)"), ("MR", "rewrite (MR, control)"),
                   ("CC", "chat cut (CC)"), ("MN", "newcomer (MN)")):
        for V in V_CANDIDATES:
            if t == "MN":
                m = res["by_V"][V]["MN"]["meta"]
            else:
                m = res["by_V"][V]["types"][t]["meta"].get(P)
            if m:
                rows.append((lab, V, m["mu"], m["lo"], m["hi"], m["k"]))
    labs = []
    y = 0
    last = None
    for lab, V, mu, lo, hi, k in rows:
        if lab != last:
            y += 0.6
            labs.append((y, lab))
            last = lab
        ax.errorbar([mu], [y], xerr=[[mu - lo], [hi - mu]], fmt="o", color=VCOL[V], ms=3)
        y += 1
    ax.axvline(0, color="k", lw=0.5)
    ax.set_yticks([yy for yy, _ in labs], [l for _, l in labs])
    ax.invert_yaxis()
    ax.set_xlabel(f"meta ΔV (SD), counterfactual {P}")
    ax.set_title("value of information by store / channel")
    for V in V_CANDIDATES:
        ax.plot([], [], "o", color=VCOL[V], label=V)
    ax.legend(frameon=False, fontsize=6, loc="lower right")


def fig5():
    fig, ax = plt.subplots(figsize=(7, 5))
    f5(ax)
    fig.tight_layout()
    fig.savefig(FIG / "F5_value_by_store.pdf")
    plt.close(fig)


def fig0(text_lines):
    fig = plt.figure(figsize=(8.27, 11.69))
    gs = fig.add_gridspec(4, 2, height_ratios=[0.9, 1.1, 1.1, 1.3], hspace=0.6, wspace=0.45,
                          left=0.17, right=0.97, top=0.97, bottom=0.05)
    ax = fig.add_subplot(gs[0, :])
    ax.axis("off")
    ax.text(-0.15, 1, "H15 · Semantic information through natural scrambles (round 1, non-holdout)",
            fontsize=10.5, weight="bold", va="top")
    ax.text(-0.15, 0.86, "\n".join(text_lines), fontsize=6.9, va="top", family="DejaVu Sans")
    f5(fig.add_subplot(gs[1, 0]))
    a = fig.add_subplot(gs[1, 1])
    f3(a, res["V_star"]["III"])
    a.set_title(f"event study on V*(III) = {res['V_star']['III']}")
    f4(fig.add_subplot(gs[2, 0]), fig.add_axes([2, 2, 0.01, 0.01]))
    f4rd(fig.add_subplot(gs[2, 1]))
    f1(fig.add_subplot(gs[3, 0]), fig.add_subplot(gs[3, 1]), fig.add_axes([2, 2, 0.01, 0.01]))
    fig.savefig(FIG / "F0_summary.pdf")
    plt.close(fig)


if __name__ == "__main__":
    fig1()
    fig3()
    fig4()
    fig5()
    lines = json.loads((OUT / "summary_lines.json").read_text()) if (OUT / "summary_lines.json").exists() else []
    fig0(lines)
    print("figures written")
