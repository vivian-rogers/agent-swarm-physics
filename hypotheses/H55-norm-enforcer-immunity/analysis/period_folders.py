"""Write replication-layer period READMEs (role `replication`) from replication/per_period.parquet.
Native periods (G51, G12, G16, G38) have hand-written READMEs; for them this script only appends nothing.
  uv run python hypotheses/H55-norm-enforcer-immunity/analysis/period_folders.py
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scheme"))
import h55common as H  # noqa: E402

import polars as pl  # noqa: E402

NATIVE = {12, 16, 38, 51}
GP = H.HDIR / "goalperiod-subhypotheses"


def titles():
    t = {}
    txt = (H.ROOT / "hypotheses/hypohypotheses/period-affordances.md").read_text().splitlines()
    for i, line in enumerate(txt):
        m = re.match(r"### G(\d+) · (.+?)( 🔒)?$", line)
        if m:
            dates = txt[i + 1].split("·")[0].strip().strip("`") if i + 1 < len(txt) else ""
            t[int(m.group(1))] = (m.group(2).strip(), dates)
    return t


def fmt(x, d=2):
    if x is None:
        return "–"
    try:
        return f"{x:.{d}f}"
    except Exception:
        return str(x)


def verdict(r):
    tests = []
    if r.get("P1_scorable"):
        tests.append(r["P1_rho"] > 0 and r["P1_p"] < 0.05)
    if r.get("P2_scorable"):
        tests.append(r["P2_gamma"] < 0 and r["P2_p"] < 0.05)
    if not tests:
        return "descriptive"
    if all(tests):
        return "supported"
    if any(tests):
        return "mixed"
    return "failed"


def main():
    df = pl.read_parquet(H.OUT / "replication/per_period.parquet")
    T = titles()
    pu = pl.read_parquet(H.SH / "period_units.parquet").filter(~pl.col("holdout"))
    for r in df.iter_rows(named=True):
        g = r["goal_no"]
        if g in NATIVE:
            continue
        title, dates = T.get(g, (f"goal period {g}", ""))
        units = pu.filter(pl.col("goal_no") == g)
        ndays = int(units["n_days"].sum()) if units.height else 0
        nag = int(units["n_agents"].max()) if units.height else 0
        v = verdict(r)
        d = GP / f"G{g:02d}"
        d.mkdir(parents=True, exist_ok=True)
        lines = [
            f"# H55 × G{g:02d}: {title} ({dates})", "",
            f"**Verdict:** {v}",
            "**Role:** replication",
            f"**Period:** regime {r['regime']} · up to {nag} agents · {ndays} non-holdout days · units {', '.join(units['unit_id'].to_list()) or '–'}"
            " (matching strata are within unit).", "",
            "## Why this period",
            "Replication layer: the common H55 estimators on every non-holdout goal period with DQ2 reply labels, giving one "
            "comparable point per period (enforcer friction, correction rate, loop persistence, address effect). Per-period immune "
            "contrasts need ≥ 15 steps with a directed correction read; no period reaches that, so corrections' effect on escape is "
            "estimated only across periods (card, Amendment 1 and Results).", "",
            "## Prediction",
            "*Templated: the card's P1, P2, P4–P8, written 2026-10-04 06:26 UTC before any H55 outcome statistic.*",
            "- P1: Spearman ρ(correction rate c_j, received field ν_j) > 0 (agent permutation, one-sided p < 0.05), if ≥ 6 agents qualify.",
            "- P2: replies to an agent's corrections are more negative than replies to its other messages (γ < 0, p < 0.05), if ≥ 20 such replies.",
            "- P4/P5/P6: corrections read in a loop or blocked spell raise escape; any directed read raises escape (descriptive per period).",
            "- **Per-period verdict rule:** supported if every scorable primary test (P1, P2) passes; mixed if some do; failed if none does; "
            "descriptive if neither is scorable.", "",
            "## Result",
            f"*Run 2026-10-04 (`analysis/explore.py`; data `data/processed/H55-norm-enforcer-immunity/G{g:02d}/results.json`).*", "",
            "| Statistic | Observed | Predicted |", "| --- | --- | --- |",
            f"| P1 ρ(c_j, ν_j) | {fmt(r['P1_rho'])} (p {fmt(r['P1_p'], 3)}; {r.get('P1_n_agents') or 0} agents){'' if r.get('P1_scorable') else ' — not scorable: ' + str(r.get('P1_why'))} | > 0 |",
            f"| P1b partial ρ (own speaker field removed) | {fmt(r['P1_rho_partial'])} (p {fmt(r['P1_p_partial'], 3)}) | ≥ half of P1 |",
            f"| P2 γ (replies to corrections − other replies, soft stance, FE) | {fmt(r['P2_gamma'], 3)} [{fmt(r['P2_lo'], 3)}, {fmt(r['P2_hi'], 3)}] (p {fmt(r['P2_p'], 3)}; {r.get('P2_n_treated') or 0} replies){'' if r.get('P2_scorable') else ' — not scorable'} | < 0 |",
            f"| P2 placebo (long parents) γ | {fmt(r['P2_placebo_len_gamma'], 3)} (p {fmt(r['P2_placebo_len_p'], 3)}) | ≈ 0 |",
            f"| P3 share of confident received opposes that are correction/decline subtypes | {fmt(r['P3_corr_decl_share'])} (n {r['P3_n_opp']}) | ≥ 0.5 |",
            f"| Jev corrections per 100 parented agent messages (S_p) | {fmt(r['S_p'])} ({r['n_corr_jev']} of {r['n_parented']}) | – |",
            f"| Restatement loops: at-risk steps / with a directed read / with a correction read | {r['loopR_steps']} / {r['loopR_dir_steps']} / {r['loopR_trt_steps']} | – |",
            f"| Loop escape rate per step; mean episode length | {fmt(r['loopR_escape'])}; {fmt(r['loop_mean_len'])} | – |",
            f"| P6 address effect on loop escape (Δ, matched) | {fmt(r['loopR_addr_delta'], 3)} [{fmt(r['loopR_addr_lo'], 3)}, {fmt(r['loopR_addr_hi'], 3)}] (n {r['loopR_addr_n'] or 0}) | > 0 |",
            f"| v3 blocked spells: at-risk windows / with a directed read / with a correction read | {r['blk_steps']} / {r['blk_dir_steps']} / {r['blk_trt_steps']} | – |",
            f"| P6 address effect on blocked escape (Δ) | {fmt(r['blk_addr_delta'], 3)} (n {r['blk_addr_n'] or 0}) | > 0 |",
            "",
            "## Scorecard (period-specific axes)",
            "| Axis | Score | Evidence |", "| --- | --- | --- |",
            f"| C adequacy | {1 if v in ('supported', 'mixed') else 0} | P1/P2 against agent permutation and the within-target design |",
            "| D unfitted predictions | 0 | per-period immune contrast not scorable (too few correction reads) |", "",
            "## Notes",
            "- Corrections use the validated Jev sensor (precision 0.93, recall ≈ 0.1; card Amendment 1); c_j is a scaled rate.",
        ]
        (d / "README.md").write_text("\n".join(lines) + "\n")
    print("wrote", df.filter(~pl.col("goal_no").is_in(list(NATIVE))).height, "replication READMEs")


if __name__ == "__main__":
    main()
