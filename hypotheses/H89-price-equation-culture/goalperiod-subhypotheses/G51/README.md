# H89 × G51: Each agent: Maximize your assigned goal! (2026-07-06 → 2026-09-20)

**Verdict:** failed
**Role:** native
**Period:** regime III · mode I/K · 21 agents · non-holdout days only (held-out days masked with `holdout_mask`).

## Why this period
Replication layer: the common H89 estimator (cross-fitted Price partition of day-to-day change of the active population's mean trait) on every non-holdout period with H34 ideas, so periods compare as points on a phase diagram.

## Native test: roster growth (#51, non-holdout 07-06 → 09-04, 11 joins)
*Prediction written 2026-10-04 20:35 UTC, before any native statistic.* #51 is the only long period with steady roster growth (11 joins on non-holdout days, no leaves). Over its 44 transitions, "style moves by migration" predicts that the period's net style change is mostly the newcomers.
- **N3-a:** cumulative roster-migration share of style ≥ 0.5.
- **N3-b:** cumulative roster-migration share of content (bge and gte) < that of style.
- **N3-c (reported, not voted):** energy \|s_Sel\| ≤ 0.2 for every trait.
- Prior 0.55. **Verdict:** supported = N3-a and N3-b; failed = neither; mixed otherwise.
- *Counts against:* cumulative style roster share < 0.5 and not above content's.

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
**failed** (native N3). 44 transitions, 07-06 → 09-04; 11 joins (9 roster-entry transitions).

| Prediction | Observed (cumulative cross-fitted share; jackknife 95% CI) | Reference | Verdict |
| --- | --- | --- | --- |
| N3-a style roster-migration share ≥ 0.5 | -0.144 [-0.335, +0.047] (all migration +0.006 [-0.414, +0.426]; ρ_cum 0.99) | S0 static agents: 0.72 | fail |
| N3-b content roster share < style's | content bge +0.016 [-0.187, +0.220], gte +0.048 [-0.086, +0.182]; conventions +0.107 [-0.040, +0.255] | style | fail |
| N3-c energy \|s_Sel\| ≤ 0.2 (reported) | content +0.002, style +0.007, conventions +0.039 | 0.2 | pass |

**Replication estimator on #51:**

**supported.** 44 day transitions; 32 agents, 828 active agent-days; 13932 in-cone adoptions by stayers (mean social weight λ̄ 0.26, SD of w 0.38); 11 roster and 160 presence entries/exits. Reliability ρ_Δ: content 0.72, style 0.71, conventions 0.74.

| Prediction | Observed (energy shares; jackknife 95% CI) | Null / reference | Verdict |
| --- | --- | --- | --- |
| c1 s_Mig(style) > s_Mig(content) | style +0.29 [+0.13, +0.45]; content +0.19 [+0.08, +0.30] (implied day-field fraction φ̂: style 0.015597505196218057, content 0.026018795885829536) | synthetic: s_Mig 0.5 needs φ ≈ 0.01 | pass |
| c2 s_Trans(content) ≥ 0.5, largest | bge +0.81 [+0.70, +0.92]; gte +0.78 [+0.66, +0.90]; self / social +0.58 / +0.23 | field-only rival R1 | pass |
| c3 \|s_Sel\| ≤ 0.2 | content +0.002 (p 0.92); style +0.007 (p 0.79); conventions +0.039 (p 0.07; leave-trait-out +0.037) | w-permutation (A2) | pass |
| P5 residual R ≥ 0.1, CI > 0 | bge +0.79 [+0.68, +0.89]; gte +0.75 [+0.63, +0.87]; kickoff share +0.023 | kill: CI ∋ 0 | reported |
| P6 persistence C > 0 | content -0.27 [-0.34, -0.20] (drift ratio δ²/s +0.36); style -0.25 | iid topics −0.5 | reported |
| P4 convergence placebo | 337 unread-placebo adoptions; placebo s_Sel +0.001, s_Trans,social +0.002 (read: +0.227) | read vs in flight | descriptive |

Cumulative (net change over the period, descriptive, A5): s_Mig style +0.01, content -0.18; s_Sel content +0.24. Migration split (energy): style roster +0.021 / presence +0.270.


## Scorecard (period-specific axes)
C (adequacy): energy shares cross-fitted between message halves (synthetic bias ≤ 0.03 at ρ ≥ 0.3); selection against the w-permutation null. D (unfitted): the style vs content migration ordering. E, G: not informed by this replication.

## Notes
- Data: `data/processed/H89-price-equation-culture/traits/G51.npz`, `adoptions.parquet`.
