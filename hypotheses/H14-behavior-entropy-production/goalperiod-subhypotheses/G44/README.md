# H14 × G44: Finetune your leader! (2026-05-26 → 2026-05-29)

**Verdict:** failed
**Role:** exploratory
**Period:** regime III · mode C for #best (4 agents fine-tune a Kimi leader), #rest picks its own goals · N = 16 (+2: Claude Opus 4.8 and the temporary fine-tuned leader join 05-28) · 4 days × 4 h. Joins on day 3; the joiners enter single-agent tests only if they reach 2 days.

## Why this period
Mixed week: a small shared-objective team inside a free room. H02's second collective-signal period.

## Prediction
*Written 2026-10-03, before running on this period.* The card's predictions (`../../README.md`, "Prediction") as they apply here:
- **P2:** ≥ 80% of agents with ≥ 1,000 transitions above the DB-surrogate 95th percentile.
- **P5:** work → chat → idle → work and work → chat → consolidate → work positive in ≥ 75% of agents; one of them dominant.
- **P4:** ΔΣ_MF and ΔΣ_PW within the cross-day null (4 days; the shared objective covers only 4 agents).

Verdict rule: **supported** if P2, P5 and P4 (null as predicted) hold; **mixed** if P2 holds and one or two of the others fail; **failed** if P2 fails.

## Result
*Run 2026-10-03 (exploratory, non-holdout). Primary single-agent estimator: H05's cross-fitted Newton bound (the pre-registered switch rule did not fire); companion `cfx` = cross-fitted exact dual minus its DB-null mean. DB surrogates: 200 per agent.*

| Prediction | Observed | Null / reference | Verdict |
| --- | --- | --- | --- |
| P2: ≥ 80% of agents (≥ 1,000 transitions) above the DB-surrogate 95th pct | 0.50 of 14 (cfx: 0.36); median Σ_i 0.008 (Newton), excess 0.008; cfx excess 0.006 nats/transition | 5% expected under the null | ✗ |
| P2 (minute grid): ≥ 60% above null; per-hour lower than on turns for ≥ 80% | 0.43 of 14; per-hour lower for 0.50 | | ✗ |
| P5: work → chat → idle → work and work → chat → consolidate → work positive in ≥ 75%; one dominant | 0.38 and 0.62 positive; dominant: work>chat>cons | sign tests p = 0.454, 0.454 | ✗ |
| P4: ΔΣ_MF within the cross-day null | excess 0.0409 (observed 0.1204), p = 0.109; ΔΣ_PW excess 0.0319, p = 0.297 | null mean 0.0795 ± 0.0321 (MF), 0.3173 ± 0.0696 (PW); N = 15, 4 days | ✓ |
| HH67 strong form: ΔΣ > Σ_1 | ΔΣ_MF excess / Σ_1 = –; ΔΣ_PW excess / Σ_1 = – (Σ_1 = Σ_i cfx on the grid = -0.0771) | | strong form holds |
| P3 (family, descriptive here unless G38/G51) | η²_lab = 0.26 (perm p = 0.402, chance 0.27); adjusted for shell share and log n: 0.24 (p = 0.434); Anthropic − OpenAI = 0.0174 (two-sided p = 0.101) | labs: Anthropic 7, DeepSeek 1, Google 3, Moonshot 1, OpenAI 4; cfx companion η² 0.12 (p 0.755) | descriptive |

**Verdict: failed.** Other numbers: act-scheme share above null 1.00; order 2 beats order 1 (held-out likelihood) for 0.62 of agents, order-2 bound > pair bound for 0.50; removing consolidate loses a median 0.57 of the excess (the rest stays above null for 0.50); median plug-in EP share in consolidate transitions 0.47.

Per-agent table (eligible agents; excess = estimate − DB-null mean, nats/transition; Newton primary, cfx companion):

| Agent | Lab | Transitions | Σ_i Newton | p | cfx excess | p | Newton excess/h | Minute excess/h | work>chat>idle A | work>chat>cons A |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Claude Sonnet 4.5 | Anthropic | 1223 | 0.061 | 0.005 | 0.070 | 0.005 | 4.48 | 1.29 | -1.05 | 1.69 |
| Gemini 3.5 Flash | Google | 2116 | 0.045 | 0.005 | 0.084 | 0.005 | 5.79 | 1.50 | 2.75 | 2.94 |
| Kimi K2.6 | Moonshot | 1178 | 0.025 | 0.005 | 0.002 | 0.463 | 1.87 | 4.60 | 0.61 | -0.96 |
| Claude Opus 4.5 | Anthropic | 2359 | 0.016 | 0.005 | 0.008 | 0.100 | 2.26 | 0.94 | -0.03 | -0.50 |
| Claude Haiku 4.5 | Anthropic | 2165 | 0.014 | 0.005 | 0.021 | 0.010 | 1.82 | 1.73 | -1.32 | 0.59 |
| Claude Opus 4.6 | Anthropic | 1575 | 0.013 | 0.010 | 0.011 | 0.035 | 1.21 | 1.53 | 0.00 | -0.06 |
| Gemini 2.5 Pro | Google | 2261 | 0.012 | 0.005 | 0.007 | 0.050 | 1.67 | -0.39 | 0.00 | 1.35 |
| Claude Opus 4.8 | Anthropic | 430 | 0.010 | 0.323 | -0.049 | 0.861 | 0.45 | 0.47 | 0.44 | 1.48 |
| DeepSeek-V3.2 | DeepSeek | 1184 | 0.007 | 0.154 | 0.019 | 0.055 | 0.49 | -0.06 | 1.38 | -0.10 |
| Claude Opus 4.7 | Anthropic | 1201 | 0.006 | 0.189 | 0.015 | 0.119 | 0.46 | 1.14 | 0.73 | 0.88 |
| GPT-5 | OpenAI | 1373 | 0.004 | 0.075 | 0.005 | 0.060 | 0.35 | 0.29 | 0.00 | -0.03 |
| Gemini 3.1 Pro | Google | 2562 | 0.003 | 0.134 | 0.003 | 0.323 | 0.54 | -0.36 | -1.25 | 1.22 |
| GPT-5.1 | OpenAI | 911 | -0.003 | 0.607 | 0.006 | 0.358 | -0.14 | 5.78 | -1.18 | 1.36 |
| GPT-5.5 | OpenAI | 1480 | -0.004 | 0.816 | -0.012 | 0.910 | -0.35 | 0.34 | -0.49 | 2.28 |
| GPT-5.2 | OpenAI | 1049 | -0.004 | 0.721 | 0.006 | 0.393 | -0.27 | 1.69 | 0.01 | 0.32 |
| Claude Sonnet 4.6 | Anthropic | 1838 | -0.005 | 0.980 | -0.044 | 1.000 | -0.57 | 0.39 | 0.00 | -0.07 |

Figures: [`figures/period_summary.pdf`](figures/period_summary.pdf). Data: `data/processed/H14-behavior-entropy-production/G44/` (`agents.parquet`, `results.json`). Code: `analysis/run_period.py --period G44`.

## Scorecard (period-specific axes)
- **C (adequacy):** single-agent arrows beat the DB surrogate for 0.50 of test agents (held-out, day-blocked cross-fit). Collective term vs. cross-day null: p = 0.109 (MF), 0.297 (PW).
- **D (unfitted):** cycle orientations (P5) are not fitted by the EP estimator: not as predicted.
- **G (ground truth):** the consolidate-linked cycle is scaffold-imposed (consolidation cadence); see the card for how much EP it carries.

## Notes
