# H14 × G38: Choose a charity and raise as much money as you can for it (2026-04-02 → 2026-04-24)

**Verdict:** failed
**Role:** exploratory
**Period:** regime III · mode C (shared objective) · N = 12 (+2: Claude Opus 4.7 joins 04-17, Kimi K2.6 04-22) · #best/#rest rooms · 17 days × 4 h. Step change inside: outreach approval (G) on 2026-04-14; analysed as one period, with 04-02 → 04-13 vs. 04-14 → 04-24 as a descriptive split.

## Why this period
The longest regime-III non-holdout period apart from #51: the most power of the 4-h periods for per-agent and per-family tests, and a shared-objective (driven) week for the payoff question.

## Prediction
*Written 2026-10-03, before running on this period.* The card's predictions (`../../README.md`, "Prediction") as they apply here:
- **P2:** ≥ 80% of agents with ≥ 1,000 transitions above the DB-surrogate 95th percentile.
- **P5:** work → chat → idle → work and work → chat → consolidate → work positive in ≥ 75% of agents; one of them dominant.
- **P3 (period part):** η²_lab ≥ 0.30 with permutation p < 0.05 (one of the two periods expected to reach it, with #51).
- **P4:** ΔΣ_MF above the cross-day null 95th percentile (17 days). ΔΣ_PW at noise.
- Split at 04-14: no prediction (descriptive).

Verdict rule: **supported** if P2, P5 and P4 (ΔΣ_MF) hold; **mixed** if P2 holds and one or two of the others fail; **failed** if P2 fails.

## Result
*Run 2026-10-03 (exploratory, non-holdout). Primary single-agent estimator: H05's cross-fitted Newton bound (the pre-registered switch rule did not fire); companion `cfx` = cross-fitted exact dual minus its DB-null mean. DB surrogates: 200 per agent.*

| Prediction | Observed | Null / reference | Verdict |
| --- | --- | --- | --- |
| P2: ≥ 80% of agents (≥ 1,000 transitions) above the DB-surrogate 95th pct | 0.71 of 14 (cfx: 0.50); median Σ_i 0.003 (Newton), excess 0.003; cfx excess 0.006 nats/transition | 5% expected under the null | ✗ |
| P2 (minute grid): ≥ 60% above null; per-hour lower than on turns for ≥ 80% | 0.64 of 14; per-hour lower for 0.50 | | ✗ |
| P5: work → chat → idle → work and work → chat → consolidate → work positive in ≥ 75%; one dominant | 0.71 and 0.86 positive; dominant: work>chat>cons | sign tests p = 0.180, 0.013 | ✗ |
| P4: ΔΣ_MF above the cross-day null | excess 0.0074 (observed 0.0140), p = 0.168; ΔΣ_PW excess 0.0019, p = 0.356 | null mean 0.0066 ± 0.0063 (MF), 0.0101 ± 0.0115 (PW); N = 12, 15 days | ✗ |
| HH67 strong form: ΔΣ > Σ_1 | ΔΣ_MF excess / Σ_1 = 0.015; ΔΣ_PW excess / Σ_1 = 0.004 (Σ_1 = Σ_i cfx on the grid = 0.4803) | | strong form fails |
| P3 (family, descriptive here unless G38/G51) | η²_lab = 0.18 (perm p = 0.644, chance 0.31); adjusted for shell share and log n: 0.27 (p = 0.496); Anthropic − OpenAI = 0.0170 (two-sided p = 0.460) | labs: Anthropic 6, DeepSeek 1, Google 2, Moonshot 1, OpenAI 4; cfx companion η² 0.16 (p 0.742) | ✗ |

**Verdict: failed.** Other numbers: act-scheme share above null 0.86; order 2 beats order 1 (held-out likelihood) for 0.86 of agents, order-2 bound > pair bound for 0.50; removing consolidate loses a median 0.60 of the excess (the rest stays above null for 0.50); median plug-in EP share in consolidate transitions 0.38.
Split at 2026-04-14 (descriptive): median change in excess b − a = 0.0010 (Wilcoxon p = 0.339, n = 12).

Per-agent table (eligible agents; excess = estimate − DB-null mean, nats/transition; Newton primary, cfx companion):

| Agent | Lab | Transitions | Σ_i Newton | p | cfx excess | p | Newton excess/h | Minute excess/h | work>chat>idle A | work>chat>cons A |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Claude Opus 4.5 | Anthropic | 11408 | 0.087 | 0.005 | 0.065 | 0.005 | 13.82 | -0.07 | 0.02 | 0.98 |
| Claude Haiku 4.5 | Anthropic | 10585 | 0.058 | 0.005 | 0.042 | 0.005 | 8.48 | 6.71 | 1.73 | 1.38 |
| GPT-5.4 | OpenAI | 8078 | 0.025 | 0.005 | 0.029 | 0.005 | 2.82 | 0.29 | 0.53 | 1.44 |
| Kimi K2.6 | Moonshot | 1334 | 0.014 | 0.005 | 0.019 | 0.010 | 1.56 | -0.31 | 1.20 | 1.23 |
| GPT-5.2 | OpenAI | 6432 | 0.010 | 0.005 | 0.016 | 0.005 | 0.86 | 1.51 | -0.12 | 0.45 |
| Claude Opus 4.7 | Anthropic | 2090 | 0.008 | 0.025 | 0.009 | 0.065 | 0.66 | 0.34 | 2.13 | 2.18 |
| Claude Opus 4.6 | Anthropic | 7021 | 0.003 | 0.015 | 0.008 | 0.005 | 0.32 | 4.76 | -2.20 | 1.33 |
| Gemini 2.5 Pro | Google | 11088 | 0.003 | 0.005 | 0.003 | 0.005 | 0.51 | 0.30 | -0.20 | -1.31 |
| Claude Sonnet 4.5 | Anthropic | 10982 | 0.002 | 0.010 | 0.002 | 0.065 | 0.37 | 0.36 | -0.03 | -1.02 |
| GPT-5 | OpenAI | 7425 | 0.002 | 0.040 | -0.001 | 0.786 | 0.22 | 0.24 | 2.31 | 1.85 |
| GPT-5.1 | OpenAI | 5648 | 0.002 | 0.149 | 1.4e-04 | 0.532 | 0.13 | 1.77 | 0.56 | 1.32 |
| Claude Sonnet 4.6 | Anthropic | 5868 | 0.001 | 0.114 | -0.006 | 0.985 | 0.12 | 9.27 | 0.03 | 1.11 |
| Gemini 3.1 Pro | Google | 13433 | -1.5e-04 | 0.597 | -2.1e-04 | 0.582 | -0.03 | 0.02 | 0.97 | 0.33 |
| DeepSeek-V3.2 | DeepSeek | 9974 | -4.5e-04 | 0.726 | -0.002 | 0.900 | -0.05 | 0.62 | 0.49 | 0.07 |

Figures: [`figures/period_summary.pdf`](figures/period_summary.pdf). Data: `data/processed/H14-behavior-entropy-production/G38/` (`agents.parquet`, `results.json`). Code: `analysis/run_period.py --period G38`.

## Scorecard (period-specific axes)
- **C (adequacy):** single-agent arrows beat the DB surrogate for 0.71 of test agents (held-out, day-blocked cross-fit). Collective term vs. cross-day null: p = 0.168 (MF), 0.356 (PW).
- **D (unfitted):** cycle orientations (P5) are not fitted by the EP estimator: not as predicted.
- **G (ground truth):** the consolidate-linked cycle is scaffold-imposed (consolidation cadence); see the card for how much EP it carries.

## Notes
