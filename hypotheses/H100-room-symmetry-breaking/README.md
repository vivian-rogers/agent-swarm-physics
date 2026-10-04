# H100: #best/#rest: explicit vs spontaneous symmetry breaking

**Status:** exploratory round 1 done (2026-10-04, non-holdout only): **mixed.** The #best/#rest content difference is mostly endogenous: after removing the members' own constants and the operator's room-field directions, the rooms still differ beyond random groupings (Q_spont 1.8–5.7, p < 0.05 in 5/7 regime-III periods; f_spont 0.58–0.91). Composition is small (f_comp 0.03–0.39). The explicit field is not visible as a direction: the room-kickoff and operator-message directions carry a chance share (#38 0.18 vs null 0.16; #44 0.08 vs 0.03), although the two fielded periods have the largest separations. The divergence regenerates at each goal (no remanence across NE42 or the 04-27 swap). Movers split: one adopts the new room within a day (Gemini 3.1 Pro), one keeps its old room's position all week (GPT-5.4), one was already aligned before the move (Sonnet 4.6, 04-02). `analysis/confirm.py` written and dry-run, not run. Card and predictions written 2026-10-04 ~20:25 UTC, before any H100 statistic on real data. Approved by Vivian in the dashboard vetting panel 2026-10-04 from HH66.
**Question (GOALS.md):** **Q2** (what is field and what is coupling: how much of a room difference is the operator's room field) and **Q3** (collective order beyond fields: is there a room-held divergence that no field and no member explains).
**Fields:** stat mech (explicit vs spontaneous symmetry breaking in a two-block vector-spin model), sociophysics (group identity vs composition; movers), econometrics analogue (two-way fixed effects identified by movers, Abowd–Kramarz–Margolis)
**Literature:** `physics-models/11-vector-spins/README.md` (Stanley 1968; mean-field O(n)); `physics-models/10-potts/README.md` (rooms as Potts domains). Project cards: H47 (rooms bound content coherence; C_B is a global share; NE42 shows no partition memory), H13 (family content fields are style), H73 (style is an agent constant), H05 (rooms couple talk only through reads), H41 (the room cut is a cage; hoppers leak about half the time, round 1b), H01/H58 (agent + own artifact is the unit), H83 (newcomer enculturation; newcomers are left to H83 here).
**Definitions used** (`physics-models/DEFINITIONS.md`): Agent; Regime; Driving / external field (room kickoffs and operator messages); Interaction (broadcast: co-located = same current room); Agent state, *vector (for model 11)* in the DQ5 variant **agent-day mean of 32-d regime-whitened, style-residualized statement vectors** (`agent_day_style_resid_<model>.npy`, both models). New named variants proposed (defined under Observables; DEFINITIONS.md not edited): **room separation S**, **relabel excess Q**, **composition / field / spontaneous shares f_comp, f_field, f_spont**, **mover index φ**, **room remanence R**.
**From:** HH66 in `hypotheses/hypohypotheses/HYPOHYPOTHESES.md` · **Models:** `physics-models/11-vector-spins/` (primary), `physics-models/10-potts/` (secondary: the room label as a Potts domain index)
**Data inputs (shared tables first):** `embeddings/agent_day.parquet` + `agent_day_style_resid_{bge_small,gte_modernbert}.npy` (primary) and `agent_day_white32_*` (variant without style removal); `embeddings/statements.parquet` + `rooms_timeline` (room of each statement; null `t_end` filled with +inf before any filter, infra Known issues); `embeddings/goals.parquet` + `goal_vectors{,_gte_modernbert}.npy` (`kickoff_room` rows); `chat_core` + `chat_{bge_small,gte_modernbert}.npy` (operator messages per room, human speakers only); `period_units`; `roster`; `hypotheses/holdout.json` via `holdout_mask`. No text is read.

## Source HH (verbatim from the HH list, including refinements)
#best/#rest: explicit vs. spontaneous symmetry breaking. The room designation is an operator field. Differences between rooms split into a response to that field and spontaneous divergence, which persists after members swap. *Check:* behavior of agents moved between rooms (NE19 Opus 4.7) vs. room averages; divergence that survives membership changes.
  *Models:* 10, 11, 08 · *Periods:* #35–#51; NE19

## Question
When the #best and #rest rooms differ in content, how much of the difference is (i) composition (each member's own constant), (ii) the response to the operator's room field (room-specific kickoffs and operator messages: explicit symmetry breaking), and (iii) a divergence that neither explains (spontaneous, endogenous symmetry breaking)? Does the spontaneous part belong to the room, so that a moved agent takes on its new room's position, or to the members?

## Design: two layers (STANDARDS §4)
- **Scope and the NE19 problem.** NE19 (Opus 4.7 moved to #rest on 2026-06-01) opens #45, which is held out. It is a confirmatory target only (`analysis/confirm.py`). Exploration uses the three non-holdout operator moves between #best and #rest: **04-02** (Sonnet 4.6, #rest → #best, start of #38), **04-27** (Opus 4.6, Sonnet 4.6 and GPT-5.4, #best → #rest, start of #39), **05-25** (Gemini 3.1 Pro, #best → #rest, start of #44). All three coincide with a goal change. Newcomers (roster joins) are H83's object and are not used as movers.
- **Replication** (role `replication`): the decomposition (O1–O4) on every non-holdout multi-room period: G35, G36, G37, G42. The same estimator also runs inside the native periods.
- **Natives** (role `native`), each with its own dated prediction:
  - **G38** (room-specific kickoffs, cosine 0.86 between room kickoffs): the explicit-field share, plus the 04-02 mover.
  - **G39** (the 04-27 reshuffle: half of #best moves to #rest): the mover index for three movers, and the swap-carry test (does the #38 room difference stay with the rooms or with the agents?).
  - **G44** (room-specific kickoffs, cosine 0.81; heavy operator traffic in #best): the field share, plus the 05-25 mover.
  - **G41** (identical kickoffs; same partition as #39 after the NE42 merge): spontaneous divergence with zero explicit field, and remanence across the merge (R between #39 and #41).
- **Exception (CLAUDE.md (b), agent-level properties):** agent constants a_i are estimated from *other* periods (leave-period-out). Their invariance across periods is checked first (O2a). **Exception (c)** for the mover and swap-carry tests: the boundary is the object.

## Model
**From:** `physics-models/11-vector-spins/` (soft-spin O(n), n = 32 whitened dimensions), with the room label as a Potts domain index (`physics-models/10-potts/`).

The content state of agent i on day d (period P, room r) is the agent-day vector x_{i,d} ∈ ℝ³². Linear two-block soft-spin model:

  x_{i,d} = g_d + a_i + b_{r(i,d)} + ε_{i,d},   b_r = χ h_r + m_r

- g_d: day field common to all agents (goal, kickoff, schedule). Removed by centering on the day mean over all present agents.
- a_i: agent field (the member's own style-free content prior). Composition is the room average of a_i.
- h_r: the operator room field: the whitened room kickoff plus the mean of operator (human) messages posted in room r during P. χ is the room susceptibility.
- m_r: spontaneous room magnetization, orthogonal to the field difference h_best − h_rest. In the linear soft-spin model with within-room coupling J, finite-N room means fluctuate with variance ∝ 1/(N_r (1 − J)²), so coupling amplifies a random room divergence above the relabel null by about 1/(1 − J)². In the mean-field O(n) model with J > n the room orders along a random direction (true spontaneous symmetry breaking).
- **Mover dynamics:** a mover k from room A to room B at time T relaxes as x_k(t) = a_k + b_A + (b_B − b_A)(1 − e^{−(t−T)/τ}). A room-held divergence gives φ → 1 (k looks like a native of B). Composition gives x_k = a_k (no room term). Agent-carried state (H58: agent + own artifact; H70: return to own repo) gives a slow τ and φ < 0 for days.

**Rivals.**
- **R-comp (composition / shared priors):** rooms differ only because the operator sorted agents with different constants. f_comp ≈ 1; residual relabel excess Q_res ≈ 1; movers keep their own constant (φ ≈ φ_comp).
- **R-field (explicit symmetry breaking only):** the room difference lies along h_best − h_rest. Large f_field in #38/#44; Q_spont ≈ 1 in identical-kickoff periods.
- **R-spont (spontaneous, room-held):** Q_spont > 1 in identical-kickoff periods; movers adopt the new room. Sub-variants: the direction regenerates at each goal (no remanence, R ≈ 0) or persists (remanence, R > 0).
- **R-carry (agent + own artifacts):** movers keep their old room's content for days (φ < 0 after the move).

## Data scheme (`scheme/`)
`scheme/build.py` → `data/processed/H100-room-symmetry-breaking/` (≤ 20 MB, `_provenance.json`). Non-holdout rows only, asserted with `holdout_mask`.
- **Agent-day table** (`agent_days.parquet`): every non-holdout agent-day of goals #33–#51 from `embeddings/agent_day.parquet` (Claude Code agent excluded), with goal, period unit, regime, n statements, and the agent's **room of the day**: the room holding the majority of its statements that day (chat: message room; intentions: as-of lookup in `rooms_timeline` with null `t_end` → +inf), its share in that room, and the number of rooms used.
- **Vectors** (`x_<variant>_<model>.npy`, float16, rows aligned with the table): `style_resid` (primary) and `white32` (variant), for `bge_small` and `gte_modernbert`.
- **Field directions** (`fields.parquet` + `fields_<model>.npy`): per multi-room period, whitened (regime whitener at d = 32) room kickoff vectors (`goals.parquet`, kind `kickoff_room`), and the whitened mean of human chat messages per room (≥ 3 messages per room; message ids from `chat_core`, vectors from `chat_<model>.npy`; no text).
- **Regimes covered:** II (#35, #36a) and III (#36b onward). Agent constants and decomposition shares use the regime-III basis only (whitening differs by regime); #35 gets Q and field shares in its own basis, without f_comp.

## Observables
*Written 2026-10-04 ~20:25 UTC, before any H100 statistic on real data.* All vectors are day-centered: x̃_{i,d} = x_{i,d} − mean over agents present on d (removes g_d).
- **O1 Room separation S and relabel excess Q.** Agent means x̄_i over the agent's days in the period (only days in its period room; movers inside a period are excluded from O1). Split each agent's days into two halves by alternating order (H1, H2). Δ^(h) = mean_{i∈best} x̄_i^(h) − mean_{i∈rest} x̄_i^(h). **S = Δ^(1)·Δ^(2)** (unbiased for |Δ_true|²). **Q = S / mean(S_null)** under the room-relabel null (random partitions with room sizes kept, 2,000 draws); p = share of S_null ≥ S. Q ≈ 1: the rooms differ like random groupings of the same agents.
- **O2 Composition share f_comp.** (a) Agent constants â_i = mean over other regime-III non-holdout periods of the agent's period-mean of x̃ (leave-period-out; for mover tests leave out both sides of the boundary). Invariance check: across agents, the correlation of â_i built from two disjoint period sets (odd vs even periods) must exceed its agent-permutation null. (b) Δ_comp = room difference of â_i. **f_comp = Δ_comp·Δ / S**, with Δ the full-data room difference. Unbiased because â_i uses other periods.
- **O3 Field share f_field.** u_f = unit vector of the whitened difference of the two room kickoffs (#38, #44; only where their cosine < 0.95), and u_op = unit vector of the difference of the rooms' mean operator-message vectors (where both rooms have ≥ 3). **f_field = (Δ^(1)·u)(Δ^(2)·u) / S**, the share of the room separation along the field. Chance for a random Δ is 1/32 ≈ 0.03; null: random unit directions drawn from the empirical agent-difference covariance (H20: isotropic nulls are too narrow).
- **O4 Spontaneous share and residual excess.** f_spont = 1 − f_comp − f_field. Residual relabel excess **Q_res**: O1 on x̄_i − â_i (composition removed at agent level); **Q_spont**: the same after projecting out u_f and u_op.
- **O5 Mover index φ (natives G38, G39, G44).** In the period after a move, cross-fitted pair similarity sim(k, j) = ½(x̄_k^(1)·x̄_j^(2) + x̄_k^(2)·x̄_j^(1)). For mover k: M_k = mean sim(k, stayers of the new room) − mean sim(k, stayers of the old room). The native contrast C = mean over stayers j of [sim(j, own-room stayers) − sim(j, other-room stayers)]. **φ_k = M_k / C** (+1: like a native of the new room; −1: like a native of the old room; 0: halfway). Comparisons: φ_k^pre (same index in the period before the move, labels of the post period), φ_k^comp (the same index with â in place of x̄), and the stayers' leave-one-out φ distribution (natives). Day-1 φ (first post-move day only) for timing. CI: bootstrap over the post period's days.
- **O6 Swap-carry (native G39).** Δ_38 (room difference in #38 by #38 rooms) and Δ_38^agent (the #38 positions grouped by the agents' #39 rooms). R_room = cos(Δ_39, Δ_38) (the rooms carry the difference); R_agent = cos(Δ_39, Δ_38^agent) (the agents carry it). Null: relabel of the #39 partition.
- **O7 Room remanence R (native G41; replication across consecutive period pairs).** R = cos(Δ_P^spont, Δ_P'^spont) for consecutive multi-room periods with the same room names; null: relabel both partitions independently.
- **Robustness:** both embedding models; style_resid vs white32; agent-weighted vs day-weighted room means.

## Null / baseline
- **N1 Room relabel** (O1, O4, O6, O7): random partitions of the period's agents with room sizes kept; 2,000 draws.
- **N2 Composition model** (O2, O5): â_i from other periods; φ_comp gives what a mover would show if only its constant mattered.
- **N3 Field-direction null** (O3): random directions from the empirical between-agent difference covariance (2,000 draws).
- **N4 Synthetic worlds (axis F):** on the real agent × day × room skeletons of #36–#44 with real statement counts: composition-only, field-only, spontaneous-room, room-held movers, carried movers, and a mixed world.

## Impostors (STANDARDS §1)
| Impostor | Relevant? | How it is handled | Status |
| --- | --- | --- | --- |
| Scheduler field | weakly | Content, not timing. Day centering removes any day-level common shift, which is where the schedule enters agent-day means. | removed |
| Exogenous field (kickoff/goal/operator) | yes: it is half the question | The global goal/kickoff field is removed by day centering. The room-specific part is *measured* (O3: room kickoff and operator-message directions, `goal_fields` kickoff_room rows), not assumed away. Unrecorded room drives (shared repos, the #35 RPG forks) cannot be separated from coupling; they count as endogenous ("spontaneous") when the room's members created them. | partly |
| Shared model priors (family, style) | yes | DQ5 `style_resid` vectors; leave-period-out agent constants (O2) remove each member's own prior, which includes its family; both embedding models. | removed (if O2a passes) |
| Contemporaneous convergence | partly | S and Q are static period-level separations, not co-movement, so co-timed convergence does not enter directly. Whether movers align through reading (vs a room-level drive they meet on arrival) needs a read vs posted-unread test at matched age; not run in round 1. | open |

## Faithfulness scorecard
Scored per model, mapping and window; 0 = not done or failed, 1 = partial, 2 = passed. Scheme and promotion thresholds: `writeup/paper.tex`, Sec. "Assessing model faithfulness".
**Rival models:** R-comp, R-field, R-spont (with or without remanence), R-carry (above).
**Locked holdout used for confirmation:** none run. `analysis/confirm.py` targets NE19 (#45: Opus 4.7 to #rest) and #46, #47, #50 (decomposition). Written and dry-run on non-holdout stand-ins; not run.

| Axis | Test | Score | Evidence |
| --- | --- | --- | --- |
| A mapping | variables defined from dataset fields; assumptions listed; invariant across families and regimes | 1 | Agent-day DQ5 vectors (style_resid, both models); rooms from statements + `rooms_timeline` (null t_end fixed); fields from `goal_fields` kickoff_room rows and operator messages. Agent constants pass the invariance check (odd vs even periods r 0.49, null p95 0.14; gte 0.45 / 0.13; 17 agents). Regime III only for the decomposition (#35 in its own basis). |
| B assumptions | stationarity, Markov order, time-rescaling, update-order audit | 1 | Static period means; within-period stationarity assumed. Mover day profiles show no relaxation transient (day-1 φ already at the period value), so the "relaxation time" τ is below one day. No Markov audit. |
| C adequacy | beats the null hierarchy, day-blocked held-out data | 1 | Relabel null beaten in 5/8 periods (bge; 6/8 gte), and after composition and field removal in 5/7 regime-III periods (bge; 4/7 gte). Null size 0.04 (synthetic). No held-out-day likelihood. |
| D unfitted predictions | unfitted statistics and the model's signature | 1 | Mover index and remanence are not fitted. Movers: 3/5 pass P5 in bge (2/5 gte), 1 carries. Remanence 0 (P6 met). The explicit-field signature (separation along h_best − h_rest) failed. |
| E interventional | predicts the change across a natural experiment | 1 | Three operator moves (04-02, 04-27, 05-25) and NE42. One clean adoption (05-25), one pre-aligned mover, one carried mover; the 04-27 native contrast is marginal (C p 0.04–0.10). NE19 reserved for confirmation. |
| F identifiability | synthetic recovery with village sampling; robust to preprocessing | 1 | Real-skeleton synthetic: Q size 0.04; shares separate the five worlds; mover rule power 0.93 at ρ = 1 but 0.45 at ρ = 0.3; remanence null fixed to a joint relabel (size 0.025). Real results agree across bge/gte and style_resid/white32 except #39 and #42 (borderline). |
| G ground truth | agrees with known structure | 1 | The two periods with room-specific kickoffs have the two largest separations (Q 6.9, 5.1 vs median 1.7; rank p 0.048, post hoc). The field's *direction* (kickoff text) is not recovered. |
| H comparative | beats the named rivals | 1 | Beats R-comp (f_comp ≤ 0.2 where rooms separate; Q_res > 1) and R-field-as-direction (chance share). Among R-spont variants, regeneration beats remanence. R-carry describes one of five movers (GPT-5.4). |
| I transfer | holds in other same-mode periods, including the holdout | 0 | Holdout not run (NE19 / #45–#48 in `confirm.py`). |

## Prediction
*Written 2026-10-04 ~20:25 UTC, before the synthetic validation and before any H100 statistic on real data.*

**What I had seen when writing this (so these are not blind):** the H47 card (C_B per period: #38 0.07, #44 −0.04, #41 0.17, identical-kickoff periods ≈ 0.55; #41 rooms separated from day 0; room-instruction directions carry ≈ 0 of the room *co-fluctuation*; NE42 r_X 0.57 → 1.37 → 0.17), H13, H73, H05, H41 (1b), H58/H70, the room-membership table (chat counts per agent, room and goal) and the move dates listed above. No content statistic of H100's estimators had been computed.

- **P0, synthetic (axis F; run first).** On the real skeletons: (a) relabel-null size of Q ≤ 0.07 at α 0.05 [0.7]; (b) f_comp, f_field, f_spont recovered within ±0.15 in the mixed world [0.6]; (c) the 04-27 mover test (3 movers, 5 post days) separates a room-held world (φ ≈ 1) from a composition world (φ ≈ φ_comp) with power ≥ 0.8 at a room effect equal to the between-agent constant spread [0.5]. If (c) fails, P5 is reported as inconclusive.
- **P1, rooms differ beyond random groupings (replication).** Q > 1 with p < 0.05 in ≥ 6 of the 8 multi-room periods (#35–#39, #41, #42, #44) [0.75].
- **P2, composition is a minor part.** f_comp ≤ 0.3 in ≥ 2/3 of the regime-III multi-room periods, in both models [0.6]. The constants pass the invariance check (O2a) [0.7].
- **P3, explicit field.** In #38 and #44, f_field along the room-kickoff direction ≥ 0.15 and above the N3 null (p < 0.05) [0.5]. In identical-kickoff periods f_field along u_op ≤ 0.1 [0.6].
- **P4, spontaneous divergence.** In the identical-kickoff periods (#36, #37, #39, #41, #42) Q_spont > 1 with p < 0.05 in ≥ 3/5 [0.6], and f_spont ≥ 0.5 in ≥ 3/5 [0.55]. #41 specifically: Q_spont > 1, p < 0.01 [0.8].
- **P5, movers take the new room's position.** Across the 5 mover-events (04-02: 1; 04-27: 3; 05-25: 1): φ_post ≥ 0.5 and φ_post − φ_comp ≥ 0.5 for ≥ 3/5 [0.55]; φ_pre ≤ 0 for ≥ 3/5 [0.6]; day-1 φ ≥ 0.5 for ≥ 3/5 (the quench completes in the first statements, H47) [0.45].
- **P6, no remanence.** R(#39, #41) within the relabel null (|z| < 2) [0.65]; mean R over consecutive same-name period pairs within ±0.15 of 0 [0.6].
- **P7, swap-carry (G39).** Both R_room and R_agent within the relabel null (the goal change regenerates the difference) [0.55]; if either is significant, R_room > R_agent [0.5].

**Verdict rules.**
- *Replication period:* **supported** if Q_res > 1 with p < 0.05 (a room divergence beyond composition) and f_comp < 0.5; **failed** if Q ≤ 1 with p > 0.2 or f_comp ≥ 0.7; **mixed** otherwise.
- *Native periods:* G38/G44 supported if P3's field clause holds there and Q_spont > 1 (p < 0.05); G39 supported if P5 holds for ≥ 2 of its 3 movers; G41 supported if Q_spont > 1 (p < 0.01) and P6 holds; failed if the primary clause is reversed; mixed otherwise.
- *Hypothesis level:* HH66's claim (both parts exist; the spontaneous part is held by the room, not the members) is **supported** if P3 (field), P4 (spontaneous) and P5 (movers) hold; **failed** if P4 and P5 both fail (the difference is composition plus field); **mixed** otherwise. "Persists after members swap" is read as P5 (within a period the divergence stays with the room) and P6/P7 (across goals).
- *Multiplicity:* 8 periods × 2 models × 2 variants; only the rules above count. Per-period p-values are descriptive.

### Amendment 1 (after the synthetic validation, before any H100 statistic on real data)
*2026-10-04 ~20:40 UTC.* `analysis/synthetic.py`, 40 worlds per setting on the real skeleton of #33–#51 (non-holdout agent-days, real rooms and moves). Calibration (instrument, not an outcome): day-to-day noise σ² = 0.0035 per coordinate; agent-constant variance τ² = 0.0014 (cross-period covariance of constants). Room-effect size ρ = |b_best − b_rest|² / E|a_i − a_j|².

| World (ρ) | Q rejects | Q_spont rejects | f_comp | f_field (#38/#44) | f_spont | φ_post / φ_comp | P5 rule passes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| null | 0.04 | 0.04 | – | – | – | (C not significant: 96%) | 0.00 |
| composition (0.3 / 1) | 0.68 / 0.99 | 0.07 / 0.10 | 0.93 / 0.97 | 0.04 / 0.03 | 0.05 / 0.02 | −0.78 / −1.00 (ρ 0.3) | 0.00 |
| field (0.3 / 1) | 0.33 / 0.31 | 0.07 / 0.09 | – | 0.71 / 0.88 (direction-null power 1.0) | – | 1.40 / −0.09 (fielded moves) | 0.00 |
| spontaneous (0.1 / 0.3 / 1) | 0.35 / 0.85 / 1.00 | 0.77 / 0.98 / 1.00 | 0.55 / 0.32 / 0.14 | 0.03 | 0.42 / 0.65 / 0.84 | 0.89 / −0.10 (ρ 0.3) | 0.03 / 0.45 / 0.93 |
| carried movers (1) | 0.98 | 1.00 | 0.15 | 0.03 | 0.83 | −1.05 / −0.02 | 0.00 |
| mixed (0.3 / 1) | 0.97 / 1.00 | 0.96 / 1.00 | 0.53 / 0.46 | 0.26 / 0.30 | 0.40 / 0.47 | 0.04 / −0.55 | 0.05 / 0.00 |

- **(a)** P0(a) passes: the relabel null has size 0.04. Q_spont keeps size ≤ 0.10 under sorted composition.
- **(b)** P0(b) partly passes. The shares separate the worlds. In the mixed world they come out near equal thirds (f_comp 0.46–0.53, f_field 0.26–0.30, f_spont 0.40–0.47). A finite room also carries *chance* composition, so f_comp is large when the room effect is small (0.55 at ρ 0.1 in the pure spontaneous world). Shares are read only where Q has p < 0.05.
- **(c)** P0(c) passes only at ρ = 1: the mover rule passes in 93% of spontaneous worlds at ρ = 1 and in 45% at ρ 0.3. Carried and composition worlds never pass it, so a P5 pass is informative; a P5 failure at ρ < 1 is weak evidence. φ is read only when the stayers' native contrast C is significant (`C_post_p` < 0.05; a stayer-relabel null, added here). Under the null C is significant in 4% of cases.
- **Null fix (O7):** with independent relabels in the two periods, R had a positive bias (median 0.15 in null worlds). The reason is that the leftover agent constant is shared by both periods. R now uses a **joint relabel** (an agent present in both periods keeps one pseudo-room). Its size is 0.025 in null worlds, and 0 in composition and spontaneous worlds with no planted remanence.
- No prediction or verdict rule changes.

## Results by goal period
Primary: bge style_resid, day-centred agent-day vectors; gte in brackets. Q = relabel excess (p); f = shares of the split-half room separation S.

| Period | Role | Verdict | Key numbers |
| --- | --- | --- | --- |
| [G35](goalperiod-subhypotheses/G35/README.md) | replication | mixed (corrected 2026-10-04; was supported) | Q 2.23 (p 0.012) [2.66, 0.014]; operator-message share 0.01; regime II, no f_comp or Q_res |
| [G36](goalperiod-subhypotheses/G36/README.md) | replication | mixed | Q 1.68 (p 0.12) [1.10, 0.36]; f_comp 0.36; Q_spont 1.02 (p 0.43) |
| [G37](goalperiod-subhypotheses/G37/README.md) | replication | supported | Q 2.30 (p 0.043); f_comp 0.09; Q_spont 2.55 (p 0.027) [2.75, 0.018] |
| [G38](goalperiod-subhypotheses/G38/README.md) | native | mixed | Q 6.85 (p 0.001); f_comp 0.03; f_field 0.18 vs null 0.16 (p 0.36) [0.00]; Q_spont 5.68 (p < 0.001); mover Sonnet 4.6 φ 2.04 → 1.99 (already aligned) |
| [G39](goalperiod-subhypotheses/G39/README.md) | native | mixed | Q 1.56 (p 0.069) [1.08, 0.37]; Q_spont 1.84 (p 0.016); movers φ_post 0.77 / 2.05 / −3.02 (Opus 4.6, Sonnet 4.6, GPT-5.4), native contrast marginal (p 0.04–0.06); swap-carry R_room −0.23, R_agent −0.21 (n.s.) |
| [G41](goalperiod-subhypotheses/G41/README.md) | native | supported | Q_spont 4.23 (p 0.001) [4.85]; f_spont 0.82; remanence R(#39, #41) −0.13 (z −1.6) |
| [G42](goalperiod-subhypotheses/G42/README.md) | replication | mixed | Q 1.50 (p 0.13) [2.33, 0.004]; f_comp 0.39 [0.46]; Q_spont 1.61 (p 0.069) |
| [G44](goalperiod-subhypotheses/G44/README.md) | native | mixed | Q 5.09 (p < 0.001); f_comp 0.08; f_field 0.08 vs null 0.03 (p 0.088) [0.04, 0.43]; Q_spont 5.20; mover Gemini 3.1 Pro φ −3.29 → 0.98 [0.76, 1.27], day 1 0.88 |

## Results
### Exploratory round 1 (2026-10-04; non-holdout only, asserted in the scheme)
- **Scheme:** 1,959 non-holdout agent-days (#33–#51), 41 field vectors; 0.5 MB in `data/processed/H100-room-symmetry-breaking/`.
- **Code:** `scheme/build.py`; `analysis/{h100lib,synthetic,run,summarize,period_folders,figures,confirm}.py`.
- **Numbers:** `results/raw_all.json` (4 instrument variants), `results/results.json` (verdicts and period tables), `synthetic/synthetic_summary.json`. Estimates: 64 rows in `per_period_estimates` (hypothesis H100).
- **Figures:** `figures/summary_obs.pdf` (decomposition and movers), `figures/summary_synthetic.pdf`.

**Headline.**
1. **The room difference is endogenous, not composition.** Agent constants are real (invariance r 0.49 vs null 0.14). They explain little of the room separation: f_comp 0.03–0.18 where rooms separate significantly (bge), 0.36–0.39 in the two periods where they do not. After removing composition and the measured field directions, the rooms still differ beyond random groupings in 5/7 regime-III periods (bge: #37, #38, #39, #41, #44; gte: #37, #38, #41, #42, #44).
2. **The operator field acts, but not along its text.** #38 and #44, the two periods with room-specific kickoffs, have the two largest separations (Q 6.85 and 5.09; identical-kickoff median 1.68; post hoc rank p 0.048). Their separation lies along the kickoff-text difference only at chance (f_field 0.18 vs null mean 0.16 in #38; 0.08 vs 0.03 in #44, p 0.088; gte 0.00 and 0.04). Operator messages per room carry ≤ 0.03 everywhere. The field is a trigger: the instruction changes what each room builds, and the content difference follows the work, not the words of the instruction.
3. **Spontaneous divergence without any field.** In #41 (identical kickoffs, after the NE42 merge) the rooms differ at Q_spont 4.23 (p 0.001; gte 4.85). It is the third-largest separation in the data.
4. **No remanence.** The spontaneous room-difference direction does not persist across goals: R(#39, #41) = −0.13 (z −1.6), all six consecutive pairs |z| < 2 (mean R 0.08, gte 0.11). The 04-27 swap shows neither room-carried (R_room −0.23, p 0.16) nor agent-carried (R_agent −0.21, p 0.31) persistence. Each goal breaks the symmetry anew.
5. **Movers: one adopts, one carries, one was already there.**
   - Gemini 3.1 Pro (05-25, #best → #rest): φ −3.29 → 0.98 [0.76, 1.27]; day 1 already 0.88. Composition predicts −0.20. A clean adoption within one day.
   - GPT-5.4 (04-27, #best → #rest): φ −1.27 → −3.02 on every day of #39 (gte −4.89). It keeps a #best-side position after the move (R-carry). The #39 native contrast is marginal (p 0.058), so this is suggestive.
   - Sonnet 4.6 (04-02, #rest → #best): φ_pre is already +2.04 (pre contrast p 0.010) and stays at 1.99. It sat on the #best side of #37 before the operator moved it: selection or anticipation, not adoption.
   - Opus 4.6 and Sonnet 4.6 (04-27): φ_post 0.77 and 2.05, but the native contrast is marginal and the day-bootstrap CIs are wide.
   - By the P5 rule: 3/5 pass in bge, 2/5 in gte.

**Synthetic validation (axis F):** see Amendment 1 (null size 0.04; shares recover the five worlds; mover power 0.93 at ρ = 1, 0.45 at ρ = 0.3).

**Outcome vs prediction**

| | Prediction (locked) | Outcome | Verdict |
| --- | --- | --- | --- |
| P0 | (a) Q size ≤ 0.07; (b) shares ± 0.15; (c) mover power ≥ 0.8 at ρ = 1 | 0.04; shares separate worlds, mixed world approximate; 0.93 at ρ = 1 (0.45 at 0.3) | (a), (c) passed; (b) partial |
| P1 | Q > 1, p < 0.05 in ≥ 6/8 | bge 5/8, gte 6/8 | mixed |
| P2 | f_comp ≤ 0.3 in ≥ 2/3 (both models); constants invariant | where Q is significant: bge 4/4, gte 4/5; all regime-III periods: bge 5/7, gte 4/7; invariance passed | passed (on separating periods) |
| P3 | f_field ≥ 0.15 and > null in #38, #44; operator share ≤ 0.1 elsewhere | #38 0.18 (null 0.16, p 0.36), #44 0.08 (p 0.088); gte 0.00, 0.04; elsewhere ≤ 0.03 | **failed** (first clause) |
| P4 | Q_spont p < 0.05 in ≥ 3/5 identical periods; f_spont ≥ 0.5 in ≥ 3/5; #41 p < 0.01 | 3/5 (both models); 5/5; #41 p 0.001 | passed |
| P5 | ≥ 3/5 movers φ_post ≥ 0.5 and − φ_comp ≥ 0.5; φ_pre ≤ 0 in ≥ 3/5; day-1 ≥ 0.5 in ≥ 3/5 | bge 3/5, gte 2/5; 4/5; 4/5 | mixed (one carried mover, one pre-aligned) |
| P6 | R(#39, #41) |z| < 2; mean R within ± 0.15 | z −1.6 (gte −1.1); mean 0.08 (0.11) | passed |
| P7 | R_room, R_agent within null | both n.s. (both models) | passed |
| HH66 | explicit + spontaneous parts; spontaneous part held by the room | spontaneous part exists and dominates; explicit part not a direction; room holds it only within a goal | **mixed** |

**What this means.**
1. In vector-spin terms, each goal is a quench that breaks the #best/#rest symmetry again. With identical kickoffs the room difference points along a direction no field sets, and it does not survive the next quench. That is spontaneous symmetry breaking without memory.
2. The operator's room instruction is a symmetry-breaking *trigger* of large amplitude (about twice the separation). It is not a static field that content aligns to.
3. Composition hardly matters: the same agents regrouped give a random-grouping separation.
4. Whether a room holds its divergence against a membership change is unresolved. One of two readable movers adopts the new room within a day, and one keeps its old position, plausibly because it kept its old project (H58/H70: agent + own artifact).

**Operator-facing conclusion.**
- Splitting a swarm into rooms with identical instructions still produces two content domains (Q_spont 1.8–4.2 in 3/5 periods). Different instructions about double the separation (Q 5–7), but do not expect the content difference to look like the instruction text.
- A moved agent can align with its new room by its first day, or keep its old room's work for a week. Check what the agent is working on, not only which room it is in.
- Room identity does not carry over goals: reassemble the rooms however you like at a goal change; nothing persists.

**Caveats.**
- **Few movers.** Five moves, all at goal starts; the native contrast is marginal at 04-27, and mover power is 0.45 at ρ = 0.3.
- **Field direction proxy.** The field is measured as the whitened kickoff-text direction. A failed P3 says the content does not follow the text direction; it does not say the instruction had no effect (Headline 2).
- **Endogenous ≠ coupling.** f_spont includes room-specific drives the members create (shared repos, the RPG forks). Coupling vs a self-made room drive is not separated (open convergence impostor).
- **Short periods.** 3–17 days; #36 uses 4 regime-III days.
- **Post hoc items:** the fielded-vs-identical ranking of Q, the "trigger" reading, and the per-mover narratives (pre-alignment, carry).

### Confirmatory design (written 2026-10-04 after exploration; not run)
`analysis/confirm.py`, frozen predictions in the script header:
- **C1 (NE19 mover):** Claude Opus 4.7 (#best → #rest, 06-01) has φ_pre ≤ 0 in #44 and φ_post ≥ 0.5 in #45, with φ_post − φ_comp ≥ 0.5, if the #45 native contrast is significant (p < 0.05) [0.5].
- **C2 (spontaneous part):** in every held-out two-room period among #45–#48 with ≥ 3 agents per room, Q_spont > 1 with p < 0.05 in ≥ half [0.6].
- **C3 (no field direction):** where room kickoffs differ (whitened cos < 0.95), f_field stays within the direction null (p > 0.05) [0.6].
- **C4 (no remanence):** R between consecutive held-out two-room periods with the same partition has |z| < 2 [0.65].
- **Safeguards:** refuses without `--confirm --i-understand-this-uses-the-locked-holdout`; refuses unless the card, the script, `h100lib.py`, `run.py` and `scheme/build.py` are committed and unmodified; calls `holdout_ledger.check()` per target. `--dry-run` runs on non-holdout stand-ins (the 05-25 move, #41, #42, #44) and asserts that no held-out row is loaded.
- **Reuse disclosure (`../holdout.md`):** #45–#48 content is planned by many hypotheses (H23, H26, H47, H81–H83 and others); NE19 (#45) is H23's and H65's target. H100's statistic (room separation decomposition; one mover's φ) is new, but #45's content is a shared modality. Disclose before running.

## Round 2 redirects
**What the direction is really after:** whether a room is an order parameter of its own (a domain that holds content independent of its members and its instructions), and what an operator's room assignment does to content.
- **H100-R1. Confirm on NE19** (`confirm.py` C1) and the held-out two-room weeks.
- **H100-R2. Read-out mechanism for movers.** Does a mover's content move toward new-room messages it *read* more than toward new-room messages posted before it arrived (matched age)? This closes the convergence impostor and separates coupling from a self-made room drive.
- **H100-R3. The field as work, not text.** Replace the kickoff-text direction with the room's DQ4 work (repo labels): a Potts field on projects. Then f_field measures whether instructions act through what the room builds.
- **H100-R4. GPT-5.4's carry and Sonnet 4.6's pre-alignment.** Check DQ4 commits and ledger reads: did GPT-5.4 keep committing to #best repos after 04-27, and did Sonnet 4.6 read or work with #best during #37?
- **H100-R5. Coordination with H81–H83** (composition, remanence, enculturation): the same agent constants and the same "no remanence" reading at village level.

## Notes
- 2026-10-04 ~20:25 UTC: card, observables, nulls and predictions written by the H100 round-1 agent, before any H100 statistic on real data.
- ~20:28 UTC: scheme built; period folders written with their dated predictions. ~20:28–20:40: synthetic validation; Amendment 1 (~20:40) before the real-data run.
- ~20:41 UTC: real-data run. One addition after seeing results (labelled): the pre-move native contrast significance (`C_pre_z`), computed because φ_pre of the 04-02 mover was positive. It does not change any verdict rule.
- Suggested shared changes (not made; outside edit scope): DEFINITIONS entries for *room separation S, relabel excess Q, shares f_comp/f_field/f_spont, mover index φ, room remanence R*; a vector-spins pitfall ("room relabel nulls across two periods need a joint relabel when agent constants are removed imperfectly"); a natural-experiments note listing the non-holdout operator moves (04-02, 04-27, 05-25) with mover names; `rooms_timeline`-based "room of each statement" helper for `infra/shared/` (H100 and H102 both need it).
- 2026-10-04: **Correction (2026-10-04, blind-rater check): G35 verdict supported → mixed.** The replication rule needs Q_res > 1 (p < 0.05) and f_comp < 0.5. Regime II (#35) has neither, because agent constants use the regime-III basis. `summarize.py` had graded #35 on Q alone. Q (2.23, p 0.012) does not remove composition, so the rule gives mixed. The code branch is fixed, and the period README and results table are updated. Card-level verdicts (P1–P7, HH66 mixed) do not change: P1 counts Q, which is unchanged, and the decomposition claims use regime III only. Period verdicts are now 2 supported (G37, G41), 6 mixed.
