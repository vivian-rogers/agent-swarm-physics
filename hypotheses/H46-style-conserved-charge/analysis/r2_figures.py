"""H46 round 2 figures: figures/r2_obs.pdf (conservation by channel; shape of the context-held state) and
figures/r2_obsb.pdf (identity across goal switches; self-pull within vs across an erasure, per lab)."""
from __future__ import annotations
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h46lib as L  # noqa: E402
import r2lib as R  # noqa: E402

import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

FIG = L.ROOT / "hypotheses/H46-style-conserved-charge/figures"
C = {"tc": "#2a78d6", "gp": "#eb6834", "fw": "#1baf7a", "content": "#eda100", "fw_tc": "#e87ba4"}
NAME = {"tc": "style (round 1)", "gp": "style, genre + position removed", "fw": "function words",
        "content": "content (bge)", "fw_tc": "function words + style"}
plt.rcParams.update({"font.size": 7, "axes.spines.top": False, "axes.spines.right": False})


def load():
    return [json.loads((R.R2 / f).read_text()) for f in ("r1.json", "r2.json", "r3.json", "posthoc.json", "synthetic.json")]


def panel_T(ax, r1, r3):
    groups = [("goal switches\n(24)", {"tc": r1["goal"]["tests"]["goal"]["tc"], "gp": r1["goal"]["tests"]["goal"]["gp"],
                                       "fw": r3["classes"]["tests"]["goal"]["fw"],
                                       "content": r1["goal"]["tests"]["goal"]["content"]}),
              ("forced erasure\n(NE41)", {"tc": r1["NE41"]["tc"]["forced"], "gp": r1["NE41"]["gp"]["forced"],
                                          "fw": r3["NE41"]["fw"]["forced"], "content": r1["NE41"]["content_bge"]["forced"]}),
              ("voluntary\nconsolidation", {"tc": r1["NE41"]["tc"]["voluntary"], "gp": r1["NE41"]["gp"]["voluntary"],
                                            "fw": r3["NE41"]["fw"]["voluntary"],
                                            "content": r1["NE41"]["content_bge"]["voluntary"]})]
    ax.axvspan(0.45, 0.55, color="0.92", zorder=0)
    ax.axvline(0.5, color="0.6", lw=0.6)
    for gi, (gname, d) in enumerate(groups):
        for k, (ch, t) in enumerate(d.items()):
            y = gi + (k - 1.5) * 0.18
            ax.errorbar(t["T"], y, xerr=[[t["T"] - t["lo"]], [t["hi"] - t["T"]]], fmt="o", ms=4.5, color=C[ch],
                        mec="white", mew=0.6, capsize=1.5, lw=1, label=NAME[ch] if gi == 0 else None)
    ax.set_yticks(range(len(groups)))
    ax.set_yticklabels([g[0] for g in groups])
    ax.invert_yaxis()
    ax.set_xlim(0.4, 0.95)
    ax.set_xlabel("boundary percentile T vs the agent's own placebo (½ = no move)")
    ax.legend(fontsize=6, frameon=False, loc="lower right")


def panel_shape(ax, ph):
    real = ph["PH_R2a"]["dC_by_lag"]
    ls = sorted(int(k) for k in real)
    v = np.array([real[str(l)][0] for l in ls])
    lo = np.array([real[str(l)][1][0] for l in ls])
    hi = np.array([real[str(l)][1][1] for l in ls])
    ax.fill_between(ls, lo, hi, color=C["gp"], alpha=0.18, lw=0)
    ax.plot(ls, v, "o-", color=C["gp"], ms=4, lw=2, label="real (style, genre + position removed)")
    ref = ph["PH_R2a"]["synthetic_reference"]
    for scen, lab, mk in (("SJ", "synthetic: offset held per segment", "s"), ("S1b", "synthetic: OU drift from reset, φ 0.9", "^")):
        r = ref[scen]["dC_by_lag"]
        rv = np.array([r[str(l)] for l in ls])
        ax.plot(ls, rv * v[0] / rv[0], mk + "--", color="0.45", ms=3.5, lw=1, label=lab + " (scaled to lag 1)")
    ax.axhline(0, color="0.6", lw=0.6)
    ax.set_xlabel("message lag l (same agent, same day)")
    ax.set_ylabel("ΔC(l): cross-product within minus across\na forced erasure (gap-matched)")
    ax.legend(fontsize=5.5, frameon=False, loc="upper left")
    ax.set_ylim(-0.2, 2.2)


def panel_fp(ax, r3):
    fp = r3["classes"]["fingerprint"]
    order = ["content", "tc", "fw", "fw_tc"]
    rng = np.random.default_rng(0)
    for k, ch in enumerate(order):
        vals = np.array(list(fp[ch]["per_boundary"].values()))
        ax.scatter(k + rng.uniform(-0.12, 0.12, len(vals)), vals, s=9, color=C[ch], alpha=0.75, lw=0)
        ax.plot([k - 0.25, k + 0.25], [vals.mean()] * 2, color="k", lw=1.5)
        ax.text(k, 1.04, f"{vals.mean():.2f}", ha="center", fontsize=6)
    ax.axhline(fp["tc"]["chance"], color="0.6", lw=0.8, ls=":")
    ax.text(3.45, fp["tc"]["chance"] + 0.02, "chance", fontsize=5.5, color="0.4", ha="right")
    ax.set_xticks(range(len(order)))
    ax.set_xticklabels(["content", "style", "function\nwords", "function words\n+ style"])
    ax.set_ylim(0, 1.1)
    ax.set_ylabel("identity accuracy across a goal switch\n(train before, test after; balanced)")


def panel_pull(ax, r2):
    p = r2["gp"]
    rows = [("pooled", p["pooled"]["pull"])] + [(k, v["pull"]) for k, v in p["labs"].items()]
    for i, (name, d) in enumerate(rows):
        for k, (key, col, lab) in enumerate((("rho_within", C["gp"], "previous messages in context"),
                                             ("rho_forced", "0.45", "previous messages erased (forced)"))):
            ci = d[key + "_ci"]
            ax.errorbar(i + (k - 0.5) * 0.25, d[key], yerr=[[d[key] - ci[0]], [ci[1] - d[key]]], fmt="o", ms=4,
                        color=col, mec="white", mew=0.5, capsize=1.5, lw=1, label=lab if i == 0 else None)
    ax.set_xticks(range(len(rows)))
    ax.set_xticklabels([f"{n}\n({r2['gp']['labs'][n]['n_agents']})" if n in r2["gp"]["labs"] else n for n, _ in rows],
                       fontsize=6)
    ax.axhline(0, color="0.6", lw=0.6)
    ax.set_ylabel("pull ρ toward the agent's own\nlast ≤ 3 messages")
    ax.legend(fontsize=5.5, frameon=False, loc="upper left")
    ax.set_ylim(-0.05, 0.75)


def main():
    r1, r2, r3, ph, _ = load()
    fig, ax = plt.subplots(1, 2, figsize=(7.0, 2.6), gridspec_kw={"width_ratios": [1.15, 1]})
    panel_T(ax[0], r1, r3)
    panel_shape(ax[1], ph)
    ax[0].set_title("(a) what moves at boundaries", fontsize=7, loc="left")
    ax[1].set_title("(b) context-held state: flat in lag, no OU decay", fontsize=7, loc="left")
    fig.tight_layout()
    for ext in ("pdf", "png"):
        fig.savefig(FIG / f"r2_obs.{ext}", dpi=200)
    fig, ax = plt.subplots(1, 2, figsize=(7.0, 2.6))
    panel_fp(ax[0], r3)
    panel_pull(ax[1], r2)
    ax[0].set_title("(a) identity across 24 goal switches", fontsize=7, loc="left")
    ax[1].set_title("(b) self-pull, in context vs erased (agents)", fontsize=7, loc="left")
    fig.tight_layout()
    for ext in ("pdf", "png"):
        fig.savefig(FIG / f"r2_obsb.{ext}", dpi=200)


if __name__ == "__main__":
    main()
