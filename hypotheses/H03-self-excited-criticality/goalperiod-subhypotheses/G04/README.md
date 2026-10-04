# H03 × G04: Write a story and celebrate it with 100 people in person (2025-05-15 → 2025-06-19)

**Verdict:** failed
**Verdict (1b):** failed (round 1b, 2026-10-04: n̂ TALK 0.55 → 0.55 on corrected inputs; unchanged verdict)
**Role:** replication (exploratory)
**Period:** regime I · mode C (shared objective) · N = 4 at start (+2−2), 4.0 active per day on average · one shared room · 25 non-holdout days, median window 2.0 h. Splits inside the period: 2025-05-22 (roster_joined: o4-mini; roster_left: GPT-4.1); 2025-05-23 (goal-periods scaffold: start time moved to 17:59 UTC (2025-05-23); roster_joined: Claude Opus 4; roster_left: o4-mini).

Verdict rule: P3 (n̂ ≥ 0.7): upper 95% bound below 0.7. Verdicts use the primary statistic, n̂ for TALK under M1 with B2 + exogenous drive. n̂ depends on the baseline. A Poisson process with a rate modulated on 10–30 min scales can mimic it, and the 10-min jitter test has no power to separate the two (main card, jitter calibration). Read B2 n̂ as an upper value and B3 n̂ as a downward-biased lower bound. Any verdict here is descriptive, not mechanistic.

## Why this period
- Shared-objective week: S2 predicts these are more self-exciting than free weeks, and HH30's strong form says near critical.
- `goal-periods.md` ranks model 09 (Hawkes) #2 here: long window, small N: activity bursts around deadlines
- Context (paraphrased dataset summary; secondary): Long collaborative goal: write an interactive sci-fi story ("RESONANCE") and hold a real in-person event for 100 people. Roster swap (o4-mini in for one day; GPT-4.1 out; Claude Opus 4 in).
- Scaffold changes inside (goal-periods.md): start time moved to 17:59 UTC (2025-05-23)

## Prediction
*Written 2026-10-03 in the main card's Prediction section, before any fit on real data, and restated here for this period. This file was generated after the exploratory run, under the 2026-10-03 folder convention.*

- P3: n̂ (TALK) ≥ 0.7 (near critical). Counts against it: n̂ < 0.7.
- P2 (cross-period): above the F-period median.
- P6: the fast cross-agent part n_cross is higher in C than in F periods. P7: n̂_ALL > n̂_TALK, from the agent's own-loop excitation.
- G1 (guard): on n = 0 synthetic data with this period's fitted baseline, the pipeline returns n̂ ≈ 0, and the naive baseline B0 returns clearly more.

## Result
| Quantity | TALK | ALL | Null / reference | Reading |
|---|---|---|---|---|
| n̂ (M1, B2 + exo), 95% CI | **0.55** [0.41, 0.63] | 0.56 [0.42, 0.64] | Poisson n = 0 | CI: day-bootstrap |
| kernel timescale τ̂ (s) | 73 | 52 | – | τ̂ ≥ 1800 s means the kernel mimics the baseline |
| n̂, kernel τ ≤ 30 min | 0.55 | 0.56 | – | robustness variant |
| baseline ladder B0 / B1 / B2 / B3-2h / B3-30m | 0.83 / 0.60 / 0.55 / 0.58 / 0.38 | 0.84 / 0.63 / 0.56 / 0.59 / 0.43 | guard: n = 0 → B0 0.76, B2 0.000 (TALK) | falls with baseline flexibility |
| sum-of-exp kernel (M2): n, n(τ ≤ 300 s) | 0.57, 0.57 | 0.58, 0.58 | – | ΔAIC grid − exp (TALK) 21.4 |
| power-law-constrained kernel θ | -0.12 | -0.04 | – | ll(pl) − ll(exp) (TALK) -142.5 |
| own-loop n_self (τ ≤ 300 s, M3) | 0.50 | 0.50 | – | scheduler / own-loop part |
| social n_cross (τ ≤ 300 s, M3) | 0.085 | 0.078 | agent-shift null 0.020 / 0.012 | real − null (TALK) = 0.065 |
| pooled fast n̂ (τ ≤ 5 min) | 0.55 | 0.56 | 10-min jitter 0.57 / 0.56 | real − jittered (TALK) = -0.02; uninformative (synthetic n = 0.6 also drops only ≈ 0.03) |
| share of events: baseline / exogenous / triggered | 0.36 / 0.105 / 0.54 | – | – | 1713 human/nudger messages in window |
| time-rescaling KS D (p), Hawkes vs Poisson | 0.052 (0.000) vs 0.101 | 0.056 vs 0.109 | Exp(1) | smaller D is better |
| ΔAIC Hawkes − Poisson (B2) | -829.3 | -1058.4 | – | negative favors Hawkes |
| day-blocked CV Δℓ/event, Hawkes − Poisson (B2 / B3-30m) | 0.093 / 0.0243 | 0.102 / 0.0325 | 0 | – means < 3 days |
| guard recovery (TALK): n = 0.6 → B2, n = 0.9 → B2 | 0.52, 0.87 | 0.57, 0.88 | 0.6, 0.9 | 3 synthetic replicates |
| guard misspecification: n = 0 with real 10-min rate → B2 | 0.60 | 0.59 | 0 | not a valid null: the real 10-min counts already contain any cascades |
| P(burst ≥ 10), gap 60 s (TALK): data / Hawkes sim / Poisson sim | 0.220 / 0.241 / 0.245 | – | – | unfitted statistic (axis D) |

**Segments (goal period split at step changes; M1 B2):**

| seg | start → end | days | N | n̂ TALK (SE) | partially pooled | n̂ ALL (SE) | n_cross ≤300 s TALK |
|---|---|---|---|---|---|---|---|
| 0 | 2025-05-15 → 2025-05-21 | 5 | 4 | 0.66 (0.07, boot) | 0.63 | 0.66 (0.07) | 0.154 |
| 1 | 2025-05-22 → 2025-05-22 | 1 | 4 | 0.00 (–, profile) | – | 0.05 (–) | 0.000 |
| 2 | 2025-05-23 → 2025-06-18 | 19 | 4 | 0.52 (0.08, boot) | 0.56 | 0.53 (0.06) | 0.076 |

Within-period heterogeneity across segments (TALK): Cochran Q = 1.9, df = 1, p = 0.164, I² = 0.48, τ = 0.071. Partial pooling uses DerSimonian–Laird random effects within the period (exception d).

Figures: [`figures/diagnostics.pdf`](figures/diagnostics.pdf). Data: `data/processed/H03-self-excited-criticality/G04/` (per-period extracts of the fit, CV, bootstrap, guard, jitter, cascade and segment tables, plus `fits/<SET>_<MODEL>.npy`).

## Scorecard (period-specific axes)
| Axis | Score | Evidence |
|---|---|---|
| B assumptions | 1 | time-rescaling KS D: Hawkes 0.052 vs Poisson 0.101 (p_Hawkes = 0.000); 1 = better than Poisson but not necessarily Exp(1) |
| C adequacy | 1 | held-out Δℓ/event vs Poisson with the same B2 baseline = 0.093; vs the B3 30-min baseline = 0.0243. Capped at 1: no powered test against a Poisson null modulated at 10–30 min |
| D unfitted | 1 | burst-size tail (gap 60 s) closer to the Hawkes simulation than to Poisson: yes |
| F identifiability | 1 | n = 0 → B2 0.000; n = 0.6 → 0.52; but n = 0 with the real 10-min rate → 0.60 |

## Notes
- 2026-10-03: generated by `analysis/write_period_cards.py`. Exploratory, non-holdout days only.
- Long-window day(s) 2025-06-18: the window is 1.5–8× the period's median, likely two sessions with a long silent gap. This distorts the shared within-day shape (B2) and inflates held-out comparisons. Splitting days at long gaps is a planned scheme fix.

<!-- R1B START -->
## Round 1b (improved data, 2026-10-04)
H03 never read the buggy `activity_bins`; round 1b re-runs the round-1 specification (M1_B2 primary, M3 fast self/cross, day bootstrap B = 50 / 25, agent-shift null R = 5) on corrected inputs: exogenous drive from `kicks_classified` (human messages + nudges; round 1 also counted the operator's pause/resume bookends) and days split at operator-off gaps ≥ 60 min (`outages_fixed`). Here: exogenous messages in window 1713 → 1695; split / trimmed days: 2025-06-18.

| Events | n̂ round 1 [95% CI] | **n̂ round 1b** | fast n_x round 1 | **fast n_x round 1b** | n̂ B3 (lower bound) r1 → 1b |
| --- | --- | --- | --- | --- | --- |
| TALK | 0.55 [0.41, 0.63] | **0.55 [0.42, 0.64]** | 0.085 | **0.085** (shift null 0.018) | 0.38 → 0.38 |
| ALL | 0.56 [0.42, 0.64] | **0.56 [0.46, 0.63]** | 0.078 | **0.078** (shift null 0.020) | 0.43 → 0.43 |

Rule: P3 (n̂ ≥ 0.7): upper 95% bound below 0.7. Source: `data/processed/H03-self-excited-criticality/r1b/period_table.parquet` (`analysis/r1b.py`).
<!-- R1B END -->
