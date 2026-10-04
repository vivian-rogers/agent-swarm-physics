# H84 × G38: Choose a charity and raise as much money as you can for it (2026-04-02 → 2026-04-24)

**Verdict:** failed
**Role:** replication (exploratory)
**Period:** regime III · 10 searching agents · 17 days with mapped search calls · units 38a, 38b, 38c, 38d, 38e.

## Why this period
A replication point for the common estimator (layer 1): the search channel's allocation information I_Q at search calls, on every regime-III non-holdout period with ≥ 30 mapped search calls. It is the I side of κ_Q; the value side is identified only at the G37 outage.

## Prediction
*Templated replication prediction, written 2026-10-04 ~20:05 UTC in the card (row R), before running on this period.*
- I_Q = I(X⁺; S_Q) at search calls (X⁺ = repo of the first work commit in the next 20 calls; S_Q = repo most named by the answer), Miller–Madow plug-in minus the within-agent permutation floor (200 permutations), CI from an agent-day cluster bootstrap (300 draws).
- **Verdict rule:** supported if permutation p < 0.05; failed if p ≥ 0.05 with ≥ 100 search calls; descriptive if fewer than 100.
- *Counts against:* I_Q not above the permutation floor.

## Result
*Run 2026-10-04 20:20 UTC (`analysis/run.py` → `results/results.json`, block `replication`).*
- n = 219 search calls (≥ 10 calls of window), 51 agent-days.
- I_Q = 0.031 bits [-0.024, 0.107]; raw plug-in 0.091, floor 0.060; permutation p 0.070.
- Answers naming a work repo: 10.5%; naming the agent's own artifact: 6.8%.
- P(return to own artifact) 1.00 when the answer names it (n 6) vs 0.80 otherwise (n 59).
- **Templated verdict:** failed.

## Scorecard (period-specific axes)
- Replication point only (layer 1): informs C (beats the permutation floor) and I (consistency across periods) in the main card.
