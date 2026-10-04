# H56: Entropy production fingerprints the platform

**Status:** exploratory round 1 done (2026-10-04; non-holdout only; predictions and nulls written before any real-data entropy-production (EP) number). **Refuted as posed.** Promoted 2026-10-04 from HH175 (approved by Vivian).
- *Refuted:* EP does not jump at scaffold changes (32 eligible scaffold-tool and prompt events: 0 hits on the full chain, tool-class p 0.23; blind change-points 0.6× chance near scaffold events). Not even at NE14b, the biggest structural change in the logs (−28% fine, −45% coarse, t −1.3, inside the weekday spread), or at the undocumented oracle swap, dated here to 04-20 (t −0.18). Family differences in fine-action EP do not vanish without scaffold records (η² 0.34 → 0.40, p 0.0005 both).
- *Held, but non-diagnostic:* no jump at roster or room changes or at NE43. EP barely jumps at anything: within-agent 3-day EP changes are almost as stable as a stationary Markov chain (real |t| SD 1.23 vs synthetic null 1.13). Goal kickoffs move the agent-only chain more than scaffold changes do (V5 class p 0.007): rival R1, task mix, wins.
- *Side results:* NE40 is dated to 2026-04-20 by answer stylometry (shipped silently with NE18); an undocumented search-tool schema change on 07-29; NE43's bookends end 08-04, not 08-21; a post hoc lead (scaffold events move agents' EP in the same direction more often than random days, p 0.01–0.05).
- `analysis/confirm.py` is written and dry-run; **not run**.
**Fields:** stochastic thermodynamics, stat mech, info theory
**Literature:** [Aguilera, Ito & Kolchinsky 2026](../../literature/aguilera-2026-entropy-production-nonequilibrium-maxent.md) (AIK estimator; the Newton-step and exact-dual bounds used here); [Kolchinsky 2024](../../literature/kolchinsky-2024-dissipation-does-not-bound-replicator-rates.md) (dissipation is set by the mechanism of the one-way step, not by the agent; bounds are often slack).
**Definitions used** (`physics-models/DEFINITIONS.md`): Regime; Action; Agent state (categorical: action class); Population (roster); Entropy production / irreversibility, in H14's variant **"entropy production (Markov pair-KL on categorical behavior states)"** (proposed by H14, not yet in DEFINITIONS.md) and two named variants proposed here (owner to add):
- **"entropy production rate (count-matched, within-agent)"**: H14's cross-fitted Newton bound on antisymmetrized transition indicators, in nats per transition, computed on random subsamples of an agent's transitions of equal size on the two sides of a comparison (hypergeometric, stratified by day), so that the estimator's count-dependent bias and noise are the same on both sides. Daily values use a fixed n₀ = 120 transitions per agent-day, cross-fitted over four within-day quarters.
- **"agent-only chain"**: the turn-level state sequence restricted to the agent's own action choices (shell, click, scroll, look, type, chat, idle), cut (not bridged) at every scaffold or system record: consolidation, history search, session start/stop, `other` records (empty `none` responses, sign-in, outreach, human-helper and room-move requests), turns with an infrastructure `error_class` (timeout, vm, resource, network), and calls whose start the scaffold set (`call_windows.gap_kind` ∈ after_summary, marker, session_start, first_of_day). Its complement, "the scaffold component", is EP(all records) − EP(agent-only chain).

**From:** HH175 in `hypotheses/hypohypotheses/HYPOHYPOTHESES.md` · **Models:** `physics-models/02-nonequilibrium-ising/` (generalized to categorical states as in H14), `physics-models/05-replicator-dissipation/` (dissipation is a property of the one-way mechanism)
**Data inputs (shared tables first):** `states_turn` (H14's action classes), `actions_bash_head_fixed` (`error_class`; `system_class` is `none` on every row, so it cannot separate anything), `call_windows` (DQ1; `gap_kind`), `calendar`, `period_units`, `period_step_changes`, `roster`, `kicks_classified` (first nudge), `outages` (descriptive), the NE catalog, `data/raw/ai-village/CHANGELOG.md` (event dates, as ground truth), and raw `events` SEARCH_HISTORY rows for numeric answer features only (NE40 dating). H14's estimators are imported read-only (`hypotheses/H14-behavior-entropy-production/analysis/h14lib.py`, which imports H05's `ep.py`). Jev v3 behavior states: only 50 windows were labelled when round 1 started, so they are round 2.

## Standards (2026-10-04)
*Documentation pass against `STANDARDS.md`. No analysis was re-run. H56 has no round-1b section; round 1 already ran on most corrected inputs.*

**Question served:** Q6. The card asks who owns fine-action irreversibility: the platform or the agent. Q2 second: scaffold steps (field) are tested against task mix and agent traits.

| Impostor | Relevant? | How it was handled | Status |
| --- | --- | --- | --- |
| Scheduler field | yes | The scaffold is the object. The agent-only chain cuts scaffold records and scaffold-set call starts (`gap_kind`) and drops a 3-transition burn-in (Amendment 1). Weekday-matched placebos (N1) cover calendar effects (R3). | removed |
| Exogenous field (kickoff/goal/operator) | yes | Goal kickoffs are a scored class against the class-level random-date null (N2); they move the agent-only chain more than scaffold steps (R1 wins). Operator events (NE10, NE43) are their own class. | removed |
| Shared model priors | yes | Lab differences tested by a within-period label permutation (N4); they survive scaffold removal (η² 0.40, R4 wins) and are reported as an agent trait, not a coupling. | removed |
| Contemporaneous convergence | no | Within-agent irreversibility; no copying or influence claim. | n/a |

**Inputs:** round 1 uses H14's `states_turn` and `call_windows`; it never reads `activity_bins` or `stall_minutes`. Still old: chain cuts use `actions_bash_head_fixed.error_class`, not `turn_outcomes.failed`; the old `outages` table is read for description only. Jev v3 states were not yet available.

**Two layers:** 34 replication folders. Native tests: 4 (`NE14` and `NE40` failed; `G51` mixed; `NE43` descriptive).

**Confirm script:** `analysis/confirm.py` exists, dry-run only, built on `states_turn` and `call_windows`. It uses no activity table and no visibility rule, so no re-freeze is required (holdout.md item 8).

## Question
Does the entropy-production rate of agents' turn-level behavior jump at scaffold changes (prompts, tools, harness) but not at goal, roster or room changes, or at the nudger switch-off (NE43), and do family differences vanish once scaffold actions are removed? If so, EP is a log-only detector of platform changes, including undocumented ones (NE40, NE43).

## Design: two layers (Vivian, 2026-10-04; see `infra/data-quality/QUEUE.md`)
- **Layer 1, replication (role `replication`):** one event-study statistic on every eligible step change in every non-holdout goal period, classed scaffold (tool/harness, prompt, family-targeted), goal kickoff, roster, room, operator, goal-prompt, plus blind change-point detection over all non-holdout days. Per goal period, a `G<NN>/` README with the period's EP level (a phase-diagram point) and its events (templated, labelled as such).
- **Layer 2, period-native tests (role `native`):**
  - **NE14** (regime II → III, scored at 2026-03-24; the 03-11 → 03-16 rollout is held out): the one scaffold change whose effect on the chain is structurally certain; is the jump carried by scaffold transitions?
  - **NE43** (2026-08-21, nudger and daily bookends silent; undocumented): a withdrawn drive. Does EP see it, and does the idle sector (the nudger's target) change?
  - **NE40** (memory-oracle swap, undocumented and undated): date it from non-text features of the search answers, then ask whether EP sees it.
  - **G51** (07-06 → 09-04 non-holdout): nine weeks with roster joins, two room changes, a role reassignment and NE43, and no documented scaffold change after 07-03. A negative control for H56 and a search for undocumented platform changes.

## Model
**From:** `physics-models/02-nonequilibrium-ising` as generalized to categorical (kinetic Potts) states by H14; reading from `physics-models/05-replicator-dissipation`.
- Each agent i is a Markov chain on states x ∈ {1..q} with transition matrix P^(i)(t). Its EP per transition is Σ_i = Σ_{a,b} π_a P_ab ln(π_a P_ab / π_b P_ba). The AIK bound with antisymmetric transition indicators g_ab = 1[a→b] − 1[b→a] equals this pair-KL and lower-bounds the EP of any stationary process with these pair statistics (H17: the chain is not Markov, so all values are lower bounds).
- **Platform-fingerprint hypothesis (H56).** Write ln(P_ab/P_ba) = F_ab^scaffold + F_ab^agent + (U_a − U_b): antisymmetric "forces" F (cycle affinities) and a potential part U. Goal, roster and room changes act like fields: they move U (which states agents occupy, the action mix), which changes occupancy π but not the cycle affinities, so Σ moves little. Scaffold changes alter F^scaffold directly (what follows what is decided by the harness: consolidate → fresh context → screenshot, forced turns, tool batching), so Σ jumps. Agents' own F^agent is small and family-independent (H14: no per-family arrow).
- **Model 05 reading.** Irreversibility comes from one-way steps (degradation-like: consolidation erases context and never reverses). Its size is set by the mechanism that implements the step, which the platform owns, not by the agent.
- **Rivals.** R1 *task mix*: EP tracks what agents are doing (GUI work is more irreversible than shell, H14), so goal kickoffs, which change the work, move EP as much as scaffold changes. R2 *composition*: day-level swarm EP moves when the roster changes because agents differ (H14's weak trait); a within-agent statistic removes it. R3 *calendar*: Mondays and returns from gaps move EP (H36), so any kickoff-aligned effect is a weekday effect. R4 *agent signature*: family differences in fine-action EP are tool-use style, so they survive removal of scaffold records.

## Data scheme (`scheme/build.py`)
- **Inputs:** listed above; non-holdout rows only for the state chains (`holdout_mask` plus the tables' `holdout` flag; asserted).
- **Event catalog (`event_catalog.parquet`):** every dated step change with its class, built by code from:
  - `CHANGELOG.md` entries (parsed by date header and tag). Class rule, fixed before any EP: an entry tagged Tools, Memory, Computer-use or Human-use is **scaffold_tool**; Prompt-only is **scaffold_prompt**; an entry that names one provider or model (Gemini, Anthropic, Claude, GPT-5.4, DeepSeek, [Temporary]) is **scaffold_family**, scored on that family's agents only (difference-in-differences against the others); Goals-only is **goal_prompt**. Exceptions by hand, listed in `scheme/build.py`: auto-nudger on/off and the whitelisted-helper entry are **operator**; hours and start-time changes are **operator_schedule**; changes agents cannot perceive (PII-model upgrade, Tinker support, text-only support, user timeout, chat premoderation, room soft-delete) are **infra_invisible** (not tested); the Claude Code buildout is excluded (one agent, different scaffold). Same-day entries merge into one event with the highest class (tool > family > prompt > goal_prompt).
  - NE catalog rows: NE14 scored at 03-24 (**NE14b**, scaffold_tool, the regime boundary); NE10 at the first observed nudge (operator); NE43 at 08-21 (operator); NE36, NE38 (operator); NE15, NE42a/b and the 08-05 / 08-24 structural room changes (**room**); NE40 (**undocumented**, dated by the NE40 native test).
  - Goal kickoffs (**goal**): the first active day of each goal period. Roster joins and leaves (**roster**; Claude Code agent excluded).
  - Day 0 = the first active day on or after the date. Events whose day 0 is held out are listed for the confirmatory script only.
- **State chains (four variants), per agent and active day:**
  - **V1 act_all:** H14's 11 fine action classes (`act`), all records (mirror turns and forced `mouse_move` already removed by the shared builder).
  - **V2 act_agent:** the agent-only chain on the 7 agent classes (definition above).
  - **V3 coarse_all:** H14's 6 coarse states (records with coarse = −1 dropped, as in H14).
  - **V4 coarse_agent:** the agent-only chain on browse, type, shell, chat and idle.
  Transitions are consecutive within-day records of one agent (cut variants also require no removed record or scaffold-set call start in between).
- **Output:** `data/processed/H56-ep-platform-fingerprint/`: `days.parquet` (active days: index, weekday, regime, holdout, goal, unit), `event_catalog.parquet`, `counts.parquet` (transition counts per agent × day × within-day quarter × variant × (a, b); no text), `ne40_search_features.parquet` (per non-holdout SEARCH_HISTORY event: answer length, line count, markdown counts, latency; numbers only), analysis outputs in `synthetic/`, `replication/`, `native/`, and `_provenance.json`.
- **Regimes covered:** all non-holdout days of regimes I, II and III (2025-04 → 2026-09-04). Comparisons never pool across a regime boundary except NE14b, whose object is that boundary (named exception (c)).

## Observables
*Written 2026-10-04, before any real-data EP.*
- **O1 daily EP rate.** Per agent-day with ≥ n₀ = 120 transitions: the cross-fitted Newton bound on a hypergeometric subsample of exactly n₀ transitions (stratified by within-day quarter, folds = quarters), averaged over R = 4 draws; per variant. Day value = mean over agents. Per hour = per transition × the agent-day's transitions per active hour (secondary). Companions: cross-fitted exact dual (`cfx`) and plug-in (the biased foil).
- **O2 event statistic.** For a step change with day 0 = d₀: pre = the 3 non-holdout active days before d₀, post = d₀ and the next 2 (all within 14 calendar days of d₀ and in one regime, except NE14b). Agents with ≥ 100 transitions on both sides; ≥ 4 agents. For agent i, both sides are subsampled to m_i = min(n_pre, n_post) transitions (stratified by day; R = 4 draws), and Δ_i = Σ̂_post − Σ̂_pre (Newton, day folds). Event statistics: Δ̄ = mean Δ_i (nats/transition), relative change Δ̄ / mean level, sign share f₊ (fraction of agents with Δ_i > 0) and t = Δ̄ / SE(Δ_i). Detection score |t|. The same statistic for the day-pooled swarm (all agents, no pairing) is the composition-sensitive companion.
- **O3 blind change-points.** |t(d)| computed at every eligible non-holdout day d with no knowledge of the catalog. Change-points = local maxima within ±2 active days with |t| ≥ τ, τ = the regime's 90th percentile of |t(d)| (alarm budget 10% of days). Scored afterwards against the catalog: hit = change-point within ±1 active day of an event's day 0; unexplained change-point = none within ±1 day of any catalogued event.
- **O4 family contrast.** Per eligible goal period (≥ 2 labs with ≥ 2 agents of ≥ 300 transitions), per-agent EP over the period (day folds; count-matched to the period's smallest test agent, R = 4), η²_lab with a within-period label permutation (2,000), and a stratified meta-test (sum of η², permuted within periods), on V1–V4. Scaffold share per agent = 1 − Σ(V2)/Σ(V1), compared by lab.
- **O5 platform signature.** For an event or change-point, f₊ (synchrony of the sign across agents) and whether it holds in every provider with ≥ 2 agents.

## Null / baseline
*Written 2026-10-04, before any real-data EP.*
- **N1 weekday-matched placebo days (primary):** non-holdout days with no catalogued event (any class except infra_invisible) whose day 0 lies in [d − 2, d + 2] active days, satisfying the same eligibility. Each event's |t| is ranked against the placebo days with the same weekday in the same regime (fallback, flagged: same weekday in any regime, then any weekday in the regime, when fewer than 8). p_E = (1 + #{placebo |t| ≥ |t_E|}) / (1 + n). Event "hit" at p_E < 0.05.
- **N2 random-date null (class level):** each event of a class is replaced by a random eligible day of its regime (any weekday, not an event day of that class); 5,000 draws of the class mean |t|. Also run against weekday-matched placebo draws.
- **N3 synthetic Markov nulls (axis F):** stationary chains with village counts (no change), occupancy-only changes with exactly preserved EP, count-only changes, roster changes with newcomers of different EP, single-agent changes; the planted scaffold-like change (affinity change) is the positive control.
- **N4 family:** lab labels permuted among agents within a period (H14's test).
- **N5 change-point permutation:** change-point positions circularly shifted within each regime stretch (2,000 shifts), giving the chance hit rate of every class.

## Prediction
*Written 2026-10-04 06:00 UTC, before any real-data EP number. Credences in brackets.* Primary variant V1 (act_all) for detection; V2 for the scaffold-removal claims; V3/V4 reported (low power: per-agent coarse EP ≈ 0.005 nats/transition in regime III, H14).
- **P0 (synthetic, axis F).** At village counts (12 agents, 160–1,300 transitions per agent-day, 3-day windows): (i) the within-agent count-matched |t| has false-alarm rate ≤ 0.07 at its null 95th percentile under occupancy-only (EP-preserving) changes, count-only changes and roster changes; (ii) power ≥ 0.8 for a ±50% affinity change of the fine chain (Σ ≈ 0.08) and ≥ 0.5 for ±50% of a coarse chain (Σ ≈ 0.008); (iii) the plug-in responds to occupancy-only or count-only changes (false alarms > 0.10), the cross-fitted estimators do not; (iv) a change confined to scaffold transitions is detected on V1-like chains and not on the agent-only chain (≤ 0.07). *Estimator rule:* Newton stays primary unless its false-alarm rate in (i) exceeds 0.10 or `cfx` has ≥ 0.15 more power at matched false alarms; then `cfx` becomes primary for O2/O3. *Falsifier:* any (i) above 0.10 for both cross-fitted estimators.
- **P1 (scaffold jumps; H56 core).** On V1, scaffold_tool events: class mean |t| beats N1 and N2 (p < 0.05), and ≥ 40% of them are hits. Scaffold_prompt: weaker, ≥ 20% hits. Excluding NE14b, the scaffold_tool class still beats N2 at p < 0.05 [0.35]. Including NE14b [0.6].
- **P2 (no jump at non-scaffold changes; H56 core).** Goal kickoffs, roster and room events: hit rate ≤ 0.10 each and class p > 0.05 on V1 and V2 [goal 0.5; roster 0.75; room 0.7]. *Against R1:* if goal kickoffs hit as often as scaffold_tool events, H56 fails and R1 wins.
- **P3 (scaffold > others).** Scaffold_tool class mean |t| exceeds the goal-kickoff class mean (one-sided permutation over class labels, p < 0.05) [0.4].
- **P4 (blind detection).** Change-points are enriched near scaffold events: hit rate on scaffold_tool + scaffold_family ≥ 2× the circular-shift chance rate (p < 0.05), and enrichment near goal kickoffs ≤ 1.5× [0.3]. Unexplained change-points are listed as candidate undocumented platform changes; ≥ 1 such candidate shows the platform signature (f₊ ≥ 0.8 or ≤ 0.2, all providers same sign) [0.4].
- **P5 (scaffold removal).** For scaffold events that are hits on V1, the agent-only chain (V2) shows a smaller jump: median |Δ̄(V2)| / |Δ̄(V1)| < 0.5 [0.4].
- **P6 (families; H56 core).** (a) On V1, the stratified family test is significant (p < 0.05) [0.55]; (b) on V2 the mean η² falls by ≥ 50% and the stratified p > 0.05 [0.3]. If (a) fails there is no family difference to remove and P6 is n/a (as H14 found on coarse states). R4 predicts (b) fails.
- **P7 (NE43, native).** H56: no jump on V1 or V2 (|t| below the Friday-placebo 95th percentile; p > 0.05) [0.6]. Drive reading (competing, low credence): the idle-sector EP (Newton on the indicators of pairs involving idle, V2) falls after 08-21 relative to Friday placebos [0.3].
- **P8 (NE14b, native).** V1 and V3 per-transition EP fall across 03-24 for ≥ 80% of agents present on both sides, with |t| beyond every weekday-matched placebo [0.8]. The coarse fall is ≥ 50% carried by scaffold transitions: |Δ̄(V4)| ≤ 0.5 |Δ̄(V3)| [0.5].
- **P9 (NE40, native).** Non-text answer features (length, line count, markdown) show one dominant break in non-holdout data, dating the oracle swap [0.6]. If dated, EP |t| at that day is a hit on V1 [0.2]; the search-sector EP (indicator pairs involving `search`, V1) changes across it [0.35].
- **P10 (G51, native).** Within #51, change-points are not enriched near roster joins or room changes (≤ 1.5× chance) [0.6]; within-agent daily EP has no trend over the nine weeks (|Spearman ρ| < 0.3) [0.6].
- **Multiplicity.** Pre-specified primaries: P1 (scaffold_tool class, N2), P2 (goal class, N2), P4 (scaffold enrichment), P6(b), P7, P8. Six tests; Holm across them is reported next to the raw p. Everything else is descriptive.

## Amendments
1. **2026-10-04 ~07:10 UTC, after the synthetic study, before any real-data EP (synthetic basis only).** P0(iv) failed: when the scaffold forces a reset (consolidation → fixed next action), the *cut* agent-only chain still changes when the reset cadence changes (detection 0.68 at the null 95th percentile), because each reset starts a relaxation transient whose currents are irreversible. Dropping the first 3 transitions of every agent-only segment removes it (0.55 → 0.05; 6 and 10 give 0.07). Added variants **V5 act_agent_b3** and **V6 coarse_agent_b3** (the agent-only chain with a 3-transition burn-in after every cut, including day starts). V5 replaces V2 as the primary "scaffold removed" chain for P5, P6 and the native carriage tests; V2 is still reported as pre-registered.
2. **Estimator rule applied (P0, synthetic):** Newton's false-alarm rate stayed at 0.03–0.05 under every nuisance change, and `cfx` had *less* power (0.56 vs 0.78 at +50%) and failed the nuisance test itself (0.10–0.15 under count and occupancy changes). **Newton stays primary**; `cfx` is reported only as a companion, flagged as not count-robust. Coarse chains (V3, V4, V6) have power ≈ 0.13 at ±50% in 3-day windows, so they are **descriptive only** for event detection (P8's coarse carriage uses them with that caveat).
3. **After the real-data replication run (procedural repair, flagged post hoc).** The pre-registered N1 rule (no catalogued event in the window) left only **35 placebo days**, because the changelog makes the catalog dense (2–6 per weekday and regime). With pools of 8–25 the smallest attainable per-event p was 0.11, so per-event "hits" were impossible by construction (all hit rates 0). Per-event p-values, the NE14 Tuesday null and the NE40 tests were recomputed against **N2 pools**: eligible days of the same regime more than 2 non-holdout days from every event of the *same class*, weekday-matched when ≥ 20 such days exist (median pool 21–68). The class-level random-date null (N2) was pre-registered and is unchanged. Both versions are reported; no verdict depends on the choice (no class beats either null).
4. **NE40 dating, post hoc.** The pre-registered answer features (length, lines, markdown counts) gave one dominant break, but on 03-25/26, where NE14b also changes how the search event is logged, so it cannot date the oracle. Five stylometric counts were added (`*   ` vs `- ` bullets, em dashes, "Based on" openings, `##` headers; numbers only, no text stored), and they date the swap to 04-17 → 04-20. Labelled post hoc throughout.
5. **Post hoc statistics (not pre-registered, reported as leads):** the direction-free magnitude M = median_i |Δ_i| / median level and the sign synchrony S = |f₊ − 0.5|, with the same class-level random-date null; a weekday profile of |t|; Holm over the six primaries.

## Faithfulness scorecard
Scored per model, mapping and window; 0 = not done or failed, 1 = partial, 2 = passed. Scheme and promotion thresholds: `writeup/paper.tex`, Sec. "Assessing model faithfulness".
**Rival models:** R1 task mix; R2 composition; R3 calendar; R4 agent signature.
**Locked holdout used for confirmation:** none yet (`analysis/confirm.py` written and dry-run, not run; it would use the holdout scaffold changes in #22, #28, the NE12/NE30 windows incl. the NE14 rollout, and the NE21+NE23 window incl. NE20, plus kickoffs #9, #14, #15, #22, #28, #29, #32, #34, #43, #45–#50).

| Axis | Test | Score | Evidence |
| --- | --- | --- | --- |
| A mapping | variables defined from dataset fields; assumptions listed; invariant across families and regimes | 1 | States are H14's shared action classes. The scaffold/agent split is explicit: consolidate, search, session, `other`, infra-error turns and scaffold-set call starts (`call_windows.gap_kind`), plus a 3-transition burn-in. Only partly regime-invariant: the boundary state is session start/stop in regimes I/II and CONSOLIDATE in III. `system_class` carries no information (all `none`). |
| B assumptions | stationarity, Markov order, time-rescaling, update-order audit | 1 | Count matching by hypergeometric subsampling (Newton is immune to thinning; plug-in and `cfx` are not, see P0). Within-agent 3-day changes are near-stationary (real \|t\| SD 1.23 vs stationary synthetic 1.13). No new Markov-order audit (H14/H17: non-Markov, so all values are lower bounds). The weekday profile of \|t\| is flat (0.85–1.13). |
| C adequacy | beats the null hierarchy, day-blocked held-out data | 0 | The H56 effect beats neither null: scaffold-tool class N2 p 0.23 (V1), 0.09 (V5); 0/17 per-event hits after Amendment 3. What does beat the nulls goes against H56: goal kickoffs on V5 (p 0.007) and family differences on V5 (p 0.0005). |
| D unfitted predictions | unfitted statistics and the model's signature | 0 | The platform signature (f₊ ≥ 0.8, all providers the same sign) appears at no unexplained change-point. Scaffold carriage at NE14b is 0.62–0.71, not ≤ 0.5. Post hoc only: sign synchrony is higher at scaffold-tool events (S 0.20 vs 0.14, p 0.047 V1, 0.013 V5). |
| E interventional | predicts the change across a natural experiment | 0 | 32 eligible documented scaffold changes (17 tool, 15 prompt), NE14b, the dated NE40 swap and NE43: no jump beyond the nulls at any of them. |
| F identifiability | synthetic recovery with village sampling; robust to preprocessing | 1 | Newton is calibrated under occupancy-only (EP-fixed), task-mix, count, roster and single-agent changes (false alarms 0.03–0.05). Power 0.78 / 0.89 at +50% / −50% on fine chains, but only 0.34 at +25% and 0.13 on coarse chains. P0(iv) failed and was fixed by the burn-in (0.68 → 0.05). `cfx` and the plug-in are not count-robust. Results move with subsampling seeds at n = 12 agents (NE14 carriage 0.50 → 0.62). |
| G ground truth | agrees with known structure | 0 | Independent ground truth exists: the NE14b event-type switch (sessions → consolidations exactly on 03-24), NE40 dated by stylometry (04-20) and the 07-29 tool-schema change. EP does not single out any of them. |
| H comparative | beats the named rivals | 0 | R1 (task mix) beats H56: goal kickoffs ≥ scaffold changes (V1 \|t\| 1.15 vs 1.10; V5 1.23 vs 1.14, class p 0.007 vs 0.09). R4 (agent signature) beats H56: fine-chain family differences survive scaffold removal. R2 (composition) is real only for the pooled statistic (synthetic: 0.27 false alarms at roster changes), which is why the within-agent statistic is primary. R3 (calendar): no Monday excess. |
| I transfer | holds in other same-mode periods, including the holdout | 0 | Nothing positive to transfer. The null holds across regimes I and III alike (22 failed, 8 descriptive, 4 n/a replication periods). Holdout not run. |

## Results by goal period
| Period | Role | Verdict | Key numbers |
| --- | --- | --- | --- |
| [NE14](goalperiod-subhypotheses/NE14/README.md) | native | failed | EP falls in 8/12 agents (−28% fine, −45% coarse) but t −1.33 (p 0.33 vs 35 Tuesdays); coarse carriage 0.62 (most of the fall is in agent transitions) |
| [NE40](goalperiod-subhypotheses/NE40/README.md) | native | failed | swap dated 04-20 by answer stylometry (Gemini bullets 55/61 days before, 0/68 after; p 0.0005), shipped with NE18; EP at 04-20 t −0.18 (p 0.86) |
| [NE43](goalperiod-subhypotheses/NE43/README.md) | native | descriptive | no jump (V1 t −1.55 / −0.20 / −1.08 over three designs, p ≥ 0.38 vs Fridays); idle sector −50 to −95% n.s.; bookends end 08-04, nudges 08-20 |
| [G51](goalperiod-subhypotheses/G51/README.md) | native | mixed | roster/room/operator not enriched (0.69×, p 0.93); V1 trend ρ −0.40 (p 0.006), V5 −0.25 n.s.; unexplained change-points 07-31 (2 days after an undocumented 07-29 tool-schema change) and 08-10, f₊ < 0.8 |
| [G02](goalperiod-subhypotheses/G02/README.md) | replication | n/a | regime I, 3 agents; EP V1 0.063, V5 0.015; scaffold share 0.32; kickoff not scored; scaffold events 0/0 hit |
| [G03](goalperiod-subhypotheses/G03/README.md) | replication | n/a | regime I, 4 agents; EP V1 0.073, V5 0.070; scaffold share 0.12; kickoff not scored; scaffold events 0/0 hit |
| [G04](goalperiod-subhypotheses/G04/README.md) | replication | failed | regime I, 5 agents; EP V1 0.077, V5 0.071; scaffold share 0.08; kickoff t 2.36 (p 0.05); scaffold events 0/2 hit |
| [G05](goalperiod-subhypotheses/G05/README.md) | replication | failed | regime I, 4 agents; EP V1 0.152, V5 0.141; scaffold share 0.13; kickoff t -3.26 (p 0.02); scaffold events 0/0 hit |
| [G06](goalperiod-subhypotheses/G06/README.md) | replication | failed | regime I, 4 agents; EP V1 0.218, V5 0.141; scaffold share 0.22; kickoff t 2.36 (p 0.05); scaffold events 0/3 hit |
| [G07](goalperiod-subhypotheses/G07/README.md) | replication | failed | regime I, 4 agents; EP V1 0.276, V5 0.170; scaffold share 0.33; kickoff t 1.66 (p 0.11); scaffold events 0/1 hit |
| [G08](goalperiod-subhypotheses/G08/README.md) | replication | failed | regime I, 4 agents; EP V1 0.252, V5 0.161; scaffold share 0.25; kickoff t 0.68 (p 0.46); scaffold events 0/4 hit |
| [G10](goalperiod-subhypotheses/G10/README.md) | replication | failed | regime I, 7 agents; EP V1 0.089, V5 0.034; scaffold share 0.49; kickoff t -1.69 (p 0.09); scaffold events 0/1 hit |
| [G11](goalperiod-subhypotheses/G11/README.md) | replication | descriptive | regime I, 7 agents; EP V1 0.096, V5 0.061; scaffold share 0.53; kickoff t 2.20 (p 0.06); scaffold events 0/0 hit |
| [G12](goalperiod-subhypotheses/G12/README.md) | replication | failed | regime I, 7 agents; EP V1 0.075, V5 0.029; scaffold share 0.57; kickoff t -1.33 (p 0.22); scaffold events 0/2 hit |
| [G13](goalperiod-subhypotheses/G13/README.md) | replication | failed | regime I, 6 agents; EP V1 0.084, V5 0.027; scaffold share 0.64; kickoff t 1.35 (p 0.20); scaffold events 0/1 hit |
| [G16](goalperiod-subhypotheses/G16/README.md) | replication | failed | regime I, 7 agents; EP V1 0.078, V5 0.015; scaffold share 0.72; kickoff not scored; scaffold events 0/1 hit |
| [G17](goalperiod-subhypotheses/G17/README.md) | replication | failed | regime I, 7 agents; EP V1 0.090, V5 0.021; scaffold share 0.49; kickoff t 0.31 (p 0.72); scaffold events 0/1 hit |
| [G18](goalperiod-subhypotheses/G18/README.md) | replication | failed | regime I, 8 agents; EP V1 0.110, V5 0.049; scaffold share 0.37; kickoff t 1.75 (p 0.09); scaffold events 0/1 hit |
| [G19](goalperiod-subhypotheses/G19/README.md) | replication | failed | regime I, 7 agents; EP V1 0.092, V5 0.032; scaffold share 0.42; kickoff t 0.94 (p 0.37); scaffold events 0/1 hit |
| [G20](goalperiod-subhypotheses/G20/README.md) | replication | failed | regime I, 10 agents; EP V1 0.119, V5 0.049; scaffold share 0.51; kickoff t 0.74 (p 0.43); scaffold events 0/2 hit |
| [G21](goalperiod-subhypotheses/G21/README.md) | replication | failed | regime I, 9 agents; EP V1 0.116, V5 0.037; scaffold share 0.75; kickoff t -0.82 (p 0.40); scaffold events 0/1 hit |
| [G23](goalperiod-subhypotheses/G23/README.md) | replication | failed | regime I, 10 agents; EP V1 0.115, V5 0.044; scaffold share 0.60; kickoff t 0.53 (p 0.57); scaffold events 0/2 hit |
| [G24](goalperiod-subhypotheses/G24/README.md) | replication | failed | regime I, 10 agents; EP V1 0.147, V5 0.085; scaffold share 0.59; kickoff t 0.84 (p 0.40); scaffold events 0/1 hit |
| [G25](goalperiod-subhypotheses/G25/README.md) | replication | descriptive | regime I, 10 agents; EP V1 0.161, V5 0.091; scaffold share 0.41; kickoff t -1.71 (p 0.09); scaffold events 0/0 hit |
| [G26](goalperiod-subhypotheses/G26/README.md) | replication | descriptive | regime I, 10 agents; EP V1 0.137, V5 0.043; scaffold share 0.62; kickoff t -1.72 (p 0.09); scaffold events 0/0 hit |
| [G27](goalperiod-subhypotheses/G27/README.md) | replication | failed | regime I, 10 agents; EP V1 0.148, V5 0.056; scaffold share 0.59; kickoff t 0.73 (p 0.43); scaffold events 0/1 hit |
| [G30](goalperiod-subhypotheses/G30/README.md) | replication | n/a | regime I, 11 agents; EP V1 0.142, V5 0.091; scaffold share 0.56; kickoff not scored; scaffold events 0/0 hit |
| [G31](goalperiod-subhypotheses/G31/README.md) | replication | descriptive | regime I, 12 agents; EP V1 0.121, V5 0.040; scaffold share 0.63; kickoff t 0.30 (p 0.72); scaffold events 0/0 hit |
| [G33](goalperiod-subhypotheses/G33/README.md) | replication | n/a | regime II, 11 agents; EP V1 0.139, V5 0.031; scaffold share 0.76; kickoff not scored; scaffold events 0/0 hit |
| [G35](goalperiod-subhypotheses/G35/README.md) | replication | descriptive | regime II, 12 agents; EP V1 0.089, V5 0.072; scaffold share 0.22; kickoff t -0.71 (p 0.50); scaffold events 0/0 hit |
| [G36](goalperiod-subhypotheses/G36/README.md) | replication | failed | regime II, 12 agents; EP V1 0.073, V5 0.052; scaffold share 0.14; kickoff not scored; scaffold events 0/1 hit |
| [G37](goalperiod-subhypotheses/G37/README.md) | replication | failed | regime III, 12 agents; EP V1 0.080, V5 0.029; scaffold share 0.41; kickoff t 0.49 (p 0.64); scaffold events 0/1 hit |
| [G38](goalperiod-subhypotheses/G38/README.md) | replication | failed | regime III, 14 agents; EP V1 0.100, V5 0.036; scaffold share 0.16; kickoff t -0.92 (p 0.49); scaffold events 0/3 hit |
| [G39](goalperiod-subhypotheses/G39/README.md) | replication | failed | regime III, 15 agents; EP V1 0.075, V5 0.035; scaffold share 0.09; kickoff t 0.81 (p 0.53); scaffold events 0/1 hit |
| [G40](goalperiod-subhypotheses/G40/README.md) | replication | descriptive | regime III, 15 agents; EP V1 0.055, V5 0.014; scaffold share 0.33; kickoff t -0.31 (p 0.72); scaffold events 0/0 hit |
| [G41](goalperiod-subhypotheses/G41/README.md) | replication | descriptive | regime III, 15 agents; EP V1 0.047, V5 0.014; scaffold share 0.50; kickoff t -0.16 (p 0.83); scaffold events 0/0 hit |
| [G42](goalperiod-subhypotheses/G42/README.md) | replication | failed | regime III, 16 agents; EP V1 0.113, V5 0.100; scaffold share -0.01; kickoff t 0.42 (p 0.66); scaffold events 0/2 hit |
| [G44](goalperiod-subhypotheses/G44/README.md) | replication | descriptive | regime III, 17 agents; EP V1 0.082, V5 0.055; scaffold share 0.10; kickoff t -1.23 (p 0.34); scaffold events 0/0 hit |

## Results
*Exploratory round 1, 2026-10-04, non-holdout only.*
- **Code:** `scheme/build.py` (counts, catalog, days; 3 s), `scheme/build_ne40.py` (numeric search-answer features; 6 s), `analysis/h56lib.py` (count-based estimators, identical to H14's to 1e-16), `analysis/synthetic.py`, `analysis/event_study.py`, `analysis/native.py`, `analysis/posthoc.py`, `analysis/figures.py`, `analysis/write_period_folders.py`, `analysis/confirm.py`.
- **Numbers:** `data/processed/H56-ep-platform-fingerprint/` (`synthetic/summary.json`, `replication/{results,posthoc,period_points,period_summary}.json`, `replication/*.parquet`, `native/*.json`, `confirm_dryrun/`).
- **Figures:** `figures/summary_obs.pdf` (event |t| by class, V1 and V5), `figures/synthetic_validation.pdf`, `figures/daily_series.pdf` (daily EP over 16 months), and native figures in `goalperiod-subhypotheses/{NE14,NE43,NE40,G51}/figures/`.

### Synthetic validation (axis F; `figures/synthetic_validation.pdf`)
12 agents with their own chains, 20 days, change at day 10, per-agent-day transitions as in regime III (median 600). Threshold = 95th percentile of 300 stationary runs per template; 120 runs per scenario.

| scenario (fine chain, Σ ≈ 0.08) | Newton | `cfx` | plug-in (matched) | pooled swarm statistic |
| --- | --- | --- | --- | --- |
| occupancy only, EP held exactly (TV 0.19) | 0.05 | 0.10 | 0.13 | 0.03 |
| occupancy + task mix, EP held (TV 0.20) | 0.03 | 0.08 | 0.11 | 0.03 |
| transitions ×2 / ×0.5 | 0.03 / 0.05 | 0.12 / 0.15 | 0.07 / 0.16 | 0.02 / 0.03 |
| 3 newcomers with 2× EP | 0.04 | 0.04 | 0.07 | **0.27** |
| one agent ×3 | 0.03 | 0.03 | 0.05 | **0.26** |
| affinity +25% / +50% / −50% | 0.34 / 0.78 / 0.89 | 0.28 / 0.56 / 0.56 | 0.43 / 0.88 / 0.96 | 0.56 / 0.99 / 1.00 |
| reset cadence 40 → 20 (with scaffold / cut agent chain / + burn-in 3) | 1.00 / 0.68 / 0.05 | | | |

Coarse chains (Σ ≈ 0.008): power 0.13–0.14 at ±50%. Blind detector (fine, +50%): change-point within ±1 day in 78% of runs, against 9% under the null, with 0.03–0.04 false alarms per day.

### Outcome vs prediction
| | Prediction | Outcome | Verdict |
| --- | --- | --- | --- |
| P0 (i) | Newton false alarms ≤ 0.07 under nuisance changes | 0.03–0.05 (cfx 0.04–0.15) | **met** (Newton) |
| P0 (ii) | power ≥ 0.8 at ±50% (fine), ≥ 0.5 (coarse) | 0.78 / 0.89 fine; 0.13 coarse | **partly met** (fine marginal; coarse failed) |
| P0 (iii) | plug-in responds to occupancy/count changes (> 0.10), cross-fitted do not | plug-in 0.13 / 0.16; Newton ≤ 0.05; `cfx` also responds (0.10–0.15) | **met** for Newton; `cfx` fails too |
| P0 (iv) | scaffold-only change not detected on the agent-only chain (≤ 0.07) | 0.68 (cut) → 0.05 with burn-in | **failed**, fixed (Amendment 1) |
| P1 | scaffold-tool class beats N1 and N2; ≥ 40% hits | V1 mean \|t\| 1.10, N2 p 0.23, weekday-placebo class p 0.07; 0/17 hits (Amendment 3); excluding NE14b p 0.25; prompts 0/15 (p 0.93) | **failed** |
| P2 | goal, roster, room: hit rate ≤ 0.10, class p > 0.05 (V1, V2) | V1: goal 3/28 hits (p 0.08), roster 0/21 (p 0.56), room 1/5 (p 0.78). V2: goal p 0.11. V5: **goal p 0.007** | **held on V1/V2 for roster and room, borderline for goal; failed for goal on V5** |
| P3 | scaffold-tool \|t\| > goal \|t\| (p < 0.05) | −0.06 (p 0.60) on V1; −0.09 on V5 | **failed** (R1 wins) |
| P4 | scaffold enrichment ≥ 2× chance; a platform-signature candidate | 0.61× (p 0.87) on V1, 0.82× on V5; 6 unexplained change-points on V1, none with f₊ ≥ 0.8 | **failed** |
| P5 | at scaffold hits, \|Δ̄(V2)\| / \|Δ̄(V1)\| < 0.5 | no scaffold hits; NE14b fine carriage 0.82 (V2), 0.82 (V5) | **n/a** (and not supported descriptively) |
| P6 (a) | family effect on V1 (stratified p < 0.05) | mean η² 0.34, p 0.0005 (29 periods) | **met** |
| P6 (b) | on V5, η² falls ≥ 50% and p > 0.05 | η² 0.40, p 0.0005 | **failed** (R4 wins). Coarse (secondary): V3 p 0.011 → V6 p 0.56, η² −30% (partial) |
| P7 | NE43: no jump (H56) [0.6]; idle sector falls (drive) [0.3] | no jump in three designs (p ≥ 0.38); idle sector −50 to −95%, n.s. (p ≥ 0.25) | **H56 part held (non-diagnostic); drive reading unsupported** |
| P8 | NE14b falls for ≥ 80% of agents, beyond all placebos; coarse carriage ≤ 0.5 | 8/12 agents fall (fine −28%, coarse −45%); t −1.33, p 0.33 against 35 Tuesdays; carriage 0.62 (V4) / 0.71 (V6) | **failed** |
| P9 | one dominant break in answer features dates NE40 [0.6]; EP hit at it [0.2]; search sector changes [0.35] | pre-registered features break at 03-26 (NE14b-confounded); post hoc stylometry dates 04-20 (p 0.0005); EP at 04-20 t −0.18 (p 0.86); search sector untestable (4 agents) | **failed** (the dating succeeded only post hoc) |
| P10 | #51: no enrichment at roster/room (≤ 1.5×) [0.6]; no trend (\|ρ\| < 0.3) [0.6] | 0.69× (p 0.93); V1 ρ −0.40 (p 0.006), V5 −0.25 (p 0.09) | **first held; trend failed on V1, held on V5** |

**Holm over the six primaries** (p for the effect H56 claims; for absence claims, the jump p): P6(b) family on V5, p 0.0005 (Holm 0.003): significant *against* H56. P2 goal jump, p 0.08 (Holm 0.40). P1, p 0.23 (Holm 0.90). P8, p 0.33. P7, p 0.38. P4, p 0.87. No primary supports H56 at any correction level.

### What it means (exploratory reading)
1. **Behavioral EP is not a platform detector at day resolution.** Within agents, per-transition EP over 3-day windows barely moves at anything: the spread of the event statistic on ordinary days is close to that of a stationary Markov chain with the same counts. Platform changes, goal changes, joins and room changes all sit inside that spread. Even NE14b, which changes the event types themselves, moves fine-chain EP by −28%, and in opposite directions for different providers (Gemini and Claude agents fall, most GPT agents rise).
2. **What does move it is the work.** Goal kickoffs move the agent-only chain more than any scaffold class (V5 p 0.007). Per-period EP levels range from 0.05 to 0.28 nats/transition with the task (highest in the 2025 regime-I build weeks, #6–#8). This is H14's "irreversibility lives in fine tool actions" read correctly: it is task-shaped tool micro-workflow, not the harness.
3. **Families differ, and not through the scaffold.** Fine-chain EP differs by lab in 29 periods (η² 0.34) and the difference *grows* without scaffold records (0.40): tool-use style, as in H13's style field. On coarse states the family difference is scaffold-carried (p 0.011 → 0.56 without scaffold records); that is the only place H56's family claim holds, and it is secondary.
4. **The scaffold share is regime-dependent.** 1 − Σ(V5)/Σ(V1) has median 0.50 in regime I (range 0.08–0.75; it rises through 2025 as session structure grows), 0.22 in regime II and 0.16 in regime III. In the perma-computer-use regime most fine irreversibility is the agent's own.
5. **Undocumented changes are easier to find with direct log features than with EP.** The answerer swap (04-20), the search-tool schema change (07-29), the 03-31/04-01 search malfunction and the end of NE43's bookends (08-04) all show up in plain counts and formats of the logs. EP, computed from the same logs, misses them.
6. **Post hoc lead.** At scaffold-tool events agents' EP moves *in the same direction* more often than on random days (sign synchrony 0.20 vs 0.14, p 0.047 on V1, 0.013 on V5), while the magnitude does not stand out (M p 0.95 / 0.06). A synchronous small shift is what a platform change should do; this is the one thing worth confirming (C6 in `confirm.py`).

### Caveats
- **Power.** Synthetic power is 0.78–0.89 for ±50% changes of fine-chain EP and 0.34 for +25%; coarse chains are blind (0.13). Scaffold changes that move EP by less than about 30% are invisible to this design. The real changes at NE14b (−28% fine) sit at that edge.
- **The catalog is dense and confounded.** 107 eligible events; only 1 scaffold-tool, 2 prompt and 5 goal events are unconfounded within their windows. Most changelog entries share a window with a kickoff or a join. The class tests compare against same-regime random days, not clean contrasts.
- **Day 0 uncertainty.** Changelog dates are merge dates; a deploy can land later, and a ±1-day miss dilutes a 3+3-day statistic. NE14 lands exactly on 03-24 in the logs, so this does not explain its null.
- **Heterogeneous responses.** The within-agent mean-change t is a poor statistic when providers respond in opposite directions (NE14b). The direction-free magnitude M does not rescue it (post hoc). Per-provider DiD was pre-registered only for family-targeted entries, and only one such event was testable (the others had fewer than 2 target agents on both sides).
- **Amendment 3 was made after seeing real data.** It is procedural (the pre-registered pool made p < 0.11 impossible), and no class beats either null, so no verdict depends on it.
- **The agent-only chain is defined, not observed.** The burn-in removes the synthetic reset footprint but may not remove all scaffold influence (e.g. prompt-induced habits). The non-Markov chain means every value is a lower bound (H14, H17).
- **`activity_bins` bug (coordinator notice, 2026-10-04):** H56 uses `states_turn` and `call_windows.gap_kind`, not `activity_bins`, `outages` or `stall_minutes`, so it is unaffected.
- **Holdout not run.** Multiplicity: six primaries (Holm above); everything else is descriptive, including 34 templated replication folders.

### Next steps
1. Run `analysis/confirm.py` on the holdout only with Vivian's sign-off (C1 is a two-sided refutation/confirmation rule; C2 is NE20, the cleanest single-family harness change; C6 is the post hoc synchrony lead).
2. Jev v3 behavior states (DQ3; 50 windows labelled at round-1 start): EP on plan/execute/verify states may separate task-driven from platform-driven irreversibility.
3. A provider-resolved event statistic (DiD per provider at every scaffold event), since NE14b shows opposite-sign responses by provider.
4. A direct log-feature change detector (event-type mix, tool schemas, tool-output stylometry, token logging) as the practical "undocumented change" monitor that EP failed to be.

## Round 2 redirects (2026-10-04)
- **Where round 1 went sideways:** behavioral EP measures what agents are doing (task-shaped tool workflows), not the platform; scaffold changes sit inside the day-to-day spread.
- **What the direction is really after:** a log-only detector of platform changes the operator did not document.
- **H56-R1.** Detect platform changes from direct log features (event mix, tool schemas, output stylometry), blind-scored against the changelog.
- **H56-R2.** Cross-agent sign synchrony (the post hoc lead) as the platform signature: holdout C6, per-provider DiD.
- **H56-R3.** EP on Jev v3 work states, split into task-driven and scaffold-driven parts.

## Notes
- 2026-10-04: promoted from HH175. Round 1 started after an API interruption; nothing had been computed before the predictions above were written.
- 2026-10-04, design facts checked before the predictions (counts only, no EP): non-holdout agent-day record counts (regime III q10/median/q90 160/608/1,264; regime I 243/446/727); 92% of `states_turn` records match a `call_windows` call start exactly (the rest are second records of merged calls); `actions_bash_head_fixed.system_class` is `none` on all 2.51M rows; `period_units` does not split #51 at NE43 (the NE43 row postdates its build).
- 2026-10-04, **data findings** (for the shared catalog; not edited here): (1) NE40 dated 2026-04-20, deployed with NE18 (Gemini-style answer bullets on 55/61 days up to 04-17, on 0/68 days from 04-20). (2) The history-search tool's date fields change from integer `startDay`/`endDay` to string `startDate`/`endDate` on 2026-07-29: undocumented (no changelog entry after 07-03). (3) The search tool returned near-empty answers on 03-31 and 04-01 (median 383 and 42 characters, 85–98 searches a day). (4) NE43: the last daily pause/resume bookend is on 08-04 and the last nudge on 08-20. (5) Search events log input tokens as 0 before 03-24.
- 2026-10-04, **proposed shared-file changes** (not made; outside this card's scope):
  1. `physics-models/DEFINITIONS.md` "Entropy production / irreversibility": add H14's variant "(Markov pair-KL on categorical behavior states)" and this card's "entropy production rate (count-matched, within-agent)" and "agent-only chain" (with the 3-transition burn-in).
  2. `hypotheses/natural-experiments.md`: date NE40 (2026-04-20, with NE18); add the 07-29 search-schema change as a new undocumented step change (next free NE number); correct NE43 (bookends end 08-04, nudges 08-20).
  3. `infra/README.md` Known issues: `actions_bash_head_fixed.system_class` is constant (`none`); search events have no token counts before 03-24; the two NE43 dates.
  4. `physics-models/02-nonequilibrium-ising` pitfalls: count matching by subsampling does not equalize the bias of the plug-in or of the cross-fitted exact dual (thinning changes their noise), so use the cross-fitted Newton bound. A scaffold reset leaves an irreversible relaxation transient in the "agent-only" chain; drop a burn-in after every reset.
  5. `infra/shared/`: `h56lib.newton_counts` / `cfx_counts` compute H14's estimators from count matrices (exactly equal, about 100× faster); worth moving to `infra/shared/` if H14's re-evaluation adopts them.
- 2026-10-04, compute and disk: local, ≤ 2 processes, about 1 CPU-hour in total (the synthetic study was about 40 min of it). `data/processed/H56-ep-platform-fingerprint/` is about 4 MB.

## Recheck (ep_newton fix) (2026-10-04)
*Post hoc estimator recheck. No prediction, threshold, state definition or catalog changed. Trigger: infra/README "Known issues" (H90). H56 copied the legacy cross-product Newton count form at d/n up to 0.46: 55 fine-class columns on n₀ = 120 transitions per agent-day (O1), and on ≥ 100 transitions per side in O2. That is the regime where the legacy form gives a spurious positive bound. Non-holdout only (the day list is asserted against `holdout_mask`). No confirm script was run.*

**What changed.**
- **Switch.** `H56_EP=heldout` in `analysis/h56lib.py` routes `newton_counts` to `infra/shared/ep_newton.py: newton_counts_heldout`. Sector sub-bounds (`pairs`) use the same closed form on the restricted columns. Outputs go to `data/processed/H56-ep-platform-fingerprint/recheck_epfix/`. The default (`xprod`) is the round-1 code path.
- **Default reproduces round 1 exactly.** I reran `event_study.py`, `native.py` and `posthoc.py` in default mode into a scratch folder. All 13 replication and native outputs equal the stored files (`recheck_epfix/verify_default.json`). The one exception is the row order of NE40's descriptive `schema` table, which comes from an unordered `group_by`. Round 1 ran the natives as `--test NE40,NE14,NE43`, then `--test G51`; the RNG stream depends on that order.
- **Rerun with the switch:** the event study, all four natives, posthoc and the synthetic study (Newton only; `cfx` and the plug-ins do not change). New script `analysis/recheck_epfix.py` adds three things: a level synthetic at H56's d/T, a real-data block-flip null for the per-agent EP level, and the old → new comparison (`recheck_epfix/compare.json`).
- **Scale.** The held-out bound is shrunk by its ridge to about 0.5 of its long-run value. Raw magnitudes are not comparable with round 1. Only excess over a null, |t| against the same-estimator day pools, and null tests are compared.

**Synthetic, event layout** (H56's own `synthetic.py` at village counts: 12 agents, 3 + 3 days, median 600 transitions per agent-day, d ≤ 55; τ = null p95; 120 runs per scenario):

| scenario (fine chain, Σ ≈ 0.08) | legacy Newton | held-out Newton |
| --- | --- | --- |
| occupancy only, EP held / + task mix | 0.05 / 0.03 | **0.11** / 0.08 |
| transitions ×2 / ×0.5 | 0.03 / 0.05 | 0.04 / 0.06 |
| 3 newcomers 2× EP / one agent ×3 | 0.04 / 0.03 | 0.06 / 0.03 |
| affinity +25% / +50% / −50% | 0.34 / 0.78 / 0.89 | **0.45 / 0.86 / 0.90** |
| coarse chain ±50% | 0.13 / 0.14 | 0.16 / 0.16 |
| reset cadence 40 → 20: with scaffold / cut agent chain | 1.00 / 0.68 | 1.00 / 0.73 |
| blind detector, +50%: hit within ±1 day (null) ; false alarms per day | 0.78 (0.09); 0.03–0.04 | 0.85 (0.11); 0.04–0.05 |
| null SD of t (real data: 1.23 → 1.23) | 1.13 | 1.10 |

The held-out bound has more power. Its false-alarm rate under EP-preserving occupancy changes is 0.11 (13/120). That is just over the P0 estimator rule's 0.10 line and not separable from 0.07 at n = 120. The cause is its per-column ridge, which depends on the occupancy. The burn-in check (0.68 → 0.05) was not rerun: its code is not in the repository.

**Synthetic, level layout** (new, `recheck_epfix.py --synthetic`; not covered by `ep_newton_synthetic.py`, which tests nested pairwise sets). One 11-state chain per agent.
- **Daily O1** (n₀ = 120, 4 quarter folds, d = 55; 300 runs): on reversible chains (Σ = 0) the legacy bound reads **+0.043** nats/transition (positive in 64% of runs); held-out reads −0.036 (positive in 25%). At true Σ = 0.08: legacy 0.104, held-out −0.004. At Σ = 0.16: legacy 0.171, held-out 0.025. **The round-1 daily level is about half bias, and the held-out daily level cannot resolve Σ ≲ 0.16.** Daily magnitudes (`figures/daily_series.pdf`) are unusable in both forms.
- **Per-agent period level vs a block-flip null** (each (day, quarter) block transposed with probability ½; 100 runs, R = 50): size 0.02 / 0.06 / 0.01 (held-out) and 0.02 / 0.03 / 0.01 (legacy) at 3 × 160, 5 × 600 and 16 × 450 transitions. Power at Σ = 0.02 is 0.08 / 0.89 / 1.00 (held-out) and 0.09 / 0.85 / 1.00 (legacy); at Σ = 0.08 it is ≥ 0.48 / 1.00 / 1.00 in both. The held-out level is 0.46–0.52 of the true Σ at 5–16 days (legacy 0.93–1.03).

**Old → new (non-holdout; nats per transition where a unit applies)**

| Number quoted in the card | Old (legacy) | New (held-out) | Verdict change? |
| --- | --- | --- | --- |
| **Is fine-action EP real?** (not tested in round 1). Agents above the block-flip null, V1, per period | (legacy, recomputed) ≥ 0.8 in 32/35 periods, min 0.67 | ≥ 0.8 in **34/35**, min 0.67 (G02, 3 agents); median excess 0.019–0.133 | new test; supports "irreversibility is real" |
| same, V5 (agent-only + burn-in) / V3 coarse / V6 | 23/35 / 22/35 / 7/35 periods ≥ 0.8 | 24/35 (min 0.43) / 22/35 / 10/35; V6 excess ≤ 0.008 | new test |
| per-period median EP V1 (raw) | 0.042–0.276 | 0.019–0.131 (ridge-shrunk; not comparable) | no (scale) |
| scaffold share, median by regime I / II / III | 0.50 / 0.22 / 0.16 (raw ratio) | 0.45 / 0.25 / **0.13** (excess ratio; raw ratio 0.44 / 0.25 / 0.13) | no |
| P1 scaffold-tool class, V1: mean \|t\|, N2 p (weekday-placebo p) | 1.10, 0.23 (0.07) | 0.92, **0.63** (0.41) | no (still failed; weaker) |
| P1 same, excluding NE14b / V5 / prompts V1 | 0.25 / 0.09 / 0.93 | 0.64 / 0.75 / 0.84 | no |
| P1 per-event hits (Amendment 3), tool V1 / V5 | 0/17 / 1/17 (CL 2025-07-16) | 0/17 / 0/17 | no (the V5 hit goes) |
| P2 goal V1: hits, class p | 3/28 (#4, #5, #6), 0.08 | 3/28 (#5, #11, #26), 0.14 | no (held, borderline) |
| P2 roster / room V1: hits, class p | 0/21, 0.56 / 1/5, 0.78 | 0/21, 0.82 / 0/5, 0.64 | no |
| P2 goal V2 / **V5**: class p (weekday-placebo p) | 0.11 / **0.007** (0.039) | 0.32 / **0.024** (0.22) | no ("failed for goal on V5" still holds against N2, not against weekday placebos) |
| P3 scaffold-tool − goal \|t\|, V1 / V5 | −0.06 (p 0.60) / −0.09 | −0.21 (p 0.83) / −0.35 (p 0.95) | no (still failed; R1 still ahead) |
| P4 enrichment near scaffold-tool, V1 / V5 | 0.61× (p 0.87) / 0.82× | 0.78× (p 0.77) / 0.60× (p 0.89) | no |
| P4 unexplained change-points V1; platform signature (f₊ ≥ 0.8, all providers same sign) | 6; card said "none with f₊ ≥ 0.8" | 8; **2025-12-31: f₊ 0.90, all 3 providers up** (10 agents) | correction, see below |
| P5 NE14b fine carriage V2 / V5 | 0.82 / 0.82 | 1.06 / 1.03 | no (n/a; the agent chain carries all of the fine fall) |
| P6(a) family η², V1 | 0.34, p 0.0005 | 0.34, p 0.001 | no (met) |
| P6(b) family η², V5 | 0.40, p 0.0005 | **0.42**, p 0.0005 | no (failed; R4 stronger) |
| P6 coarse V3 → V6 | p 0.011 → 0.56 | p 0.040 → 0.58 | no |
| P7 NE43 V1 t, three designs (Friday p) | −1.55 / −0.20 / −1.08 (≥ 0.38) | −1.28 / −0.02 / −0.80 (≥ 0.38) | no |
| P7 idle sector, k3 | −76%, p 0.25 | −70%, p 0.38 | no |
| P8 NE14b V1: agents falling, change, t, Tuesday p | 8/12, −28%, −1.33, 0.33 | 7/12, −18%, −0.83, 0.56 | no (still failed) |
| P8 NE14b coarse V3 change; carriage V4 / V6 | −45%; 0.62 / 0.71 | −31%; 0.55 / 0.88 | no (still > 0.5) |
| P9 NE40 EP at 04-20: t, p; search sector t | −0.18, 0.86 (card; stored 0.83); 0.40 | −0.56, 0.60; 0.79 | no |
| P10 G51 enrichment at roster/room/operator | 0.69×, p 0.93 | 0.92×, p 0.71 | no (held) |
| **P10 G51 within-agent daily trend, V1** / V5 | **ρ −0.40 (p 0.006)** / −0.25 | **ρ −0.24 (p 0.12)** / −0.12 (p 0.43) | **yes: the V1 trend failure is withdrawn** |
| G51 unexplained change-points (V1) | 07-31 (two days after the 07-29 schema change), 08-10 | 08-10 only | the 07-31 candidate is withdrawn |
| Post hoc sign synchrony S at scaffold-tool events, V1 / V5 | 0.20 vs 0.14, **p 0.047 / 0.013** | 0.16 vs 0.15, **p 0.37 / 0.35** | **yes: the post hoc lead is withdrawn** |
| Post hoc magnitude M, V1 / V5 | p 0.95 / 0.06 | p 0.84 / 0.29 | no |
| Holm over six primaries | P6(b) 0.003; P2 0.40; others ≥ 0.90 | P6(b) 0.003; P2 0.68; others 1.0 | no |

**Correction to round 1 (P4, second part).** The round-1 text says no unexplained change-point had f₊ ≥ 0.8. The stored 2026-01-01 change-point (V1) had f₊ = 0.80 exactly (8/10 agents), and all three providers moved up. The held-out run puts the same feature at 2025-12-31 (f₊ 0.90). On its letter, the pre-registered signature is met once in both runs. The candidate sits on the New Year break, with 10 agents. It is more likely a holiday schedule or calendar effect (R3) than an undocumented platform change. P4 stays failed on its primary part (enrichment 0.78×). V5's 2025-06-06 candidate has 4 agents from one provider, so it does not count.

**Per-period verdicts** (replication rule of `write_period_folders.py`, applied to the held-out event table; `recheck_epfix/period_verdicts.json`):
- **G11 and G26: descriptive → failed.** Their kickoffs become hits: G11 t 2.20 → 2.65 (p 0.062 → 0.046); G26 t −1.72 → −2.82 (p 0.092 → 0.031). Verdict lines updated, with a dated note.
- G04 and G06 kickoffs are no longer hits (p 0.05 → 0.11 and 0.35). Both stay failed because their scaffold events miss.
- All other replication folders are unchanged.
- **Natives:** NE14 failed, NE40 failed, NE43 descriptive. G51 stays mixed: both parts of P10 now hold, but no #51 change-point shows the platform signature. A dated note is added to each native folder.

**Verdict changes.**
- **Card level: none.** H56 stays refuted as posed. No scaffold class moves within-agent EP beyond same-regime random days, and the scaffold classes are weaker than in round 1 (V1 p 0.63, V5 0.75). Family differences survive scaffold removal more strongly (V5 η² 0.42).
- **Withdrawn:**
  - the post hoc sign-synchrony lead, which was C6 in `confirm.py` and the basis of redirect H56-R2;
  - the G51 V1 trend failure (P10 now holds on both chains);
  - the 07-31 G51 candidate;
  - round-1 daily EP magnitudes, which are about half estimator bias at n₀ = 120.
- **Weakened:** rival R1 (task mix). The goal class still beats N2 on V5 (p 0.024), but not the weekday-matched placebos (0.22), and not V1 (0.14). The held-out bound's occupancy false-alarm rate (0.11) means part of a kickoff "hit" can be estimator sensitivity to the action mix. R1 is now ahead of H56 (P3) but not shown to win.
- **P0(ii)** is now met for fine chains (0.86 / 0.90 at ±50%); coarse chains are still blind (0.16). **P0(i)** is borderline (0.11 vs the 0.10 rule). `cfx` was not rerun; it had less power in round 1, so Newton (held-out) stays primary, with this flag.
- **New, supporting:** fine-action EP is real per agent. It exceeds a reversible null with the same estimator for ≥ 80% of agents in 34/35 periods, and on the agent-only chain in 24/35.
- **Scorecard:** unchanged (A1 B1 C0 D0 E0 F1 G0 H0 I0). D loses the post hoc lead it never scored; F gains power and a borderline nuisance rate.
- **Confirm script:** `analysis/confirm.py` uses `L.newton_counts`, so it runs the legacy form unless `H56_EP=heldout` is set. It must be re-frozen on the held-out estimator, with C6 dropped or demoted, before any holdout run. It was not edited or run.
- **Per-period estimates:** 1,082 rows in `per_period_estimates` (H56 had none before). The legacy round-1 rows (`[legacy cross-product Newton, round 1]`, post_hoc false) cover the median EP, family η² and kickoff t. The post hoc rows carry `post hoc` in `method`: `[held-out Newton, per-column ridge; post hoc ep_newton recheck 2026-10-04]`, plus legacy flip-null rows `[legacy cross-product Newton, post hoc recompute 2026-10-04]`.
- **Compute:** one process, 2 threads, run in sequence. About 4 min for the event study and natives, 24 min for the synthetic (machine load 80+), and 2 min each for the level synthetic and the flip null. `recheck_epfix/` is about 3 MB.

**Claim that stands:** fine-action irreversibility is real and mostly the agents' own, not the platform's. With the held-out Newton bound, ≥ 80% of agents exceed a reversible block-flip null in 34/35 non-holdout periods. The scaffold share of the excess is 0.13 in regime III. Lab differences survive scaffold removal (V5 η² 0.42, p 0.0005). No scaffold class moves EP beyond same-regime random days (V1 p 0.63, V5 p 0.75). Excluded: the post hoc sign-synchrony lead (withdrawn), daily-level magnitudes (estimator bias at n₀ = 120), the G51 07-31 candidate (withdrawn), the New Year signature candidate (calendar, not platform), and coarse-chain event tests (unpowered, 0.16).
