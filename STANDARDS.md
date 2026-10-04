# Shared standards

Every hypothesis, re-evaluation, data build and write-up follows these rules. They collect what rounds 1 and 1b taught us (`writeup/round1b-synthesis/round1b-synthesis.pdf`). Where a rule has a home file, this page points to it rather than copying it. Research goals: [`GOALS.md`](GOALS.md).

## 1. The four impostors
Each one has produced fake collective order in this project at least once. Every claim of coupling, influence, collective order or emergence must say how it removes each impostor, or why it does not apply.

| Impostor | What it fakes | How to remove it | Reference |
| --- | --- | --- | --- |
| **Scheduler field** | Activity synchrony, collective modes, irreversibility at day edges | Trim to the all-present window (DQ8); use block-shift nulls with an edge; use per-call clocks (H40) | H38, H50, H12, H26, `infra/README.md` |
| **Exogenous field** (kickoff, goal, operator) | Content alignment, herding, "leaders" | Regress on `goal_fields` directions and operator messages; use kickoff-matched placebos | H54, H10, H24, H32 |
| **Shared model priors** (family, style) | Family "fields", conventions, assembly "selection" | `style_resid`; leave-period-out agent means; cross-family and first-day controls | H13, H46, H80 |
| **Contemporaneous convergence** | Copying, contagion, influence | In-flight placebo: compare read vs posted-but-unread at a matched lag; use the blind window before read-out | H57, H32, H34, H28, H41 |

**Audit of H01–H59 (2026-10-04): the most common gaps.** Close these first in any round 2.
- **Convergence is open in 19 cards.** Equal-time co-movement statistics have no read vs posted-but-unread placebo at a matched lag. Only H06, H07, H08, H28, H29 and some of H32/H34/H41 remove it.
- **Shared priors are open in 13 cards.** These lack `style_resid` and a cross-family control.
- **The exogenous field is partly handled in about 33 cards.** No card regresses on `goal_fields` directions or uses a kickoff-matched placebo as standard. Do both.
- **The scheduler field is handled everywhere.** It is partly handled where a trim-then-block-shift null was never run (H01, H13, H14, H22, H31, H35, H58) or a swarm/EP block was not re-run (H09, H16).
- In the impostor table, the **Status** column is `removed`, `partly`, `open`, or `n/a` (impostor not relevant).

**Shared-field gauge (H86, 2026-10-04):** report `taylor_c_shared` (c_×, channel `activity_trim`) and `taylor_phi_shared` per unit. Taylor's c_T and b are not field gauges for clocked agents (b < 1).

## 2. Inputs (use these, not the old tables)
- **Activity:** `activity_bins_fixed`, `outages_fixed`. The old `activity_bins` dropped about half the events.
- **Visibility and exposure:** the context ledger (`call_windows`, `context_ledger_items`, `context_ledger_turns`). A message acts at the recipient's **receiving call**.
- **Work and productivity:** the DQ4 `work_ledger` (agent commits; separate the automated streams). Active minutes measure attention, not work.
- **Failures:** `turn_outcomes.failed` or `behavior_states_v3.n_errors`. Never use `actions.error`, which is "stderr non-empty".
- **Content:** DQ5 vectors with **both** embedding models (bge, gte), `style_resid` and `statement_flags` (dedupe).
- **Nudge targets:** the leading-@ target. **Ground truth:** DQ6 `ground_truth_labels`. **Replies and stance:** DQ2 (parents are partly content-selected; see Known issues).
- Read `infra/README.md` "Known issues" before every build. Add any new issue you find there, in the report, not silently.

## 3. Nulls and calibration
- Use DQ8's null-size table. If a null is not in it, size the null on synthetic data at real counts and report the size.
- Day-level nulls: trim first, then use block shifts. Never use cross-day surrogates on untrimmed activity.
- Information measures (A, A*, NTIC, Ψ, Ω): compare against **size-matched** random groupings, because these measures do not decrease as the system grows. Remove fields by regression and leave-one-out means, never by subtracting a leave-in mean, which fakes synergy.
- Negative claims need power: a synthetic power of at least 0.8 at the effect size that would matter. Without it, the verdict is "inconclusive".
- Report a placebo for every event study: other days, other boundaries, other rooms.

## 4. Design
- **Unit of analysis:** one goal period, split at step changes (`period_units.parquet`). Fit within periods. Compare periods as points on a phase diagram. Never pool periods completely; the exceptions are listed in `CLAUDE.md`.
- **Two layers** (Vivian, 2026-10-04):
  - *Replication:* the common estimator on every eligible period, role `replication`.
  - *Natives:* 2–4 period-native tests that use leverage only that period has (DQ9 `period-affordances.md`, `natural-experiments.md`), each with its own dated prediction, role `native`.
- Write the prediction and the null in the card **before** running on real data. Label every later change as a dated amendment, and say whether it is post hoc.
- **Holdout:** locked (`hypotheses/holdout.md`).
  - Mask it in every exploratory script with `holdout_mask`. Do not print held-out counts.
  - Write the confirm script frozen and guarded; it runs only with Vivian's sign-off.
  - Re-freeze any confirm script built on old inputs before it runs.

## 5. Reporting
- Write per-period rows to `per_period_estimates` with `write_estimates`. Give CIs with `ci_kind` from the allowed set. Report the unit count (n units) and units for every number.
- Give every number with an uncertainty, a scope (periods, regime, channel) and its source table.
- Card: Round sections are dated, with old → new tables, a scorecard A–I, and round-2 redirects. Each Round section ends with one line, `**Claim that stands:**`. It is one scoped clause with its key number, plus a named list of exclusions (withdrawn, post hoc or unpowered sub-results). Raters score that clause (RUBRIC adjudication rule 1).
- Summary (2 pages): `content.tex` in the house style, and `meta.json` with v1 ratings, `one_line` and `models`. The coordinator writes `v2`.
- Code: put every new input behind a switch so that earlier rounds reproduce exactly. Every `data/processed/` folder has a `_provenance.json`.

## 6. Writing style
Follow "Writing style" in `writeup/hypothesis-pages/RUBRIC.md`:
- **Physicist voice:** degrees of freedom → model → measurement → result with error bars → impostors removed.
- **ASD-STE100-leaning sentences:** one idea each, ≤ 25 words, active voice, one term per meaning, no filler words.
- **Operator value:** one or two instructions with a number.

Terms follow `physics-models/DEFINITIONS.md`. Add a named variant there rather than redefining a term.

## 7. Scoring
Use Scoring v2 (`writeup/scoring/scoring-v2.pdf`, `RUBRIC.md`):
- A scoped claim.
- A credence from the evidence ladder. Count one design once.
- Mechanism level M0–M2 and a fragility flag.
- V, EU = p·V, and S.
- Independent raters for anchors: a disagreement beyond Δp 0.25 or ΔV 1 is adjudicated.

## 8. Shared code
- If two hypotheses need the same builder, move it into `infra/shared/` with a `--verify` and register it in `build_all.py`.
- Never import from another hypothesis's folder in new code.

## 9. Compute
- **Pools:** at most 2 workers per process, and one heavy job at a time per agent. Do not run parallel background jobs.
- **Thread caps:** the venv's `sitecustomize.py` sets BLAS, OpenMP and polars threads to 2 by default. Override only with a reason.
- **Why:** with 15–20 agents on the machine (10 cores), uncapped pools and implicit BLAS threads drove the load to 249 (2026-10-04). Jobs crawl and agents time out.

## 10. Data and safety
- `data/` is never committed.
- No verbatim agent text in committed files.
- No training on the data.
- Agent narration is a claim, not ground truth.
- Keep within the storage budget (20 GB total; ≲ 100 MB per hypothesis unless justified).
