# H28: Links are the contagion vector of herding

**Status:** exploratory round 1 done (2026-10-04). **The contagion claim is not supported as posed.** Seeing a link to project X goes with a higher switch hazard to X almost everywhere (pooled e^κ = 2.3, 13/14 periods p < 0.05). But in herding weeks **future links predict switches better than past ones** (pooled κ_lead − κ = +1.17 ± 0.30). Naive agents are already switching at 3.3× baseline in the hour before they first see a link. The 60-min effect beats a ±30–120 min link shift in only 3/11 herding periods (card-level P1 failed). Links mark conversational attention bursts more than they drive them. A directed link → visit signature appears only in own-artifact weeks, where nobody herds. Simulated removal of all links cuts peak pile-ons to ×0.79 (median; an upper bound). Predictions were written 2026-10-04 before any real-data run; the frozen holdout test is written, not run.
**Fields:** stat mech, sociophysics, info theory
**Origin:** HH114 (`../hypohypotheses/HYPOHYPOTHESES.md`; `../promotion-shortlist.md`). Related: HH109 (early warning of herding waves), HH79 (group exposure beats pairwise: tested here as complex contagion via distinct senders). Follows H11's next step 2 (kinetic Potts with `exposure`).
**Definitions used:** "Interaction (broadcast)", with a named variant proposed for DEFINITIONS.md, **interaction (link exposure, call-start visible)**; "Contagion / adoption event", with a named variant **arrival (project switch-in)**; H11's **agent state (categorical, project/artifact strict)**, used here in a multi-label form (**on-project state**); "Regime"; "Population N(t)" (active-population variant: agents with ≥ 1 logged turn in a 5-min bin). All defined under Data scheme.

## Question
In a kinetic Potts model with exposure, the probability that an agent switches to project X rises with the number of recent links to X it saw: an infection rate per link exposure. Throttling link-sharing would damp pile-ons. *Check:* switch hazard vs exposure count (artifact mentions in chat) with agent fixed effects, vs a common-drive rival.

Practical aim (usefulness-first batch): produce a number or rule an operator of an LLM agent swarm could compute from logs and act on. Here: an **infection probability per link exposure** λ, a **link branching number** R_link per period, and a simulated answer to "would throttling link-sharing damp pile-ons?".

## Model
**From:** `physics-models/10-potts` (kinetic Potts, transition rates conditioned on others) and `physics-models/03-contagion` (simple vs complex contagion, field vs imitation as in Bass, branching number).

**H28 variant: multi-label kinetic Potts with an exposure field (a piecewise-exponential hazard).** Agent i is *on* project X while it keeps touching X (strict mention within the last 60 min). Off X, its rate of switching in ("arriving") in 5-min bin b is

log μ_{iXb} = α_i + γ_{X,d(b)} + κ · E_{iX}(b) + J · log(1 + n_{−i,X}(b)) + η · H_{iX}(b) + ζ · K_i(b)

- α_i: agent field (propensity to switch at all); γ_{X,d}: project × day field (**common drive**: the goal, the day's agenda, announcements, the project's daily popularity). *Fitted as π_X + δ_d (project and day fields) after Amendment 1; the project × day part is handled by the link time-shift null, and γ_{X,d} is re-estimated with κ, J fixed for the simulator.*
- **E_{iX}(b): link exposure.** Links to X posted in chat by others that had become visible to i (call-start rule, below) within the last 60 min. κ is the contagion coupling; e^κ is the hazard ratio per exposure state.
- n_{−i,X}(b): other agents currently on X. J is the ordinary Potts (work-observation / mean-field) coupling, the channel H11 measured as βJ.
- H_{iX}(b): own history (i touched X before in this period; log of its prior touches; X named in i's current self-written plan): **homophily / "already heading there"** controls.
- K_i(b): agent-level common pulses (a human message in i's room in the last 30 min; a nudger message to i in the last 30 min; a goal kickoff in the last 60 min); time-of-day quarter.

Arrivals are rare per bin, so the Poisson log-likelihood with fixed effects is the piecewise-exponential (Cox-type) hazard model. In Potts language, the transition rate into state X is a softmax-type exponential in fields plus couplings; links add an agent-specific, time-local field on X.

**Infection rate per link exposure (attributable):** λ = Σ_rows (μ̂ − μ̂|_{E=0}) / N_exp, where N_exp is the number of (link, susceptible recipient) pairs: recipients that were off X, active, and saw the link. λ is the expected number of extra arrivals per link exposure.

**Branching number of the link channel:** R_link = π · k_s · λ, with π = links posted per arrival and k_s = susceptible recipients per link. Algebraically R_link = Σ(μ̂ − μ̂|_{E=0}) / Σ y: the fraction of arrivals attributable to links (the Hawkes identity "branching ratio = endogenous fraction", restricted to the link channel). R_link < 1 means link-driven cascades die out on their own; a pile-on then needs drive or the occupancy channel.

**Counterfactual:** the fitted hazard plus empirical link-posting and on-spell kernels form a generative simulator per period. Thin links by a factor f (f = 1, 0.5, 0) or cap them (≤ 1 link per project per room per 2 h) and compare simulated pile-on sizes with the f = 1 simulation.

## Data scheme (`scheme/`)
`scheme/build.py` (helpers in `scheme/h28lib.py`) builds `data/processed/H28-links-spread-herding/G<NN>/` from the shared tables, non-holdout days only (it refuses holdout periods unless called with `--allow-holdout`, which only `analysis/confirm_holdout.py` does). Imported, not modified: H11's project map (`H11/scheme/build.py: project_map`), H18's turn-time rule (`H18/scheme/build.py: turn_times`).

- **Project:** H11's map (a repo is its own project; file → parent repo; site → parent repo when known, else its own; Netlify deploy-preview prefixes stripped; domains and Google `/e` placeholders excluded).
- **Touch:** a strict artifact mention (`artifact_mentions`, `speaker_kind = agent`, `how ∈ {url, output, bare}`) of a project by agent i, from its computer-use **actions** or its own **chat** messages. One touch per (agent, source, turn or message, project). Intentions are *not* touches; they enter as the plan covariate.
- **Project universe U_g:** projects touched by ≥ 2 distinct agents in the period (non-holdout days), at most 30 (by distinct agents, then touches). Robustness: U⁺ also adds every project linked in chat at least once (failed links included).
- **On-project state (multi-label):** i is on X at time t if it touched X in [t − 60 min, t) on the same PT day. Non-exclusive (an agent can be on several projects).
- **Arrival (project switch-in):** a 5-min bin b (clock time inside the day's empirical active window) in which i was off X at bin start and touches X. *First* arrival: i never touched X earlier in the period (adoption, SI); otherwise a *return*.
- **Risk set:** (i, X, b) with i on the day's roster (Claude Code agent excluded), active in b (≥ 1 logged turn: `actions` minus `pause` mirrors, or any `events_core` event), and off X at bin start.
- **Link:** a chat message with a strict mention (`source = chat`, `how ∈ {url, bare}`) of a universe project, by an agent or a human. **Recipients:** the message's `exposure` rows (agents in the room), minus the sender.
- **Interaction (link exposure, call-start visible):** recipient i sees link m at t_vis = i's first logged turn at or after t_m (each model call shows the events since the previous call; turns are `actions` minus `pause` mirrors plus `events_core`, as in H18). **Before NE09 (2025-12-20, chat interleaved into computer use)** chat may not reach computer-use calls, so for #18–#20 t_vis = t_m + `exposure.lag_s` (next `events_core` turn) instead.
- **Covariates at bin start T_b:** E(0–15 min), E(15–60), E(60–240) (visible links, kernel bins); 1[E60 ≥ 1]; distinct senders in the last 60 min; addressed link (the link names i, `chat_mentions_clean.mentions_roster`); occupancy n_{−i,X}; own prior touches; X in i's current plan (latest `intentions` row before T_b names X, via `artifact_mentions` source = intention); human / nudger / kickoff pulses (`kicks`; nudger vs pause messages are not separated: noted); quarter of the active window.
- **Placebo exposures:** **lead** links (posted by others to X in (T_b, T_b + 60 min], counted for i only if i would be a recipient); **other-room** links (posted to X in a room i is not in, last 60 min; multi-room periods only).
- **Output:** per period `links.parquet` (msg row, t, sender, room, project, how, addressed agents), `exposures.parquet` (link, recipient, t_vis), `touches.parquet`, `turn_bins.parquet` (active agent-bins), `plans.parquet` (intention id, agent, t, project), `meta.json`; `_provenance.json` at the folder root. No text. The risk-set panel is rebuilt on the fly by `analysis/h28core.py` (it is cheap and would dominate storage).

## Candidate goal periods
- **Named candidates:** #31 (free week; the time-capsule pile-on), #18 (last-day convergence), #37 (free, two rooms), #41 (research convergence, two rooms), #38 (charity, two rooms, 17 days), #51 (private roles; non-holdout part 07-06 → 09-07 only).
- **Other herding periods** (H11 herding beyond the ±30-min local shift): #19, #24, #25, #26, #30.
- **Contrast (own-artifact weeks, no herding in H11):** #39, #40, #42. Descriptive, with a weak prediction (P9).

Per-period folders go in `goalperiod-subhypotheses/G<NN>/`; the NE09 latency contrast goes in `goalperiod-subhypotheses/NE09/`.

## Observables
All per goal period, on the risk set above, 5-min bins.
- **O1 (primary): κ̂,** the coefficient on 1[≥ 1 visible link to X from another agent in the last 60 min], in the Poisson model with agent, project and day fixed effects *(Amendment 1; was project × day)* and all controls. Uncertainty: agent × day cluster-robust SE; null calibration by the link time-shift null N1.
- **O2: kernel.** Coefficients on E(0–15), E(15–60), E(60–240) (log1p counts).
- **O3: dose-response.** Hazard ratios for exactly 1 link, 2, 3+ links (one sender) and for ≥ 2 distinct senders, at fixed count. Simple vs complex contagion by day-blocked held-out log-likelihood: *simple* = log1p(count); *complex* = count plus 1[senders ≥ 2], or threshold 1[senders ≥ 2] only.
- **O4: rival terms.** (a) lead placebo coefficient κ_lead in the joint model and the contrast κ − κ_lead; (b) κ with the momentum control (Amendment 1; was project × day × quarter fixed effects); (c) other-room placebo κ_other vs same-room κ (#37, #38, #41; #39, #42 descriptive); (d) κ in the naive subset (first arrivals by agents that never touched X); (e) event-study pre-trend: arrival hazard of naive agents in the 60 min before vs after their first visible link to X, relative to matched project-day baseline.
- **O5: λ** (extra arrivals per link exposure) and **AF = R_link** (fraction of arrivals attributable to links), with day-bootstrap CIs. Also R_all: the attributable fraction of links plus occupancy coupling.
- **O6: occupancy coupling J** and whether it survives with links in the model.
- **O7: counterfactual.** Simulated peak 30-min occupancy of a single project (max over projects and windows) and distinct visitors of the period's top project, under link thinning f ∈ {1, 0.5, 0} and the cap rule; ratio to f = 1. Calibration: observed peak occupancy vs the f = 1 simulation interval (unfitted).
- **O8 (NE09): latency.** Excess arrival density of susceptible recipients vs time since link *posting* (0–240 min), relative to a time-shifted-link baseline; median excess lag, pre-NE09 (#18, #19, #20) vs post (#24, #25, #26, #30, #31).

## Null / baseline
- **N1 (primary for O1): link time-shift.** Shift every link's posting time by a uniform ±[30, 120] min within its own day's active window (same project, sender and room), recompute visibility and features, refit; 99 draws. Keeps each project's daily link count (and so the project × day field), destroys fine timing. z_shift = (κ̂ − mean)/sd.
- **N2: fields only.** κ = J = 0 (agent and project × day fields plus controls): held-out (day-blocked) log-likelihood.
- **N3 (common drive): lead placebo and momentum control** (O4a, O4b). Under pure common drive, future links predict arrivals as well as past ones, and recent arrivals by others absorb κ.
- **N4 (common drive, room placebo):** links in the other room share the project-time drive but are invisible.
- **N5 (homophily / own visits):** naive-only fits and the event-study pre-trend (O4d, O4e).
- **Known confounds:** (i) within-day project pulses (a human prompt, an announcement without a link) drive both links and arrivals; N3/N4 address them. (ii) Agents who *ask* for a link are already heading there (not captured if the question had no strict mention). (iii) Unlinked chat talk about X ("the time capsule") is not a link and partly loads on occupancy. (iv) Mentions are attention, not work (H11).

## Faithfulness scorecard
Scored per model, mapping and window; 0 = not done or failed, 1 = partial, 2 = passed. Scheme and promotion thresholds: `writeup/paper.tex`, Sec. "Assessing model faithfulness".
**Rival models:** (R1) **common drive**: project × time fields (kickoffs, prompts, the day's agenda) with κ = 0; (R2) **homophily / already heading**: agent-project affinity, plans and own prior visits; (R3) **work-observation coupling only** (J > 0, κ = 0): agents herd on where others are, links are a by-product; (R4) **complex contagion** (needs ≥ 2 distinct senders).
**Locked holdout used for confirmation:** none yet. Targets are #22, #28, #45 (`analysis/confirm_holdout.py`; rule frozen after round 1, not run). See the reuse disclosure under Prediction.

| Axis | Test | Score | Evidence |
| --- | --- | --- | --- |
| A mapping | variables defined from dataset fields; assumptions listed; invariant across families and regimes | 1 | Touches, links, call-start visibility, arrivals and the risk set all come from shared tables, with assumptions listed (Data scheme). The same mapping is used in regimes I and III. A mention is attention, not work. The call-start visibility rule is doubtful in regime I (H18) and is contradicted before NE09 (P8). |
| B assumptions | stationarity, Markov order, time-rescaling, update-order audit | 1 | **Audited:** the fixed-effects conditioning bias (Amendment 1); a 5-min bin attenuation of ≈ 0.8–0.9 (synthetic). **Not stationary:** the shift null mean varies from −0.76 to +1.61 across periods. **Time-rescaling:** the short-lag (15 min) variant gives the same lead ≥ lag picture (post hoc). **Not audited:** Markov order. |
| C adequacy | beats the null hierarchy, day-blocked held-out data | 1 | κ > 0 with cluster-robust p < 0.05 in 13/14 periods. It beats the link time-shift null (z ≥ 2) in 6/14 (3/11 herding periods), and in 0/14 on the shared window labels. On held-out quarters it beats the occupancy-only model in 5/14 periods. |
| D unfitted predictions | unfitted statistics and the model's signature | 1 | The simulator, fitted on hazards only, reproduces the observed peak single-project occupancy inside its 90% interval in 9/14 periods (#31: 11 vs [9, 11]). It under-predicts long periods (#38, #51). The model's signature, past links outweighing future links, fails (P2a). |
| E interventional | predicts the change across a natural experiment | 0 | The NE09 prediction failed: before chat reached computer-use calls, the link → switch excess was no slower; it was faster (median excess lag 2.5 vs 7.5 min, 95% vs 90% of the excess in the first 15 min). This holds for action-only switches too (post hoc). |
| F identifiability | synthetic recovery with village sampling; robust to preprocessing | 1 | **Synthetic (12 scenarios × 25 runs):** P1 fires in 0–4% of no-link worlds and 92–100% of contagion worlds; λ and R are recovered to ≈ 0.8× (indicator version). **Preprocessing:** the sign of κ survives action-only switches, the U⁺ universe and project × day effects. The shift-null verdict does **not** survive the shared window labels. The real data contain a structure absent from every synthetic world (lead > lag), so identification of direction fails on real data. |
| G ground truth | agrees with known structure | 1 | #31: the simulated pile-on size matches the time capsule (11 agents). Own-artifact weeks show a directed link → visit pattern, consistent with agents advertising their worlds. H27 independently finds links in the 30 min before 11/21 onsets (post hoc). Agent narration was not used. |
| H comparative | beats the named rivals | 1 | **R4** (complex contagion) is beaten: simple wins, and ≥ 2 senders add −0.24 ± 0.15. **R3** (occupancy only) is beaten on held-out quarters in 5/14. **R1** (common drive / co-bursts) is **not** beaten: lead ≥ lag in 10/11 herding periods; momentum control passed. **R2** (already heading) is **not** beaten: pre-trend 3.3× (P3b failed), although naive agents show the effect too (P3a). |
| I transfer | holds in other same-mode periods, including the holdout | 0 | No consistent per-period pattern (3/11 supported, I² = 0.67). The holdout is not run (frozen script: #22, #28, #45). |

## Prediction
*Written 2026-10-04 (UTC), before running the analysis on real data.*

**What I had seen when writing this:** H11's round-1 results (βJ, z_N2, local-shift z per period); H18's and H04's results; per-period counts of strict artifact mentions by source (chat / action / intention) and by speaker kind for the candidate periods (non-holdout only); room message counts per period; median turn gaps in #31 and #41 (10–13 s). I had **not** computed any arrival, exposure, hazard or timing statistic. Humans post almost no links (≤ 8 per period), so "links" means agent-posted links.

**Minimum data rule:** a period is *tested* if it has ≥ 30 arrivals in the risk set and ≥ 20 links to universe projects; otherwise its verdict is "n/a (insufficient)", reported descriptively.

| ID | Prediction | Counts against |
| --- | --- | --- |
| **P1 (primary)** | Per period: κ̂ > 0 with z_shift ≥ 2 **and** cluster-robust p < 0.05 → *supported*; right sign with one criterion → *weak*; otherwise *failed*. **Card level:** supported if ≥ 2/3 of tested candidate + herding periods are supported and the random-effects pooled κ > 0 at p < 0.01; failed if ≤ 1/3 supported. Expected e^κ ≈ 2–5. | κ̂ ≈ 0 or below the shift null in most periods |
| **P2 (common drive, R1)** | (a) In the joint lag + lead model, κ − κ_lead > 0 (one-sided p < 0.05) in a majority of P1-supported periods, and κ_lead < κ pooled. (b) ~~With project × day × quarter fields, κ̂ keeps ≥ 50% of its primary value in a majority.~~ *(Amendment 1)* With the momentum control, κ̂ keeps ≥ 50% of its primary value and p < 0.05 in a majority. (c) Room placebo (#37, #38, #41): κ_other < κ_same and κ_other's CI includes 0. | κ_lead ≈ κ; strict FE kills κ; κ_other ≈ κ_same |
| **P3 (homophily / own visits, R2)** | (a) κ > 0 holds in the naive subset (pooled p < 0.05). (b) Pre-trend: the naive agents' excess hazard in the 60 min *before* first visible exposure is < 1/2 of the excess in the 60 min after (pooled). | Effect only in returns; pre-trend ≥ post |
| **P4 (dose-response, R4)** | Simple contagion: a single link from a single sender carries most of the effect (pooled HR(1 link) > 1, p < 0.05); the ≥ 2-senders term adds < 50% of the single-link log-HR and its pooled CI includes 0; the complex model wins held-out likelihood in < half of tested periods. | Senders ≥ 2 term dominates; 1-link HR ≈ 1 |
| **P5 (infection rate)** | λ ∈ [0.01, 0.15] extra arrivals per link exposure in most P1-supported periods; pooled median ≈ 0.04. | λ > 0.3 or ≈ 0 |
| **P6 (branching)** | R_link < 0.5 in every tested period; median 0.1–0.3. Link cascades are subcritical; pile-ons need drive or occupancy. | R_link ≥ 1 anywhere |
| **P7 (counterfactual)** | Removing all links (f = 0) lowers the simulated peak single-project occupancy by 10–30% (median over tested periods); f = 0.5 by < 15%; no period's pile-on disappears (peak stays ≥ 50% of f = 1). The f = 1 simulation contains the observed peak occupancy in its 90% interval in ≥ 2/3 of tested periods (unfitted check). | Peak falls > 50%, or < 5% everywhere; f = 1 misses observed peaks in most periods |
| **P8 (NE09, axis E)** | Median excess lag from link posting to induced arrival is shorter after NE09 (#24–#31) than before (#18–#20). Confounded with period and goal; descriptive-level evidence only. | Pre-NE09 latency ≤ post |
| **P9 (own-artifact contrast)** | In #39, #40, #42, λ is below the median λ of the shared-artifact periods. | λ in own-artifact weeks ≥ shared median |
| **P10 (occupancy, R3)** | J > 0 in most tested periods and survives with link terms in the model; links do not explain away occupancy herding (J drops by < 50% when E is added). | J ≈ 0 once E is in |

**Credences** (mine, before running): P1 card-level supported 0.55 (links→visits is natural, but per-period power at village sampling is unknown until the synthetic run); P2a 0.45 (conversation clustering makes leads positive too); P2b 0.5; P2c 0.4 (cross-room projects may barely overlap → low power); P3a 0.6; P3b 0.5; P4 0.65; P5 0.5; P6 0.8; P7 0.35; P8 0.4; P9 0.4; P10 0.7.

**Amendment 1** (2026-10-04, after a synthetic pilot only (S0–S3, 10 runs each, `analysis/synthetic.py`), before any real-data fit; predictions P1–P10 otherwise unchanged):
- **Primary fixed effects: agent + project + day** (was agent + project × day). With ≈ 2 arrivals per project-day group, project × day effects plus regressors that depend on earlier outcomes (links, occupancy) bias κ̂ negative under the null (mean −0.22), and the shifted-link κ even more (−0.49). So z_shift fired in 3/10 null runs (2/10 under drive, 4/10 under occupancy coupling). Agent + project + day gives κ̂ = −0.01 ± 0.18 under the null, 0/10 false positives by either criterion, and detects κ = ln 3 in 10/10 runs by the cluster-robust test (7/10 by z_shift; κ̂ attenuated to ≈ 0.8). Day-level project popularity, which project × day absorbed, is now handled by the link time-shift null, which keeps every link in its own day. Project × day effects are kept as a descriptive variant.
- **P2b replaced.** Project × day × quarter effects have the same bias, worse. New P2b: κ keeps ≥ 50% of its value and p < 0.05 when a **momentum** control is added (log 1 + arrivals at X by other agents in the last 30 min, a within-day common-drive proxy).
- **P10 bracket.** Under agent + project + day, J is biased upward under the null (+0.36, day-level popularity); under project × day it is biased downward. P10 now needs J > 0 under both.
- **New synthetic scenarios** (hardest confounds): S9 long, slow drive pulses; S10/S11 **announcement links** (a link marks a drive onset but causes nothing; 1 and 2 rooms).

**Calibration notes from the synthetic validation** (appended 2026-10-04 after the full synthetic run, 12 scenarios × 25 runs, 24 shifts each, and a 12-run check of λ/R variants; before any real-data run; rules above unchanged except where marked). Village sampling: N = 12–14, 15 projects, 5 days × 4 h, 200–470 arrivals and 190–470 links per run (real periods: 68–710 arrivals, 45–816 links; #51 ≈ 6,900 / 7,400).
- **P1 is well calibrated.** False "supported" calls: 4% under the null, 0% under drive pulses (45 min or 120 min), occupancy coupling and own-revisit homophily, 0–4% under announcement links (1 and 2 rooms) and with two rooms. **Power:** 92% (κ = ln 3, one room), 100% (two rooms), 52% with contagion plus drive pulses (the shift null rises), 8% under pure complex contagion. κ̂ is attenuated to ≈ 0.8–0.9 of the true κ (5-min bins miss same-bin responses).
- **P2a has low power under true contagion.** Under real cascades, links cluster in time and the lead term is positive too (median κ_lead ≈ 0.55 when κ = ln 3, ≈ 0.4 under pure drive). κ − κ_lead was significant in only 28% (one room) and 56% (two rooms) of contagion runs, and in 0% of no-link runs. **So a P2a pass is strong evidence; a P2a fail is weak evidence against.**
- **P2b (momentum)** never removes a true effect (κ ratio ≈ 1.0, still significant in 100% of contagion runs) and adds no false positives.
- **P2c (other-room placebo) works:** κ_other ≈ −0.09 with true contagion (significant in 8%), −0.10 under drive (16%).
- **P3b is a homophily test only.** The fields-only baseline shows a post-exposure excess under occupancy coupling as well (pre 1.04 / post 1.56) as under contagion (0.93 / 1.75). An occupancy-aware baseline was tried and is not informative. Own-revisit homophily correctly fails it (1.11 / 0.98).
- **P4 discriminates.** Under complex contagion the ≥ 2-senders term dominates (median 1.58 vs 0.14 for one link) and the complex model wins held-out likelihood in 25/25 runs; under simple contagion the complex model wins 6/25 (null 5/25).
- **λ and R_link: Amendment 2.** Use the 60-min indicator only (E60) for the attributable count. It recovers ≈ 80% of the true λ and R (λ 0.053 vs 0.070; R 0.41 vs 0.49) with a null floor ≈ 0 (median 0.00 under occupancy and revisits, 0.07 in a 12-run null sample). Adding the 60–240 min term recovers ≈ 90% but adds a null floor of 0.09–0.14, so it is reported only as an upper variant. Read real R_link as ≈ 0.8 × truth ± 0.07.
- **P10 bracket confirmed:** J is biased up by ≈ 0.3–0.4 under agent + project + day (null J 0.36; true J 0.8 estimated 1.11) and down under project × day (null −0.57).
- **P7 counterfactual is rough (± 0.1).** Removing links: estimated peak-occupancy ratio 0.84 vs true 0.74 (contagion only: the simulator under-states the effect); 1.03 vs 0.99 (drive only); **0.84 vs 0.96 (contagion + drive: it over-states the effect)**. The f = 1 simulation under-predicts the peak by ≈ 20% when within-day drive pulses are present (calibration ratio 0.80), since pulses are not in the simulator's project × day fields. P7 thresholds stay as written; the error bar is read as ± 0.1.
- **Held-out likelihood (axis C) has low power:** the link model beat the occupancy-only model on held-out quarters in 52% of one-room and 96% of two-room contagion runs (24% under the null).

**Holdout confirmation targets** (chosen now from `holdout.json`, rule to be frozen after round 1): **#22** (free week, regime I, pre-NE09), **#28** (quiz build and promote, C, regime I, post-NE09), **#45** (follow your leader, C, regime III, two rooms: room placebo available). Reuse disclosure: H11's frozen confirmatory test targets the same three periods (equal-time co-occupancy βJ of project labels; not yet run); H02 ran #45 on 1-min activity timing; H23 will reuse #45 for message style. H28's observable (lagged link-exposure → arrival hazard and its timing nulls) is a different statistic; if H28 runs after H11 on these periods, the reuse policy in `../holdout.md` applies (committed predictions and script, different unexamined statistic, disclosure in both cards and `LOG.md`).

## Results by goal period
All periods were run on 2026-10-04, non-holdout days only, after the card and each `G<NN>/README.md` prediction were written. Columns:
- **κ:** coefficient on a visible link to X in the last 60 min (e^κ is the hazard ratio), with its cluster-robust SE and the z against the link time-shift null.
- **κ_lead:** coefficient on links arriving in the *next* 60 min (joint model).
- **λ:** extra switches per link exposure; **R_link:** share of switches attributable to links. Both are upper bounds, see Results.
- **f = 0:** simulated peak single-project occupancy with no links, relative to links as observed.

Verdict labels: weak = P1 right sign with one of its two criteria (folder verdict "mixed").

| Period | Role | Verdict (P1) | κ ± se (z_shift) | κ_lead | λ | R_link | f = 0 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| [G18](goalperiod-subhypotheses/G18/README.md) | named, pre-NE09 | failed | +0.28 ± 0.34 (−6.1) | +3.76 | 0.012 | 0.06 | ×0.94 |
| [G31](goalperiod-subhypotheses/G31/README.md) | named | weak | +0.47 ± 0.14 (+0.8) | +1.15 | 0.036 | 0.13 | ×0.92 |
| [G37](goalperiod-subhypotheses/G37/README.md) | named, 2 rooms | weak | +1.54 ± 0.32 (+1.8) | +1.30 | 0.068 | 0.14 | ×0.75 |
| [G38](goalperiod-subhypotheses/G38/README.md) | named, 2 rooms | weak | +0.72 ± 0.22 (−0.7) | +1.68 | 0.025 | 0.10 | ×0.94 |
| [G41](goalperiod-subhypotheses/G41/README.md) | named, 2 rooms | weak | +0.82 ± 0.23 (−0.9) | +1.80 | 0.020 | 0.18 | ×0.77 |
| [G51](goalperiod-subhypotheses/G51/README.md) | named (non-holdout part) | supported | +0.58 ± 0.05 (+4.8) | +0.76 | 0.006 | 0.14 | ×0.73 |
| [G19](goalperiod-subhypotheses/G19/README.md) | herding, pre-NE09 | weak | +0.66 ± 0.32 (−0.8) | +1.96 | 0.048 | 0.19 | ×0.83 |
| [G24](goalperiod-subhypotheses/G24/README.md) | herding | supported | +2.90 ± 0.63 (+5.1) | +1.71 | 0.110 | 0.44 | ×0.48 |
| [G25](goalperiod-subhypotheses/G25/README.md) | herding | weak | +1.15 ± 0.43 (−0.0) | +2.77 | 0.029 | 0.33 | ×0.61 |
| [G26](goalperiod-subhypotheses/G26/README.md) | herding | weak | +1.09 ± 0.43 (+0.4) | +2.33 | 0.053 | 0.21 | ×0.68 |
| [G30](goalperiod-subhypotheses/G30/README.md) | herding | supported | +0.98 ± 0.23 (+3.7) | +1.14 | 0.086 | 0.25 | ×0.90 |
| [G39](goalperiod-subhypotheses/G39/README.md) | own-artifact contrast | supported | +1.19 ± 0.20 (+3.9) | +0.12 | 0.019 | 0.30 | ×0.77 |
| [G40](goalperiod-subhypotheses/G40/README.md) | own-artifact contrast | supported | +0.74 ± 0.31 (+6.0) | +0.11 | 0.012 | 0.15 | ×0.82 |
| [G42](goalperiod-subhypotheses/G42/README.md) | own-artifact contrast | supported | +0.97 ± 0.32 (+2.0) | +0.46 | 0.014 | 0.09 | ×1.00 |
| [NE09](goalperiod-subhypotheses/NE09/README.md) | spanning (latency) | failed | pre-NE09 response no slower (2.5 vs 7.5 min) | | | | |

## Results
*Exploratory round 1, 2026-10-04.*
- **Code:** `scheme/build.py`, `analysis/h28core.py`, `analysis/synthetic.py`, `analysis/explore.py`, `analysis/assemble.py`, `analysis/period_folders.py`, `analysis/figures.py`; post hoc: `analysis/posthoc.py`, `analysis/robust_shared_labels.py`; frozen confirmatory test: `analysis/confirm_holdout.py`.
- **Data:** `data/processed/H28-links-spread-herding/` (`G<NN>/round1.json`, `results_round1.parquet`, `cross_period_round1.json`, `synthetic/`, `posthoc_round1.json`, `robust_shared_labels.json`, `confirm_dryrun.json`).

**Outcome vs prediction** (11 tested herding periods: 6 named + 5 H11-herding; the 3 own-artifact weeks are the contrast)

| Prediction | Outcome | Verdict |
| --- | --- | --- |
| P1 κ > 0, p < .05, z_shift ≥ 2 (primary) | Supported in 3/11 (#24, #30, #51), weak in 7, failed in 1 (#18). Pooled κ = +0.83 ± 0.12 (e^κ 2.30, p 2e−12; I² 0.67). p < 0.05 in 10/11, but the link time-shift null is itself high (mean −0.76 to +1.61): links moved ±30–120 min predict switches almost as well | **Failed** (card rule: ≤ 1/3 supported) |
| P2a κ − κ_lead > 0 | 0/3 supported periods; κ_lead > κ in 10/11 herding periods; pooled κ − κ_lead = −1.17 ± 0.30. In synthetic worlds (post hoc tally), lead > lag occurs in only 8–16% of pure-contagion runs, but in 64% with contagion + drive and 88–100% in drive, occupancy, revisit and announcement worlds | **Failed, significantly the wrong way** |
| P2b momentum control keeps κ | 3/3; pooled κ with momentum +0.82 | Supported |
| P2c other-room placebo ≈ 0 | #37, #38, #41: κ_other −1.3 to −2.8, significant but on 2–3 switches. The rooms work on different projects, so other-room links mark projects agents avoid. That rules out cross-room drive but says nothing about within-room drive. #51: κ_other −0.05 ± 0.20 (clean) | **Failed** as written (uninformative) |
| P3a effect in naive agents | Pooled κ_naive +1.31 ± 0.23 | Supported |
| P3b pre-trend < ½ post excess | Pooled O/E 3.28 before first exposure vs 4.66 after; passes only in #24, #30, #31 (and contrasts #39, #40) | **Failed** |
| P4 simple contagion | 1-link HR e^0.82 = 2.3; ≥ 2 senders beyond count −0.24 ± 0.15; the complex model wins held-out likelihood in 2/11 | Supported |
| P5 λ ∈ [0.01, 0.15] | 2/3 supported periods in range (#51 0.006); median over tested herding periods 0.036 (predicted ≈ 0.04) | Supported (loosely) |
| P6 R_link < 0.5 | All periods; median 0.18, max 0.44 (#24) | Supported |
| P7 f = 0 lowers peaks 10–30%; f = 0.5 < 15%; none < 50%; calibration ≥ 2/3 | f = 0 median ×0.79; f = 0.5 ×0.94; cap ×0.96; #24 falls to ×0.48; observed peak inside the f = 1 interval in 9/14 | **Mixed** (two clauses fail; effects are upper bounds) |
| P8 NE09 latency shorter after | Pre-NE09 median excess lag 2.5 min vs 7.5 after; 95% vs 90% of the excess within 15 min | **Failed** |
| P9 own-artifact λ below the shared median | 0.019, 0.012, 0.014 vs 0.036 | Supported |
| P10 J > 0 under both FE | 3/11 | **Failed** (occupancy coupling is not robust to the FE bracket) |

**Synthesis**
1. **Links co-move with switches but do not lead them in herding weeks.** Three facts:
   - A visible link to X raises the switch hazard to X about 2.3× (pooled), and the excess is fast: a 0–15 min kernel term of +0.76, with 90–95% of the post-link excess within 15 min.
   - **Future links predict switches more strongly than past ones** in 10/11 herding periods (pooled κ_lead 1.83 vs κ 0.83).
   - Naive agents already switch to X at 3.3× baseline in the hour before their first exposure.

   The 60-min effect beats a ±30–120 min shift of the links in only #24, #30 and #51. Reading: links, chat about X and work on X are parts of one **attention burst**. Agents announce, link and pile on together; the link is a marker of the burst more than its cause. This matches H18 (mentions mark ongoing exchanges) and H04 (responses are context-mediated).
2. **Directed recruitment exists where herding does not.** In the own-artifact weeks (#39, #40, #42), links lead visits: κ − κ_lead +1.01 (p 0.002), +0.62 and +0.40, with small pre-trends in #39 and #40 (not #42). Agents advertising their own worlds bring visits. Each exposure recruits few (λ 0.012–0.019), and no pile-on forms.
3. **Infection rate and branching (upper bounds).**
   - λ = 0.006–0.11 extra switches per link exposure (median 0.036). Each posted link recruits λ·k_s ≈ 0.04–0.67 extra agents (median ≈ 0.14).
   - R_link = 0.06–0.44 (median 0.18; synthetic says ≈ 0.8× truth when the model holds). Link-driven cascades are subcritical everywhere.
   - Because of fact 1 these are attributable associations, not causal rates.
4. **Counterfactual.** The fitted simulator, with links removed, lowers peak single-project occupancy to ×0.79 (median; range ×0.48–×1.00). Halving links gives ×0.94; capping at one link per project per room per 2 h gives ×0.96. These are **upper bounds**: the synthetic contagion + drive world showed the simulator overstating the effect (0.84 vs a true 0.96), and the lead result says most of the link coefficient is co-burst. Throttling link-sharing would not stop pile-ons; at best it trims their peak by a few agents.
5. **No interventional support** (NE09). Before chat reached computer-use calls, the co-timing was as fast or faster, also for action-only switches (post hoc). Co-timing therefore does not need agents to read links during computer use.
6. **Heterogeneity.** No regime split: regime I and III herding periods both show lead ≥ lag. Two-room periods add nothing: other-room projects are avoided. #51 (32 agents, 7,400 links) is the cleanest supported period, with a tiny λ (0.006) because each link reaches ≈ 21 susceptible agents.

**Post hoc (after the round-1 run; labelled throughout)**
- **Short-lag check** (`analysis/posthoc.py`). A visible link in the last 15 min beats the shift null in 10/14 periods (z up to +10.8). But a link arriving in the next 15 min predicts the switch more strongly in 9/11 herding periods (pooled lag − lead −1.02 ± 0.26). In the contrast weeks lag beats lead (+0.36 pooled; #40 p = 0.008). Same picture as at 60 min: tight two-sided co-timing, direction only in own-artifact weeks.
- **Robustness on the shared deterministic labels** (coordinator request; `analysis/robust_shared_labels.py`, `project_states.parquet`, 30-min window switches). Herding periods: pooled κ +0.91 ± 0.26 (p 5e−4; κ > 0 and p < 0.05 in 6/11), but z_shift ≥ 2 in **0/11** (0/3 contrasts). **Both numbers:** touch-based arrivals give pooled κ +0.83 ± 0.12 with 3/11 beating the shift null; shared window labels give +0.91 ± 0.26 with 0/11. The headline (an association that fails the timing nulls) holds on either label set. The deterministic labels fix H11's tie-breaking only; H28's primary arrivals never used H11's `modal()`.
- **H27 cross-reference.** H27 found 11/21 herding onsets preceded within 30 min by a chat link to the project (OR 11.6). H28's model handles H27's "a link labels its poster" artifact by construction:
  - the poster's own link counts as the poster's arrival, never as its exposure;
  - κ is estimated on recipients only;
  - recipients must be off X when the link becomes visible.

  H28 confirms that recipients switch around links. It also shows they switch about as much just *before* links appear, so H27's precursor association is consistent with announcement-marked bursts and does not by itself show that links trigger onsets.

**Figures:**
- [`figures/H28_round1_summary.pdf`](figures/H28_round1_summary.pdf) (one page);
- [`figures/periods_forest.pdf`](figures/periods_forest.pdf);
- [`figures/kernel_dose.pdf`](figures/kernel_dose.pdf);
- [`figures/counterfactual.pdf`](figures/counterfactual.pdf);
- [`figures/latency_ne09.pdf`](figures/latency_ne09.pdf);
- [`figures/synthetic_validation.pdf`](figures/synthetic_validation.pdf);
- [`figures/summary_obs.pdf`](figures/summary_obs.pdf) (summary page).

**Confirmatory prediction (frozen 2026-10-04 after round 1, before any holdout data was read)**, `analysis/confirm_holdout.py`. Targets: #22 (F, regime I, pre-NE09), #28 (C, regime I), #45 (C, regime III, two rooms). Same pipeline, 99 shifts.
- **Original claim:** C1 (P1 rule) in ≥ 2/3 targets plus C2 (lead contrast), C3 (room placebo, #45) and C4 (R_link < 0.5). REFUTED if C1 fails in ≥ 2/3.
- **Round-1 pattern:** R1 κ > 0 at p < 0.05 in ≥ 2/3; R2 κ_lead ≥ κ in ≥ 2/3; R3 R_link ∈ [0.05, 0.45] everywhere.
- **Round 1 predicts:** claim REFUTED or INCONCLUSIVE; pattern HOLDS.
- **Dry run on stand-ins** (#31, #30, #41): claim REFUTED, pattern HOLDS.
- The script refuses `--confirm` unless it, `h28core.py`, `scheme/build.py` and this card are committed and unmodified (reuse policy). Running it needs Vivian's sign-off.

**Caveats**
- **Attention, not work.** Touches are strict artifact mentions; reading a repo counts.
- **Visibility rule.** Call-start visibility is doubtful in regime I (H18) and is contradicted before NE09 (P8). If agents saw chat through unlogged calls, exposure timing is mismeasured there.
- **λ and R_link are attributable associations.** Given the lead result, they bound the causal link effect from above. Synthetic recovery (≈ 0.8×) applies only if the model is right.
- **Counterfactual.** The simulator keeps activity, rooms, plans and the project × day drive as observed. Its error is ± 0.1 (synthetic), and it under-predicts peaks in long periods (#38, #51 outside the interval).
- **Rooms.** The other-room placebo turned out uninformative because the rooms work on different projects.
- **Multiplicity.**
  - 14 periods × about 12 statistics.
  - The pooled lead > lag (p ≈ 1e−4) and pooled κ (p ≈ 2e−12) survive any correction.
  - Per-period z_shift calls near 2 (#42 at +2.0, #37 at +1.8) do not.
  - #24 rests on 68 switches and 45 links.
- **Power.** Synthetic P1 power is 92% at κ = ln 3, but only 52% with drive pulses. The P2a fail would be weak evidence by itself; it is strong here only because it is significantly *reversed*. Post hoc synthetic tally: lead > lag appears in 8–16% of pure-contagion runs vs 88–100% of no-link worlds, so 10/11 real herding periods with lead > lag is far more typical of drive, occupancy or announcement worlds (or contagion mixed with drive, 64%).
- **Amendments,** with what I had seen when making them:
  1. FE agent + project + day and the momentum control replacing P2b. Made after the synthetic pilot only.
  2. λ and R_link from the 60-min indicator only. Made after the full synthetic run, before any real-data fit.
  3. Event-study baseline kept as fields-only (synthetic check).
  4. **Post hoc:** the short-lag check, the shared-label robustness and the H27 cross-reference, all after the round-1 run.

  A smoke test on #24 (3 shifts, 3 simulations) ran just before the full run, after all predictions were written; it was overwritten by the full run.

**Operator-facing rule.** Watch, don't throttle. From your logs, compute for each project:
- the switch hazard after a visible link vs before it (lag vs lead);
- R_link, the share of switches attributable to links.

If future links predict switches as well as past links do (lead ≥ lag), links are riding an attention burst. Throttling link-sharing then buys at most ~5–20% lower peak pile-ons (village: ×0.79 at most). To prevent duplicated work, act on the burst itself, e.g. assign ownership: H11's own-artifact weeks did not herd. Only where lag clearly exceeds lead do links work as directed recruitment, at ≈ 0.01–0.1 extra visits per exposure and ≈ 0.1–0.2 per posted link. Example: agents advertising their own artifacts.

**Next steps**
1. Run the frozen holdout test after sign-off.
2. A burst-level model: treat project attention episodes as the unit and ask what starts them (a human message, a kickoff, an agent announcement, a repo event). This is the R1 rival made explicit, jointly with H27's onsets.
3. Use `kicks_classified.parquet` to split exposures by sender type (nudges, human, agent announcements) and by addressed vs broadcast links: addressed links add +0.60 ± 0.16 (pooled).
4. Read the text of link messages (gated; Phase 2) to separate announcements ("I made X") from requests ("please review X"); the two predict opposite lead/lag patterns.
5. Re-check regime-I visibility (H18, H08), since P8 suggests chat may reach agents through unlogged turns.

## Notes
- **From H53 (2026-10-04):** at a project's *first* chat link adoptions jump ×22.5 (18 before vs 592 after for brand-new projects; ×3.8 for carried-over ones), with only 1.5% of adopters lacking the link in context. H28's lead > lag pattern applies to projects already known; first links are real seeds.
- 2026-10-04: promoted from HH114 by Vivian (usefulness-first batch); wave 1.
- 2026-10-04: card written (model variant, scheme, observables, nulls, predictions P1–P10) before any real-data run.
- 2026-10-04: Amendment 1 (FE, momentum) after the synthetic pilot; calibration notes and Amendment 2 (λ/R from E60) after the full synthetic run; both before any real-data fit.
- 2026-10-04: round 1 run on 14 periods (non-holdout days), then post hoc checks; the confirmatory rule was frozen and dry-run on stand-ins. The session was interrupted after all period outputs were written; nothing needed rerunning.
