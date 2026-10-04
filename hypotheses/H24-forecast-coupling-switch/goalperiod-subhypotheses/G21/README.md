# H24 × G21: Forecast the abilities and effects of AI (2025-12-01 → 12-05)

**Verdict:** failed
**Verdict (1b):** mixed (step fails; pair DiD supported)
**Role:** native (round 1b: pair-level reading DiD; also carries the replication row; round 1 was exploratory)
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



## Round 1b (improved data, 2026-10-04): replication
*Inputs: shared goal fields for #21 and for the 23 N2 placebo weeks (H24's own ĝ for #21 had cos 0.96 with the shared one; kickoff part 0.88, from a different boilerplate filter and one-string embedding; placebo weeks 0.78–1.00), gte-modernbert for statements and the 1,889 document chunks (re-embedded from the sidecar, same chunks), a multi-direction field (ĝ plus all 6 goal-text and kickoff chunk directions), DQ5 dedupe (#21: 28% of statements are self-repeats, 9% cross-agent echoes under bge) and style-residualized statement vectors. Data: `data/processed/H24-forecast-coupling-switch/G21/r1b/explore_<config>.json`, `report.json`. Numeric herding (P4, hand-verified κ 0.25, p 0.17) does not depend on embeddings and stands.*

| Configuration | ΔA_res at τᵢ [90% CI] | N1 q90 | N2 q90 | A_pre / A_post | βJ₀/n pre → post | docs ΔA_res | ramp ρ |
| --- | --- | --- | --- | --- | --- | --- | --- |
| round 1 (bge, H24 ĝ, 1-d) | +0.010 [−0.047, +0.086] | 0.122 | 0.112 | 0.33 / 0.34 | 0.67 → 0.67 | +0.128 | 0.73 |
| bge, shared ĝ | −0.011 [−0.067, +0.068] | 0.110 | 0.100 | 0.36 / 0.35 | 0.69 → 0.68 | +0.164 | 0.47 |
| bge, multi-direction field | +0.022 [−0.057, +0.096] | 0.119 | 0.124 | 0.38 / 0.40 | 0.69 → 0.71 | +0.178 | 0.72 |
| bge, deduped / no echoes / style | +0.002 / +0.017 / +0.020 | 0.12 / 0.11 / 0.16 | 0.10 / 0.10 / 0.12 | 0.34–0.37 | 0.67–0.69 → 0.68–0.69 | +0.16 | 0.57 / 0.57 / 0.75 |
| gte, shared ĝ | **+0.160 [+0.102, +0.236]** | 0.107 | 0.180 | 0.38 / 0.53 | 0.69 → 0.76 | +0.075 | 0.60 |
| gte, multi-direction field | +0.155 [+0.092, +0.236] | 0.095 | 0.182 | 0.42 / 0.57 | 0.71 → 0.77 | +0.085 | 0.60 |
| gte, deduped / no echoes / style | +0.174 / +0.178 / +0.166 | 0.11 / 0.12 / 0.16 | 0.19 / 0.20 / 0.17 | 0.35–0.37 / 0.52–0.54 | 0.68–0.69 → 0.76 | +0.07–0.08 | 0.50 / 0.50 / 0.67 |

- **P1 (literal H24) fails in all 13 configurations**, but for a model-dependent reason. Under bge there is no step (≈ 0). Under gte residual alignment does step up by 0.15–0.18 at the switch-on (CI excludes 0, above the within-week placebo), yet ordinary regime-I kickoff days show steps as large (N2 q90 0.17–0.20, also larger under gte): the step is generic kickoff-day dynamics, not a coupling switch.
- **P2 documents:** positive in both models (bge +0.16, gte +0.08, CIs > 0). **P3 snapshot βJ₀/n:** flat in bge, rises in gte (Δ CI [+0.05, +0.13]); this statistic is an upper bound inflated by field leakage (synthetic). **P6 ramp:** ρ 0.47–0.75 (bge), 0.50–0.67 (gte); 12-04 step +0.08 to +0.14; confounded as before.
- **Alignment levels** stay far above the rotation null (A_pre 0.34–0.42 vs q95 0.02–0.10) in every configuration. Removing the field along 7 directions instead of 1 does not lower them: what aligns the agents in the first hour is not the kickoff text's directions.
- GPT-5 control DiD: −0.13 (bge), +0.04 (gte): uninformative (N = 1).

## Round 1b native test: pair-level reading DiD (who read whose document)
*Prediction written 2026-10-04 07:30 UTC, before any pair-level statistic. Seen before: the round-1 results above (swarm-level step +0.010; documents +0.128; pairwise literal copying of non-round values, post hoc) and the DQ5 flag rates for #21 statements (self-repeat 28%, cross-echo 9% under bge).*
- **Design.** Reading events = computer-use turns whose reasoning sentence describes accessing a document and names another present agent (`h24lib.record_reads` plus the name patterns of `scheme/build.py`; every event on 12-01 → 12-05, not only the first), keeping the first event per (reader i, owner j, day). For each event at t: i's output before [t − 60, t) and after [t, t + 60 min); the owner's reference = unit mean of j's statements in [t − 180 min, t). a = cosine of i's window mean with j's reference (field removed along all goal and kickoff chunk directions; ≥ 2 statements per window). **DiD** = (a_post − a_pre)(i, j) − mean over controls k (a_post − a_pre)(i, k), controls = present agents not read by i within ±60 min. **Null:** owner-label permutation (j replaced by a random non-reader present agent), 2,000 draws. Outputs: statements (chat + intentions) and i's own document chunks; both models; restatement-deduped and style-residualized variants.
- **N1a (statements).** Mean DiD > 0 with permutation p < 0.05 in both models. Credence 0.35.
- **N1b (documents).** Mean DiD > 0 with permutation p < 0.05 in both models. Credence 0.5 (divergence matrices transcribe what was read).
- **Verdict rule (native):** **supported** (coupling is real at the pair level, switched on by reading, even though the swarm-level step is absent) if N1a or N1b holds in both models; **failed** if both DiDs are ≤ 0; **mixed** otherwise.

**Result (native, run 2026-10-04 after the prediction; `data/processed/H24-forecast-coupling-switch/G21/r1b/native_<config>.json`, `analysis/natives_r1b.py`).** 643 reading events (reasoning sentences describing another agent's document), 116 first events per (reader, owner, day); 102 usable for statements (≥ 2 statements in each window and in the owner's reference), 67 for documents.

| Configuration | statements: mean DiD (perm p; share > 0) | documents: mean DiD (perm p) |
| --- | --- | --- |
| bge-small | +0.036 (p 0.035; 52%) | +0.016 (p 0.26) |
| gte-modernbert | +0.030 (p 0.038; 64%, sign p 0.004) | +0.004 (p 0.43) |
| deduped, bge / gte | +0.037 (p 0.034) / +0.031 (p 0.034) | +0.018 / +0.004 (n.s.) |
| style-residualized, bge / gte | +0.023 (p 0.14) / +0.028 (p 0.084) | +0.015 (p 0.27) / +0.029 (p 0.066) |

**N1a holds in both models** (statements move toward the owner of the document just read, relative to agents not read, by about 0.03 in cosine); **N1b fails** (documents). **Native verdict: supported** by the pre-registered rule, with a caveat: the effect weakens below significance after style residualization (p 0.08–0.14), so part of it may be the reader adopting the owner's register rather than its content. A pairwise, reading-gated coupling of this size (0.03) is consistent with the swarm-level null: it is far too small and too spread out to step the swarm's alignment.
