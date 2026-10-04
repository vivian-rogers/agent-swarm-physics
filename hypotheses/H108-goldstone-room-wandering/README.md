# H108: Goldstone wandering: the spontaneous room direction should drift, while a fielded one stays pinned

**Status:** exploratory round 1 done (2026-10-04, non-holdout only): **supported by the pre-registered rule, but fragile.** Inside a goal period the #best/#rest content direction is persistent from day to day (noise-corrected P(1) 0.69–0.95 in 6/8 periods). It decorrelates faster in identical-kickoff periods (pooled P(1) 0.70, D_θ 0.35 per day) than in the room-kickoff periods (0.93, 0.075 per day): R_D 4.7 [2.1, 5.9] (gte 5.2 [2.1, 6.4]). The contrast rests on #38 (17 days, a pinned plateau P(ℓ) ≈ 0.85 out to six days): with #44 as the only fielded period, R_D is 1.4 in bge and 3.0 in gte (post hoc). It is also confounded with split size, since Goldstone diffusion itself slows as 1/(N|m|²) and the fielded rooms split most; seven periods cannot separate the two (post hoc). The fork week (#35, a work field) is not pinned (P(1) 0.32). Card and predictions written 2026-10-04 21:28–21:30 UTC; Amendment 1 (21:44 UTC) after the synthetic, before real data. `analysis/confirm.py` frozen and dry-run, not run. Approved by Vivian in the dashboard vetting panel 2026-10-04 from HH338.
**Question (GOALS.md):** **Q2** (field vs coupling: is H100's spontaneous room direction pinned like a field, so that the "spontaneous" residual is an unmeasured field) with **Q3** (collective order: does the room order parameter show the soft mode a continuous broken symmetry predicts).
**Fields:** stat mech (Goldstone modes; rotational diffusion of a finite-N order parameter; pinning by a field), dynamics (angular diffusion, Ornstein–Uhlenbeck pinning)
**Literature:** `physics-models/11-vector-spins/README.md` ("Continuous symmetry, soft modes"; "Transverse, and Goldstone physics": χ_⊥ = |m|/h diverges as h → 0). Project cards: H100 (spontaneous share 0.58–0.91; no remanence across goals), H91 (content collective modes rotate about 1 SD a day more than a stationary swarm; no room-direction comparison), H92 (forecastable content share ≈ 0.30), H102 (domains with a sharp wall), H47, H48.
**Definitions used** (`physics-models/DEFINITIONS.md`): Agent; Regime; Driving / external field; Agent state, vector variant; H100/H102 named variants **room of a statement**, **room of an agent-day**, **day-centred agent vector**, **agent constant â_i (leave-period-out)**, **relabel excess Q**; H91's **eigenvector rotation** is a different object (agent co-movement modes, not the room difference). New named variants proposed here (defined under Observables; DEFINITIONS.md not edited): **room direction m̂(d)**, **direction persistence P(ℓ)**, **angular decorrelation rate D_θ**, **rotation ω**, **effective room size N_eff**.
**From:** HH338 in `hypotheses/hypohypotheses/HYPOHYPOTHESES.md` · **Models:** `physics-models/11-vector-spins/`
**Data inputs (shared tables first):** `embeddings/statements.parquet` + `statements_style_resid32_{bge_small,gte_modernbert}.npy` (primary), `statements_white32_*` (variant); `rooms_timeline` (null `t_end` → +inf); `chat_core`, `embeddings/chat_index`; `embeddings/goals.parquet` + `goal_vectors*` (`kickoff_room`); `period_units`; `roster`; `hypotheses/holdout.json` via `holdout_mask`. No text is read.

## Source HH (verbatim from the HH list, including refinements)
- **HH338 · Goldstone wandering: the spontaneous room direction should drift, while a fielded one stays pinned.** With no field, the direction of an ordered state costs no energy to rotate, so it diffuses (a Goldstone mode). With a field, it is pinned. H91 found that content modes rotate about 1 SD a day, but it did not compare fielded and unfielded rooms.
  - *Prediction:* the day-to-day angular diffusion of the room-difference direction Δ(d) is ≥ 2× larger in identical-kickoff periods than in #38 and #44 (room-specific kickoffs), after noise correction. Within identical periods, it scales as 1/(N_room |Δ|²).
  - *Check:* daily Δ(d), both models, style-residualized. Correct for noise with within-day split-half estimates. Compare with a relabel null.
  - *Kill:* identical-kickoff rotation ≤ fielded rotation. The "spontaneous" direction is then pinned like a field, and H100's residual is an unmeasured field.
  - *Impostors:* exogenous: the contrast is field vs no field. Priors: agent constants removed. Scheduler: n/a. Convergence: n/a (direction statistic).
  - *Models:* 11 · *Builds on:* H100, H91, H92

## Question
Inside a goal period, does the direction of the #best − #rest content difference wander from day to day when the rooms got identical instructions, and stay fixed when they got different instructions?

## Design: two layers (STANDARDS §4)
- **Eligible periods:** non-holdout #best/#rest periods with ≥ 3 one-room agents per room and ≥ 3 days: G35–G39, G41, G42, G44 (H100's set). Days within one regime only (#36: its four regime-III days).
- **Replication** (role `replication`): the rotation estimator on every eligible period. The HH contrast pools the identical-kickoff periods (**G36, G37, G39, G41, G42**) against the fielded ones (**G38, G44**). This is a comparison of period parameters on the phase diagram, not a pooled fit: D_θ is estimated within each period; pooled group values are ratio-of-sums summaries, reported next to the per-period values.
- **Natives** (role `native`), each with its own dated prediction:
  - **G38** (17 days, room-specific kickoffs): the lag profile P(ℓ) for ℓ = 1…6. A pinned direction has a plateau; a diffusing one decays.
  - **G35** (the RPG fork week, NE15; regime II): a work field (each room on its own fork). It should pin like a kickoff field. Run without agent constants (regime II has none), and compared with identical periods run the same way.
- **Exception (CLAUDE.md (b)):** agent constants â_i from other periods (H100's invariance check passed).

## Model
**From:** `physics-models/11-vector-spins/` (soft-spin O(n), n = 32; rotational dynamics of the order parameter).

Room order parameter m(d) = Δ(d) = b_best(d) − b_rest(d) (day-centred, agent constants removed). Write m = |m| m̂. Langevin dynamics for the direction on S^{n−1}:

  dm̂ = −Γ χ (h·m̂_⊥) dt + √(2D) dξ_⊥,   D ≈ σ²/(2 N_eff |m|²)

- **No field (h = 0, Goldstone):** m̂ diffuses freely. E[cos θ(ℓ)] = e^{−D_θ ℓ}, with D_θ = (n_eff − 1) D per day. A finite room of N_eff agents with per-agent noise σ² gives D ∝ 1/(N_eff |m|²): HH338's scaling.
- **Field (h ≠ 0):** an Ornstein–Uhlenbeck angle around ĥ. P(ℓ) relaxes to a plateau ⟨cos θ⟩² > 0 and the day-to-day rotation is small when χ|h| ≫ D.
- **Pinned by an unmeasured field:** identical-kickoff rooms behave like fielded ones (HH338's kill).
- **Regenerating:** no persistent direction at all (P(1) ≈ 0): every day breaks the symmetry anew, as H100 found across goals.

**Rivals.** R-pinned (an unmeasured field pins every room direction); R-regen (no day-to-day memory); R-noise (apparent rotation is sampling noise; removed by the noise correction).

## Data scheme (`scheme/`)
`scheme/build.py` → `data/processed/H108-goldstone-room-wandering/` (≤ 20 MB, `_provenance.json`). A copy of H107's scheme builder (STANDARDS §8 forbids importing another hypothesis's code; both copies are candidates for `infra/shared/`). Non-holdout rows only (`holdout_mask`). No vectors are copied: row indices into the shared statement arrays.
- **Statements** (`statements.parquet`): non-holdout agent statements of goals #33–#51 (Claude Code excluded) with `srow`, agent, t, PT day, goal, unit, regime, room at the statement (H100/H102 rule, null `t_end` → +inf), room of the day, and statement parity within the agent-day (odd/even: the HH's within-day split halves).
- **Fields** (`fields.parquet` + vectors): room kickoff and operator-message vectors (H100's rule).
- **Regimes covered:** II (#35) and III (#36b onward); #51 rows serve only the agent constants.

## Observables
*Written 2026-10-04 ~21:29 UTC, before any H108 statistic on real data.* Primary: bge style_resid; gte alongside. Agent-day vectors = means of unit statement vectors (≥ 2 statements), day-centred (minus the mean over all present agents), minus â_i (H100's leave-period-out constant, period P left out). Agents in two rooms within the period are dropped.
- **O1 Daily room difference** Δ(d) = mean of present #best agents − mean of present #rest agents (≥ 2 per room present).
- **O2 Noise-corrected direction persistence (primary: relabel-excess estimator).** C(d, d′) = Δ(d)·Δ(d′) − ⟨Δ_π(d)·Δ_π(d′)⟩_π with π over 2,000 **joint** relabels (the same partition on every day; infra Known issue). E(d) = C(d, d). **P(ℓ) = Σ_d C(d, d+ℓ) / √(Σ_d E(d) · Σ_d E(d+ℓ))** over the period's day pairs at lag ℓ (ratio of sums). P(ℓ) estimates E[cos(m̂(d), m̂(d+ℓ))] with agent-day noise and leftover constants removed. **Rotation ω = 1 − P(1).** **D_θ = −ln P(1)** per day (P(1) ≤ 0 → D_θ = ∞, "no memory"; P(1) ≥ 1 → D_θ = 0).
- **O2′ Split-half estimator (the HH's literal correction; variant).** Statement parity halves within each agent-day give Δ⁽¹⁾(d), Δ⁽²⁾(d) and E_sh(d) = Δ⁽¹⁾(d)·Δ⁽²⁾(d); P_sh(1) = Σ Δ(d)·Δ(d+1) / √(Σ E_sh(d) Σ E_sh(d+1)). It removes statement noise but keeps each agent's day deviation as "signal", so I expect it to overstate rotation. The synthetic decides whether it may be used.
- **O3 Group contrast (HH338's primary).** D_id = −ln P_id(1) and D_f = −ln P_f(1), with P_g(1) the ratio of sums pooled over the group's periods (identical: G36, G37, G39, G41, G42; fielded: G38, G44). **R_D = D_id / D_f.** CI: agent bootstrap within rooms within each period (500), recomputing the relabel null (200) per replicate.
- **O4 Scaling (within identical periods).** N_eff = (1/N_best + 1/N_rest)⁻¹ (mean present per day) and Ē = mean daily E(d). Spearman(D_θ, 1/(N_eff Ē)) over the five identical periods, and the log–log slope (Goldstone: +1).
- **O5 Is there a persistent direction at all?** Relabel p for Σ_d C(d, d+1) > 0 per period (R-regen predicts p ≥ 0.05).
- **O6 Lag profile (native G38).** P(ℓ) for ℓ = 1…6 and the slope of ln P(ℓ) on ℓ (pinned: ≈ 0; Goldstone: −D_θ).
- **Robustness:** both models; style_resid vs white32; â_i removed vs not (the no-constants variant is the one compared with G35).

## Null / baseline
- **N1 Joint relabel** (O2, O5): 2,000 random partitions of the period's agents with sizes kept, the same on every day.
- **N2 Agent bootstrap** (CIs of P(1), D_θ, R_D).
- **N3 Synthetic worlds (axis F; run first):** on the real agent × day × statement-count skeletons of G35–G44: pinned direction (ρ 0.3, 1); Goldstone diffusion (planted P(1) 0.3, 0.6, 0.9); field plus diffusion; regenerating (fresh direction each day); null. Calibrated to the real statement and agent-day noise.

## Impostors (STANDARDS §1)
| Impostor | Relevant? | How it is handled | Status |
| --- | --- | --- | --- |
| Scheduler field | no | Content direction, not timing; day centring removes common daily shifts. | n/a |
| Exogenous field (kickoff/goal/operator) | yes: the contrast is field vs no field | Day centring removes the global goal field. The room fields are the design variable (kickoff-different vs identical periods; the fork week). Unmeasured room fields would show up as pinning (the kill). | partly |
| Shared model priors (family, style) | yes | DQ5 style_resid; leave-period-out agent constants; the joint relabel puts leftover constants into the null; both models. A fixed composition difference is a pinned component: it biases toward pinning, not toward wandering. | removed (regime III); open in G35 |
| Contemporaneous convergence | no | A direction statistic; no influence claim. | n/a |

## Faithfulness scorecard
Scored per model, mapping and window; 0 = not done or failed, 1 = partial, 2 = passed. Scheme and promotion thresholds: `writeup/paper.tex`, Sec. "Assessing model faithfulness".
**Rival models:** R-pinned, R-regen, R-noise (above).
**Locked holdout used for confirmation:** none run. `analysis/confirm.py` (frozen 2026-10-04, guarded by `--confirm`, `H108_CONFIRM=1`, a SHA-256 freeze and the holdout ledger) targets the held-out two-room periods #45–#48. Dry-run on non-holdout stand-ins only.

| Axis | Test (plan) | Score | Evidence |
| --- | --- | --- | --- |
| A mapping | daily room difference from DQ5 vectors, rooms from statements; both models | 1 | Daily agent vectors from style_resid statements (both models), H100's room rule, leave-period-out constants. P(1) agrees across models within 0.11 in every period with a defined value; #39 is undefined in gte (ΣE ≤ 0). |
| B assumptions | stationarity of D_θ within a period; isotropy (n_eff absorbed in D_θ) | 1 | Ratio-of-sums pooling assumes one D_θ per period. #38's lag profile is not exponential: a drop at lag 1 then a plateau (0.95 → 0.85), as a field plus fast fluctuation predicts. Day 1 is a transient (H107: c₁ 0.51 in #38). |
| C adequacy | relabel null for persistence; noise correction checked on synthetic | 1 | Persistence beats the joint relabel in 6/8 periods (bge; 5/8 gte); the test is liberal under strong regenerating rooms (size up to 0.28, Amendment 1). The relabel-excess estimator is unbiased in every synthetic world; agent-bootstrap CIs sit low. |
| D unfitted predictions | the group ratio and the 1/(N m²) scaling are not fitted | 1 | The group ratio passes its rule (R_D 4.7, CI lower bound 2.1). The Goldstone scaling is flat to weak (Spearman 0.10 bge, 0.40 gte, 4–5 periods). |
| E interventional | the field contrast (kickoffs, forks) as a quasi-intervention | 1 | Kickoff fields: #38 pinned, #44 between the groups (P(1) 0.78; gte 0.89). The fork week (a work field) is the least persistent period (0.32): a work field set on day 1 does not pin content direction. |
| F identifiability | real-skeleton synthetic: bias of P(1) under pinning, recovery under diffusion, power of R_D | 2 | Amendment 1: pinned P(1) 0.97–1.08 at ρ 1; planted cosines recovered within ±0.05; contrast rule 100% / 0% / 0% in the three contrast worlds; the split-half variant is biased low and not scored. |
| G ground truth | fielded periods should pin | 1 | The longest fielded period pins (#38: P(6) 0.85); the shorter one only partly (#44); the forks do not. |
| H comparative | Goldstone vs R-pinned vs R-regen | 1 | R-pinned (all rooms pinned like a field) is rejected in the pooled contrast but not without #38 (bge R_D 1.4). R-regen fits #36 only (no persistent direction, p 0.35). Goldstone vs a split-size effect is not separable (field coefficient −0.17 ± 1.33 in a log-log fit with log x). |
| I transfer | holdout (#45–#48) | 0 | not run |

## Prediction
*Written 2026-10-04 ~21:29 UTC, before the synthetic validation and before any H108 statistic on real data.*

**What I had seen when writing this (so these are not blind):** H100's card and results (period-level Q, Q_spont, no remanence across goals), H102's D per period, H91's rotation result (z_boot ≈ 1 per day for collective modes), H47 and H48, and the per-period counts of days and agents per room. No H108 statistic had been computed.

- **P0, synthetic (axis F; run first).** On the real skeletons: (a) under a pinned direction at ρ = 1 the primary estimator gives median P(1) ≥ 0.85 in every period with ≥ 3 days [0.6]; (b) under planted diffusion it recovers the planted P(1) within ±0.2 (median) [0.5]; (c) R_D ≥ 2 with the bootstrap CI above 1 in ≥ 80% of worlds where identical periods diffuse (P(1) = 0.5) and fielded periods are pinned, and in ≤ 10% when all periods are pinned [0.5]; (d) under constant planted D the O4 Spearman has |ρ| < 0.9 in ≥ 90% of worlds (no mechanical scaling) [0.6]. The split-half variant O2′ is expected to be biased low under pinning [0.7]; if so it is reported but not scored.
- **P1, the group contrast (HH338).** R_D ≥ 2 with CI lower bound > 1, in both models [0.3]. The kill (D_id ≤ D_f, both models) [0.35]. My expectation: identical and fielded directions persist similarly within a period, because the room difference follows the work each room picks on day 1 and the work persists for the week.
- **P2, scaling.** Spearman(D_θ, 1/(N_eff Ē)) > 0 over the identical periods [0.4] (five points: descriptive weight only).
- **P3, persistence exists.** Relabel p < 0.05 for Σ C(d, d+1) > 0 in ≥ 5 of 8 periods [0.6].
- **P4, G38 lag profile.** Slope of ln P(ℓ) over ℓ = 1…6 ≥ −0.05 per day and P(6) ≥ 0.5 [0.35].
- **P5, G35 forks.** ω(G35) ≤ ω pooled over the identical periods, both without agent constants [0.5].

**Verdict rules.**
- *Hypothesis level:* **supported** if R_D ≥ 2 with the bootstrap 95% CI lower bound > 1 in bge, and gte's R_D > 1; **failed** (HH338's kill) if D_id ≤ D_f in both models; **mixed** otherwise. If P0(a) fails (the estimator cannot recover pinning), the verdict is "inconclusive" (mixed with the reason).
- *Identical period:* **supported** if D_θ(P) ≥ 2 D_f (pooled fielded); **failed** if D_θ(P) ≤ D_f; **mixed** in between; **descriptive** if Σ E(d) ≤ 0 or no day pair is valid.
- *Fielded period (G38, G44):* **supported** if D_θ(P) ≤ ½ D_id; **failed** if D_θ(P) ≥ D_id; **mixed** otherwise. G38 native: supported if P4 holds.
- *G35 native:* supported if P5 holds; failed if ω(G35) ≥ 2× the identical no-constants ω.
- *Multiplicity:* 8 periods × 2 models × 3 variants; only these rules count.

### Amendment 1 (after the synthetic validation, before any H108 statistic on real data)
*2026-10-04 21:44 UTC.* `analysis/synthetic.py`, 40 worlds per setting, 300 joint relabels, bootstrap 200 × 100 relabels for the contrast worlds, on the real statement skeletons of all eight eligible periods. Calibration (instrument, not an outcome): statement noise s_ε² = 0.0195, agent-day deviation s_η² = 0.0026 per coordinate; leftover agent constants at the full H100 variance τ² = 0.0014 (no constants removed; conservative). Median P(1) by period (range over the 8 periods):

| World | primary P(1) | split-half P_sh(1) | persistence test rejects | pooled identical / fielded P(1) |
| --- | --- | --- | --- | --- |
| null (no room effect) | −0.48 to 0.36 (undefined: E ≈ 0) | 0.30–0.40 | 0.03–0.10 | – |
| pinned ρ 0.3 | 0.91–1.28 (q10 0.62–0.79) | 0.52–0.63 | 0.60–1.00 | 1.03 / 0.91 |
| pinned ρ 1 | 0.97–1.08 (q10 0.85–0.94) | 0.74–0.80 | 1.00 | 1.01 / 0.97 |
| Goldstone c 0.3 / 0.5 / 0.6 / 0.9 | 0.26–0.35 / 0.49–0.51 / 0.59–0.64 / 0.88–0.99 | 0.28–0.33 / 0.43–0.46 / 0.50–0.54 / 0.68–0.73 | 0.57–1.00 | matches the planted c |
| regenerating (c 0) | −0.06 to 0.05 | 0.07–0.15 | 0.03–0.28 | −0.01 / 0.01 |

Contrast worlds (the verdict rule R_D ≥ 2 with bootstrap CI lower bound > 1): identical Goldstone c 0.5 vs fielded pinned passes in **100%** (median R_D 26); all pinned in **0%**; all Goldstone in **0%** (median R_D 0.99).
- **P0(a)** passes (pinned ρ 1: median P(1) ≥ 0.97 in every period). At ρ 0.3 single-period P(1) is noisy (q10 0.62). **P0(b)** passes (planted c recovered within ±0.05 in median). **P0(c)** passes (1.00 / 0.00 / 0.00). **P0(d)** passes (|Spearman| < 0.9 in 92–100% of constant-D worlds), but five points give mechanical medians from −0.40 to +0.30, so O4 carries descriptive weight only.
- **Split-half variant (O2′):** biased low under pinning (0.74–0.80 at ρ 1, 0.52–0.63 at ρ 0.3), as the card expected: it keeps each agent's day deviation as signal. It is reported, not scored.
- **Persistence test (O5) is liberal under regenerating directions** with a strong room effect (size up to 0.28 in #38 and #44: the room effect crosses with leftover constants in the observed sum but not in the null). P3 is read with that caveat; P(1) itself is unbiased there.
- No prediction or verdict rule changes.

## Results by goal period
Primary: bge style_resid, daily agent vectors minus the leave-period-out constants; gte in brackets. P(1) = noise-corrected day-to-day cosine of the room direction (agent-bootstrap 95% CI, which sits low); D_θ = −ln P(1) per day. Pooled references (bge): D_id 0.355, D_f 0.075.

| Period | Role | Verdict | Key numbers |
| --- | --- | --- | --- |
| [G35](goalperiod-subhypotheses/G35/README.md) | native (forks) | failed | P(1) 0.32 [0.24, 0.48] (0.37); ω 0.68 vs identical 0.27 (no constants) |
| [G36](goalperiod-subhypotheses/G36/README.md) | replication | supported | P(1) 0.19 [−0.09, 0.60] (0.21); no persistent direction (p 0.35): reads as regenerating, not Goldstone |
| [G37](goalperiod-subhypotheses/G37/README.md) | replication | supported | P(1) 0.83 [0.25, 0.92] (0.83); D_θ 0.19 |
| [G38](goalperiod-subhypotheses/G38/README.md) | replication + native (lag profile) | supported | P(1) 0.95 (0.94); P(ℓ) 0.95 → 0.85 at ℓ = 6; slope −0.019 per day |
| [G39](goalperiod-subhypotheses/G39/README.md) | replication | mixed | P(1) 0.89 [0.44, 0.86]; D_θ 0.11 (between D_f and 2D_f); gte undefined |
| [G41](goalperiod-subhypotheses/G41/README.md) | replication | supported | P(1) 0.69 [0.54, 0.78] (0.75); D_θ 0.37 |
| [G42](goalperiod-subhypotheses/G42/README.md) | replication | supported | P(1) 0.78 [0.17, 0.81] (0.81); persistence p 0.12 |
| [G44](goalperiod-subhypotheses/G44/README.md) | replication | mixed | P(1) 0.78 [0.67, 0.81] (0.89); D_θ 0.25, between ½D_id and D_id |

## Results
### Exploratory round 1 (2026-10-04; non-holdout only, asserted in the scheme)
- **Scheme:** 99,272 non-holdout statements (#33–#51) with rooms and split-half parity; 0.8 MB in `data/processed/H108-goldstone-room-wandering/`.
- **Code:** `scheme/build.py` (copy of H107's); `analysis/{rslib,h108lib,synthetic,run,summarize,figures,posthoc,confirm}.py`.
- **Numbers:** `results/raw_all.json` (6 instrument variants), `results/results.json`, `results/posthoc.json`, `synthetic/synthetic_summary.json`. Estimates: 46 rows in `per_period_estimates` (hypothesis H108).
- **Figures:** `figures/persistence_by_period.pdf`, `figures/synthetic_recovery.pdf`.

**Headline.**
1. **The room direction has day-to-day memory inside a period.** Noise-corrected P(1) is 0.69–0.95 in six of eight periods (both models), and the persistence beats the joint relabel in 6/8 (bge). Only #36 (no final split) and the fork week #35 lose the direction from day to day.
2. **The pre-registered contrast passes.** Pooled identical-kickoff P(1) 0.70 [0.56, 0.75] (D_θ 0.35 per day) vs room-kickoff 0.93 [0.82, 0.92] (D_θ 0.075): R_D 4.7 [2.1, 5.9]; gte 5.2 [2.1, 6.4]; rotation difference 0.23 [0.12, 0.34].
3. **It rests on #38.** #38 is pinned: P(ℓ) falls from 0.95 to a plateau of 0.85 over six days (slope −0.019 per day), an Ornstein–Uhlenbeck angle around a fixed axis. #44, the other fielded week, sits with the identical weeks (0.78; gte 0.89). Without #38, R_D is 1.4 (bge) and 3.0 (gte); without #36 as well, 1.2 and 2.5 (post hoc).
4. **Split size confounds the field.** Goldstone diffusion slows as 1/(N_eff|m|²), and the fielded rooms have the largest splits (mean daily E 0.45 and 0.26 vs 0.03–0.22). In a log-log fit over seven periods the field coefficient is −0.17 ± 1.33 (bge) and the size slope 0.49 ± 0.59: neither is identified (post hoc). The 1/(N|m|²) scaling within identical periods is weak (Spearman 0.10 bge, 0.40 gte).
5. **A work field does not pin.** The RPG fork week, where each room worked on its own fork all week, has the least persistent direction (P(1) 0.32 [0.24, 0.48]; gte 0.37): ω 0.68 against 0.27 for identical periods without constants. P5 failed.

**Synthetic validation (axis F):** Amendment 1 (pinned P(1) ≈ 1; planted cosines recovered; contrast rule 100% / 0% / 0%; split-half variant biased low).

**Outcome vs prediction**

| | Prediction (locked) | Outcome | Verdict |
| --- | --- | --- | --- |
| P0 | (a) pinned median P(1) ≥ 0.85; (b) recovery ± 0.2; (c) contrast power ≥ 80%, false ≤ 10%; (d) no mechanical scaling | 0.97–1.08; ± 0.05; 100% / 0% / 0%; abs(ρ) < 0.9 in 92–100% | passed |
| P1 | R_D ≥ 2, CI lower bound > 1, both models [0.3]; kill D_id ≤ D_f [0.35] | 4.7 [2.1, 5.9]; gte 5.2 [2.1, 6.4] | **supported** (fragile: without #38 R_D 1.4 bge) |
| P2 | Spearman(D_θ, 1/(N_eff Ē)) > 0 [0.4] | 0.10 (bge, n 5); 0.40 (gte, n 4) | met, descriptive only |
| P3 | persistence p < 0.05 in ≥ 5/8 [0.6] | 6/8 (gte 5/8) | met |
| P4 | G38 slope ≥ −0.05 per day and P(6) ≥ 0.5 [0.35] | −0.019; 0.85 (gte −0.022; 0.84) | met |
| P5 | G35 ω ≤ identical ω (no constants) [0.5] | 0.68 vs 0.27 (gte 0.63 vs 0.24) | **failed** |
| HH338 | identical rotation ≥ 2× fielded; kill if ≤ | R_D 4.7–5.2 | **supported by rule; fragile** |

**What this means.**
1. In vector-spin terms, the room order parameter has a soft direction: it keeps about 70–90% of its orientation from one day to the next. The one long fielded week shows the pinned signature (a plateau, not a decay), and the identical weeks do not stay that close.
2. Whether the difference is pinning by a field or slower Goldstone diffusion of a larger order parameter is open: the fielded weeks split most, and both readings predict slower drift there.
3. A work assignment (the forks) does not pin the content direction. What the rooms say rotates while what they build stays fixed.

**Operator-facing conclusion.**
- Inside a week, the content difference between rooms keeps most of its direction from day to day (P(1) ≈ 0.7–0.9). With identical instructions, expect a day-to-day cosine of about 0.7 (roughly 45° of drift per day).
- Different room instructions held one room difference fixed for three weeks (#38). Do not expect a work assignment alone to do that.

**Caveats.**
- **One long fielded period.** The contrast passes because #38 is long and pinned; #44 alone does not reach R_D 2 in bge.
- **Split size vs field.** Not separable with seven periods.
- **Short identical periods.** 2–4 day pairs each; per-period CIs are wide, and agent-bootstrap CIs sit below the point estimate in #38 and #39 (duplicated agents shift the relabel null).
- **Day 1 enters the pairs.** H107 shows that day 1 is a transient; it lowers P(1) most in short periods. A day-1-excluded variant was not pre-registered.
- **Post hoc items:** the leave-one-out contrasts, the split-size fit and the "work field does not pin" reading.

**Claim that stands:** Inside a #best/#rest goal period, the noise-corrected day-to-day persistence of the room content direction is 0.69–0.95 in 6/8 periods (both models), and it is higher in the room-kickoff periods than in the identical-kickoff ones (pooled P(1) 0.93 vs 0.70; R_D 4.7 [2.1, 5.9], gte 5.2). Excluded: the field-vs-Goldstone attribution (split size confounds it; the contrast drops to R_D 1.4 in bge without #38), the 1/(N|m|²) scaling (4–5 points), the fork-week reading (P5 failed), and the split-half variant (biased).

### Confirmatory design (written 2026-10-04 after exploration; not run)
`analysis/confirm.py`, frozen predictions in the script header (SHA-256 recorded in `analysis/confirm.sha256`):
- **C1 (persistence):** in held-out two-room periods among #45–#48 with ≥ 3 days and ≥ 3 agents per room, the noise-corrected P(1) ≥ 0.6 in ≥ 2/3 of scorable periods [0.65].
- **C2 (field contrast, if both kinds occur):** pooled P(1) of held-out room-kickoff periods (whitened kickoff cos < 0.95) exceeds that of held-out identical-kickoff periods [0.55]; void if either kind is absent.
- **C3 (no mechanical rotation):** pooled held-out P(1) ≥ 0.5 [0.7].
- **Safeguards:** `--confirm` plus `H108_CONFIRM=1`; refuses unless the SHA-256 of the script and of `rslib.py`, `h108lib.py` and `scheme/build.py` match and the files are committed; `holdout_ledger.check("H108", target, "content", ["content_alignment"])` per target. `--dry-run` on non-holdout stand-ins (#37, #41, #42, #44).
- **Reuse disclosure:** as H107 (#45–#48 content; H100 C2/C4 and H102 C1 use the same room-separation family).

## Round 2 redirects
**What the direction is really after:** whether a room's content order is pinned by its instructions or diffuses freely, at matched order-parameter size.
- **H108-R1. Match on split size.** Compare D_θ between fielded and identical periods at matched mean E (e.g. #41 vs #44), or fit D_θ ∝ (N_eff E)^−a with a field term on the 7 periods plus the holdout.
- **H108-R2. Exclude the kickoff-day transient.** P(1) from day 2 on (H107: day 1 is half re-oriented).
- **H108-R3. Transverse kicks.** Does a room-specific operator message on day d rotate Δ(d+1) toward its own direction more in identical periods (χ_⊥ = |m|/h large) than in fielded ones?
- **H108-R4. Why the forks do not pin.** Split #35's content into fork-related and other statements (strict repo mentions): is the fork-related part pinned while the rest rotates?

## Notes
- 2026-10-04 21:28–21:30 UTC: card, observables, nulls and predictions written by the H108 round-1 agent, before any H108 statistic on real data.
- 21:29 UTC: period folders with dated predictions; scheme built. 21:38–21:44 UTC: synthetic validation, Amendment 1, finished before H107's real-data run (H107's daily E(d) overlaps H108's inputs; I saw H107's day profiles, not any day-to-day cross-product, before running H108).
- 21:47 UTC: real-data run (`run.py`), `summarize.py`; one labelled post hoc script (`posthoc.py`: leave-one-out contrasts and the split-size fit).
- 21:56 UTC, guard test (disclosure): `confirm.py --confirm` was invoked once with `H108_CONFIRM=1` before the SHA-256 file existed; it stopped at the hash check, before the ledger call and before any data load. No held-out row was read. H107's guard was tested only with the variable unset (refused).
- Suggested shared changes (not made): DEFINITIONS entries for *room direction m̂(d), direction persistence P(ℓ), angular decorrelation rate D_θ, rotation ω, effective room size N_eff*; a model-11 pitfall ("within-day split-half noise correction keeps agent-day deviations as signal and biases direction persistence low; use a joint-relabel excess"); move `rslib.py` and the scheme to `infra/shared/`.
