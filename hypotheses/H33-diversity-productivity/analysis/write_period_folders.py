"""Write goalperiod-subhypotheses/G<NN>/README.md for H33.

  predict  : header + dated prediction + pending result (run BEFORE evaluate.py)
  results  : fill the Result / Verdict / Scorecard sections from data/processed/H33-diversity-productivity/results.json

Usage: uv run python hypotheses/H33-diversity-productivity/analysis/write_period_folders.py predict|results
"""
from __future__ import annotations

import json
import re
import sys

import h33lib as H  # noqa: F401,I001
import h33common as C
import polars as pl

GP = C.ROOT / "hypotheses/hypohypotheses/goal-periods.md"
GDIR = C.HYP / "goalperiod-subhypotheses"
MODE = {"C": "shared objective", "I": "individual", "K": "competitive", "F": "free", "M": "mixed", "I/K": "individual/competitive"}
PRED_DATE = "2026-10-04"


def period_meta():
    txt = GP.read_text()
    meta = {}
    for m in re.finditer(r"^\| (\d+) \| (\S+) → (\S+) \| (\d+)†? \| (\d+) \| ([\d,?]+) \| (\w+) \| (\w) \| ([\w/]+) \|", txt, re.M):
        g = int(m.group(1))
        meta[g] = {"start": m.group(2), "end": m.group(3), "d": int(m.group(4)), "N": int(m.group(5)),
                   "regime": m.group(7), "by": m.group(8), "mode": m.group(9)}
    for m in re.finditer(r"^### (\d+) · (.+)$", txt, re.M):
        meta.setdefault(int(m.group(1)), {})["title"] = m.group(2).strip()
    return meta


def header(g, unit, el, meta, verdict="pending"):
    m = meta[g]
    split = " Unit 36b only: the part after the 2026-03-24 regime boundary (36a has 1 non-holdout day with PR and is ineligible)." if unit == "36b" else ""
    return (f"# H33 × G{g:02d}: {m.get('title', '')} ({m['start']} → {m['end']})\n\n"
            f"**Verdict:** {verdict}\n**Role:** exploratory (round 1, non-holdout)\n"
            f"**Period:** regime {'III (unit 36b; the period starts in II)' if unit == '36b' else m['regime']} · mode {m['mode']} ({MODE.get(m['mode'], m['mode'])}) · N = {m['N']} at start · "
            f"{el['n_days']} non-holdout days with PR10 · {el['n_ad']} agent-days with PR10 ({el['agents3']} agents with ≥ 3 days) · "
            f"write turns on {100 * el['share_w']:.0f}% of those agent-days.{split}\n")


def prediction_block(g, unit, el, meta):
    m = meta[g]
    small = el["n_ad"] < 60
    lines = [
        "## Why this period",
        f"Eligible under the card's pre-registered rule (≥ 30 agent-days with PR10, ≥ 4 agents with ≥ 3 days, write turns on ≥ 20% of agent-days). "
        f"Mode {m['mode']}: {'agents ship artifacts toward one shared objective, so output and talk are both about the same project' if m['mode'] == 'C' else 'agents work on their own artifacts, so output is individual and diversity is less tied to coordination' if m['mode'] in ('I', 'I/K') else 'free or competitive week; output is less goal-directed'}.",
        "",
        "## Prediction",
        f"*Written {PRED_DATE}, before running on this period.* The card's predictions as they apply here (`../../README.md`).",
        "- **Model:** log(1 + write turns) = agent FE + day FE + f(PR10) + controls (log raw chat count, log(1 + engaged minutes)); CR1 SEs clustered by agent, t(G − 1) reference.",
        "- **P2 (per period):** two-lines at the *pooled* Robin Hood breakpoint: b₁ > 0 below it and b₂ < 0 above it. The per-period \"maximum at the edge\" check uses a natural spline with 3 df (4 knots), interior = between the 10th and 90th percentiles of PR10.",
        f"- **Power:** {'low (fewer than 60 agent-days); significance not expected even if H33 is true' if small else 'modest; significance of one slope possible if the effect is ≥ 0.4 residual SD (synthetic)'}.",
        "- **Expected (calibrated prior, card):** b₁ > 0, b₂ ≈ 0 (saturating), i.e. **mixed or failed** rather than supported.",
        "",
        "**Period verdict rule (card):** supported if b₁ > 0 and b₂ < 0 with at least one significant (p < 0.05); failed if both slopes share a sign or the spline maximum is at an edge; mixed otherwise. "
        "**What would count against H33 here:** both slopes of the same sign, or the spline maximum at the edge of the period's PR10 range.",
        "",
        "",
    ]
    return "\n".join(lines)


def predict():
    meta = period_meta()
    el = pl.read_parquet(C.OUT / "eligibility.parquet").filter("eligible")
    for r in el.iter_rows(named=True):
        u = r["unit"]
        g = int(u.rstrip("ab"))
        d = GDIR / f"G{g:02d}"
        (d / "figures").mkdir(parents=True, exist_ok=True)
        (d / "figures" / ".gitkeep").touch()
        txt = (header(g, u, r, meta) + "\n" + prediction_block(g, u, r, meta) +
               "## Result\n<!-- RESULT -->\n*Pending: not yet run.*\n\n"
               "## Scorecard (period-specific axes)\n<!-- SCORECARD -->\n*Pending.*\n\n"
               f"## Notes\n- {PRED_DATE}: prediction written before any per-period run (data: `data/processed/H33-diversity-productivity/G{g:02d}/`).\n")
        (d / "README.md").write_text(txt)
    print(f"wrote {el.height} period folders")


def results():
    res = json.loads((C.OUT / "results.json").read_text())
    per = {p["unit"]: p for p in res["per_period"]}
    for u, p in per.items():
        g = int(u.rstrip("ab"))
        f = GDIR / f"G{g:02d}" / "README.md"
        txt = f.read_text()
        txt = re.sub(r"\*\*Verdict:\*\* \w+", f"**Verdict:** {p['verdict']}", txt, count=1)
        fmt = lambda v, k=3: "n/a" if v is None or v != v else f"{v:+.{k}f}"  # noqa: E731
        fp = lambda v: "n/a" if v is None or v != v else f"{v:.3f}"  # noqa: E731
        yes = lambda c, v: "n/a" if v is None else ("yes" if c else "no")  # noqa: E731
        b1, b2 = p["b1"], p["b2"]
        tab = ["| Check | Observed | Null / threshold | Holds |", "| --- | --- | --- | --- |",
               f"| b₁ (PR10 < x_c = {res['pooled']['two_lines']['xc']:.2f}) | {fmt(b1)} (p {fp(p['p1'])}; n {p['n_lo']}) | > 0 | {yes(b1 is not None and b1 > 0, b1)} |",
               f"| b₂ (PR10 ≥ x_c) | {fmt(b2)} (p {fp(p['p2'])}; n {p['n_hi']}) | < 0 | {yes(b2 is not None and b2 < 0, b2)} |",
               f"| spline (3 df) maximum | PR10 = {p['x_max']:.2f} ({'interior' if p['interior'] else 'edge'}) | interior | {'yes' if p['interior'] else 'no'} |",
               f"| quadratic β₂ | {fmt(p['q_b2'], 4)} (p {fp(p['q_p2'])}; vertex {p['q_vertex']:.1f}) | < 0 | {'yes' if p['q_b2'] < 0 else 'no'} |",
               f"| linear slope (all PR10) | {fmt(p['lin_b'])} (p {fp(p['lin_p'])}) | (rival R1) | – |",
               f"| self-repetition slope (T6) | {fmt(p['sr_b'])} (p {fp(p['sr_p'])}) | < 0 | {'yes' if p['sr_b'] < 0 else 'no'} |"]
        body = (f"Agent-days {p['n']} · agents {p['G']} · outcome log(1 + write turns), mean writes/agent-day {p['mean_writes']:.1f}.\n\n"
                + "\n".join(tab) + f"\n\n**Verdict: {p['verdict']}.** {p['why']}\n\n"
                f"Figure: `figures/G{g:02d}_curve.pdf` (binned partial residuals and spline).\n")
        txt = re.sub(r"<!-- RESULT -->.*?(?=\n## Scorecard)", "<!-- RESULT -->\n" + body, txt, flags=re.S)
        sc = (f"- **C (adequacy):** within-period linear vs curved not separately cross-validated (pooled CV in the card).\n"
              f"- **D (unfitted):** self-repetition slope {fmt(p['sr_b'])} (p {p['sr_p']:.3f}).\n"
              f"- **I (transfer):** sign pattern b₁ > 0, b₂ < 0 {'not estimable' if b1 is None else ('present' if (b1 > 0 and b2 < 0) else 'absent')}.\n")
        txt = re.sub(r"<!-- SCORECARD -->.*?(?=\n## Notes)", "<!-- SCORECARD -->\n" + sc, txt, flags=re.S)
        if "results filled" not in txt:
            txt = txt.rstrip("\n") + f"\n- {res['run_date']}: results filled by `analysis/evaluate.py` + `write_period_folders.py results`.\n"
        f.write_text(txt)
    print(f"filled {len(per)} period folders")


if __name__ == "__main__":
    {"predict": predict, "results": results}[sys.argv[1]]()
