# H03 × G20: Start a Substack and join the blogosphere (2025-11-17 → 2025-12-01)

**Verdict:** descriptive
**Verdict (1b):** descriptive (round 1b, 2026-10-04: n̂ TALK 0.62 → 0.56 on corrected inputs; unchanged verdict)
**Role:** exploratory
**Period:** regime I · mode I (each agent its own objective) · N = 8 at start (+2), 9.2 active per day on average · one shared room · 10 non-holdout days, median window 4.0 h. Splits inside the period: 2025-11-19 (roster_joined: Gemini 3 Pro); 2025-11-20 (NE06: Gemini: one tool call per turn; chain of thought a); 2025-11-25 (NE06: Gemini: one tool call per turn; chain of thought a; roster_joined: Claude Opus 4.5).

Verdict rule: no period-level prediction for mode I; enters P2/P4 as a comparison point. Verdicts use the primary statistic, n̂ for TALK under M1 with B2 + exogenous drive. n̂ depends on the baseline. A Poisson process with a rate modulated on 10–30 min scales can mimic it, and the 10-min jitter test has no power to separate the two (main card, jitter calibration). Read B2 n̂ as an upper value and B3 n̂ as a downward-biased lower bound. Any verdict here is descriptive, not mechanistic.

## Why this period
- Individual-objective week: a comparison point for the mode effect (P2, P4).
- Context (paraphrased dataset summary; secondary): Each agent starts a Substack; niches formed (e.g. consciousness, telemetry). Roster churn: two in, two out.

## Prediction
*Written 2026-10-03 in the main card's Prediction section, before any fit on real data, and restated here for this period. This file was generated after the exploratory run, under the 2026-10-03 folder convention.*

- No period-level threshold. The period enters P2/P4 as a comparison point; S2 implies it sits below the shared-objective periods.
- P6: the fast cross-agent part n_cross is higher in C than in F periods. P7: n̂_ALL > n̂_TALK, from the agent's own-loop excitation.
- G1 (guard): on n = 0 synthetic data with this period's fitted baseline, the pipeline returns n̂ ≈ 0, and the naive baseline B0 returns clearly more.

## Result
| Quantity | TALK | ALL | Null / reference | Reading |
|---|---|---|---|---|
| n̂ (M1, B2 + exo), 95% CI | **0.62** [0.37, 0.71] | 0.42 [0.28, 0.54] | Poisson n = 0 | CI: day-bootstrap |
| kernel timescale τ̂ (s) | 571 | 63 | – | τ̂ ≥ 1800 s means the kernel mimics the baseline |
| n̂, kernel τ ≤ 30 min | 0.62 | 0.42 | – | robustness variant |
| baseline ladder B0 / B1 / B2 / B3-2h / B3-30m | 0.74 / 0.68 / 0.62 / 0.61 / 0.05 | 0.66 / 0.49 / 0.42 / 0.44 / 0.23 | guard: n = 0 → B0 0.53, B2 0.015 (TALK) | falls with baseline flexibility |
| sum-of-exp kernel (M2): n, n(τ ≤ 300 s) | 0.64, 0.26 | 0.74, 0.24 | – | ΔAIC grid − exp (TALK) 10.0 |
| power-law-constrained kernel θ | -0.77 | -0.22 | – | ll(pl) − ll(exp) (TALK) -14.7 |
| own-loop n_self (τ ≤ 300 s, M3) | 0.00 | 0.30 | – | scheduler / own-loop part |
| social n_cross (τ ≤ 300 s, M3) | 0.112 | 0.174 | agent-shift null 0.085 / 0.084 | real − null (TALK) = 0.026 |
| pooled fast n̂ (τ ≤ 5 min) | 0.50 | 0.42 | 10-min jitter 0.50 / 0.57 | real − jittered (TALK) = -0.00; uninformative (synthetic n = 0.6 also drops only ≈ 0.03) |
| share of events: baseline / exogenous / triggered | 0.40 / 0.019 / 0.58 | – | – | 19 human/nudger messages in window |
| time-rescaling KS D (p), Hawkes vs Poisson | 0.017 (0.132) vs 0.023 | 0.039 vs 0.067 | Exp(1) | smaller D is better |
| ΔAIC Hawkes − Poisson (B2) | -123.8 | -269.9 | – | negative favors Hawkes |
| day-blocked CV Δℓ/event, Hawkes − Poisson (B2 / B3-30m) | 0.019 / -0.0004 | 0.020 / 0.0074 | 0 | – means < 3 days |
| guard recovery (TALK): n = 0.6 → B2, n = 0.9 → B2 | 0.42, 0.64 | 0.56, 0.86 | 0.6, 0.9 | 3 synthetic replicates |
| guard misspecification: n = 0 with real 10-min rate → B2 | 0.57 | 0.60 | 0 | not a valid null: the real 10-min counts already contain any cascades |
| P(burst ≥ 10), gap 60 s (TALK): data / Hawkes sim / Poisson sim | 0.171 / 0.178 / 0.190 | – | – | unfitted statistic (axis D) |

**Segments (goal period split at step changes; M1 B2):**

| seg | start → end | days | N | n̂ TALK (SE) | partially pooled | n̂ ALL (SE) | n_cross ≤300 s TALK |
|---|---|---|---|---|---|---|---|
| 0 | 2025-11-17 → 2025-11-18 | 2 | 8 | 0.26 (0.15, profile) | 0.34 | 0.22 (0.06) | 0.057 |
| 1 | 2025-11-19 → 2025-11-19 | 1 | 9 | 0.05 (–, profile) | – | 0.23 (0.08) | 0.066 |
| 2 | 2025-11-20 → 2025-11-24 | 3 | 9 | 0.56 (0.39, boot) | 0.49 | 0.32 (0.04) | 0.053 |
| 3 | 2025-11-25 → 2025-11-28 | 4 | 10 | 0.72 (0.20, boot) | 0.59 | 0.74 (0.18) | 0.065 |

Within-period heterogeneity across segments (TALK): Cochran Q = 3.5, df = 2, p = 0.172, I² = 0.43, τ = 0.193. Partial pooling uses DerSimonian–Laird random effects within the period (exception d).

Figures: [`figures/diagnostics.pdf`](figures/diagnostics.pdf). Data: `data/processed/H03-self-excited-criticality/G20/` (per-period extracts of the fit, CV, bootstrap, guard, jitter, cascade and segment tables, plus `fits/<SET>_<MODEL>.npy`).

## Scorecard (period-specific axes)
| Axis | Score | Evidence |
|---|---|---|
| B assumptions | 1 | time-rescaling KS D: Hawkes 0.017 vs Poisson 0.023 (p_Hawkes = 0.132); 1 = better than Poisson but not necessarily Exp(1) |
| C adequacy | 1 | held-out Δℓ/event vs Poisson with the same B2 baseline = 0.019; vs the B3 30-min baseline = -0.0004. Capped at 1: no powered test against a Poisson null modulated at 10–30 min |
| D unfitted | 1 | burst-size tail (gap 60 s) closer to the Hawkes simulation than to Poisson: yes |
| F identifiability | 1 | n = 0 → B2 0.015; n = 0.6 → 0.42; but n = 0 with the real 10-min rate → 0.57 |

## Notes
- 2026-10-03: generated by `analysis/write_period_cards.py`. Exploratory, non-holdout days only.

<!-- R1B START -->
## Round 1b (improved data, 2026-10-04)
H03 never read the buggy `activity_bins`; round 1b re-runs the round-1 specification (M1_B2 primary, M3 fast self/cross, day bootstrap B = 50 / 25, agent-shift null R = 5) on corrected inputs: exogenous drive from `kicks_classified` (human messages + nudges; round 1 also counted the operator's pause/resume bookends) and days split at operator-off gaps ≥ 60 min (`outages_fixed`). Here: exogenous messages in window 19 → 10; split / trimmed days: none.

| Events | n̂ round 1 [95% CI] | **n̂ round 1b** | fast n_x round 1 | **fast n_x round 1b** | n̂ B3 (lower bound) r1 → 1b |
| --- | --- | --- | --- | --- | --- |
| TALK | 0.62 [0.37, 0.71] | **0.56 [0.23, 0.64]** | 0.112 | **0.109** (shift null 0.081) | 0.05 → 0.05 |
| ALL | 0.42 [0.28, 0.54] | **0.41 [0.28, 0.50]** | 0.174 | **0.168** (shift null 0.082) | 0.23 → 0.23 |

Rule: no period-level prediction for mode I; enters P2/P4 as a comparison point. Source: `data/processed/H03-self-excited-criticality/r1b/period_table.parquet` (`analysis/r1b.py`).
<!-- R1B END -->
