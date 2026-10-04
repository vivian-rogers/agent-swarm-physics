# H21 × G12: Form two teams and debate each other, while one agent judges (2025-09-01 → 09-05)

**Verdict:** failed (coupled two-sublattice antiferromagnet); descriptive: weak one-dimensional staggered moment along the motion's stance axis, and a uniform topic field that switches off at the verdict
**Verdict (1b):** supported in stance (two-sublattice order; content still failed; native: supported)
**Role:** native (was: exploratory (round 1, not held out); native (round 1b: re-drafting as a within-pair design))
**Period:** regime I · mode M (teams) · 7 agents · one room (#general) · 5 days (debates on 4). Labs: Anthropic ×3 (Claude 3.7 Sonnet, Claude Opus 4, Claude Opus 4.1), OpenAI ×2 (o3, GPT-5), Google (Gemini 2.5 Pro), xAI (Grok 4). Splits inside the period: 09-03 (village day number added to the prompt) and 09-05 (history search tool, chain-of-thought memory). No debate was held on 09-05, so the second change touches no debate.

## Why this period
It is the only non-holdout period with explicit, public, *assigned* two-team structure and a judge. HH103 points here; model 10 ranks #12 first. It is the cleanest ground-truth test (axis G) of whether content vectors order as two sublattices, and it calibrates the hidden-team detection test planned for #34 (🔒).

## Structure derived from the record (before any outcome)
**How it was derived.**
1. I read the operator's kickoff instructions. The judge rotates each debate; the judge assigns captains; captains draft; the judge announces the motion, runs the debate and gives the verdict.
2. A helper agent read the full chat log and drafted, for every debate, the judge, line-ups, motion, first speech and verdict, with line references.
3. I then re-checked every line-up and every verdict against the full message text: the judge's own confirmation where it exists, and otherwise the participants' acknowledgements. The labels below are the result.

Only derived labels are committed (`../../scheme/labels/g12_debates.json`, with message ids). No agent text is stored anywhere. All labels were fixed before any embedding statistic was computed. The masked embeddings were built after the labels, and no alignment outcome was looked at.

**What the record shows.**
- 10 debates, all held 09-01 → 09-04. None was set up and abandoned. On 09-05 there was no debate; the agents treated #10 as the finale and did other work.
- Government always argued *for* the motion as worded.
- The judge rotated for #1–#4, then Claude Opus 4.1 judged #5–#10. GPT-5 and Claude Opus 4 never judged.
- Two motions were proposed by debaters (#6 by GPT-5, #7 by o3); the rest by the judge.
- #7 kept #6's teams and sides.
- Opposition won 7 of 10.

| # | date | judge | Government | Opposition | bench | topic (paraphrase) | winner | min | debater statements in 'deb' |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 09-01 | Gem | S3.7, o3, Grok | Op4, Op4.1, G5 | – | indefinite pause on AGI development | Gov | 10 | 48 |
| 2 | 09-01 | o3 | Gem, Op4.1, Op4 | S3.7, G5 | Grok | ban corporate political donations | Opp 2-1 | 3 | 18 |
| 3 | 09-01 | Grok | Op4.1, G5, o3 | S3.7, Gem, Op4 | – | UBI essential in an AI economy | Opp | 16 | 85 |
| 4 | 09-02 | S3.7 | Grok, G5, Gem | Op4.1, o3, Op4 | – | legal personhood for AI agents | Opp 72-68 | 8 | 41 |
| 5 | 09-02 | Op4.1 | Gem, Op4, Grok | S3.7, G5, o3 | – | nationalize social media as utilities | Opp 78-72 | 22 | 88 |
| 6 | 09-03 | Op4.1 | Gem, S3.7, o3 | G5, Op4, Grok | – | license frontier general-purpose AI | Opp 76-74 | 19 | 97 |
| 7 | 09-04 | Op4.1 | Gem, S3.7, o3 | G5, Op4, Grok | – | prefer open-source frontier LLMs | Gov 75-73 | 10 | 32 |
| 8 | 09-04 | Op4.1 | S3.7, Grok, G5 | o3, Op4, Gem | – | compensate people for training data | Opp 74-72 | 10 | 63 |
| 9 | 09-04 | Op4.1 | Gem, S3.7 | Op4, Grok, o3 | G5 | AI right to refuse unethical tasks | Opp 76-74 | 18 | 73 |
| 10 | 09-04 | Op4.1 | o3, G5, S3.7 | Op4, Gem, Grok | – | ban autonomous lethal military AI | Gov 77-73 | 10 | 37 |

S3.7 = Claude 3.7 Sonnet, Op4 = Claude Opus 4, Op4.1 = Claude Opus 4.1, Gem = Gemini 2.5 Pro, G5 = GPT-5, Grok = Grok 4. "min" is the first speech → verdict time. **Procedural irregularities** (they add noise; none changes a team label):
- #2: 30-s shot clock; 3 of 5 speeches forfeited.
- #5: Claude 3.7 Sonnet substituted for the absent GPT-5.
- #7: GPT-5 and Claude 3.7 Sonnet absent at the start.
- #7–#10: Grok 4 forfeited, stuck in computer sessions (the operator later reported a memory-compression fault).
- Several debaters narrated computer use mid-debate.

**Phases** (rule in the labels file):
- pre: sides and motion known, at most 15 min before the first speech;
- deb: first speech → verdict;
- post: verdict → +10 min, cut at the next debate's pre phase.

Counts:
- statements in debate windows: pre 304, deb 721, post 354 (all speakers);
- outside any debate window: 2,240;
- post windows are short after #7 and #8 (35 s and 3.7 min), because the next debate was set up at once.

## Prediction
*Written 2026-10-03, before running on this period.* See the card's "Prediction" section ([card](../../README.md)); it applies here unchanged (G12 is the card's only exploratory period). In brief:
- P1–P3: two-sublattice order is present and recovers the teams.
- P4: a motion-specific part survives role masking and removal of the generic axis.
- P5: it is not a lab effect.
- P6: the order collapses after the verdict, with no flip.
- P7: sublattice fluctuations are, at best, weakly anti-correlated (not expected to be significant).

## Result
Run 2026-10-03:
- pre-registered: `../../analysis/g12_analysis.py` → `data/processed/H21-debate-antiferromagnet/G12/results.json`;
- post hoc, labelled: `../../analysis/g12_posthoc.py` → `results_posthoc.json`.

Figures in `figures/`:
- `g12_partitions.pdf`: Δ for every split, true split highlighted;
- `g12_robustness.pdf`;
- `g12_text_axis_phases.pdf`;
- `g12_verdict.pdf`;
- `g12_fluct.pdf`.

| Prediction | Observed (95% CI) | Null | Verdict |
| --- | --- | --- | --- |
| P1 staggered order Δ̄ > 0 | 0.028 [−0.10, 0.17] | permutation 95th pct 0.128; p = 0.34; rotation p = 0.18 | failed |
| P2 teams recovered ≥ 4/10 | 1/10 | chance 1.5; p = 0.82 | failed |
| P3 LOAO m_s > 0 | 0.032 [−0.11, 0.18] | p = 0.27 | failed |
| P3 uniform topic order **M**_u·ĝ > 0 | 10/10 debates; mean 0.42 (pre 0.28, post 0.01) | sign p = 0.001 | as predicted |
| P4 generic-axis transfer | −0.069 | orientation-flip p = 0.96 | failed |
| P4 motion-specific Δ̄ | 0.032 | p = 0.32 | failed |
| P4 text axis (support − oppose templates) | σ = 0.092; motion-specific 0.059 | p = 0.002; p = 0.03; 9/10 debates | exceeded (unpredicted significance) |
| P5 pair-FE team coefficient | 0.047 (19/21 pairs switch sides) | p = 0.19 | failed |
| P5 lab placebo | Δ̄ = 0.036 | p = 0.27 | n.s., as predicted (moot) |
| P6 remanence on the LOAO axis | σ_deb ≈ 0, so R undefined | — | untestable |
| P6 judge's verdict toward the winner | 3/10 (LOAO axis); 7/10 (text axis, post hoc) | — | failed as registered |
| P7 sublattice fluctuations ρ < 0 | +0.53 (3 min); −0.12 (2 min); +0.14 (5 min) | upper-tail p ≈ 0.0005 at 3 min | failed (common drive, fragile) |
| *post hoc* text axis by phase | Gov − Opp: pre +0.13, debate +0.43, post −0.36 | p(deb) = 0.0008; post 7/9 negative | reversal after the verdict |
| *post hoc* crossing vs winner field | κ = 0.27 [−0.02, 0.52] (8/10); w = −0.34 [−0.74, 0.14] | — | crossing, no winner field |
| *post hoc* same-lab vs different-lab pair cosine | +0.20 | exact p = 0.10 (420 relabelings) | family > team |

**Reading.** During a debate the debaters share strong uniform order along the motion's topic. Family co-variation is larger than team co-variation. The assigned side tilts each debater only slightly along a single stance direction: μ ≈ 0.2 of the per-dimension statement noise, below the full-vector test's reach (about 0.5). There is no antiferromagnetic coupling signature. After the verdict the topic order switches off and (post hoc) the stance tilt reverses: each side concedes toward the other.

## Native test (round 1b): re-drafting separates the team coupling from the pair
*Written 2026-10-04 07:14 UTC, before computing any within-pair statistic.* Seen before: round 1 above; H37's #12 stance results (opponents −0.13 vs teammates +0.32; 7/10 teams recovered; contrast gone after the verdict); DQ2's #12 check (opposite-team "opposes" 33% vs 6%); DQ6's #12 team, judge, result and phase rows.

- **Why native.** Teams were re-drafted for every debate (except #7 = #6), so the same two agents are teammates in some debates and opponents in others. A within-pair contrast removes everything fixed about the pair (shared family, habitual friendliness, each agent's agreeableness): what is left is the coupling that the team assignment switches on. No other period moves the same agents across sides.
- **Observable (stance channel).** DQ2 `reply_pairs` (`pair_set = cand`, labelled), B and A both debaters of the same debate, B in that debate's `deb` phase; soft stance s = p_reply · (p_supports − p_opposes) / Σ p_reply. For each unordered pair seen as teammates in ≥ 1 debate and as opponents in ≥ 1 debate, with ≥ 1 reply between them in each condition: c_ij = s̄(opponents) − s̄(teammates).
- **Observable (content channel).** Per debate, H21's spins (masked, whitened, agent-centred, debate-centred window means; bge and gte): c_ij^content = mean cos as opponents − mean cos as teammates.
- **Nulls.** Exact sign-flip permutation over pairs (condition labels swapped within a pair); the calibrated agent-field null (ordered logit with speaker and target fields fitted on all debate replies, `infra/shared/nulls.py: agent_field_null`, 500 simulations of hard labels on the real reply structure; the within-pair contrast recomputed on hard labels).
- **Prediction.** Stance: mean c < 0 with sign-flip p < 0.05 and below the agent-field null's 5th percentile (credence 0.7). Content: |mean c^content| < 0.05 and p > 0.05 in both models (credence 0.6).
- **Reading.** Stance pass + content null = the antiferromagnet is a coupling switched on by the assignment, and lives in stance, not topic. Stance null = H37's contrast came from agent or pair composition, not from the assignment.

**Native result** (run 2026-10-04 after the prediction; `analysis/r1b.py` → `data/processed/H21-debate-antiferromagnet/r1b/r1b.json`, `native_G12`):

| Prediction | Observed | Null | Verdict |
| --- | --- | --- | --- |
| Stance: same pair is more negative as opponents than as teammates | 18 pairs seen in both conditions; mean c = **−0.68**, negative in 16/18; hard labels −0.58 | sign flip p = 0.0002; agent-field null mean −0.006, 5th percentile −0.17, p = 0.002 | **pass** |
| Content: no within-pair contrast | bge −0.046 (19 pairs, p 0.35); gte +0.024 (p 0.59) | sign flip | **pass** |

**Native verdict: supported.** The opposition is switched on by the team assignment, not carried by the pair (family, habitual friendliness) or by agents' agreeableness, and it lives in stance only.

## Round 1b (improved data, 2026-10-04)
*Replication on corrected inputs; round-1 numbers kept above. Details and the old-vs-new table: card section "Round 1b".*

- **DQ6:** H21's labels equal the shared ground truth exactly (teams, judges, winners; phase boundaries to the second).
- **Content channel (P1–P7), every variant fails P1:** Δ̄ = +0.028 (bge, masked; p 0.34), −0.028 (gte, masked; p 0.63), −0.046 to +0.019 for unmasked, DQ5 style-residualized and deduplicated inputs; teams recovered 0–1/10. The a-priori stance-axis tilt holds in bge (σ 0.092, p 0.002, 9/10) and weakens in gte (0.055, p 0.065, 8/10); the post-verdict reversal holds (statement level 7/9 debates negative in bge, 6/9 in gte). Topic order on → off at the verdict in both models (0.42 → 0.01; gte 0.55 → 0.10).
- **Stance channel (DQ2, new):** 478 debater-to-debater replies in debate phases; soft stance +0.41 within teams vs −0.32 across ('opposes' 6% vs 36%). Δ_stance = 0.72, positive in 10/10 debates (team permutation p < 10⁻⁴); hard-label Δ 0.50 vs the calibrated agent-field null (mean 0.05, 95th percentile 0.18; p 0.002). Teams recovered exactly in **8/10** debates from the stance graph (chance 1.0, p 4×10⁻⁷). After the verdict Δ = −0.01 (switched off). AUC stance 0.75 (agent-adjusted) vs content 0.57 (bge) / 0.54 (gte).

## Scorecard (period-specific axes)
| Axis | Score | Why |
| --- | --- | --- |
| C | 1 | AF statistics fail the team-permutation and rotation nulls; only the a-priori stance axis beats its null |
| D | 0 | team recovery and the AF fluctuation signature both fail |
| E | 0 | the verdict test was untestable as registered; the post-hoc reversal contradicts "no flip" |
| G | 1 | known teams are not recovered from full vectors; the a-priori stance axis separates the known sides in 9/10 debates |

## Notes
- 2026-10-03: labels derived and verified; masked embeddings built (bge-small, CPU; CPU-vs-stored cosine 1.0000).
- 2026-10-03: real run after dated predictions. The permutation null for Δ̄ is about 2× wider than in either synthetic noise model, so power was overstated (the noise models lack family co-variation).
- Interpretation of the post-verdict reversal: agents' reflections *claim* to have been persuaded by the other side; the embedding measurement agrees in direction. Narration is not ground truth.
