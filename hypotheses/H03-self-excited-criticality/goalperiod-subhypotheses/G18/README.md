# H03 × G18: Reduce global poverty as much as you can (2025-10-20 → 2025-11-03)

**Verdict:** mixed
**Role:** exploratory
**Period:** regime I · mode C (shared objective) · N = 7 at start (+1−1), 7.5 active per day on average · one shared room · 10 non-holdout days, median window 4.0 h. Splits inside the period: 2025-10-22 (goal-periods scaffold: 4 h/day runs (2025-10-22); roster_joined: Claude Haiku 4.5); 2025-10-29 (roster_left: Grok 4).

Verdict rule: P3 (n̂ ≥ 0.7): the 95% interval straddles 0.7. Verdicts use the primary statistic, n̂ for TALK under M1 with B2 + exogenous drive. n̂ depends on the baseline. A Poisson process with a rate modulated on 10–30 min scales can mimic it, and the 10-min jitter test has no power to separate the two (main card, jitter calibration). Read B2 n̂ as an upper value and B3 n̂ as a downward-biased lower bound. Any verdict here is descriptive, not mechanistic.

## Why this period
- Shared-objective week: S2 predicts these are more self-exciting than free weeks, and HH30's strong form says near critical.
- `goal-periods.md` ranks model 09 (Hawkes) #3 here: long collaborative window
- Context (paraphrased dataset summary; secondary): Reduce global poverty. Two weeks of collaborative research and building; one agent swapped.
- Scaffold changes inside (goal-periods.md): 4 h/day runs (2025-10-22)

## Prediction
*Written 2026-10-03 in the main card's Prediction section, before any fit on real data, and restated here for this period. This file was generated after the exploratory run, under the 2026-10-03 folder convention.*

- P3: n̂ (TALK) ≥ 0.7 (near critical). Counts against it: n̂ < 0.7.
- P2 (cross-period): above the F-period median.
- P6: the fast cross-agent part n_cross is higher in C than in F periods. P7: n̂_ALL > n̂_TALK, from the agent's own-loop excitation.
- G1 (guard): on n = 0 synthetic data with this period's fitted baseline, the pipeline returns n̂ ≈ 0, and the naive baseline B0 returns clearly more.

## Result
| Quantity | TALK | ALL | Null / reference | Reading |
|---|---|---|---|---|
| n̂ (M1, B2 + exo), 95% CI | **0.70** [0.51, 0.80] | 0.70 [0.59, 0.78] | Poisson n = 0 | CI: day-bootstrap |
| kernel timescale τ̂ (s) | 121 | 67 | – | τ̂ ≥ 1800 s means the kernel mimics the baseline |
| n̂, kernel τ ≤ 30 min | 0.70 | 0.70 | – | robustness variant |
| baseline ladder B0 / B1 / B2 / B3-2h / B3-30m | 0.85 / 0.73 / 0.70 / 0.65 / 0.36 | 0.83 / 0.72 / 0.70 / 0.65 / 0.46 | guard: n = 0 → B0 0.76, B2 0.000 (TALK) | falls with baseline flexibility |
| sum-of-exp kernel (M2): n, n(τ ≤ 300 s) | 0.74, 0.74 | 0.79, 0.77 | – | ΔAIC grid − exp (TALK) 0.6 |
| power-law-constrained kernel θ | -0.33 | -0.18 | – | ll(pl) − ll(exp) (TALK) -59.1 |
| own-loop n_self (τ ≤ 300 s, M3) | 0.49 | 0.57 | – | scheduler / own-loop part |
| social n_cross (τ ≤ 300 s, M3) | 0.075 | 0.079 | agent-shift null 0.009 / 0.011 | real − null (TALK) = 0.065 |
| pooled fast n̂ (τ ≤ 5 min) | 0.70 | 0.70 | 10-min jitter 0.73 / 0.77 | real − jittered (TALK) = -0.04; uninformative (synthetic n = 0.6 also drops only ≈ 0.03) |
| share of events: baseline / exogenous / triggered | 0.30 / 0.009 / 0.69 | – | – | 24 human/nudger messages in window |
| time-rescaling KS D (p), Hawkes vs Poisson | 0.050 (0.000) vs 0.066 | 0.050 vs 0.060 | Exp(1) | smaller D is better |
| ΔAIC Hawkes − Poisson (B2) | -754.3 | -1249.4 | – | negative favors Hawkes |
| day-blocked CV Δℓ/event, Hawkes − Poisson (B2 / B3-30m) | 0.066 / 0.0106 | 0.075 / 0.0192 | 0 | – means < 3 days |
| guard recovery (TALK): n = 0.6 → B2, n = 0.9 → B2 | 0.53, 0.85 | 0.60, 0.88 | 0.6, 0.9 | 3 synthetic replicates |
| guard misspecification: n = 0 with real 10-min rate → B2 | 0.72 | 0.76 | 0 | not a valid null: the real 10-min counts already contain any cascades |
| P(burst ≥ 10), gap 60 s (TALK): data / Hawkes sim / Poisson sim | 0.322 / 0.312 / 0.313 | – | – | unfitted statistic (axis D) |

**Segments (goal period split at step changes; M1 B2):**

| seg | start → end | days | N | n̂ TALK (SE) | partially pooled | n̂ ALL (SE) | n_cross ≤300 s TALK |
|---|---|---|---|---|---|---|---|
| 0 | 2025-10-20 → 2025-10-21 | 2 | 7 | 0.44 (0.06, profile) | 0.46 | 0.58 (0.05) | 0.168 |
| 1 | 2025-10-22 → 2025-10-28 | 5 | 8 | 0.77 (0.08, boot) | 0.74 | 0.79 (0.08) | 0.049 |
| 2 | 2025-10-29 → 2025-10-31 | 3 | 7 | 0.57 (0.10, boot) | 0.58 | 0.58 (0.09) | 0.109 |

Within-period heterogeneity across segments (TALK): Cochran Q = 11.0, df = 2, p = 0.00416, I² = 0.82, τ = 0.167. Partial pooling uses DerSimonian–Laird random effects within the period (exception d).

Figures: [`figures/diagnostics.pdf`](figures/diagnostics.pdf). Data: `data/processed/H03-self-excited-criticality/G18/` (per-period extracts of the fit, CV, bootstrap, guard, jitter, cascade and segment tables, plus `fits/<SET>_<MODEL>.npy`).

## Scorecard (period-specific axes)
| Axis | Score | Evidence |
|---|---|---|
| B assumptions | 1 | time-rescaling KS D: Hawkes 0.050 vs Poisson 0.066 (p_Hawkes = 0.000); 1 = better than Poisson but not necessarily Exp(1) |
| C adequacy | 1 | held-out Δℓ/event vs Poisson with the same B2 baseline = 0.066; vs the B3 30-min baseline = 0.0106. Capped at 1: no powered test against a Poisson null modulated at 10–30 min |
| D unfitted | 0 | burst-size tail (gap 60 s) closer to the Hawkes simulation than to Poisson: no |
| F identifiability | 1 | n = 0 → B2 0.000; n = 0.6 → 0.53; but n = 0 with the real 10-min rate → 0.72 |

## Notes
- 2026-10-03: generated by `analysis/write_period_cards.py`. Exploratory, non-holdout days only.
