"""Write the H08 goal-period cards (goalperiod-subhypotheses/G<NN>/README.md and NE41/README.md).

  uv run python hypotheses/H08-context-is-the-coupling/analysis/write_period_cards.py predict   # before any run
  uv run python hypotheses/H08-context-is-the-coupling/analysis/write_period_cards.py results   # after the runs

`predict` writes each card with its dated prediction and verdict rule and Result = pending. `results` regenerates the
same prediction text (it is deterministic) and fills Result, Scorecard and the verdict from the JSON outputs.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scheme"))
from h08lib import *  # noqa: E402,F403

PRED_STAMP = "2026-10-04 (~02:40 UTC)"
C8_POWERED = {38, 41, 51}          # >= 30 isolated nudge-target cells expected (from kick counts; no outcome seen)
C8_ANY = {30, 31, 33, 35, 36, 37, 38, 39, 40, 41, 42, 44, 51}
C23 = set(REGIME_III)
C10 = {37, 38, 39, 40, 41, 42, 44, 51}
DAY_RANGE = {}


def applies(g):
    return {"C9": True, "C8": g in C8_ANY, "C8_powered": g in C8_POWERED, "C1": g in CC_PERIODS, "C2": g in C23,
            "C3": g in C23, "C10": g in C10, "two_room": g in TWO_ROOM}


def why(g, p, a):
    bits = []
    if a["C1"]:
        bits.append("the Claude Code agent was in the village (ground truth for C1)")
    if a["C8_powered"]:
        bits.append("enough isolated nudges for a per-period kernel (C8)")
    elif a["C8"]:
        bits.append("a few nudges (C8 descriptive; pooled within regime)")
    if a["two_room"]:
        bits.append("two rooms, so other-room messages are an invisible placebo (C9-V3)")
    if g == 51:
        bits.append("the largest rooms and 8 h days (C10's long sessions); most pauses")
    if p["regime"] in ("III",) or g == 36:
        bits.append("perma-computer-use: consolidations every ≤ 41 turns (NE41 erasures, C3) and token accounting (C2)")
    if p["regime"] == "I":
        bits.append("regime I after NE09 (chat interleaved into computer-use context), so the call-start visibility rule applies")
    s = "; ".join(bits) + "."
    return s[:1].upper() + s[1:]


def prediction_text(g):
    p = PERIODS[g]; a = applies(g)
    L = [f"*Written {PRED_STAMP}, before running on this period (and before any real-data run of H08). Applies the card's "
         f"round-1 predictions and amendments A1–A6 (written after the synthetic validation, before real data).*", ""]
    L.append("- **C9-V1/V2 (visibility discontinuity, primary for every period):** among (message, recipient) pairs whose "
             "o = 0 turn is in flight, talking and addressing the sender jump at the read-out turn: D_talk = G_talk(1) − "
             "G_talk(0) > 0 and D_addr > 0, each with the day-bootstrap 95% CI excluding 0. G_addr(0) > 0 (contaminated floor, "
             "H18) but below ½ G_addr(1). A6: pre = G(0) − G(−1) ≈ 0.")
    L.append("- **C9-V4:** G_talk(2) < G_talk(1) (the response sits on the first visible turn).")
    if a["two_room"]:
        L.append("- **C9-V3:** messages from the room the recipient is not in: |D_other| < ⅓ of the own-room D, CI including 0.")
    if p["regime"] == "III" or g == 36:
        L.append("- **C9-V5:** median read-out delay of in-flight (active) recipients 10–40 s.")
    if a["C8"]:
        if a["C8_powered"]:
            L.append("- **C8-P1 (HH92, zero-parameter kernel):** nudge → target kernel (H04's design, this period only): the 95% CI "
                     "of Φ(1,5)_measured − Φ(1,5)_predicted (headroom-weighted read-out CDF F_hr) overlaps [−0.3, +0.1].")
            L.append("- **C8-P2:** F_hr(observed read-out) reaches half its 45-min value between 3 and 15 min.")
            L.append("- **C8-P3:** in 100 day-split CVs the best context-family model beats the best immediate, constant-delay and "
                     "Hawkes models each in ≥ 60% of splits, with median SSE ≤ 1.1 × the gamma ceiling.")
            L.append("- **C8-P4:** the renewal prediction (no kick information) has a faster onset than the observed-read-out one "
                     "(Φ_ren(1,5) > Φ_obs(1,5)).")
            if g == 51:
                L.append("- **C8-P5 (pause-matched):** the early response (mean G over τ = 1–5) is larger for kicks to non-paused "
                         "agents than for kicks to agents with ≥ 5 min of declared pause left (CI of the difference excludes 0). "
                         "Expected caveat from the synthetic #51 skeletons: idle agents' read-outs are often > 60 min away, so the "
                         "kernel may be small.")
        else:
            L.append("- **C8:** too few isolated nudges for a per-period test (expected < 30 cells); the per-period kernel is "
                     "descriptive and enters the pooled regime estimate (exception (d)).")
    if a["C1"]:
        if g in (30, 31, 33):
            L.append("- **C1 (amended 2026-10-04):** one room (#general), so the agent sees events from the whole village; the "
                     "room rule's recall ≥ 0.9; coverage differs by type (talk, session start/stop, CONSOLIDATE visible; WAIT, "
                     "PAUSE not); median delay is minutes, heavy-tailed; precision may fall below recall (fetch limits).")
        else:
            L.append("- **C1 (amended 2026-10-04):** two rooms (the agent in #rest from 03-16, #general from 03-24 while the "
                     "others were in #best/#rest): ≤ 5% of other-room events seen; recall ≥ 0.9; type and delay as above.")
    if a["C2"]:
        L.append("- **C2-I1/I2:** within agent-days, log uncached tokens rise with log(1 + new room messages) (b > 0, CI "
                 "excluding 0) but messages explain little (partial R² < 0.05); P(talk | ≥ 1 new message) / P(talk | 0) > 1.2; "
                 "ρ(uncached, call latency) > 0.")
    if a["C3"]:
        L.append("- **C3-E1/E2 (NE41):** where ≥ 300 erased units, addressing an old sender whose message was read before a forced "
                 "consolidation falls relative to old senders read after it (β_F < 0, CI excluding 0; relative drop ≥ 30%); "
                 "β_V within ±50% of β_F. **E3:** voluntary segments shorter when inflow per turn is higher (ρ < 0).")
    if a["C10"]:
        L.append("- **C10-L1 (HH91 as stated):** backlog k per talk turn rises with session hour (ρ > 0; within-agent-day "
                 "slope CI > 0)." + (" **L2:** Hawkes n̂ is higher in the second half of the day (Δn̂ > 0, CI excluding 0)."
                                     if g in (38, 51) else "") + (" **L3:** across weeks, ρ(n̂, mean k) > 0." if g == 51 else ""))
    L.append("")
    L.append("**Verdict rule (fixed now).** Tests: T_C9 = V1 and V2 both pass; T_C8 (powered periods) = P1 band and P3 both "
             "hold → pass, Φ outside the band or a rival family winning ≥ 60% → fail, else inconclusive; T_C3 (≥ 300 forced-"
             "erased units) = β_F < 0 with CI excluding 0 → pass, β_F > 0 with CI excluding 0 → fail, else inconclusive; "
             "T_C1 = recall ≥ 0.9 and (two rooms) other-room coverage ≤ 5% → pass, recall < 0.7 or other-room coverage > 20% "
             "→ fail. **supported** = T_C9 passes and no other test fails; **failed** = T_C9 fails; **mixed** = T_C9 passes "
             "and another test fails. C2, C10 and the secondary items are reported but do not set the verdict.")
    return "\n".join(L)


def header(g, days):
    p = PERIODS[g]
    rng = f"{days[0]} → {days[-1]}" if days else "no non-holdout days"
    return rng


def card(g, result_md="*Pending.*", verdict="pending", score_md="*Pending.*", notes=""):
    p = PERIODS[g]; a = applies(g)
    days = period_days(g)
    title = p["title"] if g != 33 else "Discuss, debate, and act on your views about the recent Pentagon-AI company news"
    txt = f"""# H08 × {gname(g)}: {title} ({header(g, days)})

**Verdict:** {verdict}
**Role:** exploratory
**Period:** regime {p['regime']} · mode {p['mode']} · N ≈ {p['N']} · {p['rooms']} · {len(days)} non-holdout days.

## Why this period
{why(g, p, a)}

## Prediction
{prediction_text(g)}

## Result
{result_md}

## Scorecard (period-specific axes)
{score_md}

## Notes
- Card: [`../../README.md`](../../README.md). Data: `data/processed/H08-context-is-the-coupling/{gname(g)}/`.
{notes}"""
    d = GP / gname(g)
    d.mkdir(parents=True, exist_ok=True)
    (d / "figures").mkdir(exist_ok=True)
    (d / "README.md").write_text(txt)


NE41_PRED = f"""*Written {PRED_STAMP}, before running C3 on any period.*

NE41 is the forced consolidation at the 41-turn cap (regime III): the context window is erased and memory kept, at a time
set by the scaffold, not the agent. Each erasure is a transition object (exception (c)); per-period estimates (G cards)
are combined by DerSimonian–Laird random effects.
- **E1:** pooled β_F < 0 with the 95% CI excluding 0 and a relative drop ≥ 30% of the in-context rate at the same age:
  an old sender read before a forced erasure is addressed less than an old sender read after it, in the same
  post-consolidation talk turns.
- **E2:** pooled β_V within ±50% of β_F.
- **E3:** voluntary segments are shorter when inflow per turn is higher (ρ < 0 in ≥ 2/3 of periods).
- **Rivals:** memory-mediated coupling (β_F ≈ 0: what matters is written to memory and read back); restart overhead only
  (absorbed by PC(τ) and the new-sender contrast).

**Verdict rule (fixed now):** supported if E1 holds; failed if the pooled β_F CI includes 0 or is positive; mixed if E1
holds in sign but the relative drop is < 30%."""


def ne41_card(result_md="*Pending.*", verdict="pending", score_md="*Pending.*"):
    d = GP / "NE41"
    d.mkdir(parents=True, exist_ok=True)
    (d / "figures").mkdir(exist_ok=True)
    (d / "README.md").write_text(f"""# H08 × NE41: forced context erasure at the 41-turn consolidation cap (regime III, #36 from 03-24 → #51)

**Verdict:** {verdict}
**Role:** exploratory
**Period:** spans #36 (from 2026-03-24), #37–#42, #44, #51 (non-holdout days only). Natural experiment NE41 (found by H15).

## Why this test
H15 found that a forced context erasure (memory kept) cuts write output 33–53% for ~10 turns. If context is the
coupling, the same erasure should cut the coupling to whatever was only in the context: messages read before it.

## Prediction
{NE41_PRED}

## Result
{result_md}

## Scorecard (test-specific axes)
{score_md}

## Notes
- Card: [`../../README.md`](../../README.md). Data: `data/processed/H08-context-is-the-coupling/ne41_pooled.json`, `G<NN>/c3.json`.
- Forced / voluntary labels come from H15's catalog (`data/processed/H15-semantic-information-scrambles/consolidations.parquet`).
""")


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "predict"
    if mode == "predict":
        for g in sorted(PERIODS):
            card(g)
        ne41_card()
        print("wrote prediction cards:", ", ".join(gname(g) for g in sorted(PERIODS)), "+ NE41")
    else:
        import fill_period_results  # noqa: F401  (results mode lives in fill_period_results.py)
        fill_period_results.main(card, ne41_card, applies)


if __name__ == "__main__":
    main()
