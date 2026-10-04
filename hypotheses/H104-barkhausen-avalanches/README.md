# H104: Barkhausen avalanches when a field is stepped

**Status:** exploratory round 1 done (2026-10-04; non-holdout only). **Failed as posed: mid-period human messages release no detectable switch bursts, and the crackling tail is not identifiable at village counts.**
- **No step response (P1, failed).** In #51, the only period with power (24 isolated human steps), switching after a step is ×1.09 [0.84, 1.32] (work) and ×1.07 [0.97, 1.18] (attention) the time-shuffle null. A planted τ = 3/2 avalanche at these counts gives ×1.87 and ×1.25 (5th percentiles 1.47 and 1.13), so the negative is powered. Pooled over 8 eligible period-channels: ×1.04 [0.86, 1.25] (work), ×0.91 [0.72, 1.14] (attention).
- **HH kill met:** big bursts are as frequent between steps as after them (BR 0.52 [0.31, 1.27] work, 1.40 [0.31, 4.78] attention). Burst size does not grow with step size (ρ −0.30 and −0.10, n.s.).
- **The tail cannot be tested (P2, inconclusive).** The synthetic validation shows the variance and Fano tests pass as often for a thin Poisson response or for endogenous bursts as for τ = 3/2 avalanches, and τ̂ lands in [1.2, 1.8] more often for the thin response.
- **Between steps, switching is near-Poisson given each agent's rate (P3, supported in #51):** quiet-window dispersion D = 1.12 (work) and 1.18 (attention), against 2.2–2.5 in a world with endogenous herding bursts.
- **Kickoffs move agents (P5, supported):** the share of agents switching in the kickoff day's first 2 h is 1.2–4.0× other days' in 7/8 period-channels.
- Natives: NE38 supported (a one-agent role reassignment: the target switches, nobody else beyond the null); NE43 mixed (the nudger stopping changes nothing beyond placebo splits); G44 uninformative (no response to localize).
- Scorecard A1 B1 C0 D0 E1 F1 G1 H0 I0. `analysis/confirm.py` (#51 tail, #43, #45) frozen, guarded and dry-run; **not run**.
**Question served (GOALS.md):** **Q2** (what is field and what is coupling?): do exogenous field steps (human messages, kickoffs) release crackling avalanches of project switches, with quiet Poisson switching in between? Q3 second: a mean-field RFIM exponent τ ≈ 3/2 would be a collective, near-critical response.
**Fields:** stat mech, dynamics, sociophysics
**Literature:** no note in `literature/` covers crackling noise. Cited from memory (†, not in `literature/`): Sethna, Dahmen & Myers, "Crackling noise", *Nature* 410, 242 (2001)†; Dahmen & Sethna, *PRB* 53, 14872 (1996)† (mean-field RFIM avalanches: P(S) ∝ S^{−3/2} at the critical disorder, cut off away from it); Perković, Dahmen & Sethna, *PRL* 75, 4528 (1995)†; Clauset, Shalizi & Newman, *SIAM Rev.* 51, 661 (2009)† (power-law fitting at small n).
**Definitions used** (`physics-models/DEFINITIONS.md`): Agent; Population N(t); Regime; Driving / external field; Contagion / adoption event, variant **arrival (project switch-in)** (H28) in the two channel forms below; H11's **agent state (categorical, project/artifact strict)** (shared `project_states`); H11 round-1b **agent state (categorical, project, work ledger)** (DQ4); Exposure (turn read-out) via `kicks_receipts`. **New named variants proposed for DEFINITIONS.md** (not edited here; outside this card's scope), defined under Data scheme: *field step (human session)*, *switch (work arrival)*, *switch (attention arrival)*, *burst size S*, *avalanche Fano F_A*.
**From:** HH330 in `hypotheses/hypohypotheses/HYPOHYPOTHESES.md` · **Models:** `physics-models/01-inverse-ising/` (random-field Ising, mean field), `physics-models/10-potts/` (project choice as a Potts variable), `physics-models/14-scaling-and-fluctuations/` (size distributions, dispersion)
**Data inputs (shared tables first):** DQ4 `work_commits` (agent work filter); shared `project_states` (w = 15 min, sources all); `kicks_classified` (+ `kicks_targets`, `kicks_receipts`) for human messages, kickoffs and nudges; `chat_core` + `embeddings/chat_bge_small.npy` (step novelty); DQ1 `call_windows` (agent spans, all-present window); `rooms_timeline`; `period_units`; `calendar`; `roster`.

## Source HH (verbatim from the HH list, including refinements)
Barkhausen avalanches: switches come in bursts when a field is stepped. In a disordered ferromagnet a slowly ramped field flips spins in avalanches with power-law sizes; this is crackling noise in the random-field Ising model. Here the field steps are mid-period human messages and kickoffs, and the flips are agents switching project or topic.
  - *Prediction:* switch bursts after field steps have a heavy-tailed size distribution whose exponent sits near the mean-field random-field Ising value τ ≈ 1.5. Burst size grows with step size. Between steps, switches are Poisson.
  - *Check:* DQ4 and `project_states` switch times, burst sizes after each step, and a time-shuffled null that keeps the step times.
  - *Kill:* burst sizes are no heavier than the null, or bursts are as frequent between steps as after them.
  - *Models:* 01, 10, 14 · *Builds on:* H54, H75, H53, HH129

## Question
When a human posts mid-period (a field step), do agents switch projects in bursts whose sizes are heavy-tailed (τ ≈ 3/2), growing with the step, while switches between steps are Poisson? Or do switches come in endogenous bursts unrelated to steps (H28, H53, H63: links announce pile-ons), with thin, Poisson-like responses to steps?

## Design: two layers (STANDARDS §4)
- **Replication (layer 1, role `replication`).** The common estimators (step response X, tail statistics V, F_A and τ̂, between-step dispersion D and burst ratio BR, dose slope ρ_s, kickoff ratio K) on every eligible non-holdout goal period, separately for two switch channels (work, attention). A period is eligible in a channel if it has ≥ 3 eligible human steps and ≥ 30 switches in agents' at-risk spans.
- **Hierarchical pooling (CLAUDE.md exception (d), named):** most periods have 3–15 human steps, too few for a per-period tail exponent. Per-period estimates are reported first; random-effects (DerSimonian–Laird) pools with shrinkage are reported next to them. Periods are never pooled completely: τ̂ is fitted per period, and the pooled τ is the RE mean of per-period τ̂.
- **Natives (layer 2, role `native`),** each with its own dated prediction in its folder:
  - **NE38** (G51, 07-29): a human reassigns one agent's role, a local field step. Does it release an avalanche beyond the target?
  - **NE43b** (G51, 08-21): the nudger stops. Nudges are tiny local steps; does the switch rate change?
  - **G44 rooms:** human messages are posted into one of two rooms. A field step acts through reading, so its excess should stay in its room.

## Model
**From:** `physics-models/01-inverse-ising` (mean-field RFIM), `physics-models/10-potts` (projects as Potts states), `physics-models/14-scaling-and-fluctuations` (size laws and dispersion).

**H104 variant: zero-temperature mean-field RFIM driven by field steps, with Poisson background flips.**
- Each agent is a Potts spin σ_i(t) = its current project. A **switch** is a flip. Each agent has a quenched random field h_i (role, own repo), a coupling J to the swarm's mean state, and a slowly varying external field H(t).
- **Step:** at t_k a human session moves H by ΔH_k. Spins whose local field crosses threshold flip; each flip raises the local field of others by J/N and can trigger more flips: an **avalanche** of A_k flips, read out within the window W.
- **Mean-field RFIM avalanche law** (Dahmen–Sethna†): P(A) ∝ A^{−τ} D(A/A*) with **τ = 3/2** at the critical disorder; A* diverges at criticality and is small far from it.
- **Between steps:** flips come from thermal noise and slow drift, so they are Poisson given each agent's rate.
- **Observed burst size:** S_k = A_k + B_k, with B_k the background flips in the window (null distribution known from the time shuffle).
- **Step size:** the session's message count m_k (primary); broadcast vs addressed; semantic novelty ν_k. RFIM predicts E[A_k] grows with ΔH_k.

**Rivals (named):**
- **R1 thin step response** (field, no avalanche): each step adds Poisson(μ) flips; F_A ≈ 1.
- **R2 endogenous herding** (H28, H53, H63): link-announced pile-ons between steps; bursts are as frequent between steps as after them; switching is over-dispersed everywhere.
- **R3 rate heterogeneity** ("fitness spread", H77/H78): agents with high switch rates fake heavy tails in pooled counts. The time-shuffle null keeps each agent-day's switches, so it removes this.
- **R4 scheduler** (day edges): switches pile up at day start. Removed by the at-risk span trim.

## Data scheme (`scheme/`)
`scheme/build.py` reads shared tables only and asserts the holdout twice (`calendar.holdout` and `common.holdout_mask`). Codes and times only (no text).
- **Agent spans (scheduler impostor):** from `call_windows` (non-holdout). Agent i is **at risk** on day d in [first call + 30 min, last call − 15 min]. Variant: the DQ8 all-present window (agents with ≥ 20 calls; [max first call, min last call]).
- **Switch (work arrival)** — primary channel: DQ4 agent work commits (`canonical & ~imported & author_kind == agent & ~automated`). Per agent and PT day, a commit on repo Y is a switch if the agent's previous work commit that day was on another repo and the agent made no commit to Y in the previous 60 min. Time = the commit time.
- **Switch (attention arrival)** — second channel: shared `project_states` (w = 15 min, sources all). A window whose modal project Y differs from the agent's previous labelled window that day and was not the agent's state in its previous 4 labelled windows. Time = the window start (15-min resolution).
- Switches count only inside the agent's at-risk span (primary).
- **Field step (human session):** `kicks_classified` kind `human_message` (subkinds plain, mention; not kickoff), merged into sessions when consecutive messages are ≤ 10 min apart on the same day. Step time t_k = first message. Size m_k = messages in the session; `broadcast` = any plain message; novelty ν_k = 1 − cos(session mean bge vector, mean bge vector of agent chat in the previous 60 min). Room = the session's (first) room.
- **Eligible step:** ≥ 3 agents at risk for all of (t_k, t_k + W], and no other session in (t_k − W, t_k) (isolated steps; variant: all).
- **Kickoff step:** `goal_kickoff` and kickoff-subkind human messages (first one per period).
- **Nudges** (`kind == nudge`): local steps, descriptive only.
- **Output:** `data/processed/H104-barkhausen-avalanches/G<NN>/` (`switches_{work,attn}.parquet`, `spans.parquet`, `steps.parquet`, `nudges.parquet`, `days.parquet`), `results/`, `synthetic/`, `_provenance.json`. Budget ≤ 50 MB.
- **Regimes covered:** I–III; all non-holdout periods that pass the eligibility rule. Fits are within period.

## Observables
*Written 2026-10-04 20:24 UTC, before any H104 statistic.* W = 60 min (variants 30, 120).

1. **Burst size** after step k: S_k = number of distinct at-risk agents with ≥ 1 switch in (t_k, t_k + W]. Variant: total switches C_k.
2. **Time-shuffle null (keeps step times):** each agent-day's switch times are rotated by an independent uniform offset within the agent's at-risk span (circular), 999 draws. It keeps every agent-day's switch count and its own clustering; it removes alignment with steps and cross-agent synchrony. A second null redraws each agent-day's switches uniformly (Poisson given the count).
3. **Step response:** X = mean S_k / mean S_k^null; one-sided p from the draws.
4. **Tail heaviness** (the Barkhausen signature):
   - V = Var(S_k)/mean Var(S_k^null) (variance ratio);
   - **avalanche Fano** F_A = [Var(S) − Var(S^null)] / [mean S − mean S^null]: Poisson-like response gives ≈ 1, a τ = 3/2 avalanche law truncated at N ≈ 15–30 gives ≈ 3–6;
   - **deconvolution MLE τ̂:** S_k = A_k + B_k, B_k from step k's empirical null pmf, A_k = 0 with probability π, else truncated power law on 1..|A_k at risk| with exponent τ; profile-likelihood 95% CI for τ.
5. **Between-step dispersion:** non-overlapping W-windows on the agents' at-risk days that start ≥ W after any step and end before the next one ("quiet windows"). D = Var(S)/mean Var(S^null) in quiet windows. **Burst ratio** BR = P(S > q95_null | post-step) / P(S > q95_null | quiet), q95_null the window's own null 95th percentile.
6. **Dose:** Spearman ρ_s between m_k and the excess E_k = S_k − mean S_k^null; secondary: broadcast vs addressed difference, and ρ with ν_k.
7. **Kickoff ratio K:** distinct agents switching in the first 120 min of the kickoff day's at-risk spans, divided by the mean of the same quantity on the period's other days (scheduler-matched placebo). Day-start switches include a change from the agent's last project of its previous active day.
8. **Pre-step placebo:** S in (t_k − W, t_k] against the null. Humans who post into ongoing bursts (reverse causation) show up here.
9. **Read-out gating (secondary):** per step and at-risk agent, switches before vs after the agent's receiving call for the session (`kicks_receipts`), as rates per minute against the null rate; Mantel–Haenszel rate ratio over steps.

**Pooling:** per-period numbers first; log X, log V, τ̂ and Fisher-z ρ_s RE-pooled across eligible periods per channel.

## Null / baseline
- Time-shuffle null (circular, primary) and uniform redraw (secondary), both keeping step times.
- Quiet windows (between steps) as the within-period baseline for BR.
- Pre-step windows (placebo for reverse causation).
- Kickoff-day vs other-day first-120-min windows (scheduler-matched kickoff placebo).
- **Synthetic worlds at real counts** (axis F, before real data): W0 Poisson null; W1 Barkhausen (τ = 3/2 avalanches at steps); W2 thin step response (Poisson, same mean); W3 endogenous Hawkes bursts, no step response (R2); W4 heterogeneous agent-day rates, no response (R3).

## Impostors (STANDARDS §1)
| Impostor | Relevant? | How H104 removes it | Status |
| --- | --- | --- | --- |
| Scheduler field | yes | At-risk spans exclude each agent's first 30 min and last 15 min; the time shuffle rotates switches inside those spans; all-present variant; the kickoff test uses a day-start-matched placebo. | removed |
| Exogenous field (kickoff, goal, operator) | yes (it is the object) | Steps are the measured field. Reverse causation (humans posting into bursts) is checked by the pre-step placebo. Kickoffs are a separate test from mid-period steps. | removed (as confound); measured (as object) |
| Shared model priors | partly | No family claim. Agent-specific switch rates (prior or role) are kept by the per-agent-day shuffle (R3). | removed |
| Contemporaneous convergence | yes | Post-step bursts could be endogenous cascades that coincide with steps. The read-out split (switches before vs after each agent's receiving call) and the quiet-window baseline test it. | partly |

## Faithfulness scorecard
Scored per model, mapping and window; 0 = not done or failed, 1 = partial, 2 = passed. Scheme and promotion thresholds: `writeup/paper.tex`, Sec. "Assessing model faithfulness".
**Rival models:** R1 thin step response; R2 endogenous herding (H28/H53/H63); R3 rate heterogeneity; R4 scheduler.
**Locked holdout used for confirmation:** none yet. `analysis/confirm.py` (#51 tail for C1–C4, #43 and #45 for the kickoff test C5) is frozen and guarded (`--confirm` + `H104_CONFIRM=1` + `holdout_ledger.check`). Dry run on the stand-in (#51 07-06 → 08-05; #38, #41) reproduces round 1 (C1 false; C2–C5 true). The tail may hold too few steps for C1–C4 (pre-declared fallback to all steps). **Not run.**
**Overall A–I:** A1 B1 C0 D0 E1 F1 G1 H0 I0.

| Axis | Test | Score | Evidence |
| --- | --- | --- | --- |
| A mapping | variables defined from dataset fields; assumptions listed; invariant across families and regimes | 1 | Switches (DQ4 work arrivals; `project_states` attention arrivals), steps (human sessions), spans (DQ1) are defined from shared tables. Step size is a crude proxy; attention time is quantized to 15 min. |
| B assumptions | stationarity, Markov order, time-rescaling, update-order audit | 1 | At-risk trim vs all-present trim and three windows audited; within-day stationarity of switch rates assumed by the rotation null. |
| C adequacy | beats the null hierarchy, day-blocked held-out data | 0 | The step model does not beat the time-shuffle null (X CIs include 1). |
| D unfitted predictions | unfitted statistics and the model's signature | 0 | No dose response; the tail signature is not identifiable; BR kill condition met. |
| E interventional | predicts the change across a natural experiment | 1 | NE38 (local step, no spread) as predicted for weak coupling; NE43 no change; kickoffs move agents. |
| F identifiability | synthetic recovery with village sampling; robust to preprocessing | 1 | Synthetic at real counts: step response identifiable in #51 (power ≥ 0.95), dispersion D identifiable; the tail is not. |
| G ground truth | agrees with known structure | 1 | Kickoffs (known large steps): K > 1 in 7/8 period-channels. |
| H comparative | beats the named rivals | 0 | The null (no step response) beats the Barkhausen model; R2 (endogenous herding) is rejected for #51's overall switching (D 1.1–1.2 vs 2.2–2.5). |
| I transfer | holds in other same-mode periods, including the holdout | 0 | No other powered period; holdout not run. |

## Prediction
*Written 2026-10-04 20:24 UTC, before any H104 statistic on real data.* **Seen beforehand:** per-period counts of non-holdout human messages, kickoff messages and naive switches (consecutive-window project changes in `project_states` w15; consecutive-commit repo changes in DQ4), with no timing relative to steps; the H63, H53, H28, H35, RE-O1, H03/H25/H34/H67 (subcritical) and H77/H78 headlines. **Not seen:** any burst size, any step-aligned or between-step statistic.

| # | Prediction | Counts against (kill) | Credence |
| --- | --- | --- | --- |
| P1 | **Steps release switches.** RE-pooled X > 1 (p < 0.05) in the attention channel; X > 1 in ≥ 1/2 of eligible periods. Work channel same direction. | pooled X ≤ 1 | 0.45 (attention) / 0.3 (work) |
| P2 | **Heavy-tailed bursts (the Barkhausen signature).** In periods with a step response, F_A > 2 with CI excluding 1, V > 1, and τ̂ in [1.2, 1.8] with CI excluding 3. **Kill:** burst sizes no heavier than the null (V ≤ 1 or F_A ≤ 1). | V ≤ 1 or F_A CI including 1 | 0.15 |
| P3 | **Poisson between steps.** In quiet windows D within [0.8, 1.25] in ≥ 2/3 of eligible periods. **Kill:** BR ≤ 1 (bursts as frequent between steps as after). | D > 1.25 in > 1/3 of periods, or BR ≤ 1 | 0.2 (D) / 0.4 (BR > 1) |
| P4 | **Burst size grows with step size.** RE-pooled Spearman ρ_s(m_k, E_k) > 0 with p < 0.05. | ρ_s ≤ 0 | 0.3 |
| P5 | **The largest step gives the largest burst.** Kickoff ratio K > 1 in ≥ 2/3 of eligible periods (descriptive manipulation check). | K ≤ 1 in ≥ 1/2 | 0.8 |
| P6 (secondary) | **Steps act through reading.** Read-after vs before-read switch rate ratio > 1 (MH, pooled). | ratio ≤ 1 | 0.5 |
| P7 (secondary) | **No reverse causation.** Pre-step S within the null band (pooled pre-step X in [0.8, 1.25]). | pre-step X > 1.25 | 0.6 |

My overall reading before data: the subcritical results (H03, H25, H34, H67) and the endogenous, link-announced herding (H28, H53, H63) make the crackling picture unlikely. The most probable outcome is a weak, thin step response (R1) on top of over-dispersed endogenous switching (R2).

**Amendment A1 (2026-10-04 21:04 UTC, after the synthetic validation, before any real-data statistic).** `analysis/synthetic.py` keeps each eligible period's real at-risk spans, isolated step times and per-agent-day switch counts (no switch timing is read) and plants four worlds (20 replicates each; 199 null draws): W0 Poisson, W1 Barkhausen (τ = 3/2 avalanches at steps), W2 thin response (Poisson, same mean), W3 endogenous bursts with no step response. Output: `data/processed/H104-barkhausen-avalanches/synthetic/summary.json`. **Eligible period-channels: 8** (#8, #12, #19, #30 attention; #38 work and attention; #51 work and attention). Only #51 has more than 4 isolated steps (24); the others have 3–4. G44 is not eligible (fewer than 3 isolated steps with ≥ 3 agents at risk).
1. **The step-1 question: can the heavy tail be told from the time-shuffle null at the observed counts? No.** In #51 the tail criterion (V > 1 and F_A CI above 1) passes in 30% (attention) / 60% (work) of W1 runs, in 10% / 45% of thin-response W2 runs, and in 80% / 70% of W3 runs with no step response at all. V and F_A react to any cross-agent clustering. τ̂ lands in [1.2, 1.8] in 10% / 30% of W1 runs and in 0% / 55% of W2 runs (median τ̂ 1.75–2.35 in both). In the 3–4-step periods no tail test ever passes. **P2 is therefore not identifiable: it is reported descriptively, and its verdict is "inconclusive" whatever the values.** The HH kill condition "burst sizes no heavier than the null" cannot be powered here.
2. **The step response X is identifiable in #51 only.** Power 0.95–1.00 (W1, W2), size 0.00–0.05 (W0) but 0.15 under W3 (steps that land in endogenous bursts). In the 3–4-step periods power is 0.25–0.75. Per-period X outside #51 is descriptive; the pooled X keeps its rule, and #51 is reported separately.
3. **Between-step dispersion D is identifiable in #51** (inside [0.8, 1.25] in 95–100% of W0–W2 runs and 0% of W3 runs) and partly in #38 attention (0.95 vs 0.05). **BR is valid only in #51** (W0 0.00; W1/W2 0.90–1.00; W3 0.00). With 3–4 steps BR's continuity correction gives size 0.65–1.00, so BR is descriptive there.
4. **Consequences for the rules.** Per-period verdicts: #51 (both channels) is the only period with power. The others are *descriptive*, as the card's rule allows (power < 0.5 for the tail test). For #51: *supported* needs X > 1 (p < 0.05), D in band and BR CI > 1, with the tail inconclusive; *failed* if X ≤ 1 or D > 1.25 with BR CI including 1 (bursts as frequent between steps). Because W3 inflates X, a step response in #51 counts only if the pre-step placebo X_pre is inside [0.8, 1.25].
5. **G44 native:** isolated steps are too few, so the native uses the "all steps" variant (W = 60 min), flagged as a variant.

**Per-period verdict rule (replication):** *supported* if X > 1 (p < 0.05), V > 1 with F_A CI above 1, and BR > 1; *failed* if V ≤ 1 or BR ≤ 1 (the HH's kill conditions); *mixed* otherwise; *descriptive* if the synthetic validation shows the period has power < 0.5 for its tail test (stated in Amendment A1).

## Results by goal period
Primary: isolated human steps, W = 60 min, at-risk spans; S = distinct switching agents; X = mean S / time-shuffle null (95% step-bootstrap CI). Amendment A1: only #51 has power; the 3–4-step periods are descriptive.

| Period | Role | Verdict | Key numbers |
| --- | --- | --- | --- |
| [G08](goalperiod-subhypotheses/G08/README.md) | replication (attention) | descriptive | 4 steps; X 0.57 [0.00, 1.27]; D 0.70; K 1.89 |
| [G12](goalperiod-subhypotheses/G12/README.md) | replication (attention) | descriptive | 3 steps; X 0.88 [0.49, 1.47]; K 1.00 |
| [G19](goalperiod-subhypotheses/G19/README.md) | replication (attention) | descriptive | 3 steps; X 0.93 [0.56, 1.29]; D 1.26; K 1.55 |
| [G30](goalperiod-subhypotheses/G30/README.md) | replication (attention) | descriptive | 4 steps; X 1.04 [0.78, 1.42]; K 1.16 |
| [G38](goalperiod-subhypotheses/G38/README.md) | replication (work, attention) | descriptive | 4 steps; X 0.93 [0.72, 1.42] / 0.65 [0.44, 0.73]; D 1.51 / 0.69; K 3.97 / 2.32 |
| [G44](goalperiod-subhypotheses/G44/README.md) | native (rooms; all-steps variant) | n/a | 9 steps; X 0.92 / 0.97: no response to localize |
| [G51](goalperiod-subhypotheses/G51/README.md) | replication (work, attention) | mixed (by the A1 rule: X > 1 but n.s.; D in band; BR CI includes 1) | 24 steps; X 1.09 [0.84, 1.32] / 1.07 [0.97, 1.18]; D 1.12 / 1.18; BR 0.52 / 1.40 (CI incl. 1); ρ −0.30 / −0.10; X_pre 0.82 / 0.93; K 2.42 / 1.65 |
| [NE38](goalperiod-subhypotheses/NE38/README.md) | native | supported | target switches (attention); others 2 (null 1–5) and 10 (null 10–15) |
| [NE43](goalperiod-subhypotheses/NE43/README.md) | native | mixed | switch rate after/before nudger stop 1.22 [0.72, 2.03] (work), 0.96 [0.86, 1.07] (attention); inside placebo bands |

## Results
*Exploratory round 1, 2026-10-04 (build 21:03 UTC, synthetic 21:03, real run 21:04, natives 21:05). Non-holdout only. Code: `scheme/build.py`, `analysis/h104lib.py`, `synthetic.py`, `run_periods.py`, `natives.py`, `summarize.py`, `confirm.py`. Data: `data/processed/H104-barkhausen-avalanches/results/{periods.parquet, steps.parquet, pooled.json, natives.json}`, `synthetic/{results.parquet, summary.json}` (28 MB in total). Figures: `figures/summary_obs_col.pdf` (peri-step switching, #51), `figures/synthetic_col.pdf`. Estimates: 94 rows in `per_period_estimates` (`hypothesis == "H104"`).*

### Headline
Mid-period human messages do not release avalanches of project switches. In #51 (24 isolated steps) switching in the hour after a step is within 10% of the time-shuffle null in both channels. The step response that a mean-field RFIM avalanche law would produce at these counts is excluded. Big bursts are as frequent between steps as after them, and switching between steps is close to Poisson given each agent's rate. Kickoffs, the largest field steps, do move agents. The crackling exponent cannot be tested with the village's step counts.

### Outcome vs prediction
| # | Prediction | Observed | Outcome |
| --- | --- | --- | --- |
| P1 | pooled X > 1 (attention), work same direction | attention 0.91 [0.72, 1.14] (k 5); work 1.04 [0.86, 1.25] (k 2); #51 1.07 / 1.09, both CIs include 1 and lie below the Barkhausen world's 5th percentile | **failed** |
| P2 | heavy tail: V > 1, F_A CI > 1, τ̂ in [1.2, 1.8] | V 1.02 / 1.19 (#51), F_A CIs include 1; τ̂ at the grid edge with π̂ 0.57–0.99 (no avalanche component) | **inconclusive** (not identifiable, A1) |
| P3 | D in [0.8, 1.25]; BR > 1 | #51 D 1.12 / 1.18 (in band; attention p 0.011 against the null band); BR CIs include 1 | D supported; **BR failed (HH kill met)** |
| P4 | ρ_s(m, E) > 0 | #51 −0.30 / −0.10; pooled −0.33 / −0.18 (n.s.) | **failed** |
| P5 | K > 1 in ≥ 2/3 | 7/8 (1.16–3.97; #12 1.00) | supported |
| P6 | read-after > before-read rate | work: 0 switches in 43 agent-hours before reading (≈ 4.4 expected), ratio 4.6× null; attention 0.68× | uninformative (unread time is idle time) |
| P7 | pre-step X in [0.8, 1.25] | #51 0.82 / 0.93 | supported (no reverse causation) |
| NE38 | target flips; no avalanche | target switches (attention); others inside the null band (2 of 26; 10 of 26) | supported |
| NE43 | nudger stop: rate ratio in [0.85, 1.15] and inside placebo band | 1.22 [0.72, 2.03] (work), 0.96 [0.86, 1.07] (attention); both inside the placebo band | mixed |
| G44 | room-local excess | no step response (X 0.92 / 0.97) | n/a |

### Findings
1. **Human messages are weak fields for project choice.** The upper CI bound of the #51 step response is ×1.32 (work) and ×1.18 (attention). A message changes what one agent does (NE38) without spreading.
2. **Switching between steps is close to Poisson given agent rates.** D ≈ 1.1–1.2 against ≈ 2.2–2.5 for a world with herding clusters of four agents in 20 min. H63's herding bursts exist, but at the level of all switches they add little over-dispersion.
3. **Kickoffs are the field steps that move the swarm.** On the kickoff day 48–100% of agents switch in the first 2 h, against 17–86% on other days (K 1.2–4.0).
4. **The crackling exponent needs many more steps.** With S bounded by N ≈ 15–30 and ≤ 24 steps, a τ = 3/2 law cannot be told from a thin response.

### Caveats
- Only #51 has power; every other period has 3–4 isolated steps.
- Attention switches have 15-min resolution, so the 60-min window holds 4 windows.
- The at-risk trim drops the first 30 min of each agent's day, so morning steps rarely qualify.
- Work switches need a commit, so idle agents cannot switch (this drives the read-out split).
- Steps are human sessions; their size (message count) is a crude field magnitude.
- Variants in #51: W = 30 / 120 min give ×0.94 / ×1.08 (work) and ×1.11 / ×0.97 (attention); the all-present trim gives ×1.20 (work, p 0.09) and ×1.04; switch counts give ×1.10 (work) and ×1.13 (attention, p 0.013). At most a 10–20% response survives in single variants.

## Round 2 redirects
- **What the direction is really after:** which inputs move a swarm's allocation of effort, and by how much.
- **H104-R1. Kickoff-scale steps.** Pool kickoffs across periods as an event study of allocation (fraction switching vs time from kickoff, per call), with day-start-matched placebos.
- **H104-R2. Directed vs broadcast human steps.** Restrict to messages that name a project or ask for a change; test switching of the named agents only.
- **H104-R3. Avalanches in content, not projects.** Use the 30-min content state (DQ5) as the spin; content flips are far more numerous than project switches, which may give tail power.

## Notes
- 2026-10-04 20:24 UTC: round 1 started; card filled before any H104 statistic.
- 2026-10-04 20:46 UTC: timestamp correction. The first versions of this card and its native folders carried estimated times that ran ahead of the clock; all times are now corrected from file creation times (`stat`). The order of events is unchanged: card and predictions, then synthetic validation, then amendments, then real data.
- 2026-10-04 21:03–21:12 UTC: scheme build (33 periods), synthetic validation (640 runs), Amendment A1, period folders, real run (8 eligible period-channels × 6 variants), natives, summary, confirm dry run.
- Proposed for `physics-models/DEFINITIONS.md` (not edited): *field step (human session)*, *switch (work arrival)*, *switch (attention arrival)*, *burst size S*, *avalanche Fano F_A*.
