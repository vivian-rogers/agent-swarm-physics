# H44: Erasure makes agents busy but unproductive

**Status:** exploratory round 1 done (2026-10-04, non-holdout; 9 regime-III periods + NE41). **Re-acquisition yes, thrash no.** A forced context erasure is followed by a burst of re-reading (re-acquisition share of calls 0.22 → 0.47 at the first call in G51; +0.079 [0.071, 0.086] among non-write calls over the first five calls, conditioned on agent and previous call, 9/9 periods) and a write dip (−26%, work commits −38%), with fewer pauses and +1 pp real failures. No temperature pulse (entropy falls slightly), no extra susceptibility to new room content (reply rate per new item RR 0.97; content pull ≈ 0), but coupling to pre-erasure items falls (ratio 0.60). Erasures break command loops (OR ≈ 0.1); re-reading files restores output fastest; memory dose does nothing. Predictions and synthetic validation came first. `confirm.py` written, dry-run only, **not run**.
**Fields:** nonequilibrium statistical mechanics (kinetic Ising / Glauber response, local field quench vs temperature pulse), information theory and physics of life (Kolchinsky–Wolpert semantic information of stores), dynamics (event studies, relaxation)
**Literature:** [Kolchinsky & Wolpert 2018](../../literature/kolchinsky-2018-semantic-information-autonomous-agency.md) (value of information under a scramble; coarse-graining interventions); [Sowinski et al. 2023](../../literature/sowinski-2023-semantic-information-resource-gathering-agents.md) (viability vs scrambled information); [Bartlett et al. 2025](../../literature/bartlett-2025-physics-of-life-information-roadmap.md) (information import as maintenance)
**Definitions used** (`physics-models/DEFINITIONS.md`): Regime; Action (turn-merged) as implemented by the DQ1 call grouping; Context fill (H30: `ctx_pos`); Exposure (turn read-out) via the DQ1 context ledger; Receiving call (H43); Semantic information (natural-scramble variant) (H15); Field effect / Catalytic effect (H39); Entropy (of behavior); Influence coupling (content pull) (H29). New named variants, defined below and proposed for DEFINITIONS.md: **call category (H44)**, **re-acquisition share**, **thrash index Θ**, **pseudo-erasure**, **reply rate per visible message (pre/post read)**.
**From:** HH156 in `hypotheses/hypohypotheses/HYPOHYPOTHESES.md` · **Models:** `physics-models/02-nonequilibrium-ising/` (kinetic multinomial spin with a context-held self-field; response vs fluctuation), `physics-models/04-semantic-information/` (which store the erasure scrambles)
**Data inputs (shared tables first):** DQ1 `context_ledger_turns`, `context_ledger_items`, `call_windows`; `actions` + `actions_bash_head_fixed`; DQ3 `turn_outcomes` (real failures, write evidence; command text read in memory only, never stored) and `behavior_states_v3`; DQ4 `work_commits`; DQ2 `reply_pairs`; DQ5 `statements_white32_bge_small` (+ gte for robustness); `memory_stats`; `period_units`; `calendar`. Not used: `activity_bins` (join bug) and `outages` (inherit it).

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
| F identifiability | synthetic recovery with village sampling; robust to preprocessing | 1 | `analysis/synthetic.py`: three worlds on real call skeletons, 100% correct at G51 and G38 counts, G37-size thrash detected 62% (missed output dip, never a false thrash); it found that the raw Θ calls a pure dip "thrash" at G51 scale (Amendment A2). Reply estimator recovers planted effects (null log DiD −0.01, cover 95%). Robust to the normalized loop hash, bge vs gte, past-only controls; classifier not cross-validated. |
| G ground truth | agrees with known structure | 1 | The cap appears exactly (40-call segments); the first post-reset call rarely writes (H15); write-call and DQ4 work-commit dips agree (−26% vs −38%); voluntary resets follow a status message (G51 talk share 0.07 → 0.17 at the last call), as consolidating at a task boundary should. No hand-labelled re-acquisition ground truth. |
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
