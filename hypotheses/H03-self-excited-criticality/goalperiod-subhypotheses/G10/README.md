# H03 × G10: Complete as many games as you can in a week! (2025-08-18 → 2025-08-25)

**Verdict:** descriptive
**Verdict (1b):** descriptive (round 1b, 2026-10-04: n̂ TALK 0.22 → 0.22 on corrected inputs; unchanged verdict)
**Role:** replication (exploratory)
**Period:** regime I · mode I (each agent its own objective) · N = 7 at start (±0), 7.0 active per day on average · one shared room · 5 non-holdout days, median window 3.0 h. Splits inside the period: 2025-08-20 (NE03: Number of chat messages fetched into context limit).

Verdict rule: no period-level prediction for mode I; enters P2/P4 as a comparison point. Verdicts use the primary statistic, n̂ for TALK under M1 with B2 + exogenous drive. n̂ depends on the baseline. A Poisson process with a rate modulated on 10–30 min scales can mimic it, and the 10-min jitter test has no power to separate the two (main card, jitter calibration). Read B2 n̂ as an upper value and B3 n̂ as a downward-biased lower bound. Any verdict here is descriptive, not mechanistic.

## Why this period
- Individual-objective week: a comparison point for the mode effect (P2, P4).
- `goal-periods.md` ranks model 09 (Hawkes) #2 here: onboarding three agents at once: response kernels to newcomers
- Context (paraphrased dataset summary; secondary): Complete as many games as possible (turn-based, since real-time games are hard to play through screenshots). GPT-5, Grok 4 and Claude Opus 4.1 joined; N jumps from 4 to 7.
- Scaffold changes inside (goal-periods.md): expanded hours (2025-08-18)

## Prediction
*Written 2026-10-03 in the main card's Prediction section, before any fit on real data, and restated here for this period. This file was generated after the exploratory run, under the 2026-10-03 folder convention.*

- No period-level threshold. The period enters P2/P4 as a comparison point; S2 implies it sits below the shared-objective periods.
- P6: the fast cross-agent part n_cross is higher in C than in F periods. P7: n̂_ALL > n̂_TALK, from the agent's own-loop excitation.
- G1 (guard): on n = 0 synthetic data with this period's fitted baseline, the pipeline returns n̂ ≈ 0, and the naive baseline B0 returns clearly more.

## Result
| Quantity | TALK | ALL | Null / reference | Reading |
|---|---|---|---|---|
| n̂ (M1, B2 + exo), 95% CI | **0.22** [0.17, 0.59] | 0.48 [0.25, 0.69] | Poisson n = 0 | CI: day-bootstrap |
| kernel timescale τ̂ (s) | 6 | 95 | – | τ̂ ≥ 1800 s means the kernel mimics the baseline |
| n̂, kernel τ ≤ 30 min | 0.22 | 0.48 | – | robustness variant |
| baseline ladder B0 / B1 / B2 / B3-2h / B3-30m | 0.34 / 0.24 / 0.22 / 0.23 / 0.19 | 0.60 / 0.55 / 0.48 / 0.54 / 0.26 | guard: n = 0 → B0 0.40, B2 0.000 (TALK) | falls with baseline flexibility |
| sum-of-exp kernel (M2): n, n(τ ≤ 300 s) | 0.57, 0.48 | 0.54, 0.45 | – | ΔAIC grid − exp (TALK) -18.7 |
| power-law-constrained kernel θ | 0.26 | -0.29 | – | ll(pl) − ll(exp) (TALK) 9.2 |
| own-loop n_self (τ ≤ 300 s, M3) | 0.32 | 0.37 | – | scheduler / own-loop part |
| social n_cross (τ ≤ 300 s, M3) | 0.069 | 0.158 | agent-shift null 0.021 / 0.063 | real − null (TALK) = 0.048 |
| pooled fast n̂ (τ ≤ 5 min) | 0.22 | 0.48 | 10-min jitter 0.68 / 0.50 | real − jittered (TALK) = -0.46; uninformative (synthetic n = 0.6 also drops only ≈ 0.03) |
| share of events: baseline / exogenous / triggered | 0.76 / 0.013 / 0.22 | – | – | 21 human/nudger messages in window |
| time-rescaling KS D (p), Hawkes vs Poisson | 0.038 (0.053) vs 0.119 | 0.043 vs 0.083 | Exp(1) | smaller D is better |
| ΔAIC Hawkes − Poisson (B2) | -429.1 | -101.2 | – | negative favors Hawkes |
| day-blocked CV Δℓ/event, Hawkes − Poisson (B2 / B3-30m) | -0.050 / -0.0837 | 0.040 / 0.0089 | 0 | – means < 3 days |
| guard recovery (TALK): n = 0.6 → B2, n = 0.9 → B2 | 0.60, 0.89 | 0.49, 0.80 | 0.6, 0.9 | 3 synthetic replicates |
| guard misspecification: n = 0 with real 10-min rate → B2 | 0.68 | 0.56 | 0 | not a valid null: the real 10-min counts already contain any cascades |
| P(burst ≥ 10), gap 60 s (TALK): data / Hawkes sim / Poisson sim | 0.100 / 0.092 / 0.097 | – | – | unfitted statistic (axis D) |

**Segments (goal period split at step changes; M1 B2):**

| seg | start → end | days | N | n̂ TALK (SE) | partially pooled | n̂ ALL (SE) | n_cross ≤300 s TALK |
|---|---|---|---|---|---|---|---|
| 0 | 2025-08-18 → 2025-08-19 | 2 | 7 | 0.38 (0.03, profile) | 0.38 | 0.61 (0.12) | 0.072 |
| 1 | 2025-08-20 → 2025-08-22 | 3 | 7 | 0.24 (0.07, boot) | 0.28 | 0.27 (0.06) | 0.050 |

Within-period heterogeneity across segments (TALK): Cochran Q = 3.4, df = 1, p = 0.0659, I² = 0.70, τ = 0.084. Partial pooling uses DerSimonian–Laird random effects within the period (exception d).

Figures: [`figures/diagnostics.pdf`](figures/diagnostics.pdf). Data: `data/processed/H03-self-excited-criticality/G10/` (per-period extracts of the fit, CV, bootstrap, guard, jitter, cascade and segment tables, plus `fits/<SET>_<MODEL>.npy`).

## Scorecard (period-specific axes)
| Axis | Score | Evidence |
|---|---|---|
| B assumptions | 1 | time-rescaling KS D: Hawkes 0.038 vs Poisson 0.119 (p_Hawkes = 0.053); 1 = better than Poisson but not necessarily Exp(1) |
| C adequacy | 0 | held-out Δℓ/event vs Poisson with the same B2 baseline = -0.050; vs the B3 30-min baseline = -0.0837. Capped at 1: no powered test against a Poisson null modulated at 10–30 min |
| D unfitted | 0 | burst-size tail (gap 60 s) closer to the Hawkes simulation than to Poisson: no |
| F identifiability | 1 | n = 0 → B2 0.000; n = 0.6 → 0.60; but n = 0 with the real 10-min rate → 0.68 |

## Notes
- 2026-10-03: generated by `analysis/write_period_cards.py`. Exploratory, non-holdout days only.

<!-- R1B START -->
## Round 1b (improved data, 2026-10-04)
H03 never read the buggy `activity_bins`; round 1b re-runs the round-1 specification (M1_B2 primary, M3 fast self/cross, day bootstrap B = 50 / 25, agent-shift null R = 5) on corrected inputs: exogenous drive from `kicks_classified` (human messages + nudges; round 1 also counted the operator's pause/resume bookends) and days split at operator-off gaps ≥ 60 min (`outages_fixed`). Here: exogenous messages in window 21 → 17; split / trimmed days: none.

| Events | n̂ round 1 [95% CI] | **n̂ round 1b** | fast n_x round 1 | **fast n_x round 1b** | n̂ B3 (lower bound) r1 → 1b |
| --- | --- | --- | --- | --- | --- |
| TALK | 0.22 [0.17, 0.59] | **0.22 [0.18, 0.55]** | 0.069 | **0.069** (shift null 0.026) | 0.19 → 0.19 |
| ALL | 0.48 [0.25, 0.69] | **0.46 [0.26, 0.67]** | 0.158 | **0.130** (shift null 0.035) | 0.26 → 0.26 |

Rule: no period-level prediction for mode I; enters P2/P4 as a comparison point. Source: `data/processed/H03-self-excited-criticality/r1b/period_table.parquet` (`analysis/r1b.py`).
<!-- R1B END -->
