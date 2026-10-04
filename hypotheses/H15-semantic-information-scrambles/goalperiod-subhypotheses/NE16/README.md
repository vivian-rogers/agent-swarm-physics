# H15 × NE16: the "never update memory" instruction removed (2026-03-26, inside #36)

**Verdict:** mixed (manipulation negligible)
**Verdict (1b):** mixed (native, 2026-10-04)
**Role:** native (round 1b, non-holdout)
**Period:** regime III · #36 "Interact with outside agents" · 12 agents · #best / #rest · units 36b (03-24 → 03-25: NE14 perma-computer-use and NE41 forced erasure begin; memory updates discouraged by a contradictory instruction) and 36c (03-26 → 03-27: NE16 fix). 507 forced erasures in 36b–36c.

## Why this NE
NE16 changes what agents write to memory at a consolidation while the erasure schedule (the 41-turn cap) stays the same. It is the closest thing in the record to KW's "erase the context with vs. without a stored copy" contrast: if the memory written at the wipe carried the session's load-bearing information, the forced-erasure output dip should be smaller in 36c (memory updates allowed) than in 36b.

## Design (native)
Same call table and estimator as `../NE41/` (ledger reset flags, per-call DQ4 work commits, real failures and write evidence). Contrast 36b vs 36c:
- manipulation check: share of forced consolidations whose memory snapshot adds ≥ 1 line, and mean stored dose;
- outcome: relative dip in work commits per call (+1…+10 vs −20…−11) and in write-evidence calls (more frequent than commits in this period), 36c − 36b, agent-day cluster bootstrap.

## Prediction
*Written 2026-10-04, before running anything split at 03-26.*
- M (manipulation): stored dose at forced consolidations is higher in 36c than in 36b. If not, NE16 did not change memory writes and the test is void (verdict n/a).
- N1 (H15 round-1 reading, R1 at the session scale): the forced-erasure dip does not shrink after the fix: 36c − 36b relative dip ∈ [−0.15, +0.15] on write evidence, CI including 0. Work commits are sparse here (low power), so only the sign is read for them.
- Counts against: 36c's dip smaller than 36b's by > 0.15 (difference > +0.15) with a CI excluding 0 (memory writes buffer the erasure).

## Result
*Run 2026-10-04 (`analysis/r1b_extra.py` → `NE16`).*

| | 36b (before fix) | 36c (after fix) |
| --- | --- | --- |
| forced erasures (with full windows) | 228 (208) | 279 (269) |
| share of forced consolidations that add ≥ 1 memory line | 0.99 | 0.99 |
| mean stored dose (lines added / lines) | 0.37 | 0.39 |
| work-commit dip | −0.39 [−0.69, +0.12] | −0.37 [−0.68, +0.46] |
| write-evidence dip | −0.13 [−0.41, +0.08] | −0.32 [−0.44, −0.15] |
| real-failure change | +0.57 [+0.10, +1.21] | +0.16 [−0.13, +0.63] |

- **M (manipulation):** passes only by the letter (0.37 → 0.39). Agents already wrote memory at 99% of forced consolidations before the fix, so the contradictory instruction did not block memory writes and NE16 is not the "erasure without a stored copy" contrast it was hoped to be.
- **N1:** 36c − 36b write-evidence dip **−0.19** [−0.43, +0.12]: outside the ±0.15 band (fails on magnitude) but in the *opposite* direction from buffering; work commits +0.02 [−0.60, +0.92] (uninformative).
- **Counts against (memory buffers the wipe):** not met: the dip did not shrink after the fix.

Verdict **mixed**: the manipulation was negligible, so this native test has little leverage; what it shows agrees with NE41 (memory writes do not buffer the erasure).
