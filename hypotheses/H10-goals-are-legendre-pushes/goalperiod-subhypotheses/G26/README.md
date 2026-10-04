# H10 × G26: Elect a leader who sets the goal (2026-01-05 → 2026-01-09)

**Verdict:** failed (round 1b native; both models)
**Role:** native (round 1b, 2026-10-04; transition exception c: #25 → #26 along the leader's goal)
**Period:** regime I · 10 agents · #general · 5 active days. The approval vote ties 9–9–9, a runoff closes 7–1–0 in ~100 s, and DeepSeek-V3.2 is elected on 01-05 19:35 UTC; it announces an interactive-fiction goal at 19:36 (not in `village_goals`); a confirmatory re-election follows on 01-09 (DQ6).

## Why this period
The only non-holdout week whose working goal was written by an agent (DQ9: "an agent-set goal as the kickoff ... response to an agent-set field (H10)"). Round 1 measured responses to operator goals only (a push at 19/19 changes into assigned goals, median ≈ 2.5 pre-period SDs, and P1 with the wrong sign). Does an agent-set goal act as a field at all, and if so, is it tilt-shaped?

## Design (round 1b)
- **Field.** ê_L = the leader's announcement message, embedded as a statement (shared chat embeddings, both models; message located by H54's rule, `g26_leader.json`), whitened, regime I, n = 32. Comparison direction: #26's operator kickoff (the election), shared `goal_fields`.
- **Segments.** F = #25 (12-29 → 01-02, all days). A = #26 on 01-06 → 01-08 (the days after the announcement; 01-09, the re-election day, excluded). Agents present in both with ≥ 6 eligible windows; the leader excluded.
- **Statistics** (H10 estimators): Δ̄ and ε along ê_L and along the operator kickoff; P1 r(Δᵢ, κ2ᵢ^F) with the exact permutation p; cross-split convergence slope; ρ and ρ⊥.

## Prediction
*Written 2026-10-04 07:20 UTC, before any H10 statistic on #25 or #26. Seen before: H54's G26 native (the announcement does not pull content beyond decoy messages within 1–3 h, percentile 0.48; day-level excess over decoys +0.20 on day 2, then negative), DQ6's election timeline, counts per day.*
- **N3a (an agent-set goal is a weak field).** ε_L < 1, below the regime-I median operator kickoff push of round 1 (≈ 2.5). Credence 0.6.
- **N3b (no fluctuation–response ordering).** P1 r ≤ 0 along ê_L. Credence 0.6.
- **Verdict rule (native):** **failed** for H10 if N3b holds (P1 wrong-signed again) with a push ε_L > 0.34 (outside the perturbative range); **supported** if r > 0 with permutation p < 0.05; **mixed** otherwise. N3a is reported as the field-strength reading (agent text vs operator text).

## Result
*Run 2026-10-04 (after the prediction above). Data: `r1b/<config>/natives.json` (G26). Script: `analysis/natives_r1b.py`.*
N = 9 agents (leader excluded). cos(announcement, operator kickoff) = 0.67 (bge).

| Prediction | bge-small | gte-modernbert | Verdict |
| --- | --- | --- | --- |
| N3a agent-set goal is a weak field: ε_L < 1 | Δ̄ +0.126 [+0.059, +0.243], ε 1.06 | Δ̄ +0.064 [+0.016, +0.145], ε 0.93 | ✗ / ✓ (≈ 1 SD in both) |
| N3b P1 r ≤ 0 along ê_L | r −0.14 (perm p 0.58); tilt LOAO error 1.8× translation's | r −0.63 (p 0.985) | ✓ / ✓ |
| Operator kickoff (goal + kickoff), same pair, descriptive | ε 0.80, r +0.56 (p 0.045) | ε 1.34, r −0.41 (p 0.86) | model-dependent (post hoc) |

Deduped: bge ε 1.10, r −0.14; gte ε 1.00, r −0.49 (failed in both). **Reading.** The elected leader's goal announcement does move the other agents' later content (about 1 SD of their holiday-week fluctuation, similar to the operator's election kickoff), so agent text can act as a field at the day scale, unlike in H54's 1–3 h window. But who moves is again not predicted by the unforced fluctuations along that direction (r ≤ 0 in every configuration). The only positive P1 in round 1b, along the operator's direction in bge (r +0.56, p 0.045), flips sign under gte and was not pre-registered.

## Notes
- 2026-10-04: native folder created in round 1b (DQ9 cross-index). #26's day 1 (the election) is the kickoff transient and is excluded from A, as in round 1.
