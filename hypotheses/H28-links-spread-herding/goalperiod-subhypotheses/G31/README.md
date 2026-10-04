# H28 × G31: Pick your own goal (farewell to Claude 3.7 Sonnet) (2026-02-16 → 2026-02-23)

**Verdict:** mixed (P1 weak)
**Verdict (1b):** failed (native: work switches κ +0.57 ± 0.24 but z_shift +0.2 and κ_lead +1.20 > κ; ledger attention κ +0.48, z +0.7)
**Role:** native (round 1b: the time-capsule wave measured in work commits, DQ4; round 1: exploratory candidate)
**Period:** regime I · mode F · 12 agents on the roster · 5 non-holdout days.

## Why this period
Named candidate and the clearest pile-on: H11 herding waves onto successive shared repos (time capsule at 11 agents in one window; βJ_CW +4.9, local-shift z +8.3). Free week, so no goal field beyond the farewell.

## Prediction
*Written 2026-10-04, before running on this period.*

Card rules (P1–P10, Amendment 1) apply; tested only if ≥ 30 arrivals and ≥ 20 links to universe projects.

- **Here:** P1 supported with the strongest κ of the regime-I periods (e^κ 2–5); R_link 0.15–0.35; f = 0 lowers the simulated peak occupancy by 10–30% but the time-capsule pile-on stays (≥ 50% of f = 1).
- **Counts against:** κ̂ ≤ 0 or inside the link time-shift null; κ_lead ≈ κ; κ vanishing with the momentum control; an effect only in returns.

## Result
*Run 2026-10-04 (`analysis/explore.py`; data `data/processed/H28-links-spread-herding/G31/round1.json`).* 710 arrivals (260 first), 434 links to 30 universe projects, 250 arrivals within 60 min of a visible link. Tested.

| Test | Observed | Rule | Verdict |
| --- | --- | --- | --- |
| P1 κ (any visible link, last 60 min) | +0.47 ± 0.14 (e^κ 1.60); p 0.000937; z_shift +0.8 (null +0.38 ± 0.11, n = 99) | κ > 0, z ≥ 2, p < 0.05 | weak |
| P2a lead placebo | κ_lead +1.15; κ − κ_lead -0.80 (one-sided p 1) | κ − κ_lead > 0, p < 0.05 | fail |
| P2b momentum control | κ +0.46 (p 0.00135); momentum +0.56 | ≥ 50% of κ, p < 0.05 | pass |
| P3a naive agents | κ +0.57 ± 0.25 (p 0.0201); first arrivals 260 | κ > 0 | pass |
| P3b pre-trend (O/E) | pre 1.90 (46 obs), post 2.88 (66 obs) | pre excess < ½ post excess | pass |
| P4 dose | d11 +0.50 (n_ev 108); d12 +0.22 (n_ev 33); d13 +0.61 (n_ev 25); dS2 +0.55 (n_ev 84); CV complex − simple -4.6 | 1-link HR > 1; S2 adds < 50% | pass |
| P5 λ (extra arrivals per exposure) | 0.036 [0.017, 0.060]; N_exp 2599 | 0.01–0.15 | pass |
| P6 R_link | 0.13 [0.06, 0.22]; R_all (links + occupancy) 0.51 | < 0.5 | pass |
| P10 occupancy J | J +0.84 (pd FE +0.16); without links +1.05 | J > 0 both; drop < 50% | pass |
| P7 counterfactual peak occupancy | f=0.5 ×0.98; f=0 ×0.92; cap ×0.96; burst f=0 ×0.92 | f=0: 0.70–0.90 (≥ 0.5) | fail |
| P7 calibration (unfitted) | observed peak 11 vs sim [9, 11]; burst 10 vs [8, 11] | inside 90% | pass |
| P8 latency (median excess lag) | 8 min; excess 0–15 +193.5, 15–60 -124.5, 60–240 -148.2 | post-NE09 < pre | – |

## Scorecard (period-specific axes)
- **C:** link time-shift null z +0.8; held-out (quarter-blocked) Δ log-lik primary − occupancy-only -23.8.
- **D:** simulated pile-on calibration inside the 90% interval.
- **H:** lead not beaten; momentum survived.

## Notes
- *Post hoc robustness (coordinator request, 2026-10-04):* on the deterministic shared labels (`project_states.parquet`, 30 min, window switches) κ = +0.11 ± 0.24 (p 0.637; 133 switches), z_shift -4.1.
- *Post hoc short-lag check:* visible link in the last 15 min b = +0.51 ± 0.12 (z vs shift null +4.3); link arriving in the next 15 min b = +0.98 ± 0.12; lag − lead -0.47 (one-sided p 0.998). Action-only latency: median excess lag 8 min.
- Holdout days: none in this period's build (non-holdout days only).

## Round 1b native: do links recruit *work*? (DQ4 work ledger)
*Prediction written 2026-10-04 16:40 UTC, before any round-1b statistic was computed.* **Seen beforehand:** round 1 above; H11's round-1b note that #31's herding wave appears in work commits (its top three repos are committed to by 11, 9 and 8 distinct agents over the week); RE-P1's note that work herds onto the same repos as attention in shared weeks. No work-switch hazard, work-arrival count or ledger exposure had been computed for H28.

**Design.** Same risk-set model, fixed effects (agent + project + day) and link features as the primary fit, with two changes: (1) link exposure on ledger visibility (t_vis = receiving call); (2) touches are **agent work commits** (DQ4 `work_commits`: `canonical & ~imported & author_kind == agent & ~automated`), so an agent is *on* X while it committed to X in the last 60 min and a **work arrival** is its first commit to X after ≥ 60 min without one. Universe: round 1's (attention-based) projects. Statistics: κ_work (E60), its link time-shift z (39 shifts), κ_lead,work in the joint lead model.

**Predictions:**
- **N31a:** κ_work > 0 at p < 0.05 [0.6].
- **N31b:** κ_lead,work ≥ κ_work (the lead ≥ lag pattern of attention carries over to work) [0.6].
- **N31c:** z_shift(κ_work) < 2 [0.6].

**Verdict rule:** *supported* (links recruit work) if κ_work > 0 at p < 0.05, z_shift ≥ 2 and κ_work > κ_lead,work; *failed* if κ_work's p ≥ 0.05 or κ_lead,work ≥ κ_work with z_shift < 2; *mixed* otherwise. Tested only if ≥ 30 work arrivals.

### Result (round 1b, run 2026-10-04)
`H28_DATA=r1b H28_TOUCH=work analysis/explore.py` → `data/processed/H28-links-spread-herding/r1b/G31/round1b_work.json` (39 shifts). 252 work arrivals (128 first), 434 links to the universe; tested.

| Test | Observed | Prediction | Verdict |
| --- | --- | --- | --- |
| N31a κ_work | **+0.57 ± 0.24** (e^κ 1.77, p 0.016) | > 0, p < 0.05 | pass |
| N31b lead vs lag (joint model) | κ_lead,work **+1.20** vs κ_work +0.40; difference −0.80 ± 0.26 | lead ≥ lag | pass |
| N31c link time-shift z | **+0.2** (null mean +0.55 ± 0.12) | < 2 | pass |
| (descriptive) momentum control; naive agents | κ +0.56 (p 0.016); naive κ +1.26 ± 0.37 | — | — |
| (descriptive) attention arrivals on ledger visibility | κ +0.48 ± 0.14, z +0.7, κ_lead +1.15 (round 1: +0.47, z +0.8) | — | — |

**Reading.** Links go with first commits to a repo about as strongly as with first mentions (e^κ ≈ 1.8 vs 1.6), but a link arriving in the *next* hour predicts the commit three times as strongly, and links moved ±30–120 min predict it just as well. The #31 wave is a burst in work as well as attention, and links mark it rather than recruit into it.

**Verdict (H28 here): failed** (all three predictions held; links do not recruit work).
