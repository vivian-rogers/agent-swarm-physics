# H45 × G16: Choose your own goal! (2025-10-06 → 2025-10-10)

**Verdict:** failed (RI -0.04 [-0.07, -0.01])
**Role:** replication
**Period:** regime I · 7 agents with calls · rooms [0] · 5 non-holdout days. Units (shared `period_units`): 16 (goal_start).

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
| P1 RI ≥ 0.5 | RI -0.04 [-0.07, -0.01] (ε 0.90 [0.88, 0.92]; η_W -0.03 [-0.04, -0.01]; 247 segments, 7 agents) | passive ε = 1 − s̄ = 0.87, RI 0 | not met |
| P3 CV ratio ≤ 0.5 | CV 0.50 vs W-permuted 0.50 (ratio 1.00, p_lower 0.577) | ratio 1 | not met |
| P2 lever slope < 0 (A1) | -0.08 [-0.13, -0.03] (291 voluntary segments) | 0 | met |
| P4 β ∈ [0.4, 0.9] | β 0.71 [0.53, 0.87] (1552 talk calls, reply rate 0.13) | 0 (constant uptake), 1 (fixed budget) | met |
| P8 P growth ≥ 1.3 | 2.33 (IQR 1.91–2.43; 161 segments) | ≈ 1 under truncation | met |
| set points | s\* median 0.075 (range 0.066–0.137, 4 agents) | – | descriptive |

**Reading.** The room share at mid-segment positions follows inflow: ε 0.90 against the passive 0.87, so RI -0.04, and own content does not respond (η_W -0.03). Reply engagement dilutes with β 0.71. Numbers: `data/processed/H45-context-homeostasis/G16/results.json` (`analysis/run_periods.py`). Cross-period figures: `figures/`.

## Scorecard (period-specific axes)
- **C:** RI against the passive benchmark (day-cluster bootstrap): does not beat passive.
- **D:** unfitted statistics: P growth consistent with accumulation; β in the predicted band.

## Notes
- 2026-10-04 06:21 UTC: folder and templated prediction written before the real-data run.
- 2026-10-04 06:46 UTC: card Amendments A1–A3 apply (made after the synthetic validation, before any real data): P2 judged by sign; verdict by P1 alone; P6 needs its CI above 1.
- 2026-10-04: results filled from `analysis/run_periods.py` (exploratory, non-holdout).
