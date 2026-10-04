# H03 × G30: Adopt a park and get it cleaned! (2026-02-09 → 2026-02-16)

**Verdict:** failed
**Verdict (1b):** failed (round 1b, 2026-10-04: n̂ TALK 0.28 → 0.28 on corrected inputs; unchanged verdict)
**Role:** replication (exploratory)
**Period:** regime I · mode C (shared objective) · N = 12 at start (±0), 12.0 active per day on average · one shared room · 5 non-holdout days, median window 4.0 h. Splits inside the period: 2026-02-10 (NE10: D auto-nudger bot switched on; goal-periods scaffold: D auto-nudger bot (2026-02-10)).

Verdict rule: P3 (n̂ ≥ 0.7): upper 95% bound below 0.7. Verdicts use the primary statistic, n̂ for TALK under M1 with B2 + exogenous drive. n̂ depends on the baseline. A Poisson process with a rate modulated on 10–30 min scales can mimic it, and the 10-min jitter test has no power to separate the two (main card, jitter calibration). Read B2 n̂ as an upper value and B3 n̂ as a downward-biased lower bound. Any verdict here is descriptive, not mechanistic.

## Why this period
- Shared-objective week: S2 predicts these are more self-exciting than free weeks, and HH30's strong form says near critical.
- `goal-periods.md` ranks model 09 (Hawkes) #1 here: nudger introduced: a new outside excitation source; measure its response kernel
- Context (paraphrased dataset summary; secondary): Adopt a park and get it cleaned: shared repo, NYC/SF 311 data, two target parks. Auto-nudger (D) starts on 2026-02-10.
- Scaffold changes inside (goal-periods.md): D auto-nudger bot (2026-02-10)

## Prediction
*Written 2026-10-03 in the main card's Prediction section, before any fit on real data, and restated here for this period. This file was generated after the exploratory run, under the 2026-10-03 folder convention.*

- P3: n̂ (TALK) ≥ 0.7 (near critical). Counts against it: n̂ < 0.7.
- P2 (cross-period): above the F-period median.
- P6: the fast cross-agent part n_cross is higher in C than in F periods. P7: n̂_ALL > n̂_TALK, from the agent's own-loop excitation.
- G1 (guard): on n = 0 synthetic data with this period's fitted baseline, the pipeline returns n̂ ≈ 0, and the naive baseline B0 returns clearly more.

## Result
| Quantity | TALK | ALL | Null / reference | Reading |
|---|---|---|---|---|
| n̂ (M1, B2 + exo), 95% CI | **0.28** [0.07, 0.36] | 0.43 [0.31, 0.48] | Poisson n = 0 | CI: day-bootstrap |
| kernel timescale τ̂ (s) | 119 | 60 | – | τ̂ ≥ 1800 s means the kernel mimics the baseline |
| n̂, kernel τ ≤ 30 min | 0.28 | 0.43 | – | robustness variant |
| baseline ladder B0 / B1 / B2 / B3-2h / B3-30m | 0.35 / 0.35 / 0.28 / 0.30 / 0.16 | 0.48 / 0.46 / 0.43 / 0.44 / 0.33 | guard: n = 0 → B0 0.25, B2 0.000 (TALK) | falls with baseline flexibility |
| sum-of-exp kernel (M2): n, n(τ ≤ 300 s) | 0.26, 0.26 | 0.46, 0.46 | – | ΔAIC grid − exp (TALK) 8.4 |
| power-law-constrained kernel θ | -0.35 | -0.13 | – | ll(pl) − ll(exp) (TALK) -9.5 |
| own-loop n_self (τ ≤ 300 s, M3) | 0.05 | 0.36 | – | scheduler / own-loop part |
| social n_cross (τ ≤ 300 s, M3) | 0.099 | 0.081 | agent-shift null 0.027 / 0.011 | real − null (TALK) = 0.072 |
| pooled fast n̂ (τ ≤ 5 min) | 0.28 | 0.43 | 10-min jitter 0.24 / 0.43 | real − jittered (TALK) = 0.04; uninformative (synthetic n = 0.6 also drops only ≈ 0.03) |
| share of events: baseline / exogenous / triggered | 0.69 / 0.015 / 0.27 | – | – | 29 human/nudger messages in window |
| time-rescaling KS D (p), Hawkes vs Poisson | 0.020 (0.246) vs 0.021 | 0.045 vs 0.057 | Exp(1) | smaller D is better |
| ΔAIC Hawkes − Poisson (B2) | -31.7 | -181.8 | – | negative favors Hawkes |
| day-blocked CV Δℓ/event, Hawkes − Poisson (B2 / B3-30m) | 0.009 / 0.0005 | 0.020 / 0.0089 | 0 | – means < 3 days |
| guard recovery (TALK): n = 0.6 → B2, n = 0.9 → B2 | 0.58, 0.81 | 0.54, 0.85 | 0.6, 0.9 | 3 synthetic replicates |
| guard misspecification: n = 0 with real 10-min rate → B2 | 0.38 | 0.49 | 0 | not a valid null: the real 10-min counts already contain any cascades |
| P(burst ≥ 10), gap 60 s (TALK): data / Hawkes sim / Poisson sim | 0.308 / 0.287 / 0.308 | – | – | unfitted statistic (axis D) |

**Segments (goal period split at step changes; M1 B2):**

| seg | start → end | days | N | n̂ TALK (SE) | partially pooled | n̂ ALL (SE) | n_cross ≤300 s TALK |
|---|---|---|---|---|---|---|---|
| 0 | 2026-02-09 → 2026-02-09 | 1 | 12 | 0.27 (0.21, profile) | 0.24 | 0.47 (0.08) | 0.010 |
| 1 | 2026-02-10 → 2026-02-13 | 4 | 12 | 0.24 (0.08, boot) | 0.24 | 0.36 (0.05) | 0.118 |

Within-period heterogeneity across segments (TALK): Cochran Q = 0.0, df = 1, p = 0.902, I² = 0.00, τ = 0.000. Partial pooling uses DerSimonian–Laird random effects within the period (exception d).

Figures: [`figures/diagnostics.pdf`](figures/diagnostics.pdf). Data: `data/processed/H03-self-excited-criticality/G30/` (per-period extracts of the fit, CV, bootstrap, guard, jitter, cascade and segment tables, plus `fits/<SET>_<MODEL>.npy`).

## Scorecard (period-specific axes)
| Axis | Score | Evidence |
|---|---|---|
| B assumptions | 1 | time-rescaling KS D: Hawkes 0.020 vs Poisson 0.021 (p_Hawkes = 0.246); 1 = better than Poisson but not necessarily Exp(1) |
| C adequacy | 1 | held-out Δℓ/event vs Poisson with the same B2 baseline = 0.009; vs the B3 30-min baseline = 0.0005. Capped at 1: no powered test against a Poisson null modulated at 10–30 min |
| D unfitted | 0 | burst-size tail (gap 60 s) closer to the Hawkes simulation than to Poisson: no |
| F identifiability | 1 | n = 0 → B2 0.000; n = 0.6 → 0.58; but n = 0 with the real 10-min rate → 0.38 |

## Notes
- 2026-10-03: generated by `analysis/write_period_cards.py`. Exploratory, non-holdout days only.

<!-- R1B START -->
## Round 1b (improved data, 2026-10-04)
H03 never read the buggy `activity_bins`; round 1b re-runs the round-1 specification (M1_B2 primary, M3 fast self/cross, day bootstrap B = 50 / 25, agent-shift null R = 5) on corrected inputs: exogenous drive from `kicks_classified` (human messages + nudges; round 1 also counted the operator's pause/resume bookends) and days split at operator-off gaps ≥ 60 min (`outages_fixed`). Here: exogenous messages in window 29 → 25; split / trimmed days: none.

| Events | n̂ round 1 [95% CI] | **n̂ round 1b** | fast n_x round 1 | **fast n_x round 1b** | n̂ B3 (lower bound) r1 → 1b |
| --- | --- | --- | --- | --- | --- |
| TALK | 0.28 [0.07, 0.36] | **0.28 [0.12, 0.35]** | 0.099 | **0.100** (shift null 0.006) | 0.16 → 0.16 |
| ALL | 0.43 [0.31, 0.48] | **0.43 [0.24, 0.48]** | 0.081 | **0.085** (shift null 0.017) | 0.33 → 0.33 |

Rule: P3 (n̂ ≥ 0.7): upper 95% bound below 0.7. Source: `data/processed/H03-self-excited-criticality/r1b/period_table.parquet` (`analysis/r1b.py`).
<!-- R1B END -->
