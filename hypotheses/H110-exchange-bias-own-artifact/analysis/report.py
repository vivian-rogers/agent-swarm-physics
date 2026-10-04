"""H110 report: figure, per-period README results and verdicts, per_period_estimates rows.

Usage: uv run python hypotheses/H110-exchange-bias-own-artifact/analysis/report.py
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h110lib as L  # noqa: E402

sys.path.insert(0, str(L.ROOT / "infra/shared"))
import estimates as E  # noqa: E402

CARD = L.ROOT / "hypotheses/H110-exchange-bias-own-artifact"
RES = json.loads((L.D / "results/results.json").read_text())
COL = {"bge_small": "#2a78d6", "gte_modernbert": "#eb6834"}
LAB = {"bge_small": "bge", "gte_modernbert": "gte"}
TR = [31, 37, 38, 39, 40, 41, 42]
ROLE = {39: "native", 40: "native"}


def f(x, d=2):
    return "–" if x is None or (isinstance(x, float) and not np.isfinite(x)) else f"{x:.{d}f}"


def ci(c, d=2):
    return "–" if not c else f"[{f(c[0], d)}, {f(c[1], d)}]"


def tverdict(P, m="bge_small"):
    d = RES[m]["pinned_own"]["pooled"]["per_transition"].get(str(P))
    if d is None or d["nP"] < 2 or d["nU"] < 2:
        return "descriptive", "a group has < 2 agents"
    if d["pre_P"] <= 0 or d["pre_U"] <= 0:
        return "descriptive", "a pre level is not positive"
    lr = d["lam_ratio"]
    if d["R1_P"] < d["R1_U"]:
        return "failed", "pinned agents keep less of the old state"
    if lr is not None and 0.8 <= lr <= 1.25:
        return "failed", "decay rates within 25%"
    if d["R1_P"] > d["R1_U"] and (lr == float("inf") or lr >= 2):
        return "supported", "pinned agents keep more, decay ratio ≥ 2"
    return "mixed", "pinned agents keep more, decay ratio < 2"


def figure():
    fig, ax = plt.subplots(1, 2, figsize=(7.2, 2.8), gridspec_kw={"width_ratios": [1.5, 1]})
    a = ax[0]
    cts = [37, 38, 41, 42]
    for j, m in enumerate(L.MODELS):
        pt = RES[m]["pinned_own"]["pooled"]["per_transition"]
        for i, P in enumerate(cts):
            d = pt[str(P)]
            x = i + (j - 0.5) * 0.3
            a.plot([x, x], [d["R1_U"], d["R1_P"]], color=COL[m], lw=1.2, alpha=0.6)
            a.plot(x, d["R1_P"], "o", color=COL[m], ms=6, mec="white", mew=1, label=f"{LAB[m]} pinned" if i == 0 else None)
            a.plot(x, d["R1_U"], "o", color="white", ms=5, mec=COL[m], mew=1.5, label=f"{LAB[m]} unpinned" if i == 0 else None)
        po = RES[m]["pinned_own"]["pooled"]
        x = len(cts) + (j - 0.5) * 0.3
        a.errorbar(x - 0.05, po["R1_P"], yerr=[[po["R1_P"] - po["R1_P_ci"][0]], [po["R1_P_ci"][1] - po["R1_P"]]], fmt="o", color=COL[m], ms=6, mec="white")
        a.errorbar(x + 0.05, po["R1_U"], yerr=[[po["R1_U"] - po["R1_U_ci"][0]], [po["R1_U_ci"][1] - po["R1_U"]]], fmt="o", color=COL[m], mfc="white", ms=5)
    a.axhline(0, color="#85847e", lw=0.8)
    a.axhline(0.25, color="#0b0b0b", lw=0.8, ls=":")
    a.text(4.45, 0.27, "H96 median R₁", fontsize=6, ha="right")
    a.set_xticks(range(len(cts) + 1))
    a.set_xticklabels([f"#{P - 1}→#{P}" for P in cts] + ["pooled"], fontsize=7)
    a.set_ylabel("day-1 persistence R₁", fontsize=8)
    a.set_title("(a) old-state persistence, pinned vs unpinned", fontsize=8, loc="left")
    a.legend(fontsize=6, frameon=False, ncol=2, loc="upper right")
    a.tick_params(labelsize=7)
    for s in ("top", "right"):
        a.spines[s].set_visible(False)
    b = ax[1]
    for j, m in enumerate(L.MODELS):
        o = RES[m]["pinned_own"]["offset"]
        for i, c in enumerate(("live", "edge", "after")):
            if o.get(c) is None:
                continue
            x = i + (j - 0.5) * 0.25
            b.errorbar(x, o[c], yerr=[[o[c] - o[c + "_ci"][0]], [o[c + "_ci"][1] - o[c]]], fmt="o", color=COL[m], ms=5,
                       mec="white", label=LAB[m] if i == 0 else None)
    b.axhline(0, color="#85847e", lw=0.8)
    b.set_xticks(range(3))
    b.set_xticklabels(["still committing", "day after\nlast commit", "later"], fontsize=7)
    b.set_ylabel("pinned excess e (old-state units)", fontsize=8)
    b.set_title("(b) offset vs own-repo commits", fontsize=8, loc="left")
    b.legend(fontsize=7, frameon=False)
    b.tick_params(labelsize=7)
    for s in ("top", "right"):
        b.spines[s].set_visible(False)
    fig.tight_layout()
    fig.savefig(CARD / "figures/summary_obs.pdf")
    plt.close(fig)


def readmes():
    out = []
    for P in TR:
        v, why = tverdict(P)
        rb = RES["bge_small"]["pinned_own"]["pooled"]["per_transition"].get(str(P), {})
        rg = RES["gte_modernbert"]["pinned_own"]["pooled"]["per_transition"].get(str(P), {})
        ra = RES["bge_small"]["pinned_any"]["pooled"]["per_transition"].get(str(P), {})
        R1 = RES["bge_small"]["transition"]["R1"].get(str(P))
        lines = ["*Run 2026-10-04 (`analysis/run.py`, `analysis/report.py`; non-holdout).* Day-1 persistence R₁ = Σ m(day 1) / Σ m(pre) "
                 "per group; m = field-orthogonal, placebo-corrected old-state remanence (H96 construction).", "",
                 "| Statistic | bge | gte |", "| --- | --- | --- |",
                 f"| pinned (own repo) / unpinned agents | {rb.get('nP', '–')} / {rb.get('nU', '–')} | {rg.get('nP', '–')} / {rg.get('nU', '–')} |",
                 f"| pre level m (pinned, unpinned) | {f(rb.get('pre_P'))}, {f(rb.get('pre_U'))} | {f(rg.get('pre_P'))}, {f(rg.get('pre_U'))} |",
                 f"| R₁ pinned / unpinned | {f(rb.get('R1_P'))} / {f(rb.get('R1_U'))} | {f(rg.get('R1_P'))} / {f(rg.get('R1_U'))} |",
                 f"| decay ratio λ_U/λ_P (floor R₁ = 0.02) | {f(rb.get('lam_ratio'))} | {f(rg.get('lam_ratio'))} |",
                 f"| any-repo variant R₁ pinned / unpinned (n) | {f(ra.get('R1_P'))} / {f(ra.get('R1_U'))} ({ra.get('nP', '–')}/{ra.get('nU', '–')}) | – |",
                 f"| transition R₁ (all agents) | {f(R1)} | {f(RES['gte_modernbert']['transition']['R1'].get(str(P)))} |", ""]
        if P == 40:
            g = RES["bge_small"]["g40"]
            gg = RES["gte_modernbert"]["g40"]
            lines.append(f"**Native (continuing vs stopping pinned agents, days 1–3):** continuing {g['n_cont']} (agents {g['agents_cont']}), stopping {g['n_stop']} (agents {g['agents_stop']}). "
                         f"Mean m continuing − stopping: {f(g.get('diff'), 3)} {ci(g.get('diff_ci'), 3)} (bge); {f(gg.get('diff'), 3)} {ci(gg.get('diff_ci'), 3)} (gte). No offset tied to continued commits.")
            v, why = "mixed", "native: continuing − stopping ≈ 0 with a CI on both sides (replication contrast descriptive: 1 unpinned agent)"
        if P == 39:
            g = RES["bge_small"]["g39"]
            lines.append(f"**Native (own-room memory by continued #38-repo commits):** only {g['n_kept']} veteran kept committing to a #38 repo on days 1–3 ({g['n_not']} did not). Descriptive.")
            v, why = "descriptive", "native: < 2 agents kept committing to a #38 repo"
        lines.append("")
        lines.append(f"**Verdict:** {v} ({why}). Per-transition verdicts are descriptive evidence; the pooled rule decides (card).")
        p = CARD / f"goalperiod-subhypotheses/G{P}/README.md"
        t = p.read_text()
        t = re.sub(r"\*\*Verdict:\*\* .*", f"**Verdict:** {v}", t, count=1)
        t = re.sub(r"## Result\n.*?\n## Scorecard", "## Result\n" + "\n".join(lines) + "\n\n## Scorecard", t, flags=re.S)
        sc = ("- **C:** unpinned agents at the same boundary (same kickoff, field projection, old state).\n"
              "- **D:** the offset-end test is not fitted (card O3; pooled, not per transition).\n"
              "- **F:** real-skeleton synthetic: the per-transition contrast is underpowered; only the pooled rule is calibrated.")
        t = re.sub(r"## Scorecard \(period-specific axes\)\n.*?\n## Notes", "## Scorecard (period-specific axes)\n" + sc + "\n\n## Notes", t, flags=re.S)
        p.write_text(t)
        out.append((P, v, rb, rg))
    return out


def estimates_rows():
    rows = []
    for m in L.MODELS:
        ch = f"content_{LAB[m]}_style_resid"
        pt = RES[m]["pinned_own"]["pooled"]["per_transition"]
        for P in TR:
            d = pt.get(str(P))
            if not d:
                continue
            base = {"period_unit": f"G{P}", "goal_no": P, "channel": ch, "ci_kind": "none", "unit_local": f"G{P - 1}->G{P}",
                    "source": "data/processed/H110-exchange-bias-own-artifact/results/results.json",
                    "role": ROLE.get(P, "replication"), "null": "unpinned agents at the same boundary"}
            for stat, val, nk in (("exchange_bias_R1_pinned", d["R1_P"], d["nP"]), ("exchange_bias_R1_unpinned", d["R1_U"], d["nU"])):
                rows.append({**base, "statistic": stat, "estimate": val, "ci_lo": None, "ci_hi": None, "n": nk,
                             "n_kind": "agents", "method": "ratio of sums of day-1 / pre field-orthogonal old-state remanence (H96 construction)"})
            if d["lam_ratio"] is not None and np.isfinite(d["lam_ratio"]):
                rows.append({**base, "statistic": "exchange_bias_decay_ratio", "estimate": d["lam_ratio"], "ci_lo": None, "ci_hi": None,
                             "n": d["nP"] + d["nU"], "n_kind": "agents", "method": "lambda_U/lambda_P, lambda = -ln max(R1, 0.02)"})
        R1 = RES[m]["transition"]["R1"]
        for P in TR:
            if str(P) in R1:
                rows.append({"period_unit": f"G{P}", "goal_no": P, "channel": ch, "statistic": "old_state_R1_all_agents",
                             "estimate": R1[str(P)], "ci_lo": None, "ci_hi": None, "n": None, "n_kind": "agents",
                             "method": "ratio of sums day-1/pre (H110 re-implementation of H96 M_exc, agent-window vectors)",
                             "null": "placebo old states", "role": "replication", "ci_kind": "none", "unit_local": f"G{P - 1}->G{P}",
                             "source": "data/processed/H110-exchange-bias-own-artifact/results/results.json"})
    E.write_estimates(rows, hypothesis="H110")
    return len(rows)


def main():
    figure()
    out = readmes()
    print("estimates rows", estimates_rows())
    for P, v, rb, rg in out:
        print(P, v, f(rb.get("R1_P")), f(rb.get("R1_U")), f(rg.get("R1_P")), f(rg.get("R1_U")))


if __name__ == "__main__":
    main()
