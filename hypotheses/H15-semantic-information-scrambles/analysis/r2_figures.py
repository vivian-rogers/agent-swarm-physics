"""H15 round 2 summary figure (figures/r2/F_r2.pdf, ~4.3 x 2.4 in), from r2/results.json only.

(a) Ratio of ratios RR = exp(b class x F) with agent-day cluster bootstrap 95% CIs (pooled NE41 fit): first-read
    classes (R2, output in calls 3-20), the concentration classes (calls 6-20) and the trail classes (R1b, calls 1-20).
(b) R3: window-swap excess recall of note terms in the next segment's commands, per period, all terms and novel terms,
    with the synthetic performative level (0) and the enacted q = 0.10 level.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import r2lib as L  # noqa: E402

import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

FIG = L.ROOT / "hypotheses/H15-semantic-information-scrambles/figures/r2"
INK, MUTED, ACC = "#333333", "#9a9a9a", "#2166ac"
plt.rcParams.update({"font.size": 7, "axes.spines.top": False, "axes.spines.right": False, "axes.titlesize": 7.5,
                     "axes.labelsize": 7})


def main():
    r = json.loads((L.DATA / "results.json").read_text())
    syn = json.loads((L.DATA / "synthetic.json").read_text())
    fig, (a, b) = plt.subplots(1, 2, figsize=(4.6, 2.5), gridspec_kw={"width_ratios": [1.15, 1]})
    R2, C, T = r["R2"]["NE41"], r["R2"]["concentration"], r["R1b"]
    rows = [("re-open last files (L)", R2["LxF"], INK), ("new messages (M)", R2["MxF"], INK),
            ("notes / search (Gp)", R2["GpxF"], MUTED), ("note names repo (Gn)", R2["GnxF"], INK),
            ("none of L, M, Gp", r["R2"]["proxy_none"], INK),
            ("L or M, calls 1–2", C["U12xF"], INK), ("L or M, calls 3–5", C["U35xF"], MUTED),
            ("trail T1 (24 h)", T["NE41"]["T1xF"], INK), ("trail T2 (24 h)", T["NE41"]["T2xF"], INK),
            ("trail ≥ 3 days (7 d)", T["secondary_days7"]["D2xF"], INK)]
    for i, (lab, d, c) in enumerate(rows):
        a.errorbar([d["RR"]], [i], xerr=[[d["RR"] - d["lo_boot"]], [d["hi_boot"] - d["RR"]]], fmt="o", ms=3.2,
                   color=c, capsize=1.8, lw=1)
    for y in (4.5, 6.5):
        a.axhline(y, color="#dddddd", lw=0.5)
    a.axvline(1, color="k", lw=0.5)
    a.set_yticks(range(len(rows)), [x[0] for x in rows], fontsize=6)
    a.invert_yaxis()
    a.set_xscale("log")
    a.set_xticks([0.7, 1, 1.4], ["0.7", "1", "1.4"])
    a.set_xlim(0.65, 1.7)
    a.set_xlabel("RR: output after erasure vs pseudo-erasure")
    a.set_title(f"(a) what softens the dip (first reads: {C['dip_share_U12']['share'] * 100:.0f}% of it)", fontsize=7)

    per = r["R3"]["per"]
    ps = [p for p in L.PERIODS if p in per and np.isfinite(per[p]["E_s"]["est"])]
    x = np.arange(len(ps))
    for k, c, lab, off in (("E_s", INK, "all note terms", -0.12), ("Enov_s", ACC, "novel terms", 0.12)):
        est = np.array([per[p][k]["est"] for p in ps])
        lo = np.array([per[p][k]["lo"] for p in ps])
        hi = np.array([per[p][k]["hi"] for p in ps])
        b.errorbar(x + off, est, yerr=[est - lo, hi - est], fmt="o", ms=2.8, color=c, capsize=1.2, lw=0.8, label=lab)
    b.axhline(0, color="k", lw=0.5)
    q10 = syn["R3"]["q0.10"]["E_s"]
    b.axhline(q10, color=MUTED, lw=0.6, ls="--", label="10% enacted (synthetic)")
    b.set_xticks(x, [p[1:] for p in ps], fontsize=6)
    b.set_xlabel("goal period")
    b.set_ylabel("excess recall (window swap)")
    b.set_title("(b) note terms in later commands")
    b.set_ylim(-0.01, 0.17)
    b.legend(frameon=False, fontsize=5.6, loc="upper left", handlelength=1)
    fig.tight_layout(pad=0.4, w_pad=0.8)
    FIG.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIG / "F_r2.pdf", bbox_inches="tight", pad_inches=0.02)
    fig.savefig(FIG / "F_r2.png", dpi=200, bbox_inches="tight", pad_inches=0.02)
    print("wrote", FIG / "F_r2.pdf")


if __name__ == "__main__":
    main()
