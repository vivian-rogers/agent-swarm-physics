# H03 × G38: Choose a charity and raise as much money as you can for it (2026-04-02 → 2026-04-27)

**Verdict:** failed
**Verdict (1b):** failed (round 1b, 2026-10-04: n̂ TALK 0.32 → 0.14 on corrected inputs; unchanged verdict)
**Role:** replication (exploratory)
**Period:** regime III · mode C (shared objective) · N = 12 at start (+2), 12.4 active per day on average · rooms (agents see only their room) · 17 non-holdout days, median window 4.0 h. Splits inside the period: 2026-04-14 (NE17: G outreach approval; goal-periods scaffold: G outreach approval (2026-04-14)); 2026-04-17 (roster_joined: Claude Opus 4.7); 2026-04-20 (NE18: History search: verbatim segments, 10-day window); 2026-04-22 (roster_joined: Kimi K2.6).

Verdict rule: P3 (n̂ ≥ 0.7): upper 95% bound below 0.7. Verdicts use the primary statistic, n̂ for TALK under M1 with B2 + exogenous drive. n̂ depends on the baseline. A Poisson process with a rate modulated on 10–30 min scales can mimic it, and the 10-min jitter test has no power to separate the two (main card, jitter calibration). Read B2 n̂ as an upper value and B3 n̂ as a downward-biased lower bound. Any verdict here is descriptive, not mechanistic.

## Why this period
- Shared-objective week: S2 predicts these are more self-exciting than free weeks, and HH30's strong form says near critical.
- `goal-periods.md` ranks model 09 (Hawkes) #3 here: long window with a mid-goal constraint
- Context (paraphrased dataset summary; secondary): Second charity fundraiser, a year after #1. Opened with an operator correcting the agents' belief about the Year-1 total ($1,984). Outreach approval (G) arrives mid-goal.
- Scaffold changes inside (goal-periods.md): G outreach approval (2026-04-14)

## Prediction
*Written 2026-10-03 in the main card's Prediction section, before any fit on real data, and restated here for this period. This file was generated after the exploratory run, under the 2026-10-03 folder convention.*

- P3: n̂ (TALK) ≥ 0.7 (near critical). Counts against it: n̂ < 0.7.
- P2 (cross-period): above the F-period median.
- P6: the fast cross-agent part n_cross is higher in C than in F periods. P7: n̂_ALL > n̂_TALK, from the agent's own-loop excitation.
- G1 (guard): on n = 0 synthetic data with this period's fitted baseline, the pipeline returns n̂ ≈ 0, and the naive baseline B0 returns clearly more.

## Result
| Quantity | TALK | ALL | Null / reference | Reading |
|---|---|---|---|---|
| n̂ (M1, B2 + exo), 95% CI | **0.32** [0.08, 0.61] | 0.57 [0.21, 0.73] | Poisson n = 0 | CI: day-bootstrap |
| kernel timescale τ̂ (s) | 199 | 582 | – | τ̂ ≥ 1800 s means the kernel mimics the baseline |
| n̂, kernel τ ≤ 30 min | 0.32 | 0.57 | – | robustness variant |
| baseline ladder B0 / B1 / B2 / B3-2h / B3-30m | 0.70 / 0.63 / 0.32 / 0.16 / 0.00 | 0.81 / 0.71 / 0.57 / 0.34 / 0.00 | guard: n = 0 → B0 0.67, B2 0.000 (TALK) | falls with baseline flexibility |
| sum-of-exp kernel (M2): n, n(τ ≤ 300 s) | 0.43, 0.17 | 0.60, 0.21 | – | ΔAIC grid − exp (TALK) -2.0 |
| power-law-constrained kernel θ | -0.55 | -0.85 | – | ll(pl) − ll(exp) (TALK) -9.0 |
| own-loop n_self (τ ≤ 300 s, M3) | 0.00 | 0.00 | – | scheduler / own-loop part |
| social n_cross (τ ≤ 300 s, M3) | 0.020 | 0.162 | agent-shift null 0.000 / 0.136 | real − null (TALK) = 0.020 |
| pooled fast n̂ (τ ≤ 5 min) | 0.32 | 0.46 | 10-min jitter 0.36 / 0.48 | real − jittered (TALK) = -0.03; uninformative (synthetic n = 0.6 also drops only ≈ 0.03) |
| share of events: baseline / exogenous / triggered | 0.61 / 0.064 / 0.32 | – | – | 149 human/nudger messages in window |
| time-rescaling KS D (p), Hawkes vs Poisson | 0.025 (0.006) vs 0.034 | 0.017 vs 0.011 | Exp(1) | smaller D is better |
| ΔAIC Hawkes − Poisson (B2) | -123.1 | -285.2 | – | negative favors Hawkes |
| day-blocked CV Δℓ/event, Hawkes − Poisson (B2 / B3-30m) | 0.033 / -0.0002 | 0.028 / 0.0000 | 0 | – means < 3 days |
| guard recovery (TALK): n = 0.6 → B2, n = 0.9 → B2 | 0.49, 0.83 | 0.46, 0.79 | 0.6, 0.9 | 3 synthetic replicates |
| guard misspecification: n = 0 with real 10-min rate → B2 | 0.43 | 0.54 | 0 | not a valid null: the real 10-min counts already contain any cascades |
| P(burst ≥ 10), gap 60 s (TALK): data / Hawkes sim / Poisson sim | 0.056 / 0.051 / 0.045 | – | – | unfitted statistic (axis D) |

**Segments (goal period split at step changes; M1 B2):**

| seg | start → end | days | N | n̂ TALK (SE) | partially pooled | n̂ ALL (SE) | n_cross ≤300 s TALK |
|---|---|---|---|---|---|---|---|
| 0 | 2026-04-02 → 2026-04-13 | 8 | 12 | 0.21 (0.04, boot) | 0.21 | 0.38 (0.17) | 0.019 |
| 1 | 2026-04-14 → 2026-04-16 | 3 | 12 | 0.74 (0.26, boot) | 0.29 | 0.78 (0.23) | 0.016 |
| 2 | 2026-04-17 → 2026-04-17 | 1 | 13 | 0.07 (0.21, profile) | 0.12 | 0.00 (–) | 0.000 |
| 3 | 2026-04-20 → 2026-04-21 | 2 | 12 | 0.00 (0.21, profile) | 0.10 | 0.04 (0.25) | 0.000 |
| 4 | 2026-04-22 → 2026-04-24 | 3 | 14 | 0.00 (0.07, boot) | 0.03 | 0.00 (0.02) | 0.026 |

Within-period heterogeneity across segments (TALK): Cochran Q = 12.5, df = 4, p = 0.0142, I² = 0.68, τ = 0.145. Partial pooling uses DerSimonian–Laird random effects within the period (exception d).

Figures: [`figures/diagnostics.pdf`](figures/diagnostics.pdf). Data: `data/processed/H03-self-excited-criticality/G38/` (per-period extracts of the fit, CV, bootstrap, guard, jitter, cascade and segment tables, plus `fits/<SET>_<MODEL>.npy`).

## Scorecard (period-specific axes)
| Axis | Score | Evidence |
|---|---|---|
| B assumptions | 1 | time-rescaling KS D: Hawkes 0.025 vs Poisson 0.034 (p_Hawkes = 0.006); 1 = better than Poisson but not necessarily Exp(1) |
| C adequacy | 1 | held-out Δℓ/event vs Poisson with the same B2 baseline = 0.033; vs the B3 30-min baseline = -0.0002. Capped at 1: no powered test against a Poisson null modulated at 10–30 min |
| D unfitted | 1 | burst-size tail (gap 60 s) closer to the Hawkes simulation than to Poisson: yes |
| F identifiability | 1 | n = 0 → B2 0.000; n = 0.6 → 0.49; but n = 0 with the real 10-min rate → 0.43 |

## Notes
- 2026-10-03: generated by `analysis/write_period_cards.py`. Exploratory, non-holdout days only.
- Long-window day(s) 2026-04-16: the window is 1.5–8× the period's median, likely two sessions with a long silent gap. This distorts the shared within-day shape (B2) and inflates held-out comparisons. Splitting days at long gaps is a planned scheme fix.
- Regime III (perma-computer-use): `events_core` holds chat and session events, but not computer-use turns, so ALL means something different here than in regime I.

<!-- R1B START -->
## Round 1b (improved data, 2026-10-04)
H03 never read the buggy `activity_bins`; round 1b re-runs the round-1 specification (M1_B2 primary, M3 fast self/cross, day bootstrap B = 50 / 25, agent-shift null R = 5) on corrected inputs: exogenous drive from `kicks_classified` (human messages + nudges; round 1 also counted the operator's pause/resume bookends) and days split at operator-off gaps ≥ 60 min (`outages_fixed`). Here: exogenous messages in window 149 → 131; split / trimmed days: 2026-04-16.

| Events | n̂ round 1 [95% CI] | **n̂ round 1b** | fast n_x round 1 | **fast n_x round 1b** | n̂ B3 (lower bound) r1 → 1b |
| --- | --- | --- | --- | --- | --- |
| TALK | 0.32 [0.08, 0.61] | **0.14 [0.06, 0.20]** | 0.020 | **0.010** (shift null 0.000) | 0.00 → 0.00 |
| ALL | 0.57 [0.21, 0.73] | **0.37 [0.21, 0.57]** | 0.162 | **0.079** (shift null 0.029) | 0.00 → 0.00 |

Rule: P3 (n̂ ≥ 0.7): upper 95% bound below 0.7. Source: `data/processed/H03-self-excited-criticality/r1b/period_table.parquet` (`analysis/r1b.py`).
<!-- R1B END -->
