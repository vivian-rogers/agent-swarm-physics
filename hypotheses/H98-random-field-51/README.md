# H98: #51 is a random-field system

**Status:** exploratory round 1 done (2026-10-04; non-holdout only). **Failed as posed by the pre-registered rule (P3); the random-field part stands, and the niche acts through conversation.**
- **#51 is random-field dominated (P1, supported).** After style removal the random-field share of the static configuration is R = 0.67–0.73 in the five counted #51 units and 0.24–0.53 in the shared-goal weeks #38–#41 (both embedding models). Without style removal the contrast weeks rise to 0.74–0.79: their agent-level disorder is mostly style.
- **Weak positive pull (P2, mixed).** b_ex = 0.23–0.31 in 5/5 #51 units (day-bootstrap CI > 0), far from the mean-field instability; one contrast week (#41) reaches 0.55.
- **Not the independent-agent overlap distribution (P3, failed in 2/5 units).** P(q) is unimodal everywhere (BC 0.20–0.51), but day-to-day overlaps are synchronized beyond the shift null in 51d (W 3.0, p 0.007) and 51g (W 1.6, p 0.048), in both models. Post hoc: one low-signal day (Kimi K3's join day) and a slow common drift, not two-state switching.
- **Rivals co-move because they share a niche, but the niche acts through conversation (P4 bge only; P5 failed).** The slope of co-movement on squared role-text overlap, fitted on non-rival pairs, predicts the rival excess (pooled β_n 0.064 [0.009, 0.118]; gap G −0.034 [−0.095, 0.028]). It is null in gte (0.010 [−0.056, 0.076]). Reads and replies remove 70% of it (0.084 → 0.025).
- Natives: NE32 untestable (isolated newcomers were silent); #focus split mixed (one mover's pull 0.42 → 0.01, the other unchanged); NE33 failed (joiners take their role field over days, not on day 1: own-role percentile 0.57 vs 0.83).
- Scorecard A1 B1 C1 D1 E1 F1 G1 H1 I0. `analysis/confirm.py` (#51 tail) frozen, guarded and dry-run; **not run**.
**Question served (GOALS.md):** **Q2** (what is field and what is coupling?): in #51 the private roles are quenched random fields and the room is a weak mean-field coupling. Q3 second: the RF picture predicts no collective order and no collective switching.
**Fields:** stat mech, sociophysics
**Literature:** no note in `literature/` covers random-field models. Cited from memory (†, not in `literature/`): Imry & Ma, *PRL* 35, 1399 (1975)† (random fields destroy order in low dimension); Schneider & Pytte, *PRB* 15, 1519 (1977)† and Aharony, *PRB* 18, 3318 (1978)† (mean-field RFIM phase diagram; Gaussian fields order at T = 0 only when Δ/J < √(2/π)); Mattis, *Phys. Lett. A* 56, 421 (1976)† (gauge ferromagnet); Mézard, Parisi & Virasoro, *Spin Glass Theory and Beyond* (1987)† (overlap distribution P(q)).
**Definitions used** (`physics-models/DEFINITIONS.md`): Agent; Population N(t); Regime (III only; whitening per regime); Driving / external field; Agent state, variant vector, in H01's named form **agent state (vector), whitened statement mean**; H22's **coupling (content co-movement, within-day)** J^c and **overlap (day-to-day content)** q(d, d′) (proposed by H22, used unchanged); H37's **stance coupling (residual)** (here the H22 round-1b soft form); Exposure (turn read-out) via `pair_day_reads`. **New named variants proposed for DEFINITIONS.md** (not edited here; outside this card's scope), defined under Observables: *random field (static agent field)*, *disorder ratio R*, *mean-field gain b*, *niche overlap (role text)*.
**From:** HH129 in `hypotheses/hypohypotheses/HYPOHYPOTHESES.md` · **Models:** `physics-models/01-inverse-ising/` (random-field Ising, mean-field forward version), `physics-models/11-vector-spins/` (content as O(n) spins)
**Data inputs (shared tables first):** DQ5 `embeddings/agent_{day,win30}_{style_resid_period,white32}_{bge_small,gte_modernbert}.npy` with `agent_day.parquet` / `agent_win30.parquet`; statement-level `statements_{style_resid_period32,white32}_<model>.npy` (time-split halves); `goal_vectors(_gte_modernbert).npy` + `goals.parquet` (`agent_goal` rows = role texts) whitened with the regime-III whitener of the same model; DQ6 `ground_truth_labels` (`preferred & ~holdout`: roles, rival and opposed pairs, room assignments); DQ2 `reply_pairs` (stance); `pair_day_reads`; `rooms_timeline`; `period_units`; `roster` (lab); `calendar`.

## Source HH (verbatim from the HH list, including refinements)
#51 is a random-field system. Private roles pin each agent's topic (a random field), and the shared room adds a weak positive mean-field pull. Rivals co-move because they share a niche (H22). A random-field Ising/O(n) model predicts the overlap distribution and the absence of collective switching. *Check:* fit random-field mean-field to #51's content (field from role text, coupling from co-movement); predict the day-to-day overlap and synchrony H22 measured.
  *Models:* 01 (random-field Ising), 11 · *Periods:* #51 non-holdout segments

## Question
H22 refuted the spin glass in #51 and, post hoc, described a random-field system with weak positive coupling. Does an explicit mean-field random-field model, fitted per unit, (i) place #51 deep in the disorder-dominated phase, unlike shared-goal weeks; (ii) predict the day-to-day overlap distribution P(q) and the absence of collective switching; and (iii) explain H22's rival homophily as a niche effect: rivals co-move because their role fields point the same way, not because they couple to each other?

## Design: two layers (STANDARDS §4)
- **Replication (layer 1, role `replication`).** The common estimators (disorder ratio R, mean-field gain b, overlap distribution P(q) and synchrony W) on every eligible non-holdout regime-III unit of `period_units` with ≥ 4 days: #51 units 51c, 51d, 51f, 51g, 51h, and the shared-goal contrast units 38a, 39, 40, 41. The niche test (P3–P5) needs roles, so it runs on #51 units only, with ≥ 3 days (51a, 51c, 51d, 51e, 51f, 51g, 51h). Each unit is one point on a (R, b) phase diagram.
- **Natives (layer 2, role `native`), each with its own dated prediction in its folder:**
  - **NE32** (`goalperiod-subhypotheses/NE32/`): on 07-09 three newcomers (forecaster, YouTuber, diplomat), each a same-role rival of an incumbent, worked in isolated rooms and could not read their rivals. A field shows up without reading; a coupling needs it.
  - **G51 room split** (`goalperiod-subhypotheses/G51/`, native section): on 08-05 two agents moved to #focus. A room-routed mean-field pull should fall for them while their static fields stay.

## Model
**From:** `physics-models/01-inverse-ising` (mean-field forward version; random-field Ising) and `physics-models/11-vector-spins` (O(n) content spins).

**H98 variant: Gaussian mean-field random-field O(n) model with a niche-filtered common drive.** Agent i's content state on day d is the unit vector s_id (n = 32):

  s_id ∝ h_i + J m_{−i,d} + g_d + z_id + ε_id

- h_i: the **quenched random field** (role, family, prior). Its role part is a_r r̂_i, with r̂_i the whitened role-text vector.
- m_{−i,d}: the mean state of the other agents in i's room (mean-field coupling J; the "weak positive pull").
- g_d: the common exogenous day field (village events, operator).
- z_id: slow per-agent drift (AR(1) over days: project changes); ε_id: sampling noise.
- **Window level (within day):** fluctuations x_iw respond to a shared window drive η_w through a niche filter, x_iw ≈ (α P_i + β) η_w + ξ_iw, with P_i the projector on i's field direction. Pair co-movement then grows with niche overlap: E⟨x_i, x_j⟩ ∝ α²(ĥ_i·ĥ_j)² + 2αβ(ĥ_i·ĥ_j)² + nβ². **Rivals co-move because ĥ_i ≈ ĥ_j**, with no direct i–j term.

**Phases (mean field).** For Ising spins with Gaussian fields of width Δ the T = 0 ferromagnet exists only for Δ/J < √(2/π)†. In the linear (spherical) version the ordering instability is at gain b = Jχ₀ → 1. The RF picture predicts #51 sits far on the disordered side: static positions are frozen by fields (q_EA > 0) while the swarm has one state, no domains and no collective switching. Order without coupling (frozen positions) is the Imry–Ma point: freezing alone is not evidence of a glass.

**Rivals (named):**
- **R1 spin glass** (H22): random-sign couplings, broad P(q). Refuted in H22; P(q) shape re-tested here.
- **R2 collective switching / metastable ferromagnet:** a bimodal or excess-variance P(q), W > 1.
- **R3 direct rival coupling** (rivals read and answer each other): rival co-movement carried by pair reading and replies, not by niche overlap.
- **R4 common drive only (paramagnet, J = 0):** no room-specific pull (tested in the G51 room-split native).

## Data scheme (`scheme/`)
`scheme/build.py` reads shared tables only and asserts the holdout twice (`calendar.holdout` and `common.holdout_mask`). It writes codes and vectors only, no text.
- **Units:** shared `period_units` (regime III, non-holdout). Replication units ≥ 4 days; niche units ≥ 3 days.
- **Agent-day states:** rows of `agent_day.parquet` in the unit with n_chat + n_intent ≥ 3; vectors from `agent_day_<variant>_<model>.npy`, unit-normalized. **Primary variant:** `style_resid_period`, bge (role claims; STANDARDS §2). Variants: `white32`; gte.
- **Half-split states** (for q_self): statements (`statements.parquet`, chat + intent) of an agent-day split at the median statement time; each half averaged from `statements_<variant>32_<model>.npy` (≥ 2 statements per half).
- **Window states:** `agent_win30` rows with ≥ 2 statements; vectors from `agent_win30_<variant>_<model>.npy`, unit-normalized.
- **Role vectors** (#51): `agent_goal` rows of `goals.parquet`, whitened with the model's regime-III whitener (d = 32), unit-normalized. Opus 5 (agent 40) has a stored vector for its second role (mathematician) only; its first role (game dev, 07-24 → 07-29, DQ6) gets the mean of the two incumbent game-dev role vectors (flagged). Agents without a role in a unit are not in the niche tests.
- **Pair covariates:** same lab (`roster`); DQ6 rival (SR) and opposed (OP) pairs time-bounded by `t_valid_from/to`; mean log(1 + ledger reads per day) from `pair_day_reads` (both directions); DQ2 reply intensity (Σ p_reply over `pair_set = cand`, labelled, agent → agent, both directions, per pair-day, log1p).
- **Output:** `data/processed/H98-random-field-51/<unit>/` (`agent_day.parquet` + `S_<variant>_<model>.npy`, `halves.parquet` + arrays, `win.parquet` + arrays, `pairs.parquet`), `roles_<model>.npy`, `results/`, `synthetic/`, `_provenance.json`. Budget ≤ 100 MB.
- **Regimes covered:** III only (36b on). #51 units 51a–51l; contrast units 38a, 39, 40, 41.

## Observables
*Written 2026-10-04 20:23 UTC, before any H98 statistic.*

**O1. Random field and disorder ratio R.** Per unit, agents with ≥ 2 states. Static field φ_i = mean_d s_id; unit mean μ̄ = mean_i φ_i.
- Random-field variance (bias-corrected): Δ² = mean_i |φ_i − μ̄|² − mean_i σ_i²/D_i, with σ_i² the within-agent day variance and D_i its day count.
- Uniform-field strength: M² = |μ̄|² − (Δ² + mean_i σ_i²/D_i)/N.
- **Disorder ratio R = Δ²/(Δ² + M²)**: 1 = pure random field, 0 = pure uniform (goal) field. Agent-bootstrap 95% CI.
- **Role share of the random field** (#51): scalar gain a from (φ_i − μ̄) ≈ a (r̂_i − r̄); R²_role = 1 − Σ|φ_i − μ̄ − a(r̂_i − r̄)|² / Σ|φ_i − μ̄|². Null: role vectors permuted across agents (2,000).

**O2. Mean-field gain b.** Window states, agent-day centered: x_iw = v_iw − mean_{w′∈d} v_iw′ (removes static and day fields). m_{−i,w} = mean of the other agents' x in w (same room in multi-room units).
- b = Σ_{i,w}⟨x_iw, m_{−i,w}⟩ / Σ_{i,w}|m_{−i,w}|².
- **Cross-day surrogate:** the same with i's day d paired with the others' day e ≠ d at the same window index (H22). b_ex = b − b_surr.
- Day-bootstrap 95% CI. b_ex contains any common window drive (an upper bound on J), and noise in m attenuates it (a lower bound). Read it as "the size of the pull", not as J.

**O3. Overlap distribution P(q) and synchrony** (H22's O6 estimator, units with ≥ 4 days).
- δ_id = s_id − m_d (day field removed), unit-normalized; q(d, d′) = mean over agents present both days of δ̂_id·δ̂_id′, using time-split halves (half 1 of d with half 2 of d′; q_self(d) from the halves of one day).
- P(q): the pooled q(d, d′), d < d′. Reported: mean q̄, SD, skewness, bimodality coefficient BC (> 0.555 suggests bimodality).
- **RF prediction for P(q):** the distribution of q(d, d′) when each agent's sequence of days is circularly shifted independently (2,000 shifts). This keeps each agent's field and drift and removes synchrony: the independent-agent random-field model. **W_P = Var_obs(q)/mean Var_null(q)**; H22's lag-residualized **W** is reported next to it.
- q_∞ (mean q at lags ≥ D/2) and memory M = (q̄(1) − q_∞)/(q̄_self − q_∞), descriptive (H22).

**O4. Niche test** (#51 units with ≥ 3 days). J^c_ij: H22's content co-movement (window states, agent-day centered, correlation r_ij over shared windows minus the cross-day surrogate), pairs with ≥ 10 shared windows (≥ 5 in 3-day units).
- **Niche overlap** n_ij = cos(r̂_i − r̄, r̂_j − r̄) of centered role vectors (exogenous: from role text only).
- **Niche slope β_n:** OLS of J^c on n_ij, same-lab and the read covariate, fitted on non-SR, non-OP pairs only. Inference: role vectors permuted across agents (2,000), refitting.
- **Predicted rival excess** T̂_SR = β_n (n̄_SR − n̄_U). Observed T_SR = mean J^c(SR) − mean J^c(U) (H22). **Mediation gap** G = T_SR − T̂_SR; agent-pair bootstrap CI (resampling agents).
- **Rival R3:** the read slope β_R and the reply slope β_Y in the same regression; the share of β_n left after both enter.
- Pooled across units by DerSimonian–Laird random effects.

**O5. Stance niche slope** (#51): J^s_ij = mean soft stance (p_supports − p_opposes, weighted by p_reply), both directions, pairs ≥ 3 replies (H22 round 1b). β_s = slope of J^s on n_ij over non-SR pairs. Mean J^s.

**O6. Phase diagram (cross-unit, descriptive).** Each replication unit is a point (R, b_ex) with CIs. #51 units vs contrast units.

**Multiplicity.** P1–P5 are the primary predictions; the variants (white32, gte) and O5 are secondary. Per-unit verdicts are counts; cross-unit summaries are random-effects.

## Null / baseline
- **Cross-day surrogate** (O2, O4): removes time-of-day-locked drives; defines b = 0 and J^c = 0 (H22).
- **Per-agent circular day shift** (O3): the independent-agent random-field model (keeps each agent's field and drift; removes synchrony). DQ8 note: synthetic size of H22's W test 0.04–0.14 (mildly anti-conservative); re-sized here at #51 counts.
- **Role-vector permutation** (O1 role share, O4 β_n): role texts reassigned across agents.
- **Agent bootstrap** (R, G) and **day bootstrap** (b).
- **Synthetic worlds at real counts** (axis F, before real data): RF paramagnet with niche-filtered drive (H98); RF + direct rival coupling (R3); RF + collective switching (R2); pure uniform field (shared-goal week).

## Impostors (STANDARDS §1)
| Impostor | Relevant? | How H98 removes it | Status |
| --- | --- | --- | --- |
| Scheduler field | partly | Content states, not activity timing. The cross-day surrogate removes time-of-day-locked drives in b and J^c; agent-day centering removes day-level states. No activity synchrony statistic is used. | removed (for content) |
| Exogenous field (kickoff, goal, operator) | yes | The model names it: the day field g_d is removed in q (δ = s − m_d) and in b, J^c (agent-day centering). The window-level common drive stays in b (upper bound) and is the niche model's driver. Role texts are the measured exogenous random field. R4 (common drive only) is tested by the room-split native. | partly |
| Shared model priors | yes | Primary vectors are `style_resid_period` (removes H13's family field); same-lab covariate in the pair regression; R uses agent fields that include priors, so R is reported with and without style residualization. | removed (pairs); partly (R) |
| Contemporaneous convergence | yes | The niche model *is* a shared-field account of co-movement, so the test is whether co-movement needs reading: the read and reply covariates (R3), and the NE32 isolation native, where rivals cannot read each other. | partly |

## Faithfulness scorecard
Scored per model, mapping and window; 0 = not done or failed, 1 = partial, 2 = passed. Scheme and promotion thresholds: `writeup/paper.tex`, Sec. "Assessing model faithfulness".
**Rival models:** R1 spin glass (H22); R2 collective switching; R3 direct rival coupling (reading / replies); R4 common drive only.
**Locked holdout used for confirmation:** none yet. `analysis/confirm.py` (the #51 tail, 09-07 → 09-21) is written, frozen (C1 threshold R > 0.531) and guarded (`--confirm` + `H98_CONFIRM=1` + `holdout_ledger.check`); dry run on the 51g stand-in reproduces round 1 (C1, C3, C5 pass; C2, C4 fail). **Not run.** Reuse: H22's `confirm_tail.py` tests T_SR on the same co-movement estimator; disclose whichever runs second.
**Overall A–I:** A1 B1 C1 D1 E1 F1 G1 H1 I0.

| Axis | Test | Score | Evidence |
| --- | --- | --- | --- |
| A mapping | variables defined from dataset fields; assumptions listed; invariant across families and regimes | 1 | Fields, pull and overlaps are defined from DQ5 vectors and DQ6 role texts. R depends on the reference center (A0) and on style residualization (the contrast ordering holds only after style removal). |
| B assumptions | stationarity, Markov order, time-rescaling, update-order audit | 1 | Day-level stationarity is assumed; W shows non-stationary days in 51d and 51g. No Markov-order test. |
| C adequacy | beats the null hierarchy, day-blocked held-out data | 1 | R ordering and b_ex beat their references (b_ex vs cross-day surrogate in 5/5 units). The independent-agent P(q) is rejected in 2/5 units. |
| D unfitted predictions | unfitted statistics and the model's signature | 1 | The non-rival niche slope predicts the rival excess (G ≈ 0, bge); P(q) unimodal as predicted. Fails in gte and in W. |
| E interventional | predicts the change across a natural experiment | 1 | #focus split: one mover's pull vanishes (0.42 → 0.01), the other's does not; NE33 failed; NE32 untestable. |
| F identifiability | synthetic recovery with village sampling; robust to preprocessing | 1 | Synthetic at real counts: R bias ≤ 0.02; W size ≤ 0.10, power 0.8–1.0; the squared-niche test separates four worlds. Not robust to the embedding swap (niche) or to style removal (R ordering). |
| G ground truth | agrees with known structure | 1 | DQ6 role texts explain 5–14% of the random field (p ≤ 0.001, 7/7); incumbents' own-role percentile 0.83. |
| H comparative | beats the named rivals | 1 | Beats R1 (spin glass: P(q) unimodal, BC ≤ 0.51) and R4 for one mover. Loses partly to R3: reads and replies absorb 70% of the niche slope. R2 (synchronized days) is present in 2/5 units. |
| I transfer | holds in other same-mode periods, including the holdout | 0 | No other private-role period; holdout not run. |

## Prediction
*Written 2026-10-04 20:23 UTC, before any H98 statistic on real data.* **Seen beforehand:** H22's full card (round 1 and 1b: T_SR ≈ +0.05, κ̂ 4–10, q_∞ 0.41–0.54, M 0.5–0.75, W ≈ 1 except gte 51c 1.61; NE38 coupling DiD −0.27 / −0.13, n.s.), H54 (#51 role-swap accuracy 0.95), H21, H64, H11, H53, H63, H66, H77/H78 headlines; the #51 role and rival tables (DQ6); agent-day counts (#51: 1,506 agent-days, median 15 chat and 19.5 intention statements); the `period_units` list. **Not seen:** any R, b, P(q) on the shared units, any role-vector or niche statistic, any read or reply covariate.

| # | Prediction (primary unless marked) | Counts against | Credence |
| --- | --- | --- | --- |
| P1 | **#51 is random-field dominated.** R in every counted #51 unit (51c, 51d, 51f, 51g, 51h) exceeds R in every contrast unit (38a, 39, 40, 41), and the #51 random-effects mean R ≥ 0.6. | any contrast unit above any #51 unit, or #51 mean R < 0.4 | 0.6 |
| P2 | **Weak positive pull.** b_ex > 0 (day-bootstrap CI above 0) in ≥ 3/5 counted #51 units, and b_ex < 0.5 in every unit (far from the mean-field instability b = 1). | b_ex CI including 0 in ≥ 3/5, or any b_ex ≥ 0.5 | 0.55 |
| P3 | **P(q) is the independent-agent RF distribution.** In each counted #51 unit: W_P inside the shift null's central 90% band, BC < 0.555 (unimodal), and q̄ inside the null's band. | W_P above the band (collective switching, R2) or BC > 0.555 in ≥ 2 units | 0.6 |
| P4 | **Rivals co-move because they share a niche.** Pooled β_n > 0 (role-permutation p < 0.05 in the RE pool), and the mediation gap G includes 0 while T̂_SR > 0: the niche slope fitted on non-rival pairs predicts the rival excess. | β_n ≤ 0, or G > 0 with CI excluding 0 (rivals co-move beyond their niche) | 0.35 |
| P5 | **Not a direct coupling (R3).** Adding the read and reply covariates leaves ≥ 70% of β_n; β_R and β_Y do not absorb the rival excess (T_SR adjusted for reads and replies stays ≥ 70% of unadjusted). | β_n falls by > 30% when reads/replies enter, or T_SR vanishes with them | 0.5 |
| P6 (secondary) | **Stance stays ferromagnetic across niches.** Mean J^s > 0 in every #51 unit with ≥ 20 stance pairs, and β_s ≥ 0 (niche overlap does not produce opposition). | β_s < 0 with CI excluding 0 | 0.7 |
| P7 (secondary) | **Role text is a measurable part of the random field.** R²_role > 0 with role-permutation p < 0.05 in ≥ 3 #51 units. | p ≥ 0.05 in ≥ 4 of the niche units | 0.75 |

**Verdict rule (per #51 unit):** *supported* if P1's ordering holds for the unit, P3 passes, and the unit's β_n > 0; *failed* if P3 fails toward R2 (W_P above the band) or β_n < 0; *mixed* otherwise; *descriptive* for contrast units (they place points on the phase diagram). **Hypothesis level:** supported if P1, P3 and P4 pass; failed if P3 fails in ≥ 2 units or P4 fails with G > 0 (rivals co-move beyond niche: R3 territory).

**Amendment A0 (2026-10-04 20:29 UTC, before any H98 statistic; definitional).** The regime-III whitener is fitted on non-holdout regime-III statements, most of which are #51's. #51's mean therefore sits near the whitening center, and M² = |μ̄|² would be small for #51 by construction. **M² is measured from a leave-own-period-out reference:** c_ref = the equal-weight mean of the other regime-III non-holdout goal periods' agent-day means (#36–#44 and #51, one vector per period), and M² = |μ̄ − c_ref|² − (Δ² + mean σ²/D)/N. Agent-day states first have their day field replaced by the unit mean (s′_id = s_id − m_d + mean_d m_d), so unequal presence across days does not leak the day field into the static fields. The P1 thresholds are unchanged. The raw-center R is reported as a variant only.

**Amendment A1 (2026-10-04 20:45 UTC, after the synthetic validation, before any real-data statistic).** Synthetic worlds keep each unit's real agents, agent-days, halves, windows, rooms, DQ6 rival pairs and real role vectors; only the content vectors are synthetic (`analysis/synthetic.py`; `data/processed/H98-random-field-51/synthetic/{summary.json, niche_A1.json}`; 20 replicates per world and unit). Findings and the changes they force:
1. **R is recovered.** Bias ≤ 0.02 at R = 0.8 (SD 0.02–0.05 per unit); +0.05 to +0.08 at R = 0.15. The P1 ordering is identifiable.
2. **The pooled P(q) variance W_P and the q̄ band are anti-conservative.** Under independent agents with AR(1) drift, W_P exceeds the shift null's band in 10–45% of runs, because the circular shift breaks the lag structure. H22's lag-residualized **W** has size 0.00–0.10 (p_W < 0.05) and power 0.80–1.00 against collective switching (R2). **P3's primary statistic becomes W (p_W ≥ 0.05 = no collective switching).** BC keeps its rule (size ≤ 0.05; power 0.45 at 5 days, 1.00 at 13 days). W_P and the q̄ band become descriptive.
3. **The card's window formula had a slip, and the linear niche regressor has no power.** The model gives E⟨x_i, x_j⟩ ∝ α² n_ij² + 2αβ + nβ²: co-movement depends on the *squared* niche overlap. With the linear n_ij, β_n > 0 in 0/20 pooled runs even in the H98 world. **P4–P5 use s_ij = n_ij² as the niche regressor** (linear n is a variant). At H22-sized rival excess (T_SR ≈ 0.05): H98 world: β_n > 0 in 20/20 and G includes 0 in 20/20; direct-coupling world (R3): β_n > 0 in 0/20 and G > 0 in 20/20; mixed world: β_n > 0 in 20/20 and G > 0 in 17/20; null world: β_n > 0 in 0/20 and G > 0 in 0/20.
4. **Per-unit role permutation is anti-conservative** for β_n: size 0.26, from the leverage of permuted near-identical rival vectors. **Primary inference is the RE pool of leave-one-agent-out jackknife SEs** (pooled size 0/20); per-unit permutation p is descriptive.
5. **The gain b reads J/(1 − J) plus any common window drive.** A planted pull J = 0.3 gives b_ex ≈ 0.50. A world with no pull but a common window drive gives 0.14–0.29. P2's threshold b_ex < 0.5 therefore means J below ≈ 0.3 even with no drive.

**Natives:** predictions are in `goalperiod-subhypotheses/NE32/README.md` and in the G51 folder's native section, written before those runs.

## Results by goal period
| Period | Role | Verdict | Key numbers |
| --- | --- | --- | --- |
Primary variant `style_resid_period` × bge. Per-unit rule: *supported* = P1 ordering, P3 pass and β_n > 0; *failed* = P3 fails (W, p < 0.05) or β_n < 0.

| Period | Role | Verdict | Key numbers |
| --- | --- | --- | --- |
| [G51](goalperiod-subhypotheses/G51/README.md) | replication (5 counted units, 2 niche-only) + native (#focus split) | mixed (3 supported: 51c, 51f, 51h; 2 failed: 51d, 51g); native mixed | R 0.67–0.73; b_ex 0.23–0.31; W 1.90 / 3.05 / 0.73 / 1.61 / 0.88 (p 0.09 / 0.007 / 0.62 / 0.048 / 0.45); β_n pooled 0.064 [0.009, 0.118]; G −0.034 [−0.095, 0.028] |
| [G38](goalperiod-subhypotheses/G38/README.md) | replication (contrast, 38a) | descriptive | R 0.42 [0.29, 0.47]; b_ex 0.30; W 3.0 (two rooms) |
| [G39](goalperiod-subhypotheses/G39/README.md) | replication (contrast) | descriptive | R 0.52 [0.35, 0.60]; b_ex 0.05; W 0.88 |
| [G40](goalperiod-subhypotheses/G40/README.md) | replication (contrast) | descriptive | R 0.24 [0.11, 0.33]; b_ex 0.45; W 0.54 |
| [G41](goalperiod-subhypotheses/G41/README.md) | replication (contrast) | descriptive | R 0.53 [0.31, 0.68]; b_ex 0.55; W 3.35 (two rooms) |
| [NE32](goalperiod-subhypotheses/NE32/README.md) | native | n/a (untestable) | newcomers made 0–1 statements while isolated |
| [NE33](goalperiod-subhypotheses/NE33/README.md) | native | failed | joiners' own-role percentile on day 1 0.57 (p 0.30) vs incumbents 0.83 |

## Results
*Exploratory round 1, 2026-10-04 (run 20:47–21:06 UTC). Non-holdout only. Code: `scheme/build.py`, `analysis/h98lib.py`, `synthetic.py`, `run_units.py`, `natives.py`, `summarize.py`, `confirm.py`. Data: `data/processed/H98-random-field-51/results/{units.parquet, pooled.json, natives.json, niche_pairs.parquet, pq_<unit>.npy}`, `synthetic/{summary.json, niche_A1.json}`. Figure: `figures/summary_obs_col.pdf`. Estimates: 332 rows in `per_period_estimates` (`hypothesis == "H98"`).*

### Headline
#51 sits deep on the disordered side of a random-field phase diagram: after style removal, 67–73% of the static content configuration is agent-specific (random field), against 24–53% in shared-goal weeks. A weak positive pull (b_ex ≈ 0.27) acts on top. The role text explains only 5–14% of the random field (p ≤ 0.001 in 7/7 units); the rest is agent-specific content (own projects). H22's rival homophily is a niche effect: the slope of co-movement on role-text overlap among non-rivals predicts the rival excess. But the niche acts mainly by choosing conversation partners: reads and replies absorb 70% of the slope. The day-to-day overlaps are not those of independent agents in 2/5 units, which fails the pre-registered rule.

### Outcome vs prediction
| # | Prediction | Observed (primary; variants) | Outcome |
| --- | --- | --- | --- |
| P1 | R(#51) > R(every contrast unit); #51 mean ≥ 0.6 | #51 min 0.673 > contrast max 0.531; mean 0.70. gte: 0.70 > 0.54. white32: 0.77 < 0.79 (fails) | **supported** (style-residualized vectors only) |
| P2 | b_ex CI > 0 in ≥ 3/5 #51 units; b_ex < 0.5 everywhere | CI > 0 in 5/5 (0.23–0.31); #41 0.55 [0.45, 0.62] | mixed |
| P3 (A1) | W p ≥ 0.05 and BC < 0.555 in each counted unit | BC < 0.555 in 5/5; W p < 0.05 in 51d (3.05) and 51g (1.61); gte the same (3.09, 1.83) | **failed** (2/5) |
| P4 (A1) | pooled β_n > 0; G CI includes 0 with T̂ > 0 | β_n 0.064 [0.009, 0.118], p 0.022; G −0.034 [−0.095, 0.028]; T̂ 0.060 [0.009, 0.111]; gte β_n 0.010 [−0.056, 0.076] | supported (bge); failed (gte) |
| P5 | reads + replies keep ≥ 70% of β_n | 0.084 [0.024, 0.145] → 0.025 [−0.015, 0.065] (30% kept); white32 26% | **failed** |
| P6 | mean stance > 0; β_s ≥ 0 | mean soft stance 0.51–0.64 (7/7); β_s 0.019 [−0.066, 0.103] | supported (replicates H22 1b) |
| P7 | R²_role > 0, p < 0.05 in ≥ 3 units | 0.05–0.14, p ≤ 0.001 in 7/7 | supported |
| NE32 | isolated newcomers align with rivals | untestable (0–1 statements while isolated; manipulation check: 0 agent items received) | n/a |
| #focus | movers' fields unchanged; pull toward #general falls | field change at the stayers' 88th percentile (primary; 80–96th in variants); pull: agent 29 0.42 → 0.01 (lowest of all), agent 6 0.07 → 0.10 | mixed |
| NE33 | joiners' own-role percentile ≥ 0.8 on day 1 | 0.57 (p 0.30; variants 0.66–0.73) vs incumbents 0.83–0.86 | **failed** |

**Verdict.** By the card's rule the hypothesis **fails** (P3 fails in 2 units). The random-field reading of #51's static structure stands (P1, P7). The dynamic reading is wrong in two places: overlaps are synchronized on some days, and the niche effect runs through who reads and answers whom.

### Findings
1. **The village's agent-level disorder changes kind with the goal.** In shared-goal weeks most between-agent spread is style (R falls from 0.74–0.79 to 0.24–0.53 when style is residualized). In #51 it is content (R stays 0.67–0.73). This is a field-strength axis for the phase diagram.
2. **Weak pull everywhere.** b_ex ≈ 0.2–0.3 in #51 corresponds to J ≲ 0.2 in the synthetic mapping (b ≈ J/(1 − J) + common drive), far from the mean-field instability at b → 1.
3. **Unimodal P(q).** No spin-glass breadth and no bimodality (BC ≤ 0.51). The W excess in 51d comes from a day with low self-overlap (07-17: q_self 0.51, mean overlap 0.46; the Kimi K3 join day). In 51g the mean overlap drifts upward over 13 days (0.44 → 0.53). Both readings are post hoc.
4. **Niche → conversation → co-movement.** Rivals have identical role texts (n² = 1); the niche slope fitted on non-rivals (n² ≤ 0.56) extrapolates to the rival excess. Most of the slope disappears once pair reads and replies enter. DQ2 reply parents are partly content-selected (Known issues), so the reply control may over-adjust; reads alone remove ≈ 30%.
5. **Newcomers settle into their role field over days.** On day 1, joiners' content aligns with their own role less than incumbents' does (0.57 vs 0.83).

### Caveats
- The niche result is embedding-model dependent (bge yes, gte no). #51 is the least robust period across models (DQ5).
- T̂_SR extrapolates from n² ≤ 0.56 to n² = 1.
- R depends on the reference center (A0) and on style residualization; the raw-center R is 0.92–0.98 for #51 (the whitener is fitted mostly on #51).
- b_ex contains the common window drive; it bounds J from above only together with the synthetic mapping.
- The W excess is real against the calibrated null, but its source is read post hoc.
- Two natives failed or were untestable; the room-split native has two agents.

## Round 2 redirects
- **What the direction is really after:** how much of a mixed-motive swarm's structure is set by assigned roles (field), and how much by who reads whom (coupling).
- **H98-R1. Niche-selected coupling.** Model pair reading as a function of niche overlap (a "niche-gated coupling" J_ij = J₀ f(n_ij²)) and test whether co-movement given reads still depends on niche.
- **H98-R2. Day-level amplitude field.** Add a per-day signal-strength term (role-specific share of content) to the RF model and re-test W with it removed.
- **H98-R3. Settling time.** Fit the joiners' approach to their role field (days to reach the incumbents' percentile) across NE32, NE33 and the single joins.

## Notes
- 2026-10-04 20:23 UTC: round 1 started; card filled before any H98 statistic.
- 2026-10-04 20:46 UTC: timestamp correction. The first versions of this card and its native folders carried estimated times that ran ahead of the clock; all times are now corrected from file creation times (`stat`). The order of events is unchanged: card and predictions, then synthetic validation, then amendments, then real data.
- 2026-10-04 20:46–21:07 UTC: replication (16 units × 4 variants, 103 s), natives, summary, confirm dry run. The NE33 native was added at 20:50 UTC after NE32 proved untestable; its prediction was written before it ran.
- Proposed for `physics-models/DEFINITIONS.md` (not edited): *random field (static agent field)*, *disorder ratio R*, *mean-field gain b*, *niche overlap (role text)*.
