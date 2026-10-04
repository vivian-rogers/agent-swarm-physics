# H14 × G41: Perform novel research! (2026-05-11 → 2026-05-15)

**Verdict:** failed
**Role:** exploratory
**Period:** regime III · mode I · N = 15 · rooms split back to #best/#rest on 05-11 · 5 days × 4 h. No step change inside.

## Why this period
Individual-objective week right after the merged #40: a second mode-I arm for P7 and a null for the collective term.

## Prediction
*Written 2026-10-03, before running on this period.* The card's predictions (`../../README.md`, "Prediction") as they apply here:
- **P2:** ≥ 80% of agents with ≥ 1,000 transitions above the DB-surrogate 95th percentile.
- **P5:** work → chat → idle → work and work → chat → consolidate → work positive in ≥ 75% of agents; one of them dominant.
- **P4:** ΔΣ_MF and ΔΣ_PW within the cross-day null.
- **P7:** median Σ_i below #40's.

Verdict rule: **supported** if P2, P5 and P4 (null as predicted) hold; **mixed** if P2 holds and one or two of the others fail; **failed** if P2 fails.

## Result
*Run 2026-10-03 (exploratory, non-holdout). Primary single-agent estimator: H05's cross-fitted Newton bound (the pre-registered switch rule did not fire); companion `cfx` = cross-fitted exact dual minus its DB-null mean. DB surrogates: 200 per agent.*

| Prediction | Observed | Null / reference | Verdict |
| --- | --- | --- | --- |
| P2: ≥ 80% of agents (≥ 1,000 transitions) above the DB-surrogate 95th pct | 0.73 of 15 (cfx: 0.60); median Σ_i 0.010 (Newton), excess 0.010; cfx excess 0.009 nats/transition | 5% expected under the null | ✗ |
| P2 (minute grid): ≥ 60% above null; per-hour lower than on turns for ≥ 80% | 0.67 of 15; per-hour lower for 0.53 | | ✗ |
| P5: work → chat → idle → work and work → chat → consolidate → work positive in ≥ 75%; one dominant | 0.60 and 0.87 positive; dominant: work>chat>cons | sign tests p = 0.607, 0.007 | ✗ |
| P4: ΔΣ_MF within the cross-day null | excess -0.0060 (observed 0.0468), p = 0.505; ΔΣ_PW excess 0.1008, p = 0.030 | null mean 0.0528 ± 0.0317 (MF), 0.2294 ± 0.0522 (PW); N = 15, 5 days | ✓ |
| HH67 strong form: ΔΣ > Σ_1 | ΔΣ_MF excess / Σ_1 = -0.019; ΔΣ_PW excess / Σ_1 = 0.328 (Σ_1 = Σ_i cfx on the grid = 0.3076) | | strong form fails |
| P3 (family, descriptive here unless G38/G51) | η²_lab = 0.11 (perm p = 0.864, chance 0.28); adjusted for shell share and log n: 0.15 (p = 0.785); Anthropic − OpenAI = -0.0008 (two-sided p = 0.930) | labs: Anthropic 6, DeepSeek 1, Google 2, Moonshot 1, OpenAI 5; cfx companion η² 0.45 (p 0.192) | descriptive |

**Verdict: failed.** Other numbers: act-scheme share above null 0.93; order 2 beats order 1 (held-out likelihood) for 0.80 of agents, order-2 bound > pair bound for 0.53; removing consolidate loses a median 1.00 of the excess (the rest stays above null for 0.31); median plug-in EP share in consolidate transitions 0.62.

Per-agent table (eligible agents; excess = estimate − DB-null mean, nats/transition; Newton primary, cfx companion):

| Agent | Lab | Transitions | Σ_i Newton | p | cfx excess | p | Newton excess/h | Minute excess/h | work>chat>idle A | work>chat>cons A |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Claude Sonnet 4.5 | Anthropic | 2715 | 0.039 | 0.005 | 0.035 | 0.005 | 5.16 | -0.21 | -0.01 | -0.51 |
| Claude Opus 4.5 | Anthropic | 2774 | 0.034 | 0.005 | 0.012 | 0.005 | 4.71 | 1.17 | -0.63 | 0.62 |
| GPT-5.4 | OpenAI | 1842 | 0.031 | 0.005 | 0.019 | 0.005 | 2.83 | 1.04 | 1.98 | 1.99 |
| GPT-5 | OpenAI | 1907 | 0.021 | 0.005 | 0.025 | 0.005 | 1.98 | 0.80 | -0.51 | -1.57 |
| Claude Opus 4.7 | Anthropic | 2493 | 0.014 | 0.005 | 0.017 | 0.015 | 1.73 | 0.98 | 1.97 | 2.51 |
| GPT-5.2 | OpenAI | 2126 | 0.012 | 0.050 | 0.018 | 0.005 | 1.21 | 0.95 | 1.81 | 1.06 |
| DeepSeek-V3.2 | DeepSeek | 1897 | 0.010 | 0.010 | 0.008 | 0.020 | 0.96 | 0.12 | 1.65 | 1.09 |
| GPT-5.1 | OpenAI | 1603 | 0.010 | 0.045 | 0.009 | 0.114 | 0.81 | 1.04 | -0.16 | 1.30 |
| Kimi K2.6 | Moonshot | 2044 | 0.009 | 0.030 | -0.017 | 0.990 | 0.89 | 0.32 | 1.26 | 2.64 |
| Claude Haiku 4.5 | Anthropic | 2998 | 0.008 | 0.035 | 0.006 | 0.100 | 1.12 | 1.64 | -0.30 | 0.14 |
| Gemini 2.5 Pro | Google | 2479 | 0.005 | 0.119 | 0.008 | 0.050 | 0.57 | 2.02 | 1.29 | 1.21 |
| GPT-5.5 | OpenAI | 2211 | 0.004 | 0.040 | 0.009 | 0.020 | 0.44 | 0.71 | -0.11 | 2.71 |
| Gemini 3.1 Pro | Google | 3257 | 0.002 | 0.234 | -0.004 | 0.806 | 0.32 | 0.80 | 0.90 | 0.88 |
| Claude Sonnet 4.6 | Anthropic | 1514 | -0.001 | 0.761 | -8.8e-04 | 0.662 | -0.11 | 8.87 | 1.64 | 0.37 |
| Claude Opus 4.6 | Anthropic | 2525 | -0.004 | 0.851 | -0.005 | 0.796 | -0.57 | 0.65 | 1.07 | 0.27 |

Figures: [`figures/period_summary.pdf`](figures/period_summary.pdf). Data: `data/processed/H14-behavior-entropy-production/G41/` (`agents.parquet`, `results.json`). Code: `analysis/run_period.py --period G41`.

## Scorecard (period-specific axes)
- **C (adequacy):** single-agent arrows beat the DB surrogate for 0.73 of test agents (held-out, day-blocked cross-fit). Collective term vs. cross-day null: p = 0.505 (MF), 0.030 (PW).
- **D (unfitted):** cycle orientations (P5) are not fitted by the EP estimator: not as predicted.
- **G (ground truth):** the consolidate-linked cycle is scaffold-imposed (consolidation cadence); see the card for how much EP it carries.

## Notes
