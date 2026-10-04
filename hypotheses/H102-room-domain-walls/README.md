# H102: Domain walls between rooms, set by bridging agents

**Status:** exploratory round 1 done (2026-10-04, non-holdout only): **failed by HH332's kill rule** (hoppers are not intermediate), with the domain half supported. Where rooms do different things the content splits into two domains (D 5.3–6.1 in #38, #41, #44; 5.5 in #51g; relabel p ≤ 0.006). The wall is sharp and empty of hoppers. The one frequent #focus hopper (Claude Fable 5, 7 hop-days) sits at s 0.06, inside the #general stayers' range (95th percentile 0.21). No hopper carries #focus content into #general. Hoppers' statements made *inside* #focus sit at s 0.15–0.51, so an agent's content follows the room it is speaking in. Hopping read-outs have no dose effect: κ_R −0.014 [−0.042, 0.024] per e-fold, where synthetic power is ≥ 0.93 at κ 0.1. The domain axis is not the room-kickoff direction (#38 |cos| 0.02, #44 0.27, both within the null). `analysis/confirm.py` written and dry-run, not run. Card and predictions written 2026-10-04 ~20:27 UTC, before any H102 statistic on real data. Approved by Vivian 2026-10-04 from HH332.
**Question (GOALS.md):** **Q1** (what couples agents: do cross-room read-outs pull a hopper's content toward the other room) and **Q3** (collective order: are room contents two domains with a wall).
**Fields:** stat mech (domain walls in a two-domain spin system; wall profile and width), sociophysics (bridging agents between groups), dynamics (read-out-driven relaxation)
**Literature:** `physics-models/11-vector-spins/README.md` (soft-spin O(n), kinetic linear form); `physics-models/01-inverse-ising/README.md` (the axis projection is a scalar Ising-like order parameter). Project cards: H47 (rooms bound coherence where they do different things; the #focus members were already decoupled), H41 round 1b (#51 hoppers bridge only about half the time: 51% of 839 cross-room adoptions inside the logged cone), H05 (rooms couple through reads), H48 (pull per read α ~ 1/250), H07 (#35 RPG forks diverge by copying), H13/H73 (style is an agent constant), H98 (#51 random field: private goals).
**Definitions used** (`physics-models/DEFINITIONS.md`): Agent; Regime; Driving / external field (room kickoffs; #51 private agent goals); Interaction (broadcast: co-located = same current room); **Exposure (turn read-out)** (H08, through the DQ1 context ledger); Agent state, *vector (for model 11)* in the DQ5 variant **statement and agent-day means of 32-d regime-whitened, style-residualized statement vectors** (`statements_style_resid32_<model>.npy`, both models). New named variants proposed (defined under Observables; DEFINITIONS.md not edited): **domain axis u**, **wall coordinate s**, **bimodality D**, **interior occupancy I**, **hopping read-outs R**, **posted-unread volume U**.
**From:** HH332 in `hypotheses/hypohypotheses/HYPOHYPOTHESES.md` · **Models:** `physics-models/11-vector-spins/` (primary), `physics-models/01-inverse-ising/` (secondary: the scalar wall coordinate)
**Data inputs (shared tables first):** `embeddings/statements.parquet` + `statements_style_resid32_{bge_small,gte_modernbert}.npy` (primary) and `statements_white32_*` (variant); `statement_flags` (`self_repeat_both`, dedupe variant); `rooms_timeline` (null `t_end` → +inf before filtering); `chat_core` (message room); DQ1 `context_ledger_items` + `context_ledger_turns` (read-outs by receiving call); `embeddings/goals.parquet` + `goal_vectors*` (room kickoffs; #51 `agent_goal`); `period_units`; `holdout.json` via `holdout_mask`. No text is read.

## Source HH (verbatim from the HH list, including refinements)
Domain walls between rooms: width set by the bridging agents. In weeks where rooms get different instructions (#38, #44) or work on different things, content forms two domains with a wall at the room boundary. Agents who hop rooms sit inside the wall.
  - *Prediction:* agent positions along the inter-domain axis are bimodal by room. Hoppers sit at intermediate positions. Wall width (the spread of the hoppers' positions) grows with the number of hopping read-outs. Note: H41 round 1b corrected #51: hoppers leak about half the time, not 97% in cone.
  - *Check:* projection onto the axis between room centroids (DQ5, both models, style-residualized), with hoppers identified from the ledger; compare with a shuffled room assignment.
  - *Kill:* hoppers are not intermediate, or the positions are not bimodal.
  - *Models:* 11, 01 · *Builds on:* H05, H41, H47, HH183

## Question
Where two rooms do different things, do agents' content positions along the axis between the room centroids split into two groups by room, and do agents who read across the boundary sit between the groups, by an amount that grows with how much they read from the other room?

## Design: two layers (STANDARDS §4)
- **Who hops.** In #35–#44 the rooms are fixed for whole goal periods; the only within-period hopper is DeepSeek-V3.2 (#rest → #best 03-26 19:48 → 03-30 17:43 UTC, across #36c and the first day of #37; a 0.3-h visit by the Claude Code agent is excluded). The operator moves at goal starts (04-02, 04-27, 05-25) are H100's movers, not hoppers. The hoppers are in **#51g** (#general ↔ #focus, 08-05 → 08-21): two agents (Gemini 2.5 Pro, Claude Opus 4.8) live mostly in #focus, two (Claude Fable 5: 16 visits, 19 h; DeepSeek-V4-Pro: 17 visits, 1.8 h) hop repeatedly, and four more visit briefly. So the hopper tests rest on #51g and on one #36 hopper; the wall-without-hoppers tests use #35–#44.
- **Replication** (role `replication`): bimodality D, interior occupancy I and the cross-room read share on every non-holdout two-room period with fixed rooms: G35, G37, G39, G41, G42.
- **Natives** (role `native`), each with its own dated prediction:
  - **G38** and **G44** (room-specific kickoffs): two domains set by an operator field; is the domain axis the kickoff direction, and is the wall empty (no hoppers, few cross reads)?
  - **G51** (unit 51g; #focus): hoppers' wall coordinate, the carry-over test on their #general statements, and the dose–response on hopping read-outs with a posted-unread placebo.
  - **G36** (DeepSeek-V3.2's #best stint): one hopper's wall coordinate before, during and after the stint.

## Model
**From:** `physics-models/11-vector-spins/` (kinetic soft-spin, linear), read along one axis (`physics-models/01-inverse-ising/`).

Each agent i has a content state x_i ∈ ℝ³² (style-residualized, whitened). Two domains A and B (rooms with different work). Kinetic rule per read-out call:

  x_i ← (1 − λ) x_i + λ [ w Σ_j π_ij x_j + (1 − w)(h_{D(i)} + a_i) ] + η

π_ij is the share of i's read items that come from j (DQ1 ledger), h_D the domain field (room kickoff, room work), a_i the agent constant, w the read-out coupling weight. Project on the domain axis u = (c_B − c_A)/|c_B − c_A| (c = centroid of the domain's core stayers) and rescale to the **wall coordinate** s_i = (x_i − c_home)·u / ((c_other − c_home)·u) (0 = home domain, 1 = other domain). At stationarity, to first order,

  s_i ≈ κ p_i + s_i^field,   κ ≈ w (1 − s̄),   p_i = R_i / (R_i + N_i^home)

with p_i the share of i's read items that come from the other domain. **The wall** is the set of agents with 0 < s < 1. A stayer (p = 0) sits at its domain (s ≈ 0); a hopper sits at s ≈ κ p. The wall width W (spread of s over the hoppers, and the interior occupancy I) grows with the hoppers' read-out share. With w = 0 (no coupling), s does not depend on p: hoppers sit where their own field puts them.

**Rivals.**
- **R-mixture:** a hopper's day vector is intermediate only because it mixes statements made in two rooms (each statement belongs to one domain). Predicts s ≈ 0 for its home-room statements.
- **R-field:** positions follow each agent's own field (its project; #51 private goals). Hoppers sit between the domains because their work spans both. Predicts s explained by the agent-goal projection, and no within-agent dose–response.
- **R-selection:** agents hop and read the other room on the days they already work on its topic. Predicts reads do not lead s (no lagged effect) and that posted-but-unread other-room volume predicts s as well as reads do.
- **R-global:** no domains (unimodal positions).

## Data scheme (`scheme/`)
`scheme/build.py` → `data/processed/H102-room-domain-walls/` (≤ 30 MB, `_provenance.json`). Non-holdout rows only (`holdout_mask`).
- **Statements** (`statements.parquet` + `x_<variant>_<model>.npy`, float16): agent chat and intentions of #35–#44 and #51 (non-holdout), Claude Code agent excluded, with the **room at the statement** (chat: message room; intentions: as-of `rooms_timeline`, null `t_end` → +inf), the period unit, the PT day, and `self_repeat_both`.
- **Agent-day-room means** (`agent_day_room.parquet` + vectors): mean statement vector per (agent, day, room), and per (agent, day) over all rooms.
- **Read-outs** (`reads_day.parquet`): per (agent, day), DQ1 ledger items of kind `agent` received, split by the sender's **home domain** in the unit (home = the room holding most of the sender's statements over the unit) and by the room the recipient was in at the receiving call: N_home, R (items from other-domain senders), and per (agent, day) the **posted-unread volume U**: other-domain agent messages posted that day in the other room that the agent did not receive.
- **Fields** (`fields.parquet` + vectors): whitened room kickoffs (#38, #44) and #51 `agent_goal` vectors per agent.
- **Hoppers:** agents with ≥ 1 segment in the other room (from `rooms_timeline`) during the unit, excluding the domain core (in #51g: the two agents with #focus as modal room on ≥ 2 days, as in H47).

## Observables
*Written 2026-10-04 ~20:27 UTC, before any H102 statistic on real data.* Vectors are day-centered (minus the mean over all present agents' agent-day vectors) before projection.
- **O1 Bimodality D and interior occupancy I (all two-room units).** Domain core = stayers (agents in one room all unit). Agent positions z_i = x̄_i·u with u fitted from the *other* half of days (alternating-day split, both directions averaged) and leaving agent i out of its own centroid. **D = (mean z_B − mean z_A) / √((σ_A² + σ_B²)/2)** (Ashman's D; D > 2 means two separated modes). **I** = share of stayers with s ∈ [0.25, 0.75]. Null: room relabel (sizes kept, axis refitted each draw, 1,000 draws) → p for D.
- **O2 Hopper position.** For hopper k: s_k(all) from all its statements, and **s_k(home)** from only its statements made in its home room (carry-over: the hopper's own state, not the mixture). Intermediate = s_k above the 95th percentile of the home-domain stayers' leave-one-out s and below the other domain's 5th percentile. Per hopper-day as well.
- **O3 Dose–response (G51).** Hopper-day s_{k,d}(home) regressed on log(1 + R_{k,d}) and log(1 + U_{k,d}) with hopper fixed effects (weighted by statements), and a lagged form with R_{k,d−1}. **κ_R** (read-outs) vs **κ_U** (posted-unread placebo: the same domain's traffic, not read). Coupling predicts κ_R > 0 and κ_R > κ_U; selection predicts κ_U ≈ κ_R. CI: hopper-cluster bootstrap and day-block bootstrap (sorted days). R-field control: add the hopper's agent-goal projection (constant per agent, absorbed by the fixed effect) and report the cross-sectional s vs goal-projection correlation.
- **O4 Wall width across units.** W = interior occupancy I over all agents (stayers and hoppers) and the cross-domain read share P = Σ R / Σ (R + N_home) per unit. Phase-diagram relation: Spearman(I, P) over units.
- **O5 Field alignment of the axis (G38, G44).** cos(u, u_f) with u_f the whitened room-kickoff difference; null: random directions from the empirical between-agent covariance.
- **O6 Single hopper (G36).** DeepSeek-V3.2's s on its statements made in #rest before the stint (03-24 → 03-26 19:48), in #best during it, and in #rest after (03-30 17:43 → 04-01), on the #36 axis (36b/c stayers) and the #37 axis.
- **Robustness:** both embedding models; style_resid vs white32; dedupe on `self_repeat_both`.

## Null / baseline
- **N1 Room relabel** (O1): random room labels with sizes kept, axis refitted.
- **N2 Stayer distribution** (O2): leave-one-out s of home-domain stayers.
- **N3 Posted-unread placebo** (O3): other-domain traffic the hopper did not read (STANDARDS §1, contemporaneous convergence).
- **N4 Synthetic worlds (axis F):** the kinetic rule on the real #51g read skeleton (ledger π_ij per day) and the real #38 skeleton: coupling (w > 0), field-only (w = 0; hoppers with intermediate own fields), mixture (statements drawn from the room the agent is in), selection (hops caused by content).

## Impostors (STANDARDS §1)
| Impostor | Relevant? | How it is handled | Status |
| --- | --- | --- | --- |
| Scheduler field | weakly | Content positions, not timing; day centering removes common daily shifts. | removed |
| Exogenous field (kickoff/goal/operator) | yes | Day centering removes the global field. The room field (kickoffs) defines the domains in #38/#44 and is measured (O5). In #51 the private agent goals are a per-agent field: R-field control in O3 (agent fixed effects; cross-sectional goal projection). | partly |
| Shared model priors (family, style) | yes | DQ5 `style_resid`; hopper fixed effects in O3 remove each hopper's constant; both models. | removed |
| Contemporaneous convergence | yes | Posted-but-unread other-domain volume as a placebo regressor (O3), and a lagged read term. Not age-matched at message level. | partly |

## Faithfulness scorecard
Scored per model, mapping and window; 0 = not done or failed, 1 = partial, 2 = passed. Scheme and promotion thresholds: `writeup/paper.tex`, Sec. "Assessing model faithfulness".
**Rival models:** R-mixture, R-field, R-selection, R-global (above).
**Locked holdout used for confirmation:** none run. `analysis/confirm.py` targets #47 and #50 (two-room bimodality) and the #51 tail (09-07 → 09-21: #focus hoppers, if #focus is still used). Written and dry-run on non-holdout stand-ins; not run.

| Axis | Test | Score | Evidence |
| --- | --- | --- | --- |
| A mapping | variables defined from dataset fields; assumptions listed; invariant across families and regimes | 1 | Statement-level DQ5 vectors (style_resid, both models), room of each statement from chat rooms and `rooms_timeline` (null t_end fixed), hoppers from segments, read-outs from the DQ1 ledger. One axis per unit; the wall coordinate is a ratio, so it is noisy for 3-agent rooms. |
| B assumptions | stationarity, Markov order, time-rescaling, update-order audit | 1 | Static unit means; the kinetic rule is used only for the synthetic. No Markov audit. |
| C adequacy | beats the null hierarchy, day-blocked held-out data | 1 | The relabel null (axis refitted) is beaten in 9/9 units (bge; 7/9 gte). D ≥ 2 holds in 5/9. No held-out-day likelihood. |
| D unfitted predictions | unfitted statistics and the model's signature | 1 | Bimodality holds where rooms do different things. The wall signature fails: hoppers are not intermediate, and there is no dose–response. |
| E interventional | predicts the change across a natural experiment | 1 | The #focus opening (51g) and DeepSeek-V3.2's #best stint (G36). The stint shifts its in-room talk by 0.25 (gte 0.20), below the 0.3 threshold, and it is back after. |
| F identifiability | synthetic recovery with village sampling; robust to preprocessing | 1 | Real skeletons: D size 0, power 0.77/1.0 at ρ 0.3/1. κ_R power ≥ 0.93 at κ ≥ 0.1, size 0.05–0.18 (liberal). Selection is not separable from coupling at the same day. Results are stable across bge/gte, style_resid/white32 and dedupe, except #35 and #39 (D near threshold). |
| G ground truth | agrees with known structure | 1 | Instruction weeks and the work-split week #41 have the largest D (5.3–6.1); identical-kickoff weeks are lower (median 1.70). The axis is not the kickoff-text direction. |
| H comparative | beats the named rivals | 1 | Beats R-global (two domains). Loses to a sharp-wall, situational rival: content follows the room of the statement (hoppers' in-room talk), not the reading history. R-field is not needed: hoppers are not intermediate at all. |
| I transfer | holds in other same-mode periods, including the holdout | 0 | Holdout not run. |

## Prediction
*Written 2026-10-04 ~20:27 UTC, before the synthetic validation and before any H102 statistic on real data.*

**What I had seen when writing this (so these are not blind):** H47 (C_B per period; #38 0.07, #44 −0.04, #41 0.17, #35 0.10, identical-kickoff periods ≈ 0.55; #focus members already decoupled before #focus: r_F 0.08 → 0.27 → 1.33), H41 round 1b (#51 hoppers: 51% of cross-room adoptions in the cone), H48 (α ~ 1/250 per read), the `rooms_timeline` segment table for #35–#44 and #51 (who hopped, segment counts and hours), and the per-agent chat counts by room and goal. No H102 statistic had been computed.

- **P0, synthetic (axis F; run first).** On the real #51g skeleton: (a) the coupling world gives κ_R > 0 with power ≥ 0.8 at w = 0.3 and κ_U ≈ 0; the field-only world gives κ_R within its null (size ≤ 0.1) [0.5]; (b) the mixture world gives s(home) ≈ 0 while s(all) is intermediate [0.7]; (c) D's relabel null has size ≤ 0.07 [0.7]. If (a)'s power is < 0.8, P3 is reported as inconclusive.
- **P1, two domains where rooms do different things.** D ≥ 2 with relabel p < 0.05 in #38, #44, #35 and #41 (instruction or work split) [0.6]. The median D of these four exceeds the median D of #37, #39, #42 (identical kickoffs) [0.65]. Stayers' interior occupancy I ≤ 0.15 in the four split periods [0.55].
- **P2, hoppers are intermediate (G51, G36).** Hoppers with ≥ 5 hop-days have s(all) above the home stayers' 95th percentile and below 1 [0.6]. Their s(home) is above the home stayers' median (carry-over into their own room) for ≥ 2/3 of them [0.4].
- **P3, wall width grows with hopping read-outs (G51).** κ_R > 0 (p < 0.05) and κ_R > κ_U [0.3]. The low credence reflects H41's 1b correction (leaks half the time) and H48's small pull per read.
- **P4, across units.** Spearman(I, P) > 0 over the two-room units [0.5]; #38 and #44 have the lowest cross-domain read shares (P < 0.02) and I = 0 [0.55].
- **P5, G38/G44 axis = field.** cos(u, u_f) above the 95th percentile of the direction null in both [0.55].
- **P6, G36 hopper.** DeepSeek-V3.2's s on its #best-stint statements exceeds its pre-stint s by ≥ 0.3 [0.45], and its post-stint s falls back toward 0 [0.4].

**Verdict rules.**
- *Replication unit:* **supported** if D ≥ 2 with p < 0.05; **failed** if D < 1 or p > 0.2; **mixed** otherwise. (Replication tests the bimodality half; hoppers are absent.)
- *Natives:* G38/G44 supported if D ≥ 2 (p < 0.05) and P5 holds; G51 supported if P2's first clause and P3 hold, mixed if only P2 holds, failed if hoppers are not intermediate; G36 supported if P6's first clause holds.
- *Hypothesis level (HH332's kill rule):* **failed** if hoppers are not intermediate (P2 first clause fails) or positions are not bimodal (D < 2 in all four split periods). **Supported** if P1, P2 and P3 hold. **Mixed** otherwise (for example bimodal and intermediate, but no dose–response).
- *Multiplicity:* about 10 units × 2 models × 2 variants; only these rules count.

### Amendment 0 (structural, from the scheme build; before any H102 statistic)
*2026-10-04 ~20:34 UTC.* The scheme's hopper rule, applied inside unit 51g only (08-05 → 08-21), changes the hopper census in "Design" above. Those hour counts came from a window that ran to 08-27 and included nights.
- **51g hoppers:** Claude Fable 5 (14 segments, 0.45 h, 17 statements in #focus), Gemini 3.5 Flash (2 segments, 1.1 h, 9 statements), GLM-5.2 (4, 0.1 h, 5), GPT-5.5 (2, < 0.01 h, 2), DeepSeek-V3.2 (1, 0.06 h, 1). DeepSeek-V4-Pro made no statement in #focus and spent < 0.25 h there inside 51g, so it counts as a stayer.
- **Hopping read-outs are tiny:** the hoppers received 2–25 items while in #focus over 13 days, against about 8,000 #general items each (P_hop ≈ 0.003). The core members (Gemini 2.5 Pro, Claude Opus 4.8) made 83 and 81 statements in #general: they are reverse hoppers. Their s is reported as a descriptive extra.
- **Other hoppers found:** Claude Haiku 4.5 in G35 (20 h and 36 statements in #best, 03-19 evening → 03-20). The #rest agents also sat in #general that night (1,062 items read outside the home room in #35). The extra G38 "hopper" is a start-of-period move artifact (1 statement).
- **Consequence:** P3 (dose–response) runs on very few hopping read-outs. The synthetic P0(a) power on this skeleton decides whether P3 is scored or reported as inconclusive. No prediction is changed.

### Amendment 1 (after the synthetic validation, before any H102 statistic on real data)
*2026-10-04 ~20:44 UTC.* `analysis/synthetic.py`, 40 worlds per setting. Statement skeletons and hopping read-outs are the real ones. Calibration (instrument, not an outcome): statement noise σ_s² per coordinate from within agent-day dispersion; agent-constant variance τ² = 0.0014 (H100). Domain separation ρ = |μ_B − μ_A|² / E|a_i − a_j|².

| Check | Result |
| --- | --- |
| D null (ρ = 0), 7 fixed-room units | rule rejects (D ≥ 2 and p < 0.05) in 0%; median D −0.51 (leave-one-out centroids bias D down) |
| D power | ρ 0.3: 77% (median D 2.7); ρ 1: 100% (median 6.3) |
| κ_R size (51g, no coupling) | 0.10 (none), 0.05 (field world), 0.18 (mixture world): the 13-day bootstrap is liberal |
| κ_R power | κ 0.1: 1.00 (recovered 0.08); κ 0.3 with day-to-day persistence 0.5: 0.93 (recovered 0.17, attenuated) |
| selection world (κ 0.3, no carry-over) | κ_R 0.29, power 1.0; lagged κ −0.04 vs +0.03 to +0.06 under coupling |
| field world (hoppers' own field 0.2–0.6) | s(all) 0.34 > stayers' p95 0.19, κ_R 0.00: hoppers look intermediate without any dose |
| mixture world (γ = 1) | s(all) 0.06, s(home) 0.04, both below the stayers' p95: the hoppers make too few #focus statements for a mixture to fake intermediacy |

- **P0(a)** passes on power (≥ 0.8). Size is borderline (0.10, up to 0.18 in the mixture world). A κ_R p-value is therefore read at α = 0.01, and P3 additionally requires a lagged κ_R > 0.
- **P0(b)** passes for s(home), but the mixture world does not make s(all) intermediate on this skeleton.
- **P0(c)** passes.
- **What the design cannot do:** contemporaneous κ_R does not separate coupling from selection. The lagged term separates them only weakly. Intermediacy without a dose–response is the field world's signature, not coupling.
- P3's verdict uses α = 0.01 and the lag condition. Other rules are unchanged.

## Results by goal period
Primary: bge style_resid statement vectors, day-centred; gte in brackets. D = Ashman bimodality of cross-fitted axis projections (stayers); p = relabel null with the axis refitted.

| Period | Role | Verdict | Key numbers |
| --- | --- | --- | --- |
| [G35](goalperiod-subhypotheses/G35/README.md) | replication | mixed | D 1.57 (p 0.007) [2.53]; RPG fork week; 3 #best stayers; the 03-19/20 room episodes give P_hop 0.073; hopper Claude Haiku 4.5 s(all) −0.17 (gte 0.14) |
| [G36](goalperiod-subhypotheses/G36/README.md) | native | mixed | D 1.86 (p 0.017); DeepSeek-V3.2 in-#best talk s 0.16 vs its #rest talk −0.09 (shift 0.25; gte 0.20); after the stint (#37) −0.13 |
| [G37](goalperiod-subhypotheses/G37/README.md) | replication | mixed | D 1.70 (p 0.039) [1.85] |
| [G38](goalperiod-subhypotheses/G38/README.md) | native | mixed | D 5.40 (p 0.003) [5.04]; I 0.08; P_hop 0.0001; axis vs kickoff |cos| 0.02 (null p95 0.49) |
| [G39](goalperiod-subhypotheses/G39/README.md) | replication | mixed | D 1.45 (p 0.011) [0.49, p 0.16] |
| [G41](goalperiod-subhypotheses/G41/README.md) | replication | supported | D 6.10 (p 0.002) [5.62]; I 0.13 |
| [G42](goalperiod-subhypotheses/G42/README.md) | replication | supported | D 2.35 (p 0.001) [2.72] |
| [G44](goalperiod-subhypotheses/G44/README.md) | native | mixed | D 5.31 (p 0.001) [5.65]; P_hop 0; axis vs kickoff |cos| 0.27 (null p95 0.34) |
| [G51](goalperiod-subhypotheses/G51/README.md) | native | failed | 51g: D 5.50 (p 0.006); hoppers s(all) −0.33 to 0.25 vs stayers' p95 0.21; Fable 5 (7 hop-days) 0.06; κ_R −0.014 [−0.042, 0.024] |

## Results
### Exploratory round 1 (2026-10-04; non-holdout only, asserted in the scheme)
- **Scheme:** 46,500 statements in 10 units (#35–#44, #51g), 156 agent-unit domain rows, 1,076 agent-day read rows; 12 MB in `data/processed/H102-room-domain-walls/`.
- **Code:** `scheme/build.py`; `analysis/{h102lib,synthetic,run,summarize,period_folders,confirm}.py`.
- **Numbers:** `results/raw_all.json` (5 instrument variants), `results/results.json`, `synthetic/synthetic_summary.json`. Estimates: 38 rows in `per_period_estimates` (hypothesis H102).
- **Figures:** `figures/summary_obs.pdf` (D per unit; the 51g wall), `figures/summary_synthetic.pdf`.

**Headline.**
1. **Two domains where rooms do different things.** In #38 and #44 (room-specific instructions) and #41 (rooms that split topics by choice), stayers project onto the inter-room axis as two separated groups: D 5.3–6.1 (relabel p95 ≈ 1.0), every stayer on its own side. In identical-kickoff weeks the split is weaker: #37 1.70, #39 1.45, #42 2.35 (median 1.70). #35's fork week is between them (1.57; gte 2.53). The #focus side room (51g) is a domain too: its two residents sit at D 5.5 from 20 #general stayers.
2. **The wall is empty.** Cross-domain read-outs are near zero in the fixed-room weeks: P_hop ≤ 0.001 in #38–#44 (H41's cage). In 51g, hoppers read 2–25 items while in #focus over 13 days, against about 8,000 #general items each (P_hop 0.004).
3. **Hoppers do not sit in the wall; they switch sides.** The one frequent hopper (Claude Fable 5, 7 hop-days) has s 0.06, inside the #general stayers' range (median 0.06, 95th percentile 0.21). So do Gemini 3.5 Flash (0.09) and GLM-5.2 (0.01). Their statements made *inside* #focus sit at s 0.15–0.51. The #focus residents' statements in #general sit 0.6–0.7 of the way toward #general. Content follows the room the agent is speaking in. Nothing carries back into its home room.
4. **No dose–response on hopping read-outs.** Hopper fixed effects: κ_R −0.014 [−0.042, 0.024] per e-fold of read-outs (bge), −0.015 [−0.068, 0.068] (gte); lagged κ_R −0.004 (gte +0.021, p 0.036, above the α 0.01 rule). For all #general agents, reads from #focus-resident senders: κ 0.000 [−0.009, 0.008]. Synthetic power is ≥ 0.93 at κ 0.1, so a shift of ≥ 0.1 of the wall per e-fold of read-outs is ruled out on this skeleton.
5. **The domain axis is not the instruction text.** #38 |cos(u, u_f)| 0.02, #44 0.27, both inside the direction null (as H100's f_field).
6. **DeepSeek-V3.2's #best stint (G36):** its in-#best talk sits 0.25 (gte 0.20) toward #best relative to its #rest talk, and its #rest talk after the stint is at −0.13. It is the same situational pattern: the room it speaks in, not a carried state. The shift is below P6's 0.3.

**Synthetic validation (axis F):** Amendment 1.

**Outcome vs prediction**

| | Prediction (locked) | Outcome | Verdict |
| --- | --- | --- | --- |
| P0 | (a) κ_R power ≥ 0.8, size ≤ 0.1; (b) mixture: s(home) ≈ 0; (c) D size ≤ 0.07 | 0.93–1.0, size 0.05–0.18; s(home) 0.04; 0.00 | (a) power yes, size borderline; (b), (c) passed |
| P1 | D ≥ 2, p < 0.05 in #38, #44, #35, #41; split median > identical median; stayer I ≤ 0.15 in split weeks | 3/4 bge (#35 1.57), 4/4 gte; 5.35 vs 1.70; I 0.08/0.13/0.17/0.45 | mostly met (#35 short in bge; I fails in #35) |
| P2 | hoppers with ≥ 5 hop-days above stayers' p95 and < 1; s(home) above stayers' median | Fable 5 0.06 vs p95 0.21; s(home) 0.06 vs median 0.06 | **failed** |
| P3 | κ_R > 0 (α 0.01 after Amendment 1), κ_R > κ_U, lagged κ_R > 0 | −0.014 [−0.042, 0.024]; κ_U −0.006; lag −0.004 | **failed** (powered at κ ≥ 0.1) |
| P4 | Spearman(I, P) > 0; #38/#44 P < 0.02 and I = 0 | 0.30 (p 0.43; gte 0.42); P ≤ 0.0001, I 0.07/0.17 | weak; I = 0 failed (I is noisy for small rooms) |
| P5 | axis along the kickoff direction in #38, #44 | 0.02 (p 0.95), 0.27 (p 0.14) | **failed** |
| P6 | G36 hopper shift ≥ 0.3, back after | 0.25 (gte 0.20); after −0.13 | mixed |
| HH332 kill | hoppers not intermediate or no bimodality | hoppers not intermediate | **failed** (bimodality half supported) |

**What this means.**
1. Rooms with different work are two content domains, and the interface between them is a sharp wall with no interior. In Ising terms, the wall width is below one agent.
2. Bridging agents do not broaden the wall. They switch domains with the room they are in: their state is local to the room's field, not an average of what they have read. This fits H41's 1b result (hoppers leak only half the time) and H48's small pull per read.
3. A hopper is a carrier only while it is physically present. It brings little content home.

**Operator-facing conclusion.**
- To keep two groups' content separate, give them different work (D ≈ 5–6). Identical instructions in separate rooms give a weaker split (D ≈ 1.5–2.4).
- Letting a few agents visit the other room does not blend the domains: at the observed visit rates (≈ 0.3% of read items), a visitor's home-room content does not move (|κ| < 0.04 per e-fold of reads).
- To transfer content across rooms, a visitor is not enough. Post into the other room, or move the agent.

**Caveats.**
- **Few hoppers, little hopping.** One hopper has ≥ 5 hop-days; hopping read-outs total about 50 items. The dose test is powered against κ ≥ 0.1 per e-fold, not against small per-read pulls (H48's α ~ 1/250).
- **Small rooms.** #best had 3 stayers in #35–#37, so leave-one-out centroids are noisy, and the stayers' interior occupancy I is inflated (0.36–0.45). D in those weeks is near threshold.
- **The κ_R bootstrap is liberal** (size up to 0.18), and same-day κ_R cannot separate coupling from selection.
- **The #focus core is 2 agents.** Their centroid sets the axis in 51g.
- **Statement-level geometry is model-dependent** (infra Known issues). Hopper positions agree within 0.05–0.25 between bge and gte.

### Confirmatory design (written 2026-10-04 after exploration; not run)
`analysis/confirm.py`, frozen predictions in the script header:
- **C1 (domains):** in each held-out two-room goal period among #45–#50 with ≥ 3 stayers per room, D > relabel p95 (p < 0.05). Where room kickoffs differ (whitened cos < 0.95), D ≥ 2 [0.65].
- **C2 (sharp wall, no carry):** in the #51 tail (09-07 → 09-21), every #general hopper with ≥ 3 hop-days has s(home) below the #general stayers' 95th percentile [0.6]. This needs #focus to be in use. If no hopper qualifies, C2 is void, not failed.
- **C3 (no axis along the instruction text):** where room kickoffs differ, |cos(u, u_f)| stays inside the direction null [0.6].
- **Safeguards:** refuses without `--confirm --i-understand-this-uses-the-locked-holdout`; refuses unless the card, the script, `h102lib.py`, `run.py` and `scheme/build.py` are committed and unmodified; calls `holdout_ledger.check()`. `--dry-run` runs on non-holdout stand-ins (#41, #42, #44, 51g) and asserts that no held-out row is loaded.
- **Reuse disclosure:** #45–#50 content and the #51 tail are planned by many content hypotheses (H26, H47, H81–H83, H98 among them). H47's C1 (room contrast C_B on #45–#47, #50) is the closest cousin; whichever runs second must say so.

## Round 2 redirects
**What the direction is really after:** what sets the width of the boundary between two content domains in a swarm, and whether bridging agents widen it.
- **H102-R1. Situational vs carried state at the statement level.** Model each hopper statement's position as room-of-statement + agent constant + time since entering the room. Measure how fast an agent's content switches on entry and on exit (minutes), using the ledger's call times.
- **H102-R2. The #35 room episodes (03-19/20).** The #rest agents spent the night of 03-19 in #general, and Claude Haiku 4.5 spent it in #best (1,062 items read outside the home room in #35). Did the domains move toward each other on 03-20, compared with the other days of #35?
- **H102-R3. Larger dose:** NE42's merged week (#40). There every agent reads the other partition: an all-hopper limit with read shares of 0.3–0.6.
- **H102-R4. Field as work:** replace the kickoff-text direction with DQ4 repo labels per room (as H100-R3).

## Notes
- 2026-10-04 ~20:27 UTC: card, observables, nulls and predictions written by the H102 round-1 agent, before any H102 statistic on real data.
- ~20:32 UTC: scheme built; period folders written with dated predictions; Amendment 0 (structural census). ~20:44 UTC: synthetic validation, Amendment 1. ~20:46 UTC: real-data run.
- Post hoc additions (labelled): the reverse-hopper numbers (core members' #general talk) and the all-agent R_dom regression were planned as descriptive extras in the scheme but not as predictions; the "situational" reading is post hoc.
- Suggested shared changes (not made): DEFINITIONS entries for *domain axis u, wall coordinate s, bimodality D (cross-fitted, axis refitted under relabel), hopping read-outs R_hop, posted-unread volume U*; a `room_at_statement` helper in `infra/shared/` (duplicated in H100 and H102 schemes); a natural-experiments note on the #35 room episodes (`rooms_timeline`): the #rest agents sat in #general 03-19 ~20:35 → 03-20 17:01 UTC while Claude Haiku 4.5 sat in #best; every agent moved to #general at the end of 03-20 (~20:45) for the weekend.
