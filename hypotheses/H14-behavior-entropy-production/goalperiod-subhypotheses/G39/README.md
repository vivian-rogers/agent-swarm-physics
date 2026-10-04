# H14 × G39: Build your own interactive world! (2026-04-27 → 2026-05-01)

**Verdict:** failed
**Verdict (1b):** failed (unchanged: the pre-registered coarse chain did not change). Corrected fine classes (shell sub-classes): 100% of test agents irreversible, 92% after scaffold removal with burn-in; pooled Jev v3 arrow significant (flip p 0.005)
**Role (1b):** native (loops vs progress, N3, below) in addition to the replication
**Role:** exploratory
**Period:** regime III · mode I (individual objectives) · N = 15 · #best/#rest rooms (reshuffled 04-27) · 5 days × 4 h. No step change inside.

## Why this period
An individual-objective week: the comparison arm for mode C (#40, same roster, next week) in P7, and an individual-work baseline for the collective term.

## Prediction
*Written 2026-10-03, before running on this period.* The card's predictions (`../../README.md`, "Prediction") as they apply here:
- **P2:** ≥ 80% of agents with ≥ 1,000 transitions above the DB-surrogate 95th percentile.
- **P5:** work → chat → idle → work and work → chat → consolidate → work positive in ≥ 75% of agents; one of them dominant.
- **P4:** ΔΣ_MF and ΔΣ_PW within the cross-day null (individual objectives, 5 days).
- **P7:** median Σ_i below #40's.

Verdict rule: **supported** if P2, P5 and P4 (null as predicted) hold; **mixed** if P2 holds and one or two of the others fail; **failed** if P2 fails.

## Result
*Run 2026-10-03 (exploratory, non-holdout). Primary single-agent estimator: H05's cross-fitted Newton bound (the pre-registered switch rule did not fire); companion `cfx` = cross-fitted exact dual minus its DB-null mean. DB surrogates: 200 per agent.*

| Prediction | Observed | Null / reference | Verdict |
| --- | --- | --- | --- |
| P2: ≥ 80% of agents (≥ 1,000 transitions) above the DB-surrogate 95th pct | 0.47 of 15 (cfx: 0.53); median Σ_i 0.005 (Newton), excess 0.005; cfx excess 0.007 nats/transition | 5% expected under the null | ✗ |
| P2 (minute grid): ≥ 60% above null; per-hour lower than on turns for ≥ 80% | 0.60 of 15; per-hour lower for 0.47 | | ✗ |
| P5: work → chat → idle → work and work → chat → consolidate → work positive in ≥ 75%; one dominant | 0.27 and 0.40 positive; dominant: work>chat>cons | sign tests p = 0.118, 0.607 | ✗ |
| P4: ΔΣ_MF within the cross-day null | excess -0.0737 (observed 0.0294), p = 0.990; ΔΣ_PW excess -0.0726, p = 0.713 | null mean 0.1031 ± 0.0381 (MF), 0.4477 ± 0.1015 (PW); N = 15, 4 days | ✓ |
| HH67 strong form: ΔΣ > Σ_1 | ΔΣ_MF excess / Σ_1 = -0.136; ΔΣ_PW excess / Σ_1 = -0.134 (Σ_1 = Σ_i cfx on the grid = 0.5428) | | strong form fails |
| P3 (family, descriptive here unless G38/G51) | η²_lab = 0.22 (perm p = 0.313, chance 0.29); adjusted for shell share and log n: 0.20 (p = 0.397); Anthropic − OpenAI = -0.0746 (two-sided p = 0.084) | labs: Anthropic 6, DeepSeek 1, Google 2, Moonshot 1, OpenAI 5; cfx companion η² 0.23 (p 0.330) | descriptive |

**Verdict: failed.** Other numbers: act-scheme share above null 0.80; order 2 beats order 1 (held-out likelihood) for 0.60 of agents, order-2 bound > pair bound for 0.20; removing consolidate loses a median 0.91 of the excess (the rest stays above null for 0.25); median plug-in EP share in consolidate transitions 0.62.

Per-agent table (eligible agents; excess = estimate − DB-null mean, nats/transition; Newton primary, cfx companion):

| Agent | Lab | Transitions | Σ_i Newton | p | cfx excess | p | Newton excess/h | Minute excess/h | work>chat>idle A | work>chat>cons A |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| GPT-5.5 | OpenAI | 2857 | 0.303 | 0.005 | 0.355 | 0.005 | 42.86 | 18.26 | -0.05 | -1.74 |
| GPT-5.4 | OpenAI | 2705 | 0.086 | 0.005 | 0.104 | 0.005 | 11.54 | 8.98 | 0.29 | 1.79 |
| Claude Haiku 4.5 | Anthropic | 2873 | 0.033 | 0.005 | 0.053 | 0.005 | 4.66 | 1.60 | -0.10 | 0.02 |
| DeepSeek-V3.2 | DeepSeek | 1266 | 0.022 | 0.005 | 0.020 | 0.005 | 1.35 | 0.52 | -0.60 | 1.94 |
| GPT-5 | OpenAI | 2454 | 0.012 | 0.005 | 0.017 | 0.005 | 1.40 | 0.80 | -0.37 | -1.52 |
| GPT-5.1 | OpenAI | 2567 | 0.008 | 0.010 | 0.010 | 0.040 | 1.06 | 1.25 | 0.67 | 2.82 |
| Claude Opus 4.6 | Anthropic | 1282 | 0.008 | 0.015 | 0.008 | 0.010 | 0.52 | 5.22 | 0.13 | 1.60 |
| Gemini 3.1 Pro | Google | 3317 | 0.005 | 0.060 | 0.006 | 0.085 | 0.81 | 0.14 | -0.02 | -0.01 |
| Claude Sonnet 4.5 | Anthropic | 2752 | 0.004 | 0.075 | 0.004 | 0.184 | 0.50 | 1.47 | -0.05 | -1.21 |
| Kimi K2.6 | Moonshot | 2213 | 0.003 | 0.144 | 0.003 | 0.259 | 0.29 | 0.41 | -0.45 | -0.47 |
| Claude Sonnet 4.6 | Anthropic | 1550 | 0.002 | 0.095 | 0.007 | 0.035 | 0.17 | 8.86 | 0.04 | 2.24 |
| Claude Opus 4.5 | Anthropic | 3608 | 4.8e-04 | 0.408 | -0.002 | 0.751 | 0.04 | 0.64 | -0.02 | -0.51 |
| GPT-5.2 | OpenAI | 2864 | -1.5e-04 | 0.473 | -7.8e-05 | 0.532 | -5.4e-03 | -0.08 | -0.06 | -0.60 |
| Claude Opus 4.7 | Anthropic | 2432 | -0.005 | 0.965 | -0.022 | 1.000 | -0.58 | 0.46 | -0.54 | -0.40 |
| Gemini 2.5 Pro | Google | 1877 | -0.008 | 0.970 | -0.011 | 0.965 | -0.84 | 0.43 | 0.00 | -0.02 |

Figures: [`figures/period_summary.pdf`](figures/period_summary.pdf). Data: `data/processed/H14-behavior-entropy-production/G39/` (`agents.parquet`, `results.json`). Code: `analysis/run_period.py --period G39`.

## Scorecard (period-specific axes)
- **C (adequacy):** single-agent arrows beat the DB surrogate for 0.47 of test agents (held-out, day-blocked cross-fit). Collective term vs. cross-day null: p = 0.990 (MF), 0.713 (PW).
- **D (unfitted):** cycle orientations (P5) are not fitted by the EP estimator: not as predicted.
- **G (ground truth):** the consolidate-linked cycle is scaffold-imposed (consolidation cadence); see the card for how much EP it carries.

## Notes

## Round 1b (improved data, 2026-10-04)
*Replication layer (templated across periods). Predictions: the card's "Round 1b" predictions as they apply here. Numbers: `data/processed/H14-behavior-entropy-production/r1b/G39/`.*

| Statistic | Round 1 | Round 1b |
| --- | --- | --- |
| coarse chain: share of test agents above DB null (median Newton excess) | 0.47 (0.0050) | 0.47 (0.0048), same transitions |
| fine classes: share above null (median excess) | `act`, shell unsplit: 0.80 (0.075) | act_sh, 7 shell sub-classes: 1.00 (0.197) |
| scaffold removed (agent-only chain, 3-transition burn-in): share above null | – | coarse_b3 0.23; act_sh_b3 0.92 |
| share of the median excess kept after scaffold removal | coarse, consolidate decimated: 0.09 | coarse_b3 0.21; act_sh_b3 1.04 |
| Jev v3 pooled EP per 5-min transition (block-flip p) | – | 0.0261 (p 0.005); argmax 0.0066 (DB p 0.045) |
| Jev v3 per agent: share above flip null (n) | – | n/a (0); descriptive (soft tests nearly blind per agent) |

The window-level burn-in variants (v3s_b1, b1c) are selection artifacts (card, Round 1b) and are not reported here.

## Native test (round 1b): loops vs progress (H14-R2)
*Prediction written 2026-10-04 before running (card, "Round 1b", N3).* #38–#40 are the loop-heavy weeks (H12's self-repetition). Pooled Jev v3 soft EP per transition on transitions whose two windows are both *productive* (git-printed commit or push, or progress score ≥ 3) exceeds that on transitions whose windows are both *stuck* (p_blocked ≥ 0.5 or longest_run ≥ 5), with the agent-day bootstrap CI of the difference above 0, in ≥ 2 of the 3 periods. Credence 0.4.

*Result (`analysis/native_r1b.py`):* productive 0.0243 (522 transitions, 1030 windows) vs stuck -0.0368 (90 transitions, 293 windows); difference +0.0611, 95% CI [-0.911, 0.613]. **Does not hold here**; across #38–#40 the prediction holds in 0/3 (failed). Stuck windows are not near-reversible.
