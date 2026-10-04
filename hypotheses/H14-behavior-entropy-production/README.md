# H14: Entropy production of behavior-state sequences: per-family arrows of time, and collective irreversibility

**Status:** exploratory round 1 done (2026-10-03; non-holdout only; predictions written before any real-data run). **Mostly refuted as posed, with a descriptive residue.**
- *Refuted or unsupported:* per-family arrows of time (HH19: no lab effect, stratified p = 0.89); a collective term (HH67: null in every regime-III period after Holm); the predicted work cycles (P5: 0/8).
- *Supported:* every agent's *fine* action-class sequence is irreversible (80–100% of agents in 9/9 periods). Regime-I behavior is 7–29× more irreversible per transition than regime-III behavior. Coarse arrows are small (0.002–0.010 nats/transition), carried mostly by the scaffold's consolidation boundary, and agent-specific (a weak trait, p = 0.02 / 0.0005).
- **Verdicts:** G27 and G51 mixed, the other 7 periods failed (P2's 80% bar).
- `analysis/confirm_h14.py` is written and dry-run; **not run** on the holdout.
Promoted 2026-10-03 by Vivian from shortlist 2.
**Fields:** thermodynamics, stat mech, info theory
**Origin:** HH19 + HH67 (shortlist 2, item 6), with HH56 (`../hypohypotheses/HYPOHYPOTHESES.md`; `../promotion-shortlist.md`)
**Literature:** [Aguilera, Ito & Kolchinsky 2026](../../literature/aguilera-2026-entropy-production-nonequilibrium-maxent.md) (AIK estimator)
**Definitions used** (`physics-models/DEFINITIONS.md`): Regime; Action; Agent state (categorical: action class); Population (roster); Entropy production / irreversibility, in two named variants proposed here (to be added to DEFINITIONS.md by its owner):
- **"entropy production (Markov pair-KL on categorical behavior states)"**: for one agent, the KL divergence between the forward and time-reversed pair distribution p(x_t, x_{t+1}) of its state sequence, i.e. the AIK bound with the antisymmetrized transition indicators as observables. Cross-fitted by day; reported per transition and per agent-hour; null = detailed-balance surrogate.
- **"entropy production (AIK cross-agent bound on categorical states)"**: on a common 1-min grid, the AIK bound with single-agent transition indicators plus cross-agent lagged antisymmetric observables (mean-field and pairwise, defined below); the collective term is the increase over the single-agent bound. Null = cross-day surrogate (as in H05's variant).

## Question
1-minute activity spins were too coarse for entropy production (H05). With richer categorical states (action classes now; Jev behavior states later), how irreversible is each agent's behavior? Does each model family have its own arrow of time (HH19)? Is the swarm's joint irreversibility more than the sum over agents (HH67)? Where do the probability currents run (HH56)? Practical payoff: irreversibility as a measure of goal-directed, driven work versus aimless activity.

## Model
**From:** `physics-models/02-nonequilibrium-ising` generalized to kinetic Potts states (`physics-models/10-potts`), with the Aguilera–Ito–Kolchinsky MaxEnt estimator and plug-in Markov EP with finite-sample bias correction. H05's validated `analysis/ep.py` is imported, not copied (cross-fitted Newton-step bound `ep_gauss_crossfit`, held-out exact dual `ep_heldout`).
- **Single agent:** x_t ∈ {1…q}, a stationary Markov chain within a goal period. Σ_i = Σ_{a,b} π_a P_ab ln(π_a P_ab / π_b P_ba) per transition. The AIK bound with observables g_ab(t) = 1[x_t=a, x_{t+1}=b] − 1[x_t=b, x_{t+1}=a] (a < b) equals this pair-KL; it lower-bounds the EP rate of any stationary process with these marginals (Roldán–Parrondo hierarchy), so a non-Markov agent is under-estimated, not over-estimated.
- **Swarm:** kinetic Potts with parallel updates, P(x_i' = a | x) ∝ exp(h_i^a + K_i^{a, x_i} + Σ_j J_ij^{a, x_j}). Non-symmetric self-kernels K_i give single-agent cycles; J_ij^{ab} ≠ J_ji^{ba} gives collective irreversibility. Hierarchy Σ_1 ≤ Σ_{1+2} ≤ Σ.
- **Hypothesis-specific variant:** 6 coarse states (below). The time base is the agent's own turn sequence (event time) for single-agent questions, and a common 1-min grid for collective ones.

## Data scheme (`scheme/build_states.py`)
- **Inputs (shared tables, non-holdout days only):** `actions` (computer-use turns), `events_core` (agent events), `calendar`, `roster`. Holdout days are never read by the scheme; the confirmatory script builds them in memory.
- **Record stream per agent:** computer-use turns ∪ agent events, sorted by time, with scaffold artifacts removed (pre-specified from structural checks, see Notes):
  - mirror turns dropped: `pause` (PAUSE), `send_message_back_to_chat` (AGENT_TALK), `search_history` (SEARCH_HISTORY), `move_to_room` (ENTER_ROOM) when the event by the same agent is within 2 s; the event is kept;
  - the scaffold-forced `mouse_move` that opens a fresh computer context (the first computer-use turn after a CONSOLIDATE or START_USING_COMPUTER event) is dropped;
  - regime-I WAIT is logged at the end of the gap: in event time the order is right; on the minute grid the gap before a WAIT is idle. CONSOLIDATE is likewise logged at completion (~3 min after the previous turn): on the minute grid the gap before it is consolidate.
- **Fine action classes (`act`, per record, 11):** shell (bash); click (all pointer clicks, drags, non-forced mouse_move, cursor_position); scroll; look (screenshot, get_pixel_coords_of_element, view_clipboard, computer-use wait); type (type, key, hold_key); chat (AGENT_TALK); idle (PAUSE, WAIT); consolidate (CONSOLIDATE); search (SEARCH_HISTORY); session (START/STOP_USING_COMPUTER); other (none, other, room moves, requests, outreach approvals, sign-in). Rare-class rule: within a period, a class with < 1% of the period's records is merged into other.
- **Coarse states (`coarse`, 6):** browse = click + scroll + look; type; shell; chat; idle; consolidate = consolidate + search + session (the regime-invariant memory/session boundary). `other` records are removed from coarse sequences (no behavior is recorded in them).
- **Lumped states (`lump4`, for currents):** work = browse + type + shell; chat; idle; consolidate.
- **Minute grid (`coarse_min`):** each agent-minute of the day's window (same grid as `activity_bins`: roster agents, minute = ⌊(t − win_start)/60 s⌋) gets chat if any chat record; else consolidate if any consolidate-class record or inside a consolidation gap; else the majority of {shell, type, browse} turns (ties shell > type > browse); else idle (declared pause, WAIT gap, or no record).
- **Any categorical state table** (agent, t or bin, state) runs through the same pipeline (`analysis/h14lib.py: load_state_table`; `run_period.py --states <parquet>`), so the Jev 10-state labels per 5-min window can replace these states without code changes.
- **Output:** `data/processed/H14-behavior-entropy-production/` (`states_turn.parquet`, `states_min.parquet`, `scheme_audit.json`, `synthetic/`, one subfolder per goal period `G<NN>/` with `agents.parquet` and `results.json`, `summary_round1.json`, `confirm_dryrun/`), with `_provenance.json`. Period READMEs and figures live in `goalperiod-subhypotheses/G<NN>/`.

## Candidate goal periods
Regime III non-holdout (#37–#42, #44), #51 non-holdout days (07-06 → 09-04; collective analysis on the constant-roster block 07-24 → 08-28), and #27 (regime I, 10 days, N = 10) as the regime comparison. Per family within periods.

## Links to other hypotheses
H05 (EP on spins, a null at this sampling; estimator code); H09 (thermodynamics framing; E2 event-level currents, E7 crude collective pass); HH56 (probability currents in work cycles); H01 (a collective arrow of time is a superagent signature); H13 (family fields).

## Observables
*Written 2026-10-03, before any real-data run.* Per goal period; agents need ≥ 2 days and ≥ 300 transitions in the period (≥ 1,000 for the "per-agent test" counts below).
- **O1 single-agent EP Σ_i.** Primary: cross-fitted Newton-step bound (H05 `ep_gauss_crossfit`, day folds, k = min(5, days)) on the antisymmetrized transition indicators of the agent's `coarse` turn sequence; nats per transition, and per agent-hour (× transitions per hour of the agent's day windows). Companions: plug-in pair-KL (pairs with both counts > 0), chi-square bias-corrected plug-in, held-out exact dual (`ep_heldout`). Also on `act` turns and on the `coarse_min` grid.
- **O2 excess** Σ_i − mean(null) and p_i against the detailed-balance surrogate (N2).
- **O3 family statistics.** η²_lab of per-agent excess Σ_i (labs from `roster.lab`; the fine-tuned leader excluded), the Anthropic − OpenAI mean difference, both with within-period label permutations; a stratified permutation across periods; agent-rank stability across periods (Kendall's W, mean pairwise Spearman); the lab effect adjusted for shell share and log(transitions).
- **O4 collective term** on the `coarse_min` grid, fixed agent set per period (on the roster all period days), first and last 5 min of each day dropped. Observables:
  - single: each agent's 15 antisymmetrized transition indicators;
  - mean-field (MF): g_i^{ab}(t) = 1[x_i(t+1)=a]·m_{−i}^b(t) − 1[x_i(t)=a]·m_{−i}^b(t+1), a, b ∈ {work, chat}, m_{−i}^b the fraction of the other agents in b (4 per agent);
  - pairwise (PW): g_ij^{c}(t) = s_i^c(t+1)s_j^c(t) − s_i^c(t)s_j^c(t+1), s^c = ±1 indicator of c ∈ {chat, work} (2 per pair).

  Σ_1 = Newton bound on all single observables jointly; ΔΣ_MF = Σ_{1+MF} − Σ_1; ΔΣ_PW = Σ_{1+PW} − Σ_1; ratio ΔΣ/Σ_1.
- **O5 currents** (`lump4` turns): net flux F_ab = (n_ab − n_ba)/n; the four triangle cycle affinities A_abc = ln(n_ab n_bc n_ca / (n_ac n_cb n_ba)) (pseudo-count 0.5); the fraction of agents with each orientation; the dominant cycle by summed |F|·|A|; the same on `coarse` (20 triangles) as description.
- **O6 Markov-order audit:** day-blocked held-out log-likelihood per transition of order-0/1/2 chains; the order-2 bound D_3/2 (Newton cross-fit on antisymmetrized 3-block indicators, per transition) vs. D_2 = Σ_i.
- **O7 regime contrast:** period medians of Σ_i per transition and per hour, #27 (regime I) vs. regime III periods.
- **O8 scaffold component:** Σ_i on the coarse sequence with consolidate records removed (decimated chain), and the share of Σ_i lost.

## Null / baseline
*Written 2026-10-03, before any real-data run.*
- **N1 estimator nulls:** time reversal (the held-out bound turns negative when θ from forward data meets reversed test days); within-day permutation of records (Σ → 0).
- **N2 detailed-balance (DB) surrogate, primary for O1, O2, O5:** per agent and period, the reversible chain P^rev_ab ∝ (n_ab + n_ba)/2 (same occupancies, same dwell/self-transition counts, same symmetric pair counts; currents removed), simulated with the agent's real day lengths and real day-start states; the same estimator is applied; 200 surrogates.
- **N3 cross-day surrogate, primary for O4:** each agent's day replaced by a different day of the same agent (derangement), minute-aligned and truncated to the shortest day. Keeps single-agent dynamics and the daily schedule; destroys same-day cross-agent timing. 100 surrogates (40 for #51). The within-day circular shift is shown only to demonstrate its bias (H05).
- **N4 family:** lab labels permuted among agents within a period (10,000 permutations); stratified across periods.
- **N5 synthetic ground truth** (axis F): Markov chains and kinetic Potts with known EP at village sizes.
- **Rivals.** R1 *scaffold clock*: irreversibility comes from the scaffold (consolidation cadence every ~40 actions, forced turns), so it sits in consolidate transitions and is the same across families. R2 *action mix*: family differences are estimation artifacts of different action mixes and turn counts. R3 *independent agents*: no collective term beyond N3.

## Faithfulness scorecard
Scored per model, mapping and window; 0 = not done or failed, 1 = partial, 2 = passed. Scheme and promotion thresholds: `writeup/paper.tex`, Sec. "Assessing model faithfulness".
**Rival models:** R1 scaffold clock; R2 action mix; R3 independent agents (single-agent Markov chains with no coupling).
**Locked holdout used for confirmation:** none yet. `analysis/confirm_h14.py` is written and dry-run on non-holdout stand-ins, not run on the holdout. It would use #45, #46, #47, #49, #50, the #51 tail (regime III) and #22, #28, #29 (regime I).

| Axis | Test | Score | Evidence |
| --- | --- | --- | --- |
| A mapping | variables defined from dataset fields; assumptions listed; invariant across families and regimes | 1 | States come from `actions` + `events_core`, with mirror turns and the scaffold's forced `mouse_move` removed and the gap-logging quirks handled. Regime invariance is partial: consolidate = CONSOLIDATE (III) vs. session start/stop (I). Shell sub-classes are unavailable (`bash_head` bug); `none` turns are dropped from coarse sequences. The result depends strongly on the state resolution (coarse vs. fine). |
| B assumptions | stationarity, Markov order, time-rescaling, update-order audit | 1 | Markov-order audit: order 2 beats order 1 (held-out) for 42–100% of agents, and the order-2 bound exceeds the pair bound for 20–87%. So order-1 Σ_i is a lower bound (P8 met in 4/9 periods). Day-fold cross-fitting; cold daily starts are calibrated synthetically. No time-rescaling check. |
| C adequacy | beats the null hierarchy, day-blocked held-out data | 1 | Single-agent arrows beat the detailed-balance surrogate in 29/30 agents (G51) and 10/10 (G27). In the 4-h regime-III periods it is 47–73% of agents, far above the 5% chance rate (binomial p ≤ 4e−6), except G37 (1/9). Fine classes: 80–100%. The collective term does not beat the cross-day null after Holm in any regime-III period. |
| D unfitted predictions | unfitted statistics and the model's signature | 1 | Cycle orientations (unfitted) failed as predicted (P5 0/8), but a consistent structure emerged: work → chat → consolidate is the dominant `lump4` cycle in 8/9 periods (G51 sign test p = 0.001). The regime contrast (P6) and "G37 lowest" (P7) held. |
| E interventional | predicts the change across a natural experiment | 0 | No event study. The regime-I vs. III contrast (P6, held at 7–29×) compares periods two months apart, confounded with roster and calendar. The #38 outreach-approval split showed no change (Wilcoxon p = 0.34). |
| F identifiability | synthetic recovery with village sampling; robust to preprocessing | 1 | Single-agent estimators and the DB test are validated: size 0.03–0.07, recovery 0.6–1.1 at n ≥ 2,000. The family test is sized only for DB-excess statistics (S2c), and its power is 0.32 at a 2× difference. The collective term is calibrated (size ≤ 0.07) but blind below ~0.3–0.5 nats/min in 5-day periods (P1(iv) failed). Results are not robust to the state resolution. |
| G ground truth | agrees with known structure | 1 | Irreversibility concentrates where the scaffold imposes direction: the consolidation boundary (52–100% of the coarse excess) and regime I's discrete sessions (7–29× higher). Both are known scaffold structure. |
| H comparative | beats the named rivals | 0 | Rival R1 (scaffold clock) wins over agent-driven cycles (P9 failed in 8/9). Rival R3 (independent agents) is not rejected (no collective term). R2 (action mix) has no family effect to explain. |
| I transfer | holds in other same-mode periods, including the holdout | 1 | The descriptive findings (fine arrows, the dominant consolidate cycle, the regime contrast, small coarse Σ) transfer across all 8 regime-III periods. Holdout not run. |

## Prediction
*Written 2026-10-03, before any real-data run of the EP pipeline.* What I had seen: H09's E2/E7 results (event-level EP collapses in regime III, median 0.0075 nats/step; per-minute 4-state EP in the #51 block highest for OpenAI, lowest for Google; crude collective ratio 0.21), H05's null EP on activity spins, and structural checks for the scheme (action-type counts; mirror turns; the immediate neighbours of CONSOLIDATE, PAUSE, AGENT_TALK, none, wait and mouse_move, pooled over regime I and regime III **including some holdout days**; no flux, EP or per-agent statistic). Those neighbour counts informed P5's cycle orientations, so P5 is **not blind**.

- **P1 (synthetic, axis F).** (i) For q = 6 chains with true Σ ∈ [0.005, 0.2] nats/transition and n ≥ 2,000 transitions over ≥ 5 days, the cross-fitted Newton bound has median recovery ≥ 60%, and |mean| ≤ 0.002 at Σ = 0; the uncorrected plug-in is biased upward at Σ = 0 by an amount ∝ 1/n. (ii) The DB-surrogate test has size ≤ 0.07 at α = 0.05, also for chains started out of stationarity each day. (iii) A family-label permutation test on Newton excess has size ≤ 0.07 when families differ only in sequence length and stickiness; on the uncorrected plug-in, size > 0.10. (iv) Kinetic Potts (N = 15, q = 6, 5 days × 240 bins): independent agents, and a shared daily field without coupling, give ΔΣ_MF and ΔΣ_PW within the cross-day null (size ≤ 0.07); asymmetric couplings with a true collective term ≥ 0.05 nats/bin are detected by ΔΣ_MF in ≥ 80% of runs. *Falsifier:* any size > 0.10, or recovery < 40%.
- **P2 (a, single-agent arrow).** In every regime-III period, ≥ 80% of agents with ≥ 1,000 transitions have Σ_i (coarse, turns) above the DB-surrogate 95th percentile; period medians between 0.01 and 0.15 nats/transition. On the minute grid ≥ 60% are above the null, and per-hour Σ_i is lower on the minute grid than on turns for ≥ 80% of agents (time coarse-graining loses irreversibility). *Falsifier:* < 50% above the null in most periods.
- **P3 (b, per-family arrow, HH19).** (i) *Primary, two-sided:* η²_lab ≥ 0.30 with permutation p < 0.05 in ≥ 2 regime-III periods, and the stratified meta-test across regime-III non-holdout periods p < 0.05. (ii) *HH19 as stated* (Anthropic > OpenAI): supported if Anthropic > OpenAI in ≥ 5 of 8 regime-III periods and the stratified one-sided test p < 0.05. My prior leans the other way (H09 E7), so (ii) is expected to fail. (iii) *Trait:* agents' Σ_i ranks are stable across regime-III periods: Kendall's W p < 0.05 for agents in ≥ 4 periods; mean pairwise Spearman ≥ 0.4. (iv) *Against R2:* the lab effect keeps partial η² ≥ 0.2 after shell share and log n. *Falsifier:* η² at permutation chance in all periods and meta p > 0.2.
- **P4 (c, collective, HH67).** *Weak form:* ΔΣ_MF above the cross-day null's 95th percentile in ≥ 2 of the 8 regime-III periods (#51 block included). ΔΣ_PW is at noise in the 5-day periods (too many observables) and detectable, if anywhere, only in the #51 block. *Strong form fails:* ΔΣ/Σ_1 ≤ 0.3 everywhere. *Falsifier:* weak form null everywhere; the strong form is supported if ΔΣ > Σ_1 with null exceedance in any period.
- **P5 (d, currents, HH56; not blind, see above).** On `lump4` turns: in regime III, the cycles work → chat → idle → work and work → chat → consolidate → work have positive affinity in that orientation for ≥ 75% of agents in each period, and one of them is the dominant cycle. In #27 (regime I), the dominant cycle runs consolidate (session start/stop) → chat → work → consolidate for ≥ 75% of agents.
- **P6 (regime contrast).** The #27 median Σ_i per transition exceeds every regime-III period median by ≥ 2× (session boundaries and out-of-session chat make regime-I turn sequences more cyclic). Per hour: descriptive only.
- **P7 (goal-directedness; low credence, ~30%).** #37 (free choice) has the lowest median Σ_i among regime-III non-holdout periods, and the mode-C periods (#38, #40, #44) have higher medians than the mode-I periods (#39, #41, #42). Descriptive (7 periods).
- **P8 (Markov order, axis B).** Order 2 beats order 1 in held-out log-likelihood for ≥ 80% of agents, and D_3/2 > D_2 for ≥ 50%: there is hidden memory, so all order-1 values are lower bounds.
- **P9 (against R1).** Removing consolidate lowers the median agent's Σ_i by < 50%, and the family effect (if any) survives the removal.

Multiple comparisons: the pre-specified primaries are P2 (per period), P3(i) meta-test, P4 weak form (per period, Holm across the 8 regime-III periods), P5 sign tests. Everything else is descriptive.

## Confirmatory test (pre-registered 2026-10-03, after exploratory round 1, before any holdout use; NOT RUN)
Script: `analysis/confirm_h14.py`. It refuses to run without `--confirm --i-understand-this-uses-the-locked-holdout`; `--dry-run` runs the same code on non-holdout stand-ins. Holdout periods: regime III #45, #46, #47, #49, #50 and the #51 tail (09-07 → 09-18); regime I #22, #28, #29. #43 and #48 (1 day each) are too short. Same pipeline as round 1: Newton primary, DB surrogates, cross-day surrogates, 200 / 100 / 40 surrogates.

| | Criterion | Threshold (exploratory basis) |
| --- | --- | --- |
| C1 | fine action classes: share of test agents above the DB null | ≥ 0.75 in ≥ 5 of 6 regime-III periods (round 1: 0.80–1.00 in 9/9) |
| C2 | regime contrast: median coarse Σ_i, regime I vs. III | every regime-I median ≥ 3× every regime-III median (round 1: 7–29×) |
| C3 | regime-III coarse arrow is small | median coarse Σ_i in [0, 0.02] in ≥ 5 of 6 (round 1: 0.0025–0.010) |
| C4 | long window: #51 tail | ≥ 80% of test agents above the DB null on coarse turns (round 1 G51: 0.97) |
| C5 | dominant current work → chat → consolidate → work | positive in > 50% of agents in ≥ 4 of 6, and the pooled one-sided sign test over agents p < 0.01 (round 1: > 50% in 6/8; G51 0.81) |
| C6 | no per-family arrow (HH19 null replicates) | stratified lab-permutation η² p > 0.05 and Anthropic − OpenAI two-sided p > 0.05 (round 1: 0.89, 0.85). Weak evidence: power 0.32 at 2× |
| C7 | agent trait, out of sample | Spearman(exploratory mean rank, holdout mean rank) > 0, one-sided permutation p < 0.05, on the **minute-grid** excess (round 1: mean pairwise ρ 0.24, p = 0.0005); turns reported as secondary (ρ 0.13, p = 0.02) |
| C8 | HH67 | (a) ΔΣ_MF and ΔΣ_PW within the cross-day null in every regime-III period after Holm; (b) #51-tail PW excess/Σ_1 < 0.3. (c) *Low credence, reported only:* ΔΣ_MF > null in ≥ 2 of 3 regime-I periods (round 1: one borderline p = 0.0495 in G27) |
| C9 | scaffold carries the coarse arrow | removing consolidate loses ≥ 50% of the median coarse excess in ≥ 4 of 6 (round 1: 0.52–1.00 in 8/8) |

**Verdict rule.**
- **Descriptive structure confirmed** if C1, C2, C5 and C9 all pass.
- **Agent-level arrow confirmed** if C7 passes.
- **HH19 stays refuted** if C6 passes; **HH67's weak form stays unsupported** if C8(a) passes.
- A failure of C3 or C4 is reported, not fatal.

**Dry run** (2026-10-03, `--dry-run --fast`; stand-ins #39–#42, #44, #51 07-06 → 07-17 for regime III and #23, #24, #25 for regime I; output in `data/processed/H14-behavior-entropy-production/confirm_dryrun/`).
- All nine criteria evaluate, and the code passes.
- The stand-ins overlap round 1, so C7 is in-sample there (ρ 0.875) and means nothing.
- *Disclosure:* #23–#25 were not part of round 1. The dry run exposed their medians (0.036–0.066 nats/transition, i.e. 3.6–14× the regime-III medians, consistent with P6). The criteria above were written before the dry run and were not changed after it.

## Results by goal period
| Period | Role | Verdict | Key numbers |
| --- | --- | --- | --- |
| [G27](goalperiod-subhypotheses/G27/README.md) | exploratory (regime I) | mixed | 10 test agents; coarse arrow 10/10 (minute 1.00, fine 1.00); median Σ_i 0.073 nats/transition (7.9/h); dominant cycle work>chat>cons, 60% in the predicted consolidate → chat → work orientation (P5 needs 75%); ΔΣ_MF p 0.0495, ΔΣ_PW p 0.66; η²_lab 0.61 (p 0.13; Anthropic 0.17 vs. OpenAI 0.03, p 0.053) |
| [G37](goalperiod-subhypotheses/G37/README.md) | exploratory | failed | 9 test agents; coarse arrow 1/9 (minute 0.11, fine 0.89); median Σ_i 0.0025 (0.19/h); work>chat>cons positive in 0.42; ΔΣ_MF p 0.98, ΔΣ_PW p 0.45 (3 days); η²_lab 0.10 (p 0.81) |
| [G38](goalperiod-subhypotheses/G38/README.md) | exploratory | failed | 14 test agents; coarse arrow 10/14 (minute 0.64, fine 0.86); median Σ_i 0.0032 (0.44/h); work>chat>cons positive in 0.86; ΔΣ_MF p 0.17, ΔΣ_PW p 0.36 (15 days); η²_lab 0.18 (p 0.64); 04-14 split: no change (p 0.34) |
| [G39](goalperiod-subhypotheses/G39/README.md) | exploratory | failed | 15 test agents; coarse arrow 7/15 (minute 0.60, fine 0.80); median Σ_i 0.0048 (0.52/h); work>chat>cons positive in 0.40; ΔΣ_MF p 0.99, ΔΣ_PW p 0.71; η²_lab 0.22 (p 0.31) |
| [G40](goalperiod-subhypotheses/G40/README.md) | exploratory | failed | 15 test agents; coarse arrow 9/15 (minute 0.40, fine 0.80); median Σ_i 0.0064 (0.77/h); work>chat>cons positive in 0.80; ΔΣ_MF p 0.93 (predicted detectable), ΔΣ_PW p 0.55; η²_lab 0.07 (p 0.97) |
| [G41](goalperiod-subhypotheses/G41/README.md) | exploratory | failed | 15 test agents; coarse arrow 11/15 (minute 0.67, fine 0.93); median Σ_i 0.0100 (0.96/h); work>chat>cons positive in 0.87; ΔΣ_MF p 0.50, ΔΣ_PW p 0.03 (Holm 0.21); η²_lab 0.11 (p 0.86) |
| [G42](goalperiod-subhypotheses/G42/README.md) | exploratory | failed | 16 test agents; coarse arrow 9/16 (minute 0.50, fine 0.94); median Σ_i 0.0075 (0.78/h); work>chat>cons positive in 0.56; ΔΣ_MF p 0.27, ΔΣ_PW p 0.14; η²_lab 0.39 (p 0.19) |
| [G44](goalperiod-subhypotheses/G44/README.md) | exploratory | failed | 14 test agents; coarse arrow 7/14 (minute 0.43, fine 1.00); median Σ_i 0.0083 (0.52/h); work>chat>cons positive in 0.62; ΔΣ_MF p 0.11, ΔΣ_PW p 0.30; η²_lab 0.26 (p 0.40) |
| [G51](goalperiod-subhypotheses/G51/README.md) | exploratory | mixed | 30 test agents; coarse arrow 29/30 (minute 0.87, fine 1.00); median Σ_i 0.0090 (0.69/h); dominant work>idle>cons (positive 0.90, p < 1e−3), work>chat>cons positive 0.81 (p 0.001); block 07-24 → 08-28 (N 27, 24 days): ΔΣ_MF p 0.32, ΔΣ_PW p 0.024 (Holm 0.20), PW excess/Σ_1 = 0.06; η²_lab 0.21 (p 0.51) |

## Results
*Exploratory round 1, 2026-10-03, non-holdout only.*
- **Code:** `scheme/build_states.py` (1.5 s), `analysis/h14lib.py`, `analysis/synthetic.py`, `analysis/run_period.py --period G<NN>`, `analysis/summarize.py`, `analysis/summary_figure.py`, `analysis/confirm_h14.py`.
- **Numbers:** `data/processed/H14-behavior-entropy-production/{synthetic/, G<NN>/, summary_round1.json}`.
- **Figures:** `figures/summary_round1.pdf` (one page), `figures/summary_obs.pdf` (for `summary/summary.pdf`), `figures/synthetic_validation.pdf`, `goalperiod-subhypotheses/G<NN>/figures/period_summary.pdf`.

### Synthetic validation (axis F; `figures/synthetic_validation.pdf`)
- **S1, q = 6 chains with known Σ, n = 500–50,000, 5 or 20 days.**
  - At Σ = 0 the Newton bound is unbiased (|mean| ≤ 0.001 at n ≥ 2,000), while the plug-in is biased up by ≈ 20/n (+0.010 at n = 2,000; +0.0004 at 50,000).
  - Newton's median recovery is 0.83–1.17 for Σ ∈ [0.03, 0.3] at n ≥ 2,000. One cell missed P1's 0.6 floor at small Σ: 0.59 at Σ ≈ 0.014, 20 days × 100 transitions.
  - It under-recovers strongly asymmetric sticky chains (0.71–0.74 at Σ ≥ 0.3), and over-recovers at most 1.12 at Σ ≥ 0.05, so the switch rule did not fire.
  - `cfx` minus its DB-null mean recovers 0.89–1.0 at Σ ≥ 0.03.
  - H05's L2 held-out ML is unstable on sparse indicators.
- **S1n, detailed-balance surrogate test** (150 runs per cell, cold and stationary daily starts).
  - Size is 0.027–0.067 for Newton, `cfx` and plug-in alike.
  - Power is 0.87–0.95 at Σ ≈ 0.02 with n = 2,000, and 1.0 at Σ ≥ 0.05.
  - For scale: a regime-III agent with Σ ≈ 0.005 and n ≈ 2,500 is near 50% power. That is why the 4-h periods sit at 47–73% above the null.
- **S2 / S2c, family test.**
  - S2 was mis-designed: true EP depends on stickiness, so its "size" cell was not a null (the true values themselves rejected 13% of the time). It was replaced, synthetic-only and before any family result was seen, by S2c: true EP drawn from one distribution, with families differing in n (10k / 2.5k / 1k) and stickiness.
  - S2c size: Newton excess 0.04, raw plug-in 0.20, raw `cfx` 0.37. Raw estimators must not be compared across families.
  - Power is 0.32 at a 2× family difference and 0.66 at 3×. The true values reach only 0.40 / 0.71, so agent heterogeneity, not estimation noise, limits power.
- **S3 / S3b, kinetic Potts** (N = 15, q = 6, 5 days × 240).
  - Calibrated: independent agents give rejection rates of 0.03 (MF) / 0.07 (PW); a shared daily field gives 0.00 / 0.03.
  - Power by true collective term: 1.73 → 1.00 / 1.00; 0.51 → 0.93 / 1.00; 0.09 → 0.20 / 0.25; 0.02 → 0.05 / 0.25.
  - The excess recovers ~18–26% (MF) and ~63–69% (PW) of the true collective EP.
  - The raw ΔΣ is biased up by high-dimensional K̂⁻¹ inflation acting on the large single-agent means, so only the excess over the cross-day null is meaningful.
  - **P1(iv) failed:** the 5-day periods are blind to collective terms below ~0.3–0.5 nats/min (whole swarm), which is the size of Σ_1 itself.

### Outcome vs. prediction
| | Prediction | Outcome | Verdict |
| --- | --- | --- | --- |
| P1 (i) | Newton median recovery ≥ 0.6 (n ≥ 2,000, Σ ∈ [0.005, 0.2]); \|bias\| ≤ 0.002 at 0; plug-in bias ∝ 1/n | 0.59–1.34 (one cell 0.59); bias ≤ 0.001; plug-in ≈ 20/n | **met, one marginal miss** |
| P1 (ii) | DB test size ≤ 0.07, including cold starts | 0.027–0.067 | **met** |
| P1 (iii) | family test size ≤ 0.07 on Newton excess; > 0.10 on raw plug-in | 0.04 vs. 0.20 (S2c) | **met** (after the S2 → S2c redesign) |
| P1 (iv) | Potts: nulls sized ≤ 0.07; true collective ≥ 0.05 detected by ΔΣ_MF in ≥ 80% | nulls 0.00–0.07; detection 0.20 at 0.09, 0.93 at 0.51 | **failed** (detection limit ~0.3–0.5) |
| P2 | ≥ 80% of agents above the DB null in every regime-III period; medians 0.01–0.15 | 1/8 regime-III periods (G51 0.97); others 0.11–0.73; medians 0.0025–0.010 | **failed**: the arrows are real but smaller than predicted; per-agent power is low in 4-h periods |
| P2 (minute grid) | ≥ 60% above null; per hour lower on the grid than on turns for ≥ 80% | ≥ 60% in 4/8 regime-III periods (+ G27); grid lower in 0.47–0.84 of agents (≥ 0.8 only in G51) | **mostly failed** |
| P3 (i) | η²_lab ≥ 0.30 with p < 0.05 in ≥ 2 periods; stratified meta p < 0.05 | 0 periods (max η² 0.39 in G42, p 0.19); meta p = 0.89; per hour 0.92, minute 0.82, no-consolidate 0.66, `cfx` 0.77 | **refuted** |
| P3 (ii) | HH19: Anthropic > OpenAI in ≥ 5/8, one-sided p < 0.05 | summed difference −0.013 (p = 0.59 one-sided; I² 0.13) | **refuted** (regime III). G27 (regime I) leans Anthropic (0.17 vs. 0.03, p = 0.053): underpowered, post hoc |
| P3 (iii) | trait: rank stability significant; mean ρ ≥ 0.4 | ρ = 0.13 (p = 0.02; 15 agents in ≥ 4 periods); minute grid 0.24 (p = 0.0005); `cfx` 0.06 (p = 0.12) | **partial**: significant but weak |
| P3 (iv) | lab effect survives adjustment | no lab effect to adjust | n/a |
| P4 weak | ΔΣ_MF above the cross-day null in ≥ 2 of 8 regime-III periods | 0/8 (Holm ≥ 0.87). ΔΣ_PW unadjusted p < 0.05 in G41 and G51 (Holm 0.21, 0.20) | **unsupported** (and blind in 5-day periods) |
| P4 strong | fails: ΔΣ/Σ_1 ≤ 0.3 | G51 PW excess/Σ_1 = 0.06, MF 0.003; bounded ≲ 0.15 in G51, ≲ 0.10 in G38 (using the S3 PW recovery); not boundable in 5-day periods | **holds where testable** |
| P5 | work → chat → idle → work and work → chat → consolidate → work positive in ≥ 75%; one dominant | 0/8 periods. work>chat>idle positive in 0.17–0.71 (no consistent orientation); work>chat>cons positive in 0.40–0.87 and dominant in 7/8 (G51: work>idle>cons, 0.90). G27: 60% in the predicted reverse orientation | **failed** as posed; the consolidate cycle is the consistent current |
| P6 | G27 median ≥ 2× every regime-III median | 7.3–29× | **met** |
| P7 | G37 lowest; mode C > mode I (low credence) | G37 lowest ✓; mode C not above mode I (mean difference −0.0015) | **half** |
| P8 | order 2 beats order 1 for ≥ 80%; D_3/2 > D_2 for ≥ 50% | ≥ 80% in 4/9 periods; ≥ 50% in 7/9 | **partial** |
| P9 | removing consolidate loses < 50% of the median excess | 52–100% lost in 8/8 regime-III periods (G27 73%) | **failed**: rival R1 (scaffold clock) wins |

### What it means (exploratory reading)
1. **Arrows of time live at fine resolution.**
   - On fine action classes, every period has 80–100% of agents above the detailed-balance null, with median excess 0.04–0.15 nats/transition.
   - That irreversibility is GUI and tool micro-workflow (click → type → key, look → click …): the "trivially irreversible tool use" of model 02's pitfalls.
   - Coarsened to six activity states, it shrinks by an order of magnitude (0.002–0.010).
2. **What coarse irreversibility remains is mostly the scaffold's.**
   - Half or more sits in transitions through consolidate (plug-in share 0.38–0.62). Removing consolidate removes 52–100% of the excess.
   - Regime I's discrete sessions (start → chat → work → stop → chat) give 7–29× more irreversibility per transition than regime III's perma-computer-use with periodic consolidation.
   - The dominant probability current is work → chat → consolidate → work: agents work, report, and the scaffold consolidates them back into work. Agent-chosen loops such as work → chat → idle → work have no consistent orientation.
3. **No family has its own arrow (HH19 refuted in regime III).**
   - What exists is agent-level: individual excesses range from ≈ 0 to 0.30 nats/transition within a period, and ranks are weakly stable across periods (ρ 0.13–0.24).
   - Post hoc and hypothesis-generating only: the most irreversible agent is an Anthropic model in 8/9 periods (Claude Sonnet 4.5 in 4). Lab *means* do not differ.
4. **No collective arrow detected (HH67).**
   - In the two long windows (G38, G51), any cross-agent term is ≲ 10–15% of the single-agent sum.
   - The 4-h, 5-day periods cannot see collective terms comparable to Σ_1, so their nulls are uninformative.
   - Regime I (G27) shows a borderline mean-field term (p = 0.0495, one period): the message-triggered regime is the place to look next.
5. **Payoff question (goal-directed vs. aimless).** The free-choice week (#37) has the lowest coarse arrow (as predicted, low credence). Shared-objective weeks are not more irreversible than individual-objective weeks. EP is not yet a usable "goal-directedness meter".

### Caveats
- **Multiplicity.** Many statistics: 9 periods × several estimators, schemes and family variants. The pre-specified primaries are P2 per period, the P3(i) meta-test, P4 with Holm, and the P5 sign tests; the rest is descriptive. The two ΔΣ_PW p ≈ 0.03 results do not survive Holm.
- **Power.** The 4-h periods give n ≈ 600–4,300 transitions per agent (G38 up to 13,000): about 50% power per agent at the observed Σ ≈ 0.005. P2's "failure" there is mostly power plus a smaller-than-predicted effect, not absence. The family test has 0.32 power at a 2× difference with 12–16 agents (S2c). The collective test is blind below ~0.3–0.5 nats/min in 5-day periods (S3b).
- **Estimator.** The Newton quadratic is a weak-asymmetry approximation, not a bound. It agrees with the `cfx` companion on every headline (P2 fractions within ±0.21, largest gap G38 0.71 vs. 0.50; family meta p = 0.89 vs. 0.77), but under-reads strongly asymmetric agents (G27 median Newton 0.073 vs. `cfx` excess 0.145).
- **States.** The coarse scheme is my choice. The headline flips between coarse and fine resolution, and the Jev states will sit in between.
  - Shell sub-classes were impossible: `actions.bash_head` is null for 87% of regime-III bash turns (shared-table bug).
  - `none` turns (6% of regime-III records) are dropped from coarse sequences.
  - The forced post-consolidation `mouse_move` removal is a judgement call. Keeping it would add a deterministic consolidate → browse transition, i.e. more scaffold irreversibility.
- **Holdout exposure.** The structural checks behind the scheme looked at immediate-neighbour counts pooled over regime III *including holdout days* (no EP, flux or per-agent statistic). They informed P5's orientations, which were labelled non-blind, and they partly inform C5. The dry run exposed non-holdout #23–#25.
- **Regime contrast.** G27 vs. regime III spans two months, a roster turnover and the NE14 bundle, so it is not an event study. NE14 itself (03-16 → 04-01) was not analysed.
- **Gap logging.** Regime-I WAIT and all CONSOLIDATE events are logged at completion. Event order is right; the minute grid assigns the gap to idle / consolidate.

### Amendments (all before any real-data run unless stated)
1. Estimator switch rule (written before the synthetic study): the trigger did not fire, so Newton stayed primary and `cfx` was added as companion.
2. ML dropped as a companion (synthetic instability).
3. S2 → S2c: the family-null redesign, after seeing S2's confounded synthetic size; synthetic only, but run while the real-data periods were already processing. No family test was looked at before S2c finished.
4. S3b (weaker couplings) added after S3, synthetic only, run in parallel with the real-data runs; it changes no real-data number.
5. After real data: only presentation changes (summary figure layout; a fine-class bar added to panel B). No threshold, estimator or state definition was changed after any real-data result.

### Next steps
1. **Jev states.** The pipeline already accepts them (`run_period.py --states … --day-col pt_date --bin-col w`; smoke-tested on the 200-window draft, which has too few consecutive windows for transitions).
   - The full run gives 5-min, 10-state sequences of ~50–100 windows per agent-day: coarser in time than turns, finer in meaning than the 6 coarse states.
   - Predictions to write then: Jev-state Σ_i between the coarse and fine values per hour; plan → execute → verify → report cycles with a consistent orientation (the agent-chosen loop the coarse states could not resolve); a family effect only if it appears at the semantic level.
   - Sequence length per agent-period is ~5× smaller than on turns, so restrict to G38, G51 and 8-h periods, or pool periods hierarchically (exception (d)).
2. **Regime I** is where both the arrow and a possible collective term are strongest. Run the remaining non-holdout regime-I periods (#18–#21, #23–#27, #30, #31) with predictions written first, and an NE14 event study on 03-16 → 04-01.
3. **Fine-class currents:** a Schnakenberg decomposition on the `act` scheme, to see whether the GUI micro-cycles are family-specific (bash-heavy vs. GUI-heavy agents).
4. **Event-time collective observables** (reply-conditioned, using `exposure`) instead of the 1-min grid, to raise power for HH67.
5. Run `confirm_h14.py` on the holdout only with Vivian's sign-off.

## Notes
- **Planned holdout reuse (2026-10-04):** H56's `confirm.py` (not run) and this card's unrun confirm script both use #45–#47, #49 and #50 with the same data type (turn-level EP). Disclose in both cards and LOG.md before either runs. H56 found EP does not jump at scaffold changes; family differences are tool-use style.
- 2026-10-03: promoted from shortlist 2 (HH19 + HH67 (shortlist 2, item 6)).
- 2026-10-03, structural checks that fixed the scheme (counts only, before predictions): in regime III, `send_message_back_to_chat`, `pause` and `search_history` turns mirror AGENT_TALK, PAUSE and SEARCH_HISTORY events (96–100% within 2 s, median lag 0.03–0.09 s); the computer-use `wait` action is a GUI wait, not the WAIT event; ~85% of CONSOLIDATE events are followed by a `mouse_move` turn (in regime I, START_USING_COMPUTER → AGENT_TALK → `mouse_move`): a fresh-context artifact, dropped; CONSOLIDATE is logged ~3 min after the previous turn (median 203 s after bash), i.e. at completion.
- 2026-10-03, **estimator decision rule, written before the synthetic study** (only a one-chain smoke test seen): the H05 Newton quadratic 2ḡᵀK⁻¹ḡ is a weak-asymmetry approximation, not a bound (smoke test: 2.45 vs. exact 1.46 nats on a strongly driven 3-cycle). Added the **cross-fitted exact dual with count-based θ** (`ep_cfx`: Θ_ab = ln((n_ab + ½)/(n_ba + ½)) from training days, the exact optimum for transition indicators, evaluated on held-out days; 1.47 on the same chain). Rule: if, in P1, Newton over-estimates true Σ by > 20% (median) at Σ ≥ 0.05 in any cell, `ep_cfx` becomes the primary single-agent estimator and Newton is reported as a companion; the collective increments ΔΣ stay on Newton (weak cross-agent asymmetries), subject to P1(iv).
- 2026-10-03, **decision rule applied after S1, before any real-data run:** the trigger did not fire (worst median Newton recovery at Σ ≥ 0.05 was 1.12, below 1.2), so **Newton stays primary** for P2–P4, P8, P9 and the family tests. S1 showed the opposite failure instead: Newton under-recovers strongly asymmetric sticky (minute-like) chains (0.71–0.74 at Σ ≥ 0.3), while `cfx` minus its DB-null mean recovers 0.89–1.0 and is ≈ 0 at Σ = 0. So every result is also reported with the `cfx` companion, and disagreements are flagged. H05's L2 held-out ML (`ep_heldout`) is dropped as a companion: it is unstable on sparse transition indicators (means down to −10 nats on sticky chains). The chi-square-corrected plug-in under-recovers (0.3–0.5) and is reported only in the per-agent tables.
- 2026-10-03, **shared-table bug found** (not fixed; outside this card's edit scope): `actions.bash_head` is null for 87% of regime-III bash turns because commands start with a `#` comment line and `scan_tables.BASH_HEAD` does not skip comment lines (regime I/II coverage 96–97%). Shell sub-classes (git, run, read, net) are therefore not used in round 1.
- 2026-10-03, **round 1 done** (exploratory, non-holdout). 9 periods (G27, G37–G42, G44, G51); synthetic S1, S1n, S2c, S3, S3b; confirmatory script dry-run.
  - Disk: `data/processed/H14-behavior-entropy-production/` 13 MB.
  - Compute: local; ≤ 2 single-threaded processes; ~45 min CPU in total.
- 2026-10-03, **proposed shared-file changes** (not made; outside this card's edit scope):
  1. `physics-models/DEFINITIONS.md`, under "Entropy production / irreversibility", add the two named variants defined at the top of this card.
  2. `infra/shared/scan_tables.py` `BASH_HEAD` should skip leading comment and blank lines (87% of regime-III bash heads are currently null). Add to `infra/README.md` "Known issues" until rebuilt.
  3. `infra/README.md`, document for `actions`:
     - `send_message_back_to_chat`, `pause` and `search_history` turns mirror events (drop when the event is within 2 s);
     - the first computer-use turn after CONSOLIDATE / START_USING_COMPUTER is a scaffold `mouse_move`;
     - CONSOLIDATE is logged at completion (~3 min after the previous turn), like regime-I WAIT.
  4. `physics-models/10-potts`: the parallel kinetic-Potts simulator with exact EP (`h14lib.simulate_potts`, `potts_exact_ep`) could move there. Its README could note that cross-fitted Newton increments ΔΣ carry a high-dimensional positive bias that only a matched surrogate removes.
  5. `physics-models/02-nonequilibrium-ising` pitfalls: the Newton quadratic is not a bound at strong asymmetry. For transition indicators the exact dual has the closed-form optimum Θ_ab = ln(p_ab / p_ba) (`ep_cfx`).
  6. The H09 E2 claim (78% of agent cells irreversible vs. a shuffle null) used a shuffle null that destroys dwell structure. Against a detailed-balance surrogate, coarse per-turn irreversibility is much weaker; H09 might note this.

## Round 2 redirects (2026-10-04)
*From the round-1 reflection (`writeup/round1-reflection/round1-reflection.pdf`).*
- **Where round 1 went sideways:** Entropy production on action classes measured the scaffold's consolidation cycle.
- **What the direction is really after:** The arrow of time of work: progress is irreversible, chatter is reversible.
- **H14-R1.** Entropy production on work states (plan, build, verify, ship; Jev) correlates with output: useful irreversibility.
- **H14-R2.** Loops are near-reversible cycles with zero progress; productive phases produce entropy. Efficiency = progress per unit of entropy produced.
- **H14-R3.** The scaffold contributes a fixed entropy-production floor (the consolidation clock); subtracting it leaves agent-generated irreversibility (E1).
