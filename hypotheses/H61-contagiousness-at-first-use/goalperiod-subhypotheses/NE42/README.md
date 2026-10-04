# H61 × NE42: rooms merged then split at a fixed roster (#39 → #40 → #41; 2026-05-04 / 2026-05-11)

**Verdict:** mixed
**Role:** native
**Period:** #39 (two rooms), #40 (merged, regime III, mode C), #41 (split back); 15 agents; non-holdout days. Exception (c) of CLAUDE.md: the transition is the object, so models fitted in one week are scored in the next.

## Why this period
The only A-B-A change of room size at a fixed roster: an intervention on the receptive count (axis E).

## Prediction
*Written 2026-10-04 19:30 UTC, before any native statistic.* NE42: #best and #rest merge into one room on 2026-05-04 (#40) and split back to the same partition on 05-11 (#41), at a fixed roster (#39 → #40 → #41). The merge raises the number of agents present per room (H34 N_room 11 → 14 → 11). The goal changes too (#40 is a shared objective), which confounds the merge.
Model F⁺ = F with the receptive *count* log(1 + n_receptive) and log room size in place of the receptive fraction (counts transfer across room sizes; fractions do not).
- **N42-a (transfer):** F⁺ fitted on all of #39 forecasts #40 better than B3 fitted on #39 (ΔLL > 0, idea-cluster CI > 0), and F⁺ fitted on #40 forecasts #41 better than B3 fitted on #40.
- **N42-b (calibration):** the #39 F⁺ model's mean predicted P(Y) for #40 is closer to #40's observed rate than B3's (B3 has no room-size or receptive term).
- **N42-c (stable sign):** the receptive-count coefficient, fitted separately in #39, #40 and #41, is > 0 in all three.
- Credence 0.4 (the goal change and small rate shifts, about +13% from H34's N^0.45 scaling, limit power). Verdict: supported = N42-a and N42-b pass; failed = N42-a fails in both transfers; mixed = otherwise.

## Result
*Run 2026-10-04 after the prediction above.* Agents present per room-day (median): #39 11, #40 14, #41 10; mean receptive count (5 min): 8.6, 11.9, 7.7.

| Prediction | Observed | Verdict |
| --- | --- | --- |
| N42-a #39 → #40: ΔLL(F⁺ − B3) > 0, CI > 0 | 33.0 [22.0, 43.5] millinats/idea (5442 ideas) | pass |
| N42-a #40 → #41 | -298.0 [-342.5, -257.5] (4725 ideas) | fail |
| N42-b #40 calibration: F⁺ closer to observed than B3 | observed 0.155; F⁺ 0.127; B3 0.077 | pass |
| N42-c receptive-count coefficient > 0 in each week | #39 -0.25 ± 0.27; #40 +0.04 ± 0.05; #41 +0.13 ± 0.12 | fail |

**Native verdict: mixed.** #41 calibration (descriptive): observed 0.212; F⁺ 0.023; B3 0.172.
