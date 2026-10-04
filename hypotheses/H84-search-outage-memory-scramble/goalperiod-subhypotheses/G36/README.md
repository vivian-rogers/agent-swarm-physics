# H84 × G36: Interact with other AI agents outside the Village! (2026-03-24 → 2026-03-27)

**Verdict:** supported
**Role:** replication (exploratory)
**Period:** regime III · 8 searching agents · 4 days with mapped search calls · units 36b, 36c.

## Why this period
A replication point for the common estimator (layer 1): the search channel's allocation information I_Q at search calls, on every regime-III non-holdout period with ≥ 30 mapped search calls. It is the I side of κ_Q; the value side is identified only at the G37 outage.

## Prediction
*Templated replication prediction, written 2026-10-04 ~20:05 UTC in the card (row R), before running on this period.*
- I_Q = I(X⁺; S_Q) at search calls (X⁺ = repo of the first work commit in the next 20 calls; S_Q = repo most named by the answer), Miller–Madow plug-in minus the within-agent permutation floor (200 permutations), CI from an agent-day cluster bootstrap (300 draws).
- **Verdict rule:** supported if permutation p < 0.05; failed if p ≥ 0.05 with ≥ 100 search calls; descriptive if fewer than 100.
- *Counts against:* I_Q not above the permutation floor.

## Result
*Run 2026-10-04 20:20 UTC (`analysis/run.py` → `results/results.json`, block `replication`).*
- n = 50 search calls (≥ 10 calls of window), 12 agent-days.
- I_Q = 0.256 bits [-0.037, 0.604]; raw plug-in 0.398, floor 0.142; permutation p 0.005.
- Answers naming a work repo: 38.0%; naming the agent's own artifact: 12.0%.
- Too few search calls with a commit to compare return rates.
- **Templated verdict:** supported.

## Scorecard (period-specific axes)
- Replication point only (layer 1): informs C (beats the permutation floor) and I (consistency across periods) in the main card.
