# H53 × G26: Elect a village leader. They choose this week’s goal! (2026-01-05 → 2026-01-12)

**Verdict:** mixed — runoff 8/8 ballots = readers in window; 17/17 ballots after read-out in runoff + confirmatory; ρ fails
**Role:** native
**Period:** regime I · mode C · 10 agents · 5 active days · 48 seeds (first chat link per project, non-holdout days). Units (step changes, `period_units`): none. Unit intercepts are not separate fits; the period is the unit (card, exception (d)).

## Why this period
Native test: see the prediction below.

## Prediction
*Written 2026-10-04, before running on this period.*
**Native test (election rounds; DQ6 ground truth).** Seeds are the three round-opening announcements in `ground_truth_labels` (`phase` rows, preferred): the 01-05 approval vote, the 01-05 runoff (opened 19:32:19 UTC, closed 19:34:00, 7–1–0) and the 01-09 confirmatory vote (scheduled window 18:45–19:00). The wave is the ballots (`ballot` rows; voter = `agent_a`; each voter's first ballot per round). Read-out = the voter's ledger receiving call of the announcement.
- **N26-a (read-out gating):** ≥ 90% of ballots are cast at or after the voter's read-out call of the round's announcement. Against: ≥ 2 ballots in a round before the voter's read-out (anticipation). Credence 0.8.
- **N26-b (latency):** in each round the median number of the voter's calls from read-out to ballot is ≤ 2. Credence 0.6.
- **N26-c (order):** Spearman ρ(read-out time, ballot time) ≥ 0.6 in the runoff and in the confirmatory round. Credence 0.6.
- **N26-d (wave = receptive count):** in the runoff, ballots cast within the 100-s window = voters whose read-out fell inside the window, ±1; non-voters read late or not at all. Credence 0.6.
- **N26-e (scheduled-field rival):** the 01-09 round was scheduled in advance. A clock-driven field predicts ballots at 18:45 regardless of read-out; H53 predicts ballots follow the opening message's read-out (N26-a holds in round 2). Credence 0.7.
- The replication estimator also runs on #26's link seeds (templated prediction as for replication periods: RR_timely CI includes 1).

*Templated replication prediction (card P1, P1b, P6, P10 applied here), written 2026-10-04 before running on this period.* 37 eligible seeds; median susceptible in-room recipients 9; mean uncommitted U 4.8; mean receptive R 2.3 (structural counts only). R averages ≥ 1 per seed; the timing test has some power if adoption events are not too rare.
- RR_timely (one cycle): 95% CI includes 1, or RR < 1.5 (card call: H53's P1 fails).
- F1 step ratio ≥ 3 would mark read-out-triggered waves; a ratio < 3 marks a pre-ramp (H28). Expected: 1.5–3.
- F4 read-locking ≥ 2 for late readers if adoptions are triggered at read-out. Expected: unclear.
- Decision rule v2 label: not "nucleation".
- Verdict rule (per period): **supported** = v2 label "nucleation" and RR_timely ≥ 1.5 with CI > 1; **failed** = RR_timely CI includes 1 *and* (F1 < 3 or F4 < 2); **mixed** = otherwise; **descriptive** = fewer than 15 adoption events in the agent-level table (underpowered).

## Result
*Run 2026-10-04 (round 1), after the prediction above.* Verdict mapping for replication periods: Amendment 2 in the card (F4 is untestable per period).

| Prediction | Observed | Verdict |
| --- | --- | --- |
| N26-a ≥ 90% of ballots at or after the voter's read-out of the round's opening message | runoff 100% (8), confirmatory 100% (9), approval 25% (8): 6 approval ballots precede the record's opening message; pooled 19/25 | pass in 2/3 rounds; fail pooled |
| N26-b median calls from read-out to ballot ≤ 2 | runoff 1 (calls [1, 1, 1, 1, 1, 1, 2, 3]), confirmatory 1 ([1, 1, 1, 1, 1, 1, 1, 1, 3]); approval n/a (ballots before the message) | pass (2/2 scorable rounds): most ballots are cast by the reading call itself |
| N26-c Spearman ρ(read-out, ballot) ≥ 0.6 | runoff 0.36, confirmatory 0.15 | fail: read-outs spread over ~1 min, less than call latencies vary, so order is scrambled |
| N26-d runoff ballots in the 100-s window = readers in the window ±1 | 8 ballots vs 8 readers; the one non-voter read at 116 s, after the close | pass |
| N26-e scheduled round (01-09): ballots follow the opening message's read-out, not the clock | 0 ballots before the message; 100% after read-out | pass |
| *Post hoc:* approval wave seeded by the first ballot (DQ2: later ballots are top-1 replies to it) | 100% of 8 later ballots after their read-out of it; calls [1, 1, 1, 1, 2, 1, 5, 4]; read ages (s) [7.7, 13.1, 20.8, 9.5, 0.3, 100.7, 219.9, 15.3] | descriptive |

**Replication estimator on this period (context):**

| Prediction (templated) | Observed | Null / reference | Verdict |
| --- | --- | --- | --- |
| P1 RR_timely (one cycle) ≥ 1.5, CI > 1 | 0.99 [0.61, 1.61] (69 adoptions) | 1 (synthetic nulls: CI > 1 in 0–10% of runs) | fail |
| P1b RR_timely (10 min) | 0.69 [0.46, 1.03] | 1 | — |
| F1 step (adoptions 30 min after / before the seed) | ∞ (no pre-seed adoption) (pre 0, post 65) | ≈ 1 field, < 1 pre-ramp, > 10 read-out-triggered (synthetic) | step |
| F2 other-room / same-room adoption | n/a (0 multi-room seeds) | ≈ 1 field, ≈ 0.3 nucleation | — |
| F3 adopters never exposed to a link before adopting | 0.03 (n = 69) | — | — |
| F4 late-reader read-locking | n = 2, ratio 0.00 | untestable below 10 | — |
| Waves | mean S 1.86, max 7, zero 46%; mean R 2.32; herded 8, never 26 | — | — |

Decision-rule-v2 label (pooled thresholds applied to this period): seed-locked field (F4 untestable here, so a "seed-locked field" label only means read-out locking could not be shown).
**Verdict: mixed** (read-out gating and wave = receptive count hold in the two rounds with a correctly placed seed; the rank-order prediction fails, and the approval round's recorded opening came after most ballots).

## Scorecard (period-specific axes)
G (ground truth, DQ6 ballots and phases): read-out gating confirmed in 2/3 rounds. E: the scheduled 01-09 round is a quasi-intervention (clock vs message): ballots follow the message. D: wave = receptive count in the 100-s runoff window (an unfitted statistic).

## Notes
- Data: `data/processed/H53-announcement-nucleation/` (`seeds.parquet`, `recipients.parquet`, `round1/period_G26.json`).
