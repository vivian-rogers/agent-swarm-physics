"""H132 summary: figure, per_period_estimates rows (G12 = unit 12a), compact results table.

    uv run python hypotheses/H132-debate-limit-cycle/analysis/summarize.py
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
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "infra/shared"))
RES = ROOT / "data/processed/H132-debate-limit-cycle/results"
SYN = ROOT / "data/processed/H132-debate-limit-cycle/synthetic/summary.json"
FIG = HERE.parent / "figures"


def figure(R, S):
    fig, ax = plt.subplots(1, 2, figsize=(7.0, 2.6))
    keys = ["bge_small|masked", "gte_modernbert|masked", "bge_small|unmasked", "gte_modernbert|unmasked"]
    lab = ["bge m", "gte m", "bge u", "gte u"]
    for j, (st, col) in enumerate((("rho1", "#2a78d6"), ("rho2", "#86b6ef"), ("Lam", "#d03b3b"))):
        for i, k in enumerate(keys):
            d = R[k]["deb"][st]
            x = i + (j - 1) * 0.22
            ax[0].plot([x, x], [d["q05"], d["q95"]], color="#bbbbbb", lw=4, solid_capstyle="butt")
            ax[0].plot(x, d["obs"], "o", color=col, ms=4, label=st if i == 0 else None)
    ax[0].axhline(0, color="k", lw=0.5)
    ax[0].set_xticks(range(4)); ax[0].set_xticklabels(lab, fontsize=7)
    ax[0].set_ylabel("turn correlation (team-centred)"); ax[0].legend(fontsize=6, frameon=False, ncol=3)
    ax[0].set_title("G12 debates: observed vs shuffle 5-95% (grey)", fontsize=8)
    ws = ["W0_speaker_only", "W1_cycle_k0.3_s1", "W1_cycle_k0.6_s1", "W1_cycle_k0.6_s0.5", "W2_drift", "W3_directed_k0.6",
          "W4_ramp", "W5_rotation_k0.6"]
    wl = ["W0", "cyc .3", "cyc .6", "cyc .6/.5", "drift", "directed", "ramp", "rotation"]
    ax[1].bar(np.arange(len(ws)) - 0.2, [S[w]["rate_Lam"] for w in ws], 0.4, color="#d03b3b", label="Λ test")
    ax[1].bar(np.arange(len(ws)) + 0.2, [S[w]["rate_L"] for w in ws], 0.4, color="#2a78d6", label="L test")
    ax[1].axhline(0.05, color="k", lw=0.5, ls=":")
    ax[1].set_xticks(range(len(ws))); ax[1].set_xticklabels(wl, fontsize=6, rotation=45)
    ax[1].set_ylabel("rejection rate"); ax[1].legend(fontsize=6, frameon=False)
    ax[1].set_title("synthetic on the real turn skeleton (100 reps)", fontsize=8)
    fig.tight_layout()
    FIG.mkdir(exist_ok=True)
    fig.savefig(FIG / "summary_obs_col.pdf"); fig.savefig(FIG / "summary_obs_col.png", dpi=150)


def estimates(R):
    import estimates as E
    rows = []
    for k, r in R.items():
        model, src = k.split("|")
        ch = f"content:{model}:{src}:issue-axis"
        base = dict(period_unit="12a", goal_no=12, channel=ch, n=float(r["deb"]["obs"]["n1"]), n_kind="turn pairs",
                    ci_kind="percentile", ci_level=0.90, source="data/processed/H132-debate-limit-cycle/results/results.json",
                    null="turn-shuffled within debate x phase x team (5000)")
        for st, name in (("rho1", "H132 lag-1 turn correlation rho1 (team-centred issue projection)"),
                         ("rho2", "H132 lag-2 turn correlation rho2"), ("Lam", "H132 turn alternation Lambda = rho2 - rho1"),
                         ("A", "H132 cycle antisymmetry A_gamma"), ("L", "H132 issue-topic cycle area L"),
                         ("rho1_vec", "H132 full-vector lag-1 turn correlation (topic echo)")):
            d = r["deb"][st]
            rows.append(base | dict(statistic=name, estimate=d["obs"], ci_lo=d["q05"], ci_hi=d["q95"], role="replication",
                                    method="pooled over 10 debates; CI = shuffle-null 5-95% band (not a CI of the estimate)",
                                    notes=f"p_hi {d['p_hi']:.4f} p_lo {d['p_lo']:.4f}"))
        d = r["post"]["Lam"]
        rows.append(base | dict(statistic="H132 N1 post-verdict turn alternation Lambda_post", estimate=d["obs"], ci_lo=d["q05"],
                                ci_hi=d["q95"], role="native", method="post phase (10 min after verdict)",
                                n=float(r["post"]["obs"]["n1"])))
        d = r["deb"]["dRho_vis"]
        rows.append(base | dict(statistic="H132 N2 read-gated difference rho1(visible) - rho1(in flight)", estimate=d["obs"],
                                ci_lo=d["q05"], ci_hi=d["q95"], role="native", method="ledger visibility of the previous turn"))
        m = r["msg"]
        rows.append(base | dict(statistic="H132 N3 within-pair contrast opponents - teammates (message level)",
                                estimate=m["N3_contrast"]["obs"], ci_lo=None, ci_hi=None, ci_kind="none", role="native",
                                n=float(m["obs"]["N3_pairs"]), n_kind="agent pairs", method="sign-flip over pairs",
                                notes=f"p_lo {m['N3_contrast']['p_lo']:.3f}"))
        rows.append(base | dict(statistic="H132 message-level same-team lag-1 correlation", estimate=m["rho_same"]["obs"],
                                ci_lo=None, ci_hi=None, ci_kind="none", role="replication", n=float(m["obs"]["n_same"]),
                                n_kind="message pairs", method="message-shuffled null", null="message shuffle",
                                notes=f"p_lo {m['rho_same']['p_lo']:.3f}"))
    E.write_estimates(rows, hypothesis="H132")
    return len(rows)


def main():
    R = json.loads((RES / "results.json").read_text())
    S = json.loads(SYN.read_text())
    figure(R, S)
    n = estimates(R)
    print("estimate rows", n)
    for k, r in R.items():
        print(k, {s: (round(r["deb"][s]["obs"], 3), round(r["deb"][s]["p_hi"], 4), round(r["deb"][s]["p_two"], 4))
                  for s in ("rho1", "rho2", "Lam", "A", "L", "rho1_vec", "dRho_vis")},
              "detrend Lam", round(r["deb_detrend"]["Lam"]["obs"], 3), round(r["deb_detrend"]["Lam"]["p_hi"], 3),
              "rho1 det", round(r["deb_detrend"]["rho1"]["obs"], 3))
        print("  per debate rho1", [round(x["rho1"], 2) for x in r["per_debate"]], "Lam", [round(x["Lam"], 2) for x in r["per_debate"]],
              "gov-opp", [round(x["gov_minus_opp"], 2) for x in r["per_debate"]])
        print("  post", {s: round(r["post"][s]["obs"], 3) for s in ("rho1", "rho2", "Lam")}, "msg", r["msg"]["obs"])


if __name__ == "__main__":
    main()
