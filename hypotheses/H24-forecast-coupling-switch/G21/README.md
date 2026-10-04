# H24 × G21: Forecast the abilities and effects of AI (2025-12-01 → 12-05)

**Verdict:** failed
**Role:** exploratory
**Period:** regime I · mode I · 8 agents on days 1–3, 9 from 12-04 (DeepSeek-V3.2 joins) · one room (#general) · 5 days × 4 h.

**Splits inside the period:**
- **G21a, the independent drafts:** each agent's [window open, τ_i) on 12-01; τ_i is 42–86 min after the open.
- **G21b, the comparison phase:** [τ_i, end of 12-03].
- **G21c, 12-04 → 12-05:** DeepSeek joins; the "don't do nothing" system-prompt change; shared tracker.

## Why this period
HH28 and the goal-period ranking put vector spins first here: the kickoff explicitly asked agents to form independent forecasts before comparing, so the coupling should switch on at a known point. It is the only forecasting week in the data.

## Switch-on (from the record, before any outcome)
See the card's "Switch-on" section. τ\* = median τ_i = 18:51:36 UTC on 12-01, 50 min after the window opened. The independent phase is ≈ 4% of the week's active time. GPT-5 never reads teammates' forecasts before 12-05 and serves as a document-uncoupled control. The chat channel carried a few numbers from 18:21, but chat reached agents only between computer sessions in this scaffold.

## Prediction
*Written 2026-10-03, before running on this period. Identical to the card's P1–P6, which also lists what I had seen.*
- **P1:** residual alignment steps up at τ_i; ΔA_res (all statements, k = 4, 60-min post window) > 0 and above the 90th percentile of both the within-period placebo (N1) and the kickoff-matched placebo weeks (N2). [0.30] Raw ΔA ≤ 0 [0.55].
- **P2:** document chunks ΔA_res > 0 for all chunks [0.6] and for own-forecast chunks [0.4].
- **P3:** snapshot βJ₀/n rises [0.4] and stays subcritical (< 0.5) after the switch [0.7].
- **P4 (not blind):** numeric herding, κ > 0 with permutation p < 0.10 and SD shrinking in ≥ 2 of 3 anchors. [0.5]
- **P5:** GPT-5 control DiD > 0 [0.5].
- **P6:** the coupling ramp, ρ > 0 over G21b–c with a positive step at 12-04. [0.45]

**Counts against:** ΔA_res inside the placebo bulk while the synthetic shows power ≥ 0.5; κ ≤ 0, or SD not shrinking.

## Result
**Data:** `data/processed/H24-forecast-coupling-switch/G21/` (`explore.json`, `synthetic_validation.json`, `numeric_handverified.parquet`). **Figures:** `figures/G21_panels.pdf` (same as `../figures/summary.pdf`) and `../figures/synthetic_validation.pdf`.

**Primary test.** Whitened n = 32, ĝ projected out, k = 4 statements per agent and segment, 200 rarefaction draws; 90% CIs from a statement bootstrap.

| | Prediction | Observed | Null | Verdict |
| --- | --- | --- | --- | --- |
| P1 step (all statements, residual) | ΔA_res > q90 of N1 and N2 | +0.010 [−0.047, +0.086] (A 0.333 → 0.342) | N1 q90 +0.122 (rank 6/8; median +0.029); N2 q90 +0.112, #21 at the 74th percentile of 23 kickoff days | **failed** |
| P1 raw | ΔA_raw ≤ 0 | −0.151 [−0.208, −0.080] | N2 raw median −0.132 | as predicted, but generic to kickoff days |
| P2 documents, all chunks | ΔA_res > 0 | +0.128 [+0.060, +0.175] | N1 q90 +0.099 (rank 2/8) | supported (includes matrices that transcribe others' numbers) |
| P2 documents, own chunks | ΔA_res > 0 | +0.049 [−0.097, +0.104] | N1 q90 −0.033 (5 placebos) | weak (CI spans 0) |
| P3 snapshot βJ₀/n | rises; post < 0.5 | 0.67 → 0.67 (Δ [−0.03, +0.06]) | synthetic: 0.34 at zero coupling (field leakage) | **failed** (an upper bound) |
| P4 numeric herding (not blind) | κ > 0 at p < 0.10 and SD shrinks in ≥ 2/3 | pre-registered extractor κ = 0.70, p = 0.0002 (SDs AGI 13.7 → 5.5, doom 19.3 → 6.5, SI 13.8 → 12.1); **hand-verified** κ = 0.25, p = 0.17 (SDs AGI 6.7 → 5.5, doom 6.7 → 6.5, SI 11.7 → 15.8) | permutation (independent updating) q90 0.28–0.32 | **failed after audit**: the pre-registered pass is an extraction artifact |
| P5 GPT-5 control DiD | > 0 | −0.137 (switched pairs −0.015, GPT-5 pairs +0.122; GPT-5 has 4 post statements) | — | failed (N = 1) |
| P6 ramp | ρ > 0, step at 12-04 > 0 | ρ = 0.73 (p = 0.025, 9 blocks), step +0.091 | — | supported (descriptive, confounded) |

**Other observations:**
- **Alignment is high from the first hour:** A_res ≈ 0.33 before any document coupling, against a rotation null q95 ≈ 0.02–0.07.
- **The addressed channel does switch on:** 7% of the switched agents' messages name another agent before τ_i, 74% in the following hour.
- **Robustness of P1:**
  - k = 3 or 5: +0.013 / +0.015;
  - n = 16: +0.010;
  - **n = 64: +0.083 [+0.036, +0.139]** (above N1 q90);
  - goal-text-only ĝ: −0.105;
  - kickoff-only ĝ: +0.031;
  - forecast-bearing statements only: +0.021.

## Scorecard (period-specific axes)
- **C 1:** the alignment levels beat the rotation null; the predicted step does not beat N1 or N2.
- **D 0:** no step; snapshot βJ₀ flat; herding gone after audit.
- **E 0:** the switch-on is the natural experiment, and its predicted effect is absent.
- **G 1:** the switch-on times agree across intentions, the models' screen descriptions and the mention rate. The GPT-5 control did not behave as a control.

## Notes
- 2026-10-03: the switch-on is on day 1, not mid-week. Pre-switch data per agent: 7–29 statements, 10–51 document chunks; only 2 agents state a numeric anchor forecast before τ_i.
- 2026-10-03 (after the first run): numeric extraction audited by hand (amendments A1, A2 on the card). The pre-registered extractor turned thresholds, complements, worked examples and scenario-conditional values into forecasts, and missed other agents' numbers cited by short name. Several of these errors sat in the "first" values, which manufactures a DeGroot pull (the synthetic regression-to-the-mean pitfall).
- 2026-10-03 (after the first run): the rotation null shared 8 matrices across agents (collisions); fixed to a fresh rotation per agent. No verdict changed.
- Copying, post hoc and descriptive: 16 non-round values first stated by one agent reappear in another agent's own statements. On 12-05, one agent's tracker submission reuses another's two-decimal values for 2 of 7 questions. This looks like pairwise copying (model 08), not mean-field herding.

