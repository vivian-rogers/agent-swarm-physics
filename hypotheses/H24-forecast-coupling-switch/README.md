# H24: In the forecast week (#21), switching from independent drafts to comparison switches the coupling on

**Status:** exploratory round 1 done (2026-10-03). The literal H24 (an alignment step at switch-on) **failed** in G21. The reformulated H24′ is mixed: a coupling ramp over the week (descriptive, confounded), and numeric herding that does not survive an extraction audit. **Round 1b (improved data, 2026-10-04): the literal H24 still fails in all 13 input configurations, but the reason is model-dependent** (no step under bge; under gte a +0.16 step that ordinary kickoff days match). Natives: reading a teammate's document pulls the reader's statements toward that teammate by ~0.03 (supported in both models, weaker after style residualization); in #41 one kickoff split into two rooms yields no room gap among independent first statements and a gap that grows over the week (mixed). Confirmatory #14 written, not run.
**Fields:** stat mech, info theory
**Origin:** HH28 (`../hypohypotheses/HYPOHYPOTHESES.md`; `../promotion-shortlist.md`)
**Definitions used:** agent; regime (all of #21 is regime I, one room); driving / external field (the goal + kickoff direction ĝ); agent state, variant *vector (for model 11)* (whitened, unit-normalized bge-small statement embeddings, regime-I basis, n = 32); interaction (broadcast: everyone is in #general); goal period as the unit of analysis, split at the switch-on and at the 12-04 step changes. Proposed new named variant: **coupling switch-on (document access)**, see "Switch-on" below and the suggested DEFINITIONS.md entry in Notes.

## Question
In #21 the agents forecast AI abilities and effects. If they first drafted independently and then compared, the coupling was effectively switched on mid-week. Do their forecasts (as vectors in content space, and as numeric forecasts where extractable) show low alignment during drafting and a jump in alignment, with shrinking variance (herding), once comparison starts? Is the crowd's diversity lost faster than independent updating would predict? Practical payoff: forecast aggregation in swarms, wisdom of crowds vs herding.

## Model
**From:** `physics-models/11-vector-spins` (O(n) and soft-spin Gaussian versions: alignment jump at coupling switch-on; mean-field βJ₀ before vs after), `01-inverse-ising` (Curie–Weiss analogue for numeric forecasts as soft spins).
- **Content (O(n), n = 32):** each agent's statements are noisy draws around a unit state s_i(t). Before switch-on, s_i = unit(h ĝ + h_i + noise) (common field plus agent fields, no coupling). After switch-on, a mean-field coupling term J₀ m₋ᵢ is added. Prediction of the model: the residual (field-removed) pairwise alignment A_res steps up at τ_i, and the snapshot mean-field coupling βJ₀/n = 1 − 1/(1 + (N − 1)A_res) rises from ≈ 0.
- **Numeric forecasts (soft spins, Curie–Weiss / DeGroot):** x_i(t) ∈ [0, 100] for a shared question. Independent updating: Δx_i independent of the others' positions. Coupled (herding): Δx_i = κ (x̄₋ᵢ − x_i) + noise with κ > 0, so cross-agent variance shrinks faster than independent updating allows. κ is the numeric analogue of βJ₀.

## Data scheme (`scheme/`)
- **Inputs:** shared `embeddings/statements.parquet` + `chat_bge_small.npy` / `intentions_bge_small.npy`, `whitening_I.npz` (`common.load_whitener`), `chat_core` + `chat_text`, `intentions` + `intentions_text`, `exposure`, `calendar`, `roster`; raw `computer_use_turns` and `computer_use_sessions` (for the #21 typed text, bash heredocs and the models' contemporaneous reasoning), raw `village_goals`.
- **Transform:**
  1. `scheme/extract_cu_text.py`: one sequential pass over raw `computer_use_turns` (24 s; 2 processes), keeping the 15,781 #21 turns: typed text, bash commands, the model's own reasoning text (truncated), tool-output head. Text sidecar, gitignored.
  2. `scheme/build.py` (rules in `scheme/h24lib.py`): switch-on times per agent (rule below); #21 statements with flags (forecast-bearing, names another agent, number of percentages) and whitened 64-d coordinates (first 32 = primary); 1,889 document chunks (~1,000 chars of typed text or heredoc content, the agents' own forecast documents and matrices) embedded with bge-small (CPU, 2 threads) and whitened in the same basis; numeric anchor forecasts extracted by rule with an attribution label; ĝ = unit(unit(W·goal) + unit(W·kickoff)), kickoff = the operator's ≥ 250-char message within 45 min of the first window, sentences about the previous goal removed (H01/H10 rule).
- **Output:** `data/processed/H24-forecast-coupling-switch/G21/`: `switch_on.parquet`, `statements.parquet` + `stmt_w64.npy`, `docs.parquet` + `docs_w64.npy`, `numeric.parquet`, `goal_vec.npz`, `cu_turns_text.parquet` (text sidecar), analysis outputs (`*.json`); `_provenance.json` at the folder root. No agent text leaves `data/`.
- **Regimes covered:** regime I only (#21; placebo weeks are other non-holdout regime-I periods).

## Candidate goal periods
G21 (2025-12-01 → 12-05; not held out). Held-out analogue for confirmation: **#14** (personality tests, regime I, mode I, held out), the only held-out period whose catalogued setup has an individual-measurement-then-compare structure; see "Confirmatory" below. No held-out period is a forecasting week.

## Links to other hypotheses
H01 (#21 descriptive in P4; H01 reports a fluctuation-based βJ₀/n = 0.86 ± 0.05 for #21 as a whole, an upper bound inflated by common day-varying fields; not recomputed here), H10 (field response), H12 (dimensional collapse at consensus).

## Switch-on (structural; determined from the record 2026-10-03 before any outcome)
**Rule** (`scheme/h24lib.py`, applied by `scheme/build.py`; identical in the confirmatory script):
- τ_intent = start of the agent's first computer session whose self-written intention has a non-negated clause planning to read, review or compare teammates' work (a clause that defers reading until later is negated; outgoing sharing doesn't count).
- τ_record = first computer-use turn whose reasoning names another present agent in a sentence with a document word and an access verb (outgoing-share sentences and prior-week artifacts excluded). This is the model's description of its own screenshot, contemporaneous with the action, so it is better evidence than chat narration, but still a claim.
- τ_i = τ_intent if a record event follows within 60 min; otherwise the first record event after τ_intent; otherwise none.

**What the record shows (#21):**

| Agent | τ_i (UTC, 12-01) | min after window open | record confirmation | role |
| --- | --- | --- | --- | --- |
| Claude Opus 4.5 | 18:43:19 | 42 | +1.6 min (opens a teammate's calibration doc from mail) | switched |
| Claude Haiku 4.5 | 18:44:10 | 43 | +1.5 min (searches mail for a teammate's forecast doc) | switched |
| Gemini 3 Pro | 18:51:22 | 50 | +36.5 min (empty reasoning; typed a mail search for forecasts at 18:55) | switched |
| Claude Sonnet 4.5 | 18:51:36 | 50 | +4.2 min | switched |
| GPT-5.1 | 18:52:53 | 51 | +4.2 min (a teammate's calibration doc on screen) | switched |
| Claude 3.7 Sonnet | 18:57:31 | 56 | +8.8 min | switched |
| Gemini 2.5 Pro | 19:27:06 | 86 | +2.5 min | switched |
| GPT-5 | (12-05 19:33) | — | none through 12-04: shares its own doc outward, never reads others' | **document-uncoupled control** |
| DeepSeek-V3.2 | joins 12-04 | — | reads teammates' material from its first session | late joiner (coupled from arrival) |

- **Swarm switch-on τ\* = median τ_i = 18:51:36 UTC on day 1, 50 min after the window opened.** The spread is 42 → 86 min. The independent phase is ≈ 4% of the week's ≈ 20 active hours.
- **The chat channel was never off.** Numeric forecasts appear in #general from 18:21 (one agent's headline numbers). Every switched agent was exposed to at least one other agent's numeric chat message (from `exposure`) 18:16–18:29, before its τ_i. But before the 2025-12-20 scaffold fix ("chat interleaved into computer-use context"), chat reached an agent only between computer sessions, and the first drafts were written inside the first sessions. So the drafts were mostly but not strictly independent.
- **The addressed channel switches on at τ_i** (from `chat_mentions_clean`, `mentions_roster`): 7% of the switched agents' day-1 messages name another agent before their τ_i, 74% in the hour after. This confirms the switch from the record; it is not an alignment outcome.
- **The kickoff asked for it.** The operator's kickoff told agents to form their own views before discussing or reading others' forecasts, to avoid groupthink. In their first messages, agents announced a three-phase plan (independent drafting, then external calibration, then team comparison) and then compressed it into the first hour.
- **After the switch the coupling ramps rather than steps** (from intentions and typed documents; descriptive):
  - day 1: pairwise reading and "divergence matrices";
  - day 2: a shared cross-framework template, where agents weight each other's frameworks;
  - day 4: a common seven-question schema and a shared tracker sheet; DeepSeek joins and builds its forecasts as weighted averages across the team's frameworks;
  - day 5: CSV submissions into the shared tracker.
- **Consequence for H24.** The card's premise of a *mid-week* switch is wrong. There is a clean, early, staggered switch-on (a ~45-min stagger, 42–86 min into the week) layered on a chat channel that was always on, then a ramp. H24 is tested as stated, as a day-1 event study around each agent's τ_i (with very little pre-switch data), and reformulated as **H24′: a coupling ramp** across the week.
- **Units (goal period split at step changes):** G21a = each agent's [window open, τ_i) on 12-01 (independent drafting); G21b = [τ_i, end of 12-03] (comparison); G21c = 12-04 → 12-05 (DeepSeek joins; "don't do nothing" prompt change; shared tracker). One folder, `G21/`.

## Observables
*Specified 2026-10-03, before any real-data alignment, dispersion or coupling statistic.* Content vectors are whitened (regime-I basis, n = 32) bge-small statement embeddings, each unit-normalized. "Residual" = with the ĝ direction projected out of every statement before averaging. Agents for O1–O3: the 7 switched agents (GPT-5 is the control, DeepSeek absent on day 1).

- **O1. Alignment step at switch-on (literal H24; day-1 event study).** Per agent, pre = [open, τ_i), post = [τ_i, τ_i + 60 min).
  - **Rarefied agent vectors:** the normalized mean of k randomly drawn statements per agent and segment, so that counts don't drive the result. Averaged over 200 draws.
  - **Statistics:** A = mean pairwise cosine of agent vectors; polarization |m| = |mean_i v_i|; ΔA = A_post − A_pre, Δ|m|.
  - **Instruments:**
    - (a) all statements (chat + intentions), k = 4;
    - (b) forecast-bearing statements, k = 4;
    - (c) document chunks, k = 5, with post = [τ_i, end of 12-01] (documents are sparser), split into *own* chunks (naming no other agent) and *all* chunks.

    Each instrument is computed raw and residual. **Primary: (a) residual ΔA_res.**
- **O2. Snapshot mean-field coupling:** βJ₀/n = 1 − 1/(1 + (N − 1)A_res), pre vs post, from O1's residual A (mean-field O(n) linear response, field removed). Bootstrap over rarefaction draws and statements.
- **O3. Coupling ramp (H24′, descriptive + trend):** A_res per active-day half (2 h blocks) over the week, k = 4, agents with ≥ 4 statements in the block. Trend = Spearman ρ of A_res vs block index over G21b–c; step at 12-04 = mean A_res(G21c) − mean A_res(G21b).
- **O4. Numeric herding (coupled phase).** Shared anchor questions q ∈ {AGI by 2035, superintelligence by 2050, p(doom) by 2100}. Only self-attributed values count (the rule in `h24lib.extract_numbers`: no other agent, aggregate, external forecaster, conditional or update marker in the sentence; first-person if the message names other agents). The four other tracker questions are descriptive.
  - **First and last value:** x_i,first and x_i,last are each agent's first and last self-attributed value in the period.
  - **Dispersion change:** ΔSD_q = SD_i(x_last) − SD_i(x_first) over agents with both.
  - **DeGroot pull:** κ = −slope of Δ_i = x_last − x_first on d_i = x_first,i − mean_{j≠i} x_first,j, with question fixed effects, pooled over anchors.
  - **Time-resolved dispersion:** S_q(t) of each agent's latest value.
  - *Count fact fixed before the test:* only 2 agents have a self-attributed anchor value before their τ_i, so O4 measures herding **during the coupled phase**, not across the switch.
- **O5. Crowd error vs diversity:** not testable. No forecast had resolved inside the data (the export ends 2026-09-20 and has no resolution data), and fetching outcomes needs the network. Stated, not attempted.
- **O6. Control contrast (descriptive, N = 1).** DiD around τ\* = (ΔA_res among switched pairs) − (ΔA_res for GPT-5–switched pairs); GPT-5's segments use τ\* as a pseudo-switch.

## Null / baseline
*Specified 2026-10-03, before any real-data run.*
- **N1, within-period placebo switch:**
  - the same per-agent offsets (τ_i − open) applied on 12-02 and 12-03, where nothing switches (and on 12-04/12-05 for the agents present);
  - τ_i + 60, + 90 and + 120 min on day 1 (inside the coupled phase).

  This gives the null distribution of ΔA under "no switch".
- **N2, kickoff-matched placebo across periods:** every non-holdout regime-I goal period except #21 with ≥ 4 agents active on its first day. τ = open + 50 min for every agent (#21's median offset), same statistic. It tests whether #21's day-1 change exceeds generic kickoff-day dynamics: agents everywhere start reading each other after the first hour, and the kickoff field decays.
- **N3, per-agent random rotation** (Haar O(32), one rotation per agent applied to both segments). It destroys cross-agent alignment and keeps each agent's own trajectory. Null for the levels A_pre and A_post.
- **N4, independent updating (numeric):**
  - permute Δ_i across agents within a question (keeps the update distribution, destroys any dependence on position; 10,000 draws);
  - a parametric version with Δ_i ~ N(0, σ̂²).

  Null distributions for ΔSD and κ.
- **Strongest rival: a decaying common field.** The kickoff makes everyone paraphrase the same instructions in the first hour, which raises raw pre-switch alignment. The field model with zero coupling predicts ΔA_raw ≤ 0 and ΔA_res ≈ 0. N2 is the test against it.

## Faithfulness scorecard
Scored per model, mapping and window; 0 = not done or failed, 1 = partial, 2 = passed. Scheme and promotion thresholds: `writeup/paper.tex`, Sec. "Assessing model faithfulness".
**Rival models:** decaying common field with no coupling (kickoff transient); agent fields only (independent agents); divergence-seeking (anti-coupling: comparison makes agents differentiate, κ < 0).
**Locked holdout used for confirmation:** none yet. Planned: #14 (`analysis/confirm.py`, written and dry-run on #21, not run on #14).

| Axis | Test | Score | Evidence |
| --- | --- | --- | --- |
| A mapping | variables defined from dataset fields; assumptions listed; invariant across families and regimes | 1 | Every variable is defined from fields: the switch-on rule from intentions and the models' own reasoning; content from whitened embeddings; numbers from chat and typed documents. Assumptions listed. Not checked for invariance across model families (style); numeric attribution needed a hand audit. |
| B assumptions | stationarity, Markov order, time-rescaling, update-order audit | 0 | Not tested. The kickoff transient (non-stationarity in the pre window) is handled by the N2 placebo, not modelled. |
| C adequacy | beats the null hierarchy, day-blocked held-out data | 1 | The alignment *levels* beat the per-agent rotation null (A_res ≈ 0.33 vs q95 ≈ 0.03). The predicted *step* does not beat the within-period (N1) or kickoff-matched (N2) placebos. |
| D unfitted predictions | unfitted statistics and the model's signature | 1 | Round 1b: the pair-level reading DiD (an unfitted prediction) holds in both models (+0.036, p 0.035 / +0.030, p 0.038), weaker after style residualization. Round 1: the signature (a step at τ_i, a rise in snapshot βJ₀/n) is absent. Numeric herding vanishes after the audit. |
| E interventional | predicts the change across a natural experiment | 1 | Round 1b: dated reading events (who opened whose document) are directed natural experiments and the reader's content follows the owner's. Round 1: the swarm-level switch-on is a dated, record-confirmed natural experiment, and its predicted alignment change is absent. |
| F identifiability | synthetic recovery with village sampling; robust to preprocessing | 1 | Synthetic world with #21's real statement times and τ_i:<br>• rule size 0.07–0.08;<br>• power 0.38–0.59 at βJ₀/n ≈ 0.35 and 0.71–0.77 at ≈ 0.55;<br>• the snapshot βJ₀ is inflated by field leakage (0.34 at zero coupling);<br>• κ is inflated by extraction noise (size 0.32), which the audit then found in practice.<br>Robust to k; not to dimension (n = 64 gives a step) or the ĝ definition. No embedding-model swap. |
| G ground truth | agrees with known structure | 1 | The switch-on times agree across three channels (intentions, screen descriptions, mention share 7% → 74%). The GPT-5 document control (N = 1, 4 post statements) did not behave as predicted. |
| H comparative | beats the named rivals | 0 | The rival (a decaying common field with no coupling step) explains day 1 as well or better: raw ΔA < 0 as on generic kickoff days, residual ΔA ≈ 0. Divergence-seeking (κ < 0) is not supported either. |
| I transfer | holds in other same-mode periods, including the holdout | 0 | #14 confirmatory script written; not run. |

## Prediction
*Written 2026-10-03, before running the analysis on real data.*

**What I had seen when writing this.**
- The structural audit above: intentions, the models' reasoning around each τ_i, chat keyword timelines and doc links.
- While reading chat to find the switch, raw snippets containing some agents' headline numbers (AGI-by-2035 values for about six agents at various times, a few p(doom) and superintelligence values). So **P4 is not blind**: the snippets suggested mild compression toward 45–50% on AGI-2035, with one low outlier.
- Counts: day-1 pre-switch statements per agent (7–29), post-60-min (10–18), doc chunks per segment, numbers of self-attributed values per question and segment. One nuisance instrument statistic for the synthetic: the within-agent, same-window statement cosine ≈ 0.50.
- H01's G21 card (polarization along ĝ 0.27; fluctuation βJ₀/n 0.86).
- I had computed no cross-agent alignment, polarization, dispersion, κ or βJ₀ on #21 or any placebo week.

**Predictions** (credences in brackets):
- **P1 (primary, literal H24).** Residual alignment steps up at switch-on: ΔA_res(a) > 0 *and* above the 90th percentile of both placebo distributions N1 and N2. [0.30]
  - Why low: the pre window is tiny; after switching, agents write about *divergences*, as the operator's anti-groupthink instruction asked; and the synthetic (below) sets the power.
  - Raw alignment: I expect ΔA_raw ≤ 0, because the kickoff paraphrase field makes the first hour similar. [0.55]
- **P2 (documents).**
  - All doc chunks: ΔA_res > 0 [0.6]. Divergence matrices copy others' content, a mechanical coupling.
  - Own-forecast chunks only: ΔA_res > 0 [0.4].
- **P3 (mean-field).** βJ₀/n (snapshot, residual) rises from pre to post [0.4]. The post value is subcritical (< 0.5) [0.7].
- **P4 (numeric herding, not blind).** κ > 0 with permutation p < 0.10 *and* ΔSD < 0 in ≥ 2 of 3 anchors. [0.5]
  - Supporting it: shared templates and weighted averaging.
  - Against it: the operator's anti-groupthink instruction, and agents framing their work as divergence analysis.
- **P5 (control, descriptive).** The DiD in O6 is > 0 (switched pairs gain more alignment than GPT-5 pairs). [0.5]
- **P6 (ramp, descriptive).** A_res trends up over G21b–c (ρ > 0), with a positive step at 12-04. [0.45]

**Verdict rules (round 1).**
- **H24 (literal) supported:** P1 passes and synthetic power at the plausible coupling is ≥ 0.5.
- **H24 failed:** ΔA_res ≤ the N1 or N2 median while synthetic power ≥ 0.5.
- **Inconclusive:** power < 0.5, whatever the sign.
- **H24′ (ramp/herding) supported:** P4 passes and P6 has ρ > 0.
- **Counts against both:**
  - ΔA_res within the placebo bulk;
  - numeric dispersion not shrinking, or κ ≤ 0 (divergence-seeking);
  - a βJ₀/n that doesn't rise.

## Confirmatory (written, not run)
`analysis/confirm.py` targets **#14** (personality tests; regime I, mode I, held out). It runs the identical automated pipeline with no hand audit: extraction → switch-on rule → statements → C0–C3. Without `--confirm --i-understand-this-uses-the-locked-holdout` it refuses, and `--dry-run` refuses held-out periods. A dry run on #21 reproduces round 1 (C0 pass, C1 ΔA_res +0.010 fail, C2 pass, C3 ρ 0.70).

*Predictions written 2026-10-03, after round 1 on #21 and before any look at #14:*
- **C0:** a switch-on exists by the rule on day 1 for ≥ 4 agents (≥ 2/3 of those present). [0.5] If it fails, H24 doesn't apply to #14.
- **C1:** the H24 step, ΔA_res > q90 of N1 and of N2. H24 predicts a pass; my credence in a pass is 0.2.
- **C2:** pre-switch residual alignment > q95 of the rotation null. [0.85]
- **C3:** a ramp, ρ > 0 over 2-h blocks. [0.55]

**Power note:** #14 has N = 6. In the #21 synthetic, power ≥ 0.5 needs a post-switch βJ₀/n ≳ 0.45, so a C1 failure would be weak evidence. No held-out period is a forecasting week, so there is no direct numeric-herding confirmation.

**Strongest non-holdout transfer test (proposed, round 2):** a pair-level reading DiD inside #21 and other regime-I weeks. The record says *whose* document each agent opened (τ_record names the owner). Test whether i's residual alignment with j rises after i reads j's document, relative to pairs that didn't read each other at the same time. This is a directed, pair-level intervention, much stronger than a swarm-level step.

## Results by goal period
| Period | Role | Verdict | Key numbers |
| --- | --- | --- | --- |
| [G21](goalperiod-subhypotheses/G21/README.md) | exploratory | failed (literal H24); ramp descriptive | τ\* = 50 min after open. ΔA_res at τ_i +0.010 [−0.047, +0.086] vs placebo q90 0.12 / 0.11. A_res ≈ 0.33 before and after (rotation q95 ≈ 0.03). Snapshot βJ₀/n 0.67 → 0.67. Documents +0.128 [+0.06, +0.18]. Ramp ρ = 0.73. Hand-verified κ = 0.25 (p = 0.17). |
| [G21](goalperiod-subhypotheses/G21/README.md) round 1b | replication + native (1b) | mixed | ΔA_res at τᵢ −0.011 (bge) / +0.160 (gte) vs N2 q90 0.10 / 0.18: P1 fails in all 13 configs; pair-level reading DiD +0.036 (p 0.035) / +0.030 (p 0.038), style-resid p 0.14 / 0.08 |
| [G41](goalperiod-subhypotheses/G41/README.md) (one kickoff, two rooms) | native (1b) | mixed | independent drafts ΔW −0.09 / −0.08 (n.s.); day-1 blocks up to +0.32 / +0.40; by day 4 cross-room alignment ≈ 0, ΔW +0.25 / +0.32 |

## Results
**Exploratory round 1 (2026-10-03; G21 only, non-holdout; holdout asserted absent in every script).**
- Code: `scheme/{extract_cu_text,build,build_placebo,numeric_audit,h24lib}.py`, `analysis/{synthetic,explore,figures,confirm,h24stats}.py`.
- Numbers: `data/processed/H24-forecast-coupling-switch/G21/{explore,synthetic_validation}.json`.
- Figures: `figures/summary.pdf` (one-page overview), `figures/summary_obs.pdf`, `figures/synthetic_validation.pdf`, `G21/figures/G21_panels.pdf`.

**Headline.** The forecast week had a real, record-confirmed coupling switch-on, but it came 50 min into the week, not mid-week. At the switch the *addressed* channel jumps: the share of messages naming a teammate goes 7% → 74%. Content alignment does not step up.
- **No step:** residual alignment changes by +0.010 [−0.047, +0.086], inside both the within-week placebo distribution and the distribution of 23 other regime-I kickoff days. The synthetic gives this test ~0.7 power for a post-switch βJ₀/n ≈ 0.55, so a moderate coupling step would likely have been seen. A small one (βJ₀/n ≲ 0.35) would not.
- **Aligned from the first hour:** agents' content is strongly aligned before anyone reads anyone's document (A_res ≈ 0.33 against a rotation null ≈ 0.03; snapshot βJ₀/n ≈ 0.67). The kickoff field, which ĝ captures only along one direction, or the always-on chat channel, does the aligning.
- **What rises:** document content (+0.13, partly because divergence matrices transcribe teammates' numbers), and alignment over the week (ρ = 0.73; +0.09 at 12-04). Both are confounded: the 12-04 step coincides with DeepSeek joining, a prompt change and the shared tracker.
- **Numeric herding is an extraction artifact.** As pre-registered, it passes strongly: κ = 0.70, p = 0.0002, and the AGI-2035 and p(doom) spreads shrink 2–3×. A hand audit shows the pass comes from mis-extracted "first" values (thresholds, complements, worked examples, scenario-conditional numbers, others' numbers). With hand-verified values, κ = 0.25 (p = 0.17), AGI-2035 SD 6.7 → 5.5, p(doom) 6.7 → 6.5, and the superintelligence-2050 spread *grows* (11.7 → 15.8).
- **What coupling there is looks pairwise and literal** (post hoc): exact non-round values copied from one agent into another's forecasts, including a final tracker submission that reuses another agent's two-decimal numbers.
- **Mode, regime, rooms:** one period (regime I, mode I, one room), so no heterogeneity can be assessed. This week was unusual: the operator explicitly asked for independence, and agents framed comparison as "divergence analysis".

**Outcome vs prediction (G21):**

| | Prediction [credence] | Observed (90% CI) | Verdict |
| --- | --- | --- | --- |
| P1 | ΔA_res > q90 of N1 and N2 [0.30]; ΔA_raw ≤ 0 [0.55] | +0.010 [−0.047, +0.086] vs q90 0.122 / 0.112; raw −0.151 [−0.208, −0.080] | **failed**; raw as predicted (but generic) |
| P2 | documents ΔA_res > 0: all [0.6], own [0.4] | all +0.128 [+0.060, +0.175]; own +0.049 [−0.097, +0.104] | supported (all); weak (own) |
| P3 | βJ₀/n rises [0.4]; post < 0.5 [0.7] | 0.67 → 0.67, Δ [−0.03, +0.06] | **failed** (upper bound) |
| P4 | κ > 0 at p < 0.10 and SD shrinks in ≥ 2/3 [0.5, not blind] | pre-registered extractor: κ 0.70, p 0.0002, 2/3 shrink; hand-verified: κ 0.25, p 0.17, SI spread grows | **failed after audit** (the pre-registered pass is an artifact) |
| P5 | GPT-5 control DiD > 0 [0.5] | −0.137 | failed (N = 1) |
| P6 | ramp ρ > 0, 12-04 step > 0 [0.45] | ρ 0.73 (p 0.025), step +0.091 | supported (descriptive, confounded) |

**Verdict rules applied:**
- **H24 (literal) failed:** ΔA_res is below the N1 median (+0.029). The synthetic power is ≥ 0.5 for a true post-switch βJ₀/n ≳ 0.45 with the kickoff transient (≳ 0.33 without), so the failure holds conditional on a moderate step.
- **H24′ is not supported:** P4 fails after the audit; P6 passes.

**Amendments (all dated 2026-10-03):**
- **A0 (before any outcome):** the switch-on is on day 1, so H24′ (ramp) was added and units G21a/b/c defined. Written in the Switch-on and Prediction sections before analysis.
- **A1 (after the first real-data run):** an amended numeric extractor (short agent names; threshold, complement, example and conditional markers), reported alongside the pre-registered one.
- **A2 (after the first run):** hand-verified first/last anchor values (`scheme/numeric_audit.py`, pointers only; reasons paraphrased there). These are the basis for interpretation; the P4 verdict is "failed after audit".
- **Bug fix (after the first run):** the per-agent rotation null reused 8 matrices across agents. Fixed (a fresh rotation per agent). It affected only the N3 bands; no verdict changed.
- **Correction:** τ\* was first written as 18:52:53 (51 min). The median of the seven τ_i is 18:51:36 (50.2 min); N2 used 50.2 min.

**Caveats:**
- **The switch-on rests on agents' own words.** It uses self-written intentions and the models' descriptions of their own screens (claims), cross-checked against mentions. The GPT-5 "control" rests on the absence of such descriptions.
- **Power:** one week, N = 7 switched agents, a ~50-min pre window (4–14 statements per agent after rarefaction constraints).
- **Field removal is one-dimensional.** ĝ is one direction of a multi-dimensional goal field. Residual alignment and the snapshot βJ₀/n are upper bounds on coupling (the synthetic shows leakage), and the step is instrument-sensitive: n = 64 gives +0.08, a goal-text-only ĝ gives −0.10.
- **Post-switch chat is coordination talk** (phase plans, matrices): topic coupling rather than forecast alignment. The forecast-bearing subset gives the same null.
- **Document alignment rises partly mechanically,** because matrices copy others' numbers.
- **Numeric extraction is fragile.** The hand-verified set is post hoc and small (20 units; several agents first state a value on 12-04).
- **No crowd-error test:** no forecast resolves inside the data, and fetching outcomes needs the network.
- **N2 weeks differ** in N, kickoff style and mode. Only the offset is matched.
- **The 12-04 step is confounded** with DeepSeek joining, the "don't do nothing" prompt change and the shared tracker.

**Next steps:**
1. The pair-level reading DiD (above). τ_record already names whose document was opened.
2. Multi-dimensional field removal (project out the top principal directions of the goal period's first-hour mean, or of the kickoff paragraphs), plus an embedding-model swap.
3. A second labeler (Jev or a blind Claude pass) for numeric values, so the audit isn't a single hand.
4. Copy fidelity of forecasts with model 08 (exact-value adoption, typed transcriptions).
5. #14 confirmatory after sign-off.

## Notes
- 2026-10-03: promoted from HH28.
- 2026-10-03: switch-on audit done before any outcome. The switch is on day 1 (τ\* = 50 min after open), not mid-week. Card reformulated (H24′ ramp) before analysis.
- 2026-10-03: round 1 done (see Results). Disk: 7.9 MB in `data/processed/H24-forecast-coupling-switch/`.
- Suggested DEFINITIONS.md variant (not added; outside this card's edit scope): **coupling switch-on (document access)**. τ_i = the start of the agent's first session whose self-written intention plans to read or compare teammates' work, confirmed within 60 min by a reasoning sentence describing another agent's document on screen (`scheme/h24lib.py`).
- 2026-10-04: round 1b (re-evaluation agent RE-C1): 13 input configurations, natives G21 (pair-level reading DiD) and G41 (one kickoff, two rooms), per-period estimates; literal H24 still failed; scorecard D and E 0 → 1 from the pair-level native.

## Round 1b (improved data, 2026-10-04)
*Re-evaluation wave, two-layer design (`infra/data-quality/QUEUE.md`): the round-1 statistics rerun on corrected inputs (replication), plus two native tests with predictions dated in their folders before running. Holdout untouched (`confirm.py`, #14, not run).*

**What changed.**
- **Goal vectors:** H24 did not read H01's file; it embedded its own goal + kickoff. Against the shared goal fields its #21 ĝ has cos 0.96 (goal part 1.00, kickoff part 0.88: a different boilerplate filter and a one-string embedding truncated at 256 tokens, vs the shared mean of chunk embeddings); the 23 N2 placebo weeks' ĝ have cos 0.78–1.00. Round 1b uses the shared vectors for #21 and all placebo weeks.
- **Multi-direction field** (vector-spins pitfall: one-direction removal leaks field into "coupling"): ĝ plus every goal-text and kickoff chunk direction (7 directions for #21, 3 for #41), both models.
- **Second model:** gte-modernbert for statements (shared) and for the 1,889 document chunks (re-embedded from the sidecar; the re-chunking reproduces round 1 exactly).
- **Dedupe:** #21 is unusually repetitive (DQ5 flags: 28% self-repeats, 9% cross-agent echoes under bge); variants drop restatements (either model) and, additionally, cross-agent echoes. **Style:** within-period style-residualized statement vectors (family style can align agents).
- **Activity:** H24 never used `activity_bins` (its switch-on comes from intentions and the models' screen descriptions), so the event-drop fix does not touch it.
- Code: `scheme/build_r1b.py`, `scheme/build_r1b_g41.py`; `analysis/explore.py --emb --goals --field --dedupe --style` (defaults reproduce round 1; round-1b outputs `G21/r1b/explore_<config>.json`); `analysis/r1b_report.py`, `natives_r1b.py`, `r1b_figures.py`, `r1b_estimates.py`.

**Replication, old vs new** (13 configurations; full table in [`G21`](goalperiod-subhypotheses/G21/README.md)):

| Prediction | Round 1 (bge, H24 ĝ) | 1b bge-small (shared ĝ) | 1b gte-modernbert | range over dedupe / style / multi-field | Verdict 1b |
| --- | --- | --- | --- | --- | --- |
| P1 ΔA_res > q90 of N1 and N2 | +0.010 vs 0.122 / 0.112 | −0.011 vs 0.110 / 0.100 | +0.160 [+0.10, +0.24] vs 0.107 / 0.180 | bge −0.01 to +0.09; gte +0.15 to +0.18 (N2 q90 0.17–0.20) | **failed** in all 13 |
| P2 documents ΔA_res > 0 | +0.128 | +0.164 [+0.10, +0.21] | +0.075 [+0.02, +0.13] | bge +0.16 to +0.18; gte +0.07 to +0.09 | supported (both) |
| P3 βJ₀/n rises | 0.67 → 0.67 | 0.69 → 0.68 | 0.69 → 0.76 (Δ CI [+0.05, +0.13]) | | model-dependent (upper bound) |
| P6 ramp ρ > 0 | 0.73 (p 0.025) | 0.47 (p 0.21) | 0.60 (p 0.09) | 0.50–0.75 | holds in sign, significance model-dependent |
| levels A_pre vs rotation q95 | 0.33 vs 0.03 | 0.36 vs 0.02 | 0.38 vs 0.07 | 0.34–0.42 vs 0.02–0.10 | robust |

- **The verdict stands, the reason shifts.** Under bge there is no step at the switch-on; under gte residual alignment does step up by 0.16, but the 23 kickoff-matched placebo days show steps as large under gte too (q90 0.18). So "no coupling step beyond generic kickoff-day dynamics" is model-robust, while "no step at all" was a bge-specific statement.
- Removing the field along 7 directions instead of 1 leaves residual alignment at the same level (0.38–0.42): the first-hour alignment is not carried by the kickoff text's own directions, so either it is a shared prior or the always-on chat channel.
- Dedupe (dropping a third of #21's statements) and style residualization change no verdict.
- P4 numeric herding does not depend on embeddings: failed after audit, as in round 1.

**Native layer** (new in 1b):

| Native test | Design | bge-small | gte-modernbert | Verdict |
| --- | --- | --- | --- | --- |
| [G21](goalperiod-subhypotheses/G21/README.md) pair-level reading DiD | does i's content move toward j's after i reads j's document, vs agents i did not read (102 events; owner-permutation null) | statements +0.036 (p 0.035); documents +0.016 (p 0.26) | +0.030 (p 0.038); +0.004 (p 0.43) | supported (statements; style-resid p 0.08–0.14) |
| [G41](goalperiod-subhypotheses/G41/README.md) one kickoff, two rooms | within- minus cross-room alignment by block and day; independent first statements via the context ledger; room-permutation null | drafts −0.09 (n.s.); block 1 +0.11 (p 0.04); days +0.10 → +0.25; day 2 just below q95 | drafts −0.08; block 1 +0.07 (n.s.); day-1 trend ρ 0.79; days +0.14 → +0.32 | mixed |

- **What the natives add.** Coupling exists but it is pairwise and gated by reading: after an agent opens a teammate's document, its next hour of statements moves toward that teammate by ~0.03 in cosine, relative to teammates it did not read. That is small enough to vanish in a swarm-level alignment statistic, which is why the literal H24 fails. In #41 a single kickoff produced two room cultures: no gap in the first independent statements, then a within-room / cross-room gap that grows over days until the rooms share nothing (cross-room alignment ≈ 0 by day 3–4), robust to style. That is the field-vs-coupling separation the card asked for, read in favor of room-local coupling, but the earliest window cannot separate fast coupling from room composition (everyone reads their room-mates within a minute).

**Scorecard after 1b:** A 1 (unchanged; embedding swap and style residualization done, the step statistic is model-dependent); C 1 (levels beat the rotation null in every configuration; the step still does not beat N2); D 0 → 1 (an unfitted pair-level prediction, reading pulls the reader toward the owner, holds in both models; weakened by style); E 0 → 1 (the reading event is a dated, directed natural experiment and the pair-level effect follows it); G 1; H 0 (the decaying-field rival still explains the swarm-level day 1); I 0. Ratings (suggested): complete 40 → 50, faithfulness 1.0 → 1.5, usefulness 1.5 (unchanged).

**Per-period estimates:** 22 rows via `write_estimates` (switch-on step, pre-switch level, document step, ramp ρ, pair DiD for statements and documents in G21; daily room gap ΔW in G41; channels `content_bge_small` / `content_gte_modernbert`).

## Round 2 redirects (2026-10-04)
*From the round-1 reflection (`writeup/round1-reflection/round1-reflection.pdf`).*
- **Where round 1 went sideways:** The alignment-step test missed the real story, which is pairwise copying.
- **What the direction is really after:** Information aggregation in swarms is copying from the first or most confident agent, not averaging.
- **H24-R1.** Anchoring cascade: first-posted numbers dominate the final consensus (a founder effect) in every estimation-like task.
- **H24-R2.** Copy fidelity vs transformation of shared numbers (H07 machinery).
