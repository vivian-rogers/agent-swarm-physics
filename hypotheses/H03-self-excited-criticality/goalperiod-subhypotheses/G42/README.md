# H03 × G42: Run your own Youtube channel! (2026-05-18 → 2026-05-25)

**Verdict:** descriptive
**Verdict (1b):** descriptive (round 1b, 2026-10-04: n̂ TALK 0.20 → 0.20 on corrected inputs; unchanged verdict)
**Role:** exploratory
**Period:** regime III · mode I (each agent its own objective) · N = 15 at start (+1), 15.6 active per day on average · rooms (agents see only their room) · 5 non-holdout days, median window 4.0 h. Splits inside the period: 2026-05-20 (roster_joined: Gemini 3.5 Flash).

Verdict rule: no period-level prediction for mode I; enters P2/P4 as a comparison point. Verdicts use the primary statistic, n̂ for TALK under M1 with B2 + exogenous drive. n̂ depends on the baseline. A Poisson process with a rate modulated on 10–30 min scales can mimic it, and the 10-min jitter test has no power to separate the two (main card, jitter calibration). Read B2 n̂ as an upper value and B3 n̂ as a downward-biased lower bound. Any verdict here is descriptive, not mechanistic.

## Why this period
- Individual-objective week: a comparison point for the mode effect (P2, P4).
- `goal-periods.md` ranks model 09 (Hawkes) #3 here: production bursts
- Context (paraphrased dataset summary; secondary): Each agent runs a YouTube channel (1–10 videos); several agents read "1–10" as "10".

## Prediction
*Written 2026-10-03 in the main card's Prediction section, before any fit on real data, and restated here for this period. This file was generated after the exploratory run, under the 2026-10-03 folder convention.*

- No period-level threshold. The period enters P2/P4 as a comparison point; S2 implies it sits below the shared-objective periods.
- P6: the fast cross-agent part n_cross is higher in C than in F periods. P7: n̂_ALL > n̂_TALK, from the agent's own-loop excitation.
- G1 (guard): on n = 0 synthetic data with this period's fitted baseline, the pipeline returns n̂ ≈ 0, and the naive baseline B0 returns clearly more.

## Result
| Quantity | TALK | ALL | Null / reference | Reading |
|---|---|---|---|---|
| n̂ (M1, B2 + exo), 95% CI | **0.20** [0.05, 0.27] | 0.02 [0.00, 0.07] | Poisson n = 0 | CI: day-bootstrap |
| kernel timescale τ̂ (s) | 55 | 53 | – | τ̂ ≥ 1800 s means the kernel mimics the baseline |
| n̂, kernel τ ≤ 30 min | 0.20 | 0.02 | – | robustness variant |
| baseline ladder B0 / B1 / B2 / B3-2h / B3-30m | 0.32 / 0.23 / 0.20 / 0.21 / 0.14 | 0.19 / 0.21 / 0.02 / 0.20 / 0.00 | guard: n = 0 → B0 0.28, B2 0.000 (TALK) | falls with baseline flexibility |
| sum-of-exp kernel (M2): n, n(τ ≤ 300 s) | 0.21, 0.21 | 0.00, 0.00 | – | ΔAIC grid − exp (TALK) 12.4 |
| power-law-constrained kernel θ | 0.10 | -3.00 | – | ll(pl) − ll(exp) (TALK) -10.2 |
| own-loop n_self (τ ≤ 300 s, M3) | 0.03 | 0.00 | – | scheduler / own-loop part |
| social n_cross (τ ≤ 300 s, M3) | 0.053 | 0.024 | agent-shift null 0.000 / 0.026 | real − null (TALK) = 0.053 |
| pooled fast n̂ (τ ≤ 5 min) | 0.20 | 0.02 | 10-min jitter 0.06 / 0.01 | real − jittered (TALK) = 0.14; uninformative (synthetic n = 0.6 also drops only ≈ 0.03) |
| share of events: baseline / exogenous / triggered | 0.76 / 0.025 / 0.20 | – | – | 34 human/nudger messages in window |
| time-rescaling KS D (p), Hawkes vs Poisson | 0.035 (0.092) vs 0.060 | 0.019 vs 0.017 | Exp(1) | smaller D is better |
| ΔAIC Hawkes − Poisson (B2) | -27.2 | 3.8 | – | negative favors Hawkes |
| day-blocked CV Δℓ/event, Hawkes − Poisson (B2 / B3-30m) | 0.018 / 0.0060 | -0.000 / 0.0000 | 0 | – means < 3 days |
| guard recovery (TALK): n = 0.6 → B2, n = 0.9 → B2 | 0.58, 0.87 | 0.54, 0.89 | 0.6, 0.9 | 3 synthetic replicates |
| guard misspecification: n = 0 with real 10-min rate → B2 | 0.32 | 0.15 | 0 | not a valid null: the real 10-min counts already contain any cascades |
| P(burst ≥ 10), gap 60 s (TALK): data / Hawkes sim / Poisson sim | 0.058 / 0.043 / 0.025 | – | – | unfitted statistic (axis D) |

**Segments (goal period split at step changes; M1 B2):**

| seg | start → end | days | N | n̂ TALK (SE) | partially pooled | n̂ ALL (SE) | n_cross ≤300 s TALK |
|---|---|---|---|---|---|---|---|
| 0 | 2026-05-18 → 2026-05-19 | 2 | 15 | 0.22 (0.06, profile) | 0.19 | 0.02 (–) | 0.084 |
| 1 | 2026-05-20 → 2026-05-22 | 3 | 16 | 0.16 (0.06, boot) | 0.19 | 0.00 (0.20) | 0.026 |

Within-period heterogeneity across segments (TALK): Cochran Q = 0.6, df = 1, p = 0.448, I² = 0.00, τ = 0.000. Partial pooling uses DerSimonian–Laird random effects within the period (exception d).

Figures: [`figures/diagnostics.pdf`](figures/diagnostics.pdf). Data: `data/processed/H03-self-excited-criticality/G42/` (per-period extracts of the fit, CV, bootstrap, guard, jitter, cascade and segment tables, plus `fits/<SET>_<MODEL>.npy`).

## Scorecard (period-specific axes)
| Axis | Score | Evidence |
|---|---|---|
| B assumptions | 1 | time-rescaling KS D: Hawkes 0.035 vs Poisson 0.060 (p_Hawkes = 0.092); 1 = better than Poisson but not necessarily Exp(1) |
| C adequacy | 1 | held-out Δℓ/event vs Poisson with the same B2 baseline = 0.018; vs the B3 30-min baseline = 0.0060. Capped at 1: no powered test against a Poisson null modulated at 10–30 min |
| D unfitted | 1 | burst-size tail (gap 60 s) closer to the Hawkes simulation than to Poisson: yes |
| F identifiability | 1 | n = 0 → B2 0.000; n = 0.6 → 0.58; but n = 0 with the real 10-min rate → 0.32 |

## Notes
- 2026-10-03: generated by `analysis/write_period_cards.py`. Exploratory, non-holdout days only.
- Regime III (perma-computer-use): `events_core` holds chat and session events, but not computer-use turns, so ALL means something different here than in regime I.

<!-- R1B START -->
## Round 1b (improved data, 2026-10-04)
H03 never read the buggy `activity_bins`; round 1b re-runs the round-1 specification (M1_B2 primary, M3 fast self/cross, day bootstrap B = 50 / 25, agent-shift null R = 5) on corrected inputs: exogenous drive from `kicks_classified` (human messages + nudges; round 1 also counted the operator's pause/resume bookends) and days split at operator-off gaps ≥ 60 min (`outages_fixed`). Here: exogenous messages in window 34 → 29; split / trimmed days: none.

| Events | n̂ round 1 [95% CI] | **n̂ round 1b** | fast n_x round 1 | **fast n_x round 1b** | n̂ B3 (lower bound) r1 → 1b |
| --- | --- | --- | --- | --- | --- |
| TALK | 0.20 [0.05, 0.27] | **0.20 [0.05, 0.25]** | 0.053 | **0.055** (shift null 0.000) | 0.14 → 0.14 |
| ALL | 0.02 [0.00, 0.07] | **0.02 [0.00, 0.07]** | 0.024 | **0.023** (shift null 0.009) | 0.00 → 0.00 |

Rule: no period-level prediction for mode I; enters P2/P4 as a comparison point. Source: `data/processed/H03-self-excited-criticality/r1b/period_table.parquet` (`analysis/r1b.py`).
<!-- R1B END -->
