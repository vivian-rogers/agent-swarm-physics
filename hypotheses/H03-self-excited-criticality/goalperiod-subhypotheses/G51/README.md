# H03 × G51: Each agent: Maximize your assigned goal! (2026-07-06 → 2026-09-20)

**Verdict:** failed
**Role:** exploratory
**Period:** regime III · mode P (private assigned roles; coded I/K) · N = 21 at start (+11), 26.5 active per day on average · rooms (agents see only their room) · 45 non-holdout days, median window 8.1 h. Splits inside the period: 2026-07-09 (NE32: GPT-5.6 Sol/Terra/Luna join in separate isolated r; roster_joined: GPT-5.6 Luna; roster_joined: GPT-5.6 Sol; roster_joined: GPT-5.6 Terra); 2026-07-10 (roster_joined: Grok 4.5); 2026-07-17 (roster_joined: Kimi K3); 2026-07-24 (roster_joined: Claude Opus 5); 2026-07-29 (NE38: A human reassigns Claude Opus 5's role (word puzzl); 2026-08-28 (roster_joined: GLM-5.3 Flash); 2026-09-01 (roster_joined: Claude Fable 5.1); 2026-09-03 (NE33: Batch join: Muse Spark 1.3, Gemini 3.8 Flash, GPT-; roster_joined: Gemini 3.8 Flash; roster_joined: Muse Spark 1.3); 2026-09-04 (NE33: Batch join: Muse Spark 1.3, Gemini 3.8 Flash, GPT-; roster_joined: GPT-6 Astra).

Verdict rule: P5 (n̂ rises with N toward 1): segment Spearman ρ = -0.64 (p = 0.044). Verdicts use the primary statistic, n̂ for TALK under M1 with B2 + exogenous drive. n̂ depends on the baseline. A Poisson process with a rate modulated on 10–30 min scales can mimic it, and the 10-min jitter test has no power to separate the two (main card, jitter calibration). Read B2 n̂ as an upper value and B3 n̂ as a downward-biased lower bound. Any verdict here is descriptive, not mechanistic.

## Why this period
- The private-role era: HH32 predicts a drift toward n → 1 as the roster grows from 21 to 32.
- `goal-periods.md` ranks model 09 (Hawkes) #2 here: long window for nonparametric kernels and the branching ratio
- Context (paraphrased dataset summary; secondary): Standing goal: each agent maximizes a private assigned role (Table IV of the overview). 21 → 32 agents, 8 h/day, the longest stationary-ish window in the data (~12k agent-hours). Some roles are held by two agents (direct competition). Humans occasionally reassign roles.

## Prediction
*Written 2026-10-03 in the main card's Prediction section, before any fit on real data, and restated here for this period. This file was generated after the exploratory run, under the 2026-10-03 folder convention.*

- P5: n̂ rises with active N across the period's windows and segments, reaching ≥ 0.9 in the last non-holdout weeks. Counts against it: no rise, or n̂ staying well below 0.9.
- P6: the fast cross-agent part n_cross is higher in C than in F periods. P7: n̂_ALL > n̂_TALK, from the agent's own-loop excitation.
- G1 (guard): on n = 0 synthetic data with this period's fitted baseline, the pipeline returns n̂ ≈ 0, and the naive baseline B0 returns clearly more.

## Result
| Quantity | TALK | ALL | Null / reference | Reading |
|---|---|---|---|---|
| n̂ (M1, B2 + exo), 95% CI | **0.54** [0.44, 0.61] | 0.59 [0.43, 0.62] | Poisson n = 0 | CI: day-bootstrap |
| kernel timescale τ̂ (s) | 108 | 265 | – | τ̂ ≥ 1800 s means the kernel mimics the baseline |
| n̂, kernel τ ≤ 30 min | 0.59 | 0.59 | – | robustness variant |
| baseline ladder B0 / B1 / B2 / B3-2h / B3-30m | 0.81 / 0.68 / 0.54 / 0.36 / 0.22 | 0.94 / 0.77 / 0.59 / 0.34 / 0.08 | guard: n = 0 → B0 0.75, B2 0.000 (TALK) | falls with baseline flexibility |
| sum-of-exp kernel (M2): n, n(τ ≤ 300 s) | 0.76, 0.39 | 0.61, 0.49 | – | ΔAIC grid − exp (TALK) 28.6 |
| power-law-constrained kernel θ | -0.28 | -0.34 | – | ll(pl) − ll(exp) (TALK) -226.3 |
| own-loop n_self (τ ≤ 300 s, M3) | 0.06 | 0.00 | – | scheduler / own-loop part |
| social n_cross (τ ≤ 300 s, M3) | 0.026 | 0.081 | agent-shift null 0.008 / 0.065 | real − null (TALK) = 0.018 |
| pooled fast n̂ (τ ≤ 5 min) | 0.59 | 0.59 | 10-min jitter 0.64 / 0.59 | real − jittered (TALK) = -0.05; uninformative (synthetic n = 0.6 also drops only ≈ 0.03) |
| share of events: baseline / exogenous / triggered | 0.45 / 0.008 / 0.54 | – | – | 854 human/nudger messages in window |
| time-rescaling KS D (p), Hawkes vs Poisson | 0.024 (0.000) vs 0.064 | 0.013 vs 0.017 | Exp(1) | smaller D is better |
| ΔAIC Hawkes − Poisson (B2) | -4392.1 | -4110.9 | – | negative favors Hawkes |
| day-blocked CV Δℓ/event, Hawkes − Poisson (B2 / B3-30m) | 0.102 / 0.0108 | 0.063 / 0.0004 | 0 | – means < 3 days |
| guard recovery (TALK): n = 0.6 → B2, n = 0.9 → B2 | 0.59, 0.90 | 0.58, 0.89 | 0.6, 0.9 | 3 synthetic replicates |
| guard misspecification: n = 0 with real 10-min rate → B2 | 0.66 | 0.62 | 0 | not a valid null: the real 10-min counts already contain any cascades |
| P(burst ≥ 10), gap 60 s (TALK): data / Hawkes sim / Poisson sim | 0.194 / 0.204 / 0.200 | – | – | unfitted statistic (axis D) |

**Segments (goal period split at step changes; M1 B2):**

| seg | start → end | days | N | n̂ TALK (SE) | partially pooled | n̂ ALL (SE) | n_cross ≤300 s TALK |
|---|---|---|---|---|---|---|---|
| 0 | 2026-07-06 → 2026-07-08 | 3 | 21 | 0.52 (0.11, boot) | 0.44 | 0.48 (0.15) | 0.045 |
| 1 | 2026-07-09 → 2026-07-09 | 1 | 24 | 0.52 (0.06, profile) | 0.49 | 0.64 (0.06) | 0.079 |
| 2 | 2026-07-10 → 2026-07-16 | 5 | 25 | 0.27 (0.05, boot) | 0.28 | 0.15 (0.06) | 0.013 |
| 3 | 2026-07-17 → 2026-07-23 | 5 | 26 | 0.55 (0.06, boot) | 0.51 | 0.57 (0.15) | 0.035 |
| 4 | 2026-07-24 → 2026-07-28 | 3 | 27 | 0.40 (0.04, boot) | 0.39 | 0.44 (0.09) | 0.059 |
| 5 | 2026-07-29 → 2026-08-27 | 22 | 27 | 0.40 (0.03, boot) | 0.40 | 0.42 (0.03) | 0.011 |
| 6 | 2026-08-28 → 2026-08-31 | 2 | 28 | 0.11 (0.05, profile) | 0.14 | 0.05 (0.03) | 0.000 |
| 7 | 2026-09-01 → 2026-09-02 | 2 | 29 | 0.18 (0.05, profile) | 0.20 | 0.33 (0.06) | 0.000 |
| 8 | 2026-09-03 → 2026-09-03 | 1 | 31 | 0.23 (0.06, profile) | 0.25 | 0.10 (0.07) | 0.000 |
| 9 | 2026-09-04 → 2026-09-04 | 1 | 32 | 0.31 (0.06, profile) | 0.31 | 0.17 (0.08) | 0.011 |

Within-period heterogeneity across segments (TALK): Cochran Q = 63.3, df = 9, p = 3.1e-10, I² = 0.86, τ = 0.127. Partial pooling uses DerSimonian–Laird random effects within the period (exception d).

**#51 drift.** Across the 10 segments between roster changes, n̂ falls with N: Spearman ρ = -0.64 (p = 0.044). The weighted slope is -0.033 per agent for TALK and -0.054 for ALL. The secondary rolling 5-day windows, which straddle joins, show the same pattern: block ρ = -0.46 (TALK). The naive constant-baseline fit (B0) reaches n̂ ≈ 0.99 in some windows, so it would have "confirmed" HH32 spuriously. Rolling outputs: `rolling51.parquet`; figure `../figures/rolling51.pdf`.

Figures: [`figures/diagnostics.pdf`](figures/diagnostics.pdf). Data: `data/processed/H03-self-excited-criticality/G51/` (per-period extracts of the fit, CV, bootstrap, guard, jitter, cascade and segment tables, plus `fits/<SET>_<MODEL>.npy`).

## Scorecard (period-specific axes)
| Axis | Score | Evidence |
|---|---|---|
| B assumptions | 1 | time-rescaling KS D: Hawkes 0.024 vs Poisson 0.064 (p_Hawkes = 0.000); 1 = better than Poisson but not necessarily Exp(1) |
| C adequacy | 1 | held-out Δℓ/event vs Poisson with the same B2 baseline = 0.102; vs the B3 30-min baseline = 0.0108. Capped at 1: no powered test against a Poisson null modulated at 10–30 min |
| D unfitted | 0 | burst-size tail (gap 60 s) closer to the Hawkes simulation than to Poisson: no |
| F identifiability | 1 | n = 0 → B2 0.000; n = 0.6 → 0.59; but n = 0 with the real 10-min rate → 0.66 |

## Notes
- 2026-10-03: generated by `analysis/write_period_cards.py`. Exploratory, non-holdout days only.
- Long-window day(s) 2026-07-07, 2026-07-28: the window is 1.5–8× the period's median, likely two sessions with a long silent gap. This distorts the shared within-day shape (B2) and inflates held-out comparisons. Splitting days at long gaps is a planned scheme fix.
- Days from 2026-09-07 on are the locked holdout (#51 tail, `holdout.json`). They are absent from the processed data and were not analyzed. The whole-period bootstrap was capped at 33 M1 / 16 M3 replicates (cost); the drift test uses segment and block bootstraps.
- Regime III (perma-computer-use): `events_core` holds chat and session events, but not computer-use turns, so ALL means something different here than in regime I.
