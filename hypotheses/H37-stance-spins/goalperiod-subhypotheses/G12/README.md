# H37 × G12: Form two teams and debate each other, while one agent judges (2025-09-01 → 2025-09-08)

**Verdict:** supported (positive control passes P1–P5)
**Role:** exploratory (positive control)
**Period:** regime I · mode M · 7 agents · one room (#general) · 5 days (debates 09-01 → 09-04). Ten Asian-Parliamentary debates with re-drafted teams and rotating judges (H21's verified labels, `../../../H21-debate-antiferromagnet/scheme/labels/g12_debates.json`).

## Why this period
The debate rules force cross-team disagreement, so if zero-shot stance labels can see conflict anywhere, they must see it here. H21 found no team order in content space (only a faint a-priori stance tilt); this period therefore separates *stance* from *topic* on known teams.

## Prediction
*Written 2026-10-04 01:53 UTC, before running on this period (card predictions P1–P5, written 01:35 UTC).*
Replies with B inside a debate's speech window [first speech, verdict), both authors among that debate's debaters; Jev responds ≥ 0.5; soft stance.
- **P1:** s̄(opposite) < 0 < s̄(same); agent-adjusted γ̂ (same − opposite) > 0 with within-debate team-permutation p < 0.01. [0.85]
- **P2:** AUC_stance ≥ 0.65, AUC_topic ∈ [0.40, 0.60]; γ̂ keeps p < 0.01 with topic cosine as covariate. [0.7]
- **P3:** per-debate ground state of the residual stance graph recovers the teams, mean accuracy ≥ 0.80 and p < 0.05 vs random balanced splits; the topic graph does not. [0.55]
- **P4 (descriptive):** pooled debate graphs less frustrated than the sign-shuffle null. [0.6]
- **P5 (HH127, descriptive):** γ̂ after the verdict < γ̂ during the debate. [0.6]
- *Against:* γ̂ ≤ 0 or p > 0.05 (the labeller cannot see forced disagreement); topic separating teams as well as stance.

## Result
*Run 2026-10-04 (`analysis/explore.py`; data `data/processed/H37-stance-spins/G12/results.json`; figure `figures/g12_stance_by_phase.pdf`).* Primary set: 926 debate-window replies between debaters (411 same-team, 515 opposite-team), Jev responds ≥ 0.5, soft stance; 7 agents; within-debate team permutation (5,000).

| Prediction | Observed | Null / reference | Verdict |
| --- | --- | --- | --- |
| P1 s̄(opp) < 0 < s̄(same); γ̂ > 0, p < 0.01 | s̄(same) +0.32, s̄(opp) −0.13; oppose/undermine share 6% vs 26%; γ̂ = +0.42 | permutation p = 0.0002 | **pass** |
| P2 AUC_stance ≥ 0.65, AUC_topic in [0.40, 0.60], γ̂ survives topic covariate | AUC 0.74 (stance) vs 0.48 (topic); γ̂(topic) −0.009; γ̂ with topic covariate p = 0.0002 | 0.5 | **pass** |
| P3 team recovery ≥ 0.80, p < 0.05; topic graph not | stance 0.89 (exact split in 7/10 debates; the 3 misses are the 3 smallest debates, 29–49 replies); topic 0.71 | chance 0.70; p < 10⁻⁴ (stance), 0.46 (topic) | **pass** |
| P4 frustration below sign-shuffle | f_gs 0.08 (true team split leaves 0.14 unsatisfied) | null 0.14, p = 0.0015 | pass (descriptive) |
| P5 γ̂ after verdict < during | γ̂ +0.42 (debate) → +0.03 (post, p 0.29); opponents' stance jumps from −0.13 to +0.36 | | pass: relaxation, no sign flip |

**Robustness.** All pairs (no relevance filter): γ̂ 0.38, AUC 0.73 vs 0.50. Hard labels: γ̂ 0.42, AUC 0.67. Debater-adjacent pairs only (Amendment 1): γ̂ 0.41 (p 0.0005), AUC 0.71 vs 0.47. Before the first speech (lineups, prep): γ̂ 0.27 (p 0.002), AUC 0.58: teams are already slightly visible. Per debate, s̄(same) > s̄(opp) in 9/10 debates (debate 10, 30 replies, reversed).

**Whole-period detector (all 5,818 relevant replies, teams not used).** Oppose/undermine share 9.7% [8.7, 10.7]; 3 of 21 agent pairs significantly negative after agent fields (Claude 3.7 Sonnet–Claude Opus 4, Gemini 2.5 Pro–GPT-5, Claude Opus 4.1–Grok 4); faction score sign-shuffle p = 0.005 (see Amendment 2 calibration in the card: this null is anti-conservative).

**Reading.** Zero-shot stance labels see assigned conflict that topic embeddings cannot (H21 found no team order in content): the same reply pairs are equally similar in topic across and within teams (cosine 0.53 vs 0.54), but opposite in sign. The conflict switches off within the 10-min post-verdict window: opponents turn as positive as teammates. HH127's "negative remanence" (a flip) is not seen in stance; relaxation is.

## Scorecard (period-specific axes)
| Axis | Score | Evidence |
| --- | --- | --- |
| C adequacy | 2 | beats team permutation, agent fields (FE) and topic (covariate and AUC) |
| D unfitted predictions | 1 | per-debate team recovery (unfitted) and frustration below null; post-verdict relaxation |
| G ground truth | 2 | verified team labels recovered exactly in 7/10 debates |

## Notes
- 2026-10-04: Amendment 1 adds judge-excluded debater-adjacent pairs (207 new); most debate-window messages are procedural.
