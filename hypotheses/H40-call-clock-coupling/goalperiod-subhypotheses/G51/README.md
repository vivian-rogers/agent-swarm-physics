# H40 × G51: Each agent: Maximize your assigned goal! (2026-07-06 → 2026-09-04, non-holdout head)

**Verdict:** supported
**Role:** native (exploratory); the replication estimator is reported here too
**Period:** regime III · 32 agents · rooms #general (+ #focus in 51g) · 45 non-holdout days · units 51a–51l (51b, 51k, 51l are one-day units) · 888,344 read-out items · 18,352 replies within 30 min. The #51 tail (09-07 → 09-21) is locked holdout and not used. Post NE44 (06-11, 5-min pause default), so idle agents sit in short timer-gated pause chains.

## Why this period
- The widest spread of cadence in the dataset: call rates from 6 to 235 per hour (SD of log rate 0.81 across agents; 0.69 across agent-units within units), 32 agents of 8 labs. The between-agent test (heavy spins) has power only here.
- Timer pauses give a quasi-exogenous read-out wait: a message that arrives during a pause is read at the timer wake, after a wait set by a duration declared before the message arrived (N1a).
- 12 units with roster changes let η be replicated inside the period (N1c).

## Prediction
*Written 2026-10-04 ~06:10 UTC (card N1, P1, P3), before any H40 statistic on G51.*
- **N1a (pause-timer dose):** among timer-wake read-outs, the reply hazard at the wake call does not grow with the wait: η₁,pause CI inside [−0.3, 0.3]. Wall clock: ≈ 1.
- **N1b (heavy spins):** between-agent slope s of per-call coupling on log call rate CI inside [−0.4, 0.4] (lab and style controls); the slowest cadence quintile's per-hour coupling ≤ 0.5× the fastest's, while its per-call coupling is within 0.67–1.5×; cadence explains more between-agent variance in per-hour coupling than lab + style.
- **N1c:** η < 0.5 in ≥ 80% of units with ≥ 2 days.
- Replication rule (P1, P4): η's CI below 0.5 and held-out call-clock model better than the wall-clock model.

## Result
| Test | Observed (95% CI) | Prediction | Verdict |
| --- | --- | --- | --- |
| P1 η (calls n ≥ 2), whole period | −0.00 [−0.09, +0.09] | CI < 0.5 | supported |
| η by gap: busy / long previous call / pause wake | +0.01 ± 0.04 / −0.37 ± 0.07 / +0.18 ± 0.06 (SE) | — | call clock; long tool calls carry *less* hazard |
| η₁ (read-out wait, all read-outs) | +0.12 [+0.09, +0.16] | — | small |
| P4 held-out Δ log-lik per item (call − wall) | +0.0050 (671,895 test items) | > 0 | supported |
| **N1a** η₁ at timer-wake read-outs (20,641 wakes, 1,137 replies at the wake) | −0.03 [−0.14, +0.08] | inside [−0.3, 0.3] | **supported** |
| N1a reduced form: log declared pause length | −0.12 [−0.34, +0.10] | ≈ 0 | consistent |
| **N1b** s, agent-unit meta-regression (243 agent-units, unit FE, τ = 0.66) | +0.11 [−0.03, +0.25]; p(s = −1) < 10⁻³⁰ | inside [−0.4, 0.4], excludes −1 | **supported** |
| s with lab FE + two style PCs | −0.00 [−0.15, +0.15] | | supported |
| s, agent-clustered SE (32 agents) / agent-level regression | +0.11 [−0.09, +0.31] / +0.04 [−0.29, +0.38] (controlled −0.13 [−0.50, +0.24]) | | consistent |
| Slowest vs fastest cadence quintile (25 vs 184 calls/h): per-hour coupling ratio (model-free P(5 min)) | 0.12 | ≤ 0.5 | supported |
| same, per-call coupling ratio: model-based α / model-free β(10 calls) | 0.87 [0.64, 1.17] / 0.18 | 0.67–1.5 | model-based yes, model-free no |
| Variance explained, per-hour coupling (α + log r): cadence / lab + style / both | R² 0.50 / 0.33 / 0.62 | cadence > lab + style | supported |
| Variance explained, per-call coupling (α): cadence / lab + style | R² 0.01 / 0.25 | (not predicted) | per-call coupling is a family/style trait |
| Model-free slopes on log rate: per-call β(10); per-hour P(5 min) | +0.74 [+0.55, +0.92]; +1.00 [+0.81, +1.19] | ~0; ≥ 0.5 | per-call **not** flat model-free (burial, below); per-hour as predicted |
| Pair level (1,016 sender × recipient pairs, sender FE): β(10); P(5 min) | +0.31 [+0.19, +0.44]; +0.49 [+0.36, +0.61] | | as the agent-unit model-free slopes |
| **N1c** η per unit (9 units with ≥ 2 days) | −0.04 to +0.18; all point estimates < 0.5; 51d CI [+0.01, +0.33] | ≥ 80% below 0.5 | **supported** (9/9) |
| Decay clocks φ / ψ / χ | −0.80 / −0.03 / −0.51 | φ dominates ψ | relevance decays per call and per newer message, not per minute |
| Cadence elasticity ε(5 / 15 / 30 min) | 0.40 / 0.29 / 0.27 (SE 0.02) | (regime III: 0.5–1.0) | lower than the regime-III pooled value |
| Robustness of η: any p_reply ≥ 0.5; addressing; certain items only; jittered starts | +0.01; −0.06; −0.03; −0.00, +0.00 | | robust |
| η by start source: chained (medium) / Gemini logged (high) | +0.08 ± 0.02 / −0.27 ± 0.02 | | small either way |

**Reading.** In G51 the reply coupling runs on the recipient's call clock: a call that spans more wall time does not carry more reply hazard (η = 0.00 ± 0.05; at timer wakes, where the wait is set in advance, −0.03 ± 0.06). Per-call coupling *at fixed batch and burial* does not depend on cadence (s ≈ 0.1, ≈ 0 with controls), and it is a family/style trait (lab + style R² 0.25, cadence 0.01). Per-hour coupling scales about linearly with call rate across agents (slope 1.0), and cadence explains half its variance. So slow agents are heavy spins: the slowest fifth (≈ 25 calls/h) answer a given message within 5 min about 8× less often than the fastest fifth (≈ 184 calls/h). The model-free per-call slope (0.74) is not zero because a slow agent's calls each face a larger, more buried batch (rank −0.60 per log rank at read-out, χ = −0.51 per log newer message): dilution and burial are the routes by which cadence lowers per-call uptake, and the hazard model separates them from the per-call coupling itself. The model's uniform-speed-up elasticity (ε(5) = 0.40) is smaller than the cross-sectional slope (1.0); the gap is between-agent composition (pause-heavy agents differ in batch structure and mentions), so the cross-sectional slope overstates what a speed-up would buy.

Data: `data/processed/H40-call-clock-coupling/results/G51.json` (replication), `native/N1_G51.json` (N1a–c). Figure: `figures/summary_obs.pdf` (b).

## Scorecard (period-specific axes)
- **C:** held-out call clock beats wall clock (Δ log-lik +0.005/item over 672k items); η = 0 recovered in every unit.
- **D:** unfitted pause-dose η₁ ≈ 0; ε ordering ε(5) > ε(30).
- **E:** the pause-timer dose is quasi-interventional (wait set before the message arrived), supported. Pause wakes are not random: agents choose to pause.
- **F:** synthetic recovery on 51c (η bias ≤ 0.04; s recovered 0.40 for a true 0.5).
- **H:** cadence beats lab + style for per-hour coupling (R² 0.50 vs 0.33); lab + style beat cadence for per-call coupling.

## Notes
- The between-agent fixed effects use agent × unit intercepts; the same agent appears in up to 12 units, so the agent-clustered and agent-level versions are reported next to the agent-unit meta-regression.
- Pause wakes: the declared duration (the pause call's `pause_s`) is available for all 226,927 wake read-out items; the reply-at-wake rate falls steeply with declared length in raw data (4.1% at < 90 s, 0.1% at > 20 min), but batch size rises from 3.6 to 83 items, and with batch, rank and mention controlled the wait has no effect.
- The NE43 nudger and bookend wind-down (08-05, 08-20) lies inside 51g; not modelled here.
