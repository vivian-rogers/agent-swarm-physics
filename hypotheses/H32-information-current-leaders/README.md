# H32: A net information current identifies de facto leaders

**Status:** exploratory round 1 **done (2026-10-03). Leader identification failed by the pre-registered rules; a narrower result stands.** Exposure-gated content transfer between agents is real in about half the goal periods, depends on exposure, and gives a reproducible outflow ranking. But that ranking does not single out the known sources: the elected leader (#26), the operator (#44) and human messages generally do not rank high. The installed fine-tuned leader (#44) is the *weakest* source in its room. Confirmatory script for #28/#22/#14 written and dry-run, not run.
**Round 1b (2026-10-04, ledger exposure, gte, style-resid, H57 placebo):** transfer replicates (17/32 bge, 23/32 gte, 18/32 style-resid; rankings ρ 0.99 vs round 1) and still needs exposure (7/8). At matched short lag, read messages beat not-yet-read ones in 17/17 transfer periods, but unread ones carry about a third of the gain (convergence). Which agent is the top source is model-dependent (same top in 17/32 across embedding models). All three leader natives fail as predicted: the elected leader over its real DQ6 term (#26 rank 5/10), #35's daily lead designers (percentile 0.43) and #44's installed leader over its full window (last of 6).
**Fields:** stat mech, sociophysics, info theory
**Origin:** HH118 (`../hypohypotheses/HYPOHYPOTHESES.md`; `../promotion-shortlist.md`), which extends HH93 (influence lives in content, not timing).
**Definitions used:** agent; regime (whitening basis = the majority regime of the goal period's days); goal period as the unit of analysis; driving / external field (goal text + kickoff per room, extended to a multi-direction field subspace, see Model); agent state, variant *vector (for model 11)*: per-regime whitened bge-small statement embeddings (`common.load_whitener`, n = 32), unit-normalized per message; interaction (broadcast): j is exposed to i's message if j's `rooms_timeline` room at the message time is the message's room (the rule `exposure.parquet` uses), and the message precedes j's message. Proposed named variants (not yet in DEFINITIONS.md; outside this card's edit scope): **content transfer (exposure-conditioned, cross-validated Gaussian)** and **outflow centralization Φ**, both defined under Observables.

## Standards (2026-10-04)
*Documentation pass against `STANDARDS.md`. No analysis was re-run. Every entry rests on this card and its round-1b section.*

**Question served:** Q2. The card separates content coupling from fields and from convergence. Q5 second: it tests whether formal leaders are levers on content.

| Impostor | Relevant? | How it was handled | Status |
| --- | --- | --- | --- |
| Scheduler field | partly | The day×room field sits in the baseline (Model). Nulls are a cross-day circular shift (N1) and a within-day shift (N1w, A1c). The estimator uses content at message times, not activity. | removed |
| Exogenous field (kickoff/goal/operator) | yes | A K = 5 field subspace (goal, kickoffs, period mean, day×room directions) is projected out. Human and automated messages are drive terms in the baseline. The transfer count depends on K (25/18/7 of 32 periods at K = 1/5/10; Caveats). | partly |
| Shared model priors | yes | Round 1b runs bge with `style_resid` (18/32 periods) and gte (23/32). Existence survives. Top-source identity changes in 10/32 under `style_resid` and in 15/32 across models. | partly |
| Contemporaneous convergence | yes | Round 1b H57 placebo (read vs unread same-room messages). At τ = 60 s, read beats unread in 17/17 transfer periods; unread carries about a third. The headline T at τ = 15 min is not net of the unread term. | partly |

**Inputs:** round 1b uses the context ledger (call-start exposure), both embeddings, `style_resid` and `statement_flags` dedupe, shared goal fields and DQ6 leader windows. Activity, work and failures are not inputs. Still old: the rival rankings in O10, i.e. mention in-degree from `chat_mentions_clean` (not the leading-@ target) and H02's round-1 timing influence.

**Two layers:** no folder has role `replication`. The common estimator runs on 32 period folders under role `exploratory`, plus NE42. Native tests: 3 (`G26` elected leader, `G35` lead designers, `G44` installed leader), all failed as predicted.

**Confirm script:** `analysis/confirm.py` exists, dry-run only. It is "identical to round 1's primary": posting-time exposure and bge alone. **Re-freeze on ledger exposure before any holdout run** (holdout.md items 8 and 15). Add the τ = 60 s unread placebo and gte as frozen clauses at re-freeze.

## Question
Content transfer entropy out minus in per agent classifies sources and sinks. The swarm-level concentration of outflow is an order parameter: centralized vs distributed coordination. Content succeeds where activity timing failed (H02; extends HH93). *Check:* source ranking vs the elected leader (#26) and the installed leader (#45, holdout); concentration across modes.

Practical aim (usefulness-first batch): produce a number or rule an operator of an LLM agent swarm could compute from logs and act on.

## Model
**From:** `physics-models/11-vector-spins` (linearized vector dynamics = a vector autoregression on embeddings, with isotropic couplings W_ij = c_ij·I; field removal along several directions) and `physics-models/02-nonequilibrium-ising` (the antisymmetric part of the directed couplings is the leader/follower structure; out minus in = the net current through a node).

**H32 variant: message-level isotropic vector autoregression with exposure-gated sources.** Each agent message m (agent j, time t, room r, day d) has a state z_m ∈ ℝ³²: the whitened, unit-normalized embedding with the period's field subspace projected out (not renormalized). The model for j's next message:

z_m = a₁ z_{j,last} + a₂ z̄_{j,ewma} + a₃ z_{j,intent} + b f_{d,r,−ij} + c r_{m,−i} + e_H h_m + e_A q_m + κ_{ij} s_{ij}(m) + ξ_m

- own past: j's previous message, the exponentially weighted mean of its messages (half-life 5 messages), and its latest self-written intention (`intentions`);
- slow field f: the leave-{i, j}-out mean of all agent messages in room r on day d (a day×room field, "common drive" at day scale);
- mean field r: the decayed sum of every *other* agent's messages that j had seen (exposure), excluding i;
- exogenous drive: decayed sums of seen human messages (h) and automated messages (q);
- source s_ij: the decayed sum of i's messages that j had seen before m, weights exp(−Δt/τ), τ = 15 min, same day, window 3τ;
- coefficients are scalars (isotropic coupling), fitted by least squares on the stacked 32 coordinates, so a pair with ~100 target messages still has ~3,200 equations for 8 parameters.

**Field subspace (several directions, H24 lesson).** Per period: the goal text, each room's kickoff (shared goal-field table, whitened in the period's basis), the period mean of agent statements, and the leading principal directions of the day×room mean vectors, orthonormalized to K = 5 directions (variants K = 1, the H01 ĝ only, and K = 10).

**Transfer.** The content transfer from i to j is the cross-validated predictive gain of adding s_ij (leave-one-day-out): G_ij = 1 − SSE_full/SSE_base summed over held-out days. For a linear-Gaussian model this is Granger causality, i.e. Gaussian transfer entropy: TE_ij ≈ −½ ln(1 − G_ij) nats per coordinate per message (Barnett, Barrett & Seth 2009†). Leave-one-day-out keeps the test on whole held-out days.

**Mean-field reading.** A star (one source, κ_Lj = κ for all j) gives Out = (κ-gain, 0, …, 0) and Φ = 1; uniform all-to-all coupling gives Φ = 0. Directed couplings with κ_ij ≠ κ_ji break detailed balance (model 02); Net_i is the node-level divergence of that current.

## Data scheme (`scheme/`)
- **Inputs:** shared `chat_core`, `embeddings/chat_bge_small.npy` + `chat_index`, `embeddings/intentions_bge_small.npy` + `intentions_index`, `intentions`, `whitening_<regime>.npz` (via `common.load_whitener`), `rooms_timeline`, `calendar`, `roster`, `chat_mentions_clean`, `artifacts` + `artifact_mentions` (validation only); the shared goal fields `embeddings/goals.parquet` + `goal_vectors.npy` (kinds `goal_whole`, `kickoff_room`; A1f; H01's copies were used before the coordinator's notice, never on real data).
- **Transform** (`scheme/build.py`): non-holdout goal periods with ≥ 3 active days and ≥ 4 agents with ≥ 20 chat messages. Every chat message (agent, human, automated) and every agent intention in those periods: time, active time, day, room, speaker; 32-d whitened unit vectors (fp16; also 64-d for the dimension robustness check); field-subspace vectors per period. Holdout asserted absent (calendar flag and `holdout_mask` by day and by goal number).
- **Output:** `data/processed/H32-information-current-leaders/` (`messages.parquet`, `vec_w64.npy`, `fields.npz`, then per-period analysis outputs in `G<NN>/`), with `_provenance.json`. No text.
- **Regimes covered:** I, II, III (not #51; see Candidate goal periods).

## Candidate goal periods
- **Ground truth:** #26 (elected leader DeepSeek-V3.2, agent 17; election decided 2026-01-09 18:59 UTC, the first moment its share of carried-forward first-person single-candidate votes in H11's `votes.parquet` reached ≥ 0.75, structural codes only); #44 (installed temporary leader, agent 28, 05-28/29 in #best; the operator posts 57 messages in #best); every analyzed period with ≥ 15 human messages (humans as a known exogenous source, positive control).
- **Coordination weeks:** #13 (human-subjects experiment, 6 agents, 10 days), #18, #19, #24, #25, #30, #38, #40 (#universe-coordination).
- **Distributed weeks:** mode I (#10, #17, #20, #21, #39, #41, #42), mode F (#3, #5, #11, #16, #31, #37), mode K (#6, #23, #27), M (#12).
- **Natural experiment NE42** (#best and #rest merged into #universe-coordination for #40, split back for #41): an A–B–A switch of exposure for cross-room pairs → `goalperiod-subhypotheses/NE42/`.
- **Every non-holdout period meeting the data rule** gets a `G<NN>/` folder. Excluded: #2, #7 (2 days); #51 (deferred: 55 days, 21+ agents, private roles; round 2).
- **Holdout:** #45 is reserved for H23's content confirmation and was used by H02 (timing), so H32 does **not** plan to use it. Confirmation targets: #28 (mode C, regime I, 11 agents), #22 (mode F) and #14 (mode I) for the transfer/stability/centralization predictions; **no** held-out period has a known leader except #45, so H32's leader claim cannot be confirmed on the holdout without a reuse decision by Vivian (see Confirmatory).

## Observables
*Specified 2026-10-03, before any real-data run.*
- **O1 pair transfer:** ΔG_ij = G_ij − median of G_ij over 40 circular-shift null replicas (below), for ordered pairs with ≥ 20 target messages of j and ≥ 10 messages of i in the period. Units: % of residual variance (×100).
- **O2 agent current:** Out_i = mean_j ΔG_ij (over targets j), In_j = mean_i ΔG_ij (over sources i), Net_i = Out_i − In_i. Significance: z_out,i against the same statistic on the null replicas (each replica centered by the median of the other replicas).
- **O3 total transfer:** T = mean_ij ΔG_ij, with p_T from the null replicas (one-sided).
- **O4 heterogeneity and centralization:** Cochran's Q of Out_i with delete-one-day jackknife variances σ_i², I² = (Q − (N−1))/Q; the order parameter **Φ = CV²_true/(N−1)**, CV²_true = (Var_i Out_i − mean_i σ_i²)/(mean_i Out_i)², i.e. the noise-corrected normalized Herfindahl index of outflow (0 = equal outflow, 1 = one agent carries it all). Reported only when T > 0 at p_T < 0.05. Secondary: the Gini coefficient of max(Out_i, 0) and the top agent's share.
- **O5 leader call:** the top agent by Out (primary) and by Net (secondary). "Identified" if Q's p < 0.05 and that agent's z_out ≥ 2.
- **O6 split-half stability:** Spearman ρ between Out computed on odd and on even days (periods with ≥ 4 days and ≥ 6 agents).
- **O7 exposure contrast** (periods with ≥ 2 populated rooms): the same gain for i's messages posted in rooms j was *not* in (unseen, same time window), added to the baseline; ΔG_seen (beyond unseen) vs ΔG_unseen. Same-room vs cross-room pairs.
- **O8 humans as a source:** human messages pooled as one pseudo-agent; its Out (gain on each agent, with h dropped from the baseline) ranked among the agents' Out.
- **O9 segment tests** (short windows, too short for day folds): pooled-sender gain Out*_i = the CV gain from adding s_i to every other agent's model with one shared coefficient, folds = 30-min blocks. Used for #26 after the election decision and for #44 #best on 05-28/29.
- **O10 rival rankings:** message count; mention in-degree (`chat_mentions_clean.mentions_roster`, messages by others naming i); H02's activity-timing net influence (`real_influence.parquet`, estimator `block`); artifact adoption A_i = artifacts first seen with agent i in the period (`artifacts.first_agent`) that ≥ 1 other agent mentions later in the period.
- **O11 synthetic recovery** (`analysis/synthetic.py`): the whole pipeline on synthetic vectors generated on real periods' message skeletons (times, speakers, rooms, days, exposure): top-1 accuracy, leader rank, false-alarm rate, Φ by scenario.

## Null / baseline
*Specified 2026-10-03, before any real-data run.*
- **N0 within the fit:** the baseline model (own past, slow field, mean field from other seen senders, exogenous drive). G_ij is the gain *beyond* it on held-out days, so a zero-coupling world gives G ≈ −(small CV penalty).
- **N1 circular shift (primary; preserves each agent's own autocorrelation):** shift every sender's whole message timeline by one random offset in active time (40 offsets, uniform between half a mean day and the period length minus half a day; wraps around), recompute its exposure (j's room at the shifted time vs the message's room) and its decayed sums, refit. Targets and controls are untouched.
- **N2 exposure (multi-room periods):** the same sender's simultaneous messages in rooms j was not in. Common drive predicts ΔG_unseen ≈ ΔG_seen; transfer predicts ΔG_unseen ≈ 0 < ΔG_seen.
- **N3 synthetic nulls:** zero coupling; zero coupling plus a latent drive that one agent follows 20 min ahead of the others (the "fast responder", the classic Granger confound).
- **Strongest rival (R3, common drive):** no transfer; agents respond, at different speeds, to shared outside fields. It predicts N1-significant transfer only through fast responders, and no exposure dependence (N2).

## Faithfulness scorecard
Scored per model, mapping and window; 0 = not done or failed, 1 = partial, 2 = passed. Scheme and promotion thresholds: `writeup/paper.tex`, Sec. "Assessing model faithfulness".
**Rival models:** R0 activity-timing influence (H02); R1 talkativeness (message count); R2 addressing (mention in-degree); R3 common drive with fast responders (no transfer).
**Locked holdout used for confirmation:** none yet. Planned: #28, #22, #14 (`analysis/confirm.py`, frozen, not run); #45 refused (reuse policy).

| Axis | Test | Score | Evidence |
| --- | --- | --- | --- |
| A mapping | variables defined from dataset fields; assumptions listed; invariant across families and regimes | 1 | Content from whitened bge-small statement embeddings with a K = 5 field subspace. Exposure is the broadcast-interaction rule (room membership at posting time; agrees with `exposure.parquet` by construction). Assumptions (isotropic linear coupling, τ = 15 min decay, day×room field) are listed. Not invariant across families: the top source is a Claude model in 21/32 periods vs 14 expected from roster shares, which may be style (H13). Exposure semantics differ by regime (regime-I chat reached agents between sessions). |
| B assumptions | stationarity, Markov order, time-rescaling, update-order audit | 1 | Stationarity of the ranking across halves of days: split-half ρ > 0 in 23/26 eligible periods. Lag structure: τ = 5 min gives the most transfer (26/32 periods significant), τ = 45 min the least (14/32), so transfer is fast and conversational. Isotropy and linearity not tested; no update-order audit. |
| C adequacy | beats the null hierarchy, day-blocked held-out data | 1 | Leave-one-day-out held-out gain beats the cross-day circular shift (each sender's autocorrelation preserved) in 18/32 periods and the stricter within-day shift too in 15/32. The level depends strongly on field removal: K = 1 gives 25/32 periods, K = 10 gives 7/32. |
| D unfitted predictions | unfitted statistics and the model's signature | 1 | Two unfitted signatures pass. The outflow ranking replicates across odd and even days (median ρ 0.38, sign p 4×10⁻⁵). Transfer needs exposure: seen > unseen in 7/8 multi-room periods (sign p 0.035), and unseen transfer is significant in only 1/8. Three predictions fail: no leader stands out (2/18), Φ does not separate modes, and T does not fall with N. |
| E interventional | predicts the change across a natural experiment | 0 | NE42 (room merge for #40): pairs split in #39/#41 show no transfer when merged (sign p 0.39; DiD CI spans 0). |
| F identifiability | synthetic recovery with village sampling; robust to preprocessing | 1 | **Synthetic, on real skeletons:**<br>• single-room weeks: the planted leader is top in 90–100% of runs at ψ ≥ 0.5% and called in 60–100% at ψ ≥ 2%;<br>• false calls 0–10%;<br>• two-room week: 60% (ψ = 2%) and 90% (ψ = 5%);<br>• Φ separates star (0.5–0.75) from distributed (0.01–0.11).<br>**Confound:** a fast responder to a latent drive is called leader in 90% of single-room runs; only the exposure contrast and the within-day null flag it.<br>**Not robust to preprocessing:** the top-source identity matches the primary in only 13–27/32 periods across 8 variants (Out ρ vs primary 0.47–0.91). No embedding-model swap. |
| G ground truth | agrees with known structure | 1 | **Rooms: yes** (exposure contrast).<br>**Leaders: no.**<br>• #26: DeepSeek ranks 7/10 after the election.<br>• #44 #best: the operator ranks 5/7 sources; the temporary leader ranks last (6/6) among agents, consistent with H23/H02.<br>• Humans as a known source: above the median agent in 4/16 periods (only the viewer-heavy #3–#6); significant positive outflow in 6/16. |
| H comparative | beats the named rivals | 1 | **R3 (common drive):** beaten where testable (exposure contrast 7/8 multi-room periods); unresolved in single rooms (synthetic confound).<br>**Other rivals:** content outflow is not talk volume (median ρ 0.34) or message length (−0.15), and differs from activity timing (H02; median abs ρ 0.24) and from mention in-degree (ρ 0.15). But no rival, H32 included, finds the known leaders. H29's net current agrees weakly (median ρ 0.27, 7 periods). |
| I transfer | holds in other same-mode periods, including the holdout | 0 | Holdout not run (`analysis/confirm.py` frozen and dry-run on stand-ins #30/#16/#17, reproducing round 1 exactly). |

## Prediction
*Written 2026-10-03, before running the analysis on real data.*

**What I had seen when writing this.** Round-1 results of H01, H02, H11, H12, H18, H23, H24 (LOG.md and their cards). Structural counts only for H32's periods: messages per agent, room and day; human and automated message counts per room and day (#13, #26, #40, #44); the #26 election-decision time from H11's vote codes; H02's per-agent table schema (not its values for any period other than what its card reports: DeepSeek 8/10 in #26). I had computed no content statistic on any period.

**Predictions** (credences in brackets; "periods" = analyzed non-holdout periods):
- **P1 transfer exists.** T > 0 at p_T < 0.05 (N1) in ≥ 60% of periods. [0.70] Reason: conversation is pairwise (answers, acknowledgements, adopted plans), and H24 saw literal copying; against it, the baseline already contains the mean field of other speakers and the day×room field.
- **P2 heterogeneity.** Cochran's Q p < 0.05 for Out in ≥ 50% of periods where P1 holds. [0.50]
- **P3 stability.** Split-half ρ(Out_odd, Out_even) > 0 in ≥ 2/3 of eligible periods, median ρ ≥ 0.3. [0.50]
- **P4 not just talk volume.** Median over periods of Spearman ρ(Out, message count) < 0.8. [0.65] And Out ranks the positive-control sources (P5, P6) higher than message count does. [0.40]
- **P5 humans are sources (G, positive control).** In periods with ≥ 15 human messages, the human pseudo-agent's Out exceeds the median agent's Out in ≥ 70% of them. [0.70]
- **P6 #26 (elected leader).** (a) Over the whole week, DeepSeek-V3.2 is *not* the top source (rank > 3 of 10): the election itself was run by others and decided only in the last day's first hour. [0.55] (b) After the decision (01-09 18:59 → end of day), DeepSeek's pooled Out* is the largest of all agents (rank 1). [0.30; ~3 h of data]
- **P7 #44 (installed leader).** (a) The temporary leader (agent 28) is not the top source in #best on 05-28/29: pooled Out* rank ≥ 3 of the #best agents present. [0.75; H23: its plans track the room] (b) The operator (human pseudo-agent) is the top source in #best over #44. [0.55] (c) Exposure contrast: same-room pair transfer > cross-room, with cross-room ΔG ≈ 0 (90% CI includes 0). [0.70]
- **P8 exposure (R3 test).** Pooled over multi-room periods, ΔG_seen > ΔG_unseen, and ΔG_unseen's 90% CI includes 0. [0.65]
- **P9 NE42 (A–B–A).** Pairs split across rooms in #39 and #41 but together in #40 have pair transfer ≈ 0 in #39 and #41 (unexposed) and > 0 in #40, larger than in #39 and #41 by a pair-level sign test (p < 0.10). [0.55]
- **P10 modes.** (a) T is higher in mode-C periods than in mode-I/F periods (Mann–Whitney one-sided p < 0.10). [0.45] (b) Φ is higher in mode-C than in mode-I/F periods (one-sided p < 0.10). [0.30] (c) The H18 dilution law carries over: T falls with N (Spearman ρ < 0). [0.60]
- **P11 timing ≠ content (R0).** Median |ρ| between Out and H02's activity-timing net influence < 0.3 across the periods both cover. [0.60]
- **P12 cross-modal validity.** Median Spearman ρ(Out, artifact adoption A_i) > 0 across periods. [0.55] Median ρ(Out, mention in-degree) > 0. [0.65]
- **P13 synthetic (axis F; predictions about the method).** At village sampling: a single leader whose term explains ≥ 2% of followers' residual variance is ranked top by Out in ≥ 80% of replicates in a single-room 10-agent week; false-alarm rate (an "identified" leader under zero coupling) ≤ 10%; a fast responder to a latent drive is called leader in ≥ 30% of replicates in single-room weeks (the confound is real), but its exposure contrast is ≈ 0 in two-room weeks.

**Verdict rules (round 1).**
- **Per period:** *supported* = P1's test passes (p_T < 0.05) **and** split-half ρ > 0 (where eligible; otherwise Q p < 0.05); *mixed* = transfer passes but no stable or heterogeneous structure; *failed* = p_T ≥ 0.05. Ground-truth periods also report their specific test (P5–P7), which decides the verdict there: *supported* only if the ground-truth test passes.
- **H32 (leader identification) supported in round 1:** P5 holds, P6b or P7a holds, P3 holds and P13's accuracy holds.
- **H32 failed:** P5 fails (the procedure cannot even find a known exogenous source), or the ground-truth leaders rank at or below the median in both #26 (after the decision) and #44 (operator).
- **Centralization order parameter useful:** Φ is computable (P1) in most periods and separates the synthetic star from the synthetic distributed swarm; real-data mode differences (P10b) are a bonus, not required.

## Amendment A1 (2026-10-03; from the synthetic validation only, before any real-data run)
- **A1a, exposure support.** A pair needs ≥ 10 of j's messages with a nonzero source term, in ≥ 2 folds. In any CV fold whose training set has < 5 exposed messages, the source coefficient is 0 ("cannot estimate, predict no effect"). Ridge 10⁻³ relative to the mean diagonal. Why: on the two-room #44 skeleton, coefficients fitted on 1–2 exposed messages extrapolated to G between −15% and −150% in the held-out day.
- **A1b, saturating sums.** Every decayed sum (source, mean field, humans, automated) enters as Σw·z / (1 + Σw), so bursts don't dominate. This lowered the null spread of ΔG in the two-room skeleton by ~20%.
- **A1c, second null.** N1w is a within-day circular shift of every sender (offset ≥ 3τ = 45 min, wrapping inside the day). The cross-day N1 stays primary as pre-registered. N1w controls same-day common drive, i.e. leakage of the day×room field through i's same-day messages. It is conservative: it also absorbs persistent within-day transfer (in the #13 skeleton it removed most of a planted leader's T). N1 was slightly liberal under zero coupling (2/18 runs at p < 0.05), N1w never false-positive (0/18). **C = 2 requires T significant under both.**
- **A1d, leader call and Φ.** Cochran's Q with delete-one-day jackknife variances was anti-conservative: 25–40% "heterogeneous" under zero coupling. It is replaced by two tests, both computed identically on the null replicas:
  - a **standout test**, s = (Out_top − mean of the others) / sd of the others;
  - a **max test**, max Out against the replicas' max.

  A leader is **called** if p_standout < 0.05 and p_max < 0.05. Φ's noise correction uses the null-replica variance of each Out_i instead of the jackknife (`cent_nullvar`); the jackknife version is still reported. In the per-period verdict rule, "Q p < 0.05" (periods not eligible for split-half) becomes "standout p < 0.05".
- **A1e, confirmatory field.** The confirmatory script must use a data-only field subspace, because held-out periods have no stored kickoff embeddings. That variant (`Kdata`: period mean + day×room principal directions, K = 5) is added to the round-1 robustness checks.
- **A1f, shared goal fields.** Goal and kickoff vectors now come from the shared `embeddings/goals.parquet` + `goal_vectors.npy` (kinds `goal_whole`, `kickoff_room`; `infra/shared/goal_fields.py`) instead of H01's `goals_raw.npy`, after the coordinator's notice that H01's #38 room kickoffs are swapped. No real-data statistic had been computed. The #38 swap leaves the field *span* unchanged, but H01's and the shared kickoff spans differ by 15–56° (principal angle) in #36, #37, #39, #40 and #42; flagged in Notes.
- **Ground-truth verdict detail.** If a period's ground-truth test (P5–P7) passes, the general verdict stands. If it fails, the verdict is *failed*, or *mixed* when the general verdict is *supported*. P6a (DeepSeek *not* top over the whole week) is descriptive context, not decisive.

## Confirmatory (written and dry-run; not run)
`analysis/confirm.py` targets the held-out #28 (mode C, regime I, 11 agents), #22 (mode F) and #14 (mode I). The pipeline is the primary one, with goal and kickoff vectors from the shared goal-field table (held-out rows used only under `--confirm`). Safeguards:
- it refuses without `--confirm --i-understand-this-uses-the-locked-holdout`, and refuses unless this card and the script are committed and unmodified (all three refusal paths checked);
- the default `--dry-run` runs the identical pipeline on the non-holdout stand-ins #30/#16/#17 and reproduces round 1 exactly (#30: T +0.091%, p 0.024);
- #45 is refused: H02 used its timing and H23 has reserved its content (same modality). A #45 leader test would need Vivian's decision under the reuse policy.

*Frozen 2026-10-03, after round 1 and before any look at the targets:*
- C1: #28 T significant (cross-day) [0.75].
- C2: at least one of #22/#14 not significant [0.7].
- C3: a leader is called in at most 1 of 3 [0.8].
- C4: #28 split-half ρ > 0 [0.75].
- C5: T(#28) > T(#22) and T(#14) [0.55].
- C6: #28 significant under both nulls [0.6].
- C7: #28's top source is Claude Opus 4.5 or GPT-5.2 [0.5].
- C8: #28's humans not above the median agent [0.7].

## Results by goal period
Verdicts by the card's rules (amendment A1; A2 is post hoc and shown only as a sensitivity). Units: % of held-out residual variance.

| Period | Role | Verdict | Key numbers |
| --- | --- | --- | --- |
| [G03](goalperiod-subhypotheses/G03/README.md) | exploratory, mode F | failed | T +0.003% (p 0.439; within-day p 0.810); top source Gemini 2.5 Pro (z 1.8, standout p 0.71); humans rank 2/5 |
| [G04](goalperiod-subhypotheses/G04/README.md) | exploratory, mode C | supported | T +0.032% (p 0.024; within-day p 0.095); top source Claude 3.7 Sonnet (z 4.9, standout p 0.05); Φ 0.03; split-half ρ +0.30; humans rank 1/7 |
| [G05](goalperiod-subhypotheses/G05/README.md) | exploratory, mode F | failed | T -0.025% (p 0.927; within-day p 1.000); top source Gemini 2.5 Pro (z 0.1, standout p 0.02); humans rank 2/5 |
| [G06](goalperiod-subhypotheses/G06/README.md) | exploratory, mode K | mixed | T +0.038% (p 0.024; within-day p 0.048); top source Claude Opus 4 (z 7.4, standout p 0.10); Φ 0.83; humans rank 2/5 |
| [G08](goalperiod-subhypotheses/G08/README.md) | exploratory, mode C | failed | T +0.013% (p 0.195; within-day p 0.048); top source Claude Opus 4 (z 4.4, standout p 0.63); humans rank 4/5 |
| [G10](goalperiod-subhypotheses/G10/README.md) | exploratory, mode I | failed | T +0.081% (p 0.122; within-day p 0.762); top source Claude Opus 4.1 (z 1.8, standout p 0.76); split-half ρ +0.07; humans rank 8/8 |
| [G11](goalperiod-subhypotheses/G11/README.md) | exploratory, mode F | failed | T -0.023% (p 0.902; within-day p 1.000); top source GPT-5 (z 4.2, standout p 0.22); split-half ρ -0.61 |
| [G12](goalperiod-subhypotheses/G12/README.md) | exploratory, mode M | mixed | T +0.029% (p 0.024; within-day p 0.048); top source Claude Opus 4 (z 7.0, standout p 0.44); Φ 1.13; split-half ρ +0.29; humans rank 5/8 |
| [G13](goalperiod-subhypotheses/G13/README.md) | exploratory, mode C | mixed | T +0.047% (p 0.024; within-day p 0.048); top source Claude Opus 4.1 (z 14.1, standout p 0.12); Φ 0.48; split-half ρ +0.89; humans rank 6/7 |
| [G16](goalperiod-subhypotheses/G16/README.md) | exploratory, mode F | failed | T +0.005% (p 0.268; within-day p 0.095); top source o3 (z 3.5, standout p 0.63); split-half ρ +0.68; humans rank 5/8 |
| [G17](goalperiod-subhypotheses/G17/README.md) | exploratory, mode I | failed | T +0.006% (p 0.195; within-day p 0.476); top source Claude Opus 4.1 (z 1.7, standout p 0.12); split-half ρ +0.43; humans rank 5/8 |
| [G18](goalperiod-subhypotheses/G18/README.md) | exploratory, mode C | mixed | T +0.188% (p 0.024; within-day p 0.048); top source Claude Opus 4.1 (z 15.0, standout p 0.59); Φ 0.08; split-half ρ +0.24; humans rank 6/9 |
| [G19](goalperiod-subhypotheses/G19/README.md) | exploratory, mode C | supported | T +0.118% (p 0.024; within-day p 0.048); top source o3 (z 11.2, standout p 0.32); Φ 0.11; split-half ρ +0.43 |
| [G20](goalperiod-subhypotheses/G20/README.md) | exploratory, mode I | mixed | T +0.125% (p 0.024; within-day p 0.048); top source Claude Opus 4.1 (z 12.1, standout p 0.39); Φ 0.07; split-half ρ +0.45; humans rank 11/11 |
| [G21](goalperiod-subhypotheses/G21/README.md) | exploratory, mode I | failed | T +0.019% (p 0.073; within-day p 0.238); top source Claude Haiku 4.5 (z 6.7, standout p 0.44); split-half ρ +0.79 |
| [G23](goalperiod-subhypotheses/G23/README.md) | exploratory, mode K | mixed | T +0.077% (p 0.024; within-day p 0.048); top source Claude Haiku 4.5 (z 12.6, standout p 0.02); Φ 0.81; split-half ρ +0.53; humans rank 11/11 |
| [G24](goalperiod-subhypotheses/G24/README.md) | exploratory, mode C | failed | T +0.018% (p 0.122; within-day p 0.048); top source Claude Opus 4.5 (z 2.2, standout p 0.95); split-half ρ +0.39 |
| [G25](goalperiod-subhypotheses/G25/README.md) | exploratory, mode C | supported | T +0.049% (p 0.024; within-day p 0.048); top source GPT-5.2 (z 3.2, standout p 0.29); Φ 0.03; split-half ρ +0.10 |
| [G26](goalperiod-subhypotheses/G26/README.md) | exploratory, mode C | mixed | T +0.056% (p 0.024; within-day p 0.143); top source GPT-5.2 (z 7.3, standout p 0.37); Φ 1.00; split-half ρ +0.21 |
| [G27](goalperiod-subhypotheses/G27/README.md) | exploratory, mode K | supported | T +0.116% (p 0.024; within-day p 0.048); top source Claude Opus 4.5 (z 14.3, standout p 0.29); Φ 0.08; split-half ρ +0.64 |
| [G30](goalperiod-subhypotheses/G30/README.md) | exploratory, mode C | failed | T +0.091% (p 0.024; within-day p 0.048); top source Claude Opus 4.5 (z 7.0, standout p 0.39); Φ 0.10; split-half ρ -0.40; humans rank 10/12 |
| [G31](goalperiod-subhypotheses/G31/README.md) | exploratory, mode F | supported | T +0.040% (p 0.024; within-day p 0.143); top source Claude Opus 4.6 (z 4.9, standout p 0.39); Φ 0.25; split-half ρ +0.65 |
| [G33](goalperiod-subhypotheses/G33/README.md) | exploratory, mode C | failed | T +0.025% (p 0.341; within-day p 0.952); A2 T +0.037% (p 0.244); top source GPT-5 (z 3.6, standout p 0.15) |
| [G35](goalperiod-subhypotheses/G35/README.md) | exploratory, mode C | supported | T +0.080% (p 0.024; within-day p 0.048); top source GPT-5.2 (z 4.6, standout p 0.93); Φ 0.18; split-half ρ +0.37 |
| [G36](goalperiod-subhypotheses/G36/README.md) | exploratory, mode C | mixed | T +0.039% (p 0.024; within-day p 0.048); top source Claude Opus 4.5 (z 3.5, standout p 0.56); Φ 1.46; split-half ρ -0.02 |
| [G37](goalperiod-subhypotheses/G37/README.md) | exploratory, mode F | failed | T -0.237% (p 0.927; within-day p 0.619); A2 T +0.079% (p 0.049); top source GPT-5.4 (z 3.0, standout p 0.37) |
| [G38](goalperiod-subhypotheses/G38/README.md) | exploratory, mode C | mixed | T +0.229% (p 0.024; within-day p 0.048); top source Claude Sonnet 4.6 (z 7.3, standout p 0.37); Φ 0.12; split-half ρ +0.82; humans rank 8/14 |
| [G39](goalperiod-subhypotheses/G39/README.md) | exploratory, mode I | failed | T -0.061% (p 0.610; within-day p 0.143); A2 T -0.115% (p 0.976); top source Claude Sonnet 4.5 (z 3.0, standout p 0.95); split-half ρ +0.02 |
| [G40](goalperiod-subhypotheses/G40/README.md) | exploratory, mode C | failed | T -0.175% (p 1.000; within-day p 1.000); A2 T -0.030% (p 0.512); top source GPT-5.4 (z 2.0, standout p 0.80); split-half ρ +0.01 |
| [G41](goalperiod-subhypotheses/G41/README.md) | exploratory, mode I | supported | T +0.088% (p 0.024; within-day p 0.048); top source Claude Opus 4.7 (z 7.3, standout p 0.29); Φ 0.24; split-half ρ +0.57 |
| [G42](goalperiod-subhypotheses/G42/README.md) | exploratory, mode I | supported | T +0.189% (p 0.024; within-day p 0.048); A2 T +0.165% (p 0.024); top source Claude Opus 4.7 (z 4.7, standout p 0.10); Φ 0.08; split-half ρ +0.47 |
| [G44](goalperiod-subhypotheses/G44/README.md) | exploratory, mode C | failed | T -0.003% (p 0.220; within-day p 0.095); A2 T +0.124% (p 0.024); top source Claude Opus 4.7 (z 3.0, standout p 0.63); split-half ρ +0.31; humans rank 10/17 |
| [NE42](goalperiod-subhypotheses/NE42/README.md) | exploratory (spans #39–#41) | failed | split pairs ΔG(#40) − ΔG(#39/41) = +0.0001% (27/51 positive, sign p 0.39) |

## Results
**Exploratory round 1 (2026-10-03).** Scope: 32 non-holdout goal periods (#3–#44, regimes I–III) plus NE42; holdout asserted absent in every script.
- **Code:** `scheme/build.py`; `analysis/{ic_core,synthetic,explore,synthesize,write_results,period_folders,figures,confirm}.py`.
- **Numbers:** `data/processed/H32-information-current-leaders/{explore,crossperiod,segments,ne42,ne42_A2,robust}.json`, `G<NN>/result*.json`, `synthetic/synthetic_summary.json`.
- **Figures:**
  - `figures/summary.pdf` (one-page figure summary);
  - `figures/summary_obs.pdf`;
  - `figures/synthetic_validation.pdf`;
  - `goalperiod-subhypotheses/G<NN>/figures/currents.pdf`.

**Headline.** Content transfer between agents is real but small. When agent j has seen agent i's recent messages, they improve the prediction of j's next message beyond:
- j's own past (last message, running mean, latest intention);
- the goal and kickoff field (5 directions removed);
- the day×room field;
- everything else j had seen.

The gain is significant against the cross-day shift null in **18/32** periods (15/32 also against the within-day shift). Typical size is +0.03% to +0.23% of held-out residual variance per pair. It is concentrated in a few strong pairs: the 10%-trimmed mean is significant in 15/32 under the post-hoc A2 fit. It is fast: τ = 5 min gives the most significant periods. In multi-room weeks it requires exposure: the same senders' simultaneous messages in other rooms predict nothing (7/8 periods seen > unseen; unseen significant in 1/8). The **outflow ranking is reproducible** across odd and even days (ρ > 0 in 23/26, median 0.38).

**But it does not identify leaders.**
- **No standout source.** A single source stands out in only 2/18 transfer periods.
- **#26.** The elected leader DeepSeek-V3.2 is not a source over the week (rank 5/10), before the election (8/10) or after it (7/10). The post-election conversation was carried by Claude Haiku 4.5 (z 7.0) and Claude Opus 4.5 (z 5.5).
- **#44 #best (05-28/29).** The operator ranks 5th of 7 sources. The installed fine-tuned leader (agent 28) ranks **last** of the six agents (ΔG −0.30%), while Claude Opus 4.8 and Kimi K2.6 (the leader's base model) top the room.
- **Humans as a known exogenous source.** Above the median agent's outflow in only 4/16 periods, all in the viewer-heavy early weeks #3–#6.

By the card's verdict rules, H32's leader identification **fails** (P5 failed, and both ground-truth leaders rank below the median). The installed-leader result agrees with H02 (timing) and H23 (its plans track the room): installing a leader did not create a content source.

**Who the content sources are.** Out ranks are partly talk volume (median ρ 0.34), not message length (−0.15). They agree weakly with artifact adoption (0.17), mention in-degree (0.15) and H29's net current (0.27, regime III). They are nearly independent of H02's activity-timing influence (median |ρ| 0.24). A Claude model is the top source in 21/32 periods vs 14 expected from roster shares: Claude Opus 4.1 in five periods, Claude Opus 4.5 in four, Claude Opus 4.7 in three. That may be a capability effect or a style effect (H13); not separated here.

**Order parameter Φ.** Computable wherever transfer is significant. It separates a synthetic star (0.5–0.75) from a synthetic distributed swarm (0.01–0.11). On real data it is noisy (0.03–1.5; values above 1 occur when some agents have negative outflow) and does not differ by mode: median 0.11 in C vs 0.16 in I/F periods (p 0.42). Total transfer T is higher in mode-C than in I/F periods (median 0.047% vs 0.006%, Mann–Whitney p 0.099), and does not fall with N (ρ +0.23).

**Mode, regime, rooms.**
- Transfer is clearest in the long regime-I coordination weeks (#18, #19, #20, #27; z_out up to 15) and in regime III's #38, #41, #42.
- It is absent in free weeks (#3, #5, #11, #16) and in #37/#39/#40. #40 is the merged #universe-coordination week, where the primary T is negative because two low-volume pairs are unstable.
- The room merge (NE42) did not switch on transfer for newly exposed pairs.

**Outcome vs prediction** (credences from the pre-registration):

| | Prediction [credence] | Observed | Verdict |
| --- | --- | --- | --- |
| P1 | p_T < 0.05 in ≥ 60% of periods [0.70] | 18/32 = 56% (15/32 both nulls); A2 post hoc 20/32 | **failed** (narrowly) |
| P2 | Leader stands out (heterogeneity) in ≥ 50% of transfer periods [0.50] | standout p < 0.05 in 2/18 (#4, #23) | **failed** |
| P3 | Split-half ρ > 0 in ≥ 2/3, median ≥ 0.3 [0.50] | 23/26, median 0.38 (A2: 21/26, 0.26) | **supported** |
| P4 | Median ρ(Out, count) < 0.8 [0.65]; Out ranks known sources above count [0.40] | 0.34; humans ranked higher by Out than by count in 12/16 | supported (both parts; the second is partly mechanical, since humans post little) |
| P5 | Humans above the median agent in ≥ 70% [0.70] | 4/16 (only #3–#6); significant positive outflow in 6/16 | **failed** |
| P6a | DeepSeek not top over #26 [0.55] | rank 5/10 | supported |
| P6b | DeepSeek top after the decision [0.30] | rank 7/10 (z 0.1) | **failed** |
| P7a | Temporary leader not top in #best [0.75] | last of 6 agents (z −1.5) | **supported** |
| P7b | Operator top in #best [0.55] | 5th of 7 (z 1.0) | **failed** |
| P7c | Same-room > cross-room, cross-room CI includes 0 [0.70] | both ≈ 0 (#44 shows no transfer in the primary fit) | passes as written, uninformative |
| P8 | Seen > unseen; unseen CI includes 0 [0.65] | 7/8 periods seen > unseen (sign p 0.035); unseen significant 1/8 | **supported** |
| P9 | NE42 split pairs gain in #40 [0.55] | +0.0001% (27/51 positive, p 0.39) | **failed** |
| P10a | T higher in C than I/F [0.45] | p 0.099 | supported (weak) |
| P10b | Φ higher in C than I/F [0.30] | p 0.42 | failed |
| P10c | T falls with N [0.60] | ρ = +0.23 | failed |
| P11 | \|ρ\| with H02 timing < 0.3 [0.60] | median \|ρ\| 0.24 (n 15) | supported |
| P12 | ρ with artifact adoption > 0 [0.55], with mention in-degree > 0 [0.65] | 0.17; 0.15 | supported (weak) |
| P13 | Synthetic recovery ≥ 80%, false alarms ≤ 10%, fast responder confound ≥ 30% (exposure flags it) | 100% (#26 skeleton, ψ 2%); 0–10%; 90%, seen ≈ unseen for F | supported |

**Amendment A2 (POST HOC, 2026-10-03, after the first real-data run).** Day-concentrated low-volume targets (22–31 messages, most on one day) made leave-one-day-out unstable. Two pairs gave G of −9% to −14% and drove the negative T of #37 and #40. Sensitivity rerun with folds skipped when their training set has < 20 of j's messages, plus a 10%-trimmed T:
- #44 becomes significant (+0.12%, p 0.024) and #37 marginal (+0.08%, p 0.049);
- #40 stays null and #39 negative;
- P1 becomes 20/32, split-half stability falls to median 0.26 (21/26), and no ground-truth verdict changes (the segment tests are unaffected).

Primary verdicts use the pre-registered fit.

**Caveats.**
- **Small effects, many tests.** Effects are fractions of a percent of residual variance. With 32 periods × 18 predictions, a few "passes" are expected by chance. Cross-period tests use one statistic per period.
- **Common drive.** Fast responders to an unobserved drive are indistinguishable from leaders in single-room weeks (synthetic: called leader 90% of the time). Only multi-room weeks give the exposure contrast, and only the within-day null removes their T.
- **Agenda setting.** A one-shot agenda-setting message (the #26 leader announcing the goal) is poorly captured by a stationary linear transfer coefficient. The method sees sustained conversational influence, not decisions.
- **Volume.** Humans post few messages. Outflow is a *total* contribution, so low-volume sources rank low even if each message matters (a per-message coupling was not computed).
- **Preprocessing.** The level of transfer depends on how much field is removed (25 → 18 → 7 periods for K = 1, 5, 10), and the identity of the top source is not robust (13–27/32 across variants). No second embedding model.
- **Measurement.** Exposure is room membership at posting time. Regime-I session gating and regime-III context limits (H08) are not modelled. The H29 recency confound affects seen-vs-unseen tests; seen and unseen messages share the same decay weights here, but are not matched in age bins.
- **Data note.** H01's kickoff vectors (#38 rooms swapped; spans for #36, #37, #39, #40 and #42 differ from the shared table by 15–56°) were replaced by the shared goal fields before any real-data run.

**Operator-facing procedure** (what to compute from logs; ~10–50 s per goal period on a laptop):
1. Embed every chat message and whiten per regime. Unit-normalize, then project out a 5-direction field: goal text, kickoffs, period mean, day×room principal directions.
2. For each ordered pair (i → j), compute the leave-one-day-out predictive gain of the exposure-gated decayed sum of i's messages (τ = 15 min) on j's next message. Baseline: j's own past, the day×room field, everything else j saw, and humans and bots. Require ≥ 10 exposed target messages.
3. Subtract the median of 40 cross-day circular-shift replicas. Report Out, In and Net per agent, total transfer T with p_T, and the within-day check.
4. Read it as follows:
   - **T not significant:** "no measurable content coupling";
   - **T significant, no standout:** "distributed: content flows among several agents". This was the common case here (16/18);
   - **standout p < 0.05 and max p < 0.05:** name the top source as the de facto content leader. In single-room swarms, warn that it may be a fast responder to an outside drive. In multi-room swarms, check its unseen-room outflow.
5. **Do not** read the result as "who is in charge": formal, elected and installed leaders were not content sources in this village.

**Next steps.**
1. Confirmatory run on #28/#22/#14 after sign-off (frozen predictions C1–C8 below).
2. A per-message coupling κ_i (gain per exposure) alongside total outflow, so low-volume sources such as operators are judged fairly.
3. An event-study variant for one-shot agenda setting: the response of everyone's content direction to a single message, e.g. the #26 announcement.
4. A family/style control (H13 residualization) before naming top sources.
5. Matched age bins for seen vs unseen (H29 recency confound).
6. A second embedding model.
7. #51 segments (four rooms, private roles) for the exposure contrast with more power.

## Round 1b (improved data, 2026-10-04)

### Inputs changed
- **Exposure (DQ1 context ledger).** Round 1: i's message was "seen" by j's message m if j was in its room and it was posted before m. Round 1b: seen iff it was posted in j's room before **the start (`t_call`) of the call that produced m** (j's latest `call_windows` start before m). Same-room messages posted during that call are now **unread** (in flight) and leave the source term. The same rule is applied to every shifted null replica. Other-room messages stay the "unseen" term of the exposure contrast (P8).
- **Copying vs convergence (H57).** New placebo: the second source term holds i's *unread* same-room messages (posted after j's call started, before m). Copying through reading predicts seen ≫ unread; contemporaneous convergence (both answer the same prior turn) predicts unread ≈ seen. Run at the card's τ = 15 min (all 32 periods) and at **τ = 60 s** (window 3 min, both terms recent; the 17 periods with transfer), which roughly matches ages.
- **Embeddings (DQ5).** Second model gte-modernbert (whitened in the period's regime basis, gte goal fields) and bge style-residualized within goal period (`statements_style_resid_period32`); 20 null replicas each.
- **Dedupe (DQ5 `statement_flags`).** Targets flagged cross-echo (either model), templated (either) or self-repeat (both) are dropped (1–35% of targets).
- **Goal fields** were already the shared ones (A1f); the H01 #38 swap never reached H32. Activity bins, outages and reply threading are not used by H32's estimator.
- **Code.** Switches in `analysis/ic_core.py`: `H32_DATA=r1b`, `H32_EMB=bge|gte|style`, `H32_S0=other|unread` (plus `H32_DEDUPE`, `H32_TAU` in `analysis/r1b.py`); defaults reproduce round 1 exactly (checked: #26 T = +0.0563%, p 0.024, identical). New: `scheme/build_r1b.py` (vectors), `analysis/r1b.py` (runs, natives), `analysis/r1b_assemble.py` (tables, verdict lines, 237 `per_period_estimates` rows, methods `H32.r1b_*`). Outputs: `data/processed/H32-information-current-leaders/r1b/` (22 MB).

### Old → new (32 non-holdout periods; % of held-out residual variance)
| Statistic | Round 1 | 1b ledger (bge) | 1b gte | 1b style-resid | 1b dedupe |
| --- | --- | --- | --- | --- | --- |
| P1 T significant (cross-day null) | 18/32 | **17/32** | 23/32 | 18/32 | 16/32 |
| Out ranking vs ledger-bge (median Spearman ρ; same top source) | 0.99 vs round 1; 28/32 | — | 0.77; 17/32 | 0.77; 22/32 | 0.99; 30/32 |
| P3 split-half ρ > 0 (median) | 23/26 (0.38) | 20/26 (0.27) | — | — | — |
| P8 seen > unseen-other-room (multi-room) | 7/8, unseen significant 1/8 | 7/8 (sign p 0.035), 1/8 | — | — | — |
| P5 humans above the median agent | 4/16 (≥ 15 human msgs) | 6/29 (any humans) | — | — | — |
| Per-period verdicts (supported / mixed / failed) | 8 / 9 / 15 | 9 / 7 / 16 | — | — | — |
| **H57, τ = 15 min:** unread term significant / seen significant | — | 24/32 / 16/32; seen > unread in 12/32 | — | — | — |
| **H57, τ = 60 s (17 transfer periods):** seen > unread; unread significant; median T seen vs unread | — | **17/17**; 13/17; 0.20% vs 0.07% | — | — | — |

Verdict changes: G04 supported → mixed (split-half ρ −0.20); G35 supported → failed (T halves, p 0.073, plus the native); G26 mixed → failed (native); G06, G36, G38 → supported; G30 failed → mixed.

**Reading.**
1. **The ledger changes almost nothing for H32.** Room exposure at posting time and ledger exposure agree for nearly every pair at τ = 15 min; only messages posted during j's own call move (to "unread"). Transfer level, rankings and the exposure contrast replicate.
2. **Transfer is model-dependent in level and identity, robust in existence.** gte finds transfer in more periods (23/32) and agrees with bge on the top source in only 17/32 (ρ 0.77); removing style within periods keeps 18/32 but changes the top source in 10/32. Statement-level claims (who the top source is) are not robust across embedding models, in line with DQ5. Copies are not the carrier: dropping echoes and templates leaves T and rankings unchanged (ρ 0.99).
3. **Most of the τ = 15 min transfer is matched by unread messages.** Messages j could not yet have read predict its next message better than the ones it had read in 20/32 periods. This is the co-response effect RE-V2 flagged for H29: j and i answer the same prior turn. Matching ages with a short kernel (τ = 60 s) separates them: **read messages beat same-age unread ones in 17/17 transfer periods**, and unread ones carry about a third of the read effect (0.3–0.6 in regime I/II periods, ≈ 0 in regime III's #36, #38, #42). So reading-based content transfer is real, but about a third of the naive short-lag gain is convergence.

### Natives (predictions written 16:45 UTC before running; all three as predicted)
| Folder | Test | Result | Verdict |
| --- | --- | --- | --- |
| [G26](goalperiod-subhypotheses/G26/README.md) | elected leader over its real term (DQ6: 01-05 19:35 → 01-09) | DeepSeek-V3.2 rank 5/10, z +0.55; top sources Claude Opus 4.5 and Gemini 2.5 Pro | failed |
| [G35](goalperiod-subhypotheses/G35/README.md) | daily designated lead designers (5 testable room-days) | mean percentile 0.43 (p 0.69); 1/5 in the top half | failed |
| [G44](goalperiod-subhypotheses/G44/README.md) | installed leader over DQ6's window (05-26 19:15 →) | agent 28 last of 6 (z −2.4); operator 6th of 7 | failed |

Elected, designated and installed leaders are not content sources. The negative ground-truth result now holds on the correct #26 window, on three designated leaders per room, and on the full #44 window.

### Scorecard changes
| Axis | Round 1 | 1b | Why |
| --- | --- | --- | --- |
| A mapping | 1 | 1 | Exposure on validated call starts; but the top source changes with the embedding model (17/32) and with style removal (22/32). |
| C adequacy | 1 | 1 | 17/32 (bge) – 23/32 (gte) significant. |
| D unfitted | 1 | 1 | Split-half stability weaker (20/26, 0.27); exposure contrast replicates. |
| E interventional | 0 | 0 | NE42 not re-run (ledger exposure leaves cross-room pairs unchanged). |
| F identifiability | 1 | 1 | Second embedding model done: existence robust, identity not. |
| G ground truth | 1 | 1 | Three leader natives, all negative as predicted; humans above the median agent in 6/29. |
| H comparative | 1 | 1 | New rival, convergence (H57): beaten at matched short lag (17/17) but accounts for about a third of the gain. |

**Model- and style-dependent results:** which agent is the top source (17/32 agreement across models; 22/32 with style removed); the per-period count of significant transfer (17 vs 23). Not model-dependent: that transfer exists in about half the periods, needs exposure, and does not single out leaders. Suggested ratings: completeness 52 (from about 45), faithfulness 1.5, usefulness 2.0.

## Notes
- 2026-10-04: promoted from HH118 by Vivian (usefulness-first batch); wave 1.
- 2026-10-03: pre-registration written (Model, Data scheme, Observables, Null, Prediction) before any real-data run.
- 2026-10-03: A1 (synthetic only) before any real-data run; shared goal fields adopted after the coordinator's notice (no real-data result affected).
- 2026-10-03: round 1 done; A2 post hoc sensitivity; confirmatory predictions frozen in `analysis/confirm.py`. Disk: see report (`data/processed/H32-information-current-leaders/`).
- Suggested DEFINITIONS.md variants (not added; outside this card's edit scope): **content transfer (exposure-conditioned, cross-validated Gaussian)** = leave-one-day-out predictive gain of the exposure-gated decayed sum of i's messages on j's next message beyond own past, day×room field, mean field and exogenous messages, minus the circular-shift null median (Granger/Gaussian TE); **outflow centralization Φ** = (Var Out − mean null variance)/(mean Out)²/(N − 1).
