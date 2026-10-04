# H14 × G51: Each agent: maximize your assigned goal! (2026-07-06 → 2026-09-04, non-holdout part)

**Verdict:** mixed
**Verdict (1b):** mixed (unchanged: the pre-registered coarse chain did not change). Corrected fine classes (shell sub-classes): 100% of test agents irreversible, 100% after scaffold removal with burn-in; pooled Jev v3 arrow significant (flip p 0.005)
**Role:** replication (exploratory)
**Period:** regime III · private assigned roles, mode I/K · N = 21 → 32 · mostly #general (GPT-5.6 triplet isolated 07-09/10; #focus 08-05 → 08-24) · 8 h/day · 45 non-holdout days (tail 09-07 → 09-21 held out). Roster steps: NE32 (07-09), 07-10, 07-17, 07-24, 08-28, 09-01, NE33 (09-03/04). Single-agent tests use each agent's own non-holdout days; the collective analysis uses the constant-roster block **07-24 → 08-28** (25 days, H09 E7's window), with weekly sub-blocks as a stability check.

## Why this period
The largest, most stationary window, with the most families together (Anthropic, OpenAI, Google, DeepSeek, Moonshot, xAI, Zhipu, Meta): the main test of HH19 and HH67. `goal-periods.md` ranks 02 Nonequilibrium Ising first for #51.

## Prediction
*Written 2026-10-03, before running on this period.* The card's predictions (`../../README.md`, "Prediction") as they apply here:
- **P2:** ≥ 80% of agents with ≥ 1,000 transitions above the DB-surrogate 95th percentile.
- **P5:** work → chat → idle → work and work → chat → consolidate → work positive in ≥ 75% of agents; one of them dominant.
- **P3 (period part):** η²_lab ≥ 0.30 with permutation p < 0.05; the HH19 direction (Anthropic > OpenAI) expected to fail (my prior from H09 E7 is OpenAI > Anthropic per minute).
- **P4 (block 07-24 → 08-28):** ΔΣ_MF above the cross-day null 95th percentile; ΔΣ_PW possibly above it; ΔΣ/Σ_1 ≤ 0.3 (strong form fails).

Verdict rule: **supported** if P2, P5, P3(period part) and P4 (ΔΣ_MF) hold; **mixed** if P2 holds and some of the others fail; **failed** if P2 fails.

## Result
*Run 2026-10-03 (exploratory, non-holdout). Primary single-agent estimator: H05's cross-fitted Newton bound (the pre-registered switch rule did not fire); companion `cfx` = cross-fitted exact dual minus its DB-null mean. DB surrogates: 200 per agent.*

| Prediction | Observed | Null / reference | Verdict |
| --- | --- | --- | --- |
| P2: ≥ 80% of agents (≥ 1,000 transitions) above the DB-surrogate 95th pct | 0.97 of 30 (cfx: 0.93); median Σ_i 0.009 (Newton), excess 0.009; cfx excess 0.010 nats/transition | 5% expected under the null | ✓ |
| P2 (minute grid): ≥ 60% above null; per-hour lower than on turns for ≥ 80% | 0.87 of 30; per-hour lower for 0.84 | | ✓ |
| P5: work → chat → idle → work and work → chat → consolidate → work positive in ≥ 75%; one dominant | 0.48 and 0.81 positive; dominant: work>idle>cons | sign tests p = 1.000, 8.8e-04 | ✗ |
| P4: ΔΣ_MF above the cross-day null | excess 0.0011 (observed 0.0051), p = 0.317; ΔΣ_PW excess 0.0227, p = 0.024 | null mean 0.0040 ± 0.0024 (MF), 0.0085 ± 0.0057 (PW); N = 27, 24 days | ✗ |
| HH67 strong form: ΔΣ > Σ_1 | ΔΣ_MF excess / Σ_1 = 0.003; ΔΣ_PW excess / Σ_1 = 0.064 (Σ_1 = Σ_i cfx on the grid = 0.3573) | | strong form fails |
| P3 (family, descriptive here unless G38/G51) | η²_lab = 0.21 (perm p = 0.513, chance 0.23); adjusted for shell share and log n: 0.11 (p = 0.847); Anthropic − OpenAI = 0.0019 (two-sided p = 0.752) | labs: Anthropic 11, DeepSeek 2, Google 4, Meta 1, Moonshot 2, OpenAI 8, Zhipu 2, xAI 1; cfx companion η² 0.17 (p 0.601) | ✗ |

**Verdict: mixed.** Other numbers: act-scheme share above null 1.00; order 2 beats order 1 (held-out likelihood) for 0.90 of agents, order-2 bound > pair bound for 0.87; removing consolidate loses a median 0.64 of the excess (the rest stays above null for 0.77); median plug-in EP share in consolidate transitions 0.50.
Weekly sub-blocks (collective, 20 surrogates each): 2026-W31: ΔΣ_MF exc 0.0003 (p 0.48), ΔΣ_PW exc -0.0276 (p 0.62); 2026-W32: ΔΣ_MF exc -0.0083 (p 0.71), ΔΣ_PW exc 0.0306 (p 0.33); 2026-W33: ΔΣ_MF exc -0.0179 (p 0.86), ΔΣ_PW exc -0.0541 (p 0.90); 2026-W34: ΔΣ_MF exc -0.0216 (p 1.00), ΔΣ_PW exc -0.0581 (p 0.81); 2026-W35: ΔΣ_MF exc 0.0056 (p 0.52), ΔΣ_PW exc 0.1141 (p 0.10).

Per-agent table (eligible agents; excess = estimate − DB-null mean, nats/transition; Newton primary, cfx companion):

| Agent | Lab | Transitions | Σ_i Newton | p | cfx excess | p | Newton excess/h | Minute excess/h | work>chat>idle A | work>chat>cons A |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Claude Opus 4.8 | Anthropic | 34054 | 0.046 | 0.005 | 0.062 | 0.005 | 4.13 | 3.33 | 2.16 | 3.77 |
| GLM-5.3 Flash | Zhipu | 2379 | 0.035 | 0.005 | 0.016 | 0.010 | 1.71 | 0.79 | -0.58 | 0.37 |
| Claude Opus 4.7 | Anthropic | 6889 | 0.034 | 0.005 | 0.023 | 0.005 | 0.62 | 0.29 | 1.06 | 3.50 |
| GPT-5.4 | OpenAI | 45272 | 0.033 | 0.005 | 0.035 | 0.005 | 3.92 | 0.98 | -0.12 | 0.87 |
| Muse Spark 1.3 | Meta | 752 | 0.030 | 0.010 | 0.035 | 0.080 | 1.41 | -5.5e-04 | -1.70 | 0.25 |
| GPT-5 | OpenAI | 30343 | 0.029 | 0.005 | 0.029 | 0.005 | 2.34 | 1.82 | 1.34 | 1.32 |
| Claude Fable 5.1 | Anthropic | 1916 | 0.024 | 0.005 | 0.022 | 0.005 | 1.48 | -0.14 | -0.95 | 0.82 |
| Kimi K2.6 | Moonshot | 32957 | 0.015 | 0.005 | 0.016 | 0.005 | 1.34 | 0.65 | -0.46 | -0.16 |
| GPT-5.6 Sol | OpenAI | 24532 | 0.015 | 0.005 | 0.016 | 0.005 | 1.08 | 1.01 | -1.03 | 0.53 |
| Claude Sonnet 4.5 | Anthropic | 27092 | 0.013 | 0.005 | 0.014 | 0.005 | 0.90 | 0.37 | -0.11 | -0.97 |
| Kimi K3 | Moonshot | 6605 | 0.011 | 0.005 | 0.018 | 0.005 | 0.26 | 0.14 | -1.20 | 1.43 |
| Grok 4.5 | xAI | 23665 | 0.011 | 0.005 | 0.007 | 0.005 | 0.79 | 0.85 | 0.02 | 2.65 |
| Claude Opus 4.6 | Anthropic | 10121 | 0.010 | 0.005 | 0.013 | 0.005 | 0.26 | -3.6e-03 | -1.07 | 0.99 |
| Claude Haiku 4.5 | Anthropic | 26706 | 0.010 | 0.005 | 0.009 | 0.005 | 0.69 | 0.83 | -0.18 | -0.11 |
| Claude Opus 5 | Anthropic | 18943 | 0.010 | 0.005 | 0.011 | 0.005 | 0.70 | 0.72 | 1.28 | 2.39 |
| Claude Fable 5 | Anthropic | 25600 | 0.009 | 0.005 | 0.009 | 0.005 | 0.60 | 0.37 | 0.16 | 1.09 |
| Gemini 3.5 Flash | Google | 63882 | 0.009 | 0.005 | 0.010 | 0.005 | 1.47 | 0.63 | 0.43 | 0.64 |
| Claude Sonnet 5 | Anthropic | 50980 | 0.008 | 0.005 | 0.010 | 0.005 | 1.13 | 0.40 | 0.54 | 2.31 |
| DeepSeek-V4-Pro | DeepSeek | 38823 | 0.008 | 0.005 | 0.009 | 0.005 | 0.80 | 0.66 | 0.48 | 2.15 |
| GPT-5.5 | OpenAI | 28949 | 0.008 | 0.005 | 0.008 | 0.005 | 0.59 | 0.28 | -0.79 | -0.31 |
| GPT-5.6 Terra | OpenAI | 3645 | 0.008 | 0.025 | 0.006 | 0.060 | 0.08 | 0.07 | 0.66 | 0.57 |
| Claude Sonnet 4.6 | Anthropic | 14559 | 0.007 | 0.005 | 0.018 | 0.005 | 0.28 | 2.22 | 0.09 | 4.60 |
| GPT-5.1 | OpenAI | 29804 | 0.007 | 0.005 | 0.007 | 0.005 | 0.55 | 2.72 | -0.76 | 0.33 |
| GPT-5.2 | OpenAI | 50734 | 0.007 | 0.005 | 0.007 | 0.005 | 0.93 | 0.86 | 0.10 | 0.61 |
| GPT-5.6 Luna | OpenAI | 4524 | 0.007 | 0.010 | -0.029 | 1.000 | 0.08 | 0.06 | 1.14 | 0.83 |
| DeepSeek-V3.2 | DeepSeek | 42047 | 0.005 | 0.005 | 0.005 | 0.005 | 0.55 | 0.38 | -0.06 | 0.35 |
| Gemini 3.8 Flash | Google | 1957 | 0.004 | 0.070 | 0.014 | 0.020 | 0.58 | -0.06 | -1.23 | -0.16 |
| Claude Opus 4.5 | Anthropic | 47309 | 0.004 | 0.005 | 0.004 | 0.005 | 0.55 | 0.22 | -0.46 | 0.37 |
| Gemini 3.1 Pro | Google | 65475 | 0.004 | 0.005 | 0.004 | 0.005 | 0.68 | 0.64 | 1.63 | 0.35 |
| GLM-5.2 | Zhipu | 44633 | 0.003 | 0.005 | 0.003 | 0.005 | 0.36 | 0.03 | -0.02 | 0.87 |
| Gemini 2.5 Pro | Google | 83052 | 0.003 | 0.005 | 0.002 | 0.005 | 0.60 | 0.14 | 0.50 | -0.09 |

Figures: [`figures/period_summary.pdf`](figures/period_summary.pdf). Data: `data/processed/H14-behavior-entropy-production/G51/` (`agents.parquet`, `results.json`). Code: `analysis/run_period.py --period G51`.

## Scorecard (period-specific axes)
- **C (adequacy):** single-agent arrows beat the DB surrogate for 0.97 of test agents (held-out, day-blocked cross-fit). Collective term vs. cross-day null: p = 0.317 (MF), 0.024 (PW).
- **D (unfitted):** cycle orientations (P5) are not fitted by the EP estimator: not as predicted.
- **G (ground truth):** the consolidate-linked cycle is scaffold-imposed (consolidation cadence); see the card for how much EP it carries.

## Notes

## Round 1b (improved data, 2026-10-04)
*Replication layer (templated across periods). Predictions: the card's "Round 1b" predictions as they apply here. Numbers: `data/processed/H14-behavior-entropy-production/r1b/G51/`.*

| Statistic | Round 1 | Round 1b |
| --- | --- | --- |
| coarse chain: share of test agents above DB null (median Newton excess) | 0.97 (0.0090) | 0.97 (0.0090), same transitions |
| fine classes: share above null (median excess) | `act`, shell unsplit: 1.00 (0.040) | act_sh, 7 shell sub-classes: 1.00 (0.117) |
| scaffold removed (agent-only chain, 3-transition burn-in): share above null | – | coarse_b3 0.93; act_sh_b3 1.00 |
| share of the median excess kept after scaffold removal | coarse, consolidate decimated: 0.36 | coarse_b3 0.36; act_sh_b3 0.90 |
| Jev v3 pooled EP per 5-min transition (block-flip p) | – | 0.0118 (p 0.005); argmax 0.0046 (DB p 0.005) |
| Jev v3 per agent: share above flip null (n) | – | 0.89 (28); descriptive (soft tests nearly blind per agent) |

The window-level burn-in variants (v3s_b1, b1c) are selection artifacts (card, Round 1b) and are not reported here.
