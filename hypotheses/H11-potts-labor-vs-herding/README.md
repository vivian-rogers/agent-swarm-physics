# H11: Division of labor vs herding is the sign of a Potts coupling, set by the goal

**Status:** exploratory round 1 done (2026-10-03); **round 1b on improved data done (2026-10-04): no verdict changes; work herds where attention does** (shared deterministic labels reproduce every round-1 sign; agents' work commits herd in 4/6 shared-artifact weeks, onto the same repos they attend; HH266's "attention herds, work stays private" holds only in own-artifact and private-role units; #26 redone per election round on DQ6 ballots). **The sign-by-goal-mode prediction is not supported.** βJ_CW > 0 (herding) in 11 of the 14 tested weeks, whatever the mode, including all five weeks predicted to be AF. The exceptions are the three weeks where agents built their own artifacts, and there the spread is static specialization (fields), not avoidance. A frozen confirmatory test of the original rule and of the round-1 pattern on the holdout (#22, #28, #45) is written but not run. Predictions below were written 2026-10-03, before any real-data run.
**Fields:** stat mech, sociophysics
**Origin:** HH24 + HH26 + HH84 (shortlist 2, item 2), plus **HH22** (the election, #26), folded in as `G26/` by Vivian on 2026-10-03 (`../hypohypotheses/HYPOHYPOTHESES.md`; `../promotion-shortlist.md`)
**Definitions used:** "Agent state (categorical)" with two named variants proposed for DEFINITIONS.md, **agent state (categorical, project/artifact strict)** and **agent state (categorical, action class)** (defined under Data scheme); "Population N(t)", active-population variant (labeled agents in a window and room); "Regime" (each period sits inside one regime); "Interaction (broadcast)" (the room is the interaction neighbourhood, so the coupling is uniform within a room block).

## Standards (2026-10-04)
**Question served:** Q2 (herding coupling vs common drive and specialization fields) and Q5 (detecting duplicated work).

| Impostor | Relevant? | How it was handled | Status |
| --- | --- | --- | --- |
| Scheduler field | partly | N2 circular shift of within-day window sequences and N1d within-agent-day permutation remove day-scale drive timing (Null / baseline). | removed |
| Exogenous field (kickoff/goal/operator) | yes | Named as a known confound and not separable from coupling (Null / baseline; axis C: drive vs coupling unseparated). Close with `goal_fields` and operator-message regressors and a kickoff-matched placebo (§1). | open |
| Shared model priors | partly | N1 within-agent permutation removes stable agent specialization. No same- vs cross-family herding split. Close with a cross-family control (§1). | partly |
| Contemporaneous convergence | yes | Not handled in H11's herding statistic (H06 ran the ledger test on the same labels). Close with the in-flight placebo (§1). | open |

**Inputs:** all current: shared `project_states`, DQ4 work labels, DQ6 ballots. Activity, embeddings and failures do not apply.

**Two layers:** 18 replication folders. Natives: 3 (G26 mixed, G31 supported, G40 mixed).

**Confirm script:** `confirm_holdout.py` (#22, #28, #45), frozen 2026-10-03, not run. Re-freeze: yes, on the deterministic shared labels (Notes, from H31). #35 contradicts frozen C2; disclose before any run (holdout item 11).

## Question
When agents work on a shared goal, do they spread across subtasks (antiferromagnetic Potts coupling: division of labor, graph coloring) or pile onto the same project (ferromagnetic: herding)? Does consensus arrive as a first-order jump (mean-field Potts, q ≥ 3)? Practical payoff: detecting duplicated work and groupthink in multi-agent systems.

## Model
**From:** `physics-models/10-potts`, mean-field forward first. One uniform-coupling q-state Potts model per period, fitted from the dominant option's share and its fluctuations. It predicts the sign of J by goal mode, and the jump size and hysteresis at consensus events. Full plmDCA couplings are only a secondary check (H02 showed pairwise inference is weak here).

**H11 variant (Curie–Weiss Potts with a neutral state, in room blocks).** In each 30-min window, the labeled agents in one room form a block of size N_b ≥ 2. States are 0 = "other" (rare projects merged), which is neutral and carries no coupling, and 1…q, the real projects:

P(σ) ∝ exp( Σ_i h(σ_i) + βJ/(N_b − 1) · Σ_{i<j ∈ b} δ(σ_i, σ_j)·[σ_i ≥ 1] )

- **Normalization.** With J/(N − 1), the mean-field self-consistency is x_a = softmax_a(h_a + βJ·x_a). So the textbook pure-Potts thresholds apply:
  - first-order transition at βJ_c = 2(q−1)ln(q−1)/(q−2): 2.77, 3.30, 3.70, 4.02 for q = 3…6;
  - ordered spinodal at βJ_s(q) = min_s ln((1+(q−1)s)/(1−s))/s: 2.75, 3.22, 3.57, 3.84;
  - disordered spinodal at βJ = q;
  - jump of the dominant share at βJ_c from 1/q to (q−1)/q.

  (Checked numerically in `analysis/potts_core.py`. The J/N vs J/(N−1) difference is O(1/N) and only rescales βJ by (N−1)/N.)
- **Exact fit.** The finite-N likelihood is computed exactly with generating functions: Z_N = N!·[z^N] Π_a Σ_k e^{h_a k + c k(k−1)/2} z^k/k!, with c = βJ/(N−1). So no composition enumeration is needed, for any q. It matches brute-force enumeration to 1e−13.
- **Where the sign comes from.** With uniform fields, βJ is identified from the fluctuations of the occupancy vector around multinomial.
  - **βJ < 0** means occupancies are steadier and more evenly divided than for interchangeable independent agents: fixed staffing, division of labor.
  - **βJ > 0** means they swing collectively: herding.

## Data scheme (`scheme/`)
`scheme/build.py` (helpers in `scheme/h11common.py`) builds `data/processed/H11-potts-labor-vs-herding/G<NN>/` from the shared tables, for every non-holdout goal period 2–44. It refuses holdout periods unless called with `--allow-holdout`, which only `analysis/confirm_holdout.py` does. Window grid: W = 30 min (primary) and 15 / 60 min (robustness), counted from each day's empirical active-window start (`calendar.win_start`).

- **Agent state (categorical, project/artifact strict).** σ_i(w) is the project with the most strict artifact mentions by agent i in window w.
  - **Strict mentions:** `artifact_mentions` with `speaker_kind = agent` and `how ∈ {url, output, bare}`, from all sources (action, chat, intention). One count per (agent, source, turn or message, project). Directory-resolved mentions are dropped, per infra/README.
  - **Project:**
    - a repo is its own project;
    - a file or site maps to its parent repo when the parent is known;
    - otherwise the site, or the Google Docs / Drive file, is its own project;
    - Netlify `deploy-preview-N--` prefixes are stripped;
    - domains and the Google `/e` placeholder ids are excluded.
  - **Ties** go to the most recent mention. An agent with no strict mention in a window is **missing**, not "idle".
  - **q per period:** projects holding ≥ 2% of the period's labeled agent-windows get their own state, up to q ≤ 8 (by rank). The rest are merged into "other" (state 0, neutral). Raw unmerged labels are kept (`project` column) for robustness.
- **Agent state (categorical, action class).** The modal class of the agent's computer-use turns and agent events in the window: 1 talk (AGENT_TALK, send_message), 2 gui (click/scroll/screenshot/…), 3 type (type/key), 4 bash, 5 wait (wait/pause, WAIT/PAUSE). All five states are coupled.
- **Rooms.** Each agent's room at the window midpoint comes from `rooms_timeline`. Regime I is one room (#general).
- **#26 votes (proxy).** Agent chat messages in #26 that contain a vote word (vote / ballot / approve / approval) and name exactly one roster agent, found with the shared mention regexes. Stored as agent, t, candidate codes only, with no text. The declared vote is carried forward until the agent's next declaration.
- **Output:** `G<NN>/labels_project_w{15,30,60}.parquet`, `labels_action_w*.parquet`, `projects_w*.parquet`, `windows_w*.parquet`, `G26/votes.parquet`, and `_provenance.json`. Total ≈ 2–3 MB.
- **Regimes covered:** #13–#31 are regime I; #37–#42 are regime III. No period crosses the 2026-03-24 boundary except #36, which is not used.

## Candidate goal periods
#13 (human-subjects experiment: antiferro expected), #18, #19 (puzzle-game consensus), #26 (election votes), #31 (guardrails pile-up: ferro), #40 (shared standards), #41 (research convergence). Transfer periods, with predictions by the same class rule:
- free weeks #11, #16, #37;
- shared-objective divisible weeks #24, #25, #30, #38;
- individual-objective weeks #20, #39, #42 (descriptive only).

Holdout confirmation targets are chosen under Prediction.

## Links to other hypotheses
Feeds H01 D3.4 (factions) and D7.1 (condensation vs leaders). Uses H07's artifacts tables. Takes H02's lesson: no individual J_ij from activity timing, so uniform coupling comes first.

## Observables
All per goal period, at W = 30 min, with merged project labels and room blocks, unless stated.
- **O1 (primary): βJ_CW.** The exact finite-N Curie–Weiss Potts MLE with uniform coupling and **uniform period-level fields**, over all room blocks with N_b ≥ 2. Uncertainty: a leave-one-day-out jackknife SE, giving t = βJ_CW/SE with D − 1 degrees of freedom (D = active days). This is the HH84 estimator ("βJ from the dominant share and its fluctuations"): fields fit the mean shares, βJ fits the occupancy fluctuations.
- **O2: βJ_PL.** Pseudo-likelihood (conditional logit) with one uniform βJ and **agent-specific fields**: the coupling *beyond* each agent's stable preferences. It is tested against the nulls N2 / N1d / N1 below, as z-scores.
  - O1 vs O2 separates *specialization* (spread carried by agent fields: O1 < 0, O2 ≈ 0) from *coordination in time* (O2 ≠ 0).
- **O3: pair-agreement ratio R.** The observed fraction of same-real-project pairs per block, divided by Σ_a p_a² (pooled shares). A descriptive companion to O1: R < 1 is spread, R > 1 is herding.
- **O4: dominant-share trajectory and jump test.** x₁(w) is the share of the period's final-day dominant option among labeled agents in window w. Three fits under a binomial quasi-likelihood (overdispersion φ from the residuals): constant, linear, and logistic step.
  - **"jump"** if the step beats both others by ΔBIC ≥ 6, the amplitude is ≥ 0.3, the width is τ ≤ 2 windows (10–90% rise within ≈ 2 h of active time), and t0 is inside the period;
  - **"gradual"** if a change is detected but is not a jump;
  - **"none"** otherwise.

  Persistence (the hysteresis proxy) is the fraction of post-step windows (after t0 + 2τ) below the step midpoint. For #26 the series is the declared-vote share of the eventual winner.
- **O5: mean-field forward check.**
  - q_eff is the perplexity of the real-state shares in the period's first third.
  - The period is in the **first-order region** iff βJ_CW ≥ βJ_s(round q_eff).
  - The MF-predicted jump at the fitted βJ_CW comes from the ordered-branch solution (0 if there is no ordered branch).
  - βJ_x1 is the zero-field inversion of the final-day dominant share: the coupling that would sustain that dominance with no field.
- **O6: action-class βJ_CW and βJ_PL** (secondary state, used as a specificity control).
- **O7: day-blocked held-out pseudo-likelihood.** The agent-field PL model with coupling vs the fields-only model, leave-one-day-out, reported as ΔlogL per observation (axis C).
- **O8: plmDCA (secondary).** Per-agent softmax regressions on the other agents' one-hot labels within the block, with L2, symmetrized and zero-sum gauged. The statistic is the mean Potts-diagonal coupling over pairs, against N1.
- **O9: robustness.**
  - O1 and O2 with raw unmerged labels, with q ≤ 4, at W = 15 and 60 min, and with all rooms pooled into one block (regime III);
  - O1 with day-level fields (βJ_CW,day). That variant is known from synthetic S1 to absorb herding (it is shown only to bound drift).

## Null / baseline
- **N0 (for O1): independent, interchangeable agents.** βJ = 0 with the period's shares (multinomial occupancies), giving the likelihood ratio. The sign call uses the jackknife t, whose calibration is in synthetic S1.
- **N1: label permutation within agent** (whole period). Keeps each agent's marginal and missingness pattern, and destroys co-occurrence. Applied to O1 (does stable specialization alone explain βJ_CW?), O2 and O8.
- **N1d: label permutation within agent-day.** Also removes day-scale common drive.
- **N2 (primary for O2): circular shift** of each agent's within-day window sequence by a random offset, with labels and presence moving together and the room kept per agent-day. Keeps each agent's persistence, and destroys cross-agent alignment.
- **N3: independent fields-only model.** Agent fields with no coupling, used for held-out likelihood (O7).
- **For O4:** constant and linear (gradual-drift) models of x₁(w).
- **Known confounds** (each quantified in synthetic S2):
  - stable agent specialization drives βJ_CW negative without any coupling. That is division of labor in the behavioral sense, but done by fields, and it is what O2 separates out;
  - common time-varying drive (the goal's phases, announcements) drives both O1 and O2 positive. Coupling and common drive are not separable from observational data (cf. H01 D3.2).

## Faithfulness scorecard
Scored per model, mapping and window; 0 = not done or failed, 1 = partial, 2 = passed. Scheme and promotion thresholds: `writeup/paper.tex`, Sec. "Assessing model faithfulness".
**Rival models:**
- (R1) **independent agents with stable agent fields** (specialization without coupling; N1/N3);
- (R2) **common time-varying field without coupling** (drive; N1d and the day-field variant);
- (R3) **Ising / voter-like gradual adoption** (a continuous transition: O4 "gradual").

**Locked holdout used for confirmation:** none yet. Targets are #22, #28 and #45 (`analysis/confirm_holdout.py`, frozen rule; not run).

| Axis | Test | Score | Evidence |
| --- | --- | --- | --- |
| A mapping | variables defined from dataset fields; assumptions listed; invariant across families and regimes | 1 | States come from strict artifact mentions, rooms and action classes, all defined from fields, with assumptions listed under Data scheme. Coverage is 28–78% of agent-windows (#11, #13, #16 below the minimum). A mention measures attention to a project, not necessarily work on it. The same mapping works in regimes I and III. Round 1b: a work-ledger state (agent work commits) is added; an agent's attention project equals its work repo in a median 84% of agent-windows with both labels (#30–#51). |
| B assumptions | stationarity, Markov order, time-rescaling, update-order audit | 1 | **Stationarity:** violated at the day scale (βJ_CW with day fields is lower but stays positive). **Time-rescaling:** W = 15 / 30 / 60 min gives the same signs and similar sizes. **Not audited:** Markov order and update order. **Equilibrium is doubtful:** persistence P(same project next window) is 0.5–0.9. |
| C adequacy | beats the null hierarchy, day-blocked held-out data | 1 | Coupling beyond agent fields beats N1, N1d and N2 in 10/14 tested periods, and survives a ±1-window local shift in 9 (post hoc). The coupled PL gains on held-out days in 8/10 of those periods. Common fast drive and coupling are not separable, so this is adequacy of an *effective* coupling. Round 1b (shared labels): 10/11 shared weeks z_N2 ≥ 2; held-out gain 10/10. |
| D unfitted predictions | unfitted statistics and the model's signature | 1 | The a-priori sign mapping failed: 5/11 correct, p = 0.73. First-order consensus passed fully in 0/4 periods. The prior |βJ| < 2 (P7) failed for βJ_CW. Only the #26 runoff jump (P-G26b) came out as predicted. **Round 1b (0 → 1):** the coupling found in attention predicts coupling in an independent output channel, agent work commits: z_N2 ≥ 2 in 4/6 shared weeks, spread in 3/3 own-artifact weeks; the #26 jump holds on the correct election (DQ6: 1/3 → 7/8 in 83 s). |
| E interventional | predicts the change across a natural experiment | 0 | Not done in round 1. Candidate: NE15 (#best / #rest split), where herding should become block-local. |
| F identifiability | synthetic recovery with village sampling; robust to preprocessing | 1 | **Synthetic recovery:** the sign is recovered with attenuation 0.4–0.75×, and per-period power is ≈ 0.35 at |βJ| = 2. **Confounds characterized:** specialization reads as AF in βJ_CW; day-level drift reads as FM in βJ_CW and is absorbed by N2; field steps are caught by the MF clause. **Preprocessing:** robust to raw labels, q ≤ 4, W, and action-only labels. Drive vs coupling remains unidentified. Round 1b: labels are now bit-reproducible; null Monte Carlo noise moves z by up to ≈ 0.5 near 2. |
| G ground truth | agrees with known structure | 1 | #26: the winner (DeepSeek-V3.2) and the runoff jump match the dataset's goal summary. #31: herding onto shared repos matches, though the narrated guardrails pile-up shows no step. #39: each agent's own world gives strong spread, as described. Round 1b: #26 per round on DQ6 ballots (exact symmetric point, 7–1–0 runoff); #31's wave appears in work commits. |
| H comparative | beats the named rivals | 1 | **R1** (agent fields only): beaten in 10 periods. **R2** (common drive): beaten at the day scale (N2, N1d), not within the day. **R3** (gradual adoption): beaten by a step in the #26 votes (ΔBIC 40) and #31 (step vs linear), but "none" in #19 and #40. |
| I transfer | holds in other same-mode periods, including the holdout | 0 | The mode rule does not transfer: AF transfer periods are 0/4 negative. The round-1 pattern holds across regimes I and III but is post hoc: βJ_CW > 0 in all 11 weeks other than the own-artifact weeks #39, #40 and #42, with z_N2 ≥ 2 in 10 of them. The ownership index sorts the periods imperfectly (#24 is 'owned' at 0.65 but herds; #40 is 'shared' at 0.26 but does not). Holdout not run. Round 1b: in new periods #33 fits, #44 and #51 are private in work as predicted, but #35 (shared, ownership 0.01) has z_N2(attention) −2.5, against the pattern. |

## Prediction
*Written 2026-10-03, before any real-data run of the analysis.*

**What I had seen when writing this:**
- the label structure per non-holdout period: q, number of distinct projects, the "other" fraction, and the window and block counts;
- the top-14 projects per candidate period, with mention counts and distinct-agent counts, which show the dominant project names;
- volume counts of artifact mentions per goal period, *including holdout periods* (counts only: no labels, shares or timing);
- for #19/#26, counts of vote-word chat messages.

I had **not** seen any window-level shares, fluctuations, couplings or time courses. The synthetic validation (S1–S4) ran while this was written; its calibration notes are appended below the predictions and dated.

**Coupling-mode classes**, assigned a priori from the goal descriptions in `goal-periods.md`:

| Class | Periods | Predicted sign |
| --- | --- | --- |
| AF: shared objective with divisible subtasks | #13, #18; transfer #24, #25, #30, #38 | βJ < 0 |
| FM-consensus: a shared choice | #19 (concept / build), #26 (election), #40 (shared universe hub) | βJ > 0 |
| FM-free: free week | #31; transfer #11, #16, #37 | βJ > 0 |
| FM-convergence | #41 (topic convergence) | βJ > 0 |
| No sign prediction (individual objectives; descriptive) | #20, #39, #42 | — |

**Minimum data rule:** a period is tested only if it has ≥ 15 room blocks with N_b ≥ 3 at W = 30. Otherwise its verdict is "n/a (insufficient labels)".

- **P1 (primary, O1). The sign of βJ_CW follows the class.**
  - **Per period:**
    - **supported** if βJ_CW has the predicted sign and |t| > t_{D−1, 0.975};
    - **weak** if the sign is right but not significant;
    - **failed** if the sign is opposite.
  - **Card level, over the 7 candidates:**
    - **supported** if ≥ 5 are "supported" and none is significantly opposite;
    - **failed** if ≤ 3 have the predicted sign, or ≥ 2 are significantly opposite;
    - **mixed** otherwise.
  - **Cross-period contrast:** βJ_CW(AF) < βJ_CW(FM), one-sided Mann–Whitney over candidate + transfer periods.
- **P2 (O2). Dynamic coupling beyond agent fields follows the class.** AF: z_N2 ≤ 0 (avoidance or none); FM: z_N2 ≥ +2. Per period: supported / weak / failed on the same pattern.
- **P3 (O4 + O5). Consensus is a first-order Potts jump** (#19; #26 on declared votes; #40; #31 for the herding project). HH22's own tests for #26 are in [`G26/README.md`](goalperiod-subhypotheses/G26/README.md) (P-G26a symmetric point, P-G26b runoff jump, P-G26c mean-field mechanism), written 2026-10-03 before running on #26. Two clauses:
  - **(a) data:** x₁ shows a "jump" (Δ ≥ 0.3, τ ≤ 2 windows) with persistence ≤ 0.15;
  - **(b) mechanism:** βJ_CW ≥ βJ_s(q_eff), the first-order region.

  Both clauses are needed for "first-order Potts consensus". (a) without (b) is a **field-driven step** (a decision or announcement), which counts against the Potts mechanism. Gradual (R3) counts against both.
- **P4 (O6, specificity control).** Action-class βJ does **not** follow the class: the AF-vs-FM contrast is not significant, and the sign is mostly positive (shared schedule). If the action-class βJ flips with mode as well, the project result is not specific to project choice.
- **P5 (O7, axis C).** Where |z_N2| ≥ 2, the coupled PL model beats the fields-only model on held-out days (ΔlogL > 0 in ≥ 4/5 folds).
- **P6 (O8).** The sign of the plmDCA mean diagonal coupling agrees with βJ_PL. Expected weak (H02).
- **P7 (my prior, competing with P3b).** From H02/H04/H05 (mean-field loop gains 0.06–0.4): |βJ_CW| and |βJ_PL| < 2 in every period, far below βJ_s(q) ≈ 2.7–3.8. Mean field then predicts **no spontaneous first-order transition** anywhere, so any consensus step is field-driven.

**Credences** (mine, before running):
| Prediction | Credence | Why |
| --- | --- | --- |
| P1 card-level supported | 0.30 | The uniform-field estimator counts each agent's own project as spread, so free weeks may also come out βJ_CW < 0 |
| P2 | 0.25 | |
| P3a | 0.5 in #19 and #26 | |
| P3b | 0.10 | |
| P4 | 0.7 | |
| P7 | 0.75 | |

**Calibration notes from the synthetic validation** (appended 2026-10-03, after S1–S4 finished and before any real-data run; the rules above are unchanged):
- **Low per-period power.** At village sampling (N = 13, 5 days × 9 windows, p_obs = 0.75), the P1 rule detects the right sign at |βJ| = 2 in about 35% of runs and at |βJ| = 4 in 40–65%.
  - At p_obs = 0.5 or N = 7 the power is 10–30%.
  - 10-day periods roughly double the power.
  - βJ_CW is attenuated to about 0.4–0.75 × the true βJ.
  - **Consequence:** even if H11 is true at |βJ| ≈ 2, the expected number of "supported" candidates is about 2–3 of 7. So the ≥ 5/7 card-level rule is strict, and the sign pattern and cross-period contrast carry most of the evidence. I keep the rule as written.
- **Specialization reads as AF, by construction.** With heterogeneous agent fields (σ_h = 1) and βJ = 0, βJ_CW comes out significantly negative in 5–25% of runs (always in the AF direction). βJ_PL stays unbiased.
- **Day-level common drift fakes FM in βJ_CW.** With βJ = 0 and drift amplitude 1, βJ_CW is +1.6 and significant in 55% of runs. βJ_PL against N2 or N1d absorbs day-level drift (2.5–5% significant). **So an FM call needs βJ_PL vs N2 to agree;** βJ_CW > 0 alone is not enough. Within-day drift was not simulated, and it would not be absorbed.
- **Jump test calibration.**
  - False "jump" rate: 0% under constant fields, 11% under a smooth field ramp.
  - An abrupt field step at βJ = 0 is called a "jump" in 62% of runs. The mean-field clause rejects 100% of these: βJ_CW never reached βJ_s, though the step inflates βJ_CW to about +1.8. So P3b is the discriminator.
  - A true first-order ramp (βJ = 4 > βJ_c(4) = 3.30) passes jump + MF in 58% of runs.
  - **Pitfall:** a frozen consensus (βJ = 6) shows no jump within the period and gives an uninformative, low βJ_CW, because occupancies don't fluctuate. A "none" verdict with an already-dominant project may be frozen order, not a weak coupling.
- **plmDCA** recovers the sign at |βJ| = 3 in 70–90% of runs, with about 10% false positives (only 9 null draws).

**Holdout confirmation targets** (chosen now, from `holdout.json`; to be run only after sign-off, with the decision rule frozen after round 1):
- **#22**, free week, FM-free: βJ_CW > 0;
- **#28**, quiz build and promote, C-divisible, AF: βJ_CW < 0;
- **#45**, Follow your leader, module assignment, C-divisible, AF within #best: βJ_CW < 0.

The script is `analysis/confirm_holdout.py`. It refuses to run without `--confirm --i-understand-this-uses-the-locked-holdout`; `--dry-run` uses non-holdout stand-ins.

## Results by goal period
All periods were run on 2026-10-03. Predictions were written before the run (card and each `G<NN>/README.md`). Numbers: βJ_CW with its jackknife t, and the z of βJ_PL against the circular-shift null N2.

| Period | Role | Verdict | Key numbers |
| --- | --- | --- | --- |
| [G13](goalperiod-subhypotheses/G13/README.md) | candidate, AF | n/a (14 blocks < 15) | descriptive βJ_CW +4.7 (opposite sign; not a test) |
| [G18](goalperiod-subhypotheses/G18/README.md) | candidate, AF | P1 failed (significantly opposite); P2 failed | βJ_CW +5.00 (t 6.7); z_N2 +8.7; last-day convergence on one repo |
| [G19](goalperiod-subhypotheses/G19/README.md) | candidate, FM-consensus | P1 supported; P2 supported; P3 failed (consensus already in place: frozen) | +2.76 (t 9.6); z +5.2; build repo at ≈ 0.6 share from the start |
| [G26](goalperiod-subhypotheses/G26/README.md) | candidate, FM-consensus + HH22 | P1 supported; P2 supported; HH22: jump supported, mechanism inconclusive | +6.13 (t 7.0); z +6.4; votes jump Δ 0.62 within 1 window; βJ_snap 2.80 [0.65, 4.65] vs βJ_s 2.75 |
| [G31](goalperiod-subhypotheses/G31/README.md) | candidate, FM-free | P1 supported; P2 supported; P3 failed (relapse 0.27) | +4.88 (t 20.4); z +14.3; herding waves onto successive shared repos |
| [G40](goalperiod-subhypotheses/G40/README.md) | candidate, FM-consensus | P1 failed (opposite, n.s.); P2 failed | −17.9 (t −2.6); z −0.1; spread carried by fields (own worlds + hub) |
| [G41](goalperiod-subhypotheses/G41/README.md) | candidate, FM-convergence | P1 supported; P2 supported | +4.30 (t 24.9); z +5.4 |
| [G11](goalperiod-subhypotheses/G11/README.md), [G16](goalperiod-subhypotheses/G16/README.md) | transfer, FM-free | n/a (3 and 5 blocks) | – |
| [G24](goalperiod-subhypotheses/G24/README.md) | transfer, AF | P1 failed (n.s.); P2 failed (significant) | +3.25 (jackknife SE 26.6, unstable); z +2.7 |
| [G25](goalperiod-subhypotheses/G25/README.md) | transfer, AF | P1 failed (significant); P2 failed | +4.12 (t 3.8); z +6.7 |
| [G30](goalperiod-subhypotheses/G30/README.md) | transfer, AF | P1 failed (significant); P2 failed | +2.01 (t 8.0); z +4.3 |
| [G37](goalperiod-subhypotheses/G37/README.md) | transfer, FM-free | P1 supported; P2 supported | +3.73 (t 23.1); z +6.9 |
| [G38](goalperiod-subhypotheses/G38/README.md) | transfer, AF | P1 failed (significant); P2 failed | +4.28 (t 16.7); z +2.1; within-day excess only +0.4 |
| [G20](goalperiod-subhypotheses/G20/README.md) | transfer, I (descriptive) | descriptive | +2.18 (t 6.3); z +1.9 |
| [G39](goalperiod-subhypotheses/G39/README.md) | transfer, I (descriptive) | descriptive | −8.61 (t −3.05); z −1.3; ownership 1.00 |
| [G42](goalperiod-subhypotheses/G42/README.md) | transfer, I (descriptive) | descriptive | −2.16 (t −1.7); z +1.3; ownership 0.73 |

**Round 1b (2026-10-04):** every tested period gets a `**Verdict (1b):**` line (shared labels; work space for #30 onward). Verdict changes: #38 P2 "failed (significant)" → "failed" and #40 P2 "failed" → "weak" (z ≈ 0 and ≈ 2 noise). Native folders: G26 (per election round), G31 (wave in work), G40 (hub vs own worlds in work). New replication folders for the work space: [G33](goalperiod-subhypotheses/G33/README.md), [G35](goalperiod-subhypotheses/G35/README.md), [G44](goalperiod-subhypotheses/G44/README.md), [G51](goalperiod-subhypotheses/G51/README.md) (seven non-holdout units).

## Results
*Exploratory round 1, 2026-10-03.*
- Code: `scheme/build.py`, `analysis/potts_core.py`, `analysis/synthetic.py`, `analysis/explore.py`, `analysis/local_shift.py` (post hoc), `analysis/assemble.py`, `analysis/figures.py`.
- Data: `data/processed/H11-potts-labor-vs-herding/` (`G<NN>/round1.json`, `results_round1.parquet`, `verdicts_round1.parquet`, `cross_period_round1.json`, `synthetic/`).

**Outcome vs prediction**

| Prediction | Outcome | Verdict |
| --- | --- | --- |
| P1 sign of βJ_CW follows the goal mode (primary) | **Candidates:** #19, #26, #31, #41 supported (FM). #18 significantly opposite and #40 opposite (n.s.). #13 n/a. **Transfer AF periods:** #24, #25, #30, #38 all positive. **Cross-period:** AF < FM contrast p = 0.47; sign test 5/11, p = 0.73. | **Mixed by the card-level rule; substantively failed.** The AF half fails 0/5, and the FM half passes only because βJ_CW > 0 in 11/14 tested weeks whatever the mode |
| P2 coupling beyond agent fields follows the mode | FM: z_N2 ≥ 2 in 5/6 (#40 ≈ 0). AF: z_N2 between +2.1 and +8.7 in 5/5, opposite to the prediction | **Failed** |
| P3 consensus is a first-order Potts jump | #19 none (consensus already in place); #31 jump but relapse 0.27; #40 none (hub given by the goal); #26 project labels gradual. On #26 votes: a jump with mean field at threshold (see HH22) | **Failed** (0/4 full passes) |
| P4 action class does not follow the mode (control) | AF vs FM p = 1.0; positive in 9/14 periods, 5 significantly; no significant negatives | **Supported** |
| P5 held-out gain where abs(z_N2) ≥ 2 | 8/10 periods gain in ≥ 80% of day folds | **Supported** |
| P6 plmDCA agrees with βJ_PL in sign | Agrees (its N1 null does not absorb drift, so its z values are inflated) | **Supported (weak)** |
| P7 abs(βJ) < 2 everywhere (prior) | abs(βJ_CW) > 2 in 12/14; the within-day excess (βJ_PL − N2 mean) is +0.4 to +3.4 | **Failed** for βJ_CW |
| HH22 P-G26a symmetric point | Passes as written (χ² p = 0.09, q_eff 3.7), but the onset rule fired on day 1, the test has little power, and the reported three-way tie is not reproduced | **Uninformative** |
| HH22 P-G26b runoff is a jump | Winner's declared share goes 0.18 → 0.80 within ≈ 1 window at window 27 of 36; persistence 0; ΔBIC step vs linear 40 | **Supported** (pre-jump level below the predicted ≈ 1/3) |
| HH22 P-G26c Potts mechanism | Runoff snapshot (8, 1, 1): βJ_snap = 2.80 [0.65, 4.65] vs βJ_s(3) = 2.75; P(≥ 8 of 10 under independent symmetric voters) = 0.01 | **Inconclusive** |

**Synthesis**
1. **The sign tracks artifact ownership, not the goal mode** (post hoc, to be confirmed). βJ_CW is positive in all 11 tested weeks where agents work mainly on common repos and documents: all 8 regime-I periods (7 significant) plus #37, #38 and #41. That spans shared-objective, free and individual-objective goals. It is negative, and the coupling beyond agent fields is ≈ 0, in the three weeks where the goal gave each agent its own artifact:
   - #39 (own worlds; ownership index 1.00);
   - #42 (own channels; 0.73);
   - #40 (own worlds plus a fixed hub; its ownership index is only 0.26, because the hub is shared).

   The ownership index correlates with z_N2 at Spearman ρ = −0.56, p = 0.04, over 14 periods. That is post hoc, would not survive correction, and the index misplaces #24 and #40. **Division of labor in this village is static specialization (fields), not avoidance (antiferromagnetic coupling).** No tested week shows agents moving *away* from what others are doing beyond their stable preferences.
2. **The herding is fast.** In 10/14 periods the co-movement beyond agent fields survives the day-level nulls (N2, N1d), and in 9 of those it also survives a ±30-min local shift. So agents are on the same project in the same half-hour, beyond slow drift.
   - Mechanism candidates: chat-mediated attention, which is coupling (someone posts a repo and others go to it), or synchronous external prompts, which is a field. These are not separable here.
   - #38 is the exception: positive βJ_CW but a small within-day excess (+0.4).
3. **Magnitudes.** βJ_CW (+2 to +6) is inflated by day-scale structure (synthetic S2). The drift-corrected within-day excess, +0.4 to +3.4, is at or below the mean-field first-order thresholds (βJ_s ≈ 2–3.6 for the observed q_eff). That fits the absence of clean first-order consensus events in the project labels.
4. **Consensus.** The one clean consensus variable, the #26 votes, does jump abruptly and stays: a first-order-*looking* step. But a single runoff snapshot cannot separate a field from a coupling, and the mean-field coupling sits at the threshold with a wide CI. #31's "pile-up" is a sequence of herding waves onto successive shared repos: `village-time-capsule` peaked at 11 agents in one window. #18, predicted AF, ends with a deadline-driven convergence of the whole swarm onto one repo on the last day.
5. **Heterogeneity.** Regime I: βJ_CW > 0 in all 8 tested periods (7 significant), and z_N2 ≥ 2 in 7 (#20: +1.9). Regime III: ferromagnetic in shared-artifact weeks (#37, #38, #41), and spread or neutral in own-artifact weeks (#39, #40, #42). Action-class coupling (P4) is weakly positive and mode-independent, which fits a shared schedule.

**Figures:**
- [`figures/H11_round1_summary.pdf`](figures/H11_round1_summary.pdf) (one page);
- [`figures/periods_forest.pdf`](figures/periods_forest.pdf);
- [`figures/dominant_share_trajectories.pdf`](figures/dominant_share_trajectories.pdf);
- [`figures/synthetic_validation.pdf`](figures/synthetic_validation.pdf).

**Confirmatory prediction (frozen 2026-10-03, after round 1, before any holdout data was read)**, `analysis/confirm_holdout.py`. Targets: #22 (F), #28 (C), #45 (C, regime III). Same pipeline: W = 30, q ≤ 8 / 2%, strict mentions, 199 nulls.
- **C1, the original H11 rule:** the sign of βJ_CW matches the class (#22 > 0; #28, #45 < 0) with |t| > t_crit in every target. **Round 1 predicts that C1 fails.**
- **C2, the round-1 pattern:**
  - targets with ownership < 0.5 need βJ_CW > 0 (significant), z_N2 ≥ 2 and z_local1 ≥ 2;
  - targets with ownership ≥ 0.5 need z_N2 < 2;
  - refuted if any shared-artifact target has z_N2 < 0.
- **C3, specificity:** the action-class βJ_CW is not significantly negative.

Dry run on stand-ins (#31, #25, #38): C1 not confirmed, C2 inconclusive (#38 fails the local-shift clause), C3 holds. Running it needs Vivian's sign-off.

**Caveats**
- **Labels are attention, not work.** A strict mention means an agent visited, pushed or linked a project; reading a shared repo counts.
- **Missing labels.** Unlabeled windows (chatting, idle, GUI work without URLs) are missing, and probably not at random: label coverage is 28–78%.
- **Common within-day drive vs coupling.** The two cannot be separated observationally (cf. H01 D3.2). "Herding" here is an *effective* coupling.
- **Specialization reads as AF in βJ_CW, by construction.** The negative values in #39, #40 and #42 are reproduced by the within-agent permutation null, so they are fields.
- **Small samples.**
  - Jackknife over 5 days gives 4 degrees of freedom.
  - #24's jackknife is unstable (SE 26.6).
  - Per-period power is ≈ 0.35 at |βJ| = 2 (synthetic S1).
- **Multiple comparisons.** 14 periods × about 10 statistics. The FM finding (z_N2 ≥ 4 in 9 periods) survives Bonferroni easily. The post hoc ownership correlation (p = 0.04) does not.
- **Amendments, with what I had seen when making them:**
  - (a) q ≤ 8 / 2% instead of q ≤ 6 / 5%. Made before any analysis, after seeing only label counts and q.
  - (b) The action-only label variant. Added after seeing #31's βJ_CW (+4.9); it did not change any sign.
  - (c) The local-shift null, ownership index, drift-corrected excess, the #31 named-project trajectories and the G26 notes. All post hoc, after the round-1 run.
  - (d) The G26 runoff-onset rule fired early; I did **not** amend it and report it as is.
  - Before predictions I had seen artifact-mention volumes per period, including holdout periods (counts only).
- **The #26 vote proxy** names 10 agents (it includes ballot organizers), not just the 6 candidates. Only candidate codes are stored, no text.
- **plmDCA null** is only 9 within-agent permutations, which do not absorb drift.
- **#19's concept choice** happened outside the artifact record, so HH25 is untested.

**Next steps**
1. Run the frozen holdout test after sign-off.
2. Separate drive from coupling with a kinetic, lagged Potts model using the `exposure` table. Does seeing a message that links project X raise the hazard of switching to X, beyond human or automated prompts?
3. File-level labels inside shared repos, to look for subtask division of labor below the repo level.
4. Concept-mention states for #19 (HH25) and task-assignment states for #13 (HH24).
5. NE15 as an intervention (axis E): herding should become block-local after the #best / #rest split.
6. Clean the #26 ballot: restrict to the candidate list and the runoff interval.

## Notes
- **2026-10-04, round 1b:** re-evaluated on the shared deterministic labels, DQ6 #26 ballots and the DQ4 work ledger (section "Round 1b" above). No card-level verdict changes; D 0 → 1.
- **From DQ6 (2026-10-04): the G26 "runoff" analysis measured the wrong election.** #26 had a 01-05 approval vote (9–9–9 tie) and a 7–1–0 runoff that closed in about 100 s, then a 01-09 confirmatory re-election (9–0). Nine of the ten declarations in this card's runoff snapshot are dated 01-09. Redo the vote tests per round with `ground_truth_labels` (`phase`, `ballot`, `tally`) in the re-evaluation wave.
- **From H31 (2026-10-04):** `modal()` breaks ties without `maintain_order`, so about 1% of labels flip between rebuilds; the confirmatory run must use the deterministic shared build. The #26 runoff winner's declared share rose 0.22 → ≥ 0.5 in 0.76 h, and many #18 and #26 projects reach a majority within one 30-min window: herding arrives as one-window waves.
- 2026-10-03: promoted from shortlist 2 (HH24 + HH26 + HH84 (shortlist 2, item 2)).
- 2026-10-03, **scheme amendment before analysis:** the first build used q ≤ 6 and a 5% share threshold. That gave q = 2 for #13 and #38, with long tails (47 and 74 distinct projects). Seeing only those structural counts, I changed to q ≤ 8 and 2% before any analysis. Raw unmerged labels are kept for robustness.
- 2026-10-03: exploratory round 1 run and assembled (see Results). Scheme amendment (q ≤ 8 / 2%) was made before analysis. The action-only robustness variant was added after seeing #31's βJ_CW, and the local-shift null and ownership index after the full run; all are flagged above.
- 2026-10-03: HH22 folded in as G26 by Vivian; G26 predictions written before running on #26. Vote states use `chat_mentions_clean.mentions_roster` (o1-bug-free), per the coordinator.

## Round 1b (improved data, 2026-10-04)

### What changed in the inputs
- **Project labels:** shared deterministic `project_states` (W = 15/30/60; ranking on non-holdout rows) instead of H11's own files, whose `modal()` broke exact ties nondeterministically. Against round 1, 633 of 7,802 W = 30 agent-windows (8.1%) change label: 111 tie re-picks, 499 renumberings, 52 in or out of "other" (reproduced exactly by `scheme/build_r1b.py`). Action-class labels get the same deterministic tie-break.
- **#26:** DQ6 `ground_truth_labels` ballots and phases (approval 9–9–9 tie, 7–1–0 runoff in ≈ 100 s on 01-05, 9–0 confirmatory vote on 01-09). Round 1's "runoff" jump and snapshot measured the 01-09 vote.
- **New state, work space:** **agent state (categorical, project, work ledger)**: the repo with the most agent work commits (DQ4 default filter `canonical & ~imported & author_kind == agent & ~automated`, author time) by agent i in window w; no commit = missing; same q ≤ 8 / 2% merging. Dense from #30. Proposed as a named variant for DEFINITIONS.md.
- **Code:** `scheme/build_r1b.py` writes `data/processed/H11-potts-labor-vs-herding/r1b/G<NN>/`; `analysis/h11data.py` reads it when `H11_LABELS=shared` (default `h11` keeps the round-1 path runnable); `analysis/round1b.py` runs the replication, the work-space version and the native tests.

### Predictions for the new round-1b analyses
*Written 2026-10-04 07:10 UTC, before running the replication, the work-space version or the native tests.* The pre-registered round-1 predictions above are unchanged and are re-scored as written.

**What I had seen when writing this:** the round-1 results; the label-change counts above; one timing run of the #31 attention replication on shared labels (βJ_CW +4.88, t 19.9, z_N2 +16.0 with 19 nulls); work-label row counts per period (e.g. #31: 286 work vs 423 attention agent-windows; #37: 84; #51: 8,508); #31's work-project table (its top three repos were committed to by 11, 9 and 8 distinct agents over the week, top share 0.19); the DQ6 #26 tallies and ballot timestamps; the H06, H28 and H53 headline results, including H53's #26 read-out finding (14/17 ballots cast by the call that read the round's opening message). I had not computed any work-space coupling, null, co-work rate or #26 snapshot fit.

- **R1b-1 (replication on shared labels).** The 14 tested periods keep their round-1 verdict category (P1 and P2) and the sign of βJ_CW, with |ΔβJ_CW| ≤ 1 in ≥ 12/14. Credence 0.8.
- **R1b-2 (work space, non-holdout periods #30 onward that pass the same minimum-data rule on work labels: ≥ 15 room blocks with ≥ 3 work-labelled agents at W = 30).** HH266 ("attention herds, work stays private") predicts z_N2(work) < 2 in most shared-artifact weeks where attention herds. My prediction is the opposite: work herds too, more weakly.
  - (a) In shared-artifact weeks (ownership index < 0.5), βJ_CW(work) > 0 and z_N2(work) ≥ 2 in at least half of the testable periods. Credence 0.55.
  - (b) The drift-corrected excess (βJ_PL − N2 mean) is smaller in work than in attention in ≥ 2/3 of the periods testable in both. Credence 0.65.
  - (c) Own-artifact weeks (#39, #40, #42): βJ_CW(work) ≤ 0 and z_N2(work) < 2 (spread by fields). Credence 0.6.
  - (d) The co-work rate (share of labelled agents whose raw project is shared by ≥ 1 block-mate in the same window) exceeds its N2 (circular-shift) null in shared weeks in both spaces; the work excess is smaller.
  - **HH266 is supported** if z_N2(work) < 2 in ≥ 2/3 of the shared-artifact weeks where z_N2(attention) ≥ 2, with a co-work excess near 0 in work. **Refuted** if (a) holds.
- **R1b-3 (#26 per election round; native, `G26/`).** Predictions in `goalperiod-subhypotheses/G26/README.md` (Round 1b section).
- **R1b-4 (#31 work-space wave; native, `G31/`)** and **R1b-5 (#40 hub vs own worlds in work; native, `G40/`).** Predictions in those period READMEs.

### Results (round 1b, run 2026-10-04)
Code: `scheme/build_r1b.py`, `analysis/round1b.py` (`replicate`, `work`, `g26`, `assemble`), `analysis/summary_figure_r1b.py`. Data: `data/processed/H11-potts-labor-vs-herding/r1b/` (`G<NN>/round1b.json`, `verdicts_round1b.parquet`, `cross_period_round1b.json`, `work/<unit>.json`, `work_vs_attention_r1b.parquet`, `g26_rounds_r1b.json`). Per-period estimates: `per_period_estimates` (H11, round 1b rows). 99 nulls per statistic (49 for #51 units).

**Layer 1, replication on shared labels (old → new).** Nothing changes that matters.

| Statistic | Round 1 | Round 1b |
| --- | --- | --- |
| βJ_CW > 0 (tested weeks) | 11/14 | 11/14; same sign in 14/14; max ΔβJ_CW 0.65 (#24: +3.25 → +2.60, still n.s.) |
| P1 per-period verdicts | – | identical in 14/14 |
| P2 per-period verdicts | – | identical in 12/14: #38 "failed (significant)" → "failed" (z_N2 +2.1 → +1.9); #40 "failed" → "weak" (−0.1 → +0.1) |
| Mode rule: sign test / AF < FM (Mann–Whitney) | 5/11, p = 0.73 / p = 0.47 | 5/11, p = 0.73 / p = 0.53 |
| Shared-artifact weeks with z_N2 ≥ 2 / with local-shift z ≥ 2 | 10/11 / 9 | 10/11 / 9 (#20 rises to +2.1, #38 falls to +1.9) |
| Ownership vs z_N2 (Spearman, post hoc) | −0.56, p = 0.04 | −0.53, p = 0.054 |
| P3 project-label consensus jumps | 0/4 | 0/4 |
| P4 action class AF vs FM | p = 1.0 | p = 1.0 (action-class labels unchanged by the deterministic tie-break) |
| P5 held-out gain where abs(z_N2) ≥ 2 | 8/10 | 10/10 |
| P7 abs(βJ_CW) < 2 | 0/14 | 1/14 (#30 +1.97) |

Monte Carlo noise: the same z_N2 drawn with a different null seed moves by up to ≈ 0.5 near z = 2 (#38: +1.9 in the replication run, +2.4 in the work run). Verdicts that hinge on z ≈ 2 (#20, #38) are not stable.

**Work space (#30 onward; R1b-2).** 18 units: #30–#44 whole, #51 split into its seven non-holdout units with ≥ 3 active days (unit of analysis rule). Work labels cover 37–75% of the attention agent-windows; #37 has too few work blocks (12 < 15).

| Unit | ownership (att / work) | z_N2 attention | z_N2 work | excess att / work | co-location att / work (N2 mean) | work repo = attention project |
| --- | --- | --- | --- | --- | --- | --- |
| #30 | 0.00 / 0.00 | +5.1 | +0.8 | +1.60 / +0.43 | 0.94 / 0.86 (0.85) | 0.83 |
| #31 | 0.07 / 0.13 | +14.1 | +7.2 | +2.36 / +1.87 | 0.69 / 0.54 (0.47) | 0.69 |
| #33 | 0.06 / 0.05 | +22.0 | +9.0 | +1.66 / +1.97 | 0.94 / 0.94 (0.94) | 0.97 |
| #35 | 0.01 / 0.00 | −2.5 | +2.2 | −0.58 / +2.77 | 0.98 / 1.00 (0.98) | 0.98 |
| #37 | 0.13 / 0.29 | +7.8 | +2.3 (n/a: 12 blocks) | +3.16 / +1.38 | 0.63 / 0.58 (0.53) | 0.78 |
| #38 | 0.12 / 0.11 | +2.4 | +1.8 | +0.42 / +0.62 | 0.78 / 0.75 (0.71) | 0.85 |
| #39 (own) | 1.00 / 1.00 | −1.2 | all private (no shared repo) | – | 0.12 / 0.00 | 0.97 |
| #40 (own + hub) | 0.26 / 0.27 | −0.1 | +0.6 | −0.04 / +0.43 | 0.78 / 0.73 (0.73) | 0.96 |
| #41 | 0.10 / 0.25 | +5.3 | +3.8 | +1.43 / +1.13 | 0.72 / 0.65 (0.61) | 0.89 |
| #42 (own) | 0.73 / 0.74 | +1.1 | +1.4 | +0.99 / +1.13 | 0.23 / 0.20 (0.18) | 0.94 |
| #44 | 0.51 / 0.74 | +5.0 | +1.3 | +1.98 / +0.77 | 0.43 / 0.18 (0.14) | 0.80 |
| #51 units (7) | 0.57–0.75 / 0.71–0.97 | −0.7 to +5.7 | ill-determined (see caveat) | – | 0.18–0.30 / 0.04–0.21 | 0.56–0.88 |

- **(a) Work herds in shared-artifact weeks: supported.** βJ_CW(work) > 0 and z_N2(work) ≥ 2 in 4/6 testable shared weeks (#31, #33, #35, #41; not #30, #38).
- **(b) Work coupling is weaker than attention's: not supported** (work excess below attention's in 4/9 testable periods #30–#44; 3/5 where attention herds).
- **(c) Own-artifact weeks are spread in work too: supported** (#39 βJ_CW at the lower bound, every work label private; #40 −17.4, z +0.6; #42 −2.4, z +1.4).
- **(d) Co-location above the shift null in shared weeks: 4/6 in attention, 4/6 in work;** the excesses are about equal (#31: +0.07 vs +0.07).
- **HH266 ("attention herds, work stays private") is not supported in shared-artifact weeks:** of the 5 shared weeks where attention herds, work also has z_N2 ≥ 2 in 3 (#31, #33, #41), with #30 and #38 below 2. Agents' work repo equals their attention project in a median 84% of agent-windows with both labels (56–98%). Attention labels mostly measure where work goes.
- **Where work *is* more private than attention (post hoc): own-artifact and private-role units.** Co-location in work vs attention: #44 0.18 vs 0.43, #51 units 0.04–0.21 vs 0.18–0.30 (51a 0.06 vs 0.30; 51g 0.04 vs 0.18), #39 0.00 vs 0.12. There agents look at each other's artifacts more than they commit to them.
- **Reconciling with H06 (post hoc):** most *projects* are private, most *work* is shared. In shared weeks 25–67% of work repos have one committer (singletons), yet 71–100% of work agent-windows go to repos with ≥ 2 committers (#31: 25% singletons, 87% of work on shared repos; top three repos 43%). In own-artifact weeks the effort share on shared repos drops (#39 0.00, #42 0.38, #44 0.26; #51 0.63 vs 0.88 in attention). H06 counted species (fragmented intention topics); H11 weighs effort.

**Native layer (R1b-3 to R1b-5).**
- **#26 per election round (`G26/`; mixed).** On the correct election, the runoff goes from an exact symmetric point (all 9 voters approved all three tied candidates) to 7/8 for DeepSeek-V3.2 in 83 s, and the 01-09 vote confirms it 9–0: P-G26b's jump holds on DQ6 ground truth. Snapshot coupling βJ_snap = 3.2 [1.05, 6.0] vs βJ_s(3) = 2.75 (inconclusive, as predicted); independent symmetric voters give ≥ 7/8 with p = 0.008. **My field prediction failed:** only 3/8 runoff ballots were cast having seen ≤ 1 earlier ballot (mean 2.6 seen; predicted ≥ 5/8), and DeepSeek-V3.2 led the visible candidate mentions for 0/8 voters (Gemini 2.5 Pro led for 7/8). The runoff looks like a ballot cascade seeded by the first ballot (a candidate voting for a rival), not a pre-set field. The confirmatory vote is the opposite: 6/9 ballots cast with no earlier ballot seen, all for the incumbent (a field).
- **#31 work wave (`G31/`; supported).** Work herds: βJ_CW +4.04 (t 10.7), z_N2 +7.2, local-shift z +4.5; weaker than attention (excess 1.87 vs 2.36); 9 agents committed to one repo in one 30-min window (predicted ≤ 6; attention 11); work repo = attention project in 69% of agent-windows.
- **#40 hub vs own worlds (`G40/`; mixed).** Work is spread by fields as predicted (βJ_CW −17.4, z_N2 +0.6), but the hub carries as much work as attention (0.73 vs 0.74 of labelled agent-windows; predicted ≥ 0.2 lower) and ownership is the same (0.27 vs 0.26). HH266 fails here too.

**Verdict changes.** None at the card level. P1 stays mixed by rule (substantively failed), P2 failed, P3 failed (0/4 on project labels; the #26 vote jump holds on the correct election but the mechanism stays at threshold), P4 and P5 supported (P5 now 10/10). New: work-space herding in shared-artifact weeks (R1b-2a supported; HH266 not supported), and the runoff's ballot-visibility pattern points to a cascade rather than my predicted field (n = 8).

**Caveats (round 1b).**
- **#51 work PL is ill-determined:** most #51 work agent-windows fall into "other" (each agent has its own repo; q ≤ 8), so βJ_CW sits at the grid bound and z_N2 swings (−4.4 to +3.0). Use co-location there.
- **#35 contradicts the frozen C2 rule:** a shared-artifact week (ownership 0.01) with z_N2(attention) = −2.5. Had it been a holdout target, C2 would be refuted. Disclose before running `confirm_holdout.py`.
- Work is commits (author time) of agents with public repos: regime I is too sparse; bulk commits in #40 count once per commit.

**Scorecard changes (round 1b):** D 0 → 1 (the effective coupling found in attention predicts coupling in an independent output channel, work commits, in 4/6 shared weeks and spread in 3/3 own-artifact weeks; the #26 jump holds on the correct election); others unchanged (C stays 1: P5 10/10 but drive vs coupling still unseparated; I stays 0: #35 contradicts the post hoc pattern in attention). Ratings suggested: complete 40 → 50, faithfulness 1.5 (unchanged), usefulness 2.0 → 2.5 (the attention-based herding statistic now tracks duplicated *work*, not only attention).

## Round 2 redirects (2026-10-04)
*From the round-1 reflection (`writeup/round1-reflection/round1-reflection.pdf`).*
- **Where round 1 went sideways:** The sign of the Potts coupling was tied to goal mode, but herding appears regardless of mode, which points to a mechanism.
- **What the direction is really after:** Why do agents pile on: imitation, or attraction to where the work already is?
- **H11-R1.** Preferential attachment: P(join X) ∝ (recent activity on X)^α. With α near 1 this is a Yule process, which predicts the project-size distribution (E2).
- **H11-R2.** Herding is stigmergic, not social: artifact activity predicts joining better than chat mentions of X (E3, vs H28).
- **H11-R3.** Herding is a coordination solution that raises output; own-artifact spread duplicates effort (test against the work ledger).
