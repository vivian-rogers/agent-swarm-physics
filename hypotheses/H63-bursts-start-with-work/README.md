# H63: Herding bursts start with a work signal

**Status:** exploratory round 1 done (2026-10-04; non-holdout only). **Failed as posed: herding bursts do not start with a work signal; chat links come first.**
- **State changes rarely precede bursts.** A deploy-type state change on the project falls in the 60 min before the follower onset for 7/317 herding bursts (2.2%), against 100/5,470 matched 1–2-agent clusters (1.8%). Pooled OR_S = 1.53 [0.77, 3.05]; the signal time-shift null gives z = −0.23.
- **Links precede most bursts:** 190/317 (60%) vs 12% of controls, OR_L = 11.9 [9.2, 15.3]. Among the 11 bursts with both, the state change came first in 3.
- **No work lead in the arrival hazard:** h_S − h_S′ = +0.15 [−0.08, 0.37] (11 periods). In the trimmed window links *lead* arrivals (κ − κ′ = +0.30 [0.04, 0.57]); untrimmed it is −0.10 [−0.40, 0.20], so day-edge co-bursts push toward H28's lead ≥ lag.
- **Natives:** G31's time-capsule wave starts before any state change or link (failed); in G39's own-world week visitors arrive a median 4.9 min before the first deploy (failed); the G40 kickoff control behaves as predicted (supported).
- Scorecard A1 B1 C0 D0 E0 F1 G1 H0 I0. `confirm.py` frozen, guarded and dry-run; **not run**.
**Research question (GOALS.md):** **Q2** (what is field and what is coupling): is the trigger of a herding burst an artifact field step (the project becomes usable) or the chat coupling (links)? Q1 is the secondary question (links as coupling).
**Fields:** stat mech, sociophysics, dynamics
**Literature:** none in `literature/` covers trigger attribution directly; the nearest is `literature/pinero-2025-neutral-theory-cooperative-dynamics.md` (frequency-dependent joining). Classical background named, not filed: Bass diffusion (innovation field vs imitation), event-study lead–lag designs.
**Definitions used** (`physics-models/DEFINITIONS.md`): Agent; Population N(t); Regime; Driving / external field; **Contagion / adoption event, variant arrival (project switch-in)** and **Interaction (link exposure)** (H28 named variants; visibility by posting time and room, see Data scheme); **Agent state (categorical, on-project multi-label)** (H28); H11's strict touch rule. **New named variants proposed for DEFINITIONS.md** (not edited here), defined under Data scheme: *work signal (state change, DQ4)*, *herding burst (H63, arrival cluster)*, *follower onset*.
**From:** HH263 in `hypotheses/hypohypotheses/HYPOHYPOTHESES.md` ("Making the faithful ones better") · **Models:** `physics-models/10-potts/`, `physics-models/03-contagion/`
**Data inputs (shared tables first):** DQ4 `work_commits` (agent work filter), `artifact_mentions` + `artifacts` (strict touches, chat links, deploy commands; project map from `infra/shared/project_states.py: project_map`), `call_windows` (activity, spans, all-present window), `kicks_classified` (kickoffs, human messages), `context_ledger_turns` (recipient room), `calendar`, `period_units`. Cross-reference only: H27/H28/H53 published numbers.

## Question
Do herding bursts start at a visible artifact state change (first deploy, first working build or site, a commit that makes a project usable), with chat links following rather than leading?

**Why it should.** H28 found that links mark attention bursts rather than start them: future links predict switches better than past ones (pooled κ − κ_lead −1.04 ± 0.24), and recipients switch at 6.5× baseline in the ~17 s before they can read a link. H53 found that a project's *first* link seeds adoption (×22.5), and H27 found work onsets coincide with attention onsets. Something starts the burst. HH263's candidate: a visible change in the artifact (a site goes live, a deploy), with the poster's link following.

## Design: two layers (Vivian, 2026-10-04; see `infra/data-quality/QUEUE.md`)
- **Replication (layer 1):** the common estimators (burst-level precedence and the arrival-hazard lead–lag model) on every eligible non-holdout period: ≥ 30 agent work commits (DQ4 default filter) and ≥ 3 herding bursts. Git is dense only from #30 (DQ4), so periods #2–#27 are not eligible (a zero work signal there is ambiguous). Role `replication`.
- **Period-native tests (layer 2), each with its own dated prediction in its folder:**
  - **G31** (free week; the field-free time-capsule wave in dense git): does the largest wave start with a state change, with its first link after it?
  - **G39** (15 own worlds, each deployed and advertised by its builder; H28 found links lead visits here): the cleanest test of a work → link → visit chain.
  - **G40** (the hub set by the goal at the kickoff): the negative control. Herding there is field-frozen, so it should start before any state change.
- **Faithfulness lever (HH263):** H (a rival trigger tested against links) and G (DQ4 commits as ground-truth work events). The scorecard says whether each was raised.

## Model
**From:** `physics-models/10-potts` (kinetic Potts with project fields) and `physics-models/03-contagion` (Bass: innovation field vs imitation).

**H63 variant: kinetic Potts with an artifact field step.** Agent i, off project X, switches onto X in 5-min bin b at rate

  log μ_iXb = α_i + π_X + δ_d + h_S·S_Xb + h_S'·S'_Xb + h_R·R_Xb + h_R'·R'_Xb + κ·L_iXb + κ'·L'_iXb + ζ·K_ib

- S_Xb = 1 if a **state-change work signal** on X (by another agent) happened in the last 60 min; S'_Xb = 1 if one happens in the next 60 min (lead term).
- R_Xb, R'_Xb: the same for **routine commits** on X (placebo commits: agent work commits that are not state changes).
- L_iXb = 1 if another agent posted a chat link to X in i's room in the last 60 min; L'_iXb in the next 60 min (H28's lead–lag).
- α_i, π_X, δ_d: agent, project and day fields (H28 Amendment 1). K_ib: kickoff in the last 60 min, human message in i's room in the last 30 min, nudge to i in the last 30 min.

A **field step** at the state change (H63) predicts h_S > h_S' (the signal leads arrivals) and h_S > h_R (state changes, not any commit). A **co-burst** (attention burst emits commits, deploys and links; H28's reading) predicts h_S' ≥ h_S and κ' ≥ κ. **Link-led nucleation** (H53) predicts κ > κ' and h_S' ≥ h_S (the link precedes the work).

## Data scheme (`scheme/`)
- **Project:** `project_states.project_map()` (file → parent repo; site → parent repo when known). A project **exists** from its first strict mention or first commit; bins before that are not at risk.
- **Touch (H11 strict rule):** `artifact_mentions` with `speaker_kind = agent`, `how ∈ {url, output, bare}`, source action or chat; one per (agent, source, turn/message, project).
- **Arrival (H28):** agent i's first touch of X after ≥ 60 min without one, on the same PT day. **Primary (scheduler impostor):** an arrival counts only if it lies inside the day's all-present window (DQ8) and ≥ 30 min after the agent's first call of the day; the untrimmed variant keeps all.
- **Work signal (state change, DQ4; proposed named variant):** on X, from agent work commits (`canonical & ~imported & author_kind == agent & ~automated`) and deploy commands:
  - *deploy event* = a commit on a pages branch or with a deploy message, or an action with verb `deploy` that strictly mentions X;
  - **S (state change, primary):** X's first deploy event in the dataset ("goes live"), and any later deploy event ≥ 60 min after X's previous deploy event ("new version live");
  - **B (birth):** X's first agent work commit. Reported descriptively only: no one can arrive before a project exists, so births lead arrivals mechanically;
  - **R (routine, placebo commits):** every other agent work commit on X.
  - Each signal has an author; the author is excluded from the risk set of X in the 60 min after its own signal.
- **Link:** an agent chat message with a strict mention (`source = chat`, `how ∈ {url, bare}`) of X. Recipients = agents whose room (`context_ledger_turns.room` of their latest call) is the link's room. The poster's own link counts as the poster's touch, never as its exposure. (Visibility by posting time: the ledger delay, median 17 s, is far below the 5-min bin.)
- **Herding burst (H63, arrival cluster; proposed named variant):** arrivals onto X linked by gaps ≤ 20 min; a burst has ≥ 3 distinct agents and ≥ 60 min without an arrival onto X before its first arrival. **Onset** t₀ = the first arrival; **follower onset** t_f = the second distinct agent's arrival; end = the last arrival. Primary: t_f in the trimmed window (all-present, ≥ 30 min after the day's first call).
- **Matched non-burst arrivals (the burst-level control):** clusters on the same projects with 1–2 distinct agents, same window rules; their "follower onset" is their last arrival.
- **Exogenous flags:** a burst is *kickoff-led* if t₀ is within 60 min of a goal kickoff (`kicks_classified` goal_kickoff, or the first window start of a goal's first day), *human-led* if a human chat link to X precedes t_f within 60 min.
- **Output:** `data/processed/H63-bursts-start-with-work/G<NN>/` (`touches`, `arrivals`, `signals`, `links`, `bins`, `bursts` parquet; codes only, no text), `results/`, `synthetic/`, `_provenance.json`. Budget ≤ 100 MB.
- **Regimes covered:** I (#30, #31, #33), II (#35, #36a), III (#36b on). Fits are within period.

## Observables
1. **Burst-level precedence (primary).** For each herding burst: whether an S signal on X falls in [t_f − 60 min, t_f); the same for links, routine commits and births. **OR_S** = odds of a preceding S signal for bursts vs matched non-burst arrivals (Mantel–Haenszel across periods; per period where ≥ 5 bursts). Same for links (OR_L) and routine commits (OR_R).
2. **Ordering.** Among bursts with both an S signal and a link in [t₀ − 60 min, end], the share where the first S signal precedes the first link (sign test against 0.5).
3. **Arrival-hazard lead–lag** (model above): h_S − h_S', κ − κ', h_S − h_R, per period with cluster-robust (agent × day) SEs; random-effects pooling.
4. **Link coefficient with and without the work terms:** the share of κ removed when S and R enter.
5. **Work blind window:** arrival excess of non-authors in (t_S, first chat mention of X after t_S] vs the following 60 min (does the work signal act before anyone announces it?). Descriptive.
6. **Exogenous shares:** kickoff-led and human-led bursts.

## Null / baseline
- **Matched non-burst arrivals** (observable 1): does a state change predict that an arrival grows into a herd?
- **Placebo commits** (routine R signals): the same lead–lag and OR statistics for commits that change nothing visible.
- **Signal time-shift null:** S times shifted by ±U(30, 120) min within the same day window (same project), 99 draws; z for OR_S and h_S − h_S'.
- **Lead terms** (S', L'): a common burst predicts arrivals from both sides.
- **Synthetic worlds** (axis F, before real data) at real counts: work-led (field step at S), marker/co-burst (a latent attention pulse emits arrivals, commits, deploys and links), link-led, and null.

## Impostors (STANDARDS §1)
| Impostor | How H63 removes it | Residual risk |
| --- | --- | --- |
| **Scheduler field** | Arrivals, bursts and signals counted only inside the DQ8 all-present window and ≥ 30 min after the agent's first call of the day (agents' first touches of the day are not arrivals); day fixed effects; the risk set is the agent's active 5-min bins (≥ 1 call). Untrimmed variant reported. | Within-day work rhythms (lunch-hour-like pauses) are not modelled |
| **Exogenous field** (kickoff, goal, operator) | Kickoff, human-message and nudge pulses in the hazard; kickoff-led and human-led bursts flagged and reported with and without them; G40 is the field-led control. | A human request to deploy that also pulls agents (rare; flagged when it carries a link) |
| **Shared model priors** | Agent fields α_i; projects are within-period; no family-level claim is made. | Same-family agents choosing the same project for prior reasons |
| **Contemporaneous convergence** | Lead terms (S', L'), matched non-burst arrivals, placebo commits, the time-shift null and the work blind window. | A burst that starts and emits a deploy in the same 5 min (resolution limit) |

## Faithfulness scorecard
Scored per model, mapping and window; 0 = not done or failed, 1 = partial, 2 = passed. Scheme and promotion thresholds: `writeup/paper.tex`, Sec. "Assessing model faithfulness".
**Rival models:** (R1) co-burst / common attention drive (H28); (R2) link-led nucleation (H53); (R3) kickoff/goal field (H54, G40); (R4) occupancy herding (Potts J).
**Locked holdout used for confirmation:** none yet. `analysis/confirm.py` (frozen, guarded, not run) targets #43, the #51 tail and #45.

| Axis | Test | Score | Evidence |
| --- | --- | --- | --- |
| A mapping | variables defined from dataset fields; assumptions listed; invariant across families and regimes | 1 | Arrivals, bursts, links and work signals come from shared tables (strict mentions, DQ4 work filter). A "state change" is proxied by deploy-type events (pages-branch or deploy-message commits, deploy commands); "first working build" and "a commit that makes a project usable" are not identifiable without text. |
| B assumptions | stationarity, Markov order, time-rescaling, update-order audit | 1 | Trimmed window audited against the untrimmed variant (link lead–lag changes sign); 5-min bins; same-bin events excluded from both sides. No Markov-order or time-rescaling test. |
| C adequacy | beats the null hierarchy, day-blocked held-out data | 0 | The work-signal model does not beat the matched non-burst control (OR_S CI includes 1) or the signal time-shift null (z −0.23). No held-out likelihood. |
| D unfitted predictions | unfitted statistics and the model's signature | 0 | The signature (state change before the follower onset and before the link) fails in pooled and per-period tests and in two natives. |
| E interventional | predicts the change across a natural experiment | 0 | No NE used; the G40 control is a goal-field contrast, not an intervention. |
| F identifiability | synthetic recovery with village sampling; robust to preprocessing | 1 | Point-process worlds at village counts: joint criterion power 15/15, size 0–1/15. Stylized (not real schedules); OR_S alone not specific (5/15 in the co-burst world). |
| G ground truth | agrees with known structure | 1 | DQ4 commits as work events. The G40 hub wave starts 1.9 min after the kickoff and 95 min before its first deploy, as H27/H31 described. |
| H comparative | beats the named rivals | 0 | Loses to R2 (link first: OR_L 11.9) and R3 (kickoff field in G40); R1 (co-burst) is consistent with the untrimmed lead–lag. |
| I transfer | holds in other same-mode periods, including the holdout | 0 | Fails in 6/7 tested periods; no holdout run. |

**Faithfulness lever (HH263):** H was raised for the *rival* question it targeted: the work-signal trigger is now tested and rejected, which strengthens H28/H53's link-first reading. G was used (DQ4 commits) but did not support the claim.

## Prediction
*Written 2026-10-04 19:25 UTC, before any real-data statistic. Seen beforehand: table schemas; agent-work commit counts per goal period (DQ4 design numbers: #30 352, #31 1,391, #38 1,393, #39 2,232, #40 2,945, #51 48k); the published results of H27, H28 (round 1b), H53 and RE-P1. Not seen: any arrival, burst, deploy timing or hazard statistic for H63.*

**Synthetic (axis F), before real data** (N = 12 agents, 5 days × 4–8 h, 15 projects, ~20 state changes, 25 runs per world):
- **S1 (power):** in the work-led world, P1's OR_S criterion and P3's h_S − h_S' > 0 each pass in ≥ 70% of runs. [0.6]
- **S2 (size):** in the co-burst, link-led and null worlds, the joint P1 + P3 criterion passes in ≤ 10% of runs. [0.6]
- **S3 (ordering):** P2's ordering share is > 0.5 in the work-led world and ≤ 0.5 in the link-led world. [0.7]

**Real data (exploratory, non-holdout).**

| # | Prediction | Counts against | Credence |
| --- | --- | --- | --- |
| P1 | **Bursts follow state changes (primary).** Pooled OR_S ≥ 2 with 95% CI excluding 1, above the time-shift null (z ≥ 2); per period OR_S > 1 in ≥ 2/3 of periods with ≥ 5 bursts. | pooled OR_S ≤ 1 or CI including 1 | 0.35 |
| P2 | **Links follow work.** Among bursts with both, the first S signal precedes the first link in > 50% (sign test p < 0.05). | ≤ 50% | 0.5 |
| P3 | **State changes lead arrivals.** Pooled h_S − h_S' > 0 (p < 0.05), while links replicate H28: κ − κ' ≤ 0. | h_S' ≥ h_S | 0.35 (work) / 0.75 (links) |
| P4 | **Not any commit.** Pooled h_S > h_R and OR_S > OR_R. | h_S ≤ h_R | 0.45 |
| P5 | **Links partly carry the work signal.** Adding S and R to the model lowers the pooled link coefficient κ by ≥ 25%. | κ drops < 10% | 0.3 |
| P6 | **Exogenous share.** ≤ 30% of herding bursts are kickoff-led or human-led. | > 50% | 0.6 |

**Amendment A1 (2026-10-04 20:35 UTC, after the synthetic validation, before any real-data statistic).** Seen: synthetic runs only, and the per-period input counts printed by the scheme build (touches, links, signals by class; e.g. #35 has 1 S signal).
- **Estimator fixes:** a Haldane 0.5 correction for 2×2 tables with a zero cell (otherwise OR = ∞); Newton steps clipped in the Poisson fit; day-block bootstrap with 20 draws in the synthetic runs (50 on real periods, 20 for #51).
- **Synthetic verdicts (15 runs per world; N = 12, 5 days, 15 projects):** S1 **passed** (work-led world: P1 and P3 each pass 15/15; median OR_S 142, median h_S − h_S' +2.05). S2 **passed** for the joint criterion (P1 and P3 together: co-burst 1/15, link-led 0/15, null 0/15). S3 **passed** (ordering share: work-led 1.00, link-led 0.33).
- **Consequence (stated before real data):** OR_S alone is not specific. It passes in 5/15 co-burst runs, because agents on a bursting project emit deploys. h_S − h_S' alone passes in 3/15 null runs (5-day bootstrap). A period counts as **work-led only when P1 and P3 both pass**; the per-period rule below already requires both for *supported*.

**Per-period verdict rule (replication):** *supported* if OR_S > 1 with p < 0.05 and h_S − h_S' > 0; *failed* if OR_S ≤ 1 and h_S − h_S' ≤ 0; *mixed* otherwise; *descriptive* if the period has < 3 herding bursts or < 5 S signals.

Native predictions are in `goalperiod-subhypotheses/G31/`, `G39/` and `G40/` (written before those runs).

## Results by goal period
Per-period rule (card; *supported* needs OR_S > 1 at p < 0.05 and h_S − h_S′ CI > 0). **0 supported, 1 mixed (#41), 6 failed, 6 descriptive** (13 eligible periods; descriptive = < 3 herding bursts or < 5 S signals).

| Period | Role | Verdict | Key numbers (trimmed window) |
| --- | --- | --- | --- |
| [G30](goalperiod-subhypotheses/G30/README.md) | replication | failed | bursts 8; S before 1/8 vs controls 0/46; OR_L 46.67; h_S−h_S′ 0.13 [-1.06, 0.55]; κ−κ′ 1.24 |
| [G31](goalperiod-subhypotheses/G31/README.md) | native + replication | failed (native and replication) | bursts 33; S before 0/33 vs controls 1/221; OR_L 4.73; h_S−h_S′ 0.41 [-0.65, 0.99]; κ−κ′ 0.04 |
| [G33](goalperiod-subhypotheses/G33/README.md) | replication | descriptive | bursts 2; S before 1/2 vs controls 0/20; OR_L 5.67; h_S−h_S′ 2.00 [0.00, 2.47]; κ−κ′ 0.45 |
| [G35](goalperiod-subhypotheses/G35/README.md) | replication | descriptive | bursts 1; S before 0/1 vs controls 0/17; OR_L 0.59; h_S−h_S′ -22.68 [0.00, 0.00]; κ−κ′ -1.40 |
| [G36](goalperiod-subhypotheses/G36/README.md) | replication | failed | bursts 28; S before 0/28 vs controls 3/482; OR_L 12.21; h_S−h_S′ 0.06 [-1.70, 0.70]; κ−κ′ 0.29 |
| [G37](goalperiod-subhypotheses/G37/README.md) | replication | descriptive | bursts 3; S before 0/3 vs controls 0/90; OR_L 34.00; h_S−h_S′ 0.82 [-19.50, 1.32]; κ−κ′ -0.22 |
| [G38](goalperiod-subhypotheses/G38/README.md) | replication | failed | bursts 10; S before 0/10 vs controls 0/354; OR_L 32.08; h_S−h_S′ 0.38 [-1.19, 1.16]; κ−κ′ 0.29 |
| [G39](goalperiod-subhypotheses/G39/README.md) | native + replication | failed (native); descriptive (replication) | bursts 2; S before 0/2 vs controls 4/86; OR_L 2.44; h_S−h_S′ -0.28 [-0.65, 0.48]; κ−κ′ -0.14 |
| [G40](goalperiod-subhypotheses/G40/README.md) | native (control) + replication | supported (native control); descriptive (replication) | bursts 2; S before 1/2 vs controls 8/71; OR_L 3.18; h_S−h_S′ 1.02 [-0.24, 2.14]; κ−κ′ 0.27 |
| [G41](goalperiod-subhypotheses/G41/README.md) | replication | mixed | bursts 9; S before 3/9 vs controls 6/97; OR_L 3.51; h_S−h_S′ -0.20 [-1.64, 0.35]; κ−κ′ -0.06 |
| [G42](goalperiod-subhypotheses/G42/README.md) | replication | descriptive | bursts 0; S before 0/0 vs controls 7/61; OR_L n/a; h_S−h_S′ 0.86 [-0.03, 3.09]; κ−κ′ 1.32 |
| [G44](goalperiod-subhypotheses/G44/README.md) | replication | failed | bursts 11; S before 0/11 vs controls 3/77; OR_L 100.72; h_S−h_S′ 0.11 [-1.31, 2.50]; κ−κ′ 1.28 |
| [G51](goalperiod-subhypotheses/G51/README.md) | replication | failed | bursts 218; S before 3/218 vs controls 87/4193; OR_L 12.03; h_S−h_S′ 0.17 [-0.11, 0.43]; κ−κ′ 0.39 |

## Results
*Exploratory round 1, 2026-10-04: 13 eligible non-holdout periods (#30 onward), 7 tested (≥ 3 bursts and ≥ 5 S signals), 317 herding bursts and 5,470 matched clusters. Numbers from `data/processed/H63-bursts-start-with-work/results/{periods.parquet,summary.json,untrim_hazard.parquet}` and `synthetic/summary.json`. Code: `scheme/build.py`, `analysis/h63lib.py`, `synthetic.py`, `run_periods.py`, `untrim_hazard.py`, `summarize.py`, `write_period_folders.py`, `figs_col.py`, `confirm.py`.*

### Headline
Herding bursts do not start at a visible artifact state change. A deploy-type state change precedes 2.2% of bursts and 1.8% of matched non-burst clusters (OR 1.53 [0.77, 3.05]). What precedes bursts is a chat link to the project (60% vs 12%; OR 11.9) or the project's birth (15% vs 1%; mechanical for new projects). Where both a state change and a link exist, the link usually comes first (8/11). Commits and deploys follow the pile-on.

### Outcome vs prediction
| # | Prediction | Observed | Outcome |
| --- | --- | --- | --- |
| S1 | work-led world: P1, P3 pass in ≥ 70% | 15/15, 15/15 | passed |
| S2 | joint P1 + P3 ≤ 10% in other worlds | co-burst 1/15, link-led 0/15, null 0/15 | passed |
| S3 | ordering > 0.5 (work-led), ≤ 0.5 (link-led) | 1.00, 0.33 | passed |
| P1 | pooled OR_S ≥ 2, CI excluding 1, z_shift ≥ 2 | 1.53 [0.77, 3.05], z −0.23; per period > 1 with p < 0.05 in 1/7 (#41) | **failed** |
| P2 | state change before the first link in > 50% | 3/11 (p 0.23) | **failed** |
| P3 | h_S − h_S′ > 0; links κ − κ′ ≤ 0 | +0.15 [−0.08, 0.37]; links +0.30 [0.04, 0.57] (trimmed) | **failed** (both halves) |
| P4 | h_S > h_R and OR_S > OR_R | h_S − h_R +0.33 [0.17, 0.48]; OR_S 1.53 < OR_R 2.05 | mixed |
| P5 | work terms lower κ by ≥ 25% | κ 0.96 with vs 0.91 without (−6% drop) | **failed** |
| P6 | ≤ 30% kickoff- or human-led | 0% of trimmed bursts | supported (uninformative: the trim removes the kickoff hour) |

### Findings
1. **Links, not work, precede herding.** 60% of bursts have an agent's chat link to the project in the hour before the second agent arrives (OR 11.9). This replicates H27's link precursor on a larger set (317 bursts vs 21 onsets) and H53's seed.
2. **Work follows attention.** Routine commits are more common before bursts (34% vs 21%; OR 2.0) because agents already on the project commit while others arrive. Deploy-type state changes are not (2.2% vs 1.8%). In G39 the order is link → visit → deploy.
3. **The link lead–lag depends on the day edge.** Trimmed to the all-present window, links lead arrivals (+0.30); untrimmed, the contrast is −0.10. Day-start co-bursts (everyone starts, links and touches together) are part of H28's "future links predict better" result (post hoc reading; H28's design differs in rooms, windows and visibility).
4. **Kickoff-led herding is a separate route.** The G40 hub wave starts 1.9 min after the first window and 95 min before the first deploy.

### Caveats
- "State change" is a proxy (deploy-type events). Only 2.2% of bursts have one nearby, so a better text-based detector of "made usable" (Phase 2) could change the picture for working-build events.
- Only 7 periods are tested; #51 contributes 218 of 317 bursts. The pooled OR is dominated by #51 (OR 0.66).
- Births precede bursts mechanically (no one can arrive before a project exists); they are not counted as evidence for work-led herding.
- Bursts are attention clusters (strict mentions), not work clusters. The synthetic validation is stylized.

## Round 2 redirects
- **What the direction is really after:** what starts a pile-on, early enough for an operator to see it.
- **H63-R1. Text-defined state changes.** Detect "it works / it is live" from commit messages and deploy outputs (Phase 2 text) and rerun P1 with that signal.
- **H63-R2. Link content.** Split the preceding links into announcements of a new artifact vs requests about an existing one (H28 next step 4); test which one seeds bursts.
- **H63-R3. Day-edge decomposition of link lead–lag.** Rerun H28's model with and without the all-present trim to size the scheduler's share of lead ≥ lag.

## Notes
- 2026-10-04 19:25 UTC: round 1 started; card filled before any real-data statistic.
- 2026-10-04 20:35 UTC: Amendment A1 after the synthetic validation; replication-period READMEs templated at 20:40 UTC, before the run.
- 2026-10-04 ~20:40–21:00 UTC: replication run (13 periods, ~5 min, 2 workers after the coordinator's load notice), untrimmed hazard variant (~3 min), natives.
- Data: `data/processed/H63-bursts-start-with-work/` (3.7 MB).
- Proposed for `physics-models/DEFINITIONS.md` (not edited): *work signal (state change, DQ4)*, *herding burst (H63, arrival cluster)*, *follower onset*.
