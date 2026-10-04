# H35: The nudger is a measurably inefficient Maxwell demon

**Status:** **round 1b done (2026-10-04, work ledger + DQ1 sustained runs):** the nudger buys glances (+0.08, near-efficient, η_SU 0.88), not work: sustained runs and work commits per nudge are zero after placebo differencing (+0.22 commits/h [−0.29, +0.82]), the trap-age response is flat for work and the once-early policy gain (×2.3 active minutes) does not carry over to commits. NE10 and NE43 are invisible in work. Round-1 numbers below reproduce unchanged. Exploratory round 1 done (2026-10-03; 13 non-holdout goal periods + NE10 + an undocumented nudger stop inside #51). **The nudger is an inefficient demon, in a stronger form than predicted, and only in the short-pause scaffold.**
- **Information used:** 1.42 bits of agent state per nudge (G51), out of 10.7 bits of decision entropy per nudge. Trap age (length of the pause chain) carries most of it.
- **Work bought:** 1.45 [0.72, 2.20] extra active minutes per first nudge (H04: 1.54). That is 0.5% of the swarm's active agent-minutes.
- **Efficiency (G51, trap-age space):** η_SU = 0.38 [−0.08, 0.68] of the work the same bits could buy; η_KW = 0.15 of the bits were needed; κ = 0.49 extra active min per bit per nudge. Among agents already pausing, its choice is *worse than random* (−0.04 to −0.08 escapes per nudge): 38% of nudges go to chains ≥ 10 pauses deep, where a nudge buys 0.5 min, against 2.2–2.6 min at k = 1–9.
- **Policy:** nudge once, during an early re-pause (k = 2–3), only while the agent is in a declared pause, and stop re-nudging deep traps. At the same budget that is ×2.3 [1.7, 5.2] work per nudge (G51).
- **Regime dependence:** before the 06-11 pause-default change (12 h → 5 min), a nudge wakes a pausing agent at any trap age (escape 0.86–1.0), so targeting hardly matters (G38, G41).
- Confirmatory script written and dry-run on stand-ins; **not run**.
**Fields:** stat mech, sociophysics, info theory
**Origin:** HH124 (`../hypohypotheses/HYPOHYPOTHESES.md`; `../promotion-shortlist.md`); HH18 (nudger as a Maxwell demon) and HH52 (catalyst vs field) as background.
**Definitions used** (`physics-models/DEFINITIONS.md`): Agent; Regime; Action; Driving / external field (automated nudges); Interaction (addressed) for directed kicks; Mutual information (here between the controller's action and an agent's state: proposed named variant "Mutual information (controller–state)"); Semantic information (Kolchinsky–Wolpert), with work in place of viability (proposed named variant "Semantic efficiency of a controller"). **Work** here is *not* the DEFINITIONS "Energy / work proxy" (tokens): it is activity gained, proposed as the named variant "Work (feedback, activity gain)". DEFINITIONS.md is not edited here; the variants are proposed in the round-1 report.

## Standards (2026-10-04)
*Documentation pass against `STANDARDS.md`. No analysis was re-run. Every entry rests on this card and its round-1b section.*

**Question served:** Q5. The nudge is an operator lever, and the card measures what it buys. Q6 second: Sagawa–Ueda and Kolchinsky–Wolpert efficiency of a feedback controller.

| Impostor | Relevant? | How it was handled | Status |
| --- | --- | --- | --- |
| Scheduler field | partly | Matched strata are agent × idle × gate × trap age × day-third; placebo window [−30, −16] min (Definitions, Null 2). Outage windows are not censored (Caveats). Close by censoring `outages_fixed` (§1, row 1). | partly |
| Exogenous field (kickoff/goal/operator) | partly | The nudge is the field under study. Strict past-only isolation drops minutes with a human message or agent mention in the prior 30 min. | removed |
| Shared model priors | no | Agent-level response with agent strata; no family or content claim. | n/a |
| Contemporaneous convergence | no | No peer-to-peer influence claim. | n/a |

**Inputs:** the leading-@ target was used from round 1. Active rows come from `events_core` and `actions`, not `activity_bins`. Round 1b adds the DQ4 work ledger and DQ1 ledger sustained runs. Still old: outages are not censored with `outages_fixed`. Failures and embeddings are not inputs.

**Two layers:** no folder has role `replication`. The common estimator (bits per nudge, first-nudge ATT) runs on 13 period folders under role `exploratory`; only G51 is powered. Native tests: 4 (`G51` work outcomes, mixed; `G38` NE44 contrast, failed as worded; `NE10` and `NE43` in work, supported).

**Confirm script:** `analysis/confirm.py` exists, dry-run only. Its inputs reproduce exactly in round 1b, but its outcomes are round-1 active minutes and TS2r escapes. **Re-freeze before any holdout run** (round-1b synthesis decision 2; holdout.md item 8). Add the glance, sustained-run and work-commit outcomes with the post hoc DiD placebo.

## Question
How many bits of agent-state information does the auto-nudger use per extra active minute it buys, and how close is that to the best possible use of the same bits? H04 found that a nudge raises the named agent's activity after a delay (A30 = 1.54 extra active minutes, regime III); H16 found that a directed message during a pause raises the odds of acting at the timer gate ×1.5–2.9, saturating, while traps age. A feedback controller that acts on measured state is a Maxwell demon; the thermodynamics of information (Sagawa–Ueda; Kolchinsky–Wolpert) says how much work a given amount of information can buy. Practical aim (usefulness-first batch): a number an operator can compute from logs (work per bit, and the fraction of attainable work) and a concrete better nudging rule.

## Model
**From:** `physics-models/04-semantic-information` (Kolchinsky–Wolpert value of information, information/viability curve, semantic efficiency) and `physics-models/02-nonequilibrium-ising` (response to a kick at a state-dependent update; the gate model of H09/H16).

**Background.**
- *Sagawa–Ueda (feedback control):* with measurement outcome M of system state X, the extractable work obeys ⟨W⟩ ≤ −ΔF + k_BT·I(X;M); the efficiency of information use is η = W/(k_BT·I) ≤ 1, reached only by a reversible feedback protocol.
- *Kolchinsky–Wolpert:* value of information ΔV = V(actual) − V(scrambled), with the full scramble p(x)p(m); the information/viability curve Δ(R) = max V over interventions keeping R bits; stored semantic information S = the least information that preserves V; semantic efficiency η = S/I; thermodynamic multiplier κ = ΔV/I ("bang per bit").

**H35 variant: the nudge engine.**
- **System X:** an agent's state at a decision epoch: idle duration D (minutes since its last active row), gate timing G (in a declared pause, and time to the pause's expiry), trap age K (re-pause count of the current pause chain, H16's TS2r k).
- **Demon action M ∈ {0, 1}:** a nudge naming the agent (the leading @-target of an automated `repeated-idling` message) in that epoch. Budget r = E[M].
- **Work Y:** extra active minutes of the target in the 30 min after the epoch (A30, H04's window; secondary: extra non-mirror tool turns).
- **Response function** g(x) = E[Y | do(M = 1), x] − E[Y | do(M = 0), x].
- **Value of the demon's information:** ΔV(π) = E[π(X) g(X)] − r·E[g(X)]: the work bought beyond a random nudger with the same budget (the full scramble).
- **Information–work frontier** (the H35 Δ(R)): V*(R) = max ΔV(π) over policies with E[π] = r and I(X;M) ≤ R. Solution (rate-constrained Blahut–Arimoto; the free-energy / bounded-rational policy): π_β(x) = σ(logit r + β(g(x) − λ_β)), λ_β fixing the budget; β = 0 is random nudging, β → ∞ the deterministic top-r rule.
- **Landauer-like ceiling** (Donsker–Varadhan): ΔV ≤ σ_g·√(2 r I) (I in nats per epoch), i.e. per nudge ΔV/r ≤ σ_g·√(2 b ln 2) with b = bits per nudge. The spread σ_g of the response across states plays the role of k_BT: information buys work only if agents respond differently in different states.
- **Efficiencies of the logged nudger** (I_log bits, ΔV_log work):
  - κ = ΔV_log / I_log: extra active minutes per bit (per nudge: ΔV_log/r over b);
  - η_SU = ΔV_log / V*(I_log): the fraction of the work attainable with the same bits (Sagawa–Ueda-like);
  - η_KW = R*(ΔV_log) / I_log, with R* the inverse frontier: the fraction of the bits used that were needed (Kolchinsky–Wolpert semantic efficiency).
- **Gate decomposition (regime III; H09/H16 mechanism):** a nudge during a pause is read at the next expiry; g(x) = Δp_esc(x)·B(x), with Δp_esc the change in the probability of acting at the gate and B the extra active minutes per escape.

**Rivals.**
- **R0 worthless information (catalyst):** g(x) is flat across states, so ΔV ≈ 0 for every policy at fixed budget; the nudger works only through its budget, and its bits buy nothing (HH52's catalyst reading).
- **R1 efficient demon:** the nudger already sits near the frontier (η_SU ≳ 0.7).
- **R2 no work:** g ≡ 0 (nudges are read and ignored).
- **R3 selection artifact:** the nudger fires on agents whose escape hazard is falling (aging, H16), so naive before/after or future-selected controls bias the work either way.

## Definitions (operational; shared tables only)
- **Nudge:** an `automated` chat message whose text carries the `repeated-idling` trigger tag (text is read in memory, never stored). **Target** = the agent named by the leading `@`, matched with `infra/shared/common.mention_regexes` against that day's roster. Other agents mentioned later in the text are recorded as `n_mentions` but are not targets. Sensitivity: H04's mapping (automated message with ≥ 1 valid roster mention; all mentioned agents are targets). Automated messages without the tag are the daily pause/resume bookends and are dropped.
- **Active row:** H16's rule (any `events_core` agent event except WAIT and PAUSE; any `actions` turn except the `pause` mirror), via `h16lib.load_rows` (imported, not modified). Present agent-day: ≥ 1 active row that day; the Claude Code agent is excluded.
- **Decision epochs.**
  - *Minute level:* every present agent-minute (i, m) with m ≥ 15 (burn-in) and m + 30 inside the day's window.
  - *Gate level (regime III):* every TS2r gate (PAUSE event) from `h16lib.build_ts2`; M_g = 1 if a nudge to the agent arrives between the PAUSE and its gate.
- **State bins (fixed now).**
  - D: [0, 1) active · [1, 3) · [3, 10) · [10, 30) · ≥ 30 min · cold (no active row yet today).
  - G: none · in pause with > 5 min left · 2–5 min left · ≤ 2 min left · overdue (expired, still no active row).
  - K: 0 (not in a chain) · 1 · 2–3 · 4–9 · ≥ 10 (TS2r k of the current chain; a chain ends at its escape).
  - N (controller memory, not agent state): minutes since the last nudge to the agent that day: none · < 30 · 30–90 · ≥ 90.
  - Gate-level state: K bin × declared-duration bin (≤ 5, (5, 30], > 30 min) × N bin.
  - Regime I/II (no pause tool): G is dropped; K = the length of the current run of consecutive WAIT events.
- **Information.** Plug-in I(M; X) on the joint count table with the Miller–Madow correction, minus the mean of a permutation null (each agent-day's nudge count is redistributed by a circular shift over that agent-day's eligible minutes); reported per epoch and as **bits per nudge** b = I/r. Chain-rule decomposition I(M;D) + I(M;G|D) + I(M;K|D,G); add-ons I(M;A|X) (agent identity) and I(M;N|X) (controller memory). Determinism δ = I(M; X, N, A)/H(M). Day-block bootstrap CIs.
- **Work, minute level (ITT, past-only isolation).** Treated: first nudges (no direct kick to the agent in [m − 30, m − 1]; direct = nudge to it, human message in its room or naming it, agent message naming it). Controls: same-stratum minutes with no direct kick in [m − 30, m]; **future kicks are allowed in both arms**, so the contrast is "nudge now vs not now, the policy continuing" (no conditioning on the future; rival R3). Stratum = agent × D × G × K × day-third, with fallback to the stratum without agent when < 20 controls. ATT on A30 and on tool turns; placebo window [−30, −16]. H04's future-isolated design is reported as a variant. Repeat nudges (another nudge to the agent in [m − 60, m − 1]) are reported separately.
- **Work, gate level.** Logistic gate model with agent fixed effects: logit P(escape_r) = α_i + θ ln k + ψ ln declared + γ_N 1[nudge during the pause] + λ 1[nudge]·(ln k − c) + Σ_c γ_c 1[other directed kick c] (c = agent / human mention). B(K bin) = mean A30 after escape minus after re-pause, from un-nudged gates. ĝ(x) = Δp̂_esc(x)·B̂(K). Cross-fitted by alternating days.
- **Policy values (per nudge, same budget as logged).** Direct method on the cross-fitted ĝ over the logged epochs, plus inverse-propensity weighting where the logged propensity overlaps:
  - *logged* (the nudges that happened);
  - *random-gate* (the same count spread uniformly over gates; the Kolchinsky full scramble at gate level);
  - *random-minute* (uniform over present agent-minutes; needs ĝ for active states, which nudges never visit: bounded below by g = 0 and above by the directed-agent-mention response; secondary);
  - *gate-once(k\*)* (one nudge per chain, during re-pause k\*, k\* ∈ {1, 2, 3});
  - *frontier* π_β.
- **Synthetic validation:** `analysis/synthetic.py`. Agents with timer-gated pause chains, aging escape and agent frailty; nudges read at the next gate with a known state-dependent effect; a logged-like `repeated-idling` policy with re-firing; random, gate-once and frontier policies. True I, g, ΔV, κ, η from the generative model; estimators run at village sample sizes (G51-like: ~700 nudges; small-period-like: ~25).

## Data scheme (`scheme/`)
- **Inputs:** `events_core`, `actions`, `chat_core`, `chat_text` (trigger tag and leading target only, in memory), `chat_mentions_clean`, `exposure`, `calendar`, `roster`; `h16lib` (rows, TS2r gates) and `h04lib` (H04's nudge mapping, sensitivity only) imported unmodified.
- **Output:** `data/processed/H35-nudger-maxwell-demon/G<NN>/` with `nudges.parquet` (message id, time, target, n_mentions; no text), `grid.parquet` (agent-minute states, M, kicks, outcomes), `gates.parquet` (gate states, M_g, outcomes), `results.json`, `_provenance.json`. Also `G27/` (NE10 before-period), `G51off/` (08-21 → 09-02, nudger silent; `offstep_results.json`), `NE10/`, `synthetic/`, `confirm_dryrun/` (stand-ins G44, G51a = 07-06..07-10, G51b = 07-13..07-17, G31, G35). Total ≈ 8 MB.

## Candidate goal periods (unit of analysis: one goal period; non-holdout only)
Structural check before predictions (counts only; no H35 statistic): nudges carry a single trigger tag, `repeated-idling` (1,550 messages in total, all starting with "@Target"; 345 also mention other agents). Non-holdout nudge counts: #30 12 (all on 02-13), #31 24, #33 22, #35 17, #36 6, #37 17, #38 108, #39 7, #40 11, #41 59, #42 25, #44 27, #51 728. **The nudger falls silent on 2026-08-20 (5 nudges that day, none afterwards) with no CHANGELOG entry**; the daily bookends had already stopped on 08-05; 18 human messages appear on 08-20. This creates an undocumented nudger-off step inside #51 (non-holdout days 08-21 → 09-02 before NE33), since catalogued in parallel as **NE43** (whose row dates the bookend stop to 08-21; the data show 08-05).

| Period | Role | Regime | Nudges | Analysis |
| --- | --- | --- | --- | --- |
| G51 (07-06 → 08-19) | primary | III, 8 h | 728 | full: information, minute and gate work, frontier, policies |
| G51 off-step (08-21 → 09-02) | natural experiment | III | 0 | DiD on gates by the nudger's trigger region; work accounting |
| G38, G41 | secondary | III, 4 h | 108, 59 | full, lower power |
| G37, G39, G40, G42, G44 | descriptive | III | 7–27 | information; ATT |
| G31, G33, G35, G36 | descriptive | I / II | 6–24 | information (no gates); ATT |
| NE10 (G30 + G31) | natural experiment | I | 12 + 24 | switch-on: work accounting; regime-I information |
| 🔒 #45, #47, #50, #32, #34 | confirmatory | | | `analysis/confirm.py`, not run |

## Observables
- **O1** bits per nudge b (minute level), its decomposition (D, G | D, K | D,G), agent and controller-memory add-ons, determinism δ.
- **O2** gate-level information I_gate (bits per nudged gate).
- **O3** ATT (A30, tool turns) of first and repeat nudges; placebo.
- **O4** gate model: γ_N, λ (does the kick effect fall with trap age?), B(K).
- **O5** policy values per nudge; ΔV, κ, η_SU, η_KW; the frontier V*(R) and the Donsker–Varadhan ceiling.
- **O6** G51 off-step: escape-probability DiD (gates in the nudger's trigger region vs below it, before vs after 08-20), chain-length tail, aggregate active fraction vs the accounting prediction Σ(per-nudge work)/agent-minutes.
- **O7** NE10: the same accounting for the switch-on; regime-I information.

## Null / baseline
1. **Information:** the permutation null (nudge counts per agent-day kept, timing scrambled within the agent-day) gives the bias floor; I is "used" only above its 95th percentile.
2. **Work:** ATT = 0, with the placebo window [−30, −16] required to be ≈ 0; H04's future-isolated design as a contrast that shows the selection bias direction.
3. **Value of information:** the full scramble (random nudging, same budget), ΔV = 0 by construction; **R0 test**: heterogeneity of ĝ across state cells (Wald χ² on the gate-model interaction and the CATE cells). If ĝ is flat, every policy has the same value and η is undefined: the nudger's bits are worthless.
4. **Policy:** logged = gate-once (value ratio CI including 1).
5. **Off-step:** no change in the DiD (the nudger had no effect on the gates it targeted).

## Faithfulness scorecard
Scored per model, mapping and window; 0 = not done or failed, 1 = partial, 2 = passed. Scheme and promotion thresholds: `writeup/paper.tex`, Sec. "Assessing model faithfulness". Scored after round 1 (2026-10-03).
**Rival models:** R0 worthless information (catalyst); R1 efficient demon; R2 no work; R3 selection artifact.
**Locked holdout used for confirmation:** none yet. `analysis/confirm.py` targets #45, #47, #50 (information, gate mechanism, policy ranking) and #32, #34 (work, information); written, dry-run on stand-ins, not run. Reuse is disclosed below.

| Axis | Test | Score | Evidence |
| --- | --- | --- | --- |
| A mapping | variables defined from dataset fields; assumptions listed; invariant across families and regimes | 1 | Nudge = the `repeated-idling` tag, target = the leading @ (all 1,550 nudges carry the one tag); state from active rows, PAUSE events and TS2r chains; work = A30 and tool turns. The mapping holds across periods, but the *response* flips with the pause default (12 h → 5 min on 06-11), so a single response model is not regime-invariant |
| B assumptions | stationarity, Markov order, time-rescaling, update-order audit | 1 | Identification rests on selection on observables (the nudger reads the event log). It holds only partly: agent identity carries 0.43 bits per nudge beyond (D, G, K), so the nudger uses state we do not capture. The strict past-only design has a clean placebo (0.38 [−0.08, 0.86]); the repeat and H04-isolation variants do not. No stationarity audit within #51 |
| C adequacy | beats the null hierarchy, day-blocked held-out data | 1 | Information above the permutation null in 9/13 periods (all with ≥ 15 nudges except G33). Work beats ATT = 0 (G51). Response heterogeneity rejects R0 (k 1–9 minus k ≥ 10: 1.86 [0.47, 3.53] min). Policy values are cross-fitted over 5 day-folds. No prediction on wholly held-out days of a policy actually changed |
| D unfitted predictions | unfitted statistics and the model's signature | 1 | Predicted before the run and held: the swarm-level accounting (nudges buy ≤ 1% of active minutes, so NE10 and the 08-20 stop are invisible at swarm level). Predicted and failed: the information magnitude (1.4 vs 3–8 bits per nudge), agent-blindness, and positive value of information among gates |
| E interventional | predicts the change across a natural experiment | 1 | NE10 and the undocumented 08-20 nudger stop. The accounting prediction is met in both (no detectable change), a weak test. The gate DiD at the stop has the predicted sign but is 10× the accounting and matches an in-period placebo drift |
| F identifiability | synthetic recovery with village sampling; robust to preprocessing | 1 | Synthetic recovery at G51 size: information within ~5% of truth; past-only ATT within ±0.2 min of the Monte Carlo truth; policy ratios and η_SU, η_KW recovered, though levels run 10–20% low. H04's future-isolated design is biased low under re-firing, as predicted. Not identifiable at ≤ 30 nudges (small periods are descriptive). Robustness to preprocessing is partial (two gate models, three isolation designs; bins not varied) |
| G ground truth | agrees with known structure | 1 | The only trigger tag is `repeated-idling`, and the measured targeting is dominated by trap age. H04's nudge A30 is reproduced (1.45 vs 1.54). H09's "only @-mentions get through a pause" appears as the long-pause wake-up effect |
| H comparative | beats the named rivals | 1 | In G51: R0 rejected (heterogeneous response), R1 rejected (η_SU 0.38; negative value among gates), R2 rejected (ATT > 0). R3 is only partly excluded: the strict placebo is clean, the variant placebos are not. In the long-pause periods R0 is close to true *among gates* (targeting barely matters) |
| I transfer | holds in other same-mode periods, including the holdout | 1 | The information level transfers across regime-III periods (b = 1.2–1.4 in G38, G42, G44 and G51; 2.2 in G37). The "deep traps don't respond" pattern does not transfer to the long-pause periods (G38: the effect rises with trap age). G51 is the only short-pause non-holdout period. Holdout not used |

## Prediction
*Written 2026-10-03, before any H35 statistic was computed on real data and before the synthetic validation.*

**What had been seen first:** the H04, H09 and H16 cards and LOG entries (nudge A30 = 1.54 [0.80, 2.29] in regime III; delayed response peaking ~15 min; re-firing on non-responders; directed kicks at gates OR 1.5–2.9, saturating; aging traps); H30's message counts; and my own structural counts above (trigger tags, nudges per period, the 08-20 silence, mention counts per nudge). No nudge-state cross-tabulation, no response and no gate outcome has been computed by me.

**Decision rules.** Verdicts are per period; card-level claims need G51 plus the stated count of secondary periods. With ~13 periods × ~10 statistics, single-period hits in small periods are not evidence; only G51, G38 and G41 carry weight, and small periods are descriptive.

- **P1 (information is used).** b is above the permutation null p95 in G51, G38, G41 and in every other period with ≥ 15 nudges. G51: b ∈ [3, 8] bits per nudge. D and K together carry ≥ 60% of I(M;X); gate timing given (D, K) ≤ 25%; agent identity given X ≤ 15% (the nudger is agent-blind). Controller memory N adds ≥ 0.3 bits per nudge beyond X (cooldown and re-fire cadence).
- **P2 (work).** First-nudge ATT on A30 in G51 ∈ [0.5, 3] extra active minutes with a CI excluding 0; positive point estimates in G38 and G41. Placebo window CI includes 0. Repeat nudges have ATT ≤ 50% of first nudges (saturation; H16). The future-isolated (H04) design gives a *smaller* ATT than the past-only design (selection of controls on later activity).
- **P3 (state dependence; against R0).** The response is heterogeneous: the gate-model interaction λ < 0 (the kick's effect falls with trap age) or the CATE at K ≥ 10 is below the CATE at K ≤ 3, in G51, and the heterogeneity test rejects flatness at p < 0.05 in G51.
- **P4 (inefficient demon; against R1).** In G51 at gate level: ΔV_log > 0; η_SU ≤ 0.5 and η_KW ≤ 0.3, with bootstrap CIs whose upper end is below 0.7. κ ∈ [0.05, 0.5] extra active minutes per bit per nudge.
- **P5 (better policy).** At the logged budget, gate-once with k\* ∈ {1, 2} has a value per nudge ≥ 1.25 × the logged nudger's in G51 (cross-fitted direct method), and the point ratio is ≥ 1 in G38 and G41. The frontier at the logged bit budget roughly doubles the logged ΔV (V*(I_log)/ΔV_log ≥ 2, the same statement as η_SU ≤ 0.5).
- **P6 (G51 off-step, 08-20).** (a) Accounting: nudges buy ≤ 1% of G51's active agent-minutes, so the aggregate active fraction after 08-20 does not change beyond day-to-day noise (|Δ| below 2 day-SDs). (b) Gates in the nudger's trigger region (defined from the pre-period propensity) lose escape probability relative to gates below it after 08-20 (DiD < 0); magnitude consistent with the pre-period nudge rate × Δp̂_esc. Sign only; power is low.
- **P7 (NE10, regime I).** The accounting predicts a ≤ 0.5% change in active agent-minutes from the switch-on, i.e. undetectable; b on #30–#31 is above the permutation null.

**What would count against the hypothesis:** η_SU > 0.7 (R1, an efficient demon); a flat response (R0: bits buy nothing, so "inefficiency" is moot); a first-nudge ATT with a CI including 0 in G51 (R2); a placebo-window response (R3, selection).

## Amendments (dated; what had been seen)
- **Before any real data (2026-10-03), after the first synthetic smoke test:**
  - the minute state is read at the *end* of the minute, so it includes the PAUSE event that triggers a nudge inside the minute (reading at the start put treated cells in the wrong state);
  - conditional information terms use a within-stratum permutation null;
  - matching uses exact chain age (capped at 15);
  - cross-fitting moved from day halves to 5 day-folds (small worlds broke the halves);
  - a shared-slope gate model ("transport": mentions identify the trap-age slope where the nudger never acts) was added and set as the code default. **The card's own gate model (written above, nudge-specific slope) is the primary for scoring**: in G51 the nudger acts at every trap age, so no transport is needed, and the data reject transport (nudge slope −0.32 ± 0.13 vs mention slope +0.02 ± 0.06). Both models are reported everywhere.
- **A1, post hoc, after the first G51 run.**
  - *What had been seen:* the G51 information decomposition, where the circular-shift-corrected shares exceeded 1.
  - *The problem:* on real data agent-days differ in idleness, so the circular-shift null keeps real "which agent-days" information; it is a pure bias floor only in the synthetic, which has no day-level heterogeneity.
  - *Fix:* marginal terms now subtract a full-permutation bias null (≈ 0 after Miller–Madow at these sizes). The within-day timing part (circular shift) is reported separately: 0.62 of G51's 1.42 bits.
  - The synthetic validation was rerun with the amended estimator (numbers below are from the rerun).
- **A2, post hoc, after the first G51 run:** two additions.
  - The **minute-level trap-age efficiency** (X = 5 chain-age bins, work = the directly measured first-nudge A30, shrunk). The gate route (Δp_esc × minutes per escape) captured only ~0.4 of the 1.45 min per nudge, because nudge-induced activity is more persistent than spontaneous escapes (H04's Onsager ratio 1.54).
  - The **coarse efficiency** (pause status × idle duration), with unvisited groups bounded at 0 and at the agent-mention response.
  - P4 is scored as written (gate level); the minute-level numbers are labelled secondary.
- **A3, post hoc:** an ATT variant with H04's isolation set (nudges + human messages; agent mentions allowed).
  - Strict isolation leaves almost no first nudges in the 4-h periods (G41: 0) or in regime I/II.
  - The variant's placebo is not clean in G51 (0.57 [0.19, 1.01]), so it is reported, never scored.

## Synthetic validation (axis F; `analysis/synthetic.py`, rerun 2026-10-03 with the amended estimator)
**Simulated data.**
- Regime-III-like agents: active bursts, pause chains with 5/15/30-min pauses, glances, aging escape (θ = −0.5 per ln k) and agent frailty.
- A known response: a nudge or mention during a pause is read at the gate, and one kick counts; γ_N(k) = ln 2 − 0.3 (ln k − ln 3), mentions at 0.8× the nudge effect.
- Scenarios:
  - S1 inefficient: a logged-like `repeated-idling` policy (k ≥ 4, cooldown, re-firing) under that response;
  - S2 efficient: nudge once at k = 1;
  - S3 flat: no trap-age dependence.
- Sizes: G51-like (30 agents × 33 eight-hour days, ~700 nudges, 6 reps), G38-like (12 × 17 four-hour days, ~110–170 nudges, 10 reps), small (12 × 5, ~25 nudges, 20 reps).

Results: `data/processed/H35-nudger-maxwell-demon/synthetic/synthetic_summary.json`, `figures/synthetic_validation.pdf`.

| Check (G51-like unless noted) | Truth | Estimate (mean ± SD over reps) | Consequence |
| --- | --- | --- | --- |
| bits per nudge, S1 / S2 / S3 | 2.14 / 3.99 / 3.01 | 2.25 ± 0.11 / 3.99 ± 0.06 / 2.85 ± 0.13 | information recovered |
| bits per nudge, small size | same | 1.99 / 3.03 / 2.29 | biased low ~25% at ~25 nudges |
| first-nudge ATT (past-only), S1 / S2 / S3 | 0.25 / 0.96 / 0.65 (Monte Carlo replay) | 0.41 ± 0.18 / 0.90 ± 0.26 / 0.64 ± 0.15 (first run: S1 0.18 vs 0.29) | unbiased within ±0.2 min |
| H04 future-isolated design, S3 (re-firing) | 0.65 | 0.44 ± 0.15 | **biased low under re-firing** (why past-only is primary) |
| policy ratio once(k=1) / logged, S1 | 4.00 | 3.60 ± 1.00 (shared gate model) | ranking recovered |
| η_SU, η_KW, S1 / S2 | −0.86, 0 / 0.99, 0.96 | −0.84, 0 / 0.99, 0.96 | efficiencies recovered |
| flat response S3: ΔV, ratios | 0, 1.03 | 0.01 ± 0.02, 0.87–0.94 | R0 is detectable |
| level of policy values | | 10–20% low | TS2r escape and chain-age definitions blur the gate outcome; use ratios |
| separate-slope model, S1 (no nudges at k < 4) | 4.00 | 2.61 ± 1.69 | extrapolation fails without support; in G51 support exists at every k |
| G38-like size, S1 ratio | 3.09 | 3.46 ± 1.98 | direction only |
| small size | | ratios ±10 or worse | **gate efficiencies not identifiable at ≤ 30 nudges** |

## Confirmatory predictions (C-*): for the locked holdout, written 2026-10-03 after round 1, not run
Script: `analysis/confirm.py`.
- **Guards:** it refuses without `--confirm --i-understand-this-uses-the-locked-holdout`, and refuses if the H35 folder has uncommitted changes. `--dry-run` uses stand-ins: #45 → G44, #47 → G51 07-06..07-10, #50 → G51 07-13..07-17, #32 → G31, #34 → G35. The stand-ins overlap exploration data, so the dry run is a code check, not evidence. Its output is in `data/processed/H35-nudger-maxwell-demon/confirm_dryrun/`.
- **Overall rule:** supported if no primary prediction fails and ≥ 1 passes; failed if none passes; otherwise mixed.
- **Regime split:** the pause default changed 12 h → 5 min on 06-11, so #45 is long-pause, while #47 and #50 are short-pause.
- **Reuse (holdout policy):**
  - H04's confirmatory run computed the nudge A30 kernel on #45 (segment A1) and #46–#50 (NE21 segments), so H35 makes **no work (ATT) prediction there**. Its statistics on #45, #47 and #50 are the nudger's state information, the gate mechanism and the policy ranking, which nobody has computed.
  - #32 (H05's NE12 window; H16's unrun script) and #34 have no earlier nudge-response statistic.
  - The card and script must be committed before the run; the disclosure goes in LOG.md.

| ID | Target | Statement | Primary |
| --- | --- | --- | --- |
| C1 | #45, #47, #50 | information above the permutation null, b ∈ [0.8, 3.0] bits per nudge | yes |
| C2 | #47, #50 | trap age carries the targeting: I(M;K) + I(M;K given D,G) > I(M;G given D) | yes |
| C3 | #47, #50 | nudging once at the first re-pause (k* = 2) beats the logged nudger per nudge (card gate model, escapes, ratio > 1) | yes |
| C4 | #47, #50 | the nudge's effect at the gate falls with trap age (card model nudge × ln k < 0) | yes |
| C7 | #45 | long-pause wake-up: escape at nudged gates ≥ 0.8 and at un-nudged gates ≤ 0.6 | no |
| C5 | #32, #34 | first-nudge ATT (H04 isolation set) has a positive point estimate | no |
| C6 | #32, #34 | information above the permutation null | no |

- **Dry run (stand-ins, not evidence):** C1 3/3 pass; C2, C3, C4 2/2 pass; C7 pass; C5 0/2 pass; C6 1/2 pass.
- **Expectations and power:** #47 and #50 have 88 and 94 nudges. G51's 5-day stand-ins gave a C3 ratio of 1.1–2.0 and a C4 slope SE of ≈ 0.4, so C4 is a sign test with modest power.

## Results by goal period
Verdict rules are in each folder; small periods are descriptive (P1 scored only with ≥ 15 nudges in the grid).

| Period | Role | Verdict | Key numbers (b bits per nudge; first-nudge ATT min; gate effect slope; once(k=2)/logged) |
| --- | --- | --- | --- |
| [G51](goalperiod-subhypotheses/G51/README.md) | primary (short pauses) | mixed | b 1.42; ATT 1.45 [0.72, 2.20]; nudge × ln k −0.32 ± 0.13; ×2.01 (card model), ×1.58 [1.34, 1.81] (shared); η_SU 0.38, η_KW 0.15; off-step invisible at swarm level |
| [G38](goalperiod-subhypotheses/G38/README.md) | secondary (long pauses) | mixed | b 1.25; ATT 1.27 [−0.32, 2.91]; slope **+1.18** ± 0.52 (wake-up); ×1.02 |
| [G41](goalperiod-subhypotheses/G41/README.md) | secondary (long pauses) | mixed | b 0.44; strict ATT n/a (H04-isolation 3.25); slope (shared) +0.36 ± 0.40; ×1.11 |
| [G37](goalperiod-subhypotheses/G37/README.md) | descriptive | descriptive | b 2.20 (above null) |
| [G42](goalperiod-subhypotheses/G42/README.md) | descriptive | descriptive | b 1.37 (above null) |
| [G44](goalperiod-subhypotheses/G44/README.md) | descriptive | descriptive | b 1.19 (above null) |
| [G39](goalperiod-subhypotheses/G39/README.md), [G40](goalperiod-subhypotheses/G40/README.md) | descriptive | descriptive | 6 and 9 nudges |
| [G33](goalperiod-subhypotheses/G33/README.md) | descriptive (II) | descriptive | b ≈ 0, **not** above null (15 nudges) |
| [G31](goalperiod-subhypotheses/G31/README.md), [G35](goalperiod-subhypotheses/G35/README.md), [G36](goalperiod-subhypotheses/G36/README.md) | descriptive (I/II) | descriptive | 11, 6, 4 nudges |
| [NE43](goalperiod-subhypotheses/NE43/README.md) | natural experiment (nudger silent after 08-20, inside #51) | mixed | nudges = 0.50% of active minutes; Δ active fraction −1.4 pp [−4.8, +2.0] (invisible, as predicted); gate DiD −0.050 vs predicted −0.005 and placebo drift −0.032 (inconclusive) |
| [NE10](goalperiod-subhypotheses/NE10/README.md) | natural experiment | supported (accounting only) | switch-on predicted ≤ 0.4 pp of agent-minutes; observed +1.1 pp [−2.8, +4.9]; detectable ≈ 7 pp |

## Results
### Exploratory round 1 (2026-10-03; non-holdout)
- **Scripts:**
  - `scheme/build.py`;
  - `analysis/run_period.py <period>`, `offstep.py`, `ne10.py`;
  - `synthetic.py`, `summarize_synthetic.py`;
  - `figures.py`, `write_period_folders.py`;
  - `confirm.py`;
  - library `analysis/h35lib.py` (imports `h16lib` unmodified).
- **Numbers:** `data/processed/H35-nudger-maxwell-demon/<period>/results.json`, `G51off/offstep_results.json`, `NE10/ne10_results.json`, `synthetic/`.
- **Figures:** `figures/summary_obs.pdf` (one-page summary figure), `figures/cross_period.pdf`, `figures/synthetic_validation.pdf`.

**Outcome vs prediction (card-level).**

| Prediction | Predicted | Outcome | Verdict |
| --- | --- | --- | --- |
| P1 information | b ∈ [3, 8] in G51, above null in every period with ≥ 15 nudges; D+K ≥ 60%; G given (D,K) ≤ 25%; agent ≤ 15%; memory ≥ 0.3 | G51 b = 1.42 (10.7 bits of decision entropy per nudge, so 13% determined by state); above null in 7/8 scored periods (G33 not). D+K 89%; G given (D,K) 11%; agent 31%; memory 0.32 bits | **partly**: right composition, ~2.5× fewer bits than predicted, not agent-blind |
| P2 work | ATT ∈ [0.5, 3], CI excl. 0; placebo ∋ 0; repeat ≤ 50%; H04 design smaller | 1.45 [0.72, 2.20]; placebo 0.38 [−0.08, 0.86]; repeat 1.04 (71%); H04 design 1.40 | **mostly supported** (the repeat clause fails, with a selection-tainted placebo) |
| P3 state dependence | response falls with trap age; flatness rejected (G51) | card model −0.32 ± 0.13; minute response 2.2–2.6 (k 1–9) vs 0.52 (k ≥ 10) min; difference 1.86 [0.47, 3.53] | **supported in G51**; reversed in the long-pause G38 |
| P4 inefficient demon (gate level) | ΔV_log > 0; η_SU ≤ 0.5; η_KW ≤ 0.3; κ ∈ [0.05, 0.5] | ΔV among gates **negative** (−0.076 card model; −0.042 [−0.062, −0.024] shared); η_SU < 0; η_KW = 0. Minute trap-age space: ΔV +0.50 [−0.09, 1.16] min, η_SU 0.38 [−0.08, 0.68], η_KW 0.15 [0, 0.48], κ 0.49 [−0.10, 1.11] | **failed as worded** (a stronger inefficiency: harmful fine-grained choice); bands met in the minute-level space (secondary) |
| P5 better policy | once at k* ∈ {1, 2} ≥ 1.25 × logged (G51); ≥ 1 in G38 and G41 | G51: ×2.18 / ×2.01 (card model), ×1.55 [1.26, 1.84] / ×1.58 [1.34, 1.81] (shared); ×2.31 [1.66, 5.20] in minutes (k 2–3). G38 ×1.02, G41 ×1.11 (k* = 2) | **supported** (the k* = 1 policy loses in the long-pause periods) |
| P6 off-step (08-20) | accounting: invisible; gate DiD < 0 near −0.005 | nudges = 0.50% of active minutes; Δ active fraction −1.4 pp [−4.8, +2.0] (placebo −2.9); DiD −0.050 [−0.099, −0.005] vs placebo −0.032 | (a) **supported**; (b) **inconclusive** (drift) |
| P7 NE10 | accounting ≤ 0.5%; information above null | predicted ≤ 0.4 pp, observed +1.1 pp, detectable ≈ 7 pp; information unscorable (< 15 nudges per period) | accounting **supported**; information n/a |

**Reading.**
1. **What the demon measures.** The auto-nudger's decisions carry 1.4 bits of agent state per nudge out of 10.7 bits of decision entropy, so most of *when and whom* is unexplained by idle duration, pause timing and trap age. What it does read is trap age: the nudge rate rises 20× from agents not in a pause chain to chains ≥ 10 pauses deep. It also favours particular agents beyond their state (0.43 bits), and its own cooldown and re-fire memory adds 0.32 bits. It fires a median 133 s after the agent's latest PAUSE.
2. **What a nudge buys.** 1.45 extra active minutes and 6 extra tool turns in the next 30 min (G51). Summed over its 20 nudges a day, that is 0.5% of the swarm's active agent-minutes, too small to see when the nudger switches on (NE10) or silently off (08-20).
3. **How efficiently.** This is Sagawa–Ueda and Kolchinsky–Wolpert bookkeeping, with work in extra active minutes. The analytic ceiling is ΔV ≤ s·√(2 r I), with s the half-range of the response across states (the k_BT analogue).
   - *Coarse:* the information "this agent is idle or pausing" is used fairly well: η_SU ≈ 0.7, κ ≈ 1.2 min per bit.
   - *Trap age:* the nudger gets 38% of the work its bits could buy (η_SU) and needed only 15% of them (η_KW).
   - *Among pausing agents:* its choice is worse than random, because it concentrates on the deepest traps, which barely respond (gate escape 0.07 with or without a nudge at k ≥ 10, against +0.07 to +0.22 at k = 1–9). This is Kolchinsky's negative value of information: correlations that are real but used against the viability (here work) objective.
4. **The better policy.** In the current, short-pause scaffold:
   - nudge each pause chain **once**, at the first or second re-pause (k = 2–3);
   - nudge only while the agent is in a declared pause (the 23% of nudges to agents not in a chain buy ~0);
   - do not re-nudge chains past ~10 pauses; those need a different intervention (H16: messages never break error loops; traps age).
   
   At the logged budget this doubles to triples the work per nudge (×2.3 [1.7, 5.2] in minutes; ×1.6–2.0 in gate escapes). Even so the swarm-level stake is small (≈ 1% of active minutes) unless the budget grows. Under the old 12-h pause default, a nudge woke the agent at any trap age and targeting mattered little.

**Caveats.**
- *Identification.*
  - Selection on observables is plausible (the nudger is an algorithm reading the event log) but incomplete: agent identity carries information beyond our state.
  - The past-only design's placebo is clean in G51 only for strict isolation, so the repeat-nudge ATT and the H04-isolation variant carry selection.
  - The minute-level response by trap age rests on 20–99 first nudges per bin and is shrunk; the K = 1 and K = 2–3 bins have wide CIs (2.2 ± 1.1, 2.6 ± 1.2).
- *Model dependence.*
  - The gate route (Δp_esc × minutes per escape) captures only ~0.4 of the directly measured work. Minutes per escape is an observational difference, and nudge-induced activity is more persistent.
  - The efficiencies depend on the chosen state space; three spaces are reported and they differ (coarse ≈ 0.7, trap age 0.38, gates < 0).
  - The shared-slope gate model rests on a transport assumption the data reject. The card's nudge-specific model is primary.
- *Power and multiplicity.*
  - Only G51 is powered.
  - G51 is the only short-pause non-holdout period, so the policy result has no out-of-period replication yet.
  - About 13 periods × ~10 statistics: single hits in small periods are not evidence.
- *Data.*
  - The 08-20 nudger stop is undocumented and coincides with an unusual burst of human messages; the daily bookends stopped on 08-05.
  - Calendar windows with outages (H16 A3) were not censored here.
- *Post hoc.* A1–A3 above (null for marginal information terms; minute-level and coarse efficiency spaces; H04-isolation variant). Scored verdicts use the predictions as written.

**One-page figure summary** (`figures/summary_obs.pdf`). (a) The G51 information–work plane in trap-age space. The frontier V*(R) at the logged budget and the Donsker–Varadhan ceiling bound what any policy using R bits per nudge can buy beyond random nudging. The logged nudger (1.04 bits, +0.50 min) sits far below the frontier (+1.32 min at the same bits); nudging only at k = 2–3 reaches the frontier's end (+2.0 min); nudging only deep traps is worse than random. (b) The share of nudges by trap age against the response per nudge: the nudger's mass sits where the response is lowest.

## Round 1b (improved data, 2026-10-04)

### What changed
- **Inputs:** H35 already used the leading-@ target and never read `activity_bins` (active rows come from `events_core` + `actions` via `h16lib`), so the round-1 grids, information and A30 numbers reproduce exactly (bits per nudge 1.42; first-nudge A30 +1.45 [0.72, 2.20]). No round-1 primary statistic changes.
- **New outcomes** (`analysis/r1b_outcomes.py`; outputs `data/processed/H35-nudger-maxwell-demon/<period>/r1b/`, `r1b/r1b_summary.json`): **glance** (any active row in 30 min), **sustained** (a run of ≥ 3 consecutive active DQ1 ledger calls starts within 30 min; H43's definition), **work** (DQ4 agent work commits in 30/60 min, automated commits excluded). Same past-only matched design, strata, trap-age bins and frontier code; gate model refit on a sustained run within 15 min of the pause expiry.
- **Post hoc (`--did`):** the matched design fails its placebo window for sustained runs (+0.058) and work commits (−0.35): nudged agents had just finished a burst. A rate difference-in-differences (post rate − placebo rate) is reported next to the matched ATT, labelled post hoc.

### Round 1 vs round 1b (G51)
| Quantity | Round 1 (active minutes) | Round 1b |
| --- | --- | --- |
| bits per nudge | 1.42 | 1.42 (unchanged) |
| work per first nudge | +1.45 active min [0.72, 2.20] | glance +0.082 [+0.035, +0.132] (placebo clean); sustained runs +0.29/h [−0.16, +0.70] (DiD); work commits **+0.22/h [−0.29, +0.82]** (DiD; matched −1.16, placebo not clean) |
| η_SU / η_KW (trap-age space) | 0.38 [−0.08, 0.68] / 0.15 | glance 0.88 [0.26, 0.97] / 0.79; sustained: flat response, η undefined (ΔV = 0); work (DiD) 0.19 [−1.39, 0.70] / 0.05 [0, 0.43] |
| κ | 0.49 active min per bit per nudge | glance 0.033 per bit; work 0.006 commits/h per bit (n.s.) |
| once-early (k = 2–3) / logged | ×2.30 [1.71, 4.75] | active min ×2.30 (same); glance ×0.92; work ×1.29 (CI spans 0); gate sustained ×1.03 |
| response k 1–9 minus k ≥ 10 | +1.87 min [0.33, 3.60] | glance −0.05 (deep traps glance most); sustained +0.04 [−0.03, +0.13] |
| share of swarm output bought | 0.5% of active minutes | ≈ 0.4% of work commits (upper CI 1.5%) |

### Natives (predictions dated before the run, in the folders)
- **G51** (work on three definitions): **mixed.** Glance > 0 as predicted; the sustained and work clauses fail as worded because the pre-registered design fails its placebo for them; after differencing both are zero, the trap-age response is flat and the once-early gain vanishes for work, as predicted in substance.
- **G38** (NE44 contrast, long pauses): **failed as worded** (sustained 0.058 vs G51 0.094); post hoc DiD reverses the order (+1.26 vs +0.29 runs/h, CIs wide).
- **NE10** (first nudges, work ledger): **supported** (work z +0.92; no strictly isolated first nudges for the per-nudge test).
- **NE43** (two steps, work ledger): **supported** (nudger off −0.03 day-SD; bookends off −0.49 day-SD).

### Verdict changes and scorecard
- Card-level claim narrows: **the nudger is an inefficient demon for activity (glances, active minutes) and a worthless one for work.** Its bits buy glances near-efficiently (η_SU 0.88), active minutes at 38% efficiency, and no measurable committed work or sustained runs; the once-early policy (×2.3 active minutes) should not be sold as a work lever. This agrees with H43 (glance ×1.75, no sustained escape) and H39 (catalytic glance).
- Period verdicts: G51 mixed → mixed; G38 mixed → failed (native, as worded); G41 mixed (unchanged); NE10 supported → supported (now in work); NE43 mixed → supported (work: both steps invisible); small periods descriptive.
- **Scorecard (1b): all 1s (unchanged).** B is weaker than it looked: selection on observables fails for sustained and work outcomes (placebo). D gains a held prediction (H43's glance-not-work, confirmed after differencing). Ratings (suggested): completeness 45 → 55, faithfulness 2.0 → 2.0, **usefulness 2.5 → 2.0** (the policy buys glances, not output).

### What the work ledger changes
Round 1's "work" was active minutes, which a glance inflates. Measured as commits that land, a nudge buys nothing detectable (≈ 0.4% of commits at most), and neither the nudger's switch-on (NE10) nor its two-step shutdown (NE43) moves the swarm's committed work. The demon accounting still works; what it accounts for is attention, not production.

## Notes
- **From RE-V1 (2026-10-04):** the ledger shows no early wakes at nudge-receiving calls before or after 06-11 (NE44). The pre-06-11 "nudge wakes a pausing agent at any trap age" pattern reflects fewer targets being mid-pause (38% vs 73%), not wake-on-message. H04's corrected nudge effect in #51: A30 1.16 [0.75, 1.57] (first 1.38, repeats 0.90).
- 2026-10-04: promoted from HH124 by Vivian (usefulness-first batch); wave 2.
- 2026-10-03: round 1 started. Predictions above written before any real-data statistic. Structural finding: an undocumented nudger stop on 2026-08-20 inside #51, now NE43 in the shared catalog (added in parallel by someone else). The test is in `goalperiod-subhypotheses/NE43/`.
- 2026-10-03: round 1 done. Compute: local, ≤ 2 threads; synthetic ~15 min, real data ~10 min. Disk: `data/processed/H35-nudger-maxwell-demon/` ≈ 8 MB. A session limit interrupted the final rerun of all periods; on resume every period's outputs were checked on disk, all were complete, and nothing was rerun.
- 2026-10-03: holdout reuse. #45 and #46–#50 had the nudge A30 computed by H04's confirmatory run, so H35 predicts only information, gate-mechanism and policy statistics there; #32 and #34 have no earlier nudge-response statistic. The card and confirm.py must be committed before any run; disclose in LOG.md.
