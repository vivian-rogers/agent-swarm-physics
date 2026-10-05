"""Round-2 summary figure (column width): (a) content read-out jump by hop (matched age); (b) relay event-study
profile, real vs the length-dependent null world (diagnosis), with the post hoc relay RD; (c) regime-I kernel on
logged-start recipients: talk vs the chat-mode channel. Writes figures/r2_summary_col.pdf."""
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
import r2lib as R2  # noqa: E402

ROOT = HERE.parents[2]
OUT = ROOT / "data/processed/H50-field-vs-coupling-transfer-lag/r2"
FIG = ROOT / "hypotheses/H50-field-vs-coupling-transfer-lag/figures"
BLUE, ORANGE, AQUA, GRAY, INK = "#2a78d6", "#eb6834", "#1baf7a", "#8a8984", "#0b0b0b"


def style(ax):
    ax.tick_params(labelsize=6)
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    ax.axhline(0, color=GRAY, lw=0.6, zorder=0)


def main():
    fig, axs = plt.subplots(3, 1, figsize=(3.4, 5.0))
    # (a) content
    c = json.loads((OUT / "content_summary.json").read_text())["pooled"]
    ax = axs[0]
    hops = np.array([1, 2, 3])
    for lab, sub, reg, col, off, ls in (("III named", "named", "III", ORANGE, -0.15, "-"), ("III unnamed", "unnamed", "III", BLUE, 0.0, "-"),
                                        ("I all", "all", "I", GRAY, 0.15, "--")):
        d = c[f"bge|primary|{sub}|{reg}"]
        m = np.array([d[f"J{h}"] for h in hops])
        s = np.array([d[f"J{h}_se"] for h in hops]) * 1.96
        if reg == "I":
            m, s = m[:2], s[:2]
        x = hops[:len(m)] + off
        ax.errorbar(x, m, yerr=s, fmt="o", ms=3, color=col, lw=1, capsize=0, ls=ls, label=lab)
        ax.plot(x, m, color=col, lw=1, ls=ls)
    ax.set_xticks(hops)
    ax.set_xlabel("hop of the recipient's statement (1 = read-out call)", fontsize=6)
    ax.set_ylabel("content jump $J^c_h$ (cos)", fontsize=6)
    ax.set_ylim(-0.04, 0.12)
    ax.legend(fontsize=5.5, frameon=False, loc="upper right", ncol=3)
    ax.set_title("(a) content jump by hop (matched age)", fontsize=6.5, loc="left")
    style(ax)
    # (b) relay event study: real vs length-dependent null (regime III)
    ax = axs[1]
    rs = json.loads((OUT / "relay_summary.json").read_text())["III"]
    ev = [-3, -2, -1, 0, 1, 2]
    m = [rs[f"treated_g{e}"][0] if e != -1 else 0.0 for e in ev]
    s = [1.96 * rs[f"treated_g{e}"][1] if e != -1 else 0.0 for e in ev]
    ax.errorbar(np.array(ev) - 0.08, m, yerr=s, fmt="o-", ms=3, color=BLUE, lw=1, capsize=0, label="real, regime III")
    syn = json.loads((OUT / "synthetic_relay_rd.json").read_text())
    w = []
    for e in (-3, -2, 0, 1):
        pass
    gm2 = np.mean([np.mean([x["gm2"][0] for x in syn[f"{u}|W0L"]]) for u in ("51b", "38a", "51c")])
    g0 = np.mean([np.mean([x["G"][0] for x in syn[f"{u}|W0L"]]) for u in ("51b", "38a", "51c")])
    gp1 = np.mean([np.mean([x["gp1"][0] for x in syn[f"{u}|W0L"]]) for u in ("51b", "38a", "51c")])
    ax.plot([-2.0 + 0.08, -1 + 0.08, 0 + 0.08, 1 + 0.08], [gm2, 0, g0, gp1], "s--", ms=3, color=GRAY, lw=1,
            label="null world, talk tied to call length")
    rd = json.loads((OUT / "relay_rd_summary.json").read_text())["III"]
    ax.text(0.52, 0.42, f"post hoc relay RD (C-hop ≥ 2):\nnamed {rd['rd2_named']['J']:.3f} ± {1.96 * rd['rd2_named']['se']:.3f},"
            f"\nunnamed {rd['rd2_unnamed']['J']:.3f} ± {1.96 * rd['rd2_unnamed']['se']:.3f}", transform=ax.transAxes, fontsize=5.5, color=INK)
    ax.set_xlabel("event time e = C-hop − relay-read hop (e = −1 reference)", fontsize=6)
    ax.set_ylabel("Δ P(talk)", fontsize=6)
    ax.legend(fontsize=5.5, frameon=False, loc="upper right")
    ax.set_ylim(-0.004, 0.055)
    ax.set_title("(b) relay event study (regime III)", fontsize=6.5, loc="left")
    style(ax)
    # (c) regime-I kernel, logged-start recipients
    ax = axs[2]
    k = json.loads((OUT / "kernel_I_summary.json").read_text())
    h = np.arange(1, 7)
    for lab, key, col, off in (("talk, logged-start recipients", "logged", BLUE, -0.12), ("chat-mode call, all recipients", "mode_all", ORANGE, 0.0),
                               ("talk, recipients in chat mode", "all_chat", AQUA, 0.12)):
        m = np.array([k[key][f"k{i}"][0] for i in h])
        s = np.array([k[key][f"k{i}"][1] for i in h]) * 1.96
        ax.errorbar(h + off, m, yerr=s, fmt="o-", ms=3, color=col, lw=1, capsize=0, label=lab)
    ax.set_xlabel("hop after the read-out (cumulative kernel)", fontsize=6)
    ax.set_ylabel("Δ P", fontsize=6)
    ax.set_ylim(-0.02, 0.36)
    ax.legend(fontsize=5.5, frameon=False, loc="upper left", ncol=1, bbox_to_anchor=(0.0, 1.02))
    ax.set_title("(c) regime-I kernel", fontsize=6.5, loc="left")
    style(ax)
    fig.tight_layout(h_pad=0.6)
    FIG.mkdir(exist_ok=True)
    fig.savefig(FIG / "r2_summary_col.pdf")
    fig.savefig("/private/tmp/claude-501/-Users-wrogers-Documents-school-fun-agenttesting/015f2aa2-05c1-4a7e-ba6c-25bf6c9d1344/scratchpad/r2.png", dpi=160)


if __name__ == "__main__":
    main()
