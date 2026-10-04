# H45 × G51: maximize your private role (#51 head, 2026-07-06 → 09-04)

**Verdict:** failed (N sweep slope 0.90 [0.77, 0.99] × passive; RI 0.04 [0.02, 0.05])
**Role:** native (N sweep across units 51a–51l), plus the replication estimators
**Period:** regime III · one room (#general; #focus in 51g) · N 21 → 32 in 11 dated steps (period_units 51a–51l) · 45 non-holdout days, 8 h/day. The tail 51m (09-07 → 09-18) is held out. Splits: the period_units steps (joins; NE32 07-09; NE38 07-29; bookends end 08-05; nudges end 08-21 inside 51g).

## Why this period
The roster grows from 21 to 32 agents at a fixed goal, room and hours, so the room traffic each agent receives per call rises in steps that the agent does not choose. Under passive accumulation an agent's set point rises with its inflow (slope 1 − s̄ in logs); a homeostat holds it. #51 also carries the largest sample of forced erasures (14.6k), talk calls with reply labels, and the only non-holdout days under the 200-event cap (NE22 itself, 06-11, is held out).

## Prediction
*Written 2026-10-04 06:32 UTC, before running H45 on #51.*
- **W1 (flood exists):** λ (inflow per call) rises with N across units (Spearman ρ > 0.5 over unit medians).
- **W2 (N sweep, H45):** the within-agent slope of ln s\* on ln λ across units (agent fixed effects, agent-units with ≥ 30 band calls) divided by (1 − s̄) is ≤ 0.3 (the set point holds). Passive: ≈ 1. My prior: ≈ 1.
- **W3 (replication estimators, card rule):** RI, η_W, β, γ_R/γ_W and the forced-reset overshoot as in the card (P1, P4, P5, P6), with agent × unit fixed effects.
- **W4 (200-event cap):** cap-hit calls are < 0.1% of #51 calls and occur at the first call after a long absence; the omitted items lower that call's room tokens, but the cap does not set any agent's s\* (descriptive).

## Result
| Prediction | Observed | Null / reference | Verdict |
| --- | --- | --- | --- |
| W1: λ rises with N across units (ρ > 0.5) | ρ(N, λ) 0.38 over 12 units; λ 235–532 room tokens per call, highest in 51k–51l (N 31–32); ρ(N, s) 0.39 | – | not met (a weak flood; inflow per call also depends on call cadence) |
| W2 (H45): within-agent slope of ln s\* on ln λ across units / (1 − s̄) ≤ 0.3 | **0.90** [0.77, 0.99] (254 agent-units, 27 agents; s̄ 0.20) | passive 1 | **failed** (near passive) |
| W3 P1: RI ≥ 0.5 | RI 0.04 [0.02, 0.05] (ε 0.80 vs passive 0.83; η_W −0.04 [−0.06, −0.02]; 19,692 segments, 32 agents) | 0 | failed |
| W3 P3: CV ratio ≤ 0.5 | 1.07 (observed CV 0.55 > permuted 0.51) | 1 | failed |
| W3 P2 (A1): lever slope < 0 | −0.044 [−0.057, −0.030] (9,494 voluntary segments) | 0 (passive synthetic); controller −0.10 | met on sign, weak |
| W3 P4: β ∈ [0.4, 0.9] | 0.91 [0.88, 0.94] (33,091 talk calls) | H18 (mentions) 0.61 | just outside |
| W3 P5: γ_R < 0, γ_W > 0 | γ_R +0.090 [0.065, 0.116]; γ_W −0.065 [−0.114, −0.005] (32,010 cu talk calls) | controller pattern | failed (opposite on γ_R; competition-like on γ_W) |
| W3 P6: forced-reset talk ≥ 1.2 | 0.77 [0.70, 0.84], τ 11 calls (14,600 segments); voluntary 0.64 [0.57, 0.71] | 1 | failed (undershoot) |
| W3 P8: P growth ≥ 1.3 | 1.92 (IQR 1.67–2.15) | 1 under truncation | met |
| W4: 200-event cap | 443 of 928,207 calls (0.048%), 34,612 omitted items; cap hits follow timer pauses (303), memory calls (85) and first calls of the day (31); median position 16 | – | met (< 0.1%); it sets no agent's s\* |

Set points: s\* median 0.18 (range 0.09–0.68 over 31 agents), the highest of any period (one large room).

**Reading.** As the roster grows from 21 to 32, the agents' room share moves with their inflow at 0.90 × the passive slope. There is a slight compensation (RI 0.04; voluntary consolidations come ~4% sooner per doubling of early inflow), but it is an order of magnitude below a homeostat. Engagement rises with room content already in context and falls with own content. That is conversational momentum plus own-work competition, not a share controller; post hoc, the momentum part goes with having already talked in the segment (`posthoc.json`). The 200-event cap is a scaffold ceiling on items per call that binds almost only after long timer pauses in this busy room. It is too rare to set anyone's share.

Figures: card `figures/`. Data: `G51/results.json`, `G51/native.json`.

## Scorecard (period-specific axes)
- **C:** RI's CI excludes both 0 (slightly) and 0.5; passive is the better description.
- **E:** roster steps act as an exogenous flood: set points follow at 0.90 × passive.
- **G:** cap hits sit where the scaffold rule says (> 200 events after pauses).

## Notes
- 2026-10-04 06:32 UTC: prediction written before the run.
- 2026-10-04: results from `analysis/run_periods.py` and `analysis/natives.py`; Amendments A1–A3 apply.
