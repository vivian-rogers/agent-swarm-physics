# H45 × G04: Write a story and celebrate it with 100 people in person (2025-05-15 → 2025-06-18)

**Verdict:** failed (RI -0.02 [-0.05, 0.01])
**Role:** replication
**Period:** regime I · 6 agents with calls · rooms [0] · 25 non-holdout days. Units (shared `period_units`): 4a (goal_start), 4b (roster_join:o4-mini; roster_leave:GPT-4.1), 4c (roster_join:Claude Opus 4; roster_leave:o4-mini), 4d (outage:300min).

## Why this period
Replication layer: the common H45 estimators on every eligible goal period (≥ 3 agents with ≥ 30 computer-use context segments carrying prompt tokens), so that each period is a comparable point on the phase diagram. Regime I: computer-use sessions (reset by the agent's own session stop) beside chat mode; talk happens in chat mode, whose prompt the scaffold rebuilds from recent chat, so the share-dependence test (P5) and the forced-erasure test (P6) do not apply.

## Prediction
*Templated from the card's predictions (written 2026-10-04 06:21 UTC, before running H45 on any period; replication layer).*
- **P1 (primary):** regulation index RI = 1 − ε/(1 − s̄) ≥ 0.5 with the day-bootstrap CI excluding 0 (agent × unit fixed effects, band positions 15–35). Passive accumulation: RI ≈ 0.
- **P3 (band):** within-agent CV of segment band shares ≤ 0.5 × the CV after permuting own content across the agent's segments.
- **P4:** dilution exponent β (reply-parent engagement, cloglog with agent-day effects) ∈ [0.4, 0.9], CI excluding 0.
- **P8:** P(j 30–35)/P(j 8–12) ≥ 1.3 (no truncation plateau).
- **P2 (session lever, regimes I–II):** among segments ended by the agent's own session stop, slope of ln L on ln(early inflow) ≤ −0.3.
- **Verdict rule:** supported if P1 holds and (where testable) P5's sign pattern holds; failed if the RI CI's upper bound is < 0.5 and P5 does not show the controller pattern; mixed otherwise.
- **Against H45:** RI ≈ 0 (the share tracks inflow).

## Result
| Prediction | Observed | Null / reference | Outcome |
| --- | --- | --- | --- |
| P1 RI ≥ 0.5 | RI -0.02 [-0.05, 0.01] (ε 0.91 [0.88, 0.93]; η_W -0.03 [-0.06, -0.01]; 665 segments, 6 agents) | passive ε = 1 − s̄ = 0.89, RI 0 | not met |
| P3 CV ratio ≤ 0.5 | CV 0.61 vs W-permuted 0.59 (ratio 1.02, p_lower 0.935) | ratio 1 | not met |
| P2 lever slope < 0 (A1) | -0.01 [-0.05, 0.03] (643 voluntary segments) | 0 | not met |
| P4 β ∈ [0.4, 0.9] | β 0.74 [0.65, 0.81] (5301 talk calls, reply rate 0.30) | 0 (constant uptake), 1 (fixed budget) | met |
| P8 P growth ≥ 1.3 | 2.41 (IQR 1.89–2.50; 398 segments) | ≈ 1 under truncation | met |
| set points | s\* median 0.128 (range 0.057–0.227, 5 agents) | – | descriptive |

**Reading.** The room share at mid-segment positions follows inflow: ε 0.91 against the passive 0.89, so RI -0.02, and own content does not respond (η_W -0.03). Reply engagement dilutes with β 0.74. Numbers: `data/processed/H45-context-homeostasis/G04/results.json` (`analysis/run_periods.py`). Cross-period figures: `figures/`.

## Scorecard (period-specific axes)
- **C:** RI against the passive benchmark (day-cluster bootstrap): does not beat passive.
- **D:** unfitted statistics: P growth consistent with accumulation; β in the predicted band.

## Notes
- 2026-10-04 06:21 UTC: folder and templated prediction written before the real-data run.
- 2026-10-04 06:46 UTC: card Amendments A1–A3 apply (made after the synthetic validation, before any real data): P2 judged by sign; verdict by P1 alone; P6 needs its CI above 1.
- 2026-10-04: results filled from `analysis/run_periods.py` (exploratory, non-holdout).
