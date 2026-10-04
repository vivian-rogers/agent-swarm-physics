# H21: The debate week (#12) is a two-sublattice antiferromagnet

**Status:** running. Exploratory round 1 done 2026-10-03: **primary prediction failed.** There is no full-vector two-sublattice order, but a weak staggered moment along the motion's a-priori stance axis. #34 confirm script written, not run. Promoted 2026-10-03 by Vivian from HH103.
**Round 1b (2026-10-04, section below): two-sublattice order is supported in reply stance, not in content.** The content null holds in both embedding models and every input variant. In DQ2 reply stance the drafted teams order as two sublattices (Δ_stance 0.72, 10/10 debates, beyond the calibrated agent-field null; teams recovered 8/10), the same agent pair turns hostile only when drafted onto opposite sides (16/18 pairs), and the order switches off at the verdict. Where nobody assigns sides (#26 vote, #33 news debate) no camps form. A coupling beyond the assigned field is still not shown.
**Fields:** stat mech, sociophysics
**Origin:** HH103 (`../hypohypotheses/HYPOHYPOTHESES.md`; `../promotion-shortlist.md`)
**Definitions used:** Agent (roster agent), Regime (I), Agent state, **variant vector** (`physics-models/DEFINITIONS.md`), here the sub-variant *"agent state (vector, masked window mean)"* defined below (proposed for DEFINITIONS.md; not added there, edit scope). Agent state, **variant categorical** for the team label (σ_i ∈ {Gov, Opp, judge, bench} per debate). Driving / external field (goal and motion text; the verdict).

## Question
In #12 the agents formed two teams to debate, with one agent judging. In content space, do the teams order as two sublattices: aligned within a team, anti-aligned across teams along the debate axis? Is the staggered magnetization m_A − m_B the order parameter? Does the judge act as an external field that is zero during the debate and switched on at the verdict, collapsing or flipping the order? Practical payoff: detecting factions or teams from content alone, which links to finding hidden teams (D8.3).

**What the record says about the structure (derived before any outcome; see [G12](goalperiod-subhypotheses/G12/README.md)).** #12 is not one long two-team match. It is a tournament of **10 Asian-Parliamentary debates** (09-01 → 09-04; none on 09-05). Each has its own judge, motion and teams, re-drafted every debate (except #7 = #6). Government always argues *for* the motion. So the system gives 10 independent two-sublattice "samples" with known sublattice labels, each with a field (the motion) and a switch-off/switch-on event (the verdict). Team labels: `scheme/labels/g12_debates.json`.

## Model
**From:** `physics-models/11-vector-spins` (vector spins on two sublattices), `physics-models/10-potts` (two-sublattice ordering; q = 2 antiferromagnetic Potts = graph 2-colouring), `physics-models/01-inverse-ising` (antiferromagnetic mean field: staggered susceptibility).

**The magnet, precisely.** For debate d, each debater i carries a unit spin s_i ∈ S^{n−1} (n = 32 whitened embedding dimensions; definition below). Sublattice A = Government (ε_i = +1), B = Opposition (ε_i = −1); the judge sits on neither. The Hamiltonian:

  H_d = − (k_in/N) Σ_{i~j same team} s_i·s_j + (k_out/N) Σ_{i∈A, j∈B} s_i·s_j − h_u ĝ_d·Σ_i s_i − h_s â_d·Σ_i ε_i s_i − Σ_i **h**_i·s_i − h_v(t) ε_W â_d·Σ_i s_i

- ĝ_d: the motion's *topic* direction. Both teams talk about the same motion, so it is a **uniform** field h_u.
- â_d: the motion's *stance* axis (for vs against). The assigned sides are a **staggered field** h_s, on from the motion until the verdict.
- k_in > 0: ferromagnetic coupling within a team (coordination, shared case). k_out > 0: antiferromagnetic coupling across teams (rebuttal pushes the other way).
- **h**_i: the agent/family field (each model's habitual content). Removed by agent-centring, which is legitimate because sides rotate across debates.
- h_v(t) ε_W â_d: the **judge's field**. Zero during the debate; after the verdict it points toward the winner W.

**Order parameters.** Sublattice magnetizations **m**_A, **m**_B; uniform **M**_u = (**m**_A + **m**_B)/2; staggered (Néel) **M**_s = (**m**_A − **m**_B)/2. With the uniform field along ĝ and the staggered order along â ⟂ ĝ, the expected state is a **canted** two-sublattice state (spin-flop-like): both sublattices lean along the topic and split along the stance.

**Mean field.** Staggered self-consistency m_s = L_n(β[(k_in + k_out) m_s + h_s]). The staggered loop gain K_s = β(k_in + k_out) enhances the staggered susceptibility χ_s ∝ 1/(1 − K_s); the uniform gain is K_u = β(k_in − k_out).
- **Fluctuation route** (linear two-block Gaussian limit): the equal-time correlation of the two sublattice magnetizations along â is ρ = −k_out/(1 − k_in), and χ_s/χ_u = Var(δm_A − δm_B)/Var(δm_A + δm_B) = (1 − K_u)/(1 − K_s). We report **K_AF ≡ −ρ**. Common drive (both teams moving with the topic) gives ρ > 0 (ferro-like); antiferromagnetic coupling gives ρ < 0. Measurement noise attenuates |ρ| toward 0, so this is a lower bound.

**What separates a coupled antiferromagnet from its rivals.** A debate *assigns* the sides, so staggered order is expected from h_s alone. The AF claim needs coupling signatures beyond that.

| Model | static staggered order (O1–O3) | after agent-centring (O5) | after role masking / generic axis removed (O4) | remanence after the verdict (O6) | sublattice fluctuations ρ (O7) |
| --- | --- | --- | --- | --- | --- |
| **coupled AF** (k_out > 0, k_in > 0) + h_s | yes | survives | motion-specific part survives | slow decay, R > 0 | ρ < 0 |
| **staggered paramagnet** (h_s only, k = 0) | yes | survives | survives | instant collapse, R ≈ 0 | ρ = 0 |
| **family fields** (teams = labs) | only uncentred | vanishes | n/a | n/a | n/a |
| **role vocabulary** ("as Leader of the Opposition…") | yes (unmasked) | survives | vanishes | n/a | n/a |
| **ferromagnetic topic order** (uniform field only) | no | — | — | — | ρ > 0 |

## Data scheme (`scheme/`)
- **Inputs:** shared `chat_core` + `chat_text` (text in memory only), `roster`, `calendar`, `embeddings/chat_index`, regime-I whitener (`common.load_whitener("I", 32)`, fitted on non-holdout statements). `chat_mentions_clean` is not needed (no mention-based variables).
- **Labels** (`scheme/labels/g12_debates.json`, committed; no agent text): judge, Government/Opposition line-ups, bench, winner and score, paraphrased topic, and the message ids of the line-up, motion, first speech and verdict. Derived from the record before any outcome; see [G12/README.md](goalperiod-subhypotheses/G12/README.md).
- **Phases** (rule fixed before outcomes):
  - pre = [max(line-up fixed, motion announced, first speech − 15 min), first speech);
  - deb = [first speech, verdict);
  - post = [verdict, min(verdict + 10 min, next debate's pre start, day end)).
- **Transform** (`scheme/build_g12.py`):
  - **Masking.** Agent names and aliases → "someone"; team/role words (Government, Opposition, PM, LO, Whip, …) → "speaker" (`scheme/masking.py`). Stance words are kept.
  - **Embedding.** bge-small-en-v1.5 on CPU, the same model as the shared embeddings. The CPU-vs-stored cosine on unmasked text is 1.0000. Masking changed 2,624 of 3,619 messages.
- **Agent state (vector, masked window mean):**
  1. whiten the masked embedding (regime I, D = 32);
  2. subtract the agent's mean over all its #12 statements (agent-centring);
  3. average the agent's statements in the window (≥ 2 statements), unweighted;
  4. subtract the debaters' window mean (debate-centring), or, for any projection of agent i onto a team axis, the mean of the *other* debaters only (leave-one-agent-out frame);
  5. normalize.
- **Output:** `data/processed/H21-debate-antiferromagnet/G12/`:
  - `statements.parquet`: message id, time, agent, lab, length, debate, phase, team, verdict flag, row links;
  - `emb_masked.npy`: fp16, 3,619 × 384;
  - `motions.npz`: topic and pro/con template embeddings of each motion; the motion text itself is not stored;
  - `debates_resolved.json`;
  - `_provenance.json`.

  2.8 MB in total. Results files are written by `analysis/`.
- **Regimes covered:** I only (#12).

## Candidate goal periods
G12 (2025-09-01 → 09-05; not held out). Confirmation: #34 (🔒), saboteurs vs villagers with hidden roles. There, recovering the teams from staggered order would be a detection test (`analysis/confirm_g34.py`, written, not run).

## Links to other hypotheses
H01 D3.4 (polarization), D8.3 (hidden-role detection), H11 (Potts sign), H13 (family fields, a confound to control).

## Observables
All computed per debate on the 'deb' phase unless stated, then pooled with equal weight per debate. Debaters only; judge and bench excluded. Code: `analysis/afmlib.py`, `analysis/h21core.py`.

- **O1 Staggered order (primary): Δ̄.** Within-team minus cross-team mean cosine of the debaters' spins (agent- and debate-centred), averaged over debates. Two-sublattice order gives Δ̄ > 0.
- **O2 Team recovery from content alone.** For each debate, the two-block partition with the true block sizes that maximizes Δ (exhaustive: 3–10 partitions per debate). We count debates where it equals the true team split; chance is 1/(number of partitions) per debate. This is the zero-temperature two-sublattice (q = 2 AF Potts) ground state of the content-similarity graph.
- **O3 Staggered magnetization along a cross-fitted debate axis.**
  - **LOAO projection.** For each agent i, the axis is â_{−i} = unit(mean_{A∖i} s − mean_{B∖i} s), built only from the *other* agents (frame centred on their mean). Then σ_i = ε_i s_i·â_{−i} and m_s = ⟨σ⟩.
  - **Magnetizations.** We also report |**M**_s| and |**M**_u| (agent-centred, not debate-centred spins), and the topic alignment **M**_u·ĝ_d by phase. ĝ_d is the motion text's embedding.
- **O4 Generic vs motion-specific stance; role-vocabulary leakage.**
  - **Generic axis.** For debate d, the generic Gov−Opp axis is fitted on the *other* nine debates (cross-fitted), and we measure σ along it.
  - **Motion-specific part.** O1–O3 recomputed after projecting the generic axis out.
  - **Masking.** Masked vs unmasked embeddings.
  - **A-priori text axis.** The embedding difference of "I strongly support / oppose the motion: ⟨motion⟩" templates. We test it raw, and with the cross-debate template mean removed.
- **O5 Family-field confound.** Four checks:
  1. lab sorting of the teams vs its partition expectation;
  2. O1 without agent-centring;
  3. pair regression cos_ij = b_team·same_team + b_lab·same_lab with debate fixed effects (b_team p-value by re-partitioning);
  4. lab-partition placebo: Anthropic vs others as the "teams".
- **O6 The verdict as a field.**
  - **Remanence** R = ⟨σ_post⟩/⟨σ_deb⟩. Post-verdict spins are taken in each agent's debate-phase LOAO frame, so a uniform shift toward the winner is kept.
  - **Winner asymmetry.** (Δσ of winners) − (Δσ of losers), per debate. A field toward the winner raises the winners' σ and lowers the losers'.
  - **Loser flip.** Mean loser σ_post < 0 means the losers crossed to the winning side.
  - **Judge check.** The projection of the judge's verdict message on the debate axis, signed by the winner (manipulation check).
- **O7 Staggered susceptibility from fluctuations.** 3-min bins in the 'deb' phase. Sublattice magnetizations m_A(b), m_B(b) are projected on a debate axis cross-fitted across odd/even bins and demeaned per debate. We report ρ = corr(δm_A, δm_B), χ_s/χ_u and K_AF = −ρ. The 2-min and 5-min bins are robustness checks.
- **Secondary:** O1–O2 in the 'pre' and 'post' phases. Robustness: D = 16, 64; unmasked; length-weighted means; min statements 1 or 3; dropping #7 (same teams as #6).

## Null / baseline
- **N1 Team-label permutation.** Within each debate, re-partition the debaters into blocks of the true sizes (exact enumeration; 50,000 joint draws for pooled statistics), for O1, O3, O4 and O5(3). For O2, chance recovery is a Poisson-binomial with p_d = 1/(number of partitions).
- **N2 Per-agent random rotation** (model 11): one Haar-random orthogonal matrix per agent for the whole week, applied to its agent-centred vectors. It keeps each agent's trajectory and destroys cross-agent alignment. 2,000 draws, for O1 and O3.
- **N3 Family field.** Agent-centring on vs off; lab-partition placebo; same-lab covariate (O5).
- **N4 Role vocabulary.** Masked vs unmasked; generic cross-debate axis (O4).
- **N5 Fluctuations.** Permute the Opposition's bins within each debate (breaks temporal pairing, keeps marginals), for O7.
- **N6 Rival models** (table above): staggered paramagnet, family fields, role vocabulary, ferromagnetic topic order.
- **Synthetic** (axis F, `analysis/synthetic.py`). Null calibration of every test at G12's exact design (who spoke when), including strong family fields and deliberately lab-sorted teams.

## Prediction
*Written 2026-10-03, before running the analysis on real data.* At this point the labels and masked embeddings were built and the synthetic validation (axis F) had run on G12's design. No alignment statistic of the real #12 data had been computed. Power context (synthetic, G12's exact design: 10 debates, 4–6 debaters, real statement counts):
- Δ̄ under the null has sd ≈ 0.037.
- Δ̄ reaches 80% power at a staggered field μ ≈ 0.5 per-dimension noise units (Δ̄ ≈ 0.12, about 3.7 of 10 teams recovered). It reaches 100% at μ = 0.8 (Δ̄ ≈ 0.27, about 6.6 recovered).
- Injection into the real #12 statement noise (E6, team structure destroyed by within-agent shuffling; finished before the real run) is a little harder. The null sd of Δ̄ is 0.045. Power is 0.60 at μ = 0.5 (about 2.7 teams recovered) and 0.995 at μ = 0.8 (Δ̄ ≈ 0.27, about 5.4 recovered).
- So P1 is a test of whether the debate's staggered field is at least about half the per-dimension statement noise.

Credences are mine, given only the structure above.

- **P1 (primary): two-sublattice order exists.** Δ̄ > 0 with team-permutation p < 0.01, and above the per-agent rotation null's 95th percentile. Expected size Δ̄ ≈ 0.10–0.35: assigned public sides plus one-paragraph argumentative speeches should be a strong staggered field, diluted by procedural and waiting messages. Credence 80%. **Against:** p > 0.05.
- **P2: teams are recoverable from content alone.** Exact recovery of the team split in ≥ 4 of 10 debates (chance ≈ 1.2), Poisson-binomial p < 0.01. Credence 65%. **Against:** ≤ 2 recovered.
- **P3: staggered, not uniform, order along the debate axis.**
  - LOAO staggered magnetization m_s > 0, p < 0.01.
  - |**M**_s| exceeds its partition-null mean in the 'deb' phase.
  - The uniform magnetization carries the topic: **M**_u·ĝ_d > 0 in 'deb' for ≥ 8/10 debates (the canted state).

  Credence 75%.
- **P4: motion-specific stance, beyond role words and generic rhetoric.**
  - After projecting out the cross-debate generic axis, Δ̄ keeps ≥ 50% of its value and stays significant (p < 0.05). Credence 70%.
  - The generic "proposing vs opposing" direction transfers across motions too (σ_gen > 0, orientation-flip p < 0.05). Credence 50%.
  - Unmasked Δ̄ > masked Δ̄ (role vocabulary inflates it). Credence 80%.
  - The a-priori text axis (pro − con templates of the motion) gives σ_text > 0 but weakly. Bag-of-meaning embeddings are poor at negation, so p < 0.05 is *not* predicted. Credence of significance 25%.
- **P5: not labs.**
  - Teams are not lab-sorted beyond their partition expectation.
  - The pair-fixed-effects team coefficient b_team > 0 (p < 0.05). This is the within-pair contrast that removes any persistent pair similarity, including shared family.
  - The lab-partition placebo in agent-centred data is not significant (p > 0.05).
  - Δ̄ keeps ≥ 70% of its uncentred value after agent-centring.

  Credence 70%. **Against:** b_team ≤ 0 or the lab placebo significant.
- **P6: the verdict switches the order off; the judge's field is weak.**
  - Staggered remanence after the verdict R = σ_post/σ_deb < 0.5, with the debate-bootstrap CI upper bound < 1. Credence 55%; post windows are short and noisy.
  - Losers do not flip: mean loser σ_post ≥ −0.05.
  - Winner asymmetry > 0 in sign but not significant (no significance predicted).
  - Manipulation check: the judge's verdict message points toward the winner's side in ≥ 7/10 debates (credence 60%).
- **P7: sublattice fluctuations (staggered susceptibility).** ρ(δm_A, δm_B) < 0, i.e. χ_s/χ_u > 1 and K_AF > 0, in sign only. **Not** predicted significant: synthetic E4 shows the test is badly underpowered at G12's bin occupancy. ρ > 0 with p < 0.05 would count against AF and for common drive.

**Verdict rule for G12.**
- **"Two-sublattice order: supported (exploratory)"** if P1, P2 and P5 pass.
- **"Coupled antiferromagnet"** additionally requires coupling evidence beyond the assigned staggered field: P7 significant (ρ < 0), or remanence R > 0 together with ρ ≤ 0.
- **Expected outcome:** two-sublattice order supported, but **"staggered paramagnet" not rejected**. The sides are assigned, so h_s alone can produce the order. Post-verdict remanence can come from single-agent inertia (reflecting on one's own case) without any coupling, so R > 0 alone is not coupling evidence.

### Round-1b pre-registration: a stance channel next to the content channel (2026-10-04 07:14 UTC, before any round-1b statistic)
**Seen before writing:** round 1; H37's #12 stance results (its own Jev labels: opponents −0.13 vs teammates +0.32, AUC 0.74, 7/10 teams); DQ2's #12 check on its labels (opposite-team "opposes" 33% vs 6%, soft sign −0.18 vs +0.31). So the stance-channel expectations below are informed replications, not blind predictions. P1–P7 above are unchanged and are re-run on the content channel with the second embedding model (gte, masked text re-embedded), the shared style-residualized vectors and the dedupe flags.

**Stance spin of a reply** (DQ2 `reply_pairs`, `pair_set = cand`, labelled; B and A debaters of the same debate, B inside the phase): s = p_supports − p_opposes, weighted by p_reply (soft); hard class +1 / 0 / −1 for the calibrated null.
- **S1 (P1 in stance).** Δ_stance = mean s over same-team replies − mean s over opposite-team replies, equal weight per debate, > 0 with team-permutation p < 0.01 **and** above the 95th percentile of the calibrated agent-field null (`infra/shared/nulls.py: agent_field_null`, ordered logit with speaker and target fields, 500 simulations). Credence 0.9.
- **S2 (P2 in stance).** The ground-state two-camp split of each debate's stance graph (debaters only, true block sizes, exact enumeration) equals the true teams in ≥ 4/10 debates (Poisson-binomial p < 0.01). Credence 0.7.
- **S3 (P6 in stance).** In the post-verdict window Δ_stance falls below half its debate value. Credence 0.7.
- **S4 (beyond topic, H37's O2 on DQ2 labels).** On the same replies, AUC of stance for same vs opposite team ≥ 0.65 while the content cosine (masked bge and gte) gives AUC in [0.4, 0.6]. Credence 0.75.
- **Content channel under the new inputs.** P1 still fails (credence 0.85); the a-priori text-axis tilt stays positive in gte (credence 0.6).
- **Verdict rule for 1b:** "two-sublattice order: supported (exploratory)" now needs P1 **or** S1, plus P2 **or** S2, plus P5; "coupled antiferromagnet" still needs a coupling signature beyond the assigned field (P7, or the G12 native within-pair contrast in stance).

## Confirmatory test (#34, 🔒, written 2026-10-03, not run)
`analysis/confirm_g34.py` refuses to run without `--confirm --i-understand-this-uses-the-locked-holdout`. `--dry-run` runs every code path on non-holdout stand-ins: the label rule on #33, and detection on #12 with a seeded random 1–2-member minority of each Opposition as stand-in "saboteurs". It asserts that no holdout row is read.

- **Question.** In #34, private d6 rolls make a hidden saboteur minority each day. Hidden roles are a hidden staggered field. Can an *unsupervised* sublattice score recover them from public chat content?
- **Labels.** An agent-day is a saboteur if the agent's *own* intentions or chat that day self-identify as saboteur (pre-registered regexes, no villager pattern), and a villager otherwise; days matching both are ambiguous and dropped. Coverage gate: fewer than 4 saboteur agent-days, or a saboteur rate below 1/24 (expected 1/6), makes the test **untestable**.
- **Content.**
  - public chat only (intentions are the label source and are never used as content);
  - masked for names, role words and game-role words (saboteur, villager, roll results);
  - whitened (regime II, fitted on non-holdout data), agent-centred over #34.
- **Primary statistic.** Minority-sublattice score q_i = −u_i·mean_{j≠i} u_j, in the uncentred frame where the room's shared direction defines the majority. AUC(saboteur > villager), with a within-day label-permutation null.
- **Secondary statistics.** Exact recovery of the size-k saboteur set; supervised LOAO m_s; lab-as-role placebo; uncentred AUC.
- **Decision.**
  - SUPPORTED if AUC ≥ 0.60 and p < 0.05;
  - FAILED if AUC < 0.55 or p > 0.20;
  - else MIXED.

  Credence of SUPPORTED ≈ 30%. Saboteurs try *not* to stand out, and a hidden private field is far weaker than G12's assigned public sides.
- **Reuse (holdout policy).** Other written-but-not-run confirm scripts also plan to use #34:
  - H01 `confirm_d32.py`: pair residual cosines of content embeddings around #voted-out;
  - H05 `confirm_ne12.py`: rooms and activity;
  - H07 `confirm_h34.py`: repo lineage;
  - H12 `confirm.py`: dimensional collapse of content embeddings;
  - H19 `confirm.py`: loop gain.

  H21's statistic is different from all of these: hidden-role labels and a sublattice-recovery AUC, which nobody computes. If H01 or H12 run first, H21 shares their modality (chat embeddings) but not their statistic. Under the 2026-10-03 reuse policy that is allowed with disclosure in both cards and in LOG.md, provided no one has examined the saboteur labels.

## Faithfulness scorecard
Scored per model, mapping and window; 0 = not done or failed, 1 = partial, 2 = passed. Scheme and promotion thresholds: `writeup/paper.tex`, Sec. "Assessing model faithfulness". Scored for the **coupled two-sublattice antiferromagnet** on masked content vectors in G12 (round 1); round-1b scores (marked) use the DQ2 stance mapping, evidence in the Round 1b section.
**Rival models:** staggered paramagnet (assigned sides only); family (lab) fields; role vocabulary; ferromagnetic topic order in the motion's uniform field.
**Locked holdout used for confirmation:** none yet. #34 is planned (`analysis/confirm_g34.py`, not run).

| Axis | Test | Score | Evidence |
| --- | --- | --- | --- |
| A mapping | variables defined from dataset fields; assumptions listed; invariant across families and regimes | 1 | Spins: masked, whitened, agent-centred chat window means. Teams: verified labels with message ids. Phases: a rule fixed before outcomes. Family field handled by agent-centring and pair fixed effects. One regime, one embedding model; masking is a design choice. |
| B assumptions | stationarity, Markov order, time-rescaling, update-order audit | 0 | No stationarity or equilibrium audit. χ_s from fluctuations assumes FDT, which is untested. |
| C adequacy | beats the null hierarchy, day-blocked held-out data | 2 (1b, stance; round 1: 1) | The full-vector AF statistics do **not** beat the team-permutation or rotation nulls (Δ̄ p = 0.34, m_s p = 0.27). Only the a-priori text-axis staggered moment beats its permutation null (p = 0.002; 9/10 debates; each debate is an independent block). |
| D unfitted predictions | unfitted statistics and the model's signature | 1 (1b; round 1: 0) | Teams not recovered (1/10, chance 1.5). AF fluctuation signature absent: ρ = +0.53 at 3 min (common drive), not robust across bin widths. |
| E interventional | predicts the change across a natural experiment | 1 (1b; round 1: 0) | Pre-registered verdict test untestable (no order on the LOAO axis to collapse); judge check 3/10. Post-hoc: on the text axis the order *flips* after the verdict, contradicting the "no flip" prediction. The uniform topic field switching off at the verdict (8/8) is descriptive. |
| F identifiability | synthetic recovery with village sampling; robust to preprocessing | 2 (1b; round 1: 1) | Synthetic at G12's exact design: power curves, calibration of every null, three estimator biases found and fixed before the real run, real-noise injection. But the real null is about 2× wider than either synthetic noise model (missing family co-variation), so power was overstated. No embedding-model swap. |
| G ground truth | agrees with known structure | 2 (1b, stance; round 1: 1) | The known teams are *not* recovered from full vectors (0). The a-priori stance axis does separate the known sides (9/10 debates). |
| H comparative | beats the named rivals | 1 (1b; round 1: 0) | The data favour uniform topic order + family co-variation + a weak 1-D staggered field. The coupled AF beats neither the staggered paramagnet nor topic order. |
| I transfer | holds in other same-mode periods, including the holdout | 0 | #34 not run. |

## Results by goal period
| Period | Role | Verdict | Key numbers |
| --- | --- | --- | --- |
| [G12](goalperiod-subhypotheses/G12/README.md) | exploratory | **failed** (AF); descriptive: weak 1-D staggered moment | Δ̄ = 0.028 [−0.10, 0.17], p = 0.34; teams recovered 1/10 (chance 1.5); text-axis σ = 0.092, p = 0.002 (9/10); post-verdict flip −0.36 (post hoc, 7/9); topic order on/off 0.42 → 0.01 |
| [G12](goalperiod-subhypotheses/G12/README.md) round 1b | exploratory + native | **supported in stance** | Δ_stance 0.72 (10/10; agent-field p 0.002); teams 8/10 (chance 1.0); within-pair −0.68 (16/18); post-verdict −0.01; content Δ̄ +0.028 (bge) / −0.028 (gte) |
| [G26](goalperiod-subhypotheses/G26/README.md) | native (1b) | failed (as predicted) | ballot camps vs stance r 0.000 (p 0.51); content −0.07 / +0.08 |
| [G33](goalperiod-subhypotheses/G33/README.md) | native (1b) | failed (as predicted) | mean stance +0.50; camps p 0.10 vs agent-field null; 1 negative pair (null 1.2) |
| #34 🔒 | confirmatory (planned) | not run | `analysis/confirm_g34.py`; dry run OK on #33 / #12 stand-ins |

## Results
**Round 1 (G12, 2026-10-03). Code:** `analysis/g12_analysis.py` (pre-registered), `analysis/g12_posthoc.py` (post hoc, labelled), `analysis/synthetic.py`. **Data:** `data/processed/H21-debate-antiferromagnet/G12/results*.json`. **Figures:** `figures/summary.pdf` (one page), `figures/summary_obs.pdf`, `figures/synthetic_validation.pdf`, `goalperiod-subhypotheses/G12/figures/`.

**In magnet language, what the debate week is.** During a debate the six debaters form a **ferromagnet in the motion's uniform field**, not a two-sublattice antiferromagnet.
- **Uniform order is strong.** |**M**_u| ≈ 0.64–0.90; alignment with the motion's topic direction ĝ is 0.42 in debates (10/10 positive).
- **The uniform field switches.** Topic alignment is 0.28 in the pre phase and falls to 0.01 within 10 min after the verdict (8/8 debates, sign p = 0.004).
- **Staggered order is absent in the full vector space.** Within-team minus cross-team cosine Δ̄ = 0.028 (p = 0.34). The true team split is the best-separated split in 1/10 debates (chance 1.5). The LOAO staggered magnetization is 0.03 (p = 0.27).
- **Null across every variant:** masked or unmasked, D = 16/32/64/128, length-weighted, speeches only, 1–3 statement minimum, dropping #7, and the pre and post phases.
- **Family co-variation beats team order.** Pairs from the same lab stay more aligned than team-mates, even after agent-centring (b_lab = 0.24 vs b_team = 0.08; post-hoc same-lab excess +0.20 cos, exact p = 0.10). The family "exchange" is a debate-dependent *shared response*, not a constant field.

**Where the staggered order does live: one externally defined direction.**
- **The axis.** It is the embedding difference of "I strongly support / oppose the motion: ⟨motion⟩" templates, built from the motion text with no labels.
- **Pre-registered result.** Government speakers sit on the support side of Opposition speakers: σ_text = 0.092 (p = 0.002; 9/10 debates). With the cross-debate template mean removed, 0.059 (p = 0.03). This was pre-registered as a secondary test *not* predicted to reach significance.
- **Size.** At the statement level the Gov − Opp separation is 0.43 whitened units (p = 0.0008), a staggered field μ ≈ 0.2 of the per-dimension statement noise.
- **Why the full-vector tests miss it.** Under real noise, full-vector order needs μ ≳ 0.5 to show (synthetic E6; the real null is wider still). So the system is a **staggered paramagnet with a small, essentially one-dimensional staggered moment**: the assigned side tilts each debater slightly along the stance axis; topic, family and individual noise dominate the other 31 dimensions.
- **No coupling signature.** Sublattice fluctuations are not anti-correlated (3-min ρ = +0.53, common drive, as pre-specified against AF; it is not robust: 2-min −0.12, 5-min +0.14).

**The verdict (post hoc, labelled).** On the stance axis the order does not relax to zero after the verdict; it **reverses**.
- Gov − Opp goes from +0.43 in debates to −0.36 in the 10 minutes after the verdict (7/9 debates negative; post/deb ratio −0.92, bootstrap CI [−1.94, −0.31]).
- **Decomposition.** A *crossing* field of κ = +0.27 (8/10 debates): each side moves toward the side it did not argue. *No* winner field (w = −0.34, 2/10 positive; if anything, winners concede more).
- The judge's verdict message itself points toward the winner on this axis in 7/10 debates.
- In magnet terms this is **negative remanence**: once the staggered field is removed, a memory-dependent field opposite to each agent's previous side takes over. A plausible mechanism is a trained "acknowledge the other side" prior. The agents' own reflections narrate exactly this; narration is a claim, but the embedding measurement agrees.
- This was found after the primary null, among seven post-hoc checks. One-sided p ≈ 0.015 is not significant after a Bonferroni correction over those seven checks. Treat it as a new hypothesis (proposed HH), not a result.

**Outcome vs prediction** (predictions dated 2026-10-03, before the real-data run):

| # | Prediction | Observed | Verdict |
| --- | --- | --- | --- |
| P1 | Δ̄ > 0, team-permutation p < 0.01; above the rotation null's 95th percentile; Δ̄ ≈ 0.10–0.35 | Δ̄ = 0.028 [−0.10, 0.17], p = 0.34; rotation p = 0.18 | **failed** |
| P2 | teams recovered in ≥ 4/10, p < 0.01 | 1/10 (chance 1.5), p = 0.82 | **failed** |
| P3 | m_s > 0 (p < 0.01); \|**M**_s\| > null; **M**_u·ĝ > 0 in ≥ 8/10 | m_s = 0.032 (p = 0.27); \|**M**_s\| above its null mean in 6/10, small excess; **M**_u·ĝ > 0 in 10/10 | **failed** (staggered); uniform part as predicted |
| P4a | motion-specific part ≥ 50% and p < 0.05 | Δ̄_spec = 0.032 (p = 0.32); no total to keep | **failed** |
| P4b | generic transfer σ_gen > 0, p < 0.05 | −0.069 (flip p = 0.96) | **failed** |
| P4c | unmasked > masked | 0.017 vs 0.028 | **failed** (no role-word inflation, because there is no order to inflate) |
| P4d | text axis σ_text > 0, *not* significant | 0.092, p = 0.002 (9/10); motion-specific 0.059, p = 0.03 | **exceeded** (significant, unpredicted) |
| P5 | not labs: not lab-sorted; pair-FE b_team > 0; lab placebo n.s. | lab sorting −0.08 (anti-sorted); b_team = 0.047 (p = 0.19); placebo p = 0.27; same-lab pairs out-align teams | **moot / failed**: no team effect to protect; family > team |
| P6 | R < 0.5; no loser flip; winner asymmetry n.s.; judge toward winner ≥ 7/10 | LOAO σ_deb ≈ 0, so R undefined (−1.5 ± 6); asymmetry −0.16 (n.s.); judge 3/10. Post hoc on the text axis: flip (−0.36), judge 7/10, crossing κ = 0.27, no winner field | **untestable as registered**; post hoc contradicts "no flip" |
| P7 | ρ < 0 in sign, not significant | ρ = +0.53 at 3 min (upper-tail p ≈ 0.0005); −0.12 at 2 min; +0.14 at 5 min | **failed** (common drive at 3 min, fragile) |

**G12 verdict rule outcome:** P1, P2 and P5 fail, so "two-sublattice order" is **not supported**, and the coupled antiferromagnet is not reached. The honest model is **uniform field + family co-variation + a weak one-dimensional staggered field along the motion's stance axis**, with (post hoc) a post-verdict reversal.

**Synthetic validation (axis F)**, at G12's exact design (`data/processed/H21-debate-antiferromagnet/synthetic/synthetic.json`, `figures/synthetic_validation.pdf`):
- **E1 power.** Δ̄ power 0.21 / 0.83 / 1.0 at μ = 0.3 / 0.5 / 0.8. Calibration: Δ̄ ≈ 0.04 / 0.12 / 0.27. Teams recovered 2.0 / 3.7 / 6.6 of 10. Null rejection ≤ 0.05.
- **E2 family fields.** With the real (reshuffled) teams, the false-positive rate is ≤ 0.01 even at a family field of 3× noise, with or without agent-centring. With *fixed lab-sorted* teams it is 0.31–0.34 even after agent-centring, because persistent pair similarity masquerades as order. Pair fixed effects: 0.02–0.09 (pooled 0.056) on the real design.
- **E3 generic axis.** The generic-axis test is calibrated (0.02–0.05) only with the orientation-flip null and an axis built without agent i (two earlier versions gave 14–16% and 13% false positives).
- **E4 dynamics.** ρ is unbiased after demeaning within bin parity; power 0.8–1.0 at K_s = 0.8 but 0.14–0.24 at K_s = 0.4. A field ramp alone gives false positives up to 0.18. Remanence is 0.13–0.31 with *no* coupling (single-agent inertia) and rises with K_s, so it is not identifiable without the relaxation time.
- **E5.** The rotation null is calibrated (0.017).
- **E6.** Injection into real #12 noise: power 0.60 at μ = 0.5, 0.995 at μ = 0.8. The real permutation null is still about 2× wider than E6's (family co-variation is destroyed by within-agent shuffling).

**Caveats.**
1. **Power.** The full-vector test could only see Δ̄ ≳ 0.13 (μ ≳ 0.55). "No order" means "staggered field < about half the per-dimension noise", consistent with μ ≈ 0.2 on the text axis.
2. **Post hoc.** The text-axis result was pre-registered (as secondary). The post-verdict flip and the crossing/winner decomposition are post hoc (seven post-hoc checks, Q1–Q7).
3. **Template axis.** It keeps stance words. Gov − Opp separation along it could partly be generic "we support / we oppose" rhetoric. The motion-specific version survives (p = 0.03), but the data-driven generic axis does not transfer, so this is unresolved.
4. **One embedding model** (bge-small, poor at negation). No NLI or stance-classifier check.
5. **Procedural noise.** Forfeits, computer-use narration mid-debate, and a judge fixed for #5–#10. Speeches-only is also null, so dilution is not the explanation.
6. **Post windows** are short (35 s and 3.7 min after #7 and #8) and contain the next debate's setup.
7. **Sample.** 7 agents, 10 debates, 4 days, regime I.
8. **The fluctuation estimator** can be pushed negative by a staggered-field ramp, and positive by common topic drift.

**Amendments** (all before the real-data run unless stated):
1. LOAO frame excludes agent i (synthetic found a +0.05 null bias).
2. Generic-axis test switched to a leave-agent-out axis with an orientation-flip null.
3. Fluctuation series demeaned within bin parity (a +0.10 bias).
4. Pair-fixed-effects team test added.
5. Post window 10 min (first draft of the build: 20 min; changed before outcomes).
6. After G12, before any #34 run: `confirm_g34.py` adds S4 (a-priori template role axis) and lowers credences. The primary is unchanged.

**Next steps.**
- Measure stance directly: an NLI / stance scorer of each statement against the motion, and an embedding swap.
- Fit the honest model explicitly: uniform field, family exchange matrix, 1-D staggered field μ.
- Test the post-role reversal on other role-play periods (proposed HH; #26, #51 non-holdout days).
- Decide whether #34 is worth spending: credence of SUPPORTED is now about 10%.

## Round 1b (improved data, 2026-10-04)
*Re-run of round 1's pre-registered statistics (P1–P7 unchanged) on corrected inputs, plus the stance channel (S1–S4, pre-registered above at 07:14 UTC with the H37/DQ2 results disclosed) and three period-native tests (G12 re-drafting, G26 ballots, G33 unassigned debate; predictions written 07:14 UTC in their folders before running). #34 untouched; `confirm_g34.py` not run.*

**What changed in the inputs.**
- **DQ6 ground truth:** H21's #12 labels agree exactly with `ground_truth_labels` (10/10 debates: teams, judges, winners; phase boundaries identical to the second). Nothing to change.
- **Second embedding model:** the masked texts were re-embedded with gte-modernbert on CPU (`scheme/build_g12.py --model gte_modernbert`; CPU vs stored cosine 1.000 on unmasked probes) → `emb_masked_gte_modernbert.npy`, `motions_gte_modernbert.npz`.
- **Other content inputs:** unmasked shared embeddings (both models), DQ5 `style_resid_period` vectors (both models), statements flagged as restatements or copies removed.
- **Stance (DQ2):** `reply_pairs` (`pair_set = cand`, labelled) between two debaters of the same debate; soft stance p_supports − p_opposes weighted by p_reply; hard classes for the calibrated agent-field null (`infra/shared/nulls.py: agent_field_null`, 500 simulations).
- Code (old paths unchanged): `g12_analysis.CONFIG` (model, source, dedupe), new `analysis/r1b.py`, `r1b_figures.py`, `r1b_estimates.py`. Outputs: `data/processed/H21-debate-antiferromagnet/r1b/`.

**Old vs new, content channel (P1–P7).**

| Statistic | Round 1 (bge, masked) | bge masked (1b) | gte masked | DQ5 style-residualized (bge / gte) | restatements removed (bge / gte) |
| --- | --- | --- | --- | --- | --- |
| P1 Δ̄ (team-permutation p) | 0.028 (0.34) | 0.028 (0.34) | −0.028 (0.63) | 0.019 (0.37) / −0.000 (0.49) | 0.008 (0.43) / −0.041 (0.69) |
| P2 teams recovered (of 10; chance 1.5) | 1 | 1 | 1 | 1 / 0 | 1 / 0 |
| P3 LOAO m_s (p) | 0.032 (0.27) | 0.032 (0.27) | 0.012 (0.44) | 0.023 (0.26) / 0.025 (0.28) | 0.014 (0.40) / −0.009 (0.62) |
| P4d a-priori text axis σ (p; positive debates) | 0.092 (0.002; 9/10) | same | 0.055 (0.065; 8/10) | 0.057 (0.010; 9) / 0.031 (0.15; 7) | 0.089 (0.003) / 0.047 (0.086) |
| statement-level Gov − Opp on the axis (p) | 0.43 (0.0008) | 0.43 (0.001) | 0.22 (0.039) | 0.04 (0.006) / 0.01 (0.30) | 0.40 / 0.18 |
| post-verdict reversal (post Gov − Opp; debates negative) | −0.36 (7/9) | −0.36 (7/9) | −0.20 (6/9) | −0.07 (8/9) / −0.03 (6/9) | −0.31 (7/9) / −0.20 (6/9) |
| P5 pair-FE b_team (p) | 0.047 (0.19) | 0.047 (0.19) | −0.013 (0.59) | 0.084 (0.038) / 0.073 (0.072) | 0.054 / −0.021 |
| P7 sublattice ρ at 3 min | +0.53 | +0.53 | +0.33 | +0.15 / +0.02 | +0.32 / +0.21 |
| topic order M_u·ĝ, deb → post | 0.42 → 0.01 | 0.42 → 0.01 | 0.55 → 0.10 | 0.37 → −0.01 / 0.51 → 0.07 | 0.44 → 0.02 / 0.56 → 0.10 |

Unmasked inputs give the same picture (Δ̄ 0.017 bge, −0.046 gte). **The content null is model- and preprocessing-robust;** the text-axis tilt is weaker in gte (negation is still poorly encoded), and the post-verdict reversal survives in both models at the statement level.

**Stance channel (S1–S4).** 478 debater-to-debater replies in debate phases (264 within teams, 214 across).

| Prediction | Observed | Verdict |
| --- | --- | --- |
| S1 Δ_stance > 0 beyond team permutation (p < 0.01) and the agent-field null | soft stance +0.41 within vs −0.32 across ("opposes" 6% vs 36%); **Δ_stance = 0.72**, 10/10 debates, team permutation p < 10⁻⁴ (null 95th pct 0.28); hard labels 0.50 vs agent-field null mean 0.05 (95th pct 0.18), p = 0.002 | **pass** |
| S2 teams recovered from the stance graph ≥ 4/10 | **8/10** (chance 1.0, p = 4×10⁻⁷); misses #9 and #10 (7 and 5 observed pairs) | **pass** |
| S3 order switches off after the verdict | post-verdict Δ = −0.01 (9 debates) vs 0.67 during the same debates; pre-phase Δ already 0.44 | **pass** |
| S4 stance AUC ≥ 0.65, content AUC in [0.4, 0.6] on the same replies | stance 0.79 raw / 0.75 agent-adjusted; content 0.54 / 0.57 (bge), 0.51 / 0.54 (gte) | **pass** |

**Native tests.**
- **G12, re-drafting within pairs: supported.** For the 18 pairs seen both as teammates and as opponents, stance is lower as opponents in 16 (mean −0.68; sign flip p 0.0002; hard labels −0.58 vs agent-field null 5th percentile −0.17, p 0.002), while content shows no contrast (bge −0.046, gte +0.024, n.s.). The hostility follows the assignment, not the pair.
- **G26, ballots as camps: failed, as predicted.** Ballot dissimilarity does not predict stance (Mantel r 0.000, p 0.51) or content (−0.07 / +0.08) during the contest, nor afterwards.
- **G33, unassigned "debate": failed, as predicted.** Mean stance +0.50, "opposes" 6.3% (noise floor), no camps beyond agent fields (p 0.10), 1 negative pair (null 1.2).

**Which verdicts change.** By the 1b rule (P1 or S1, P2 or S2, P5), **two-sublattice order is supported (exploratory) in the stance channel**; P5's intent (not labs or pair affinity) is met by the within-pair contrast. In content P1–P4 still fail. The pre-registered 1b rule also lists the within-pair contrast as coupling evidence; on reflection I do not use it that way: stance measures whether two agents' positions agree, so an assigned staggered field alone predicts opposite-team hostility, and the within-pair design removes pair constants, not the field. **"Coupled antiferromagnet" therefore stays not shown** (P7 is still positive, common drive). G12 Verdict (1b): supported in stance. The post-verdict reversal (round 1, post hoc) is seen on the content stance axis in both models but not in reply stance (Δ ≈ 0 after the verdict: relaxation, not reversal), matching H37.

**Scorecard after 1b** (now scored on the stance mapping, content kept as the failed mapping): C 1 → 2 (stance order beats team permutation and the calibrated agent-field null, per debate), D 0 → 1 (teams recovered 8/10, unfitted; no AF fluctuation signature), E 0 → 1 (ten field switch-offs at known verdict instants: stance order off within 10 min), F 1 → 2 (content null robust across two lineages and five input variants; stance null calibrated, H37 size 0.04), G 1 → 2 (drafted teams recovered; within-pair contrast), H 0 → 1 (stance beats topic and pair affinity; the staggered paramagnet is still not separated from coupling). A 1, B 0, I 0 unchanged (#34 not run; no non-holdout period with assigned teams).
**Figure:** `figures/r1b_stance_vs_content.pdf`. **Estimates:** 28 rows in `per_period_estimates`.

## Notes
- **From H37 (2026-10-04):** stance spins do find the #12 antiferromagnet that topic missed: opponents −0.13 vs teammates +0.32 (AUC 0.74 vs 0.48 for topic), teams recovered exactly in 7/10 debates, contrast gone within 10 min of the verdict. H21's null was a topic-channel result. H37's planned #34 confirmatory run (`confirm_g34.py`, not run) reuses H21's saboteur ground-truth rule with a new modality, which must be disclosed when run.
- 2026-10-03: promoted from HH103.
- 2026-10-03: round 1. Derived and verified labels for 10 debates. Built masked embeddings (2.8 MB). Synthetic validation found and fixed three estimator biases before the real run. Real run: primary failed; a-priori stance axis passed; post-hoc post-verdict reversal. #34 confirm script written, amended, dry run OK, not run. Data folder 3.0 MB.

## Round 2 redirects (2026-10-04)
*From the round-1 reflection (`writeup/round1-reflection/round1-reflection.pdf`).*
- **Where round 1 went sideways:** Antiferromagnetic order was sought in embeddings, but debates are topic fields.
- **What the direction is really after:** LLM agents don't form coalitions; assigned roles leave no lasting imprint.
- **H21-R1.** Role imprint lifetime: roles bias stance only while active, then reverse (HH127); measure across all role periods.
- **H21-R2.** Agreement is the default stance (sycophancy as ferromagnetic stance coupling); disagreement appears only when assigned.
