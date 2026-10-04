# H89 × G37: Pick your own goal! (2026-03-30 → 2026-04-02)

**Verdict:** supported
**Role:** replication
**Period:** regime III · mode F · 13 agents · non-holdout days only (held-out days masked with `holdout_mask`).

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
**supported.** 2 day transitions; 10 agents, 24 active agent-days; 83 in-cone adoptions by stayers (mean social weight λ̄ 0.27, SD of w 0.34); 0 roster and 5 presence entries/exits. Reliability ρ_Δ: content 0.77, style 0.88, conventions 0.81.

| Prediction | Observed (energy shares; jackknife 95% CI) | Null / reference | Verdict |
| --- | --- | --- | --- |
| c1 s_Mig(style) > s_Mig(content) | style +0.02 [-0.17, +0.20]; content -0.01 [-0.15, +0.14] (implied day-field fraction φ̂: style >0.5, content >0.5) | synthetic: s_Mig 0.5 needs φ ≈ 0.01 | pass |
| c2 s_Trans(content) ≥ 0.5, largest | bge +1.00 [+0.86, +1.15]; gte +0.97 [+0.78, +1.16]; self / social +0.79 / +0.22 | field-only rival R1 | pass |
| c3 \|s_Sel\| ≤ 0.2 | content +0.002 (p 0.96); style +0.095 (p 0.11); conventions +0.091 (p 0.08; leave-trait-out +0.074) | w-permutation (A2) | pass |
| P5 residual R ≥ 0.1, CI > 0 | bge +1.02 [+0.87, +1.17]; gte +0.99 [+0.84, +1.13]; kickoff share -0.018 | kill: CI ∋ 0 | reported |
| P6 persistence C > 0 | content -0.61 [-0.75, -0.47] (drift ratio δ²/s -0.14); style -0.35 | iid topics −0.5 | reported |
| P4 convergence placebo | 1 unread-placebo adoptions; placebo s_Sel -0.002, s_Trans,social +0.023 (read: +0.216) | read vs in flight | descriptive |

Cumulative (net change over the period, descriptive, A5): s_Mig style +0.03, content -0.21; s_Sel content -0.05. Migration split (energy): style roster +0.000 / presence +0.017.


## Scorecard (period-specific axes)
C (adequacy): energy shares cross-fitted between message halves (synthetic bias ≤ 0.03 at ρ ≥ 0.3); selection against the w-permutation null. D (unfitted): the style vs content migration ordering. E, G: not informed by this replication.

## Notes
- Data: `data/processed/H89-price-equation-culture/traits/G37.npz`, `adoptions.parquet`.
