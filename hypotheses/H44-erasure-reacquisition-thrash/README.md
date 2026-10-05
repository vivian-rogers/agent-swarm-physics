# H44: Erasure makes agents busy but unproductive

**Status:** exploratory round 2 done (2026-10-05, non-reserved data; see "Round 2" at the end). The call classifier holds on 300 blind labels (re-acquisition κ 0.87; Θ_c on checked labels +0.106 [0.089, 0.122], 9/9). The sawtooth has two timescales (a one-call re-reading spike, a tail of about 8 calls) and no segment-long linear ramp. A 20-call cap would give 12% less output per call than 40 (Y(20)/Y(40) 0.88). Post-reset reads re-open the working set at the mid-segment rate (no targeted restoration). A wipe does not pay as a loop breaker (E_loop −0.086 writes per call). Round 1 (2026-10-04, non-holdout; 9 regime-III periods + NE41): **Re-acquisition yes, thrash no.** A forced context erasure is followed by a burst of re-reading (re-acquisition share of calls 0.22 → 0.47 at the first call in G51; +0.079 [0.071, 0.086] among non-write calls over the first five calls, conditioned on agent and previous call, 9/9 periods) and a write dip (−26%, work commits −38%), with fewer pauses and +1 pp real failures. No temperature pulse (entropy falls slightly), no extra susceptibility to new room content (reply rate per new item RR 0.97; content pull ≈ 0), but coupling to pre-erasure items falls (ratio 0.60). Erasures break command loops (OR ≈ 0.1); re-reading files restores output fastest; memory dose does nothing. Predictions and synthetic validation came first. `confirm.py` written, dry-run only, **not run**.
**Fields:** nonequilibrium statistical mechanics (kinetic Ising / Glauber response, local field quench vs temperature pulse), information theory and physics of life (Kolchinsky–Wolpert semantic information of stores), dynamics (event studies, relaxation)
**Literature:** [Kolchinsky & Wolpert 2018](../../literature/kolchinsky-2018-semantic-information-autonomous-agency.md) (value of information under a scramble; coarse-graining interventions); [Sowinski et al. 2023](../../literature/sowinski-2023-semantic-information-resource-gathering-agents.md) (viability vs scrambled information); [Bartlett et al. 2025](../../literature/bartlett-2025-physics-of-life-information-roadmap.md) (information import as maintenance)
**Definitions used** (`physics-models/DEFINITIONS.md`): Regime; Action (turn-merged) as implemented by the DQ1 call grouping; Context fill (H30: `ctx_pos`); Exposure (turn read-out) via the DQ1 context ledger; Receiving call (H43); Semantic information (natural-scramble variant) (H15); Field effect / Catalytic effect (H39); Entropy (of behavior); Influence coupling (content pull) (H29). New named variants, defined below and proposed for DEFINITIONS.md: **call category (H44)**, **re-acquisition share**, **thrash index Θ**, **pseudo-erasure**, **reply rate per visible message (pre/post read)**.
**From:** HH156 in `hypotheses/hypohypotheses/HYPOHYPOTHESES.md` · **Models:** `physics-models/02-nonequilibrium-ising/` (kinetic multinomial spin with a context-held self-field; response vs fluctuation), `physics-models/04-semantic-information/` (which store the erasure scrambles)
**Data inputs (shared tables first):** DQ1 `context_ledger_turns`, `context_ledger_items`, `call_windows`; `actions` + `actions_bash_head_fixed`; DQ3 `turn_outcomes` (real failures, write evidence; command text read in memory only, never stored) and `behavior_states_v3`; DQ4 `work_commits`; DQ2 `reply_pairs`; DQ5 `statements_white32_bge_small` (+ gte for robustness); `memory_stats`; `period_units`; `calendar`. Not used: `activity_bins` (join bug) and `outages` (inherit it).

## Standards (2026-10-04)
*Documentation pass against `STANDARDS.md`. No analysis was re-run. H44 has no round-1b section; round 1 already ran on the corrected inputs.*

**Question served:** Q4. The card asks which store holds an agent's working state: the context window (erased), memory or artifacts. Q5 second: forced erasure costs about 4–10% of output.

| Impostor | Relevant? | How it was handled | Status |
| --- | --- | --- | --- |
| Scheduler field | partly | Call-level event study within one agent-day. Pseudo-erasures sit in the same segments about 10 calls earlier, so hour of day matches (KS ≤ 0.04, Notes). Windows truncate at day edges. | removed |
| Exogenous field (kickoff/goal/operator) | partly | Forced resets are timed by the 41-record cap; the forced pre-trend equals the pseudo-erasure band (N-NE41). | removed |
| Shared model priors | partly | Θ_c conditions on agent × previous call category (A2); the effect holds across Anthropic, OpenAI and Google agents (axis A). | removed |
| Contemporaneous convergence | partly | Reply rates per read item are compared with pseudo-erasures in log-age bins (Null); any common co-response cancels in the DiD. | removed |

**Inputs:** round 1 uses the context ledger, DQ3 `turn_outcomes` (real failures), the DQ4 work ledger, DQ2 replies and bge with gte as a sensitivity model. It never reads `activity_bins` or `outages`. Still old: none of the listed inputs. Content pull uses `white32`, not `style_resid`.

**Two layers:** 6 replication folders. Native tests: 4 (`G38` loops, supported; `G36`, `G51` and `NE41`, mixed).

**Confirm script:** `analysis/confirm.py` exists, dry-run only, built on the corrected inputs (CF1–CF5). No re-freeze needed. Disclose reuse with H15, H08, H39 and H46 before a run (Confirmatory plan).

## Question
After a forced context erasure, are agents busy re-acquiring context (reading, browsing, re-opening artifacts) rather than producing, with behavior entropy raised like a local temperature pulse and susceptibility to new room content raised while coupling to pre-erasure senders falls?

Reconciles H39 (idle −0.13 after erasure) with H15 (output −45% for ~10 turns).

## Design: two layers (Vivian, 2026-10-04; see `infra/data-quality/QUEUE.md`)
- **Replication:** the common estimator on every eligible goal period (comparable phase-diagram points). Period README role: `replication`.
- **Period-native tests:** 2–4 goal periods (or NEs) whose setup gives special leverage for this question, each with its own observable, null, ground truth or intervention, its own dated prediction, and period-specific tooling where needed. Period README role: `native`.

Eligible periods: every non-holdout regime-III goal period with forced erasures: **G36** (units 36b–36c), **G37, G38, G39, G40, G41, G42, G44, G51** (51a–51l, non-holdout days to 09-04). Held out (confirmation only): #43, #45–#50, the #51 tail.
- Replication (common estimator only): G37, G39, G40, G41, G42, G44.
- Native (common estimator plus a period-specific test): **G51** (re-acquisition path → output recovery, memory dose, DQ4 work commits at scale), **G36** (NE41 onset at the NE14 switch and the NE16 memory fix), **G38** (loop-heavy weeks: does an erasure break loops?), **NE41** (spanning: forced vs voluntary, quasi-random timing, pooled estimates, cross-period learning trend).
- Unit-of-analysis exception (CLAUDE.md (c)): the erasure is the object; each event compares the two sides of one reset within one agent-day. Estimates are per period; the NE41 folder reports a random-effects pool next to the per-period numbers, never a pooled fit.

## Model
**From:** `physics-models/02-nonequilibrium-ising/` with `04-semantic-information/` for the store bookkeeping.

**Agent as a kinetic multinomial spin with a context-held self-field.** An agent's model call t has a category s_t ∈ {write, run, local read, notes read, remote read, look, GUI, room read, talk, monitor, setup, idle, other} (the call category, below). Its update rule is
P(s_{t+1} = c) ∝ exp[ h⁰_c + h^room_c(t) + h^ctx_c(n) + J(n) 1[c = s_t] ],
with n = `ctx_pos` (calls since the last reset), h⁰ the agent's baseline field (what it does with no task context), h^room the drive from room items that newly entered the context, h^ctx(n) the task field held in the context window (the open files, the current plan in working memory, recent tool output), and J(n) the persistence (self-coupling) that keeps an agent on its current activity. An erasure sets n → 0. H44's claim is that **h^ctx and J are context-held**: h^ctx(n) ≈ h^ctx_∞ (1 − e^{−n/ℓ}), J(n) ≈ J_∞ (1 − e^{−n/ℓ}), with a relaxation length ℓ of a few to ~15 calls.

Consequences (the three worlds used throughout):
- **(i) Re-acquisition thrash (H44):** right after the reset the state distribution relaxes toward h⁰, which favours reading (artifacts, notes, room, screen). The re-acquisition share rises even among non-write calls; switching rises (J small); entropy rises; output (writes, commits) falls; susceptibility to room items rises, because a spin with no self-field responds more to an external field (linear response χ = β(1 − m²) grows as the self-magnetization m → 0); coupling to senders read before the reset falls (their influence was held in h^ctx). Everything relaxes over ℓ calls.
- **(ii) Pure restart overhead (rival R1):** a fixed cost of a few calls during which writes are suppressed, while the composition of the non-write calls, switching and susceptibility stay at baseline.
- **(iii) No effect (rival R0).**
- **Rival R2, temperature pulse:** β drops (all fields scaled down): entropy rises but χ falls or stays put. Discriminated from (i) by the sign of the susceptibility change.
- **Rival R3, task boundary:** the post-reset change reflects a finished task rather than the erasure. Forced erasures (timing set by the 41-call cap) then show less than voluntary ones, whose timing the agent chose at a task boundary.

**Kolchinsky–Wolpert reading (model 04).** Stores: the context window C (erased), memory M (kept; rewritten by the agent at the consolidation, KW's agent-chosen coarse-graining f), artifacts A (kept: files, repos, the agent's own notes files) and the room R (environment). The forced erasure is a natural scramble of C with M, A and R intact. ΔV is the output lost per erasure (write calls and work commits over +1…+20 vs the counterfactual); restoration runs through re-reading A, M (already in the prompt after the reset) or R. H44 asks which store held the load-bearing information, via which re-acquisition path restores output fastest and whether memory dose (lines written at the consolidation) shortens the dip (H15: no).

## Data scheme (`scheme/`)
- **Inputs:** `context_ledger_turns` (calls, `ctx_pos`, `reset_forced`, `reset_consol`, `reset_session`, `first_of_day`, `prev_seg_len`, new items by kind, `n_ment`); `context_ledger_items` (which call read which message); `actions` rows + `actions_bash_head_fixed` (action type) mapped to calls by (agent, time ∈ [t_first, t_log]); `turn_outcomes` (bash/type turns: `failed`, `commit_ok`, `push_ok`, `file_write`, `api_write`, `deploy`; `cmd` is read in memory to classify the command and to hash it for loop detection, never stored); `work_commits` (agent work = `canonical & ~imported & author_kind=="agent" & ~automated`) mapped to the call whose `t_log` is the first ≥ the author time (same agent, ≤ 10 min); `behavior_states_v3` (5-min windows, probability vectors); `reply_pairs` (`pair_set == "cand"`, `parent`); statements + white32 vectors; `memory_stats` (snapshot within 180 s after a consolidation: `lines_added`, `n_lines`).
- **Transform:**
  1. Regime-III, non-holdout calls (`holdout == False` and `common.holdout_mask`), non-summary (`ctx_mode == "cu"`); each call gets one **call category (H44)** by priority write > talk > room read > notes read > local read > remote read > run > look > GUI type > GUI > monitor > setup > idle > other:
     - **write**: any bash write evidence (`commit_ok | push_ok | file_write | api_write | deploy`);
     - **talk**: `send_message_back_to_chat`;
     - **room read**: `search_history`;
     - **notes read**: a read-only shell command (cat/head/tail/less/grep/rg/sed -n/awk/wc/jq) on a file whose name contains note, memory, memo, todo, handoff, journal, diary, scratch, progress, checklist, context, plan or session (the agent's own external memory);
     - **local read**: other read-only shell commands (cat, head, tail, less, grep, rg, find, ls, tree, wc, stat, diff, jq, sed -n, awk, pwd, which, file; git status/log/show/diff/branch/remote/rev-parse/ls-files/blame/reflog/describe);
     - **remote read**: curl/wget/http without write flags; gh/glab view/list/status/api without write flags; git fetch/pull/clone/ls-remote;
     - **run**: interpreters, builds, tests, scripts (python, node, npm, make, pytest, bash x.sh, codex, tmux, nohup, timeout, ffmpeg, …) without write evidence;
     - **look**: screenshot, get_pixel_coords_of_element, cursor_position, view_clipboard;
     - **GUI type**: `type`; **GUI**: clicks, scroll, key, mouse moves, drags;
     - **monitor**: sleep, ps, top, pgrep, kill, pkill, date, uptime, jobs, wait (shell);
     - **setup**: only cd / export / set / source / mkdir / touch / chmod / variable assignments;
     - **idle**: pause, wait (tool); **other**: none, room moves, requests, unclassified shell.
     The **re-acquisition share** R = share of calls in {room read, notes read, local read, remote read, look}. **R_nw** = the same share among non-write calls (the thrash signature).
  2. Events. Each agent's non-summary calls are indexed in time order within the PT day. A reset sits between calls i−1 and i when call i has `reset_consol`. **Forced** = `reset_forced` (the closed segment had 41–42 records; NE41); **voluntary** = `reset_consol & ~reset_forced` with `prev_seg_len` 10–38 (H15's CV band; all voluntary as a variant). Offsets: +1 = first call after the reset, −1 = last call before it. Windows −20…+20, truncated at the next reset of any kind (consolidation, session reset, first of day) and at the day edge.
  3. **Pseudo-erasure** (control): every call at `ctx_pos == 21` whose window −10…+20 contains no reset of any kind (so it sits in ctx 11–41 of one segment), same agent-day pool; a second variant at `ctx_pos == 16` (window −5…+15). They carry the same offsets and estimators.
  4. Loop flag: per call, a 64-bit hash of the classified command text (bash) or action type (GUI), stored as an integer; a call is "in loop" when its hash already occurred ≥ 2 times in the previous 10 calls, or it is the 3rd real failure in 10 calls.
  5. Reply and content tables: talk messages B of the agent within ±20 calls of an event or pseudo-event, their visible pool (ledger items read by the agent's calls in the 60 min before B, same day), each pool message's read call relative to the boundary (pre/post) and age; B's DQ2 parent (if any). Content pull pairs: consecutive chat statements of the agent on one day straddling exactly one forced (or voluntary) reset, or no reset (within pairs), with messages read between them split at the boundary (within pairs: at the middle call).
- **Output:** `data/processed/H44-erasure-reacquisition-thrash/` (`calls.parquet`: one row per regime-III non-holdout call with category, write flags, failures, work commits, new items, ctx_pos, loop flag and command hash (integer only); `events.parquet`; `v3_windows.parquet` (window features + time since reset); `reply_pools.parquet`; `pull_pairs.parquet`; per-period `G<NN>/results.json`; `synthetic/`; `_provenance.json`). Budget ≤ 200 MB.
- **Regimes covered:** regime III only (2026-03-24 → 2026-09-04, non-holdout days). Earlier regimes have no consolidation cap.

## Observables
Per event e and offset k, per period; agent-day cluster bootstrap (1,000 draws) for every CI; ratio-of-sums for rates.
- **O1 re-acquisition:** R(k), R_nw(k); contrasts ΔR = R(+1…+5) − R(−20…−11) and the **thrash index Θ = R_nw(+1…+5) − R_nw(−20…−11)**; per-category shares (k).
- **O2 temperature:** category entropy H(k) across events (Miller–Madow), within-event entropy of the 13-category histogram over five-call blocks, switching rate σ(k) = P(s_k ≠ s_{k−1}); relaxation length ℓ from an exponential fit of R(k), k = 1…20. v3: per 5-min window, Shannon entropy of the probability vector, p_research_browse, p_execute_task, p_self_maintenance, progress_score, n_errors, against minutes since the last reset (forced vs voluntary) with agent-day fixed effects.
- **O3 output:** write share W(k); relative dip Ω = W(+1…+10)/W(−20…−11) − 1 (H15's statistic: a replication, not an independent test); work commits per call; real failures per call.
- **O4 susceptibility:** (a) **reply rate per visible message**, for pool messages read before vs after the boundary, in log-age bins (≤ 1, 1–3, 3–10, 10–30, 30–60 min), erasure vs pseudo-erasure (DiD on the log rate ratio); (b) P(B has a parent) and P(talk) per call; (c) **content pull** a(S) = Σ y·u / Σ |u|² (H29) of the post-boundary statement toward pre- vs post-read messages, stratified by agent × time gap between the two statements in 0.05-decade bins (H46 Amendment 2) and by message age.
- **O5 Kolchinsky:** ΔV = Σ_{k=1..20} [W(k) − W_ref] per erasure (write calls lost) and the same for work commits; hazard of the first post-erasure write by first re-acquisition path (within agent); Spearman ρ(memory lines added at the consolidation, Ω).

## Null / baseline
- **Pseudo-erasures** (ctx_pos 21 and 16, no reset in window): every contrast must be ≈ 0 there (the flatness check for the mid-segment baseline and the estimator's size).
- **Far-pre reference** (−20…−11) as in H15, plus a steady-state reference (the agent-day's calls at ctx 11–30); the near-pre window (−10…−1) is reported to expose end-of-segment drift (H46: context-full state).
- **Forced vs voluntary** (rival R3).
- **Past-only eligibility** (DQ8 lever-design rule): event and pseudo-event eligibility uses only calls up to the event (truncation at the next reset is applied identically to both arms and to all offsets > 0, and reported as a sensitivity with a balanced +1…+20 subset).
- **Matched time of day:** pseudo-events reweighted to the forced events' hour-of-day distribution within period.
- **Gap strata** for the content-pull pairs (0.05 decades) and log-age bins for reply rates (recency confound, H29/H46).
- **Synthetic worlds** (axis F) on real call skeletons: (i) thrash, (ii) pure output dip, (iii) none; the pipeline must classify each correctly at real counts.

## Faithfulness scorecard
Scored per model, mapping and window; 0 = not done or failed, 1 = partial, 2 = passed. Scheme and promotion thresholds: `writeup/paper.tex`, Sec. "Assessing model faithfulness".
**Rival models:** R0 no effect; R1 pure restart overhead (output dip, no thrash); R2 temperature pulse (entropy up, susceptibility down); R3 task boundary (voluntary ≫ forced).
**Locked holdout used for confirmation:** none yet; planned in `analysis/confirm.py` (#43, #45, NE21+NE23 = #46–#50, #51 tail; written and dry-run on stand-ins, **not run**).

| Axis | Test | Score | Evidence |
| --- | --- | --- | --- |
| A mapping | variables defined from dataset fields; assumptions listed; invariant across families and regimes | 1 | Calls (DQ1), call categories from logged action types and in-memory command classification, write evidence (DQ3 `turn_outcomes`), DQ4 work commits, DQ2 reply parents, ledger visibility. Assumptions listed (scheme, Amendments). The command classifier is a heuristic, not validated against hand labels; GUI clicks and typing cannot be split into navigation vs production. Holds across Anthropic, OpenAI and Google agents (agent × previous-call conditioning absorbs composition), only regime III exists. |
| B assumptions | stationarity, Markov order, time-rescaling, update-order audit | 1 | Θ_c conditions on first-order (agent × previous category) state; the synthetic shows why (pure-dip spillover), real data are higher order. **Not stationary within a segment:** writes ramp up and reads decline across all 40 calls (pseudo-erasures Ω +13%), so the far reference sits on a ramp. Time measured in calls (update order = the agent's own calls); 5-min wall-clock windows are biased toward dense activity after a forced reset. |
| C adequacy | beats the null hierarchy, day-blocked held-out data | 1 | Beats the no-reset pseudo-erasure null in 9/9 periods (Θ_c) and 8/9 (Ω); past-only pseudo control and balanced windows agree; the hour-of-day match is built in (KS ≤ 0.04). No held-out-day likelihood; the model's susceptibility and entropy signatures fail. |
| D unfitted predictions | unfitted statistics and the model's signature | 1 | Unfitted and as predicted: Θ_c sign and size, forced ≥ voluntary, no excess pre-trend, relaxation tail ℓ 5–7 calls (predicted 3–15), coupling cut, loop breaking, memory dose ≈ 0, work-commit dip. Unfitted and failed: entropy rise, susceptibility rise (RR 0.97), content pull rise (D ≈ 0, G51 negative), onset effect and learning trend (G36). |
| E interventional | predicts the change across a natural experiment | 1 | NE41's forced resets (timed by the 41-record cap; pre-trend = the no-reset band) were the pre-registered intervention: re-acquisition, output and coupling-cut predictions held in every period, susceptibility predictions did not. NE16 had no first stage. Holdout not run. |
| F identifiability | synthetic recovery with village sampling; robust to preprocessing | 2 | **Round 2 (2026-10-05): 2.** Every round-2 estimator was validated on real skeletons with size and power before real data, which found three design flaws (Amendments A3–A6). Round 1: `analysis/synthetic.py`: three worlds on real call skeletons, 100% correct at G51 and G38 counts, G37-size thrash detected 62% (missed output dip, never a false thrash); it found that the raw Θ calls a pure dip "thrash" at G51 scale (Amendment A2). Reply estimator recovers planted effects (null log DiD −0.01, cover 95%). Robust to the normalized loop hash, bge vs gte, past-only controls; classifier not cross-validated. |
| G ground truth | agrees with known structure | 2 | **Round 2 (2026-10-05): 2.** 300 blind hand labels (one rater, Claude; tool names and arguments only) agree with the call classifier on re-acquisition in 95% of population-weighted calls (κ 0.87). Round 1: The cap appears exactly (40-call segments); the first post-reset call rarely writes (H15); write-call and DQ4 work-commit dips agree (−26% vs −38%); voluntary resets follow a status message (G51 talk share 0.07 → 0.17 at the last call), as consolidating at a task boundary should. No hand-labelled re-acquisition ground truth. |
| H comparative | beats the named rivals | 1 | Rejects R0 (no effect), R1 (pure restart overhead: Θ_c 0.06–0.10 vs ≤ 0.005 in the synthetic dip world), R2 (temperature pulse: entropy falls) and R3 (task boundary: forced ≥ voluntary). But H44's own field-quench signature (susceptibility up) also fails, so the winning description is narrower than the model. |
| I transfer | holds in other same-mode periods, including the holdout | 1 | Θ_c > 0 in 9/9 regime-III periods (τ 0.006), Ω < 0 in 8/9, from the first erasure days (#36) to #51. Holdout not run. |

## Prediction
*Written 2026-10-04 06:40 UTC, before running the analysis on real data.*

**What had been looked at before writing this:** table schemas; the regime-III counts of calls by kind and of resets by period and by closed-segment length (41–42 spike; 21,165 forced vs 16,357 voluntary); the regime-III action-type and bash-head frequency tables (aggregate, not aligned to any reset); DQ2 label coverage (top-1 candidates labelled, ranks 2–3 mostly not); memory_stats row counts. No statistic aligned to a reset or to `ctx_pos` was computed. Known from other cards: H15 (writes −33…−53% over +1…+10 in 8/9 periods; first post-reset turn rarely writes; memory dose ρ ≈ 0), H39 (idle −0.13, browse +0.056, type+shell +0.099 after erasure on the 1-min grid), H08 (addressing of pre-read senders −18% ± 6%), H46 (style drifts with ctx_pos and resets at erasure).

| # | Prediction | Counts against |
| --- | --- | --- |
| P1 re-acquisition | Forced erasures: ΔR(+1…+5) ≥ +0.05 absolute and **Θ > 0** with the pooled CI above 0 and ≥ 6/9 periods positive; pseudo-erasures \|ΔR\|, \|Θ\| < 0.02 | Θ ≤ 0 or its CI including 0 in the pool (→ R1 pure overhead) |
| P2 temperature | Switching σ(+1…+5) and entropy H(+1…+5) above the far-pre reference (pooled CI > 0, ≥ 6/9 periods same sign); ℓ for R(k) between 3 and 15 calls; v3: entropy and p_research_browse higher, p_execute_task lower in the first 5 min after a forced reset than at 10–15 min | σ and H flat or lower |
| P3 output | Ω between −0.25 and −0.60 (≥ 7/9 periods CI < 0); work commits per call down over +1…+10; recovery to within 10% of reference by +20 | Ω ≥ 0 |
| P4a coupling cut | Reply rate per visible pre-read message falls relative to post-read ones after a forced erasure more than after a pseudo-erasure (pooled log-ratio DiD < 0) | DiD ≥ 0 |
| P4b susceptibility | Reply rate per visible post-read message after a forced erasure exceeds the pseudo-erasure rate at matched age (pooled ratio > 1, CI) | ratio ≤ 1 |
| P4c content pull | Pull toward post-read minus pull toward pre-read messages is larger across forced pairs than within pairs (gap-stratified, pooled CI > 0) | ≤ 0 |
| P5 forced vs voluntary | Θ_forced > 0 and ≥ 0.5 × Θ_voluntary (the erasure, not the task boundary, drives thrash); voluntary has the larger pre-window write excess | Θ_forced ≈ 0 while Θ_voluntary > 0 (R3) |
| P6 field vs temperature | If σ/H rise (P2), the susceptibility (P4b) rises too: a field quench, not a temperature pulse | entropy up with χ down (R2) |
| P7 synthetic (F) | The pipeline classifies thrash / pure dip / none correctly in ≥ 90% of replicates at G51 counts and ≥ 70% at G37-size counts | misclassification of the pure-dip world as thrash > 10% |

**Native predictions:**
- **G51 (path → recovery; memory dose; DQ4):** among forced erasures, a first re-acquisition call on local artifacts or notes is followed by an earlier first write (within-agent hazard ratio > 1) than a first call that looks at the screen, browses or reads the room; memory dose does not shorten the dip (\|ρ\| < 0.1); work commits dip like write calls (relative dip within ±0.2 of Ω).
- **G36 (NE41 onset, NE16):** the thrash index on the first two days of forced erasure (03-24/25) is larger than the G38–G51 mean (agents had not yet adapted); NE16's memory fix (03-26) does not change Θ or Ω beyond noise (memory is not the load-bearing store). Across periods Θ declines and the notes-read share rises from #36 to #51 (learning; a phase-diagram trend, not a pooled fit).
- **G38 (loops):** among events whose pre-window is in a loop (≥ 3 calls in loop in −10…−1), the loop recurs in +1…+10 less often after a forced erasure than after a pseudo-erasure with a loop in its pre-window (odds ratio < 0.7, CI < 1).
- **NE41 (spanning):** forced erasures show no pre-trend in W or R over −20…−1 beyond the pseudo-erasure band (quasi-random timing); voluntary erasures show a write excess in −10…−1.

**Verdict rule (per period, replication layer):** *supported* if Θ > 0 (CI), Ω < 0 (CI), σ or H up (CI) and P4b not significantly opposite; *failed* if Θ ≤ 0 with CI below +0.01 or Ω ≥ 0; *mixed* otherwise; *descriptive* if fewer than 150 forced events with a usable window. Native folders add their own test to the period verdict (both must hold for *supported*). (Amendment A2: Θ here means Θ_c, with the 0.01 floor.)

## Results by goal period
| Period | Role | Verdict | Key numbers (forced resets) |
| --- | --- | --- | --- |
| [G36](goalperiod-subhypotheses/G36/README.md) | native (NE41 onset, NE16) | mixed | Θ_c +0.069 [0.046, 0.096], Ω −25%; σ/H not up; onset not larger than later weeks; NE16 no first stage |
| [G37](goalperiod-subhypotheses/G37/README.md) | replication | mixed | Θ_c +0.061 [0.027, 0.098]; Ω −5% (n.s.; 368 resets, synthetic power 62%) |
| [G38](goalperiod-subhypotheses/G38/README.md) | native (loops) | supported | Θ_c +0.068 [0.056, 0.082], Ω −24%, σ +0.032; loops recur 16% vs 72% (OR 0.08) |
| [G39](goalperiod-subhypotheses/G39/README.md) | replication | mixed | Θ_c +0.096, Ω −25%; σ/H flat |
| [G40](goalperiod-subhypotheses/G40/README.md) | replication | mixed | Θ_c +0.070, Ω −25%; σ/H flat |
| [G41](goalperiod-subhypotheses/G41/README.md) | replication | mixed | Θ_c +0.102, Ω −37%; σ/H flat |
| [G42](goalperiod-subhypotheses/G42/README.md) | replication | mixed | Θ_c +0.086, Ω −28%; σ/H flat |
| [G44](goalperiod-subhypotheses/G44/README.md) | replication | supported | Θ_c +0.059, Ω −33%, σ +0.061 |
| [G51](goalperiod-subhypotheses/G51/README.md) | native (paths, dose, commits) | mixed | Θ_c +0.081 [0.073, 0.088], Ω −24%, work −38%; susceptibility RR 0.90 (opposite); artifact-first resumes writing 2.6 calls sooner; dose ρ −0.03 |
| [NE41](goalperiod-subhypotheses/NE41/README.md) | native (spanning) | mixed | pooled Θ_c +0.079 (9/9), Ω −26%, forced ≥ voluntary, no excess pre-trend; entropy −0.027; RR(new items) 0.97; coupling-cut ratio 0.60; loops OR 0.11 |

Replication verdicts follow the pre-registered rule, whose temperature clause (σ or H up) fails in most periods; the re-acquisition (Θ_c) and output (Ω) clauses hold almost everywhere. The nine replication points are not independent tests of one claim.

## Results
*Exploratory round 1, 2026-10-04, non-holdout regime III (G36–G51; 1.24M calls; 21,165 forced and 16,357 voluntary resets; 21,806 no-reset pseudo-erasures per kind). Scripts: `scheme/build.py`, `analysis/synthetic.py`, `analysis/run_all.py`, `analysis/write_period_folders.py`, `analysis/figures.py`, `analysis/confirm.py`. Numbers: `data/processed/H44-erasure-reacquisition-thrash/{G<NN>,NE41}/results.json`, `synthetic/synthetic.json`, `robustness_pseudo_past.json`, `per_period_estimates_H44.parquet`. Figures: `figures/summary_obs.pdf`, `figures/forest.pdf`, `figures/synthetic_validation.pdf`, per-period `goalperiod-subhypotheses/G<NN>/figures/event_study.pdf`. Pooled numbers are DerSimonian–Laird over per-period estimates (CLAUDE.md exception (c)).*

### Synthetic validation (axis F, before real data)
Planted worlds on real call skeletons (real agent-days, real reset positions and events): (i) field-quench thrash, (ii) pure output dip, (iii) none. With the A2 statistic Θ_c and floor 0.01, classification accuracy is 100% / 100% / 100% at G51 (14,593 forced resets, 10 replicates) and G38 (2,333; 24 replicates); at G37 (368; 40 replicates) 62% / 98% / 93%: the small-period failure is a missed output dip ("busy"), never a false thrash. The raw Θ would have called the pure dip "thrash" in 100% of G51 and 58% of G38 replicates (Markov and agent-mix spillover): the main thing the synthetic taught. Planted entropy changes are small and sign-unstable under a field quench (Amendment A1). The reply estimator recovers planted susceptibility (×1.4 → RR 1.33–1.36) and coupling cut (log 0.5 → −0.61 to −0.69) and is unbiased under the null (log DiD −0.01 to +0.06, CI covers 0 in 95–100%; RR 0.96–0.98).

### Outcome vs prediction
| # | Prediction | Observed (pooled over 9 periods unless stated) | Verdict |
| --- | --- | --- | --- |
| P1 | Θ > 0 (CI), ΔR ≥ +0.05, ≥ 6/9; pseudo ≈ 0 | Θ_c +0.079 [0.071, 0.086], 9/9 CIs > 0; ΔR +0.101; pseudo Θ_c −0.011 [−0.016, −0.006] | **supported** |
| P2 | σ and H up; ℓ 3–15 calls; v3 entropy and browse up, execute down | σ +0.018 [0.004, 0.031] (7/9); H −0.027 [−0.050, −0.004] (2/9 up); ℓ: spike at call 1, tail 5–7 calls; v3 windows: execute +0.035, progress +0.15, entropy n.s. | **failed** (no temperature pulse; σ rise tiny) |
| P3 | Ω −0.25…−0.60, ≥ 7/9 CI < 0; commits down; recovery by +20 | Ω −26% [−29, −23], 8/9; work commits −38% [−41, −35]; writes back to the far level by +15…+20 (ℓ_W ≈ 3 calls) | **supported** (H15 replication) |
| P4a | coupling cut: log DiD < 0 | ratio 0.60 [0.44, 0.81], 8/9 negative | **supported** |
| P4b | susceptibility to post-reset items RR > 1 | 0.97 [0.91, 1.04]; G51 0.90 [0.85, 0.95] | **failed** (G51 opposite) |
| P4c | content pull D > 0 | −0.026 [−0.064, 0.012] (bge), −0.028 (gte); G51 −0.027 [−0.047, −0.007] | **failed** |
| P5 | Θ_c(F) ≥ 0.5 Θ_c(V); voluntary pre-window write excess | 0.079 vs 0.057; voluntary pre-trend +18% vs forced +7% (= pseudo +7%); talk share 0.07 → 0.17 at the last call before voluntary resets (G51) | **supported** (R3 rejected) |
| P6 | σ/H up together with χ up (field quench, not temperature) | entropy down, χ flat: neither a temperature pulse nor a χ-raising quench | **failed** (R2 rejected too) |
| P7 | synthetic ≥ 90% at G51, ≥ 70% at G37 size | 100% at G51 and G38; G37 thrash 62% | **mixed** |
| N-G51 | artifact-first resumes sooner; \|ρ_dose\| < 0.1; commits dip like writes | artifact −2.6 calls vs screen (room −0.5, direct −3.8); ρ −0.033; −38% vs −24% | **supported** |
| N-G36 | onset larger; NE16 no change; Θ declines, notes rise | onset Θ_c 0.075 vs 0.080 later; NE16 no first stage; ρ(Θ_c, time) +0.23 (p 0.55) | **failed** |
| N-G38 | loops recur less after a reset (OR < 0.7) | 16% vs 72%, OR 0.08 [0.04, 0.13]; normalized hash 0.07 | **supported** |
| N-NE41 | no forced pre-trend beyond the pseudo band | +7% vs +7% | **supported** |

### What the event study shows
- **Re-acquisition (O1).** In G51 the share of calls that read (local files, git, notes, web/API, screenshots, history search) doubles at the first call after a forced reset (0.22 → 0.47), stays ~+0.08 for calls 2–5 and decays with a tail of ℓ ≈ 7 calls [5.4, 9.2] (G38 5.7, G40 4.7, G41 7.0). Among non-write calls, conditioned on agent and previous call, the rise over calls 1–5 is Θ_c +0.06 to +0.10 in every period. What rises is local reads (+0.048 in G51), screenshots (+0.041) and remote reads (+0.014); history search (the room) +0.002, notes files +0.002, talk 0.
- **"Busy" (H39) and "unproductive" (H15) are the same calls seen at two scales.** Per call, pause/wait calls fall (−0.015 to −0.019), writes fall (Ω −26%) and real failures rise (+0.010 [0.006, 0.015] on a base of 2–5%: trial and error with a lost working state). At 5-min resolution the Jev v3 labeller sees post-reset windows as *more* executing and more productive (execute +0.035, progress +0.15; also against the last 5 min before a reset), because a 5-min window (~15 calls) blends the 1–5-call burst with the resumed work and wall-clock windows after a forced reset are selected for dense activity.
- **No temperature pulse (O2).** Category entropy over calls 1–5 falls slightly (−0.027) and switching rises only +0.018. The re-acquisition is an orderly, concentrated mode (read, then resume), not disordered thrash. The erasure acts on a field (the composition), not on the temperature.
- **A 40-call sawtooth, not a 10-call blip (O3).** Writes recover quickly (ℓ_W ≈ 3–4 calls) but keep rising slowly through the whole segment: the last 10 calls before a reset write 7% more than calls −20…−11, in forced segments and identically in no-reset pseudo-erasures. Each forced reset costs 0.27–0.89 write calls and 0.05–0.33 work commits (+1…+20 vs far), i.e. **3.7–8.7% of all write calls and 4.8–10.9% of all agent work commits per period** (G37 ≈ 0).
- **Susceptibility (O4).** After a reset an agent replies to a newly arrived room item at the same rate as after a no-reset boundary (RR 0.97; G51 0.90), and its next statement is not pulled harder toward new items (D ≈ 0, G51 slightly negative in both embedding models). It is somewhat more likely to reply to something at all (P(has parent) ×1.07). What does drop is coupling to items read before the reset: their reply rate falls to 0.60 of post-read items' relative to in-context controls (H08's −18% with a different estimator). The agent is not a blank slate that absorbs the room; it rebuilds from its own artifacts.
- **Loops (G38 native).** When the last 10 calls before a reset contain a command loop, the looping command recurs in the next 10 calls 16% of the time vs 72% without a reset (G38; pooled OR 0.11 [0.05, 0.26] over 7 periods; G51 weaker, 0.34). The same holds for a normalized hash that ignores cd prefixes and numbers.

### Kolchinsky–Wolpert reading: which store does the erasure scramble?
- **Context window (C) scrambled, load-bearing at the call scale.** ΔV ≈ −0.4 write calls per erasure (G51), ~4–9% of all output; κ (ΔV per bit) is not estimable without token-level content.
- **Memory (M) carries little of what restores output.** The lines an agent writes into memory at the consolidation do not shorten the dip (within-agent ρ −0.08…+0.02; G51 −0.033), as in H15. NE16 could not test memory as a store (no change in lines written).
- **Artifacts (A) are the restoring store.** In G51, a first call that re-reads local files or notes is followed by the first write 2.6 calls sooner [2.3, 2.8] than one that looks at the screen (same agent and task mode); remote reads 1.4 sooner; reading the room only 0.5 sooner. In G38, remote reads (−3.0) and local files (−1.1) lead. Observational: the agent chooses its path.
- **The room (R) is barely consulted** (history-search share +0.002, talk unchanged) and is the slowest re-acquisition path: the scaffold re-shows a room snapshot after the reset, and agents rebuild their *task* state, which lives in their files and screen.

### Interpretation
H44 as posed (busy but unproductive *thrash*, a temperature pulse, a blank slate absorbing the room) is half right. The call-level picture is a **field quench of a context-held task state**: right after the wipe the agent reverts to reading (a baseline field toward re-acquisition), fails a few more commands, writes less, and rebuilds its working state from artifacts over ~3–7 calls, then keeps ramping its output through the rest of the 40-call segment. It does not become more random and does not listen more to other agents. For operators: the cap costs a measurable ~4–10% of output, breaks most command loops, and the cheapest recovery path is pointing the agent at its working files.

## Confirmatory plan
`analysis/confirm.py` (written 2026-10-04 after round 1, dry-run on non-holdout stand-ins, **not run**). Guarded by `--confirm --i-understand-this-uses-the-locked-holdout`; refuses with uncommitted H44 changes; calls `holdout_ledger.check()` per target (all four allowed, all need disclosure). Targets: G43, G45, NE21+NE23 (#46–#50), #51 tail; per-target estimates, DerSimonian–Laird decision.

| | Criterion | Round 1 |
| --- | --- | --- |
| CF1 | Θ_c (forced) pooled > 0.01, CI > 0, > 0 in ≥ 3/4 targets | +0.079 [0.071, 0.086], 9/9 |
| CF2 | Θ_c (voluntary) CI > 0 and Θ_c(F) ≥ 0.5 Θ_c(V) | 0.079 vs 0.057 |
| CF3 | Θ_c (no reset, pos 31) upper CI < 0.01 | −0.011 [−0.016, −0.006] |
| CF4 | real-failure share up after forced resets (CI > 0) | +0.010 [0.006, 0.015] |
| CF5 | no susceptibility rise: reply-rate RR upper CI < 1.10 | 0.97 [0.91, 1.04] |

Confirmed if CF1, CF3, CF4 pass and neither CF2 nor CF5 fails. Reported, not scored: Ω (H15's statistic, its C3 on the same targets), σ, entropy, the coupling-cut DiD (overlaps H08's CF4 concept). Dry run on stand-ins (G41, G42, G39/G40/G44, #51 08-24 → 09-04): all five pass (a plumbing check; the stand-ins are exploration data). **Reuse disclosure:** #45 was run by H02 and H04, NE21+NE23 by H04 (different statistics); H15 (C3), H08 (CF4), H39 (C6) and H46 (C3) plan NE41-adjacent tests on the same targets. Whoever runs first makes the others second users: disclose in all cards and LOG.md before running.

## Caveats
- **Categories are heuristics.** Bash commands are classified by regex in memory (no hand-labelled validation); GUI clicks, scrolls and typing cannot be split into navigation vs production, so "re-acquisition" counts screenshots and reads, not GUI browsing. Write evidence is DQ3's command-text heuristic; DQ4 work commits agree in sign and size.
- **The reference sits on a ramp.** Writes rise and reads fall across every 40-call segment, so Ω depends on the reference (far window −20…−11 here, as in H15); against the no-reset pseudo-erasures the dip would be larger.
- **Θ_c conditions on first-order state.** It removes the simulated spillover of a pure dip (≤ 0.005); real higher-order dependence could leak a little more, but the observed 0.06–0.10 is far above the floor.
- **Paths are observational.** Agents choose what to re-read; strata (agent × task mode) do not remove task-state differences.
- **Replies and pull.** DQ2 labels exist mostly for top-1 candidates; after a reset, new items compete with fewer in-context items, which favours P4b, and it still failed. Statement-level embedding geometry is model-sensitive (DQ5), though bge and gte agree here.
- **Jev v3 windows** (5 min ≈ 15 calls) cannot resolve a 1–5-call transient and are selected for dense activity after a forced reset; they are reported, not used for the verdict.
- **Power and multiplicity.** G37 (368 resets) has 62% synthetic power for the full thrash pattern. 9 periods × ~12 statistics with no correction; the pooled Θ_c, Ω, failure, coupling-cut and loop results would survive any correction, σ (+0.018) and the per-period entropy and pull estimates would not.

## Round 2 redirects
**What the direction is really after:** how much of an agent's productive state lives in its context window rather than in memory or artifacts, and what an operator pays, and gains, each time the scaffold wipes it.
- **H44-R1. Validate the call classifier.** A blind hand-labelled sample of ~300 post-reset and mid-segment calls (re-acquisition vs production vs other), plus the GUI split; recompute Θ_c on the validated labels.
- **H44-R2. The sawtooth and the best cap.** Fit the two-timescale relaxation (first-call spike, ~5-call tail, segment-long write ramp) per lab and model, and ask at which segment length output per call peaks; compare 40-call forced segments with long voluntary ones.
- **H44-R3. What exactly is re-read.** Join post-reset reads to `artifact_mentions`: are they the files touched just before the reset (re-opening, the context store's semantic content) or new ones? This is the Kolchinsky "semantic content" of the context window.
- **H44-R4. Loop breaking as a lever.** Net output of loop-stuck agents across resets vs loop-free ones; does a well-timed voluntary consolidation (or a forced one) pay for its re-acquisition cost when the agent is looping?
- **H44-R5. Why no susceptibility rise.** Test whether the post-reset room snapshot already supplies room context (compare items in the snapshot with items arriving after the reset), and carry the negative result to HH204 (don't expect mismatch thrash to raise susceptibility).
- **H44-R6. Run `confirm.py`** after committing the card and disclosing reuse.

## Notes
- 2026-10-04: card written before any outcome statistic; two-layer design; G36/G38/G51/NE41 native, others replication.
- 2026-10-04 (~07:00 UTC), **build facts (non-outcome):** a forced segment holds **40 calls** (41–42 records: the forced mouse_move marker is not a call and mirrors merge), so the pseudo-erasures are anchored at within-segment call position `pos` 31 (window −20…+10, +10 = pos 40) and 21 (window −10…+20) of segments with ≥ 40 calls; `pos` is the scheme's calls-since-reset (resets = consolidation, session reset, first call of the day), which equals the ledger's `ctx_pos` up to session resets. Events: 21,165 forced, 16,357 voluntary (all lengths; the 10–38 band is a sensitivity), 21,806 pseudo-erasures of each kind. Pseudo-erasures sit in the same forced segments as the forced events (about 10 calls earlier), so the hour-of-day match is built in; the planned reweighting is replaced by a reported KS distance.
- 2026-10-04, **Amendment A1 (synthetic smoke test, before real data):** in the planted field-quench world the cross-sectional entropy H can *fall* (the re-acquisition distribution is more concentrated than the working mix), while the switching rate σ rises robustly. Entropy is therefore not a signature of world (i); it stays an observable (P2), but the field-vs-temperature reading (P6) uses σ and the susceptibility, not H.
- 2026-10-04, **Amendment A2 (synthetic, before real data):** at G51 counts a pure output dip leaks a small positive raw Θ (+0.013 to +0.020, CI above 0) through Markov spillover (fewer writes → fewer write-following categories) and agent-mix shifts. The thrash test therefore uses **Θ_c**, the re-acquisition rise among non-write calls *conditioned on agent × category of the previous call* (Σ_c w_c [R_nw(post5 | c) − R_nw(far | c)]), plus a practical floor Θ_c ≥ 0.01 (pure-dip residual ≤ 0.005). P1's "Θ > 0" and the verdict rule's Θ clause are read on Θ_c; raw Θ is reported alongside.
- 2026-10-04, **after the real run (post hoc, labelled):** added the normalized loop hash (cd/export prefixes dropped, digits collapsed), relaxation fits for writes and for the re-acquisition tail (k ≥ 2), a density-matched v3 comparison (last 5 min before a forced reset) and a past-only pseudo-erasure control (pos 31 without requiring the segment to reach 40 calls; DQ8). None changes a verdict.
- 2026-10-04, **code map:** `scheme/h44common.py` (paths, guards, call categories, command classifier), `scheme/build.py` (calls, events, v3 windows, reply pools, pull pairs; parameterized for confirm), `analysis/h44lib.py` (panels, window stats, Θ_c, curves, relaxation fits, reply rates, pull DiD, DL pool), `analysis/synthetic.py`, `analysis/run_all.py`, `analysis/write_period_folders.py`, `analysis/figures.py`, `analysis/confirm.py`. Data 40 MB.
- 2026-10-04, **cross-notes for other cards (not edited by H44):** H39's post-erasure idle drop is fewer pause calls per call (−0.015 to −0.019) plus wall-clock windows selected for dense activity; H15's write dip replicates (−26%) and DQ4 work commits dip −38%; H08's coupling cut replicates with DQ2 replies (ratio 0.60); HH204 should not expect a susceptibility rise.

## Round 2 (2026-10-05): the sawtooth and the cap, what is re-read, loop breaking, the classifier check
*Scope: H44-R2, R3, R4 and R1 (R1 without any paid API call: the blind labels are mine, made from tool names and arguments). R5 (snapshot) and R6 (confirm run) are not part of this round. Non-reserved data only (`holdout_mask` and the calendar flag, asserted in every script). Round-1 scripts and outputs are unchanged; round 2 lives in new scripts (`scheme/build_r2.py`, `analysis/r2lib.py`, `analysis/r2_synthetic.py`, `analysis/r2_run.py`, `analysis/r2_label.py`, `analysis/r2_figures.py`) and `data/processed/H44-erasure-reacquisition-thrash/r2/`.*

### Round 2 design, predictions and kill rules
*Written 2026-10-05 02:45 UTC, before any round-2 statistic on real data. Facts seen beforehand (none aligned to a reset outcome):*
- *Segments by opening and closing reset (round-1 `calls.parquet`): forced → forced 15,570 (40 calls each), voluntary → voluntary 9,951 (median 21), voluntary → forced 5,182, forced → voluntary 4,613 (median 29). Forced-opened segments that reach 40 calls per period: G36 385, G37 289, G38 1,934, G39 626, G40 688, G41 519, G42 608, G44 265, G51 10,766.*
- *Labs per period: G51 has 9 OpenAI agents (240k calls), plus Anthropic, Google, Moonshot, Zhipu, xAI, Meta, DeepSeek; earlier periods have 1–5 agents per lab.*
- *`artifact_mentions` (action source) resolves files only through URLs (22.6k file mentions in all time); local paths are not resolved. Repos come mostly through `cwd` (precision 0.89).*
- *Cap variation outside regime III: NE22 (200 unseen events) binds in 0.048% of #51 calls (H45), and NE03 (regime-I chat window) left no visible change (H45). Neither gives variation. The usable cap difference is NE11/NE14: computer-use sessions before regime III had no 41-record cap. Non-reserved sessions longer than 40 calls: regime I 3,442 (19 longer than 60), regime II 608 (1 longer than 60). Dense git and DQ3 write evidence exist from #30. Non-reserved arm: G30, G31 (regime I), G33, G35 (regime II).*

**R2. The sawtooth and the best cap.**
- *Curves.* For segments opened by a consolidation, y(k) at segment position k = 1…40 for y ∈ {W (write share), R (re-acquisition share), work commits per call, in-loop share}. **Primary sample: complete sawtooths** (forced → forced, 40 calls, both ends set by the cap). Variants: all forced-opened segments (survival-weighted) and voluntary-opened segments.
- *Model (two timescales plus a ramp):* y(k) = c + β(k − 1) + A₁ e^{−(k−1)/ℓ₁} + A₂ e^{−(k−1)/ℓ₂}, with ℓ₁ ∈ [0.3, 3] and ℓ₂ ∈ [2, 20] (ℓ₂ ≥ 1.5 ℓ₁) on a grid and (c, β, A₁, A₂) by weighted least squares on per-k counts. Nested rivals: M1 (one timescale plus ramp), M0 (two timescales, no ramp). Selection by binomial AIC (ΔAIC ≥ 4). Fits per period, per lab within a period (≥ 300 complete sawtooths), per model in G51 (≥ 300). Agent-day cluster bootstrap (B = 200).
- *Output per call under a cap L:* Y(L) = Σ_{k≤L} Ŵ(k) / (L + c₀), with Ŵ the empirical complete-sawtooth curve and c₀ = 1 summary call per consolidation (variant c₀ = 0; variant per wall-clock minute). L* = argmax Y over L ∈ [5, 40]; the bootstrap gives P(L* = 40), the edge probability. Beyond 40 the fitted model is extrapolated (with a curvature variant γ(k − 1)²), and the regime I/II arm measures W(k) for k up to 60 directly.
- *Voluntary resets as variation (descriptive):* observed output per call of voluntary-closed segments by length bin (10–19, 20–29, 30–39) vs Y(L) predicted from the forced curve. The agent's own reset choice is task-confounded, so this tests the context-held clock, not the cap.
- *Reference-window sensitivity:* Ω (+1…+10) and ΔV (+1…+20) of forced resets against five references: far (−20…−11, round 1), near (−10…−1), the whole closed segment (−40…−1), the agent-day steady state (pos 11–30), and the complete-sawtooth mean (k 1…40). Reported per period.
- **P-R2a (two timescales; prior 0.7):** for R(k), M2 beats M1 (ΔAIC ≥ 4) in ≥ 5 of the 9 periods, with ℓ₁ ≤ 2 calls and ℓ₂ in 3–15 calls; for W(k), M2 or M1 with β > 0 beats M0 (a ramp exists) in ≥ 7/9 periods. *Against:* one timescale suffices for R(k), or no ramp in W(k).
- **P-R2b (no shorter cap helps; prior 0.8):** Y(L) is increasing at L = 40: P(L* = 40) ≥ 0.8 in ≥ 7/9 periods, and the same in every lab fit in G51. *Kill:* P(L* < 35) ≥ 0.8 in ≥ 3 periods (a shorter cap would raise output per call).
- **P-R2c (longer sessions; prior 0.55):** in the regime I/II arm, W over k 41–60 is not below W over k 31–40 (pooled over sessions in each period with ≥ 100 sessions past 40 calls). *Against:* W(41–60) < W(31–40) with CI: output declines in long contexts, so the optimal cap would be finite near 40.
- **P-R2d (the dip is not a reference artifact; prior 0.85):** Ω < 0 (CI) under all five references in ≥ 7/9 periods, and the spread of Ω across references is ≥ 5 points in ≥ 6/9 periods (the reference matters for the size, not the sign). *Kill:* the pooled Ω CI includes 0 under any reference.

**R3. What is re-read.**
- *Objects per call:* (L1, primary) file-path tokens parsed in memory from the bash command text and typed text (tokens with a file extension, or with a slash; last two path components; URLs excluded), stored only as 63-bit hashes; (L2) `artifact_mentions` artifacts (action source, `how` ∈ {url, output, bare}; variant with `cwd`), mapped to calls by agent and time as in round 1.
- *Events:* forced, voluntary and pseudo31 (pos 31) events with ≥ 20 pre and ≥ 10 post calls. Pre set P_e = objects of calls −20…−1. Post read calls = calls in +1…+10 with category local read, notes read or remote read that carry ≥ 1 object.
- *Statistic:* the **re-open share** ρ = share of object-bearing post read calls that touch ≥ 1 object of P_e (ratio of sums over events). Contrasts Δρ_F = ρ(forced) − ρ(pseudo31) and Δρ_V = ρ(forced) − ρ(voluntary); agent-day cluster bootstrap; DerSimonian–Laird pool across periods with ≥ 200 usable forced events. Descriptive: the recency rank of the re-opened object in the pre window (1 = the last object touched before the reset), and the share of post read calls that touch only objects never touched earlier that agent-day.
- *Reading:* in a pseudo-erasure, pre-window objects are still in context, so a read call there has less reason to re-open them. If the context window held "which files", reads right after a wipe re-open the erased objects more often than mid-segment reads do (Δρ_F > 0). Exploration of a new task predicts Δρ_F < 0; habit (agents read the same few files whatever the context) predicts Δρ_F ≈ 0.
- **P-R3a (re-opening; prior 0.55):** Δρ_F > 0 pooled (CI > 0, L1) and > 0 in ≥ 2/3 of the usable periods. *Kill:* pooled Δρ_F ≤ 0 with synthetic power ≥ 0.8 at the planted effect: post-reset reads are not targeted at the erased content.
- **P-R3b (forced vs voluntary; prior 0.6):** Δρ_V > 0 pooled (voluntary resets at task boundaries re-open less). *Against:* Δρ_V ≤ 0.

**R4. Loop breaking as a lever.**
- *Strata* from the pre window −10…−1 (round-1 exact-hash loop flag): **looping** = ≥ 3 in-loop calls; **loop-free** = 0. Events forced and pseudo31 (variant voluntary; variant normalized hash).
- *Net output per event:* ΔW = W(+1…+10) − W(−10…−1) (writes per call; work commits per call as second outcome). **Reset effect in stratum s:** E_s = mean ΔW(forced, s) − mean ΔW(pseudo31, s). **Pays:** E_loop > 0 (on the absolute scale, the output an operator gets). **Lever:** E_loop − E_free > 0, calibrated against a synthetic null in which the reset has the same *relative* dip in both strata (a multiplicative dip shrinks in absolute size where baseline output is low, which an absolute DDD would read as a lever).
- *Operator number:* net write calls (and work commits) per reset for a looping agent over +1…+10, and its sign.
- **P-R4a (the reset costs looping agents less; prior 0.75):** E_loop − E_free > its synthetic multiplicative-null 95th percentile, pooled and in ≥ 2/3 of periods with ≥ 30 looping forced events.
- **P-R4b (the reset pays when looping; prior 0.4):** E_loop > 0 pooled (CI > 0). *Kill for "pays":* E_loop CI entirely below 0: even for looping agents the re-acquisition cost exceeds the gain within 10 calls.
- *Link to R2:* the in-loop share by segment position k (complete sawtooths). Rising loop share with k would make loop breaking a reason for a finite cap.

**R1. Classifier check (blind, no paid API).**
- *Sample:* 300 regime-III non-reserved calls, stratified by classifier category and window: post-reset (+1…+5 after a forced reset) and mid-segment (pos 11–30, no reset in window), 150 each. Quotas per window: 15 each for the eight bash-derived categories (write, notes read, local read, remote read, run, monitor, setup, other) and GUI type, and 15 shared over the tool-name categories (look, GUI, room read, talk, idle). Seed fixed. The sample file shows only shuffled IDs, tool names and arguments (truncated, scratchpad only, never committed); the classifier output sits in a separate key file that I do not open until every label is written.
- *Labels:* the same 14 categories, judged from the command alone (writes = commands that write files, commit, push, post or deploy), plus a GUI split for typed text (navigation: URLs, search terms, short keys; production: prose or code). Clicks carry only coordinates, so they cannot be split; that is a reported limit.
- *Statistics:* agreement and Cohen's κ for the 14 categories and for 3 classes (re-acquisition, production, other), weighted back to the population shares of each stratum; the confusion matrix; **Θ_c(checked)**: Θ_c with each call's re-acquisition indicator replaced by P(true re-acquisition | classifier category, window) from the labels (post-reset rates for the post window, mid-segment rates for the far window), with the label sample resampled inside the bootstrap.
- **P-R1a (classifier adequate; prior 0.7):** 3-class weighted agreement ≥ 0.8 and κ ≥ 0.6. *Against:* below either.
- **P-R1b (Θ_c survives the check; prior 0.85):** Θ_c(checked) > 0.01 with CI > 0 in ≥ 7/9 periods and pooled. *Kill:* pooled Θ_c(checked) CI includes 0.01.

**Synthetic validation first (axis F).** On real call skeletons (real agent-days, segments, events, objects, loop flags): (R2) planted curves with known ℓ₁, ℓ₂, β, including one world with an interior L* = 25 and one with a monotone ramp, to check recovery and the edge rule; (R3) planted re-opening (forced read calls draw from P_e with probability q + 0.15) vs null (same q), with real pre-set sizes; (R4) a multiplicative-dip null and a planted loop-breaking world. A statistic is read only where its synthetic size is ≤ 0.10 and its power ≥ 0.8; otherwise it is "inconclusive".

**Estimates.** Rows `r2_*` per period via `write_estimates`, role `replication` (G51 and G38 natives keep `native` for their native statistics).

### Round 2 synthetic validation (axis F; run 2026-10-05 02:52–03:01 UTC, before any round-2 statistic on real data)
`analysis/r2_synthetic.py` → `r2/synthetic.json`. Real skeletons: complete sawtooths of G51 (353,680 calls), G38 (67,720) and G37 (9,640); real events, real pre-window object sets and real loop strata. Agent and agent-day multipliers make the counts overdispersed (dispersion ĉ 1.2–2.5). 30 replicates per world (R3: 30), cluster bootstrap B = 100–200.

**R2 (rates over replicates; G51 / G38 / G37).**

| Planted world | M2 beats M1 (ΔAIC ≥ 4) | β (ℓ₂ ≤ 12) CI > 0 | P(L* = 40) ≥ 0.8 | P(L* < 35) ≥ 0.8 |
| --- | --- | --- | --- | --- |
| W: two timescales + ramp (β 0.0006) | 0.83 / 0.10 / 0.00 | 0.93 / 0.40 / 0.23 | 1.00 / 1.00 / 0.37 | 0 / 0 / 0 |
| W: one timescale + ramp | 0.00 / 0.00 / 0.03 | 1.00 / 0.20 / 0.07 | 1.00 / 0.93 / 0.47 | 0 / 0 / 0 |
| W: two timescales, no ramp | 0.67 / 0 / 0 | **0.03** / 0.03 / 0.00 | 0.97 / 0.63 / 0.00 | 0 / 0 / 0.03 |
| W: decline, planted L* = 34 | 1.00 / 1.00 / 0.73 | 0 (CI < 0: 1.00) | 0 / 0 / 0 | 0.37 / 0.20 / 0.37 |
| W: decline, planted L* = 25 | 1.00 / 1.00 / 0.93 | 0 (CI < 0: 1.00) | 0 / 0 / 0 | **1.00 / 1.00 / 1.00** |
| R: spike + tail (two timescales) | **1.00** / 0.37 / 0.03 | — | — | — |
| R: spike only (one timescale) | **0.03** / 0.00 / 0.00 | — | — | — |

Readings:
1. The two-timescale test (M2 vs M1) has size ≤ 0.03 and power 0.83–1.00 only at G51 counts (≈ 10,000 sawtooths). At G38 counts power is 0.10–0.37.
2. The ramp cannot be read from M2 vs M0. With ℓ₂ free up to 20 calls, a slow exponential mimics the ramp, and "ramp" wins in only 0.1–0.2 of ramp worlds even at G51. β read from the M2 fit with ℓ₂ ≤ 12 calls has size 0.03 and power 0.93–1.00 at G51, but 0.07–0.40 in smaller periods.
3. "No shorter cap helps" (L* at the 40-call edge) holds in any world with a dip and no late decline, with or without a ramp. The edge rule therefore tests "no late decline", not the ramp. The kill rule detects a decline with an optimum at L* = 25 in every replicate at every size, and never fires in ramp worlds.

**R3 (re-open share; G51 / G38 / G37).** Under the recency null the raw contrast Δρ_F is biased *negative*: mean −0.018 / −0.022 / −0.012, with CI < 0 in 1.00 / 0.27 / 0.00 of replicates. Pseudo-erasure pre windows sit inside a running segment, so their objects carry more recency weight (frac 0.80 vs 0.77 at G51). The **recency-adjusted excess** (observed contrast minus q̂·Δfrac, q̂ fitted on pseudo31) has mean −0.002 / −0.009 / −0.005, CI > 0 in 0 / 0 / 0 and CI < 0 in 0.07 / 0.13 / 0.07 of null replicates. Its power at δ = 0.15 is 1.00 / 1.00 / 0.73 (mean excess +0.07).

**R4 (loop lever).** Periods with ≥ 30 looping forced events: G36 (32), G38 (170), G39 (44), G40 (49), G41 (68), G51 (741). Under the multiplicative-dip null:
- The absolute DDD is biased negative at G51 (mean −0.016, q95 −0.004). Its null q95 is +0.012 at G38 and +0.04 to +0.08 in the small periods.
- Against the null q95, power to detect planted loop breaking is 1.00 (G51), 0.70 (G38) and about 0.2–0.5 elsewhere.
- E_loop > 0 ("pays") has power 0.40 at G51 even with strong planted loop breaking, because the re-acquisition dip offsets the gain.
- The log-ratio DDD is unbiased under the null (CI > 0 in 0.00–0.03) and has power 1.00 at G51.

### Amendments (2026-10-05 03:01 UTC, after the synthetic validation, before any round-2 statistic on real data)
- **A3 (ramp).** The ramp clause of P-R2a is decided by β from the M2 fit with ℓ₂ ≤ 12 calls, not by M2 vs M0 (reading 2). It passes if β CI > 0 in G51 and the pooled β CI > 0, with β > 0 in ≥ 7/9 periods (sign count; the small periods have no per-period power).
- **A4 (R3 decision).** P-R3a and P-R3b are decided on the recency-adjusted excess (excess_FP, excess_FV). The raw Δρ is reported alongside. The kill rule applies to the pooled excess_FP; power is ≥ 0.8 at G38 size and above.
- **A5 (where a statistic is read).** The two-timescale clause of P-R2a is read in G51 only (power ≥ 0.8). Elsewhere, and in the per-lab and per-model fits, the fitted parameters (ℓ₁, ℓ₂, β, A₁, A₂) are reported as phase-diagram coordinates without a model decision. The edge clause of P-R2b is read where its synthetic pass rate is ≥ 0.8 (G51, G38); the kill rule is read everywhere. P-R4a is decided on G51 (power 1.00) and on the pooled DDD over periods with ≥ 30 looping forced events. The per-period counts are descriptive. The log-ratio DDD is reported as a calibrated variant.
- **A6 (P-R4b).** A failure of E_loop > 0 is "inconclusive" (power 0.40), not "failed". The kill rule (E_loop CI entirely below 0) stands.

### Round 2 outcome vs prediction
*Run 2026-10-05 03:03–03:13 UTC (`analysis/r2_label.py` → `r2/r1_check.json`; `analysis/r2_run.py` → `r2/G<NN>/r2_results.json`, `r2/long_arm.json`, `r2/pooled.json`). Non-reserved data only. Decision rules as amended (A3–A6). Pooled values are DerSimonian–Laird over periods (CLAUDE.md exception (c)); per-period values are in the table below.*

| Prediction | Observed | Verdict |
| --- | --- | --- |
| **P-R1a** classifier: 3-class agreement ≥ 0.8, κ ≥ 0.6 | 300 blind labels, population-weighted. 3 classes: agreement 0.92, κ 0.89. Re-acquisition vs not: 0.95, κ 0.87, precision 0.94, recall 0.87. All 14 categories: 0.86, κ 0.84. | **pass** |
| **P-R1b** Θ_c on checked labels > 0.01 in ≥ 7/9 and pooled | **+0.106 [0.089, 0.122]**, 9/9. With mid-segment label rates in both windows: +0.072 [0.067, 0.078], 9/9. With typed navigation counted as re-acquisition: +0.090 [0.072, 0.108]. Round-1 classifier: +0.079. | **pass** |
| **P-R2a** two timescales in R(k) (G51, A5) | ΔAIC(M2 − M1) = +104. The spike lasts one call (ℓ₁ at the 0.3 grid floor); the tail has ℓ₂ = 8.2 [5.8, 11.8] calls. Elsewhere unpowered: G39 +12, G41 +9, others < 2. | **pass** (G51) |
| **P-R2a** ramp in W(k) (A3: β CI > 0 in G51 and pooled) | Pooled β +0.0004 [0.0001, 0.0006] per call, positive in 8/9 periods. **G51 +0.0002 [−0.0002, 0.0005]**. The rise saturates: the slow write relaxation has ℓ₂ = 8.5 [5.9, 11.1] calls pooled. | **failed** (no segment-long linear ramp) |
| **P-R2b** no shorter cap helps (edge in G51, G38; kill everywhere) | P(L* = 40) = 1.00 in G51 and 0.50 in G38 (flat curve). Kill not met: the highest P(L* < 35) is 0.74 (G37, write share 0.03). **Y(20)/Y(40) = 0.88 [0.85, 0.91]**, below 1 in 9/9 periods (CI < 1 in 8/9). Per wall-clock minute, P(L* = 40) ≥ 0.83 in 9/9. | **pass** (G51); G38 flat |
| **P-R2c** longer sessions (regime I/II arm) | W(41–60) − W(31–40) = +0.04 to +0.15 (CI > 0) in G30, G31, G33 and G35. But sessions longer than 40 calls end within about 50 calls, so k 41–60 holds the end-of-session write burst. Trimming the last 10 calls leaves 1–23 calls. | **inconclusive** (confounded) |
| **P-R2d** dip not a reference artifact | Pooled Ω < 0 under all five references: far −26%, near −31%, whole segment −20%, steady state −32%, cycle mean −11% [−18, −4]. All five CIs < 0 in 5/9 periods; the cycle-mean reference includes 0 in G37, G38, G44 and G51. The spread across references is ≥ 9 points in 9/9 periods. ΔV per reset: −0.19 (whole) to −0.59 (near, steady) write calls; +0.07 [−0.04, +0.18] against the cycle mean. | **mixed** (sign holds against every pre-reset window; size depends on the reference) |
| **P-R3a** re-opening of erased files (recency-adjusted, A4) | Excess vs no reset −0.039 [−0.085, +0.007], positive in 2/9 periods. G51 +0.001 [−0.015, 0.017]; G38, G40 and G41 below 0 (CI). Raw re-open share: forced 0.60 [0.53, 0.67], no reset 0.66 [0.57, 0.75]. Artifact level (L2): +0.024 [−0.012, 0.061]. | **failed** (kill met: powered ≥ 0.8) |
| **P-R3b** forced vs voluntary | Excess **+0.040 [0.017, 0.062]**, positive in 8/9 periods. | **pass** |
| **P-R4a** reset costs looping agents less (G51 vs null q95; pooled) | G51 DDD −0.028 [−0.070, +0.003], below its null q95 (−0.004). Pooled −0.027 [−0.076, +0.022]. Log-ratio variant +0.23 [0.10, 0.36], 6/6: looping agents lose a smaller *fraction* (G51 −19% vs −32%), from a write base 3 times higher. | **failed** (absolute); relative variant positive |
| **P-R4b** reset pays when looping | E_loop **−0.086 [−0.151, −0.022]** writes per call over +1…+10 (6 periods), G51 −0.073 [−0.114, −0.042]. Work commits −0.037 [−0.063, −0.010] per call. | **failed** (kill met) |
| Loop accumulation (R2 link) | In-loop share rises over calls 1–10, then is flat: slope over k 11–40 +0.0001 [−0.0000, +0.0003] per call pooled (CI > 0 only in G38). | no accumulation |

**Round-2 numbers by period** (complete forced sawtooths; R3 on file-path objects; E_loop where ≥ 30 looping forced events):

| Period | complete sawtooths | R tail ℓ₂ (calls) | W slope β (per call) | Y(20)/Y(40) | P(L* = 40) | Ω range over 5 references | re-open excess vs no reset | E_loop (looping events) | Θ_c checked |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| G36 | 319 | 11.8 [2.0, 11.8] | +4.8 [−12.0, +24.1] ×10⁻⁴ | 0.89 [0.83, 0.96] | 0.83 | −25% to −15% | −0.046 [−0.133, +0.036] | +0.108 [−0.035, +0.195] (32) | +0.100 [+0.051, +0.162] |
| G37 | 241 | 8.2 [2.0, 11.8] | +2.4 [−6.0, +15.2] ×10⁻⁴ | 1.02 [0.87, 1.21] | 0.23 | −37% to +13% | −0.114 [−0.290, +0.044] | n/a (10 < 30) | +0.091 [+0.046, +0.142] |
| G38 | 1,693 | 11.8 [2.0, 11.8] | +4.2 [−0.0, +8.5] ×10⁻⁴ | 0.93 [0.89, 0.97] | 0.50 | −27% to +2% | −0.119 [−0.174, −0.070] | −0.020 [−0.084, +0.022] (170) | +0.091 [+0.056, +0.131] |
| G39 | 569 | 11.8 [4.8, 11.8] | +14.0 [+3.2, +25.0] ×10⁻⁴ | 0.85 [0.81, 0.88] | 0.96 | −32% to −10% | −0.032 [−0.070, +0.009] | −0.182 [−0.235, −0.121] (44) | +0.125 [+0.082, +0.182] |
| G40 | 583 | 4.1 [2.4, 11.8] | +12.1 [+0.6, +26.5] ×10⁻⁴ | 0.88 [0.85, 0.91] | 1.00 | −31% to −20% | −0.084 [−0.134, −0.028] | −0.156 [−0.215, −0.084] (49) | +0.115 [+0.062, +0.182] |
| G41 | 441 | 11.8 [3.4, 11.8] | −2.6 [−19.9, +12.3] ×10⁻⁴ | 0.82 [0.78, 0.87] | 1.00 | −41% to −25% | −0.093 [−0.146, −0.034] | −0.146 [−0.220, −0.081] (68) | +0.154 [+0.088, +0.235] |
| G42 | 563 | 11.8 [2.0, 11.8] | +7.1 [−5.8, +19.4] ×10⁻⁴ | 0.84 [0.76, 0.91] | 0.98 | −41% to −15% | +0.123 [+0.065, +0.173] | n/a (18 < 30) | +0.104 [+0.072, +0.144] |
| G44 | 191 | 11.8 [2.0, 11.8] | +6.3 [−20.2, +26.9] ×10⁻⁴ | 0.84 [0.73, 0.94] | 0.60 | −37% to −15% | −0.042 [−0.131, +0.043] | n/a (13 < 30) | +0.101 [+0.039, +0.174] |
| G51 | 8,842 | 8.2 [5.8, 11.8] | +2.0 [−1.5, +5.5] ×10⁻⁴ | 0.91 [0.89, 0.92] | 1.00 | −33% to −2% | +0.001 [−0.015, +0.017] | −0.073 [−0.114, −0.042] (741) | +0.109 [+0.065, +0.160] |

ℓ₂ = 11.8 is the 12-call cap of the fit (Amendment A3): the tail is resolved only in G51 and G40.

### Round 2 results
**1. The classifier holds (R1).**
- On 300 blind labels, the re-acquisition class agrees with my labels in 95% of population-weighted calls (κ 0.87).
- The errors sit inside the re-acquisition class or at its edge:
  - "Notes read" catches project documents whose names contain plan, session or context (20 of 30 sampled calls). Both labels count as re-acquisition.
  - Python scripts that fetch web pages are "run" (20–27% of run calls are reads).
  - Echo narration and touch/mkdir sit in "setup".
- Window-specific label rates *raise* Θ_c to +0.106. The conservative variant, mid-segment rates in both windows, gives +0.072 [0.067, 0.078]. Either way the round-1 value (+0.079) is not a classifier artifact.
- Typed text after a reset is navigation (URLs, search terms, game commands) in 47% of GUI-type calls (73% mid-segment; n = 15 each). Clicks carry only coordinates and cannot be split.

**2. The sawtooth has two timescales and no linear ramp (R2).**
- Re-reading spikes for exactly one call (G51 R: 0.46 at k = 1, then 0.25), then decays with ℓ₂ ≈ 8 calls to a plateau near 0.21.
- Writes drop to 0.06 at k = 1, recover most of the way by k ≈ 5 (0.10) and approach a plateau (0.13) with ℓ ≈ 8–10 calls.
- Round 1's "segment-long write ramp" is the end of this slow relaxation. In G51, where the slope test has power, there is no residual linear slope.
- The same shape holds in each lab of G51 (Anthropic, Google, OpenAI, Moonshot). Y(20)/Y(40) is below 1 for 10 of the 11 G51 models with ≥ 300 sawtooths.
- One model reverses: gpt-5-2025-08-07 writes most right after a reset, so its Y(20)/Y(40) = 1.20 [1.11, 1.32]. The best cap is model-dependent.

**3. Halving the cap would cost about 12% of output per call; longer caps are not identified.**
- Y(L) rises up to L = 40 in every well-sampled period: shorter caps are worse (Y(20)/Y(40) = 0.88, Y(30)/Y(40) = 0.95 [0.94, 0.96]). This also holds per wall-clock minute, because a consolidation takes about 4.5 min (257–315 s) against 18–26 s per call.
- Beyond 40 the data are silent. Curvature fits extrapolate to optima from 44 to more than 200 calls.
- The regime I/II sessions that ran longer than 40 calls end within about 50, so their late calls carry the end-of-session write burst. Loops do not accumulate with segment position, so loop growth gives no reason for a finite cap.
- The restart dip itself transfers: in regime I/II sessions, writes over the first 10 calls are 0.48–0.52 of calls 11–40 (descriptive; a different scaffold).

**4. The size of the dip depends on the reference (R2, explicit).** Against windows before the reset the dip is −20% (whole closed segment) to −32% (agent-day steady state). Round 1's far window gives −26%. Against the mean of the 40-call cycle, which contains the dip, it is −11%. The cost per reset ranges from 0.19 to 0.59 write calls. The cost of the sawtooth relative to the late-segment plateau, 1 − ⟨W(1…40)⟩/⟨W(31…40)⟩, is 5–15% of write calls (G51 8.5%; point values, no CI). Round 1's "4–11% of output" sits inside this band. Quote the reference with any cap cost.

**5. Agents re-read their working set, not the erased files in particular (R3).**
- 60% of post-reset read calls touch a file from the last 20 calls before the wipe. The file is usually the most recent one (median rank 1–4 calls; 60–91% within the last 5).
- Mid-segment reads do this as often or more (0.66), and the recency-adjusted excess is −0.04 [−0.09, +0.01].
- The wipe raises the *volume* of re-reading (Θ_c), not its *targeting*.
- After a voluntary reset, reads go to the erased working set less often (excess +0.04 [0.02, 0.06]). Voluntary resets mark task boundaries; forced ones interrupt a task that the agent then resumes from the same files.
- In Kolchinsky–Wolpert terms: the semantic content that the wipe removes, as file identity, is the agent's current working set. The agent recovers it by its ordinary working-set habit, which the wipe amplifies.

**6. A wipe does not pay as a loop breaker (R4).**
- Over the next 10 calls a forced reset costs a looping agent 0.86 write calls (E_loop −0.086 per call), against 0.57 for a loop-free agent. The absolute difference is not significant.
- The round-1 loop flag mostly marks *productive* repetition. Looping pre-windows write at 0.43 per call vs 0.13 (G51), and 617 of 741 looping G51 events contain writes (repeated appends, commits, deploys).
- Post hoc, on stuck loops only (≥ 3 in-loop calls, no write): the reset is neutral (+0.011 [−0.015, 0.037], G38 and G51 only, 220 events). Breaking a productive loop costs 0.15 writes per call (−0.149 [−0.201, −0.097]).

### Round 2 scorecard (old → new)
| Axis | Round 1 | Round 2 | Why |
| --- | --- | --- | --- |
| A mapping | 1 | 1 | Classifier validated blind (κ 0.87 on the re-acquisition class), but clicks cannot be split into navigation and production; regime III only for the event study |
| B assumptions | 1 | 1 | Within-segment non-stationarity is now a measured two-timescale relaxation (spike 1 call, tail ≈ 8 calls, slow write recovery ≈ 8.5 calls), not a ramp; Θ_c still first-order |
| C adequacy | 1 | 1 | Unchanged nulls; checked labels and five references keep the sign |
| D unfitted predictions | 1 | 1 | New passes: two timescales (G51), cap edge (G51), Y(20)/Y(40) < 1 in 9/9, forced > voluntary re-opening. New fails: linear ramp, targeted re-reading, loop lever |
| E interventional | 1 | 1 | Forced resets (quasi-random cap timing) remain the intervention; the NE11/NE14 cap difference is confounded by session ends |
| F identifiability | 1 | **2** | Round-2 synthetic on real skeletons for every estimator, with size and power; it found three design flaws before real data: the ramp is unidentified by AIC, raw re-open contrasts are biased under recency, and the absolute DDD is biased under a multiplicative dip |
| G ground truth | 1 | **2** | The hand-labelled ground truth the card lacked now exists (300 blind labels; single rater, Claude) and agrees with the classifier (0.95) |
| H comparative | 1 | 1 | Beats the classifier-artifact and reference-artifact rivals; the "targeted restoration" and "loop lever" readings lose to "working-set habit" and "productive loops" |
| I transfer | 1 | 1 | Restart dip of about 50% in regime I/II sessions (descriptive); reserved data not run |

**Round 2 scorecard: A1 B1 C1 D1 E1 F2 G2 H1 I1.**

**Rivals after round 2.** R0 (no effect), R1 (pure restart overhead), R2 (temperature pulse) and R3 (task boundary) stay rejected; R1 is now rejected on checked labels. New rivals: classifier artifact (beaten, P-R1b); reference artifact for the dip (beaten for the sign, not the size); targeted restoration of erased files (beaten by working-set habit, which is a rival to H44's original story); loop breaking pays (rejected).

**Operator values.** Keep the context cap at 40 calls or more: halving it to 20 cuts output per call by about 12% (Y(20)/Y(40) 0.88 [0.85, 0.91]). Do not use forced consolidation to break loops: it costs a looping agent about 0.9 write calls per reset over the next 10 calls (E_loop −0.086 [−0.151, −0.022]).

**Claim that stands:** In regime III (9 non-reserved periods), a forced context wipe triggers a one-call re-reading spike with an about-8-call tail (Θ_c +0.106 [0.089, 0.122] on blind-checked labels, 9/9 periods) and a write dip of −20% to −32% depending on the reference window, and a 20-call cap would yield 12% less output per call than the 40-call cap (Y(20)/Y(40) 0.88 [0.85, 0.91]). *Excluded:* a segment-long linear write ramp (withdrawn; the rise saturates with ℓ ≈ 8.5 calls); any optimum beyond 40 calls (not identified; the regime I/II arm is confounded by session ends); targeted re-reading of erased files (failed; working-set habit); loop breaking as a lever (failed; E_loop −0.086 [−0.151, −0.022]); the stuck-loop result (post hoc, 2 periods); the gpt-5 reversal (post hoc, one model).
