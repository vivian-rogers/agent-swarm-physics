# H132: Debate is a two-sublattice limit cycle: topic ping-pong at lag one

**Status:** exploratory round 1 done (2026-10-04; non-holdout only). **Failed (kill K): debate content does not alternate; it persists from turn to turn across the team line.**
- **No limit cycle.** On the motion's issue axis, team-centred turn projections are positively correlated at lag 1 (ρ₁ +0.16, shuffle p_hi 0.002; ρ₁ < 0 in 2/10 debates) and lag 2 (ρ₂ +0.21). The alternation Λ = ρ₂ − ρ₁ = +0.05 is not beyond the turn-shuffled null (p 0.08); the synthetic power for k_× = 0.6 is 1.00 (0.74 at k_× = 0.3).
- **No direction, no current:** A_γ +0.05 (p 0.71 two-sided); cycle area L −0.07 (p 0.39); negative in all four variants, significant only in unmasked bge (p 0.04).
- **Topic echo (R2):** full-vector ρ₁^vec +0.15 (p 0.0002, all variants). Message level: same-team ρ +0.30 and cross-team +0.12, both positive.
- **Natives:** verdict switch-off uninformative (no cycle to switch off; Λ_post −0.18, n.s.); read gate Δρ₁ −0.01 (n.s.); re-drafted pairs −0.05 (sign-flip p 0.29).
- Scorecard A1 B1 C1 D1 E0 F2 G1 H1 I0. `analysis/confirm.py` (#34) frozen, guarded and dry-run; **not run**.
**Question served (GOALS.md):** **Q1** (what couples agents?): when two drafted teams alternate in a debate, does each move answer the other team's last move in content (an antiferromagnetic coupling acting through reading), or do the teams only hold assigned positions while the format alternates the speakers? **Q6** second: a content cycle with a direction would be broken detailed balance made by a coupling, not by the scheduler.
**Fields:** stat mech (kinetic Ising on two sublattices, broken detailed balance), sociophysics (debate, opinion dynamics)
**Literature:** [Aguilera, Ito & Kolchinsky 2026](../../literature/aguilera-2026-entropy-production-nonequilibrium-maxent.md) (entropy production from the antisymmetric part of lagged correlations). Cited from memory (†, not in `literature/`): Glauber, *J. Math. Phys.* 4, 294 (1963)† (single-spin-flip kinetics); Aguilera, Moosavi & Shimazaki, *Nat. Commun.* 12, 1197 (2021)† (mean-field asymmetric kinetic Ising; period-2 cycles under parallel/alternating updates with antiferromagnetic coupling); Zia & Schmittmann, *J. Stat. Mech.* P07012 (2007)† (probability currents and the area of a cycle as the signature of broken detailed balance). Model references: [`physics-models/02-nonequilibrium-ising/README.md`](../../physics-models/02-nonequilibrium-ising/README.md), [`physics-models/01-inverse-ising/README.md`](../../physics-models/01-inverse-ising/README.md).
**Definitions used** (`physics-models/DEFINITIONS.md`): Agent; Regime (I); Agent state, **variant vector** (whitened statement vectors) and **variant categorical** (team σ_i ∈ {Gov, Opp, judge, bench} per debate); Driving / external field (motion, assigned sides, verdict); **Interaction (ledger-visible exposure)** and its **unread (in-flight) exposure placebo** (RE-D1); H21's phase rule (pre / deb / post) and **a-priori text axis** (the support-minus-oppose template embedding of each motion); H37's and H21's **stance coupling** (comparison only). **New named variants proposed for DEFINITIONS.md** (not edited here), defined under Observables: *debate turn*, *team-centred issue projection z_t*, *turn alternation ρ₁, ρ₂ and Λ*, *cycle antisymmetry A_γ*, *issue–topic cycle area L*.
**From:** HH375 in `hypotheses/hypohypotheses/HYPOHYPOTHESES.md` · **Models:** `physics-models/02-nonequilibrium-ising/` (primary: kinetic two-sublattice dynamics, broken detailed balance), `physics-models/01-inverse-ising/` (antiferromagnetic block coupling)
**Data inputs:** H21's #12 processed products, read as data only (`data/processed/H21-debate-antiferromagnet/G12/`: `statements.parquet` with debate, phase and team; `emb_masked.npy` and `emb_masked_gte_modernbert.npy`, agent names and team/role words masked; `motions.npz` and `motions_gte_modernbert.npz`, the embeddings of each motion's topic, support and oppose templates; no text); shared `ground_truth_labels` (#12 `team`, `phase`, `judge`; re-checked against H21's labels), `embeddings/statements.parquet` + `statements_white32_<model>.npy` (unmasked variant), regime-I whiteners (`common.load_whitener`, `embed_models.load_whitener`), `producing_calls` (visibility of the previous turn). No text is read.

## Source HH (verbatim from the HH list, including refinements)
- **HH375 · Debate is a two-sublattice limit cycle: topic ping-pong at lag one.** Two teams that each respond to the other's last move form a pair of antiferromagnetically coupled sublattices updating in turn. That gives a period-2 cycle in content: team A's message points along the issue, team B's rebuts it, and so on. This breaks detailed balance (the cycle runs one way).
  - *Prediction:* in #12, the lagged cross-team content correlation is negative at lag 1 and positive at lag 2 (in turns), and its antisymmetric part is nonzero (the cycle has a direction); within-team lags show no alternation.
  - *Check:* turn sequences per debate from the DQ6 schedule; content projections on each debate's issue axis.
  - *Kill:* no alternation beyond a turn-shuffled null.
  - *Impostors:* the debate format forces alternation (a scheduler field); test whether the content alternates, not just the speakers.
  - *Models:* 02, 01 · *Builds on:* H21, H37, H101, HH353

## Question
#12 ran ten Asian-Parliamentary debates with drafted Government and Opposition teams. H21 found no full-vector two-sublattice order in content, only a small staggered tilt along the motion's a-priori stance axis (statement-level Gov − Opp 0.43 whitened units in bge). H21 1b and H37 found the antiferromagnet in reply stance. HH375 asks a dynamic question: beyond each team's assigned position, does each move push the issue projection opposite to the other team's previous move, so that the content alternates at lag one? The speakers alternate by format, so only the content can carry the claim.

## Design: two layers (STANDARDS §4)
- **Replication (layer 1, role `replication`).** The common estimator (ρ₁, ρ₂, Λ, A_γ, L) on every non-holdout period with drafted opposing teams and a turn schedule. Only G12 qualifies (#34's hidden teams are held out; #26 and #33 assign no sides). Its ten debates are the samples; per-debate values are reported, and the period estimate pools turn pairs over debates with debate-specific centring.
- **Natives (layer 2, role `native`),** each with its own dated prediction in the G12 folder, written before it runs:
  - **N1 verdict switch-off** (G12): the judge's verdict ends the debate. A coupling driven by the opponent's last move should stop when the teams stop debating (post phase, 10 min).
  - **N2 read gate** (G12): a rebuttal needs the previous move. Split consecutive cross-team turns by whether the responding turn's first message was produced by a call that could see the previous turn (ledger-visible) or not (in flight).
  - **N3 re-drafting within pairs** (G12): teams are re-drafted every debate. For message-level consecutive pairs (agent a then agent b), compare the same pair when drafted as opponents and as teammates.

## Model
**From:** `physics-models/02-nonequilibrium-ising` (kinetic Ising with antisymmetric couplings or a fixed sweep order) and `physics-models/01-inverse-ising` (two-block antiferromagnetic mean field).

**H132 variant: alternating-update two-sublattice linear dynamics on the issue axis.** Debate d has an exogenous issue axis â_d (the motion's support-minus-oppose template direction, built without labels; H21). Turn t is a maximal run of consecutive debater messages from one team; its content projection is y_t = v_t·â_d, with v_t the mean whitened vector of the turn's messages. Sublattice A = Government (ε = +1), B = Opposition (ε = −1). The dynamics:

  y_t = ε_t μ_d + a_i(t) + u_t + e_t,     u_{t+1} = −k_× u_t + η_{t+1}   (team changes between t and t+1),

- μ_d: the **staggered field** (assigned sides; H21's tilt, ≈ 0.2 of the per-dimension statement noise).
- a_i: the speaker's own field (model family, habits). e_t: sampling noise of the turn mean.
- u_t: the dynamic issue state. k_× > 0 is the **antiferromagnetic response** of a team to the other team's last move (rebuttal pushes the other way).
- With directed response (only Opposition rebuts, k_{GO} ≠ k_{OG}), the cycle has a direction.

**Signatures.** After removing each team's mean (the static staggered field), z_t = y_t − ȳ_team(t):
- ρ₁ = corr(z_t, z_{t+1}) ≈ −k_× r (r = reliability of a turn mean; noise attenuates toward 0);
- ρ₂ = corr(z_t, z_{t+2}) ≈ +k_×² r (two sign flips);
- **Λ = ρ₂ − ρ₁ > 0** is the alternation (zero for any static field, positive for a period-2 cycle, negative for a common drift where ρ₁ > 0);
- **A_γ = ρ_{G→O} − ρ_{O→G}**: the antisymmetric part of the lag-1 cross-team correlation (Gov turn then Opp turn, minus the reverse). It is odd under time reversal and is zero for a reversible process;
- **L**: the mean signed area swept per turn in the (issue, topic) plane, L = mean_t (a_t g_{t+1} − g_t a_{t+1}) / (sd_a sd_g), with a = issue projection and g = projection on the motion's topic direction ĝ_d (both team-centred). A probability current gives L ≠ 0.

**The scheduler (speaker-only alternation).** If teams hold positions without responding (k_× = 0), turns still alternate speakers, so raw y alternates with sign ε_t μ_d. Team centring removes it: ρ₁ = ρ₂ = 0 up to the centring bias, which the turn-shuffled null reproduces exactly.

**Rivals (named):**
- **R1 speaker-only alternation / staggered paramagnet** (H21's honest model): Λ ≈ 0 against the shuffle null.
- **R2 topic echo / common drift** (a rebuttal repeats the words it rebuts; bag-of-meaning embeddings encode negation poorly): ρ₁ > 0, Λ < 0.
- **R3 static antiferromagnet without dynamics:** large staggered field, no residual alternation (same as R1 in the residuals).
- **R4 staggered-field ramp** (sides harden over a debate): a trend in u that centring does not remove; checked by a within-debate detrended variant.

## Data scheme (`scheme/`)
`scheme/build.py` reads H21's G12 products as data and shared tables, re-checks teams and phases against DQ6 `ground_truth_labels`, asserts no row is in the holdout (#12 is not held out; the assertion uses `common.holdout_mask`), and writes codes and vectors only.
- **Messages:** H21's `statements.parquet` rows with team ∈ {Gov, Opp} (debaters; judge and bench excluded), phases deb / post / pre, ordered by time within debate.
- **Vectors:** masked embeddings (bge primary, gte variant) whitened with the regime-I whitener of the same model (32-d, not normalized per message). Variant: unmasked shared `statements_white32_<model>` rows matched by message id.
- **Axes:** â_d = unit(W(support) − W(oppose)) and ĝ_d = unit(W(topic)) from `motions*.npz` (row order: topic, support, oppose; checked by H21's construction).
- **Turns:** maximal runs of consecutive debater messages from one team within one debate and phase; v_t = mean of the run's whitened vectors; a turn keeps its speaker list, first message id and first-message producing call (`producing_calls`).
- **Output:** `data/processed/H132-debate-limit-cycle/G12/` (`messages.parquet`, `turns.parquet`, `turn_vectors_<model>_<src>.npy`, `axes_<model>.npz`), `results/`, `synthetic/`, `_provenance.json`. Budget ≤ 10 MB.
- **Regimes covered:** I only (#12, 2025-09-01 → 09-04).

## Observables
*Written 2026-10-04 22:23 UTC, before any H132 statistic.*
- **O1 turn alternation.** z_t = team-centred issue projection within debate and phase. ρ₁ and ρ₂ pooled over debates (sums of products over sums of squares, debate-centred), and per debate. **Λ = ρ₂ − ρ₁** (primary).
- **O2 antisymmetry A_γ** = ρ_{G→O}(1) − ρ_{O→G}(1) (pooled).
- **O3 within-team alternation (message level).** Consecutive debater messages, team-centred message projections: ρ_same(1) over same-team consecutive pairs and ρ_cross(1) over cross-team pairs.
- **O4 cycle area L** in the (â_d, ĝ_d) plane (team-centred turn projections, standardized per debate).
- **O5 static check (descriptive).** Raw ȳ_Gov − ȳ_Opp per debate (H21's tilt), to show the staggered field the centring removes.
- **Variants:** gte masked; unmasked bge/gte; a detrended variant (team-centred z minus a per-debate linear trend in turn index; R4); a full-vector variant ρ₁^vec = pooled cosine-weighted correlation of team-centred 32-d turn vectors (the topic channel, where R2 predicts ρ₁ > 0).

**Null / baseline.**
- **Turn-shuffled null (kill null):** within each debate and phase, permute turn contents among the same team's turns (5,000 draws). It keeps the speaker/team sequence, the static staggered field, the agent mix per team and the centring bias, and destroys any turn-to-turn dynamics. All statistics are recomputed on each draw, including the centring.
- **Message-shuffled null** for O3: permute message contents within team, debate and phase.
- **Debate bootstrap** (resampling debates) for CIs.
- **Synthetic worlds on the real skeleton** (axis F, before real data): real team sequences, message counts and turn runs of the ten debates, with issue projections from W0 speaker-only alternation (staggered field + agent fields + noise), W1 symmetric limit cycle (k_× ∈ {0.3, 0.6}), W2 common drift (AR(1) across turns, ρ = 0.5), W3 directed cycle (only Opposition responds), W4 staggered-field ramp. Each statistic's size and power are reported at noise levels matched to H21's statement-level tilt.

## Impostors (STANDARDS §1)
| Impostor | Relevant? | How H132 removes it | Status (planned) |
| --- | --- | --- | --- |
| Scheduler field (format alternates speakers) | yes (central) | Team-centring removes the staggered field that alternation of speakers carries; the turn-shuffled null keeps the exact speaker sequence (size 0.05 in W0). A ramp gives Λ false positives in 10% of worlds and detrending does not remove it. | removed |
| Exogenous field (motion, assigned sides, verdict) | yes | The issue axis is exogenous (motion text). Side assignment is a static field per team, removed by team-centring. A slow common topic drift inside a debate is what the positive ρ₁, ρ₂ look like (R2). | removed (sides); partly (drift) |
| Shared model priors | partly | Masked embeddings remove team/role words and names; the shuffle keeps each team's agent mix; N3 compares the same agent pair as opponents and teammates (null). | partly |
| Contemporaneous convergence | yes | N2 splits consecutive turns by whether the responder could read the previous move (ledger-visible vs in flight): no difference (Δρ₁ −0.01). | removed (no read-gated effect to protect) |

## Faithfulness scorecard
Scored per model, mapping and window; 0 = not done or failed, 1 = partial, 2 = passed. Scheme and promotion thresholds: `writeup/paper.tex`, Sec. "Assessing model faithfulness".
**Rival models:** R1 speaker-only alternation (staggered paramagnet); R2 topic echo / common drift; R3 static antiferromagnet; R4 staggered-field ramp.
**Locked holdout used for confirmation:** none yet. Planned: #34 (hidden, daily die-rolled teams: saboteurs vs villagers), family `content_alignment`, via `analysis/confirm.py` (frozen with `confirm.sha256`; guarded by `--confirm` + `H132_CONFIRM=1` + hash check + `holdout_ledger.check`; leave-day-out team axis because #34 has no motion; dry run on G12: C1 fails, C2 and C3 pass, as in round 1). **Not run.**
**Overall A–I:** A1 B1 C1 D1 E0 F2 G1 H1 I0.

| Axis | Test | Score | Evidence |
| --- | --- | --- | --- |
| A mapping | variables defined from dataset fields; assumptions listed; invariant across families and regimes | 1 | Turns, teams and the issue axis come from DQ6/H21 labels and the motion text; same result in two embedding models, masked and unmasked. One period. |
| B assumptions | stationarity, Markov order, time-rescaling, update-order audit | 1 | Update order is the debate format (audited: 306 alternating turns); team-centring assumes static sides within a debate; a ramp is a known residual false-positive mode. |
| C adequacy | beats the null hierarchy, day-blocked held-out data | 1 | The limit cycle does not beat the turn-shuffled null; the persistence alternative (ρ₁, ρ₂ > 0) does, in all variants. |
| D unfitted predictions | unfitted statistics and the model's signature | 1 | The cycle's signature (ρ₁ < 0, ρ₂ > 0, A_γ ≠ 0) is absent; the within-team prediction (no alternation) holds. |
| E interventional | predicts the change across a natural experiment | 0 | Verdict switch-off is uninformative without a cycle; no NE tested. |
| F identifiability | synthetic recovery with village sampling; robust to preprocessing | 2 | Calibrated size (0.01–0.06) and power (Λ 0.74–1.00; A_γ 0.83; L 1.00) on the real turn skeleton; result robust to model and masking. |
| G ground truth | agrees with known structure | 1 | DQ6 teams verified (58/58); the static staggered tilt (H21) is reproduced in raw projections (Gov − Opp > 0 in 8/10 debates, bge masked). |
| H comparative | beats the named rivals | 1 | Loses to R2 (topic echo / drift: ρ₁ > 0, ρ₁^vec > 0); R1 (speaker-only) and R3 do not explain the positive ρ₁ either. |
| I transfer | holds in other same-mode periods, including the holdout | 0 | No other non-holdout period with drafted teams; #34 not run. |

## Prediction
*Written 2026-10-04 22:23 UTC, before any H132 statistic on real data.* **Seen beforehand:** H21's full card (rounds 1, 1b and the 1c pre-registration: no full-vector staggered order; a-priori text axis σ_text 0.092 bge / 0.055 gte; statement-level Gov − Opp 0.43 bge / 0.22 gte; post-verdict reversal; sublattice 3-min ρ +0.53 bge / +0.33 gte, common drive), H37 (stance antiferromagnet, teams recovered 7/10), H101 (J_team +0.15 within vs −0.60 across in co-usage), H115's card (judge sink, timing). Skeleton counts only: 582 debater messages in debate phases → 306 turns (296 lag-1 turn pairs); message-level consecutive pairs 296 cross-team and 276 same-team; post phase 142 turns; pre phase 129. **Not seen:** any projection, correlation or alternation statistic of this design.

| # | Prediction (primary unless marked) | Counts against | Credence |
| --- | --- | --- | --- |
| P1 | **Content alternates (HH primary).** Pooled ρ₁ < 0 and ρ₂ > 0, each beyond the turn-shuffled null (one-sided p < 0.05), so Λ > 0 with p < 0.05 (bge masked). | Λ's shuffle p ≥ 0.05 (**kill K**) | 0.15 |
| P2 | **The cycle has a direction.** A_γ ≠ 0 beyond the shuffle null (two-sided p < 0.05). | p ≥ 0.05 | 0.10 |
| P3 | **No alternation within teams.** Message-level ρ_same(1) ≥ 0 or not below the message-shuffled null (one-sided p ≥ 0.05). | ρ_same(1) < 0 with p < 0.05 | 0.80 |
| P4 (secondary) | **Probability current in the issue–topic plane.** L ≠ 0 beyond the shuffle null (two-sided p < 0.05). | p ≥ 0.05 | 0.10 |
| P5 (secondary) | **Topic echo in the full vector** (R2's signature): ρ₁^vec > 0 beyond the shuffle null. | ρ₁^vec ≤ 0 | 0.60 |
| P6 (secondary) | **Model robustness.** If P1 passes in bge, Λ > 0 with p < 0.1 in gte masked. | gte Λ ≤ 0 | 0.5 (conditional) |

**Kill rule (from the HH):** **K** fires when the alternation Λ is not beyond the turn-shuffled null (one-sided p ≥ 0.05, bge masked, primary). If the synthetic power at H21-sized noise is < 0.5 for k_× = 0.3, a kill is reported as "no alternation of the size the synthetic can see" with that size stated, not as a general negative.
**Verdict rule (G12):** *supported* if P1 passes and P3 holds; *failed* if K fires and the synthetic power for k_× = 0.6 is ≥ 0.8; *inconclusive* (written *mixed* in the table) if K fires with lower power, or if only one of ρ₁ < 0, ρ₂ > 0 is significant.

**Amendment A1 (2026-10-04 23:10 UTC, after the synthetic validation, before any real-data statistic).** Synthetic worlds keep the real debate-phase message sequences (306 turns in 10 debates), team runs, agents and visibility flags; issue and topic projections are synthetic (message noise sd 1, staggered field μ 0.2, agent fields sd 0.3; `analysis/synthetic.py`; `data/processed/H132-debate-limit-cycle/synthetic/summary.json`; 100 replicates per world, 200 shuffles each). Findings:
1. **The turn-shuffled null is calibrated.** Speaker-only alternation (W0): rejection 0.05 (Λ), 0.04 (ρ₁ < 0), 0.03 (ρ₂ > 0), 0.03 (A_γ), 0.01 (L), 0.04 (Δρ₁ visibility). Team-centring alone gives E[ρ₂] ≈ −0.08 and E[Λ] ≈ −0.08 under W0; the shuffle reproduces both.
2. **Power of Λ:** 0.74 at k_× = 0.3 (latent sd 1), 1.00 at k_× = 0.6, 0.68 at k_× = 0.6 with latent sd 0.5. A directed cycle (W3) gives Λ power 0.60 and A_γ power 0.83.
3. **P1's "both significant" clause is underpowered.** ρ₂ > 0 reaches significance in only 0.20 (k_× = 0.3) and 0.33 (k_× = 0.6, sd 0.5) of cycle worlds, because the lag-2 signal is k_×² and the centring bias pulls ρ₂ down. **P1 now passes when Λ and ρ₁ are significant and ρ₂ exceeds its null mean (sign only).** The kill K (Λ) is unchanged.
4. **Rivals:** a common drift (W2) gives ρ₁ +0.26 and never a positive Λ (0/100). A staggered-field ramp (W4) gives a false Λ in 0.10 of worlds; detrending does not remove it (0.11), so a Λ near the 5% edge is read with that caveat. A rotation (W5) is caught only by L (power 1.00).
5. **N2** (visibility split) has size 0.03–0.06 in every world; no world plants a visibility-dependent cycle, so its power is not set by this synthetic.
6. **Verdict rule** unchanged otherwise: *failed* (K fires) needs the k_× = 0.6 power ≥ 0.8, which holds (1.00); at k_× = 0.3 the power is 0.74, so a kill excludes cycles of k_× ≳ 0.4 at H21-sized noise, not weaker ones.

**Natives:** predictions in `goalperiod-subhypotheses/G12/README.md`, written before they run.

## Results by goal period
| Period | Role | Verdict | Key numbers |
| --- | --- | --- | --- |
| [G12](goalperiod-subhypotheses/G12/README.md) | replication (10 debates) + natives N1–N3 | failed (K fires; power 1.00 at k_× = 0.6) | ρ₁ +0.16 (p_hi 0.002), ρ₂ +0.21, Λ +0.05 (p 0.08), A_γ +0.05 (p 0.71), ρ₁^vec +0.15 (p 0.0002); N1 uninformative, N2 −0.01, N3 −0.05 (n.s.) |

## Results
*Exploratory round 1, 2026-10-04 (run 23:11–23:13 UTC, after Amendment A1). Code: `scheme/build.py`, `analysis/{h132lib,synthetic,run,summarize,confirm}.py`. Data: `data/processed/H132-debate-limit-cycle/` (`G12/{messages.parquet, msg_white_*.npy, axes_*.npz}`, `results/results.json`, `synthetic/summary.json`; < 1 MB). Figure: `figures/summary_obs_col.pdf`. Estimates: 40 rows in `per_period_estimates` (`hypothesis == "H132"`; the CI columns hold the shuffle-null 5–95% band, flagged in `method`).*

### Headline
The #12 debates are not a two-sublattice limit cycle. After each team's static position is removed, a turn's projection on the motion's support–oppose axis is *positively* correlated with the other team's previous turn (ρ₁ = +0.16, beyond the turn-shuffled null at p 0.002) and with the same team's previous turn (ρ₂ = +0.21). The alternation Λ = ρ₂ − ρ₁ = +0.05 is inside the shuffle null (p 0.08), where a cycle of k_× = 0.6 would be found every time and one of k_× = 0.3 three times in four. The full-vector topic channel shows the same echo (ρ₁^vec = +0.15). Rebuttals restate what they rebut, and both teams drift together through a debate.

### Outcome vs prediction
| # | Prediction | Observed (bge masked; variants) | Outcome |
| --- | --- | --- | --- |
| P1 / K | Λ > 0 beyond the shuffle (p < 0.05); ρ₁ < 0; ρ₂ > null mean (A1) | Λ +0.047 (p 0.081); ρ₁ +0.161 (p_lo 0.998); ρ₂ +0.209; gte masked Λ +0.043 (p 0.105), ρ₁ +0.086; unmasked bge +0.029 (0.110), gte +0.010 (0.174); detrended +0.049 (0.085) | **failed** (K fires) |
| P2 | A_γ ≠ 0 (p < 0.05) | +0.048 (p 0.71); variants +0.02 to +0.11 (p ≥ 0.37) | failed |
| P3 | no within-team alternation | message-level ρ_same +0.30 (gte +0.20), ρ_cross +0.12 | **supported** |
| P4 | L ≠ 0 | −0.071 (p 0.39); unmasked bge −0.17 (p 0.04), gte masked −0.15 (p 0.09), gte unmasked −0.13 (p 0.13) | failed (primary); a consistent negative sign, post hoc |
| P5 | ρ₁^vec > 0 (topic echo) | +0.145 (p 0.0002); +0.18 to +0.19 in variants | **supported** |
| P6 | gte Λ > 0 (p < 0.1) if P1 | P1 failed | n/a |
| N1 | Λ_post < Λ_deb, n.s. | Λ_post −0.18 (p 0.61) | uninformative (no cycle) |
| N2 | ρ₁(visible) < ρ₁(in flight) | Δρ₁ −0.006 (p 0.47) | failed |
| N3 | opponents < teammates (pairs) | −0.047 over 18 pairs (sign-flip p 0.29); gte +0.08 | failed |

**Verdict.** K fires with power ≥ 0.8 at k_× = 0.6, so by the card's rule the hypothesis **fails**. A cycle weaker than k_× ≈ 0.4 at H21-sized noise is not excluded. The observed sign is the opposite of a cycle.

### Findings
1. **Persistence, not ping-pong.** The issue projection keeps a positive memory across turns and across the team line. Per debate, ρ₁ > 0 in 8/10 (bge masked). A common within-debate drift (synthetic W2: ρ₁ +0.26, never a positive Λ) is the closest world.
2. **Teams keep their own line more than they answer the other.** Same-team consecutive messages correlate more (+0.30) than cross-team ones (+0.12). With Λ slightly positive, ρ₂ > ρ₁: each side's line persists, with a weaker shared drift.
3. **The format's alternation stays in the static field.** Raw Gov − Opp projections are positive in 8/10 debates (H21's tilt). All of the speaker alternation is static; none of it is dynamic.
4. **The read gate adds nothing.** Turns that could read the previous move look like turns that could not (Δρ₁ ≈ 0).

### Caveats
- Embeddings encode negation poorly (H21), so a rebuttal that restates the claim reads as agreement on the issue axis. A stance-classified sequence (DQ2/v2.1 reply stance) would test the cycle on the channel where H21/H37 found the antiferromagnet.
- 306 turns in 10 debates; per-debate values are noisy (ρ₁ from −0.41 to +0.66).
- A staggered-field ramp gives Λ false positives in 10% of synthetic worlds; the observed Λ (p 0.08) is below that bar anyway.
- The cycle area L is negative in all four variants (significant in one); this is post hoc and not claimed.

**Claim that stands:** in #12's ten debates the team-centred issue projection is positively correlated across consecutive turns of opposite teams (ρ₁ +0.16, shuffle p 0.002; full-vector echo +0.15), and there is no lag-one alternation beyond the turn-shuffled null (Λ +0.05, p 0.08; power 1.00 for k_× = 0.6, 0.74 for k_× = 0.3). Exclusions: the cycle direction A_γ and area L (null; L's negative sign is post hoc); the natives (uninformative or null); weak cycles (k_× < 0.4) are not excluded.

## Round 2 redirects
- **What the direction is really after:** whether assigned opposition creates a dynamic coupling (answer the other side) or only a static field (hold your side).
- **H132-R1. Stance sequence.** Re-run the turn statistics on DQ10 stance v2.1 (`disagree_validated_agent`) and DQ2 soft stance of each reply to the previous turn: the antiferromagnet lives in stance (H21 1b, H37), so a cycle, if any, should too.
- **H132-R2. Drift model.** Fit a two-component model (common drift + team-specific persistence) to the turn sequence and report the persistence time in turns.
- **H132-R3. Other alternating formats.** #23 chess pairings and #26 runoff speeches as turn sequences with assigned sides (no motion axis; leave-out team axis as in `confirm.py`).

## Notes
- 2026-10-04 22:23 UTC: round 1 started; card filled before any H132 statistic. H21, H37 and H115 cards were read, not edited (a stance v2.1 re-test of H21/H37 and H115's round 1 are running).
- 2026-10-04 22:24–23:10 UTC: scheme built (DQ6 teams agree with H21's labels 58/58); synthetic validation on the real turn skeleton; Amendment A1 written 23:10 UTC before any real-data statistic.
- 2026-10-04 23:11 UTC: real run (5,000 shuffles × 4 variants); summary, estimates; confirm.py frozen (`confirm.sha256`) and dry-run on G12. Guard tested: refuses without `H132_CONFIRM=1`.
- Proposed for `physics-models/DEFINITIONS.md` (not edited): *debate turn*, *team-centred issue projection z_t*, *turn alternation ρ₁, ρ₂, Λ*, *cycle antisymmetry A_γ*, *issue–topic cycle area L*.
