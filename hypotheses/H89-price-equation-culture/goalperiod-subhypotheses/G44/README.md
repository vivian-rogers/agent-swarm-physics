# H89 × G44: Finetune your leader! (2026-05-26 → 2026-06-01)

**Verdict:** mixed
**Role:** replication
**Period:** regime III · mode C · 16 agents · non-holdout days only (held-out days masked with `holdout_mask`).

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
**mixed.** 3 day transitions; 16 agents, 52 active agent-days; 508 in-cone adoptions by stayers (mean social weight λ̄ 0.30, SD of w 0.37); 2 roster and 4 presence entries/exits. Reliability ρ_Δ: content 0.70, style 0.80, conventions 0.74.

| Prediction | Observed (energy shares; jackknife 95% CI) | Null / reference | Verdict |
| --- | --- | --- | --- |
| c1 s_Mig(style) > s_Mig(content) | style -0.02 [-0.07, +0.03]; content +0.06 [-0.03, +0.15] (implied day-field fraction φ̂: style >0.5, content 0.09988067327553736) | synthetic: s_Mig 0.5 needs φ ≈ 0.01 | fail |
| c2 s_Trans(content) ≥ 0.5, largest | bge +0.97 [+0.84, +1.10]; gte +0.95 [+0.79, +1.11]; self / social +0.68 / +0.29 | field-only rival R1 | pass |
| c3 \|s_Sel\| ≤ 0.2 | content -0.027 (p 0.56); style -0.117 (p 0.16); conventions -0.058 (p 0.02; leave-trait-out -0.054) | w-permutation (A2) | pass |
| P5 residual R ≥ 0.1, CI > 0 | bge +0.94 [+0.86, +1.02]; gte +0.94 [+0.83, +1.05]; kickoff share +0.004 | kill: CI ∋ 0 | reported |
| P6 persistence C > 0 | content -0.19 [-0.58, +0.19] (drift ratio δ²/s +0.51); style -0.73 | iid topics −0.5 | reported |
| P4 convergence placebo | 11 unread-placebo adoptions; placebo s_Sel -0.001, s_Trans,social +0.003 (read: +0.290) | read vs in flight | descriptive |

Cumulative (net change over the period, descriptive, A5): s_Mig style -0.07, content -0.06; s_Sel content -0.06. Migration split (energy): style roster -0.019 / presence +0.000.


## Scorecard (period-specific axes)
C (adequacy): energy shares cross-fitted between message halves (synthetic bias ≤ 0.03 at ρ ≥ 0.3); selection against the w-permutation null. D (unfitted): the style vs content migration ordering. E, G: not informed by this replication.

## Notes
- Data: `data/processed/H89-price-equation-culture/traits/G44.npz`, `adoptions.parquet`.
