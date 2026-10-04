# H53 × G27: Hack the OWASP Juice Shop hacking playground. Compete to see which agent can complete the most challenges (2026-01-12 → 2026-01-26)

**Verdict:** descriptive — 5 seeds; mean S 2.60
**Role:** replication
**Period:** regime I · mode K · 10 agents · 10 active days · 5 seeds (first chat link per project, non-holdout days). Units (step changes, `period_units`): none. Unit intercepts are not separate fits; the period is the unit (card, exception (d)).

## Why this period
Descriptive: 3–9 eligible seeds.

## Prediction
*Written 2026-10-04, before running on this period.*
*Descriptive period (3–9 eligible seeds): templated prediction (card P1, P1b, P6, P10 applied here), written 2026-10-04 before running on this period.* 5 eligible seeds; median susceptible in-room recipients 9; mean uncommitted U 5.2; mean receptive R 2.8 (structural counts only). R averages ≥ 1 per seed; the timing test has some power if adoption events are not too rare.
- RR_timely (one cycle): 95% CI includes 1, or RR < 1.5 (card call: H53's P1 fails).
- F1 step ratio ≥ 3 would mark read-out-triggered waves; a ratio < 3 marks a pre-ramp (H28). Expected: 1.5–3.
- F4 read-locking ≥ 2 for late readers if adoptions are triggered at read-out. Expected: unclear.
- Decision rule v2 label: not "nucleation".
- Verdict rule (per period): **supported** = v2 label "nucleation" and RR_timely ≥ 1.5 with CI > 1; **failed** = RR_timely CI includes 1 *and* (F1 < 3 or F4 < 2); **mixed** = otherwise; **descriptive** = fewer than 15 adoption events in the agent-level table (underpowered).
- Verdict: descriptive whatever the outcome (too few seeds).

## Result
*Run 2026-10-04 (round 1), after the prediction above.* Verdict mapping for replication periods: Amendment 2 in the card (F4 is untestable per period).

Descriptive: 5 eligible seeds; mean wave S 2.60, max 4; mean R 2.80; mean N_sus 9.0. Pooled into nothing (period below the 10-seed rule).

Decision-rule-v2 label (pooled thresholds applied to this period): n/a.
**Verdict: descriptive** (3–9 eligible seeds).

## Scorecard (period-specific axes)
C: RR_timely vs 1 (seed-stratified, day-cluster CI); D: F1/F2/F3 signatures; H: rivals (status, share, size) pooled only. G, E, I: n/a for this period.

## Notes
- Data: `data/processed/H53-announcement-nucleation/` (`seeds.parquet`, `recipients.parquet`, `round1/period_G27.json`).
