# H14 × G42: Run your own Youtube channel! (2026-05-18 → 2026-05-22)

**Verdict:** failed
**Verdict (1b):** failed (unchanged: the pre-registered coarse chain did not change). Corrected fine classes (shell sub-classes): 100% of test agents irreversible, 93% after scaffold removal with burn-in; pooled Jev v3 arrow significant (flip p 0.020)
**Role:** exploratory
**Period:** regime III · mode I · N = 15 (+1: Gemini 3.5 Flash joins 05-20) · #best/#rest rooms · 5 days × 4 h. The join is a roster step; Gemini 3.5 Flash has 3 days and enters single-agent tests only.

## Why this period
Third mode-I arm; production-heavy (video uploads), so more GUI work than #39/#41.

## Prediction
*Written 2026-10-03, before running on this period.* The card's predictions (`../../README.md`, "Prediction") as they apply here:
- **P2:** ≥ 80% of agents with ≥ 1,000 transitions above the DB-surrogate 95th percentile.
- **P5:** work → chat → idle → work and work → chat → consolidate → work positive in ≥ 75% of agents; one of them dominant.
- **P4:** ΔΣ_MF and ΔΣ_PW within the cross-day null (the collective analysis uses the 15 agents present all 5 days).

Verdict rule: **supported** if P2, P5 and P4 (null as predicted) hold; **mixed** if P2 holds and one or two of the others fail; **failed** if P2 fails.

## Result
*Run 2026-10-03 (exploratory, non-holdout). Primary single-agent estimator: H05's cross-fitted Newton bound (the pre-registered switch rule did not fire); companion `cfx` = cross-fitted exact dual minus its DB-null mean. DB surrogates: 200 per agent.*

| Prediction | Observed | Null / reference | Verdict |
| --- | --- | --- | --- |
| P2: ≥ 80% of agents (≥ 1,000 transitions) above the DB-surrogate 95th pct | 0.56 of 16 (cfx: 0.50); median Σ_i 0.008 (Newton), excess 0.007; cfx excess 0.005 nats/transition | 5% expected under the null | ✗ |
| P2 (minute grid): ≥ 60% above null; per-hour lower than on turns for ≥ 80% | 0.50 of 16; per-hour lower for 0.62 | | ✗ |
| P5: work → chat → idle → work and work → chat → consolidate → work positive in ≥ 75%; one dominant | 0.25 and 0.56 positive; dominant: work>chat>cons | sign tests p = 0.077, 0.804 | ✗ |
| P4: ΔΣ_MF within the cross-day null | excess 0.0167 (observed 0.0814), p = 0.267; ΔΣ_PW excess 0.0739, p = 0.139 | null mean 0.0646 ± 0.0277 (MF), 0.2383 ± 0.0637 (PW); N = 15, 5 days | ✓ |
| HH67 strong form: ΔΣ > Σ_1 | ΔΣ_MF excess / Σ_1 = –; ΔΣ_PW excess / Σ_1 = – (Σ_1 = Σ_i cfx on the grid = -0.2777) | | strong form holds |
| P3 (family, descriptive here unless G38/G51) | η²_lab = 0.39 (perm p = 0.193, chance 0.27); adjusted for shell share and log n: 0.40 (p = 0.187); Anthropic − OpenAI = 0.0214 (two-sided p = 0.101) | labs: Anthropic 6, DeepSeek 1, Google 3, Moonshot 1, OpenAI 5; cfx companion η² 0.30 (p 0.261) | descriptive |

**Verdict: failed.** Other numbers: act-scheme share above null 0.94; order 2 beats order 1 (held-out likelihood) for 0.75 of agents, order-2 bound > pair bound for 0.44; removing consolidate loses a median 0.57 of the excess (the rest stays above null for 0.53); median plug-in EP share in consolidate transitions 0.38.

Per-agent table (eligible agents; excess = estimate − DB-null mean, nats/transition; Newton primary, cfx companion):

| Agent | Lab | Transitions | Σ_i Newton | p | cfx excess | p | Newton excess/h | Minute excess/h | work>chat>idle A | work>chat>cons A |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Claude Sonnet 4.6 | Anthropic | 2772 | 0.073 | 0.005 | 0.082 | 0.005 | 9.96 | 9.23 | -6.18 | 0.08 |
| Claude Haiku 4.5 | Anthropic | 3408 | 0.044 | 0.005 | 0.031 | 0.005 | 7.41 | 2.44 | -1.21 | 2.26 |
| Claude Opus 4.7 | Anthropic | 2429 | 0.032 | 0.005 | 0.022 | 0.005 | 3.84 | 1.42 | 1.12 | 1.42 |
| GPT-5.4 | OpenAI | 2445 | 0.023 | 0.005 | 0.026 | 0.005 | 2.73 | 2.40 | 0.19 | 2.66 |
| Claude Sonnet 4.5 | Anthropic | 2219 | 0.016 | 0.005 | 0.009 | 0.050 | 1.73 | -0.19 | -1.05 | 0.54 |
| Claude Opus 4.6 | Anthropic | 2539 | 0.012 | 0.005 | 0.014 | 0.005 | 1.51 | 0.24 | 0.11 | 1.04 |
| DeepSeek-V3.2 | DeepSeek | 1595 | 0.012 | 0.010 | -0.011 | 0.930 | 0.94 | -0.12 | -1.98 | -0.24 |
| GPT-5.5 | OpenAI | 2796 | 0.010 | 0.005 | -0.004 | 0.881 | 1.31 | 1.69 | -0.05 | -0.11 |
| GPT-5 | OpenAI | 2044 | 0.006 | 0.015 | 0.006 | 0.010 | 0.55 | 0.13 | 0.00 | 0.00 |
| GPT-5.1 | OpenAI | 1917 | 0.004 | 0.144 | 0.018 | 0.010 | 0.36 | 1.54 | -0.15 | 3.23 |
| Gemini 2.5 Pro | Google | 4145 | 0.003 | 0.060 | 0.004 | 0.070 | 0.62 | 0.42 | 2.51 | 1.42 |
| Claude Opus 4.5 | Anthropic | 2784 | 0.003 | 0.134 | -0.003 | 0.826 | 0.37 | 0.60 | -0.04 | -0.60 |
| Gemini 3.1 Pro | Google | 3234 | 0.002 | 0.174 | 0.001 | 0.433 | 0.40 | 0.63 | -1.40 | -0.66 |
| Kimi K2.6 | Moonshot | 2167 | 0.001 | 0.303 | 0.001 | 0.443 | 0.16 | 0.24 | -0.04 | -0.46 |
| GPT-5.2 | OpenAI | 3088 | 8.0e-04 | 0.373 | 0.001 | 0.383 | 0.09 | 1.33 | -0.04 | -0.40 |
| Gemini 3.5 Flash | Google | 2206 | -0.003 | 0.841 | -0.005 | 0.796 | -0.60 | -1.20 | -0.92 | 1.02 |

Figures: [`figures/period_summary.pdf`](figures/period_summary.pdf). Data: `data/processed/H14-behavior-entropy-production/G42/` (`agents.parquet`, `results.json`). Code: `analysis/run_period.py --period G42`.

## Scorecard (period-specific axes)
- **C (adequacy):** single-agent arrows beat the DB surrogate for 0.56 of test agents (held-out, day-blocked cross-fit). Collective term vs. cross-day null: p = 0.267 (MF), 0.139 (PW).
- **D (unfitted):** cycle orientations (P5) are not fitted by the EP estimator: not as predicted.
- **G (ground truth):** the consolidate-linked cycle is scaffold-imposed (consolidation cadence); see the card for how much EP it carries.

## Notes

## Round 1b (improved data, 2026-10-04)
*Replication layer (templated across periods). Predictions: the card's "Round 1b" predictions as they apply here. Numbers: `data/processed/H14-behavior-entropy-production/r1b/G42/`.*

| Statistic | Round 1 | Round 1b |
| --- | --- | --- |
| coarse chain: share of test agents above DB null (median Newton excess) | 0.56 (0.0074) | 0.56 (0.0074), same transitions |
| fine classes: share above null (median excess) | `act`, shell unsplit: 0.94 (0.111) | act_sh, 7 shell sub-classes: 1.00 (0.155) |
| scaffold removed (agent-only chain, 3-transition burn-in): share above null | – | coarse_b3 0.67; act_sh_b3 0.93 |
| share of the median excess kept after scaffold removal | coarse, consolidate decimated: 0.43 | coarse_b3 1.14; act_sh_b3 1.02 |
| Jev v3 pooled EP per 5-min transition (block-flip p) | – | 0.0073 (p 0.020); argmax 0.0042 (DB p 0.169) |
| Jev v3 per agent: share above flip null (n) | – | n/a (0); descriptive (soft tests nearly blind per agent) |

The window-level burn-in variants (v3s_b1, b1c) are selection artifacts (card, Round 1b) and are not reported here.
