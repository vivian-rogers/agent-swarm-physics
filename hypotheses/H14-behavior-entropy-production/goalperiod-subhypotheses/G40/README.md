# H14 × G40: Connect your worlds into a 3D universe! (2026-05-04 → 2026-05-08)

**Verdict:** failed
**Verdict (1b):** failed (unchanged: the pre-registered coarse chain did not change). Corrected fine classes (shell sub-classes): 100% of test agents irreversible, 93% after scaffold removal with burn-in; pooled Jev v3 arrow not significant (flip p 0.139)
**Role (1b):** native (loops vs progress, N3, below) in addition to the replication
**Role:** replication (exploratory)
**Period:** regime III · mode C (shared objective) · N = 15 · rooms merged into #universe-coordination on 05-04 (GPT-5 left alone in #rest) · 5 days × 4 h. The merge is at the period start, so no split inside.

## Why this period
Shared objective in one merged room: the most favourable 5-day period for a collective term. H02 found its only robust collective signal (mean-field co-activation) in #40 and #44.

## Prediction
*Written 2026-10-03, before running on this period.* The card's predictions (`../../README.md`, "Prediction") as they apply here:
- **P2:** ≥ 80% of agents with ≥ 1,000 transitions above the DB-surrogate 95th percentile.
- **P5:** work → chat → idle → work and work → chat → consolidate → work positive in ≥ 75% of agents; one of them dominant.
- **P4:** ΔΣ_MF above the cross-day null 95th percentile. ΔΣ_PW at noise.
- **P7:** median Σ_i above #39's and #41's.

Verdict rule: **supported** if P2, P5 and P4 (ΔΣ_MF) hold; **mixed** if P2 holds and one or two of the others fail; **failed** if P2 fails.

## Result
*Run 2026-10-03 (exploratory, non-holdout). Primary single-agent estimator: H05's cross-fitted Newton bound (the pre-registered switch rule did not fire); companion `cfx` = cross-fitted exact dual minus its DB-null mean. DB surrogates: 200 per agent.*

| Prediction | Observed | Null / reference | Verdict |
| --- | --- | --- | --- |
| P2: ≥ 80% of agents (≥ 1,000 transitions) above the DB-surrogate 95th pct | 0.60 of 15 (cfx: 0.53); median Σ_i 0.006 (Newton), excess 0.006; cfx excess 0.009 nats/transition | 5% expected under the null | ✗ |
| P2 (minute grid): ≥ 60% above null; per-hour lower than on turns for ≥ 80% | 0.40 of 15; per-hour lower for 0.73 | | ✗ |
| P5: work → chat → idle → work and work → chat → consolidate → work positive in ≥ 75%; one dominant | 0.67 and 0.80 positive; dominant: work>chat>cons | sign tests p = 0.302, 0.035 | ✗ |
| P4: ΔΣ_MF above the cross-day null | excess -0.0361 (observed 0.0152), p = 0.931; ΔΣ_PW excess -0.0124, p = 0.554 | null mean 0.0512 ± 0.0251 (MF), 0.2087 ± 0.0584 (PW); N = 15, 5 days | ✗ |
| HH67 strong form: ΔΣ > Σ_1 | ΔΣ_MF excess / Σ_1 = -0.131; ΔΣ_PW excess / Σ_1 = -0.045 (Σ_1 = Σ_i cfx on the grid = 0.2748) | | strong form fails |
| P3 (family, descriptive here unless G38/G51) | η²_lab = 0.07 (perm p = 0.971, chance 0.29); adjusted for shell share and log n: 0.33 (p = 0.314); Anthropic − OpenAI = -0.0021 (two-sided p = 0.822) | labs: Anthropic 6, DeepSeek 1, Google 2, Moonshot 1, OpenAI 5; cfx companion η² 0.20 (p 0.588) | descriptive |

**Verdict: failed.** Other numbers: act-scheme share above null 0.80; order 2 beats order 1 (held-out likelihood) for 0.60 of agents, order-2 bound > pair bound for 0.53; removing consolidate loses a median 0.86 of the excess (the rest stays above null for 0.27); median plug-in EP share in consolidate transitions 0.46.

Per-agent table (eligible agents; excess = estimate − DB-null mean, nats/transition; Newton primary, cfx companion):

| Agent | Lab | Transitions | Σ_i Newton | p | cfx excess | p | Newton excess/h | Minute excess/h | work>chat>idle A | work>chat>cons A |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Claude Opus 4.6 | Anthropic | 1118 | 0.052 | 0.005 | 0.073 | 0.005 | 2.88 | 1.90 | 0.31 | 4.30 |
| GPT-5.4 | OpenAI | 2804 | 0.050 | 0.005 | 0.063 | 0.005 | 6.85 | 0.53 | 1.92 | 4.18 |
| Gemini 2.5 Pro | Google | 2190 | 0.033 | 0.040 | 0.004 | 0.338 | 3.48 | 0.35 | 0.00 | -0.03 |
| GPT-5.5 | OpenAI | 2485 | 0.026 | 0.005 | 0.034 | 0.005 | 3.18 | 0.74 | 2.65 | 0.04 |
| Claude Opus 4.7 | Anthropic | 2575 | 0.021 | 0.005 | 0.031 | 0.005 | 2.75 | 2.61 | 0.22 | 3.46 |
| Claude Sonnet 4.6 | Anthropic | 2042 | 0.017 | 0.005 | 0.021 | 0.005 | 1.71 | 12.59 | 0.06 | 1.47 |
| GPT-5 | OpenAI | 2230 | 0.008 | 0.010 | 0.009 | 0.010 | 0.91 | 0.31 | 0.00 | -0.02 |
| Kimi K2.6 | Moonshot | 1973 | 0.006 | 0.075 | 0.010 | 0.050 | 0.61 | 0.21 | 1.77 | 2.08 |
| GPT-5.2 | OpenAI | 2768 | 0.005 | 0.040 | 0.012 | 0.005 | 0.77 | 0.37 | 0.04 | 2.51 |
| DeepSeek-V3.2 | DeepSeek | 2763 | 0.003 | 0.050 | -0.010 | 0.995 | 0.42 | 0.29 | 0.04 | 0.88 |
| Claude Haiku 4.5 | Anthropic | 4336 | 0.003 | 0.090 | -0.003 | 0.866 | 0.60 | -0.31 | -0.02 | 1.15 |
| GPT-5.1 | OpenAI | 2301 | 0.002 | 0.229 | 0.004 | 0.219 | 0.24 | 1.04 | 0.00 | 1.10 |
| Claude Opus 4.5 | Anthropic | 4231 | 0.002 | 0.134 | 0.005 | 0.085 | 0.39 | 0.04 | 0.02 | 1.29 |
| Claude Sonnet 4.5 | Anthropic | 3820 | 0.002 | 0.104 | -9.3e-04 | 0.647 | 0.33 | 0.36 | -1.15 | -1.04 |
| Gemini 3.1 Pro | Google | 4168 | 0.002 | 0.204 | -0.002 | 0.806 | 0.31 | 1.04 | 1.46 | 0.66 |

Figures: [`figures/period_summary.pdf`](figures/period_summary.pdf). Data: `data/processed/H14-behavior-entropy-production/G40/` (`agents.parquet`, `results.json`). Code: `analysis/run_period.py --period G40`.

## Scorecard (period-specific axes)
- **C (adequacy):** single-agent arrows beat the DB surrogate for 0.60 of test agents (held-out, day-blocked cross-fit). Collective term vs. cross-day null: p = 0.931 (MF), 0.554 (PW).
- **D (unfitted):** cycle orientations (P5) are not fitted by the EP estimator: not as predicted.
- **G (ground truth):** the consolidate-linked cycle is scaffold-imposed (consolidation cadence); see the card for how much EP it carries.

## Notes

## Round 1b (improved data, 2026-10-04)
*Replication layer (templated across periods). Predictions: the card's "Round 1b" predictions as they apply here. Numbers: `data/processed/H14-behavior-entropy-production/r1b/G40/`.*

| Statistic | Round 1 | Round 1b |
| --- | --- | --- |
| coarse chain: share of test agents above DB null (median Newton excess) | 0.60 (0.0062) | 0.60 (0.0064), same transitions |
| fine classes: share above null (median excess) | `act`, shell unsplit: 0.80 (0.055) | act_sh, 7 shell sub-classes: 1.00 (0.117) |
| scaffold removed (agent-only chain, 3-transition burn-in): share above null | – | coarse_b3 0.21; act_sh_b3 0.93 |
| share of the median excess kept after scaffold removal | coarse, consolidate decimated: 0.14 | coarse_b3 0.06; act_sh_b3 0.84 |
| Jev v3 pooled EP per 5-min transition (block-flip p) | – | 0.0026 (p 0.139); argmax 0.0007 (DB p 0.428) |
| Jev v3 per agent: share above flip null (n) | – | n/a (0); descriptive (soft tests nearly blind per agent) |

The window-level burn-in variants (v3s_b1, b1c) are selection artifacts (card, Round 1b) and are not reported here.

## Native test (round 1b): loops vs progress (H14-R2)
*Prediction written 2026-10-04 before running (card, "Round 1b", N3).* #38–#40 are the loop-heavy weeks (H12's self-repetition). Pooled Jev v3 soft EP per transition on transitions whose two windows are both *productive* (git-printed commit or push, or progress score ≥ 3) exceeds that on transitions whose windows are both *stuck* (p_blocked ≥ 0.5 or longest_run ≥ 5), with the agent-day bootstrap CI of the difference above 0, in ≥ 2 of the 3 periods. Credence 0.4.

*Result (`analysis/native_r1b.py`):* productive 0.0052 (695 transitions, 1117 windows) vs stuck 0.4058 (88 transitions, 286 windows); difference -0.4007, 95% CI [-3.123, -0.167]. **Does not hold here**; across #38–#40 the prediction holds in 0/3 (failed). Stuck windows are not near-reversible; here they are more irreversible than productive ones.
