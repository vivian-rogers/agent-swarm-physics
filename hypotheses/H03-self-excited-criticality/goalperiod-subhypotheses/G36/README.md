# H03 × G36: Interact with other AI agents outside the Village! (2026-03-23 → 2026-03-30)

**Verdict:** failed
**Verdict (1b):** failed (round 1b, 2026-10-04: n̂ TALK 0.29 → 0.29 on corrected inputs; unchanged verdict)
**Role:** exploratory
**Period:** regime II/III · mode C (shared objective) · N = 13 at start (±0), 13.0 active per day on average · rooms (agents see only their room) · 5 non-holdout days, median window 4.0 h. Splits inside the period: 2026-03-24 (NE14: Consolidate tool, pause tool, F perma-computer-use; goal-periods scaffold: F perma-computer-use (2026-03-24)); 2026-03-26 (NE16: Fix: contradictory "never update memory" instructi).

Verdict rule: P3 (n̂ ≥ 0.7): upper 95% bound below 0.7. Verdicts use the primary statistic, n̂ for TALK under M1 with B2 + exogenous drive. n̂ depends on the baseline. A Poisson process with a rate modulated on 10–30 min scales can mimic it, and the 10-min jitter test has no power to separate the two (main card, jitter calibration). Read B2 n̂ as an upper value and B3 n̂ as a downward-biased lower bound. Any verdict here is descriptive, not mechanistic.

## Why this period
- Shared-objective week: S2 predicts these are more self-exciting than free weeks, and HH30's strong form says near critical.
- `goal-periods.md` ranks model 09 (Hawkes) #2 here: compare branching ratio and kernels across F
- Context (paraphrased dataset summary; secondary): Interact with AI agents outside the Village: teams, public repos. **Perma-computer-use (F) lands mid-goal** (2026-03-24).
- Scaffold changes inside (goal-periods.md): F perma-computer-use (2026-03-24)

## Prediction
*Written 2026-10-03 in the main card's Prediction section, before any fit on real data, and restated here for this period. This file was generated after the exploratory run, under the 2026-10-03 folder convention.*

- P3: n̂ (TALK) ≥ 0.7 (near critical). Counts against it: n̂ < 0.7.
- P2 (cross-period): above the F-period median.
- P6: the fast cross-agent part n_cross is higher in C than in F periods. P7: n̂_ALL > n̂_TALK, from the agent's own-loop excitation.
- G1 (guard): on n = 0 synthetic data with this period's fitted baseline, the pipeline returns n̂ ≈ 0, and the naive baseline B0 returns clearly more.

## Result
| Quantity | TALK | ALL | Null / reference | Reading |
|---|---|---|---|---|
| n̂ (M1, B2 + exo), 95% CI | **0.29** [0.14, 0.37] | 0.18 [0.02, 0.41] | Poisson n = 0 | CI: day-bootstrap |
| kernel timescale τ̂ (s) | 79 | 58 | – | τ̂ ≥ 1800 s means the kernel mimics the baseline |
| n̂, kernel τ ≤ 30 min | 0.29 | 0.18 | – | robustness variant |
| baseline ladder B0 / B1 / B2 / B3-2h / B3-30m | 0.46 / 0.34 / 0.29 / 0.24 / 0.15 | 0.37 / 0.22 / 0.18 / 0.12 / 0.06 | guard: n = 0 → B0 0.36, B2 0.000 (TALK) | falls with baseline flexibility |
| sum-of-exp kernel (M2): n, n(τ ≤ 300 s) | 0.31, 0.31 | 0.38, 0.11 | – | ΔAIC grid − exp (TALK) 9.9 |
| power-law-constrained kernel θ | -0.27 | -0.42 | – | ll(pl) − ll(exp) (TALK) -16.6 |
| own-loop n_self (τ ≤ 300 s, M3) | 0.11 | 0.05 | – | scheduler / own-loop part |
| social n_cross (τ ≤ 300 s, M3) | 0.008 | 0.038 | agent-shift null 0.002 / 0.033 | real − null (TALK) = 0.006 |
| pooled fast n̂ (τ ≤ 5 min) | 0.29 | 0.18 | 10-min jitter 0.23 / 0.27 | real − jittered (TALK) = 0.06; uninformative (synthetic n = 0.6 also drops only ≈ 0.03) |
| share of events: baseline / exogenous / triggered | 0.69 / 0.015 / 0.29 | – | – | 13 human/nudger messages in window |
| time-rescaling KS D (p), Hawkes vs Poisson | 0.030 (0.083) vs 0.034 | 0.021 vs 0.028 | Exp(1) | smaller D is better |
| ΔAIC Hawkes − Poisson (B2) | -46.5 | -20.5 | – | negative favors Hawkes |
| day-blocked CV Δℓ/event, Hawkes − Poisson (B2 / B3-30m) | 0.025 / 0.0030 | 0.003 / -0.0024 | 0 | – means < 3 days |
| guard recovery (TALK): n = 0.6 → B2, n = 0.9 → B2 | 0.54, 0.86 | 0.57, 0.87 | 0.6, 0.9 | 3 synthetic replicates |
| guard misspecification: n = 0 with real 10-min rate → B2 | 0.40 | 0.34 | 0 | not a valid null: the real 10-min counts already contain any cascades |
| P(burst ≥ 10), gap 60 s (TALK): data / Hawkes sim / Poisson sim | 0.146 / 0.112 / 0.101 | – | – | unfitted statistic (axis D) |

**Segments (goal period split at step changes; M1 B2):**

| seg | start → end | days | N | n̂ TALK (SE) | partially pooled | n̂ ALL (SE) | n_cross ≤300 s TALK |
|---|---|---|---|---|---|---|---|
| 0 | 2026-03-23 → 2026-03-23 | 1 | 13 | 0.03 (–, profile) | – | 0.23 (0.07) | 0.000 |
| 1 | 2026-03-24 → 2026-03-25 | 2 | 13 | 0.20 (0.08, profile) | 0.24 | 0.29 (0.12) | 0.000 |
| 2 | 2026-03-26 → 2026-03-27 | 2 | 13 | 0.35 (0.06, profile) | 0.33 | 0.16 (0.05) | 0.077 |

Within-period heterogeneity across segments (TALK): Cochran Q = 2.4, df = 1, p = 0.122, I² = 0.58, τ = 0.084. Partial pooling uses DerSimonian–Laird random effects within the period (exception d).

Figures: [`figures/diagnostics.pdf`](figures/diagnostics.pdf). Data: `data/processed/H03-self-excited-criticality/G36/` (per-period extracts of the fit, CV, bootstrap, guard, jitter, cascade and segment tables, plus `fits/<SET>_<MODEL>.npy`).

## Scorecard (period-specific axes)
| Axis | Score | Evidence |
|---|---|---|
| B assumptions | 1 | time-rescaling KS D: Hawkes 0.030 vs Poisson 0.034 (p_Hawkes = 0.083); 1 = better than Poisson but not necessarily Exp(1) |
| C adequacy | 1 | held-out Δℓ/event vs Poisson with the same B2 baseline = 0.025; vs the B3 30-min baseline = 0.0030. Capped at 1: no powered test against a Poisson null modulated at 10–30 min |
| D unfitted | 1 | burst-size tail (gap 60 s) closer to the Hawkes simulation than to Poisson: yes |
| F identifiability | 1 | n = 0 → B2 0.000; n = 0.6 → 0.54; but n = 0 with the real 10-min rate → 0.40 |

## Notes
- 2026-10-03: generated by `analysis/write_period_cards.py`. Exploratory, non-holdout days only.
- Regime III (perma-computer-use): `events_core` holds chat and session events, but not computer-use turns, so ALL means something different here than in regime I.

<!-- R1B START -->
## Round 1b (improved data, 2026-10-04)
H03 never read the buggy `activity_bins`; round 1b re-runs the round-1 specification (M1_B2 primary, M3 fast self/cross, day bootstrap B = 50 / 25, agent-shift null R = 5) on corrected inputs: exogenous drive from `kicks_classified` (human messages + nudges; round 1 also counted the operator's pause/resume bookends) and days split at operator-off gaps ≥ 60 min (`outages_fixed`). Here: exogenous messages in window 13 → 8; split / trimmed days: none.

| Events | n̂ round 1 [95% CI] | **n̂ round 1b** | fast n_x round 1 | **fast n_x round 1b** | n̂ B3 (lower bound) r1 → 1b |
| --- | --- | --- | --- | --- | --- |
| TALK | 0.29 [0.14, 0.37] | **0.29 [0.13, 0.36]** | 0.008 | **0.011** (shift null 0.002) | 0.15 → 0.14 |
| ALL | 0.18 [0.02, 0.41] | **0.18 [0.02, 0.42]** | 0.038 | **0.036** (shift null 0.079) | 0.06 → 0.06 |

Rule: P3 (n̂ ≥ 0.7): upper 95% bound below 0.7. Source: `data/processed/H03-self-excited-criticality/r1b/period_table.parquet` (`analysis/r1b.py`).
<!-- R1B END -->
