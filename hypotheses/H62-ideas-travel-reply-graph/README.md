# H62: Ideas travel the reply graph, not the room

**Status:** exploratory round 1 done (2026-10-04). **A robust reply premium; transmission along reply edges is not separated from a thread field.**
- **Reply premium.** Exposure through a DQ2 reply partner locks adoption more sharply than room-only exposure in 23/26 eligible periods. Pooled Λ = HR_rep / HR_room is 1.92 [1.52, 2.42]. Per-edge transmissibility is 2.70× higher [2.07, 3.51] (CI > 1 in 24/26). The premium survives the tie-only guard (23/26) and is largest in #51 (Λ 9.6 [8.6, 10.9], the native's prediction).
- **But the decisive in-flight test mostly fails.** Inside the reply channel, a read use beats an unread-only use at matched 300 s in only 2/14 powered periods (G38, G51). Pooled C_rep is 1.22 [0.93, 1.60]. On real schedules, a thread field (reply partners co-producing terms without reading each other) gives Λ ≈ 3.2 and T ≈ 3.2. The observed premium is therefore consistent with a field carried by conversation, except in the largest swarm.
- **Room-only exposure still locks** (median HR_room 6.2, regime III 18.5). The room-channel placebo has no synthetic power, so "room is a field" is untested.
- **Verdicts (A2):** 2 supported (G38, G51), 24 mixed, 0 failed, 6 n/a. Natives: G51 supported, NE42 mixed, G12 descriptive.
- Scorecard A1 B1 C1 D1 E1 F2 G1 H1 I0. `analysis/confirm.py` is frozen and dry-run (C1–C4 pass on stand-ins, C5 fails), not run.
**Question (GOALS.md):** Q2 (what is field and what is coupling: is room exposure a shared field and the reply edge the coupling?), with Q1 (what couples agents).
**Fields:** sociophysics, stat mech, info theory
**Literature:** [Kolchinsky & Corominas-Murtra 2020](../../literature/kolchinsky-2020-copying-versus-transformation.md) (copy information relative to an arbitrary prior; the in-flight unread rate is the prior here). Background named, not filed: Hawkes processes with marks and parents (Hawkes 1971†; Zhou, Zha & Song 2013†), epidemic processes on networks (Pastor-Satorras et al., *RMP* 87, 925 (2015)†), complex contagion (Centola & Macy 2007†).
**Definitions used** (`physics-models/DEFINITIONS.md`): Agent; Regime; Population N(t); Interaction (broadcast) and its draft variant (reply), replaced here by the DQ2 named variant below; Contagion / adoption event with **Idea (H34 marker rule)**; **Interaction (ledger-visible exposure)** and **Unread (in-flight) exposure placebo** (RE-D1); H34's **Branching ratio (content)**, **HR₁₀** and **Contagion share**. New named variants, defined under "Operational definitions" and proposed for DEFINITIONS.md (not edited here): **Interaction (reply channel, DQ2)**, **Interaction (room-only)**, **HR_rep / HR_room and the reply premium Λ**, **per-edge transmissibility T_c**, **channel copy excess C_c**.
**From:** HH254 in `hypotheses/hypohypotheses/HYPOHYPOTHESES.md` ("Making the faithful ones better") · **Models:** `physics-models/03-contagion/` (primary: contagion on a temporal network with a field), `physics-models/09-hawkes/` (secondary: marked Hawkes with parents; the shared simulator's parents for calibration)
**Data inputs (shared tables first):** H34 markers (`data/processed/H34-idea-cascades/markers/`, read as data), DQ2 `reply_pairs` (`parent`, `pair_set = cand`), DQ1 context ledger (`call_windows`, `context_ledger_items`), `chat_core`, `calendar`, `roster`, `rooms_timeline`, `period_units`; DQ8 `simulate.py` (Hawkes with parents) for the synthetic check; DQ6 `ground_truth_labels` is not needed. Shared loader: `infra/shared/idea_ledger.py` (new; serves H61 and H62).

## Question
Do idea cascades show a higher branching ratio and sharper exposure locking (HR₁₀) when exposure is defined by DQ2 reply parents rather than room membership, so room exposure is mostly a shared field?

## Design: two layers (Vivian, 2026-10-04)
- **Replication:** the common estimator on every eligible goal period of H34's 32 non-holdout periods. Period README role: `replication`.
- **Period-native tests**, each with its own dated prediction, role `native`:
  - **G51** (21–32 agents, room size ≈ 25, the largest rooms): attention dilution is strongest here (H18, H34: per-pair branching ∝ N^−0.55), so room-only exposure should be weakest relative to reply exposure.
  - **NE42** (#39 → #40 → #41, merge then split at a fixed roster): the merge raises room size (11 → 14 median) without changing who replies to whom much. Room-only per-edge transmissibility should drop in #40 and recover in #41; reply-channel transmissibility should not move. Axis E.
  - **G12** (DQ6 debate teams in one room): a team is a shared stance field. If ideas travel the reply graph, cross-team replies (rebuttals) still carry ideas; if rooms and teams are fields, same-team room-only exposure should carry more.
- **Faithfulness lever (HH254):** H (rival exposure models: room vs reply) and F (calibration on the shared simulator's Hawkes parents). Answered in the scorecard.

## Model
**From:** `physics-models/03-contagion/` and `physics-models/09-hawkes/`. H62 variant: **channel-resolved contagion hazard with a field.**
- Each idea i is a mark. Agent j is at risk from the idea's first use until its own first use. j updates only at its talk calls (read-out gating, H08). At talk call c, j's adoption hazard is
  λ_ij(c) = λ₀_i(c) · exp(β_rep · E^rep_ij(c) + β_room · E^room_ij(c) + β_u,rep · U^rep_ij(c) + β_u,room · U^room_ij(c) + β_h · E^hum_ij(c)),
  where λ₀_i is an idea-specific baseline (it absorbs the idea's fitness and any idea-level field) and the E and U terms are binary exposures defined below.
- **Channels.** A use by agent k is a *reply-channel* exposure for j if, before the use was posted, k and j were joined by a DQ2 reply edge: the use itself replies to a message of j, or k and j exchanged a reply (either direction) in the 2 h before the use. Otherwise it is a *room-only* exposure: j read it only because they share a room.
- **What HH254 predicts.** Coupling runs along reply edges: β_rep > β_room, and room-only exposure is close to a shared field, i.e. a room-only read raises the hazard no more than an in-flight (unread) use at the same lag. On the reply graph the per-edge transmissibility is higher, and branching per exposure edge rises.
- **Identity worth stating.** The adopter-level branching ratio R̂ (H34) counts adopters with any visible parent. Restricting exposure to a subset of edges can only *lower* R̂ (fewer adopters have a qualifying parent). So HH254's "branching ratio rises" is tested in its only non-trivial form: **per-exposure-edge transmissibility** T_c = P(adopt within the next 3 talk calls | first read of a use via channel c), and the branching per edge. R̂ is decomposed into R̂_rep + R̂_room, reported descriptively.
- **Rivals.**
  - (R1) *Room contagion:* any read use transmits equally; β_rep = β_room, T_rep = T_room.
  - (R2) *Thread field (conversation state):* reply partners share a topic, so they co-produce the same terms whether or not they read each other. Then reply-channel unread uses predict adoption as much as read ones (β_u,rep ≈ β_rep at matched lag).
  - (R3) *Pure field:* no read effect in either channel (all β ≈ β_u).

## Operational definitions (written 2026-10-04 19:25 UTC, before any real-data outcome)
- **Ideas, uses, first uses.** H34 round-1b ideas of period g; uses are messages containing the marker. Only agent uses (Claude Code excluded) are transmission sources; uses by humans or the operator form the nuisance indicator E^hum.
- **Visibility.** A use m is *read* by j at talk call c iff m reached one of j's receiving calls with `t_call` ≤ the start of the call that produced c (DQ1 ledger; H34 round-1b rule). It is *unread (in flight)* at c iff it was posted before c, j has not yet read it, and j reads it later (same room).
- **Reply edges.** DQ2 `reply_pairs` with `pair_set == cand` and `parent == True` (one parent per message). An edge (b_msg → a_msg) joins the authors of b and a at the time of b.
- **Interaction (reply channel, DQ2).** For a use m by k and a recipient j: (a) *direct*: m's DQ2 parent is a message by j; or (b) *tie*: a DQ2 parent edge joined k and j (either direction) with the replying message posted in [t_m − 2 h, t_m). No edge that involves j's adopting message or any later message enters (no circularity with the outcome). **Interaction (room-only):** a read agent use that is not a reply-channel use.
- **Tie-only guard (circularity check, P6).** Same as (b) but restricted to edges whose replying message was posted before the idea's first use; direct replies dropped.
- **At-risk talk calls.** For each idea (cap 4,000 ideas per class per period, fixed seed; H34's cap) and each agent j who talks in the period, j's talk calls after the idea's first use up to and including j's first use. Calls with no exposure are kept only within 24 h of the first use; exposed calls are kept for the first 15 calls after first exposure (H34's at-risk rule).
- **Model A (HR₁₀-comparable recency window).** Indicators at call c: RecRep = ≥ 1 reply-channel use read within j's last 3 talk-call windows; RecRoom = recent read agent uses exist but none is reply-channel; RecHum = a human/operator use read in the window. **HR_rep = e^{β_RecRep}, HR_room = e^{β_RecRoom}; reply premium Λ = HR_rep / HR_room.**
- **Model B (matched lag 300 s, in-flight placebo per channel).** Indicators over uses posted in (t_c − 300 s, t_c): SeenRep5, UnrRep5, SeenRoom5, UnrRoom5 (seen = read by the producing call; unread = in flight), plus nuisance OldRead (read uses older than 300 s within the window) and Hum. **Channel copy excess C_rep = e^{β_SeenRep5 − β_UnrRep5}, C_room = e^{β_SeenRoom5 − β_UnrRoom5}.**
- **Estimator.** Conditional (idea-stratified) Poisson likelihood on aggregated cells (idea × indicator pattern: talk calls, adoptions), which equals the fixed-effect Poisson / rare-event conditional logit; weak ridge prior N(0, 3²) on each β so empty cells stay finite; Wald 95% CIs from the Hessian, plus an idea-cluster bootstrap (200 replicates) for Λ and C.
- **Per-edge transmissibility T_c.** For each (idea, j) the first read of an agent use, classified by channel (reply if any use read at that call is reply-channel). Adoption = j's first use within its next 3 talk calls after that read. T_c = adoptions / exposure events; ratio T_rep/T_room with an idea-bootstrap 95% CI.
- **Branching decomposition.** H34's adopter-level parent (latest read use before the producing call) classified by channel: R̂ = R̂_rep + R̂_room + R̂_hum; contagion shares R_c,rep = R̂_rep(1 − 1/HR_rep), R_c,room = R̂_room(1 − 1/HR_room).
- **Eligibility.** ≥ 20 adoptions at RecRep calls and ≥ 20 at RecRoom calls (Model A); Model B terms reported where both cells of a channel have ≥ 10 adoptions.

## Data scheme (`scheme/`)
- **Inputs:** listed above. Held-out days removed with `holdout_mask` and `calendar.holdout` before reading; ledger joins assert no held-out call.
- **Transform:** `scheme/build.py` → per period: (1) aggregated at-risk cells for Models A and B and the tie-only guard; (2) exposure events for T_c; (3) per-adopter parent channel for the R̂ decomposition; (4) per-pair reply-tie counts for the natives (team or room labels joined later). No text; markers are hashes.
- **Output:** `data/processed/H62-ideas-travel-reply-graph/G<NN>/{cells_A,cells_B,cells_T,events,adopters}.parquet`, `results/`, `synthetic/`, `_provenance.json`. Budget ≤ 60 MB.
- **Regimes covered:** I, II, III.

## Observables
- **O1.** HR_rep, HR_room, Λ (Model A) per period, with CIs.
- **O2.** T_rep, T_room and their ratio per period; exposure counts per channel.
- **O3.** C_rep and C_room (Model B); the room-only seen and unread hazard ratios against no recent use.
- **O4.** R̂ decomposition and contagion shares by channel.
- **O5 (unfitted, cross-period).** Spearman ρ of T_room and of T_rep against median room size N_room across periods.
- **O6.** Λ under the tie-only guard.
- **O7.** Pooled random-effects log Λ and log(T_rep/T_room), reported next to the per-period values.

## Null / baseline
- **Room contagion null (R1):** synthetic transmission through any read use at one rate, on the real messages, ledger and DQ2 parents (S1a). Λ and T_rep/T_room must centre on 1; the P1 test must reject in ≤ 10%.
- **Thread-field null (R2):** a synthetic field that raises j's adoption whenever a reply partner posts the idea, read or not (S1c). C_rep must centre on 1.
- **Pure field (R3):** adoptions at a constant per-call rate (S1d). Every read effect ≈ 1.

## Impostors (STANDARDS.md §1)
| Impostor | How it could fake "ideas travel the reply graph" | How H62 removes it, or why it does not apply |
| --- | --- | --- |
| Scheduler field | Reply partners are active at the same time, so their calls coincide with the idea's burst; any channel active in a burst shows locking. | The hazard is per talk call (call clock), stratified by idea; the comparison is between channels within the same idea and the same burst. Model B matches the lag (300 s) so both channels sit in the same scheduler state. |
| Exogenous field (kickoff, goal, operator) | Goal terms are produced by everyone; operator and human uses read by all. | Idea strata absorb idea-level fields (including goal-aligned ideas); human/operator uses enter as a separate nuisance indicator, never as a channel. |
| Shared model priors | Same-family agents reply to each other and coin the same terms. | Partly: idea strata absorb what an idea "is"; same-family co-production at the same moment is caught by the unread terms of Model B. Family is not modelled (stated limit). |
| Contemporaneous convergence | Reply partners answer the same prior turn and reuse the same words without reading each other (H57; ≈ half of H34's HR₁₀; RE-V2: DQ2 parents are partly content-selected). | **In-flight placebo at matched lag per channel (Model B: C_rep, C_room).** Reply channels are defined only from edges posted before the use (no edge involving the adopting message); the tie-only guard (P6) also drops direct replies and post-first-use edges. |

## Faithfulness scorecard
Scored per model, mapping and window; 0 = not done or failed, 1 = partial, 2 = passed. Scheme and promotion thresholds: `writeup/paper.tex`, Sec. "Assessing model faithfulness".
**Rival models:** R1 room contagion, R2 thread field, R3 pure field.
**Locked holdout used for confirmation:** none yet; `analysis/confirm.py` (frozen, dry-run on stand-ins, not run) targets the #51 tail (primary), #15 and #28.

| Axis | Test | Score | Evidence |
| --- | --- | --- | --- |
| A mapping | variables defined from dataset fields; assumptions listed; invariant across families and regimes | 1 | Channels come from the DQ1 ledger and DQ2 parents (edges before the use only); assumptions are listed. DQ2 finds parents for 37–54% of messages (regime-dependent), so the reply channel is under-detected (S2: Λ attenuated ×0.3–0.5). |
| B assumptions | stationarity, Markov order, time-rescaling, update-order audit | 1 | Idea strata absorb idea-level fields; per-talk-call clock. Assumed: a 3-call recency window, a 2-h tie window and a 300-s matched lag. Day-level non-stationarity is not modelled. |
| C adequacy | beats the null hierarchy, day-blocked held-out data | 1 | Λ CI > 1 in 23/26 and T in 24/26 against room contagion (synthetic size 0.06–0.11). No held-out-day design. |
| D unfitted predictions | unfitted statistics and the model's signature | 1 | Two unfitted signatures: the dilution prediction (G51 has the largest premium and the lowest T_room) holds; the cross-period N slope (P5) fails (ρ(T_room, N) −0.15, p 0.47). |
| E interventional | predicts the change across a natural experiment | 1 | NE42: the reply-channel T in the merged week sits within ±30% of the neighbouring weeks, and cross-group pairs transmit 3.7× more via reply ties. The predicted drop of room-only T at the merge did not occur (0.004 → 0.011 → 0.011). |
| F identifiability | synthetic recovery with village sampling; robust to preprocessing | 2 | Four truths on real schedules plus the shared simulator's Hawkes parents. Found and fixed the additive-placebo artifact (A1), showed that the thread field fakes the premium, measured parent-noise attenuation, and documented C_rep's power (0.44). |
| G ground truth | agrees with known structure | 1 | G12 (DQ6 teams): reply exposure crosses team lines (T ratio 3.2 [1.4, 11.9] for cross-team pairs), but the same-team room-only cell has 6 adoptions (descriptive). |
| H comparative | beats the named rivals | 1 | Beats room contagion (R1) and pure field (R3). It does **not** beat the thread field (R2): C_rep is pooled 1.22 [0.93, 1.60], with CI > 1 in 2/14 powered periods. |
| I transfer | holds in other same-mode periods, including the holdout | 0 | The premium transfers across all regimes (I 12/15, II 2/2, III 9/9 with CI > 1). The holdout is not run. |

**Faithfulness lever (HH254: H and F).** F rose to 2 (simulator calibration, two artifacts found). H: the premium beats the room rival, but the thread-field rival stands.

## Prediction
*Written 2026-10-04 19:25 UTC, before any H62 statistic was computed on real data.* Seen beforehand: H34's cards (HR₁₀ 6.4 / 20 / 47 in regimes I / II / III on the ledger; HR_unread5 / HR_seen5 median 0.56), H41 (names gate, numbers co-generated), H29 round 1b (reply network reproducible, parent premium partly built in), H18/H45 (dilution ∝ N^−0.6), DQ2's coverage (parents for 37 / 48 / 54% of agent messages in regimes I / II / III) and the table schemas. No channel-resolved statistic had been computed.

| # | Prediction | Counts against |
| --- | --- | --- |
| P1 | **Sharper locking on the reply graph.** Λ = HR_rep / HR_room > 1 with lower 95% CI > 1 in ≥ 2/3 of eligible periods; pooled log Λ > 0 | Λ CI includes 1 in > 1/2, or pooled Λ ≤ 1 |
| P2 | **Higher per-edge branching.** T_rep / T_room > 1 (CI) in ≥ 2/3 of eligible periods; median ratio ≥ 2 | median ratio < 1.3 |
| P3 | **Room-only exposure is mostly a field.** C_room CI includes 1, or C_room < 1.5, in ≥ 1/2 of periods with Model B power; while C_rep lower CI > 1 in ≥ 1/2 | C_room > 1.5 with CI > 1 in ≥ 2/3: room reads transmit |
| P4 | **Reply edges carry the contagion.** The reply channel's share of the contagion share, R_c,rep / (R_c,rep + R_c,room), exceeds its share of read exposure events by ≥ 2× in ≥ 2/3 of periods | ratio < 1.2 in most periods |
| P5 | **Dilution separates the channels (unfitted).** Across periods, T_room falls with N_room (Spearman ρ < 0, p < 0.05) while T_rep does not (ρ CI includes 0 or ρ_rep > ρ_room) | T_rep falls as steeply as T_room |
| P6 | **Not built in.** Under the tie-only guard, Λ lower CI > 1 in ≥ 1/2 of eligible periods | the premium vanishes when direct replies and post-first-use edges are dropped |

Prior credences (2026-10-04): P1 0.65, P2 0.7, P3 0.3, P4 0.5, P5 0.45, P6 0.5.

**Per-period verdict rule** (written before the run):
- **supported:** Λ lower 95% CI > 1 *and* T_rep / T_room lower 95% CI > 1;
- **failed:** Λ ≤ 1 and T_rep / T_room ≤ 1 (point estimates);
- **mixed:** otherwise;
- **n/a:** not eligible.

**Synthetic validation plan (axis F; before real data).**
- **S1, real skeletons** (G20 regime I, G38 and G41 regime III; real messages, ledger reads and DQ2 parents; 600 synthetic ideas seeded at random agent messages; adoption per talk call). Truths: (a) room contagion q per read use; (b) reply-only contagion q_rep on reply-channel uses; (c) thread field: hazard raised when a reply partner posts the idea in the last 300 s, read or not; (d) pure field ε. The pipeline must give Λ ≈ 1 and size ≤ 0.10 under (a), Λ > 1 with power ≥ 0.8 under (b), C_rep ≈ 1 under (c), and all ratios ≈ 1 under (d).
- **S2, shared simulator** (`simulate.py`, Hawkes with parents, n_x 0.3, n_s 0.2, on G38's skeleton): true parents known; observed parents keep the true one with probability 0.5 (DQ2 recall) and draw a wrong recent candidate with probability 0.07. Reply-only transmission is planted on true parents. Measures the attenuation of Λ by parent-label noise.

## Synthetic validation (axis F; first run 2026-10-04 19:23–19:35 UTC, before any real-data channel statistic)
Code: `analysis/synthetic.py`; outputs `data/processed/H62-ideas-travel-reply-graph/synthetic/`. S1 on G20, G38 and G41 (real messages, ledger reads and DQ2 parents; 1,000 synthetic ideas per run; 6 runs per period and truth). Medians over 18 runs, with the share of runs whose 95% CI excludes 1:

| Truth | Λ | Λ CI > 1 | T_rep/T_room | T CI > 1 | C_rep (additive coding) | C_rep CI > 1 |
| --- | --- | --- | --- | --- | --- | --- |
| pure field | 0.90 | 0.06 | 0.98 | 0.11 | 1.46 | 0.00 |
| room contagion | 0.93 | 0.11 | 0.97 | 0.11 | 1.36 | 0.11 |
| thread field (reply partner posts the idea; read or not) | **3.24** | **0.94** | **3.21** | **1.00** | **2.57** | **0.67** |
| reply contagion | 10.5 | 1.00 | 7.4 | 1.00 | 2.43 | 0.78 |

Findings:
- Λ and T reject the room and field truths at about the nominal rate (0.06–0.11) and detect reply contagion in 100% of runs.
- **A thread field fakes the reply premium.** Λ ≈ 3.2 and T ≈ 3.2 arise when reply partners co-produce a term without reading each other. So Λ and T measure a *reply premium*, not transmission along reply edges.
- **The pre-registered in-flight placebo was mis-coded.** With additive seen and unread indicators, C_rep = 2.6 under the thread field (67% false positives). Calls with an unread reply-partner use usually also have a seen one, so the unread coefficient is identified only from the overlap.

## Amendments (pre-real; written 2026-10-04 19:44 UTC, after the first synthetic run, before any real-data channel statistic)
- **A1 (estimator).** Model B's unread indicators become exclusive: *unread-only* = an unread use of that channel posted in the 300-s window and no seen use of that channel in the window (`u_rep5x`, `u_room5x`, derived from the stored cells). C_rep = HR(seen, reply) / HR(unread-only, reply); C_room likewise. The additive coding is kept as `MODEL_B_ADDITIVE` for the record. S1 is re-run with A1, and S2 (shared-simulator Hawkes parents) is run for the first time; their numbers are added below before the real-data run.
- **A2 (verdict: the C_rep clause).** Because a thread field produces Λ and T > 1 without reading, the per-period verdict changes:
  - **supported:** Λ lower CI > 1, T_rep/T_room lower CI > 1, *and* C_rep lower 95% CI > 1 (reading matters inside the reply channel at a matched 300-s lag);
  - **mixed:** a reply premium (Λ or T lower CI > 1) without C_rep lower CI > 1, or C_rep underpowered (< 10 adoptions in either cell). The premium is then consistent with a thread field;
  - **failed:** Λ ≤ 1 and T ≤ 1 (point estimates);
  - **n/a:** as before.

  P1 and P2 are reported as written and read as "reply premium". **P3's C_rep part is the decisive test of HH254's transmission claim.**

**Re-run with A1 (finished 2026-10-04 ≈19:44 UTC, before the real-data run).** S1 again, now with exclusive unread coding:

| Truth | Λ (CI > 1) | T ratio (CI > 1) | C_rep (CI > 1) | C_room (CI > 1) |
| --- | --- | --- | --- | --- |
| pure field | 0.90 (0.06) | 0.98 (0.11) | 1.71 (0.00) | 2.12 (0.00) |
| room contagion | 0.93 (0.11) | 0.97 (0.11) | 1.45 (0.06) | 1.16 (0.00) |
| thread field | 3.24 (0.94) | 3.21 (1.00) | **0.98 (0.00)** | 0.73 (0.00) |
| reply contagion | 10.5 (1.00) | 7.4 (1.00) | 2.25 (**0.44**) | 1.25 (0.00) |

- A1 fixes the placebo: the thread field no longer fakes copying (C_rep 0.98, no false positives).
- **C_rep has low power.** It detects reply contagion in only 44% of runs at ≈ 900 adoptions, because unread-only reply exposures are rare. Under A2, a "mixed" period may therefore be an underpowered transmission period. The pooled log C_rep (random effects across periods) is the better test.
- C_room has no power in any truth (0/72 rejections), so **P3's room-only part is not testable.** It is reported as descriptive.
- **S2, shared simulator** (`simulate.py` Hawkes with parents on G38a's skeleton; 4 seeds per truth): with true parents, reply contagion gives Λ 15.6 and T 9.4; room contagion gives Λ 1.00 and T 0.81. With DQ2-like noisy parents (true parent kept with probability 0.5, a wrong recent candidate with probability 0.07), reply contagion gives Λ 4.9 and T 4.6, attenuated ×0.3–0.5; room contagion gives Λ 1.04, with CI > 1 in 1/4 runs. **Parent-label noise shrinks the premium but does not create one.**

## Disclosure (2026-10-04)
- **One outcome count was seen before the synthetic run.** While checking the builder on G20 at about 19:28 UTC, I printed the parent-channel counts of exposed adopters: 740 reply-channel vs 533 room-only (and 8 human). Together with the exposure-event counts printed in the same check (11,205 reply vs 15,854 room-only first exposures), this reveals a crude reply-vs-room adoption contrast for G20. The check came after the card's predictions (19:25 UTC) and before the synthetic validation and amendments. No hazard ratio, transmissibility or placebo was computed. G20 is one of 32 replication periods and is not a native.
- **Timestamps.** Some stamps in my working files were first written ahead of the real clock and were corrected to file modification times on 2026-10-04 19:42 UTC. Every prediction here still predates the corresponding real-data run.

## Results by goal period
Verdict rule with amendment A2 (written in every G card before its run).

| Period | Role | Verdict | Key numbers |
| --- | --- | --- | --- |
| [G05](goalperiod-subhypotheses/G05/README.md) | replication | mixed | regime I, N_room 4.0; Λ 1.88 [1.06, 3.87]; T ratio 1.41 [0.84, 3.21]; C_rep 0.29 [0.12, 0.72] (underpowered); guard Λ 1.62 |
| [G06](goalperiod-subhypotheses/G06/README.md) | replication | n/a | regime I; 52 reply / 10 room-only adoptions (< 20) |
| [G07](goalperiod-subhypotheses/G07/README.md) | replication | n/a | regime I; 15 reply / 5 room-only adoptions (< 20) |
| [G08](goalperiod-subhypotheses/G08/README.md) | replication | n/a | regime I; 44 reply / 10 room-only adoptions (< 20) |
| [G10](goalperiod-subhypotheses/G10/README.md) | replication | n/a | regime I; 17 reply / 15 room-only adoptions (< 20) |
| [G11](goalperiod-subhypotheses/G11/README.md) | replication | n/a | regime I; 88 reply / 18 room-only adoptions (< 20) |
| [G12](goalperiod-subhypotheses/G12/README.md) | native + replication | descriptive (native); mixed (replication) | regime I, N_room 7.0; Λ 2.40 [1.60, 3.92]; T ratio 4.06 [2.62, 7.02]; C_rep 0.76 [0.45, 1.28]; guard Λ 2.75 |
| [G13](goalperiod-subhypotheses/G13/README.md) | replication | mixed | regime I, N_room 6.0; Λ 2.55 [1.62, 4.42]; T ratio 3.08 [1.78, 6.80]; C_rep 0.83 [0.32, 2.14] (underpowered); guard Λ 1.82 |
| [G16](goalperiod-subhypotheses/G16/README.md) | replication | mixed | regime I, N_room 7.0; Λ 1.37 [0.71, 2.63]; T ratio 5.34 [2.72, 11.27]; C_rep 1.72 [0.24, 12.62] (underpowered); guard Λ 1.91 |
| [G17](goalperiod-subhypotheses/G17/README.md) | replication | n/a | regime I; 46 reply / 17 room-only adoptions (< 20) |
| [G18](goalperiod-subhypotheses/G18/README.md) | replication | mixed | regime I, N_room 7.5; Λ 1.27 [1.05, 1.56]; T ratio 1.74 [1.43, 2.13]; C_rep 1.29 [0.76, 2.19]; guard Λ 1.40 |
| [G19](goalperiod-subhypotheses/G19/README.md) | replication | mixed | regime I, N_room 7.0; Λ 1.75 [1.37, 2.31]; T ratio 3.58 [2.56, 5.07]; C_rep 1.93 [0.86, 4.36] (underpowered); guard Λ 1.77 |
| [G20](goalperiod-subhypotheses/G20/README.md) | replication | mixed | regime I, N_room 9.0; Λ 2.21 [1.83, 2.66]; T ratio 3.53 [2.86, 4.31]; C_rep 1.29 [0.72, 2.32]; guard Λ 2.22 |
| [G21](goalperiod-subhypotheses/G21/README.md) | replication | mixed | regime I, N_room 8.0; Λ 2.05 [1.61, 2.67]; T ratio 2.56 [1.93, 3.47]; C_rep 3.48 [0.87, 13.88] (underpowered); guard Λ 2.18 |
| [G23](goalperiod-subhypotheses/G23/README.md) | replication | mixed | regime I, N_room 10.0; Λ 0.89 [0.65, 1.23]; T ratio 1.69 [0.98, 2.87]; C_rep 5.71 [0.11, 294.53] (underpowered); guard Λ 0.98 |
| [G24](goalperiod-subhypotheses/G24/README.md) | replication | mixed | regime I, N_room 10.0; Λ 1.93 [1.39, 2.59]; T ratio 4.68 [3.54, 6.35]; C_rep 1.25 [0.57, 2.73] (underpowered); guard Λ 1.91 |
| [G25](goalperiod-subhypotheses/G25/README.md) | replication | mixed | regime I, N_room 10.0; Λ 1.70 [1.37, 2.13]; T ratio 1.39 [1.10, 1.81]; C_rep 2.32 [0.86, 6.24] (underpowered); guard Λ 1.64 |
| [G26](goalperiod-subhypotheses/G26/README.md) | replication | mixed | regime I, N_room 10.0; Λ 1.79 [1.43, 2.28]; T ratio 1.80 [1.36, 2.46]; C_rep 0.89 [0.54, 1.44]; guard Λ 1.72 |
| [G27](goalperiod-subhypotheses/G27/README.md) | replication | mixed | regime I, N_room 10.0; Λ 1.48 [1.29, 1.69]; T ratio 1.38 [1.18, 1.64]; C_rep 1.34 [0.73, 2.46]; guard Λ 1.44 |
| [G30](goalperiod-subhypotheses/G30/README.md) | replication | mixed | regime I, N_room 12.0; Λ 1.16 [0.98, 1.39]; T ratio 1.62 [1.34, 1.98]; C_rep 0.68 [0.40, 1.18]; guard Λ 1.24 |
| [G31](goalperiod-subhypotheses/G31/README.md) | replication | mixed | regime I, N_room 12.0; Λ 1.90 [1.65, 2.20]; T ratio 2.35 [1.97, 2.85]; C_rep 1.53 [0.83, 2.82]; guard Λ 1.86 |
| [G33](goalperiod-subhypotheses/G33/README.md) | replication | mixed | regime II, N_room 12.0; Λ 1.29 [1.11, 1.47]; T ratio 1.94 [1.65, 2.28]; C_rep 1.04 [0.71, 1.53]; guard Λ 1.45 |
| [G35](goalperiod-subhypotheses/G35/README.md) | replication | mixed | regime II, N_room 8.0; Λ 1.21 [1.03, 1.40]; T ratio 1.46 [1.26, 1.69]; C_rep 0.59 [0.40, 0.88]; guard Λ 1.36 |
| [G36](goalperiod-subhypotheses/G36/README.md) | replication | mixed | regime III, N_room 7.0; Λ 1.42 [1.20, 1.71]; T ratio 1.96 [1.65, 2.31]; C_rep 9.46 [1.46, 61.36] (underpowered); guard Λ 1.65 |
| [G37](goalperiod-subhypotheses/G37/README.md) | replication | mixed | regime III, N_room 5.0; Λ 1.46 [1.04, 2.17]; T ratio 1.90 [1.33, 2.71]; C_rep 2.07 [0.68, 6.37] (underpowered); guard Λ 1.62 |
| [G38](goalperiod-subhypotheses/G38/README.md) | replication | supported | regime III, N_room 6.0; Λ 2.13 [1.88, 2.38]; T ratio 2.55 [2.28, 2.86]; C_rep 1.58 [1.02, 2.45]; guard Λ 2.32 |
| [G39](goalperiod-subhypotheses/G39/README.md) | replication | mixed | regime III, N_room 7.0; Λ 1.66 [1.13, 2.47]; T ratio 4.08 [2.87, 5.98]; C_rep 1.07 [0.11, 10.75] (underpowered); guard Λ 1.77 |
| [G40](goalperiod-subhypotheses/G40/README.md) | replication | mixed | regime III, N_room 14.0; Λ 2.21 [1.98, 2.52]; T ratio 3.49 [3.08, 3.93]; C_rep 0.51 [0.36, 0.72]; guard Λ 2.28 |
| [G41](goalperiod-subhypotheses/G41/README.md) | replication | mixed | regime III, N_room 7.0; Λ 2.38 [2.04, 2.85]; T ratio 3.90 [3.27, 4.66]; C_rep 1.02 [0.73, 1.43]; guard Λ 2.49 |
| [G42](goalperiod-subhypotheses/G42/README.md) | replication | mixed | regime III, N_room 6.5; Λ 3.92 [2.97, 5.05]; T ratio 4.89 [3.94, 6.22]; C_rep 1.45 [0.68, 3.10] (underpowered); guard Λ 2.26 |
| [G44](goalperiod-subhypotheses/G44/README.md) | replication | mixed | regime III, N_room 7.5; Λ 3.50 [2.80, 4.78]; T ratio 4.15 [3.13, 5.50]; C_rep 1.03 [0.63, 1.70]; guard Λ 2.86 |
| [G51](goalperiod-subhypotheses/G51/README.md) | native + replication | supported (native); supported (replication) | regime III, N_room 23.0; Λ 9.62 [8.57, 10.91]; T ratio 9.96 [9.10, 11.02]; C_rep 1.70 [1.15, 2.53]; guard Λ 9.79 |
| [NE42](goalperiod-subhypotheses/NE42/README.md) | native | mixed | T_room #39/#40/#41 0.004 / 0.011 / 0.011 (rises, not falls); T_rep 0.016 / 0.037 / 0.045; merged-week cross-group T ratio 3.69 [3.11, 4.43] |

## Outcome vs prediction
| # | Prediction (19:25 UTC; A1–A2 19:44 UTC) | Outcome | Verdict |
| --- | --- | --- | --- |
| P1 | Λ CI > 1 in ≥ 2/3; pooled log Λ > 0 | 23/26; pooled Λ 1.92 [1.52, 2.42]; median 1.83 (regime I 1.79, II 1.25, III 2.21) | **pass** (premium) |
| P2 | T_rep/T_room CI > 1 in ≥ 2/3; median ≥ 2 | 24/26; median 2.56; pooled 2.70 [2.07, 3.51] | **pass** |
| P3 | C_room ≈ 1 in ≥ 1/2; C_rep CI > 1 in ≥ 1/2 | C_room CI ∋ 1 in 12/12 (no synthetic power: untestable); C_rep CI > 1 in 2/14 (Wald); pooled C_rep 1.22 [0.93, 1.60]; C_room 0.84 [0.63, 1.12] | **fail** (C_rep), C_room untestable |
| P4 | reply share of R_c ≥ 2× its exposure share in ≥ 2/3 | 5/26; median ratio 1.27 (exposure share 0.55, R_c share 0.66) | **fail** |
| P5 | T_room falls with N (ρ < 0, p < 0.05); T_rep does not | ρ(T_room, N) −0.15 (p 0.47); ρ(T_rep, N) −0.29 (p 0.16) | **fail** |
| P6 | guard Λ CI > 1 in ≥ 1/2 | 23/26; median 1.80 | **pass** |

Prior credences: P1 0.65, P2 0.7, P3 0.3, P4 0.5, P5 0.45, P6 0.5.

## Results
`analysis/explore.py` writes `data/processed/H62-ideas-travel-reply-graph/results/{periods.json, period_table.parquet, summary.json}`; `analysis/natives.py` writes `results/natives.json`. Figures are in `figures/summary_obs.pdf` and `figures/summary_obs2.pdf`.

**1. Ideas adopted through a reply partner lock sharper and spread more per edge.**
- **Scale:** 26 eligible periods; idea-stratified conditional Poisson on aggregated at-risk talk calls.
- **Hazard ratios** against calls with no recent read (median): 10.6 for a recent read use from a reply partner (direct reply or a DQ2 tie within 2 h before the use), 6.2 for room-only uses.
- **Premium:** pooled Λ = 1.92 [1.52, 2.42].
- **Per edge:** the first read of a reply-partner use is followed by adoption within 3 talk calls 2.70× [2.07, 3.51] as often as a room-only read (median T_rep 0.032 vs T_room 0.011).
- **Not built in by DQ2:** the guard keeps the premium (23/26, median 1.80). It uses ties formed before the idea existed and drops direct replies.
- **By regime:** the premium grows in regime III (HR_rep 73 vs HR_room 19). It is largest in #51, with 23 agents per room-day: Λ 9.6, T ratio 10.0.
- **Branching decomposition:** 64% of exposed adopters' latest read use came through a reply partner (median), while 55% of first exposures did. The reply channel's share of the contagion share R_c is 0.66, not ≥ 2× its exposure share (P4 fails).

**2. The premium is not yet transmission.** On real schedules, a thread field gives the same premium (Λ ≈ 3.2, T ≈ 3.2): reply partners produce a term at the same moment because they answer the same turn, whether or not they read each other. Only the matched-lag placebo inside the reply channel can tell the two apart (C_rep, seen vs unread-only at 300 s).
- **On real data:** C_rep > 1 with CI > 1 in 2/14 powered periods (G38 1.58 [1.02, 2.45], G51 1.70 [1.15, 2.53]). It is below 1 in G35 and G40. Pooled 1.22 [0.93, 1.60].
- **Power:** synthetic power at the observed counts is ≈ 0.44, so a single period's null is weak evidence. The pooled estimate excludes a large copying excess.
- **Reading:** in most periods the reply premium is consistent with conversation-carried co-production. In the largest swarm, reading inside threads adds ≈ 1.7×.

**3. Room-only exposure is not shown to be a field.** HR_room is well above 1 (6.2; 18.5 in regime III). The room-only placebo (C_room, pooled 0.84 [0.63, 1.12]) has no synthetic power (0/72 rejections, even under room contagion). So HH254's "room exposure is mostly a shared field" is neither shown nor refuted. Two observations are consistent with a field share: C_room < 1, and the premium.

**4. Dilution:**
- **G51** has the lowest room-only transmissibility (0.004) and a mid-range T_rep (0.038), as predicted.
- **Across periods**, T_room does not fall significantly with room size (ρ −0.15). P5 fails: room size alone does not set room-only transmissibility.

**5. Natives.**
- **G51 (supported):** Λ 9.6 [8.6, 10.9], against a regime-III median of 2.2. T_room is the regime-III minimum; T_rep lies within the range.
- **NE42 (mixed):** T_rep in the merged week is 0.037, within ±30% of #39/#41 (0.030). Cross-group pairs in #40 transmit 3.7× [3.1, 4.4] more through reply ties than through room-only reads. But room-only T rose rather than fell (0.004 → 0.011 → 0.011), so the merge did not dilute room exposure. The goal change confounds this.
- **G12 (descriptive):** reply exposure across debate teams transmits 3.2× [1.4, 11.9] more per edge than room-only exposure across teams. The hazard comparison against same-team room-only exposure rests on 6 adoptions.

**Model- and style-dependence.** No embeddings enter H62, so nothing depends on bge vs gte or on style. The results depend on DQ2's parent labels (recall ≈ 0.5; S2 shows attenuation, not inflation) and on the 2-h tie window.

**Operator reading.** To spread an item, put it into an active reply thread rather than broadcasting it: per first read, a reply partner's use is adopted ≈ 2.7× as often (10× in a 25-agent room). Do not read this as proof that agents copy each other. Outside the largest swarm, the same premium appears when thread partners co-produce the term unread.

## Caveats
- The decisive copying test (C_rep) is underpowered per period, because unread-only reply exposures are rare. Pool it, or lengthen the window, before concluding.
- DQ2 keeps one parent per message and finds parents for 37–54% of messages. Ties are therefore under-detected, which biases Λ toward 1 (S2).
- Ideas are hashed H34 markers, which count co-generated names and numbers as adoptions.
- The Newton fitter diverged on the first real run. It was replaced by a damped, overflow-safe version before any result was used. The synthetic runs used the earlier fitter; they converged there and give the same MLE.
- A2 changed the verdict rule after the first synthetic run and before the real run. G20 adopter channel counts were seen early (Disclosure).
- The 26 replication folders are one estimator, not 26 tests.

## Confirmatory predictions (frozen 2026-10-04 after round 1, before any holdout use; `analysis/confirm.py`, not run)
- **Targets:** T1 = #51 tail (primary), T2 = #15, T3 = #28.
- **C1:** T1 Λ ≥ 3, CI > 1.
- **C2:** T1 T ratio ≥ 3, CI > 1.
- **C3:** T1 guard Λ CI > 1.
- **C4:** Λ CI > 1 in #15 or #28.
- **C5:** T1 C_rep Wald CI > 1, with ≥ 10 adoptions per cell.
- **Verdict:** the reply premium is confirmed if C1–C3 pass; transmission is confirmed only if C5 also passes.
- **Dry run** (`results/confirm_dryrun.json`, non-holdout stand-ins): T1 (#51 08-24 → 09-04) gives Λ 4.9 [4.4, 5.4], T 7.6 (lower CI 6.8), guard 4.6, C_rep 1.32 [0.82, 2.11]. C1–C4 pass and C5 fails.
- **Reuse:** the same targets are planned by H34 and H61 (different statistics). The script calls `holdout_ledger.check()` and refuses without both flags.

## Round 2 redirects (2026-10-04)
*Proposed by the round-1 agent; the coordinator may revise.*
- **H62-R1.** A powered copying test: pool C_rep hierarchically across periods. Alternatively, use the blind window (post → first read) of each reply-partner use as a within-pair placebo.
- **H62-R2.** A multi-parent reply graph (a DQ2 multi-label sample) to remove the one-parent budget and the attenuation.
- **H62-R3.** Separate the thread field directly: compare reply partners who are in the same thread at the moment of use with partners from an older thread.
- **H62-R4.** Room-only exposure: build a powered placebo (a longer matched lag, or cross-room unread uses) before claiming "room is a field".

## Notes
- 2026-10-04 19:25 UTC: round-1 agent wrote definitions, observables, nulls, impostor table and predictions before any real-data outcome.
- 19:28: builder test on G20 (disclosed above). 19:23–19:35: first synthetic run. 19:44: amendments A1–A2 and the A1 re-run of S1 + S2; period predictions written 19:45 (natives' predictions present in `analysis/write_period_cards.py` from 19:33). Real-data run from 19:45; re-run with the damped fitter after the first run's numerical divergence.
- New shared code used: `infra/shared/idea_ledger.py`, `infra/shared/idea_markers.py` (written for H61/H62; verified against H34).
- Proposed for DEFINITIONS.md: *Interaction (reply channel, DQ2)*, *Interaction (room-only)*, *reply premium Λ*, *per-edge transmissibility T_c*, *channel copy excess C_c (unread-only coding)*.
