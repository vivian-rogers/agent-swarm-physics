# H03 × G21: Forecast the abilities and effects of AI (2025-12-01 → 2025-12-08)

**Verdict:** descriptive
**Verdict (1b):** descriptive (round 1b, 2026-10-04: n̂ TALK 0.68 → 0.63 on corrected inputs; unchanged verdict)
**Role:** exploratory
**Period:** regime I · mode I (each agent its own objective) · N = 8 at start (+1), 8.4 active per day on average · one shared room · 5 non-holdout days, median window 4.0 h. Splits inside the period: 2025-12-02 (goal-periods scaffold: text-only agents supported (2025-12-02)); 2025-12-04 (NE07: Prompt: "don't do nothing"; roster_joined: DeepSeek-V3.2).

Verdict rule: no period-level prediction for mode I; enters P2/P4 as a comparison point. Verdicts use the primary statistic, n̂ for TALK under M1 with B2 + exogenous drive. n̂ depends on the baseline. A Poisson process with a rate modulated on 10–30 min scales can mimic it, and the 10-min jitter test has no power to separate the two (main card, jitter calibration). Read B2 n̂ as an upper value and B3 n̂ as a downward-biased lower bound. Any verdict here is descriptive, not mechanistic.

## Why this period
- Individual-objective week: a comparison point for the mode effect (P2, P4).
- Context (paraphrased dataset summary; secondary): Forecast AI abilities and effects. Agents deliberately drafted independent predictions first, then compared.
- Scaffold changes inside (goal-periods.md): text-only agents supported (2025-12-02)

## Prediction
*Written 2026-10-03 in the main card's Prediction section, before any fit on real data, and restated here for this period. This file was generated after the exploratory run, under the 2026-10-03 folder convention.*

- No period-level threshold. The period enters P2/P4 as a comparison point; S2 implies it sits below the shared-objective periods.
- P6: the fast cross-agent part n_cross is higher in C than in F periods. P7: n̂_ALL > n̂_TALK, from the agent's own-loop excitation.
- G1 (guard): on n = 0 synthetic data with this period's fitted baseline, the pipeline returns n̂ ≈ 0, and the naive baseline B0 returns clearly more.

## Result
| Quantity | TALK | ALL | Null / reference | Reading |
|---|---|---|---|---|
| n̂ (M1, B2 + exo), 95% CI | **0.68** [0.09, 1.01] | 0.31 [0.14, 0.66] | Poisson n = 0 | CI: day-bootstrap |
| kernel timescale τ̂ (s) | 650 | 108 | – | τ̂ ≥ 1800 s means the kernel mimics the baseline |
| n̂, kernel τ ≤ 30 min | 0.68 | 0.31 | – | robustness variant |
| baseline ladder B0 / B1 / B2 / B3-2h / B3-30m | 0.82 / 0.81 / 0.68 / 0.68 / 1.64 | 0.81 / 0.79 / 0.31 / 0.64 / 0.10 | guard: n = 0 → B0 0.65, B2 0.000 (TALK) | falls with baseline flexibility |
| sum-of-exp kernel (M2): n, n(τ ≤ 300 s) | 0.73, 0.19 | 0.55, 0.17 | – | ΔAIC grid − exp (TALK) 9.0 |
| power-law-constrained kernel θ | -0.97 | -0.45 | – | ll(pl) − ll(exp) (TALK) -4.4 |
| own-loop n_self (τ ≤ 300 s, M3) | 0.00 | 0.07 | – | scheduler / own-loop part |
| social n_cross (τ ≤ 300 s, M3) | 0.070 | 0.102 | agent-shift null 0.022 / 0.032 | real − null (TALK) = 0.048 |
| pooled fast n̂ (τ ≤ 5 min) | 0.52 | 0.31 | 10-min jitter 0.45 / 0.36 | real − jittered (TALK) = 0.07; uninformative (synthetic n = 0.6 also drops only ≈ 0.03) |
| share of events: baseline / exogenous / triggered | 0.35 / 0.008 / 0.64 | – | – | 6 human/nudger messages in window |
| time-rescaling KS D (p), Hawkes vs Poisson | 0.024 (0.129) vs 0.027 | 0.023 vs 0.032 | Exp(1) | smaller D is better |
| ΔAIC Hawkes − Poisson (B2) | -58.6 | -32.7 | – | negative favors Hawkes |
| day-blocked CV Δℓ/event, Hawkes − Poisson (B2 / B3-30m) | 0.029 / -0.0010 | 0.004 / -0.0036 | 0 | – means < 3 days |
| guard recovery (TALK): n = 0.6 → B2, n = 0.9 → B2 | 0.28, 0.69 | 0.46, 0.84 | 0.6, 0.9 | 3 synthetic replicates |
| guard misspecification: n = 0 with real 10-min rate → B2 | 0.63 | 0.57 | 0 | not a valid null: the real 10-min counts already contain any cascades |
| P(burst ≥ 10), gap 60 s (TALK): data / Hawkes sim / Poisson sim | 0.204 / 0.201 / 0.196 | – | – | unfitted statistic (axis D) |

**Segments (goal period split at step changes; M1 B2):**

| seg | start → end | days | N | n̂ TALK (SE) | partially pooled | n̂ ALL (SE) | n_cross ≤300 s TALK |
|---|---|---|---|---|---|---|---|
| 0 | 2025-12-01 → 2025-12-01 | 1 | 8 | 0.13 (–, profile) | – | 0.31 (0.06) | 0.130 |
| 1 | 2025-12-02 → 2025-12-03 | 2 | 8 | 1.00 (0.06, profile) | – | 0.72 (0.18) | 0.052 |
| 2 | 2025-12-04 → 2025-12-05 | 2 | 9 | 0.22 (–, profile) | – | 0.21 (–) | 0.029 |

Figures: [`figures/diagnostics.pdf`](figures/diagnostics.pdf). Data: `data/processed/H03-self-excited-criticality/G21/` (per-period extracts of the fit, CV, bootstrap, guard, jitter, cascade and segment tables, plus `fits/<SET>_<MODEL>.npy`).

## Scorecard (period-specific axes)
| Axis | Score | Evidence |
|---|---|---|
| B assumptions | 1 | time-rescaling KS D: Hawkes 0.024 vs Poisson 0.027 (p_Hawkes = 0.129); 1 = better than Poisson but not necessarily Exp(1) |
| C adequacy | 1 | held-out Δℓ/event vs Poisson with the same B2 baseline = 0.029; vs the B3 30-min baseline = -0.0010. Capped at 1: no powered test against a Poisson null modulated at 10–30 min |
| D unfitted | 1 | burst-size tail (gap 60 s) closer to the Hawkes simulation than to Poisson: yes |
| F identifiability | 1 | n = 0 → B2 0.000; n = 0.6 → 0.28; but n = 0 with the real 10-min rate → 0.63 |

## Notes
- 2026-10-03: generated by `analysis/write_period_cards.py`. Exploratory, non-holdout days only.

<!-- R1B START -->
## Round 1b (improved data, 2026-10-04)
H03 never read the buggy `activity_bins`; round 1b re-runs the round-1 specification (M1_B2 primary, M3 fast self/cross, day bootstrap B = 50 / 25, agent-shift null R = 5) on corrected inputs: exogenous drive from `kicks_classified` (human messages + nudges; round 1 also counted the operator's pause/resume bookends) and days split at operator-off gaps ≥ 60 min (`outages_fixed`). Here: exogenous messages in window 6 → 3; split / trimmed days: none.

| Events | n̂ round 1 [95% CI] | **n̂ round 1b** | fast n_x round 1 | **fast n_x round 1b** | n̂ B3 (lower bound) r1 → 1b |
| --- | --- | --- | --- | --- | --- |
| TALK | 0.68 [0.09, 1.01] | **0.63 [0.06, 0.98]** | 0.070 | **0.074** (shift null 0.020) | 1.64 → 1.20 |
| ALL | 0.31 [0.14, 0.66] | **0.28 [0.15, 1.05]** | 0.102 | **0.101** (shift null 0.048) | 0.10 → 0.10 |

Rule: no period-level prediction for mode I; enters P2/P4 as a comparison point. Source: `data/processed/H03-self-excited-criticality/r1b/period_table.parquet` (`analysis/r1b.py`).
<!-- R1B END -->
