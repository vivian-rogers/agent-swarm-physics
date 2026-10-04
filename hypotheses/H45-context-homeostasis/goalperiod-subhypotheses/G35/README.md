# H45 × G35: Test your game to make it as fun and functional as you can! (2026-03-16 → 2026-03-20)

**Verdict:** failed (RI 0.08 [0.04, 0.11])
**Role:** replication
**Period:** regime II · 12 agents with calls · rooms [0, 2, 3] · 5 non-holdout days. Units (shared `period_units`): 35 (goal_start).

## Why this period
Replication layer: the common H45 estimators on every eligible goal period (≥ 3 agents with ≥ 30 computer-use context segments carrying prompt tokens), so that each period is a comparable point on the phase diagram. Regime II: computer-use sessions plus chat mode; the consolidate tool arrives during NE14.

## Prediction
*Templated from the card's predictions (written 2026-10-04 06:21 UTC, before running H45 on any period; replication layer).*
- **P1 (primary):** regulation index RI = 1 − ε/(1 − s̄) ≥ 0.5 with the day-bootstrap CI excluding 0 (agent × unit fixed effects, band positions 15–35). Passive accumulation: RI ≈ 0.
- **P3 (band):** within-agent CV of segment band shares ≤ 0.5 × the CV after permuting own content across the agent's segments.
- **P4:** dilution exponent β (reply-parent engagement, cloglog with agent-day effects) ∈ [0.4, 0.9], CI excluding 0.
- **P8:** P(j 30–35)/P(j 8–12) ≥ 1.3 (no truncation plateau).
- **P5 (homeostat signature):** γ_R < 0 and γ_W > 0, both CIs excluding 0 (cu talk calls).
- **P2 (session lever, regimes I–II):** among segments ended by the agent's own session stop, slope of ln L on ln(early inflow) ≤ −0.3.
- **Verdict rule:** supported if P1 holds and (where testable) P5's sign pattern holds; failed if the RI CI's upper bound is < 0.5 and P5 does not show the controller pattern; mixed otherwise.
- **Against H45:** RI ≈ 0 (the share tracks inflow).

## Result
| Prediction | Observed | Null / reference | Outcome |
| --- | --- | --- | --- |
| P1 RI ≥ 0.5 | RI 0.08 [0.04, 0.11] (ε 0.85 [0.82, 0.89]; η_W 0.09 [0.05, 0.13]; 834 segments, 12 agents) | passive ε = 1 − s̄ = 0.92, RI 0 | not met |
| P3 CV ratio ≤ 0.5 | CV 0.47 vs W-permuted 0.50 (ratio 0.93, p_lower 0.005) | ratio 1 | not met |
| P2 lever slope < 0 (A1) | -0.00 [-0.01, 0.01] (959 voluntary segments) | 0 | not met |
| P4 β ∈ [0.4, 0.9] | β 0.97 [0.89, 1.03] (1756 talk calls, reply rate 0.44) | 0 (constant uptake), 1 (fixed budget) | not met |
| P5 γ_R < 0, γ_W > 0 | γ_R -0.048 [-0.133, 0.100]; γ_W -0.341 [-0.812, 0.227] (843 cu talk calls) | 0, 0 (passive); −, − (competition) | not met |
| P8 P growth ≥ 1.3 | 2.10 (IQR 1.81–2.33; 595 segments) | ≈ 1 under truncation | met |
| set points | s\* median 0.067 (range 0.019–0.127, 9 agents) | – | descriptive |

**Reading.** The room share at mid-segment positions follows inflow: ε 0.85 against the passive 0.92, so RI 0.08, and own content does not respond (η_W 0.09). Reply engagement dilutes with β 0.97 (a literal one-reply-per-talk budget). Engagement does not change detectably with own content (γ_W -0.34) and does not change detectably with old room content (γ_R; per-period γ is not identified, Amendment A2). Numbers: `data/processed/H45-context-homeostasis/G35/results.json` (`analysis/run_periods.py`). Cross-period figures: `figures/`.

## Scorecard (period-specific axes)
- **C:** RI against the passive benchmark (day-cluster bootstrap): does not beat passive.
- **D:** unfitted statistics: P growth consistent with accumulation; β outside the predicted band.

## Notes
- 2026-10-04 06:21 UTC: folder and templated prediction written before the real-data run.
- 2026-10-04 06:46 UTC: card Amendments A1–A3 apply (made after the synthetic validation, before any real data): P2 judged by sign; verdict by P1 alone; P6 needs its CI above 1.
- 2026-10-04: results filled from `analysis/run_periods.py` (exploratory, non-holdout).
