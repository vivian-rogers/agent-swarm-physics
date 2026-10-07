# H130: #51 agents are Ornstein–Uhlenbeck particles in private wells: reads kick them and the kick decays at the well's rate

**Status:** exploratory round 1 done (2026-10-04; non-holdout only). **Failed as posed (kill K1): reads do kick #51 agents, but the kick is a fast transient that decays about 15× faster than the agent's own well.**
- **Reads kick (K2 not met).** The read-minus-in-flight jump is positive in 11/12 units and every unit with ≥ 3 days: pooled J_K 0.044 [0.038, 0.050] (bge), 0.049 [0.041, 0.057] (gte).
- **Two rates, not one (K1 fires).** The well relaxes at γ_auto 0.0094 [0.0076, 0.0115] per call (1/γ ≈ 100 calls ≈ 1 h; no between-unit spread, I² 0). The sender-specific kick decays at γ_kick ≈ 0.13–0.17 per call (≈ 6–8 calls). Pooled ρ_γ 14.8, 90% CI [7.2, 30.4] (bge), 20.2 [6.8, 59.9] (gte).
- **Pairs that read each other more co-move more:** β_R 0.018 [0.012, 0.024] (all three variants). The pair cross-correlation does not decay at γ (γ_×/γ_auto ≈ 6–8).
- **Natives:** NE41: an erasure leaves own content memory intact (R_C 1.03 [0.95, 1.10]); the kick has already decayed before lag 4, so R_K is undefined. Joiners sit at 0.39 of the way to their well all through day 1 (no approach at γ_auto: the well is reached over days). Rival kicks: inconclusive (ratio 2.4 / 1.3, CI spans 0–5).
- Scorecard A1 B1 C2 D1 E1 F2 G0 H1 I0. `analysis/confirm.py` (#51 tail) frozen, guarded and dry-run; **not run**.
**Question served (GOALS.md):** **Q1** (what couples agents?): in #51, does reading another agent's message move the reader's content, and is the move a transient that the reader's own well erases at its own rate? **Q2** second: is the kick read-gated (coupling), or contemporaneous convergence (field)?
**Fields:** stat mech (Langevin / Ornstein–Uhlenbeck dynamics, linear response), sociophysics (influence)
**Literature:** no note in `literature/` covers Ornstein–Uhlenbeck processes. Cited from memory (†, not in `literature/`): Uhlenbeck & Ornstein, *Phys. Rev.* 36, 823 (1930)† (the OU process; autocorrelation e^(−γτ)); Kubo, *Rep. Prog. Phys.* 29, 255 (1966)† (fluctuation–dissipation: for a linear Langevin system the impulse response equals the normalized autocorrelation); Friedkin & Johnsen, *J. Math. Sociol.* 15, 193 (1990)† (opinion dynamics with anchoring to an initial position: the social analog of a private well). Model references: [`physics-models/11-vector-spins/README.md`](../../physics-models/11-vector-spins/README.md) (dynamics: vector autoregression on embeddings), [`physics-models/02-nonequilibrium-ising/README.md`](../../physics-models/02-nonequilibrium-ising/README.md) (measured response vs fluctuation route; FDT violation).
**Definitions used** (`physics-models/DEFINITIONS.md`): Agent; Regime (III only); Agent state, **variant vector** (statement vectors, 32-d whitened, `style_resid_period`); Exposure (turn read-out) and **Interaction (ledger-visible exposure)** (RE-D1) with its **unread (in-flight) exposure placebo**; H67's **in-flight placebo (matched-lag)**; H40's **call clock**; H98's **random field (static agent field) h_i^RF** (here the well centre) and **niche overlap**; H65's **read-gated susceptibility χ_j** (comparison only). **New named variants proposed for DEFINITIONS.md** (not edited here), defined under Model and Observables: *private well centre h_i (leave-day-out)*, *well relaxation rate γ_auto*, *kick response function K(τ)*, *read jump J_K*, *kick decay rate γ_kick*, *rate ratio ρ_γ*.
**From:** HH371 in `hypotheses/hypohypotheses/HYPOHYPOTHESES.md` · **Models:** `physics-models/11-vector-spins/` (primary: linear vector dynamics), `physics-models/02-nonequilibrium-ising/` (linear response vs fluctuations)
**Model folder:** `physics-models/16-langevin-relaxation/` (added 2026-10-07)
**Data inputs (shared tables first):** DQ5 `embeddings/statements.parquet` with `statements_{style_resid_period32,white32}_{bge_small,gte_modernbert}.npy`; `statement_flags` (exact repeats); `chat_core` (message ids); `producing_calls` (the call that produced each message); DQ1 `call_windows` (agent call clock), `context_ledger_items` (what each call read), `context_ledger_turns` (`reset_forced`, `reset_consol`, room); `pair_day_reads`; `agent_win30` vectors (pair co-movement); DQ6 `ground_truth_labels` (`rival_pair`, `preferred & ~holdout`); `roster` (join dates); `period_units`; `calendar`. No text is read.

## Source HH (verbatim from the HH list, including refinements)
- **HH371 · #51 agents are Ornstein–Uhlenbeck particles in private wells: reads kick them and the kick decays at the well's rate.** H98 found #51 is a static random field with a weak pull, plus co-movement through conversation. The simplest kinetic version: each agent relaxes toward its own private goal direction at rate γ, and each read of another agent's message is a small kick toward it.
  - *Prediction:* after a read, an agent's content moves toward the sender by a small amount that decays as e^(−γτ), and the same γ also sets the agent's own autocorrelation decay (an unfitted consistency check). Pairs with more reads co-move more, and the co-movement decays at γ.
  - *Check:* per-call content projections in #51 main body; event-triggered averages after reads vs matched non-read calls; fit γ two ways.
  - *Kill:* the two γ estimates differ by more than ×2, or no read kick beyond the in-flight placebo.
  - *Impostors:* niche overlap (shared role text) is a common field; use the read vs in-flight contrast.
  - *Models:* 11, 02 · *Builds on:* H98, H22, H65 (read_response)

## Question
In #51 every agent had a private role. H98 found the static content configuration is a random field (disorder ratio 0.67–0.73) with a weak pull (b_ex ≈ 0.27), and that pair co-movement runs mostly through reads and replies. Is the simplest kinetic version right? Each agent's content is an Ornstein–Uhlenbeck particle in its own well: it relaxes to its well centre at rate γ, and each message it reads is a small kick toward the sender. If so, two unfitted consequences follow. The kick decays at the same rate as the agent's own content autocorrelation (the linear fluctuation–response identity), and pairs that read each other more co-move more.

## Design: two layers (STANDARDS §4)
- **Replication (layer 1, role `replication`).** The common estimators (J_K, γ_auto, γ_kick, ρ_γ, β_R, γ_×) on every non-holdout #51 unit of `period_units` (51a–51l; 51m is the held-out tail). Units with < 3 days (51b, 51i–51l) get per-unit rows but enter the pooled tests only through the random-effects pool (CLAUDE.md exception (d), named: short units). #51 is the only private-role period, so the replication layer is the units of one period; each unit is a point.
- **Agent-level exception (CLAUDE.md (b), named):** the well centre h_i is an agent property estimated from all of the agent's non-holdout #51 days except the statement's own day. Its role text is constant through #51 (DQ6). Invariance is checked by comparing γ across units (P5).
- **Natives (layer 2, role `native`),** each with a dated prediction in its folder, written before it runs:
  - **N1 rival kicks** (G51 folder): DQ6 same-role rival pairs exist only in #51. Is the per-read kick from a same-role rival the same as from any other sender (isotropic κ, OU) or larger (niche-gated coupling, H98-R1)?
  - **N2 forced erasure** (NE41 folder): the 41-turn cap erases the context at a time set by the scaffold. If the OU state lives in the agent's well-anchored content, autocorrelation and kicks pass through an erasure unchanged at matched lag. If the state is held in the context window, both drop at the erasure.
  - **N3 joiners** (G51 folder): eight to ten agents join #51 mid-period (NE32 triplet, single joins, NE33). An OU particle dropped into its well relaxes at γ_auto. H98 saw joiners take days to reach their role, which would mean the well is built, not found.

## Model
**From:** `physics-models/11-vector-spins` (dynamics: s_i(t+1) ∝ s_i(t) + η Σ_j A_ij s_j(t) + h_i + noise; linearized, a vector autoregression) and `physics-models/02-nonequilibrium-ising` (measured response vs fluctuations).

**H130 variant: vector Ornstein–Uhlenbeck particles with read kicks, on the call clock.** Agent i's content state is x_i(n) ∈ ℝ³² (deviation from its well centre h_i), updated once per model call n of agent i:

  x_i(n+1) = (1 − γ) x_i(n) + κ Σ_{m read at call n} (z_m − h_i)_⊥ + ξ_i(n),

and every chat statement B emitted at call n is z_B = h_i + x_i(n) + ε_B.
- h_i: the **private well centre** (role, own project, model prior: H98's static random field).
- γ: the **well relaxation rate** per call (OU stiffness). 1/γ is the memory in calls.
- κ: the **kick per read**. z_m is the message read; (·)_⊥ is its idiosyncratic part, the message minus the room's contemporaneous consensus (common drive removed).
- ξ_i: the agent's own innovations (new sub-tasks, tool output). ε_B: statement sampling noise.
- Common drives (room topic, operator, time of day) enter every agent alike; they are the field.

**Consequences (unfitted relations).**
1. **Own autocorrelation.** For lags τ ≥ 1 call within a day: C_i(τ) = ⟨x_i(n)·x_i(n+τ)⟩ = σ_x² (1 − γ)^τ ≈ σ_x² e^(−γτ). Statement noise ε adds only at τ = 0 (excluded). A slowly drifting well (H98: day-level project drift) adds a plateau B.
2. **Kick response.** The event-triggered average of the reader's later statements, projected on the unit idiosyncratic direction û_m of a message read τ calls earlier: K(τ) = ⟨x_B·û_m⟩ = κ |(z_m − h_i)_⊥| e^(−γτ) + echo + drive. For a linear Langevin system the impulse response and the normalized autocorrelation decay at the same rate (Kubo†). **The consistency check:** γ_kick = γ_auto.
3. **Read gate.** Messages posted after the producing call started cannot kick the statement. The jump between read and in-flight messages at matched posting age is κ alone; echo and drive enter both arms.
4. **Pairs.** Kicks make pair covariance grow with reads: Cov(x_i, x_j) ≈ κ (r_ij + r_ji) σ²/(2γ) for weak coupling, and the pair cross-correlation decays at γ for |τ| ≫ 1/γ (a convolution of two exponentials gives (1 + γ|τ|) e^(−γ|τ|), whose one-exponential fit reads ≈ 0.6–0.8 γ).

**Rivals (named):**
- **R1 context-held kick** (kick lives in the context window and fades as the window scrolls or is erased): γ_kick ≠ γ_auto (typically faster), and kicks drop at forced erasures (N2).
- **R2 contemporaneous convergence / common drive** (no reading needed): K(0) equals the in-flight placebo level; co-movement does not need reads.
- **R3 niche-gated coupling** (H98-R1): kicks only from same-niche senders (N1 ratio ≫ 1).
- **R4 static random field only** (H98's static picture, κ = 0): no read jump; autocorrelation set by the well alone; pair co-movement unrelated to reads.
- **R5 built well** (the well forms over days, H98 NE33): joiners relax much slower than γ_auto (N3).

## Data scheme (`scheme/`)
`scheme/build.py` reads shared tables only, masks the holdout twice (`calendar.holdout` and `common.holdout_mask`), and writes codes and row ids only (no text). A guarded `--include-holdout` switch for `confirm.py` only (writes outside the round-1 folder; refuses without the acknowledgement flag).
- **Statements:** DQ5 `statements.parquet` rows with `kind == chat`, `goal_no == 51`, non-holdout, agent speaker, joined to `chat_core` (message id) and `producing_calls` (producing call `turn_id_prod`, `t_call_prod`). Exact self-repeats (`statement_flags.exact_self_repeat`) are dropped. Statements whose producing call is a fallback (`prod_fallback`) are dropped.
- **Call clock:** each agent's non-holdout #51 `call_windows` rows ordered by (`t_call`, `turn_id`), numbered per agent-day: n = 0, 1, 2, … (all call kinds; H40's per-call clock). Each statement carries n_B (its producing call's index); each read carries n_r.
- **Reads:** `context_ledger_items` rows of kind `agent` at the agent's #51 calls, sender ≠ reader, joined to the sender's statement row (the read message's vector). Each read keeps reader, sender, receiving call (`turn_id`, `t_call`, n_r), posting time and room.
- **Resets:** `context_ledger_turns.reset_forced` and `reset_consol` per call (for N2), as a per-agent-day cumulative reset count.
- **Output:** `data/processed/H130-ou-private-wells-51/` (`statements.parquet`, `reads.parquet`, `calls.parquet`, `_provenance.json`; `results/`, `synthetic/`). Budget ≤ 100 MB.
- **Regimes covered:** III only; #51 non-holdout days 2026-07-06 → 2026-09-04 (units 51a–51l).

## Observables
*Written 2026-10-04 22:20–22:22 UTC, before any H130 statistic.* Vectors z: 32-d whitened statement vectors, primary `style_resid_period` × bge_small; variants white32, gte_modernbert. All products are unnormalized dot products (linear in x), so decay rates are ratio estimators, not cosine times (Known issue: cosine decay times are amplitude-biased).

- **Well centre h_i (leave-day-out).** Mean of agent i's chat statement vectors over all non-holdout #51 days except the statement's own day. x_B = z_B − h_i. Agents need ≥ 2 days.
- **O1 own autocorrelation C(τ).** Over pairs of agent i's statements on the same PT day with lag τ = n_B′ − n_B ≥ 1 call: C(τ) = mean of x_B·x_B′ per lag bin (bins of calls: 1–3, 4–7, 8–15, 16–31, 32–63, 64–127, 128–255, 256–511, 512–1023). Pairs produced by the same call (τ = 0) are excluded.
- **O2 kick response K(τ).** For each statement B of agent i and each agent message m that i read at call n_r ≤ n_B on the same day (sender ≠ i): y = x_B·û_m, with û_m = unit(z_m − c_m). c_m is the room consensus at the posting time: the mean statement vector of agents other than the sender in the same room within ±15 min of t_m. τ = n_B − n_r ≥ 0 calls; same bins plus τ = 0. K(τ) = mean y per bin.
- **O3 read jump J_K (kick existence).** At each statement B with producing call c_B (start T_c): read arm = messages read at c_B posted in the mirror window (T_c − d, T_c); in-flight arm = agent messages by others posted in i's room in (T_c, t_B), which c_B cannot have read. d = clip(t_B − T_c, 1, 300) s. J_K = mean y(read) − mean y(in-flight). Both arms share time-local fields, echo and niche.
- **O4 decay rates.** γ_auto: weighted nonlinear least squares of C(τ) = A e^(−γτ) + B on the bins τ ≥ 1 (bin-mean τ; weights 1/bootstrap variance). γ_kick: the same form fitted to K(τ) on τ ≥ 0 (plateau B free). **Rate ratio ρ_γ = γ_kick/γ_auto.** Uncertainty: agent-day block bootstrap within unit (200 draws), the same draws for both rates, so ρ_γ's CI keeps their covariance.
- **O5 pair co-movement vs reads.** H22's J^c_ij (agent-day-centred `agent_win30` vectors, correlation over shared windows minus the cross-day surrogate; pairs with ≥ 10 shared windows, ≥ 5 in units < 4 days) regressed on log(1 + mean daily reads in both directions) (`pair_day_reads`) and same lab. Slope β_R; jackknife over agents; units pooled by DerSimonian–Laird.
- **O6 pair cross-correlation decay γ_×.** Pairs of statements by different agents in the same room on the same day, lag τ = |t_B′ − t_B| in seconds ≥ 30 s: C_×(τ) = mean x_B·x_B′ per lag bin (30 s–2 min, 2–5, 5–10, 10–20, 20–40, 40–80, 80–160, 160–320 min). Fit A e^(−γ_× τ) + B. Compared with γ_auto on the seconds clock (O1 on t instead of n).
- **Clock variants:** O1, O2, O4 on active wall seconds (same-day lags) next to the call clock.

**Null / baseline.**
- **In-flight placebo (matched-lag, H67 / RE-D1):** the read-gate test (O3).
- **Cross-day surrogate** (O5): removes time-of-day-locked drives (H22).
- **Agent-day block bootstrap** for every per-unit statistic; random-effects pools across units.
- **Synthetic worlds on the real skeleton** (axis F, before real data): real statements, calls, reads and rooms of #51 units; OU wells with and without kicks, a context-held kick (R1), a common-drive world (R2). Each estimator's size, power and bias are reported.

## Impostors (STANDARDS §1)
| Impostor | Relevant? | How H130 removes it | Status (planned) |
| --- | --- | --- | --- |
| Scheduler field | partly | Content projections, not activity timing. The per-call clock is used for decay rates; lags are within a PT day, so day edges and nights never enter a lag. | removed |
| Exogenous field (kickoff, goal, operator) | yes | Wells are subtracted (static fields cancel). A1: the common drive leaks into any message-direction profile, so γ_kick uses static pair directions with generic-reading controls and γ_auto subtracts the cross-agent covariance (both drive-robust in synthetic worlds with 5-min to 3-h drives); the in-flight arm shares every time-local field. | removed |
| Shared model priors | yes | `style_resid_period` vectors (removes the family field); wells absorb each agent's prior; white32 variant gives the same rates. | removed |
| Contemporaneous convergence | yes (central) | J_K is read vs in-flight at matched posting age (positive in every unit); the dose regression adds j's in-flight messages. Pair co-movement uses the cross-day surrogate with reads as a dose, but no in-flight arm. | removed (kick); partly (pairs) |

## Faithfulness scorecard
Scored per model, mapping and window; 0 = not done or failed, 1 = partial, 2 = passed. Scheme and promotion thresholds: `writeup/paper.tex`, Sec. "Assessing model faithfulness".
**Rival models:** R1 context-held kick; R2 contemporaneous convergence; R3 niche-gated coupling; R4 static random field (κ = 0); R5 built well.
**Locked holdout used for confirmation:** none yet. Planned: the #51 tail (2026-09-07 → 09-21), families `kick_response` + `content_alignment`, via `analysis/confirm.py` (frozen with `confirm.sha256`, guarded by `--confirm` + `H130_CONFIRM=1` + hash check + `holdout_ledger.check`; dry run on the 51g stand-in: C1–C3 pass, C4 fails, as in round 1). **Not run.**
**Overall A–I:** A1 B1 C2 D1 E1 F2 G0 H1 I0.

| Axis | Test | Score | Evidence |
| --- | --- | --- | --- |
| A mapping | variables defined from dataset fields; assumptions listed; invariant across families and regimes | 1 | Wells, kicks and clocks are defined from DQ5 vectors, the ledger and `call_windows`. Rates agree across bge/gte/white32. One period, one regime. |
| B assumptions | stationarity, Markov order, time-rescaling, update-order audit | 1 | γ_auto homogeneous across 12 units (I² 0). Neither clock wins (call clock better in 5/12). A single-rate OU is rejected: two time scales. |
| C adequacy | beats the null hierarchy, day-blocked held-out data | 2 | The read jump beats the in-flight placebo in every unit with ≥ 3 days; co-movement slope beats zero in all variants. |
| D unfitted predictions | unfitted statistics and the model's signature | 1 | The unfitted one-rate check fails (ρ_γ ≈ 15); the joiner relaxation fails; the read→co-movement prediction holds. |
| E interventional | predicts the change across a natural experiment | 1 | NE41: content memory survives a forced erasure (R_C 1.03); the kick part is unidentified (already decayed). |
| F identifiability | synthetic recovery with village sampling; robust to preprocessing | 2 | Synthetic on the real skeleton: γ_auto within ±10% under all drives; γ_kick recovered (0.009 at 0.01) and the context-held world separated (ρ ≈ 5); the registered profile was shown biased and replaced before real data (A1). |
| G ground truth | agrees with known structure | 0 | Rival-pair native (DQ6) inconclusive; no other known structure tested. |
| H comparative | beats the named rivals | 1 | Beats R2 (convergence) and R4 (κ = 0) on the read jump; loses to R1 (fast, transient kick) and R5 (built well). |
| I transfer | holds in other same-mode periods, including the holdout | 0 | No other private-role period; holdout not run. |

## Prediction
*Written 2026-10-04 22:20–22:22 UTC, before any H130 statistic on real data.* **Seen beforehand:** H98's full card (R 0.67–0.73; b_ex 0.23–0.31; reads and replies absorb 70% of the niche slope; joiners' own-role percentile 0.57 vs 0.83); H65, H67 (g_lag #51 0.142; J₁\* matched-lag design), H48 (τ_settle 4.5 h bge / 1.9 h gte; pull per read ≈ 1/250 if read-out drives settling), H96 (content decays with work, not nights), H109 (forced erasure does not drop room alignment; κ_R 0.019 per e-fold of room items read), H46 (content does not move at erasures), H99 (Onsager regression fails in regime III: kicks outlive the fluctuation clock ×9.5), RE-D1 (in-flight messages carry 1/3–1/2 of exposure effects). Skeleton counts only: 40,958 non-holdout #51 chat statements (28,090 intentions), 1,099 agent-days on 45 days, median 761 calls and 20 chat statements per agent-day over ≈ 8 h; H65's G51 table holds ≈ 0.33 in-flight messages per statement. **Not seen:** any autocorrelation, kick, decay or co-movement statistic of this design.

| # | Prediction (primary unless marked) | Counts against | Credence |
| --- | --- | --- | --- |
| P1 | **Read kick exists.** Pooled J_K > 0 with 95% CI above 0 (RE pool of units), and J_K > 0 in ≥ 60% of the units with ≥ 3 days. | pooled CI includes 0 or J_K ≤ 0 (**kill K2**) | 0.55 |
| P2 | **One rate.** ρ_γ = γ_kick/γ_auto lies in [0.5, 2] (pooled, call clock). | point ρ_γ outside [0.5, 2] with its 90% CI excluding 1 (**kill K1**); point outside but CI covering 1 → inconclusive | 0.35 |
| P3 | **Reads → co-movement.** Pooled β_R > 0 (CI above 0). | β_R ≤ 0 or CI includes 0 | 0.75 |
| P4 (secondary) | **Pair co-movement decays at γ.** γ_×/γ_auto (seconds clock) in [0.4, 2] (the lower bound allows the (1 + γτ) shape). | outside [0.4, 2] | 0.35 |
| P5 (secondary) | **The well is an agent property.** Per-unit γ_auto agree across units (RE heterogeneity I² < 50%), and 1/γ_auto lies between 30 and 600 calls (≈ 20 min to 6 h). | I² ≥ 50% or 1/γ_auto outside the range | 0.45 |
| P6 (secondary) | **Clock.** The call clock fits O1 at least as well as the seconds clock (lower weighted residual of the exponential fit in ≥ 60% of units). | seconds clock better in > 60% | 0.5 |

**Kill rules (from the HH):** **K1** fires when the two γ estimates differ by more than ×2 (point outside [0.5, 2] and the 90% CI of ρ_γ excludes 1). **K2** fires when there is no read kick beyond the in-flight placebo (pooled J_K CI includes 0 or J_K ≤ 0).
**Verdict rule (per unit):** *supported* if J_K > 0 (unit CI above 0) and ρ_γ in [0.5, 2]; *failed* if J_K ≤ 0 with CI below or including 0 while the unit has ≥ 3 days, or ρ_γ meets K1; *mixed* otherwise; *descriptive* for units < 3 days. **Hypothesis level:** supported if P1 and P2 pass and neither kill fires; failed if either kill fires; mixed otherwise.

**Amendment A1 (2026-10-04 22:48 UTC, after the synthetic validation, before any real-data statistic).** Synthetic worlds keep each unit's real statements, producing calls, per-call clock, reads and forced resets (units 51c, 51d, 51g; 3 replicates per world; `analysis/synthetic.py`; `data/processed/H130-ou-private-wells-51/synthetic/{runs.parquet, summary.json}`). Planted γ = 0.01 per call unless stated; κ = 0.003–0.006 per read; statement noise 0.6, well 0.25, OU state 0.2 per dimension; room drive 0.05–0.2 per dimension with time scale 5 min–3 h. Findings and the changes they force:
1. **The registered kick profile K(τ) measures the room drive, not the kick.** In a one-room village every agent reads every message, so the message-specific part of a kick is common to all readers. The drive enters x_B and z_m alike, and no consensus window removes it: γ from K(τ) reads 0.04–0.25 per call (the drive's rate) in every world, including the no-kick null. K(τ) stays reported but is not used for γ_kick.
2. **New primary γ_kick (sender-specific distributed lag).** Rows are (statement B of reader i, other agent j). The response is y_Bj = x_B·unit(h_j − h_i), the projection on the static direction from i's well to j's well. Regressors are counts of j's messages that i read in lag bins (calls: 0 in the mirror window, 0 older, 1–3, 4–15, 16–63, 64–255, 256–1023), j's in-flight messages, and the same counts summed over all senders (generic reading). Fixed effects per (pair, reader agent-day) absorb the day-level noise of leave-day-out wells, which otherwise fakes a negative slope (synthetic null). The j coefficients are the kick toward the sender actually read, beyond the pull of any read. γ_kick = the rate of A e^(−γτ) fitted to the coefficients of bins 0-older … 256–1023 at their mean lags. Recovery: median 0.009 (κ 0.003), 0.008 (κ 0.006), 0.009 under a 5-min drive, 0.006 under a 3-h drive, 0.002 at planted 0.003. A context-held kick (R1, decay 0.05, erased at resets) gives 0.057.
3. **New primary γ_auto (drive-corrected).** O1 products minus the cross-agent covariance at the same wall lag (O6, interpolated on log lag). The common drive is shared by all agents, so what is left is the agent's own relaxation. Recovery 0.0098–0.0109 in every world at planted 0.01 (0.0035 at 0.003). The raw O1 reads 0.0067 (3-h drive) to 0.020 (5-min drive); it is reported as a variant.
4. **Kill K1 on the pool, not per unit.** Per unit, ρ_γ falls in [0.5, 2] in 56–89% of OU worlds, and a slow drive biases it low (median 0.57; K1 false fires in 4/9 units). In the context-held world ρ_γ ≈ 5 (K1 fires in 7/9 units). Per-unit SE of ln ρ_γ ≈ 0.3, pooled ≈ 0.1. **K1 is evaluated on the random-effects pool of ln ρ_γ over units** (point outside [0.5, 2] and the pooled 90% CI excluding ρ = 1). Per-unit ρ_γ is descriptive. A low ρ_γ (< 0.5) is weaker evidence than a high one, because a slow drive pushes ρ_γ down.
5. **Kill K2 on the pool.** The registered J_K has per-unit SE ≈ 0.03–0.036; per-unit detection 0.11–0.22 at κ ≤ 0.006. Pooled over 12 units the estimated power is 0.7–1.0 at κ 0.003–0.006 (0.24 under a 3-h drive). K2 uses the RE pool of J_K (as registered); the dose analog J_pair = β(R0m) − β(U) is secondary (power ≤ 0.6).
6. **N2.** The erasure ratio of kicks R_K (dose coefficients for reads 4–39 calls before B, crossed vs not crossed by a forced reset) separates the worlds: −0.12 (context-held) vs 0.70–1.23 (OU). R_C ≈ 1 in every world (no world has a context-held own state). Both keep their registered thresholds.
7. The symmetric ±15-min consensus window is kept for J_K, as registered (both arms share any window bias). A planted κ = 0.01 makes 51d supercritical (κr/γ > 1); κ ≤ 0.006 is used.

**Natives:** predictions in `goalperiod-subhypotheses/G51/README.md` (N1, N3) and `goalperiod-subhypotheses/NE41/README.md` (N2), written before those runs.

## Results by goal period
Primary variant `style_resid_period` × bge. Per-unit rule (card, A1): *supported* = J_K CI above 0 and ρ_γ in [0.5, 2]; *failed* = J_K ≤ 0 or ρ_γ outside [0.5, 2] with the unit's 90% CI excluding 1; *mixed* otherwise; *descriptive* for units < 3 days.

| Period | Role | Verdict | Key numbers |
| --- | --- | --- | --- |
| [G51](goalperiod-subhypotheses/G51/README.md) | replication (12 units) + natives N1, N3 | failed (K1 fires on the pool; units: 2 failed 51d, 51g; 5 mixed 51a, 51c, 51e, 51f, 51h; 5 descriptive) | J_K 0.044 [0.038, 0.050]; γ_auto 0.0094 [0.0076, 0.0115]/call; γ_kick ≈ 0.13/call; ρ_γ 14.8 [7.2, 30.4] (90%); β_R 0.018 [0.012, 0.024]; N1 inconclusive; N3 failed |
| [NE41](goalperiod-subhypotheses/NE41/README.md) | native N2 (forced erasure inside #51) | mixed | R_C 1.03 [0.95, 1.10] (content memory survives); R_K −0.45 [−2.2, 0.85] (kick already gone by lag 4; undefined) |

## Results
*Exploratory round 1, 2026-10-04 (run 22:56–23:13 UTC, after Amendment A1). Non-holdout only. Code: `scheme/build.py`, `analysis/{h130lib,synthetic,run_units,natives,summarize,confirm}.py`. Data: `data/processed/H130-ou-private-wells-51/` (`statements/reads/calls.parquet`; `results/{units.parquet, units.json, natives.json, comove*.json|parquet, summary.json}`; `synthetic/{runs.parquet, summary.json}`; ≈ 15 MB). Figure: `figures/summary_obs_col.pdf`. Estimates: 112 rows in `per_period_estimates` (`hypothesis == "H130"`).*

### Headline
In #51 a read moves the reader's next statement toward the sender: the read jump over in-flight messages is J_K = 0.044 [0.038, 0.050] (bge; 0.049 in gte), positive in every unit with ≥ 3 days. The agent's own content relaxes to its well at γ_auto = 0.0094 per call (1/γ ≈ 100 calls ≈ 1 h), the same in all 12 units. But the kick does not live on that clock. The sender-specific kick decays within 6–8 calls (γ_kick ≈ 0.13–0.17 per call, pooled ρ_γ ≈ 15, 90% CI [7, 30]). So the OU picture with one rate fails (kill K1): reading leaves a short echo in the next statement or two; it does not displace the agent's state, which the well then restores. Pairs that read each other more still co-move more (β_R 0.018), as reads repeat.

### Outcome vs prediction
| # | Prediction | Observed (primary; variants) | Outcome |
| --- | --- | --- | --- |
| P1 / K2 | pooled J_K > 0 (CI above 0); J_K > 0 in ≥ 60% of units ≥ 3 days | 0.044 [0.038, 0.050]; 7/7 units ≥ 3 days, 11/12 overall; gte 0.049 [0.041, 0.057]; white32 0.044; J_pair 0.010 [0.006, 0.014] | **supported** (K2 not met) |
| P2 / K1 | ρ_γ in [0.5, 2] (pooled) | 14.8, 90% CI [7.2, 30.4]; gte 20.2 [6.8, 59.9]; white32 13.9 [7.8, 24.9]; pooled-data fit 15.2 [10.3, 24.7] | **failed** (K1 fires in all variants) |
| P3 | β_R > 0 | 0.018 [0.012, 0.024]; gte 0.019; white32 0.019; positive in 12/12 units | **supported** |
| P4 | γ_×/γ_auto (seconds) in [0.4, 2] | median 8.0 (bge), 6.0 (gte); in range in 2/9 units | **failed** |
| P5 | γ_auto homogeneous (I² < 50%); 1/γ in 30–600 calls | I² 0 (all variants); 1/γ ≈ 106 calls (gte 109) | **supported** |
| P6 | call clock fits better in ≥ 60% of units | 5/12 (seconds better in 7/12) | not supported (neither clock wins) |
| N1 | κ_rival/κ_other in [0.5, 2] | 2.39 [−0.66, 5.32] (bge); 1.30 [−0.76, 3.42] (gte); rival reads are 2% of reads | inconclusive (underpowered) |
| N2 | R_C ≥ 0.5 and R_K ≥ 0.5 | R_C 1.03 [0.95, 1.10] (gte 1.00 [0.91, 1.07]); R_K −0.45 [−2.2, 0.85] (gte 0.06 [−1.5, 2.1]) | mixed: R_C supported; R_K undefined |
| N3 | γ_J within ×2 of γ_auto | day-1 own-well position 0.39 (gte 0.38) of the day-2+ level, flat through ≈ 600 calls; bge fit 0.013 [0, 0.60], gte no approach | **failed** (R5: the well is reached over days) |

**Verdict.** By the card's rule the hypothesis **fails** (K1 fires; K2 does not). The read kick is real and read-gated; the one-rate OU consistency is wrong by an order of magnitude.

### Findings
1. **Two clocks in one agent.** The agent's content state has a memory of ≈ 100 own calls (≈ 1 h), set by its private well and indifferent to context erasure (R_C ≈ 1). What it reads acts for ≈ 6–8 calls (≈ 4–5 min). In magnet language the swarm is a set of slow OU particles with a fast, non-integrating input channel. In the synthetic, that pattern is the context-held kick world (R1), not the OU world.
2. **The kick is read-gated, not convergence.** Messages posted during the call that produced a statement project on it less than messages read at that call, at matched posting age, in every unit. The jump is ≈ 0.13 of the per-direction spread of x per read.
3. **Reading still matters for pairs.** Pair co-movement rises with reads at the same slope in every unit. The pair cross-correlation decays ≈ 6–8× faster than the own memory on the wall clock, so pair co-movement is the sum of short echoes, not shared slow states.
4. **New agents do not relax into a pre-existing well.** Joiners sit at ≈ 0.4 of their later position for the whole first day (H98: own-role percentile 0.57 on day 1). The well is learned over days.

### Caveats
- γ_kick rests on the first 2–3 lag bins (later coefficients are ≈ 0); its CI spans ×4. The K1 verdict does not depend on that: even the lower 90% bound of ρ_γ is 7.
- The registered kick profile K(τ) and γ_auto estimators were replaced before real data (A1, synthetic). The raw estimators give the same conclusion (γ_auto,raw 0.012; message-direction profile decays within ≈ 10 calls).
- In one-room #51 every agent reads every message, so beyond the first read-out the kick is only identified through sender-specific doses on static pair directions.
- R_K is undefined because the kick has decayed before the shortest erasure lag (4 calls); NE41 cannot tell where the fast kick lives.
- Short units (1–2 days) carry wide ρ_γ CIs; the pool has I² 0.

**Claim that stands:** in #51 a read pulls the reader's next statement toward the sender beyond the in-flight placebo (J_K 0.044 [0.038, 0.050], 11/12 units, both models), and the pull fades about 15× faster (≈ 7 calls) than the agent's own content memory (γ_auto 0.0094/call, ≈ 100 calls, homogeneous over 12 units). Exclusions: the HH's one-rate OU claim (failed, K1); pair co-movement decaying at γ (failed); joiner relaxation at γ (failed); rival-kick ratio and erasure kick ratio (unpowered or undefined).

## Round 2 redirects
- **What the direction is really after:** what clock the swarm's influence runs on, separate from what clock its memory runs on.
- **H130-R1. Fast-kick kernel.** Fit the read-response kernel on the call clock with 1-call resolution (0, 1, 2, …, 10 calls) and test whether it ends at the agent's next talk call (a reply) or decays smoothly.
- **H130-R2. Kick vs reply.** Split reads by whether the next statement is a DQ2 reply to the sender (content-selected, read with care) to see whether the fast kick is just replying.
- **H130-R3. Well formation.** Fit the joiners' approach to their well over days (NE32, NE33, single joins) as a second, slow time scale; compare with H98-R3.
- **H130-R4. Transfer.** Run the read jump and the two rates on shared-goal regime-III periods (#38–#44), where wells are weaker (H98: R 0.24–0.53).

## Notes
- 2026-10-04 22:20 UTC: round 1 started; card filled before any H130 statistic. Card text and predictions written 22:20–22:22 UTC.
- 2026-10-04 22:24–22:48 UTC: synthetic validation on the real skeleton; Amendment A1 written 22:48 UTC before any real-data statistic.
- 2026-10-04 22:56 UTC: first real-data numbers (unit 51a, printed by a run that then crashed on unit 51b because 1-day units had no leave-day-out wells; fixed by computing wells over all #51 days, as the card specifies). No amendment followed that print.
- 2026-10-04 23:13 UTC: replication, natives, summary, estimates; confirm.py frozen (`confirm.sha256`) and dry-run on 51g (C1–C3 pass, C4 fails). Guard tested: refuses without `H130_CONFIRM=1`.
- 2026-10-04 (resume note): an API limit interrupted the session; on resume the on-disk card, period predictions and scheme were checked before continuing. No timestamp was changed.
- Proposed for `physics-models/DEFINITIONS.md` (not edited): *private well centre h_i (leave-day-out)*, *well relaxation rate γ_auto (drive-corrected)*, *read jump J_K*, *sender-specific kick decay γ_kick*, *rate ratio ρ_γ*.
