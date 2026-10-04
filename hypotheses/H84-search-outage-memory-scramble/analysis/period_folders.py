"""Write the H84 replication period READMEs (G36, G38, G41, G42, G44) from results/results.json.
G37 and G51 are native folders; their replication numbers are written into those READMEs by hand.
Usage: uv run python hypotheses/H84-search-outage-memory-scramble/analysis/period_folders.py
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
H = ROOT / "hypotheses/H84-search-outage-memory-scramble/goalperiod-subhypotheses"
RES = ROOT / "data/processed/H84-search-outage-memory-scramble/results/results.json"
NATIVE = {"G37", "G51"}


def titles() -> dict:
    t = {}
    for line in (ROOT / "hypotheses/hypohypotheses/goal-periods.md").read_text().splitlines():
        m = re.match(r"^### (\d+) · (.+)$", line)
        if m:
            t[int(m.group(1))] = m.group(2).strip()
    return t


def main():
    rep = json.loads(RES.read_text())["replication"]
    tt = titles()
    for k, r in rep.items():
        if k.startswith("_") or k in NATIVE:
            continue
        g = int(k[1:])
        title = tt.get(g, f"goal #{g}")
        d = H / k
        (d / "figures").mkdir(parents=True, exist_ok=True)
        ret = (f"P(return to own artifact) {r['p_return_named']:.2f} when the answer names it (n {r['n_return_named']}) "
               f"vs {r['p_return_other']:.2f} otherwise (n {r['n_return_other']})."
               if r["p_return_named"] is not None and r["p_return_other"] is not None else
               "Too few search calls with a commit to compare return rates.")
        txt = f"""# H84 × {k}: {title} ({r['days'][0]} → {r['days'][1]})

**Verdict:** {r['verdict']}
**Role:** replication (exploratory)
**Period:** regime III · {r['n_agents']} searching agents · {r['days'][2]} days with mapped search calls · units {', '.join(r['units'])}.

## Why this period
A replication point for the common estimator (layer 1): the search channel's allocation information I_Q at search calls, on every regime-III non-holdout period with ≥ 30 mapped search calls. It is the I side of κ_Q; the value side is identified only at the G37 outage.

## Prediction
*Templated replication prediction, written 2026-10-04 ~20:05 UTC in the card (row R), before running on this period.*
- I_Q = I(X⁺; S_Q) at search calls (X⁺ = repo of the first work commit in the next 20 calls; S_Q = repo most named by the answer), Miller–Madow plug-in minus the within-agent permutation floor (200 permutations), CI from an agent-day cluster bootstrap (300 draws).
- **Verdict rule:** supported if permutation p < 0.05; failed if p ≥ 0.05 with ≥ 100 search calls; descriptive if fewer than 100.
- *Counts against:* I_Q not above the permutation floor.

## Result
*Run 2026-10-04 20:20 UTC (`analysis/run.py` → `results/results.json`, block `replication`).*
- n = {r['n']} search calls (≥ 10 calls of window), {r['n_clusters']} agent-days.
- I_Q = {r['I']:.3f} bits [{r['I_ci'][0]:.3f}, {r['I_ci'][1]:.3f}]; raw plug-in {r['I_raw']:.3f}, floor {r['I_floor']:.3f}; permutation p {r['p_perm']:.3f}.
- Answers naming a work repo: {r['named_share']:.1%}; naming the agent's own artifact: {r['open_share']:.1%}.
- {ret}
- **Templated verdict:** {r['verdict']}.

## Scorecard (period-specific axes)
- Replication point only (layer 1): informs C (beats the permutation floor) and I (consistency across periods) in the main card.
"""
        (d / "README.md").write_text(txt)
        print("wrote", d)


if __name__ == "__main__":
    main()
