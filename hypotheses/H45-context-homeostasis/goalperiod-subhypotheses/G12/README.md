# H45 × G12: Form two teams and debate each other, while one agent judges. Choose your teammates wisely (2025-09-01 → 2025-09-05)

**Verdict:** failed (RI -0.07 [-0.10, -0.03])
**Role:** replication
**Period:** regime I · 7 agents with calls · rooms [0] · 5 non-holdout days. Units (shared `period_units`): 12a (goal_start), 12b (ne:NE04).

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
| P1 RI ≥ 0.5 | RI -0.07 [-0.10, -0.03] (ε 0.84 [0.82, 0.86]; η_W -0.09 [-0.12, -0.06]; 227 segments, 7 agents) | passive ε = 1 − s̄ = 0.79, RI 0 | not met |
| P3 CV ratio ≤ 0.5 | CV 0.49 vs W-permuted 0.47 (ratio 1.04, p_lower 0.826) | ratio 1 | not met |
| P2 lever slope < 0 (A1) | -0.11 [-0.17, -0.04] (252 voluntary segments) | 0 | met |
| P4 β ∈ [0.4, 0.9] | β 0.54 [0.43, 0.66] (3239 talk calls, reply rate 0.15) | 0 (constant uptake), 1 (fixed budget) | met |
| P8 P growth ≥ 1.3 | 2.37 (IQR 1.78–2.51; 104 segments) | ≈ 1 under truncation | met |
| set points | s\* median 0.166 (range 0.077–0.399, 7 agents) | – | descriptive |

**Reading.** The room share at mid-segment positions follows inflow: ε 0.84 against the passive 0.79, so RI -0.07, and own content does not respond (η_W -0.09). Reply engagement dilutes with β 0.54. Numbers: `data/processed/H45-context-homeostasis/G12/results.json` (`analysis/run_periods.py`). Cross-period figures: `figures/`.

## Scorecard (period-specific axes)
- **C:** RI against the passive benchmark (day-cluster bootstrap): does not beat passive.
- **D:** unfitted statistics: P growth consistent with accumulation; β in the predicted band.

## Notes
- 2026-10-04 06:21 UTC: folder and templated prediction written before the real-data run.
- 2026-10-04 06:46 UTC: card Amendments A1–A3 apply (made after the synthetic validation, before any real data): P2 judged by sign; verdict by P1 alone; P6 needs its CI above 1.
- 2026-10-04: results filled from `analysis/run_periods.py` (exploratory, non-holdout).
