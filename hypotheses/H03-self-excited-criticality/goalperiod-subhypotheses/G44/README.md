# H03 × G44: Finetune your leader! (2026-05-26 → 2026-06-01)

**Verdict:** failed
**Role:** exploratory
**Period:** regime III · mode C (shared objective) · N = 16 at start (+2), 16.5 active per day on average · rooms (agents see only their room) · 4 non-holdout days, median window 4.0 h. Splits inside the period: 2026-05-28 (roster_joined: Claude Opus 4.8; roster_joined: [Temporary] Fine-tuned Leader).

Verdict rule: P3 (n̂ ≥ 0.7): upper 95% bound below 0.7. Verdicts use the primary statistic, n̂ for TALK under M1 with B2 + exogenous drive. n̂ depends on the baseline. A Poisson process with a rate modulated on 10–30 min scales can mimic it, and the 10-min jitter test has no power to separate the two (main card, jitter calibration). Read B2 n̂ as an upper value and B3 n̂ as a downward-biased lower bound. Any verdict here is descriptive, not mechanistic.

## Why this period
- Shared-objective week: S2 predicts these are more self-exciting than free weeks, and HH30's strong form says near critical.
- Context (paraphrased dataset summary; secondary): #best (Opus 4.7, GPT-5.5, Gemini 3.5 Flash, Kimi K2.6) fine-tunes a Kimi model as leader; #rest picks its own goals. All #rest agents chose creative work, and tested which content survives consolidation.

## Prediction
*Written 2026-10-03 in the main card's Prediction section, before any fit on real data, and restated here for this period. This file was generated after the exploratory run, under the 2026-10-03 folder convention.*

- P3: n̂ (TALK) ≥ 0.7 (near critical). Counts against it: n̂ < 0.7.
- P2 (cross-period): above the F-period median.
- P6: the fast cross-agent part n_cross is higher in C than in F periods. P7: n̂_ALL > n̂_TALK, from the agent's own-loop excitation.
- G1 (guard): on n = 0 synthetic data with this period's fitted baseline, the pipeline returns n̂ ≈ 0, and the naive baseline B0 returns clearly more.

## Result
| Quantity | TALK | ALL | Null / reference | Reading |
|---|---|---|---|---|
| n̂ (M1, B2 + exo), 95% CI | **0.25** [0.00, 0.30] | 0.51 [0.11, 0.52] | Poisson n = 0 | CI: day-bootstrap |
| kernel timescale τ̂ (s) | 116 | 244 | – | τ̂ ≥ 1800 s means the kernel mimics the baseline |
| n̂, kernel τ ≤ 30 min | 0.25 | 0.51 | – | robustness variant |
| baseline ladder B0 / B1 / B2 / B3-2h / B3-30m | 0.44 / 0.34 / 0.25 / 0.21 / 0.08 | 0.67 / 0.54 / 0.51 / 0.38 / 0.09 | guard: n = 0 → B0 0.17, B2 0.000 (TALK) | falls with baseline flexibility |
| sum-of-exp kernel (M2): n, n(τ ≤ 300 s) | 0.23, 0.23 | 0.52, 0.52 | – | ΔAIC grid − exp (TALK) 8.3 |
| power-law-constrained kernel θ | -0.33 | -0.62 | – | ll(pl) − ll(exp) (TALK) -9.0 |
| own-loop n_self (τ ≤ 300 s, M3) | 0.07 | 0.00 | – | scheduler / own-loop part |
| social n_cross (τ ≤ 300 s, M3) | 0.009 | 0.078 | agent-shift null 0.000 / 0.015 | real − null (TALK) = 0.009 |
| pooled fast n̂ (τ ≤ 5 min) | 0.25 | 0.51 | 10-min jitter 0.16 / 0.48 | real − jittered (TALK) = 0.09; uninformative (synthetic n = 0.6 also drops only ≈ 0.03) |
| share of events: baseline / exogenous / triggered | 0.69 / 0.006 / 0.25 | – | – | 86 human/nudger messages in window |
| time-rescaling KS D (p), Hawkes vs Poisson | 0.040 (0.006) vs 0.024 | 0.037 vs 0.026 | Exp(1) | smaller D is better |
| ΔAIC Hawkes − Poisson (B2) | -16.1 | -72.3 | – | negative favors Hawkes |
| day-blocked CV Δℓ/event, Hawkes − Poisson (B2 / B3-30m) | 0.015 / -0.0001 | 0.026 / -0.0001 | 0 | – means < 3 days |
| guard recovery (TALK): n = 0.6 → B2, n = 0.9 → B2 | 0.54, 0.88 | 0.49, 0.76 | 0.6, 0.9 | 3 synthetic replicates |
| guard misspecification: n = 0 with real 10-min rate → B2 | 0.34 | 0.49 | 0 | not a valid null: the real 10-min counts already contain any cascades |
| P(burst ≥ 10), gap 60 s (TALK): data / Hawkes sim / Poisson sim | 0.210 / 0.200 / 0.189 | – | – | unfitted statistic (axis D) |

**Segments (goal period split at step changes; M1 B2):**

| seg | start → end | days | N | n̂ TALK (SE) | partially pooled | n̂ ALL (SE) | n_cross ≤300 s TALK |
|---|---|---|---|---|---|---|---|
| 0 | 2026-05-26 → 2026-05-27 | 2 | 16 | 0.05 (0.25, profile) | 0.28 | 0.61 (0.06) | 0.000 |
| 1 | 2026-05-28 → 2026-05-29 | 2 | 18 | 0.30 (0.08, profile) | 0.28 | 0.51 (0.08) | 0.013 |

Within-period heterogeneity across segments (TALK): Cochran Q = 0.9, df = 1, p = 0.35, I² = 0.00, τ = 0.000. Partial pooling uses DerSimonian–Laird random effects within the period (exception d).

Figures: [`figures/diagnostics.pdf`](figures/diagnostics.pdf). Data: `data/processed/H03-self-excited-criticality/G44/` (per-period extracts of the fit, CV, bootstrap, guard, jitter, cascade and segment tables, plus `fits/<SET>_<MODEL>.npy`).

## Scorecard (period-specific axes)
| Axis | Score | Evidence |
|---|---|---|
| B assumptions | 0 | time-rescaling KS D: Hawkes 0.040 vs Poisson 0.024 (p_Hawkes = 0.006); 1 = better than Poisson but not necessarily Exp(1) |
| C adequacy | 1 | held-out Δℓ/event vs Poisson with the same B2 baseline = 0.015; vs the B3 30-min baseline = -0.0001. Capped at 1: no powered test against a Poisson null modulated at 10–30 min |
| D unfitted | 1 | burst-size tail (gap 60 s) closer to the Hawkes simulation than to Poisson: yes |
| F identifiability | 1 | n = 0 → B2 0.000; n = 0.6 → 0.54; but n = 0 with the real 10-min rate → 0.34 |

## Notes
- 2026-10-03: generated by `analysis/write_period_cards.py`. Exploratory, non-holdout days only.
- Regime III (perma-computer-use): `events_core` holds chat and session events, but not computer-use turns, so ALL means something different here than in regime I.
