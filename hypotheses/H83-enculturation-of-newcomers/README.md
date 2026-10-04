# H83: Enculturation of newcomers

**Status:** **exploratory round 1 done (2026-10-04, non-holdout only). Inconclusive: no detectable enculturation into a village culture; newcomers already sit near the veterans' alignment from tenure day 2.**
- **P1 (headline) inconclusive:** enculturation index ΔG = +0.020 [−0.025, +0.070] (bge; 11/19 joins positive) and −0.011 [−0.047, +0.026] (gte), below the calibrated null cut +0.032. Synthetic power at closure 0.5 is only 0.15–0.30, because the veterans' persistent shared content is about 3% of statement variance.
- **Small initial gap:** newcomers' window-E gap −0.020 [−0.056, +0.020]; by days 8–14 it is +0.001.
- **Family signature at entry, fading:** newcomers are closer to their own family's newcomer baseline at days 2–4 (K_E +0.038 [+0.014, +0.061], 13/15; gte +0.031), and the signature fades by days 8–14 (ΔK −0.018 [−0.033, −0.004]; gte CI touches 0). Kill 1 (converge only to family) fails.
- **Rooms:** in #38 newcomers align with their own room's veterans as strongly as veterans do from their first days (R 0.18 vs 0.16). No dose response; style does not approach the veterans.
- **NE32 did not happen as catalogued:** the GPT-5.6 triplet left its isolated rooms after about 1.5–2 h on 07-09 and posted nothing there.
- Card, nulls and predictions written 2026-10-04 20:08 UTC before any real-data statistic; synthetic validation and Amendment A1 before real data. `analysis/confirm.py` written, dry-run, **not run**.
**Question (GOALS.md):** **Q3** (is there collective order beyond fields?): it asks whether the village holds a culture that newcomers acquire, beyond the goal field and their model priors. It also serves Q2 (it separates the kickoff field, the family prior and reading-borne convergence for one event class).
**Fields:** stat mech (vector spins: relaxation of an agent constant in a mean field), sociophysics (cultural transmission, conformity), info theory (dose: items read)
**Literature:** [Ashery et al. 2025](../../literature/ashery-2025-emergent-social-conventions-llm-populations.md) (LLM populations converge on shared conventions; collective bias lives in the history-conditional response, so a flat first-day prior does not rule out a family effect later); [Centola & Baronchelli 2015](../../literature/centola-2015-spontaneous-emergence-of-conventions.md) (well-mixed populations reach one convention; isolated newcomers cannot form one). Project cards: H13 (family fields are style), H46 (style moves at goal switches and erasures, not at roster changes), H73 (style is mostly an agent constant), H41 (rooms cage spread), H15 (newcomers' empty memory costs little).
**Definitions used** (`physics-models/DEFINITIONS.md`): Agent; Population N(t); Regime; Driving / external field (goal and kickoff field); H46's **agent state (vector, chat agent-day, style-residualized)** (DQ5 `style_resid_period`) used here at statement level; H46's **agent state (style, chat agent-day)** (here the 20 standardized H13 features, not type-controlled); **Exposure (turn read-out)** (H08, through the DQ1 ledger). New named variants proposed for DEFINITIONS.md (defined under Observables; not edited here): **newcomer tenure τ**, **village vector V_d (veteran centroid)**, **family newcomer baseline F_f**, **village alignment gap G**, **enculturation index ΔG**.
**From:** HH292 in `hypotheses/hypohypotheses/HYPOHYPOTHESES.md` · **Models:** `physics-models/11-vector-spins/` (primary: agent constants in a mean field), `physics-models/13-cultural-evolution-conventions/` (secondary: transmission through reads)
**Data inputs (shared tables first):** `roster`, `calendar`, `period_units`, `rooms_timeline`; DQ5 `statements_style_resid_period32_{bge_small,gte_modernbert}.npy`, `statements_white32_*` (variant), `statement_flags` (`self_repeat_both`); `embeddings/goals.parquet` + `goal_vectors*` (kickoff and goal fields, whitened per regime); `text_features` (20 style features); DQ1 `context_ledger_items` + `call_windows` (veteran items read). Not used: `activity_bins` (join bug), `exposure` (superseded by the ledger).

## Source HH (verbatim from the HH list, including literature refinements)
Enculturation: newcomers drift toward a village-specific culture vector. H46 says style is a fixed charge plus a context excitation. Enculturation asks whether the charge itself moves. Prediction: a newcomer's style-residualized content and its style start near its family's newcomer baseline (the mean first-day vector of same-family newcomers across all joins) and converge toward the contemporaneous village culture vector, not toward its family. The rate scales with read exposure to veterans (context ledger), and the converged position is village-specific. *Check:* the distance-to-village minus distance-to-family-baseline trajectory over a newcomer's first 2 weeks, against a kickoff-only model; dose = veteran items read. *Kill:* newcomers converge only to their family, or only as far as the kickoff pulls everyone.
  *Models:* 11 · *Revamps:* H13, H46 · *Periods:* NE32 (#51 newcomers), every roster join

## Question
In its first two weeks, does a newcomer's style-free content (and its style) move toward the veterans' contemporaneous centroid by more than the veterans themselves move on the same days, after the goal and kickoff field is projected out, and does the move scale with what it reads from veterans?

## Design: two layers (STANDARDS §4)
- **Replication:** the common estimator (ΔG, below) on every eligible join. A join's unit is the period unit of its join day (exception (c): the join is the object, and the tenure windows may cross a goal boundary; the same-day veteran difference removes the boundary). Period README role: `replication`.
- **Period-native tests:** NE32 (G51: the isolated GPT-5.6 triplet, a dose-0 day then a merge), G38 (two rooms: own-room vs other-room veterans, read vs unread), NE27 (G10: three newcomers join four veterans; who moves). Each has its own dated prediction. Role: `native`.

## Model
**From:** `physics-models/11-vector-spins/` (an agent's state is a unit vector; agent constants plus day fields).

**H83 variant: a newcomer's constant relaxes in the village mean field.** A chat statement s of agent i on day d, in goal period P and room r, has a 32-d style-residualized, regime-whitened unit vector u_s. After the goal and kickoff field is projected out (operator Π_P, below):

  ũ_s ∝ Π_P [ q_i(τ) + h_d + ε_s ],   q_i(τ) = q_i⁰ + λ (1 − e^{−D_i(τ)/D*}) (V̄ − q_i⁰)

- q_i⁰ is the newcomer's entry constant: its family newcomer baseline F_f plus an agent part. h_d is the day field (the day's topic, common to all present agents). ε_s is statement noise.
- V̄ is the veterans' centroid (the village culture vector). D_i(τ) is the cumulative number of veteran chat items i has read by tenure day τ (DQ1 ledger). D* is a dose scale. λ ∈ [0, 1] is the closure fraction at saturation.
- **Enculturation:** λ > 0, with the move set by D, not by calendar time. **Kickoff-only model (the null, λ = 0):** the newcomer keeps q_i⁰ and responds to the goal and kickoff field like everyone else. Then any change in its alignment with the village equals the veterans' change on the same days.
- Π_P removes the span of the period's whitened goal-text vector, its all-room kickoff vector and the room kickoff vector (shared `goal_fields`), then renormalizes. This is "subtract the kickoff pull".

**Rivals.**
- **R1, kickoff/field only (λ = 0):** newcomers converge only as far as the field pulls everyone (HH kill 2).
- **R2, family attractor:** newcomers drift toward their family's position, not the village (HH kill 1).
- **R3, generic experience attractor:** newcomers drop an onboarding register and move toward a generic "settled agent" position that any village centroid would show. Separated by a mismatched-village target (veteran centroids from other dates).
- **R4, contemporaneous convergence:** newcomers share topics with veterans without reading them (co-generation under shared fields). Separated by the dose test, the NE32 isolated day and the G38 own-room vs other-room contrast.
- **R5, the village moves to the newcomer:** veterans accommodate the newcomer, so the alignment rises without the newcomer moving. Separated in NE27 (veterans' alignment with the newcomers vs newcomers' with the veterans).

## Data scheme (`scheme/`)
Script: `scheme/build.py` (shared tables only; no text read or written; holdout rows dropped with `calendar.holdout` and `common.holdout_mask` and asserted).
- **Inputs:** `embeddings/statements.parquet` (chat rows), `statements_style_resid_period32_{bge_small,gte_modernbert}.npy`, `statements_white32_{bge_small,gte_modernbert}.npy`, `statement_flags.self_repeat_both`, `chat_index` + `text_features` (20 `f_*`), `goals.parquet` + `goal_vectors{,_gte_modernbert}.npy` (kinds `goal`, `kickoff`, `kickoff_room`), whiteners per regime and model, `roster`, `calendar`, `rooms_timeline`, `context_ledger_items` × `call_windows` (newcomer receiving calls).
- **Transform:**
  1. Eligible statements: agent chat, non-holdout, not `self_repeat_both`; agents 19 (Claude Code), 28 and 30 (fine-tuned leaders) dropped.
  2. Kickoff projection Π_P per (goal, room): whiten each goal/kickoff vector with the statement's regime whitener (32-d, same model), orthonormalize, project out, renormalize. Stored per model (fp16): `vec_{bge,gte}.npy`, plus the unprojected style-residualized and white32 vectors as variants.
  3. Style: the 20 H13 features, winsorized at the non-holdout 0.1/99.9% quantiles and z-scored on non-holdout agent chat (a shared ruler, exception (a)): `style.npy`.
  4. Tenure: τ(d) = rank of day d among `calendar` days on or after the join date (held-out days count in τ but carry no data). Veteran on day d: τ > 20 or a founding agent.
  5. Dose: per newcomer and day, the veteran agent items its receiving calls read (`context_ledger_items` kind `agent`, sender a veteran that day), and all agent items read.
  6. Room per agent-day: modal room of its chat statements that day.
- **Output:** `data/processed/H83-enculturation-of-newcomers/` (`statements.parquet`: keys, agent, day, goal, regime, room, tenure, role flags; `vec_*.npy`, `style.npy`; `doses.parquet`; `newcomers.parquet`; analysis outputs in `synthetic/`, `replication/`, `natives/`, `confirm/`; `_provenance.json`).
- **Regimes covered:** I, II, III (non-holdout days). Family baselines are built within a regime (the whitening differs between regimes).

## Eligible joins
Newcomer = roster agent with `joined` after 2025-04-02, not 19/28/30. Eligible for the replication: the join day is non-holdout, and both windows E (τ 2–4) and L (τ 8–14) contain ≥ 2 observed agent-days and ≥ 5 eligible statements of the newcomer. At least 3 placebo veterans must also be observed in both windows. Sampling facts already seen (2026-10-04, about 20:05 UTC): join dates; per-newcomer counts of observed chat days and statements in their first 28 days (about 16–20 joins qualify; regime-III newcomers post 2–20 statements a day; joins on held-out days and the #51 tail are excluded). No alignment statistic has been computed.

## Observables
*Written 2026-10-04 20:08 UTC, before any real-data alignment statistic.*

**Village vector.** V_d = the agent-weighted mean of present veterans' mean projected vectors on day d (each veteran's statements averaged first). For a veteran j its own vector is left out (V_{d,−j}). Room variant V_{d,r}: veterans whose modal room that day is r.

**Alignment.** a_{i,d} = mean over i's eligible statements on day d of cos(ũ_s, V̂_{d,−i}). A statement-level mean is unbiased in the number of statements, so chatty and quiet days are comparable.

**Village alignment gap.** G_{i,d} = a_{i,d} − mean over veterans j present that day of a_{j,d}. Window means Ḡ_E (τ 2–4) and Ḡ_L (τ 8–14) average agent-day values. Day 1 (onboarding) is reported separately as G_1.

**O1. Enculturation index (primary).** ΔG_i = (ā_{i,L} − ā_{i,E}) − mean_j (ā_{j,L} − ā_{j,E}), over placebo veterans j observed in both windows on the same calendar days. This is a difference in differences: anything common to the newcomer and the veterans on those days (topic, goal switch, regime step, kickoff) cancels. Closure fraction c_i = ΔG_i / (−Ḡ_E) when Ḡ_E < 0.

**O2. Family signature.** F_f = agent-weighted mean of the τ = 1 projected vectors of the other newcomers of family f (`roster.lab`) in the same regime; F_¬f = the same over newcomers of other families (≥ 2 newcomers). K_{i,d} = mean_s cos(ũ_s, F̂_f) − mean_s cos(ũ_s, F̂_¬f). The onboarding topic is common to both baselines and cancels. ΔK_i = (K̄_L − K̄_E) − mean_j over the same veterans of their change against the same two baselines.

**O3. Dose.** D_i = log(1 + veteran agent items read on τ 1–7). Cross-newcomer Spearman ρ(ΔG_i, D_i), with a permutation p. Day-level variant: G_{i,d} on log(1 + cumulative veteran reads before day d) and log τ, with newcomer fixed effects.

**O4. Specificity (R3).** The same DiD with a mismatched village vector: for each day, V of a same-regime non-holdout day ≥ 40 village days away (both directions, the nearest qualifying day; held fixed across the newcomer's windows' days by day offset). Δspec_i = ΔG_i − ΔG_i^mismatch.

**O5. Style channel.** The same DiD on the per-message squared distance of the 20-d standardized style vector to the veterans' day style centroid (lower = closer): ΔS_i (enculturation means ΔS_i < 0). Family style signature K^style_i analogous to O2 (squared distances, sign flipped).

**Variants (robustness, not separate tests):** gte instead of bge; no kickoff projection; `white32` (not style-residualized); E = τ 1–4 (onboarding day included); L = τ 8–20.

**O6. Natives.**
- **NE32 (G51; 07-09 isolated, merged 07-10):** the triplet's pooled gap G on the isolated day (veteran reads = 0, checked in the ledger) against their pooled gap on 07-10…07-16, as a DiD with the veterans' change between the same days: ΔG_NE32. Descriptive: the triplet's mutual alignment on the isolated day vs post-merge.
- **G38 (two rooms):** for the G38 newcomers (Opus 4.7, 04-17; Kimi K2.6, 04-22), per day with two rooms: R_{i,d} = a_{i,d}(own-room veterans) − a_{i,d}(other-room veterans). Prediction on the window means and their change, DiD with the veterans' own-vs-other R on the same days. The other two-room joins (#35, #39, #42, #44) are pooled as a descriptive check.
- **NE27 (G10; 3 newcomers, 4 veterans, 08-18):** newcomers' ΔG (toward the veterans) vs veterans' ΔG^rev (toward the newcomers' centroid, DiD against the newcomers' self-alignment on the same days). Who moves.

**Multiplicity.** Card-level verdicts use the pooled replication over joins (P1–P5) and the three natives. Per-join rows are templated replications, not independent tests.

## Null / baseline
*Written 2026-10-04 20:08 UTC.*
- **Kickoff-only model (λ = 0):** ΔG = 0, ΔK = 0, ρ = 0. Its size is measured on synthetic data at real counts (real statements, agents, days and windows; planted agent constants, day fields, kickoff pulls, onboarding transient; no drift).
- **Placebo veterans** carry the same-day field in O1, O2 and O5.
- **Card-level tests:** the newcomer-bootstrap CI of the mean ΔG (resampling joins), and a sign test over joins.
- **Dose null:** permutation of D over joins (10,000 draws).
- **Specificity null:** mismatched-village DiD (R3).

## Impostor table (STANDARDS.md §1)
| Impostor | How it could fake enculturation | How H83 removes it | Status |
| --- | --- | --- | --- |
| Scheduler field | Newcomers' first days are partial or have fewer calls, which changes how many statements they make | Statement-level means are unbiased in volume; the observable is content, not timing | n/a |
| Exogenous field (kickoff, goal, operator) | A new goal or kickoff pulls everyone toward the new topic during the newcomer's windows; the operator's onboarding message is a newcomer-only field on day 1 | Π_P projects out the goal and kickoff span; the DiD subtracts veterans' change on the same days; day 1 is excluded from the windows | removed (the #51 private roles stay an agent-specific field) |
| Shared model priors (family, style) | A family attractor (R2), or a family-wide drift, looks like movement | `style_resid_period` vectors; the within-agent DiD cancels the agent constant; family baselines are leave-one-newcomer-out, within regime; K tests the family part | removed |
| Contemporaneous convergence | Newcomers co-generate the veterans' topics without reading them | Dose test (O3), NE32 isolated day (dose 0), G38 own-room vs other-room veterans; the DiD removes a constant co-generation level | partly (a co-generation that grows with tenure is not excluded) |

## Prediction
*Written 2026-10-04 20:08 UTC, before running the analysis on real data. Verdict rules fixed now.*

**Replication (card level).**
- **P1 enculturation (headline):** newcomers start below the veterans (mean Ḡ_E < 0, bootstrap CI < 0) and close part of the gap: mean ΔG > 0 with the join-bootstrap 95% CI above 0, ΔG > 0 in ≥ 2/3 of eligible joins, same sign with gte. *Against (kill 2):* mean ΔG ≤ 0 or CI including 0: newcomers converge only as far as the field pulls everyone. My prior: 35% (H46: roster changes move nothing; H73: the agent constant dominates).
- **P2 family:** where a family baseline exists, newcomers start closer to their family's newcomer baseline than to other families' (mean K̄_E > 0, CI > 0) and the family signature fades (mean ΔK < 0). *Against (kill 1):* ΔK ≥ 0 together with ΔG ≤ 0 (they converge only to their family). If K̄_E ≤ 0 the family clause is uninformative (H13 expects no family field in style-free content).
- **P3 dose:** ρ(ΔG, D) > 0 with permutation p < 0.05; the day-level dose coefficient > 0. *Against:* ρ ≤ 0. If synthetic power is < 0.8 at the planted effect, a null is "inconclusive".
- **P4 specificity (R3):** mean Δspec > 0 with CI above 0. *Against:* Δspec ≤ 0 (a generic experience attractor).
- **P5 style:** mean ΔS < 0 with CI below 0. *Against:* CI including 0 (the style charge does not move: H46/H73). Prior 25%.

**Natives (dated predictions also in each folder).**
- **N1 NE32:** ΔG_NE32 > 0 (the merge lets the triplet move toward the veterans), and the isolated-day gap is ≤ the mean newcomer Ḡ_E. *Against:* ΔG_NE32 ≤ 0.
- **N2 G38:** own-room alignment exceeds other-room alignment (mean R > 0) and the own-room preference grows with tenure faster than the veterans' (ΔR_DiD > 0). *Against:* R ≤ 0 (the newcomer converges to the whole village alike: a field, not reading).
- **N3 NE27:** enculturation is one-way: newcomers' ΔG exceeds the veterans' ΔG^rev. *Against:* ΔG^rev ≥ ΔG (the village meets the newcomers halfway or moves to them: composition, not a culture).

**Overall reading (fixed now).** **Supported** if P1 and P4 pass and at least one of P3 or N1 passes. **Mixed** if P1 passes but P4 fails, or P1 passes with neither P3 nor N1. **Refuted** if P1 fails and synthetic power for P1 is ≥ 0.8 at a closure fraction of 0.5 over two weeks (the effect that would matter). **Inconclusive** if P1 fails with lower power.

## Amendment A0 (2026-10-04 20:12 UTC, before any real-data statistic; not post hoc)
O4/P4 as first written cannot separate R3 from enculturation: in one village, a mismatched-epoch village vector shares the veterans' constants with the contemporaneous one and differs only in the day field. So the mismatched-village DiD is re-read as a **persistence test**, and R3 is named as not separable.
- **O4 (revised):** ΔG^mm = the O1 DiD with V_{d'} (a same-regime, non-holdout day ≥ 40 village days from d, nearest qualifying, either direction) in place of V_d. ΔG measures convergence to the village on that day (its conversation plus its persistent part); ΔG^mm measures convergence to the part that persists across epochs.
- **P4 (revised):** mean ΔG^mm > 0 with the join-bootstrap CI above 0. *Reading:* ΔG > 0 with ΔG^mm ≤ 0 means convergence to the day's conversation only (coupling, not culture). ΔG^mm > 0 means a persistent village component (culture, or R3's generic attractor; the two are not separable in one village). The overall rule is unchanged: supported needs P1 and P4.

## Synthetic validation (axis F; run 2026-10-04 20:14–20:29 UTC, before any real-data alignment statistic)
`analysis/synthetic.py` → `data/processed/H83-enculturation-of-newcomers/synthetic/synthetic.json` (40 replicates per scenario) and `synthetic_size.json` (200 replicates of the nulls). Village sampling: the real eligible statement schedule (114,504 statements; agent, day, room, tenure, veteran flag), the real joins and windows (19 eligible joins in 15 join units; 15 with a family baseline) and the real veteran read doses. Vectors: x = normalize(q_i + f_lab + χ·(C_P + C_v) + h_d + h_{d,room} + η_{i,d} + onboarding·e^{−(τ−1)} + ε) in 32-d. Variance components calibrated on **veterans only** (pairwise statement cosines): same agent-day 0.214, different agents same day 0.085, same agent other days 0.030, different agents and days within a goal period 0.029, different goal periods 0.005. So a veteran's persistent shared component (C_P + C_v) holds about 3% of the statement variance, and the agent constant almost none.

| Check | Result |
| --- | --- |
| P1 size (S0: newcomers share C fully; S0b: newcomers keep half of C forever), rule "cluster-bootstrap CI > 0" | 0.06 / 0.085 (200 reps): anti-conservative about ×3 against a one-sided 0.025 |
| Null mean ΔG, 95th percentile (S0 / S0b) | +0.027 / +0.032 (mean +0.002 / +0.005, SD 0.015–0.017) |
| P1 power, dose-driven closure 1.0 / 0.5 (S1) | 0.45 / 0.30 at the CI rule; mean ΔG +0.025 / +0.016 |
| P1 power, calendar-driven closure 1.0 / 0.5 (S2) | 0.40 / 0.15 |
| Initial gap Ḡ_E, S0 / S0b / S1 | −0.008 / −0.047 / −0.035 to −0.042 |
| P4 (mismatched village) size / power at full closure | 0.055 / 0.18: the cross-period shared part is too small to test |
| K (family) size, first version (unit-normalized baselines) | 0.15–0.55: **biased** by the onboarding component shared by first-day baselines of unequal size |
| K size, unnormalized baselines | 0.035–0.085 |
| P3 dose ρ power (S1) | ≤ 0.12 |
| NE27 reverse statistic, first version (veterans toward the newcomers' centroid, DiD vs newcomers' self-alignment) | null mean −0.07, 93% "asymmetric": **biased** (the newcomers share and lose the onboarding component) |
| NE32 d1 / d2 (null) | mean +0.004 / +0.006, SD 0.095 / 0.100 |
| NE27 batch gap Ḡ_E (null S0 / S0b) | −0.003 / −0.035, SD 0.036 |
| Rooms ΔR DiD, first version | undefined for G38 joins: from 04-28 the own room (#rest) holds one veteran |

## Amendment A1 (2026-10-04 20:33 UTC, after the synthetic validation, before any real-data statistic)
- **A1.1 (P1 calibration).** The CI rule over-rejects (size 0.06–0.085). P1 now also needs the mean ΔG above the larger synthetic null 95th percentile, **+0.032** (a calibrated one-sided p < 0.05). The pre-registered refutation rule needs power ≥ 0.8 at closure 0.5; the synthetic power is 0.15–0.30. **So a P1 failure reads "inconclusive", not "refuted".**
- **A1.2 (P3, P4 descriptive).** Power ≤ 0.2 for both. They are reported with their nulls but cannot decide the overall verdict. The overall rule becomes: **supported** if P1 passes and N1 or N2 passes; **mixed** if P1 passes alone; **inconclusive** if P1 fails.
- **A1.3 (K).** The family signature uses unnormalized baselines: K = M · (F_f − F_¬f).
- **A1.4 (N3 NE27, replaced).** The reverse statistic is not identifiable (any target built from the newcomers carries their onboarding component and the entry period's field). New N3: on the only join that coincides with a goal start (all seven agents get the #10 kickoff the same day), the batch's window-E gap Ḡ_E < 0 (veterans carry a component beyond the kickoff that newcomers lack) with a day-bootstrap CI < 0, and the batch's mean ΔG > 0. *Against:* Ḡ_E ≥ 0.
- **A1.5 (N1 NE32, re-specified).** The isolated day is also τ = 1, when every newcomer carries the onboarding component, so the triplet's τ1 → post change is confounded. New N1 compares the triplet with the other newcomers at the same tenure: d1 = G1(triplet, isolated, no veteran reads) − mean G1(other newcomers), d2 = [Ḡ(τ 2–6) − G1](triplet) − mean of the same change for the other newcomers. Prediction: d1 < 0 and d2 > 0 (reading on the day raises alignment; the triplet catches up after the merge). Bootstrap over the other newcomers. Power is low (null SD 0.10).
- **A1.6 (N2 G38, re-specified).** Two rooms with ≥ 2 veterans each exist only on 04-20 → 04-24. N2 uses those days: R_new = mean over the two newcomers' agent-days of [alignment with own-room veterans − alignment with the other room's veterans]; reference R_vet = the veterans' R on the same days. Prediction: R_new > 0 with a day-and-agent bootstrap CI > 0 (convergence follows the read population). *Against:* R_new ≤ 0. Descriptive: R_new / R_vet. The pooled two-room joins (#35, #39) are reported where both rooms hold ≥ 2 veterans.

## Results by goal period
Roles: `replication` = templated per-join point (not an independent test); `native` = period-specific design. Join units: the period of the join day (windows may run into the next period).

| Period | Role | Verdict | Key numbers |
| --- | --- | --- | --- |
| [G04](goalperiod-subhypotheses/G04/README.md) | replication | failed | Opus 4: Ḡ_E +0.061, ΔG −0.019 (gte +0.051) |
| [G10](goalperiod-subhypotheses/G10/README.md) | native | mixed | NE27 batch gap −0.017 [−0.103, +0.066] (gte +0.013); batch ΔG −0.037 |
| [G18](goalperiod-subhypotheses/G18/README.md) | replication | failed | Haiku 4.5: ΔG −0.005 (gte +0.002) |
| [G19](goalperiod-subhypotheses/G19/README.md) | replication | supported | GPT-5.1: Ḡ_E −0.049, ΔG +0.054 (gte −0.011) |
| [G20](goalperiod-subhypotheses/G20/README.md) | replication | mixed | Gemini 3 Pro ΔG −0.121; Opus 4.5 +0.072 |
| [G31](goalperiod-subhypotheses/G31/README.md) | replication | failed | Sonnet 4.6: ΔG −0.035 (gte −0.077) |
| [G35](goalperiod-subhypotheses/G35/README.md) | replication | supported | GPT-5.4: Ḡ_E −0.097, ΔG +0.073 (gte +0.117) |
| [G38](goalperiod-subhypotheses/G38/README.md) | native | supported | own-room minus other-room alignment 0.178 [0.099, 0.262] (gte 0.181); veterans 0.161 |
| [G39](goalperiod-subhypotheses/G39/README.md) | replication | supported | GPT-5.5: Ḡ_E −0.023, ΔG +0.023 (gte −0.067) |
| [G51](goalperiod-subhypotheses/G51/README.md) | native | n/a | NE32 premise false (isolation ≈ 1.5–2 h, no statements); #51 joins ΔG −0.09 to +0.25 |

## Outcome vs prediction
*Run 2026-10-04 20:34–20:40 UTC (`analysis/replication.py`, `analysis/natives.py`). Non-holdout only; copies (`self_repeat_both`) removed; 19 eligible joins in 15 join units.*

| Prediction | Observed | Verdict |
| --- | --- | --- |
| P1 newcomers start below (Ḡ_E < 0) and close the gap: mean ΔG > +0.032 (A1.1), CI > 0, ≥ 2/3 positive, gte same sign | Ḡ_E −0.020 [−0.056, +0.020]; ΔG +0.020 [−0.025, +0.070], 11/19 (bge); −0.011 [−0.047, +0.026], 8/19 (gte). Variants (no projection, white32, E = 1–4, L = 8–20): +0.013 to +0.020, all CIs span 0 | **fail → inconclusive** (power 0.15–0.30 at closure 0.5) |
| P2 family signature at entry (K_E > 0) that fades (ΔK < 0) | K_E +0.038 [+0.014, +0.061], 13/15 (gte +0.031 [+0.007, +0.051]); ΔK −0.018 [−0.033, −0.004], 4/15 positive (gte −0.012 [−0.025, +0.004]). PH1 without same-day joins: K_E +0.042, ΔK −0.018 | **pass (bge)**; fade not robust in gte |
| P3 dose: ρ(ΔG, veteran items read, days 1–7) > 0 | ρ +0.06 (p 0.41; gte −0.10); day-level dose slope +0.010 [−0.045, +0.058] | fail (descriptive: power ≤ 0.12) |
| P4 persistent part: ΔG^mm > 0 (A0) | +0.040 [−0.030, +0.110], 10/17 (gte −0.011) | fail (descriptive: power 0.18) |
| P5 style approaches the veterans: ΔS < 0 | ΔS +0.95 [−2.26, +4.52] (squared-distance units; positive = away); family style signature K_style_E +2.27 [−0.35, +4.58] | fail |
| N1 NE32: d1 < 0, d2 > 0 | premise false: the triplet read 733 veteran items on 07-09 and posted no statement while isolated | **n/a** |
| N2 G38: R_new > 0 | 0.178 [0.099, 0.262] (gte 0.181 [0.126, 0.242]); veterans 0.161 / 0.148 | **supported** |
| N3 NE27: batch Ḡ_E < 0 (CI < 0) and ΔG > 0 | −0.017 [−0.103, +0.066] (gte +0.013); batch ΔG −0.037 | mixed (inconclusive) |

**Overall (A1.2 rule):** P1 fails, so H83 is **inconclusive**. The data show no enculturation into a village culture that the test could detect, but the test could detect only near-full closure of a small gap.

## Results
**1. There is little to acquire.** In style-free content, a veteran's persistent shared component (the part shared with other veterans on other days) holds about 3% of the statement variance (calibration: cos 0.029 within a period, 0.005 across periods). Newcomers start within ±0.05 of the veterans' alignment with their own centroid from tenure day 2 (Ḡ_E −0.020 [−0.056, +0.020]). By days 8–14 the gap is +0.001 (bge). So newcomers join the conversation at once: their content tracks what the village talks about that day, not a slow culture.

**2. The headline test cannot decide.** ΔG is +0.020 (bge) and −0.011 (gte); the models disagree in sign, and both CIs span 0. Synthetic villages with the real schedule give power 0.15–0.30 at closure 0.5 and 0.40–0.45 at full closure. H89's independent NE32 Price partition shows the same model dependence (bge +0.26, gte −0.03; coordinator note).

**3. A family signature at entry, then fading.** Measured against other newcomers' first-day vectors of the same regime, a newcomer at days 2–4 sits closer to its own family's baseline than to other families' (13/15 joins; both models). By days 8–14 the signature shrinks (ΔK −0.018, bge; −0.012, gte, CI touching 0). This is the one trace of the HH's "start near the family baseline". It does not convert into a measurable move toward the village (P1). H13's finding (no family field in style-free content among incumbents) is consistent with a signature that newcomers lose within two weeks.

**4. Rooms route convergence immediately.** In #38's two rooms, newcomers align with the veterans of the room they read 0.18 more than with the other room's veterans, the same as veterans do (0.16). No growth window exists in the data (from 04-28 the newcomers' room holds one veteran).

**5. No dose response, no style move.** Veteran items read in days 1–7 do not predict ΔG (ρ +0.06). Style distance to the veterans' day centroid does not fall (ΔS +0.95). Style stays an agent constant, as H46 and H73 found.

**6. NE32 is mis-catalogued.** `rooms_timeline` and the DQ1 ledger show the three GPT-5.6 agents moving from their sol/terra/luna rooms to #general at 21:38–22:02 UTC on 07-09, about 1.5–2 h after joining. They posted nothing in the isolated rooms. The rooms were deleted on 07-10.

Figures: `figures/summary_obs.pdf` (ΔG per join, both models, with the null band; family signature trajectories), `figures/summary_obsb.pdf` (synthetic power; #38 room alignment). Data: `data/processed/H83-enculturation-of-newcomers/` (`replication/replication.json`, `natives/natives.json`, `synthetic/synthetic.json`, `synthetic/synthetic_size.json`, `confirm/confirm_dryrun.json`). Estimates: 108 rows in `per_period_estimates` (hypothesis H83).

## Faithfulness scorecard
*Round 1, 2026-10-04.* Scored per model, mapping and window; 0 = not done or failed, 1 = partial, 2 = passed.
**Rival models:** R1 field only (λ = 0), R2 family attractor, R3 generic experience attractor, R4 contemporaneous convergence, R5 the village moves to the newcomer.
**Locked holdout used for confirmation:** none yet (`analysis/confirm.py`, dry-run only).

| Axis | Test | Score | Evidence |
| --- | --- | --- | --- |
| A mapping | variables defined from dataset fields; assumptions listed; invariant across families and regimes | 1 | Tenure, veterans, village vector, family baselines and doses come from shared tables. Whitening is per regime, so family baselines exist only within a regime; ΔG changes sign between embedding models. |
| B assumptions | stationarity, Markov order, time-rescaling, update-order audit | 1 | Day 1 (onboarding) is excluded; statement-level means are unbiased in volume; matched-size centroids fix a leave-one-out level bias. The relaxation model (dose-driven closure) is not testable at this power. |
| C adequacy | beats the null hierarchy, day-blocked held-out data | 0 | ΔG does not beat the calibrated kickoff-only null (+0.032) in either model. |
| D unfitted predictions | unfitted statistics and the model's signature | 1 | The family signature at entry is predicted from other newcomers' first-day vectors (unfitted): 13/15 (bge), 11/15 (gte). The dose and persistence signatures are absent. |
| E interventional | predicts the change across a natural experiment | 1 | NE32 did not happen as catalogued (n/a). NE27 (kickoff-matched start): no veteran-only component. Rooms (#38): alignment follows the read population at once. |
| F identifiability | synthetic recovery with village sampling; robust to preprocessing | 1 | Synthetic at real counts with veteran-calibrated variance: size measured (0.06–0.085, calibrated cut), two biased estimators found and replaced (K normalization, NE27 reverse statistic). Power is low (0.15–0.30 at closure 0.5). Variants agree in sign (bge). |
| G ground truth | agrees with known structure | 1 | Room membership predicts which veterans newcomers align with (#38). |
| H comparative | beats the named rivals | 1 | R2 rejected (the family signature fades rather than grows). R1, R3, R4 not separable at this power. R5 not identifiable (A1.4). |
| I transfer | holds in other same-mode periods, including the holdout | 0 | Per-join ΔG scatters (−0.13 to +0.25); models disagree; holdout not run. |

## Confirmatory predictions (written 2026-10-04 21:15 UTC after round 1, before any holdout use; `analysis/confirm.py`, dry-run only, **not run**)
Targets: joins on held-out days or with windows in held-out windows (#1: GPT-4.1, o3, Gemini 2.5 Pro; #14: Sonnet 4.5; #22: GPT-5.2; #29: Opus 4.6; NE30: Gemini 3.1 Pro; NE21+NE23: Fable 5, Sonnet 5, DeepSeek-V4-Pro, GLM-5.2; #51 tail: Muse Spark 1.3, Gemini 3.8 Flash, GPT-6 Astra, and the L windows of GLM-5.3 Flash and Fable 5.1).
- **C1:** mean Ḡ_E in [−0.05, +0.02]. **C2:** mean ΔG < +0.032. **C3:** mean K_E > 0 and > half of joins positive. **C4:** mean ΔK < 0. **C5 (descriptive):** Gemini 3.1 Pro K_E > 0.
- **Overall:** the round-1 picture is confirmed if C1, C2 and C3 pass. Dry run on the 19 round-1 joins: all pass.
- **Reuse disclosure:** NE21+NE23 (H04 executed, activity), NE30 and the #51 tail have planned content users (H01, H13, H46, H73, …). Disclose in both cards and `LOG.md` if run.

## Caveats
- **Low power.** The persistent shared component is small, so P1 can detect only near-full closure. A null here is "inconclusive", not "no culture".
- **Model dependence.** bge and gte disagree on ΔG (statement-level geometry is model-dependent: infra Known issues, DQ5).
- **Family baselines** use 1–4 same-family newcomers per regime and share an onboarding component; unnormalized baselines remove the shared part (A1.3). The ΔK fade has CI-rule size 0.065–0.08 and is significant in bge only.
- **Batch joins** (NE27, NE32) share windows; the bootstrap resamples join days, which leaves 15 clusters.
- **#51 roles** are an agent-specific field. The own role text is projected out, but role-driven topics remain.
- **Windows cross goal boundaries** (exception (c)); the same-day veteran difference removes common shifts only.
- **Post hoc:** PH1 (baselines without same-day joins) and the NE32 premise check were added after the first real-data run.

## Round 2 redirects (2026-10-04)
*Proposed by the round-1 agent; the coordinator may revise.*
- **Where round 1 went sideways:** the culture newcomers could acquire is a few percent of content variance, and newcomers match the day's conversation at once. The window test asks a question the content channel cannot answer with 19 joins.
- **What the direction is really after:** whether a village holds anything newcomers must learn, beyond the conversation they read.
- **H83-R1.** Conventions, not centroids: follow village-coined terms and file conventions (H34 markers, HH291) through each newcomer's first uses, with ledger reads as the light cone (H41). Discrete adoptions have far more power than a 3% vector component.
- **H83-R2.** The entry family signature: find which content carries it (self-description, tooling, onboarding replies) and fit its decay time per join; run C3/C4 on the holdout joins.
- **H83-R3.** Call-level reading: newcomers' first calls after a room move, read vs posted-but-unread at matched lag (H57), to separate reading from a shared field in the immediate convergence (#38 rooms).
- **H83-R4.** Fix the NE32 catalog entry (isolation ≈ 1.5–2 h) and drop NE32 as an isolation experiment.

## Notes
- 2026-10-04 20:08 UTC: card written by the round-1 agent before any real-data alignment statistic. Seen before writing: roster join dates, calendar, period units, per-newcomer chat counts in the first 28 days.
- 2026-10-04 20:37 UTC: **prior information from H89 (coordinator message, received after H83's predictions were fixed and the replication had run; nothing changed in the design).** H89's NE32 Price partition: the #51 newcomers' content moves toward the veterans with bge (cos +0.26) but not with gte (−0.03), and their style moves away (−0.48); only GPT-5.6 Terra is active across the merge. Within periods, transmission among stayers carries 0.98 of content change; content changes carry no persistent attractor (C > 0 in 0/29 periods); at day resolution copying cannot be separated from a common field. These agree with H83's model dependence (bge ΔG +0.020, gte −0.011) and its untestable persistent component (P4), and they are cited in Results as independent context, not as a replication.
- 2026-10-04 21:03 UTC: **H81 methods warning and results seen (coordinator message; after H83's real-data replication had run).** (1) Leave-period-out personal vectors manufacture cross-period structure (H81 synthetic +0.37 under the null); H81 uses two-way agent + goal fixed effects. H83 uses no leave-period-out personal prior: O1 is a within-newcomer E→L difference minus the same-day veterans' difference, so an agent's prior cancels. The one cross-period object is the family newcomer baseline F_f (other newcomers' τ = 1 vectors from other periods); K's size was measured on synthetic data with the real join schedule (0.035–0.085 for the CI rule) and K is reported with that caveat. (2) Placebo-corrected excesses can be biased upward (+0.02–0.03): H83's P1 was calibrated on synthetic nulls (null mean ΔG +0.002 / +0.005; critical value +0.032, Amendment A1.1), which is the same order as H81's bias, so the calibration stands. No design change. H81/H82 context noted: regime-I collective slow mode τ ≈ 23–28 days; #51 common mode ≈ 3 active days; H82's day-1 carry-over is absorbed by each agent's own previous content; isolated #51 newcomers load weakly on regime-III history in bge only (H83 finds the same bge-only pattern for the #51 joins).
- 2026-10-04 21:24 UTC: round 1 finished. Order (file times): card 20:08 → scheme 20:10 → A0 20:12 → synthetic 20:14–20:29 → A1 20:33 → period predictions 20:34 → replication 20:34–20:37 → natives 20:36 → PH1/PH2 20:37–20:40. One heavy job at a time, pools ≤ 2. Data: `data/processed/H83-enculturation-of-newcomers/` (~55 MB) with `_provenance.json`. No code imported from other hypotheses' folders. The NE32 catalog correction is reported to the coordinator, not edited in `natural-experiments.md`.
