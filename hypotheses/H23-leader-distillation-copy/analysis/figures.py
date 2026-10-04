"""H23 figures: G44 panels, the one-page summary PDF, and the hypothesis-page observable figure.

Reads data/processed/H23-leader-distillation-copy/{G44/results.json, G44/verdicts.json, G44/hand_coding_sensitivity.json,
G44/marker_class_rates.json, synthetic.json}. Writes:
    goalperiod-subhypotheses/G44/figures/g44_lexical.pdf, g44_plans.pdf, g44_embedding.pdf
    figures/summary.pdf, figures/summary_obs.pdf (4.3 x 2.6 in), figures/synthetic_validation.pdf (by synthetic.py)
No text from the record is drawn.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h23lib as L  # noqa: E402

HERE = Path(__file__).resolve().parents[1]
FIG, GFIG = HERE / "figures", HERE / "goalperiod-subhypotheses/G44/figures"
D = L.OUT / "G44"
# reference categorical palette (fixed order; color follows the entity)
COL = {"leader": "#2a78d6", "corpus": "#eb6834", "K_same": "#1baf7a", "V_same": "#eda100", "K_field": "#e87ba4",
       "offline": "#4a3aa7", "CTRL": "#8a8984"}
NAME = {"leader": "leader\nlive", "corpus": "corpus\ntargets", "offline": "student\noffline",
        "K_same": "Kimi\nsame win.", "V_same": "village\nsame win.", "K_field": "Kimi\nfield",
        "CTRL": "controls", "leader (hand)": "leader\n(hand-coded)", "leader contexts": "leader's\ncontexts"}
INK, MUTED = "#0b0b0b", "#6f6e69"
plt.rcParams.update({"font.size": 8, "axes.edgecolor": MUTED, "axes.labelcolor": INK, "xtick.color": MUTED,
                     "ytick.color": MUTED, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.titlesize": 8.5, "axes.titleweight": "bold", "legend.frameon": False})


def ci_bars(ax, groups, vals, ylabel, title, ref=None):
    x = np.arange(len(groups))
    for i, g in enumerate(groups):
        m, lo, hi = vals[g]
        ax.bar(i, m, width=0.62, color=COL.get(g, MUTED), edgecolor="white", linewidth=1)
        ax.errorbar(i, m, yerr=[[m - lo], [hi - m]], color=INK, lw=0.9, capsize=2)
    if ref is not None:
        ax.axhline(ref[0], color=MUTED, lw=0.8, ls="--")
        ax.text(len(groups) - 0.5, ref[0], ref[1], ha="right", va="bottom", fontsize=6.5, color=MUTED)
    ax.set_xticks(x, [NAME.get(g, g) for g in groups], fontsize=6.5)
    ax.set(ylabel=ylabel, title=title)
    ax.yaxis.grid(True, color="#e6e5e0", lw=0.6)
    ax.set_axisbelow(True)


def coarse4(profile: dict) -> np.ndarray:
    tot = sum(profile.values()) or 1
    d = sum(profile.get(a, 0) for a in L.DIRECTIVE)
    req = profile.get("REQUEST", 0)
    rep = profile.get("REPORT", 0)
    return np.array([d, req, rep, tot - d - req - rep]) / tot


def main():
    R = json.loads((D / "results.json").read_text())
    V = json.loads((D / "verdicts.json").read_text())
    H = json.loads((D / "hand_coding_sensitivity.json").read_text())
    MC = json.loads((D / "marker_class_rates.json").read_text())
    S = json.loads((L.OUT / "synthetic.json").read_text())
    GFIG.mkdir(parents=True, exist_ok=True)
    FIG.mkdir(exist_ok=True)
    O1 = R["O1"]["means"]
    order = ["corpus", "offline", "leader", "K_same", "V_same", "K_field"]

    # ---------------- lexical
    fig, ax = plt.subplots(1, 3, figsize=(10, 3.1))
    g = ["offline", "leader", "K_same", "V_same", "K_field"]
    ci_bars(ax[0], g, {k: O1[k]["r_corpus"] for k in g}, "per 100 tokens",
            f"Corpus-distinctive n-grams\nleader vs controls p = {V['P1a']['p']:.3f}")
    ci_bars(ax[1], g, {k: O1[k]["c2"] for k in g}, "share of bigrams in corpus",
            f"Corpus bigram copy\nleader vs controls p = {V['P1b']['p']:.2f}",
            ref=(R["O1"]["corpus_loo"]["c2"][0], "corpus self-copy (LOO)"))
    cls = ["agent-address", "punctuation/markup", "content words", "function words"]
    x = np.arange(len(cls))
    ax[2].bar(x - 0.18, [MC["leader"].get(c, 0) for c in cls], 0.34, color=COL["leader"], label="leader")
    ax[2].bar(x + 0.18, [MC["CTRL"].get(c, 0) for c in cls], 0.34, color=COL["CTRL"], label="controls")
    ax[2].set_xticks(x, ["agent\naddress", "punctuation\n/markup", "content\nwords", "function\nwords"], fontsize=6.5)
    ax[2].set(ylabel="per 100 tokens", title="Where the excess comes from")
    ax[2].legend(fontsize=7)
    fig.suptitle("H23 × G44 · phrase level: the leader uses more of the corpus's vocabulary than the room does, "
                 "but copies almost no phrases", fontsize=9)
    fig.tight_layout()
    fig.savefig(GFIG / "g44_lexical.pdf")
    plt.close(fig)

    # ---------------- plans
    P = R["O2"]["profiles"]
    rows = [("corpus", P["corpus"]), ("offline", P["offline"]), ("leader", P["leader"]),
            ("leader (hand)", H["leader"]["hand_profile"]), ("K_same", P["K_same"]), ("V_same", P["V_same"]),
            ("leader contexts", P["leader_ctx"])]
    fig, ax = plt.subplots(1, 3, figsize=(10.5, 3.3), gridspec_kw={"width_ratios": [1.5, 1, 1]})
    cats = ["directive", "request", "report", "other"]
    ccol = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100"]
    for i, (nm, prof) in enumerate(rows):
        v = coarse4({k: int(c) for k, c in prof.items()})
        left = 0
        for j in range(4):
            ax[0].barh(i, v[j], left=left, color=ccol[j], edgecolor="white", linewidth=1.2,
                       label=cats[j] if i == 0 else None)
            left += v[j]
        n = sum(int(c) for c in prof.values())
        ax[0].text(1.01, i, f"n={n}", va="center", fontsize=6.5, color=MUTED)
    ax[0].set_yticks(range(len(rows)), [NAME.get(r[0], r[0]).replace("\n", " ") for r in rows], fontsize=7)
    ax[0].invert_yaxis()
    ax[0].set(xlim=(0, 1.12), xlabel="share of messages (primary plan act)",
              title=f"Plan profiles · JSD(leader, corpus) = {R['O2']['jsd']['leader']:.2f} "
                    f"(corpus self p95 {R['O2']['jsd_corpus_self_n']['p95']:.2f})")
    ax[0].legend(ncol=4, fontsize=6.5, loc="lower center", bbox_to_anchor=(0.45, -0.38))
    ch = R["O2"]["corpus_channel"]
    gg = ["leader", "K_same", "V_same"]
    x = np.arange(len(gg))
    ax[1].bar(x - 0.18, [ch[g]["fine"]["c_ex"] for g in gg], 0.34, color=[COL[g] for g in gg], label="observed")
    ax[1].bar(x + 0.18, [ch[g]["fine"]["perfect_copy_ref"]["c_ex"] for g in gg], 0.34, color="white",
              edgecolor=[COL[g] for g in gg], hatch="///", label="if it copied perfectly")
    ax[1].axhline(0, color=MUTED, lw=0.8)
    ax[1].set_xticks(x, [NAME[g] for g in gg], fontsize=6.5)
    ax[1].set(ylabel="excess plan copy  c − c_null", title="Corpus → speaker channel\n(nearest-scenario pairing)")
    from matplotlib.patches import Patch
    ax[1].legend(handles=[Patch(facecolor="#8a8984", label="observed"),
                          Patch(facecolor="white", edgecolor="#8a8984", hatch="///", label="if it copied perfectly")],
                 fontsize=6.5)
    cv = R["O2"]["conversation"]
    gg = ["corpus", "leader", "V_same", "kimi_period"]
    lab = {"corpus": "corpus\n(snippet→target)", "leader": NAME["leader"], "V_same": NAME["V_same"],
           "kimi_period": "Kimi K2.6\nall #44"}
    colr = {"corpus": COL["corpus"], "leader": COL["leader"], "V_same": COL["V_same"], "kimi_period": COL["K_same"]}
    x = np.arange(len(gg))
    ax[2].bar(x - 0.18, [cv[g]["fine"]["I_copy_ex"] for g in gg], 0.34, color=[colr[g] for g in gg],
              label="I_copy (excess)")
    ax[2].bar(x + 0.18, [cv[g]["fine"]["I_transform_ex"] for g in gg], 0.34, color="white",
              edgecolor=[colr[g] for g in gg], hatch="xx", label="I_transform (excess)")
    ax[2].axhline(0, color=MUTED, lw=0.8)
    ax[2].set_xticks(x, [lab[g] for g in gg], fontsize=6.5)
    ax[2].set(ylabel="bits (minus shuffle null)", title="Context → response channel\n(plan acts, K&CM)")
    from matplotlib.patches import Patch
    ax[2].legend(handles=[Patch(facecolor="#8a8984", label="I_copy (excess)"),
                          Patch(facecolor="white", edgecolor="#8a8984", hatch="xx", label="I_transform (excess)")],
                 fontsize=6.5)
    fig.suptitle("H23 × G44 · plan level: the leader's plans neither copy the corpus nor depend on it; "
                 "they look like the room's", fontsize=9)
    fig.tight_layout()
    fig.savefig(GFIG / "g44_plans.pdf")
    plt.close(fig)

    # ---------------- embedding
    O3 = R["O3"]
    fig, ax = plt.subplots(1, 2, figsize=(7.5, 3.0))
    g = ["offline", "leader", "K_same", "V_same"]
    ci_bars(ax[0], g, {k: O3["d"][k] for k in g}, "cos(z, corpus) − cos(z, Kimi field)",
            f"Closer to corpus than to base?\nleader vs controls p = {V['P3a']['p']:.2f}")
    F = O3["field"]
    labels = ["Kimi split-half"] + [f"agent {a}" for a in F["cross_agent_cos"]]
    vals = [F["kimi_split_half_cos"]] + list(F["cross_agent_cos"].values())
    o = np.argsort(vals)[::-1]
    ax[1].barh(np.arange(len(vals)), np.array(vals)[o],
               color=[COL["K_same"] if labels[i] == "Kimi split-half" else "#c9c8c2" for i in o])
    ax[1].set_yticks(np.arange(len(vals)), [labels[i] for i in o], fontsize=6)
    ax[1].invert_yaxis()
    ax[1].set(xlabel="cos(h_Kimi^A, h^B)", title="Invariance check (exception (b)): fails")
    fig.tight_layout()
    fig.savefig(GFIG / "g44_embedding.pdf")
    plt.close(fig)

    # ---------------- hypothesis-page observable (4.3 x 2.6 in)
    fig, ax = plt.subplots(1, 2, figsize=(4.3, 2.6), gridspec_kw={"width_ratios": [1, 1]})
    g = ["offline", "leader", "K_same", "V_same"]
    short = {"offline": "student\noffline", "leader": "leader\nlive", "K_same": "Kimi\n(base)", "V_same": "village"}
    for i, k in enumerate(g):
        m, lo, hi = O1[k]["r_corpus"]
        ax[0].bar(i, m, 0.62, color=COL[k], edgecolor="white")
        ax[0].errorbar(i, m, yerr=[[m - lo], [hi - m]], color=INK, lw=0.8, capsize=1.5)
    ax[0].set_xticks(range(len(g)), [short[k] for k in g], fontsize=6)
    ax[0].set_title("Vocabulary: corpus markers\nper 100 tokens", fontsize=7)
    ax[0].tick_params(labelsize=6)
    ds = R["O2"]["directive_share"]
    items = [("corpus", ds["corpus"][0], COL["corpus"]), ("student\noffline", ds["offline"][0], COL["offline"]),
             ("leader\n(coder)", ds["leader"][0], COL["leader"]), ("leader\n(hand)", H["leader"]["hand_directive"],
                                                                    COL["leader"]),
             ("controls\n(hand)", H["CTRL_hand_directive"], COL["CTRL"])]
    for i, (nm, v, c) in enumerate(items):
        ax[1].bar(i, v, 0.62, color=c if "hand" not in nm or "leader" not in nm else "white", edgecolor=c,
                  hatch="///" if nm.startswith("leader\n(hand") else None)
    ax[1].set_xticks(range(len(items)), [i[0] for i in items], fontsize=5.5)
    ax[1].set_ylim(0, 1.05)
    ax[1].set_title("Plans: directive share\n(decide/assign/gate/redirect)", fontsize=7)
    ax[1].tick_params(labelsize=6)
    fig.tight_layout(pad=0.4)
    fig.savefig(FIG / "summary_obs.pdf")
    plt.close(fig)

    # ---------------- one-page summary
    fig = plt.figure(figsize=(8.5, 11))
    gs = fig.add_gridspec(4, 3, height_ratios=[0.75, 1, 1, 1.05], hspace=0.75, wspace=0.45, left=0.15, right=0.96, top=0.96, bottom=0.05)
    tx = fig.add_subplot(gs[0, :])
    tx.axis("off")
    t = (
        "H23 · Distilling the village into a fine-tuned leader copies its vocabulary but transforms its plans\n"
        "Exploratory round 1 (G44, non-holdout), 2026-10-03. #45 confirmation written, not run.\n\n"
        "Pipeline (from the record): the deployed leader (kimi-leader-v7-aug-64; agent 28 in #44, agent 30 in #45) is base Kimi K2.6\n"
        "LoRA-fine-tuned on 64 rows: 51 base-Kimi self-distilled replies to 20 synthetic #best scenarios + 13 agent-written rows.\n"
        "No village chat was a training target. 31/64 rows recovered verbatim from the agents' terminals.\n\n"
        f"P1 vocabulary copied: marker rate {V['P1a']['leader']:.1f} vs {V['P1a']['ctrl']:.1f} /100 tok (p={V['P1a']['p']:.3f}) SUPPORTED; "
        f"bigram copy {V['P1b']['leader']:.3f} vs {V['P1b']['ctrl']:.3f} INCONCLUSIVE.\n"
        f"P2a plans not copied: directive share {V['P2a']['directive_leader']:.2f} (hand {H['leader']['hand_directive']:.2f}) vs corpus 1.00 SUPPORTED.\n"
        f"P2b plans transformed: excess plan copy {V['P2b_fine']['c_ex']:.2f} (perfect copy {V['P2b_fine']['perfect_copy_ref']['c_ex']:.2f}), "
        f"I_transform within null → NOT TRANSMITTED.\n"
        f"P3 closer to corpus than base: d {V['P3a']['leader']:.3f} vs controls {V['P3a']['ctrl']:.3f} FAILED; Kimi field invariance FAILED.\n"
        "Rivals: base echo (R1) not rejected; latest-chat echo (R2) fits the plans better than the corpus (JSD 0.15 vs 0.35)."
    )
    tx.text(0, 1, t, va="top", fontsize=7.4, family="DejaVu Sans", color=INK)
    a = fig.add_subplot(gs[1, 0])
    ci_bars(a, ["offline", "leader", "K_same", "V_same"], {k: O1[k]["r_corpus"] for k in ["offline", "leader", "K_same", "V_same"]},
            "per 100 tokens", "Corpus-distinctive n-grams")
    a = fig.add_subplot(gs[1, 1])
    ci_bars(a, ["offline", "leader", "K_same", "V_same"], {k: O1[k]["c2"] for k in ["offline", "leader", "K_same", "V_same"]},
            "share of bigrams", "Corpus bigram copy", ref=(R["O1"]["corpus_loo"]["c2"][0], "corpus LOO"))
    a = fig.add_subplot(gs[1, 2])
    cls = ["agent-address", "punctuation/markup", "content words"]
    x = np.arange(3)
    a.bar(x - 0.18, [MC["leader"].get(c, 0) for c in cls], 0.34, color=COL["leader"], label="leader")
    a.bar(x + 0.18, [MC["CTRL"].get(c, 0) for c in cls], 0.34, color=COL["CTRL"], label="controls")
    a.set_xticks(x, ["address", "markup", "content"], fontsize=6.5)
    a.set_title("Marker classes")
    a.legend(fontsize=6)
    a = fig.add_subplot(gs[2, 0:2])
    for i, (nm, prof) in enumerate(rows):
        v = coarse4({k: int(c) for k, c in prof.items()})
        left = 0
        for j in range(4):
            a.barh(i, v[j], left=left, color=ccol[j], edgecolor="white", linewidth=1, label=cats[j] if i == 0 else None)
            left += v[j]
    a.set_yticks(range(len(rows)), [NAME.get(r[0], r[0]).replace("\n", " ") for r in rows], fontsize=6.5)
    a.invert_yaxis()
    a.set(xlabel="share of messages", title="Plan profiles (primary act)")
    a.legend(ncol=4, fontsize=6, loc="lower center", bbox_to_anchor=(0.5, -0.42))
    a = fig.add_subplot(gs[2, 2])
    gg = ["leader", "K_same", "V_same"]
    x = np.arange(3)
    a.bar(x - 0.18, [ch[g]["fine"]["c_ex"] for g in gg], 0.34, color=[COL[g] for g in gg])
    a.bar(x + 0.18, [ch[g]["fine"]["perfect_copy_ref"]["c_ex"] for g in gg], 0.34, color="white",
          edgecolor=[COL[g] for g in gg], hatch="///")
    a.axhline(0, color=MUTED, lw=0.8)
    a.set_xticks(x, ["leader", "Kimi", "village"], fontsize=6.5)
    a.set_title("Plan copy: observed vs\nperfect-copy (hatched)")
    a = fig.add_subplot(gs[3, 0])
    ci_bars(a, ["offline", "leader", "K_same", "V_same"], {k: O3["d"][k] for k in ["offline", "leader", "K_same", "V_same"]},
            "cos(z,C) − cos(z,K)", "Embedding: corpus vs base")
    a = fig.add_subplot(gs[3, 1])
    for (k, acc), mk in [((10, 0.6), "o"), ((10, 1.0), "^")]:
        for n, ls in [(16, "--"), (70, "-")]:
            r1 = [r for r in S["A"] if r["k"] == k and r["acc"] == acc and r["n"] == n and r["beta"] == 0]
            a.plot([r["alpha"] for r in r1], [r["power_c"] for r in r1], ls, marker=mk, color=COL["leader"], ms=3)
            r2 = [r for r in S["A"] if r["k"] == k and r["acc"] == acc and r["n"] == n and r["alpha"] == 0]
            a.plot([r["beta"] for r in r2], [r["power_I_transform"] for r in r2], ls, marker=mk, color=COL["corpus"], ms=3)
    a.axhline(0.1, color=MUTED, lw=0.7)
    a.set(xlabel="copy α (blue) / transform β (orange)", ylabel="power", ylim=(0, 1),
          title="Synthetic: plan channel power\n(-- n=16, — n=70; ○ coder 0.6, △ perfect)")
    a = fig.add_subplot(gs[3, 2])
    for (nl, nc), ls in [((16, 45), "--"), ((70, 600), "-")]:
        r1 = [r for r in S["C"] if r["n_l"] == nl and r["p0"] == 0.05]
        a.plot([r["ratio"] for r in r1], [r["power"] for r in r1], ls, marker="o", color=COL["leader"], ms=3)
    a.axhline(0.1, color=MUTED, lw=0.7)
    a.axvline(V["P1a"]["leader"] / V["P1a"]["ctrl"], color=COL["corpus"], lw=0.8, ls=":")
    a.set(xlabel="leader/control marker ratio", ylabel="power", ylim=(0, 1),
          title="Synthetic: marker test power\n(dotted: observed ratio)")
    fig.savefig(FIG / "summary.pdf")
    plt.close(fig)
    print("figures written")


if __name__ == "__main__":
    main()
