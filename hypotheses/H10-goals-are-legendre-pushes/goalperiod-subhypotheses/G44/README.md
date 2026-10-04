# H10 × G44: #best fine-tunes a leader; #rest picks its own goals (2026-05-26 → 2026-05-29)

**Verdict:** mixed (round 1b native; model-dependent)
**Role:** native (round 1b, 2026-10-04; transition exception c: #42 → #44 per room)
**Period:** regime III · 16 → 18 agents · #best (Opus 4.7, Kimi K2.6, GPT-5.5, Gemini 3.5 Flash; assigned goal: build training data and fine-tune a leader) / #rest (12 agents; per-room override: pick your own goal) · 4 active days. Splits: 44a (05-26 → 05-27) / 44b (05-28: Opus 4.8 and the temporary leader join). The joiners are not in the free reference, so they drop out of every per-agent statistic.

## Why this period
The only non-holdout week with a two-arm field contrast on the same days, scaffold and hours (DQ9): one room gets an operator-written target, the other a per-room instruction to choose its own. H10's round 1 found that assigned goals act as quenches toward a common target with field-specific dispersal along ĝ (variance ×1.9–7.7 along ĝ, transverse unchanged), not as small Legendre tilts. #44 asks whether that signature belongs to *assigned* goals: a self-chosen goal names no shared target (H54: #44's self-chosen room is one of its four target failures).

## Design (round 1b)
- **Segments.** F = #42, all non-holdout days (05-18 → 05-22; #43 is held out and skipped). A = #44 days 2+ (05-27 → 05-29). Per room r, the agents assigned to r in #44 (DQ6 `room_assignment`) that have ≥ 6 eligible 30-min windows in both segments.
- **Directions.** ĝ_r = the room's own kickoff (shared `goal_fields`, kind `kickoff_room`; #best room 2, #rest room 3), whitened in the regime-III basis, n = 32. Variant: unit(unit(goal) + unit(kickoff_room)).
- **Statistics** (H10's estimators, `h10lib.analyze_pair` restricted to each room): Δ̄ (mean push along ĝ_r, day-block bootstrap CI), ε = push in free-week SDs, ρ = ln(Σκ2^A/Σκ2^F) along ĝ_r and ρ⊥ along 50 transverse directions, cross-split convergence slope (Δᵢ on μᵢ^F), P1 r (descriptive for #best, N ≤ 4). Cross-room control: each room's push along the other room's ĝ.
- Both embedding models (bge-small, gte-modernbert), shared goal vectors; DQ5 restatement-deduped variant.

## Prediction
*Written 2026-10-04 07:20 UTC, before any H10 statistic on #42 or #44. Seen before: H54's G44 native result (room swap 0.31, the vague room more spread out, 0.80 vs 0.50, and shallower, depth −0.25 vs +0.37); H10 round-1 results on the three regime-I/III pairs; counts per day.*
- **N1a (assigned goal = quench).** #best's push along its own ĝ_best is positive with 90% CI > 0 and ε > 1. Credence 0.75.
- **N1b (the field is room-specific).** Δ̄_best(ĝ_best) − Δ̄_rest(ĝ_best) > 0 with bootstrap CI > 0. Credence 0.7.
- **N1c (no field, no field-specific dispersal).** In #rest, ρ along ĝ_rest is within ln 1.5 of ρ⊥ (no dispersal specific to its kickoff direction). Credence 0.55. In #best, ρ > ln 1.5 with |ρ⊥| < ln 1.5 (round-1 signature). Credence 0.4 (N = 4, three days).
- **Verdict rule (native):** **supported** (the round-1 reading "assigned goals are quenches along their own direction; a self-chosen goal is not a field") if N1a and N1b hold and N1c holds for #rest; **failed** if N1a fails or N1b's difference is ≤ 0; **mixed** otherwise. H10's literal Legendre claim is not testable here (no free week along a shared #44 field); P1 r is reported for #rest only as a descriptive.

## Result
*Run 2026-10-04 (after the prediction above). Data: `data/processed/H10-goals-are-legendre-pushes/r1b/<config>/natives.json` (G44). Script: `analysis/natives_r1b.py`. Figure: [`../../figures/r1b_models.pdf`](../../figures/r1b_models.pdf) panel (b).*
N = 4 (#best) and 10 (#rest) agents present in both segments. cos(ĝ_best, ĝ_rest) = 0.39 (bge).

| Prediction | bge-small | gte-modernbert | Verdict |
| --- | --- | --- | --- |
| N1a #best push along ĝ_best > 0, CI > 0, ε > 1 | Δ̄ +0.183 [+0.126, +0.235], ε 0.97 | Δ̄ +0.239 [+0.201, +0.277], ε 1.55 | ✗ / ✓ (bge misses ε > 1 by 0.03; goal + kickoff variant ε 1.04) |
| N1b room-specific: Δ̄_best − Δ̄_rest along ĝ_best > 0 | +0.173 [+0.113, +0.228] | +0.174 [+0.106, +0.244] | ✓ / ✓ |
| N1c #rest: no field-specific dispersal along ĝ_rest | ρ −0.51 vs ρ⊥ −0.09 (gap 0.42 > ln 1.5) | ρ −0.27 vs ρ⊥ +0.10 | ✗ / ✓ |
| N1c #best: ρ > ln 1.5, \|ρ⊥\| < ln 1.5 | ρ −0.29 (variance fell) | ρ −0.19 | ✗ / ✗ |
| #rest push along its own (self-chosen) kickoff | Δ̄ −0.051 [−0.073, −0.027] | +0.015 [−0.004, +0.033] | no push in either |

Restatement-deduped (DQ5): bge failed (ε 0.98), gte mixed (N1c_rest fails). **Reading.** The assigned room moves along its own kickoff by about one free-week SD (0.18–0.24 in alignment), the self-chosen room does not move along its kickoff at all, and the difference is room-specific in every configuration. So an operator-written target acts as a field and a "pick your own goal" instruction does not (consistent with H54). But the round-1 quench signature (variance growing along ĝ) is absent here: #best's variance along ĝ fell, which is what a tilt of a bounded distribution predicts at ε ≈ 1. The pre-registered ε > 1 threshold makes the verdict model-dependent.

## Notes
- 2026-10-04: native folder created in round 1b (DQ9 cross-index: "#44 assigned vs free room on the same days").
