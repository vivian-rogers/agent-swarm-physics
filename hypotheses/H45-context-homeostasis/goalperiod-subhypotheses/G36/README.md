# H45 × G36: Interact with other AI agents outside the Village! (2026-03-23 → 2026-03-27)

**Verdict:** failed (RI 0.05 [-0.02, 0.13])
**Role:** replication
**Period:** regime II/III · 12 agents with calls · rooms [0, 2, 3] · 5 non-holdout days. Units (shared `period_units`): 36a (goal_start), 36b (ne:NE14; ne:NE41), 36c (ne:NE16).

## Why this period
Replication layer: the common H45 estimators on every eligible goal period (≥ 3 agents with ≥ 30 computer-use context segments carrying prompt tokens), so that each period is a comparable point on the phase diagram. Regime III: one continuous computer-use context per agent, erased by forced (41-call cap, NE41) and voluntary consolidations; talk happens inside that context, so every test applies.

## Prediction
*Templated from the card's predictions (written 2026-10-04 06:21 UTC, before running H45 on any period; replication layer).*
- **P1 (primary):** regulation index RI = 1 − ε/(1 − s̄) ≥ 0.5 with the day-bootstrap CI excluding 0 (agent × unit fixed effects, band positions 15–35). Passive accumulation: RI ≈ 0.
- **P3 (band):** within-agent CV of segment band shares ≤ 0.5 × the CV after permuting own content across the agent's segments.
- **P4:** dilution exponent β (reply-parent engagement, cloglog with agent-day effects) ∈ [0.4, 0.9], CI excluding 0.
- **P8:** P(j 30–35)/P(j 8–12) ≥ 1.3 (no truncation plateau).
- **P5 (homeostat signature):** γ_R < 0 and γ_W > 0, both CIs excluding 0 (cu talk calls).
- **P2 (consolidation lever):** among voluntarily ended segments, slope of ln L on ln(early inflow) ≤ −0.3.
- **P6 (post-erasure overshoot):** k-adjusted talk propensity in calls 1–3 after a forced reset ≥ 1.2 × the j 20–40 baseline, τ ≤ 10 calls.
- **Verdict rule:** supported if P1 holds and (where testable) P5's sign pattern holds; failed if the RI CI's upper bound is < 0.5 and P5 does not show the controller pattern; mixed otherwise.
- **Against H45:** RI ≈ 0 (the share tracks inflow).

## Result
| Prediction | Observed | Null / reference | Outcome |
| --- | --- | --- | --- |
| P1 RI ≥ 0.5 | RI 0.05 [-0.02, 0.13] (ε 0.89 [0.82, 0.95]; η_W 0.06 [-0.00, 0.14]; 755 segments, 11 agents) | passive ε = 1 − s̄ = 0.93, RI 0 | not met |
| P3 CV ratio ≤ 0.5 | CV 0.58 vs W-permuted 0.61 (ratio 0.95, p_lower 0.030) | ratio 1 | not met |
| P2 lever slope < 0 (A1) | -0.02 [-0.05, -0.00] (375 voluntary segments) | 0 | met |
| P4 β ∈ [0.4, 0.9] | β 1.12 [0.99, 1.27] (1164 talk calls, reply rate 0.43) | 0 (constant uptake), 1 (fixed budget) | not met |
| P5 γ_R < 0, γ_W > 0 | γ_R 0.332 [0.010, 0.681]; γ_W -0.466 [-0.759, -0.185] (967 cu talk calls) | 0, 0 (passive); −, − (competition) | not met |
| P6 overshoot ≥ 1.2 | forced 0.51 [0.35, 0.64], τ 13.8 calls (507 segments); voluntary 0.65 [0.23, 1.23] | 1 | not met |
| P8 P growth ≥ 1.3 | 2.05 (IQR 1.81–2.26; 512 segments) | ≈ 1 under truncation | met |
| set points | s\* median 0.061 (range 0.021–0.105, 10 agents) | – | descriptive |

**Reading.** The room share at mid-segment positions follows inflow: ε 0.89 against the passive 0.93, so RI 0.05, and own content does not respond (η_W 0.06). Reply engagement dilutes with β 1.12 (a literal one-reply-per-talk budget). Engagement falls with own content (γ_W -0.47) and rises with old room content (γ_R; per-period γ is not identified, Amendment A2). After forced erasures the agents talk less (k-adjusted ratio 0.51), the opposite of an import overshoot. Numbers: `data/processed/H45-context-homeostasis/G36/results.json` (`analysis/run_periods.py`). Cross-period figures: `figures/`.

## Scorecard (period-specific axes)
- **C:** RI against the passive benchmark (day-cluster bootstrap): does not beat passive.
- **D:** unfitted statistics: P growth consistent with accumulation; β outside the predicted band.
- **E:** forced erasures (NE41) as interventions: overshoot not met.

## Notes
- 2026-10-04 06:21 UTC: folder and templated prediction written before the real-data run.
- 2026-10-04 06:46 UTC: card Amendments A1–A3 apply (made after the synthetic validation, before any real data): P2 judged by sign; verdict by P1 alone; P6 needs its CI above 1.
- 2026-10-04: results filled from `analysis/run_periods.py` (exploratory, non-holdout).
