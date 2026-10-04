# H115: Blind role recovery in the debate week: the judge is a sink of antisymmetric coupling (#12)

**Status:** exploratory round 1 **done (2026-10-04): failed as specified. The judge is not recoverable blind as a sink, and debate talk couples across teams, not within them.** Card and predictions written 2026-10-04 22:02 UTC, Amendment A1 (synthetic) 22:17 UTC, ranking frozen and hashed 22:17:44 UTC, all before any role label or real-data statistic.
- **P1 (primary, blind):** judge rank 1 in 3 of 10 debates, median rank 2.5, mean normalized rank 0.38 (uniform p 0.15; field-only skeleton null p 0.24). Not supported, not killed. Against the synthetic: a judge sink ≥ 0.6 Ising units is excluded (P 0.01); the data sit at a ≈ 0.15.
- **P2 (HH kill fires, reversed):** J_ST − J_OT = −0.16 ± 0.08 Ising units (team permutation p(≤) 0.01). Debaters talk after reading an opponent (J_OT 0.20 ± 0.05), not a team-mate (J_ST 0.04 ± 0.06): R-alternation.
- **P3 failed** as specified; post hoc, debaters' talk drops at the verdict against a rising within-debate trend.
- **Replication (R1):** the elected leader of #26 is the top talk source in 4 of 6 windows (mean u_L 0.80 vs skeleton 0.55, Fisher p ≈ 0.08); #35 lead designers (3/5) and #44's leader (1/2) show nothing.
- Scorecard A1 B1 C1 D1 E1 F2 G1 H1 I0. `analysis/confirm.py` (#48 / NE37 focal agent) frozen, guarded, dry-run; **not run**.
**Fields:** stat mech (kinetic Ising, broken detailed balance), sociophysics (roles, teams), info theory (directed influence)
**Literature:** [Aguilera, Ito & Kolchinsky 2026](../../literature/aguilera-2026-entropy-production-nonequilibrium-maxent.md) (kinetic Ising; the antisymmetric part of J as the source of irreversibility). Cited from memory (†, not in `literature/`): Roudi & Hertz, *PRL* 106, 048702 (2011)† (mean-field and ML inference of asymmetric kinetic Ising couplings); Glauber, *J. Math. Phys.* 4, 294 (1963)† (single-spin-flip kinetics).
**Definitions used** (`physics-models/DEFINITIONS.md`): Agent; Regime; Driving / external field (assigned roles, the motion, the verdict); Exposure (turn read-out) as implemented by the context ledger; **Call clock** and **per-call coupling** (H40 named variants); **In-flight placebo (matched-lag)** as in H67's read-out jump J₁\* (P = peer messages posted in (t_call, t_first) of the recipient's call); **Taylor field gauge c_×** (H86). New named variants proposed for DEFINITIONS.md (not edited here), defined under Model: *talk spin (per call)*, *read-gated sender input*, *sink score S_i*, *additive in/out coupling model*.
**From:** HH353 in `hypotheses/hypohypotheses/HYPOHYPOTHESES.md` · **Models:** `physics-models/02-nonequilibrium-ising/` (primary: kinetic Ising, asymmetric J), `physics-models/01-inverse-ising/` (symmetric part of J as team blocks)
**Data inputs (shared tables first):** `call_windows` (agent, t_call, t_first, talk, ctx_mode, gap_kind, first_of_day), `context_ledger_turns` (room per call), `context_ledger_items` (validation of the read rule only), `chat_core` (agent and human message times and rooms), `calendar`, `period_units`, `per_period_estimates` (H86 c_×), `ground_truth_labels` (#12 `phase` rows before the freeze; `judge`, `team`, `debate_result` rows only after the freeze; #26 / #35 / #44 `leader` rows). No text is read.

## Source HH (verbatim from the HH list, including refinements)
- **HH353 · Blind role recovery in the debate week: the judge is a sink of antisymmetric coupling (#12).** Debaters address the judge and the judge rules on them. That is a known one-way influence pattern.
  - *Prediction:* from talk spins alone, the agent with the largest in-minus-out antisymmetric coupling Σ_j(J_ji − J_ij) is the judge (rank 1 of 7), and the team blocks show positive within-team J. The judge's rulings act as field steps on the debaters, not the other way round.
  - *Check:* fit on non-holdout #12 days; compare against the DQ6 ground-truth roles only after the ranking is frozen.
  - *Kill:* judge rank ≥ 4, or team blocks absent from symmetric J (H101 found them in co-usage, J +0.15 within vs −0.60 across).
  - *Impostors:* assigned roles are a field; the read-gated contrast separates reacting to a read message from following the schedule.
  - *Models:* 02, 01 · *Builds on:* H21, H37, H101

## Standards (2026-10-04)
**Question served:** **Q1** (what couples agents?): does the per-call talk coupling carry a role's direction, so that a one-way role is recoverable blind from timing? **Q2** second: is the judge's signature a coupling (read-gated) or the role's field (schedule)?

| Impostor | Relevant? | How it is removed | Status (planned) |
| --- | --- | --- | --- |
| Scheduler field | yes | Per-call clock (each call is one update); calls trimmed to each day's all-present window; agent × call-mode and agent × phase intercepts; H86 c_× reported per unit as the gauge. Sink scores are differences of couplings, so a pure per-agent rate field cancels. | removed (planned) |
| Exogenous field (assigned roles, motion, verdict) | yes (central) | Agent × phase (pre / deb / post) intercepts absorb role schedules; a field-only skeleton null (real per-agent × debate × phase × mode talk rates, J = 0) calibrates the judge's rank; the in-flight sink score S^P ranks agents by the same role timing without read-gating. | removed (planned) |
| Shared model priors | partly | Roles rotate across debates, so the within-agent contrast (P1b) compares the same model as judge and as debater. Family talk propensity sits in the intercepts. | partly (planned) |
| Contemporaneous convergence | yes | In-flight placebo (matched-lag, H67): messages posted during the recipient's call cannot be read by it; the read-gated coupling must exceed it. Partition contrast (STANDARDS §3): read vs in-flight, and same-team vs opposite-team. | removed (planned) |

**Inputs:** the context ledger's call clock and visibility rule (my read rule is checked against `context_ledger_items`), `chat_core`, DQ6 labels; nothing from `activity_bins`.
**Two layers:** natives on G12 (P1 blind judge rank, P1b within-agent judge contrast, P2 team blocks, P3 rulings as fields); replication on G26, G35, G44 (blind sink rank of the designated leader, R1).
**Blind protocol:** the per-debate sink rankings are computed from spins only, written to `data/processed/H115-debate-judge-role-recovery/G12/frozen_ranking.json` with a SHA-256 hash recorded in this card, and only then are the DQ6 `judge`, `team` and `debate_result` rows read.
**Frozen 2026-10-04 22:17:44 UTC** (file mtime) (before any role label was read): SHA-256 `cc87142cdee7141bc2245e5b16792340690a7efb309e35ac8e6dc7fa3e2ca5a8` (`analysis/run_g12_blind.py`, λ = 4 from A1). Top sink per debate (primary, agent codes): 5, 8, 5, 0, 9, 6, 6, 11, 6, 9.
**Confirm script:** `analysis/confirm.py` (NE37 / #48 focal agent; C1–C2), frozen 2026-10-04 22:35 UTC (SHA-256 `4745ed30…61c5`), guarded (`--confirm` + `H115_CONFIRM=1` + ledger check + coordinator-supplied `--focal`), dry-run on a non-holdout stand-in (#26 01-07, agent 17: u_F 1.00 vs null q90 0.89); **not run**. #45 was the first choice but is blocked: H02 ran the same estimator family (kinetic-Ising couplings, leader's net influence) on #45.

## Question
In #12 the village ran ten Asian-Parliamentary debates, each with one judge and two drafted teams. A judge listens and rules; debaters speak and answer each other. Does the per-call talk kinetic Ising fitted to timing alone put the judge at the top of the in-minus-out (sink) ranking, without being told who judged? And does the symmetric part of J show the team blocks? A yes would mean that one-way roles are visible in who-talks-after-reading-whom, which is a cheap detector for hidden leaders or hidden factions.

## Design: two layers (STANDARDS §4)
- **Natives (G12, role `native`):** P1 blind judge rank per debate (primary); P1b within-agent judge contrast; P2 team blocks in the symmetric couplings; P3 rulings as field steps.
- **Replication (role `replication`):** the same blind sink-rank estimator on every non-holdout period with a single designated role agent in DQ6: G26 (elected leader, term windows), G35 (daily lead designers per room), G44 (installed fine-tuned leader in #best). #45 (installed leader) and #34 (hidden saboteurs) are held out; #51's roles are classes, not single hubs, so #51 is not eligible.

## Model
**From:** `physics-models/02-nonequilibrium-ising/` (kinetic Ising, asymmetric couplings; Glauber single-spin updates at agent-specific attempt times).

**Degrees of freedom: talk spin (per call).** Agent i updates only at its model calls c (the ledger's `t_call`; summary calls dropped). The spin is s_i(c) = +1 if call c produces a chat message (`call_windows.talk`), −1 otherwise. This is H40's call clock.

**Inputs: read-gated sender input.** x_ij(c) = 1 if agent j posted at least one chat message in i's room in [t_call of i's previous non-summary call, t_call(c)), else 0. These are exactly the messages that enter c's context under the ledger's visibility rule. The in-flight placebo input is x^P_ij(c) = 1 if j posted in i's room in (t_call(c), t_first(c)): posted during c's model call, so c cannot read it, while sharing every time-local field.

**Kinetic rule.** P(s_i(c) = +1) = e^{H_i(c)} / 2cosh H_i(c), with
H_i(c) = h_{i,κ(c)} + h_{i,φ(c)} + J_ii s_i(c⁻) + Σ_{j≠i} J_ij x_ij(c) + Σ_{j≠i} J^P_ij x^P_ij(c) + γ·wake(c) + η·hum_i(c).
κ = call mode (chat / computer use); φ = phase of the debate (pre / deb / post, from DQ6 `phase` timing rows, which carry no agent); c⁻ = i's previous call; wake = gap kind in {pause, first_of_day, after_summary, session_start, marker}; hum = a human message read at c.

**Index convention (fixed here, before data).** J_ij is the effect of j's read talk on i's next talk: row = recipient, column = sender. In-coupling in_i = Σ_j J_ij (how much i answers others); out-coupling out_i = Σ_j J_ji (how much others answer i). **Sink score S_i = in_i − out_i = Σ_j (J_ij − J_ji).** HH353 writes Σ_j(J_ji − J_ij) and calls it "in-minus-out"; read with the opposite index order (J_ji = effect of j on i) that is the same quantity. Its stated meaning, in-minus-out, is the operative definition. The judge as a sink means the judge's talk follows what it reads while others' talk does not follow the judge's.

**Primary estimator: additive in/out model.** A debate window gives only 170–630 calls (7 agents), too few for 42 free couplings. The primary fit therefore constrains J_ij = α_i + β_j (i ≠ j): α_i is i's in-coupling per read sender, β_j is j's out-coupling per reader. Then S_i = N(α_i − β_i) − Σ_k(α_k − β_k): the ranking is by α_i − β_i. One gauge direction (α + c, β − c) leaves every J_ij, every S_i and every ranking unchanged. The same form holds for the placebo couplings J^P. Fit: penalized maximum likelihood (L2 ridge λ on α, β, α^P, β^P; light ridge 0.1 on intercepts), per debate window. Variants: (i) full J with ridge (per-recipient logistic); (ii) chat-mode calls only with reads re-indexed to the previous chat-mode call (the H67-R1 regime-I clock).

**Team-block model (P2, after the freeze).** Pooled over the ten debates, couplings by pair type: J_ij = J_{τ(i,j)} with τ ∈ {same team (ST), opposite team (OT), judge reads debater (JD), debater reads judge (DJ), any pair with a bench agent (B)}, with the same intercepts, self and placebo terms (placebo couplings also by pair type). J_ST and J_OT are symmetric by construction, so J_ST − J_OT is the team-block contrast of the symmetric part of J.

**What each picture predicts.**
| Picture | judge's S rank | J_ST − J_OT | read vs in-flight | verdict |
| --- | --- | --- | --- | --- |
| **H115 (judge = sink; teams cohere)** | 1 (top) | > 0 | S^R rank of judge > S^P rank | debaters' talk field steps; J_DJ ≈ 0 |
| **R-chair (judge = source/agenda)**: the judge calls speakers and others answer it (H65: judges receive +0.45 replies per statement, #12) | bottom half | any | judge's out-coupling high | — |
| **R-alternation (turn-taking)**: AP speeches alternate Gov/Opp, so each speaker follows the other team | any | < 0 | — | — |
| **R-field (role schedule only)**: roles shift talk rates by phase, no directed coupling | same in S^R and S^P; field-only skeleton reproduces it | 0 | no read-gated excess | — |
| **R-null (no role signal)** | uniform | 0 | — | — |

## Data scheme (`scheme/`)
- **`scheme/callspins.py`** (library; an identical copy lives in H116's `scheme/`, see Notes) builds, for one goal period and a list of non-holdout days: the call table (turn_id, agent, day, t_call, t_first, room, s, mode, wake, previous-call spin), the read matrix X_R (calls × agents, uint8), the in-flight matrix X_P, and a human-read indicator. Rooms come from `context_ledger_turns.room`; message rooms from `chat_core`. The read rule is checked against `context_ledger_items` (share of calls whose sender set agrees exactly).
- **`scheme/build.py --period G<NN>`** → `data/processed/H115-debate-judge-role-recovery/G<NN>/`: `calls.parquet`, `xr.npy`, `xp.npy`, `windows.parquet` (debate or role windows; for G12 from DQ6 `phase` rows only), `_provenance.json`. Codes only; no text.
- **All-present trim:** per day, calls between the latest first call and the earliest last call of the day's present agents (agents with ≥ 20 calls that day); variant untrimmed.
- **Regimes covered:** I (G12, G26), II (G35), III (G44).

## Observables
*Written 2026-10-04 22:02 UTC.*
- **O1 blind sink ranking (G12).** Per debate d (window = DQ6 pre start → post end), the additive fit gives S_i^R (read couplings) and S_i^P (in-flight couplings) for agents with ≥ 5 calls in the window. Ranks r_i(d) (1 = largest S). Frozen and hashed before labels are read.
- **O2 judge rank.** r_judge(d) for d = 1..10; the median, the count of rank 1, and the mean normalized rank u = (r − 1)/(n_d − 1) (0 = top sink).
- **O3 within-agent judge contrast (P1b).** For each judge, S as judge (in its debate) minus its mean S in the debates it did not judge; averaged over debates.
- **O4 team blocks (P2).** J_ST − J_OT from the pooled pair-type model (Ising units), with J^P_ST − J^P_OT; also per phase (pre vs deb).
- **O5 rulings as fields (P3).** (a) J_DJ − J^P_DJ (debaters' read-out response to the judge, over its placebo); (b) the verdict field step Δh_D = mean over debaters of (h_post − h_deb) in the per-debate fits.
- **O6 leader rank (replication).** Per role window (G26 term-1 and term-2 day windows; G35 room-days; G44 #best days with the leader present), the designated agent's normalized sink rank u_L.
- **Gauge:** H86 c_× (`taylor_c_shared`, `activity_trim`) for each unit, read from `per_period_estimates`.

## Null / baseline
*Written 2026-10-04 22:02 UTC.*
- **N1 rank null:** under no role signal the judge's rank is uniform on 1..n_d: P(rank 1) = 1/n_d; the median-rank and rank-1-count tests use the exact Poisson-binomial / enumeration distribution.
- **N2 field-only skeleton null (assigned roles are a field):** 200 synthetic weeks on the real call skeleton with each agent's real talk rate per debate × phase × call mode and J = 0; the same estimator; the distribution of the true judge's rank (computed after the freeze). This is the calibration the H65 Known issue asks for ("single-agent percentile tests are biased by the skeleton").
- **N3 in-flight placebo:** the judge's rank under S^P; the read-gated claim needs r(S^R) < r(S^P) on average.
- **N4 team permutation (P2):** re-partition each debate's debaters into blocks of the true sizes (exact enumeration, 20,000 joint draws), refit the pair-type model.
- **N5 placebo boundaries (P3b):** the same Δh at 20 random split times inside each debate's deb phase.
- **Synthetic (axis F, before real data):** kinetic Ising on the real #12 skeleton and update order (real t_call, t_first, call modes; one room) with a planted sink judge per debate (random agent), planted team couplings, and a role-field-only world; recovery of the planted judge's rank and of J_ST − J_OT. The ridge λ is chosen there and frozen.

## Faithfulness scorecard
Scored per model, mapping and window; 0 = not done or failed, 1 = partial, 2 = passed. Scheme and promotion thresholds: `writeup/paper.tex`, Sec. "Assessing model faithfulness".
**Rival models:** R-chair (judge as source/agenda), R-alternation (turn-taking across teams), R-field (role schedule only), R-null.
**Locked holdout used for confirmation:** none yet. Planned: NE37 / #48 (2026-06-22; the operator-designated focal agent; R1 transfer). #45 is blocked by H02's same-family run.

| Axis | Test | Score | Evidence |
| --- | --- | --- | --- |
| A mapping | variables defined from dataset fields; assumptions listed; invariant across families and regimes | 1 | Ledger call-clock spins and reads (99.97% agreement); regime-I clock contested (H67); the chat-clock variant moves the judge to median rank 4. |
| B assumptions | stationarity, Markov order, time-rescaling, update-order audit | 1 | Real call order in fits and synthetic; per-debate stationarity and a constant self term assumed. |
| C adequacy | beats the null hierarchy, day-blocked held-out data | 1 | P1 inside rank and field-only nulls (p 0.15 / 0.24); P2 beats the team permutation reversed (p 0.01); G26 leader vs skeleton Fisher p ≈ 0.08. |
| D unfitted predictions | unfitted statistics and the model's signature | 1 | Team blocks reversed; verdict step inside the band as specified; J_DJ − J^P_DJ ≤ 0.05 holds. |
| E interventional | predicts the change across a natural experiment | 1 | Role rotation: within-agent judge contrast +0.39 (p 0.12). |
| F identifiability | synthetic recovery with village sampling; robust to preprocessing | 2 | Synthetic on the real skeleton: size ≤ 0.01, 80% power at a = 0.6, role field fakes no sink, team power 0.87. |
| G ground truth | agrees with known structure | 1 | DQ6 judges rank 1 in 3/10 (chance 1.4); teams recovered with the opposite sign; #26 leader recovered as a source. |
| H comparative | beats the named rivals | 1 | R-alternation beats H115 on teams; R-chair rejected for judges; R-null not rejected. |
| I transfer | holds in other same-mode periods, including the holdout | 0 | Leader-as-source in G26 only (G35, G44 null); holdout not run. |

## Prediction
*Written 2026-10-04 22:02 UTC, before running any H115 statistic on real data.*

**What I had seen.** Cards H21, H37, H65, H101, H67, H40, H86 and H90 (headlines). In particular: H65 reports that #12 judges receive +0.45 more agent replies per statement than as debaters (an argument for R-chair); H67 reports the regime-I per-call read-out jump J₁\* ≈ 0.007 [−0.002, 0.014] in 12a and calls the hop-1 clock "wrong" for regime I; H101 reports co-usage team blocks (J +0.15 within vs −0.60 across). Structural counts only for H115: calls, chat-mode calls and talk calls per debate window (170–630 calls, 7 agents present in every debate) and the DQ6 `phase` timing rows (no agent column). I have not read which agent judged any debate, nor the teams.

**Power context.** Per-call coupling in regime I is small (J₁\* ≈ 0.007 in probability, about 0.02 in Ising units). A judge-sink signal must be far larger than the typical coupling to be ranked first in a 7-agent, 300-call window. The synthetic decides the minimum detectable sink before the real run.

| ID | Prediction | Against (kill) | Credence |
| --- | --- | --- | --- |
| **P1 (primary)** | Blind S^R ranking: judge median rank ≤ 2 over the 10 debates **and** rank 1 in ≥ 4 debates (Bin(10, 1/7) p ≈ 0.05), and the judge's rank beats the field-only skeleton null (N2, p < 0.05). | **Kill (HH):** judge median rank ≥ 4. | 0.25 |
| P1b | Within-agent contrast: S as judge minus S as non-judge > 0 (judge-label permutation p < 0.05). | ≤ 0 | 0.35 |
| P1c (read-gating) | Mean judge rank under S^R better (smaller) than under S^P. | S^P ranks the judge as well or better (role timing, R-field) | 0.4 |
| **P2** | Team blocks: J_ST − J_OT > 0, team-permutation p < 0.05. | **Kill (HH):** J_ST − J_OT ≤ 0 or p > 0.2 (team blocks absent), provided the synthetic power at J_ST = 0.3 is ≥ 0.8; else inconclusive. Rival R-alternation predicts J_OT > J_ST in the deb phase. | 0.3 |
| P3 | Rulings are fields: (a) J_DJ − J^P_DJ ≤ 0.05 (no read-out kick from the judge's talk on debaters) **and** (b) |Δh_D| at the verdict exceeds the 95th percentile of placebo boundaries. | (a) fails with CI above 0.05, or (b) inside the placebo band | 0.4 |
| **R1 (replication)** | Designated leaders are not sinks: the leader's normalized sink rank u_L ≥ 0.5 (source half) in ≥ 2/3 of role windows (G26, G35, G44 pooled count), following H65's attention premium. The sink score then separates judges (P1) from leaders. | u_L < 0.5 in ≥ 2/3 of windows | 0.55 |

**What would count against H115 as a whole:** P1's kill (judge median rank ≥ 4) together with P2's kill. If P1 fails but the judge ranks at the bottom (median u ≥ 0.75), R-chair is supported instead: the judge is a source, not a sink.

### Synthetic result (axis F) and Amendment A1 (2026-10-04 22:17 UTC, after the synthetic, before any real-data H115 statistic)
Kinetic Ising on the real #12 skeleton and update order (12,711 calls; real t_call, t_first, call modes; one room). Field = each agent's real week-level talk logit per call mode; J₀ = 0.02 for all pairs; self coupling 0.3. Per debate a random planted judge with in-couplings +a from every debater, random teams with within-team +b. 100 worlds per grid point (`analysis/synthetic.py`; `data/processed/H115-debate-judge-role-recovery/synthetic/synthetic.json`). Variants: 50 worlds (`synthetic_variants.py`).

| Planted | P(judge rank 1) | P1 support rule | P1 kill (median ≥ 4) | J_ST − J_OT (z > 1.96) |
| --- | --- | --- | --- | --- |
| a = 0 (null) | 0.14 | 0.00 | 0.71 | 0.01 |
| a = 0.15 | 0.23 | 0.07 | 0.20 | — |
| a = 0.3 | 0.36 | 0.46 | 0.06 | — |
| a = 0.6 | 0.53 | 0.86 | 0.00 | — |
| a = 1.0 | 0.64 | 0.95 | 0.00 | — |
| b = 0.3 (teams only) | 0.13 | 0.00 | 0.67 | est 0.27, power 0.87 |
| role field only (judge +0.4 post, −0.2 deb; a = 0) | 0.14 | 0.01 | 0.63 | 0.03 |

(additive estimator, λ = 4; λ = 1 and 16 within ±0.07 everywhere.)
- **Size:** the P1 support rule fires in ≤ 1% of null and role-field-only worlds. The agent × phase intercepts absorb a planted role schedule: the field-only judge ranks first in 14% of debates (chance 1/7).
- **Power:** the minimum sink the support rule detects at 80% is a ≈ 0.6 Ising units (a logit step of 1.2 per read debater). The kill rule (median rank ≥ 4) fires in ≤ 7% of worlds with a ≥ 0.3, so a kill rules out a ≥ 0.3 at power ≥ 0.93; it does not rule out a ≈ 0.15 (kill 20%).
- **In-flight S^P** carries no planted signal (judge rank 1 in 13–19%), as P1c needs.
- **Teams:** b = 0.3 is detected with power 0.87 (size 0.01–0.04), so P2's kill clause is powered at J_ST − J_OT = 0.3.
- **Variants:** full J (λ = 4) matches the additive fit (support 0.56 / 0.84 at a = 0.3 / 0.6; kill 0.56 at a = 0). The chat-mode clock variant has much less power (support 0.18 / 0.28) because it drops ~75% of calls; it is a reading of H67-R1, not a power-equivalent estimator.

**Amendment A1 (not post hoc):** λ = 4 (logit ridge on couplings; prior SD 0.25 Ising units) for the additive primary and the full-J variant; the pair-type model also uses λ = 4. Predictions unchanged. P1's kill is read as "excludes a judge sink of ≥ 0.3 Ising units"; a pass of the support rule needs a ≳ 0.6.

## Results by goal period
| Period | Role | Verdict | Key numbers |
| --- | --- | --- | --- |
| [G12](goalperiod-subhypotheses/G12/README.md) | native | failed | judge rank 1 in 3/10, mean u 0.38 (p 0.15 / 0.24); J_ST − J_OT −0.16 ± 0.08 (p(≤) 0.01) |
| [G26](goalperiod-subhypotheses/G26/README.md) | replication | supported | leader source half 5/6, mean u_L 0.80 vs null 0.55 (Fisher p ≈ 0.08) |
| [G35](goalperiod-subhypotheses/G35/README.md) | replication | failed | source half 3/5, mean u_L 0.48 = null 0.48 |
| [G44](goalperiod-subhypotheses/G44/README.md) | replication | mixed | 2 windows: u_L 0.80, 0.00 |

## Results
### Round 1 (2026-10-04): exploratory, non-holdout
Scheme check: my read rule reproduces the ledger's sender sets in 99.97% of #12 calls (99.94–99.99% in #26, #35, #44). Code: `scheme/callspins.py`, `scheme/build.py`, `analysis/run_g12_blind.py`, `run_g12_unblind.py`, `run_replication.py`; data `data/processed/H115-debate-judge-role-recovery/`. H86 gauge (`taylor_c_shared`, activity_trim): c_× = 0.044 [0.025, 0.059] in 12a (φ_sh 0.28), 0.032 [0.005, 0.062] in 26 (φ_sh 0.17), 0.007 in 35, −0.003 in 44b. The agent × phase (or × mode) intercepts absorb such a field, and the role-field-only synthetic shows no false sink.

**Predictions scored (as written, read through A1):**
| ID | Prediction | Observed | Verdict |
| --- | --- | --- | --- |
| P1 | judge median rank ≤ 2, rank 1 in ≥ 4, beyond the field null | ranks 2, 6, 6, 1, 1, 3, 7, 4, 2, 1 (median 2.5; rank 1 in 3); mean u 0.38; uniform p 0.15, field-only skeleton p 0.24 | not supported (kill not reached) |
| P1b | within-agent judge contrast > 0 | +0.39 (permutation p 0.12) | not supported |
| P1c | read beats in-flight | mean rank 3.3 vs 4.0 | direction only |
| P2 | J_ST − J_OT > 0 | −0.16 ± 0.08; permutation p(≥) 0.99, p(≤) 0.01; in-flight −0.06 ± 0.09 | **failed: HH kill fires (reversed)** |
| P3 | J_DJ − J^P_DJ ≤ 0.05 and a verdict field step | +0.02 ± 0.11 (consistent); \|Δh\| 0.12 inside placebo band (p 0.81) | failed |
| R1 | leaders in the source half in ≥ 2/3 of windows | 9 of 13 windows (0.69) pooled; G26 5/6, G35 3/5, G44 1/2 | supported pooled, carried by G26 |

**Reading.**
1. **No blind judge.** The judge leans toward the sink end (mean u 0.38 vs 0.46 under the field-only null), but by an amount the week cannot resolve. In synthetic terms the observation is the median of a = 0.15 worlds and the 1st percentile of a = 0.6 worlds. A judge whose talk follows debaters' talk by ≥ 0.6 Ising units per read debater does not exist here. Post hoc, with labels, the pooled pair-type fit gives the judge's in-coupling from debaters J_JD = 0.28 ± 0.09 and debaters' coupling to the judge J_DJ = 0.07 ± 0.07: the direction HH353 named, at a size too small for blind ranking.
2. **Debate talk is antiferromagnetic across teams.** A debater's next call talks more after reading an opponent (J_OT 0.20) than a team-mate (J_ST 0.04); the read-gated contrast (−0.16) is larger than the in-flight one (−0.06), so it is a read-out coupling, not a shared schedule. It is strongest before the first speech (pre −0.36 ± 0.15). This is the opposite sign to the co-usage blocks of H101 (+0.15 within, −0.60 across): team-mates share words, opponents answer each other.
3. **Leaders are talk sources, when they are anything.** The #26 elected leader is the top source of ten agents on 01-06, 01-07 and 01-09, as H65 found for content. Rotating lead designers (#35) and an intermittent installed leader (#44) show no signal. Rank tests on one agent need the skeleton null: the null mean u_L is 0.38–0.62 per window, not 0.5.
4. **Clock.** The chat-mode clock variant (H67-R1) puts the judge at median rank 4, but the synthetic gives it little power (it drops ~75% of calls), so it does not decide which clock is right.

**Scorecard (round 1).**
| Axis | Score | Evidence |
| --- | --- | --- |
| A mapping | 1 | Spins and reads from the ledger call clock (99.97% agreement); regime-I clock contested (H67), and the chat-clock variant moves the judge to median rank 4. |
| B assumptions | 1 | Update order is the real call order (the synthetic uses it); per-debate stationarity and a constant self term assumed; agent × phase fields. |
| C adequacy | 1 | P1 does not beat the rank or field-only nulls; P2 beats the team permutation in the reversed direction (p 0.01); G26 beats the skeleton null weakly (Fisher p ≈ 0.08). |
| D unfitted predictions | 1 | Team blocks and the verdict step were not used in ranking: one came out reversed, one inside the placebo band. |
| E interventional | 1 | Role rotation across debates gives a within-agent contrast of +0.39 (p 0.12). |
| F identifiability | 2 | Synthetic on the real skeleton: support-rule size ≤ 0.01; 80% power at a = 0.6; a role field alone fakes no sink; team power 0.87 at 0.3. |
| G ground truth | 1 | DQ6 judges ranked first in 3/10 (chance 1.4); teams recovered with the opposite sign; the #26 leader recovered as a source. |
| H comparative | 1 | R-alternation beats H115 on teams; R-chair is rejected for judges (mean u 0.38 < 0.5); R-null is not rejected for judges. |
| I transfer | 0 | Leader-as-source holds in G26 only; holdout not run. |

**Claim that stands:** In the #12 debates, per-call talk coupling runs across teams rather than within them (J_ST − J_OT = −0.16 ± 0.08 Ising units, team-permutation p 0.01), and the judge is not recoverable blind as a sink (rank 1 in 3/10 debates; a sink ≥ 0.6 Ising units excluded at P 0.01). **Exclusions:** the pooled J_JD vs J_DJ direction (post hoc, labels used); the signed verdict step (post hoc); the leader-as-source replication (one unit, Fisher p ≈ 0.08); the chat-clock variant (unpowered).

## Confirmatory (planned, not run)
`analysis/confirm.py`, frozen 2026-10-04 22:35 UTC after round 1 (SHA-256 `4745ed30b7fb0910351809a8b0080e426bf5c27c47befa30ae242a13166561c5`).
- **Target:** NE37 / goal #48 (2026-06-22, held out): the whole village redirected to help one agent. The focal agent's code is supplied at run time by the coordinator from the goal record; no held-out text is read.
- **C1:** the focal agent is in the source half of the blind sink ranking (u_F ≥ 0.5). **C2:** u_F above the 90th percentile of its 200-world field-only skeleton null.
- **Reuse:** G48 has one executed run (H04; kick-response, Hawkes, Curie–Weiss families) and no kinetic-Ising-coupling run; H116's confirm uses the same day with a different statistic (a step across #47 → #48): whichever runs second discloses. Holdout ledger family: `kinetic_ising_couplings`, modality talk timing.

## Round 2 redirects
- **H115-R1. Blind team recovery from cross-team coupling.** Pre-register the q = 2 partition of debaters that maximizes cross-block J (antiferromagnetic ground state) and score it against DQ6 teams on G12; then on #34 (held out) for saboteur camps, if a camp structure is defensible there.
- **H115-R2. Addressed reads.** Split read inputs into named and unnamed messages (H08: named messages couple). A judge is addressed by name; the sink signal may sit in the named partition.
- **H115-R3. Leader as source, more units.** A within-agent leader contrast pooled over G26 days, plus #48 / NE37 (planned confirm).
- **H115-R4. Regime-I clock.** Decide between the all-call and chat-mode clocks with a likelihood comparison on G12 and G26 before using either for role recovery.

## Notes
- 2026-10-04 22:02 UTC: H116 needs the same per-call spin scheme. STANDARDS §8 says to move it to `infra/shared/`; the round-1 instructions forbid editing shared files, so `scheme/callspins.py` is duplicated byte-identically in H116's `scheme/` and the move is listed as a suggested shared-file change.
- 2026-10-04 22:40 UTC: `confirm.py` imports `scheme/callspins.py` (SHA-256 prefix `c40dbe842340a79a`, identical in H115 and H116) and `analysis/h115lib.py` (`3d10b6d89834f5ca`); these are frozen with it. The confirm-only switch `callspins.ALLOW_HOLDOUT` is set in memory only after the guard passes.
