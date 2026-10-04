# H45 × G38: Choose a charity and raise as much money as you can for it (2026-04-02 → 2026-04-24)

**Verdict:** failed (RI 0.05 [0.02, 0.07])
**Role:** replication
**Period:** regime III · 14 agents with calls · rooms [2, 3] · 17 non-holdout days. Units (shared `period_units`): 38a (goal_start), 38b (ne:NE17), 38c (roster_join:Claude Opus 4.7), 38d (ne:NE18), 38e (roster_join:Kimi K2.6).

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
| P1 RI ≥ 0.5 | RI 0.05 [0.02, 0.07] (ε 0.90 [0.87, 0.92]; η_W 0.04 [0.02, 0.06]; 2500 segments, 14 agents) | passive ε = 1 − s̄ = 0.94, RI 0 | not met |
| P3 CV ratio ≤ 0.5 | CV 0.60 vs W-permuted 0.64 (ratio 0.94, p_lower 0.005) | ratio 1 | not met |
| P2 lever slope < 0 (A1) | 0.04 [0.01, 0.06] (496 voluntary segments) | 0 | not met |
| P4 β ∈ [0.4, 0.9] | β 0.97 [0.90, 1.03] (3127 talk calls, reply rate 0.43) | 0 (constant uptake), 1 (fixed budget) | not met |
| P5 γ_R < 0, γ_W > 0 | γ_R 0.027 [-0.088, 0.107]; γ_W -0.290 [-0.538, -0.079] (3095 cu talk calls) | 0, 0 (passive); −, − (competition) | not met |
| P6 overshoot ≥ 1.2 | forced 0.69 [0.56, 0.82], τ 3.0 calls (2338 segments); voluntary 0.78 [0.64, 0.97] | 1 | not met |
| P8 P growth ≥ 1.3 | 2.04 (IQR 1.82–2.19; 1929 segments) | ≈ 1 under truncation | met |
| set points | s\* median 0.051 (range 0.017–0.116, 13 agents) | – | descriptive |

**Reading.** The room share at mid-segment positions follows inflow: ε 0.90 against the passive 0.94, so RI 0.05, and own content does not respond (η_W 0.04). Reply engagement dilutes with β 0.97 (a literal one-reply-per-talk budget). Engagement falls with own content (γ_W -0.29) and does not change detectably with old room content (γ_R; per-period γ is not identified, Amendment A2). After forced erasures the agents talk less (k-adjusted ratio 0.69), the opposite of an import overshoot. Numbers: `data/processed/H45-context-homeostasis/G38/results.json` (`analysis/run_periods.py`). Cross-period figures: `figures/`.

## Scorecard (period-specific axes)
- **C:** RI against the passive benchmark (day-cluster bootstrap): does not beat passive.
- **D:** unfitted statistics: P growth consistent with accumulation; β outside the predicted band.
- **E:** forced erasures (NE41) as interventions: overshoot not met.

## Notes
- 2026-10-04 06:21 UTC: folder and templated prediction written before the real-data run.
- 2026-10-04 06:46 UTC: card Amendments A1–A3 apply (made after the synthetic validation, before any real data): P2 judged by sign; verdict by P1 alone; P6 needs its CI above 1.
- 2026-10-04: results filled from `analysis/run_periods.py` (exploratory, non-holdout).
