# H29: Driver nodes: where an operator message moves the whole swarm

**Status:** exploratory round 1 **done (2026-10-04): the driver-node hypothesis is not supported; a narrower post hoc finding stands.** Observables, nulls and predictions were written 2026-10-04 ~01:45 UTC, and Amendment 1 (synthetic-based) at ~02:20 UTC, both before any real-data run. Amendment 2 is **post hoc** (after the first real-data run) and labeled as such everywhere.
- **The pre-registered influence test failed in the opposite direction.** Net pull κ < 0 (CI below 0) in 7/9 counted units. Recipients' next statements move *more* toward messages posted during their own model call than toward messages they read. Two causes, both diagnosed:
  - the "invisible" set imported from H18's visibility rule is contaminated. 39–70% of it comes from call windows > 30 s (PAUSE or long tool calls), and the wake call does see those messages;
  - content similarity falls steeply with time-to-reply (co-response).
- **Post hoc: influence exists, but it is address-gated.** At matched time-to-reply (within 30 s of the call boundary), messages a recipient could see pull its next statement more than truly unseen ones, in 4/9 counted units (G39, G51b, G51c, G51d) and in both descriptive #51 segments. Like-for-like controls in the five #51 segments:
  - a message that **names** the recipient: jump 0.03–0.09 of the gap per message (CI > 0 in all five);
  - an unnamed message: 0.009–0.021, so named/unnamed ≈ 3–6×;
  - in the two-room weeks the boundary has too few rows (inconclusive).
- **No validated "where to inject" ranking.**
  - The Gramian driver score is not reproducible across halves of days (split-half median 0.05 pre-registered, 0.17 post hoc). The exception is G51b (0.87), where the score reduces to message volume (ρ 0.89).
  - Neither the driver score, volume nor out-strength predicts the held-out 2-h swarm spread (pooled ρ 0.04–0.09, CIs span 0). The spread statistic itself replicates only in G51b and G41.
  - Even in G51b, where a true model would have validated (synthetic ρ ≈ 0.29), the observed ρ is 0.05.
  - Structural controllability is uninformative (N_D ≈ N on the sparse significant graph, 1 on the dense one).
  - Steering-cost scaling is model-only: median agent ∝ N^2.7 [2.2, 3.4]; best driver flat.
- Scorecard A1 B1 C1 D0 E0 F1 G1 H0 I0. Not promoted. `analysis/confirm.py` (G47 and the #51 tail; G45 optional) written and dry-run, not run.
- **Round 1b (improved data, 2026-10-04):** on the DQ1 context-ledger visibility rule (both embedding models) the pre-registered κ is **still negative in 7/9 (bge) / 6/9 (gte) counted units**, so the round-1 failure is not mainly the contaminated placebo: messages posted during the recipient's own call are answered together with it (co-response). The matched-age boundary test replicates (CI > 0 in 4/9 bge, 5/9 gte) and **address gating is sharper**: in #51 named recipients move 0.04–0.08 of the gap per message, unnamed ones 0.00–0.013 (CI includes 0 in G51b–d under bge). **New: a reply-graph network (DQ2) gives a reproducible driver ranking** (split-half median 0.65) that weakly predicts held-out swarm spread (pooled ρ 0.23 [0.05, 0.39] bge, 0.12 [−0.06, 0.29] gte; volume ≈ 0), where the content-pull network still predicts nothing (−0.01 / 0.09). Natives: NE38 supported (the operator's reassignment moved Opus 5 strongly, 96th–100th percentile, and did not relay to bystanders); #35 mixed (designated leaders get 1.4× more replies per message, no broadcast pull, no extra volume); #26 failed (the elected leader's reply attention did not rise more than others'; its broadcast pull rose most, rank 10/10, regime I). Scorecard A1 B1 C1 D1 E1 F1 G1 H1 I0.
**Fields:** stat mech, sociophysics, info theory
**Origin:** HH110 (`../hypohypotheses/HYPOHYPOTHESES.md`; `../promotion-shortlist.md`)
**Definitions used** (`physics-models/DEFINITIONS.md`): Agent; Population N(t); Regime; Driving / external field (human messages); Agent state, variant vector (statement embedding, whitened, unit-normalized; H01's named variant at the statement level); Interaction, variant broadcast, restricted to H18's *pending set* (proposed there as "Interaction (addressed, pending-sender)"; here the unaddressed version). New terms defined under Observables and proposed for the shared file: **influence coupling (content pull)**, **driver score (mean-output Gramian)**, **net influence current (out − in strength)**.

## Standards (2026-10-04)
**Question served:** Q1 (content influence is address-gated) and Q5 (where an operator should inject).

| Impostor | Relevant? | How it was handled | Status |
| --- | --- | --- | --- |
| Scheduler field | no | Content pull at the recipient's next statement. | n/a |
| Exogenous field (kickoff/goal/operator) | yes | Field-corrected pull with a cross-day placebo (N2), a synthetic room-topic drive (N3), and NE38's operator message as a native. Goal and operator directions are not regressed out of the pull (§1). | partly |
| Shared model priors | partly | The cross-day placebo removes static style; no `style_resid`. Close with `style_resid` (§1). | partly |
| Contemporaneous convergence | yes | Strictly ledger-invisible same-call placebo and the matched-age boundary test (post hoc); co-response diagnosed (Round 1b). | removed |

**Inputs:** round 1b uses the context ledger, both embedding models and the DQ2 reply graph. Still old: no `style_resid` and no `statement_flags` dedupe.

**Two layers:** 12 replication folders (#51 in 5 units). Natives: 3 (NE38 supported, G35 mixed, G26 failed).

**Confirm script:** `confirm.py` (G47, #51 tail; G45 optional), written and dry-run, not run. Re-freeze: yes, on ledger visibility, fixed bins and leading-@ (holdout item 12). Its predictions freeze post hoc findings (Caveats).

## Question
Linearize the influence network and compute network controllability. A_ij is how much i's messages move j's next content. Compute the minimal driver set and per-agent control energy. HH110's prediction: driver nodes are high-exposure agents in small rooms, and control energy scales as N^0.6. *Check:* the observed spread of content after messages from different senders and from humans vs the predicted driver ranking.

Practical aim (usefulness-first batch): a "where to inject" ranking procedure that an operator of an LLM agent swarm could compute from logs, with a measured reliability.

## Model
**From:** `physics-models/02-nonequilibrium-ising` (linear response; directed couplings J_ij ≠ J_ji), with the vector content states of `11-vector-spins`, and linear network controllability (Liu, Slotine & Barabási, *Nature* 473, 167 (2011)†; Yan et al., *PRL* 108, 218703 (2012)†; Pasqualetti, Zampieri & Bullo, *IEEE TCNS* 1, 40 (2014)†; Gu et al., *Nat. Commun.* 6, 8414 (2015)†; Cowan et al., *PLoS ONE* 7, e38398 (2012)†; Jia et al., *Nat. Commun.* 4, 2002 (2013)†). † = not in `literature/`; cited from memory.

### H29 variant: linear content-pull dynamics (DeGroot / Friedkin–Johnsen form of model 02's linear response)
| Control theory | Village | Dataset fields |
| --- | --- | --- |
| state x_j(t) ∈ R^32 | what agent j is talking about | j's chat statements: bge-small embedding, regime-III whitener (`common.load_whitener("III", 32)`), unit-normalized |
| one update of node j | j's talk turn τ_n | `chat_core` (speaker_kind = agent) |
| inputs seen by j at τ_n | the visible set V(τ_n): others' messages that reached j after its previous call started and before this call started | `exposure` + call starts from `actions` / `events_core` (H18's visibility rule, imported) |
| edge weight a_ij | pull per message: the fraction of the gap to i's message that j's next statement closes | estimator below |
| coupling A_ij (per active hour) | a_ij × (i's messages absorbed by j per active hour) | `exposure` counts, `calendar.window_s` |
| restoring rate Γ | relaxation of an agent's content deviations toward its own field | lag-2/lag-1 autocorrelation ratio of 30-min window means (readout noise cancels) |
| input u_k | an operator message that sets agent k's content | B = e_k (H04: responses go only to the named agent) |

Per talk turn (statements e_τ = x_j(τ) + η are noisy readouts):

  x_j(τ_n) = x_j(τ_{n−1}) + Σ_{m∈V(τ_n)} a_{s(m)j} [x_m − x_j(τ_{n−1})] + γ_j [h_j − x_j(τ_{n−1})] + ξ.

Coarse-grained to active hours: dx/dt = Q x + B u, with Q_ji = A_ij and Q_jj = −Σ_i A_ij − Γ.

**Controllability quantities, single driver k (B = e_k), horizon T = 4 h (one regime-III active day):**
- mean-output reachability D_k = ∫_0^T (1ᵀ e^{Qt} e_k)² dt;
- **driver score** = D_k. The **mean-output control energy** E_k = N²/D_k is the minimum input energy to shift the swarm-mean content by one unit at T through k alone (output controllability with y = 1ᵀx/N);
- average controllability AC_k = tr W_k(T), with W_k(T) = ∫ e^{Qt} e_k e_kᵀ e^{Qᵀt} dt;
- **structural controllability** (Liu–Slotine–Barabási): N_D = max(N − |M*|, 1) from a maximum matching M* on the significant-edge graph. Driver classes (critical / intermittent / redundant) as in Jia et al. With nodal self-dynamics (Cowan et al.), N_D = the number of root strongly connected components.

### Theory notes, written before the data
1. **Consensus coupling conserves the sum.** 1ᵀQ e_k = out_k − in_k − Γ, where out_k = Σ_j A_kj and in_k = Σ_i A_ik. So right after a kick at k, the swarm mean grows only if k is a **net source of influence** (out-strength > in-strength). Over long horizons the conserved quantity is the DeGroot left eigenvector w ("social power"): a kick at k moves the eventual consensus by w_k. Consequences:
   - with symmetric or balanced coupling, the swarm-mean energy through any single node is **E ∝ N², whatever the coupling strength**. Coupling spreads a kick around but does not amplify it;
   - only asymmetry (leaders: high out, low in) brings E below N²;
   - the Gramian driver ranking at T = 4 h should be close to the **net influence current** out_k − in_k. That is H32's (HH118) source/sink classification, here derived from linear control rather than transfer entropy.
2. **What N^0.6 could mean.** With per-pair coupling ∝ N^−0.6 (H18), out and in strengths each scale as N^0.4. Strong asymmetry then gives E* ∝ N^1.2, i.e. input *amplitude* √E* ∝ N^0.6, which is HH110's number. Weak asymmetry gives E* ∝ N², and so does H04's "named-only" rival (no spread at all). Strong symmetric coupling also stays at N². So HH110's scaling needs strong leaders.
3. **Structural controllability is near-trivial here.** Rooms are dense (everyone sees everyone's messages), and every agent has self-dynamics (Γ > 0). So structurally N_D = number of rooms that receive no influence from outside. The LSB count on a *thresholded* graph mostly measures how many edges pass significance, i.e. sample size.
4. **HH110's "small rooms".** Per-recipient pull is higher in small rooms (H18 dilution), but a small room holds a small fraction of the swarm. For moving the *whole-swarm* mean, theory favors agents in the larger room.

## Data scheme (`scheme/`)
`scheme/build.py` reads shared tables only. It imports H18's loaders (`Shared`, `turn_times`, `room_lookup`, `room_at`) unmodified, and drops holdout days unless `analysis/confirm.py` calls it with its flags. **No text and no vectors are written**: vectors are looked up from `embeddings/chat_bge_small.npy` at analysis time.
- **Output:** `data/processed/H29-driver-nodes/<unit>/`, with `_provenance.json`:
  - `turns.parquet`: talk turn, recipient, previous own statement, call starts, room, room size;
  - `rows.parquet`: (turn, message) rows, with sender kind and code, visible or invisible, whether the message names the recipient;
  - `msgs.parquet`: all messages on the unit's days, with time, room and mentions;
  - `meta.json`.

**Units** (goal periods split at the same step changes as H01/H12/H22):

| Unit | Dates (PT) | Days | N (recipients) | Rooms | Role |
| --- | --- | --- | --- | --- | --- |
| G37 | 03-30 → 04-01 | 3 | 10 | #best / #rest | descriptive (short) |
| G38 | 04-02 → 04-24 | 17 | 14 | #best / #rest | counted |
| G39 | 04-27 → 05-01 | 5 | 14 | #best / #rest | counted |
| G40 | 05-04 → 05-08 | 5 | 14 | merged | counted |
| G41 | 05-11 → 05-15 | 5 | 14 | #best / #rest | counted |
| G42 | 05-18 → 05-22 | 5 | 15 | #best / #rest | counted |
| G44 | 05-26 → 05-29 | 4 | 17 | #best / #rest | counted |
| G51a | 07-06 → 07-08 | 3 | 21 | #general | descriptive (short) |
| G51b | 07-09 → 08-04 | 19 | 27 | #general (+isolated rooms 07-09/10) | counted |
| G51c | 08-05 → 08-24 | 14 | 27 | #general + #focus | counted |
| G51d | 08-25 → 09-02 | 7 | 29 | #general | counted |
| G51e | 09-03 → 09-04 | 2 | 29 | #general | descriptive (short) |

Holdout (🔒, `analysis/confirm.py` only): **G47** (06-15 → 06-19; inside the NE21 window that H04 used for activity timing → reuse disclosure needed), **#51 tail** (09-07 → 09-18), and optionally **G45** (reuse; H02 used activity timing, and H23 plans message *wording*; disclosure needed).

### What I had seen when writing the predictions
- **Scheme counts:** turns, visible and invisible rows, and recipients per unit (table above). Invisible rows are 3–7% of visible rows. The median visible set k is 3 (G38) to 8 (G51b).
- **Nuisance calibration** (`analysis/calibrate.py` → `calibration.json`), from agents' *own* statements only, in G38, G41 and G51b:

  | Quantity | Value |
  | --- | --- |
  | agent-mean variance share | 0.13–0.23 |
  | day-mean share | 0.03–0.08 |
  | agent-day share | 0.27–0.41 |
  | residual (readout noise + fast dynamics) | 0.59–0.74 |
  | lag-1 cosine of consecutive centered own statements | 0.27–0.39 |
  | restoring rate Γ | 0.56–1.03 per active hour (ρ_30min 0.60–0.76) |
  | turns per agent per active hour | 3.8–7.3 |

- No pull toward received messages, no placebo contrast and no cross-agent statistic had been computed.

## Observables
- **O1, net pull per message κ (unit level).** The pull slope is a(S) = Σ_S y·u / Σ_S |u|², where y = x(τ_n) − x(τ_{n−1}), u = x_m − x(τ_{n−1}), and S is a set of rows. Then

  κ = [a(V) − a(X_V)] − [a(I) − a(X_I)]

  with:
  - V: visible rows;
  - I: **invisible** rows. These are messages that reached j *during* τ_n's own model call, so τ_n could not read them, and they could not have read τ_n. They are the placebo for common topic and conversation state;
  - X: **cross-day** counterparts. The message is replaced by a seeded random message of the same sender (same kind for humans) from another day of the unit. This is the placebo for static position, style and regression to the mean.

  95% CI from a day-block bootstrap (1000 draws).
- **O2, influence network.** Per-pair κ_ij = a_ij(V) − a_ij(X_V) − c, with c = a(I) − a(X_I) at unit level (contamination assumed homogeneous). Agent senders only, pairs with ≥ 15 visible rows. Day-bootstrap SEs. Empirical-Bayes shrinkage toward an additive sender + receiver fit. A_ij = max(0, shrunk κ_ij) × r_ij.
  - Significant edges: z = κ_ij/SE, Benjamini–Hochberg q = 0.1 within the unit.
- **O3, structural controllability** on the significant-edge graph: N_D/N (no self-loops), root SCCs (with self-loops), driver classes. Split-half (even vs odd days) Jaccard of the driver sets.
- **O4, Gramian driver ranking.** D_k (and E_k = N²/D_k, AC_k) with Γ from `gamma_unit`.
  - Reliability: split-half Spearman of D_k between even-day and odd-day fits;
  - robustness: Γ × {0.5, 2}, signed vs clipped A, raw-centered 384-d vectors instead of whitened.
- **O5, net influence current** I_k = out_k − in_k (from A), and its rank correlation with D_k.
- **O6, observed spread (validators), always on the held-out half of days.** Cross-fitting: fit on even days, test on odd days, and the reverse.
  - **V1, one-step per-message spread:** s_k = mean over k's messages of Σ_{recipients j} [Δsim_j(m) − Δsim_j(m′)], where Δsim_j(m) = cos(x_j(τ_n), x_m) − cos(x_j(τ_{n−1}), x_m) and m′ is the cross-day placebo message. Predicted by the per-message out-pull Σ_j κ_kj.
  - **V2, the driver validator: hourly swarm spread at a 2-h horizon.** H_k = (k's messages per active hour) × mean over k's messages of Σ_{all agents j ≠ k} [cos(x_j(after), x_m) − cos(x_j(before), x_m) − same for m′]. Here "before" is j's last statement before t_m, and "after" is j's last statement in (t_m, t_m + 2 h] on the same day. Non-recipients (other rooms) are included, so indirect spread counts. Predicted by D_k.
- **O7, rival rankings** for V2: message volume (messages per active hour), exposure (recipients × volume), out-strength out_k alone (one-step, no propagation), net current I_k, uniform.
- **O8, scaling.** Best-driver energy E*(N) = min_k N²/D_k per unit. Log-log slope η across units (N = recipients in the network), and within the #51 segments.
- **O9, dilution in content.** Net pull per message vs the visible-set size k (bins 1, 2–3, 4–7, 8–15, 16+). Log-log slope per unit, random-effects pooled. This is the content analog of H18's k^−0.6.
- **O10, humans and naming.**
  - Net pull per message for human messages on the named agent vs bystanders.
  - Net pull of agent messages on named vs unnamed recipients (H04's "named only").
  - 2-h swarm spread after human messages that name an agent, vs that agent's training-half driver score (pooled across units, rank-normalized within unit).

## Null / baseline
- **N1, common topic / conversation state:** the invisible same-call placebo (H18's P10 design, here on content). Influence must exceed it.
- **N2, static field / style / regression to the mean:** the cross-day placebo.
- **N3, synthetic common-drive null:** A = 0 with a room-level drifting topic, at village sampling. Shows the false-positive rate of κ, and that the raw contrast (without N1) is biased.
- **N4, ranking nulls:** split-half Spearman under random relabeling of senders within (recipient, day) is ≈ 0. Rival rankings as in O7.
- **N5, scaling nulls:**
  - η = 2: symmetric coupling, or H04's named-only rival;
  - η = 1.2: HH110 (strong asymmetry with dilution);
  - η ≈ 0: a dominant leader.

## Faithfulness scorecard
Scored per model, mapping and window; 0 = not done or failed, 1 = partial, 2 = passed. Scheme and promotion thresholds: `writeup/paper.tex`, Sec. "Assessing model faithfulness".
**Rival models:**
- R1 common drive (no influence; N1/N3);
- R2 volume model (influence ∝ messages sent);
- R3 H04 named-only (pull only on named recipients, no network propagation);
- R4 one-step out-strength (no propagation);
- R5 H32's content transfer-entropy source ranking (running in parallel; compared if available).

**Locked holdout used for confirmation:** none yet. `analysis/confirm.py` targets G47 and the #51 tail, G45 optional. Reuse disclosures are required before it runs:
- **G47** lies inside the NE21 window that H04 used for activity timing. H29's statistic is the content (embedding) pull, a different modality;
- **#51 tail:** content confirmations are written but unrun in H12, H13 and H22;
- **G45:** used by H02 (timing); H23 plans wording.

| Axis | Test | Score | Evidence |
| --- | --- | --- | --- |
| A mapping | variables defined from dataset fields; assumptions listed; invariant across families and regimes | 1 | Every variable comes from shared tables (exposure, call starts, embeddings, mentions). But the imported visibility rule fails for long call windows: 39–70% of "invisible" rows come from PAUSE or long tool calls. The response measure mixes influence with co-response at short lags. Not invariant: the two-room era has too few near-boundary rows. |
| B assumptions | stationarity, Markov order, time-rescaling, update-order audit | 1 | A visibility/update-order audit was done, and it found the flaw. Split-half stationarity of the network fails in most units. No Markov-order test. |
| C adequacy | beats the null hierarchy, day-blocked held-out data | 1 | Pre-registered κ fails (negative in 7/9). Post hoc, the matched-age boundary test beats the truly-invisible null in 4/9 counted units, plus 2 descriptive (day-block bootstrap); named recipients like-for-like in 5/5 #51 segments. Post hoc, so capped at 1. |
| D unfitted predictions | unfitted statistics and the model's signature | 1 | Round 1: 0 (held-out spread not predicted, pooled ρ 0.09 / 0.04; P9b failed). **Round 1b:** the content-pull network still predicts nothing (−0.07 / 0.04), but the reply-graph network's driver score (net reply current) predicts the unfitted held-out 2-h spread in 6/9 (bge) / 7/9 (gte) units, pooled 0.23 [0.05, 0.39] / 0.12 [−0.06, 0.29]; network defined in round 1b, validator noisy. |
| E interventional | predicts the change across a natural experiment | 1 | Round 1: 0. **Round 1b native NE38:** the operator's reassignment of Opus 5 moved the named agent to the 96th–100th percentile of named-message pulls and did not relay to its 19 room-mates (71st / 92nd percentile), as the address-gated model predicts. Single event. |
| F identifiability | synthetic recovery with village sampling; robust to preprocessing | 1 | **Synthetic:** κ never false-positive; ranking recovery ρ 0.47–0.79 (0.32 in the over-coupled G51b regime); robust to nonlinearity. **Preprocessing:** rankings are robust to Γ and baseline (≥ 0.9) but only partly to raw 384-d vectors (0.15–0.99). **Fitted magnitude (post hoc):** in G51b recovery is 0.64 and real split-half (0.87) exceeds the model's (0.63). In the two-room weeks real split-half falls below what a true model gives. |
| G ground truth | agrees with known structure | 1 | Recovers H04's named-agent structure in content (named ≫ unnamed). Rooms: per-recipient pull is higher in the smaller room in 6/7 units (H18), but confounded by composition (#best). No leader ground truth outside the holdout. |
| H comparative | beats the named rivals | 1 | Round 1: 0 (driver score did not beat volume R2 or out-strength R4). **Round 1b:** the reply-graph score beats volume and reply in-rate on held-out spread (0.23 vs −0.06 / −0.06 bge; 0.12 vs 0.00 / −0.04 gte); R3 (named-only) still describes the content pull best (unnamed jump ≈ 0 on the ledger). |
| I transfer | holds in other same-mode periods, including the holdout | 0 | Holdout not run. Strongly heterogeneous across the two-room era and #51. |

## Prediction
*Written 2026-10-04 ~01:45 UTC, before running the analysis on real data (only the counts and nuisance calibration above had been seen).* Counted units: G38, G39, G40, G41, G42, G44, G51b, G51c, G51d (9). Descriptive: G37, G51a, G51e. With 9 units and ~10 predictions, results are reported as counts of units, not as single p-values.

**Synthetic (axis F, run first):**

| # | Prediction | Counts against |
| --- | --- | --- |
| S1 | Under the common-drive null (A = 0, calibrated drift), κ's 95% CI lies above 0 in ≤ 10% of replicates. The raw contrast a(V) − a(X_V) (no invisible placebo) is positive in ≥ 50% | κ false-positive rate > 20% |
| S2 | Linear generator, a_mean = 0.03 per message, sender heterogeneity σ_s = 0.7 (lognormal), on the real G38 and G51b skeletons. The estimated D_k ranking recovers the true injection ranking with Spearman ≥ 0.6, and the true top driver is in the estimated top 3 in ≥ 50% of replicates. On a 5-day skeleton (G41): Spearman ≥ 0.3 | Spearman < 0.3 on G38/G51b |
| S3 | Nonlinear generator (bounded confidence + k^−0.6 dilution): recovery Spearman drops by ≤ 0.2 vs linear | drop > 0.4 |
| S4 | Estimator choice: marginal ratio-of-sums vs joint ridge. The higher median S2 Spearman wins; ties (\|Δ\| < 0.05) go to marginal. Decided on synthetic data only | |

**Real data:**

| # | Prediction | Counts against |
| --- | --- | --- |
| P1 | **Influence exists.** κ > 0 with day-bootstrap CI excluding 0 in ≥ 6/9 counted units | ≤ 3/9 |
| P2 | **Most raw pull is common cause.** Contamination a(I) − a(X_I) is ≥ 50% of the field-corrected pull a(V) − a(X_V) in the median counted unit | < 25% |
| P3 | **Dilution in content.** Pooled log-log slope of net pull vs k in [−1.0, −0.3] | slope ≥ 0 |
| P4 | **Structural controllability is uninformative.** With self-loops, N_D = root SCCs ≤ rooms + 2. Without, N_D/N ≥ 0.3 on the BH graph. Split-half Jaccard of LSB driver sets < 0.3 in most units | Jaccard ≥ 0.5 in ≥ half the counted units (then structural drivers are informative) |
| P5 | **Gramian ranking is reliable where data are large.** Split-half Spearman of D_k ≥ 0.4 in G38, G51b, G51c; median over counted units ≥ 0.2 | median ≤ 0, or < 0.4 in all three |
| P6 | **Predictive validity.** Cross-fitted Spearman(D_k on train half, H_k on test half) > 0 in ≥ 6/9 counted units; pooled (Fisher z, weights N − 3) ρ ≥ 0.3. Beats out-strength alone (pooled Δρ > 0), but does **not** beat message volume by > 0.1 | pooled ρ ≤ 0; or ρ(Gramian) < ρ(volume) − 0.1 (then the controllability layer adds nothing an operator can't get from counting messages) |
| P7 | **Driver profile.** (a) D_k vs net current I_k: Spearman ≥ 0.7 within units. (b) Two-room units: the top driver is in the larger room in ≥ 2/3 (HH110's "small rooms" fails for whole-swarm steering). (c) Per-recipient pull is higher in the smaller room | (a) ρ < 0.4; (b) small room wins ≥ 2/3 |
| P8 | **Scaling.** η (E* vs N across units) in [1.5, 2.3]. HH110's amplitude ∝ N^0.6 (η = 1.2) is supported only if the 90% CI excludes 2. Expected: inconclusive (N spans ×3) | η < 1.0 or > 2.8 |
| P9 | **Humans.** (a) Human messages pull the named agent ≥ 2× more than bystanders. (b) The 2-h swarm spread after a human message naming a top-third driver is ≥ 1.5× that for a bottom-third driver. Low power expected (~100–200 named human messages) | (a) bystanders ≥ named; (b) reversed with CI excluding 1 |
| P10 | **Named vs unnamed (R3).** Agent messages' net pull on named recipients ≥ 2× unnamed, but unnamed pull > 0 (broadcast influence exists, so the network is not purely address-gated) | unnamed pull ≤ 0 in ≥ 6/9 (then the operator's lever is naming, not the network) |

### Amendment 1 (synthetic-based; written 2026-10-04 ~02:20 UTC, before any real-data run)
Synthetic design (`analysis/synthetic.py` → `data/processed/H29-driver-nodes/synthetic/`).
- **Setup:**
  - real event skeletons of G38, G41 and G51b: who posted when, visible sets, rooms, names. Only the vectors are synthetic;
  - nuisance variances from `calibration.json`;
  - ground truth: paired injection runs (common random numbers) giving D_true_k for every agent;
  - conditions × replicates: 8 per condition on G38 and G41, 3 on G51b.
- **Results:**

  | Condition | κ CI > 0 | ρ(D̂, D_true) | true top driver in estimated top 3 | split-half | held-out V2 ρ(D̂, H) [ceiling ρ(D_true, H)] |
  | --- | --- | --- | --- | --- | --- |
  | null (A = 0, common drive) | **0/8, 0/8, 0/3** (raw contrast without the invisible placebo: **100%** positive) | — | — | 0.00–0.09 | ≈ 0 |
  | G38 linear a = 0.03 | 6/8 | **0.78** (out-strength 0.46, volume 0.33) | 8/8 | 0.85 | 0.31 [0.45] |
  | G38 linear a = 0.01 | 2/8 | 0.79 | 7/8 | 0.64 | 0.35 [0.35] |
  | G38 nonlinear (bounded confidence + k^−0.6) | 0/8 | 0.79 | 7/8 | 0.37 | 0.32 [0.39] |
  | G41 (5 days) linear a = 0.03 / 0.01 / nonlinear | 7/8 / 5/8 / 1/8 | 0.47 / 0.59 / 0.47 | 5/8 / 8/8 / 6/8 | 0.45 / 0.47 / 0.30 | 0.09 / 0.16 / −0.02 [0.25 / 0.33 / 0.23] |
  | G51b linear a = 0.03 / 0.01 / nonlinear | 3/3 / 3/3 / 0/3 | 0.32 / 0.48 / 0.75 | 1/3 / 3/3 / 2/3 | 0.71 / 0.64 / 0.59 | −0.12 / 0.25 / 0.35 [0.59 / 0.59 / 0.35] |

- **Verdicts on S1–S4:**
  - **S1 passed.** κ never false-positive. Under pure common drive it is biased slightly *negative*: CI < 0 in 3/8 (G38) and 2/3 (G51b), because invisible messages sit closer in time to the reply than visible ones. Under true influence the invisible placebo also absorbs network-induced common input. **κ is conservative**: a P1 failure can come from weak influence; it is not proof of none.
  - **S2 partly passed.** G38: 0.78 and 8/8 ✓. G41: 0.47 ✓. G51b at a = 0.03: 0.32 ✗. #51's visible sets are large (k up to 30+), so a = 0.03 gives a total pull per turn above 1. That over-coupled regime overshoots and breaks the coarse-graining. At a = 0.01, or with dilution, G51b recovers 0.48–0.75.
  - **S3 passed.** The nonlinear generator loses ≤ 0.01 in G38 and G41, and *gains* in G51b, where dilution removes the overshoot.
  - **S4: marginal estimator chosen.** The joint ridge recovers worse in every condition (median ρ −0.12 to 0.49).
- **Amendments adopted:**
  1. **V2 redefined** (the original cross-day-placebo version was confounded by topic drift: per-message spread came out negative and scaled with volume, so ρ(D_true, H) was negative). The new placebo is the **contemporaneous message** m*: the nearest-in-time message in the same room by another agent (≤ 15 min). The contribution is (x_j,after − x_j,before)·(x_m − x_m*), excluding the senders of m and m*. H_k = Σ_m spread / mean |x_m − x_m*|² / active hours. A shared drift enters x_m and x_m* alike and cancels.
  2. **Marginal estimator** throughout (S4).
  3. **Calibrating P6.** Even when the model is exactly true, the held-out V2 correlation at village sampling is ρ ≈ 0.1–0.4 (ceiling 0.25–0.6). So the pooled ρ ≥ 0.3 in P6 is close to the best achievable. A pooled ρ of 0.15–0.3 is consistent with a true model; ρ ≈ 0 is not.
  4. **Synthetic D̂ ≡ net current** (ρ 0.98–1.0 in every condition), as theory note 1 says. P7a is therefore nearly guaranteed by construction. The informative part is whether the net current (equivalently D̂) predicts the held-out spread better than volume and out-strength (P6).
  5. **Post-hoc recovery check at the fitted magnitude.** After the real fit, re-run the synthetic at each unit's fitted κ and heterogeneity. This tells whether that unit's ranking is identifiable. Disclosed as post hoc.

## Results by goal period
Verdict rule (round-1b verdicts on ledger visibility are in each folder's `Verdict (1b)` line; they are unchanged for every unit under bge, and G40 becomes mixed under gte):
- **mixed:** the post hoc boundary test detects influence, but the driver ranking is not validated;
- **failed:** neither;
- **descriptive:** units shorter than 4 days.

Key numbers:
- κ: pre-registered net pull [95% CI];
- jump: post hoc visibility jump (named and unnamed are like-for-like);
- split-half D: pre-registered / post hoc;
- V2: pre-registered held-out validation ρ.

| Period | Role | Verdict | Key numbers |
| --- | --- | --- | --- |
| [G37](goalperiod-subhypotheses/G37/README.md) | descriptive | descriptive | κ -0.006 [-0.065, 0.032]; post hoc jump 0.074 [-0.128, 0.165] (named -0.04, unnamed 0.114); split-half D 0.17/0.06; V2 0.17 |
| [G38](goalperiod-subhypotheses/G38/README.md) | exploratory (counted) | failed | κ -0.063 [-0.081, -0.041]; post hoc jump -0.014 [-0.044, 0.024] (named -0.07, unnamed -0.002); split-half D -0.21/-0.31; V2 0.28 |
| [G39](goalperiod-subhypotheses/G39/README.md) | exploratory (counted) | mixed | κ 0.008 [-0.001, 0.027]; post hoc jump 0.046 [0.022, 0.095] (named —, unnamed 0.034); split-half D 0.40/0.55; V2 0.20 |
| [G40](goalperiod-subhypotheses/G40/README.md) | exploratory (counted) | failed | κ -0.003 [-0.017, 0.016]; post hoc jump 0.016 [-0.025, 0.047] (named -0.05, unnamed 0.015); split-half D 0.01/0.17; V2 -0.08 |
| [G41](goalperiod-subhypotheses/G41/README.md) | exploratory (counted) | failed | κ -0.037 [-0.051, -0.020]; post hoc jump -0.022 [-0.057, 0.029] (named -0.02, unnamed -0.024); split-half D 0.51/-0.04; V2 0.01 |
| [G42](goalperiod-subhypotheses/G42/README.md) | exploratory (counted) | failed | κ -0.014 [-0.029, -0.001]; post hoc jump 0.038 [-0.008, 0.087] (named 0.09, unnamed 0.040); split-half D 0.03/0.52; V2 0.36 |
| [G44](goalperiod-subhypotheses/G44/README.md) | exploratory (counted) | failed | κ -0.020 [-0.028, -0.012]; post hoc jump 0.004 [-0.021, 0.037] (named 0.03, unnamed -0.008); split-half D 0.26/-0.09; V2 0.44 |
| [G51a](goalperiod-subhypotheses/G51a/README.md) | descriptive | descriptive | κ -0.013 [-0.023, -0.007]; post hoc jump 0.033 [0.030, 0.047] (named 0.08, unnamed 0.021); split-half D 0.14/0.49; V2 -0.24 |
| [G51b](goalperiod-subhypotheses/G51b/README.md) | exploratory (counted) | mixed | κ -0.019 [-0.023, -0.014]; post hoc jump 0.033 [0.023, 0.043] (named 0.08, unnamed 0.013); split-half D 0.17/0.87; V2 -0.32 |
| [G51c](goalperiod-subhypotheses/G51c/README.md) | exploratory (counted) | mixed | κ -0.027 [-0.035, -0.021]; post hoc jump 0.025 [0.013, 0.038] (named 0.05, unnamed 0.011); split-half D -0.09/0.38; V2 0.17 |
| [G51d](goalperiod-subhypotheses/G51d/README.md) | exploratory (counted) | mixed | κ -0.013 [-0.024, -0.004]; post hoc jump 0.033 [0.019, 0.044] (named 0.09, unnamed 0.018); split-half D 0.05/-0.18; V2 0.14 |
| [G51e](goalperiod-subhypotheses/G51e/README.md) | descriptive | descriptive | κ -0.012 [-0.016, -0.010]; post hoc jump 0.013 [0.010, 0.015] (named 0.03, unnamed 0.009); split-half D -0.05/0.33; V2 0.11 |
| [NE38](goalperiod-subhypotheses/NE38/README.md) | native (round 1b) | supported | operator reassignment of Opus 5: target pull 96th/100th pct (bge/gte), bystanders 71st/92nd pct (no relay) |
| [G35](goalperiod-subhypotheses/G35/README.md) | native (round 1b) | mixed | designated leaders: replies per message ×1.39 [1.09, 1.69]; volume ×0.97; broadcast pull ×1.09 [0.76, 1.41] |
| [G26](goalperiod-subhypotheses/G26/README.md) | native (round 1b) | failed | elected leader: reply-attention DiD −0.20 (rank 5/10); broadcast-pull DiD +0.08 (rank 10/10) |

## Results
Scripts:
- `analysis/explore.py`: pre-registered pipeline;
- `analysis/posthoc.py`: Amendment 2, post hoc;
- `analysis/summarize.py`: scoring.

Outputs are in `data/processed/H29-driver-nodes/` (`summary.json`, per-unit `results*.json`). The figure summary is `figures/h29_summary.pdf`.

### Outcome vs prediction
| # | Predicted | Observed | Verdict |
| --- | --- | --- | --- |
| S1 | κ never false-positive under common drive; raw contrast biased | 0/19 false positives; raw contrast positive in 19/19 | **passed** |
| S2 | ranking recovery ≥ 0.6 on G38/G51b | G38 0.78 (top driver in top 3: 8/8); G41 0.47; G51b 0.32 at a = 0.03 (over-coupled), 0.48–0.75 at realistic coupling | **partly passed** |
| S3 | nonlinear loses ≤ 0.2 | −0.01 / 0 / +0.43 | **passed** |
| S4 | pick the estimator on synthetic data | marginal beats joint everywhere | marginal adopted |
| P1 | κ > 0 in ≥ 6/9 | **0/9 positive; 7/9 significantly negative** | **failed (opposite direction)**; diagnosed as a contaminated placebo plus a proximity confound (Amendment 2) |
| P2 | contamination ≥ 50% of the field-corrected pull | median ratio 1.7: the placebo pull *exceeds* the visible pull | **supported (exceeded)** |
| P3 | log-log slope of pull vs k in [−1, −0.3] | κ changes sign, so the slope is undefined. κ(k = 1) > κ(k ≥ 16) in 9/9, but k is confounded with message age | **inconclusive** |
| P4 | structural controllability uninformative | LSB N_D/N 0.5–1.0 on the sparse significant graph; N_D = 1 on the dense post hoc graph in #51; split-half Jaccard high only because almost every node is a driver | **as predicted** (the formal falsifier, Jaccard ≥ 0.5 in 6/9, is triggered by that degenerate reason) |
| P5 | split-half D ≥ 0.4 in G38, G51b, G51c; median ≥ 0.2 | pre-registered −0.21, 0.17, −0.09; median 0.05 (post hoc: −0.31, **0.87**, 0.38; median 0.17). Message volume: median 0.94 | **failed** |
| P6 | held-out ρ(D, H) > 0 in ≥ 6/9; pooled ≥ 0.3; beats out-strength; does not beat volume by > 0.1 | > 0 in 7/9; pooled **0.09 [−0.08, 0.27]** (post hoc 0.04); out-strength −0.01; volume −0.06. The validator replicates across halves at median 0.10 | **failed** (and largely uninformative: the validator is noise outside G51b and G41) |
| P7 | (a) D ≈ net current; (b) top driver in the larger room; (c) pull higher in the smaller room | (a) ρ 0.93–1.00, by construction; (b) 4/6, base rate 0.69; (c) 6/7 pre-registered and 6/7 post hoc, confounded by #best composition | (a) passed (trivial); (b) weak; (c) supported, confounded |
| P8 | η ∈ [1.5, 2.3]; HH110's 1.2 only if the CI excludes 2 | **Pre-registered E\*:** 2.15 [1.62, 2.64], trivially N², since that network is mostly clipped to zero. **Post hoc best driver:** −0.33 [−1.57, 0.76]. **Post hoc median agent:** 2.66 [2.17, 3.40] | HH110's N^0.6 amplitude **not supported**. The best driver's cost does not grow with N in one room (a high-volume hub); the median agent's grows at about N² or more. Model-only, unvalidated |
| P9 | (a) humans: named ≥ 2× bystanders; (b) top-third driver ≥ 1.5× bottom third | (a) 5/6 usable units; (b) 98 messages, 0.10 vs 0.23, difference CI [−0.60, 0.38] | (a) supported (small n); (b) **failed / inconclusive** |
| P10 | named ≥ 2× unnamed, and unnamed > 0 | ≥ 2× in 7/9. Pre-registered unnamed κ ≤ 0 in 8/9 (falsifier triggered). Post hoc like-for-like unnamed jump > 0 in G39, G51a, G51b, G51d and G51e (0.009–0.034) | first part supported; second **failed as pre-registered**, weakly positive post hoc |

### Amendment 2 (POST HOC, written after the first real-data run)
**Diagnosis of P1:**
- **Invisible-set contamination.** The invisible window [s(τ), t_τ) is ~10 s at the median (the model call). Its tail runs to minutes when s(τ) is a PAUSE or a long tool call, and the wake call sees the messages that arrived meanwhile. That tail is **39–70%** of invisible rows. Their pull is as high as visible rows' (`figures/h29_summary.pdf` a).
- **Proximity confound.** Field-corrected pull falls 5–23-fold from < 10 s to > 20 min of message age (G38 to G51b). So even truly invisible messages, being the closest in time to the reply, look like influence. The H18 rule (shared code) has the same flaw; H18's failed invisible placebo is at least partly this.

**Post hoc estimators** (`h29lib.rd_kappa`, `pair_kappa_prox`, `fit_network_v2`):
1. **Boundary test.** Field-corrected pull of visible rows minus truly invisible rows (call window ≤ 30 s), compared within matched 10-s age bins (0–30 s), with a day-block bootstrap. **Like-for-like** versions compare named visible with named invisible, and unnamed with unnamed.
2. **Network.** Pair pulls are the boundary jump plus the pair's residual relative to the unit's pull-vs-age curve, followed by EB shrinkage.
3. **Post hoc recovery check at the fitted magnitude** (`posthoc_recovery.py`):
   - G51b: a true model gives ranking recovery 0.64, split-half 0.63, held-out V2 0.29 (ceiling 0.70), validator split-half 0.66;
   - G38 / G41: V2 ceiling 0.25 / 0.06.

   So **G51b is the one unit where the controllability ranking could have been validated, and it was not** (real V2 0.05, while the real validator replicates at 0.45). In the two-room weeks a null V2 is expected even under a true model.

### Synthesis
1. **Content influence between agents exists, and it runs through names.**
   - Named recipients move ~0.03–0.09 of the way toward a message per message (like-for-like, #51); unnamed recipients ~0.01–0.02, i.e. ~3–6× less.
   - This is the content version of H04's "responses go only to the named agent": addressing is the gate, and broadcast is weak.
   - Per-recipient pull is higher in small rooms (6/7), consistent with H18's dilution but confounded with which models sit in #best.
2. **A linear controllability model on this network does not yield a usable driver ranking.**
   - In a single large room the driver score is essentially message volume (#51: ρ 0.34–0.89), which is reproducible but not validated.
   - In the two-room weeks the score is not even reproducible across days.
   - Theory note 1 holds by construction (D ≈ net current, ρ ≥ 0.93). But the net current from content pull is noise-dominated outside #51.
3. **Observed swarm-level spread from individual senders is mostly unmeasurable at village sampling.**
   - The 2-h, contemporaneous-placebo spread replicates across halves only in G51b and G41.
   - Where it replicates (G51b), it is not predicted by the driver score, volume, out-strength, being named or human attention.
   - So *what* makes some agents' content spread in #51 remains open (an exploratory hint: agents who name others a lot spread less broadly, ρ −0.43).
4. **Steering cost.** In the fitted model, moving the whole-swarm mean through a typical agent costs ∝ N^2.7, while a high-volume hub in one room keeps the cost roughly flat. With weak, address-gated coupling the model reduces to "a kick stays where it lands": HH110's N^0.6 amplitude would need strong asymmetric leaders, which the data do not show.

### Operator-facing procedure: "where to inject", with its measured reliability
1. **To move one agent, name it.** A message that names an agent pulls that agent's next statement 3–6× more than the same exposure without the name. Reliability: CI > 0 in 5/5 #51 segments; inconclusive in the small two-room weeks.
2. **To move the whole swarm, address every agent by name** (or post a message that names each, or message each); do not rely on a relay. Broadcast propagation is ~0.01 per message per bystander. No sender's broadcasts measurably move the swarm more than another's (held-out pooled ρ ≈ 0).
3. **If you must pick a single relay, pick the most active agent in the largest room.** That is what the controllability ranking reduces to (split-half of volume ≥ 0.65 in every unit), but its expected gain over a random agent is **not detectable** in our data (validation ρ 0.04 [−0.13, 0.22]). Treat it as a tie-breaker, not a lever.
4. **Before trusting a model-based driver list on your own swarm**, compute it on even and odd days separately (require split-half ≥ 0.4), and check it against held-out observed spread (require that the spread statistic replicates across halves first). In every one of our 12 units at least one check fails: in G51b both prerequisites pass and the validation itself fails (ρ 0.05).
5. **Measure influence at the visibility boundary, not with "message seen vs not" overall.** If your logs give model-call start times, compare messages that arrived just before vs during the call. Anything else is dominated by conversation co-response.

### Caveats
- **Most of the positive findings are post hoc** (Amendment 2). The pre-registered tests failed or were uninformative. The confirmatory script freezes the post hoc findings as predictions for the holdout.
- **Visibility boundary.** The boundary test assumes the call starts at the previous logged turn when the window is ≤ 30 s; the scaffold's exact context-assembly time is not logged. A real effect that saturates within seconds would be understated; a misassigned boundary biases toward 0.
- **The named effect may partly be conversation state.** Like-for-like controls shrink it by about a quarter (0.115 → 0.084 in G51b) but cannot exclude that named messages are answered in a different mode. Mentions also carry H18's engagement contamination.
- **Content geometry.** Pull is measured in a 32-d whitened bge-small space. Raw 384-d vectors give the same boundary signs in #51 but unstable driver rankings in some units (ρ 0.15–0.99). No second embedding model was used (planned project-wide).
- **Power and multiplicity.** 9 counted units × 10 predictions. Two-room weeks have 30–60 visible rows within 10 s of a reply. Units with N = 9–15 make rank statistics coarse. Per-period verdicts are reported as counts, not p-values.
- **Synthetic realism.** The generator's common drive is a slow OU drift, and it under-produced the real co-response (real pre-registered κ is −0.013 to −0.063 vs −0.001 to −0.004 under the synthetic null). Synthetic false-positive control holds for the drift it models, not for fast conversational co-response.
- **No leader ground truth** outside the holdout (#45). The temporary leader in G44 (2 days) was not a top driver.

### Figure summary (`figures/h29_summary.pdf`)
- **a:** pull vs message age in G51b. Visible messages decay smoothly; truly invisible ones (call ≤ 30 s) sit below visible ones at matched age (the boundary jump); "invisible" rows from long windows behave like visible ones (the contamination).
- **b:** like-for-like visibility jump by unit. Named ≫ unnamed in every #51 segment; the two-room weeks are underpowered.
- **c:** split-half reliability. Message volume is always reproducible; the driver score is reproducible only in some #51 segments; the grey band is what a true model gives.
- **d:** held-out validation. No ranking predicts 2-h swarm spread; the grey bars show that the spread statistic itself rarely replicates.
- **e:** model steering cost vs N: median agent ∝ N^2.7; best driver flat (a one-room hub).
- **f:** synthetic. When the model is true, the driver score beats out-strength and volume at finding the right injection point.

## Round 1b (improved data, 2026-10-04)
*Re-run of the round-1 pipeline (`explore.py`, `posthoc.py`, `summarize.py`) on corrected inputs, plus the reply-graph network and three period-native tests. Predictions P1–P10 and the per-period rule are unchanged; native predictions were written in their folders at 07:31 UTC, before any native statistic was computed.*

**What changed in the inputs.**
- **Visibility (DQ1 context ledger).** Round 1 imported H18's call-start rule; 39–70% of its "invisible" rows were messages that arrived during a PAUSE or long tool call and *were* read by the next call. Round 1b matches each talk turn to its model call (AGENT_TALK time between the call's `t_first` and `t_log`, DQ2's rule) and takes V(τ_n) = the ledger items received by the calls after τ_{n−1}'s call up to τ_n's call, I(τ_n) = items of the next call posted before τ_n itself. Every invisible row is now strictly invisible, so the boundary test needs no 30-s call-window filter (`C_MAX_S = ∞`). Effect on rows (G41): invisible 867 → 566; share of invisible rows from call windows > 30 s 0.43 → 0.23 (the remaining ones are long generations, still unseen). every talk turn matched its call except 153 in #35.
- **Second embedding model (DQ5).** Everything is run with bge-small (primary) and gte-modernbert (each whitened in its own regime basis).
- **Reply graph (DQ2).** A new influence network from `reply_graph` (hard parent counts; `reply_pairs` with `pair_set = cand` for the parent premium): A^rep_ij = c × (replies by j to i's messages per active hour), with c = the unit's field-corrected pull of reply-parent rows; the same Gramian, split-half and held-out V2 validation as round 1. **This network is a round-1b design choice (the re-evaluation brief), not a pre-registered one.**
- Code: `scheme/build.py --data r1b` (new `build_unit_ledger`; the old path is the default and unchanged), `H29_DATA=r1b` / `H29_EMB=gte_modernbert` switches in `h29lib.py`, new `analysis/r1b_extra.py`. Outputs: `data/processed/H29-driver-nodes/r1b/` (ledger units; bge results) and `r1b_gte/` (gte results).

**Old vs new (counted units G38–G51d unless stated).**

| Statistic | Round 1 (H18 visibility, bge) | Round 1b, bge | Round 1b, gte |
| --- | --- | --- | --- |
| P1 κ > 0 (CI) · κ < 0 (CI) | 0/9 · 7/9 | 1/9 (G39) · 7/9 | 0/9 · 6/9 |
| P2 contamination / field-corrected pull, median | 1.70 | 1.90 | 1.79 |
| post hoc boundary jump CI > 0 | 4/9 (G39, G51b–d) + 2 short | 4/9 (same) + 2 short | 5/9 (+G40) + 2 short |
| #51 named like-for-like jump (G51b, c, d) | 0.084, 0.053, 0.087 | 0.069, 0.049, 0.056 | 0.079, 0.068, 0.068 |
| #51 unnamed like-for-like jump (G51b, c, d) | 0.013*, 0.011, 0.018* | 0.007, 0.002, 0.012 (all CI ∋ 0) | 0.013*, −0.001, 0.007* |
| P5 split-half D (pre-registered), median · G38 / G51b / G51c | 0.05 · −0.21 / 0.17 / −0.09 | 0.29 · 0.29 / 0.45 / 0.00 | 0.18 · 0.47 / 0.43 / 0.13 |
| P5 post hoc network split-half median | 0.17 | 0.30 | 0.22 |
| P6 held-out ρ(D, H) pooled, pre-registered · post hoc | 0.09 · 0.04 | −0.07 · −0.01 | 0.04 · 0.09 |
| validator H split-half, median | 0.10 | 0.10 | 0.01 |
| P8 η (pre-registered E*) | 2.15 [1.62, 2.64] | 1.98 [1.42, 2.53] | 1.94 [0.88, 2.79] |
| P10 named ≥ 2× unnamed (pre-registered κ subsets) · unnamed κ ≤ 0 | 7/9 · 8/9 | 7/9 · 7/9 | 8/9 · 8/9 |
| **reply network:** split-half of D^rep, median | – | **0.65** | **0.66** |
| **reply network:** held-out ρ(D^rep, H) pooled · > 0 | – | **0.23 [0.05, 0.39] · 6/9** | **0.12 [−0.06, 0.29] · 7/9** |
| reply network rivals: in-rate · volume (pooled ρ) | – | −0.06 · −0.06 | −0.04 · 0.00 |
| reply-parent premium (parent minus other visible rows, matched age) | – | 0.11–0.17 (all CI > 0) | 0.12–0.19 (all CI > 0) |

\* CI excludes 0.

**What the corrected visibility says about P1.** The ledger removes the pause/long-call contamination, yet κ stays negative in 7/9 units and the placebo pull still exceeds the visible pull (median ratio 1.9). So the round-1 failure is mostly the second diagnosed cause: messages posted *during* the recipient's own generation are co-responses to the same prior turn (they sit closest in time and share its topic), not influence that leaked into the placebo. P1 stays failed; the diagnosis is sharpened (Amendment 2's matched-age boundary test is the right estimator, and it replicates).

**Address gating is sharper, not weaker.** Under the ledger the unnamed like-for-like jump in #51 shrinks to 0.00–0.013 (CI includes 0 in G51b–d under bge; gte 0.007–0.013 in G51b and G51d), while the named jump stays 0.05–0.08 in every #51 segment and both models. Named/unnamed ≈ 5–25×. The two-room weeks remain underpowered.

**A reply-graph network gives a usable ranking.** The content-pull network still fails both reliability (pre-registered split-half median 0.29, ≥ 0.4 only in G51b) and validity (held-out ρ ≈ 0). The reply network is reproducible (split-half 0.29–0.91, median 0.65) and its Gramian score, which reduces to the **net reply current** (replies received minus replies given, propagated), predicts the held-out 2-h swarm spread in 6/9 (bge) / 7/9 (gte) counted units, pooled 0.23 [0.05, 0.39] / 0.12 [−0.06, 0.29], inside Amendment 1.3's "consistent with a true model" band (0.15–0.3) under bge. Neither raw reply in-rate nor message volume predicts it (pooled ≈ 0). Caveats: the validator itself replicates poorly (median 0.10 / 0.01), the network was chosen in round 1b, and the reply-parent premium (0.11–0.19) is partly built in, because DQ2 ranks parent candidates partly by content similarity and Jev judges replies from text (a reply is *about* its parent). It is a consistency check, not separate evidence of influence.

**Native tests (layer 2).**

| Folder | Design | Prediction (07:31 UTC) | Result | Verdict |
| --- | --- | --- | --- | --- |
| [NE38](goalperiod-subhypotheses/NE38/README.md) | the operator's role reassignment of Claude Opus 5 (07-29 16:50), vs 52 other named human messages in G51b–d | target pull ≥ 75th pct; bystander spread inside the 5th–95th pct | target 95.6th (bge) / 100th (gte) pct (displacement 0.28 / 0.34); bystanders 70.6th / 92.2nd pct | **supported** |
| [G35](goalperiod-subhypotheses/G35/README.md) | designated daily leaders (6 agent-days), within-agent | replies per message × ≥ 1.3 and volume × ≥ 1.2; broadcast pull ratio CI ∋ 1 | replies × 1.39 [1.09, 1.69]; volume × 0.97 [0.77, 1.20]; broadcast pull × 1.09 [0.76, 1.41] (gte 1.10 [0.91, 1.25]) | **mixed** (attention yes, volume no, broadcast influence no) |
| [G26](goalperiod-subhypotheses/G26/README.md) | elected leader (agent 17) before vs after 01-05 19:35, DiD vs the other 9 | reply attention DiD > 0; broadcast pull DiD CI ∋ 0 | reply attention DiD −0.20 (rank 5/10); broadcast pull DiD +0.08 (bge) / +0.07 (gte), the largest of 10 (rank p ≈ 0.1) | **failed** (by the reply clause) |

Reading: an operator message is a strong content field on the agent it names and does not relay (NE38, as predicted from round 1's synthesis); designated or elected leadership buys attention (more replies per message, #35) without making the leader a broadcast driver in regime II; in regime I the elected leader's broadcast pull rose more than anyone's, consistent with H50's finding that unaddressed messages couple in regime I but not in III.

**Which verdicts change.** Card level: P1 failed (unchanged; now diagnosed as co-response rather than placebo contamination); P5 moves from failed to **partly supported** (pre-registered median 0.29 ≥ 0.2, but ≥ 0.4 only in G51b of the three named units); P6 failed (unchanged for the pre-registered network); P10 first part 7/9 (bge) / 8/9 (gte), second part still fails (unnamed κ ≤ 0 in 7–8/9); the post hoc address-gating finding is confirmed on corrected visibility and a second model. Per period (rule unchanged, bge): G39, G51b, G51c, G51d stay mixed; the other counted units stay failed; G42 and G44 now carry a negative *unnamed* jump (G44 −0.026 [−0.034, −0.004]). **Verdict (1b)** lines are in each period README.

**Scorecard after 1b:** A 1 (ledger visibility fixes the mapping flaw; co-response still contaminates the response measure); B 1; C 1 (boundary test beats the strictly-invisible null in 4–5/9; post hoc); **D 0 → 1** (the reply-network ranking predicts an unfitted held-out statistic, pooled 0.23 under bge, though defined in round 1b); **E 0 → 1** (NE38: the operator intervention behaves as the address-gated model predicts); F 1; G 1 (#35 leaders get attention, not broadcast influence); **H 0 → 1** (reply-network score beats volume and in-rate on held-out spread); I 0 (holdout not run; two-room weeks underpowered). **A1 B1 C1 D1 E1 F1 G1 H1 I0.**

**Operator rule, revised.** (1) To move one agent, name it (named/unnamed ≈ 5–25× in #51 on ledger visibility). (2) An operator message to one agent stays with that agent (NE38). (3) If a relay must be chosen, rank agents by net reply current (replies received minus given) from the reply graph, not by volume or content-pull "driver" scores; expect a weak edge (held-out ρ ≈ 0.1–0.2). (4) Designating a leader buys replies, not reach.

**Disclosure.** A probe for the leading-@ nudge rule (shared with H30/H39 work) printed per-period nudge *counts* including held-out periods (#32, #34, #45–#50, #51 tail); no outcome was computed on them.

## Notes
- 2026-10-04: promoted from HH110 by Vivian (usefulness-first batch); wave 1.
- 2026-10-04 ~01:45 UTC: observables, nulls, rivals and predictions written before any real-data pull statistic.
- 2026-10-04 ~02:20 UTC: Amendment 1 (synthetic-based) written before any real-data run; per-period folders with dated predictions written ~02:25 UTC.
- 2026-10-04: first real-data run (explore.py); P1 failed in the opposite direction; diagnosis and Amendment 2 (post hoc: boundary test, like-for-like named controls, proximity-adjusted network, recovery at fitted magnitude). `confirm.py` written and dry-run on G38/G51d stand-ins (C1 pass, C1b fail, C2–C4 pass, C5 fail, C6 pass on stand-ins); not run on the holdout.
- **Proposed shared changes** (not made; outside H29's edit scope): DEFINITIONS.md entries for *influence coupling (content pull)*, *visibility jump (boundary test)*, *driver score (mean-output Gramian)*, *net influence current*; an infra/README Known issue: the H18 call-start visibility rule misclassifies messages arriving during PAUSE or long tool calls (39–70% of "invisible" rows in regime III); a `call_windows` shared table with model-call starts if any log field allows it.
- 2026-10-04: round 1b on the context ledger, both embedding models and the DQ2 reply graph (`r1b_extra.py`), natives NE38 / G35 / G26; ~15 min of compute on ≤ 2 processes; disk +4.5 MB in `data/processed/H29-driver-nodes/r1b*/`.
