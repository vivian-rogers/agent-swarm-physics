# H03 × G12: Form two teams and debate each other, while one agent judges. Choose your teammates wisely! (2025-09-01 → 2025-09-08)

**Verdict:** descriptive
**Role:** exploratory
**Period:** regime I · mode M (teams / hidden roles) · N = 7 at start (±0), 7.0 active per day on average · one shared room · 5 non-holdout days, median window 3.0 h. Splits inside the period: 2025-09-05 (NE04: C history-search tool; chain-of-thought memory con; goal-periods scaffold: C history search + CoT memory (2025-09-05)).

Verdict rule: no period-level prediction for mode M; enters P2/P4 as a comparison point. Verdicts use the primary statistic, n̂ for TALK under M1 with B2 + exogenous drive. n̂ depends on the baseline. A Poisson process with a rate modulated on 10–30 min scales can mimic it, and the 10-min jitter test has no power to separate the two (main card, jitter calibration). Read B2 n̂ as an upper value and B3 n̂ as a downward-biased lower bound. Any verdict here is descriptive, not mechanistic.

## Why this period
- Teams / hidden-roles week: a comparison point for the mode effect (P2, P4); the only non-holdout M period.
- Context (paraphrased dataset summary; secondary): Two teams debate (Asian Parliamentary format) while one agent judges. Teams were chosen by the agents.
- Scaffold changes inside (goal-periods.md): C history search + CoT memory (2025-09-05)

## Prediction
*Written 2026-10-03 in the main card's Prediction section, before any fit on real data, and restated here for this period. This file was generated after the exploratory run, under the 2026-10-03 folder convention.*

- No period-level threshold. The period enters P2/P4 as a comparison point; S2 implies it sits below the shared-objective periods.
- P6: the fast cross-agent part n_cross is higher in C than in F periods. P7: n̂_ALL > n̂_TALK, from the agent's own-loop excitation.
- G1 (guard): on n = 0 synthetic data with this period's fitted baseline, the pipeline returns n̂ ≈ 0, and the naive baseline B0 returns clearly more.

## Result
| Quantity | TALK | ALL | Null / reference | Reading |
|---|---|---|---|---|
| n̂ (M1, B2 + exo), 95% CI | **0.63** [0.39, 0.68] | 0.65 [0.45, 0.70] | Poisson n = 0 | CI: day-bootstrap |
| kernel timescale τ̂ (s) | 108 | 86 | – | τ̂ ≥ 1800 s means the kernel mimics the baseline |
| n̂, kernel τ ≤ 30 min | 0.63 | 0.65 | – | robustness variant |
| baseline ladder B0 / B1 / B2 / B3-2h / B3-30m | 0.69 / 0.64 / 0.63 / 0.58 / 0.45 | 0.71 / 0.65 / 0.65 / 0.59 / 0.47 | guard: n = 0 → B0 0.37, B2 0.020 (TALK) | falls with baseline flexibility |
| sum-of-exp kernel (M2): n, n(τ ≤ 300 s) | 0.64, 0.64 | 0.71, 0.66 | – | ΔAIC grid − exp (TALK) 7.9 |
| power-law-constrained kernel θ | -0.34 | -0.25 | – | ll(pl) − ll(exp) (TALK) -37.3 |
| own-loop n_self (τ ≤ 300 s, M3) | 0.57 | 0.60 | – | scheduler / own-loop part |
| social n_cross (τ ≤ 300 s, M3) | 0.102 | 0.099 | agent-shift null 0.015 / 0.024 | real − null (TALK) = 0.087 |
| pooled fast n̂ (τ ≤ 5 min) | 0.63 | 0.65 | 10-min jitter 0.62 / 0.66 | real − jittered (TALK) = 0.01; uninformative (synthetic n = 0.6 also drops only ≈ 0.03) |
| share of events: baseline / exogenous / triggered | 0.31 / 0.007 / 0.62 | – | – | 18 human/nudger messages in window |
| time-rescaling KS D (p), Hawkes vs Poisson | 0.060 (0.000) vs 0.062 | 0.062 vs 0.056 | Exp(1) | smaller D is better |
| ΔAIC Hawkes − Poisson (B2) | -242.7 | -324.0 | – | negative favors Hawkes |
| day-blocked CV Δℓ/event, Hawkes − Poisson (B2 / B3-30m) | 0.056 / 0.0148 | 0.057 / 0.0163 | 0 | – means < 3 days |
| guard recovery (TALK): n = 0.6 → B2, n = 0.9 → B2 | 0.58, 0.84 | 0.51, 0.89 | 0.6, 0.9 | 3 synthetic replicates |
| guard misspecification: n = 0 with real 10-min rate → B2 | 0.66 | 0.67 | 0 | not a valid null: the real 10-min counts already contain any cascades |
| P(burst ≥ 10), gap 60 s (TALK): data / Hawkes sim / Poisson sim | 0.525 / 0.535 / 0.802 | – | – | unfitted statistic (axis D) |

**Segments (goal period split at step changes; M1 B2):**

| seg | start → end | days | N | n̂ TALK (SE) | partially pooled | n̂ ALL (SE) | n_cross ≤300 s TALK |
|---|---|---|---|---|---|---|---|
| 0 | 2025-09-01 → 2025-09-04 | 4 | 7 | 0.55 (0.08, boot) | 0.57 | 0.57 (0.05) | 0.098 |
| 1 | 2025-09-05 → 2025-09-05 | 1 | 7 | 0.61 (0.13, profile) | 0.57 | 0.59 (0.11) | 0.000 |

Within-period heterogeneity across segments (TALK): Cochran Q = 0.1, df = 1, p = 0.716, I² = 0.00, τ = 0.000. Partial pooling uses DerSimonian–Laird random effects within the period (exception d).

Figures: [`figures/diagnostics.pdf`](figures/diagnostics.pdf). Data: `data/processed/H03-self-excited-criticality/G12/` (per-period extracts of the fit, CV, bootstrap, guard, jitter, cascade and segment tables, plus `fits/<SET>_<MODEL>.npy`).

## Scorecard (period-specific axes)
| Axis | Score | Evidence |
|---|---|---|
| B assumptions | 1 | time-rescaling KS D: Hawkes 0.060 vs Poisson 0.062 (p_Hawkes = 0.000); 1 = better than Poisson but not necessarily Exp(1) |
| C adequacy | 1 | held-out Δℓ/event vs Poisson with the same B2 baseline = 0.056; vs the B3 30-min baseline = 0.0148. Capped at 1: no powered test against a Poisson null modulated at 10–30 min |
| D unfitted | 1 | burst-size tail (gap 60 s) closer to the Hawkes simulation than to Poisson: yes |
| F identifiability | 1 | n = 0 → B2 0.020; n = 0.6 → 0.58; but n = 0 with the real 10-min rate → 0.66 |

## Notes
- 2026-10-03: generated by `analysis/write_period_cards.py`. Exploratory, non-holdout days only.
