# H101: Pairwise Ising vs full multi-information in co-usage

**Status:** exploratory round 1 done (2026-10-04; non-holdout only). **Co-usage is pairs plus fields; no group term is resolved, and the instrument cannot separate one from a heterogeneous field.**
- **Raw Schneidman ratio:** I₂/I_N median 0.95 over 71 units (multi-information resolved in 70). The synthetic shows this is uninformative here: a planted group term also gives 0.89–0.95 (Amendment A1).
- **After field removal:** ρ_F median 0.91 (regime I 0.89, III 0.93); ρ_F ≥ 0.9 in 56% of resolved units, < 0.8 in 4 of 71 (all regime I). The uniform item field carries φ = 0.71 of the multi-information in regime I but only 0.26 in regime III, where pairwise structure dominates.
- **A small higher-order remainder is real but field-sized:** r_HO median 0.03–0.05 of I_N; z ≥ 2.33 against the pairwise bootstrap in 83% of resolved units with N ≥ 6 (pairwise-world rate 17–33%); it stays at or below the heterogeneous-field reference in 92% of those. No unit meets the egregore rule in conventions.
- **Known structure appears as signed pairs:** #12 team-mates J +0.15 vs opponents −0.60 (p 0.0005); rooms in #39 and #41 (p 0.0005). Projects (pooled over days) give five regime-I/#51 candidates that the day field may explain.
- Natives: G12 mixed, NE42 mixed (rooms as pair blocks; the merge does not raise the field share), G51 supported (Roudi: ρ_F falls and z rises with subset size). Scorecard A1 B1 C1 D1 E1 F1 G2 H1 I0. `confirm.py` frozen, guarded and dry-run; **not run**.
**Research question (GOALS.md):** **Q3** (is there collective order beyond fields?): a higher-order remainder in co-usage beyond fields and pairs is one of the egregore signatures; its absence is a powered negative. **Q2** second: how much of the co-usage multi-information is a shared field.
**Fields:** stat mech (pairwise maximum entropy, inverse Ising), info theory (multi-information, higher-order interactions), sociophysics (conventions)
**Literature:** [`literature/meshulam-2019-coarse-graining-fixed-points-scaling-neurons.md`](../../literature/meshulam-2019-coarse-graining-fixed-points-scaling-neurons.md) (max-ent and population structure in neurons); [`literature/rosas-2019-o-information-high-order-interdependencies.md`](../../literature/rosas-2019-o-information-high-order-interdependencies.md) (hard constraints fake synergy); [`literature/ashery-2025-emergent-social-conventions-llm-populations.md`](../../literature/ashery-2025-emergent-social-conventions-llm-populations.md) (conventions in LLM populations). Cited, not stored: Schneidman, Berry, Segev & Bialek, *Nature* 440, 1007 (2006)† (I₂/I_N); Tkačik et al., *PLoS Comput. Biol.* 10, e1003408 (2014)† (K-pairwise model: pairwise + population-count constraint); Roudi, Nirenberg & Latham, *PLoS Comput. Biol.* 5, e1000380 (2009)† (pairwise sufficiency is trivially high for small populations at low rates); Miller (1955)† (entropy bias).
**Definitions used** (`physics-models/DEFINITIONS.md`): Agent; Population N(t) (active variant: agents with ≥ 10 marker uses that day); Regime; Driving / external field; **Idea (H34 marker rule)** (H34 named variant); Mutual information between agents (here the multi-information of one agent-subset). **New named variants proposed for DEFINITIONS.md** (not edited here), defined under Model: *co-usage spin (agent-day)*, *shared-field (K) model*, *pairwise sufficiency after field removal ρ_F*, *higher-order remainder*.
## Standards (2026-10-04)
**Question served:** Q3 (no separable higher-order co-usage beyond pairs and fields; a powered negative only against uniform fields) and Q2 (field share by regime).
**Impostor table:** see "Impostors" below (scheduler removed; exogenous field partly, with the no-human-items variant; shared priors partly, with the no-rare-words variant; convergence n/a for the claim).
**Inputs:** H34 marker uses (hashes; `idea_markers.py` rule), `chat_core`, `calendar`, `period_units`, `roster`, `ground_truth_labels`. No text is read.
**Two layers:** 33 replication folders (#12 and #51 sit in native folders). Natives: 3 (G12 mixed, NE42 mixed, G51 supported).
**Confirm script:** `analysis/confirm.py` (#22, #28, #43; C1–C4), frozen, guarded, dry-run on stand-ins; not run.

**From:** HH322 in `hypotheses/hypohypotheses/HYPOHYPOTHESES.md` · **Models:** `physics-models/01-inverse-ising/` (primary), `physics-models/12-information-dynamics/` (multi-information; size-matched and constraint pitfalls)
**Data inputs (shared tables first):** H34 marker uses (hashes only; `data/processed/H34-idea-cascades/markers/uses.parquet`, the table `infra/shared/idea_markers.py` reproduces), `chat_core` (speaker, agent, day, goal), `calendar`, `period_units`, `roster`, `rooms_timeline` (room per agent-day), `ground_truth_labels` (#12 teams, room assignments). No text is read.

## Source HH (verbatim from the HH list, including refinements)
Higher-order structure in co-usage: pairwise max-ent vs the full multi-information (Schneidman). For binary use of conventions or projects per agent-day, fit a pairwise Ising model and report the fraction of multi-information I_N it captures, I_2/I_N.
  - *Prediction:* I_2/I_N > 0.9 after field removal: pairwise structure suffices, there is no higher-order "group mind", and this matches H49's dense-field reading. A substantial higher-order remainder (I_2/I_N < 0.8) beyond a shared-field null would be the egregore-positive outcome.
  - *Kill for the egregore reading:* I_2/I_N ≈ 1.
  - *Models:* 01 · *Builds on:* H49, H11, HH298

## Question
When agents use the same conventions (names, coinages, numbers) or the same projects (repos, sites, files) on the same day, is the joint pattern of who-uses-what explained by agent rates, a shared item-popularity field and pairwise couplings? Or does a higher-order remainder ("group mind") survive beyond fields and pairs?

## Design: two layers (STANDARDS §4)
- **Replication (layer 1):** the common estimator on every eligible non-holdout unit (`period_units`: ≥ 1 day with ≥ 4 active agents and ≥ 100 items). One README per goal period, role `replication`; unit estimates pooled within a period by a random-effects mean. Item families: conventions (primary), projects (secondary).
- **Period-native tests (layer 2), each with its own dated prediction in its folder:**
  - **G12** (#12 debates, assigned teams per debate, DQ6 `team` labels): teams are a known block structure. Pairwise blocks, or a team-level higher-order term?
  - **NE42** (#39 → #40 → #41: two rooms merged into one, then split, at a fixed roster): the merge should raise the shared-field share and leave pairwise sufficiency unchanged.
  - **G51** (N 21–32, the only units large enough): a size sweep of subsets n = 4…12. Roudi et al. show pairwise sufficiency falls with n when higher order exists; at low rates it is trivially near 1 for small n.

## Model
**From:** `physics-models/01-inverse-ising` (pairwise maximum entropy), with the multi-information of `physics-models/12-information-dynamics`.

**Degrees of freedom (co-usage spin, agent-day).** In unit-day d, an *item* m is an H34 marker used in agent chat that day by at least one active agent (Claude Code agent excluded). Agent i's spin for item m is s_i(m) = 1 if i used m in a chat message that day, else 0. The samples are the items of the day; the variables are agents. Families: **conventions** = marker classes N (names, coinages, identifiers, quoted phrases), W (rare words) and D (numbers); **projects** = class U (repo, site and file artifacts).

**Population and subsets.** Active agents of the day: ≥ 10 marker uses that day. For each day, draw S = 20 random subsets of n = min(8, N_d) active agents (all subsets when fewer exist). All entropies are exact sums over the 2ⁿ patterns. Items used only by agents outside the subset give the all-zero pattern: there is **no truncation** on the subset count K, so no hard constraint enters at the subset level. The unit-level truncation (every item has K_unit ≥ 1) is reported.

**Model hierarchy (per day and subset, all fitted by maximum likelihood with L2 penalty 10⁻³):**
- P₁ independent: fields h_i (the agent-day rate). Entropy S₁.
- P_K shared field: P(s) ∝ exp(Σ h_i s_i + V(K)), K = Σ s_i. V(K) is the maximum-entropy model of a shared item-popularity field (an exchangeable common input: a hot topic used by many). Entropy S_K.
- P₂ pairwise Ising: exp(Σ h_i s_i + Σ_{i<j} J_ij s_i s_j). Entropy S₂.
- P₂K pairwise + shared field (Tkačik's K-pairwise model). Entropy S₂K.
- P_N the empirical pattern distribution. Entropy S_N (plug-in, Miller–Madow corrected).
- Fitted-model entropies are corrected to first order for overfitting: S_model + k/(2T), with k free parameters and T items.

**Quantities.**
- Multi-information I_N = S₁ − S_N.
- **Raw pairwise sufficiency** (Schneidman) ρ_raw = (S₁ − S₂)/(S₁ − S_N) = I₂/I_N.
- **Shared-field share** φ = (S₁ − S_K)/(S₁ − S_N).
- **Pairwise sufficiency after field removal** (primary) ρ_F = (S_K − S₂K)/(S_K − S_N): the fraction of the multi-information *beyond agent rates, agent-day activity and the shared item field* that pairwise couplings capture.
- **Higher-order remainder** r_HO = (S₂K − S_N)/I_N: what neither fields nor pairs explain.
- Per unit: ratios of sums over days and subsets (Σ numerator / Σ denominator); CIs by item bootstrap within days (B = 100), refitting every model.

**Fields removed.** Agent rates and agent-day activity: fields h_i are fitted per day (the ensemble is one day), so agents active on the same days do not look coupled. Item popularity (goal, kickoff, operator, a hot topic): V(K). Room- or team-level fields are *not* removed by V(K); they appear as pairwise blocks (J within the room) or, if the room field is strong and shared by ≥ 3 agents, as higher order. The NE42 and G12 natives test this.

## Data scheme (`scheme/`)
- **Inputs:** `data/processed/H34-idea-cascades/markers/uses.parquet` (msg, marker, cls; hashes), `chat_core` (row index = msg; speaker_kind, agent, pt_date, goal_no), `calendar`, `period_units`, `roster`, `rooms_timeline`, `ground_truth_labels`, `kicks_classified` (human messages, for the exogenous-item variant).
- **Transform (`scheme/build.py`):** per non-holdout unit (held-out days removed with `common.holdout_mask` and `calendar.holdout`, asserted twice): agent chat rows of the unit's days; marker uses joined; per (day, family) an item × agent binary matrix (uint8; marker hashes replaced by row numbers; no text); active agents per day; each agent's modal room that day; the set of items any human used that day (variant: exogenous items dropped).
- **Output:** `data/processed/H101-pairwise-vs-multi-information/` with `days/<unit>.npz` (binary matrices, agent codes, room codes), `results/subsets.parquet`, `results/units.parquet`, `results/periods.parquet`, `synthetic/`, `natives/`, `_provenance.json`. Budget ≤ 50 MB.
- **Regimes covered:** I, II, III (non-holdout). Fits are within one day; summaries within unit.

## Observables
1. Per unit and family: I_N (nats per item), ρ_raw, φ, ρ_F, r_HO with CIs; mean rate per agent-item; mean K; number of items, days, subsets.
2. The pairwise-truth bootstrap band of r_HO (simulate from the fitted P₂K at the same T, refit; 20 draws per day) and the shared-field null (below).
3. Variants: exogenous (human-used) items dropped; W class dropped (style-adjacent rare words); n = 6 and n = 10.
4. Natives: J within vs between teams (G12) or rooms (NE42); ρ_F(n) and r_HO(n) for n = 4…12 (G51).

## Null / baseline
- **Pairwise-truth parametric bootstrap:** data drawn from the fitted P₂K at the real T. It calibrates the estimator bias of ρ_F and r_HO under "no higher order". A higher-order claim needs the observed r_HO above this band's 95th percentile.
- **Shared-field (latent-class) null:** s_i ~ Bernoulli(σ(h_i + φ_m)) with a 4-level latent item field φ_m, fitted by EM to each subset (rates and the K distribution). Conditionally independent given the field, so every bit of its multi-information is "field". Its ρ_raw, φ and ρ_F at the real T are the reference values for "fields only".
- **Size-matched groupings:** every statistic is computed on random n-subsets of the same size within the same day, never on whole units of different N (model 12: multi-information grows with system size). The G51 sweep reports the n-dependence.
- **Independent model:** I_N not above the item-shuffle null (each agent's column permuted within day: rates kept, co-usage destroyed) → the unit is *descriptive* (nothing to decompose).

## Impostors (STANDARDS §1)
| Impostor | Relevant? | How H101 removes it | Status |
| --- | --- | --- | --- |
| Scheduler field | partly | The ensemble is one day, so who is active when (day edges, outages) only enters through agent-day rates h_i, which are fitted per day. No within-day timing is used. | removed |
| Exogenous field (kickoff, goal, operator) | yes | Item popularity is the shared field V(K), removed in ρ_F; the variant drops every item a human used that day. Room- and team-level drives are not removed by V(K) (tested in the natives). | partly |
| Shared model priors | yes | Same-family agents share vocabulary, which makes pairwise J within family, not higher order. The variant drops the W class (style-adjacent rare words). No family-block test in round 1. | partly |
| Contemporaneous convergence | n/a for the claim | The claim is about the order of the co-usage structure (pairs vs groups), not about influence. J_ij is co-usage, not copying. Any claim about *who influences whom* would need the in-flight placebo. | n/a |

## Faithfulness scorecard
Scored per model, mapping and window; 0 = not done or failed, 1 = partial, 2 = passed. Scheme and promotion thresholds: `writeup/paper.tex`, Sec. "Assessing model faithfulness".
**Rival models:** shared-field only (latent class; H49's dense-field reading); higher-order group interactions (egregore reading; planted 3- and 4-body terms in the synthetic); independent agents.
**Locked holdout used for confirmation:** none yet. `analysis/confirm.py` (frozen, guarded, not run) targets #22, #28 (regime I) and #43 (regime III), conventions family.

| Axis | Test | Score | Evidence |
| --- | --- | --- | --- |
| A mapping | variables defined from dataset fields; assumptions listed; invariant across families and regimes | 1 | Spins are agent-day uses of hashed H34 markers; the ensemble is one day, so agent-day activity is a field h_i. Assumptions listed: items are exchangeable samples (they are not: markers co-occur in messages), K ≥ 1 support. Projects pool days on agents active every day, so their day field is not removed. |
| B assumptions | stationarity, Markov order, time-rescaling, update-order audit | 1 | Stationarity within a day. Sample independence is violated (several markers per message); the bootstrap resamples items, not messages. Robust to dropping human-used items (ρ_F 0.908) and rare words (0.883). |
| C adequacy | beats the null hierarchy, day-blocked held-out data | 1 | I_N beats the independent bootstrap in 70/71 units. The pairwise + uniform-field model leaves a significant remainder in 83% of resolved N ≥ 6 units, so it does not pass its own null; the heterogeneous-field reference absorbs the remainder in 92%. |
| D unfitted predictions | unfitted statistics and the model's signature | 1 | Roudi's size dependence passes in #51 (ρ_F 0.99 → 0.90 and z 0.5 → 6.7 from n = 4 to 8 in 51c). The HH's own threshold (ρ_F > 0.9) holds at the median (0.91) but in only 56% of units. |
| E interventional | predicts the change across a natural experiment | 1 | NE42: rooms are pairwise blocks on both two-room sides (p 0.0005); ρ_F does not move at the merge (0.891 vs 0.906); the predicted rise of the field share failed (0.535 → 0.469 → 0.338). |
| F identifiability | synthetic recovery with village sampling; robust to preprocessing | 1 | Bootstrap bias correction recovers ρ_F ≈ 0.93–1.00 in pairwise worlds (first-order corrections gave 0.45). The remainder test detects a planted 4-agent group term in 67–100% at N ≥ 10 (0% at N = 4) with size 17–33%; ρ_F < 0.8 is never reached by it, and a heterogeneous shared field produces a larger remainder. |
| G ground truth | agrees with known structure | 2 | #12 assigned teams appear as signed couplings (J +0.15 within vs −0.60 across, p 0.0005, 10 debates); DQ6 room assignments appear as pair blocks in #39 and #41 (p 0.0005 each). |
| H comparative | beats the named rivals | 1 | Beats the uniform-field (K) model where z ≥ 2.33; does not beat the heterogeneous-field reference (r_HO ≤ reference in 92%); the group-term rival is not separable at these counts. |
| I transfer | holds in other same-mode periods, including the holdout | 0 | The pattern (ρ_F ≈ 0.9, field-sized remainder) recurs in every regime and in 33 periods, but no holdout run. |

## Prediction
*Written 2026-10-04 20:24 UTC, before any H101 statistic on real data. Seen beforehand: table schemas, unit counts, the size of the H34 marker table (604k uses); published results of H49 (regime-III activity excess is a dense shared field; pair structure exists in talk), H11 (work herds in 11/14 weeks), H34 (idea cascades subcritical), H12 (content modes real). Not seen: any co-usage statistic.*

**Synthetic (axis F), before real data.** Item × agent matrices simulated at the real T, n and per-agent rates of four units (regime I and III):
- **Y1 pairwise truth** (planted J ~ N(0.3, 0.5²) plus a shared field): ρ_F ≥ 0.9 and r_HO inside the bootstrap band in ≥ 80% of replicates. [0.6]
- **Y2 shared latent field only:** φ ≥ 0.5; ρ_F reported (the reference for "fields only"). [0.6]
- **Y3 planted higher order** (a 4-agent group term: a bonus when ≥ 3 of a 4-agent group co-use an item, sized so that r_HO ≈ 0.2 in the population): ρ_F < 0.8 and r_HO above the bootstrap band in ≥ 70% of replicates. [0.5]
- **Y4 Roudi check:** in the Y3 world, raw ρ_raw is reported. If ρ_raw ≥ 0.9 there, raw I₂/I_N is uninformative at village rates and only ρ_F is read.
- **Y5 identifiability:** if Y3 is not separated from Y1 (power < 0.7) at a unit's counts, that unit's verdict is *inconclusive*, not *supported*.

**Real data (exploratory, non-holdout).**
- **R1 (conventions; the HH's prediction).** ρ_F ≥ 0.9 in ≥ 70% of resolved units (I_N above the item-shuffle null), period median ρ_F ≥ 0.9. *Counts against:* ρ_F < 0.8 with r_HO above the bootstrap band in ≥ 30% of resolved units (the egregore-positive outcome). [0.5]
- **R2 (fields dominate).** The shared-field share φ ≥ 0.5 (median over resolved units). [0.55]
- **R3 (raw Schneidman ratio).** ρ_raw ≥ 0.9 (median); read only if Y4 shows it is informative. [0.5]
- **R4 (no group mind).** r_HO above the pairwise-truth band in ≤ 20% of resolved units. [0.6]
- **R5 (projects).** Same as R1 where resolved; fewer units resolve (artifact mentions are sparse in regime I). [0.4]
- **R6 (regime).** ρ_F shows no regime difference (|median III − median I| < 0.05); φ is larger in regime III than in regime I (H49's shared field). [0.4]

**What would count against H101 as a whole:** a higher-order remainder (ρ_F < 0.8, r_HO above the pairwise band and above the shared-field null) in ≥ 30% of resolved convention units, repeated in projects: that is the egregore-positive outcome.

### Synthetic result (axis F) and Amendment A1 (2026-10-04 20:37 UTC, after the synthetic, before any real co-usage statistic)
Disclosure: to size the synthetic, the per-day item counts, active-agent counts, per-agent use rates and the variance ratio of the per-item user count K (0.5–1.75 in six units; below 1 from the K ≥ 1 truncation) were printed. No ratio of the hierarchy was computed on real data.
Run: `analysis/synthetic.py` (12 replicates × 4 worlds × 4 real unit shapes: 4c N = 4, 27 N = 10, 40 N = 13, 51g N ≈ 19; real day counts, item counts and per-agent rates; planted group term β = 3 on two 4-agent groups). Table: `data/processed/H101-pairwise-vs-multi-information/synthetic/`.
- **The first-order bias correction fails.** With k/(2T) and Miller–Madow, a pairwise world gives ρ_F ≈ 0.45 at n = 6–8 and T ≈ 500. **Amended:** every entropy is corrected by a parametric bootstrap from the fitted K-pairwise model (bias = mean refit − exact value in that world; B = 12), and n = 6 (not 8), S = 10 subsets per day.
- **Y1 pairwise truth:** corrected ρ_F = 0.93–1.00 (N ≥ 10), 1.12 at N = 4. ρ_F ≥ 0.9 in 67–100% of replicates. Passes Y1 except at N = 4 (overshoot).
- **Y3 planted group term:** ρ_F = 0.87–1.08 and never < 0.8 (0/48 replicates). **The HH's egregore threshold ρ_F < 0.8 is unreachable at village counts even for a strong planted group term.** The remainder z-test against the pairwise bootstrap detects it (z ≥ 2.33 in 100% / 83% / 67% of replicates at N = 10 / 13 / 19; 0% at N = 4), but its size under Y1 is 17–33% (marginalizing a pairwise swarm onto 6 observed agents creates real higher-order terms in the subset).
- **Y4 Roudi check:** raw ρ_raw = 0.89–0.95 in the Y3 world (N ≥ 10). **Raw I₂/I_N is uninformative here**; it is reported, not read.
- **Shared-field reference:** a latent-class field with agent-specific loadings gives a *larger* remainder (r_HO 0.04–0.19) than the planted group world (0.02–0.04). **A group interaction of this size cannot be separated from a heterogeneous shared field** (the egregore rule "z ≥ 2.33 and r_HO above the field reference" fired in 0/48 Y3 replicates).
- **Y2 uniform field only:** the remainder beyond the K-model is ≈ 0, so ρ_F is undefined (0/0); r_HO is read instead.

**Amended reading of the predictions (no prediction is re-written):**
- R1 and R3 are reported as written, but neither ρ_F ≥ 0.9 nor ρ_raw ≥ 0.9 can exclude a group term (Y3). A "pairs suffice" verdict is therefore **inconclusive on the negative claim** (STANDARDS §3: power < 0.8 at the effect that matters) and is labelled *descriptive*.
- R4 is read against the Y1 rate: the share of resolved units (N_d ≥ 6) with z ≥ 2.33 is compared with ≤ 33% (the worst Y1 rate).
- **R7 (new, written before real data):** departures from "pairs + uniform field" are common: z ≥ 2.33 in > 50% of resolved units with N_d ≥ 6. [0.5]
- **R8 (new):** where departures occur, the remainder does not exceed the heterogeneous-field reference (r_HO ≤ field r_HO) in ≥ 80% of those units, so the departure reads as heterogeneous fields, not as a separable group term. [0.6]
- Units with median N_d < 6 (most regime-I units: N = 4) have no power (Y3 detection 0/12): verdict *inconclusive*.

## Results by goal period
| Period | Role | Verdict | Key numbers |
| --- | --- | --- | --- |
| [G02](goalperiod-subhypotheses/G02/README.md) | replication | descriptive | ρ_F 0.81, φ 0.50, r_HO 0.094, I₂/I_N 0.91 (N_d 3.5) |
| [G03](goalperiod-subhypotheses/G03/README.md) | replication | descriptive | ρ_F 0.91, φ 0.51, r_HO 0.042, I₂/I_N 0.89 (N_d 4) |
| [G04](goalperiod-subhypotheses/G04/README.md) | replication | descriptive | ρ_F 0.89, φ 0.53, r_HO 0.055, I₂/I_N 0.96 (N_d 4) |
| [G05](goalperiod-subhypotheses/G05/README.md) | replication | descriptive | ρ_F 0.93, φ 0.66, r_HO 0.025, I₂/I_N 0.94 (N_d 4) |
| [G06](goalperiod-subhypotheses/G06/README.md) | replication | descriptive | ρ_F 1.61, φ 0.53, r_HO -0.077, I₂/I_N 1.07 (N_d 4) |
| [G07](goalperiod-subhypotheses/G07/README.md) | replication | descriptive | ρ_F 0.99, φ 0.63, r_HO 0.004, I₂/I_N 0.93 (N_d 4) |
| [G08](goalperiod-subhypotheses/G08/README.md) | replication | descriptive | ρ_F 0.96, φ 0.74, r_HO 0.010, I₂/I_N 0.89 (N_d 4) |
| [G10](goalperiod-subhypotheses/G10/README.md) | replication | descriptive | ρ_F 0.90, φ 0.32, r_HO 0.041, I₂/I_N 0.94 (N_d 6.75) |
| [G11](goalperiod-subhypotheses/G11/README.md) | replication | descriptive | ρ_F 0.96, φ 0.59, r_HO 0.014, I₂/I_N 0.97 (N_d 7) |
| [G12](goalperiod-subhypotheses/G12/README.md) | native | mixed | team J +0.15 vs −0.60 (p 0.0005); debate r_HO 0.087 |
| [G13](goalperiod-subhypotheses/G13/README.md) | replication | descriptive | ρ_F 0.96, φ 0.56, r_HO 0.019, I₂/I_N 0.96 (N_d 6) |
| [G16](goalperiod-subhypotheses/G16/README.md) | replication | descriptive | ρ_F 0.91, φ 0.60, r_HO 0.036, I₂/I_N 0.91 (N_d 7) |
| [G17](goalperiod-subhypotheses/G17/README.md) | replication | mixed | ρ_F 0.87, φ 0.62, r_HO 0.051, I₂/I_N 0.92 (N_d 7) |
| [G18](goalperiod-subhypotheses/G18/README.md) | replication | mixed | ρ_F 0.89, φ 0.65, r_HO 0.033, I₂/I_N 0.96 (N_d 7) |
| [G19](goalperiod-subhypotheses/G19/README.md) | replication | mixed | ρ_F 0.85, φ 0.81, r_HO 0.029, I₂/I_N 0.95 (N_d 7.5) |
| [G20](goalperiod-subhypotheses/G20/README.md) | replication | mixed | ρ_F 0.85, φ 0.65, r_HO 0.046, I₂/I_N 0.94 (N_d 9) |
| [G21](goalperiod-subhypotheses/G21/README.md) | replication | descriptive | ρ_F 0.86, φ 0.74, r_HO 0.036, I₂/I_N 0.95 (N_d 8.5) |
| [G23](goalperiod-subhypotheses/G23/README.md) | replication | mixed | ρ_F 0.81, φ 0.85, r_HO 0.029, I₂/I_N 0.94 (N_d 10) |
| [G24](goalperiod-subhypotheses/G24/README.md) | replication | mixed | ρ_F 0.83, φ 0.72, r_HO 0.047, I₂/I_N 0.91 (N_d 10) |
| [G25](goalperiod-subhypotheses/G25/README.md) | replication | mixed | ρ_F 0.82, φ 0.79, r_HO 0.037, I₂/I_N 0.95 (N_d 10) |
| [G26](goalperiod-subhypotheses/G26/README.md) | replication | mixed | ρ_F 0.89, φ 0.84, r_HO 0.019, I₂/I_N 0.96 (N_d 10) |
| [G27](goalperiod-subhypotheses/G27/README.md) | replication | mixed | ρ_F 0.83, φ 0.84, r_HO 0.027, I₂/I_N 0.96 (N_d 10) |
| [G30](goalperiod-subhypotheses/G30/README.md) | replication | descriptive | ρ_F 0.93, φ 0.90, r_HO 0.008, I₂/I_N 0.99 (N_d 11) |
| [G31](goalperiod-subhypotheses/G31/README.md) | replication | mixed | ρ_F 0.86, φ 0.82, r_HO 0.022, I₂/I_N 0.97 (N_d 11) |
| [G33](goalperiod-subhypotheses/G33/README.md) | replication | mixed | ρ_F 0.84, φ 0.80, r_HO 0.032, I₂/I_N 0.96 (N_d 11) |
| [G35](goalperiod-subhypotheses/G35/README.md) | replication | descriptive | ρ_F 0.91, φ 0.51, r_HO 0.044, I₂/I_N 0.95 (N_d 12) |
| [G36](goalperiod-subhypotheses/G36/README.md) | replication | descriptive | ρ_F 0.92, φ 0.67, r_HO 0.045, I₂/I_N 0.94 (N_d 11) |
| [G37](goalperiod-subhypotheses/G37/README.md) | replication | descriptive | ρ_F 0.92, φ 0.30, r_HO 0.054, I₂/I_N 0.93 (N_d 9) |
| [G38](goalperiod-subhypotheses/G38/README.md) | replication | mixed | ρ_F 0.94, φ 0.14, r_HO 0.051, I₂/I_N 0.92 (N_d 11.5) |
| [G39](goalperiod-subhypotheses/G39/README.md) | replication | mixed | ρ_F 0.87, φ 0.54, r_HO 0.062, I₂/I_N 0.89 (N_d 11) |
| [G40](goalperiod-subhypotheses/G40/README.md) | replication | mixed | ρ_F 0.89, φ 0.47, r_HO 0.058, I₂/I_N 0.92 (N_d 13) |
| [G41](goalperiod-subhypotheses/G41/README.md) | replication | descriptive | ρ_F 0.94, φ 0.34, r_HO 0.037, I₂/I_N 0.96 (N_d 13) |
| [G42](goalperiod-subhypotheses/G42/README.md) | replication | mixed | ρ_F 0.88, φ 0.36, r_HO 0.072, I₂/I_N 0.88 (N_d 12.5) |
| [G44](goalperiod-subhypotheses/G44/README.md) | replication | descriptive | ρ_F 0.93, φ 0.25, r_HO 0.051, I₂/I_N 0.94 (N_d 13.5) |
| [G51](goalperiod-subhypotheses/G51/README.md) | native | supported | ρ_F 0.99 → 0.90 (n 4 → 8, 51c); z 0.5 → 6.7 |
| [NE42](goalperiod-subhypotheses/NE42/README.md) | native | mixed | room J within − across +0.37, +1.44 (p 0.0005); φ 0.54 → 0.47 → 0.34 |

## Results
### Round 1 (2026-10-04): exploratory, non-holdout
Tables: `data/processed/H101-pairwise-vs-multi-information/results/` (`units_conv.parquet` → `units_conv_classed.parquet`, `units_proj.parquet`, `scoring.json`), `natives/`, `synthetic/`. Code: `scheme/build.py`, `analysis/{h101lib,run,synthetic,summarize,natives,native_estimates,confirm}.py`. Figures: `figures/summary_obs.pdf`, `figures/synthetic.pdf`. 71 non-holdout units, 282 unit-days, conventions on 6-agent subsets (10 per day); estimates rows: 491 replication + 10 native.

**Predictions scored (as written, read through A1):**
| Prediction | Observed | Verdict |
| --- | --- | --- |
| Y1–Y5 synthetic | Y1 pass (ρ_F 0.93–1.00, N ≥ 10); Y2 φ ≥ 0.5 pass; Y3 fail (ρ_F never < 0.8; z detects at N ≥ 10); Y4 raw ratio uninformative; Y5 N = 4 has no power | 2 pass, 1 fail, 2 informative |
| R1 ρ_F ≥ 0.9 in ≥ 70% of resolved units, median ≥ 0.9 | median 0.91; share 56% (I 44%, II 67%, III 74%) | **mixed** (descriptive under A1) |
| R2 φ ≥ 0.5 (median) | 0.56 overall; I 0.71, II 0.75, III 0.26 | supported overall, not in regime III |
| R3 raw I₂/I_N ≥ 0.9 | 0.95 (I 0.96, III 0.93) | supported, uninformative (A1) |
| R4 remainder above the pairwise band in ≤ 20% | 83% of resolved N ≥ 6 units (pairwise-world rate ≤ 33%) | **failed** |
| R5 projects as R1 | 15 resolved units, ρ_F median 0.98 (60% ≥ 0.9); 5 higher-order candidates (18b, 19a, 26, 31c, 51g) with days pooled | mixed |
| R6 no regime difference in ρ_F; φ larger in III | Δρ_F (III − I) = +0.04; φ smaller in III (0.26 vs 0.71) | **failed** (second clause) |
| R7 (A1) z ≥ 2.33 in > 50% of resolved N ≥ 6 units | 83% | supported |
| R8 (A1) remainder ≤ heterogeneous-field reference in ≥ 80% of those | 92% | supported |

**Reading.**
- Who uses which convention on a day is captured to about 91% (median) by agent rates, a uniform item-popularity field and pairwise couplings. A residual 3–5% of the multi-information is higher order; it is statistically real in most units, but it is the size that agent-specific responses to a shared topic field produce, and no unit shows more.
- The raw Schneidman ratio (0.95) looks like strong pairwise sufficiency, but at village rates it is near 1 even with a planted group term. Only the field-removed ratio and the remainder test carry information.
- Regime III differs from regime I in *where* the multi-information sits: the uniform field carries 71% of it in regime I and 26% in regime III, where pairwise blocks (rooms, teams, conversation partners) dominate. This is the co-usage counterpart of H49's dense shared field in activity being absent from talk and content pairs.
- Assigned structure is pairwise and signed: team-mates share terms and opponents avoid each other's terms (#12); room-mates share terms (#39, #41). Nothing in the known structure required a higher-order term.
- The egregore question stays open at this resolution: a group term of the planted size (β = 3 on 4-agent groups) would also look like this.

## Round 2 redirects
- **What the direction is really after:** whether co-usage needs any interaction beyond pairs once agent-specific responses to shared fields are modelled.
- **H101-R1. Latent-factor max-ent.** Fit pairwise couplings plus agent-specific loadings on one latent field and test the remainder beyond that model, which is the rival A1 could not separate.
- **H101-R2. Message-level resampling.** Resample messages, not items, for CIs; markers inside one message are not independent.
- **H101-R3. Projects with day fields.** Fit day-specific fields with shared J on pooled project items and re-test the five candidates.
- **H101-R4. Debate pooling.** Pool #12 debates with debate-specific fields to give the team-level higher-order test power.

## Notes
- 2026-10-04: card written from the HH322 stub.
- 2026-10-04: the A1 synthetic (`synthetic/synthetic.parquet`) was run with process-hash seeds; the seeds were then fixed to CRC32 strings. A re-run reproduces the design, not the exact draws.
- 2026-10-04: the item-bootstrap intervals in `units_conv.parquet` (`*_lo`, `*_hi`) are biased (duplicated items lower the plug-in entropy) and are not used; estimates rows carry `ci_kind = none` with the remainder z in `notes`.
- 2026-10-04: H34's `uses.parquet` holds non-holdout rows only; `confirm.py` re-extracts held-out markers with `idea_markers.uses_for_rows(..., allow_holdout=True)`.
