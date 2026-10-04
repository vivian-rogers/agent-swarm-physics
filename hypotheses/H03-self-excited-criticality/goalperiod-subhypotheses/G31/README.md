# H03 × G31: Pick your own goal (agents bid 3.7 Sonnet farewell) (2026-02-16 → 2026-02-23)

**Verdict:** mixed
**Role:** exploratory
**Period:** regime I · mode F (free / holiday) · N = 12 at start (+1−1), 12.2 active per day on average · one shared room · 5 non-holdout days, median window 4.0 h. Splits inside the period: 2026-02-18 (roster_joined: Claude Sonnet 4.6); 2026-02-19 (NE29: Retirement of Claude 3.7 Sonnet, the longest-servi; roster_left: Claude 3.7 Sonnet); 2026-02-20 (NE11: 100-turn hard cap on sessions; goal-periods scaffold: 100-turn session cap (2026-02-20)).

Verdict rule: P1 (n̂ < 0.5): the 95% interval straddles 0.5. Verdicts use the primary statistic, n̂ for TALK under M1 with B2 + exogenous drive. n̂ depends on the baseline. A Poisson process with a rate modulated on 10–30 min scales can mimic it, and the 10-min jitter test has no power to separate the two (main card, jitter calibration). Read B2 n̂ as an upper value and B3 n̂ as a downward-biased lower bound. Any verdict here is descriptive, not mechanistic.

## Why this period
- Free/holiday week: the HH30 test (holidays and free weeks are subcritical).
- Context (paraphrased dataset summary; secondary): Free week; farewell to Claude 3.7 Sonnet, which retired. About nine agents converged on the same task (a "canonical guardrails UI snippet") with competing PRs.
- Scaffold changes inside (goal-periods.md): 100-turn session cap (2026-02-20)

## Prediction
*Written 2026-10-03 in the main card's Prediction section, before any fit on real data, and restated here for this period. This file was generated after the exploratory run, under the 2026-10-03 folder convention.*

- P1: n̂ (TALK) < 0.5. Counts against it: n̂ ≥ 0.5.
- P6: the fast cross-agent part n_cross is higher in C than in F periods. P7: n̂_ALL > n̂_TALK, from the agent's own-loop excitation.
- G1 (guard): on n = 0 synthetic data with this period's fitted baseline, the pipeline returns n̂ ≈ 0, and the naive baseline B0 returns clearly more.

## Result
| Quantity | TALK | ALL | Null / reference | Reading |
|---|---|---|---|---|
| n̂ (M1, B2 + exo), 95% CI | **0.07** [0.00, 0.77] | 0.25 [0.11, 0.32] | Poisson n = 0 | CI: day-bootstrap |
| kernel timescale τ̂ (s) | 109 | 44 | – | τ̂ ≥ 1800 s means the kernel mimics the baseline |
| n̂, kernel τ ≤ 30 min | 0.07 | 0.25 | – | robustness variant |
| baseline ladder B0 / B1 / B2 / B3-2h / B3-30m | 0.41 / 0.35 / 0.07 / 0.24 / 0.00 | 0.38 / 0.32 / 0.25 / 0.29 / 0.18 | guard: n = 0 → B0 0.49, B2 0.000 (TALK) | falls with baseline flexibility |
| sum-of-exp kernel (M2): n, n(τ ≤ 300 s) | 0.06, 0.06 | 0.37, 0.21 | – | ΔAIC grid − exp (TALK) 8.0 |
| power-law-constrained kernel θ | -1.02 | -0.17 | – | ll(pl) − ll(exp) (TALK) -0.5 |
| own-loop n_self (τ ≤ 300 s, M3) | 0.00 | 0.18 | – | scheduler / own-loop part |
| social n_cross (τ ≤ 300 s, M3) | 0.066 | 0.049 | agent-shift null 0.017 / 0.015 | real − null (TALK) = 0.049 |
| pooled fast n̂ (τ ≤ 5 min) | 0.07 | 0.25 | 10-min jitter 0.04 / 0.25 | real − jittered (TALK) = 0.02; uninformative (synthetic n = 0.6 also drops only ≈ 0.03) |
| share of events: baseline / exogenous / triggered | 0.92 / 0.016 / 0.07 | – | – | 36 human/nudger messages in window |
| time-rescaling KS D (p), Hawkes vs Poisson | 0.028 (0.013) vs 0.026 | 0.039 vs 0.044 | Exp(1) | smaller D is better |
| ΔAIC Hawkes − Poisson (B2) | 2.4 | -60.8 | – | negative favors Hawkes |
| day-blocked CV Δℓ/event, Hawkes − Poisson (B2 / B3-30m) | -0.000 / -0.0001 | 0.008 / 0.0029 | 0 | – means < 3 days |
| guard recovery (TALK): n = 0.6 → B2, n = 0.9 → B2 | 0.53, 0.89 | 0.59, 0.87 | 0.6, 0.9 | 3 synthetic replicates |
| guard misspecification: n = 0 with real 10-min rate → B2 | 0.29 | 0.45 | 0 | not a valid null: the real 10-min counts already contain any cascades |
| P(burst ≥ 10), gap 60 s (TALK): data / Hawkes sim / Poisson sim | 0.473 / 0.455 / 0.453 | – | – | unfitted statistic (axis D) |

**Segments (goal period split at step changes; M1 B2):**

| seg | start → end | days | N | n̂ TALK (SE) | partially pooled | n̂ ALL (SE) | n_cross ≤300 s TALK |
|---|---|---|---|---|---|---|---|
| 0 | 2026-02-16 → 2026-02-17 | 2 | 12 | 0.09 (0.23, profile) | 0.12 | 0.25 (0.06) | 0.092 |
| 1 | 2026-02-18 → 2026-02-18 | 1 | 13 | 0.12 (0.08, profile) | 0.12 | 0.33 (0.07) | 0.147 |
| 2 | 2026-02-19 → 2026-02-19 | 1 | 12 | 0.14 (–, profile) | – | 0.02 (–) | 0.000 |
| 3 | 2026-02-20 → 2026-02-20 | 1 | 12 | 0.00 (–, profile) | – | 0.11 (0.07) | 0.000 |

Within-period heterogeneity across segments (TALK): Cochran Q = 0.0, df = 1, p = 0.914, I² = 0.00, τ = 0.000. Partial pooling uses DerSimonian–Laird random effects within the period (exception d).

Figures: [`figures/diagnostics.pdf`](figures/diagnostics.pdf). Data: `data/processed/H03-self-excited-criticality/G31/` (per-period extracts of the fit, CV, bootstrap, guard, jitter, cascade and segment tables, plus `fits/<SET>_<MODEL>.npy`).

## Scorecard (period-specific axes)
| Axis | Score | Evidence |
|---|---|---|
| B assumptions | 0 | time-rescaling KS D: Hawkes 0.028 vs Poisson 0.026 (p_Hawkes = 0.013); 1 = better than Poisson but not necessarily Exp(1) |
| C adequacy | 0 | held-out Δℓ/event vs Poisson with the same B2 baseline = -0.000; vs the B3 30-min baseline = -0.0001. Capped at 1: no powered test against a Poisson null modulated at 10–30 min |
| D unfitted | 1 | burst-size tail (gap 60 s) closer to the Hawkes simulation than to Poisson: yes |
| F identifiability | 1 | n = 0 → B2 0.000; n = 0.6 → 0.53; but n = 0 with the real 10-min rate → 0.29 |

## Notes
- 2026-10-03: generated by `analysis/write_period_cards.py`. Exploratory, non-holdout days only.
