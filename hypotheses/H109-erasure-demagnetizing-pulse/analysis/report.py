"""H109 report: figures, per-period README results and verdicts, per_period_estimates rows.

Usage: uv run python hypotheses/H109-erasure-demagnetizing-pulse/analysis/report.py
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
import polars as pl  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h109lib as L  # noqa: E402

sys.path.insert(0, str(L.ROOT / "infra/shared"))
import estimates as E  # noqa: E402

CARD = L.ROOT / "hypotheses/H109-erasure-demagnetizing-pulse"
RES = json.loads((L.D / "results/results.json").read_text())
SYN = {m: json.loads((L.D / f"synthetic/synthetic_summary_{m}.json").read_text()) for m in L.MODELS}
COL = {"bge_small": "#2a78d6", "gte_modernbert": "#eb6834"}
LAB = {"bge_small": "bge", "gte_modernbert": "gte"}
ROLE = {36: "replication", 37: "replication", 38: "native", 39: "replication", 41: "native", 42: "replication",
        44: "native", 51: "native"}
UNIT = {36: ("G36", "36b+36c", "2026-03-24", "2026-03-27"), 51: ("51g", "51g", "2026-08-05", "2026-08-21")}
POWER = {m: {int(k): v["reject_pos"] for k, v in SYN[m]["worlds"]["read30"]["periods"].items()}
         for m in L.MODELS if "read30" in SYN[m]["worlds"]}


def f(x, d=2):
    return "–" if x is None or (isinstance(x, float) and not np.isfinite(x)) else f"{x:.{d}f}"


def ci(c, d=2):
    return "–" if not c else f"[{f(c[0], d)}, {f(c[1], d)}]"


def verdict(P: int) -> tuple[str, str]:
    d = RES["models"]["bge_small"]["restate"][str(P)]["F"]
    pw = POWER["bge_small"].get(P, 0)
    if d.get("n", 0) == 0:
        return "n/a", "no forced boundaries"
    if d["A_pre_ci"][0] <= 0:
        return "descriptive", "pre-erasure room alignment not identified (CI includes 0)"
    lo, hi = d["delta_ci"]
    if d["delta"] >= 0.30 and lo > 0:
        return "supported", "drop ≥ 0.30 with CI > 0"
    if hi < 0.30 and pw >= 0.8:
        return "failed", f"CI upper < 0.30 with synthetic power {pw:.2f}"
    return "mixed", f"inconclusive: CI {ci(d['delta_ci'])} and synthetic power {pw:.2f} < 0.8"


def figures():
    fig, ax = plt.subplots(1, 2, figsize=(7.2, 2.8), gridspec_kw={"width_ratios": [1.5, 1]})
    a = ax[0]
    xs = np.arange(len(L.PERIODS) + 1)
    for j, m in enumerate(L.MODELS):
        B = RES["models"][m]["restate"]
        for i, P in enumerate(L.PERIODS):
            d = B[str(P)]["F"]
            if d.get("n", 0) == 0 or d["A_pre_ci"][0] <= 0:
                continue
            lo, hi = np.clip(d["delta_ci"], -1.2, 1.2)
            a.plot([i + (j - 0.5) * 0.25] * 2, [lo, hi], color=COL[m], lw=2, solid_capstyle="round")
            a.plot(i + (j - 0.5) * 0.25, np.clip(d["delta"], -1.2, 1.2), "o", ms=5, color=COL[m],
                   mec="white", mew=1, label=LAB[m] if i == 2 else None)
        re_ = B["re_F"]
        a.plot([len(L.PERIODS) + (j - 0.5) * 0.25] * 2, re_["ci"], color=COL[m], lw=2)
        a.plot(len(L.PERIODS) + (j - 0.5) * 0.25, re_["mu"], "D", ms=5, color=COL[m], mec="white", mew=1)
    a.axhline(0, color="#85847e", lw=0.8)
    a.axhline(0.30, color="#0b0b0b", lw=1, ls="--")
    a.text(len(L.PERIODS) + 0.45, 0.32, "HH339: 30% drop", ha="right", va="bottom", fontsize=7)
    a.set_xticks(xs)
    a.set_xticklabels([f"#{P}" if P != 51 else "51g" for P in L.PERIODS] + ["RE"], fontsize=7)
    a.set_ylim(-1.25, 1.25)
    a.set_ylabel("drop fraction δ_F", fontsize=8)
    a.set_title("(a) room-alignment drop at forced erasures", fontsize=8, loc="left")
    a.legend(fontsize=7, frameon=False, loc="lower right")
    a.tick_params(labelsize=7)
    for s in ("top", "right"):
        a.spines[s].set_visible(False)
    # (b) synthetic: pooled power vs world, and the observed pooled value
    b = ax[1]
    S = SYN["bge_small"]["worlds"]
    names = [w for w in ["null", "noise", "drive", "drop30", "read30", "read50"] if w in S]
    est = [S[w]["estimand"]["all"] for w in names]
    rej = [S[w]["pooled"]["reject_pos"] for w in names]
    b.bar(np.arange(len(names)), rej, color="#2a78d6", width=0.6)
    for i, (e_, r_) in enumerate(zip(est, rej)):
        b.text(i, r_ + 0.03, f"δ={e_:.2f}", ha="center", fontsize=6)
    b.set_xticks(np.arange(len(names)))
    b.set_xticklabels(names, fontsize=6, rotation=30)
    b.set_ylim(0, 1.15)
    b.set_ylabel("P(pooled CI > 0)", fontsize=8)
    b.set_title("(b) synthetic worlds (bge, 30 reps)", fontsize=8, loc="left")
    b.tick_params(labelsize=7)
    for s in ("top", "right"):
        b.spines[s].set_visible(False)
    fig.tight_layout()
    fig.savefig(CARD / "figures/summary_obs.pdf")
    plt.close(fig)
    # event profile
    st, bd, rd = L.load_tables()
    fig, ax = plt.subplots(figsize=(3.6, 2.6))
    for m in L.MODELS:
        X = L.load_X(st, m)
        Xc = L.day_center(st, X)
        A = L.agent_constants(st, Xc)
        F = L.field_dirs(m)
        a_, _, _ = L.axes_and_alignment(st, Xc, X, A, F)
        bb = bd.filter((pl.col("variant") == "restate") & (pl.col("label") == "F"))
        prof = {k: [] for k in list(range(-3, 0)) + list(range(1, 11))}
        for pre, post in zip(bb["pre"].to_list(), bb["postk"].to_list()):
            for j, s in enumerate(reversed(pre)):
                if np.isfinite(a_[s]):
                    prof[-(j + 1)].append(a_[s])
            for j, s in enumerate(post):
                if np.isfinite(a_[s]):
                    prof[j + 1].append(a_[s])
        base = np.mean(prof[-1] + prof[-2] + prof[-3])
        ks = sorted(prof)
        mu = [np.mean(prof[k]) / base for k in ks]
        se = [np.std(prof[k]) / np.sqrt(len(prof[k])) / base for k in ks]
        xk = [k if k < 0 else k - 0.5 for k in ks]
        ax.errorbar(xk, mu, yerr=1.96 * np.array(se), color=COL[m], lw=1.5, marker="o", ms=3, capsize=0, label=LAB[m])
    ax.axvline(-0.25, color="#0b0b0b", lw=0.8)
    ax.axhline(1, color="#85847e", lw=0.8)
    ax.axhline(0.7, color="#0b0b0b", lw=0.8, ls="--")
    ax.text(9.5, 0.71, "30% drop", fontsize=6, ha="right", va="bottom")
    ax.set_xlabel("statement index relative to forced erasure", fontsize=8)
    ax.set_ylabel("room alignment / pre mean", fontsize=8)
    ax.set_title("Pooled event profile (8 periods, restate-deduped)", fontsize=8, loc="left")
    ax.legend(fontsize=7, frameon=False)
    ax.tick_params(labelsize=7)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    fig.tight_layout()
    fig.savefig(CARD / "figures/summary_obsb.pdf")
    plt.close(fig)


def period_readmes():
    rows = []
    for P in L.PERIODS:
        g = f"G{P}"
        v, why = verdict(P)
        lines = ["*Run 2026-10-04 (`analysis/run.py`, `analysis/report.py`; non-holdout).* Primary: bge style_resid, "
                 "restatements dropped; gte alongside.", "",
                 "| Statistic | bge | gte |", "| --- | --- | --- |"]
        Bb = RES["models"]["bge_small"]["restate"][str(P)]
        Bg = RES["models"]["gte_modernbert"]["restate"][str(P)]
        lines.append(f"| forced / voluntary / within boundaries | {Bb['n_events']['F']} / {Bb['n_events']['V']} / {Bb['n_events']['W']} | same |")
        lines.append(f"| pre-erasure room alignment Ā_pre [CI] | {f(Bb['F'].get('A_pre'), 3)} {ci(Bb['F'].get('A_pre_ci'), 3)} | {f(Bg['F'].get('A_pre'), 3)} {ci(Bg['F'].get('A_pre_ci'), 3)} |")
        lines.append(f"| δ_F forced drop [agent-day CI] | {f(Bb['F'].get('delta'))} {ci(Bb['F'].get('delta_ci'))} | {f(Bg['F'].get('delta'))} {ci(Bg['F'].get('delta_ci'))} |")
        lines.append(f"| δ_F agent-cluster CI | {ci(Bb['F_agent'].get('delta_ci'))} | {ci(Bg['F_agent'].get('delta_ci'))} |")
        lines.append(f"| δ_F regression (± SE) | {f(Bb['reg'].get('delta_reg'))} ± {f(Bb['reg'].get('delta_reg_se'))} | {f(Bg['reg'].get('delta_reg'))} ± {f(Bg['reg'].get('delta_reg_se'))} |")
        lines.append(f"| gap-matched coverage of F events | {f(Bb['F'].get('coverage'))} | {f(Bg['F'].get('coverage'))} |")
        lines.append(f"| δ_V voluntary [CI] | {f(Bb['V'].get('delta'))} {ci(Bb['V'].get('delta_ci'))} | {f(Bg['V'].get('delta'))} {ci(Bg['V'].get('delta_ci'))} |")
        kid = "identified" if Bb["K"].get("A_pre_ci", [0])[0] > 0 else "not identified"
        lines.append(f"| δ_K kickoff alignment [CI] (pre level {kid}) | {f(Bb['K'].get('delta'))} {ci(Bb['K'].get('delta_ci'))} | {f(Bg['K'].get('delta'))} {ci(Bg['K'].get('delta_ci'))} |")
        rb, rg = RES["models"]["bge_small"]["recovery"][str(P)], RES["models"]["gte_modernbert"]["recovery"][str(P)]
        lines.append(f"| κ_R re-read slope [CI]; κ_U | {f(rb.get('kR'), 3)} {ci(rb.get('kR_ci'), 3)}; {f(rb.get('kU'), 3)} | {f(rg.get('kR'), 3)} {ci(rg.get('kR_ci'), 3)}; {f(rg.get('kU'), 3)} |")
        lines.append(f"| synthetic power at δ = 0.30 (read30) | {f(POWER['bge_small'].get(P))} | {f(POWER['gte_modernbert'].get(P))} |")
        lines.append("")
        lines.append(f"**Verdict:** {v} ({why}). Negative δ = alignment rises after the erasure.")
        res_md = "\n".join(lines)
        sc = ("- **C:** W-boundary placebo (gap-matched within agent) and kickoff control.\n"
              "- **E:** NE41 forced erasures in this period (exogenous timing).\n"
              f"- **F:** real-skeleton synthetic power {f(POWER['bge_small'].get(P))} (bge) at δ = 0.30.")
        p = CARD / f"goalperiod-subhypotheses/{g}/README.md"
        t = p.read_text()
        t = re.sub(r"\*\*Verdict:\*\* .*", f"**Verdict:** {v}", t, count=1)
        t = re.sub(r"## Result\n.*?\n## Scorecard", "## Result\n" + res_md + "\n\n## Scorecard", t, flags=re.S)
        t = re.sub(r"## Scorecard \(period-specific axes\)\n.*?\n## Notes", "## Scorecard (period-specific axes)\n" + sc + "\n\n## Notes", t, flags=re.S)
        p.write_text(t)
        rows.append((P, v, Bb, Bg))
    return rows


def ne41_readme():
    M = RES["models"]
    lines = ["*Run 2026-10-04 (`analysis/run.py`, `analysis/report.py`; non-holdout).*", "",
             "| Statistic (pooled over 8 periods) | bge | gte |", "| --- | --- | --- |"]
    for key, name in (("re_F", "δ_F random-effects mean [95% CI]"), ("re_V", "δ_V voluntary, RE"), ("re_K", "δ_K kickoff, RE")):
        lines.append(f"| {name} | {f(M['bge_small']['restate'][key].get('mu'))} {ci(M['bge_small']['restate'][key].get('ci'))} (I² {f(M['bge_small']['restate'][key].get('I2'))}) | {f(M['gte_modernbert']['restate'][key].get('mu'))} {ci(M['gte_modernbert']['restate'][key].get('ci'))} |")
    for key, name in (("pooled_direct_F", "δ_F direct pooled stratified"),):
        lines.append(f"| {name} | {f(M['bge_small']['restate'][key]['delta'])} {ci(M['bge_small']['restate'][key]['delta_ci'])} | {f(M['gte_modernbert']['restate'][key]['delta'])} {ci(M['gte_modernbert']['restate'][key]['delta_ci'])} |")
    for v, name in (("none", "δ_F RE, no dedupe"), ("copy", "δ_F RE, copies dropped"), ("restate_k1", "δ_F RE, first statement only")):
        lines.append(f"| {name} | {f(M['bge_small'][v]['re_F'].get('mu'))} {ci(M['bge_small'][v]['re_F'].get('ci'))} | {f(M['gte_modernbert'][v]['re_F'].get('mu'))} {ci(M['gte_modernbert'][v]['re_F'].get('ci'))} |")
    lines.append(f"| δ_F RE, no agent constant / white32 (bge) | {f(M['bge_small']['noconst']['re_F'].get('mu'))} {ci(M['bge_small']['noconst']['re_F'].get('ci'))} / {f(M['bge_small']['white32']['re_F'].get('mu'))} {ci(M['bge_small']['white32']['re_F'].get('ci'))} | – |")
    for k in ("R0", "Rpos"):
        lines.append(f"| R-fast: δ_F for post statements with R {'= 0' if k == 'R0' else '> 0'} (n F) | {f(M['bge_small']['restate']['pooled_rfast'][k]['delta'])} {ci(M['bge_small']['restate']['pooled_rfast'][k]['delta_ci'])} ({M['bge_small']['restate']['pooled_rfast'][k]['n']}) | {f(M['gte_modernbert']['restate']['pooled_rfast'][k]['delta'])} {ci(M['gte_modernbert']['restate']['pooled_rfast'][k]['delta_ci'])} |")
    for key, name in (("recovery", "κ_R after forced erasures [CI]"), ("recovery_V", "κ_R after voluntary erasures [CI]")):
        rb = M["bge_small"][key]["pooled"] if key == "recovery" else M["bge_small"][key]
        rg = M["gte_modernbert"][key]["pooled"] if key == "recovery" else M["gte_modernbert"][key]
        lines.append(f"| {name}; κ_R − κ_U [CI] | {f(rb['kR'], 3)} {ci(rb['kR_ci'], 3)}; {f(rb['kR_minus_kU'], 3)} {ci(rb['kR_minus_kU_ci'], 3)} | {f(rg['kR'], 3)} {ci(rg['kR_ci'], 3)}; {f(rg['kR_minus_kU'], 3)} {ci(rg['kR_minus_kU_ci'], 3)} |")
    lines.append("| synthetic null 95th pct of κ_R; κ_R − κ_U (A1) | 0.014; 0.020 | 0.018; 0.023 |")
    lines += ["", "**Verdict:** failed (HH339's kill fires: the pooled δ_F CI upper bound is below 0.30 in both models, "
              "synthetic power 1.00). P5 holds (δ_V within 0.15 of δ_F). Reading adds a small pull (κ_R ≈ 0.02 per e-fold of "
              "items, above the null 95th percentile in bge, at it in gte), but no drop exists for it to recover."]
    p = CARD / "goalperiod-subhypotheses/NE41/README.md"
    t = p.read_text()
    t = re.sub(r"\*\*Verdict:\*\* .*", "**Verdict:** failed", t, count=1)
    t = re.sub(r"## Result\n.*?\n## Scorecard", "## Result\n" + "\n".join(lines) + "\n\n## Scorecard", t, flags=re.S)
    t = re.sub(r"## Scorecard \(period-specific axes\)\n.*?\n## Notes", "## Scorecard (period-specific axes)\n- **C:** W-boundary placebo; kickoff control; posted-unread placebo.\n- **E:** 3,477 forced erasures (exogenous) and 2,559 voluntary.\n- **F:** pooled power 1.00 at δ = 0.30; size 0.00.\n- **H:** R-art / R-prior (no drop) beat R-ctx; R-fast and R-loop moot.\n\n## Notes", t, flags=re.S)
    p.write_text(t)


def estimates_rows():
    rows = []
    for m in L.MODELS:
        ch = f"content_{LAB[m]}_style_resid"
        for P in L.PERIODS:
            B = RES["models"][m]["restate"][str(P)]
            pu, ul, fd, ld = UNIT.get(P, (f"G{P}", None, None, None))
            base = {"period_unit": pu, "goal_no": P, "channel": ch, "unit_local": ul, "first_day": fd, "last_day": ld,
                    "ci_kind": "percentile", "ci_level": 0.95, "source": "data/processed/H109-erasure-demagnetizing-pulse/results/results.json"}
            for stat, d, meth, null in (
                    ("erasure_drop_delta_F", B["F"], "gap-matched forced vs within-segment boundary, agent-day bootstrap",
                     "W boundaries (same agent, 0.05-decade gap strata)"),
                    ("erasure_drop_delta_V", B["V"], "gap-matched voluntary vs within boundary", "W boundaries"),
                    ("erasure_drop_delta_K_kickoff", B["K"], "kickoff alignment drop, gap-matched", "W boundaries")):
                if d.get("n", 0) == 0:
                    continue
                rows.append({**base, "statistic": stat, "estimate": d["delta"], "ci_lo": d["delta_ci"][0],
                             "ci_hi": d["delta_ci"][1], "n": d["n"], "n_kind": "boundaries", "method": meth,
                             "null": null, "role": "replication",
                             "notes": f"A_pre {d['A_pre']:.3f} CI {d['A_pre_ci'][0]:.3f},{d['A_pre_ci'][1]:.3f}"})
            rr = RES["models"][m]["recovery"][str(P)]
            if "kR" in rr:
                rows.append({**base, "statistic": "erasure_reread_slope_kappa_R", "estimate": rr["kR"], "ci_lo": rr["kR_ci"][0],
                             "ci_hi": rr["kR_ci"][1], "n": rr["n"], "n_kind": "post-erasure statements",
                             "method": "event-FE WLS on log1p(items read), log1p(posted-unread), log k",
                             "null": "posted-unread kappa_U; synthetic null q95", "role": "native" if P == 51 else "replication"})
    E.write_estimates(rows, hypothesis="H109")
    return len(rows)


def main():
    figures()
    rows = period_readmes()
    ne41_readme()
    n = estimates_rows()
    print("estimates rows", n)
    for P, v, Bb, Bg in rows:
        print(P, v, f(Bb["F"].get("delta")), ci(Bb["F"].get("delta_ci")), f(Bg["F"].get("delta")), ci(Bg["F"].get("delta_ci")))


if __name__ == "__main__":
    main()
