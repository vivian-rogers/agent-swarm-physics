# H47: Rooms set the coherence length

**Status:** exploratory round 1 done (2026-10-04): **mixed.** Claim 1 (coherence length = room) **supported by its rule**: content co-moves inside rooms and much less across them (C_B ≤ 0.3 with p < 0.05 in 6/9 multi-room periods, median 0.23), and NE42's merge/split moves the boundary with the channel (DiD 1.0, p 0.001). But a room is not a flat block (inside rooms correlation sits in pairs that address each other, G ≈ 0.4; 0.18 in #51's big room), and post hoc the boundary is sharp only where rooms work on different topics. Claim 2 (per-room detector beats the swarm one) **failed** (unpowered: 2 clean room events). Claim 3 (one room leads at goal changes) **failed**: both rooms switch within minutes of the kickoff. `analysis/confirm.py` written and dry-run, not run. Predictions, nulls and verdict rules below were written 2026-10-04 ~05:40 UTC, before the synthetic validation and before any H47 statistic on real data. Promoted 2026-10-04 by Vivian from HH172.
**Fields:** stat mech (correlation length of a vector-spin field), sociophysics (group boundaries), info theory (where shared content lives), dynamics (lead–lag)
**Literature:** none specific beyond `physics-models/11-vector-spins/README.md` (Stanley 1968, Bialek et al. 2012 on flock correlation functions).
**Definitions used** (`physics-models/DEFINITIONS.md`): Agent; Regime; Interaction (broadcast: co-located = same current room); Agent state, *vector (for model 11)* in H26's named variant **"agent state (vector), linear statement mean"** (unnormalized mean of whitened, unit-normalized 32-d bge statement vectors per agent and window); H26's **"loop gain (equal-time, room excess)"** pair correlations ρ_w, ρ_c (split-half normalized); H36's **"content centroid shift (R1)"**; Population N(t) (agents with statements in the window). **New named variants proposed** (for whoever owns DEFINITIONS.md; not edited here): *room contrast C_B*, *conversational tier ratio G*, *room-localized centroid shift R1_loc*, *room lead index L* (all defined under Observables).
**From:** HH172 in `hypotheses/hypohypotheses/HYPOHYPOTHESES.md` · **Models:** `physics-models/11-vector-spins/`
**Data inputs (shared tables first):** shared bge statement embeddings + regime whiteners (`embeddings/statements`, `chat_bge_small`, `intentions_bge_small`, `whitening_<regime>`), `embeddings/agent_day` (+ `agent_day_vec`), `rooms`, `rooms_timeline`, `period_units`, `goal_fields` (`embeddings/goals.parquet`, kind `goal`/`kickoff`/`kickoff_room`), `outages`/`stall_minutes` (village-off windows), `chat_core` + `chat_mentions_clean`, `kicks_classified` (room kickoff times), DQ6 `ground_truth_labels` (`room_assignment` vs `room_presence`), DQ5 style-residualized statement vectors (`statements_style_resid32_bge_small.npy`). DQ5's second embedding model (gte) does not exist yet → embedding swap is round 2.

## Standards (2026-10-04)
*Documentation pass against `STANDARDS.md`. No analysis was re-run. H47 has no round-1b section; every entry rests on round 1.*

**Question served:** Q1. The card asks whether rooms bound content coherence because they route reading (NE42). Q2 second: C_B cannot tell coupling from a room-level drive (Amendment 1a).

| Impostor | Relevant? | How it was handled | Status |
| --- | --- | --- | --- |
| Scheduler field | partly | The room-relabel null permutes labels within each slot and keeps room sizes (N1), so swarm-wide timing cancels in C_B. Village-off windows are dropped with the old `outages` table. | removed |
| Exogenous field (kickoff/goal/operator) | yes | Goal, kickoff and per-room kickoff directions from `goal_fields` are projected out (L1). Room-specific task drives are not separable from coupling: C_B tracks topic separation (Spearman −0.83, post hoc). NE42 is goal-confounded. | partly |
| Shared model priors | partly | DQ5 `style_resid` vectors as a sensitivity variant (\|ΔC_B\| ≤ 0.13). | removed |
| Contemporaneous convergence | yes | Not handled. Within-room co-movement may be convergence on a shared room topic. Close with the read-out test: drift toward read vs unread room messages at matched age (R1; §1, row 4). | open |

**Inputs:** still old: village-off masks from `outages` / `stall_minutes`, not `outages_fixed`; content on bge only (no gte); conversational tiers from `chat_mentions_clean`, not DQ2 replies; no context-ledger visibility. DQ5 `style_resid`, the self-repeat flag and DQ6 room assignments are used.

**Two layers:** 5 replication folders. Native tests: 5 (`G38`, `G41`, `G44` supported; `NE42` mixed; `G51` failed).

**Confirm script:** `analysis/confirm.py` exists, dry-run only. It reads the old `outages` table and bge only. **Re-freeze on `outages_fixed` before any holdout run** (holdout.md item 8); add gte as a sensitivity.

## Question
Does content correlation drop sharply at room boundaries (so the coherence length of the swarm's content field is the room), does a per-room topic-shift detector beat the swarm-level one on room events, and does one room shift first and lead the others at swarm-wide goal changes?

## Design: two layers (Vivian, 2026-10-04; see `infra/data-quality/QUEUE.md`)
- **Replication:** the common estimator (room correlation function, C_B) on every eligible multi-room goal period. Period README role: `replication`. G35, G36, G37, G39, G42 (templated prediction, labelled as such).
- **Period-native tests** (role `native`), each with its own observable, null and dated prediction:
  - **G41** (identical instructions in both rooms): the clean test of channel-coupling vs room-specific drive; plus between-room centroid divergence (endogenous symmetry breaking).
  - **G38 and G44** (room-specific instructions): the drive-confounded contrast; share of room co-fluctuation carried by the room-instruction directions.
  - **NE42** (A-B-A merge/split, #39 → #40 → #41): does the boundary in content correlation follow the channel?
  - **G51** (#focus weeks: 51f → 51g → 51h, plus the single-room 27-agent units): does a self-made side room cut coherence, and is coherence in one big room flat across conversational distance?
- The detector test and the leadership test span periods; their per-event numbers go in the period/NE folders where the event sits (NE42, G51; goal changes in G36–G44) and the synthesis is here.

## Model
**From:** `physics-models/11-vector-spins/` (soft-spin O(n), linear kinetic form).

Each agent i carries a content vector s_i(t) ∈ ℝ³² (whitened bge). Kinetic soft-spin rule (the synthetic generator):

  s_i(t+1) = φ s_i(t) + (1 − φ)[ J m_{r(i)}(t) + J_p Σ_{j∈∂i} s_j(t)/|∂i| + h_i + h_{r(i)}(t) + h_g(t) ] + η_i(t)

with m_r the room mean (broadcast coupling, J), ∂i a sparse set of conversation partners inside the room (pairwise coupling, J_p), h_i static agent fields, h_r(t) time-varying room drives, h_g(t) global drives (goal, schedule, platform). Observed statements are noisy samples of s_i.

**Correlation function on a room graph.** Distance is categorical: same room (r_ij = 0) vs different rooms (r_ij = 1); inside a room, conversational distance (pairs that address each other a lot vs rarely). The coherence length is "the room" if C(r = 1)/C(r = 0) ≈ 0 while C stays flat across conversational distance inside the room (a mean-field block). A conversation-limited ξ shows up as within-room decay; a swarm-wide ξ as C(1) ≈ C(0).

**Rivals:**
- **R-global:** global drives dominate; coherence is swarm-wide (C_B ≈ 1).
- **R-drive:** rooms are coherent because each room gets its own time-varying drive (instructions, task phases), not because agents couple. C_B cannot tell R-drive from coupling (H26 synthetic); G41's identical instructions and NE42's A-B-A are the levers.
- **R-conversation:** coherence is set by who talks to whom, not by the room (within-room decay, G ≪ 1).
- **R-leader (for the leadership claim):** rooms respond to a goal change with equal speed; apparent leads are sampling asymmetry (room size, message rate, late starts).

## Data scheme (`scheme/`)
`scheme/build.py` → `data/processed/H47-room-coherence-length/` (≤ 200 MB, `_provenance.json`). Non-holdout days only, asserted with `holdout_mask` and `calendar.holdout`.
- **Statements:** agent chat + intentions (shared `embeddings/statements.parquet`) from 2026-03-16 on (rooms era with structural rooms), Claude Code agent excluded, holdout days dropped. Each statement gets: whitened 32-d unit vector (`common.load_whitener(regime, 32)` on the raw bge embedding; frozen fp16 copy), its `period_units` unit, its 30-min window of the day (`calendar.win_start`), its room (chat: the message's room; intentions: the agent's room at that time from `rooms_timeline`), the DQ6 assigned room, and a **self-repeat flag** (raw bge cosine > 0.95 to an earlier chat statement by the same agent that PT day; infra Known issues). The DQ5 style-residualized vector is copied alongside (robustness).
- **Agent room per window/day:** modal room over the agent's statements (presence); assigned room from DQ6 where defined (`room_assignment`, `preferred & ~holdout`).
- **Village-off windows:** windows with ≥ 50% of minutes inside shared `outages` runs flagged `village_off` are dropped.
- **Mention counts:** per unit, directed clean mentions (`chat_mentions_clean.mentions_roster`) between agents → pair weights m_ij = m_{i→j} + m_{j→i}.
- **Day vectors for the detector:** shared `agent_day` raw 384-d vectors centered on the non-holdout mean (H36's R1 convention, Amendment 0e there), with the agent's modal room that day.
- **Static field directions per unit:** shared `goal_fields` rows of the unit's goal (`goal`, `kickoff`, `kickoff_room`), whitened, orthonormalized (H26's L1).
- **Regimes covered:** II (#35, #36a) and III (#36b–#44, #51 non-holdout). Holdout periods #43, #45–#50, the #51 tail and every NE window are excluded.

## Observables
*Written 2026-10-04 ~05:40 UTC, before any H47 statistic on real data.*

All content statistics use H26's estimator (imported read-only from `hypotheses/H26-content-near-critical/analysis/h26lib.py`): per pair class, ρ = Σ_{pairs,slots} δs_i·δs_j / Σ_{pairs,slots} √(S_i S_j), with δs the agent's deviation from its unit mean after projecting out the unit's static field directions (H26's L1) and S_i the split-half signal variance. Primary resolution **w30** (equal-time 30-min windows; many units are 1–3 days); day level secondary for units ≥ 3 days. Self-repeats dropped; village-off windows dropped.

- **O1. Room correlation function and room contrast.** ρ_w (same-room pairs), ρ_c (different-room pairs), **C_B = ρ_c / ρ_w** (0 = sharp boundary, 1 = no boundary) and **Δ_B = ρ_w − ρ_c**. Per unit and pooled over a period's units (sums over units; each unit keeps its own centering).
- **O2. Conversational tier ratio inside rooms.** Same-room pairs split at the unit's median mention weight m_ij into "high" and "low" tiers; **G = ρ_w,low / ρ_w,high** (1 = flat inside the room, i.e. a mean-field block; ≪ 1 = conversation-limited). Sharp-boundary criterion: the boundary drop (1 − C_B) exceeds the within-room drop (1 − G).
- **O3. Room-localized centroid shift (detector).** For day d and each cohort c (agents grouped by their room on d, and separately by their room on d − 1; |c| ≥ 2 and smaller than the set of agents present on both days), D_c = 1 − cos(mean of the cohort's day-d vectors, mean of the same agents' day-(d−1) vectors). z_c = (D_c − mean)/SD over 300 random same-size cohorts drawn from the agents present on both days. **R1_loc(d) = max_c z_c** (undefined on single-room days). Rivals: **R1_swarm** (H36's R1 exactly, trailing-z, 10 days), **R1_naive** (max over persistent room codes of the per-room R1, trailing-z per room), and **R1_comb** = max(R1_swarm z, R1_loc).
- **O4. Room lead index (leadership).** On a goal-kickoff day, cohorts = rooms (#40: previous rooms; #41: new rooms). For cohort r, statements in 15-min bins from the room's kickoff message; y_r(τ) = (x̄_r(τ) − pre_r)·u_r / |post_r − pre_r| with pre_r = the cohort's mean on the last non-holdout active day before the kickoff, post_r = its mean over the next two active days, u_r the unit vector of post_r − pre_r (raw 384-d bge, so no whitening jump across 03-24). **L = mean over the first 8 bins (2 h) of y_A(τ) − y_B(τ)**, using only bins with ≥ 3 statements in both cohorts (A = #best, B = #rest; L > 0: #best ahead). Secondary: T50 difference (first bin where a 2-bin rolling y ≥ 0.5).
- **O5. Native observables.**
  - G41/G38/G44: **between-room centroid distance** per day, D_rooms(d) = 1 − cos(m̄_best(d), m̄_rest(d)) on whitened agent-day means, with a room-relabel null; its day-0 value and its trend over the unit (Spearman).
  - G38/G44 vs G41: **instruction-direction share** = (Δ_B(L0) − Δ_B(L1)) / Δ_B(L0), where L1 projects out the unit's goal, kickoff and per-room kickoff directions.
  - NE42: pairs labelled by the A partition (modal room in #39 and #41; agents not in both are dropped); **r_X = ρ_XP / ρ_WP** (cross-partition over within-partition) in #39, #40, #41; DiD = r_X(40) − mean(r_X(39), r_X(41)).
  - G51: F = agents with #focus as modal room on ≥ 2 days of 51g; **r_F = ρ_FG / ρ_GG** (focus-member–general pairs over general–general pairs) in 51f, 51g, 51h; G in every single-room #51 unit.
- **Robustness:** L0 vs L1; dedupe on/off; DQ6 assigned rooms instead of presence (35–44); DQ5 style-residualized vectors; day vs w30.

## Null / baseline
- **N1. Room-relabel permutation (primary for O1/O5):** agents' room labels permuted within the unit, keeping room sizes per slot (H26's `permute_rooms`), 300 draws; p for Δ_B (one-sided), and for r_X / r_F with partition labels permuted at agent level.
- **N2. Tier permutation (O2):** mention tiers permuted among same-room pairs (tier sizes kept), 300 draws.
- **N3. Random cohorts (O3):** built into R1_loc (same-day, same-size random cohorts).
- **N4. Placebo days (O3):** H36's design: non-holdout active days ≥ 3 active days from every catalogued event; here restricted to multi-room days (≥ 2 rooms with ≥ 2 agents on d or d − 1) so that R1_loc is defined; hits = alarm on day −1, 0 or +1; AUC on day 0 vs placebos.
- **N5. Cohort-relabel permutation (O4):** agents permuted between the two cohorts (sizes kept), pre/post/u recomputed for each permuted cohort, 500 draws; p for |L|. Agent bootstrap within cohort for a CI.
- **N6. Synthetic worlds (axis F):** global-drive-only, room-drive-only, room-coupling, pairwise-coupling and mixed worlds at village sampling (below), plus detector and leadership worlds with known truth.

## Faithfulness scorecard
Scored per model, mapping and window; 0 = not done or failed, 1 = partial, 2 = passed. Scheme and promotion thresholds: `writeup/paper.tex`, Sec. "Assessing model faithfulness".
**Rival models:** R-global, R-drive, R-conversation, R-leader (above).
**Locked holdout used for confirmation:** none run. `analysis/confirm.py` targets #45, #46, #47, #50 (C1, C2), NE15 with the held-out #34d as its pre side (C3), the #46 kickoff (C4) and the #showcase-live opening inside #46 (C5). Written and dry-run on non-holdout stand-ins; not run.

| Axis | Test | Score | Evidence |
| --- | --- | --- | --- |
| A mapping | variables defined from dataset fields; assumptions listed; invariant across families and regimes | 1 | Content state = linear mean of regime-whitened bge statement vectors per agent and 30-min window (H26 variant); rooms from presence (`rooms_timeline`, chat rooms) and DQ6 assignment (same C_B within 0.02); mentions from `chat_mentions_clean`. Assumptions listed. Regimes II and III only; families not checked; one embedding model. |
| B assumptions | stationarity, Markov order, time-rescaling, update-order audit | 1 | Equal-time estimator within short units (1–17 days), stationarity assumed; the synthetic derived the reading rule (C_B = global share of a room's collective fluctuation). Leadership found the quench completes within the first statements (1–3 min), so 15-min bins can't resolve timing. No Markov or update-order audit. |
| C adequacy | beats the null hierarchy, day-blocked held-out data | 1 | Room-relabel null beaten in 7/9 periods (p ≤ 0.02), rule-supported in 6/9 (3 mixed: G37, G39, G42). Tier-permutation null beaten in 8/9 (correlation concentrated in talking pairs). No held-out-day likelihood. |
| D unfitted predictions | unfitted statistics and the model's signature | 1 | Pre-registered NE42 DiD met (1.0, p 0.001). The block signature (flat inside rooms, G ≥ 0.6) failed (median 0.40); detector and leadership predictions failed. |
| E interventional | predicts the change across a natural experiment | 1 | NE42 A-B-A: content coherence follows the channel (r_X 0.57 → 1.37 → 0.17), rejecting a persistent team identity. Goal-confounded; one event; the #focus side room was not informative (2 members, already decoupled). NE15 reserved for confirmation. |
| F identifiability | synthetic recovery with village sampling; robust to preprocessing | 1 | Synthetic: C_B separates global from room-local fluctuation but not coupling from room drive (0.04 vs 0.05 at no global drive; coupling raises C_B to 0.43 under a weak global drive); G separates broadcast from pairwise coupling (0.98 vs 0.68); the A-B-A DiD separates channel (0.47) from identity (−0.06); L keeps size under sampling asymmetry (0.02–0.06). Real C_B robust to L0/L1, dedup, DQ5 style vectors, DQ6 rooms (Δ ≤ 0.13). No embedding swap. |
| G ground truth | agrees with known structure | 1 | The two periods with room-specific kickoffs (#38, #44; goal_fields cosine 0.86, 0.81) have the sharpest boundaries (C_B 0.07, −0.04); NE42's merged partition behaves as one room; DQ6 assigned and actual rooms agree. |
| H comparative | beats the named rivals | 1 | Beats R-global in 6/9 periods. Does not beat R-drive: post hoc, boundary sharpness tracks topic separation (Spearman −0.83) and instruction type. R-conversation wins inside rooms (G ≈ 0.4; 0.18 in #51). R-leader wins (no room lead). |
| I transfer | holds in other same-mode periods, including the holdout | 0 | Holdout not run. Strong heterogeneity across periods (C_B −0.04 to 0.57), organized by topic separation. |

## Prediction
*Written 2026-10-04 ~05:40 UTC, before the synthetic validation and before any H47 statistic on real data.*

**What I had seen when writing this (so these are not blind):** the H26 card (day-level ρ_w and ρ_c per H01 unit; cross-room content ρ_c ≈ 0.05; #41 room excess 0.77; content within-room ρ falls with room size), the H01 and H05 cards (rooms more ordered than random groups; ρ_within 0.06–0.66 vs ρ_cross −0.01 to 0.14; talk couples within rooms only), the H36 card (R1 AUC 0.95 on goal changes; R1 z 5.2 at the 05-04 merge and 9.0 at the 05-11 split; room events 1/5 for the physics alarm), and design facts: room sizes (#best 4–6, #rest 7–13), per-room chat counts per goal, #focus membership (2 persistent members, ~5 short visitors; 08-05 → ~08-24), per-room kickoff messages arrive within 2 s of each other (#36–#44), DQ6 assigns everyone to #general in #51 (#focus is agent-made). No H47 estimator had been run on any real unit.

- **P0, synthetic (axis F; run first).**
  - (a) Global drive only: C_B ≥ 0.7, and N1 rejects in ≤ 10% of worlds at α = 0.05 [0.7].
  - (b) Room broadcast coupling (J only) and room drive only (J = 0) both give C_B ≤ 0.3 with N1 p < 0.05 in ≥ 80% of worlds, and are indistinguishable by C_B (|ΔC_B| < 0.1) [0.7]: the drive confound, stated.
  - (c) Pairwise conversational coupling inside rooms gives G ≤ 0.6; broadcast coupling gives G ≥ 0.8 [0.55].
  - (d) A one-room content switch at a day boundary: R1_loc AUC ≥ 0.8 and above R1_swarm's; a global switch: R1_swarm AUC ≥ 0.9, R1_loc ≤ 0.65 [0.6].
  - (e) Equal response speed with asymmetric sampling (room sizes 5 vs 11, message rates ×2, one room starting 20 min late): L's permutation test false-leader rate ≤ 0.10 [0.6]; the T50 difference has a false-leader rate > 0.2 [0.5]; a planted 30-min lead is detected by L (p < 0.05) in ≥ 50% of worlds [0.5].
- **P1, coherence length (replication layer; headline).** At w30 the content correlation drops at the room boundary: C_B ≤ 0.3 with N1 p < 0.05 in ≥ 2/3 of eligible periods; median C_B over periods ≤ 0.25 [0.7].
- **P2, sharpness inside rooms.** Median G ≥ 0.6 over periods [0.5], and the boundary drop exceeds the within-room drop, (1 − C_B) > (1 − G), in ≥ 2/3 of periods [0.55].
- **P3, detector.** On room events, AUC(R1_loc) > AUC(R1_swarm) (day 0 vs multi-room placebo days) [0.45]. Both alarms fire within ±1 day of the goal-confounded NE42 merge and split [0.7]. On the clean #focus opening (08-05): R1_swarm z < 3 [0.6] and R1_loc ≥ 2 within ±1 day [0.35; #focus had about two core members]. With ≤ 6 room events this is close to unpowered; the verdict is descriptive unless the clean events agree.
- **P4, leadership.** No room leads beyond the sampling null: |L| has N5 p ≥ 0.05 in ≥ 2/3 of goal changes [0.6], and no consistent leader (the same room ahead in ≤ 5 of 8 goal changes) [0.65]. HH172's third prediction is therefore expected to fail: rooms cannot read each other, and the kickoff reaches both rooms within seconds.
- **P5, G41 (native).** C_B(41) ≤ 0.3 with N1 p < 0.01 [0.7]; G41's boundary is as sharp as the G38/G44 median (|C_B(41) − median(C_B(38), C_B(44))| ≤ 0.15) [0.55]; between-room centroid distance rises over the week (Spearman > 0) [0.45].
- **P6, G38 and G44 (native).** Instruction-direction share ≤ 0.15 in both [0.6]; day-0 between-room centroid distance larger than G41's day 0 [0.7].
- **P7, NE42 A-B-A (native).** r_X ≤ 0.3 in #39 and #41 and ≥ 0.7 in #40 [0.55]; DiD > 0.4 with partition-permutation p < 0.05 [0.5]; residual partition memory in #40, r_X(40) < 0.9 [0.5].
- **P8, G51 (native).** r_F(51g) < min(r_F(51f), r_F(51h)) − 0.2 [0.4]; G ≥ 0.6 in the single-room #51 units (median) [0.45]. Underpowered (2–3 core #focus members).

**Verdict rules.**
- *Replication period* (w30, pooled over the period's units): **supported** if C_B ≤ 0.3 and N1 p < 0.05; **failed** if C_B ≥ 0.6 or N1 p > 0.2; **mixed** otherwise.
- *Native periods:* by their own predictions above (supported if the primary item — P5 first clause, P6 first clause, P7 first clause, P8 first clause — holds; failed if it is reversed; mixed otherwise).
- *Hypothesis level:* claim 1 (coherence length) **supported** if ≥ 2/3 of eligible periods are supported and median C_B ≤ 0.3; claim 2 (detector) **supported** only if AUC(R1_loc) > AUC(R1_swarm) on room events *and* R1_loc catches a clean room event that R1_swarm misses; claim 3 (leadership) **supported** if |L| is significant in ≥ half the goal changes and the same room leads in ≥ 75% of those. H47 overall = the pattern of the three.
- *Multiplicity:* ~17 units × 2 resolutions × several robustness variants; only the rules above count. Per-unit p-values are descriptive.

### Amendment 1
*2026-10-04 ~06:15 UTC: after the synthetic validation (`analysis/synthetic.py`, below) and the scheme build, before any H47 statistic on real data.* What I had seen: the synthetic numbers and the scheme counts (96,813 statements, 2,757 self-repeats, 117 statements in village-off windows, 29 non-holdout units from #35 on). Predictions and verdict rules are unchanged except as stated.
- **(a) Reading rule for C_B.** C_B is the *global share of a room's collective content fluctuation*. Room coupling amplifies global drives as much as room-level noise, so at equal global drive coupling *raises* C_B (synthetic: room coupling + weak global drive 0.43; the same coupling without a global drive 0.04; a room drive without coupling 0.05). A low C_B therefore says global drives are a small part of what moves a room; it cannot tell coupling from room drives. P1's rule stands as a description of the boundary's sharpness, but a supported P1 is not evidence of coupling. P0(b) is scored as failed in its first part.
- **(b) Detector: primary per-room detector = R1_room** (the per-room R1 the card listed as "R1_naive": each persistent room's balanced-cohort centroid shift, trailing z over that room's own history, max over rooms present that day). Reason: in two-room synthetic worlds R1_room has AUC 0.89 on one-room switches vs R1_swarm 0.80 and R1_loc 0.72, and R1_loc is blind to global switches by design (0.35). R1_loc is kept as the *localization diagnostic* (is a shift specific to a room?) and is the only one that can score a brand-new room (#focus); R1_comb is secondary. Claim 2's rule now reads: AUC(R1_room) > AUC(R1_swarm) on room events, and R1_room *or* R1_loc catches a clean room event that R1_swarm misses.
- **(c) Leadership power.** L keeps its size under asymmetric sampling (false-leader rate 0.02–0.06) but detects a planted 30-min lead in only 13–27% of worlds. A non-significant L per event is weakly informative. Added before real data: a pooled Stouffer test over goal changes of the signed z = L / SD(null L) (sign: #best ahead > 0) for a consistent leader. Claim 3's rule is unchanged. I will also report the real per-statement projection noise next to the synthetic value (0.7).
- **(d) NE42.** Under coupling with a weak global drive, A-phase r_X is 0.39–0.52 rather than ≤ 0.3, so P7a's A-phase threshold is strict; the DiD separates the channel world (0.47) from a team-identity world (−0.06) and is the informative part.

## Results by goal period
w30, pooled over each period's units, L1, self-repeats dropped. C_B = ρ_c/ρ_w; p = room-relabel permutation for Δ_B; G = tier ratio.

| Period | Role | Verdict | Key numbers |
| --- | --- | --- | --- |
| [G35](goalperiod-subhypotheses/G35/README.md) | replication | supported | ρ_w 0.55, ρ_c 0.06, C_B 0.10 (p 0.003); G 1.03 (the only flat room); separate RPG forks |
| [G36](goalperiod-subhypotheses/G36/README.md) | replication | supported | C_B 0.24 (p 0.003); G 0.51; identical kickoffs; #36 lead L 0.23 (p 0.27) |
| [G37](goalperiod-subhypotheses/G37/README.md) | replication | mixed | C_B 0.55 (p 0.08; day 0.97); G 0.16; identical kickoffs, rooms barely separated |
| [G38](goalperiod-subhypotheses/G38/README.md) | native | supported | C_B 0.07 (p 0.003); instruction-direction share −0.02 (difference direction 0.001); #38 L 0.76 (p 0.044: a level offset, not a lead) |
| [G39](goalperiod-subhypotheses/G39/README.md) | replication | mixed | C_B 0.57 (p 0.11); ρ_w 0.08 (weakest rooms); G 0.16 |
| [G41](goalperiod-subhypotheses/G41/README.md) | native | supported | identical instructions, C_B 0.17 (p 0.003); rooms separated from day 0 (F 7.4, z 12.6); G 0.39 |
| [G42](goalperiod-subhypotheses/G42/README.md) | replication | mixed | C_B 0.54 (p 0.02); G 0.48; identical kickoffs |
| [G44](goalperiod-subhypotheses/G44/README.md) | native | supported | C_B −0.04 (p 0.003), sharpest; instruction share −0.01 |
| [G51](goalperiod-subhypotheses/G51/README.md) | native | failed | #focus members already decoupled before #focus (r_F 0.08 → 0.27 → 1.33); single-room G median 0.18; 51g C_B 0.23 (p 0.007, 2 members); no detector fires at #focus |
| [NE42](goalperiod-subhypotheses/NE42/README.md) | native | mixed | r_X 0.57 → 1.37 → 0.17; DiD 1.00 [0.50, 1.34], p 0.001; rule fails only at #39's threshold; detector fires at merge (swarm) and split (swarm, per-room) |

## Results
### Exploratory round 1 (2026-10-04; non-holdout only, asserted in every loader)
**Labeled exploratory.**
- **Scheme:** 96,813 statements (2,757 self-repeats, 117 in village-off windows), 29 non-holdout units from #35 on; 13 MB in `data/processed/H47-room-coherence-length/`.
- **Code:** `scheme/build.py`; `analysis/{h47lib,synthetic,explore,summarize,figures,write_period_folders,write_period_results,posthoc_first_statement,confirm}.py`.
- **Numbers:** `results/{coherence,separation,ne42,g51,detector,leadership,summary,posthoc_first_statement}.json`, `results/detector_days.parquet`, `synthetic/synthetic_summary.json`, `synthetic/lead_calibrated_posthoc.json`, `confirm/confirm_dryrun.json`.
- **Figures:** `figures/coherence_by_period.pdf` (ρ_w/ρ_c, C_B by instruction type, C_B vs separation, G), `figures/summary_obs.pdf`, `figures/summary_obs2.pdf`, `figures/leadership.pdf`, `figures/detector.pdf`, `figures/synthetic_validation.pdf`, per-period `goalperiod-subhypotheses/*/figures/*_h47.pdf`.

**Headline.**
1. **Content coherence stops at the room boundary, most of the time.** Cross-room per-pair content correlation is a small fraction of within-room correlation: C_B ≤ 0.3 with p < 0.05 in 6 of 9 multi-room periods (median 0.23; never failed, 3 mixed). It is robust to the field-removal level, self-repeat dedupe, DQ5 style-residualized vectors and DQ6 assigned instead of actual rooms (|ΔC_B| ≤ 0.13).
2. **The boundary follows the channel.** In NE42's A-B-A, pairs from different #39/#41 rooms correlate at 0.57× and 0.17× the within-room level while apart and at 1.37× while merged in #40 (DiD 1.0 [0.50, 1.34], p 0.001). A persistent team identity would have kept the boundary through the merge (synthetic DiD ≈ 0).
3. **But the room is not a flat block.** Inside rooms, content correlation is concentrated in pairs that address each other (median G 0.40; flat only in G35). In #51's single room of 21–32 agents, G is 0.18: coherence there is shorter than the room.
4. **Post hoc, the boundary is sharp where rooms do different things.** C_B falls with between-room topic separation (Spearman −0.83, permutation p 0.014, 8 periods). The two periods with room-specific kickoffs (#38, #44) have the two sharpest boundaries (mean 0.02 vs median 0.54 in identical-kickoff periods; exact p 0.048, 0.018 counting #35's separate forks). G41 is the exception that matters: identical instructions, yet the rooms split topics on the first day and the boundary is sharp (0.17).
5. **No per-room detector advantage** (claim 2 failed). On room events the swarm R1 has AUC 0.79 and the per-room R1 0.62 (5–6 events, 3 of them goal kickoffs); on the 2 clean events (#focus opens, #focus empties) nothing fires (AUC 0.45–0.64, 11 multi-room placebo days).
6. **No leading room** (claim 3 failed). 1 of 8 goal changes has a significant lead index (#38, p 0.044; about 0.4 expected by chance), the pooled Stouffer test is null (Z 0.88, p 0.38), and #best is ahead in 5/8. The response curves are flat from the first 15-min bin: post hoc, each agent's first post-kickoff statement comes 1–3 min after the kickoff (about 11 min in two rooms) and already carries most of the shift (median y 0.45–1.15). #38's significant L is a level offset: #rest's kickoff-day content stays near its pre-day position, a room-specific instruction arc rather than a lag.

**Synthetic validation (axis F; `figures/synthetic_validation.pdf`; 40 worlds per coherence scenario, N = 15 in 5 + 10, 5 days × 10 windows, Poisson statements; detector: 20 worlds × 80 days; leadership: 100 worlds per arm).**

| Check | Result |
| --- | --- |
| C_B by scenario | none: noisy around 0 (N1 size 0.075); global drive: 0.98 (size 0.025); room coupling + weak global drive: **0.43** (rejects 0.88); room coupling, no global: 0.04 (0.80); room drive only: 0.05 (1.0); pairwise coupling: 0.46 (0.95); mix: 0.45 (1.0) |
| G by scenario | broadcast coupling 0.97–0.98; room drive 1.01; pairwise coupling **0.68** (N2 rejects 0.70); global 1.01 |
| A-B-A (NE42 analogue) | channel worlds r_X 0.39 / 0.99 / 0.52, DiD 0.47 (> 0.4 in 75%); team-identity worlds DiD −0.06 |
| Detector AUC (one-room switch / global switch) | swarm R1 0.80 / 0.99; per-room R1 0.89 / 0.98; R1_loc 0.72 / 0.35. #focus-like (2 of 27 agents): swarm 0.45, per-room 0.61, R1_loc 0.63 |
| Leadership (p < 0.05 rate) | L: null 0.02–0.06 (symmetric, asymmetric, late start); 30-min lead 0.13–0.27 at noise 0.7. dT50: null ≤ 0.02, lead ≤ 0.13. Post hoc at the real noise (0.25): L null 0.02–0.05, 15-min lead 0.10–0.22, 30-min lead 0.53–0.73 |

**Outcome vs prediction**

| | Prediction (locked) | Outcome | Verdict |
| --- | --- | --- | --- |
| P0a | global only: C_B ≥ 0.7, N1 size ≤ 0.1 [0.7] | 0.98; size 0.025 | passed |
| P0b | room coupling and room drive both C_B ≤ 0.3 and indistinguishable [0.7] | coupling with a weak global drive 0.43; without it 0.04 vs room drive 0.05 | **failed in part** (C_B is a global share; Amendment 1a) |
| P0c | pairwise G ≤ 0.6, broadcast ≥ 0.8 [0.55] | 0.68 (N2 rejects 70%); 0.97–0.98 | partial |
| P0d | R1_loc AUC ≥ 0.8 and > swarm on one-room switches; global: swarm ≥ 0.9, R1_loc ≤ 0.65 [0.6] | R1_loc 0.72 < swarm 0.80 (per-room R1 0.89); global 0.99 / 0.35 | **failed** (per-room R1 adopted, Amendment 1b) |
| P0e | L size ≤ 0.10 [0.6]; dT50 false > 0.2 [0.5]; 30-min lead found ≥ 50% [0.5] | 0.02–0.06; ≤ 0.02; 13–27% (53–73% at the real noise, post hoc) | partial |
| P1 | C_B ≤ 0.3, p < 0.05 in ≥ 2/3 of periods; median ≤ 0.25 [0.7] | 6/9 (3 mixed, 0 failed); median 0.23 | **passed** (at the threshold) |
| P2 | median G ≥ 0.6 [0.5]; boundary drop > within-room drop in ≥ 2/3 [0.55] | median G 0.40; 6/9 | half |
| P3 | AUC(per-room) > AUC(swarm) on room events [0.45]; both fire at the NE42 merge and split [0.7]; #focus: swarm < 3 [0.6], R1_loc ≥ 2 [0.35] | 0.62 vs 0.79 (clean: 0.45 vs 0.50); merge: swarm only (per-room undefined), split: both; #focus: swarm −0.97, R1_loc 0.05 | **failed** |
| P4 | |L| n.s. in ≥ 2/3 of goal changes [0.6]; same room ahead in ≤ 5/8 [0.65] | 7/8 n.s.; #best ahead 5/8; Stouffer p 0.38 | passed (HH172's leadership claim fails) |
| P5 (G41) | C_B ≤ 0.3, p < 0.01 [0.7]; as sharp as G38/G44 ± 0.15 [0.55]; separation rises [0.45] | 0.17, p 0.003; off by 0.157; separated from day 0 | primary met; others not |
| P6 (G38, G44) | instruction share ≤ 0.15 [0.6]; day-0 separation > G41's [0.7] | −0.02, −0.01 (difference direction 0.001); G38 yes, G44 no | primary met |
| P7 (NE42) | r_X ≤ 0.3 / ≥ 0.7 / ≤ 0.3 [0.55]; DiD > 0.4, p < 0.05 [0.5]; memory r_X(40) < 0.9 [0.5] | 0.57 / 1.37 / 0.17; DiD 1.00, p 0.001; 1.37 | mixed by rule; **DiD met** |
| P8 (G51) | r_F drop in 51g [0.4]; single-room G ≥ 0.6 [0.45] | 0.08 / 0.27 / 1.33; 0.18 | **failed** |
| Claim 1 | ≥ 2/3 supported and median C_B ≤ 0.3 | 6/9, 0.23 | **supported** (by rule; not a flat block; not evidence of coupling) |
| Claim 2 | per-room AUC > swarm and a clean event caught that swarm misses | neither | **failed** |
| Claim 3 | significant lead in ≥ half, same leader ≥ 75% | 1/8 | **failed** |

**What this means.**
1. **Rooms do bound content coherence, and the bound moves with the channel.** That is the most reliable statement: merge two rooms and their content fluctuations merge within the week; split them and the boundary returns at once (NE42), with identical instructions in the split week (#41).
2. **The bound is set by what the rooms are doing, not by the room as such.** Where both rooms get the same task, about half of each room's content fluctuation is shared with the other room (C_B ≈ 0.55), presumably the common task arc acting as a global drive. Where they work on different things, by instruction (#38, #44) or by their own choice (#41), almost nothing is shared. By Amendment 1(a) this is what C_B measures: the global share of a room's fluctuation. A low C_B cannot tell coupling from room drives.
3. **Inside a room, coherence is conversation-limited.** Pairs that address each other carry most of the within-room correlation, strongly so in the 27-agent #51 room. "Coherence length = room" is too coarse; "coherence length ≤ room, set by who works with whom" fits better. The mention tiers are endogenous (co-workers both talk and share topics), so this is a description, not a mechanism.
4. **Reorganizations are fast and simultaneous.** A goal change moves both rooms within the first few minutes, at each agent's first statement; there is no leader to watch. With the room events available, a per-room topic detector adds nothing to H36's swarm detector.

**Operator-facing conclusion.**
- To keep a group's content independent, put it in its own room *and* give it a different task. Same task in separate rooms shares about half the content fluctuation.
- Merging rooms merges content coherence within days; splitting restores the boundary immediately (NE42).
- In a big room, coherence lives in conversation pairs; per-room monitoring of a 25-agent room averages over sub-groups that don't co-move.
- Don't expect one room to lead a goal change: all rooms switch within minutes. A swarm-level topic-shift alarm (H36 R1) is enough at day resolution.

**Caveats.**
- **Coupling vs room drive is not identified.** C_B is a global share (synthetic); the post hoc topic-separation pattern fits both a task drive and coupling-driven divergence. The mechanism test needs read-out data (round 2).
- **G is endogenous.** Mention tiers co-vary with co-working and shared artifacts.
- **NE42 is goal-confounded** (each phase a new goal; #40's shared objective acts as a global drive), one event, N = 15.
- **Detector power is nil**: 2 clean room events, 11 multi-room placebo days; #focus had 2 core members. The side-room (07-24) held one agent and is not scorable.
- **Leadership resolution:** the quench completes within 1–3 min, below the 15-min bins; L mostly measures level offsets between rooms (room-specific arcs). The agent bootstrap CI for L is anti-conservative relative to the cohort permutation (CIs exclude 0 in 4/8 events while p > 0.05 in 7/8); the permutation is the primary inference.
- **Short units** (1–17 days); per-unit p descriptive; ~9 periods × 2 resolutions × 5 variants, only the card's rules count. P1 passes exactly at its 2/3 threshold.
- **Instrument:** one embedding model (bge-small); DQ5's style-residualized vectors (robust) were still being built by DQ5 and may change; the gte swap is round 2.
- **Post hoc items** (instruction type, separation pattern, first-statement latency, calibrated leadership power) were found after the real-data run and are leads, frozen as C2/C4 in the confirm script.

### Confirmatory design (written 2026-10-04 after exploration; not run)
`analysis/confirm.py`, frozen predictions C1–C5 (in the script header):
- **C1:** C_B ≤ 0.3 with room-relabel p < 0.05 in ≥ 3 of #45, #46, #47, #50 [0.6].
- **C2 (post hoc rule, frozen):** in each target, median between-room separation F ≥ 5 → C_B < 0.3, and F ≤ 3 → C_B > 0.3 [0.5].
- **C3 (NE15 channel cut):** with the #35 partition, r_X(#34d, one room, held out) ≥ 0.7 and DiD = r_X(#35) − r_X(#34d) ≤ −0.4, p < 0.05 [0.55].
- **C4:** no lead at the #46 kickoff (|L| p ≥ 0.05) and both rooms' first post-kickoff statements carry ≥ half the shift [0.55].
- **C5:** at the #showcase-live opening (06-11, inside #46), R1_swarm z < 3 and R1_loc ≥ 2 within ±1 day [0.3].
- **Safeguards:** refuses without `--confirm --i-understand-this-uses-the-locked-holdout`; refuses unless the script, card, `h47lib.py`, `explore.py` and `scheme/build.py` are committed and unmodified. `--dry-run` on non-holdout stand-ins (#41, #42, #44; #40 → #41; #42 kickoff; the 05-11 split) asserts no holdout day is loaded and reproduces the exploratory C_B for #41 and #44 within 0.01 (also r_X, L, and H36's R1 z 9.02 on 05-11): `data/processed/H47-room-coherence-length/confirm/confirm_dryrun.json`.
- **Reuse disclosure (policy in `../holdout.md`):** #45 used by H02 (activity couplings), planned by H23 (content); #46/#47 are H26's unrun primary targets with a closely related statistic (content room excess), so whichever runs second must treat its C1 as non-independent; #34 (C3's pre side) is targeted by the unrun confirm scripts of H01, H05, H07, H12, H19 and H21; NE15 was used by H05's confirmatory run (talk-activity coupling, a different modality). Disclose in this card, the other cards and LOG.md before running.

## Round 2 redirects
**What the direction is really after:** where the boundaries of shared content are in an agent swarm, and whether they are set by the channel (who can read whom), the task, or conversation. Round 1: the channel bounds it (NE42), the task sets how sharp the boundary is, and conversation shapes it inside a room.
- **H47-R1. Read-out-conditioned coupling (the mechanism test).** With DQ1's context ledger (`context_ledger_items`), ask whether an agent's next 30-min content moves toward the room messages it actually *read* more than toward room-mates' messages it did not read (matched age, H29's recency confound). That separates coupling from a room-level task drive, which C_B cannot.
- **H47-R2. Coherence length inside rooms on the reply graph.** Correlation as a function of reply-graph distance (DQ2 `reply_graph`) instead of a median split on mentions: a continuous ξ inside rooms, especially #51's 27-agent room.
- **H47-R3. Confirmatory run** (`confirm.py`: #45–#47, #50, NE15) after the reuse disclosures, and coordination with H26's confirm (shared targets).
- **H47-R4. Instrument:** DQ5's gte embedding swap and the final style-residualized vectors.
- **H47-R5. Drop or redesign leadership.** The quench completes at each agent's first statement; a leadership test would need event-time onsets per agent (latency of the first on-topic statement), and a channel through which one room could lead (shared repos, agents moving rooms). Probably not worth pursuing.
- **H47-R6. Detector:** per-room R1 can only be evaluated on more room events; the onboarding and showcase rooms inside the holdout windows (#46, #50) are the remaining ones.

## Notes
- 2026-10-04 ~05:40 UTC: card, observables, nulls and predictions written (round 1 started by the H47 agent; first session cut by an API limit before any file was written; resumed).
- ~06:00 UTC: synthetic validation run; scheme built. ~06:10 UTC: period and NE folders written with their dated predictions. ~06:15 UTC: Amendment 1. Then the real-data exploration.
- ~06:30 UTC: exploration run. One fix after the first run: a single statement 2 s before a day's window start had a null 30-min window (unit 40); it is clipped to window 0 and NE42 was rerun (r_X unchanged to 3 decimals). Post hoc checks added after seeing results (labelled as such): room kickoff identity vs C_B, separation vs C_B, first-statement latency, leadership power at the real noise level.
- Read-only imports: `hypotheses/H26-content-near-critical/analysis/h26lib.py` (Panel, deviations, contributions, permute_rooms, orthobasis), `hypotheses/H36-reorganization-alarm/analysis/h36lib.py` (trailing_z, auc, auc_ci), and H36's processed `scores.parquet` (R1 z, placebo flags) and `day_stats.parquet`. No shared versions exist; candidates for `infra/shared/`.
- Suggested shared changes (not made; outside edit scope): DEFINITIONS entries for *room contrast C_B*, *conversational tier ratio G*, *room-localized centroid shift R1_loc*, *room lead index L*; a vector-spins pitfall ("C_B / room excess is the global share of a room's fluctuation; coupling amplifies global drives"); a natural-experiments note that #36, #37, #39, #40, #42 had identical room kickoffs (only #38, #44 differ) and that #focus empties by 08-24; a LOG entry.
