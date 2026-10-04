# H01 × NE29: same-lab succession Claude 3.7 Sonnet → Claude Sonnet 4.6 (#31), exploratory stand-in for NE30

**Verdict:** mixed (the successor joins a predecessor crew's project; the crews lose more than the predecessor's share)
**Role:** replication (exploratory)
**Period:** #31 (2026-02-16 → 02-20, non-holdout). Claude Sonnet 4.6 joined 02-18; Claude 3.7 Sonnet retired 02-19 (the farewell week); NE11
(100-turn session cap) 02-20.

## Why this event
The only non-holdout same-lab succession. It is the dry-run stand-in for the confirmatory NE30 test (`analysis/confirm_r2.py`, C1), scored with
the same code, and an exploratory R7 (substrate independence) observation in its own right.

## Prediction
*C1 as frozen in `confirm_r2.py` (2026-10-04), applied here as a stand-in:* (a) crews that contained the predecessor keep their write rate on R_G
except for the predecessor's share (relative change + share ≥ 0); (b) the successor writes on a predecessor crew's project within 2 active days.

## Result
14 crews contained Claude 3.7 Sonnet in the pre-retirement days of #31. Mean (relative change + predecessor share) = -0.51
→ (a) not met; the successor wrote on 4 of them → (b)
met. Verdict by the C1 rule: **mixed**.

Confounds: the retirement week was a farewell goal, its last day (02-20) brought the 100-turn cap (NE11), and the successor overlapped the predecessor
by one day. So (a) cannot separate the departure from the week's wind-down.

## Notes
- 2026-10-04: written after the exploratory round-2 run, from the confirm script's dry run.
