# H29 × G26: the elected leader (2026-01-05 → 2026-01-09)

**Verdict:** failed
**Role:** native (round 1b, non-holdout)
**Period:** regime I · one room · 5 days · DQ6 ground truth: approval vote → 9–9–9 tie → runoff 7–1–0; agent 17 elected at 2026-01-05 19:35:22 UTC (term 1), re-elected 9–0 on 01-09 19:00:43 UTC.

## Why this period
The only non-holdout period with an elected leader and a known start time. If leadership makes a driver node, the winner's outgoing influence should rise after 19:35 on 01-05 relative to everyone else's.

## Prediction
*Written 2026-10-04 07:31 UTC, before running anything on #26. Seen before writing: DQ6's phase, ballot and leader rows (timing and winner only) and H32's round-1 note that the winner ranks 7/10 in information current after the vote.*

Observables as in G35 (R reply attention per message, P_u broadcast pull per message, Vol), for agent 17 before (01-05 up to 19:35 UTC) vs after (01-05 19:35 → 01-09), each as a difference-in-differences against the median of the other agents' before/after changes; bootstrap over days (post) and 30-min blocks (pre).

Predictions:
- **N1:** R(17) rises more than the others' (DiD log ratio > 0, point).
- **N2:** P_u(17) does not rise more than the others' (DiD CI includes 0). Regime I couples unaddressed messages more than regime III (H50: 0.031 vs 0.042), so N2 is less certain here than in #35.
- **Verdict rule:** supported if N1 and N2; failed if P_u's DiD > 0 with CI excluding 0, or R's DiD ≤ 0; mixed otherwise. Credence 0.45.

## Result
*Run 2026-10-04 ~08:50 UTC (`analysis/r1b_extra.py`; ledger rows, native unit G26; regime-I whitener). Pre = 01-05 before 19:35:22 UTC; post = after it to 01-09. Log ratios (R) and differences (P_u) post − pre per agent; DiD = agent 17 minus the median of the other 9.*

| Statistic | agent 17 | others (median) | DiD | rank of 17 among 10 | Prediction | Verdict |
| --- | --- | --- | --- | --- | --- | --- |
| R reply attention per message (log ratio) | +0.34 | +0.54 | **-0.20** | 5 | DiD > 0 | ✗ |
| P_u broadcast pull (bge) | -0.012 | -0.092 | +0.080 | 10 (largest) | DiD CI ∋ 0 | ✗ by rank (p ≈ 0.1) |
| P_u broadcast pull (gte) | -0.031 | -0.105 | +0.074 | 10 (largest) | | |

Agent 17 before / after: messages 25 / 158; replies per message 0.69 / 0.97.

**Verdict: failed** (by the reply clause). After winning the runoff the leader did not gain reply attention relative to the others (DiD −0.20, rank 5/10), while its broadcast pull on unnamed recipients rose more than anyone else's in both models (rank 10/10; with 10 agents that is p ≈ 0.1, so the N2 falsifier is not formally met). Regime I couples unaddressed messages (H50), so an elected leader's broadcasts may carry there in a way they do not in regime III. The pre side is short (one afternoon), so this is a weak test.
