# 12 · Information dynamics: decomposition, emergence and individuality

**Fields:** info theory, complex systems, stat mech
**References** (notes in `../../literature/`):
- Williams & Beer 2010, partial information decomposition: `williams-2010-nonnegative-decomposition-multivariate-information.md`.
- Barrett 2015, Gaussian PID and MMI: `barrett-2015-synergy-redundancy-gaussian-systems.md`.
- Rosas et al. 2019, O-information: `rosas-2019-o-information-high-order-interdependencies.md`.
- Rosas et al. 2020, causal emergence Ψ, Δ, Γ: `rosas-2020-reconciling-emergences-causal-emergence.md`.
- Mediano et al. 2022, ΦID review: `mediano-2022-greater-than-the-parts-causal-emergence-review.md`.
- Krakauer et al. 2020, individuality: `krakauer-2020-information-theory-of-individuality.md`.
- Lizier et al. 2008, local storage and transfer: `lizier-2008-framework-local-information-dynamics.md`.
- Lizier et al. 2013, modification as synergy: `lizier-2013-synergy-information-modification.md`.
- Kolchinsky & Corominas-Murtra 2020, copy vs transformation: `kolchinsky-2020-copying-versus-transformation.md`.
- From memory, not in `literature/`: Bertschinger et al. 2008 (autonomy, NTIC)†; Bertschinger et al. 2014 (BROJA PID)†; Ince 2017 (I_ccs)†; Stramaglia et al. 2021 (dynamic O-information)†; Schneidman et al. 2006 (I₂/I_N)†; Harder et al. 2013 (I_red)†.

**Related models:** `../08-copying-vs-transformation/` owns the copy/transformation split for content chains; this folder uses it as one atom of the read-out channel. `../04-semantic-information/` adds viability and scrambles on top of these quantities. `../01-inverse-ising/` gives the pairwise max-ent reference for I₂/I_N.

## The model

This folder is a family of estimators, not one Hamiltonian. Each one splits a mutual information among parts, wholes and an environment. The degrees of freedom are agents' states X^i_t (i = 1…n), a macro-variable V_t computed from them, and an environment E_t.

**Partial information decomposition (PID).** Two sources R₁, R₂ and a target S:

$$I(S;R_1,R_2)=\mathrm{Rdn}+\mathrm{Unq}_1+\mathrm{Unq}_2+\mathrm{Syn},\qquad I(S;R_i)=\mathrm{Rdn}+\mathrm{Unq}_i$$

- The redundancy function sets the atoms. Williams–Beer I_min overstates redundancy. BROJA†, I_ccs† and I_red† are the alternatives.
- Co-information is I(S;R₁;R₂) = Syn − Rdn. Net synergy (whole minus sum) is WMS = Syn − Rdn too.
- Three sources give 18 atoms. Keep to ≤ 3 sources at village sizes.
- Gaussian, univariate target: every marginal-based PID equals MMI, Rdn = min_i I(S;R_i) (Barrett 2015). The weaker source then has zero unique information by construction.
- Transfer entropy splits as T_{Y→X} = Unq(read) + Syn(read, own past) (Barrett 2015; Lizier 2013).

**O-information.** Target-free, over n variables:

$$\Omega(X^n)=\mathrm{TC}-\mathrm{DTC}=(n-2)H(X^n)+\sum_j\big[H(X_j)-H(X^n_{-j})\big]$$

- Ω > 0 is redundancy-dominated. Ω < 0 is synergy-dominated. For n = 3, Ω = Rdn − Syn.
- Bounds scale with n, so compare units by Ω/(n−2).
- Local ω_ij = I(X_i;X_j;X_{−ij}) locates the pairs that carry synergy.

**Causal emergence (Rosas 2020).** V_t supervenes on X_t. Three sufficient criteria use only pairwise mutual informations:

$$\Psi=I(V_t;V_{t'})-\sum_j I(X^j_t;V_{t'}),\quad \Delta=\max_j\Big[I(V_t;X^j_{t'})-\sum_i I(X^i_t;X^j_{t'})\Big],\quad \Gamma=\max_j I(V_t;X^j_{t'})$$

- Ψ > 0 means V is emergent. Δ > 0 means downward causation. Ψ > 0 with Γ ≈ 0 suggests causal decoupling.
- The criteria count redundancy up to n times. Redundancy pushes Ψ down, so Ψ < 0 is inconclusive.
- The exact ΦID atoms need a redundancy function. They are estimable only for pairs of agents (Mediano 2022).

**Individuality (Krakauer 2020).** System S, environment E, one step n → n+1:

$$A^*=I(S';S),\quad A=I(S';S\,|\,E),\quad nC=I(S';E\,|\,S),\quad \mathrm{NTIC}=A^*-A=I(S';E)-nC$$

- A* is organismal individuality. A is colonial individuality. nC is environmental determination. NTIC is environmental coding.
- Identity: A* + nC = A + I(S';E).
- **A and A\* never decrease when the system grows.** Boundary expansion: nC′ = nC − I(S';ΔS|S) + I(ΔS';E′|ΔS,S',S). A boundary closes where adding a part lowers nC and the next addition raises it.
- Bertschinger's autonomy† is the colonial A. NTIC† is the same quantity in both papers.

**Local storage, transfer and modification (Lizier 2008, 2013).** For destination X with history x^(k):
- active storage a_X = log p(x_{n+1}|x^(k)) / p(x_{n+1});
- local transfer t_{Y→X} = log p(x_{n+1}|x^(k), y_n) / p(x_{n+1}|x^(k));
- separable information s_X = a_X + Σ_Y t_{Y→X}. s < 0 marks a candidate modification event;
- modified information M_X = the synergy atoms over {own past, sources}. It is the state-dependent part of transfer.

**Copy vs transformation (Kolchinsky & Corominas-Murtra 2020).** For a channel p(y|x) with a shared alphabet and any prior p_Y:

$$D^{\rm copy}_x=d\big(p(x|x)\,\|\,p_Y(x)\big)\ \text{if}\ p(x|x)>p_Y(x),\ \text{else }0;\qquad I=I^{\rm copy}+I^{\rm trans}$$

d is the binary KL divergence. The prior can be "what unread agents reproduce at the same lag", which makes copy information an in-flight-corrected copying measure. Copy information has no data-processing inequality and is not additive over sub-channels.

### Order and control parameters
| Quantity | Order parameter | Control parameters in the village |
| --- | --- | --- |
| O-information | Ω/(n−2) on field-removed residuals; enrichment of ω_ij < 0 in read cones | read density (H41 cones), field strength (kickoff specificity), N |
| Causal emergence | Ψ − (field-only surrogate 95th percentile); Γ/Ψ | partition into parts (agents vs agent + own artifact), lag t′ − t relative to the read-out hop |
| Individuality | colonial A as a z-score against size-matched groupings; NTIC/A* | bin width Δ (30 min to 1 day), boundary (agent → agent + artifact → repo → room) |
| Storage / transfer / modification | A/H(X′); T_read − T_in-flight; M_X/I | history construction k, source set, address gating (named vs unnamed) |
| Copy vs transformation | copy efficiency η = I^copy/I against the unread prior | item type (identifier vs content), hop count |

## Interesting behavior

- **Redundancy hides synergy.** A shared field adds Rdn and makes Ω > 0. A system can hold synergy while Ω ≥ 0 (Williams–Beer Fig. 4A: co-information negative with synergy present).
- **Spurious synergy from constraints.** Hard collective constraints (shares that sum to 1, fixed call slots, turn-taking) give Ω < 0 with no integration (Rosas 2019). Subtracting a leave-in mean does the same: residual correlation −1/(N−1) gives Ω = −0.085 nats per triplet at N = 4 (Barrett 2015 formula; computed in the notes).
- **Gaussian log-concavity synergy.** Uncorrelated Gaussian sources give WMS > 0 (0.059 nats at a = c = 0.5). The variance-based WMS_Σ is 0 there, so it separates real integration from the log (Barrett 2015).
- **Individuality favors the bigger unit.** A and A* never fall as parts are added. Only an excess over size-matched groups means anything (Krakauer 2020).
- **Short history inflates modification.** In complex cellular automata, M_X/I is 0.29–0.30 at k = 16 and 0.86–0.90 at k = 1 (Lizier 2013). Unseparated storage returns as synergy.
- **Coordinates move atoms.** XOR synergy becomes unique information under a change of parts (Mediano 2022). Emergence on agents can become unique information on agent + own artifact. That is a direct test of whether "the collective" is stigmergic.
- **Copiers and permuters look alike to I.** A perfect copier and a perfect permutation have the same I(X;Y). Only the copy/transformation split separates them.

## Mapping to the village

- **Parts X^i_t** (one per agent, per unit):
  - content: DQ5 `agent_win30_style_resid_period`, projected to the unit's top 1–3 PCs, both embedding models (bge, gte);
  - behavior: a 1-d contrast of `behavior_states_v3` `p_*` (e.g. p_execute − p_communicate) per 5-min window, or the sampled discrete state (11 states);
  - allocation: the DQ4 `work_ledger` which-repo state per 30-min bin (agent work only: `author_kind == "agent"`, `~automated`), carried across bins, top-k repos plus "other" (≤ 7 symbols).
- **Macro V_t:** the room or village content centroid (fixed out of sample), the repo-share vector, the dominant repo, or a convention's use rate. Never a quantity computed from operator text (supervenience fails).
- **Environment E_t:** the impostor bundle, strictly lagged:
  - the scheduler phase (`call_windows.gap_kind`, the DQ8 `all_present_window` mask);
  - the kickoff/goal projection (`goal_fields`);
  - the rest of the swarm's state.
  - The agent's leave-period-out prior enters as a model covariate, not as part of E. Operator nudges react to agents (H35), so they are not exogenous.
- **Read-out channel:** the context ledger. A source item is a `context_ledger_items` row at the receiver's `call_windows.t_call`. The in-flight placebo is an item posted but not yet read at matched lag (H41's logged light cone). 21% of ledger items are `uncertain`; report with and without them.
- **Targets for PID and copy information:** the receiver's next DQ4 repo, its next `behavior_states_v3` state, or its next use of an H34 marker (hashed). `infra/shared/copy_info.py` holds the shared copy-information code.
- **Natural experiments as interventions:** forced erasures (`context_ledger_turns.reset_forced`, NE41) scramble storage. NE15, NE42 and #focus change the read graph. NE43 removes operator organs. Compare the two sides of each boundary (exception (c)).

## Identifiability at village sizes

Units have N = 4–32 agents. There are 71 non-holdout units over 283 days, about 4 days per unit.

- **Agent-day vectors give T ≈ 4 per unit.** That is useless for any within-unit information measure. Use 30-min windows (T ~ 10²) or 5-min behavior windows (T ~ 10²–10³; about 2.9k labelled agent-windows per unit).
- **Gaussian MI bias is ≈ pq/2T nats per term.** For Ψ with 1-d parts, n = 16 and T = 100, the summed bias is ≈ 0.08 nats. With 3-d parts it is ≈ 0.7 nats, larger than any plausible signal. Rule: 1-d parts, T ≥ 100, n ≤ 16 (random 16-subsets above that), shuffle or analytic correction.
- **O-information:** Gaussian Ω needs T ≥ 10n. Discrete plug-in Ω on 11 behavior states is identifiable for triplets only. Binary states allow n ≤ 6–8.
- **PID:** ≤ 3 sources (own past, the read, one bundled field). Plug-in alphabets ≤ 7 symbols.
- **Storage and transfer:** plug-in estimates allow history k = 1. Replace x^(k) with a constructed sufficient state: the agent's own artifact, carried across nights and erasures (H58 M0), plus time since its last commit. Lizier used 6 × 10⁶ samples at k = 16; we have 10³–10⁴ agent-steps per unit.
- **Individuality:** plug-in tables over (S′, S, E) with 7 · 7 · 27 cells are not identifiable. Use held-out parametric log-loss with day-blocked cross-validation (H58's estimator). Held-out estimates fall when variables are added, which is the opposite of the theory, so estimator variance can set a "boundary". Check boundaries on synthetic skeletons.
- **ΦID capacity (𝒢, 𝒟):** pairs only. A unit of 32 gives a 496-pair synergy matrix. Ψ at order k = 2 needs n ≤ 8.
- **Local events:** threshold local s or t against within-agent, within-day source shuffles at p < 0.01. A single negative local value in a stochastic system is usually noise.

## How to fit (or measure)

1. Fix the partition, V, E, the bin and the lag in the card before looking. Report alternatives as sensitivity.
2. Remove fields by regression on exogenous directions and leave-one-out means. Never subtract a leave-in mean.
3. Estimate on DQ8-trimmed windows within one unit. Bootstrap errors by circular day blocks.
4. Compute the same statistic on DQ8 `simulate.py` field-only skeletons and on size-matched random groupings. Report data minus the surrogate 95th percentile.
5. For PID, report BROJA and I_ccs and trust a sign only where they agree. For Gaussian targets, use a multivariate target or a non-marginal measure, and report WMS_Σ.
6. Write per-unit rows to `per_period_estimates`. Compare units as points on a phase diagram (Ω/(n−2) or Ψ against field strength and read density).

## Nulls and controls

- **Size-matched random groupings.** A, A*, NTIC, Ψ and Ω do not decrease as the system grows. Draw random groups of the same size from the same unit, matched on member activity. This is the reference for every individuality or emergence claim.
- **Field-only skeletons:** DQ8 `simulate.py` presets (rate-matched independent agents plus global, room, time-of-day and day fields on the real schedule). They carry the scheduler and kickoff impostors with zero coupling.
- **Trimmed block-shift:** trim to the all-present window first, then block-shift agents (DQ8 null-size table).
- **In-flight placebo source:** for every transfer, PID or copy statistic, add a posted-but-unread item at matched lag. Real transfer is T(read) − T(in-flight).
- **Placebo lag:** a lag shorter than one read-out hop (H41: one hop per 1.5–5 talk calls). Anything at that lag is co-generation.
- **Constraint-preserving surrogate** for Ω < 0: keep each agent's marginal and the per-bin count of busy agents.
- **Copy-only simulator** for modification: DQ8 Potts herding or DeGroot dynamics on the real schedules.

## Pitfalls

**The four impostors** (`../../STANDARDS.md` §1):
- **Scheduler field.** Common start/stop makes every pair correlated, which is Ω > 0. A fast common-mode nuisance that V cancels (a share, a normalized centroid) inflates Ψ without integration. First-of-day calls re-read artifacts and inflate storage at day starts. Use trimmed windows and the per-call clock (H40).
- **Exogenous field.** A slow kickoff field is redundancy counted n times: it pushes Ψ down and Ω up. Raw Ψ < 0 is therefore inconclusive, not a negative. Colonial A removes the field only if the field is in E. Organismal A* contains the field by construction, so never use A* alone for a collective claim.
- **Shared model priors.** Same-family responses look like redundancy, and prior × own-state interactions look like state-dependent transfer (modification). Use `style_resid_period` vectors, condition on agent identity or the leave-period-out prior, and report same-family vs cross-family pairs.
- **Contemporaneous convergence.** Two unread messages correlated with the target give Rdn > 0 and apparent transfer. Every transfer and PID atom needs the in-flight placebo source. A third to a half of apparent exposure effects are in flight (H32, H34).

**Estimator traps:**
- **Leave-in mean fakes synergy** (Barrett 2015 notes): residual correlation −1/(N−1) gives Ω = −0.085 nats per triplet at N = 4 and −0.004 at N = 8, and a singular full covariance.
- **Gaussian MMI labels all transfer "modification"** when the own past is the stronger source (the expected case). Run the transfer PID on discrete states (`behavior_states_v3`, DQ4 which-repo).
- **I_min hands the copier result for free.** It inflates redundancy, which is HH299's predicted outcome. Do not use it alone.
- **One-axis targets make second-measure checks void.** Every redundancy measure in Barrett's class equals MMI there.
- **Krakauer names were swapped in H01 and H58** (Krakauer notes). I(x′;x) is organismal A*. I(x′;x|y) is colonial A. The tests ran on the right quantity; the wording was wrong.
- **Individuality decays with lag in general.** State τ* relative to bin width, or report colonial A / I(S′;S,E) z-scored against size-matched units.
- **Copy information on whole messages is fragile.** One changed token zeroes D^copy under 0–1 loss. Use per-item or vector-valued losses. Chains must be defined by reads, because re-reading the original restores copy information.
- **Granger, not Pearl.** All quantities are predictive on observational data. Hidden drivers (operator, platform) create unique information. Natural experiments are the nearest thing to interventions.
- **Never pool periods.** Pairwise synergy matrices invite pooling. Compare per-unit summaries.
- **Restatement loops are context copies** (H69, 2026-10-04): self-repeats need the source in the context window (in-context enrichment OR 3.4× [2.6, 4.5]; pseudo-erasure 1.13). An agent's own-past predictability inside a segment is therefore partly a copy from context, not stored state. Split active storage by whether the source is still in context (`reset_consol | reset_session` segments).

## Hypothesis seeds

- **HH296 · Autonomy and closure across scales.** Colonial A and NTIC for agent → agent + artifact → repo + contributors → room → village, with the impostors in E, against size-matched groupings. Prediction: autonomy per bit peaks at agent + artifact.
- **HH297 · Conditional Ψ of the agenda.** Ψ of the room centroid minus the field-only surrogate. Prediction: ≤ 0 in ≥ 80% of units; exceptions are long talk-coupled free periods (#38, #51).
- **HH298 · O-information after field removal.** Residual Ω/(n−2) within rooms near 0; ω_ij < 0 enriched ≥ 1.5× among mutually reading pairs; no enrichment for in-flight pairs.
- **HH299 · Storage, transfer, modification.** A/H(X′) ≥ 0.3 with the constructed artifact state; T_read − T_in-flight ≤ 0.02 bits outside shared-repo weeks; s < 0 events cluster 1–3 calls after merges (NE42, #26 elections).
- **HH300 · Markov blankets.** Krakauer boundary expansion as the search step: the blanket closes at agent + own artifact.
- **HH305 · The operator as an organ.** Village nC with and without operator and scheduler variables in S, across NE43.
- **HH319 · Two reads.** Synergy of two senders' reads about the receiver's next content, with a multivariate target and WMS_Σ. Prediction: redundancy dominates (H59 "one read = one kick").
- **HH321 · Individuality vs bin width.** Colonial A(Δ) z-scores for agent + artifact, repo units and the culture residual.
- **HH322 · Pairwise sufficiency.** I₂/I_N† > 0.9 after field removal for binary co-usage.
- **Copy at the read hop** (from the copy-information notes): η ≥ 0.8 for repo names and URLs, ≤ 0.3 for H34 content markers, against the unread prior.
- **Coordinates test for stigmergy** (Mediano notes): Ψ of repo shares falls ≥ 50% when each part includes its own artifact.

**Hypotheses that use this model:** H01 and H58 (Krakauer individuality; held-out log-loss estimator), H32 (cross-validated content transfer), H59 (redundancy of reads, through HH319), H57 and H23 (copy information; owned by model 08), H12 and H49 (pairwise vs higher-order structure, through HH298 and HH322).
