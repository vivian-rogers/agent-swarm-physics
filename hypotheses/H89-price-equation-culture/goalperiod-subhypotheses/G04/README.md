# H89 × G04: Write a story and celebrate it with 100 people in person (2025-05-15 → 2025-06-19)

**Verdict:** supported
**Role:** replication
**Period:** regime I · mode C · 4 agents · non-holdout days only (held-out days masked with `holdout_mask`).

## Why this period
Replication layer: the common H89 estimator (cross-fitted Price partition of day-to-day change of the active population's mean trait) on every non-holdout period with H34 ideas, so periods compare as points on a phase diagram.

## Prediction
*Written 2026-10-04 20:35 UTC, before running on this period* (after the card's predictions at 20:15 UTC and amendments A1–A5 at 20:30 UTC; no real-data Price share had been computed for any period).

| # | Prediction here | Counts against |
| --- | --- | --- |
| c1 (P1) | style moves more by migration than content does: s_Mig(style) > s_Mig(content, bge) | s_Mig(style) ≤ s_Mig(content) |
| c2 (P2) | content moves by transmission: s_Trans(content, bge) ≥ 0.5 and the largest term | s_Trans < 0.5 or another term larger |
| c3 (P3) | selection is not a material share: \|s_Sel\| ≤ 0.2 for content, style and conventions | \|s_Sel\| > 0.2 for any reliable trait |
| P5 | residual R (content) ≥ 0.1 with jackknife CI > 0 | CI includes 0 (migration + kickoff explain the change) |
| P6 | persistence C (content) > 0 with CI > 0 (periods with ≥ 4 transitions) | C ≤ 0 |

**Verdict rule (card, A1):** supported = c1, c2 and c3; failed = none; mixed = otherwise; n/a = not eligible (< 2 transitions with ≥ 3 stayers or < 20 in-cone adoptions by stayers) or content or style reliability ρ_Δ < 0.3. P5 and P6 are reported, not voted here.

## Result
**supported.** 24 day transitions; 6 agents, 99 active agent-days; 786 in-cone adoptions by stayers (mean social weight λ̄ 0.28, SD of w 0.30); 4 roster and 2 presence entries/exits. Reliability ρ_Δ: content 0.86, style 0.75, conventions 0.86.

| Prediction | Observed (energy shares; jackknife 95% CI) | Null / reference | Verdict |
| --- | --- | --- | --- |
| c1 s_Mig(style) > s_Mig(content) | style +0.10 [-0.08, +0.28]; content +0.00 [-0.00, +0.01] (implied day-field fraction φ̂: style 0.07779481513839767, content >0.5) | synthetic: s_Mig 0.5 needs φ ≈ 0.01 | pass |
| c2 s_Trans(content) ≥ 0.5, largest | bge +1.00 [+0.96, +1.04]; gte +0.99 [+0.96, +1.03]; self / social +0.72 / +0.28 | field-only rival R1 | pass |
| c3 \|s_Sel\| ≤ 0.2 | content -0.005 (p 0.65); style +0.015 (p 0.58); conventions +0.047 (p 0.00; leave-trait-out +0.043) | w-permutation (A2) | pass |
| P5 residual R ≥ 0.1, CI > 0 | bge +0.91 [+0.84, +0.99]; gte +0.91 [+0.84, +0.98]; kickoff share +0.081 | kill: CI ∋ 0 | reported |
| P6 persistence C > 0 | content -0.34 [-0.42, -0.25] (drift ratio δ²/s +0.25); style -0.43 | iid topics −0.5 | reported |
| P4 convergence placebo | 48 unread-placebo adoptions; placebo s_Sel +0.002, s_Trans,social +0.016 (read: +0.277) | read vs in flight | descriptive |

Cumulative (net change over the period, descriptive, A5): s_Mig style +0.31, content -0.01; s_Sel content -0.30. Migration split (energy): style roster +0.021 / presence +0.079.


## Scorecard (period-specific axes)
C (adequacy): energy shares cross-fitted between message halves (synthetic bias ≤ 0.03 at ρ ≥ 0.3); selection against the w-permutation null. D (unfitted): the style vs content migration ordering. E, G: not informed by this replication.

## Notes
- Data: `data/processed/H89-price-equation-culture/traits/G04.npz`, `adoptions.parquet`.
