# H128: Free kickoffs coarsen, named kickoffs freeze: a kinetic Potts quench

**Status:** exploratory round 1 **done (2026-10-04, non-holdout only): HH369's kill is met. Free and named kickoffs give the same post-kickoff project curves, and free weeks lose projects by finishing, not merging.** Card and predictions written 22:15–22:18 UTC before any real-data statistic; Amendment A1 (22:37 UTC) after the synthetic, before real data; A2 post hoc. Approved by Vivian in the dashboard vetting panel 2026-10-04 from HH369.
- **Primary observable (A1):** the domain-wall fraction dw = (N_p − 1)/(N_h − 1). The HH-literal count N_p tracks how many agents hold a label, not how many domains there are (it reads per-agent freezes and pure finishing as "slow" in 100% of synthetic runs).
- **Kill contrast (P3) failed:** freeze time free vs named, one-sided exact Mann–Whitney p = 0.32; excess area p = 0.73 (7 free vs 5 named testable units). A true Potts coarsening vs field freeze would give p < 0.05 with power 0.96–1.00 on these skeletons, so the null is powered.
- **P1 (free weeks coarsen as t^−α):** 1/7 (G30, α̂ 0.44 [0.32, 0.60]). **P2 (named weeks freeze within 3 h):** 1/5 (G39, frozen at dw = 1: one world per agent). **P4 (merging, not finishing):** merge share 0.00–0.38 in 7/7 free units; finishing (label expiry) carries most project deaths.
- **Natives:** G44 rooms failed (the free room stays scattered at dw ≈ 0.92; the named room drifts down); NE42 failed (the named merge week is the only coarsening-like curve, dw 1 → 0.2 over 16 h, α̂ 0.26; the free split week fragments, dw 0.3 → 0.6); G37 replicas descriptive.
- Scorecard A1 B1 C0 D1 E0 F1 G1 H1 I0. `analysis/confirm.py` (held-out kickoffs #46–#49) frozen and dry-run; **not run**.
**Question (GOALS.md):** **Q2** (what is field and what is coupling: does a free kickoff leave a coupling-driven coarsening that a named kickoff's field skips?), with **Q5** second (what a kickoff's wording does to the time a swarm takes to settle).
**Fields:** stat mech (zero-temperature quench, phase-ordering kinetics, coarsening exponents), sociophysics (voter and majority dynamics, consensus times), dynamics (relaxation shape: power law vs exponential vs step)
**Literature:** no coarsening paper is filed in `literature/`. Background named, not filed (†): Bray, "Theory of phase-ordering kinetics", *Adv. Phys.* 43, 357 (1994)†; Castellano, Fortunato & Loreto, "Statistical physics of social dynamics", *Rev. Mod. Phys.* 81, 591 (2009)† (voter coarsening, consensus times); Kingman, "The coalescent", *Stoch. Proc. Appl.* 13, 235 (1982)† (mean-field voter: number of surviving opinions ∝ 1/t). Speed-limit context: [Kolchinsky, Dechant, Yoshimura & Ito 2026](../../literature/kolchinsky-2026-generalized-free-energy-excess-housekeeping.md) (via H75's slack).
**Definitions used** (`physics-models/DEFINITIONS.md`): Agent; Regime; Driving / external field (the kickoff); *Agent state (categorical, project, work ledger)* (H11 round 1b) as carried by *Host (work ledger, call-clock expiry)* (H77/H78, `infra/shared/replicator_hosts.py`, W = 30, E = 100); *Birth*, *Departure*, *Expiry* (H77/H78); H75's *settling time* (for comparison only). New named variants proposed (defined under Observables; DEFINITIONS.md not edited): **active project count N_p(t) (H128)**, **merge-only project count N_p^m(t) (H128)**, **freeze time t_f (H128)**, **coarsening exponent α (H128)**, **project death kind (H128)**, **kickoff code (assigned artifact, H128)**.
**From:** HH369 in `hypotheses/hypohypotheses/HYPOHYPOTHESES.md` · **Models:** `physics-models/10-potts/` (primary: kinetic Potts quench with and without a field)
**Builds on:** H75 (named kickoffs freeze at the speed limit, slack 1.0–1.4; free ones churn, 5–15), H95 (the slack splits kickoffs by whether the goal assigns an artifact; post-hoc code), H93 (choice logit: habit b_own 2.5–6 nats; βĴ not identified as J), H94 (work quanta, ownership price), H77/H78 (host replay; most arrivals are formation).
**Data inputs (shared tables first):** DQ4 `work_commits` through `infra/shared/replicator_hosts.py` (agent-work filter, host labels, events), `call_windows` (expiry clock), `calendar` (active windows), `period_units`, `roster` (leave times), `ground_truth_labels` (`room_assignment`, #44), `rooms_timeline` (#37 rooms, through `infra/shared/rooms_asof.py`), `context_ledger_items` (read tags, inside `replicator_hosts.tag_arrivals`). No message text is stored; repo names are hashed on output.

## Source HH (verbatim from the HH list, including refinements)
- **HH369 · Free kickoffs coarsen, named kickoffs freeze: a kinetic Potts quench.** In a zero-temperature Potts quench, many small domains merge and the number of distinct domains falls as a power of time (coarsening). A strong field (a named project) skips coarsening and freezes at once. H75 found named kickoffs freeze instantly (slack 1.0–1.4) and free ones are slow (5–15).
  - *Prediction:* in free-kickoff weeks, the number of active projects falls as t^(−α) with α ≈ 0.3–0.5 over the first days; in named-kickoff weeks it drops to its final value within hours, with no power-law stretch.
  - *Check:* H94/H77 project tables; active projects per active hour from each kickoff; fit power law vs exponential vs step.
  - *Kill:* the free and named curves have the same shape.
  - *Impostors:* projects finish for exogenous reasons (deadlines); exclude finished-and-shipped projects from "merged" counts.
  - *Models:* 10 · *Builds on:* H75, H94, H93

## Question
After a goal kickoff, does the number of distinct projects that agents work on fall slowly, as a power of time, when the kickoff leaves the target open? And does it drop at once to its final value when the kickoff names the target?

## Design: two layers (STANDARDS §4)
- **Replication** (role `replication`): the common estimator on the first 20 active hours after the kickoff of every non-holdout period with a dense work ledger: G30, G31, G33, G35, G36, G37, G38, G39, G40, G41, G42 and G51 (51a kickoff; #51's horizon is 2.5 days of 8 h, before the NE32 joins of 07-09).
- **Natives** (role `native`):
  - **N1 · G44 rooms.** #best is told to fine-tune a named leader; #rest picks its own goal. Same days, same scaffold: a named vs free pair with everything else fixed.
  - **N2 · NE42 A-B-A (G39 → G40 → G41).** Same roster of 15. Labels are carried across the two boundaries. On 05-04 the rooms merge and the goal names a shared target ("connect your worlds"); on 05-11 the rooms split and the goal is free ("novel research").
  - **N3 · G37 room replicas.** Two rooms with identical free kickoff text on the same days: two independent quenches from the same field.
- **Confirmation:** held-out kickoffs #45–#50, coded from goal titles only (see Confirmatory design). Written into `analysis/confirm.py`; not run.

## Model
**From:** `physics-models/10-potts/` ("Dynamics: a kinetic Potts model has each agent's next state drawn from a softmax"; "Social-dynamics relatives: voter model … Potts-like coarsening dynamics").

**H128 variant: a kinetic Potts quench on repo labels, with births.** Each committing agent i carries a host label σ_i(t) (its current repo). It updates only at its own work windows (30-min windows with an agent work commit). At an update it picks repo j with
P(j) ∝ exp(βJ s_j + h_j + b_own [j = σ_i]), plus a "new repo" option with weight exp(α_new),
- s_j: share of the other hosts on j; βJ > 0 is the ferromagnetic coupling (herding onto occupied repos);
- h_j: the kickoff field. *Free kickoff:* h_j ≈ 0 for every repo. *Named kickoff:* h_T ≫ 1 on a shared target T, or h_{T_i} ≫ 1 on one target per agent (own world, own channel, private goal);
- b_own: habit (H93: 2.5–6 nats);
- α_new: formation (births).

**The quench.** The kickoff changes h at t = 0. Agents start scattered: each agent's first post-kickoff label is a random, mostly new repo (a high-temperature start).
- **Free (h = 0, βJ > 0): coarsening.** Projects merge as their last hosts move to occupied repos. In the mean-field voter limit the number of surviving projects falls as N_p ∝ 1/t (Kingman coalescent, α = 1 asymptotically). Habit slows the clock but not the exponent. At N ≈ 12–15 only one decade of decline exists, and the pre-asymptotic exponent is smaller. HH369 expects α ≈ 0.3–0.5.
- **Named, shared target: freeze.** Each agent's first update lands on T. N_p drops to its final value N∞ within one round of first commits (≤ 1–2 active h) and stays.
- **Named, one target per agent: freeze at N.** Each agent lands on its own target. N_p ≈ N_h from the first round on. There is nothing to coarsen.
- **Exogenous finish (impostor).** With βJ = 0, projects end when work on them stops (deadlines, shipped). N_p falls, but through expiries, not merges. The merge-only count N_p^m stays flat.

## Data scheme (`scheme/build.py`)
- **Inputs:** `replicator_hosts.load_commits`, `load_calls`, `leave_times`, `window_labels` (W = 30), `replay_events` (E = 100), `classify_arrivals`, `tag_arrivals` (read tags; text only in memory inside the shared code); `calendar`; `ground_truth_labels` (`room_assignment`, #44, `preferred & ~holdout`); `rooms_asof` (#37). Holdout days dropped by `replicator_hosts.period_days` (`holdout_mask`).
- **Transform:**
  1. **Host replay** per goal period on non-holdout days (shared code, defaults W = 30, E = 100). Events: birth, recruit, depart (with `to_repo`), expire, leave.
  2. **Active clock.** Concatenate the period's calendar windows from the kickoff (`win_start` of the first day); t in active hours. Events outside a window snap to the nearest window edge if ≤ 15 min away, else they are dropped and counted.
  3. **Horizon** H = min(20 active h, the period's active length); #51: the first 20 active h (2.5 days).
  4. **Grid:** 15 active minutes. At each grid point: hosts N_h, distinct hosted repos N_p, merge-only count N_p^m, effective number K_eff = 1/Σ p_j² (p_j = hosts on j / N_h).
  5. **Project death kind** (when a repo's host count falls to 0): *merge* (its last host departs to a repo that already has a host), *hop-new* (its last host departs to a repo born at that moment), *finish* (its last host expires or leaves). N_p^m keeps finished repos counted until the horizon end: only merges and hop-new deaths lower it.
  6. **Initial condition.** Primary: every agent starts unlabelled at the kickoff (labels from the previous period are not carried). Variant (N2 only): labels carried from the previous period's last day.
  7. **Rooms** (natives): #44 by DQ6 room assignment (host counted in its room); #37 by the agent's room at the event (`rooms_asof`).
- **Output:** `data/processed/H128-coarsening-vs-freeze/G<NN>/curve.parquet` (unit, t_active, N_h, N_p, N_p_m, K_eff), `deaths.parquet` (hashed repo, t_active, kind), `events.parquet` (hashed), `results.json`; `synthetic/`; `results/`; `_provenance.json`. Expected < 10 MB.
- **Regimes covered:** I (#30, #31), II (#33, #35, #36), III (#37–#42, #44, #51). DQ4 has dense git from #30 on.

## Observables
- **O1 · Shape class** of N_p(t) on the fit window [t_pk, H], where t_pk is the first time N_p reaches its maximum within the first 8 active hours. Four least-squares fits on the 15-min grid:
  - *constant* N̄ (1 parameter);
  - *step* N0 → N∞ at t_s (3);
  - *exponential* N∞ + (N0 − N∞) e^{−(t−t_pk)/τ} (3);
  - *power law* A (t − t_pk + 0.25 h)^{−α} (2), the HH's form. Variant with an offset: N∞ + A(·)^{−α} (3).
  Selected by BIC with n_eff = the fit window's length in active hours (≥ 4). The synthetic calibrates this rule (axis F); a failed rule is replaced by a dated amendment before the real run.
- **O2 · Coarsening exponent α̂** from the power-law fit, with a 95% interval from a 2-h moving-block residual bootstrap (500 draws).
- **O3 · Freeze time t_f:** the first grid time after which N_p stays within ±max(1, 0.15 N∞) of N∞ until H. N∞ = the median of N_p over the last 20% of the horizon. Censored when it first holds after 0.8 H.
- **O4 · Decline ratio** R_d = N_pk / N∞.
- **O5 · Merge share** c_m = merge deaths / all project deaths in [t_pk, H]. Plus the same curve statistics on N_p^m (impostor control) and on K_eff (variant).
- **O6 · Normalized excess area** A_u = ∫ u(t) dt over [t_pk, t_pk + 8 h], with u(t) = (N_p(t) − N∞)/(N_pk − N∞) (0 when N_pk = N∞). In hours. A step at once gives ≈ 0; slow coarsening gives several hours.
- **O7 · Read share of merges:** the share of merge arrivals tagged `read` by `tag_arrivals` (a ledger-read chat link to the target before the move), vs `self`.

## Null / baseline
- **Freeze baseline (named):** constant or step shape with t_f ≤ 3 active h.
- **Shape-free null (the kill):** free and named units draw their curves from one distribution. Test: one-sided Mann–Whitney on t_f and on A_u between the kickoff codes (exact p).
- **Exogenous-finish null:** projects die only by expiry or leave. Then N_p falls but N_p^m does not, and c_m ≈ 0.
- **Synthetic worlds on the real skeleton** (below): the decision rule's false-classification rates under each world.

## Impostors (STANDARDS §1)
| Impostor | Relevant? | How it is handled | Status |
| --- | --- | --- | --- |
| Scheduler field | partly | Active-hour clock (calendar windows); labels carry over nights; expiry runs on the agent's own call clock, so nights and day starts are not label changes. Day-1 fill-in (agents' first commits) sets t_pk and is excluded from the fit window. | removed |
| Exogenous field (kickoff, goal, operator) | yes | The kickoff field is the object (named vs free code, fixed before data). Deadlines and shipped projects: the merge-only count N_p^m and the death kinds (finish vs merge). Mid-week operator messages are not removed; noted per period. No `goal_fields` regression: the state is categorical and the field enters through the code. | partly |
| Shared model priors | partly | In a free week every LLM may pick the same "obvious" project at once, which looks like a freeze without a named field. Reported: lab mix of the largest project at t_pk; G37's two rooms (N3) are a replica check. No style control applies to repo labels. | partly |
| Contemporaneous convergence | partly | Coarsening by copying and coarsening by independent convergence give the same curve. The shape test does not need to separate them; the coupling reading does. O7 reports the read share of merges (`tag_arrivals`), not a matched-lag in-flight placebo. | open |

## Synthetic validation (axis F; before any real-data statistic)
`analysis/synthetic.py`. Skeleton: each period's real agents, their real work windows (agent × 30-min window with ≥ 1 commit, in real order) and real calls (for E-expiry). Synthetic repo labels are drawn per window and replayed through the same shared host code and the same curve code. Worlds (100 runs each):
- **Q0 coarsening:** h = 0, βJ = 4, b_own = 2, α_new falling from 0 at t = 0 to −4 by 2 active h (a scattered start, then few births). First update of each agent: a new repo.
- **Q0w weak coarsening:** βJ = 2.
- **Q1 shared field:** h_T = 6 on one target, βJ = 4.
- **Q2 per-agent field:** h_{T_i} = 6 on each agent's own target.
- **Q3 exogenous finish:** βJ = 0, h = 0; each project ends after an exponential lifetime (mean 4 active h) and its host starts a new repo.
**Decision rule fixed now:** the shape test is valid on a skeleton if (a) Q0 is classified as *not freeze* (power or exponential, t_f > 3 h) in ≥ 0.7 of runs, (b) Q1 and Q2 are classified as freeze (constant or step, t_f ≤ 3 h) in ≥ 0.8 of runs, and (c) the merge-only count of Q3 has c_m ≤ 0.2 and is classified as freeze or constant in ≥ 0.8 of runs. The α band in P1 is scored only if Q0's α̂ has |bias| ≤ 0.2 and median CI width ≤ 0.6 on that skeleton; otherwise "not identified".

## Faithfulness scorecard
Scored per model, mapping and window; 0 = not done or failed, 1 = partial, 2 = passed. Scheme and promotion thresholds: `writeup/paper.tex`, Sec. "Assessing model faithfulness".
**Rival models:** (R1) exogenous finish (projects end by deadline, no merging); (R2) instant freeze for every kickoff (H75's R2: the field always names a target, explicitly or by genre prior); (R3) exponential relaxation with one time scale (H54's τ ≈ 5 h; H75's field-limited settling).
**Locked holdout used for confirmation:** held-out kickoffs #45–#50 (planned; see Confirmatory design).

| Axis | Test | Score | Evidence |
| --- | --- | --- | --- |
| A mapping | variables defined from dataset fields; assumptions listed; invariant across families and regimes | 1 | Host labels from the DQ4 work ledger (shared replay, W 30, E 100); dw defined from counts. The HH's N_p is confounded by the host count (A1). Same mapping in regimes I–III. |
| B assumptions | stationarity, Markov order, time-rescaling, update-order audit | 1 | The quench assumes a scattered start and constant fields. Real free weeks start concentrated and fragment (G41 dw 0.30 → 0.62); labels lapse on the call clock, so domains also die by expiry. |
| C adequacy | beats the null hierarchy, day-blocked held-out data | 0 | The kickoff code does not order freeze time or excess area (p 0.32, 0.73). The freeze baseline holds in 1/5 named units. |
| D unfitted predictions | unfitted statistics and the model's signature | 1 | The model's signature, merging domains, is absent: merge share 0.00–0.38 in 7/7 free units (unfitted). Read share of merges 0–1.0 (few merges per unit). |
| E interventional | predicts the change across a natural experiment | 0 | NE42 and G44 go the wrong way: the named shared-target boundary coarsens slowly; the free boundary and the free room do not coarsen. |
| F identifiability | synthetic recovery with village sampling; robust to preprocessing | 1 | dw passes the decision rule on 12/13 period skeletons; N_p passes on 0/16. Power vs exponential is not identified (power selected in ≤ 0.48 of true-coarsening runs). Kill contrast powered (0.96–1.00). |
| G ground truth | agrees with known structure | 1 | Own-artifact weeks sit at dw ≈ 1 throughout (G39 1.00, G51 0.97), as expected; the #44 #best team is the only room that converges. |
| H comparative | beats the named rivals | 1 | R1 (exogenous finish) explains the death kinds; R3 (exponential) ties or beats the power law in 4/7 free units (ΔBIC < 2). R2 (instant freeze everywhere) fails too: most named weeks are not frozen. |
| I transfer | holds in other same-mode periods, including the holdout | 0 | Holdout not run. |

## Prediction
*Written 2026-10-04 22:15–22:18 UTC, before running any H128 statistic on real data.*

**What I had seen when writing this:** the cards of H75, H95, H93, H94, H77, H78 and H54 and their headline numbers (H75 slacks: G39 1.00, G40 1.25, G41 5.09, G51 1.40, G44 #best 2.5 / #rest 14.5; T_e 0.25–9.5 h; H95's assigned-artifact code separating S 1.0–2.5 from 3.0–14.5; H93's per-period counts of choice events 48–1,477 and of repos 2–133; H77/H78: 76–100% of arrivals are formation, 66% of recruitments are returns); goal titles; per-period active hours from `calendar`. Not seen: any project-count curve, any death kind, any shape fit.

**Kickoff code (fixed now, from the goal title; H95's assigned-artifact rule extended to #30–#36).** *Named* (the goal assigns a concrete artifact, shared or one per agent): #35 (test your game: the #34 RPG), #39 (own world), #40 (connect the worlds into one universe), #42 (own YouTube channel), #44 #best (fine-tune a named leader), #51 (private assigned goals). *Free* (open or objective only): #30 (adopt a park: the park is chosen), #31 (pick your own goal), #33 (discuss and act on the news), #36 (interact with agents outside), #37 (pick your own goal), #38 (choose a charity), #41 (novel research), #44 #rest (free). Disclosure: H95's code was post hoc and agrees with H75's slacks, which I have seen.

**Testability rule (fixed now).** A unit is testable if N_p reaches ≥ 4 at t_pk with ≥ 6 hosts, and H ≥ 10 active h. Otherwise descriptive.

| ID | Prediction | Counts against | Credence |
| --- | --- | --- | --- |
| P1 (HH, free) | In testable free units, the power law is selected, α̂'s 95% interval overlaps [0.3, 0.5], and t_f > 3 h, in ≥ 2/3 of them | power law not selected or t_f ≤ 3 h in > 1/3 | 0.25 |
| P2 (HH, named) | In testable named units, the shape is constant or step with t_f ≤ 3 h and no power-law selection, in ≥ 2/3 of them | power law selected or t_f > 3 h in > 1/3 | 0.55 |
| P3 (kill contrast) | Free units have later t_f and larger A_u than named units: one-sided exact Mann–Whitney p < 0.05 on both | p ≥ 0.05 on either (HH369's kill: same shape) | 0.45 |
| P4 (coarsening, not finishing) | In free units with a decline (R_d ≥ 1.5), merges are ≥ half of project deaths (c_m ≥ 0.5) and N_p^m declines too (not classified constant) | c_m < 0.5, or N_p^m flat while N_p falls (R1, exogenous finish) | 0.30 |
| P5 (rival R3) | In free units, the power law beats the exponential by ΔBIC ≥ 2 in ≥ 1/2 of them | the exponential wins or ties in > 1/2 | 0.30 |
| Kill (HH369) | the free and named curves have the same shape: P3 fails | — | P(kill) 0.5 |

**Natives (role `native`; predictions per folder).**
- **N1 G44 rooms:** #rest has t_f > 3 h and a larger A_u than #best; #best freezes (t_f ≤ 3 h). Credence 0.6.
- **N2 NE42:** with labels carried, the 05-04 boundary (merge plus named shared target) reaches its new final level within 3 active h; the 05-11 boundary (split plus free) takes > 3 h. Credence 0.45.
- **N3 G37 replicas:** both rooms are classified the same (both slow or both frozen), and |t_f(A) − t_f(B)| ≤ 3 h. Credence 0.5.

**My expectation, stated before data.** H93 and H94 found that agents mostly stay on their own repos and that 76–100% of arrivals are formation. So I expect free weeks to settle slowly through churn and births rather than by merging. P1's power-law form and P4's merge share are the weak points; P2 and the contrast P3 are likelier.

Per-period predictions are in each `goalperiod-subhypotheses/G<NN>/README.md`, written before that period is run.

### Amendment A1 (2026-10-04 22:37 UTC, after the synthetic validation, before any H128 statistic on real data)
*What I had seen:* the synthetic summaries (`data/processed/H128-coarsening-vs-freeze/synthetic/summary.json`; 60 runs per world on 16 skeletons: 13 periods, #44 and #37 rooms) and the skeletons' sizes. No real curve, death kind or fit.
1. **The HH-literal count N_p fails the decision rule on every skeleton.** In the per-agent field world Q2 and the exogenous-finish world Q3, N_p is classified "slow" in 100% of runs on 15/16 skeletons. N_p tracks the number of hosts (agents drop in and out through call-clock expiry and day starts), not the number of domains. **Primary observable from now on: the domain-wall fraction dw(t) = (N_p − 1)/(N_h − 1)** on grid points with N_h ≥ 2: 0 when every host shares one project, 1 when every host is alone. N_p stays as the HH-literal secondary; its verdicts are reported, not scored.
2. **dw passes the rule on 12 of 13 period skeletons.** Q0 (βJ = 4) is "not freeze" in 0.73–1.00 of runs, Q1 and Q2 freeze in 0.80–1.00 (G40: Q2 0.70, fails (b)), Q3 freezes in 1.00 with merge share c_m = 0. Room skeletons: #44 #best is too small (N_h < 6, untestable), #44 #rest fails (a) (Q0 freezes in 0.32 of runs), #37 #best has < 2 committing hosts (dw undefined), #37 #rest passes.
3. **Shape (power vs exponential) is not identified.** Under true kinetic Potts coarsening (Q0) the power law is selected in 0.00–0.48 of runs (median ≈ 0.1); the exponential usually wins. So P1, which needs the power law selected, would be scored "supported" in at most about half of the free units even if HH369 were exactly right, and P5 is underpowered. Both are scored as written; a "slow" free unit without a power law is "mixed" by the period rule, which now reads as "coarsening-compatible, shape not identified".
4. **α is a coupling-dependent effective exponent.** α̂ on dw: Q0 median 0.53–0.83, Q0w (βJ = 2) 0.08–0.61; run-to-run SD 0.08–0.21 and median bootstrap CI width 0.15–0.45. The card's "bias" criterion has no ground truth (no planted exponent), so it is replaced by run-to-run SD ≤ 0.2 and median CI width ≤ 0.6: met on 12/13 period skeletons (G38 SD 0.21). The α band [0.3, 0.5] is scored where met; it is a coupling range, not a universality class.
5. **Rule changes (pre-data, needed by the density observable):** tolerance for t_f on dw = max(1/(N̄_h,end − 1), 0.15 dw∞) (one domain's worth); freeze = t_f ≤ 3 h and the power law not selected (step, constant or a fast exponential: a shared target's fill-in is a fast drop on dw); testability = N_h ≥ 6 at the peak and H ≥ 10 h, with N_p ≥ 4 required only for an α fit (a named week that freezes onto one repo has N_p < 4 and must stay testable).
6. **Natives:** N1 is scored as written but carries the caveat that #best is below the testability floor and #rest fails rule (a); N3 is descriptive (#37 #best has < 2 hosts).
Not amended: the kickoff code, the periods, roles, P2–P4 thresholds, the kill (on dw), credences.

## Results by goal period
| Period | Role | Verdict | Key numbers |
| --- | --- | --- | --- |
| [G30](goalperiod-subhypotheses/G30/README.md) | replication | supported | free; dw slow, power α̂ 0.44 [0.32, 0.60], t_f 4.75 h; merge share 0.27 |
| [G31](goalperiod-subhypotheses/G31/README.md) | replication | mixed | free; dw slow (censored), constant shape; merge share 0.36 |
| [G33](goalperiod-subhypotheses/G33/README.md) | replication | failed | free; frozen at dw ≈ 0.08 from 0.5 h (one shared repo) |
| [G35](goalperiod-subhypotheses/G35/README.md) | replication | mixed | named; N_p constant at 2 (frozen) but dw slow (host-count noise) |
| [G36](goalperiod-subhypotheses/G36/README.md) | replication | mixed | free; dw slow, flat at 0.44 |
| [G37](goalperiod-subhypotheses/G37/README.md) | replication + native N3 | mixed | free; dw rises (+0.011/h); N3 descriptive (#best < 2 hosts) |
| [G38](goalperiod-subhypotheses/G38/README.md) | replication | mixed | free; dw slow decline (−0.015/h), step shape; merge share 0.10 |
| [G39](goalperiod-subhypotheses/G39/README.md) | replication | supported | named per agent; frozen at dw = 1.00 from 0.25 h |
| [G40](goalperiod-subhypotheses/G40/README.md) | replication | failed | named shared; slow power-law decline, α̂ 0.20 [0.11, 0.30], t_f 15.75 h; merge share 0.60 |
| [G41](goalperiod-subhypotheses/G41/README.md) | replication | mixed | free; fragments, dw 0.30 → 0.62 (+0.021/h) |
| [G42](goalperiod-subhypotheses/G42/README.md) | replication | mixed | named per agent; dw 0.77 → 0.86, slow |
| [G44](goalperiod-subhypotheses/G44/README.md) | native N1 | failed | #rest (free) flat at dw 0.92; #best (named, 4 hosts) drifts down |
| [G51](goalperiod-subhypotheses/G51/README.md) | replication | mixed | named per agent; dw 0.97 flat, one dip sets t_f 7.25 h |
| [NE42](goalperiod-subhypotheses/NE42/README.md) | native N2 | failed | merge (named): dw 1 → 0.2, α̂ 0.26 [0.19, 0.35]; split (free): dw 0.3 → 0.6 |

## Results
### Exploratory round 1 (2026-10-04; non-holdout only)
- **Code:** `analysis/h128lib.py` (active clock, curves, fits, Potts quench generator), `analysis/synthetic.py`, `scheme/build.py`, `analysis/run.py`, `analysis/figures.py`, `analysis/confirm.py` (frozen, dry-run only).
- **Data:** `data/processed/H128-coarsening-vs-freeze/` (per unit `curve.parquet`, `deaths.parquet`, `meta.json`; `G<NN>/events.parquet` hashed; `synthetic/`; `results/`; `confirm_dryrun/`; `_provenance.json`; < 5 MB).
- **Figures:** [`figures/summary_obs.pdf`](figures/summary_obs.pdf) (dw curves by kickoff code; freeze time and drift per unit), [`figures/summary_synth.pdf`](figures/summary_synth.pdf) (synthetic freeze rates by world, dw vs N_p).
- **Estimates:** 64 rows in `per_period_estimates` (`h128_freeze_time_dw`, `h128_excess_area_dw`, `h128_coarsening_alpha_dw`, `h128_merge_share`; jackknife-over-agents or bootstrap intervals).

**Outcome vs prediction**

| Prediction | Outcome | Verdict |
| --- | --- | --- |
| P1 free: power law, α in [0.3, 0.5], t_f > 3 h in ≥ 2/3 | 1/7 (G30); 6/7 are slow but 5 of them are flat, rising or step-like | failed |
| P2 named: freeze (t_f ≤ 3 h, no power law) in ≥ 2/3 | 1/5 (G39) | failed |
| P3 free later t_f and larger A_u than named (p < 0.05) | t_f p = 0.32, A_u p = 0.73 (N_p version p = 0.56); power 0.96–1.00 | failed: HH369's kill is met |
| P4 merges ≥ half of deaths where free units decline | 0/3 declining free units (G31, G37, G38); c_m 0.00–0.38 in 7/7 | failed |
| P5 power beats exponential (ΔBIC ≥ 2) in ≥ 1/2 free | 3/7 (G33, G36, G38) | failed |
| N1 G44: #rest slow, #best frozen | #rest scattered and flat; #best drifts down | failed |
| N2 NE42: named boundary ≤ 3 h, free > 3 h | both slow; the named one coarsens, the free one fragments | failed |
| N3 G37 replicas | #best room < 2 hosts | descriptive |

**Synthesis.**
1. *The kickoff's naming does not set the shape of re-allocation in project space.* On dw, free and named units overlap in freeze time and in excess area. The contrast is powered: a Potts coarsening vs a field freeze would separate them with power ≥ 0.96.
2. *Free weeks do not coarsen.* They stay scattered (G44 #rest dw 0.92), fragment after a concentrated start (G41, G37, G33) or decline slowly (G30, G38). Where projects disappear, finishing (label expiry) dominates: merge share ≤ 0.38. That is rival R1, the exogenous finish.
3. *Own-artifact kickoffs freeze trivially at dw ≈ 1* (G39 1.00, G51 0.97): one project per agent from the first round. H75's instant freeze at the speed limit is this per-agent freeze; it is not a skipped coarsening.
4. *The one coarsening-like curve follows a shared target meeting a scattered start* (A2, post hoc): G40 after the NE42 merge, dw 1 → 0.2 over 16 active h with α̂ 0.20–0.26 and merge share 0.60–0.72. That is the reverse of HH369's assignment: the named shared target drives slow merging, and the free goal fragments.
5. *Amendment A2 (post hoc, disclosed): signed drift of dw after the peak* (OLS slope, Kendall τ). Negative (merging direction, p < 0.05): G30, G38 (free), G40, G44 #best (named). Positive (fragmenting): G33, G37, G41 (free), G42 (named). The code does not set the sign either.

**Claim that stands.** After a goal kickoff, the domain-wall fraction of agents' work projects does not separate free from named kickoffs (freeze time p = 0.32, excess area p = 0.73, 7 vs 5 units, power ≥ 0.96), and free weeks lose projects by finishing, not merging (merge share 0.00–0.38 in 7/7): HH369's coarsening-vs-freeze split is killed. *Excluded:* the coarsening exponent (shape not identified by the synthetic), the post hoc drift signs (A2), the NE42 coarsening reading (one boundary, post hoc).

### Confirmatory design (frozen 2026-10-04 in `analysis/confirm.py`; dry-run on stand-ins only, NOT RUN)
Targets: held-out kickoffs coded from goal titles only: free #46, #47, #49; named #48; #45 and #50 reported, not scored. C1: at most 1 of 3 free targets is "supported" by the period rule (HH369 absent). C2: at most 1 of 3 free targets has a significant negative dw drift. C3: merge share < 0.5 in ≥ 2 of 3 free targets. Dry run (stand-ins free #36, #38, #41; named #40): C1, C2, C3 pass; a pipeline check, not evidence. Guards: `--confirm` plus `H128_CONFIRM=1`, sha256 freeze (`confirm.sha256`), `holdout_ledger.check()` (family `project_potts`, modality work). Disclosure: H95's agent read #45–#50 setup lines (#47 #best's Help Kit live within 11 min); #45–#47 and #50 work allocation is planned by H75, H77, H78, H93, H94, H95.

## Round 2 redirects (proposed by the round-1 agent, 2026-10-04)
- **H128-R1. A per-agent field strength, not a kickoff code.** H95-R1's share of agents whose first post-kickoff commit lands on their settled repo; test dw drift against it.
- **H128-R2. Separate finishing from abandonment.** Expiry mixes "shipped" and "dropped"; use deploy/README commits (DQ4 `deploy_msg`) to tag finished projects.
- **H128-R3. Shared target into a scattered start.** NE42 suggests coarsening needs both. Test it on held-out #45 (follow the leader after #44) once frozen.

## Notes
- 2026-10-04 22:15 UTC: round-1 agent (H128 together with H129). Card written before any H128 statistic. Compute: ≤ 2 threads, one heavy job at a time; no LLM labels.
- 2026-10-04 22:37 UTC: Amendment A1 after the synthetic (before real data). 22:40 UTC: real run, estimates, figures. 22:43 UTC: confirm.py frozen and dry-run (guards tested: refuses without the freeze and without H128_CONFIRM=1).
