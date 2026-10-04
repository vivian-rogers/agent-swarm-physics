"""H116 figures: figures/summary_obs.pdf (event and re-election steps vs placebos) and figures/synthetic.pdf (power).

  uv run python hypotheses/H116-election-coupling-step/analysis/figures.py
"""
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
import h116lib as L  # noqa: E402

FIG = HERE.parent / "figures"
BLUE, RED, GREY = "#2a78d6", "#d03b3b", "#85847e"


def main():
    FIG.mkdir(exist_ok=True)
    r = json.loads((L.DATA / "G26" / "results.json").read_text())
    ph = json.loads((L.DATA / "G26" / "posthoc_n2.json").read_text())
    ev = r["event"]
    fig, ax = plt.subplots(1, 2, figsize=(7.0, 2.5), gridspec_kw={"width_ratios": [1.3, 1]})
    a = ax[0]
    rng = np.random.default_rng(0)
    tp = [p["dJout"] for p in r["time_placebos"]]
    ap = list(ev["agent_placebos"].values())
    rp = [p["dJout"] for p in ph["placebos"]]
    cols = [("time placebos\n(event offsets)", tp, GREY), ("agent placebos\n(same T*)", ap, GREY),
            ("time placebos\n(re-election offsets)", rp, GREY)]
    for k, (lab, v, c) in enumerate(cols):
        a.plot(k + rng.uniform(-0.15, 0.15, len(v)), v, "o", color=c, ms=3.5, alpha=0.8)
    a.plot([0, 1], [ev["coef"]["dJout"]] * 2, "D", color=BLUE, ms=8, label="01-05 result (N1)")
    a.plot([2], [ph["obs"]], "D", color=RED, ms=8, label="01-09 re-election (N2)")
    a.axhline(0, color=GREY, lw=0.6)
    a.axhline(0.05, color=BLUE, lw=0.8, ls=":")
    a.set_xticks(range(3))
    a.set_xticklabels([c[0] for c in cols], fontsize=7)
    a.set_ylabel(r"$\Delta J_{out}$ (Ising, $\lambda=4$)")
    a.set_title("winner's out-coupling step vs placebos", fontsize=9)
    a.legend(fontsize=7, frameon=False, loc="upper left")
    a = ax[1]
    labs = ["G26 result\n(magnitude)", "G26 re-election\n(magnitude)", "G12 judges\n(role step)", "G35 leads\n(role step)"]
    est = [ev["magnitude"]["dJout"]["est"], ph["magnitude"]["dJout"]["est"]]
    se = [ev["magnitude"]["dJout"]["se"], ph["magnitude"]["dJout"]["se"]]
    for g in ("G12", "G35"):
        rep = json.loads((L.DATA / g / "replication.json").read_text())
        est.append(rep["obs"]["dOut"])
        se.append(rep["obs"]["se_dOut"])
    a.errorbar(range(4), est, yerr=1.96 * np.array(se), fmt="o", color=BLUE, ecolor=GREY, capsize=3)
    a.axhline(0, color=GREY, lw=0.6)
    a.set_xticks(range(4))
    a.set_xticklabels(labs, fontsize=6.5)
    a.set_ylabel("out-coupling step (Ising)")
    a.set_title("steps with 95% intervals", fontsize=9)
    fig.tight_layout()
    fig.savefig(FIG / "summary_obs.pdf")
    syn = json.loads((L.DATA / "synthetic" / "synthetic.json").read_text())
    raw = json.loads((L.DATA / "synthetic" / "synthetic_raw.json").read_text())
    fig, ax = plt.subplots(1, 2, figsize=(7.0, 2.2))
    a = ax[0]
    D = syn["deltas"]
    z = np.array([x["event"]["0.0_4.0"]["dJout"] for x in raw])
    q = np.percentile(z, 95)
    p_time, p_comb = [], []
    for d in D:
        dt_, dc_ = [], []
        for x in raw:
            e = x["event"][f"{d}_4.0"]["dJout"]
            thr = np.nanpercentile(np.array(x["placebo"]["4.0"], float), 95)
            dt_.append(e >= 0.05 and e > thr)
            dc_.append(e >= 0.05 and e > thr and e > q)
        p_time.append(np.mean(dt_))
        p_comb.append(np.mean(dc_))
    a.plot(D, p_time, "s--", color=GREY, label="time placebos only")
    a.plot(D, p_comb, "o-", color=BLUE, label="with skeleton null (A1)")
    a.axvline(0.05, color=RED, lw=0.8, ls=":")
    a.axhline(0.05, color=GREY, lw=0.6)
    a.set_xlabel(r"planted step $\Delta$ (Ising)")
    a.set_ylabel("detection rate (50 worlds)")
    a.legend(fontsize=7, frameon=False)
    a = ax[1]
    m = [np.mean([x["event"][f"{d}_4.0"]["dJout"] for x in raw]) for d in D]
    m1 = [np.mean([x["event"][f"{d}_1.0"]["dJout"] for x in raw]) for d in D]
    a.plot(D, D, color=GREY, lw=0.8, ls=":")
    a.plot(D, m, "o-", color=BLUE, label=r"$\lambda=4$")
    a.plot(D, m1, "s-", color="#fab219", label=r"$\lambda=1$")
    a.set_xlabel(r"planted step $\Delta$")
    a.set_ylabel("mean estimate")
    a.legend(fontsize=7, frameon=False)
    fig.tight_layout()
    fig.savefig(FIG / "synthetic.pdf")
    pf = HERE.parent / "goalperiod-subhypotheses" / "G26" / "figures"
    pf.mkdir(parents=True, exist_ok=True)
    fig, a = plt.subplots(figsize=(3.4, 2.4))
    a.hist(tp, bins=10, color=GREY, alpha=0.7, label="time placebos")
    a.axvline(ev["coef"]["dJout"], color=BLUE, lw=2, label="result")
    a.axvline(ev["skeleton_q95_dJout"], color="k", lw=1, ls="--", label="skeleton q95")
    a.set_xlabel(r"$\Delta J_{out}$ ($\lambda=4$)")
    a.legend(fontsize=7, frameon=False)
    fig.tight_layout()
    fig.savefig(pf / "event_vs_placebos.pdf")


if __name__ == "__main__":
    main()
