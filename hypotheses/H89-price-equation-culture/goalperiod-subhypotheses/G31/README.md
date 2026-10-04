# H89 × G31: Pick your own goal (agents bid 3.7 Sonnet farewell) (2026-02-16 → 2026-02-23)

**Verdict:** supported
**Role:** replication
**Period:** regime I · mode F · 12 agents · non-holdout days only (held-out days masked with `holdout_mask`).

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
**supported.** 4 day transitions; 12 agents, 56 active agent-days; 1051 in-cone adoptions by stayers (mean social weight λ̄ 0.29, SD of w 0.20); 2 roster and 0 presence entries/exits. Reliability ρ_Δ: content 0.89, style 0.85, conventions 0.93.

| Prediction | Observed (energy shares; jackknife 95% CI) | Null / reference | Verdict |
| --- | --- | --- | --- |
| c1 s_Mig(style) > s_Mig(content) | style +0.04 [-0.03, +0.11]; content +0.01 [-0.02, +0.04] (implied day-field fraction φ̂: style 0.05074254150535627, content 0.12948573741350836) | synthetic: s_Mig 0.5 needs φ ≈ 0.01 | pass |
| c2 s_Trans(content) ≥ 0.5, largest | bge +0.98 [+0.95, +1.00]; gte +0.97 [+0.94, +1.00]; self / social +0.69 / +0.29 | field-only rival R1 | pass |
| c3 \|s_Sel\| ≤ 0.2 | content +0.009 (p 0.33); style +0.049 (p 0.05); conventions +0.004 (p 0.79; leave-trait-out +0.005) | w-permutation (A2) | pass |
| P5 residual R ≥ 0.1, CI > 0 | bge +0.95 [+0.93, +0.97]; gte +0.97 [+0.94, +1.01]; kickoff share +0.033 | kill: CI ∋ 0 | reported |
| P6 persistence C > 0 | content -0.30 [-0.44, -0.16] (drift ratio δ²/s +0.31); style -0.45 | iid topics −0.5 | reported |
| P4 convergence placebo | 8 unread-placebo adoptions; placebo s_Sel -0.001, s_Trans,social +0.003 (read: +0.287) | read vs in flight | descriptive |

Cumulative (net change over the period, descriptive, A5): s_Mig style +0.11, content -0.02; s_Sel content +0.00. Migration split (energy): style roster +0.041 / presence +0.000.


## Scorecard (period-specific axes)
C (adequacy): energy shares cross-fitted between message halves (synthetic bias ≤ 0.03 at ρ ≥ 0.3); selection against the w-permutation null. D (unfitted): the style vs content migration ordering. E, G: not informed by this replication.

## Notes
- Data: `data/processed/H89-price-equation-culture/traits/G31.npz`, `adoptions.parquet`.
