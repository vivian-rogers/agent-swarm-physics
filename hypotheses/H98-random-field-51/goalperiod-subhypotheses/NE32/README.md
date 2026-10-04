# H98 × NE32: isolated newcomers and their rivals (2026-07-09 → 07-16)

**Verdict:** n/a
**Role:** native (exploratory)
**Period:** regime III · #51 private roles · 07-09: GPT-5.6 Sol, Terra and Luna join in separate isolated rooms, which close 07-10 (NE32). Units 51b (07-09, 1 day) and 51c (07-10 → 07-16, merged).

## Why this period
Each newcomer received a role that an incumbent already held: forecaster (35 ↔ 20), YouTuber (36 ↔ 18), diplomat (37 ↔ 17) (DQ6 rival pairs). On 07-09 a newcomer could not read its rival (isolated room). A shared random field (the role niche) aligns rivals without any reading; a coupling (R3) needs reading and should build up after the rooms merge. This separates field from coupling by design, which no other #51 day allows.

## Prediction
*Written 2026-10-04 20:25 UTC, before running on this period.*
- **N1a (field without reading).** On 07-09, each newcomer's day state (day field removed, primary variant) aligns with its rival's static field (φ from 51c, centered) more than with non-rival incumbents' static fields. Statistic: the rival's alignment percentile among incumbents, averaged over the 3 newcomers; null: random incumbent labels (exact enumeration). Predicted mean percentile ≥ 0.8 and p < 0.05. Credence 0.65.
- **N1b (no build-up after merging).** The newcomer–rival alignment in 51c (merged, agent static fields) minus that on 07-09, averaged over the 3 pairs, is ≤ +0.10. R3 (coupling through reading) predicts a rise. Credence 0.6.
- **N1c (co-movement without reading, descriptive).** Window co-movement on 07-09 for the 3 rival pairs minus non-rival newcomer–incumbent pairs > 0. One day: low power, sign only.
- **Manipulation check:** ledger reads between each newcomer and its rival on 07-09 are 0 (`pair_day_reads`).
- Counts against the field reading: N1a percentile ≤ 0.6, or N1b rise > 0.2 (alignment built by reading).

**Amendment A1 (2026-10-04 20:26 UTC, before running; from `rooms_timeline` only, no outcome seen).** The isolated rooms (10, 11, 12) held the newcomers only from ≈ 20:04 to 21:38–22:02 UTC on 07-09; they then moved to #general the same day. So:
- the **isolated state** of a newcomer is the mean of its statements (chat + intentions, primary variant) with t inside its own isolated interval; it needs ≥ 3 statements, else N1a is untestable for that newcomer;
- the incumbents' static fields come from **51a (07-06 → 07-08)**, before any newcomer existed, so no incumbent can have copied a newcomer;
- N1b compares the isolated state with the newcomer's 51c static field (both aligned to the incumbents' 51a fields);
- the **manipulation check** uses ledger items (`context_ledger_items`) received by the newcomer's calls inside its isolated interval: items authored by its rival must number 0;
- N1c (window co-movement) is dropped: the isolated interval holds 3–4 thirty-minute windows.

## Result
*Run 2026-10-04 20:49 UTC.*
- **Untestable.** The newcomers made 1, 0 and 0 statements during their isolated intervals (118, 97 and 93 min). N1a needs ≥ 3, so N1a and N1b cannot be computed.
- **Manipulation check:** their calls inside the interval received 3 items each, none from an agent (0 from their rivals). The isolation was real; the newcomers were onboarding, not working.
- The question moved to the NE33 native (late joiners), added before it ran.
