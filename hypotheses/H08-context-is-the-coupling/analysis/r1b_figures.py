"""H08 round-1b summary figures (same style as figures.py; reads only round-1b JSON outputs).

  uv run python hypotheses/H08-context-is-the-coupling/analysis/r1b_figures.py

figures/r1b_summary_obs.pdf  (page 1): addressing excess by turn offset on the context ledger, clean recipients.
figures/r1b_summary_obs2.pdf (page 2): (a) #51 nudge kernel aligned on the kick vs on the target's receiving call
                                       (H04 round 1b); (b) NE41 forced-erasure effect on the reply coupling.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from figures import AQUA, BLUE, GRID, INK, INK2, MUTED, ORANGE, ALL, c9_curve, style  # noqa: E402
from figures import plt, np, OUT, FIG, PERIODS, gname, ROOT  # noqa: E402

R1B = OUT / "r1b"


def main():
    plt.rcParams.update({"font.size": 6})
    fig, ax = plt.subplots(figsize=(3.45, 1.7), dpi=200)
    offs = np.arange(-2, 4)
    r3, r1, a3 = [], [], []
    for g in ALL:
        p = R1B / gname(g) / "c9.json"
        if not p.exists():
            continue
        d = json.loads(p.read_text())
        c = c9_curve(d, "posthoc_clean", "addr")
        ca = c9_curve(d, "posthoc_clean", "auth")
        if c is None:
            continue
        reg3 = PERIODS[g]["regime"] in ("III", "II/III")
        (r3 if reg3 else r1).append(100 * c[0])
        if ca is not None:
            a3.append(100 * ca[0])
        ax.plot(offs, 100 * c[0], color=BLUE if reg3 else ORANGE, lw=0.5, alpha=0.35)
    ax.plot(offs, np.median(r3, 0), color=BLUE, lw=1.8, marker="o", ms=3, mec="white", mew=0.6, label=f"regime III, mention ({len(r3)})")
    ax.plot(offs, np.median(r1, 0), color=ORANGE, lw=1.8, marker="o", ms=3, mec="white", mew=0.6, label=f"regimes I–II, mention ({len(r1)})")
    ax.plot(offs, np.median(a3, 0), color=AQUA, lw=1.3, ls=(0, (3, 1.5)), label=f"all, reply author ({len(a3)})")
    ax.axvspan(-2.4, 0.5, color="#f1f0ec", lw=0, zorder=0)
    ax.text(-0.95, 2.45, "model call began\nbefore the message", ha="center", va="top", fontsize=5.5, color=MUTED)
    ax.axhline(0, color=INK2, lw=0.5)
    ax.set_xticks(offs); ax.set_xlim(-2.4, 3.4); ax.set_ylim(-0.4, 2.6)
    ax.set_xlabel("recipient's call offset (0 = in flight, 1 = the call that received the message)")
    ax.set_ylabel("excess P(responds to sender), pp")
    ax.legend(loc="upper right", fontsize=5)
    style(ax)
    fig.tight_layout(pad=0.3)
    fig.savefig(FIG / "r1b_summary_obs.pdf")
    plt.close(fig)

    fig, axs = plt.subplots(1, 2, figsize=(3.45, 1.95), dpi=200, gridspec_kw={"width_ratios": [1.25, 1]})
    ax = axs[0]
    h4 = json.loads((ROOT / "data/processed/H04-reversible-forcing/r1b/G51.json").read_text())
    tau = np.arange(-30, 61)
    m = (tau >= -5) & (tau <= 30)
    gk = np.array([np.nan if x is None else x for x in h4["G"]["nudge_target_all"]["G"]], float)
    gr = np.array([np.nan if x is None else x for x in h4["G"]["nudge_target_readout_aligned"]["G"]], float)
    ax.plot(tau[m], gk[m], color=BLUE, lw=1.3, label="aligned on the nudge")
    ax.plot(tau[m], gr[m], color=ORANGE, lw=1.3, label="aligned on the receiving call")
    ax.axhline(0, color=INK2, lw=0.5); ax.axvline(0, color=MUTED, lw=0.5)
    ax.set_xlabel("minutes"); ax.set_ylabel("excess P(active)")
    ax.set_title("(a) #51 nudge → target", loc="left", fontsize=6.2)
    ax.legend(loc="upper right", fontsize=5, handlelength=1.4)
    style(ax)
    ax = axs[1]
    n41 = json.loads((R1B / "ne41_pooled.json").read_text())
    gs = list(n41["periods"].keys())
    for i, g in enumerate(gs):
        b = n41["periods"][g]["auth"].get("beta", {}).get("erased_F")
        if b:
            ax.plot([100 * b[1], 100 * b[2]], [i, i], color=BLUE, lw=1.1)
            ax.plot(100 * b[0], i, "o", color=BLUE, ms=2.6, mec="white", mew=0.4)
    pz = n41["pooled"]["auth"]["erased_F"]
    ax.plot([100 * (pz["mu"] - 1.96 * pz["se"]), 100 * (pz["mu"] + 1.96 * pz["se"])], [len(gs), len(gs)], color=INK, lw=1.8)
    ax.plot(100 * pz["mu"], len(gs), "D", color=INK, ms=3)
    ax.axvline(0, color=INK2, lw=0.5)
    ax.set_yticks(list(range(len(gs))) + [len(gs)]); ax.set_yticklabels([g.replace("G", "#") for g in gs] + ["pooled"], fontsize=5)
    ax.set_xlabel("Δ P(reply to old sender), pp"); ax.set_xlim(-14, 4)
    ax.set_title("(b) NE41 forced erasure", loc="left", fontsize=6.2)
    style(ax); ax.grid(axis="x", color=GRID, lw=0.4)
    fig.tight_layout(pad=0.3, w_pad=0.6)
    fig.savefig(FIG / "r1b_summary_obs2.pdf")
    plt.close(fig)


if __name__ == "__main__":
    main()
