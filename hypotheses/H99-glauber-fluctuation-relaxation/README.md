# H99: Fluctuations predict relaxation (mean-field Glauber)

**Status:** exploratory round 1 done (2026-10-04; non-holdout only). **Fluctuations predict relaxation only where they cannot be tested; where talk coupling is real, the collective outlives the prediction.**
- **Talk has no single-agent memory at minute resolution** (ρ_⊥(1) median 0.006, 70 units), so the HH's log-ratio relaxation time is undefined; a post hoc statistic, the collective memory excess Δρ₁ = ρ_c(1) − ρ_⊥(1)^(1−g_χ), replaces it (Amendment A2).
- **Regime III fails in the slow direction:** period median Δρ₁ = +0.077; #51 +0.067 [0.034, 0.100]; slow calls in 8 of 15 resolved units. The collective talk mode keeps memory that single agents lack: a delayed (read-out) coupling or a conversation field, as H67 measured, not mean-field Glauber.
- **Regime I is consistent but powerless** (Δρ₁ median +0.007; 23 of 25 resolved units consistent): at the observed sub-minute agent clock a fast shared field is flagged in only 0–6% of synthetic replicates, so H67's fast-field reading is neither confirmed nor refuted.
- **Kicks outlive the fluctuation clock:** the #51 nudge response integrates to ×9.5 [7.0, 12.3] the Onsager prediction from its own peak and the agents' activity clock (H04 kernel read as data); human-message kicks decay with λ = 0.54 [0.21, 0.86] per minute in #4c against a predicted 0.15.
- **Content is a field, not a coupling:** g_χ ≈ 0.55, but Δg₁ < 0 in 92% of 60 units (median −0.17).
- Natives: NE42 mixed (the merge collapses g_χ by 0.13–0.22; the relation does not flip), NE14 descriptive, G51 failed. Scorecard A1 B1 C1 D1 E1 F1 G1 H1 I0. `confirm.py` frozen, guarded and dry-run; **not run**.
**Research question (GOALS.md):** **Q2** (what is field and what is coupling?): a fluctuation–relaxation consistency check separates a coupling from a shared field without inferring J. **Q3** second (how close to criticality is the swarm on its coupled channels?).
**Fields:** stat mech (kinetic Ising, linear response, Onsager regression), dynamics, sociophysics
**Literature:** model references in [`physics-models/02-nonequilibrium-ising/README.md`](../../physics-models/02-nonequilibrium-ising/README.md) ("Mean-field forward version", "Susceptibility, response and effective temperature") and [`physics-models/01-inverse-ising/README.md`](../../physics-models/01-inverse-ising/README.md) ("Mean-field forward version"). Glauber, *J. Math. Phys.* 4, 294 (1963)†; Onsager, *Phys. Rev.* 37, 405 (1931)† (regression hypothesis); Cugliandolo, Kurchan & Peliti, *PRE* 55, 3898 (1997)†. No notes file in `literature/` covers kinetic mean-field relaxation.
**Definitions used** (`physics-models/DEFINITIONS.md`): Agent; Population N(t) (active variant: agents with ≥ 30 record minutes that day); Regime; Driving / external field; **Loop gain (equal-time, daily dial)** and **Per-pair correlation ρ̄** (H25 named variants; here pooled per unit on the trimmed grid); **Content soft spin (30-min window)** (H25 named variant, with the DQ5 `style_resid_period` vectors in place of whitened means); **Operator kick classes** (H30). **New named variants proposed for DEFINITIONS.md** (not edited here), defined under Model: *collective / transverse mode (mean-field split)*, *fluctuation gain g_χ*, *relaxation gain g_τ*, *fluctuation–relaxation gap Δg*.
## Standards (2026-10-04)
**Question served:** Q2 (field vs coupling by a second, dynamical observable) and Q3 (the collective talk mode's memory is not Glauber).
**Impostor table:** see "Impostors" below (scheduler removed by design; exogenous field partly; shared priors removed; convergence partly).
**Inputs:** `activity_bins_fixed`, `outages_fixed/stall_minutes`, DQ5 `style_resid_period` vectors (bge and gte), `kicks_classified`; H04/H59 round-1b kernels read as data. Not used: the context ledger (H67 owns the call-clock estimator).
**Two layers:** 34 replication folders (#51 sits in its native folder). Natives: 3 (NE42 mixed, NE14 descriptive, G51 failed).
**Confirm script:** `analysis/confirm.py` (#22, #28, #43; C1–C4), frozen, guarded, dry-run on stand-ins; not run.

**From:** HH81 in `hypotheses/hypohypotheses/HYPOHYPOTHESES.md` · **Models:** `physics-models/02-nonequilibrium-ising/` (primary, mean-field Glauber), `physics-models/01-inverse-ising/` (Curie–Weiss fluctuation relation), `physics-models/09-hawkes/` (rival reading of kick kernels)
**Data inputs (shared tables first):** `activity_bins_fixed` (talk and activity spins), `outages_fixed/stall_minutes` (stall variant), DQ5 `agent_win30_style_resid_period_{bge_small,gte_modernbert}.npy` + `agent_win30.parquet` (content), `kicks_classified` (human messages), `calendar`, `period_units`, `roster`. Read as data only (never recomputed): H04 round-1b kernels (`data/processed/H04-reversible-forcing/r1b/G*.json`), H59 shared call-lag kernel (`data/processed/H59-one-lever-model/G51/results.json`), H25's and H67's per-period rows in `per_period_estimates`.

## Source HH (verbatim from the HH list, including refinements)
Mean-field Glauber predicts response kernels (variant of HH31, HH46; H04). Mean-field dynamics, dm/dt = [−m + tanh(β(J₀m + h))]/τ₀, give a relaxation time τ = τ₀ / (1 − βJ₀(1−m²)). The βJ₀ estimated from fluctuations (HH80) should *predict* how fast responses to kicks decay: a consistency test without learning J. *Check:* predicted vs. measured response decay time per regime.
  *Models:* 02 (mean-field), 09 · *Periods:* non-holdout kicks; NE21 and NE23 for confirmation

## Question
Does the loop gain read from equal-time fluctuations, βJ₀(1−m²), predict how much slower the collective mode relaxes than a single agent, as mean-field Glauber dynamics requires? Run on talk and content (coupled channels, H12, H67), with activity (scheduler-dominated) as the control.

**Why this separates field from coupling.** A coupling raises the collective variance *and* slows the collective mode by the same factor 1/(1 − g). A shared field raises the collective variance by its own amount but relaxes on its own clock. A fast field (shorter-lived than one agent's memory) gives variance without slowing. A slow field gives more slowing than its variance implies. So the sign of the gap Δg = g_τ − g_χ names the impostor, and Δg ≈ 0 is the coupling signature. H67 found that the equal-time talk dial reads fast fields as gain in regime I; this card tests that reading with a second, independent observable.

## Design: two layers (STANDARDS §4)
- **Replication (layer 1):** the common estimator (below) on every eligible non-holdout period unit (`period_units`: ≥ 3 agents with ≥ 30 record minutes on ≥ 1 day, ≥ 120 trimmed minutes). One README per goal period, role `replication`. Units of a split period are reported separately and pooled by a random-effects mean (CLAUDE.md exception (d)). Channels: talk (primary), content (secondary), activity (control).
- **Period-native tests (layer 2), each with its own dated prediction in its folder:**
  - **NE42** (#39 → #40 → #41, two rooms merged into one and split again at a fixed roster): H25 and H67 saw talk coupling vanish in the merged room. Mean field says g_χ and g_τ fall *together*.
  - **NE14** (#36, regime II → III inside one goal): read-out coupling switches on (H67). The relation should hold on both sides, while the gain changes.
  - **G51 kernels** (largest kick sample; H04 and H59 round-1b kernels read as data): mean field predicts that a kick on one agent (a nudge) decays on the *transverse* (single-agent) clock τ_⊥, not on τ_c, and that bystanders respond at order g/N of the target.

## Model
**From:** `physics-models/02-nonequilibrium-ising` (mean-field Glauber), with the Curie–Weiss fluctuation relation of `physics-models/01-inverse-ising`.

**Degrees of freedom.** In a unit, agent i has a state x_i(t) per bin:
- *talk:* s_i(t) = 1 if `activity_bins_fixed.talk` > 0 in minute t, else 0;
- *activity (control):* s_i(t) = 1 if `state` ≥ 3 (acting or talking);
- *content:* v_i(w) ∈ R³², the DQ5 `agent_win30_style_resid_period` vector (bge; gte as check) in 30-min window w, for windows with ≥ 1 agent chat message.

**Fields removed before any statistic.** Each day is trimmed to its all-present window (DQ8: minutes where every agent with ≥ 30 record minutes that day is between its first and last record). Binary spins are centred per agent within each (day, 30-min block): X_it = s_it − ⟨s_i⟩_block (H25's estimator; removes any field slower than 30 min). Content vectors are centred per agent over the unit (removes the agent prior) and by the day mean over all agent-windows (removes the day's shared topic field).

**Mean-field split.** With N_t agents in bin t: the collective mode M_t = Σ_i X_it/√N_t; the transverse part X^⊥_t = X_t − (M_t/√N_t)·1.

**Mean-field Glauber (linearized).** τ₀ ẋ_i = −x_i + (g/N) Σ_j x_j + h_i(t) + noise, g = βJ₀(1−m²). The collective mode relaxes at rate (1 − g)/τ₀; transverse modes relax at 1/τ₀. Detailed balance gives the equal-time statics:

  Var(M)/Var(X^⊥) = 1/(1 − g)  (statics),  ln ρ_c(k) / ln ρ_⊥(k) = 1 − g  (relaxation; exact for point sampling at any lag k).

Both sides contain the same g. Neither needs the J matrix.

**Estimators (per unit, pooled over its trimmed days).**
- **Fluctuation gain** g_χ = 1 − Σ_t p_t / Σ_t c_t, with c_t = M_t², p_t = (Σ_i X_it² − M_t²)/(N_t − 1). Under independence E c_t = E p_t, so g_χ = 0. It equals H25's dial g = 1 − 1/VR in the large-N limit.
- **Relaxation gain** g_τ = 1 − ln ρ_c(1) / ln ρ_⊥(1), with lag-1 autocorrelations over pairs of kept minutes (same day, same block): ρ_c(1) = Σ M_t M_{t+1} / Σ M_t², ρ_⊥(1) = Σ ⟨X^⊥_t, X^⊥_{t+1}⟩ / Σ |X^⊥_t|².
- **Fluctuation–relaxation gap** Δg = g_τ − g_χ. **Prediction of the model:** Δg = 0. Equivalent form: the measured collective relaxation time τ_c = −1/ln ρ_c(1) against the predicted τ_c^pred = τ_⊥/(1 − g_χ), ratio K = τ_c/τ_c^pred.
- **Variants:** multi-lag rates (least-squares slope of ln ρ over k = 1–3); the noise-robust ratio λ = ρ(2)/ρ(1) with signal variances C(1)/λ (white measurement noise cancels; primary for content); stall minutes masked; untrimmed grid; content with the gte model.
- **Uncertainty:** bootstrap over 1-h blocks within days (B = 400; H67: day blocks with ≤ 5 days are anti-conservative). For content, day blocks (30-min windows give too few pairs per hour).

**What each reading predicts for Δg.**
| World | g_χ | g_τ | Δg |
| --- | --- | --- | --- |
| Mean-field Glauber coupling (instantaneous) | g | g | 0 |
| Fast shared field (lifetime ≲ one agent's memory) | > 0 | ≈ 0 | < 0 |
| Slow shared field (lifetime ≫ τ₀, < 30 min) | > 0 | > g_χ | > 0 |
| Read-out coupling delayed by one call (H50, H67) | small | > g_χ | ≥ 0 (size from synthetic) |
| Independent agents | 0 | 0 | 0 (trivial; reported as descriptive) |

**Kick layer.**
- *Field kick on all (talk):* a human message in a room is a field on every agent in the room. Mean field: the room's collective talk excess decays as e^{−t/τ_c}, so τ_kick = τ_c^pred. Measured by the event-triggered average of the room's talk count in minutes 0–20 after the message, minus matched placebo minutes (same day, trimmed window, no human message within ±20 min), and fit as an exponential on the tail after the peak. Rival readings: τ_kick ≈ τ_⊥ (no collective slowing), or τ_kick set by the read-out delay distribution.
- *Kick on one agent (native G51):* the target's self-response R_ii(t) = (1/N) e^{−t/τ_c} + (1 − 1/N) e^{−t/τ_⊥} ≈ e^{−t/τ_⊥}; the bystander response R_ji = (g/(N(1−g)))·R_ii in static weight.

## Data scheme (`scheme/`)
- **Inputs:** `activity_bins_fixed` (pt_date, minute, agent, talk, state), `outages_fixed/stall_minutes` (variant), `calendar` (holdout, goal_no), `period_units` (unit days), `roster` (Claude Code agent excluded), DQ5 `agent_win30.parquet` + `agent_win30_style_resid_period_*.npy`, `kicks_classified` (kind = human_message: t, room, pt_date).
- **Transform (`scheme/build.py`):** per non-holdout unit (held-out days dropped with `common.holdout_mask` and `calendar.holdout`, asserted twice):
  1. day grids N × L for talk and activity; presence = between the agent's first and last record minute (state ≥ 2); agents with < 30 record minutes that day are dropped from that day;
  2. the all-present window per day; days with < 60 kept minutes or < 3 agents dropped;
  3. per agent minute-to-room map from `rooms_timeline` is *not* needed (talk spins are swarm-level); human-message kicks keep their room and are mapped to the unit's agents in that room by the modal room of the agent that day (`rooms_timeline`);
  4. content: agent-window vectors for the unit's days, centred as above.
- **Output:** `data/processed/H99-glauber-fluctuation-relaxation/` with `grids/<unit>.npz` (int8 spins, kept-minute masks; codes only), `content/<unit>.npz`, `kicks/<unit>.parquet`, `results/units.parquet`, `results/periods.parquet`, `synthetic/`, `natives/`, `_provenance.json`. Budget ≤ 100 MB.
- **Regimes covered:** I, II, III (non-holdout). Fits are within unit.

## Observables
Per unit and channel (per period by random-effects pooling):
1. g_χ, g_τ, Δg with 95% CIs; ρ_c(1), ρ_⊥(1); τ_c, τ_⊥, τ_c^pred, K; N, kept minutes (or agent-windows).
2. Variants: multi-lag, noise-robust ratio, stall-masked, untrimmed, gte (content).
3. Talk kick layer: τ_kick (minutes) with CI, τ_c^pred, τ_⊥, number of kicks.
4. The synthetic bias of Δg under the Glauber world at the unit's counts (from the synthetic table) and the bias-corrected Δg.

## Null / baseline
- **The model is the null here:** Δg = 0. Its finite-sample bias at real counts comes from the Glauber synthetic on real masks (axis F).
- **Independent agents:** g_χ CI includes 0. Then consistency is trivial and the period is *descriptive*, not *supported*.
- **Block-shift null (DQ8, trimmed):** each agent's centred series shifted circularly within its (day, 30-min block). It destroys cross-agent structure, so g_χ, g_τ → 0; it sizes the g_χ test (share of units with CI excluding 0 under the null).
- **Rivals:** fast shared field, slow shared field, delayed read-out coupling (the table above). Each is simulated on real masks.

## Impostors (STANDARDS §1)
| Impostor | Relevant? | How H99 removes it | Status |
| --- | --- | --- | --- |
| Scheduler field | yes | All-present trim (DQ8) and 30-min block centring before any statistic; the block-shift null on the trimmed grid; activity is the control channel where the scheduler is the field. A residual fast scheduler field is exactly what Δg < 0 detects. | removed (by design; residual is the measured object) |
| Exogenous field (kickoff, goal, operator) | yes | Day-mean centring removes day-constant goal and kickoff content; 30-min block centring removes slow drives; human messages are the measured kicks in the kick layer. A within-day operator burst is a fast field and shows as Δg < 0. No `goal_fields` regression on the binary channels (the block centring is stronger). | partly |
| Shared model priors | partly | Content uses `style_resid_period` vectors centred per agent (family field removed, H13/DQ5). Binary spins are centred per agent within blocks, which removes each agent's talk propensity. | removed |
| Contemporaneous convergence | partly | g_χ is equal-time and contains convergence; g_τ uses lag-1 pairs. Convergence is a fast common input: it appears as Δg < 0, not as Δg ≈ 0. No in-flight placebo at the call level (H67 owns that estimator). | partly |

## Faithfulness scorecard
Scored per model, mapping and window; 0 = not done or failed, 1 = partial, 2 = passed. Scheme and promotion thresholds: `writeup/paper.tex`, Sec. "Assessing model faithfulness".
**Rival models:** fast shared field; slow shared field; delayed (read-out) coupling (H67, H50); Hawkes self-excitation of individual agents (model 09; relaxation set per agent, no collective slowing).
**Locked holdout used for confirmation:** none yet. `analysis/confirm.py` (frozen, guarded, not run) targets #22 and #28 (regime I) and #43 (regime III), talk channel.

| Axis | Test | Score | Evidence |
| --- | --- | --- | --- |
| A mapping | variables defined from dataset fields; assumptions listed; invariant across families and regimes | 1 | Spins, trims and modes come from `activity_bins_fixed` and DQ5. An assumption was audited and failed: the agent clock is below one minute for talk (ρ_⊥(1) ≈ 0), about 1 min for activity and longer for content, so one estimator does not cover all channels (A1 for activity and content, A2 for talk). |
| B assumptions | stationarity, Markov order, time-rescaling, update-order audit | 1 | Stationarity within 30-min blocks (block centring). Calls survive the stall mask in 90% (talk) and 83% (activity) of units and the untrimmed grid in 76% / 69%. No update-order audit; the 1-min bin is coarser than the talk clock. |
| C adequacy | beats the null hierarchy, day-blocked held-out data | 1 | g_χ beats independence (CI > 0) in 61% of talk units and 95% of content units (block-shift p < 0.1 in 70% of talk units). The model fails where it is testable: Δρ₁ > 0 in regime III. No held-out likelihood. |
| D unfitted predictions | unfitted statistics and the model's signature | 1 | The collective relaxation is predicted from equal-time fluctuations without fitting J. It holds in regime I (Δρ₁ ≈ 0.007) and fails in regime III (+0.077), in content (Δg₁ −0.17) and for kicks (nudge ×9.5; human-message λ 0.54 vs 0.15). |
| E interventional | predicts the change across a natural experiment | 1 | NE42: the merge collapses g_χ (−0.13 [−0.24, −0.002] and −0.22 [−0.36, −0.09]) and the collective memory against #41 (−0.12 [−0.24, −0.004]); the relation does not flip sign at the boundary. NE14 descriptive (one regime-II day). |
| F identifiability | synthetic recovery with village sampling; robust to preprocessing | 1 | A1 synthetic on real masks (τ₀ ≥ 1 min): Glauber consistent in 78–100%, fast field flagged 78% (τ₀ = 1), slow field 69% at lag 2. A2 synthetic at the real talk clock (τ₀ = 15 s): slow field 88–100%, delayed coupling 100% (lag 2), **fast field 0–6% at the real g_χ**. Content: leave-in day centring faked g_χ = −0.21 and was dropped. |
| G ground truth | agrees with known structure | 1 | Agrees with H67 (the regime-III slow calls sit where g_lag > 0), H25 (#40 collapse), H49/H50 (in-window activity gain ≈ 0 in regime III: 17/26 units unresolved), H59 (fat nudge tail) and H25/H26 (content gain is field-like). |
| H comparative | beats the named rivals | 1 | Separates slow fields and delayed coupling from Glauber (regime III, content). Cannot separate a fast field from Glauber at the talk clock (regime I), so the fast-field reading of H67 is untested here. |
| I transfer | holds in other same-mode periods, including the holdout | 0 | Slow calls recur in every resolved regime-II/III period (6 of 6: #35, #36, #37, #41, #42, #51), but no holdout run. |

## Prediction
*Written 2026-10-04 20:22 UTC, before any H99 statistic on real data. Seen beforehand: table schemas and unit counts; published results of H25 (trimmed talk dial ≈ 0.14, activity ≈ 0.10–0.16), H26 (content room gain ≈ 0.5 at day means), H67 (regime-III g_lag ≈ 0.13, regime I ≈ 0; equal-time dial reads fast fields in regime I, g_eq − g_lag ≈ +0.17), H49 (regime-III activity excess is a dense shared field), and the published H04 round-1b nudge-kernel summaries (G51 A30 1.16, t50 14 min). Not seen: any H99 statistic.*

**Synthetic (axis F), before real data.** Binary spins simulated with fine time steps (10 s) and binned to minutes on the real trimmed masks of four units (regime I and III), and content vectors on two units' window masks:
- **S1 Glauber recovery:** planted g ∈ {0.1, 0.2, 0.4}: g_χ and g_τ within ±0.05 of each other (median |Δg| ≤ 0.05 after the bias table), and the 95% CI of Δg covers 0 in ≥ 80% of replicates. [0.65]
- **S2 fast field:** a shared field with lifetime 1 min and no coupling, sized to g_χ ≈ 0.15: Δg < −0.05 with CI excluding 0 in ≥ 70% of replicates. [0.6]
- **S3 slow field:** lifetime 10 min, no coupling, g_χ ≈ 0.15: Δg > +0.05 with CI excluding 0 in ≥ 70%. [0.6]
- **S4 delayed coupling:** responses at a 1–3 min delay, gain 0.15: Δg ≥ 0 (reported, no threshold).
- **S5 independent:** g_χ CI excludes 0 in ≤ 10% (size). [0.8]
- **S6 identifiability (I₂-style check for this card):** at the smallest units (N = 4, ≈ 3 days), the CI half-width of Δg is ≤ 0.15; units above that are reported but not given a verdict. [0.5]

**Real data (exploratory, non-holdout).**
- **P1 (talk, regime III: coupling).** In regime-III periods with g_χ resolved (CI > 0), Glauber consistency holds: bias-corrected |Δg| < 0.10 with the CI covering 0 in ≥ 60% of those periods; median Δg in [−0.05, +0.10]. *Counts against:* |Δg| ≥ 0.10 with CI excluding 0 in > 50% of regime-III periods. [0.45]
- **P2 (talk, regime I: fast field).** Regime-I talk fails consistency in the fast-field direction: Δg < 0 (CI excluding 0) in ≥ 60% of regime-I periods with g_χ resolved; median g_τ < g_χ/2. *Counts against:* median Δg ≥ 0. [0.55]
- **P3 (activity, control).** Activity fails consistency (CI of Δg excludes 0) in ≥ 50% of resolved periods, either sign. *Counts against:* activity consistent as often as talk in regime III. [0.5]
- **P4 (content, slow topic field).** Content Δg ≥ 0 in ≥ 60% of resolved periods (topics outlive one agent's memory); Glauber consistency in < 50%. Low power expected (≈ 8 windows per agent-day). [0.4]
- **P5 (talk kicks).** For units with ≥ 30 human-message kicks in the trimmed window, τ_kick lies within [0.5, 2] × τ_c^pred in ≥ 60%, and is closer to τ_c^pred than to τ_⊥ in ≥ 60%. *Counts against:* τ_kick ≈ τ_⊥ in most units (no collective slowing in the response). [0.35]
- **P6 (subcritical).** Every unit's g_χ and g_τ upper bounds < 0.6 on talk and activity (H25, H67). [0.8]

### Synthetic result (axis F) and Amendment A1 (2026-10-04 20:41 UTC, after the synthetic, before any H99 statistic on real data)
Runs: `analysis/synthetic.py` (binary spins at 10-s substeps on the real trimmed masks of units 8, 27, 38a, 51g; 8 replicates per cell; τ₀ = 1 and 3 min; minute observation "any substep", plus point sampling) and `analysis/synthetic_content.py` (32-d content on the real agent-window masks of 40 and 51g; 6 replicates; measurement noise 0 or equal to the signal). Tables: `data/processed/H99-glauber-fluctuation-relaxation/synthetic/`. Disclosure: per-agent real talk rates were read to set the simulated rates; one smoke test printed the unit count of content blocks.

| World (binary, talk-like) | τ₀ | g_χ (median) | Δg₁ (lag 1) | Δg₂ (lag 2) | consistent / fast call / slow call (rule below) |
| --- | --- | --- | --- | --- | --- |
| independent | 1, 3 | −0.01, 0.00 | +0.01 | −0.03, 0.00 | 1.00 / 0 / 0 |
| Glauber g = 0.1 | 1, 3 | 0.13, 0.10 | −0.03, −0.01 | +0.04, +0.01 | 0.81–0.88 / ≤ 0.09 / ≤ 0.09 |
| Glauber g = 0.2 | 1, 3 | 0.28, 0.21 | −0.04, −0.02 | +0.01, −0.02 | 0.78–1.00 / ≤ 0.16 / ≤ 0.06 |
| Glauber g = 0.4 | 1, 3 | 0.76, 0.66 | −0.01, −0.02 | +0.03, −0.01 | 0.91–1.00 / 0 / ≤ 0.09 |
| fast field (lifetime 15 s) | 1, 3 | 0.17, 0.08 | −0.14, −0.05 | −0.21, −0.06 | fast call 0.78 (τ₀ = 1), 0.16 (τ₀ = 3) |
| slow field (lifetime 10 min) | 1, 3 | 0.19, 0.09 | +0.04, +0.02 | +0.17, +0.03 | slow call 0.69 (τ₀ = 1), 0.06 (τ₀ = 3) |
| delayed coupling (2 min, g = 0.15) | 1, 3 | 0.01, 0.08 | +0.07, +0.03 | +0.33, +0.07 | slow call 0.97 (τ₀ = 1), 0.38 (τ₀ = 3) |

- **S1 (Glauber recovery): mixed.** Median |Δg₁| ≤ 0.04 in every Glauber cell, but the lag-1 CI covers 0 in only 59–69% of replicates at g ≥ 0.2 with τ₀ = 1 min. Minute binning of a sub-minute process biases Δg₁ by about −0.04 there.
- **S2 (fast field): passes at τ₀ = 1 min (0.78), fails at τ₀ = 3 min (0.34).**
- **S3 (slow field): fails at lag 1** (0.31 and 0.09). A 10-min field and a coupling look alike at one minute. **Lag 2 separates them at τ₀ = 1 min (0.69).**
- **S4 (delayed coupling): Δg ≥ 0, as tabled**; at lag 2 the delay world is flagged in 97% (τ₀ = 1).
- **S5 (size of g_χ under independence): 6%.** **S6 (N = 4 unit): Δg₁ half-width 0.07.** Both pass.
- **Content:** a leave-in day-mean centring fakes anti-correlation (g_χ = −0.21 for independent agents; model 12's warning). With agent centring only, independent and Glauber worlds give |Δg₁| ≤ 0.03 (CI covers 0 in 67–100%). A white shared field per window gives Δg₁ ≈ −1.3 to −2.6 (always flagged). An OU field with coefficient 0.8 per window gives Δg₁ = −0.04 to −0.25: a content field that decays at the rate Glauber predicts for its variance cannot be told from coupling. The noise-robust variant is biased (−0.10 to +0.44 under independence) and is dropped.

**Amended rule (applies to every real-data verdict):**
1. Two lags. **Fast-field call:** Δg₁ < −0.08 with its CI below 0. **Slow-field or delayed-coupling call:** Δg₂ > +0.08 with its CI above 0. **Consistent:** neither call. With these thresholds the false-call rate in Glauber worlds is ≤ 16% per arm (≤ 22% combined).
2. **Power depends on the agent clock.** Each unit reports ρ_⊥(1). Where ρ_⊥(1) ≥ 0.6 (τ₀ ≳ 2 min), "consistent" cannot exclude fields (detection ≤ 0.38): the unit's verdict is *descriptive*, not *supported* (STANDARDS §3).
3. The table "What each reading predicts" is read relative to the Glauber prediction: Δg < 0 means the collective decays faster than τ₀/(1 − g_χ) (a field shorter-lived than that), Δg > 0 slower.
4. Content: agent centring only (no day centring); lag 1 and lag 2 as for binary spins; the noise-robust variant is dropped.
5. Predictions P1–P6 stand as written, with "consistent" and "Δg < 0 / > 0" read through this rule (P2's "Δg < 0 with CI excluding 0" becomes the fast-field call).

### Amendment A2 (2026-10-04 20:45 UTC, **post hoc**: after the first real-data run)
The first real run showed that **talk minutes carry no single-agent memory**: ρ_⊥(1) is −0.09 to 0.17 across the 70 units (it is near the −1/29 bias of 30-min block centring), while ρ_c(1) is 0.0–0.28. The agent clock τ₀ is below one minute, outside the A1 synthetic (τ₀ ≥ 1 min). There the log-ratio g_τ is undefined (ρ_⊥ ≤ 0) or unstable, so the A1 talk rule cannot be applied. Activity (ρ_⊥(1) ≈ 0.2–0.35) and content (0.3–0.5) are inside the A1 range and keep the A1 rule.

**A2 statistic (robust at ρ_⊥ ≈ 0):** the collective memory excess Δρ_k = ρ_c(k) − max(ρ_⊥(k), 0.001)^(1 − g_χ). Glauber predicts Δρ_k = 0 at any agent clock. A field slower than the Glauber prediction or a delayed coupling gives Δρ > 0; a fast field gives Δρ < 0.

**A2 synthetic** (`analysis/synthetic_a2.py`, units 27 and 51g, 8 replicates, τ₀ = 0.25 min so that ρ_⊥(1) ≈ 0.03 as in the data):

| World (τ₀ = 0.25 min) | g_χ | Δρ₁ | Δρ₁ CI > 0 / < 0 | Δρ₂ | Δρ₂ CI > 0 |
| --- | --- | --- | --- | --- | --- |
| independent | 0.01 | 0.00 | 0.06 / 0 | −0.04 | 0 |
| Glauber g = 0.2 | 0.29 | 0.00 | 0.06 / 0.06 | −0.05 | 0 |
| Glauber g = 0.4 | 0.81 | +0.02 | 0.31 / 0 | +0.02 | 0 |
| fast field (15 s) | 0.55 | −0.10 | 0 / 0.88 | −0.09 | 0 |
| slow field (10 min) | 0.34 | +0.20 | 1.00 / 0 | +0.21 | 1.00 |
| delayed coupling (2 min) | 0.01 | −0.01 | 0.06 / 0 | +0.08 | 1.00 |

At τ₀ = 1 min the same statistic is biased (Glauber g = 0.2: Δρ₁ = −0.025, CI below 0 in 56%), which is why activity keeps the A1 rule.

**A2 power check** (`analysis/synthetic_a2_power.py`, post hoc, field sizes giving the real talk range g_χ ≈ 0.07–0.28): a sub-minute shared field is flagged as fast in 0–6% of replicates (g_χ 0.15–0.28), so **at the observed agent clock a fast field and a Glauber coupling cannot be told apart at minute resolution**. A 10-min field is flagged as slow in 88–100% (g_χ 0.07–0.15). Consequence: under A2, "consistent" is reported as *consistent (low power)* and makes a period *descriptive*, not *supported*; only slow calls carry information.

**A2 rule (talk, and any unit with ρ_⊥(1) < 0.15):** fast-field call if Δρ₁ ≤ −0.03 with CI below 0; slow-field or delayed-coupling call if Δρ₁ ≥ +0.03 or Δρ₂ ≥ +0.03 with that CI above 0; consistent otherwise. Units with ρ_⊥(1) ≥ 0.15 use the A1 rule. **This rule was chosen after seeing ρ_c(1) and ρ_⊥(1) of the talk units** (from which Δρ₁ follows), so every talk verdict below is labelled post hoc. Predictions P1–P6 are scored as written, through this rule.

**What would count against H99 as a whole:** Δg excluding 0 in the majority of resolved talk periods of *both* regimes, with no sign pattern by regime: the fluctuation gain then predicts nothing about relaxation, and the equal-time dial cannot be read as βJ₀(1−m²) anywhere.

## Results by goal period
| Period | Role | Verdict | Key numbers |
| --- | --- | --- | --- |
| [G02](goalperiod-subhypotheses/G02/README.md) | replication | descriptive | talk g_χ 0.57, Δρ₁ -0.096; activity failed |
| [G03](goalperiod-subhypotheses/G03/README.md) | replication | descriptive | talk g_χ nan, Δρ₁ n/a; activity descriptive |
| [G04](goalperiod-subhypotheses/G04/README.md) | replication | mixed | talk g_χ 0.37, Δρ₁ -0.078; activity failed; content Δg₁ -0.126 |
| [G05](goalperiod-subhypotheses/G05/README.md) | replication | descriptive | talk g_χ 0.11, Δρ₁ +0.020; activity descriptive; content Δg₁ -0.326 |
| [G06](goalperiod-subhypotheses/G06/README.md) | replication | descriptive | talk g_χ 0.23, Δρ₁ +0.011; activity supported; content Δg₁ -0.061 |
| [G07](goalperiod-subhypotheses/G07/README.md) | replication | descriptive | talk g_χ 0.13, Δρ₁ +0.021; activity descriptive |
| [G08](goalperiod-subhypotheses/G08/README.md) | replication | descriptive | talk g_χ -0.02, Δρ₁ +0.004; activity failed; content Δg₁ -0.100 |
| [G10](goalperiod-subhypotheses/G10/README.md) | replication | descriptive | talk g_χ 0.22, Δρ₁ +0.045; activity supported; content Δg₁ -0.386 |
| [G11](goalperiod-subhypotheses/G11/README.md) | replication | descriptive | talk g_χ 0.20, Δρ₁ +0.154; activity descriptive; content Δg₁ -0.263 |
| [G12](goalperiod-subhypotheses/G12/README.md) | replication | descriptive | talk g_χ 0.23, Δρ₁ -0.004; activity descriptive; content Δg₁ -0.722 |
| [G13](goalperiod-subhypotheses/G13/README.md) | replication | supported | talk g_χ 0.10, Δρ₁ -0.070; activity descriptive; content Δg₁ -0.174 |
| [G16](goalperiod-subhypotheses/G16/README.md) | replication | failed | talk g_χ 0.32, Δρ₁ -0.111; activity supported; content Δg₁ -0.113 |
| [G17](goalperiod-subhypotheses/G17/README.md) | replication | descriptive | talk g_χ 0.43, Δρ₁ -0.047; activity failed; content Δg₁ -0.240 |
| [G18](goalperiod-subhypotheses/G18/README.md) | replication | descriptive | talk g_χ 0.33, Δρ₁ -0.026; activity failed; content Δg₁ -0.290 |
| [G19](goalperiod-subhypotheses/G19/README.md) | replication | descriptive | talk g_χ 0.31, Δρ₁ +0.024; activity failed; content Δg₁ -0.375 |
| [G20](goalperiod-subhypotheses/G20/README.md) | replication | descriptive | talk g_χ 0.18, Δρ₁ +0.066; activity descriptive; content Δg₁ -0.193 |
| [G21](goalperiod-subhypotheses/G21/README.md) | replication | descriptive | talk g_χ 0.21, Δρ₁ -0.010; activity failed; content Δg₁ -0.150 |
| [G23](goalperiod-subhypotheses/G23/README.md) | replication | descriptive | talk g_χ 0.22, Δρ₁ -0.038; activity descriptive; content Δg₁ -0.092 |
| [G24](goalperiod-subhypotheses/G24/README.md) | replication | descriptive | talk g_χ 0.22, Δρ₁ +0.059; activity descriptive; content Δg₁ -0.186 |
| [G25](goalperiod-subhypotheses/G25/README.md) | replication | descriptive | talk g_χ 0.20, Δρ₁ +0.048; activity descriptive; content Δg₁ -0.298 |
| [G26](goalperiod-subhypotheses/G26/README.md) | replication | descriptive | talk g_χ 0.38, Δρ₁ +0.093; activity supported; content Δg₁ -0.266 |
| [G27](goalperiod-subhypotheses/G27/README.md) | replication | descriptive | talk g_χ 0.08, Δρ₁ -0.016; activity failed; content Δg₁ -0.176 |
| [G30](goalperiod-subhypotheses/G30/README.md) | replication | descriptive | talk g_χ 0.21, Δρ₁ -0.017; activity descriptive; content Δg₁ -0.196 |
| [G31](goalperiod-subhypotheses/G31/README.md) | replication | descriptive | talk g_χ 0.09, Δρ₁ +0.047; activity descriptive; content Δg₁ -0.229 |
| [G33](goalperiod-subhypotheses/G33/README.md) | replication | descriptive | talk g_χ 0.10, Δρ₁ +0.020; activity descriptive; content Δg₁ -0.240 |
| [G35](goalperiod-subhypotheses/G35/README.md) | replication | failed | talk g_χ 0.13, Δρ₁ +0.086; activity descriptive; content Δg₁ -0.282 |
| [G36](goalperiod-subhypotheses/G36/README.md) | replication | failed | talk g_χ 0.17, Δρ₁ +0.049; activity supported; content Δg₁ +0.071 |
| [G37](goalperiod-subhypotheses/G37/README.md) | replication | failed | talk g_χ 0.26, Δρ₁ +0.098; activity supported; content Δg₁ -0.108 |
| [G38](goalperiod-subhypotheses/G38/README.md) | replication | descriptive | talk g_χ 0.10, Δρ₁ -0.010; activity supported; content Δg₁ -0.136 |
| [G39](goalperiod-subhypotheses/G39/README.md) | replication | descriptive | talk g_χ 0.11, Δρ₁ -0.010; activity descriptive; content Δg₁ -0.089 |
| [G40](goalperiod-subhypotheses/G40/README.md) | replication | descriptive | talk g_χ -0.01, Δρ₁ -0.032; activity descriptive; content Δg₁ -0.240 |
| [G41](goalperiod-subhypotheses/G41/README.md) | replication | failed | talk g_χ 0.21, Δρ₁ +0.086; activity descriptive; content Δg₁ -0.307 |
| [G42](goalperiod-subhypotheses/G42/README.md) | replication | mixed | talk g_χ 0.20, Δρ₁ +0.105; activity descriptive; content Δg₁ -0.055 |
| [G44](goalperiod-subhypotheses/G44/README.md) | replication | descriptive | talk g_χ 0.02, Δρ₁ +0.088; activity descriptive; content Δg₁ -0.244 |
| [G51](goalperiod-subhypotheses/G51/README.md) | native | failed | nudge response ×9.5 the Onsager prediction; talk 4/9 consistent |
| [NE14](goalperiod-subhypotheses/NE14/README.md) | native | descriptive | 36c slow (Δρ₁ +0.137); 36a, 36b unresolved |
| [NE42](goalperiod-subhypotheses/NE42/README.md) | native | mixed | g_χ #40 − #39 = −0.13, − #41 = −0.22; #41 slow call |

## Results
### Round 1 (2026-10-04): exploratory, non-holdout
Tables: `data/processed/H99-glauber-fluctuation-relaxation/results/` (`units.parquet` → `units_called.parquet`, `periods.parquet`, `kicks.parquet`, `scoring.json`), `natives/`, `synthetic/`. Code: `scheme/build.py`, `analysis/{h99lib,run,synthetic,synthetic_content,synthetic_a2,synthetic_a2_power,summarize,natives,native_estimates,confirm}.py`. Figures: `figures/summary_obs.pdf`, `figures/synthetic.pdf`. 70 non-holdout units (35 goal periods; 51b dropped: empty all-present window), 61,548 trimmed talk minutes; estimates rows: 399 replication + 5 native in `per_period_estimates`.

**Predictions scored (as written, read through A1/A2):**
| Prediction | Observed | Verdict |
| --- | --- | --- |
| S1–S6 synthetic | S1 mixed (lag-1 CI covers 0 in 59–69% at g ≥ 0.2, τ₀ = 1), S2 pass at τ₀ = 1 / fail at 3, S3 fail at lag 1 (lag 2 passes), S4–S6 pass | 3/6 pass, 2 partial |
| P1 regime-III talk consistent in ≥ 60% of resolved periods | 0 of 4 resolved regime-III periods consistent; units: 8 slow vs 7 consistent (low power); median Δρ₁ +0.077 | **failed** (slow direction) |
| P2 regime-I talk fails as a fast field | 2 fast calls in 25 resolved units; A2 power for a fast field of that size 0–6% | **not testable** |
| P3 activity fails consistency in ≥ 50% of resolved periods | 9 of 16 resolved periods fail (8 regime I, fast direction; #51); regime-III activity is mostly unresolved (g_χ ≈ 0 in the trimmed window) | supported |
| P4 content Δg ≥ 0 in ≥ 60%; consistent in < 50% | Δg₁ < 0 in 92% of 60 units (median −0.17); consistent in 30% | **failed** (sign), second clause holds |
| P5 human-message kicks: τ_kick within ×0.5–2 of the Glauber prediction | decay resolved in 1 of 8 units (#4c: λ 0.54 [0.21, 0.86] vs 0.15) | **failed** (slower than predicted) |
| P6 every g_χ upper bound < 0.6 (talk, activity) | talk: all but #2 (175 min, 3–4 agents); activity: all but #6a (0.63) and #10a (0.75) | mostly supported |

**Reading.**
- *Talk.* Agents carry no minute-scale memory of their own talk, but the swarm's collective talk mode does. In regime III the collective memory exceeds what the equal-time gain predicts in every resolved period (#51 Δρ₁ = 0.067 [0.034, 0.100]). That is the signature the synthetic gives for a coupling delayed by one call or for a conversation field slower than the agents, and it sits where H67 measured read-out coupling (g_lag ≈ 0.13). The equal-time dial g_χ (median 0.15) therefore is not βJ₀(1−m²) of a Glauber swarm in regime III; it is the instantaneous slice of a delayed interaction.
- *Regime I* passes the consistency check, but the check has no power there: with a sub-minute agent clock, a sub-minute shared field and an instantaneous coupling both predict zero lag-1 memory.
- *Activity* in regime I fails in 8 of 12 resolved periods, mostly in the fast-field direction (8 fast vs 2 slow unit calls): synchronous scheduled turns. In regime III the trimmed activity gain is unresolved in 17 of 26 units, as H49 and H50 found.
- *Content* is field-like everywhere: the collective co-alignment (g_χ ≈ 0.55, both embedding models; gte keeps the call in 87%, Spearman 0.82 for Δg₁) decays faster than a Glauber mode of that variance would.
- *Kicks* do not relax on the fluctuation clock. A nudge's 30-min response is ×9.5 the Onsager value; human messages ring for about two minutes when spontaneous talk forgets in under one. The read-out delay and the nudger's selection (H59) are the likely carriers.

### Round 2 (2026-10-04): call clock, two-timescale kernel, receiving-call kicks, scheduler removal
*Design, predictions, nulls and kill rules written 2026-10-04 21:20 UTC, before any round-2 statistic on real data and before the round-2 synthetic. Seen beforehand: every round-1 H99 number above; H67's published per-unit g_lag, J₁* and named/unnamed split; H40's per-call decay (φ −0.60); H86's c_× summary (0.008 trimmed); H59's call-lag kernel; the Known issues on nudge selection and receiving-call alignment. Not seen: any call-clock talk statistic, any removal-stack Δρ₁, any partition, any receiving-call kick kernel.*

**Scope.** Non-holdout units only (`holdout_mask` asserted). Primary: regime III (the round-1 slow calls). Regimes I and II are reported descriptively. Inputs added (behind the `--round 2` switch; round 1 reproduces unchanged): `call_windows`, `context_ledger_turns` (room, item counts), `chat_core` + `chat_mentions_clean` (message times, rooms, names), `kicks_receipts` + `kicks_targets` (receiving calls of human messages and nudges), `kicks_classified` (exogenous mask), H86's `taylor_c_shared` (activity_trim) and H67's `readout_loop_gain_g_lag` rows in `per_period_estimates` (read as data).

**R1. Per-call clock (Glauber vs one-call-delayed coupling).** Each agent's receiving calls (`ctx_mode != summary`) inside the DQ8 call-based all-present window (agents with ≥ 20 calls that day), ordered by (`t_call`, `turn_id`). Outcome Y_ic = the call talks. Per call c of recipient i, other agents' messages counted in windows aligned on t_c, with w_c = clip(t_first − t_call, 1 s, 120 s) (H67's matched lag):
- *hop 0, in flight* P⁰: posted in i's room in (t_c, t_c + w_c) (cannot be read at c);
- *hop 1, read* R¹: posted in i's room in [max(t_{c−1}, t_c − w_c), t_c) (read at c, matched lag), and R¹ᵒ for older reads at c;
- *hop 2, read one call earlier* R²: everything read at c − 1;
- *cross-room* X⁰, X¹, X²: messages posted in other rooms in the same three windows (never readable; they share any village-wide drive at the identical lag);
- each split into messages that name i (`mentions_roster`) and the rest.
Linear-probability model with agent × day × call-class fixed effects (class = chat/cu × wake/ordinary), own lags Y_{c−1}, Y_{c−2} and exogenous reads (human, nudge). 1-h block bootstrap (B = 200).
- *Single-agent memory on the call clock:* ρ_s = lag-1-call autocorrelation of Y centred within (agent, day, 30-min block).
- *Kernel:* placebo-corrected per-message responses J_h = β(R^h) − β(X^h) (room gate, same window) and J₁* = β(R¹) − β(P⁰) (H67's in-flight gate). In loop-gain units g_h = m̄ r̄ J_h (m̄ messages per talk call, r̄ readers per message).
- *Readings:* instantaneous Glauber or a fast field puts the response at hop 0 (β(P⁰) ≈ β(R¹)); read-out Glauber on the call clock (Markov) puts it at hop 1 only (J₂ ≈ 0 given Y_{c−1}); one-call-delayed coupling gives J₂ > 0; a slow common drive gives β(R^h) ≈ β(X^h) ≈ β(P⁰) at every hop, the same for named and unnamed messages.

**R2. Two-timescale kernel fitted to the minute-grid collective memory.** A simulator on each regime-III unit's real call skeleton (real agents, call times, latencies, rooms, per agent × day × class talk rates; one synthetic message per talk call, posted at t_first; readers by the ledger's visibility rule; named share and a ×19 named boost as H67) plants an instantaneous shared field of amplitude g₀ (lifetime 15 s) and a one-call (hop-1) read-out coupling g₁ = r̄ J. The minute grid is built the same way for real and synthetic data (talk minute = a talk message posted in that minute, keep = the call-based all-present window). Indirect inference: g₁ grid {0, 0.1, 0.2, 0.3, 0.45}, 3 replicates each, g₀ set so that g_χ matches the unit; g₁,fit is where the synthetic Δρ₁ curve meets the real Δρ₁ (CI by inverting the real Δρ₁ CI). **Test:** g₁,fit against H67's g_lag for the same unit (read as data).

**R4. Kicks on the receiving call.** Human messages (each room recipient) and nudges (leading-@ primary target, `kicks_targets`) are aligned on each recipient's receiving call (`kicks_receipts.t_call`, same day). Outcomes: activity (state ≥ 3) and talk in minutes k = 0…29 after the receiving call's minute (grid of round 1), and talk on calls n = 0…10 after it. Placebo: the same agent's receiving calls of the same day and class (wake vs ordinary) with no exogenous item read and no kick read in the previous 30 min (past-only matching; future kicks are never used, Known issues). G(k) = kicked − placebo mean of the agent-day-class stratum. **Onsager prediction from spontaneous regression on the same clock:** S(k) = placebo trajectory − agent-day mean; A30_Ons = G(0) Σ_k S(k)/S(0). **Statistic:** Ω = Σ_k G(k) / A30_Ons, with stratum-block bootstrap CI. Round 1's ×9.5 used H04's message-aligned kernel and a geometric minute-grid ρ_⊥ = 0.34.

**Scheduler-field removal (minute grid, talk).** Round-1 estimator with these removals stacked:
- V1 *call windows:* talk spins centred within (agent, day, 30-min block, call-occupancy class: 0, 1–3, ≥ 4 receiving calls starting in the minute), so co-movement in call availability (synchronized wakes, stalls) is removed;
- V2 *day edges:* first and last 30 min of each all-present window dropped (H76: the excess sits at the day end);
- V3 *exogenous drives:* minutes in [t, t + 15 min] after any human message, nudge or operator message (`kicks_classified`) masked, and the first 60 min of a kickoff day dropped;
- V4 *shared activity field:* each agent's talk spin residualized (OLS) on the leave-one-out collective act-only mode (state 3, not talking) at lags −1, 0, +1;
- V5 = V1 + V2 + V3 + V4.
- *c_× gauge:* Spearman of the unit's Δρ₁ (main and V5) with H86's `taylor_c_shared` (activity_trim) across regime-III units.

**Partition contrast (the drive does not know the gate).**
- *Minute grid, room gate:* for units with ≥ 2 rooms of ≥ 2 agents, per-pair lag-1 correlations r_ij(1) = Σ_t (X_it X_j,t+1 + X_jt X_i,t+1)/2 / √(V_i V_j) (V5 spins), averaged over same-room pairs and cross-room pairs (modal room of the day). With ρ_⊥ ≈ 0, Glauber predicts r_ij(1) ≈ 0, so r_ij(1) is the per-pair memory excess. Ratio Π = r̄_same(1) / r̄_cross(1) and the share of the cross-agent lag-1 covariance carried by same-room pairs.
- *Call clock, address and read gates:* named vs unnamed J₁*, read vs in-flight (β(R¹) vs β(P⁰)), same-room vs cross-room (β(R¹) vs β(X¹)).

**Nulls and validation (before real data).** Worlds on the real skeletons of 38a, 41, 51c and 51g (6 replicates): W0 independent talk at the real call times (keeps the real scheduler and call-window structure); W1 hop-1 read-out coupling g₁ = 0.13 and 0.30; W2 one-call-delayed coupling (response at the call after the read call) g = 0.13; W3 slow village-wide drive (OU, lifetime 5 min) sized to give Δρ₁ ≈ 0.08 on the minute grid; W4 the same drive per room; W5 fast field (15 s). Required: V5 removes ≥ 70% of Δρ₁ in W0; the room partition gives Π CI covering 1 in W3 in ≥ 80% of replicates and Π > 2 in W1 (g = 0.30) in ≥ 70%; the call-clock J₂ separates W2 from W1 (J₂ CI > 0 in ≥ 70% of W2, ≤ 15% of W1); g₁,fit recovers the planted g₁ within ×[0.5, 2] in W1. Any failure is reported and the affected test is labelled before real data (dated amendment).

**Predictions (real data, exploratory).**

| # | Prediction | Counts against | Credence |
| --- | --- | --- | --- |
| Q-R1a | Single-agent talk memory is resolvable on the call clock: ρ_s CI excludes 0 in ≥ 70% of regime-III units; median ρ_s > 0 | ρ_s CI covers 0 in > 50% of regime-III units | 0.7 |
| Q-R1b | The response is not instantaneous: pooled regime III β(P⁰) ≤ ⅓ β(R¹) for named messages | β(P⁰) ≥ β(R¹) | 0.75 |
| Q-R1c | The kernel outlasts one call: pooled regime III J₂ > 0 (CI) with J₂/J₁ in [0.2, 0.8] (H40's per-call decay) | J₂ CI covers 0 and J₂/J₁ < 0.1 | 0.5 |
| Q-R2 | The minute-grid memory needs no more coupling than reading supplies: g₁,fit / g_lag in [0.5, 2] for the regime-III median and in ≥ 60% of resolved regime-III units | median ratio > 2 (residual drive) or < 0.5 | 0.4 |
| Q-S1 | Δρ₁ survives scheduler removal: V5 regime-III median ≥ +0.04 and the #51 random-effects pool CI excludes 0 | V5 median < +0.02 with the #51 CI covering 0 | 0.6 |
| Q-S2 | Δρ₁ does not track the shared-field gauge: Spearman(Δρ₁ V5, c_×) ≤ 0.3 across regime-III units | ≥ 0.5 with p < 0.05 | 0.6 |
| Q-P1 | Room gate on the minute grid: pooled regime III Π ≥ 2, cross-room r̄(1) CI covers 0 | Π CI covers 1 | 0.55 |
| Q-P2 | Address and room gates on the call clock: named J₁* ≥ 5 × unnamed; \|β(X¹)\| below the unnamed β(R¹) | named ≤ 2 × unnamed, or β(X¹) ≥ β(R¹) | 0.65 |
| Q-R4a | The nudge's Onsager violation does not survive the receiving call: #51 Ω ≤ 2 | Ω CI above 2 | 0.55 |
| Q-R4b | Human-message kicks obey Onsager on the receiving call: regime-III pooled Ω in [0.5, 2] | Ω CI outside [0.5, 2] | 0.45 |

**Kill rules (fixed now).**
- **Slow-drive rival wins** (round-1 regime-III claim withdrawn) if Q-S1 counts against *or* both partitions fail (Π CI covers 1 *and* named J₁* ≤ 2 × unnamed).
- **Coupling claim stands** only if Q-S1 holds, at least one partition passes (Π > 1 with CI, or named ≥ 5 × unnamed with β(X¹) ≈ 0), and Q-R2 is not contradicted in the residual-drive direction.
- **The ×9.5 is withdrawn** if Ω ≤ 2 (Q-R4a holds); it survives if Ω's CI lies above 2.
- All talk statistics stay labelled post hoc in the A2 sense (the round-2 tests target a statistic chosen after round-1 data); the round-2 predictions themselves are pre-registered here.

## Round 2 redirects
- **What the direction is really after:** a dynamical check that tells a coupling from a field without inferring J, on the clock at which agents actually update.
- **H99-R1. Per-call clock.** Re-index talk on each agent's call sequence (H40, H67) so the single-agent memory is resolvable and Glauber vs one-call-delayed coupling separate at hop 1.
- **H99-R2. Two-timescale kernel.** Fit an instantaneous-plus-one-call collective kernel and test whether the delayed amplitude equals H67's g_lag.
- **H99-R3. Regime-I power.** Simulate sub-minute fields from call logs at 10-s resolution to restore power against the fast-field reading.
- **H99-R4. Kicks on the receiving call.** Align human-message kicks on each recipient's receiving call (DQ1) before fitting the decay; compare with the collective memory excess.
- **H99-R5. Content fields.** Residualize content on goal_fields and operator-message directions within the day, then repeat the A1 test.

## Notes
- 2026-10-04: card written from the HH81 stub.
- 2026-10-04: the A1 synthetic covered agent clocks τ₀ ≥ 1 min; the real talk clock is shorter (A2, post hoc). The A2 statistic and rule were chosen after ρ_c(1) and ρ_⊥(1) of the talk units had been seen, so all talk verdicts are labelled post hoc in the estimates table.
- 2026-10-04: the H04 and H59 kernels were read from their round-1b outputs as data; nothing of H04/H59 was recomputed or imported.
- 2026-10-04: activity kernels from H04 are aligned on the receiving call; the Onsager prediction uses the #51 activity ρ_⊥(1) pooled over 11 units (0.34). HH81 names NE21 and NE23 for confirmation; both are in the locked holdout and were used by H04's executed run, so H99's confirm targets are #22, #28 and #43 (talk), disclosed in `confirm.py`.
