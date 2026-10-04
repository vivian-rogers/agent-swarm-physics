# H125: The kickoff response is a damped oscillator: look for the day-2 undershoot

**Status:** exploratory round 1 **done (2026-10-04): failed. The kickoff response is overdamped: day 1 overshoots, then the excess decays to its settled level within two active days without swinging below it.**
- **Undershoot (P1, failed by the kill clause, powered).** U = −0.006 [−0.020, +0.008] (bge) and −0.002 [−0.017, +0.013] (gte), 90% CI, 27 kickoffs; 12/27 positive; not beyond 80 placebo-day origins (Mann–Whitney p 0.79 / 0.69). The synthetic at the observed overshoot gives power 1.00 for ζ ≤ 0.5.
- **Overshoot replicates (S1, supported).** E₁ = +0.055 ± 0.012 (bge, 22/27) and +0.062 ± 0.015 (gte, 23/27). Day 2 keeps +0.02, day 3 sits at 0.
- **Natives:** G51 own roles (N = 21) failed (fade, no swing); NE38 failed (a one-agent step neither overshoots nor undershoots); G38 passes its ring-down rule but weakly (size 0.19–0.26; the two models disagree on ζ and period).
- Card and predictions written 22:16 UTC before any real-data statistic; Amendment 1 (22:29 UTC) after the synthetic. `analysis/confirm.py` frozen and dry-run (reproduces the stand-ins exactly); **not run**. Scorecard A1 B1 C1 D1 E1 F2 G1 H1 I1.
**Question (GOALS.md):** **Q2** (what is field and what is coupling): is the day-1 overshoot toward the kickoff an inertial swing (agents carry plans past the target and swing back) or a field that fades? Second: **Q5** (when to read the steady state after a new goal).
**Fields:** stat mech (vector spins under a step field), dynamics (damped harmonic oscillator vs overdamped relaxation)
**Literature:** none in `literature/` covers damped relaxation of opinions or content. Background from memory: Landau & Lifshitz, *Mechanics* §25 (damped oscillations; logarithmic decrement)†. Project cards: H97 (restoring force, overshoot a_K +0.12), H54 (kickoff target; kickoff remanence 0.24 → 0.11), H96 (goal switch is a quench), H103 (remanence decays on the active-hour clock; nights re-orient slightly toward the goal), H48 (content settles with τ ≈ 4.5 active h), H36 (post-kickoff alignment drift).
**Definitions used** (`physics-models/DEFINITIONS.md`): Agent (Claude Code agent 19 and fine-tuned agents 28, 30 excluded); Regime (whitening per regime, every series inside one regime); Driving / external field (the kickoff, shared `goal_fields`; #51 `agent_goal` for the natives); Activity time, in H103's named variant **active-hour clock H**; Agent state, variant *vector*, as unit regime-whitened statement vectors (d = 32, DQ5); H54's **quench target (kickoff)** with H54/H103's genericness correction; H97's **overshoot intercept a_K** (as background). New named variants proposed (defined under Observables; DEFINITIONS.md not edited): **kickoff excess alignment a(h)**, **undershoot U**, **overshoot E₁**, **peak-ratio damping ζ_pk**, **fitted damping ζ_fit**.
**From:** HH366 in `hypotheses/hypohypotheses/HYPOHYPOTHESES.md` · **Models:** `physics-models/11-vector-spins/` (primary: content spins under a stepped field), `physics-models/02-nonequilibrium-ising/` (secondary: the overdamped mean-field relaxation τ₀ṁ = −m + h(t) as the rival)

## Source HH (verbatim from the HH list, including refinements)
- **HH366 · The kickoff response is a damped oscillator: look for the day-2 undershoot.** H97 found a day-1 overshoot toward the goal (+0.12). An overdamped spin cannot overshoot; an underdamped one (inertia plus restoring force, x″ + γx′ + kx = 0) overshoots and then undershoots. Inertia here would be agents carrying their own momentum (plans, open tasks) past the target.
  - *Prediction:* the alignment with the goal direction, relative to its settled level, goes positive on day 1 and negative on day 2–3 (an undershoot), with the ratio of the two peaks giving the damping ratio ζ < 1. If ζ ≥ 1 (no undershoot), the overshoot is a field that fades (the kickoff text's salience), not inertia.
  - *Check:* H97's kickoff-aligned series per active hour, both models; fit damped-oscillator vs overdamped-plus-fading-field on all 18 kickoffs.
  - *Kill:* no undershoot beyond placebo days in either model.
  - *Impostors:* a fading kickoff field mimics overshoot without undershoot. That is exactly the rival this tests. Scheduler: active-hour clock (H103).
  - *Models:* 11, 02 · *Builds on:* H97, H54, H96

## Standards (2026-10-04)
**Question served:** Q2 (field vs inertia in the kickoff response), Q5 (when the steady state can be read).

| Impostor | Relevant? | How it is handled | Status |
| --- | --- | --- | --- |
| Scheduler field | yes | The time axis is H103's active-hour clock (nights removed). The fits carry a 4-slot time-of-day profile, because H103 found a morning re-orientation toward the goal (+0.03). U compares whole days 2–3 with whole days 4–5, so each side holds the same slots and the same number of nights. The oscillation half-period is bounded to 0.5–4 active days, so a within-day profile cannot fit as an oscillation. | removed (by design; checked in synthetic world W_tod) |
| Exogenous field (kickoff/goal/operator) | yes | The fading kickoff field is the rival (M_fade). A later operator re-kick along k̂ would fake an undershoot (days 4–5 rise). Variant: drop kickoffs with a human message on days 4–5 of the period; covariate: human messages on days 4–5 minus days 2–3 (`kicks_classified`). The genericness correction removes the generic pull of every kickoff text. | partly |
| Shared model priors | yes | U and the window series use within-agent contrasts (agent offsets cancel; fixed incumbents, so composition is constant). Variant `statements_style_resid_period32`. Both embedding models. | removed |
| Contemporaneous convergence | no | No agent-to-agent influence claim. The object is the swarm's response shape to a common field. | n/a |

**Inputs:** DQ5 `embeddings/statements.parquet` + `statements_white32_{bge_small,gte_modernbert}.npy` and `statements_style_resid_period32_*.npy`; `statement_flags` (`self_repeat_both`, dedupe variant); shared `goal_fields` (`embeddings/goals.parquet`, `goal_vectors*.npy`, whiteners via `embed_models.load_whitener`); `calendar`; `period_units`; `roster`; `kicks_classified` (human messages); H54 `kickoffs.parquet` (t0, read-only); `holdout_mask`. No text is read.

**Two layers:** replication on every eligible kickoff (role `replication`); natives G51 (own-role alignment of ~21 agents), NE38 (one-agent reassignment) and G38 (longest regime-III shared-kickoff period: room for a second swing), role `native`.

**Confirm script:** `analysis/confirm.py`, frozen and guarded, not run.

## Question
After a goal kickoff, the swarm's content moves toward the kickoff and overshoots its settled level on day 1 (H97, H54). Does it then swing below the settled level on days 2–3 (an underdamped oscillator, inertia), or decay to it from above (an overdamped spin under a fading field)?

**Practical payoff:** if the response rings, an operator who reads day 2–3 content as "the swarm lost the goal" is wrong, and the settled level appears only after the second swing. If the field fades, the day-2 level is already a lower bound on the steady state.

## Model
**From:** `physics-models/11-vector-spins` (agent content states in the regime-whitened 32-d basis, the kickoff as a step field along k̂). The order parameter is the swarm's excess alignment along k̂, A(h) = ⟨a_i(h)⟩_i, on the active-hour clock h since the kickoff time t₀.

**H125 variant: two response laws for the same step.**
- **M_osc (HH366, inertia):** ẍ + 2ζω₀ẋ + ω₀²(x − x_∞) = 0 after the step. Solution with ζ < 1:
  A(h) = A_∞ + B e^{−λh} cos(ω_d h + φ) + s(slot),  λ = ζω₀, ω_d = ω₀√(1 − ζ²).
  Five shape parameters (A_∞, B, λ, ω_d, φ) plus 3 slot effects. ζ_fit = λ/√(λ² + ω_d²). The half-period π/ω_d is bounded to [0.5, 4] median active days of the period.
- **M_fade (rival, overdamped + fading field; model 02):** τ₀ẋ = −(x − g(h)), g(h) = g_∞ + g₁e^{−h/τ_f}. The solution is a sum of two decaying exponentials:
  A(h) = A_∞ + c₁e^{−h/τ₁} + c₂e^{−h/τ₂} + s(slot).
  Five shape parameters plus 3 slot effects, so SSE compares directly with M_osc. A sum of two exponentials crosses A_∞ at most once. Starting below (the pre-kickoff level), it rises, peaks above A_∞ and decays from above: an overshoot without an undershoot. A critically damped M_osc (ζ = 1) is a limit of M_fade.
- **Model-free signature:** with the settled level A_∞ = the days 4–5 level, M_osc with a day-1 peak and ζ < 1 predicts days 2–3 below A_∞ (U > 0); M_fade predicts days 2–3 at or above A_∞ (U ≤ 0).

**Peak-ratio damping:** E₁ = the day-1 excess over A_∞ (overshoot), E₂ = the days 2–3 excess (= −U). For successive extremes half a period apart, δ = ln(E₁/|E₂|) and ζ_pk = δ/√(π² + δ²). ζ_pk is defined only when U > 0; otherwise ζ_pk ≥ 1 ("no undershoot").

**Rivals:**
- **R1 fading field (M_fade):** HH366's own rival; U ≤ 0, ζ ≥ 1.
- **R2 monotone drift:** M_fade plus a slow decline of alignment as work diversifies (H36's drift, topic turnover); U < 0.
- **R3 time-of-day field:** a daily morning re-orientation (H103 +0.03) with no inertia; it can fit as a within-day wiggle on 30-min bins, not as a day-scale U.
- **R4 operator re-kick:** a human message along k̂ on days 4–5 raises A_∞; U > 0 without inertia.
- **R5 wrap-up return:** end-of-period reports re-cite the goal; U > 0 if day 5 is a wrap-up day. Variant: A_∞ from day 4 only.

## Data scheme (`scheme/`)
`scheme/build.py` builds `data/processed/H125-kickoff-damped-oscillator/` from shared tables only. No text is read.
- **Eligible kickoffs (replication):** goal periods with a shared kickoff (`goals.kind = kickoff`), a non-holdout kickoff day and ≥ 5 non-holdout active days from day 1, all in one regime; #2 (no kickoff) and #23 (H10 keeps it blind) excluded. Counts seen before writing this card: 27 kickoffs (#4, 5, 6, 8, 10–13, 16–21, 24–27, 30, 31, 35, 38–42, 51), 4–21 incumbents. #3, #33, #37 and #44 have < 5 days. 17 of H97's 18 are included (#36 has a regime boundary on day 2).
- **t₀:** H54's first kickoff message time (shared-room row), else `goals.win_start`.
- **Incumbents:** agents with ≥ 1 statement on day 1 after t₀ (later joiners excluded, so composition is fixed).
- **Statements:** every statement of an incumbent on days 1–10 of the period (non-holdout, `holdout_mask` asserted), plus the previous active day and day-1 statements before t₀ (segment `pre`, for H127). Per statement: row index into the shared arrays, agent, t, pt_date, day index, active-hour clock h (active hours since t₀, summed over `calendar` windows, as H103), slot (quarter of the day's calendar window), segment.
- **Vectors:** per kickoff, model and regime basis, unit k̂ = unit(W_r · kickoff) for the own kickoff and every decoy (`vectors.npz`).
- **Natives:** G51 (#51 days 1–10 from 07-06; each agent's own `agent_goal` vector valid on 07-06); NE38 (#51, 07-24 → 08-07, the window around Opus 5's reassignment at 07-29 16:51 UTC, new role gid 242); G38 (#38 days 1–15).
- **Output:** `kickoffs.parquet`, `stmt.parquet`, `vectors.npz`, `_provenance.json`; analysis outputs in `G<NN>/`, `NE34/` (cross-kickoff), `natives/`, `synthetic/`.
- **Regimes covered:** I, II (#35), III.

## Observables
*Specified 2026-10-04 22:16 UTC, before any real-data statistic along a kickoff direction.*
- **Kickoff excess alignment (per statement):** a_s = ⟨z_s, k̂_p⟩ − mean_q ⟨z_s, k̂_q⟩, z_s the unit regime-whitened statement vector; decoys q = every other eligible non-holdout kickoff of any period except p − 1, p + 1 and #23, whitened in p's regime basis (H54/H103 genericness correction). It is linear in the statements. No window or day vector is renormalized, so the amplitude bias of cosines on unit window vectors (infra Known issues, H96) does not enter, and nothing is a slope between normalized segments (H97 issue).
- **Agent-day level:** A_id = mean of a_s over agent i's statements on day d (≥ 3 statements). Day 1 uses statements after t₀.
- **Undershoot (primary):** U_i = mean(A_i4, A_i5) − mean(A_i2, A_i3) for agents with ≥ 1 eligible day in each pair; U = mean_i U_i (equal agent weights, within-agent contrast). SE: agent jackknife. U > 0 means days 2–3 sit below the days 4–5 level.
- **Overshoot:** E₁ = mean_i (A_i1 − mean(A_i4, A_i5)).
- **ζ_pk** from E₁ and U as in the Model (per kickoff, and from the meta means).
- **Window series and fits:** 30-min windows on the active-hour clock over days 1–5: A_w = mean over agents of (agent's window mean of a_s − the agent's mean over all its fit windows). M_osc and M_fade fitted by weighted least squares (weight = agents in the window; multistart). Statistics: ΔSSE = (SSE_fade − SSE_osc)/SSE_fade; the winner; ζ_fit with an agent-bootstrap CI (100 draws).
- **Placebo-day U (P_days, the HH's placebo):** the same U on pseudo-origins d inside the same goal period and regime, along the same k̂_p: U_d = mean(A_{d+3}, A_{d+4}) − mean(A_{d+1}, A_{d+2}), d ≥ 6 (past the kickoff transient), days d … d + 4 inside the non-holdout period. Available in the long periods (#4, 6, 8, 13, 18–20, 27, 38, 51).
- **Decoy-direction U (P_dir, kickoff-matched placebo):** the same U over the same days and agents along each decoy direction q (excess against the other decoys). Own-k̂ percentile π_U among the decoys.
- **Covariate:** human messages (`kicks_classified` kind `human_message`, not kickoff) on days 4–5 minus days 2–3.

## Null / baseline
- **N0 placebo days (P_days):** U at ordinary origins, same k̂, same agents' period. A kickoff U is "beyond placebo" when the kickoff U distribution exceeds the placebo U distribution (Mann–Whitney, one-sided).
- **N1 decoy directions (P_dir):** the same days and agents along other kickoffs' directions.
- **N2 agent jackknife** within kickoff for every per-kickoff SE; across kickoffs a DerSimonian–Laird random-effects mean and a sign test. Periods are never pooled into one fit (each kickoff is fitted on its own; exception (c), the step response is the object).
- **N3 synthetic worlds** on the real skeleton (axis F): W_fade, W_fade + drift, W_fade + time-of-day profile, W_fade + day-4 re-kick, W_osc (ζ 0.2, 0.5), at the real statement times, agents and clocks, with noise calibrated on decoy-direction projections (no k̂ statistic).

## Faithfulness scorecard
Scored per model, mapping and window; 0 = not done or failed, 1 = partial, 2 = passed. Scheme and promotion thresholds: `writeup/paper.tex`, Sec. "Assessing model faithfulness".
**Rival models:** R1 fading field (M_fade, model 02 overdamped); R2 monotone drift; R3 time-of-day field; R4 operator re-kick; R5 wrap-up return.
**Locked holdout used for confirmation:** none yet. Planned: held-out kickoffs with ≥ 5 days (`analysis/confirm.py`, frozen, not run).

*Scorecard plan (filled after round 1):* A from the dataset mapping and both models; B from the active-hour clock and slot audit; C from U against both placebos; D from U and ζ_pk (unfitted signatures of M_osc); E from NE38 (one-agent step); F from the synthetic worlds; G none direct (DQ6 roles for NE38/G51); H from M_osc vs M_fade; I from transfer across regimes and the holdout.

| Axis | Test | Score | Evidence |
| --- | --- | --- | --- |
| A mapping | variables defined from dataset fields; assumptions listed; invariant across families and regimes | 1 | Linear excess alignment from DQ5 statements and shared `goal_fields`, genericness-corrected; both models and style/dedupe variants agree. The target is a text proxy; day 1 includes restating the kickoff. |
| B assumptions | stationarity, Markov order, time-rescaling, update-order audit | 1 | Active-hour clock with slot effects (H103); U balances slots and nights. Calendar windows that span village-off gaps (#6 day 3, #51 day 2) lengthen the clock. |
| C adequacy | beats the null hierarchy, day-blocked held-out data | 1 | The overdamped reading matches the placebo-day null (U inside it) and the decoy null (π_U 0.39 / 0.43); no held-out test yet. |
| D unfitted predictions | unfitted statistics and the model's signature | 1 | The unfitted signature of M_osc (U > 0, ζ_pk < 1) is absent; M_fade's (U ≤ 0) is present. ζ itself is bounded only from below (≥ 1, or ≥ 0.5 at the stated power). |
| E interventional | predicts the change across a natural experiment | 1 | NE38: a one-agent step gives a monotone approach, as M_fade predicts; one agent only. |
| F identifiability | synthetic recovery with village sampling; robust to preprocessing | 2 | 9 worlds × 40 replicates on the real skeleton, both calibrations: P1 size 0.00, power 1.00 (ζ 0.2, 0.5); P2's liberal size and ζ_fit's uninformativeness found before real data (Amendment 1). |
| G ground truth | agrees with known structure | 1 | Reassignment time and roles from DQ6 / `agent_goals` (NE38, G51). |
| H comparative | beats the named rivals | 1 | R1 (fading field) beats HH366's M_osc on U; M_osc still wins SSE in 18–19/27 single fits (liberal, size 0.12–0.20). R4 (re-kick) and R5 (wrap-up) checked by variants. |
| I transfer | holds in other same-mode periods, including the holdout | 1 | U ≤ 0 in regimes I and III and in 7/8 input variants; holdout not run. |

## Prediction
*Written 2026-10-04 22:16 UTC, before running the analysis on real data.*

**What I had seen when writing this:** the round-1 cards of H97 (overshoot a_K +0.12 ± 0.02, gte +0.17), H54 (day-1 kickoff excess 0.24 → plateau 0.11; #51 agents land on their own goals with no decay over 9 weeks), H103 (remanence decays on the active-hour clock in 17/22 periods; across the night alignment rises +0.03 relative to a midday split), H96 (quench), H48 (τ ≈ 4.5 active h, single-exponential settling fails in about half of periods), H36 (monotone post-kickoff drift). Counts only for H125: eligible kickoffs, incumbents per kickoff, non-holdout days per period (H103's `periods.parquet`). No alignment statistic computed.

**Primary predictions** (meta-analysis across kickoffs; per-kickoff numbers are descriptive):

| ID | Prediction | Counts against | Credence |
| --- | --- | --- | --- |
| **P1** undershoot (HH366) | U > 0 with meta 90% CI above 0 **and** kickoff U above the placebo-day U distribution (Mann–Whitney one-sided p < 0.05), in **both** embedding models (white32) | Kill: neither holds in either model (U meta ≤ 0, or not beyond placebo days) | 0.2 |
| **P2** model comparison | M_osc beats M_fade (ΔSSE > 0) in ≥ 2/3 of kickoffs, sign test p < 0.05, both models | M_fade wins in ≥ half | 0.2 |
| **P3** damping ratio | ζ_pk from the meta means < 1 (U > 0) and the median ζ_fit over kickoffs where M_osc wins < 1 with its CI below 1 | U ≤ 0 (ζ_pk undefined, ≥ 1) | 0.2 |

**Secondary:**

| ID | Prediction | Counts against | Credence |
| --- | --- | --- | --- |
| S1 | The overshoot replicates in this estimator: E₁ > 0, meta CI above 0, in ≥ 2/3 of kickoffs, both models (H97/H54) | E₁ ≤ 0 | 0.85 |
| S2 | If an undershoot exists, it is larger in regime III (continuous context carries open tasks) than in regime I: U(III) > U(I), Mann–Whitney one-sided p < 0.1 | reversed or equal | 0.3 |
| S3 | P1's sign survives `style_resid_period`, dedupe (`self_repeat_both`), A_∞ from day 4 only (R5), and dropping kickoffs with a human message on days 4–5 (R4) | sign flips in ≥ 2 variants | 0.5 |
| S4 | Own-k̂ percentile among decoy directions (P_dir): median π_U > 0.5 with sign test p < 0.05 | median ≤ 0.5 | 0.25 |

**Native predictions** (each also in its folder README):

| ID | Unit | Prediction | Counts against | Credence |
| --- | --- | --- | --- |
| N1 | G51 (#51 kickoff 2026-07-06; ~21 agents, private roles) | Own-role excess alignment (decoys = the other agents' roles, near-duplicates with cos > 0.95 dropped) undershoots: U_own > 0 with 90% CI above 0 in both models | U_own ≤ 0 or CI includes 0 | 0.15 |
| N2 | NE38 (#51, Opus 5 reassigned 2026-07-29 16:51 UTC) | Opus 5's own-new-role alignment overshoots on day 1 and undershoots on days 2–3: its U exceeds the 90th percentile of the other #51 agents' own-role U over the same days, both models | Opus 5's U within the others' range | 0.15 |
| N3 | G38 (#38, 15 analysed days, 12 agents) | With room for a second swing, M_osc beats M_fade on days 1–10 (ΔSSE > 0) with ζ_fit < 1 in both models | M_fade wins in either model | 0.15 |

**Overall verdict rule:** **supported** if P1 holds; **failed** if the kill clause holds (U not beyond placebo days in either model); **mixed** otherwise (e.g. one model only, or U > 0 but within placebo). P2–P3 grade the model fit; S1 is a setup check (if S1 fails, P1 is "inconclusive": no overshoot to swing back from).

**Per-kickoff replication rule (templated):** supported if U > 0 with jackknife 90% CI above 0 and U above the 95th percentile of the pooled placebo-day U (bge, white32); failed if U ≤ 0; mixed otherwise; descriptive if fewer than 4 agents have both day pairs.

**Multiplicity and power.** Three primaries share one design (count once). The synthetic run states the power for P1 at ζ = 0.2 and 0.5 and the size under W_fade, W_fade + drift, W_fade + time-of-day before the real run. If the power at ζ = 0.5 is below 0.8, a P1 miss is reported as "inconclusive at ζ ≥ 0.5".

**Amendment 1** (2026-10-04 22:29 UTC, after the calibration and the synthetic run, before any real-data statistic along a kickoff direction; the calibration used decoy directions only). `analysis/calibrate.py` (variance components on decoy directions: statement SD ≈ 0.09, agent-window SD ≈ 0.05, agent-day SD ≈ 0.035, agent-offset SD 0.03–0.06) and `analysis/synthetic.py` (40 replicates × 9 worlds on the real skeleton of the 27 kickoffs, both models' calibrations; `synthetic/results_{bge,gte}_white.json`).
1. **P1 is calibrated as written.** Size 0.00 in every null world (W_fade τ 3 and 8 h, W_drift, W_tod, W_rekick at 0.04, W_noisy with day noise ×2). Power 1.00 at ζ 0.2 and 0.5 (overshoot amplitude 0.12, H97's a_K) and 0.55–0.57 at half that amplitude (ζ 0.5). Under a fading field U is negative (−0.01 to −0.06): the days 2–3 still carry the decaying excess, so U is conservative.
2. **P2 is liberal** under heavy day noise and a day-4 re-kick (size 0.12–0.20; M_osc wins 56–59% of single kickoffs with no inertia). P2 counts only together with P1 (one design) and is reported with this size.
3. **P3 changes (not post hoc on real data).** ζ_fit < 1 holds by construction of M_osc (null worlds give median ζ_fit 0.15–0.42 among M_osc winners), so "median ζ_fit < 1" is uninformative. P3 now reads: ζ_pk < 1 from the meta means (equivalent to U > 0), and ζ_fit is interpreted only if P1 holds (recovery 0.20 at a planted 0.2, 0.40 at 0.5). ζ_pk is biased low when ringing persists into days 4–5 (0.37 at a planted 0.5; 0 at 0.2), because days 4–5 are then not settled; it is reported as a lower bound.
4. **Per-kickoff rule** is weak at ζ 0.5 (passes 11% of kickoffs) and strong at ζ 0.2 (85%); null rate 0.00–0.04. Card-level P1 is the test; per-kickoff verdicts are descriptive of heterogeneity.
5. The real-data placebo pool comes from 10 long periods (origins d ≥ 6); in the synthetic it held 80 origins (pooled 95th percentile ≈ 0.03 under the null worlds).

## Results by goal period
Replication rule (templated): supported if U > 0 with jackknife 90% CI above 0 and U above the pooled placebo 95th percentile (+0.093, bge); failed if U ≤ 0; mixed otherwise. ± is one jackknife SE.

| Period | Role | Verdict | Key numbers |
| --- | --- | --- | --- |
| NE34 (27 kickoffs) | replication (cross-kickoff) | failed | U −0.006 [−0.020, +0.008] (bge), −0.002 [−0.017, +0.013] (gte), 90% CI; not beyond 80 placebo origins (p 0.79 / 0.69); E₁ +0.055 ± 0.012 / +0.062 ± 0.015 |
| [G04](goalperiod-subhypotheses/G04/README.md) | replication | failed | U -0.061 ± 0.029 (gte -0.041); E₁ +0.110; N 4 |
| [G05](goalperiod-subhypotheses/G05/README.md) | replication | mixed | U +0.011 ± 0.029 (gte +0.073); E₁ +0.064; N 4 |
| [G06](goalperiod-subhypotheses/G06/README.md) | replication | failed | U -0.051 ± 0.034 (gte -0.051); E₁ +0.064; N 4 |
| [G08](goalperiod-subhypotheses/G08/README.md) | replication | supported | U +0.094 ± 0.012 (gte +0.141); E₁ +0.020; N 4 |
| [G10](goalperiod-subhypotheses/G10/README.md) | replication | failed | U -0.033 ± 0.023 (gte -0.051); E₁ +0.072; N 7 |
| [G11](goalperiod-subhypotheses/G11/README.md) | replication | failed | U -0.036 ± 0.008 (gte +0.001); E₁ +0.066; N 7 |
| [G12](goalperiod-subhypotheses/G12/README.md) | replication | failed | U -0.109 ± 0.039 (gte -0.088); E₁ +0.246; N 7 |
| [G13](goalperiod-subhypotheses/G13/README.md) | replication | failed | U -0.010 ± 0.026 (gte +0.005); E₁ +0.028; N 6 |
| [G16](goalperiod-subhypotheses/G16/README.md) | replication | mixed | U +0.025 ± 0.024 (gte -0.011); E₁ -0.061; N 7 |
| [G17](goalperiod-subhypotheses/G17/README.md) | replication | mixed | U +0.015 ± 0.041 (gte +0.033); E₁ -0.007; N 7 |
| [G18](goalperiod-subhypotheses/G18/README.md) | replication | mixed | U +0.030 ± 0.009 (gte -0.041); E₁ +0.057; N 7 |
| [G19](goalperiod-subhypotheses/G19/README.md) | replication | failed | U -0.003 ± 0.026 (gte +0.055); E₁ +0.075; N 7 |
| [G20](goalperiod-subhypotheses/G20/README.md) | replication | mixed | U +0.000 ± 0.028 (gte +0.009); E₁ +0.130; N 8 |
| [G21](goalperiod-subhypotheses/G21/README.md) | replication | failed | U -0.027 ± 0.026 (gte -0.019); E₁ +0.152; N 8 |
| [G24](goalperiod-subhypotheses/G24/README.md) | replication | failed | U -0.042 ± 0.017 (gte -0.000); E₁ +0.042; N 10 |
| [G25](goalperiod-subhypotheses/G25/README.md) | replication | mixed | U +0.085 ± 0.013 (gte +0.039); E₁ -0.070; N 10 |
| [G26](goalperiod-subhypotheses/G26/README.md) | replication | failed | U -0.091 ± 0.032 (gte -0.022); E₁ +0.185; N 10 |
| [G27](goalperiod-subhypotheses/G27/README.md) | replication | failed | U -0.052 ± 0.016 (gte -0.046); E₁ +0.068; N 10 |
| [G30](goalperiod-subhypotheses/G30/README.md) | replication | mixed | U +0.040 ± 0.022 (gte +0.022); E₁ +0.028; N 11 |
| [G31](goalperiod-subhypotheses/G31/README.md) | replication | mixed | U +0.014 ± 0.014 (gte +0.046); E₁ +0.022; N 10 |
| [G35](goalperiod-subhypotheses/G35/README.md) | replication | mixed | U +0.038 ± 0.011 (gte +0.013); E₁ +0.011; N 12 |
| [G38](goalperiod-subhypotheses/G38/README.md) | native (+ replication) | mixed | U +0.035 ± 0.005 (gte -0.008); E₁ -0.007; N 12; N3 10-day M_osc wins (ΔSSE +0.07 / +0.11) but size 0.19–0.26 and ζ_fit 0.56 vs 0.04 |
| [G39](goalperiod-subhypotheses/G39/README.md) | replication | failed | U -0.016 ± 0.013 (gte -0.027); E₁ +0.046; N 14 |
| [G40](goalperiod-subhypotheses/G40/README.md) | replication | failed | U -0.074 ± 0.021 (gte -0.068); E₁ +0.113; N 15 |
| [G41](goalperiod-subhypotheses/G41/README.md) | replication | failed | U -0.042 ± 0.012 (gte -0.064); E₁ +0.085; N 15 |
| [G42](goalperiod-subhypotheses/G42/README.md) | replication | failed | U -0.025 ± 0.021 (gte -0.002); E₁ +0.061; N 15 |
| [G51](goalperiod-subhypotheses/G51/README.md) | native (+ replication) | failed | U +0.010 ± 0.006 (gte +0.008); E₁ -0.020; N 21; N1 own roles: U_own −0.009 ± 0.016 / −0.026 ± 0.015 (failed) |
| [NE38](goalperiod-subhypotheses/NE38/README.md) | native | failed | Opus 5 U −0.012 / −0.011 at the others' median (pct 0.46 / 0.38); no day-1 overshoot (E₁ −0.023 / −0.044) |

## Results
**Headline.** After a goal kickoff the swarm's excess alignment with the kickoff text is highest on day 1 and relaxes to its settled level within about two active days. It does not swing below that level on days 2–3. Over 27 kickoffs the undershoot is U = −0.006 [−0.020, +0.008] (bge) and −0.002 [−0.017, +0.013] (gte), inside the spread of 80 ordinary-day origins. The day-1 overshoot (+0.055 ± 0.012) is a field that fades, not inertia. HH366 fails by its own kill clause.

**Outcome vs prediction**

| Prediction | Credence | Outcome | Verdict |
| --- | --- | --- | --- |
| P1 U > 0, beyond placebo days, both models | 0.2 | bge −0.006 [−0.020, +0.008], p 0.79; gte −0.002 [−0.017, +0.013], p 0.69 | failed (kill clause; power 1.00 at ζ ≤ 0.5) |
| P2 M_osc wins in ≥ 2/3, sign p < 0.05 | 0.2 | bge 18/27 (p 0.06); gte 19/27 (p 0.03); size 0.12–0.20 (Amendment 1) | not supported in bge; gte passes by rule but carries no weight without P1 |
| P3 ζ_pk < 1 (amended) | 0.2 | ζ_pk ≥ 1 in both models | failed |
| S1 overshoot E₁ > 0 | 0.85 | +0.055 ± 0.012 (22/27); gte +0.062 ± 0.015 (23/27) | supported |
| S2 U(III) > U(I) | 0.3 | III −0.019 vs I −0.010 (p 0.65); gte −0.027 vs +0.003 (p 0.91) | not supported |
| S3 sign survives variants | 0.5 | U ≤ 0 in 7/8 configurations (style, dedupe, day-4 settled); the no-human-days-4–5 subset (k = 5) gives −0.003 / +0.004, CI containing 0 | no positive U in any variant |
| S4 decoy percentile π_U > 0.5 | 0.25 | median 0.39 / 0.43 (sign p 0.84 / 0.94) | not supported |
| N1 G51 own roles undershoot | 0.15 | U_own −0.009 ± 0.016 / −0.026 ± 0.015; M_fade wins | failed |
| N2 NE38 Opus 5 swings | 0.15 | U −0.012 / −0.011 at the others' median; no overshoot | failed |
| N3 G38 ring-down | 0.15 | ΔSSE +0.07 / +0.11, ζ_fit 0.56 / 0.04; size on this skeleton 0.19–0.26 | passes by rule; weak |
| **Overall (rule)** | | kill clause holds in both models | **failed** |

**Synthesis**
1. **Overdamped, not underdamped.** The day profile (mean over kickoffs, relative to days 4–5) is +0.059 on day 1, +0.019 on day 2, +0.001 on day 3, and stays within ±0.012 on days 6–10 (bge; gte the same within 0.01). That is the shape of M_fade: a sum of decaying terms, crossing the settled level at most once.
2. **Power.** The observed day-1 overshoot (+0.055) equals the overshoot the synthetic oscillator worlds produced at planted amplitude 0.12; there P1 passed in 100% of replicates at ζ 0.2 and 0.5. The upper CI bound of U (+0.008) is below the U a ζ = 0.5 oscillator gives (+0.015). An oscillator with 0.5 < ζ < 1 would undershoot by ≤ 0.2× E₁ (e.g. 4% at ζ 0.7) and cannot be excluded.
3. **No inertia at the single-agent level.** Opus 5's reassignment (NE38) moves it onto its new role from below, with no day-1 overshoot and no swing. In G51 each of 21 agents overshoots its own role on day 1 (+0.055) and keeps decaying into days 4–5.
4. **Where the overshoot comes from.** H127 (round 1, same data) finds the alignment peaks at each agent's read-out call of the kickoff (≈ 2.4× its late day-1 plateau) and decays over tens of calls. The overshoot is that spike: the kickoff's salience fades call by call. Part of it is likely restatement of the kickoff text.
5. **Model comparison is liberal.** M_osc wins the 30-min SSE comparison in 18–19 of 27 single kickoffs, close to what heavy day noise alone gives (56–59% in synthetic null worlds). Only the model-free U carries the verdict. G38's 10-day preference is of this kind.

**Caveats.** The target is a text embedding of the kickoff. Day 1 contains restatements of the kickoff, which inflate E₁ without changing U. Only 10 long periods supply placebo origins (#4 and #51 most of them). Calendar windows that include village-off gaps lengthen the active-hour clock on two days. U compares day means, so an oscillation with a period under one active day would be invisible here (the 30-min fits cover it and show no consistent preference).

**Code.** `scheme/build.py`; `analysis/h125lib.py`, `calibrate.py`, `synthetic.py`, `synthetic_g38.py` (post hoc N3 size), `run.py`, `natives.py`, `figures.py`, `period_folders.py`, `write_rows.py`, `confirm.py` (not run). **Data:** `data/processed/H125-kickoff-damped-oscillator/` (≈ 3 MB). **Figures:** `figures/summary_obs.pdf`, `figures/synthetic_compact.pdf`.

**Per-period estimates:** rows written with `write_estimates` (`kickoff_undershoot_U`, `kickoff_overshoot_E1_days45`, `kickoff_osc_vs_fade_dsse`; channels bge/gte × white/style; natives `g51_own_role_undershoot_U`, `ne38_opus5_undershoot_U`, `g38_osc_vs_fade_dsse_10d`).

**Claim that stands:** After a goal kickoff the swarm's within-agent excess alignment with the kickoff overshoots on day 1 (E₁ +0.055 ± 0.012, 22/27 kickoffs, both models) and decays to its days 4–5 level within two active days without an undershoot (U −0.006 [−0.020, +0.008], inside 80 placebo-day origins; powered for ζ ≤ 0.5): an overdamped response to a fading field. Excluded: G38's ring-down (weak, size 0.19–0.26), the M_osc SSE preference (liberal), damping between 0.5 and 1 (unpowered).

## Confirmatory test (written 2026-10-04 after exploration; NOT run)
`analysis/confirm.py` refuses to run without `--confirm --i-understand-this-uses-the-locked-holdout`, a clean git state for its files and a holdout-ledger check. `--dry-run` on the stand-ins #11–#13, #38–#42 reproduces the exploratory per-kickoff values exactly (C1 U −0.030 [upper −0.003], p 0.99, pass; C2 E₁ +0.079, 7/8, pass). Frozen predictions on the held-out kickoffs with ≥ 5 days (from #1, #9, #14, #15, #28, #29, #34, #43, #45–#50; #22, #23, #32 excluded for H10):
- **C1** no undershoot: meta U 90% upper bound < +0.015 and Mann–Whitney vs the exploratory placebo pool p ≥ 0.05 (credence 0.75).
- **C2** overshoot: meta E₁ 90% CI above 0 and E₁ > 0 in ≥ 2/3 (credence 0.8).
- Reuse: H54 and H97 plan the same held-out kickoffs with different statistics in the same k̂-projection family; disclose in all three cards and LOG.md when run.

## Round 2 redirects (2026-10-04)
- **H125-R1. The overshoot at call resolution.** Fit the decay of the read-out spike (H127) on the call and hour clocks from each agent's read-out call; this is the fading field's time constant.
- **H125-R2. Restatement vs re-orientation.** Drop statements that copy the kickoff text (DQ5 cross-echo against the kickoff message, or cos to k̂ above the 99th decoy percentile) and re-measure E₁; U should not change.
- **H125-R3. G38's non-monotone 10 days.** Regress the #38 series on operator and room-kickoff directions before reading any second swing.

## Notes
- 2026-10-04 23:19 UTC: round 1 done (synthetic → Amendment 1 → replication on 27 kickoffs × 8 configurations → natives → estimates → confirm.py frozen and dry-run). Post hoc (labelled): the N3 size check on G38's skeleton (`synthetic_g38.py`).
- 2026-10-04 22:16 UTC: card, observables and predictions written from HH366 (approved by Vivian in the dashboard), before any real-data statistic along a kickoff direction.
- Proposed DEFINITIONS.md variants (H125): **kickoff excess alignment a(h)** = per statement ⟨z, k̂_p⟩ − mean over decoy kickoffs ⟨z, k̂_q⟩, averaged linearly (no renormalization) over an agent's statements in a window or day, on the active-hour clock h since t₀; **undershoot U** = within-agent mean of (days 4–5 level − days 2–3 level); **overshoot E₁** = within-agent day-1 level minus the days 4–5 level; **peak-ratio damping ζ_pk** = δ/√(π² + δ²) with δ = ln(E₁/U), defined for U > 0; **fitted damping ζ_fit** = λ/√(λ² + ω_d²) from M_osc.
