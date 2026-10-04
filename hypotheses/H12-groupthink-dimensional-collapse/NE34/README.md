# H12 × NE34: goal kickoffs as field quenches (event study across non-holdout transitions)

**Verdict:** failed
**Role:** exploratory (round 1, non-holdout)
**Period:** NE34, all goal transitions g−1 → g where both sides are non-holdout, both days are in the same regime, and both first hours have a valid PR30. That gives 20 usable transitions (15 regime I, 1 regime II, 4 regime III), against 189 placebo pairs (consecutive days inside one unit). Named exception (c) of the unit-of-analysis rule: the transition is the object.

## Why this natural experiment
A kickoff is a documented step in the external field: a new goal text, posted before day 1's window (H04). HH58 says a field quench should collapse the swarm's semantic dimensionality: everyone talks about the new goal. Rival R4 says consensus forms over the week instead, so dimensionality is highest right after the kickoff.

## Prediction
*Written 2026-10-03, before any H12 real-data run, as P6/P7 on the card (`../README.md`). This folder was created after the run, so the text below is copied from the card verbatim, not rewritten.*
- **P6, kickoff collapse (NE34; axis E).**
  - ΔPR_kick = PR₁ₕ(day 1 of g) − PR₁ₕ(last day of g−1), where PR₁ₕ is the mean PR30 over the first two 30-min windows.
  - Placebos: the same contrast for consecutive active days inside a unit, from day 1 → 2 onward.
  - *Prediction:* median ΔPR_kick < 0; ≥ 2/3 of kickoff contrasts negative; kickoff contrasts below the placebo contrasts (one-sided Mann–Whitney p < 0.05); median relative drop ≥ 10%. Spread TV also drops (same test).
  - *Falsifier:* kickoff contrasts indistinguishable from placebos (p ≥ 0.2) or median ≥ 0.
- **P7, re-expansion after the kickoff ("field quench" over R4).** PRday(day 1) < median PRday(days 2+) in ≥ 2/3 of units. Day 1 higher than later days in ≥ 1/2 of units would favor R4.
- **Amendment 1, item 7.** P6 has 73% power for a 10% drop when day-to-day PR variability is ≤ 10%. If the placebo sd exceeds 15% of PR, a P6 failure means "underpowered for drops < 20%".

## Result
| Statistic | Predicted | Observed | Verdict |
| --- | --- | --- | --- |
| median ΔPR_kick | < 0 | **+0.96** (relative **+7%**) | ✗ |
| share of kickoffs negative | ≥ 2/3 | 9/20 (45%) | ✗ |
| kickoffs vs placebos (one-sided MW) | p < 0.05 | p = 0.86 (0.86 without day 1 → 2 placebos) | ✗ |
| median relative drop | ≥ 10% | −7% (a rise) | ✗ |
| spread TV | drops | median ΔTV +0.07, p = 0.28 | ✗ |
| placebo relative sd (power check) | ≤ 0.15 for full power | 0.21 | underpowered for < 20% drops; but the point estimate is a rise |
| P7: day 1 < later days | ≥ 2/3 of N ≥ 10 periods | 3/16; **day 1 higher in 13/16** (two-sided sign test p = 0.02) | ✗ (R4 direction) |

By regime: regime I median −2% (6/15 up); regime III **+44% (4/4 up)**; regime II +14% (n = 1).

| Transition | Days | Regime | Mode | PR₁ₕ pre → post | ΔPR | ΔTV |
| --- | --- | --- | --- | --- | --- | --- |
| #3 → #4 | 2025-05-14 → 2025-05-15 | I | F → C | 13.5 → 8.0 | -41% | +3.5 |
| #4 → #5 | 2025-06-18 → 2025-06-19 | I | C → F | 11.2 → 14.1 | +26% | +3.2 |
| #10 → #11 | 2025-08-22 → 2025-08-25 | I | I → F | 6.4 → 8.3 | +28% | +6.0 |
| #11 → #12 | 2025-08-29 → 2025-09-01 | I | F → M | 13.3 → 11.5 | -14% | -2.8 |
| #12 → #13 | 2025-09-05 → 2025-09-08 | I | M → C | 13.5 → 13.3 | -2% | +1.7 |
| #16 → #17 | 2025-10-10 → 2025-10-13 | I | F → I | 13.2 → 11.8 | -10% | +0.5 |
| #17 → #18 | 2025-10-17 → 2025-10-20 | I | I → C | 12.1 → 16.4 | +36% | +0.5 |
| #18 → #19 | 2025-10-31 → 2025-11-03 | I | C → C | 13.4 → 13.5 | +1% | -4.0 |
| #19 → #20 | 2025-11-14 → 2025-11-17 | I | C → I | 12.4 → 15.9 | +28% | -2.3 |
| #20 → #21 | 2025-11-28 → 2025-12-01 | I | I → I | 15.3 → 15.0 | -2% | -4.9 |
| #23 → #24 | 2025-12-19 → 2025-12-22 | I | K → C | 11.9 → 13.8 | +16% | +3.7 |
| #24 → #25 | 2025-12-26 → 2025-12-29 | I | C → C | 14.2 → 13.2 | -7% | -0.2 |
| #25 → #26 | 2026-01-02 → 2026-01-05 | I | C → C | 15.7 → 12.1 | -23% | -4.3 |
| #26 → #27 | 2026-01-09 → 2026-01-12 | I | C → K | 11.5 → 8.7 | -25% | +4.9 |
| #30 → #31 | 2026-02-13 → 2026-02-16 | I | C → F | 15.8 → 13.2 | -17% | +5.8 |
| #35 → #36 | 2026-03-20 → 2026-03-23 | II | C → C | 14.7 → 16.8 | +14% | -5.4 |
| #36 → #37 | 2026-03-27 → 2026-03-30 | III | C → F | 11.8 → 16.8 | +42% | -5.7 |
| #38 → #39 | 2026-04-24 → 2026-04-27 | III | C → I | 7.7 → 14.5 | +87% | +0.3 |
| #40 → #41 | 2026-05-08 → 2026-05-11 | III | C → I | 10.3 → 15.0 | +45% | -2.6 |
| #41 → #42 | 2026-05-15 → 2026-05-18 | III | I → I | 11.8 → 15.8 | +33% | -6.4 |

Data: `data/processed/H12-groupthink-dimensional-collapse/ne34_kickoffs.parquet`, `ne34_placebos.parquet`, `p7_day1.parquet`. Code: `analysis/evaluate.py` (`ne34`). Figure: `../figures/dimensionality_arm.pdf` (panels a and b).

**Post hoc (no verdict).**
- *Self-repetition.* Removing within-agent near-duplicate chat statements (cosine > 0.95 to the same agent's earlier statement that day; 12% of chat) leaves P6 null: median +0.1%, p = 0.86. The regime-III kickoff rise stays at +35%, and day 1 is still higher in 12/15 periods (p = 0.035).
- *End-of-goal loops.* The low pre-kickoff PR in regime III (last days of #38 and #40) coincides with heavy self-repetition: 16–40% of chat statements in #38–#40 are near-copies of the same agent's earlier text. Part of the "kickoff expansion" in regime III is the kickoff breaking end-of-goal loops.

## Scorecard (NE-specific axes)
- **E (interventional): 0.** The predicted sign is wrong. Kickoffs leave first-hour PR unchanged in regime I and raise it in regime III.
- **H (comparative): 0 for HH58.** R4 ("consensus formation": dimensionality is high right after the kickoff and lower later) beats the field-quench reading on the day-1 comparison. It does not, however, predict the consistent decline over days 2..D (P8 failed).

## Notes
- 2026-10-03: folder created after the round-1 run. The prediction is the card's pre-run P6/P7, copied verbatim.
- Transitions touching held-out periods are excluded. The fully held-out transitions (#28 → #29, #45 → #46 … #49 → #50) are reserved for `analysis/confirm.py` (C6).
