# H03 × G06: Create your own merch store. Whichever agent's store makes the most profit wins! (2025-06-26 → 2025-07-16)

**Verdict:** descriptive
**Role:** exploratory
**Period:** regime I · mode K (competition) · N = 4 at start (±0), 4.0 active per day on average · one shared room · 15 non-holdout days, median window 2.0 h. Splits inside the period: 2025-07-03 (NE02: Screenshot PII redaction; goal-periods scaffold: screenshot PII redaction (2025-07-03)).

Verdict rule: no period-level prediction for mode K; enters P2/P4 as a comparison point. Verdicts use the primary statistic, n̂ for TALK under M1 with B2 + exogenous drive. n̂ depends on the baseline. A Poisson process with a rate modulated on 10–30 min scales can mimic it, and the 10-min jitter test has no power to separate the two (main card, jitter calibration). Read B2 n̂ as an upper value and B3 n̂ as a downward-biased lower bound. Any verdict here is descriptive, not mechanistic.

## Why this period
- Competition week: a comparison point for the mode effect (P2, P4).
- `goal-periods.md` ranks model 09 (Hawkes) #3 here: cross-excitation between rivals
- Context (paraphrased dataset summary; secondary): First competition: each agent builds its own merch store; most profit wins. Claude Opus 4 won ($126 from 24 orders), ahead of Sonnet ($68), o3 ($39) and Gemini ($22).
- Scaffold changes inside (goal-periods.md): screenshot PII redaction (2025-07-03)

## Prediction
*Written 2026-10-03 in the main card's Prediction section, before any fit on real data, and restated here for this period. This file was generated after the exploratory run, under the 2026-10-03 folder convention.*

- No period-level threshold. The period enters P2/P4 as a comparison point; S2 implies it sits below the shared-objective periods.
- P6: the fast cross-agent part n_cross is higher in C than in F periods. P7: n̂_ALL > n̂_TALK, from the agent's own-loop excitation.
- G1 (guard): on n = 0 synthetic data with this period's fitted baseline, the pipeline returns n̂ ≈ 0, and the naive baseline B0 returns clearly more.

## Result
| Quantity | TALK | ALL | Null / reference | Reading |
|---|---|---|---|---|
| n̂ (M1, B2 + exo), 95% CI | **0.65** [0.17, 0.81] | 0.46 [0.38, 0.58] | Poisson n = 0 | CI: day-bootstrap |
| kernel timescale τ̂ (s) | 227 | 41 | – | τ̂ ≥ 1800 s means the kernel mimics the baseline |
| n̂, kernel τ ≤ 30 min | 0.31 | 0.46 | – | robustness variant |
| baseline ladder B0 / B1 / B2 / B3-2h / B3-30m | 1.01 / 0.63 / 0.65 / 0.43 / 0.21 | 0.99 / 0.60 / 0.46 / 0.52 / 0.43 | guard: n = 0 → B0 0.98, B2 0.000 (TALK) | falls with baseline flexibility |
| sum-of-exp kernel (M2): n, n(τ ≤ 300 s) | 0.93, 0.37 | 0.92, 0.48 | – | ΔAIC grid − exp (TALK) -42.3 |
| power-law-constrained kernel θ | -0.57 | -0.14 | – | ll(pl) − ll(exp) (TALK) 5.1 |
| own-loop n_self (τ ≤ 300 s, M3) | 0.16 | 0.37 | – | scheduler / own-loop part |
| social n_cross (τ ≤ 300 s, M3) | 0.122 | 0.099 | agent-shift null 0.032 / 0.024 | real − null (TALK) = 0.090 |
| pooled fast n̂ (τ ≤ 5 min) | 0.31 | 0.46 | 10-min jitter 0.23 / 0.31 | real − jittered (TALK) = 0.08; uninformative (synthetic n = 0.6 also drops only ≈ 0.03) |
| share of events: baseline / exogenous / triggered | 0.31 / 0.061 / 0.63 | – | – | 436 human/nudger messages in window |
| time-rescaling KS D (p), Hawkes vs Poisson | 0.039 (0.003) vs 0.067 | 0.073 vs 0.128 | Exp(1) | smaller D is better |
| ΔAIC Hawkes − Poisson (B2) | 28.5 | -401.7 | – | negative favors Hawkes |
| day-blocked CV Δℓ/event, Hawkes − Poisson (B2 / B3-30m) | 0.144 / 0.0075 | 0.237 / 0.0537 | 0 | – means < 3 days |
| guard recovery (TALK): n = 0.6 → B2, n = 0.9 → B2 | 0.45, 0.81 | 0.60, 0.87 | 0.6, 0.9 | 3 synthetic replicates |
| guard misspecification: n = 0 with real 10-min rate → B2 | 0.37 | 0.45 | 0 | not a valid null: the real 10-min counts already contain any cascades |
| P(burst ≥ 10), gap 60 s (TALK): data / Hawkes sim / Poisson sim | 0.078 / 0.108 / 0.056 | – | – | unfitted statistic (axis D) |

**Segments (goal period split at step changes; M1 B2):**

| seg | start → end | days | N | n̂ TALK (SE) | partially pooled | n̂ ALL (SE) | n_cross ≤300 s TALK |
|---|---|---|---|---|---|---|---|
| 0 | 2025-06-26 → 2025-07-02 | 6 | 4 | 0.40 (0.24, boot) | 0.23 | 0.71 (0.09) | 0.263 |
| 1 | 2025-07-03 → 2025-07-15 | 9 | 4 | 0.22 (0.08, boot) | 0.23 | 0.42 (0.05) | 0.028 |

Within-period heterogeneity across segments (TALK): Cochran Q = 0.5, df = 1, p = 0.474, I² = 0.00, τ = 0.000. Partial pooling uses DerSimonian–Laird random effects within the period (exception d).

Figures: [`figures/diagnostics.pdf`](figures/diagnostics.pdf). Data: `data/processed/H03-self-excited-criticality/G06/` (per-period extracts of the fit, CV, bootstrap, guard, jitter, cascade and segment tables, plus `fits/<SET>_<MODEL>.npy`).

## Scorecard (period-specific axes)
| Axis | Score | Evidence |
|---|---|---|
| B assumptions | 1 | time-rescaling KS D: Hawkes 0.039 vs Poisson 0.067 (p_Hawkes = 0.003); 1 = better than Poisson but not necessarily Exp(1) |
| C adequacy | 1 | held-out Δℓ/event vs Poisson with the same B2 baseline = 0.144; vs the B3 30-min baseline = 0.0075. Capped at 1: no powered test against a Poisson null modulated at 10–30 min |
| D unfitted | 0 | burst-size tail (gap 60 s) closer to the Hawkes simulation than to Poisson: no |
| F identifiability | 1 | n = 0 → B2 0.000; n = 0.6 → 0.45; but n = 0 with the real 10-min rate → 0.37 |

## Notes
- 2026-10-03: generated by `analysis/write_period_cards.py`. Exploratory, non-holdout days only.
- Long-window day(s) 2025-06-29: the window is 1.5–8× the period's median, likely two sessions with a long silent gap. This distorts the shared within-day shape (B2) and inflates held-out comparisons. Splitting days at long gaps is a planned scheme fix.
