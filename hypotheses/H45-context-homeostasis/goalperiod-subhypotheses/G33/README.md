# H45 × G33: Discuss, debate, and act on your views about the recent Pentagon-AI company news (2026-03-02 → 2026-03-04)

**Verdict:** failed (RI 0.08 [0.01, 0.11])
**Role:** replication
**Period:** regime II · 11 agents with calls · rooms [0] · 3 non-holdout days. Units (shared `period_units`): 33 (goal_start).

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
| P1 RI ≥ 0.5 | RI 0.08 [0.01, 0.11] (ε 0.73 [0.70, 0.79]; η_W 0.08 [0.03, 0.10]; 370 segments, 11 agents) | passive ε = 1 − s̄ = 0.79, RI 0 | not met |
| P3 CV ratio ≤ 0.5 | CV 0.46 vs W-permuted 0.49 (ratio 0.94, p_lower 0.005) | ratio 1 | not met |
| P2 lever slope < 0 (A1) | -0.01 [-0.02, -0.00] (444 voluntary segments) | 0 | met |
| P4 β ∈ [0.4, 0.9] | β 0.92 [0.88, 0.97] (1688 talk calls, reply rate 0.35) | 0 (constant uptake), 1 (fixed budget) | not met |
| P5 γ_R < 0, γ_W > 0 | γ_R 0.233 [0.143, 0.451]; γ_W -0.369 [-0.749, -0.058] (532 cu talk calls) | 0, 0 (passive); −, − (competition) | not met |
| P8 P growth ≥ 1.3 | 2.23 (IQR 1.93–2.48; 178 segments) | ≈ 1 under truncation | met |
| set points | s\* median 0.169 (range 0.121–0.285, 8 agents) | – | descriptive |

**Reading.** The room share at mid-segment positions follows inflow: ε 0.73 against the passive 0.79, so RI 0.08, and own content does not respond (η_W 0.08). Reply engagement dilutes with β 0.92 (a literal one-reply-per-talk budget). Engagement falls with own content (γ_W -0.37) and rises with old room content (γ_R; per-period γ is not identified, Amendment A2). Numbers: `data/processed/H45-context-homeostasis/G33/results.json` (`analysis/run_periods.py`). Cross-period figures: `figures/`.

## Scorecard (period-specific axes)
- **C:** RI against the passive benchmark (day-cluster bootstrap): does not beat passive.
- **D:** unfitted statistics: P growth consistent with accumulation; β outside the predicted band.

## Notes
- 2026-10-04 06:21 UTC: folder and templated prediction written before the real-data run.
- 2026-10-04 06:46 UTC: card Amendments A1–A3 apply (made after the synthetic validation, before any real data): P2 judged by sign; verdict by P1 alone; P6 needs its CI above 1.
- 2026-10-04: results filled from `analysis/run_periods.py` (exploratory, non-holdout).
